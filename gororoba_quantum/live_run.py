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

--submit re-reads each chosen backend just before submission: a backend that
left the eligibility gate fails the run, and a group whose calibration values
moved on its qubits and edges recompiles and re-simulates;
last_update_date advances without value changes, so values, not timestamps,
decide. Each backend's chosen circuits then go out as one client-side Sampler
job (qiskit_ibm_runtime.executor_sampler) after usage() for that backend's
instance clears --min-remaining-seconds. --collect reads a finished run's jobs,
fetches the Target and properties in force when they ran (target_history and
properties with datetime=), checks them against each other, and re-simulates
under that Target with the run's own shots and seed, so measurement is compared
against the calibration of its own execution.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import subprocess
import sys
from collections.abc import Callable
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
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.executor_sampler import Sampler

from experiments import MIRROR_SUFFIX, Group, Member, experiment_groups, tvd

SHOTS = 4096
OPT_LEVEL = 3
SEED_TRANSPILER = 20261010
SEED_SIMULATOR = 20261011
JOINT_CANDIDATES = 3
DEFAULT_SEEDS = 8
DEFAULT_MAX_PENDING = 25
DEFAULT_MIN_REMAINING_S = 60.0
MAX_REVALIDATION = 3
RECORD_SCHEMA_VERSION = 2

EXPERIMENT_SOURCE_MANIFEST = (
    "boolean_anf.py",
    "cd_core.py",
    "designs.py",
    "experiments.py",
    "factoring.py",
    "live_run.py",
    "modular_arithmetic.py",
    "order_finding.py",
    "predict.py",
    "select_lcu.py",
)

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
    native_cz: bool = True

    def ineligible_reason(self, max_pending: int | None) -> str | None:
        if not self.native_cz:
            return "no native cz instruction; the exclusion policy and compiles assume CZ"
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
    if "cz" not in backend.target.operation_names:
        snap.native_cz = False
        return snap
    faulty_q = set(props.faulty_qubits())
    faulty_edges = {tuple(g.qubits) for g in props.faulty_gates() if g.gate == "cz"}
    # A faulty single-qubit instruction (sx, x, measure) on an operational
    # qubit still makes that qubit unusable for these circuits.
    faulty_gate_q = {q: g.gate for g in props.faulty_gates() if g.gate != "cz" for q in g.qubits}
    t1s, t2s, ros, czs = [], [], [], []
    for q in range(backend.num_qubits):
        reason = f"faulty {faulty_gate_q[q]}" if q in faulty_gate_q else _qubit_reason(props, q, faulty_q)
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


def _qargs(circuit: QuantumCircuit, instruction: Any) -> tuple[int, ...]:
    return tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)


def _ops(isa: QuantumCircuit) -> list[tuple[str, tuple[int, ...]]]:
    """Return every possible physical operation, including nested control-flow blocks."""
    operations: list[tuple[str, tuple[int, ...]]] = []

    def walk(circuit: QuantumCircuit, physical_qubits: tuple[int, ...]) -> None:
        for instruction in circuit.data:
            local_indices = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
            mapped = tuple(physical_qubits[index] for index in local_indices)
            if isinstance(instruction.operation, ControlFlowOp):
                for block in instruction.operation.blocks:
                    if block.num_qubits != len(mapped):
                        raise LiveRunError(
                            f"{isa.name}: control-flow block has {block.num_qubits} qubits, expected {len(mapped)}"
                        )
                    walk(block, mapped)
            elif instruction.operation.name not in ("barrier", "delay"):
                operations.append((instruction.operation.name, mapped))

    walk(isa, tuple(range(isa.num_qubits)))
    return operations


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


CALIBRATED = ("cz", "sx", "x", "measure")


def _property_values(name: str, qargs: tuple[int, ...], props: Any) -> dict[str, float]:
    """Error and duration of one calibrated instruction, read from the properties."""
    if name == "measure":
        return {"error": props.readout_error(qargs[0]), "duration": props.readout_length(qargs[0])}
    gate_qubits: Any = list(qargs) if len(qargs) > 1 else qargs[0]
    return {"error": props.gate_error(name, gate_qubits), "duration": props.gate_length(name, gate_qubits)}


