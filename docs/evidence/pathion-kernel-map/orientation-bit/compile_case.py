"""Routed cost and snapshot noise prediction of the orientation-bit case.

The case is written in docs/design/pathion-kernel-map-orientation-bit.md.

Every number comes from the retained Target snapshot of ibm_fez (docs/evidence/heron_platform/targets.json,
calibration 2026-10-14), never from a live backend: the live compile and the calibration of the day are owed to the
binding dry run (scripts/approved_run.sh --check).

Routed cost. Each member circuit is transpiled to the basis cz, rz, sx, x at optimization level 3 (live_run.OPT_LEVEL)
onto each of the best-ESP six-qubit tiles of HeronLattice.find_disjoint_tiles, for each transpiler seed; the CZ count
per (member, tile, seed) is the routed cost, compared with the retained 136 to 173 of the kernel map and between each
moved or swapped circuit and its control (a departure above 20 percent rejects the moved bit). Every member of a tile
and seed routes on the layout of the first operand's control, as the live run routes a whole group on one layout.

Noise prediction. The same routed circuits run exactly (density matrix, no sampling) under a depolarizing model from the
snapshot: each cz carries its coupler error, each sx and x its qubit error, and each measured qubit a symmetric
readout flip of its measure error. The snapshot holds no T1 or T2, so the model has no relaxation and no operand-
dependent decay of the orientation qubit; its gaps lambda_16 - lambda_0 therefore follow from character weight and
readout alone. The replicas are the tiles; the statistics are those of orientation_bit_analysis (the family and the
exploratory diff_cm and diff_cs, the model floors of the comparison across two physical qubits).

Relaxation prediction. The snapshot holds no T1 or T2, and the only per-qubit T1, T2 and asymmetric readout error of
ibm_fez in the tree belong to the retained kernel-map run (results/live/2026-11-06T183538.809814Z/record.json,
calibration 2026-11-06T10:24:29-08:00), which covers its five placed regions. The "relaxation" block routes the same
members with the first transpiler seed onto those five regions and simulates them exactly (Aer density matrix, no
sampling) under four noise models built from that one record (per-qubit T1, T2, sx, x and cz errors and durations, and
the prob_meas1_prep0 and prob_meas0_prep1 readout errors): depolarizing gate errors with a symmetric readout flip (the
model of the snapshot rows, on these regions), relaxation alone (T1 and T2 over every gate and idle interval of an
ASAP schedule that ends all wires together, ideal gates and readout), asymmetric readout alone, and all three. The
replicas are the five regions, the statistics those of orientation_bit_analysis, and the retained signs they are read
against are -0.155 (nullity 4) and +0.103 (nullity 12).

"$PYTHON" -B compile_case.py --out DIR --seed-transpiler \
    qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#0 ...#1 ...#2   (draw-2026-11-24T022126Z.json)
"$PYTHON" -B compile_case.py --check      recompute and compare with the committed case_compile.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Kraus

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import orientation_bit_analysis as oba  # noqa: E402

import parallel  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402
import pathion_kernel_map_orientation as pko  # noqa: E402
import qrng_seeds  # noqa: E402
from heron_multiprogramming import HERON_BASIS, DisjointTile, HeronLattice  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
RETAINED_RECORD = ROOT / "results/live/2026-11-06T183538.809814Z/record.json"
COMMITTED = HERE / "case_compile.json"
BACKEND = "ibm_fez"
OPT_LEVEL = 3
TILE_SIZE = 6
TILES = 5
REJECT = 0.20
SCRIPT = "docs/evidence/pathion-kernel-map/orientation-bit/compile_case.py"
EXPERIMENT = "pathion-kernel-map-orientation-bit-compile"
# Retained CZ counts of the kernel map on ibm_fez (docs/evidence/pathion-kernel-map/README.md, findings table): the case
# compares its members with this range and with the retained primary and twin of each operand.
RETAINED_CZ_RANGE = (136, 173)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def variants() -> dict[str, QuantumCircuit]:
    """Circuits to route: the four roles of the case per operand and the alternative moved bit 0."""
    out: dict[str, QuantumCircuit] = {}
    for operand in pko.OPERANDS:
        for role in pko.ROLES:
            out[pko.unit_name(role, operand)] = pko.role_template(role, operand)
        out[f"alt_bit0_{pkm.operand_tag(operand)}"] = pko.kernel_map_template(operand, orientation_bit=0)
    return out


def route(
    circuit: QuantumCircuit, lattice: HeronLattice, tile: DisjointTile, seed: int, layout: list[int] | None = None
) -> QuantumCircuit:
    return transpile(
        circuit,
        coupling_map=lattice.tile_coupling_map(tile),
        basis_gates=list(HERON_BASIS),
        optimization_level=OPT_LEVEL,
        seed_transpiler=seed,
        initial_layout=layout,
    )


def reference_layout(lattice: HeronLattice, tile: DisjointTile, seed: int) -> list[int]:
    """Placement of the control of the first operand on one tile. The live run routes every member of a group on one
    layout, so each member of the model is routed on this one: the swap member then puts data bit 4 on the physical
    qubit that carries data bit 1 in the other members."""
    first = pko.role_template("ctrl", pko.OPERANDS[0]).assign_parameters({pkm.ORIENTATION: 0.0})
    routed = route(first, lattice, tile, seed)
    if routed.layout is None:
        raise ValueError("the routed control carries no layout")
    return [int(q) for q in routed.layout.initial_index_layout(filter_ancillas=True)]


@functools.cache
def snapshot_lattice() -> HeronLattice:
    return HeronLattice.from_snapshot(SNAPSHOT, BACKEND)


@functools.cache
def snapshot_tiles() -> list[DisjointTile]:
    return snapshot_lattice().find_disjoint_tiles(TILE_SIZE, min_buffer_distance=2, max_tiles=TILES)


def routed_templates() -> dict[str, QuantumCircuit]:
    bound = variants()
    retained = {f"retained_{pkm.operand_tag(op)}": pkm.kernel_map_template(op) for op in pko.OPERANDS}
    twins = {
        f"retained_twin_{pkm.operand_tag(twin)}": pkm.kernel_map_template(twin)
        for twin, primary in pkm.TWINS
        if primary in pko.OPERANDS
    }
    return {**bound, **retained, **twins}


def cz_counts(item: tuple[int, int]) -> dict[str, int]:
    """CZ count of every routed template on one (tile index, transpiler seed) pair."""
    tile_index, seed = item
    lattice, tile = snapshot_lattice(), snapshot_tiles()[tile_index]
    layout = reference_layout(lattice, tile, seed)
    return {
        name: route(template.assign_parameters({pkm.ORIENTATION: 0.0}), lattice, tile, seed, layout)
        .count_ops()
        .get("cz", 0)
        for name, template in routed_templates().items()
    }


def cz_table(tiles: list[DisjointTile], seeds: list[int]) -> dict[str, Any]:
    rows = parallel.ordered_map(cz_counts, [(i, seed) for i in range(len(tiles)) for seed in seeds], min_items=1)
    flat = {name: [row[name] for row in rows] for name in rows[0]}
    ratios = {}
    for operand in pko.OPERANDS:
        t = pkm.operand_tag(operand)
        ctrl = flat[pko.unit_name("ctrl", operand)]
        for label, key in (
            ("move", pko.unit_name("move", operand)),
            ("swap", pko.unit_name("swap", operand)),
            ("alt_bit0", f"alt_bit0_{t}"),
        ):
            r = [m / c for m, c in zip(flat[key], ctrl, strict=True)]
            ratios[f"{label}_over_ctrl_{t}"] = {
                "min": min(r),
                "max": max(r),
                "median": median(r),
                "rejected": bool(max(abs(x - 1.0) for x in r) > REJECT),
            }
    return {
        "per_member": {
            name: {"min": min(v), "median": median(v), "max": max(v), "n": len(v)} for name, v in flat.items()
        },
        "ratios": ratios,
    }


def noise_laws(circuit: QuantumCircuit, lattice: HeronLattice, tile: DisjointTile) -> np.ndarray:
    """Exact outcome law (64 bins, clbit j = bit j) of a routed circuit under the snapshot's depolarizing and readout
    model, with the tile's physical errors on the tile positions."""
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    model = NoiseModel(basis_gates=list(HERON_BASIS))
    position = {q: i for i, q in enumerate(tile.qubits)}
    for (a, b), error in lattice.cz_errors.items():
        if a in position and b in position:
            lam = min(1.0, error * 4.0 / 3.0)
            for pair in ((position[a], position[b]), (position[b], position[a])):
                model.add_quantum_error(depolarizing_error(lam, 2), "cz", list(pair))
    for q in tile.qubits:
        lam = min(1.0, lattice.sx_errors[q] * 2.0)
        for gate in ("sx", "x"):
            model.add_quantum_error(depolarizing_error(lam, 1), gate, [position[q]])
    measured: dict[int, int] = {}
    stripped = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if instruction.operation.name == "measure":
            measured[circuit.find_bit(instruction.clbits[0]).index] = circuit.find_bit(instruction.qubits[0]).index
        elif instruction.operation.name != "barrier":
            stripped.append(instruction.operation, [circuit.find_bit(q).index for q in instruction.qubits])
    order = [measured[j] for j in range(len(measured))]
    stripped.save_probabilities(order, label="p")
    simulator = AerSimulator(method="density_matrix", noise_model=model)
    law = np.asarray(simulator.run(transpile(stripped, simulator, optimization_level=0)).result().data()["p"])
    flips = [lattice.readout_errors[tile.qubits[measured[j]]] for j in range(len(measured))]
    for j, flip in enumerate(flips):
        confusion = np.array([[1.0 - flip, flip], [flip, 1.0 - flip]])
        law = np.moveaxis(
            np.tensordot(confusion, np.moveaxis(law.reshape([2] * len(flips)), -1 - j, 0), axes=(1, 0)), 0, -1 - j
        )
        law = law.reshape(-1)
    return law


