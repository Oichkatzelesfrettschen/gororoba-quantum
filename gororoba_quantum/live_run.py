"""Live-calibrated backend selection, compilation, noise simulation, and submission.

Every run fetches each accessible backend's status and calibration afresh
(IBMBackend.refresh and properties(refresh=True)) and compiles, scores,
simulates, and optionally submits inside that one process; no calibration value
is cached across runs or read back from a file to drive a submission. A backend
is eligible when it reports operational and status_msg "active" and its queue is
at most --max-pending jobs. Qubits and CZ edges outside the QUALITY policy, or
listed faulty, are excluded; a candidate layout touching one is rejected.

For each experiment group (experiments.py) and each eligible backend, the
primary circuit is transpiled under --seeds seeds; the best candidates by
estimated success probability (ESP, the product of 1 - error over every gate and
measurement, from the backend Target) compile their controls onto the same
initial layout, and the candidate with the highest geometric-mean ESP across
the group wins. ESP ranks layouts; the prediction is the noise simulation of the
chosen ISA circuits with noise from that same Target, after the Target's errors
are checked against the properties fetched with it on every qubit and edge of
the plan.

--submit sends each backend's chosen circuits as one client-side Sampler job
(qiskit_ibm_runtime.executor_sampler) after re-reading the calibration values of
the plan's qubits and edges and recompiling any group whose values moved;
last_update_date advances without value changes, so values, not timestamps,
decide. --collect reads a finished run's jobs, fetches the Target and
properties in force when they ran (target_history and properties with
datetime=), checks them against each other, and re-simulates under that Target,
so measurement is compared against the calibration of its own execution.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import ControlFlowOp
from qiskit.providers import BackendV2, Options
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

from experiments import MIRROR_SUFFIX, Group, experiment_groups, tvd

SHOTS = 4096
OPT_LEVEL = 3
SEED_TRANSPILER = 20261010
SEED_SIMULATOR = 20261011
JOINT_CANDIDATES = 3
DEFAULT_SEEDS = 8
DEFAULT_MAX_PENDING = 25
DEFAULT_MIN_REMAINING_S = 60.0

# Exclusion policy: values outside these bounds mark degraded hardware that the
# backend may report without a faulty flag. Missing T1 or T2 also excludes.
QUALITY = {"max_readout_error": 0.08, "max_cz_error": 0.03, "max_sx_error": 0.01, "min_t1_us": 20.0, "min_t2_us": 20.0}


class LiveRunError(RuntimeError):
    """A live check failed: stale or mismatched calibration, policy, or budget."""


@dataclass
class Snapshot:
    backend: Any
    properties: Any
    name: str
    operational: bool
    status_msg: str
    pending_jobs: int
    calibration: str
    fetched_at: str
    excluded_qubits: dict[int, str] = field(default_factory=dict)
    excluded_edges: dict[tuple[int, int], str] = field(default_factory=dict)
    medians: dict[str, float] = field(default_factory=dict)

    def ineligible_reason(self, max_pending: int | None) -> str | None:
        if not self.operational or self.status_msg != "active":
            return f"status operational={self.operational} msg={self.status_msg!r}"
        if max_pending is not None and self.pending_jobs > max_pending:
            return f"{self.pending_jobs} pending jobs exceeds --max-pending {max_pending}"
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "operational": self.operational,
            "status_msg": self.status_msg,
            "pending_jobs": self.pending_jobs,
            "calibration": self.calibration,
            "fetched_at": self.fetched_at,
            "medians": self.medians,
            "excluded_qubits": {str(q): r for q, r in sorted(self.excluded_qubits.items())},
            "excluded_edges": {f"{a}-{b}": r for (a, b), r in sorted(self.excluded_edges.items())},
        }


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def take_snapshot(service: QiskitRuntimeService, name: str) -> Snapshot:
    """Fresh status, Target, and properties for one backend, with the exclusion policy applied."""
    backend = service.backend(name)
    backend.refresh()
    props = backend.properties(refresh=True)
    status = backend.status()
    snap = Snapshot(
        backend=backend,
        properties=props,
        name=backend.name,
        operational=bool(status.operational),
        status_msg=str(status.status_msg),
        pending_jobs=int(status.pending_jobs),
        calibration=props.last_update_date.isoformat(),
        fetched_at=_now(),
    )
    faulty_q = set(props.faulty_qubits())
    faulty_edges = {tuple(g.qubits) for g in props.faulty_gates() if g.gate == "cz"}
    t1s, t2s, ros, czs = [], [], [], []
    for q in range(backend.num_qubits):
        reason = _qubit_reason(props, q, faulty_q)
        if reason:
            snap.excluded_qubits[q] = reason
        else:
            t1s.append(props.t1(q) * 1e6)
            t2s.append(props.t2(q) * 1e6)
            ros.append(props.readout_error(q))
    for qargs, inst in backend.target["cz"].items():
        err = inst.error if inst is not None else None
        edge = (qargs[0], qargs[1])
        if edge in faulty_edges or tuple(reversed(edge)) in faulty_edges:
            snap.excluded_edges[edge] = "faulty"
        elif err is None or err > QUALITY["max_cz_error"]:
            snap.excluded_edges[edge] = f"cz error {err}"
        else:
            czs.append(err)
    snap.medians = {
        "t1_us": float(np.median(t1s)),
        "t2_us": float(np.median(t2s)),
        "readout_error": float(np.median(ros)),
        "cz_error": float(np.median(czs)),
    }
    return snap


def _qubit_reason(props: Any, q: int, faulty: set[int]) -> str | None:
    if q in faulty:
        return "faulty"
    if not props.is_qubit_operational(q):
        return "not operational"
    try:
        t1, t2, ro = props.t1(q) * 1e6, props.t2(q) * 1e6, props.readout_error(q)
        sx = props.gate_error("sx", q)
    except Exception as exc:  # BackendPropertyError for a missing parameter
        return f"missing calibration: {exc}"
    if t1 < QUALITY["min_t1_us"] or t2 < QUALITY["min_t2_us"]:
        return f"T1={t1:.1f}us T2={t2:.1f}us"
    if ro > QUALITY["max_readout_error"]:
        return f"readout error {ro:.3f}"
    if sx > QUALITY["max_sx_error"]:
        return f"sx error {sx:.4f}"
    return None


def _qargs(isa: QuantumCircuit, inst: Any) -> tuple[int, ...]:
    return tuple(isa.find_bit(q).index for q in inst.qubits)


def _ops(isa: QuantumCircuit) -> list[tuple[str, tuple[int, ...]]]:
    return [
        (inst.operation.name, _qargs(isa, inst)) for inst in isa.data if inst.operation.name not in ("barrier", "delay")
    ]


def esp(isa: QuantumCircuit, target: Any) -> float:
    """Product of (1 - error) over every gate and measurement of isa, from target."""
    log_p = 0.0
    for name, qargs in _ops(isa):
        props = target[name].get(qargs) if name in target.operation_names else None
        err = props.error if props is not None and props.error is not None else 0.0
        log_p += math.log1p(-min(err, 1.0 - 1e-15))
    return math.exp(log_p)


def _violations(isa: QuantumCircuit, snap: Snapshot) -> list[str]:
    bad = []
    for name, qargs in _ops(isa):
        bad += [f"qubit {q}" for q in qargs if q in snap.excluded_qubits]
        if name == "cz" and (qargs in snap.excluded_edges or tuple(reversed(qargs)) in snap.excluded_edges):
            bad.append(f"edge {qargs}")
    return sorted(set(bad))


def fingerprint(isas: list[QuantumCircuit], props: Any) -> dict[str, float]:
    """Calibration values of exactly the qubits and CZ edges the circuits use."""
    out: dict[str, float] = {}
    for isa in isas:
        for name, qargs in _ops(isa):
            for q in qargs:
                out[f"t1:{q}"] = props.t1(q)
                out[f"t2:{q}"] = props.t2(q)
                out[f"ro:{q}"] = props.readout_error(q)
                out[f"sx:{q}"] = props.gate_error("sx", q)
            if name == "cz":
                out[f"cz:{qargs[0]}-{qargs[1]}"] = props.gate_error("cz", list(qargs))
    return out


def check_target_matches_properties(isas: list[QuantumCircuit], target: Any, props: Any, label: str) -> None:
    """The Target that scores and noise read and the properties agree on every qubit and edge of isas.

    Agreement proves both views come from one calibration fetch, so the ESP
    ranking and the noise simulation describe the same device state.
    """
    for isa in isas:
        for name, qargs in _ops(isa):
            if name == "cz":
                pairs = [(target["cz"][qargs].error, props.gate_error("cz", list(qargs)))]
            elif name == "sx":
                pairs = [(target["sx"][qargs].error, props.gate_error("sx", qargs[0]))]
            elif name == "measure":
                pairs = [(target["measure"][qargs].error, props.readout_error(qargs[0]))]
            else:
                continue
            for t_err, p_err in pairs:
                if t_err is None or abs(t_err - p_err) > 1e-12:
                    raise LiveRunError(f"{label} {name}{qargs}: target error {t_err} vs properties {p_err}")


@dataclass
class Choice:
    """The winning compile of a group, with mirror twins appended as entries."""

    group: Group
    snap: Snapshot
    seed: int
    layout: list[int]
    isas: list[QuantumCircuit]
    member_scores: list[float]
    joint_score: float
    entries: list[tuple[str, QuantumCircuit, np.ndarray]] = field(default_factory=list)


def _compile(qc: QuantumCircuit, snap: Snapshot, seed: int, layout: list[int] | None = None) -> QuantumCircuit:
    return transpile(
        qc, backend=snap.backend, optimization_level=OPT_LEVEL, seed_transpiler=seed, initial_layout=layout
    )


def _gate_time_view(isa: QuantumCircuit) -> QuantumCircuit:
    """isa with each control-flow op replaced by its first block's gates.

    estimate_duration rejects control flow; the view keeps every gate the true
    branch can run and drops the classical feed-forward latency, which the
    Target does not report, so its duration is a lower bound for dynamic
    circuits.
    """
    out = isa.copy_empty_like()
    for inst in isa.data:
        if isinstance(inst.operation, ControlFlowOp):
            body = inst.operation.blocks[0]
            for sub in body.data:
                if sub.clbits:
                    raise LiveRunError(f"{isa.name}: classical operation inside a control-flow block")
                out.append(sub.operation, [inst.qubits[body.find_bit(q).index] for q in sub.qubits])
        else:
            out.append(inst)
    return out


def duration_s(isa: QuantumCircuit, target: Any) -> float:
    return float(_gate_time_view(isa).estimate_duration(target, unit="s"))


def coherence(isa: QuantumCircuit, target: Any) -> float:
    """exp(-T sum_q 1/T2_q) over the qubits isa touches, T its estimated duration.

    ESP counts gate and readout error; this factor charges idle dephasing on the
    chosen qubits for the length of the circuit (literature/notes/2509.18259.md).
    """
    duration = duration_s(isa, target)
    rate = sum(1.0 / target.qubit_properties[q].t2 for q in _physical(isa))
    return math.exp(-duration * rate)


def layout_score(isa: QuantumCircuit, target: Any) -> float:
    return esp(isa, target) * coherence(isa, target)


def mirror_isa(isa: QuantumCircuit, backend: Any, name: str) -> QuantumCircuit:
    """First half of isa's CZ content, a barrier, its inverse, measured as isa measures.

    The twin runs on isa's physical qubits with about isa's two-qubit count and
    ideally returns all zeros, so its measured <Z> is the attenuation a witness's
    <Z> is divided by (literature/notes/2507.08088.md, Sec. IV A 3). Translation
    to the ISA runs at optimization level 0 on the trivial layout, so no gate
    moves, and the barrier keeps the halves from cancelling.
    """
    body = isa.remove_final_measurements(inplace=False)
    total = body.count_ops().get("cz", 0)
    half = QuantumCircuit(isa.num_qubits)
    seen = 0
    for inst in body.data:
        if inst.operation.name == "barrier":
            continue
        if inst.operation.name == "cz":
            if seen >= total // 2:
                break
            seen += 1
        half.append(inst.operation, _qargs(body, inst))
    out = QuantumCircuit(isa.num_qubits, isa.num_clbits, name=name)
    out.compose(half, inplace=True)
    out.barrier()
    out.compose(half.inverse(), inplace=True)
    for inst in isa.data:
        if inst.operation.name == "measure":
            out.measure(isa.find_bit(inst.qubits[0]).index, isa.find_bit(inst.clbits[0]).index)
    return transpile(out, backend=backend, optimization_level=0, initial_layout=list(range(isa.num_qubits)))


def attach_mirrors(choice: Choice) -> Choice:
    """Entries: every member's ISA, then a mirror twin for each member that asks for one."""
    choice.entries = [(m.name, isa, m.ideal) for m, isa in zip(choice.group.members, choice.isas, strict=True)]
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        if member.mirror:
            name = member.name + MIRROR_SUFFIX
            twin = mirror_isa(isa, choice.snap.backend, name)
            zeros = np.zeros(2**member.circuit.num_clbits)
            zeros[0] = 1.0
            choice.entries.append((name, twin, zeros))
    return choice


