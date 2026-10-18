"""Ghost error-scale sweep: per run, the CZ and readout error factors that bring Aer closest to the hardware.

Each retained run's members are rebuilt and sampled as scripts/ghost_run.py
does (prepare, sample, each member at its pub_shots tier, under the
calibration snapshot in force when its PUB began). The snapshot is first
scaled: every cz error by a factor c and every readout flip probability
(e01, e10) by a factor r. A scaled CZ error stops at 1 and a scaled flip at
0.5, where the readout channel starts to invert the bit (a reported flip
above 0.5 keeps its value). NoiseModel.from_backend then
builds each CZ channel as thermal relaxation over the gate duration plus the
depolarizing part that brings its error to the scaled value, so c scales the
modeled CZ infidelity until the depolarizing part reaches zero at the
relaxation floor. Single-qubit gate errors, T1 and T2 keep their reported
values. Every grid point samples with the same seed, so shot noise is common
along the grid and differences between points come from the model.

The output keeps every replica's TV distance to its hardware distribution at
every grid point. Per snapshot it records the run's couplers and qubits,
their mean reported CZ and readout error, the modeled mean CZ infidelity at
each c (which shows the relaxation floor), and how many of them each factor
caps. At each run's minimizing point a second draw under an independent
seed gives the resample floor, the TV distance between two model draws at
the members' shots, which the hardware distance reaches only when the model
is exact.

``--report FILE...`` gives, per run, the mean distance at every grid point, the
minimizing (c, r), its paired change from (1, 1) with the standard error
clustered by executed PUB, and a bootstrap over PUBs of the minimizing
factors. Two reference ends bound the reading: the resample floor, and the
TV distance from each hardware distribution to the uniform one, which every
model approaches as its errors grow without bound. ``--check FILE...`` requires the files (one per kernel) to hold
every audited run exactly once, rebuilds
each run's members, shots, execution snapshots, grid, coverage, means and
cap counts from the archived inputs and the retained distances, requires the
(1, 1) means to agree with docs/evidence/ghost_runs/result.json, and reruns
the ``--runs`` subset on the CPU at (1, 1), its minimizing point and the
grid's top corner, each within five standard errors.

``--regenerate-diagnostics IN --out OUT`` rewrites a retained part's
calibration-derived fields (each run's per-snapshot diagnostics and the
``scaled`` block) from the archived calibration and circuits, keeps every
other field, and writes OUT in the sweep's own serialization.
``--provenance PART KERNEL_OUTPUT...`` passes when PART is byte for byte the
regeneration of the kernel outputs merged in argument order, so PART carries
the kernels' simulation fields unchanged and calibration-derived fields equal
to a fresh recomputation; otherwise it names the first differing path.
Several outputs are shard kernels, one or more runs each, whose headers
(every field but ``runs``) agree; their runs concatenate into one part.
A snapshot group whose circuits apply no CZ samples only the c = 1 point
of each readout factor and repeats its distances along c; --check requires
that repetition, and ``--self-test-cz-free [RUN...]`` shows that one seed
gives such a group identical counts at every c while a CZ group's counts
change. A member ghost_run draws from its exact law (``member_law``) takes
that law under each scaled snapshot.
``--self-test`` drives that comparison on synthetic parts with the
regeneration replaced by the identity: shards in order pass, and swapped or
missing shards, a differing header, a reserialized part and an empty kernel
list each fail naming the first differing path.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import average_gate_fidelity  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

GHOST_RESULT = ROOT / "docs/evidence/ghost_runs/result.json"
CZ_FACTORS = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0)
READOUT_FACTORS = (0.5, 1.0, 1.5, 2.0, 3.0)
SEED = ghost_run.SEED
BOOTSTRAP = 2000
SCHEMA = "ghost-error-scale-v1"
CZ_CAP = 1.0
FLIP_CAP = 0.5
require = ghost_run.require


def scaled(snapshot: dict[str, Any], cz: float, readout: float) -> dict[str, Any]:
    """The snapshot with every cz error times cz and every readout flip times readout, under the caps."""
    out = copy.deepcopy(snapshot)
    for entry in out["instructions"]["cz"]:
        if entry["error"] is not None:
            entry["error"] = min(cz * entry["error"], CZ_CAP)
    for qubit in out["qubits"]:
        qubit["e01"] = flip(qubit["e01"], readout)
        qubit["e10"] = flip(qubit["e10"], readout)
    return out


def flip(value: float, factor: float) -> float:
    """A readout flip times factor, stopping at FLIP_CAP; a reported flip above the cap keeps its value."""
    return min(factor * value, max(value, FLIP_CAP))


def footprint(circuits: list[QuantumCircuit]) -> tuple[set[int], set[frozenset[int]]]:
    """Physical qubits and CZ couplers the circuits act on; ISA circuits index qubits physically.

    A control-flow instruction counts its declared qubits, and every block
    it holds contributes its own instructions on the outer physical qubits,
    so a CZ inside an if_else body is a coupler of the circuit.
    """
    qubits: set[int] = set()
    couplers: set[frozenset[int]] = set()

    def walk(circuit: QuantumCircuit, physical: list[int]) -> None:
        for instruction in circuit.data:
            if instruction.operation.name == "barrier":
                continue
            indices = [physical[circuit.find_bit(q).index] for q in instruction.qubits]
            qubits.update(indices)
            if instruction.operation.name == "cz":
                couplers.add(frozenset(indices))
            for block in getattr(instruction.operation, "blocks", ()):
                if block is not None:
                    walk(block, indices)

    for circuit in circuits:
        walk(circuit, list(range(circuit.num_qubits)))
    return qubits, couplers


def scaled_block() -> dict[str, Any]:
    """The part header's record of which snapshot fields the grid scales and their caps."""
    return {
        "cz": "instructions.cz[].error",
        "readout": "qubits[].e01 and qubits[].e10",
        "cz_cap": CZ_CAP,
        "readout_cap": FLIP_CAP,
    }