def fingerprint(isas: list[QuantumCircuit], props: Any) -> dict[str, float]:
    """Calibration values the plan depends on: T1, T2 of its qubits, error and duration of its instructions.

    The layout score reads errors and durations, the noise model reads both plus
    T1 and T2, and the readout correction reads prob_meas1_prep0 and
    prob_meas0_prep1, so a change to any of them moves the plan.
    """
    out: dict[str, float] = {}
    for isa in isas:
        for name, qargs in _ops(isa):
            for q in qargs:
                out[f"t1:{q}"] = props.t1(q)
                out[f"t2:{q}"] = props.t2(q)
            if name in CALIBRATED:
                for field_name, value in _property_values(name, qargs, props).items():
                    out[f"{name}{qargs}:{field_name}"] = value
            if name == "measure":
                # readout_corrected reads the asymmetric channel, which can move
                # while the aggregate readout_error holds.
                e10, e01 = readout_flips(props, qargs[0])
                out[f"e10:{qargs[0]}"], out[f"e01:{qargs[0]}"] = e10, e01
    return out


def readout_flips(props: Any, q: int) -> tuple[float, float]:
    """(e10, e01) = (prob_meas1_prep0, prob_meas0_prep1) of qubit q, or readout_error for both.

    The noise model, the readout correction, and the fingerprint all read the
    channel here, so a backend that omits the asymmetric fields gets the same
    symmetric fallback in each.
    """
    try:
        return props.qubit_property(q, "prob_meas1_prep0")[0], props.qubit_property(q, "prob_meas0_prep1")[0]
    except Exception:  # BackendPropertyError: asymmetric fields absent for this qubit
        error = props.readout_error(q)
        return error, error


def check_target_matches_properties(isas: list[QuantumCircuit], target: Any, props: Any, label: str) -> None:
    """The Target that scores and noise read and the properties agree on every qubit and edge of isas.

    Errors and durations of every CZ, sx, x, and measurement, and T1 and T2 of
    every touched qubit, must match, which proves both views come from one
    calibration fetch: the ESP ranking reads errors, and the noise model reads
    errors, durations, and T1/T2 from the Target.
    """
    for isa in isas:
        for name, qargs in _ops(isa):
            pairs: list[tuple[str, Any, float]] = []
            if name in CALIBRATED:
                inst = target[name][qargs]
                values = _property_values(name, qargs, props)
                pairs += [("error", inst.error, values["error"]), ("duration", inst.duration, values["duration"])]
            for q in qargs:
                qp = target.qubit_properties[q]
                pairs += [("t1", qp.t1, props.t1(q)), ("t2", qp.t2, props.t2(q))]
            for field_name, t_val, p_val in pairs:
                if t_val is None or not math.isclose(t_val, p_val, rel_tol=1e-9, abs_tol=1e-15):
                    raise LiveRunError(f"{label} {name}{qargs} {field_name}: target {t_val} vs properties {p_val}")


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


def _bind(isa: QuantumCircuit, member: Member) -> QuantumCircuit:
    return isa.assign_parameters(member.binding) if member.binding else isa


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
    # The barrier spans only the qubits the twin uses, so the untouched qubits
    # of the full-width ISA stay idle from initialization.
    out.barrier(_physical(isa))
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
        primary = group.members[0]
        for seed in range(SEED_TRANSPILER, SEED_TRANSPILER + seeds):
            isa = _compile(primary.circuit, snap, seed)
            bad = _violations(isa, snap)
            trace.append({"seed": seed, "cz": isa.count_ops().get("cz", 0), "rejected": bad})
            if bad:
                continue
            # Scoring follows rejection: coherence() divides by T2, which an
            # excluded qubit may lack, so a rejected layout is never scored.
            score = layout_score(isa, snap.backend.target)
            trace[-1]["primary_score"] = score
            primaries.append((score, seed, isa))
        primaries.sort(key=lambda item: -item[0])
        for _, seed, isa in primaries[:JOINT_CANDIDATES]:
            layout = isa.layout.initial_index_layout(filter_ancillas=True)
            # Members that share the primary's parametrized circuit reuse its ISA
            # with their own parameter values: one routing, one readout qubit.
            isas = [_bind(isa, primary)] + [
                _bind(isa if m.circuit is primary.circuit else _compile(m.circuit, snap, seed, layout), m)
                for m in group.members[1:]
            ]
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