def select(group: Group, snaps: list[Snapshot], seeds: int, log: dict[str, Any]) -> Choice:
    """Best (backend, seed, layout) for the group by geometric-mean layout score over its members."""
    best: Choice | None = None
    log[group.name] = {}
    for snap in snaps:
        trace: list[dict[str, Any]] = []
        log[group.name][snap.name] = trace
        primaries = []
        for seed in range(SEED_TRANSPILER, SEED_TRANSPILER + seeds):
            isa = _compile(group.members[0].circuit, snap, seed)
            bad = _violations(isa, snap)
            score = layout_score(isa, snap.backend.target)
            trace.append({"seed": seed, "primary_score": score, "cz": isa.count_ops().get("cz", 0), "rejected": bad})
            if not bad:
                primaries.append((score, seed, isa))
        primaries.sort(key=lambda item: -item[0])
        for _, seed, isa in primaries[:JOINT_CANDIDATES]:
            layout = isa.layout.initial_index_layout(filter_ancillas=True)
            isas = [isa] + [_compile(m.circuit, snap, seed, layout) for m in group.members[1:]]
            if any(_violations(c, snap) for c in isas[1:]):
                continue
            scores = [layout_score(c, snap.backend.target) for c in isas]
            joint = math.exp(sum(math.log(s) for s in scores) / len(scores))
            trace.append({"seed": seed, "joint_score": joint, "layout": layout})
            better = best is None or (joint, -snap.pending_jobs) > (best.joint_score, -best.snap.pending_jobs)
            if better:
                best = Choice(group, snap, seed, layout, isas, scores, joint)
    if best is None:
        raise LiveRunError(f"{group.name}: no eligible backend produced a layout clear of excluded hardware")
    return attach_mirrors(best)


