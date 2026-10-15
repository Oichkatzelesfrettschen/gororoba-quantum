"""Audit guard-banded tile packing and Target duration arithmetic on the three Heron r2 backends.

The audit reads docs/evidence/heron_platform/targets.json through
gororoba_quantum/heron_multiprogramming.py and records, per backend: Target
medians, tile plans at guard distance 2 (and one at distance 3), native RZZ
against its CZ-basis synthesis, shot-rate ratios at two assumed circuit
durations, and the couplers above the rz, cz, sx flag threshold. Every
figure is arithmetic on the snapshot; no circuit is scheduled or executed.

Usage:
    "$PYTHON" scripts/heron_spatial_multiprogramming.py \\
        --out docs/evidence/heron_platform/spatial_multiprogramming_audit.json
    "$PYTHON" scripts/heron_spatial_multiprogramming.py \\
        --check docs/evidence/heron_platform/spatial_multiprogramming_audit.json
    "$PYTHON" scripts/heron_spatial_multiprogramming.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import median
from typing import Any

from qiskit import QuantumCircuit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from heron_multiprogramming import (  # noqa: E402
    HeronLattice,
    bent_hidden_shift_circuit,
    fano_plane_incidence_matrix,
    hoeffding_model_discrimination,
    lcu_zero_product_witness,
    sedenion_associator_witness,
    steane_coherent_syndrome_patch,
    steane_z_syndrome_patch,
)

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
# name, qubits per tile, requested tiles, the circuit that fits one tile
TILE_PLANS = (
    ("k5", 5, 16, "heron_multiprogramming.lcu_zero_product_witness"),
    ("k10", 10, 8, "heron_multiprogramming.steane_z_syndrome_patch"),
    ("k2", 2, 20, "heron_multiprogramming.bell_delay_probe"),
    ("k7", 7, 12, "designs.design_c_associator_spectrum at dimension 128"),
)
# Assumed circuit durations: 5 us, and 50 us from the typical 50-100 us in
# docs/notes/ibm_quantum/estimate-job-run-time.md.
CIRCUIT_DURATIONS_S = (5e-6, 50e-6)
REP_DELAYS_S = (250e-6, 100e-6, 50e-6, 20e-6, 10e-6)
FLAG_THRESHOLD = 0.004


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def target_medians(lattice: HeronLattice) -> dict[str, Any]:
    """Medians over undirected couplers (worst direction) and over qubits."""
    two_cz = {e: 1 - (1 - err) ** 2 for e, err in lattice.cz_errors.items()}
    rzz_below = sum(lattice.rzz_errors[e] < two_cz[e] for e in lattice.rzz_errors)
    return {
        "cz_error": round(median(lattice.cz_errors.values()), 7),
        "two_cz_error": round(median(two_cz.values()), 7),
        "rzz_error": round(median(lattice.rzz_errors.values()), 7),
        "rzz_below_two_cz_couplers": rzz_below,
        "sx_error": round(median(lattice.sx_errors.values()), 7),
        "duration_ns": {
            name: round(median(values.values()) * 1e9, 3) for name, values in sorted(lattice.durations.items())
        },
    }


def checked_plan(lattice: HeronLattice, name: str, k: int, requested: int, distance: int) -> dict[str, Any]:
    plan = lattice.plan_tiles(name, k, requested, min_buffer_distance=distance)
    closest = lattice.min_tile_distance(plan.tiles)
    require(closest is None or closest >= distance, f"{lattice.backend_name} {name}: tiles at distance {closest}")
    return {**plan.to_dict(lattice.num_qubits), "min_tile_distance": closest}


def build_audit(snapshot_path: Path) -> dict[str, Any]:
    require(snapshot_path.exists(), f"Snapshot {snapshot_path} does not exist")
    backends: dict[str, Any] = {}
    for bname in ROSTER:
        lattice = HeronLattice.from_snapshot(snapshot_path, bname)
        plans = {name: {**checked_plan(lattice, name, k, n, 2), "fits": use} for name, k, n, use in TILE_PLANS}
        backends[bname] = {
            "qubit_count": lattice.num_qubits,
            "undirected_edges": lattice.graph.num_edges(),
            "default_rep_delay_us": round(lattice.default_rep_delay_s * 1e6, 3),
            "rep_delay_range_us": [round(v * 1e6, 3) for v in lattice.rep_delay_range_s],
            "target_medians": target_medians(lattice),
            "tile_plans": plans,
            "guard_distance_3": checked_plan(lattice, "k5_d3", 5, 16, 3),
            "rzz_durations": lattice.rzz_duration_summary(),
            "shot_rate_ratios": {
                f"circuit_{round(c * 1e6)}us": {
                    f"rep_delay_{round(d * 1e6)}us": lattice.shot_rate_ratio(c, d) for d in REP_DELAYS_S
                }
                for c in CIRCUIT_DURATIONS_S
            },
            "rz_cz_sx_flag_couplers": {
                "cz_error_threshold": FLAG_THRESHOLD,
                "count": len(lattice.high_error_couplers(FLAG_THRESHOLD)),
            },
        }
    return {
        "schema": "heron-tile-packing-audit-v2",
        "scope": (
            "Arithmetic on the retained Target snapshot. Shot-rate ratios use assumed circuit durations and "
            "repetition delays that need a state-preparation control below the default; no ratio is a yield."
        ),
        "inputs": {
            "targets_snapshot": str(snapshot_path.relative_to(ROOT)),
            "targets_snapshot_sha256": sha256(snapshot_path),
            "roster": list(ROSTER),
        },
        "backends": backends,
    }


def expect_value_error(action: Any, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise RuntimeError(message)


def self_test() -> None:
    lattice = HeronLattice.from_snapshot(SNAPSHOT, "ibm_fez")
    for distance in (2, 3):
        tiles = lattice.find_disjoint_tiles(5, min_buffer_distance=distance, max_tiles=16)
        require(lattice.min_tile_distance(tiles) == distance, f"guard distance {distance} does not hold")
    tiles = lattice.find_disjoint_tiles(10, max_tiles=2)
    expect_value_error(
        lambda: lattice.build_multiplexed_pub([QuantumCircuit(10)] * 2, [tiles[0], tiles[0]]),
        "the composer accepted one tile twice",
    )
    qubits = tiles[0].qubits
    allowed = set(tiles[0].internal_edges)
    off = next((a, b) for a in range(10) for b in range(a + 1, 10) if (qubits[a], qubits[b]) not in allowed)
    stray = QuantumCircuit(10)
    stray.cz(*off)
    expect_value_error(lambda: lattice.build_multiplexed_pub([stray], tiles[:1]), "an off-tile CZ was placed")
    patch = lattice.route_to_tile(steane_z_syndrome_patch(error_qubit=4), tiles[0])
    require(lattice.build_multiplexed_pub([patch], tiles[:1]).num_qubits == 156, "a routed patch did not compose")
    qa, qb = lattice.high_error_couplers(FLAG_THRESHOLD)[0]
    delayed = [("rz", (qa,)), ("cz", (qa, qb)), ("delay", (qa,)), ("sx", (qa,))]
    require(not lattice.flag_rz_cz_sx(delayed), "a delay did not end the flagged run")
    expect_value_error(
        lambda: lattice.tile_parity_covariance(["0", "0"], [slice(0, 5)]), "a slice past the strings was accepted"
    )
    expect_value_error(lambda: lattice.shot_rate_ratio(5e-6, 3e-3), "a delay outside rep_delay_range was accepted")
    require(lcu_zero_product_witness().metadata["p_success"] == 0.0, "the default witness is not the dark pair")
    require(bent_hidden_shift_circuit(4).metadata["polar_rank"] == 4, "bent hidden shift polar rank mismatch")
    require(fano_plane_incidence_matrix().shape == (7, 7), "Fano plane matrix shape mismatch")
    require(steane_coherent_syndrome_patch(1).num_qubits == 10, "coherent Steane patch qubit count mismatch")
    require(
        hoeffding_model_discrimination({"0": 8000}, {"1": 8000}, alphabet_size=2)["models_distinguishable"],
        "Hoeffding model discrimination failed",
    )
    coords_cov = HeronLattice.tile_parity_covariance(
        ["00", "11"],
        [slice(0, 1), slice(1, 2)],
        tile_coords=[(0.0, 0.0), (3.0, 4.0)],
    )
    require(coords_cov["distance_matrix"][0][1] == 5.0, "coordinate distance mismatch")
    require(sedenion_associator_witness(1, 2, 4).num_qubits == 5, "sedenion witness qubit count mismatch")
    print("self-test: guard distances, composer, routing, flag, covariance, and elevated runs hold")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write audit JSON to path")
    mode.add_argument("--check", type=Path, help="verify against retained audit JSON")
    mode.add_argument("--self-test", action="store_true", help="run self-test validation")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0

    rendered = json.dumps(build_audit(SNAPSHOT), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(f"Wrote tile packing audit to {args.out}")
    if args.check:
        require(args.check.exists(), f"Check file {args.check} does not exist")
        require(
            args.check.read_text(encoding="utf-8") == rendered, f"Audit in {args.check} differs from recomputed audit"
        )
        print(f"tile packing audit check: passed against {args.check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
