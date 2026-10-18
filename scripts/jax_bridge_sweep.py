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
label with its largest probability difference. A sampled replica whose
difference exceeds PARITY_TOLERANCE is listed as skipped with the gap, its
distances do not count, and the script exits 1. Replicas with reset,
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
programs reproduce the per-factor exports of the scaled noise models; under
a small batch budget the largest replay group takes several calls whose
padded stacks equal the whole group's rows and whose diagonals equal one
call's; the sampled parity holds in numpy complex128; and parity_failure
passes a gap at PARITY_TOLERANCE and fails one above it.
``--self-test --device cpu`` also replays the restructured programs in JAX,
compares them with numpy, and compares the chunked JAX replay with one call.
``--unit-test`` checks template reuse, CZ Kraus channels and padded replay
chunks on five synthetic two-qubit circuits without archived runs or JAX.

Kaggle. The sweep reads the retention audit, the calibration history and
each audited run's record.json, isa.qpy and collect.json, about 93 MB that
the gororoba-retained-runs dataset carries with the tree's digests; inline
in run.py they exceed what SaveKernel accepts, so the push attaches the
dataset:

    "$PYTHON" scripts/kaggle_run.py push scripts/jax_bridge_sweep.py \\
        --slug gororoba-jax-bridge-sweep-tpu --dataset gororoba-retained-runs \\
        --machine TpuV5E8 --timeout 3600 -- \\
        --device tpu --runs all --parity-sample 2 --out results/kaggle_out/jax-bridge-sweep-tpu.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
import time
from collections.abc import Callable, Iterator
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

import aer_resources  # noqa: E402
import calibration_snapshot  # noqa: E402
import jax_bridge  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "jax-bridge-sweep-v2"
PARITY_SAMPLE = 2
PARITY_SEED = ghost_run.SEED
# complex64 bytes per replay call: each program's density matrix plus its
# padded Kraus stacks, which the host builds per call and transfers to the
# device. The CZ contraction holds about rank (16) times the density-matrix
# bytes in device intermediates.
BATCH_BYTES = 2**28
# A budget under which the self-test's largest replay group takes several
# calls, the last one partial.
CHUNK_TEST_BYTES = 2**20
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
# Largest admitted |p_numpy - p_Aer| over a factor-1 distribution when both
# evolve in complex128, so only the order of floating-point operations
# separates them.
NUMPY_PARITY_TOLERANCE = 1e-8
# Largest admitted difference of a JAX replay from a complex128 reference,
# Aer's factor-1 distribution in the sweep or the numpy diagonal in the
# self-test. The JAX replay stores complex64 (unit roundoff 2^-24, about
# 6e-8) and contracts at Precision.HIGHEST, so its rounding grows with the op
# count from that floor; 1e-5 leaves two orders of magnitude above the
# complex64 floor and still fails an export, ordering or readout defect,
# which moves probabilities by far more.
PARITY_TOLERANCE = 1e-5


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


def parity_failure(gap: float) -> str | None:
    """The skip reason of a replica whose factor-1 distribution differs from Aer's by more than PARITY_TOLERANCE."""
    if gap > PARITY_TOLERANCE:
        return f"factor-1 probabilities differ from Aer by {gap:.3g} > {PARITY_TOLERANCE:g}"
    return None


Replay = Callable[[list[jax_bridge.Program]], tuple[np.ndarray, set[str]]]
# (structure, n, per-operation Kraus stacks with a leading batch axis) to
# the batch's register diagonals and the platforms that computed them.
Evolve = Callable[[list[tuple[int, ...]], int, list[np.ndarray]], tuple[np.ndarray, set[str]]]