def _distribution(counts: dict[str, int], clbits: int) -> np.ndarray:
    dist = np.zeros(2**clbits)
    for key, c in counts.items():
        dist[int(key.replace(" ", ""), 2)] += c
    return np.asarray(dist / dist.sum())


class TargetView(BackendV2):
    """A BackendV2 whose only content is a Target, for building Aer noise from it.

    AerSimulator.from_backend reads gate errors, durations, and T1/T2 from
    backend.target, so the view turns a live or historical Target into a noise
    model without a second calibration source.
    """

    def __init__(self, name: str, target: Any) -> None:
        super().__init__(name=name)
        self._view_target = target

    @property
    def target(self) -> Any:
        return self._view_target

    @property
    def max_circuits(self) -> None:
        return None

    @classmethod
    def _default_options(cls) -> Options:
        return Options()

    def run(self, run_input: Any, **options: Any) -> Any:
        raise NotImplementedError("TargetView carries a Target for noise modeling only")


def noise_simulator(name: str, target: Any) -> AerSimulator:
    """AerSimulator with noise from exactly this Target; planning and --collect both use it."""
    return AerSimulator.from_backend(TargetView(name, target))


def simulate(choice: Choice, noise: Any) -> dict[str, np.ndarray]:
    out = {}
    for name, isa, _ in choice.entries:
        counts = noise.run(isa, shots=SHOTS, seed_simulator=SEED_SIMULATOR).result().get_counts()
        out[name] = _distribution(counts, isa.num_clbits)
    return out


