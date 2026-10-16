"""JAX bridge sweep: exact model probabilities of retained replicas across the error-scale grid, on a chosen JAX device.

For every retained run and member, under the snapshot in force when its PUB
began (ghost_run.prepare), each replica whose measurements are all terminal
becomes one program per CZ factor of scripts/ghost_error_scale.py, and the
programs replay as batched JAX calls on the requested device. The readout
factors act on the resulting register diagonal classically, with the same cap
as ghost_error_scale.flip, so each replica yields the exact model
distribution at all fifty grid points and its TV distance to the hardware
distribution retained in collect.json. These distances carry hardware shot
noise only; the ghost sweep's sampled distances also carry the model draw,
so the two estimators are reported side by side and never merged.

Programs come from one factor-1 noise model per snapshot. Replicas of equal
jax_bridge.structure_key share one template export and differ only in their
gate angles; a CZ factor replaces only the CZ local errors, with
jax_bridge.CzChannel at the error ghost_error_scale.scaled reports for that
factor (min(factor * error, CZ_CAP)). Every other channel of the scaled
noise model equals the factor-1 one, because scaled changes only cz errors
and readout flips and the program reads readout classically.

Before its distances count, a seeded sample of each run's replicas (sorted
``member#k`` labels, ``--parity-sample`` of them, ``all`` for every one) has
its factor-1 distribution compared with Aer's own density matrix
(calibration_snapshot.noise_simulator with save_density_matrix in place of
the terminal measurements) on the CPU; the output records each checked
label with its largest probability difference. Replicas with reset,
mid-circuit measurement or classical control are listed as skipped with the
reason. ``--device`` names the JAX platform the replay must use (cpu, gpu or
tpu); a missing platform raises instead of falling back, and the output
records the platform of every result array.

``--self-test`` runs the contracts on a reduced case on the CPU without
JAX: every replica's template instance equals its direct export; the
rescaled CZ stack of every coupler the case drives, and of every coupler
whose reported error exceeds the 4/5 cap, equals the channel of a freshly
built Aer noise model at four factors that reach the zero-depolarizing branch, the interior
and both caps; the scaled models change no other channel; the restructured
programs reproduce the per-factor exports of the scaled noise models; and
the sampled parity holds. ``--self-test --device cpu`` also replays the
restructured programs in JAX and compares them with numpy.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale  # noqa: E402
import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Kraus, SuperOp  # noqa: E402

import calibration_snapshot  # noqa: E402
import jax_bridge  # noqa: E402

SCHEMA = "jax-bridge-sweep-v2"
PARITY_SAMPLE = 2
PARITY_SEED = ghost_run.SEED
# complex64 density-matrix bytes per replay call; the CZ contraction holds
# about rank (16) times this in intermediates.
BATCH_BYTES = 2**28
require = ghost_run.require

# The reduced case: three members of the dark/bright design run whose
# replicas fall into eight structure keys of three, and the baseline run,
# whose delays exercise the relaxation pass.
REDUCED = {
    "results/live/2026-10-15T070853.550532Z": (
        "design_b_dark_1_10_4_15",
        "design_b_bright_1_10_4_15",
        "design_d_1_10_4_15_phase_0of8",
    ),
    "results/live/2026-10-15T070847.644554Z": None,
}
# Factors whose freshly built noise models the self-test compares channels
# with: 1e-3 leaves most couplers at the relaxation floor (no depolarizing
# part), 0.5 and 12 are grid points, 1000 reaches the error cap 4/5 and the
# depolarizing cap 16/15.
CONTRACT_FACTORS = (1e-3, 0.5, 12.0, 1000.0)
REFERENCE_FACTORS = (0.5, 1.0, 12.0)
CHANNEL_TOLERANCE = 1e-12
REPRODUCTION_TOLERANCE = 1e-9
PARITY_TOLERANCE = 1e-8
JAX_TOLERANCE = 1e-5


def cz_error(reported: float | None, factor: float) -> float | None:
    """ghost_error_scale.scaled's cz entry: the reported error times factor, stopping at CZ_CAP."""
    return None if reported is None else min(factor * reported, ghost_error_scale.CZ_CAP)