def chunk_size(programs: list[jax_bridge.Program], ranks: list[int], batch_bytes: int) -> int:
    """Programs per replay call: as many as batch_bytes holds, at least one and at most all.

    Each program costs one complex64 density matrix plus its complex64 Kraus
    stacks padded to ranks.
    """
    per_program = 8 * 4 ** programs[0].n + sum(
        8 * rank * kraus.shape[1] ** 2 for rank, (_, kraus) in zip(ranks, programs[0].ops, strict=True)
    )
    return max(1, min(len(programs), batch_bytes // per_program))


def replay_chunks(
    programs: list[jax_bridge.Program], batch_bytes: int
) -> Iterator[tuple[list[int], int, list[np.ndarray]]]:
    """Per replay call of programs sharing one structure: its program indices, the count it reports, its Kraus stacks.

    Every call has the same batch size (the last one repeats its first
    program after the count it reports), and every stack is complex64,
    zero-padded to the group's largest rank (jax_bridge.stack_ranks). The
    host holds the padded stacks of one call at a time, so peak host memory
    follows batch_bytes.
    """
    ranks = jax_bridge.stack_ranks(programs)
    chunk = chunk_size(programs, ranks, batch_bytes)
    for start in range(0, len(programs), chunk):
        count = min(chunk, len(programs) - start)
        rows = list(range(start, start + count)) + [start] * (chunk - count)
        stacked = jax_bridge.stack_programs([programs[k] for k in rows], ranks, np.complex64)
        yield rows, count, [kraus for _, kraus in stacked]


def chunked_replay(evolve: Evolve, batch_bytes: int) -> Replay:
    """Replay of programs sharing one structure in replay_chunks calls of evolve, diagonals in program order."""

    def replay(programs: list[jax_bridge.Program]) -> tuple[np.ndarray, set[str]]:
        n, structure = programs[0].n, programs[0].structure()
        platforms: set[str] = set()
        parts = []
        for _, count, arrays in replay_chunks(programs, batch_bytes):
            replayed, seen = evolve(structure, n, arrays)
            platforms |= seen
            parts.append(replayed[:count])
        return np.concatenate(parts), platforms

    return replay


def jax_replay(device: Any, batch_bytes: int) -> Replay:
    """Batched JAX replay on device in replay_chunks calls; each (structure, n) compiles once, its batch size fixed."""
    import jax

    evolvers: dict[Any, Any] = {}

    def evolve(structure: list[tuple[int, ...]], n: int, arrays: list[np.ndarray]) -> tuple[np.ndarray, set[str]]:
        key = (tuple(structure), n)
        if key not in evolvers:
            evolvers[key] = jax_bridge.make_jax_evolver(structure, n)
        replayed = evolvers[key]([jax.device_put(kraus, device) for kraus in arrays]).block_until_ready()
        return np.asarray(replayed, dtype=np.float64), {d.platform for d in replayed.devices()}

    return chunked_replay(evolve, batch_bytes)


def row_diagonal(item: tuple[int, list[tuple[tuple[int, ...], np.ndarray]]]) -> np.ndarray:
    """Register diagonal of one batch row, (n, per-operation Kraus stacks), evolved in complex128 numpy."""
    n, ops = item
    return diagonal(jax_bridge.Program(n=n, physical=list(range(n)), ops=ops))


class RowCollector:
    """An Evolve that records each batch row and returns its index, deferring every row to one later map.

    A chunked replay through it yields, in place of diagonals, the indices
    of the rows its truncation and concatenation keep, so rows of several
    replays evolve in one parallel.ordered_map over row_diagonal.
    """

    def __init__(self) -> None:
        self.rows: list[tuple[int, list[tuple[tuple[int, ...], np.ndarray]]]] = []

    def __call__(
        self, structure: list[tuple[int, ...]], n: int, arrays: list[np.ndarray]
    ) -> tuple[np.ndarray, set[str]]:
        start = len(self.rows)
        self.rows += [
            (n, [(qargs, kraus[b]) for qargs, kraus in zip(structure, arrays, strict=True)])
            for b in range(len(arrays[0]))
        ]
        return np.arange(start, len(self.rows))[:, None], set()


def replay_groups(programs: list[jax_bridge.Program]) -> dict[tuple[int, tuple[tuple[int, ...], ...]], list[int]]:
    """Indices of programs grouped by (n, qargs sequence), in first-appearance order."""
    groups: dict[tuple[int, tuple[tuple[int, ...], ...]], list[int]] = {}
    for k, program in enumerate(programs):
        groups.setdefault((program.n, tuple(program.structure())), []).append(k)
    return groups


def replay_all(programs: list[jax_bridge.Program], replay: Replay) -> tuple[list[np.ndarray], set[str]]:
    """Register diagonals of every program in input order, replayed in groups of equal (n, structure)."""
    out: list[np.ndarray] = [np.zeros(0)] * len(programs)
    platforms: set[str] = set()
    for (n, structure), members in replay_groups(programs).items():
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
    for label, gap in checked.items():
        failure = parity_failure(gap)
        if failure is not None:
            skipped[label] = failure
    seconds["parity"] += time.perf_counter() - start
    tvd: dict[str, list[list[list[float]]]] = {}
    for label in labels:
        if label in skipped:
            continue
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
    names = ("jax", "jaxlib", "libtpu", "numpy", "qiskit", "qiskit-aer")
    for name in (*names, *aer_resources.gpu_aer_distributions()):
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out


def superop_distance(stack: np.ndarray, error: Any) -> float:
    return float(np.max(np.abs(SuperOp(Kraus(list(stack))).data - SuperOp(error.to_quantumchannel()).data)))


def non_cz_channels(noise: Any) -> dict[str, Any]:
    """calibration_snapshot.channel_table of noise without its cz entries."""
    return {k: e for k, e in calibration_snapshot.channel_table(noise).items() if not k.startswith("cz[")}


@dataclass
class ScaledModelCheck:
    """Builds snapshot's Aer noise model at one CZ factor (readout factor 1, ghost_error_scale.scaled) and checks it.

    Returns whether every non-CZ channel equals base's, the model itself at
    a factor in keep, and its CZ errors on couplers at a factor in contract.
    """

    snapshot: dict[str, Any]
    base: dict[str, Any]
    couplers: list[tuple[int, ...]]
    keep: tuple[float, ...]
    contract: tuple[float, ...]

    def __call__(self, factor: float) -> tuple[bool, Any, dict[tuple[int, ...], Any]]:
        model = calibration_snapshot.noise_model(ghost_error_scale.scaled(self.snapshot, factor, 1.0))[1]
        others = non_cz_channels(model)
        equal = others.keys() == self.base.keys() and all(others[k] == self.base[k] for k in others)
        errors = model._local_quantum_errors["cz"]
        cz = {qargs: errors[qargs] for qargs in self.couplers} if factor in self.contract else {}
        return equal, model if factor in self.keep else None, cz


def stack_distance(item: tuple[np.ndarray, Any]) -> float:
    """superop_distance of one (rescaled CZ stack, Aer QuantumError) pair."""
    return superop_distance(*item)


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


def unit_test() -> dict[str, Any]:
    """Synthetic two-qubit template, CZ-channel and padded chunk contracts without archives or JAX."""
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

    channel = jax_bridge.CzChannel.build([(None, None), (None, None)], None)
    require(cz_error(None, 12.0) is None, "an absent CZ error acquires a scaled value")
    require(cz_error(0.03, 1000.0) == ghost_error_scale.CZ_CAP, "the CZ factor exceeds its recorded cap")
    require(abs(channel.depolarizing(0.03) - 0.04) <= CHANNEL_TOLERANCE, "the no-relaxation CZ infidelity is wrong")

    def noise(error: float | None) -> Any:
        model = NoiseModel()
        model.add_quantum_error(depolarizing_error(0.02, 1), "h", [0])
        model.add_quantum_error(depolarizing_error(channel.depolarizing(error), 2), "cz", [0, 1])
        model.add_readout_error(ReadoutError([[0.97, 0.03], [0.04, 0.96]]), [0])
        return model

    circuits = []
    factors = (0.0, 0.1, 0.5, 12.0, 1000.0)
    for position in range(len(factors)):
        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.h(1)
        circuit.rz(0.13 * position, 0)
        circuit.cz(0, 1)
        circuit.h(0)
        circuit.measure([0, 1], [1, 0])
        circuits.append(circuit)
    base = noise(0.03)
    cache: dict[int, np.ndarray] = {}
    skeleton = jax_bridge.template(circuits[0], base, cache)
    require(bool(skeleton.angles) and bool(skeleton.cz), "the synthetic template lacks angle or noisy CZ slots")
    programs = []
    channel_distance = 0.0
    reproduction = 0.0
    for circuit, factor in zip(circuits, factors, strict=True):
        require(
            jax_bridge.structure_key(circuit) == jax_bridge.structure_key(circuits[0]),
            "angle changes alter a synthetic structure key",
        )
        instance = jax_bridge.instantiate(skeleton, circuit)
        require(programs_equal(instance, jax_bridge.export(circuit, base, cache)), "template reuse changes the export")
        error = cz_error(0.03, factor)
        stack = channel.kraus(error)
        reference_noise = noise(error)
        expected_error = depolarizing_error(channel.depolarizing(error), 2)
        channel_distance = max(channel_distance, superop_distance(stack, expected_error))
        scaled = jax_bridge.rescale_cz(instance, {(0, 1): stack})
        direct = jax_bridge.export(circuit, reference_noise)
        left, right = diagonal(scaled), diagonal(direct)
        for readout_scale in (0.0, 1.0, 12.0):
            reproduction = max(
                reproduction,
                float(
                    np.max(
                        np.abs(
                            jax_bridge.probabilities(scaled, left, readout_scale=readout_scale)
                            - jax_bridge.probabilities(direct, right, readout_scale=readout_scale)
                        )
                    )
                ),
            )
        programs.append(scaled)
    require(channel_distance <= CHANNEL_TOLERANCE, f"synthetic CZ Kraus channel differs by {channel_distance}")
    require(reproduction <= REPRODUCTION_TOLERANCE, f"synthetic rescaled exports differ by {reproduction}")
    require(len({program.ops[program.cz[0][0]][1].shape[0] for program in programs}) > 1, "Kraus ranks never vary")

    ranks = jax_bridge.stack_ranks(programs)
    per_program = 8 * 4 ** programs[0].n + sum(
        8 * rank * kraus.shape[1] ** 2 for rank, (_, kraus) in zip(ranks, programs[0].ops, strict=True)
    )
    budget = 2 * per_program
    require(chunk_size(programs, ranks, budget) == 2, "the synthetic budget fails to make two-program chunks")
    whole = [kraus.astype(np.complex64) for _, kraus in jax_bridge.stack_programs(programs)]
    chunks = list(replay_chunks(programs, budget))
    require([count for _, count, _ in chunks] == [2, 2, 1], "the synthetic final chunk is not partial")
    for rows, _, arrays in chunks:
        require(
            all(np.array_equal(part, full[rows]) for part, full in zip(arrays, whole, strict=True)),
            "chunk padding changes the synthetic Kraus rows",
        )
    collector = RowCollector()
    several = chunked_replay(collector, budget)(programs)[0][:, 0]
    single = chunked_replay(collector, len(programs) * per_program)(programs)[0][:, 0]
    diagonals = np.array(parallel.ordered_map(row_diagonal, collector.rows))
    require(np.array_equal(diagonals[several], diagonals[single]), "synthetic chunked diagonals differ from one call")
    require(parity_failure(PARITY_TOLERANCE) is None, "the parity boundary fails")
    require(parity_failure(2 * PARITY_TOLERANCE) is not None, "a parity violation passes")
    return {
        "programs": len(programs),
        "chunks": len(chunks),
        "max_channel_gap": channel_distance,
        "max_export_gap": reproduction,
    }


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
    # Each factor's build and comparison runs for seconds, so the six factors
    # map with min_items=1. The models of REFERENCE_FACTORS return to this
    # process, where the reproduction's exports key their Kraus caches by
    # object id; the (coupler, factor) superop distances map as one list.
    clock = time.perf_counter()
    # The couplers the reduced case drives, and every coupler whose reported
    # error already exceeds the 4/5 cap.
    couplers = sorted(
        {qargs for programs in restructured.values() for _, qargs in programs[0].cz}
        | {tuple(e["qargs"]) for e in state.snapshot["instructions"]["cz"] if (e["error"] or 0) > 4 / 5}
    )
    factors = sorted({*CONTRACT_FACTORS, *REFERENCE_FACTORS})
    check = ScaledModelCheck(
        state.snapshot, non_cz_channels(state.noise), couplers, REFERENCE_FACTORS, CONTRACT_FACTORS
    )
    built = dict(zip(factors, parallel.ordered_map(check, factors, min_items=1), strict=True))
    models = {factor: model for factor, (_, model, _) in built.items() if model is not None}
    branches = {"zero_depolarizing": 0, "interior": 0, "error_cap": 0, "depolarizing_cap": 0}
    checks: list[tuple[np.ndarray, Any]] = []
    for factor, (equal, _, errors) in built.items():
        require(equal, f"factor {factor}: a channel other than cz differs from the factor-1 model")
        if factor not in CONTRACT_FACTORS:
            continue
        for qargs in couplers:
            channel, reported = state.channel(qargs)
            error = cz_error(reported, factor)
            p = channel.depolarizing(error)
            branches["zero_depolarizing" if p == 0 else "depolarizing_cap" if p == 16 / 15 else "interior"] += 1
            branches["error_cap"] += error is not None and error > 4 / 5
            checks.append((state.stack(qargs, factor), errors[qargs]))
    channel_distance = max([0.0, *parallel.ordered_map(stack_distance, checks)])
    require(channel_distance <= CHANNEL_TOLERANCE, f"rescaled CZ channel differs from Aer's by {channel_distance}")
    require(all(branches.values()), f"the contract factors leave a branch unreached: {branches}")
    timing["cz_channels"] = time.perf_counter() - clock

    # Reproduction: the restructured programs give the distributions of the
    # per-factor exports under the scaled noise models, at every readout factor.
    # The exports run in-process in loop order, since each factor's Kraus
    # cache keys by object id; their evolutions run as one map.
    clock = time.perf_counter()
    reproduction = 0.0
    caches: dict[float, dict[int, np.ndarray]] = {factor: {} for factor in REFERENCE_FACTORS}
    cases = [
        (
            (label, factor),
            jax_bridge.export(replica, models[factor], caches[factor]),
            restructured[label][ghost_error_scale.CZ_FACTORS.index(factor)],
        )
        for _, label, replica in replicas
        for factor in REFERENCE_FACTORS
    ]
    evolved = parallel.ordered_map(diagonal, [program for _, reference, mine in cases for program in (reference, mine)])
    restructured_diagonals: dict[tuple[str, float], np.ndarray] = {}
    for k, (case, reference, mine) in enumerate(cases):
        left, right = evolved[2 * k], evolved[2 * k + 1]
        restructured_diagonals[case] = right
        for r in ghost_error_scale.READOUT_FACTORS:
            difference = jax_bridge.probabilities(reference, left, readout_scale=r) - jax_bridge.probabilities(
                mine, right, readout_scale=r
            )
            reproduction = max(reproduction, float(np.max(np.abs(difference))))
    require(reproduction <= REPRODUCTION_TOLERANCE, f"restructured programs differ by {reproduction}")
    timing["reproduction"] = time.perf_counter() - clock

    # Chunking: under CHUNK_TEST_BYTES the largest replay group takes several
    # calls, the last one partial. Each call's stacks equal the whole group's
    # complex64 stack at the call's rows, and the chunked diagonals equal the
    # one-call replay's.
    clock = time.perf_counter()
    flat = [program for programs in restructured.values() for program in programs]
    members = max((m for (_, structure), m in replay_groups(flat).items() if structure), key=len)
    group = [flat[k] for k in members]
    ranks = jax_bridge.stack_ranks(group)
    chunk = chunk_size(group, ranks, CHUNK_TEST_BYTES)
    require(
        chunk < len(group) and len(group) % chunk != 0 and chunk_size(group, ranks, BATCH_BYTES) == len(group),
        f"{len(group)} programs take {chunk} and {chunk_size(group, ranks, BATCH_BYTES)} per call",
    )
    whole = [kraus.astype(np.complex64) for _, kraus in jax_bridge.stack_programs(group)]
    calls = 0
    for rows, _, arrays in replay_chunks(group, CHUNK_TEST_BYTES):
        calls += 1
        require(
            all(a.dtype == np.complex64 and np.array_equal(a, w[rows]) for a, w in zip(arrays, whole, strict=True)),
            f"call {calls}: padded stacks differ from the whole group's rows {rows}",
        )
    require(calls == -(-len(group) // chunk), f"{calls} calls for {len(group)} programs at {chunk} per call")
    collector = RowCollector()
    several_rows = chunked_replay(collector, CHUNK_TEST_BYTES)(group)[0][:, 0]
    single_rows = chunked_replay(collector, BATCH_BYTES)(group)[0][:, 0]
    row_diagonals = np.array(parallel.ordered_map(row_diagonal, collector.rows))
    require(np.array_equal(row_diagonals[several_rows], row_diagonals[single_rows]), "chunked diagonals differ")
    timing["chunking"] = time.perf_counter() - clock

    # Sampled parity against Aer's density matrix, and the sample's
    # determinism. A sampled program is the restructured factor-1 program
    # whose diagonal the reproduction map evolved.
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
        label: float(
            np.max(np.abs(jax_bridge.probabilities(program, restructured_diagonals[(label, 1.0)]) - reference))
        )
        for label, (_, program), reference in zip(chosen, pairs, aer_probabilities(pairs, state.aer()), strict=True)
    }
    require(max(parity.values()) <= NUMPY_PARITY_TOLERANCE, f"parity against Aer {parity}")
    require(parity_failure(PARITY_TOLERANCE) is None, "a gap at the tolerance passes")
    require(parity_failure(2 * PARITY_TOLERANCE) is not None, "a gap above the tolerance fails")
    timing["parity"] = time.perf_counter() - clock

    out: dict[str, Any] = {
        "replicas": len(replicas),
        "structure_keys": len(groups),
        "shared_keys_with_differing_angles": len(shared),
        "cz_couplers_compared": len(couplers),
        "cz_branches": branches,
        "max_cz_superop_minus_aer": channel_distance,
        "max_probability_minus_per_factor_export": reproduction,
        "chunking": {"programs": len(group), "per_call": chunk, "calls": calls},
        "parity": parity,
    }
    if device is not None:
        import jax

        clock = time.perf_counter()
        replayed, _ = replay_all(flat, jax_replay(jax.devices(device)[0], BATCH_BYTES))
        references = parallel.ordered_map(diagonal, flat)
        distance = max(float(np.max(np.abs(a - b))) for a, b in zip(replayed, references, strict=True))
        require(distance <= PARITY_TOLERANCE, f"JAX replay differs from numpy by {distance}")
        out["max_jax_minus_numpy_diagonal"] = distance
        chunked = jax_replay(jax.devices(device)[0], CHUNK_TEST_BYTES)(group)[0]
        chunk_distance = float(np.max(np.abs(chunked - np.array([replayed[k] for k in members]))))
        require(chunk_distance <= PARITY_TOLERANCE, f"chunked JAX replay differs from one call by {chunk_distance}")
        out["max_jax_chunked_minus_one_call"] = chunk_distance
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
    parser.add_argument("--unit-test", action="store_true", help="check synthetic templates, channels and chunks")
    args = parser.parse_args()
    if args.unit_test:
        print(json.dumps(unit_test(), indent=1))
        return 0
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
        "parity_tolerance": PARITY_TOLERANCE,
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
    failed = [run["run"] for run in out["runs"] if run.get("max_abs_probability_minus_aer", 0.0) > PARITY_TOLERANCE]
    if failed:
        print(f"Aer parity above {PARITY_TOLERANCE:g} in {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