def _physical(isa: QuantumCircuit) -> list[int]:
    return sorted({q for _, qargs in _ops(isa) for q in qargs})


def _choice_record(choice: Choice, noisy: dict[str, np.ndarray], noise_calibration: str) -> dict[str, Any]:
    target = choice.snap.backend.target
    members = []
    for name, isa, ideal in choice.entries:
        members.append(
            {
                "name": name,
                "cz": isa.count_ops().get("cz", 0),
                "depth": isa.depth(),
                "duration_s": duration_s(isa, target),
                "feed_forward": any(isinstance(i.operation, ControlFlowOp) for i in isa.data),
                "physical_qubits": _physical(isa),
                "esp": esp(isa, target),
                "coherence": coherence(isa, target),
                "ideal": [round(float(p), 12) for p in ideal],
                "noisy": [round(float(p), 6) for p in noisy[name]],
                "tvd_noisy_to_ideal": tvd(noisy[name], ideal),
            }
        )
    return {
        "group": choice.group.name,
        "backend": choice.snap.name,
        "calibration": choice.snap.calibration,
        "noise_model_calibration": noise_calibration,
        "seed_transpiler": choice.seed,
        "initial_layout": choice.layout,
        "joint_score": choice.joint_score,
        "summary": choice.group.summarize(noisy),
        "members": members,
    }


