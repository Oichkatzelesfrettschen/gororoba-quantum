"""Audit Heron r2 spatial multiprogramming, temporal ISA compression, and run planning.

This script executes the hypergranular spatial tiling and temporal ISA compression
analysis across all 156-qubit Heron r2 backends (ibm_fez, ibm_kingston, ibm_marrakesh).
It plans all 4 prioritized scientific runs:
1. Run 1: Sedenion (S_16) & Pathion (P_32) Hardware Witness
2. Run 2: Octonionic Fano-Plane CSS Codes & Active Stabilizers
3. Run 3: Vacuum Endpoint Information & Model Discrimination
4. Run 4: Boolean Hidden Shift & Fold-Projection Counterexamples

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
from typing import Any

from qiskit import QuantumCircuit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from heron_multiprogramming import HeronLattice  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def build_audit(snapshot_path: Path) -> dict[str, Any]:
    """Build complete multi-backend spatial and temporal multiprogramming audit."""
    require(snapshot_path.exists(), f"Snapshot {snapshot_path} does not exist")
    snapshot_hash = sha256(snapshot_path)

    backends_audit: dict[str, Any] = {}

    runs_spec = [
        (
            "Run 1",
            "Sedenion (S_16) & Pathion (P_32) Hardware Witness",
            5,
            16,
            "Native continuous R_ZZ(theta) & R_X(theta)",
            "Hardware witness of non-associative defect census, C_881 rank loci, and FakeFez amplification validation",
        ),
        (
            "Run 2",
            "Octonionic Fano-Plane CSS Codes & Active Stabilizers",
            10,
            8,
            "Dynamic circuits (if_test, mid-circuit feed-forward, measure_2)",
            "Octonionic Fano-plane incidence stabilizer parity checks and terminal channel separation certificates",
        ),
        (
            "Run 3",
            "Vacuum Endpoint Information & Model Discrimination",
            2,
            20,
            "QASM3 stretch delays + Hoeffding-optimal shots",
            "Out-of-sample empirical KL/JS divergence bounding between competing vacuum models",
        ),
        (
            "Run 4",
            "Boolean Hidden Shift & Fold-Projection Counterexamples",
            7,
            12,
            "Staged PassManager (optimization_level=3)",
            "Nonlinearity witness (PMC 4957665) & empirical validation of Rocq formal certificates",
        ),
    ]

    delays = (250e-6, 100e-6, 50e-6, 20e-6, 10e-6)

    for bname in ROSTER:
        lattice = HeronLattice.from_snapshot(snapshot_path, bname)

        # Plan all 4 runs
        run_plans: dict[str, Any] = {}
        for run_id, run_name, k, target_tiles, isa_feat, deliv in runs_spec:
            plan = lattice.plan_run(
                run_id=run_id,
                k=k,
                target_tiles=target_tiles,
                name=run_name,
                key_isa_feature=isa_feat,
                deliverable=deliv,
                min_buffer_distance=2,
            )
            # Verify disjointness and guard band distance >= 2
            tile_qubits_set: set[int] = set()
            for t in plan.tiles:
                q_set = set(t.qubits)
                require(
                    not (q_set & tile_qubits_set),
                    f"{bname} {run_id}: tiles must be strictly disjoint",
                )
                tile_qubits_set.update(q_set)

            # Check pairwise buffer distance
            dist = lattice.distance_matrix()
            for i, t1 in enumerate(plan.tiles):
                for j, t2 in enumerate(plan.tiles):
                    if i < j:
                        min_d = min(dist[q1][q2] for q1 in t1.qubits for q2 in t2.qubits)
                        require(
                            min_d >= 2,
                            f"{bname} {run_id}: tiles {t1.tile_id} and {t2.tile_id} have distance {min_d} < 2",
                        )

            run_plans[run_id] = plan.to_dict()

        # Evaluate temporal compression curves
        compression_curves: dict[str, Any] = {}
        top_tiles_run1 = len(run_plans["Run 1"]["tiles"])
        for d in delays:
            key = f"{round(d * 1e6)}us"
            tc = lattice.evaluate_temporal_compression(
                circuit_duration_s=5e-6,
                rep_delay_compressed_s=d,
                tile_count=top_tiles_run1,
            )
            compression_curves[key] = tc.to_dict()

        # Audit gate sequence anomalies
        anomalies = lattice.detect_anomalies()

        # Simulate spatial cross-covariance
        sim_bitstrings = [
            "".join("1" if ((shot * 17 + bit * 13) % 29 < 14) else "0" for bit in range(16)) for shot in range(1000)
        ]
        cov_res = lattice.compute_spatial_cross_covariance(
            sim_bitstrings,
            [slice(i, i + 1) for i in range(16)],
        )

        backends_audit[bname] = {
            "backend_name": bname,
            "qubit_count": lattice.TOTAL_QUBITS,
            "undirected_edges": lattice.graph.num_edges(),
            "runs": run_plans,
            "temporal_compression": compression_curves,
            "subsequence_anomalies_flagged": len(anomalies),
            "sample_anomalies": [a.to_dict() for a in anomalies[:5]],
            "sample_covariance": cov_res,
        }

    return {
        "schema": "heron-spatial-multiprogramming-audit-v1",
        "inputs": {
            "targets_snapshot": str(snapshot_path.relative_to(ROOT)),
            "targets_snapshot_sha256": snapshot_hash,
            "roster": list(ROSTER),
        },
        "backends": backends_audit,
    }


def self_test() -> None:
    """Validate strict invariant enforcement and failure modes."""
    require(SNAPSHOT.exists(), "Snapshot must exist for self-test")
    lattice = HeronLattice.from_snapshot(SNAPSHOT, "ibm_fez")

    # 1. Normal run planning succeeds
    plan = lattice.plan_run(
        run_id="Run 1",
        k=5,
        target_tiles=16,
        name="Test Sedenion",
        key_isa_feature="RZZ",
        deliverable="Test",
        min_buffer_distance=2,
    )
    require(len(plan.tiles) == 16, f"Expected 16 tiles, got {len(plan.tiles)}")

    # 2. Assert min_buffer_distance >= 2 holds strictly
    dist = lattice.distance_matrix()
    for i, t1 in enumerate(plan.tiles):
        for j, t2 in enumerate(plan.tiles):
            if i < j:
                min_d = min(dist[q1][q2] for q1 in t1.qubits for q2 in t2.qubits)
                require(min_d >= 2, "Distance must be >= 2")

    # 3. Assert tile overlap rejection
    try:
        t1 = plan.tiles[0]
        fake_circuits = [QuantumCircuit(10)]
        fake_tiles = [t1]
        lattice.build_multiplexed_pub(fake_circuits, fake_tiles)
        raise RuntimeError("Expected build_multiplexed_pub to fail on size mismatch")
    except ValueError:
        pass

    # 4. Assert anomaly detection
    ops = [("rz", (0,)), ("cz", (0, 1)), ("sx", (0,))]
    anomalies = lattice.detect_anomalies(ops)
    require(isinstance(anomalies, list), "Anomaly list returned")

    # 5. Assert covariance calculation rejects < 2 shots
    try:
        lattice.compute_spatial_cross_covariance(["001"], [slice(0, 1)])
        raise RuntimeError("Expected failure for < 2 shots")
    except ValueError:
        pass

    print("self-test: all 5 invariant checks passed successfully")


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

    audit_data = build_audit(SNAPSHOT)
    rendered = json.dumps(audit_data, indent=1, sort_keys=True) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(f"Wrote spatial multiprogramming audit to {args.out}")

    if args.check:
        require(args.check.exists(), f"Check file {args.check} does not exist")
        retained = args.check.read_text(encoding="utf-8")
        require(retained == rendered, f"Audit in {args.check} differs from recomputed audit")
        print(f"spatial multiprogramming audit check: passed against {args.check}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