def routed_members(lattice: HeronLattice, tile: DisjointTile, seed: int) -> dict[str, QuantumCircuit]:
    """Every member of the group routed once per template onto one tile, on the layout of reference_layout, and bound
    to its arm's phase."""
    group = pko.pathion_kernel_map_orientation_group()
    layout = reference_layout(lattice, tile, seed)
    routed: dict[str, QuantumCircuit] = {}
    bound: dict[str, QuantumCircuit] = {}
    for member in group.members:
        template_name = member.name.rsplit("_", 1)[0]
        if template_name not in routed:
            routed[template_name] = route(member.circuit, lattice, tile, seed, layout)
        bound[member.name] = routed[template_name].assign_parameters(member.binding)
    return bound


def snapshot_laws(item: tuple[int, int]) -> dict[str, list[float]]:
    """Depolarizing-model laws of every member on one snapshot tile (tile index, transpiler seed)."""
    tile_index, seed = item
    lattice, tile = snapshot_lattice(), snapshot_tiles()[tile_index]
    return {name: noise_laws(c, lattice, tile).tolist() for name, c in routed_members(lattice, tile, seed).items()}


def summarize_statistics(laws: list[dict[str, list[float]]]) -> dict[str, Any]:
    """Mean, standard error, t, n and 95 percent interval of every test of the family over the replicas, whose laws
    are one dict of member name to law per replica."""
    group = pko.pathion_kernel_map_orientation_group()
    entry = {"group": group.name, "measured": {m.name: [replica[m.name] for replica in laws] for m in group.members}}
    result = oba.analyze(entry)
    keep: dict[str, Any] = {}
    for key, row in {**result["tests"], **result["exploratory"]}.items():
        entry_row = {k: (row[k] if math.isfinite(row[k]) else None) for k in ("mean", "se", "t", "n")}
        if math.isfinite(row["se"]) and math.isfinite(row["mean"]):
            half = float(oba.stats.t.isf(0.025, row["n"] - 1)) * row["se"]
            entry_row["interval95"] = [row["mean"] - half, row["mean"] + half]
        keep[key] = entry_row
    return keep