def write_part(path: Path, part: dict[str, Any]) -> None:
    path.write_text(serialize(part), encoding="utf-8")


def serialize(part: dict[str, Any]) -> str:
    return json.dumps(part) + "\n"


def diagnostics(snapshot: dict[str, Any], circuits: list[QuantumCircuit], infidelity: bool) -> dict[str, Any]:
    """Reported means, cap counts per factor and, with infidelity, the modeled mean CZ infidelity per factor."""
    qubits, couplers = footprint(circuits)
    # The Target lists every coupler in both orientations; a footprint edge
    # counts once, under its first listed orientation.
    entries = []
    seen: set[frozenset[int]] = set()
    for e in snapshot["instructions"]["cz"]:
        edge = frozenset(e["qargs"])
        if edge in couplers and edge not in seen and e["error"] is not None:
            seen.add(edge)
            entries.append(e)
    flips = [v for q in sorted(qubits) for v in (snapshot["qubits"][q]["e01"], snapshot["qubits"][q]["e10"])]
    # NoiseModel.from_backend builds each CZ channel from that instruction's
    # own error and duration and its qubits' T1 and T2, so the snapshot
    # restricted to the footprint (renumbered in ascending physical order)
    # with its cz rows alone yields the same CZ channels and skips building
    # every other instruction's channel on the full device.
    active = sorted(qubits)
    position = {q: k for k, q in enumerate(active)}
    footprint_view = snapshot_laws.restrict(snapshot, active)
    reduced = dict(footprint_view, instructions={"cz": footprint_view["instructions"]["cz"]})
    cz_rows = []
    for factor in CZ_FACTORS:
        row: dict[str, Any] = {"factor": factor, "capped": sum(factor * e["error"] > CZ_CAP for e in entries)}
        if infidelity:
            row["model_infidelity_mean"] = None
            if entries:
                channels = calibration_snapshot.channel_table(
                    calibration_snapshot.noise_model(scaled(reduced, factor, 1.0))[1]
                )
                row["model_infidelity_mean"] = round(
                    float(
                        np.mean(
                            [
                                1
                                - average_gate_fidelity(
                                    channels[f"cz{[position[q] for q in e['qargs']]}"].to_quantumchannel()
                                )
                                for e in entries
                            ]
                        )
                    ),
                    9,
                )
        cz_rows.append(row)
    return {
        "qubits": len(qubits),
        "couplers": len(entries),
        "reported_cz_error_mean": round(float(np.mean([e["error"] for e in entries])), 9) if entries else None,
        "reported_readout_error_mean": round(
            float(np.mean([(snapshot["qubits"][q]["e01"] + snapshot["qubits"][q]["e10"]) / 2 for q in sorted(qubits)])),
            9,
        ),
        "cz": cz_rows,
        "readout": [{"factor": f, "capped": sum(flip(e, f) < f * e for e in flips)} for f in READOUT_FACTORS],
    }


def snapshot_diagnostics(prepared: dict[str, Any], members: list[str]) -> dict[str, dict[str, Any]]:
    """Per execution snapshot, in sorted path order: its member count and diagnostics() with the modeled infidelity."""
    execution = prepared["execution"]
    entries = {}
    for relative in sorted(set(execution.values())):
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        circuits = [replica for m in chosen for replica in prepared["replicas"][m][1]]
        entries[relative] = {"members": len(chosen), **diagnostics(snapshot, circuits, infidelity=True)}
    return entries


class DiagnosticsBuilder:
    """A run's snapshot_diagnostics() from its archived inputs, or None for a skipped run; picklable for the pool."""

    def __init__(self, index: dict[str, Any]) -> None:
        self.index = index

    def __call__(self, run_name: str) -> dict[str, dict[str, Any]] | None:
        prepared = ghost_run.prepare(run_name, self.index)
        if "skipped" in prepared:
            return None
        return snapshot_diagnostics(prepared, [m for m in prepared["members"] if m in prepared["execution"]])