@dataclass
class SnapshotState:
    """What every replica exported under one calibration snapshot shares."""

    snapshot: dict[str, Any]
    noise: Any
    kraus: dict[int, np.ndarray] = field(default_factory=dict)
    cz: dict[tuple[int, ...], tuple[jax_bridge.CzChannel, float | None]] = field(default_factory=dict)
    stacks: dict[tuple[tuple[int, ...], float], np.ndarray] = field(default_factory=dict)
    templates: dict[tuple[Any, ...], jax_bridge.Program] = field(default_factory=dict)
    simulator: Any = None

    @classmethod
    def load(cls, relative: str) -> SnapshotState:
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        return cls(snapshot=snapshot, noise=calibration_snapshot.noise_model(snapshot)[1])

    def channel(self, qargs: tuple[int, ...]) -> tuple[jax_bridge.CzChannel, float | None]:
        if qargs not in self.cz:
            self.cz[qargs] = jax_bridge.cz_channel(self.snapshot, qargs)
        return self.cz[qargs]

    def stack(self, qargs: tuple[int, ...], factor: float) -> np.ndarray:
        if (qargs, factor) not in self.stacks:
            channel, reported = self.channel(qargs)
            self.stacks[(qargs, factor)] = channel.kraus(cz_error(reported, factor))
        return self.stacks[(qargs, factor)]

    def programs(self, replica: QuantumCircuit) -> tuple[tuple[Any, ...], list[jax_bridge.Program]]:
        """The replica's structure key and its program at every CZ factor of the grid."""
        key = jax_bridge.structure_key(replica)
        if key not in self.templates:
            self.templates[key] = jax_bridge.template(replica, self.noise, self.kraus)
        program = jax_bridge.instantiate(self.templates[key], replica)
        return key, [
            jax_bridge.rescale_cz(program, {qargs: self.stack(qargs, c) for _, qargs in program.cz})
            for c in ghost_error_scale.CZ_FACTORS
        ]

    def aer(self) -> Any:
        if self.simulator is None:
            self.simulator = calibration_snapshot.noise_simulator(self.snapshot, "CPU")
        return self.simulator


def aer_probabilities(pairs: list[tuple[QuantumCircuit, jax_bridge.Program]], simulator: Any) -> list[np.ndarray]:
    """Per (circuit, program), Aer's distribution from the density matrix on the program's qubits.

    Each circuit's terminal measurements become save_density_matrix, and
    every circuit goes to Aer in one run call, which parallelizes the
    experiments itself.
    """
    bodies = []
    for circuit, program in pairs:
        body = QuantumCircuit(*circuit.qregs, *circuit.cregs)
        for instruction in circuit.data:
            if instruction.operation.name != "measure":
                body.append(instruction.operation, instruction.qubits, instruction.clbits)
        body.save_density_matrix(qubits=[body.qubits[q] for q in program.physical])
        bodies.append(body)
    result = simulator.run(bodies, shots=1).result()
    return [
        jax_bridge.probabilities(program, np.diag(np.asarray(result.data(k)["density_matrix"])))
        for k, (_, program) in enumerate(pairs)
    ]


def parity_labels(labels: list[str], sample: int | None, seed: int, run_name: str) -> list[str]:
    """A seeded choice of sample labels from the sorted labels; None selects every label.

    The generator is seeded by seed and the run name, so runs draw
    independently and a rerun draws the same labels.
    """
    ordered = sorted(labels)
    if sample is None or sample >= len(ordered):
        return ordered
    rng = np.random.default_rng([seed, int(hashlib.sha256(run_name.encode()).hexdigest()[:8], 16)])
    return sorted(ordered[k] for k in rng.choice(len(ordered), size=sample, replace=False))


Replay = Callable[[list[jax_bridge.Program]], tuple[np.ndarray, set[str]]]


def replay_numpy(programs: list[jax_bridge.Program]) -> tuple[np.ndarray, set[str]]:
    """Register diagonals of programs in complex128 numpy, one evolution each."""
    return np.array([np.real(np.diag(jax_bridge.evolve_numpy(p))) for p in programs]), set()