def simulate(tiles: list[DisjointTile], seed: int) -> dict[str, Any]:
    laws = parallel.ordered_map(snapshot_laws, [(i, seed) for i in range(len(tiles))], min_items=1)
    return {"replicas": len(tiles), "tiles": [t.qubits for t in tiles], "statistics": summarize_statistics(laws)}


# ----------------------------------------------------------------------------------------- relaxation prediction

MODELS: dict[str, dict[str, Any]] = {
    "depolarizing_symmetric_readout": {"depolarizing": True, "relaxation": False, "readout": "symmetric"},
    "relaxation_only": {"depolarizing": False, "relaxation": True, "readout": "none"},
    "asymmetric_readout_only": {"depolarizing": False, "relaxation": False, "readout": "asymmetric"},
    "depolarizing_relaxation_asymmetric_readout": {"depolarizing": True, "relaxation": True, "readout": "asymmetric"},
}
# The retained effects of the character gap lambda_16 - lambda_0 that the prediction is read against.
RETAINED_GAP = {"e1pe26": -0.155, "e1pe18": 0.103}


@dataclass(frozen=True)
class Calibration:
    """Per-qubit and per-coupler calibration of the five regions of one retained run, in SI units."""

    regions: list[list[int]]
    t1: dict[int, float]
    t2: dict[int, float]
    sx_error: dict[int, float]
    sx_duration: dict[int, float]
    x_error: dict[int, float]
    x_duration: dict[int, float]
    cz_error: dict[tuple[int, int], float]
    cz_duration: dict[tuple[int, int], float]
    readout_error: dict[int, float]
    meas1_prep0: dict[int, float]
    meas0_prep1: dict[int, float]
    t2_clamped: list[int]
    calibration: str