def _pub_counts(pub: Any, isa: QuantumCircuit) -> dict[str, int]:
    """Join every classical register in circuit order into global clbit order."""
    register_names = [register.name for register in isa.cregs]
    if not register_names:
        raise LiveRunError(f"{isa.name}: result decoder needs at least one classical register")
    joined = pub.join_data(register_names)
    if not hasattr(joined, "get_counts"):
        raise LiveRunError(f"{isa.name}: joined result data does not provide bit counts")
    return dict(joined.get_counts())


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


def noise_simulator(name: str, target: Any, props: Any) -> AerSimulator:
    """AerSimulator with gate and coherence noise from this Target and readout from props.

    The Target's measure entries carry only the aggregate readout_error, from
    which Aer builds a symmetric channel. The noise model takes each qubit's
    asymmetric channel [[1 - e10, e10], [e01, 1 - e01]] (e10 =
    prob_meas1_prep0, e01 = prob_meas0_prep1) from the properties instead, the
    same channel readout_corrected inverts, so a corrected prediction removes
    exactly the readout error the simulation applied. A qubit without the two
    fields gets the symmetric readout_error channel from readout_flips, as the
    correction does. Planning and --collect both use it.
    """
    view = TargetView(name, target)
    noise = NoiseModel.from_backend(view, readout_error=False)
    for q in range(target.num_qubits):
        try:
            e10, e01 = readout_flips(props, q)
        except Exception:  # BackendPropertyError: no readout calibration at all
            continue
        noise.add_readout_error(ReadoutError([[1.0 - e10, e10], [e01, 1.0 - e01]]), [q])
    return AerSimulator.from_backend(view, noise_model=noise)


def simulate(choice: Choice, noise: Any) -> dict[str, np.ndarray]:
    out = {}
    for name, isa, _ in choice.entries:
        counts = noise.run(isa, shots=SHOTS, seed_simulator=SEED_SIMULATOR).result().get_counts()
        out[name] = _distribution(counts, isa.num_clbits)
    return out


def readout_corrected(dist: np.ndarray, isa: QuantumCircuit, props: Any, symmetric: bool = False) -> np.ndarray:
    """dist with each classical bit's readout channel inverted, unclipped.

    A raw P(0) carries prob_meas0_prep1 of its readout qubit as an additive
    floor, so even a perfect zero divisor reads a nonzero dark probability.
    Each clbit's 2x2 channel [[1 - e10, e01], [e10, 1 - e01]] comes from the
    physical qubit that last wrote it (e10 = prob_meas1_prep0, e01 =
    prob_meas0_prep1), and their Kronecker product is inverted with clbit 0 as
    the least significant index bit. Aer's noise model applies the symmetric
    readout_error by default; noise_simulator replaces it with the same
    asymmetric channel, so in simulation and on hardware the inversion matches
    the channel applied.

    symmetric replaces both flip probabilities with their mean: measurement
    twirling randomizes the measured bit and reverses it classically, so a
    twirled job's effective channel is the symmetric average.
    """
    writer: dict[int, int] = {}
    for inst in isa.data:
        if inst.operation.name == "measure":
            writer[isa.find_bit(inst.clbits[0]).index] = isa.find_bit(inst.qubits[0]).index
    inverse = np.ones((1, 1))
    for clbit in reversed(range(isa.num_clbits)):
        e10, e01 = readout_flips(props, writer[clbit])
        if symmetric:
            e10 = e01 = (e10 + e01) / 2.0
        inverse = np.kron(inverse, np.linalg.inv(np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])))
    return np.asarray(inverse @ dist)


