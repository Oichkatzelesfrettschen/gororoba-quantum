"""Routed cost and snapshot noise prediction of the orientation-bit case.

The case is written in docs/design/pathion-kernel-map-orientation-bit.md.

Every number comes from the retained Target snapshot of ibm_fez (docs/evidence/heron_platform/targets.json,
calibration 2026-10-14), never from a live backend: the live compile and the calibration of the day are owed to the
binding dry run (scripts/approved_run.sh --check).

Routed cost. Each member circuit is transpiled to the basis cz, rz, sx, x at optimization level 3 (live_run.OPT_LEVEL)
onto each of the best-ESP six-qubit tiles of HeronLattice.find_disjoint_tiles, for each transpiler seed; the CZ count
per (member, tile, seed) is the routed cost, compared with the retained 136 to 173 of the kernel map and between each
moved circuit and its control (a departure above 20 percent rejects the moved bit).

Noise prediction. The same routed circuits run exactly (density matrix, no sampling) under a depolarizing model from the
snapshot: each cz carries its coupler error, each sx and x its qubit error, and each measured qubit a symmetric
readout flip of its measure error. The snapshot holds no T1 or T2, so the model has no relaxation and no operand-
dependent decay of the orientation qubit; its gaps lambda_16 - lambda_0 therefore follow from character weight and
readout alone. The replicas are the tiles; the statistics are those of orientation_bit_analysis.

"$PYTHON" -B compile_case.py --out DIR --seed-transpiler \
    qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#0 ...#1 ...#2   (draw-2026-11-24T022126Z.json)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import orientation_bit_analysis as oba  # noqa: E402

import pathion_kernel_map as pkm  # noqa: E402
import pathion_kernel_map_orientation as pko  # noqa: E402
import qrng_seeds  # noqa: E402
from heron_multiprogramming import HERON_BASIS, DisjointTile, HeronLattice  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
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


def variants() -> dict[str, tuple[tuple[int, int, int], int, int | None]]:
    """Circuits to route as (operand, orientation bit, exchange bit): the three roles of the case per operand and the
    alternative moved bit 0."""
    out: dict[str, tuple[tuple[int, int, int], int, int | None]] = {}
    for operand in pko.OPERANDS:
        for role in pko.ROLES:
            out[pko.unit_name(role, operand)] = (operand, *pko.role_options(role, operand))
        out[f"alt_bit0_{pkm.operand_tag(operand)}"] = (operand, 0, None)
    return out


def route(circuit: QuantumCircuit, lattice: HeronLattice, tile: DisjointTile, seed: int) -> QuantumCircuit:
    return transpile(
        circuit,
        coupling_map=lattice.tile_coupling_map(tile),
        basis_gates=list(HERON_BASIS),
        optimization_level=OPT_LEVEL,
        seed_transpiler=seed,
    )


def cz_table(lattice: HeronLattice, tiles: list[DisjointTile], seeds: list[int]) -> dict[str, Any]:
    bound = {
        name: pko.kernel_map_template(op, orientation_bit=bit, exchange_bit=exchange)
        for name, (op, bit, exchange) in variants().items()
    }
    retained = {f"retained_{pkm.operand_tag(op)}": pkm.kernel_map_template(op) for op in pko.OPERANDS}
    twins = {
        f"retained_twin_{pkm.operand_tag(twin)}": pkm.kernel_map_template(twin)
        for twin, primary in pkm.TWINS
        if primary in pko.OPERANDS
    }
    every = {**bound, **retained, **twins}
    counts: dict[str, list[list[int]]] = {name: [] for name in every}
    for tile in tiles:
        for seed in seeds:
            for name, template in every.items():
                circuit = template.assign_parameters({pkm.ORIENTATION: 0.0})
                counts[name].append([route(circuit, lattice, tile, seed).count_ops().get("cz", 0)])
    flat = {name: [c[0] for c in rows] for name, rows in counts.items()}
    ratios = {}
    for operand in pko.OPERANDS:
        t = pkm.operand_tag(operand)
        ctrl = flat[pko.unit_name("ctrl", operand)]
        for label, key in (("move", pko.unit_name("move", operand)), ("alt_bit0", f"alt_bit0_{t}")):
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


def simulate(lattice: HeronLattice, tiles: list[DisjointTile], seed: int) -> dict[str, Any]:
    group = pko.pathion_kernel_map_orientation_group()
    measured: dict[str, list[list[float]]] = {m.name: [] for m in group.members}
    for tile in tiles:
        routed: dict[str, QuantumCircuit] = {}
        for member in group.members:
            template_name = member.name.rsplit("_", 1)[0]
            if template_name not in routed:
                routed[template_name] = route(member.circuit, lattice, tile, seed)
            bound = routed[template_name].assign_parameters(member.binding)
            measured[member.name].append(noise_laws(bound, lattice, tile).tolist())
    entry = {"group": group.name, "measured": measured}
    result = oba.analyze(entry)
    keep = {key: {k: row[k] for k in ("mean", "se", "t", "n")} for key, row in result["tests"].items()}
    for row in keep.values():
        half = float(oba.stats.t.isf(0.025, row["n"] - 1)) * row["se"]
        row["interval95"] = [row["mean"] - half, row["mean"] + half]
    return {"replicas": len(tiles), "tiles": [t.qubits for t in tiles], "statistics": keep}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    qrng_seeds.add_seed_argument(ap, "--seed-transpiler", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    lattice = HeronLattice.from_snapshot(SNAPSHOT, BACKEND)
    tiles = lattice.find_disjoint_tiles(TILE_SIZE, min_buffer_distance=2, max_tiles=TILES)
    if len(tiles) < TILES:
        raise SystemExit(f"the snapshot holds {len(tiles)} tiles, fewer than {TILES}")
    seeds = list(args.seed_transpiler)
    record = {
        "schema": "orientation-bit-compile-v1",
        "label": "retained snapshot, not a live Target",
        "snapshot": {
            "path": "docs/evidence/heron_platform/targets.json",
            "sha256": sha256(SNAPSHOT),
            "backend": BACKEND,
        },
        "optimization_level": OPT_LEVEL,
        "tiles": [t.qubits for t in tiles],
        "retained_cz_range": list(RETAINED_CZ_RANGE),
        "cz": cz_table(lattice, tiles, seeds),
        "simulation": simulate(lattice, tiles, seeds[0]),
        "seed_source": [qrng_seeds.seed_record(SCRIPT, "--seed-transpiler", EXPERIMENT, args.seed_transpiler_source)],
    }
    (args.out / "case_compile.json").write_text(json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