def load_calibration(path: Path) -> Calibration:
    """Calibration of the replica regions of the first group of a retained live record. T2 above 2 T1 is clamped to
    2 T1, the physical bound of the thermal-relaxation channel, and the clamped qubits are listed."""
    group = json.loads(path.read_text())["groups"][0]
    fingerprint = group["calibration_fingerprint"]
    regions = [list(r["physical_qubits"]) for r in group["replicas"]]
    qubits = [q for region in regions for q in region]
    placed = group["placed_qubit_calibration"]
    t1: dict[int, float] = {}
    t2: dict[int, float] = {}
    clamped: list[int] = []
    for q in qubits:
        t1[q] = float(placed[str(q)]["T1"]) * 1e-6
        t2[q] = float(placed[str(q)]["T2"]) * 1e-6
        if t2[q] > 2.0 * t1[q]:
            t2[q], clamped = 2.0 * t1[q], [*clamped, q]
    sx_error = {q: float(fingerprint[f"target:sx({q},):error"]) for q in qubits}
    sx_duration = {q: float(fingerprint[f"target:sx({q},):duration"]) for q in qubits}
    x_error = {q: float(fingerprint.get(f"target:x({q},):error", sx_error[q])) for q in qubits}
    x_duration = {q: float(fingerprint.get(f"target:x({q},):duration", sx_duration[q])) for q in qubits}
    cz_error: dict[tuple[int, int], float] = {}
    cz_duration: dict[tuple[int, int], float] = {}
    for region in regions:
        for a in region:
            for b in region:
                if f"target:cz({a}, {b}):error" in fingerprint:
                    cz_error[(a, b)] = float(fingerprint[f"target:cz({a}, {b}):error"])
                    cz_duration[(a, b)] = float(fingerprint[f"target:cz({a}, {b}):duration"])
    return Calibration(
        regions=regions,
        t1=t1,
        t2=t2,
        sx_error=sx_error,
        sx_duration=sx_duration,
        x_error=x_error,
        x_duration=x_duration,
        cz_error=cz_error,
        cz_duration=cz_duration,
        readout_error={q: float(placed[str(q)]["readout_error"]) for q in qubits},
        meas1_prep0={q: float(placed[str(q)]["prob_meas1_prep0"]) for q in qubits},
        meas0_prep1={q: float(placed[str(q)]["prob_meas0_prep1"]) for q in qubits},
        t2_clamped=sorted(clamped),
        calibration=str(group["calibration"]),
    )


@functools.cache
def retained_calibration() -> Calibration:
    return load_calibration(RETAINED_RECORD)


def region_tile(lattice: HeronLattice, region: list[int], index: int) -> DisjointTile:
    """A routing tile on the induced couplers of one retained region."""
    return DisjointTile(index, list(region), lattice.induced_edges(region), [], 0.0, 0.0, 0.0, 0.0, 0.0)


def _strip(circuit: QuantumCircuit) -> tuple[QuantumCircuit, list[int]]:
    """The routed circuit without measures and barriers, and for each classical bit j the qubit measured into it."""
    measured: dict[int, int] = {}
    stripped = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if instruction.operation.name == "measure":
            measured[circuit.find_bit(instruction.clbits[0]).index] = circuit.find_bit(instruction.qubits[0]).index
        elif instruction.operation.name != "barrier":
            stripped.append(instruction.operation, [circuit.find_bit(q).index for q in instruction.qubits])
    return stripped, [measured[j] for j in range(len(measured))]


def _confuse(law: np.ndarray, matrices: list[np.ndarray]) -> np.ndarray:
    """Apply one 2 x 2 confusion matrix (rows: read value, columns: true value) per classical bit j."""
    for j, confusion in enumerate(matrices):
        law = np.moveaxis(
            np.tensordot(confusion, np.moveaxis(law.reshape([2] * len(matrices)), -1 - j, 0), axes=(1, 0)), 0, -1 - j
        ).reshape(-1)
    return law