def regenerate(part: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    """The part with its scaled block and every run's snapshots recomputed; every other field is kept in place."""
    out = copy.deepcopy(part)
    out["scaled"] = scaled_block()
    names = [run["run"] for run in out["runs"]]
    for run, entries in zip(
        out["runs"], parallel.ordered_map(DiagnosticsBuilder(index), names, min_items=2), strict=True
    ):
        if entries is None:
            require("skipped" in run, f"{run['run']}: inputs are skipped although the part holds a sweep")
            continue
        require("skipped" not in run, f"{run['run']}: marked skipped although its inputs rebuild")
        run["snapshots"] = entries
    return out


def first_difference(a: Any, b: Any, path: str = "") -> str | None:
    """The first JSON path, in document order, where a and b differ in value, type or key order."""
    if type(a) is not type(b):
        return path or "/"
    if isinstance(a, dict):
        if list(a) != list(b):
            for key in list(a) + list(b):
                if key not in a or key not in b or list(a).index(key) != list(b).index(key):
                    return f"{path}/{key}"
        for key in a:
            found = first_difference(a[key], b[key], f"{path}/{key}")
            if found is not None:
                return found
        return None
    if isinstance(a, list):
        for k, (x, y) in enumerate(zip(a, b, strict=False)):
            found = first_difference(x, y, f"{path}[{k}]")
            if found is not None:
                return found
        return f"{path}[{min(len(a), len(b))}]" if len(a) != len(b) else None
    return None if a == b else (path or "/")


def merge_shards(shards: list[dict[str, Any]], names: list[str]) -> dict[str, Any]:
    """One part from shard parts with equal headers, their runs concatenated in shard order."""
    merged = dict(shards[0])
    for shard, name in zip(shards[1:], names[1:], strict=True):
        header = {key: value for key, value in shard.items() if key != "runs"}
        expected = {key: value for key, value in merged.items() if key != "runs"}
        where = first_difference(header, expected)
        require(where is None, f"{name}: header differs from {names[0]} at {where}")
    merged["runs"] = [run for shard in shards for run in shard["runs"]]
    return merged


def provenance(
    part_path: Path,
    kernel_paths: list[Path],
    index: dict[str, Any],
    rebuild: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] = regenerate,
) -> None:
    """Require part_path's bytes to equal rebuild() of the kernel parts merged in order."""
    require(bool(kernel_paths), "--provenance needs PART and at least one KERNEL_OUTPUT")
    text = part_path.read_text(encoding="utf-8")
    names = [str(path) for path in kernel_paths]
    shards = [json.loads(path.read_text(encoding="utf-8")) for path in kernel_paths]
    expected = rebuild(merge_shards(shards, names), index)
    source = " + ".join(names)
    if text != serialize(expected):
        where = first_difference(json.loads(text), expected)
        raise SystemExit(
            f"{part_path}: differs from the regeneration of {source} at {where}"
            if where is not None
            else f"{part_path}: equal in value to the regeneration of {source} but serialized differently"
        )
    print(f"{part_path}: the regeneration of {source}")


def expect_failure(action: Callable[[], Any], fragment: str) -> None:
    try:
        action()
    except SystemExit as reason:
        require(fragment in str(reason), f"self-test: failure {reason!s} lacks {fragment!r}")
        return
    raise SystemExit(f"self-test: expected a failure naming {fragment!r}")


def self_test() -> None:
    """--provenance on synthetic shards, with the identity in place of the archived-input regeneration."""
    header = {"schema": SCHEMA, "device": "CPU", "max_qubits": 14, "seed": SEED, "grid": [[1.0, 1.0]]}
    runs = [{"run": f"results/live/run-{k}", "tvd": [0.01 * k]} for k in range(3)]

    def identity(part: dict[str, Any], _index: dict[str, Any]) -> dict[str, Any]:
        return part

    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        part = root / "part.json"
        part.write_text(serialize({**header, "runs": runs}), encoding="utf-8")
        shards = []
        for k, run in enumerate(runs):
            shards.append(root / f"shard-{k}.json")
            shards[-1].write_text(serialize({**header, "runs": [run]}), encoding="utf-8")
        whole = root / "whole.json"
        whole.write_text(serialize({**header, "runs": runs}), encoding="utf-8")
        foreign = root / "foreign.json"
        foreign.write_text(serialize({**header, "device": "GPU", "runs": [runs[2]]}), encoding="utf-8")
        spaced = root / "spaced.json"
        spaced.write_text(json.dumps({**header, "runs": runs}, indent=1) + "\n", encoding="utf-8")

        provenance(part, shards, {}, identity)
        provenance(part, [whole], {}, identity)
        expect_failure(lambda: provenance(part, [shards[1], shards[0], shards[2]], {}, identity), "at /runs[0]/run")
        expect_failure(lambda: provenance(part, shards[:2], {}, identity), "at /runs[2]")
        expect_failure(lambda: provenance(part, [*shards, shards[2]], {}, identity), "at /runs[3]")
        expect_failure(lambda: provenance(part, [*shards[:2], foreign], {}, identity), "header differs from")
        expect_failure(lambda: provenance(spaced, shards, {}, identity), "serialized differently")
        expect_failure(lambda: provenance(part, [], {}, identity), "at least one KERNEL_OUTPUT")
    guarded = QuantumCircuit(3, 1)
    guarded.measure(0, 0)
    with guarded.if_test((guarded.clbits[0], 1)):
        guarded.cz(1, 2)
    require(not cz_free([guarded]), "self-test: a CZ inside an if_else body reads CZ-free")
    require(footprint([guarded])[1] == {frozenset((1, 2))}, "self-test: the body CZ maps to its outer qubits")
    full = full_grid()
    picked = sampled_points(full, True)
    require(
        sorted(set(picked.values())) == [full.index((1.0, r)) for r in READOUT_FACTORS],
        "self-test: a CZ-free full grid samples other than its c = 1 points",
    )
    sub = [(1.0, 1.0), (0.5, 1.0), (12.0, 3.0)]
    require(sampled_points(sub, True) == {0: 0, 1: 0, 2: 2}, "self-test: a sub-grid without c = 1 at r = 3")
    require(sampled_points(sub, False) == {0: 0, 1: 1, 2: 2}, "self-test: a CZ group skips a point")
    print("ghost error-scale self-test: shard provenance merges in order and names every mismatch")