def plan(service: QiskitRuntimeService, args: argparse.Namespace) -> tuple[list[Choice], dict[str, Any]]:
    names = args.backends or [b.name for b in service.backends()]
    snaps, skipped = [], {}
    for name in names:
        snap = take_snapshot(service, name)
        reason = snap.ineligible_reason(args.max_pending)
        print(
            f"{snap.name}: {snap.status_msg} pending={snap.pending_jobs} calibration={snap.calibration} "
            f"medians={ {k: round(v, 5) for k, v in snap.medians.items()} } "
            f"excluded qubits={len(snap.excluded_qubits)} edges={len(snap.excluded_edges)}"
            + (f" -> skipped: {reason}" if reason else "")
        )
        if reason:
            skipped[snap.name] = {"reason": reason} | snap.summary()
        else:
            snaps.append(snap)
    if not snaps:
        raise LiveRunError("no eligible backend")
    groups = [g for g in experiment_groups() if not args.groups or g.name in args.groups]
    trace: dict[str, Any] = {}
    choices = [select(group, snaps, args.seeds, trace) for group in groups]
    record = {
        "started": args.started,
        "versions": {pkg: version(pkg) for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
        "policy": QUALITY
        | {"max_pending": args.max_pending, "seeds": args.seeds, "joint_candidates": JOINT_CANDIDATES},
        "shots": SHOTS,
        "seed_simulator": SEED_SIMULATOR,
        "backends": {s.name: s.summary() for s in snaps},
        "skipped_backends": skipped,
        "selection_trace": trace,
    }
    return choices, record


def evaluate(choices: list[Choice], record: dict[str, Any]) -> None:
    """Noise-simulate each choice under its backend's live properties, after proving they match the Target."""
    sims: dict[str, tuple[AerSimulator, str]] = {}
    record["groups"] = []
    for choice in choices:
        isas = [isa for _, isa, _ in choice.entries]
        check_target_matches_properties(isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name)
        if choice.snap.name not in sims:
            sims[choice.snap.name] = (
                noise_simulator(choice.snap.name, choice.snap.backend.target),
                choice.snap.calibration,
            )
        sim, cal = sims[choice.snap.name]
        noisy = simulate(choice, sim)
        entry = _choice_record(choice, noisy, cal)
        record["groups"].append(entry)
        cz = [m["cz"] for m in entry["members"]]
        summary = {k: round(v, 4) for k, v in entry["summary"].items()}
        print(
            f"{choice.group.name}: {choice.snap.name} seed={choice.seed} layout={choice.layout} "
            f"joint_score={choice.joint_score:.4f} cz={cz} summary={summary}"
        )


def submit(
    service: QiskitRuntimeService, choices: list[Choice], args: argparse.Namespace, record: dict[str, Any]
) -> None:
    """Re-read the plan's calibration, recompile groups whose values moved, check budget, submit."""
    from qiskit_ibm_runtime.executor_sampler import Sampler

    moved = False
    for idx, choice in enumerate(choices):
        isas = [isa for _, isa, _ in choice.entries]
        before = fingerprint(isas, choice.snap.properties)
        fresh = take_snapshot(service, choice.snap.name)
        if fingerprint(isas, fresh.properties) != before or _any_violation(isas, fresh):
            print(f"{choice.group.name}: calibration moved on {choice.snap.name}; recompiling")
            choices[idx] = select(choice.group, [fresh], args.seeds, record.setdefault("reselection_trace", {}))
            moved = True
    if moved:
        # The record's predictions must describe the circuits that run.
        evaluate(choices, record)
        record["reevaluated_before_submit"] = True
    usage = service.usage()
    remaining = float(usage["usage_remaining_seconds"])
    if remaining < args.min_remaining_seconds:
        raise LiveRunError(f"{remaining} s of QPU time remaining, below --min-remaining-seconds")
    record["submission"] = {"usage_before": usage, "jobs": []}
    by_backend: dict[str, list[Choice]] = {}
    for choice in choices:
        by_backend.setdefault(choice.snap.name, []).append(choice)
    for name, group_choices in by_backend.items():
        circuits = [isa for c in group_choices for _, isa, _ in c.entries]
        names = [entry_name for c in group_choices for entry_name, _, _ in c.entries]
        sampler = Sampler(mode=group_choices[0].snap.backend)
        sampler.options.default_shots = SHOTS
        sampler.options.environment.job_tags = ["gororoba-quantum", args.started]
        if args.twirl:
            sampler.options.twirling.enable_gates = True
            sampler.options.twirling.enable_measure = True
        if args.dd:
            sampler.options.dynamical_decoupling.enable = True
            sampler.options.dynamical_decoupling.sequence_type = args.dd
        job = sampler.run(circuits)
        record["submission"]["jobs"].append(
            {
                "backend": name,
                "job_id": job.job_id(),
                "members": names,
                "calibration": group_choices[0].snap.calibration,
                "options": sampler.options.model_dump(mode="json"),
            }
        )
        print(f"submitted {len(circuits)} circuits to {name}: job {job.job_id()}")


def _any_violation(isas: list[QuantumCircuit], snap: Snapshot) -> bool:
    return any(_violations(isa, snap) for isa in isas)


def collect(service: QiskitRuntimeService, run_dir: Path) -> None:
    """Measured distributions against the noise model of the calibration in force at execution."""
    record = json.loads((run_dir / "record.json").read_text())
    with open(run_dir / "isa.qpy", "rb") as handle:
        isas = {c.name: c for c in qpy.load(handle)}
    groups = {g.name: g for g in experiment_groups()}
    out = []
    for job_entry in record["submission"]["jobs"]:
        job = service.job(job_entry["job_id"])
        result = job.result()
        ran_at = job.metrics()["timestamps"]["running"]
        backend = service.backend(job_entry["backend"])
        when = datetime.fromisoformat(ran_at)
        props_then = backend.properties(datetime=when)
        target_then = backend.target_history(datetime=when)
        check_target_matches_properties(
            [isas[n] for n in job_entry["members"]], target_then, props_then, f"{backend.name}@{ran_at}"
        )
        sim_then = noise_simulator(f"{backend.name}@{ran_at}", target_then)
        measured: dict[str, np.ndarray] = {}
        replayed: dict[str, np.ndarray] = {}
        for name, pub in zip(job_entry["members"], result, strict=True):
            isa = isas[name]
            measured[name] = _distribution(pub.data.c.get_counts(), isa.num_clbits)
            counts = sim_then.run(isa, shots=SHOTS, seed_simulator=SEED_SIMULATOR).result().get_counts()
            replayed[name] = _distribution(counts, isa.num_clbits)
        for gname, group in groups.items():
            if all(m.name in measured for m in group.members):
                out.append(
                    {
                        "group": gname,
                        "backend": job_entry["backend"],
                        "ran_at": ran_at,
                        "calibration_at_run": props_then.last_update_date.isoformat(),
                        "measured_summary": group.summarize(measured),
                        "replayed_summary": group.summarize(replayed),
                        "tvd_measured_to_replayed": {
                            m.name: tvd(measured[m.name], replayed[m.name]) for m in group.members
                        },
                    }
                )
    (run_dir / "collect.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backends", type=lambda s: s.split(","), help="comma-separated pin; default all accessible")
    parser.add_argument("--groups", type=lambda s: s.split(","), help="comma-separated experiment groups")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS, help="transpiler seeds per group and backend")
    parser.add_argument("--max-pending", type=int, default=DEFAULT_MAX_PENDING)
    parser.add_argument("--out", type=Path, help="directory under which the run's audit record is written")
    parser.add_argument("--submit", action="store_true", help="submit the chosen circuits (spends QPU time)")
    parser.add_argument("--min-remaining-seconds", type=float, default=DEFAULT_MIN_REMAINING_S)
    parser.add_argument("--twirl", action="store_true", help="Pauli-twirl gates and measurements on submission")
    parser.add_argument("--dd", choices=("XX", "XpXm", "XY4"), help="dynamical decoupling sequence on submission")
    parser.add_argument("--collect", type=Path, help="run directory whose submitted jobs to collect")
    args = parser.parse_args(argv)
    if args.submit and not args.out:
        parser.error("--submit needs --out so the job ids land in an audit record")
    service = QiskitRuntimeService()
    try:
        if args.collect:
            collect(service, args.collect)
            return 0
        args.started = _now()
        choices, record = plan(service, args)
        evaluate(choices, record)
        run_dir = args.out / args.started.replace(":", "") if args.out else None
        if run_dir:
            write_record(run_dir, choices, record)
        if args.submit and run_dir:
            try:
                submit(service, choices, args, record)
            finally:
                write_record(run_dir, choices, record)
    except LiveRunError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


def write_record(run_dir: Path, choices: list[Choice], record: dict[str, Any]) -> None:
    """The run's ISA circuits as QPY, named by member, and its JSON record."""
    run_dir.mkdir(parents=True, exist_ok=True)
    archived = []
    for choice in choices:
        for name, isa, _ in choice.entries:
            named = copy.copy(isa)
            named.name = name
            archived.append(named)
    with open(run_dir / "isa.qpy", "wb") as handle:
        qpy.dump(archived, handle)
    (run_dir / "record.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(f"audit record: {run_dir}")


if __name__ == "__main__":
    sys.exit(main())