def _gate_duration(cal: Calibration, name: str, qubits: tuple[int, ...]) -> float:
    q = qubits[0]
    if name == "rz":
        return 0.0
    if name == "sx":
        return cal.sx_duration[q]
    if name == "x":
        return cal.x_duration[q]
    if name == "cz":
        return cal.cz_duration[(qubits[0], qubits[1])]
    raise ValueError(f"no duration for {name}")


def with_relaxation(stripped: QuantumCircuit, cal: Calibration, tile: DisjointTile) -> QuantumCircuit:
    """The circuit with T1 and T2 relaxation (thermal_relaxation_error, ground-state population 1) on every qubit over
    each gate duration and each idle interval of the ASAP schedule, the wires ending together at the last gate (the
    measures act at that common time). Virtual rz gates take no time."""
    from qiskit_aer.noise import thermal_relaxation_error

    physical = tile.qubits
    channels: dict[tuple[int, float], Kraus] = {}

    def relax(out: QuantumCircuit, position: int, seconds: float) -> None:
        if seconds <= 0.0:
            return
        key = (position, seconds)
        if key not in channels:
            q = physical[position]
            channels[key] = Kraus(thermal_relaxation_error(cal.t1[q], cal.t2[q], seconds).to_quantumchannel())
        out.append(channels[key], [position])

    free = [0.0] * stripped.num_qubits
    out = QuantumCircuit(stripped.num_qubits)
    for instruction in stripped.data:
        positions = [stripped.find_bit(q).index for q in instruction.qubits]
        name = instruction.operation.name
        seconds = _gate_duration(cal, name, tuple(physical[p] for p in positions))
        start = max(free[p] for p in positions)
        for p in positions:
            relax(out, p, start - free[p])
        out.append(instruction.operation, positions)
        for p in positions:
            relax(out, p, seconds)
            free[p] = start + seconds
    end = max(free)
    for p in range(stripped.num_qubits):
        relax(out, p, end - free[p])
    return out


def model_laws(
    circuit: QuantumCircuit, cal: Calibration, tile: DisjointTile, depolarizing: bool, relaxation: bool, readout: str
) -> np.ndarray:
    """Exact outcome law (64 bins, clbit j = bit j) of a routed circuit on one retained region under one noise model."""
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    physical = tile.qubits
    position = {q: i for i, q in enumerate(physical)}
    stripped, order = _strip(circuit)
    if relaxation:
        stripped = with_relaxation(stripped, cal, tile)
    model = None
    if depolarizing:
        model = NoiseModel(basis_gates=list(HERON_BASIS))
        for (a, b), error in cal.cz_error.items():
            if a in position and b in position:
                model.add_quantum_error(
                    depolarizing_error(min(1.0, error * 4.0 / 3.0), 2), "cz", [position[a], position[b]]
                )
        for q in physical:
            for gate, error in (("sx", cal.sx_error[q]), ("x", cal.x_error[q])):
                model.add_quantum_error(depolarizing_error(min(1.0, error * 2.0), 1), gate, [position[q]])
    stripped.save_probabilities(order, label="p")
    simulator = AerSimulator(method="density_matrix", noise_model=model)
    law = np.asarray(simulator.run(transpile(stripped, simulator, optimization_level=0)).result().data()["p"])
    if readout == "none":
        return law
    matrices = []
    for p in order:
        q = physical[p]
        if readout == "symmetric":
            f = cal.readout_error[q]
            p10 = p01 = f
        else:
            p10, p01 = cal.meas1_prep0[q], cal.meas0_prep1[q]
        matrices.append(np.array([[1.0 - p10, p01], [p10, 1.0 - p01]]))
    return _confuse(law, matrices)


def region_laws(item: tuple[int, int]) -> dict[str, dict[str, list[float]]]:
    """Laws of every member on one retained region under each of the four noise models (region index, seed)."""
    index, seed = item
    cal, lattice = retained_calibration(), snapshot_lattice()
    tile = region_tile(lattice, cal.regions[index], index)
    members = routed_members(lattice, tile, seed)
    return {
        model: {name: model_laws(c, cal, tile, **options).tolist() for name, c in members.items()}
        for model, options in MODELS.items()
    }