CZ_FREE_RUN = "results/live/2026-10-15T070847.644554Z"
CZ_CONTROL_RUN = "results/live/2026-10-15T070853.550532Z"


class CountsAt:
    """A GridSampler's counts at one point under SEED; picklable for the process pool."""

    def __init__(self, sampler: GridSampler) -> None:
        self.sampler = sampler

    def __call__(self, point: tuple[float, float]) -> list[dict[str, int]]:
        return self.sampler.counts(point, (SEED,))[0]


def group_sampler(run_name: str, index: dict[str, Any], members: int | None = None) -> GridSampler:
    """The GridSampler sweep_run builds for the run's first execution snapshot group, or its first members."""
    prepared = ghost_run.prepare(run_name, index)
    execution = prepared["execution"]
    relative = sorted(set(execution.values()))[0]
    chosen = [m for m in prepared["members"] if execution.get(m) == relative][:members]
    snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    group = {m: prepared["replicas"][m][1] for m in chosen}
    laws = {m: prepared["laws"][m] for m in chosen}
    return GridSampler(snapshot, "CPU", 1, chosen, group, prepared["measured"], prepared["shots"], laws)


def cz_free_self_test(run_name: str, control_name: str, index: dict[str, Any]) -> None:
    """Under one seed a CZ-free group's counts repeat at every c of the grid, and a CZ group's counts change.

    sweep_run samples a CZ-free group at c = 1 alone on this ground: scaled()
    changes only cz channels, which a circuit without a CZ never applies.
    """
    sampler = group_sampler(run_name, index)
    require(cz_free(sampler.circuits), f"{run_name}: the group applies a CZ")
    points = [(c, 1.0) for c in CZ_FACTORS]
    counts = parallel.ordered_map(CountsAt(sampler), points, min_items=2)
    differing = [points[j] for j, row in enumerate(counts) if row != counts[CZ_FACTORS.index(1.0)]]
    require(not differing, f"{run_name}: CZ-free counts differ from c = 1 at {differing}")
    control = group_sampler(control_name, index, members=1)
    require(not cz_free(control.circuits), f"{control_name}: the control group applies no CZ")
    low, high = parallel.ordered_map(CountsAt(control), [(1.0, 1.0), (CZ_FACTORS[-1], 1.0)], min_items=2)
    require(low != high, f"{control_name}: CZ counts repeat at c = {CZ_FACTORS[-1]}, so the test cannot fail")
    print(
        f"ghost error-scale CZ-free self-test: {len(sampler.circuits)} circuits repeat their counts at "
        f"{len(CZ_FACTORS)} CZ factors; the CZ control changes"
    )


def grid_means(points: list[dict[str, Any]], members: list[str]) -> list[float]:
    return [round(float(np.mean([v for m in members for v in p["tvd"][m]])), 6) for p in points]