def corrected_summary(
    group: Group, dists: dict[str, tuple[np.ndarray, QuantumCircuit]], props: Any, symmetric: bool = False
) -> Any:
    """The group summary on readout-inverted distributions, or why it is skipped.

    readout_corrected assumes each classical bit passes through its own
    output-only channel. In a feed-forward circuit a misread mid-circuit bit
    also steers the conditional gate, so the second bit's distribution depends
    on the first readout error and the separable inversion is biased; such
    groups report the reason instead of a corrected summary. props is one
    properties object, or a per-circuit mapping when circuits ran under
    different calibrations.
    """
    if any(_is_dynamic(isa) for _, isa in dists.values()):
        return {"skipped": "feed-forward circuits: readout error steers the conditional branch"}
    return group.summarize(
        {
            name: readout_corrected(dist, isa, props[name] if isinstance(props, dict) else props, symmetric)
            for name, (dist, isa) in dists.items()
        }
    )


def experiment_digest() -> str:
    """Return sha256 over the declared source closure that defines a run.

    Group membership, circuits, ideals, and summaries live in the experiment
    modules, and live_run.py itself holds the distribution, readout-correction,
    and replay code that turns counts into summaries, so collection under a
    different digest would reinterpret a run's measurements.
    """
    here = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for relative_path in EXPERIMENT_SOURCE_MANIFEST:
        path = here / relative_path
        if not path.is_file():
            raise LiveRunError(f"experiment source manifest entry is missing: {path}")
        digest.update(relative_path.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _code_commit() -> dict[str, Any]:
    """HEAD of the checkout and whether its gororoba_quantum sources differ from it."""
    here = Path(__file__).resolve().parent
    try:
        head = subprocess.run(["git", "-C", str(here), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        dirty = subprocess.run(
            ["git", "-C", str(here), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or f"exit {error.returncode}"
        raise LiveRunError(f"cannot establish Git provenance: {detail}") from error
    return {"head": head.stdout.strip() or None, "sources_modified": bool(dirty.stdout.strip())}


def _physical(isa: QuantumCircuit) -> list[int]:
    return sorted({q for _, qargs in _ops(isa) for q in qargs})


def _choice_record(choice: Choice, noisy: dict[str, np.ndarray], noise_calibration: str) -> dict[str, Any]:
    target = choice.snap.backend.target
    members = []
    for name, isa, ideal in choice.entries:
        dynamic = _is_dynamic(isa)
        members.append(
            {
                "name": name,
                "cz": isa.count_ops().get("cz", 0),
                "depth": isa.depth(),
                "duration_s": duration_s(isa, target),
                "duration_bound": "lower_without_classical_latency" if dynamic else "scheduled",
                "dynamic": dynamic,
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
        "summary_readout_corrected": corrected_summary(
            choice.group,
            {name: (noisy[name], isa) for name, isa, _ in choice.entries},
            choice.snap.properties,
        ),
        "members": members,
    }


def plan(service: QiskitRuntimeService, args: argparse.Namespace) -> tuple[list[Choice], dict[str, Any]]:
    known = {g.name for g in experiment_groups()}
    unknown = sorted(set(args.groups or []) - known)
    if unknown:
        raise LiveRunError(f"unknown experiment groups {unknown}; known: {sorted(known)}")
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
        "schema_version": RECORD_SCHEMA_VERSION,
        "state": "planned",
        "started": args.started,
        "versions": {pkg: version(pkg) for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
        "policy": QUALITY
        | {"max_pending": args.max_pending, "seeds": args.seeds, "joint_candidates": JOINT_CANDIDATES},
        "shots": SHOTS,
        "seed_simulator": SEED_SIMULATOR,
        "experiment_digest": experiment_digest(),
        "code_commit": _code_commit(),
        "backends": {s.name: s.summary() for s in snaps},
        "skipped_backends": skipped,
        "selection_trace": trace,
    }
    return choices, record


def evaluate(choices: list[Choice], record: dict[str, Any]) -> None:
    """Noise-simulate each choice under its backend's live properties, after proving they match the Target."""
    # One simulator per snapshot: a group recompiled on a fresh snapshot of a
    # backend is simulated with that snapshot's Target, not an earlier one.
    sims: dict[int, tuple[AerSimulator, str]] = {}
    record["groups"] = []
    for choice in choices:
        isas = [isa for _, isa, _ in choice.entries]
        check_target_matches_properties(isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name)
        key = id(choice.snap)
        if key not in sims:
            sims[key] = (
                noise_simulator(choice.snap.name, choice.snap.backend.target, choice.snap.properties),
                choice.snap.calibration,
            )
        sim, cal = sims[key]
        noisy = simulate(choice, sim)
        entry = _choice_record(choice, noisy, cal)
        record["groups"].append(entry)
        cz = [m["cz"] for m in entry["members"]]
        summary = {k: round(v, 4) for k, v in entry["summary"].items()}
        print(
            f"{choice.group.name}: {choice.snap.name} seed={choice.seed} layout={choice.layout} "
            f"joint_score={choice.joint_score:.4f} cz={cz} summary={summary}"
        )


def check_budget(name: str, usage: dict[str, Any], minimum: float) -> None:
    """Reject an exhausted or below-minimum finite quota; an instance with no limit passes.

    usage() can omit usage_remaining_seconds or report None for an instance
    without a configured limit; usage_limit_reached still marks exhaustion.
    """
    if usage.get("usage_limit_reached"):
        raise LiveRunError(f"{name}: the instance reports its usage limit reached")
    remaining = usage.get("usage_remaining_seconds")
    if remaining is not None and float(remaining) < minimum:
        raise LiveRunError(f"{name}: {remaining} s of QPU time remaining, below --min-remaining-seconds")


def submit(
    service: QiskitRuntimeService,
    choices: list[Choice],
    args: argparse.Namespace,
    record: dict[str, Any],
    archive: Callable[[], None],
    checkpoint: Callable[[], None],
) -> None:
    """Re-gate and re-read each chosen backend until nothing moved, then archive and submit.

    Recompiling and re-simulating takes long enough for the calibration, the
    status, or the queue to move again, so the gate repeats on fresh snapshots
    until a pass changes nothing, at most MAX_REVALIDATION passes. The final
    circuits reach isa.qpy before the first job is sent, and each job id is
    then checkpointed by a JSON-only atomic write, so no QPY rewrite stands
    between QPU time spent and its job id reaching disk.
    """
    for attempt in range(MAX_REVALIDATION):
        fresh_by_backend: dict[str, Snapshot] = {}
        moved = False
        for idx, choice in enumerate(choices):
            name = choice.snap.name
            if name not in fresh_by_backend:
                fresh_by_backend[name] = take_snapshot(service, name)
            fresh = fresh_by_backend[name]
            reason = fresh.ineligible_reason(args.max_pending)
            if reason:
                raise LiveRunError(f"{name} left the eligibility gate before submission ({reason}); rerun to replan")
            isas = [isa for _, isa, _ in choice.entries]
            before = fingerprint(isas, choice.snap.properties)
            if fingerprint(isas, fresh.properties) != before or _any_violation(isas, fresh):
                print(f"{choice.group.name}: calibration moved on {name}; recompiling")
                choices[idx] = select(choice.group, [fresh], args.seeds, record.setdefault("reselection_trace", {}))
                moved = True
        if not moved:
            break
        # The record's predictions must describe the circuits that run, and the
        # archive moves with them, so an abort on a later pass still leaves
        # record.json and isa.qpy describing the same circuits.
        evaluate(choices, record)
        record["reevaluated_before_submit"] = attempt + 1
        archive()
    else:
        raise LiveRunError(f"calibration kept moving through {MAX_REVALIDATION} revalidation passes; rerun later")
    archive()
    planned = sorted({choice.snap.name for choice in choices})
    # complete turns true only after every planned job has an id on disk; a
    # failure between jobs leaves it false for --collect to report.
    record["submission"] = {"planned_backends": planned, "jobs": [], "complete": False}
    record["state"] = "submission_started"
    by_backend: dict[str, list[Choice]] = {}
    for choice in choices:
        by_backend.setdefault(choice.snap.name, []).append(choice)
    for name, group_choices in by_backend.items():
        # service.backend selects the backend's instance as the active one, and
        # usage() reports the active instance, so each job's budget is checked
        # against the instance that pays for it.
        backend = service.backend(name)
        entries = [(entry_name, isa) for c in group_choices for entry_name, isa, _ in c.entries]
        # Circuits with mid-circuit measurement, reset, or feed-forward go in
        # their own job, which configure_sampler keeps free of twirling and DD.
        static = [(n, isa) for n, isa in entries if not _is_dynamic(isa)]
        dynamic = [(n, isa) for n, isa in entries if _is_dynamic(isa)]
        for kind, batch in (("static", static), ("dynamic", dynamic)):
            if not batch:
                continue
            usage = service.usage()
            check_budget(name, usage, args.min_remaining_seconds)
            sampler = configure_sampler(backend, kind, args.twirl, args.dd, ["gororoba-quantum", args.started, kind])
            job = sampler.run([isa for _, isa in batch])
            record["submission"]["jobs"].append(
                {
                    "backend": name,
                    "kind": kind,
                    "job_id": job.job_id(),
                    "members": [n for n, _ in batch],
                    "calibration": group_choices[0].snap.calibration,
                    "budget_before": _budget(service, usage),
                    "options": sampler.options.model_dump(mode="json"),
                }
            )
            # The job id is the only handle on QPU time already spent; it reaches
            # disk before the next job is sent.
            record["state"] = "partially_submitted"
            checkpoint()
            print(f"submitted {len(batch)} {kind} circuits to {name}: job {job.job_id()}")
    record["submission"]["complete"] = True
    record["state"] = "submitted"
    checkpoint()


def configure_sampler(backend: Any, kind: str, twirl: bool, dd: str | None, tags: list[str]) -> Sampler:
    """The client-side Sampler for one job: twirling and DD apply to static jobs only.

    IBM's Sampler rejects dynamical decoupling on dynamic circuits, and the 0.50
    client-side Sampler's twirling boxes circuits through samplomatic, which
    rejects if_else. With DD on, idle qubits still in their initial state get no
    pulses: a 3- to 5-qubit experiment on a 156-qubit ISA would otherwise drive
    the unused qubits too.
    """
    sampler = Sampler(mode=backend)
    sampler.options.default_shots = SHOTS
    sampler.options.environment.job_tags = tags
    if twirl and kind == "static":
        sampler.options.twirling.enable_gates = True
        sampler.options.twirling.enable_measure = True
    if dd and kind == "static":
        sampler.options.dynamical_decoupling.enable = True
        sampler.options.dynamical_decoupling.sequence_type = dd
        sampler.options.dynamical_decoupling.skip_reset_qubits = True
    return sampler


def _is_dynamic(isa: QuantumCircuit) -> bool:
    """Control flow, reset, or any measurement followed by later quantum work."""
    measurement_seen = False
    for inst in isa.data:
        name = inst.operation.name
        if isinstance(inst.operation, ControlFlowOp) or name == "reset":
            return True
        if measurement_seen and name not in ("measure", "barrier", "delay"):
            return True
        if name == "measure":
            measurement_seen = True
    return False


def _budget(service: QiskitRuntimeService, usage: dict[str, Any]) -> dict[str, Any]:
    """usage() seconds and window, with the instance identified only by a hash of its CRN."""
    instance = str(service.active_instance() or "")
    return {
        "instance_sha256_12": hashlib.sha256(instance.encode()).hexdigest()[:12],
        "usage_period": usage.get("usage_period"),
        "usage_limit_seconds": usage.get("usage_limit_seconds"),
        "usage_consumed_seconds": usage.get("usage_consumed_seconds"),
        "usage_remaining_seconds": usage.get("usage_remaining_seconds"),
    }


def _any_violation(isas: list[QuantumCircuit], snap: Snapshot) -> bool:
    return any(_violations(isa, snap) for isa in isas)


def pub_windows(result: Any, count: int) -> list[tuple[datetime, datetime]]:
    """Start and stop of the execution spans that hold each PUB's shots.

    The Sampler result carries them at result.metadata["execution"]
    ["execution_spans"] (IBM's Sampler input/output guide, "View execution
    spans"); the job-level running timestamp can precede the shots by
    server-side preparation, across a calibration update. Naive span times are
    UTC.
    """
    execution = result.metadata.get("execution") or {}
    spans = execution.get("execution_spans")
    if spans is None or len(spans) == 0:
        raise LiveRunError(f"result metadata carries no execution spans (keys {sorted(result.metadata)})")
    windows = []
    for idx in range(count):
        # ExecutionSpans.filter_by_pub keeps every span and empties those
        # without the PUB, so the PUB's own window comes from the spans whose
        # pub_idxs include it.
        own = [span for span in spans if idx in span.pub_idxs]
        if not own:
            raise LiveRunError(f"no execution span covers PUB {idx}")
        start, stop = min(span.start for span in own), max(span.stop for span in own)
        windows.append(
            (
                start if start.tzinfo else start.replace(tzinfo=UTC),
                stop if stop.tzinfo else stop.replace(tzinfo=UTC),
            )
        )
    return windows


def collect(service: QiskitRuntimeService, run_dir: Path) -> None:
    """Measured distributions against the noise model of the calibration in force at execution."""
    record = json.loads((run_dir / "record.json").read_text())
    with open(run_dir / "isa.qpy", "rb") as handle:
        isas = {c.name: c for c in qpy.load(handle)}
    groups = {g.name: g for g in experiment_groups()}
    if record.get("experiment_digest") != experiment_digest():
        commit = record.get("code_commit", {}).get("head")
        raise LiveRunError(
            f"experiment definitions differ from the run's (digest {record.get('experiment_digest')}); "
            f"collect from commit {commit}, where groups, ideals, and summaries match the archived circuits"
        )
    if "submission" not in record:
        raise LiveRunError(f"{run_dir} is a dry-run record with no submitted jobs to collect")
    submission = record["submission"]
    sent = {job["backend"] for job in submission["jobs"]}
    unsent = [name for name in submission.get("planned_backends", []) if name not in sent]
    if not submission.get("complete", False):
        print(
            f"incomplete submission: no job was sent to {unsent}; collecting the {len(sent)} that were", file=sys.stderr
        )
    shots, seed = int(record["shots"]), int(record["seed_simulator"])
    out: list[dict[str, Any]] = [
        {"submission_complete": bool(submission.get("complete", False)), "unsent_backends": unsent}
    ]
    for job_entry in record["submission"]["jobs"]:
        job = service.job(job_entry["job_id"])
        result = job.result()
        metrics = job.metrics()
        members = job_entry["members"]
        windows = pub_windows(result, len(members))
        twirled_readout = bool(job_entry.get("options", {}).get("twirling", {}).get("enable_measure"))
        backend = service.backend(job_entry["backend"])
        # One calibration fetch per distinct execution start: a PUB is replayed
        # under the Target and properties in force when its shots began.
        at: dict[datetime, tuple[Any, Any]] = {}
        for start, _ in windows:
            if start not in at:
                props_then = backend.properties(datetime=start)
                target_then = backend.target_history(datetime=start)
                at[start] = (
                    props_then,
                    noise_simulator(f"{backend.name}@{start.isoformat()}", target_then, props_then),
                )
                starting = [isas[n] for (st, _), n in zip(windows, members, strict=True) if st == start]
                check_target_matches_properties(starting, target_then, props_then, f"{backend.name}@{start}")
        measured: dict[str, np.ndarray] = {}
        props_by_name: dict[str, Any] = {}
        replayed: dict[str, np.ndarray] = {}
        executed: dict[str, dict[str, Any]] = {}
        for idx, (name, pub) in enumerate(zip(members, result, strict=True)):
            isa = isas[name]
            start, stop = windows[idx]
            props_then, sim_then = at[start]
            measured[name] = _distribution(_pub_counts(pub, isa), isa.num_clbits)
            props_by_name[name] = props_then
            counts = sim_then.run(isa, shots=shots, seed_simulator=seed).result().get_counts()
            replayed[name] = _distribution(counts, isa.num_clbits)
            stop_calibration = backend.properties(datetime=stop).last_update_date
            executed[name] = {
                "start": start.isoformat(),
                "stop": stop.isoformat(),
                "calibration": props_then.last_update_date.isoformat(),
                "calibration_changed_during_shots": stop_calibration != props_then.last_update_date,
            }
        for gname, group in groups.items():
            present = [n for n in measured if n in {m.name for m in group.members}]
            if not present:
                continue
            # A summary needs every member and every mirror twin; a job that
            # lacks some still reports the distributions it has.
            required = [m.name for m in group.members] + [m.name + MIRROR_SUFFIX for m in group.members if m.mirror]
            missing = [n for n in required if n not in measured]
            entry: dict[str, Any] = {
                "group": gname,
                "backend": job_entry["backend"],
                "executed": {n: executed[n] for n in required if n in executed},
                "job_usage": metrics.get("usage"),
                "measured": {n: [round(float(p), 6) for p in measured[n]] for n in required if n in measured},
            }
            # A circuit whose shots straddle a calibration update has no single
            # calibration to correct or replay against; its group keeps the raw
            # measurement and states why the rest is absent.
            straddling = [n for n in required if n in executed and executed[n]["calibration_changed_during_shots"]]
            if missing:
                entry["summary_unavailable"] = f"missing {missing}"
            else:
                entry["measured_summary"] = group.summarize(measured)
                if straddling:
                    entry["calibration_dependent_summaries_unavailable"] = (
                        f"calibration changed during the shots of {straddling}"
                    )
                else:
                    entry["measured_summary_readout_corrected"] = corrected_summary(
                        group, {n: (measured[n], isas[n]) for n in required}, props_by_name, symmetric=twirled_readout
                    )
                    entry["replayed_summary"] = group.summarize(replayed)
                    entry["tvd_measured_to_replayed"] = {n: tvd(measured[n], replayed[n]) for n in required}
            out.append(entry)
    text = json.dumps(out, indent=2) + "\n"
    _replace_atomically(run_dir / "collect.json", lambda handle: handle.write(text), "w")
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
        now = datetime.now(UTC)
        args.started = now.isoformat(timespec="microseconds")
        # Microsecond names and exclusive creation keep concurrent runs from
        # sharing a directory.
        run_dir = args.out / now.strftime("%Y-%m-%dT%H%M%S.%fZ") if args.out else None
        choices, record = plan(service, args)
        evaluate(choices, record)
        if run_dir:
            run_dir.mkdir(parents=True, exist_ok=False)
            write_archive(run_dir, choices)
            write_json(run_dir, record)
        if args.submit and run_dir:
            try:
                submit(
                    service,
                    choices,
                    args,
                    record,
                    lambda: write_archive(run_dir, choices),
                    lambda: write_json(run_dir, record),
                )
            finally:
                write_json(run_dir, record)
    except LiveRunError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


def _replace_atomically(target: Path, write: Callable[[Any], None], mode: str) -> None:
    """Write beside target, fsync, and os.replace over it: an interruption leaves the old file whole."""
    tmp = target.with_name(target.name + ".tmp")
    with open(tmp, mode) as handle:
        write(handle)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)


def write_archive(run_dir: Path, choices: list[Choice]) -> None:
    """The run's ISA circuits as QPY, named by member."""
    archived = []
    for choice in choices:
        for name, isa, _ in choice.entries:
            named = copy.copy(isa)
            named.name = name
            archived.append(named)
    _replace_atomically(run_dir / "isa.qpy", lambda handle: qpy.dump(archived, handle), "wb")


def write_json(run_dir: Path, record: dict[str, Any]) -> None:
    """The run's JSON record."""
    text = json.dumps(record, indent=2, default=str) + "\n"
    _replace_atomically(run_dir / "record.json", lambda handle: handle.write(text), "w")
    print(f"audit record: {run_dir}")


if __name__ == "__main__":
    sys.exit(main())