def relaxation_prediction(seed: int) -> dict[str, Any]:
    cal = retained_calibration()
    per_region = parallel.ordered_map(region_laws, [(i, seed) for i in range(len(cal.regions))], min_items=1)
    models = {model: summarize_statistics([replica[model] for replica in per_region]) for model in MODELS}
    return {
        "label": "five regions of the retained kernel-map run, its own calibration; exact density matrix, no sampling",
        "calibration_source": {
            "path": RETAINED_RECORD.relative_to(ROOT).as_posix(),
            "sha256": sha256(RETAINED_RECORD),
            "calibration": cal.calibration,
            "backend": BACKEND,
        },
        "regions": cal.regions,
        "t2_clamped_to_2_t1": cal.t2_clamped,
        "models": {name: dict(options) for name, options in MODELS.items()},
        "schedule": "ASAP, wires end together, rz virtual, relaxation over gate durations and idle intervals",
        "retained_gap": RETAINED_GAP,
        "statistics": models,
    }


# ------------------------------------------------------------------------------------------------------------ record


def build_record(seeds: list[int], sources: list[str]) -> dict[str, Any]:
    tiles = snapshot_tiles()
    if len(tiles) < TILES:
        raise SystemExit(f"the snapshot holds {len(tiles)} tiles, fewer than {TILES}")
    return {
        "schema": "orientation-bit-compile-v2",
        "label": "retained snapshot, not a live Target",
        "snapshot": {
            "path": "docs/evidence/heron_platform/targets.json",
            "sha256": sha256(SNAPSHOT),
            "backend": BACKEND,
        },
        "optimization_level": OPT_LEVEL,
        "tiles": [t.qubits for t in tiles],
        "disjoint_tiles_available": {
            "guard_distance_2": len(
                snapshot_lattice().find_disjoint_tiles(TILE_SIZE, min_buffer_distance=2, max_tiles=40)
            ),
            "guard_distance_3": len(
                snapshot_lattice().find_disjoint_tiles(TILE_SIZE, min_buffer_distance=3, max_tiles=40)
            ),
        },
        "retained_cz_range": list(RETAINED_CZ_RANGE),
        "cz": cz_table(tiles, seeds),
        "simulation": simulate(tiles, seeds[0]),
        "relaxation": relaxation_prediction(seeds[0]),
        "seed_source": [qrng_seeds.seed_record(SCRIPT, "--seed-transpiler", EXPERIMENT, sources)],
    }


def differences(want: Any, got: Any, path: str = "") -> list[str]:
    """Paths at which two records differ: structure and strings exactly, floats within 1e-6."""
    if isinstance(want, dict) and isinstance(got, dict):
        out = [f"{path}/{k}: only in one record" for k in set(want) ^ set(got)]
        return out + [d for k in sorted(set(want) & set(got)) for d in differences(want[k], got[k], f"{path}/{k}")]
    if isinstance(want, list) and isinstance(got, list):
        if len(want) != len(got):
            return [f"{path}: length {len(want)} against {len(got)}"]
        return [d for i, (a, b) in enumerate(zip(want, got, strict=True)) for d in differences(a, b, f"{path}[{i}]")]
    if isinstance(want, float) or isinstance(got, float):
        close = (
            isinstance(want, (int, float)) and isinstance(got, (int, float)) and math.isclose(want, got, abs_tol=1e-6)
        )
        return [] if close else [f"{path}: {want} against {got}"]
    return [] if want == got else [f"{path}: {want!r} against {got!r}"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    qrng_seeds.add_seed_argument(ap, "--seed-transpiler", nargs="+")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true", help="recompute the record and compare it with case_compile.json")
    args = ap.parse_args()
    if args.check:
        committed = json.loads(COMMITTED.read_text())
        sources = committed["seed_source"][0]["sources"]
        seeds = [qrng_seeds.resolve(ref)[0] for ref in sources]
        found = differences(committed, json.loads(json.dumps(build_record(seeds, sources), allow_nan=False)))
        for line in found[:20]:
            print(f"differs: {line}")
        print(f"{'FAIL' if found else 'ok'}: {len(found)} differences from case_compile.json")
        return 1 if found else 0
    if args.seed_transpiler is None or args.out is None:
        ap.error("--seed-transpiler and --out are required without --check")
    record = build_record(list(args.seed_transpiler), args.seed_transpiler_source)
    (args.out / "case_compile.json").write_text(json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