def aer_threads(items: int) -> int:
    """Aer threads per pooled point, so the pool's workers share the CPUs without oversubscribing them."""
    return max(1, parallel.available_cpus() // max(1, min(parallel.workers(), items)))


class GridSampler:
    """One snapshot group's TV distances at a (c, r) point; picklable, so the process pool maps it over the grid.

    Aer counts do not depend on its thread count under a fixed seed, so the
    pooled grid equals the serial one. A member ghost_run.member_laws draws
    from its exact law takes that law under the scaled snapshot
    (ghost_run.exact_law), and the Aer simulator is built only for a group
    holding an Aer-sampled member.
    """

    def __init__(
        self,
        snapshot: dict[str, Any],
        device: str,
        threads: int,
        chosen: list[str],
        replicas: dict[str, list[QuantumCircuit]],
        measured: dict[str, list[np.ndarray]],
        shots: dict[str, int],
        laws: dict[str, str] | None = None,
    ) -> None:
        self.snapshot, self.device, self.threads = snapshot, device, threads
        self.chosen, self.replicas = chosen, replicas
        self.measured = {m: measured[m] for m in chosen}
        self.circuits = [r for m in chosen for r in replicas[m]]
        self.shots = [shots[m] for m in chosen for _ in replicas[m]]
        laws = laws or {}
        self.exact = [laws.get(m) == ghost_run.EXACT_MULTINOMIAL for m in chosen for _ in replicas[m]]

    def counts(self, point: tuple[float, float], seeds: tuple[int, ...]) -> list[list[dict[str, int]]]:
        """Every circuit's counts at the point, one draw per seed."""
        model = scaled(self.snapshot, *point)
        simulator = None
        if not all(self.exact):
            simulator = calibration_snapshot.noise_simulator(model, self.device)
            simulator.set_options(
                max_parallel_threads=self.threads, max_parallel_experiments=ghost_run.PARALLEL_EXPERIMENTS
            )
        exact = {k: ghost_run.exact_law(model, c) for k, c in enumerate(self.circuits) if self.exact[k]}
        return [ghost_run.sample(simulator, self.circuits, self.shots, seed, exact) for seed in seeds]

    def __call__(self, point: tuple[float, float]) -> dict[str, list[float]]:
        counts = iter(self.counts(point, (SEED,))[0])
        return {
            m: [
                round(ghost_run.tv(self.measured[m][k], ghost_run.distribution(next(counts), r.num_clbits)), 6)
                for k, r in enumerate(self.replicas[m])
            ]
            for m in self.chosen
        }


def cz_free(circuits: list[QuantumCircuit]) -> bool:
    """Whether the circuits apply no CZ, so scaled() changes no channel they use and every c samples alike."""
    return not footprint(circuits)[1]


def sampled_points(grid: list[tuple[float, float]], free: bool) -> dict[int, int]:
    """Each grid index mapped to the index whose sample it takes.

    A group with a CZ samples every point. A CZ-free group samples one point
    per readout factor, the c = 1 point where the grid holds it and else the
    first point with that factor, and every other point takes that sample.
    """
    if not free:
        return {j: j for j in range(len(grid))}
    chosen: dict[float, int] = {}
    for j, (c, r) in enumerate(grid):
        if r not in chosen or (c == 1.0 and grid[chosen[r]][0] != 1.0):
            chosen[r] = j
    return {j: chosen[r] for j, (_, r) in enumerate(grid)}


def sweep_run(
    run_name: str,
    device: str,
    index: dict[str, Any],
    grid: list[tuple[float, float]],
    floor_point: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """The run's TV distances at every grid point, and the resample floor at floor_point or the minimizing point.

    A CZ-free snapshot group samples only the c = 1 point of each readout
    factor and gives every other c that point's distances: under one seed
    a full c sweep of such a group returns the same counts at every c
    (--self-test-cz-free).
    """
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    replicas, measured, shots, execution, laws = (
        prepared["replicas"],
        prepared["measured"],
        prepared["shots"],
        prepared["execution"],
        prepared["laws"],
    )
    members = [m for m in prepared["members"] if m in execution]
    points: list[dict[str, Any]] = [{"cz": c, "readout": r, "tvd": {}} for c, r in grid]
    snapshots = snapshot_diagnostics(prepared, members)
    samplers: dict[str, GridSampler] = {}
    for relative in snapshots:
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        group = {m: replicas[m][1] for m in chosen}
        source = sampled_points(grid, cz_free([r for rows in group.values() for r in rows]))
        picks = sorted(set(source.values()))
        sampler = GridSampler(
            snapshot, device, aer_threads(len(picks)), chosen, group, measured, shots, {m: laws[m] for m in chosen}
        )
        samplers[relative] = sampler
        found = dict(zip(picks, parallel.ordered_map(sampler, [grid[j] for j in picks], min_items=1), strict=True))
        for j, point in enumerate(points):
            point["tvd"].update(found[source[j]])
    means = grid_means(points, members)
    best = int(np.argmin(means))
    cz, readout = floor_point or (points[best]["cz"], points[best]["readout"])
    floor: dict[str, Any] = {"cz": cz, "readout": readout, "tvd": {}}
    for sampler in samplers.values():
        first, second = (iter(draw) for draw in sampler.counts((cz, readout), (SEED, ghost_run.RESAMPLE_SEED)))
        for m in sampler.chosen:
            floor["tvd"][m] = [
                round(
                    ghost_run.tv(
                        ghost_run.distribution(next(first), r.num_clbits),
                        ghost_run.distribution(next(second), r.num_clbits),
                    ),
                    6,
                )
                for r in replicas[m][1]
            ]
    floor["mean_tvd"] = round(float(np.mean([v for m in members for v in floor["tvd"][m]])), 6)
    print(
        json.dumps({"run": run_name, "best": [points[best]["cz"], points[best]["readout"]], "mean_tvd": means[best]}),
        flush=True,
    )
    return {
        "run": run_name,
        "backend": prepared["backend"],
        "members": members,
        "member_shots": {m: shots[m] for m in members},
        "member_law": {m: laws[m] for m in members},
        "execution_snapshot": {m: execution[m] for m in members},
        "snapshots": snapshots,
        "mean_tvd": means,
        "points": points,
        "floor": floor,
    }


def full_grid() -> list[tuple[float, float]]:
    return [(c, r) for c in CZ_FACTORS for r in READOUT_FACTORS]


def pub_sums(run: dict[str, Any]) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Per executed PUB: the summed TV distance at each grid point and its replica count."""
    executed = ghost_run.measured_members(ROOT / run["run"])[1]
    pubs = sorted({executed[m]["pub"] for m in run["members"]})
    position = {pub: k for k, pub in enumerate(pubs)}
    sums = np.zeros((len(pubs), len(run["points"])))
    counts = np.zeros(len(pubs))
    for m in run["members"]:
        k = position[executed[m]["pub"]]
        counts[k] += len(run["points"][0]["tvd"][m])
        for j, point in enumerate(run["points"]):
            sums[k, j] += sum(point["tvd"][m])
    return pubs, sums, counts


def clustered_delta(run: dict[str, Any], j: int, base: int) -> dict[str, Any]:
    """Mean per-replica distance at point j minus at point base, standard error clustered by PUB."""
    executed = ghost_run.measured_members(ROOT / run["run"])[1]
    pairs = [
        (executed[m]["pub"], b - a)
        for m in run["members"]
        for a, b in zip(run["points"][base]["tvd"][m], run["points"][j]["tvd"][m], strict=True)
    ]
    deltas = np.array([d for _, d in pairs])
    mean = float(deltas.mean())
    residual: dict[str, float] = {}
    for pub, d in pairs:
        residual[pub] = residual.get(pub, 0.0) + d - mean
    clusters = len(residual)
    error = (
        math.sqrt(clusters / (clusters - 1) * sum(v * v for v in residual.values())) / len(pairs)
        if clusters > 1
        else None
    )
    return {"mean_delta": round(mean, 6), "standard_error": round(error, 6) if error is not None else None}


def load(paths: list[Path]) -> dict[str, Any]:
    """The runs of every part file, which must share the schema and the module's grid."""
    runs: list[dict[str, Any]] = []
    for path in paths:
        part = json.loads(path.read_text(encoding="utf-8"))
        require(part["schema"] == SCHEMA, f"{path}: schema must be {SCHEMA}")
        require(part["grid"] == [list(p) for p in full_grid()], f"{path}: grid differs from the module's factors")
        runs += part["runs"]
    return {"runs": runs}


def report(paths: list[Path]) -> dict[str, Any]:
    retained = load(paths)
    grid = full_grid()
    base = grid.index((1.0, 1.0))
    rows = []
    for run in retained["runs"]:
        if "skipped" in run:
            rows.append({"run": run["run"], "skipped": run["skipped"]})
            continue
        means = run["mean_tvd"]
        best = int(np.argmin(means))
        pubs, sums, counts = pub_sums(run)
        # A PUB bootstrap with a seed fixed by the run name, so the report is reproducible.
        rng = np.random.default_rng(int(hashlib.sha256(run["run"].encode()).hexdigest()[:8], 16))
        draws = rng.integers(0, len(pubs), size=(BOOTSTRAP, len(pubs)))
        boot = np.argmin(sums[draws].sum(axis=1) / counts[draws].sum(axis=1)[:, None], axis=1)
        cz_draws = np.array([grid[j][0] for j in boot])
        readout_draws = np.array([grid[j][1] for j in boot])
        cz_profile = {str(c): min(m for (gc, _), m in zip(grid, means, strict=True) if gc == c) for c in CZ_FACTORS}
        readout_profile = {
            str(r): min(m for (_, gr), m in zip(grid, means, strict=True) if gr == r) for r in READOUT_FACTORS
        }
        rows.append(
            {
                "run": run["run"],
                "backend": run["backend"],
                "members": len(run["members"]),
                "pubs": len(pubs),
                "mean_tvd_at_reported": means[base],
                "resample_floor": {
                    "cz": run["floor"]["cz"],
                    "readout": run["floor"]["readout"],
                    "mean_tvd": run["floor"]["mean_tvd"],
                },
                "uniform_mean_tvd": uniform_tvd(run),
                "best": {"cz": grid[best][0], "readout": grid[best][1], "mean_tvd": means[best]},
                "best_minus_reported": clustered_delta(run, best, base),
                "cz_profile": cz_profile,
                "readout_profile": readout_profile,
                "bootstrap": {
                    "draws": BOOTSTRAP,
                    "cz_quantiles_16_50_84": [
                        float(np.quantile(cz_draws, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)
                    ],
                    "readout_quantiles_16_50_84": [
                        float(np.quantile(readout_draws, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)
                    ],
                    "cz_above_1": round(float(np.mean(cz_draws > 1.0)), 4),
                    "cz_at_grid_top": round(float(np.mean(cz_draws == CZ_FACTORS[-1])), 4),
                    "readout_above_1": round(float(np.mean(readout_draws > 1.0)), 4),
                    "readout_at_grid_top": round(float(np.mean(readout_draws == READOUT_FACTORS[-1])), 4),
                },
            }
        )
    fitted = [r for r in rows if "skipped" not in r]
    return {
        "schema": "ghost-error-scale-report-v1",
        "sources": [path.as_posix() for path in paths],
        "cz_factors": list(CZ_FACTORS),
        "readout_factors": list(READOUT_FACTORS),
        "runs": rows,
        "counts": {
            "runs": len(fitted),
            "cz_above_1_in_84_percent": sum(r["bootstrap"]["cz_above_1"] >= 0.84 for r in fitted),
            "cz_at_most_1_in_84_percent": sum(r["bootstrap"]["cz_above_1"] <= 0.16 for r in fitted),
            "readout_above_1_in_84_percent": sum(r["bootstrap"]["readout_above_1"] >= 0.84 for r in fitted),
            "readout_at_most_1_in_84_percent": sum(r["bootstrap"]["readout_above_1"] <= 0.16 for r in fitted),
        },
    }


def uniform_tvd(run: dict[str, Any]) -> float:
    """Mean TV distance from each hardware distribution to the uniform distribution over its outcomes."""
    measured = ghost_run.measured_members(ROOT / run["run"])[0]
    return round(
        float(np.mean([ghost_run.tv(d, np.full(len(d), 1 / len(d))) for m in run["members"] for d in measured[m]])), 6
    )


def tolerance(run: dict[str, Any], members: list[str]) -> float:
    """Five standard errors of the difference of two independent draws of the mean over the members' replicas.

    The mean runs over every replica row, so the sample count is the
    members' replica count, each row weighted by its member's shots.
    """
    rows = [run["member_shots"][m] for m in members for _ in run["points"][0]["tvd"][m]]
    inverse_shots = float(np.mean([1 / shots for shots in rows]))
    return 5 * math.sqrt(2.0 * inverse_shots / len(rows)) + 1e-3


def validate(run: dict[str, Any], index: dict[str, Any], grid: list[tuple[float, float]]) -> None:
    """Require every field the archived inputs and the retained distances determine."""
    name = run["run"]
    prepared = ghost_run.prepare(name, index)
    if "skipped" in prepared:
        require(run.get("skipped") == prepared["skipped"], f"{name}: skip reason differs")
        return
    require("skipped" not in run, f"{name}: marked skipped although its inputs rebuild")
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    require(run["backend"] == prepared["backend"], f"{name}: backend differs")
    require(run["members"] == members, f"{name}: members differ")
    require(run["member_shots"] == {m: prepared["shots"][m] for m in members}, f"{name}: member shots differ")
    require(run["execution_snapshot"] == {m: execution[m] for m in members}, f"{name}: execution snapshots differ")
    laws = {m: prepared["laws"][m] for m in members}
    require(
        run.get("member_law", dict.fromkeys(members, ghost_run.AER_SAMPLED)) == laws,
        f"{name}: member laws differ from the rule over its archived inputs",
    )
    require([(p["cz"], p["readout"]) for p in run["points"]] == grid, f"{name}: grid differs")
    # The sampler groups members by execution snapshot, so a run that spans
    # a calibration change keys its distances in group order.
    for point in run["points"]:
        require(sorted(point["tvd"]) == sorted(members), f"{name}: {point['cz']}x{point['readout']} member coverage")
        for m, row in point["tvd"].items():
            require(len(row) == len(prepared["replicas"][m][1]), f"{name}: {m} replica count")
    require(run["mean_tvd"] == grid_means(run["points"], members), f"{name}: means differ from the distances")
    best = int(np.argmin(run["mean_tvd"]))
    floor = run["floor"]
    require((floor["cz"], floor["readout"]) == grid[best], f"{name}: resample floor is not at the minimizing point")
    require(sorted(floor["tvd"]) == sorted(members), f"{name}: resample floor member coverage")
    for m, row in floor["tvd"].items():
        require(len(row) == len(prepared["replicas"][m][1]), f"{name}: {m} floor replica count")
    require(
        floor["mean_tvd"] == round(float(np.mean([v for m in members for v in floor["tvd"][m]])), 6),
        f"{name}: floor mean differs from its distances",
    )
    require(sorted(run["snapshots"]) == sorted(set(execution.values())), f"{name}: snapshots differ")
    for relative, entry in run["snapshots"].items():
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        circuits = [replica for m in chosen for replica in prepared["replicas"][m][1]]
        rebuilt = diagnostics(snapshot, circuits, infidelity=False)
        retained = {
            **entry,
            "cz": [{k: v for k, v in row.items() if k != "model_infidelity_mean"} for row in entry["cz"]],
        }
        require(retained == {"members": len(chosen), **rebuilt}, f"{name}: {relative} diagnostics differ")
        # A CZ-free group samples alike at every c, so its distances repeat
        # along c at each readout factor.
        if cz_free(circuits):
            for j, k in sampled_points(grid, True).items():
                require(
                    all(run["points"][j]["tvd"][m] == run["points"][k]["tvd"][m] for m in chosen),
                    f"{name}: CZ-free {relative} differs along c at {grid[j]}",
                )


class RunValidator:
    """validate() over one retained run, for the process pool."""

    def __init__(self, index: dict[str, Any], grid: list[tuple[float, float]]) -> None:
        self.index = index
        self.grid = grid

    def __call__(self, run: dict[str, Any]) -> None:
        validate(run, self.index, self.grid)


def check(paths: list[Path], runs: str, index: dict[str, Any]) -> None:
    retained = load(paths)
    grid = full_grid()
    listed = [run["run"] for run in retained["runs"]]
    require(
        sorted(listed) == ghost_run.audited_runs() and len(set(listed)) == len(listed),
        "the files do not hold each audited run exactly once",
    )
    # Results return in run order, so the first failing run raises as in a serial loop.
    parallel.ordered_map(RunValidator(index, grid), retained["runs"], min_items=2)
    # The (1, 1) point is the unscaled noise model, so its execution means
    # agree with the ghost runs' execution-state means.
    ghosts = {run["run"]: run for run in json.loads(GHOST_RESULT.read_text(encoding="utf-8"))["runs"]}
    base = grid.index((1.0, 1.0))
    for run in retained["runs"]:
        if "skipped" in run:
            continue
        for relative in run["snapshots"]:
            own = [m for m in run["members"] if run["execution_snapshot"][m] == relative]
            mine = float(np.mean([v for m in own for v in run["points"][base]["tvd"][m]]))
            theirs = ghosts[run["run"]]["summary"][relative]["execution_mean_tvd"]
            require(abs(mine - theirs) <= tolerance(run, own), f"{run['run']}: (1, 1) {mine} vs ghost {theirs}")
    named = None if runs == "all" else set(runs.split(","))
    checked = 0
    for run in retained["runs"]:
        if "skipped" in run or (named is not None and run["run"] not in named):
            continue
        checked += 1
        best = int(np.argmin(run["mean_tvd"]))
        picks = sorted({base, best, len(grid) - 1})
        fresh = sweep_run(run["run"], "CPU", index, [grid[j] for j in picks], grid[best])
        for relative, entry in run["snapshots"].items():
            require(
                fresh["snapshots"][relative]["cz"] == entry["cz"],
                f"{run['run']}: {relative} modeled infidelity differs",
            )
        for k, j in enumerate(picks):
            old, new = run["mean_tvd"][j], fresh["mean_tvd"][k]
            require(abs(old - new) <= tolerance(run, run["members"]), f"{run['run']}: {grid[j]} {old} vs {new}")
        old, new = run["floor"]["mean_tvd"], fresh["floor"]["mean_tvd"]
        require(abs(old - new) <= tolerance(run, run["members"]), f"{run['run']}: floor {old} vs {new}")
    require(checked > 0 and (named is None or checked == len(named)), "--runs names a run the files lack")
    print(f"{len(listed)} runs validated; {checked} rerun on the CPU")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, nargs="+", help="retained part files that together hold every run")
    parser.add_argument("--report", type=Path, nargs="+", help="print the fitted factors of retained part files")
    parser.add_argument(
        "--regenerate-diagnostics", type=Path, metavar="IN", help="rewrite a part's calibration-derived fields to --out"
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        nargs="+",
        metavar="PATH",
        help="PART KERNEL_OUTPUT...: require PART to be the regeneration of the kernel parts merged in order",
    )
    parser.add_argument("--self-test", action="store_true", help="exercise --provenance on synthetic shards")
    parser.add_argument(
        "--self-test-cz-free",
        nargs="*",
        metavar="RUN",
        help=f"show a CZ-free group samples alike at every c (default {CZ_FREE_RUN}, control {CZ_CONTROL_RUN})",
    )
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.self_test_cz_free is not None:
        index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
        for run in args.self_test_cz_free or [CZ_FREE_RUN]:
            cz_free_self_test(run, CZ_CONTROL_RUN, index)
        return 0
    if args.report:
        print(json.dumps(report(args.report), indent=1))
        return 0
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.check:
        check(args.check, args.runs, index)
        return 0
    if args.provenance:
        provenance(args.provenance[0], args.provenance[1:], index)
        return 0
    if args.regenerate_diagnostics:
        require(args.out is not None, "--out is required")
        part = json.loads(args.regenerate_diagnostics.read_text(encoding="utf-8"))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_part(args.out, regenerate(part, index))
        return 0
    require(args.out is not None, "--out is required")
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    grid = full_grid()
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": device,
        "max_qubits": ghost_run.MAX_QUBITS,
        "seed": SEED,
        "grid": [list(p) for p in grid],
        "scaled": scaled_block(),
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for run in runs:
        # Written after every run, so a failure keeps every finished one.
        out["runs"].append(sweep_run(run, device, index, grid))
        write_part(args.out, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