def jax_replay(device: Any, batch_bytes: int) -> Replay:
    """Batched JAX replay of programs sharing one structure, at most batch_bytes of states per call.

    Every call of one group has the same batch size (the last chunk repeats
    its first program), and every stack is padded to the group's largest
    rank, so each structure compiles once.
    """
    import jax

    evolvers: dict[Any, Any] = {}

    def replay(programs: list[jax_bridge.Program]) -> tuple[np.ndarray, set[str]]:
        n, structure = programs[0].n, programs[0].structure()
        key = (tuple(structure), n)
        if key not in evolvers:
            evolvers[key] = jax_bridge.make_jax_evolver(structure, n)
        stacked = jax_bridge.stack_programs(programs)
        chunk = max(1, min(len(programs), batch_bytes // (8 * 4**n)))
        platforms: set[str] = set()
        parts = []
        for start in range(0, len(programs), chunk):
            count = min(chunk, len(programs) - start)
            rows = list(range(start, start + count)) + [start] * (chunk - count)
            arrays = [jax.device_put(kraus[rows].astype(np.complex64), device) for _, kraus in stacked]
            replayed = evolvers[key](arrays).block_until_ready()
            platforms.update(d.platform for d in replayed.devices())
            parts.append(np.asarray(replayed, dtype=np.float64)[:count])
        return np.concatenate(parts), platforms

    return replay


def replay_all(programs: list[jax_bridge.Program], replay: Replay) -> tuple[list[np.ndarray], set[str]]:
    """Register diagonals of every program in input order, replayed in groups of equal (n, structure)."""
    groups: dict[Any, list[int]] = {}
    for k, program in enumerate(programs):
        groups.setdefault((program.n, tuple(program.structure())), []).append(k)
    out: list[np.ndarray] = [np.zeros(0)] * len(programs)
    platforms: set[str] = set()
    for (n, structure), members in groups.items():
        if not structure:
            # A replica that only measures leaves |0...0> unchanged; readout alone acts.
            diagonals = np.zeros((len(members), 2**n))
            diagonals[:, 0] = 1.0
        else:
            diagonals, seen = replay([programs[k] for k in members])
            platforms |= seen
        for row, k in zip(diagonals, members, strict=True):
            out[k] = row
    return out, platforms


def sweep_run(
    run_name: str,
    replay: Replay,
    index: dict[str, Any],
    states: dict[str, SnapshotState],
    parity_sample: int | None,
    parity_seed: int,
) -> dict[str, Any]:
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    seconds = {"export": 0.0, "parity": 0.0, "replay": 0.0}
    skipped: dict[str, str] = {}
    built: dict[str, tuple[str, QuantumCircuit, list[jax_bridge.Program]]] = {}
    keys: set[tuple[str, tuple[Any, ...]]] = set()
    start = time.perf_counter()
    for m in members:
        relative = execution[m]
        for k, replica in enumerate(prepared["replicas"][m][1]):
            try:
                jax_bridge.structure_key(replica)
            except jax_bridge.UnsupportedCircuit as reason:
                skipped[f"{m}#{k}"] = str(reason)
                continue
            if relative not in states:
                states[relative] = SnapshotState.load(relative)
            key, programs = states[relative].programs(replica)
            keys.add((relative, key))
            built[f"{m}#{k}"] = (relative, replica, programs)
    seconds["export"] += time.perf_counter() - start
    labels = list(built)
    flat = [program for label in labels for program in built[label][2]]
    start = time.perf_counter()
    diagonals, platforms = replay_all(flat, replay)
    seconds["replay"] += time.perf_counter() - start
    factors = len(ghost_error_scale.CZ_FACTORS)
    by_label = {label: diagonals[j * factors : (j + 1) * factors] for j, label in enumerate(labels)}
    base = ghost_error_scale.CZ_FACTORS.index(1.0)
    checked: dict[str, float] = {}
    start = time.perf_counter()
    chosen: dict[str, list[str]] = {}
    for label in parity_labels(labels, parity_sample, parity_seed, run_name):
        chosen.setdefault(built[label][0], []).append(label)
    for relative, group in chosen.items():
        pairs = [(built[label][1], built[label][2][base]) for label in group]
        for label, (_, program), reference in zip(
            group, pairs, aer_probabilities(pairs, states[relative].aer()), strict=True
        ):
            model = jax_bridge.probabilities(program, by_label[label][base])
            checked[label] = float(np.max(np.abs(model - reference)))
    checked = dict(sorted(checked.items()))
    seconds["parity"] += time.perf_counter() - start
    tvd: dict[str, list[list[list[float]]]] = {}
    for label in labels:
        m, position = label.rsplit("#", 1)
        measured = prepared["measured"][m][int(position)]
        tvd.setdefault(m, []).append(
            [
                [
                    round(ghost_run.tv(measured, jax_bridge.probabilities(program, row, readout_scale=r)), 6)
                    for r in ghost_error_scale.READOUT_FACTORS
                ]
                for program, row in zip(built[label][2], by_label[label], strict=True)
            ]
        )
    grid = np.array([cell for rows in tvd.values() for cell in rows]) if tvd else np.zeros((0,))
    means = grid.mean(axis=0).round(6).tolist() if grid.size else None
    parity = max(checked.values(), default=0.0)
    print(json.dumps({"run": run_name, "replicas": len(labels), "parity": parity}), flush=True)
    return {
        "run": run_name,
        "backend": prepared["backend"],
        "execution_snapshot": {m: execution[m] for m in tvd},
        "member_shots": {m: prepared["shots"][m] for m in tvd},
        "skipped_replicas": skipped,
        "replicas": len(labels),
        "structures": len(keys),
        "parity_checked": checked,
        "max_abs_probability_minus_aer": parity,
        "result_platforms": sorted(platforms),
        "seconds": {k: round(v, 2) for k, v in seconds.items()},
        "mean_tvd": means,
        "tvd": tvd,
    }


def parity_count(text: str) -> int | None:
    if text == "all":
        return None
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("--parity-sample takes a positive count or all")
    return value


def versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for name in ("jax", "jaxlib", "libtpu", "numpy", "qiskit", "qiskit-aer", "qiskit-aer-gpu-cu11"):
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out


def superop_distance(stack: np.ndarray, error: Any) -> float:
    return float(np.max(np.abs(SuperOp(Kraus(list(stack))).data - SuperOp(error.to_quantumchannel()).data)))


def programs_equal(left: jax_bridge.Program, right: jax_bridge.Program) -> bool:
    return (
        left.n == right.n
        and left.physical == right.physical
        and left.measured == right.measured
        and left.num_clbits == right.num_clbits
        and left.cz == right.cz
        and left.angles == right.angles
        and left.readout.keys() == right.readout.keys()
        and all(np.array_equal(left.readout[q], right.readout[q]) for q in left.readout)
        and len(left.ops) == len(right.ops)
        and all(
            qa == qb and ka.shape == kb.shape and np.array_equal(ka, kb)
            for (qa, ka), (qb, kb) in zip(left.ops, right.ops, strict=True)
        )
    )


def diagonal(program: jax_bridge.Program) -> np.ndarray:
    return np.real(np.diag(jax_bridge.evolve_numpy(program)))


def self_test(device: str | None) -> dict[str, Any]:
    """The contracts on the REDUCED case; see the module docstring."""
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    timing: dict[str, float] = {}
    clock = time.perf_counter()
    replicas: list[tuple[str, str, QuantumCircuit]] = []
    for run, chosen_members in REDUCED.items():
        prepared = ghost_run.prepare(run, index)
        require("skipped" not in prepared, f"{run}: {prepared.get('skipped')}")
        execution = prepared["execution"]
        for m in prepared["members"]:
            if m in execution and (chosen_members is None or m in chosen_members):
                replicas += [(execution[m], f"{run}:{m}#{k}", r) for k, r in enumerate(prepared["replicas"][m][1])]
    snapshots = sorted({relative for relative, _, _ in replicas})
    require(len(snapshots) == 1, f"the reduced case spans snapshots {snapshots}")
    state = SnapshotState.load(snapshots[0])
    timing["prepare"] = time.perf_counter() - clock

    # Structure: every template instance equals the replica's direct export,
    # export finds every CZ local error, and some key is shared by replicas
    # whose angles differ.
    clock = time.perf_counter()
    groups: dict[tuple[Any, ...], list[QuantumCircuit]] = {}
    restructured: dict[str, list[jax_bridge.Program]] = {}
    cz_errors = state.noise._local_quantum_errors["cz"]
    for _, label, replica in replicas:
        key, programs = state.programs(replica)
        groups.setdefault(key, []).append(replica)
        restructured[label] = programs
        direct = jax_bridge.export(replica, state.noise, state.kraus)
        require(
            programs_equal(jax_bridge.instantiate(state.templates[key], replica), direct),
            f"{label}: template instance differs from the direct export",
        )
        gates = sum(
            1
            for i in replica.data
            if i.operation.name == "cz" and tuple(replica.find_bit(q).index for q in i.qubits) in cz_errors
        )
        require(len(direct.cz) == gates, f"{label}: {len(direct.cz)} CZ slots for {gates} noisy CZ gates")

    def angles(circuit: QuantumCircuit) -> list[float]:
        return [float(p) for i in circuit.data if jax_bridge.angle_gate(i.operation) for p in i.operation.params]

    shared = [k for k, g in groups.items() if len(g) > 1 and any(angles(r) != angles(g[0]) for r in g[1:])]
    require(bool(shared), "no structure key is shared by replicas of differing angles")
    require(any(state.templates[k].cz for k in shared), "no shared structure key carries a CZ local error")
    timing["structure"] = time.perf_counter() - clock

    # CZ channels: the rescaled stack of every coupler equals the channel of
    # a freshly built scaled noise model, and every other channel of that
    # model equals the factor-1 one.
    clock = time.perf_counter()
    models = {
        c: calibration_snapshot.noise_model(ghost_error_scale.scaled(state.snapshot, c, 1.0))[1]
        for c in sorted({*CONTRACT_FACTORS, *REFERENCE_FACTORS})
    }
    base_table = {k: e for k, e in calibration_snapshot.channel_table(state.noise).items() if not k.startswith("cz[")}
    # The couplers the reduced case drives, and every coupler whose reported
    # error already exceeds the 4/5 cap.
    couplers = sorted(
        {qargs for programs in restructured.values() for _, qargs in programs[0].cz}
        | {tuple(e["qargs"]) for e in state.snapshot["instructions"]["cz"] if (e["error"] or 0) > 4 / 5}
    )
    branches = {"zero_depolarizing": 0, "interior": 0, "error_cap": 0, "depolarizing_cap": 0}
    channel_distance = 0.0
    for factor, model in models.items():
        others = {k: e for k, e in calibration_snapshot.channel_table(model).items() if not k.startswith("cz[")}
        require(
            others.keys() == base_table.keys() and all(others[k] == base_table[k] for k in others),
            f"factor {factor}: a channel other than cz differs from the factor-1 model",
        )
        if factor not in CONTRACT_FACTORS:
            continue
        errors = model._local_quantum_errors["cz"]
        for qargs in couplers:
            channel, reported = state.channel(qargs)
            error = cz_error(reported, factor)
            p = channel.depolarizing(error)
            branches["zero_depolarizing" if p == 0 else "depolarizing_cap" if p == 16 / 15 else "interior"] += 1
            branches["error_cap"] += error is not None and error > 4 / 5
            channel_distance = max(channel_distance, superop_distance(state.stack(qargs, factor), errors[qargs]))
    require(channel_distance <= CHANNEL_TOLERANCE, f"rescaled CZ channel differs from Aer's by {channel_distance}")
    require(all(branches.values()), f"the contract factors leave a branch unreached: {branches}")
    timing["cz_channels"] = time.perf_counter() - clock

    # Reproduction: the restructured programs give the distributions of the
    # per-factor exports under the scaled noise models, at every readout factor.
    clock = time.perf_counter()
    reproduction = 0.0
    caches: dict[float, dict[int, np.ndarray]] = {factor: {} for factor in REFERENCE_FACTORS}
    for _, label, replica in replicas:
        for factor in REFERENCE_FACTORS:
            reference = jax_bridge.export(replica, models[factor], caches[factor])
            mine = restructured[label][ghost_error_scale.CZ_FACTORS.index(factor)]
            left, right = diagonal(reference), diagonal(mine)
            for r in ghost_error_scale.READOUT_FACTORS:
                difference = jax_bridge.probabilities(reference, left, readout_scale=r) - jax_bridge.probabilities(
                    mine, right, readout_scale=r
                )
                reproduction = max(reproduction, float(np.max(np.abs(difference))))
    require(reproduction <= REPRODUCTION_TOLERANCE, f"restructured programs differ by {reproduction}")
    timing["reproduction"] = time.perf_counter() - clock

    # Sampled parity against Aer's density matrix, and the sample's determinism.
    clock = time.perf_counter()
    labels = [label for _, label, _ in replicas]
    chosen = parity_labels(labels, PARITY_SAMPLE, PARITY_SEED, "self-test")
    require(chosen == parity_labels(labels, PARITY_SAMPLE, PARITY_SEED, "self-test"), "the parity sample is not seeded")
    require(len(chosen) == PARITY_SAMPLE and chosen == sorted(set(chosen)), "the parity sample has repeats")
    require(parity_labels(labels, None, PARITY_SEED, "self-test") == sorted(labels), "a full parity misses labels")
    by_label = {label: replica for _, label, replica in replicas}
    base = ghost_error_scale.CZ_FACTORS.index(1.0)
    pairs = [(by_label[label], restructured[label][base]) for label in chosen]
    parity = {
        label: float(np.max(np.abs(jax_bridge.probabilities(program, diagonal(program)) - reference)))
        for label, (_, program), reference in zip(chosen, pairs, aer_probabilities(pairs, state.aer()), strict=True)
    }
    require(max(parity.values()) <= PARITY_TOLERANCE, f"parity against Aer {parity}")
    timing["parity"] = time.perf_counter() - clock

    out: dict[str, Any] = {
        "replicas": len(replicas),
        "structure_keys": len(groups),
        "shared_keys_with_differing_angles": len(shared),
        "cz_couplers_compared": len(couplers),
        "cz_branches": branches,
        "max_cz_superop_minus_aer": channel_distance,
        "max_probability_minus_per_factor_export": reproduction,
        "parity": parity,
    }
    if device is not None:
        import jax

        clock = time.perf_counter()
        flat = [program for programs in restructured.values() for program in programs]
        replayed, _ = replay_all(flat, jax_replay(jax.devices(device)[0], BATCH_BYTES))
        distance = max(
            float(np.max(np.abs(a - b))) for a, b in zip(replayed, replay_all(flat, replay_numpy)[0], strict=True)
        )
        require(distance <= JAX_TOLERANCE, f"JAX replay differs from numpy by {distance}")
        out["max_jax_minus_numpy_diagonal"] = distance
        timing["jax"] = time.perf_counter() - clock
    out["seconds"] = {k: round(v, 2) for k, v in timing.items()}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--device", choices=("cpu", "gpu", "tpu"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--parity-sample", type=parity_count, default=PARITY_SAMPLE, help="a count, or all")
    parser.add_argument("--parity-seed", type=int, default=PARITY_SEED)
    parser.add_argument("--batch-bytes", type=int, default=BATCH_BYTES)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"versions": versions(), **self_test(args.device)}, indent=1))
        return 0
    require(args.device is not None and args.out is not None, "a sweep needs --device and --out")
    import jax

    device = jax.devices(args.device)[0]
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": {"requested": args.device, "selected": str(device), "kind": getattr(device, "device_kind", None)},
        "visible_devices": [str(d) for d in jax.devices(args.device)],
        "grid": {"cz": list(ghost_error_scale.CZ_FACTORS), "readout": list(ghost_error_scale.READOUT_FACTORS)},
        "precision": "complex64 storage, Precision.HIGHEST contractions",
        "parity": {"sample": "all" if args.parity_sample is None else args.parity_sample, "seed": args.parity_seed},
        "batch_bytes": args.batch_bytes,
        "versions": versions(),
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    replay = jax_replay(device, args.batch_bytes)
    states: dict[str, SnapshotState] = {}
    for run in runs:
        out["runs"].append(sweep_run(run, replay, index, states, args.parity_sample, args.parity_seed))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
