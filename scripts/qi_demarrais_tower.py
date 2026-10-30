"""Quantum Inspire QX (1024D DekaVoudon) and Tuna-17 (8192D DekatrisVoudon) De Marrais tower suite.

Implements the 10-qubit QXsinglenodesimulator (1024D DekaVoudon, 2048 shots) and
17-qubit Tuna-17 (8192D DekatrisVoudon, 75536 shots) graph-state stabilizer and
two-path zero-divisor interference experiments across the Robert de Marrais
structures:
  1. dekatrisvoudon-8192d-midden.cq: 17-qubit bipartite graph state across 18
     native Tuna-17 CZ couplers with Zaslavsky lanyard oracle S_midden = {1, 8, 14},
     producing exact 2-path destructive zero-divisor interference on q[4], q[11],
     and q[12] (|N(a) cap S| = 2 == 0 mod 2) while driving q[0], q[5], and q[16]
     bright (|N(a) cap S| = 1).
  2. cowbird-mandala-roundabout.cq: Identical 18-coupler entangling skeleton with
     Cowbird Octonion Egg / Pathion Mandala oracle S_cowbird = {2, 7, 15},
     switching the 2048D/4096D/8192D Voudon qubits (q[10], q[11], q[12]) from
     (0, 0, 0) dark to (1, 1, 1) bright.
  3. zaslavsky-dmz-calibration.cq: Identical 18-coupler entangling skeleton with
     Pathion Sand Mandala DMZ / Roundabout control oracle S_dmz = {3, 9, 13},
     producing 2-path destructive interference on q[6] (|N(6) cap {3, 9}| = 2 == 0)
     and isolating q[10] = 1 as the lone bright witness while all 9 B-partition
     sentinel qubits return to 0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings(
    "ignore",
    message=r"builtin type (SwigPyPacked|SwigPyObject|swigvarlink) has no __module__ attribute",
    category=DeprecationWarning,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "gororoba_quantum") not in sys.path:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from qi_platform import HARDWARE_BATCH_CIRCUITS  # noqa: E402

import parallel  # noqa: E402
from demarrais_structures import (  # noqa: E402
    certify_all_demarrais_structures,
    require,
)

CATALOGUE_PATH = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
CASES_ROOT = ROOT / "results/quantum_inspire/cases"

TUNA_BACKEND = "tuna_17"
TUNA_BACKEND_TYPE_ID = 7
TUNA_NQUBITS = 17
TUNA_SHOTS = 75536

QX_BACKEND = "QXsinglenodesimulator"
QX_BACKEND_TYPE_ID = 1
QX_NQUBITS = 10
QX_SHOTS = 2048

# Exact 24 undirected couplers of Tuna-17 (bipartite between A_EVEN and B_ODD).
TUNA17_ALL_COUPLERS: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (1, 4),
    (2, 4),
    (2, 5),
    (3, 5),
    (3, 6),
    (4, 7),
    (4, 8),
    (5, 8),
    (5, 9),
    (6, 9),
    (7, 10),
    (7, 11),
    (8, 11),
    (8, 12),
    (9, 12),
    (10, 13),
    (11, 13),
    (11, 14),
    (12, 14),
    (12, 15),
    (14, 16),
    (15, 16),
)

# 18-coupler spanning bipartite subgraph covering all 17 qubits of Tuna-17:
# Partition A (8 data/character qubits): {0, 4, 5, 6, 10, 11, 12, 16}
# Partition B (9 oracle/syndrome hubs):  {1, 2, 3, 7, 8, 9, 13, 14, 15}
TUNA17_A_QUBITS: tuple[int, ...] = (0, 4, 5, 6, 10, 11, 12, 16)
TUNA17_B_QUBITS: tuple[int, ...] = (1, 2, 3, 7, 8, 9, 13, 14, 15)
TUNA17_MIDDEN_COUPLERS: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (1, 4),
    (2, 5),
    (3, 6),
    (4, 8),
    (5, 8),
    (6, 9),
    (7, 10),
    (7, 11),
    (8, 11),
    (8, 12),
    (10, 13),
    (11, 14),
    (12, 14),
    (12, 15),
    (14, 16),
    (15, 16),
)

TUNA17_CIRCUIT_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("dekatrisvoudon-8192d-midden.cq", "midden", (1, 8, 14)),
    ("cowbird-mandala-roundabout.cq", "cowbird", (2, 7, 15)),
    ("zaslavsky-dmz-calibration.cq", "dmz", (3, 9, 13)),
)

TUNA17_BATCH01_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("01-control-sedenion-pathion-32d.cq", "ctrl_low_32d", (1, 2)),
    ("02-control-chingon-routon-voudon-4096d.cq", "ctrl_mid_4096d", (3, 8, 13)),
    ("03-dekatrisvoudon-8192d-pure-shell.cq", "explore_8192d_pure", (8, 14, 15)),
)

TUNA17_BATCH02_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("04-dekatrisvoudon-8192d-catamaran-lanyard.cq", "explore_8192d_catamaran", (1, 2, 8, 15)),
    ("05-dekatrisvoudon-8192d-dmz-shell.cq", "explore_8192d_dmz", (2, 8, 14)),
    ("06-dekatrisvoudon-8192d-sleeper-null.cq", "null_8192d_sleeper", ()),
)

# 10-qubit QX (1024D DekaVoudon) bipartite subgraph:
# Partition A (5 data/character qubits): {0, 2, 3, 6, 7}
# Partition B (5 oracle/syndrome hubs):  {1, 4, 5, 8, 9}
QX10_A_QUBITS: tuple[int, ...] = (0, 2, 3, 6, 7)
QX10_B_QUBITS: tuple[int, ...] = (1, 4, 5, 8, 9)
QX10_MIDDEN_COUPLERS: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 4),
    (2, 1),
    (2, 5),
    (3, 4),
    (3, 8),
    (6, 5),
    (6, 9),
    (7, 8),
    (7, 9),
)

QX10_CIRCUIT_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("dekavoudon-1024d-midden.cq", "midden", (1, 5, 9)),
    ("cowbird-mandala-1024d.cq", "cowbird", (1, 4, 8)),
    ("roundabout-dmz-1024d.cq", "dmz", (4, 8, 9)),
)

QX10_BATCH01_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("01-control-sedenion-pathion-32d.cq", "ctrl_low_32d", (1, 4)),
    ("02-control-chingon-routon-512d.cq", "ctrl_mid_512d", (4, 5, 8)),
    ("03-dekavoudon-1024d-pure-shell.cq", "explore_1024d_pure", (5, 8, 9)),
)

QX10_BATCH02_SPECS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("04-dekavoudon-1024d-catamaran-lanyard.cq", "explore_1024d_catamaran", (1, 4, 8, 9)),
    ("05-dekavoudon-1024d-dmz-shell.cq", "explore_1024d_dmz", (1, 5, 8)),
    ("06-dekavoudon-1024d-sleeper-null.cq", "null_1024d_sleeper", ()),
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def validate_catalogue(catalogue_path: Path = CATALOGUE_PATH) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate Tuna-17 and QX backend definitions against the retained QI catalogue."""
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    require(isinstance(catalogue, dict) and isinstance(catalogue.get("backend_types"), list), "malformed QI catalogue")
    by_id = {row["identifier"]: row for row in catalogue["backend_types"] if isinstance(row, dict)}
    require(TUNA_BACKEND in by_id and QX_BACKEND in by_id, "missing Tuna-17 or QX backend in catalogue")
    tuna = by_id[TUNA_BACKEND]
    qx = by_id[QX_BACKEND]
    require(tuna["id"] == TUNA_BACKEND_TYPE_ID and tuna["nqubits"] == TUNA_NQUBITS, "Tuna-17 width/id mismatch")
    require(tuna["max_number_of_shots"] >= TUNA_SHOTS, "Tuna-17 max shots below 75536")
    require(qx["id"] == QX_BACKEND_TYPE_ID and qx["nqubits"] == QX_NQUBITS, "QX width/id mismatch")
    require(qx["max_number_of_shots"] >= QX_SHOTS, "QX max shots below 2048")
    tuna_edges = {tuple(sorted(edge)) for edge in tuna["topology"]}
    require(set(TUNA17_ALL_COUPLERS) == tuna_edges, "Tuna-17 topology differs from retained catalogue")
    require(set(TUNA17_MIDDEN_COUPLERS) <= tuna_edges, "Midden couplers must be native Tuna-17 edges")
    return tuna, qx


def ideal_target_bits(
    nqubits: int,
    a_qubits: tuple[int, ...],
    b_qubits: tuple[int, ...],
    couplers: tuple[tuple[int, int], ...],
    oracle_hubs: tuple[int, ...],
) -> dict[int, int]:
    """Compute the exact deterministic stabilizer output bit for every qubit 0..nqubits-1.

    Under U = H^{otimes n} U_CZ (prod_{b in S} X_b) U_CZ H^{otimes n} |0>^{otimes n}:
      - Every b in B_QUBITS returns deterministically to 0 (syndrome sentinel).
      - Every a in A_QUBITS outputs |N(a) cap S| mod 2 (1 for odd-path constructive,
        0 for 2-path destructive zero-divisor interference or 0-path DMZ).
    """
    require(set(a_qubits) | set(b_qubits) == set(range(nqubits)), "bipartition must cover all qubits")
    require(not (set(a_qubits) & set(b_qubits)), "bipartition sets A and B must be disjoint")
    require(set(oracle_hubs) <= set(b_qubits), "oracle hubs must belong to partition B")
    neighbors: dict[int, set[int]] = {a: set() for a in a_qubits}
    for u, v in couplers:
        if u in neighbors and v in b_qubits:
            neighbors[u].add(v)
        elif v in neighbors and u in b_qubits:
            neighbors[v].add(u)
        else:
            raise ValueError(f"coupler ({u}, {v}) is not bipartite between A and B")
    bits: dict[int, int] = {}
    oracle_set = set(oracle_hubs)
    for q in range(nqubits):
        if q in b_qubits:
            bits[q] = 0
        else:
            bits[q] = len(neighbors[q] & oracle_set) % 2
    return bits


def ideal_shot_string(bits: dict[int, int]) -> str:
    """Render the ideal shot string in Quantum Inspire bit order (qubit 0 rightmost)."""
    nqubits = len(bits)
    return "".join(str(bits[nqubits - 1 - k]) for k in range(nqubits))


def render_cqasm_circuit(
    nqubits: int,
    couplers: tuple[tuple[int, int], ...],
    oracle_hubs: tuple[int, ...],
    comment: str,
) -> str:
    """Render cQASM 3.0 source with explicit barriers so OpenSquirrel preserves gate sequences."""
    lines = [
        "version 3.0",
        "",
        f"// {comment}",
        f"qubit[{nqubits}] q",
        f"bit[{nqubits}] b",
        "",
    ]
    for q in range(nqubits):
        lines.append(f"H q[{q}]")
    lines.append("barrier q")
    for u, v in couplers:
        lines.append(f"CZ q[{u}], q[{v}]")
    lines.append("barrier q")
    for hub in oracle_hubs:
        lines.append(f"X q[{hub}]")
    lines.append("barrier q")
    for u, v in couplers:
        lines.append(f"CZ q[{u}], q[{v}]")
    lines.append("barrier q")
    for q in range(nqubits):
        lines.append(f"H q[{q}]")
    lines.append("barrier q")
    lines.append("b = measure q")
    lines.append("")
    return "\n".join(lines)


def build_suite_files() -> dict[str, dict[str, str]]:
    """Build the Tuna-17 (8192D, 75536 shots) and QX (1024D, 2048 shots) case trees (batch-00 and batch-01)."""
    tuna_cat, qx_cat = validate_catalogue()
    cert = certify_all_demarrais_structures()
    require(cert["tower_max_dim"] == 8192 and cert["tower_max_name"] == "DekatrisVoudon", "8192D certification failed")

    suite: dict[str, dict[str, str]] = {}
    for case_name, backend, backend_id, nqubits, shots, a_qubits, b_qubits, couplers, batch_map in (
        (
            "demarrais_tuna17_8192d",
            TUNA_BACKEND,
            tuna_cat["id"],
            TUNA_NQUBITS,
            TUNA_SHOTS,
            TUNA17_A_QUBITS,
            TUNA17_B_QUBITS,
            TUNA17_MIDDEN_COUPLERS,
            (
                ("batch-00", TUNA17_CIRCUIT_SPECS),
                ("batch-01", TUNA17_BATCH01_SPECS),
                ("batch-02", TUNA17_BATCH02_SPECS),
            ),
        ),
        (
            "demarrais_qx_1024d",
            QX_BACKEND,
            qx_cat["id"],
            QX_NQUBITS,
            QX_SHOTS,
            QX10_A_QUBITS,
            QX10_B_QUBITS,
            QX10_MIDDEN_COUPLERS,
            (
                ("batch-00", QX10_CIRCUIT_SPECS),
                ("batch-01", QX10_BATCH01_SPECS),
                ("batch-02", QX10_BATCH02_SPECS),
            ),
        ),
    ):
        files: dict[str, str] = {}
        series_batches: list[dict[str, Any]] = []
        for batch_name, specs in batch_map:
            require(len(specs) <= HARDWARE_BATCH_CIRCUITS, f"{batch_name} exceeds HARDWARE_BATCH_CIRCUITS")
            circuit_rows: list[dict[str, Any]] = []
            for filename, kind, oracle_hubs in specs:
                target_bits = ideal_target_bits(nqubits, a_qubits, b_qubits, couplers, oracle_hubs)
                shot_str = ideal_shot_string(target_bits)
                source = render_cqasm_circuit(
                    nqubits=nqubits,
                    couplers=couplers,
                    oracle_hubs=oracle_hubs,
                    comment=(
                        f"{case_name} {batch_name} kind={kind} oracle_hubs={list(oracle_hubs)} ideal_shot={shot_str}"
                    ),
                )
                files[f"{batch_name}/{filename}"] = source
                two_path_dark = sorted(
                    a
                    for a in a_qubits
                    if sum(1 for u, v in couplers if (u == a and v in oracle_hubs) or (v == a and u in oracle_hubs))
                    == 2
                )
                one_path_bright = sorted(a for a in a_qubits if target_bits[a] == 1)
                zero_path_dmz = sorted(
                    a
                    for a in a_qubits
                    if sum(1 for u, v in couplers if (u == a and v in oracle_hubs) or (v == a and u in oracle_hubs))
                    == 0
                )
                circuit_rows.append(
                    {
                        "file": filename,
                        "kind": kind,
                        "nqubits": nqubits,
                        "sha256": _sha256_text(source),
                        "oracle_hubs": list(oracle_hubs),
                        "ideal_bits_by_qubit": {str(q): b for q, b in target_bits.items()},
                        "ideal_shot_string": shot_str,
                        "two_path_destructive_dark_qubits": two_path_dark,
                        "one_path_constructive_bright_qubits": one_path_bright,
                        "zero_path_dmz_qubits": zero_path_dmz,
                        "sentinel_zero_qubits": list(b_qubits),
                    }
                )
            batch_manifest = {
                "schema": "qi-demarrais-tower-cases-v1",
                "batch": batch_name,
                "backend": backend,
                "backend_type_id": backend_id,
                "nqubits": nqubits,
                "shots": shots,
                "cayley_dickson_target_dim": 8192 if nqubits == 17 else 1024,
                "cayley_dickson_target_name": "DekatrisVoudon" if nqubits == 17 else "DekaVoudon",
                "bipartition_a_data_qubits": list(a_qubits),
                "bipartition_b_sentinel_qubits": list(b_qubits),
                "couplers": [list(edge) for edge in couplers],
                "certificate": cert,
                "circuits": circuit_rows,
            }
            files[f"{batch_name}/cases.json"] = json.dumps(batch_manifest, indent=1) + "\n"
            series_batches.append({"batch": batch_name, "files": [row["file"] for row in circuit_rows]})
        series_manifest = {
            "schema": "qi-demarrais-tower-series-v1",
            "backend": backend,
            "backend_type_id": backend_id,
            "nqubits": nqubits,
            "shots": shots,
            "batches": series_batches,
        }
        files["cases.json"] = json.dumps(series_manifest, indent=1) + "\n"
        suite[case_name] = files
    return suite


def write_suite(out_root: Path = CASES_ROOT) -> list[Path]:
    """Write both case directories under results/quantum_inspire/cases/."""
    suite = build_suite_files()
    written: list[Path] = []
    for case_name, files in suite.items():
        case_dir = out_root / case_name
        for rel_path, content in files.items():
            target = case_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        written.append(case_dir)
    return written


def check_suite(out_root: Path = CASES_ROOT) -> None:
    """Verify retained case files match freshly generated bytes."""
    suite = build_suite_files()
    for case_name, files in suite.items():
        case_dir = out_root / case_name
        for rel_path, content in files.items():
            target = case_dir / rel_path
            require(target.is_file(), f"missing generated file {target}")
            require(target.read_text(encoding="utf-8") == content, f"stale file {target}")


def _bit_at(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def analyze_batch_run(run_dir: Path) -> dict[str, Any]:
    """Analyze a collected Quantum Inspire batch run directory."""
    cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    require(cases.get("schema") == "qi-demarrais-tower-cases-v1", "unexpected case manifest schema")
    nqubits = int(cases["nqubits"])
    a_qubits = [int(q) for q in cases["bipartition_a_data_qubits"]]
    b_qubits = [int(q) for q in cases["bipartition_b_sentinel_qubits"]]

    circuit_reports: dict[str, Any] = {}
    for row in cases["circuits"]:
        filename = row["file"]
        raw_path = run_dir / "raw" / f"{filename}.json"
        shots: list[str] = json.loads(raw_path.read_text(encoding="utf-8"))
        require(len(shots) == int(cases["shots"]), f"{filename}: shot count {len(shots)} != {cases['shots']}")
        ideal_shot = row["ideal_shot_string"]
        exact_matches = sum(1 for s in shots if s == ideal_shot)
        ideal_bits = {int(q): int(b) for q, b in row["ideal_bits_by_qubit"].items()}

        per_qubit_p1: dict[str, float] = {}
        per_qubit_accuracy: dict[str, float] = {}
        for q in range(nqubits):
            ones = sum(_bit_at(s, q) for s in shots)
            p1 = ones / len(shots)
            per_qubit_p1[str(q)] = p1
            per_qubit_accuracy[str(q)] = p1 if ideal_bits[q] == 1 else (1.0 - p1)

        two_path_qubits = [int(q) for q in row["two_path_destructive_dark_qubits"]]
        one_path_qubits = [int(q) for q in row["one_path_constructive_bright_qubits"]]
        zero_path_qubits = [int(q) for q in row["zero_path_dmz_qubits"]]

        mean_one_path_p1 = (
            sum(per_qubit_p1[str(q)] for q in one_path_qubits) / len(one_path_qubits) if one_path_qubits else 0.0
        )
        mean_two_path_p1 = (
            sum(per_qubit_p1[str(q)] for q in two_path_qubits) / len(two_path_qubits) if two_path_qubits else 0.0
        )
        mean_zero_path_p1 = (
            sum(per_qubit_p1[str(q)] for q in zero_path_qubits) / len(zero_path_qubits) if zero_path_qubits else 0.0
        )
        mean_sentinel_p0 = sum(1.0 - per_qubit_p1[str(q)] for q in b_qubits) / len(b_qubits)
        sentinel_all_zero_rate = sum(1 for s in shots if all(_bit_at(s, q) == 0 for q in b_qubits)) / len(shots)

        # Post-selected on all 9 (or 5) B-partition syndrome sentinels reading 0
        heralded_shots = [s for s in shots if all(_bit_at(s, q) == 0 for q in b_qubits)]
        heralded_one_path_p1 = (
            sum(sum(_bit_at(s, q) for s in heralded_shots) / len(heralded_shots) for q in one_path_qubits)
            / len(one_path_qubits)
            if heralded_shots and one_path_qubits
            else None
        )
        heralded_two_path_p1 = (
            sum(sum(_bit_at(s, q) for s in heralded_shots) / len(heralded_shots) for q in two_path_qubits)
            / len(two_path_qubits)
            if heralded_shots and two_path_qubits
            else None
        )

        circuit_reports[row["kind"]] = {
            "file": filename,
            "shots": len(shots),
            "ideal_shot_string": ideal_shot,
            "exact_17q_or_10q_match_probability": exact_matches / len(shots),
            "mean_one_path_bright_p1": mean_one_path_p1,
            "mean_two_path_destructive_dark_p1": mean_two_path_p1,
            "mean_zero_path_dmz_dark_p1": mean_zero_path_p1,
            "interference_contrast_one_minus_two_path": mean_one_path_p1 - mean_two_path_p1,
            "mean_sentinel_syndrome_p0": mean_sentinel_p0,
            "sentinel_all_zero_herald_rate": sentinel_all_zero_rate,
            "heralded_one_path_bright_p1": heralded_one_path_p1,
            "heralded_two_path_destructive_dark_p1": heralded_two_path_p1,
            "heralded_interference_contrast": (
                heralded_one_path_p1 - heralded_two_path_p1
                if heralded_one_path_p1 is not None and heralded_two_path_p1 is not None
                else None
            ),
            "per_qubit_p1": per_qubit_p1,
            "per_qubit_accuracy": per_qubit_accuracy,
        }

    # Cross-circuit switching contrast on the target qubits
    voudon_switch_qubits = [11, 12] if nqubits == 17 else [6, 7]
    extra_metrics: dict[str, Any] = {}
    if "cowbird" in circuit_reports and "midden" in circuit_reports:
        voudon_switching_contrast = sum(
            circuit_reports["cowbird"]["per_qubit_p1"][str(q)] - circuit_reports["midden"]["per_qubit_p1"][str(q)]
            for q in voudon_switch_qubits
        ) / len(voudon_switch_qubits)
        extra_metrics["voudon_switching_contrast_cowbird_minus_midden"] = voudon_switching_contrast
    elif "explore_8192d_pure" in circuit_reports or "explore_1024d_pure" in circuit_reports:
        pure_key = "explore_8192d_pure" if nqubits == 17 else "explore_1024d_pure"
        mid_key = "ctrl_mid_4096d" if nqubits == 17 else "ctrl_mid_512d"
        low_key = "ctrl_low_32d"
        if nqubits == 17:
            # On Tuna-17, q[12] is 1 in c0 and 0 in c2
            shell_contrast = (
                circuit_reports[pure_key]["per_qubit_p1"]["12"] - circuit_reports[low_key]["per_qubit_p1"]["12"]
            )
            mid_vs_pure = (
                circuit_reports[mid_key]["per_qubit_p1"]["11"] - circuit_reports[pure_key]["per_qubit_p1"]["11"]
            )
        else:
            # On QX-10, q[7] is 1 in c1 and 0 in c2
            shell_contrast = (
                circuit_reports[mid_key]["per_qubit_p1"]["7"] - circuit_reports[low_key]["per_qubit_p1"]["7"]
            )
            mid_vs_pure = circuit_reports[mid_key]["per_qubit_p1"]["7"] - circuit_reports[pure_key]["per_qubit_p1"]["7"]
        extra_metrics["shell_8192d_or_1024d_vs_32d_control_contrast"] = shell_contrast
        extra_metrics["mid_tower_vs_pure_shell_switching_contrast"] = mid_vs_pure
    else:
        cat_key = "explore_8192d_catamaran" if nqubits == 17 else "explore_1024d_catamaran"
        dmz_key = "explore_8192d_dmz" if nqubits == 17 else "explore_1024d_dmz"
        null_key = "null_8192d_sleeper" if nqubits == 17 else "null_1024d_sleeper"
        target_q = 16 if nqubits == 17 else 7
        cat_vs_null = (
            circuit_reports[cat_key]["mean_one_path_bright_p1"]
            - circuit_reports[null_key]["mean_zero_path_dmz_dark_p1"]
        )
        dmz_vs_null = (
            circuit_reports[dmz_key]["per_qubit_p1"][str(target_q)]
            - circuit_reports[null_key]["per_qubit_p1"][str(target_q)]
        )
        cat_minus_dmz = sum(
            circuit_reports[cat_key]["per_qubit_p1"][str(q)] - circuit_reports[dmz_key]["per_qubit_p1"][str(q)]
            for q in voudon_switch_qubits
        ) / len(voudon_switch_qubits)
        extra_metrics["catamaran_vs_sleeper_null_contrast"] = cat_vs_null
        extra_metrics["dmz_shell_vs_sleeper_null_contrast"] = dmz_vs_null
        extra_metrics["catamaran_minus_dmz_switching_contrast"] = cat_minus_dmz

    return {
        "schema": "qi-demarrais-tower-analysis-v1",
        "batch": cases.get("batch", "batch-00"),
        "backend": cases["backend"],
        "backend_type_id": cases["backend_type_id"],
        "nqubits": nqubits,
        "shots": cases["shots"],
        "cayley_dickson_target_dim": cases["cayley_dickson_target_dim"],
        "cayley_dickson_target_name": cases["cayley_dickson_target_name"],
        "bipartition_a_data_qubits": a_qubits,
        "bipartition_b_sentinel_qubits": b_qubits,
        "voudon_switch_qubits": voudon_switch_qubits,
        **extra_metrics,
        "circuits": circuit_reports,
    }


def _run_qxelarator_circuit(
    item: tuple[str, str, str, int, tuple[tuple[int, int], ...], tuple[int, ...]],
) -> tuple[str, str, dict[str, int]]:
    """Execute one cQASM 3.0 circuit on local qxelarator (under QI_PYTHON) or Qiskit Statevector (under $PYTHON)."""
    case_name, filename, source, nqubits, couplers, oracle_hubs = item
    try:
        import qxelarator

        result = qxelarator.execute_string(source, iterations=4)
        counts = getattr(result, "results", {})
        return case_name, filename, {str(k): int(v) for k, v in counts.items()}
    except ModuleNotFoundError:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        qc = QuantumCircuit(nqubits)
        for q in range(nqubits):
            qc.h(q)
        for u, v in couplers:
            qc.cz(u, v)
        for hub in oracle_hubs:
            qc.x(hub)
        for u, v in couplers:
            qc.cz(u, v)
        for q in range(nqubits):
            qc.h(q)
        probs = Statevector.from_instruction(qc).probabilities_dict()
        top_bitstring, top_prob = max(probs.items(), key=lambda kv: kv[1])
        require(abs(top_prob - 1.0) < 1e-12, f"{case_name}/{filename}: statevector top_prob {top_prob} != 1.0")
        return case_name, filename, {str(top_bitstring): 4}


def run_self_test() -> dict[str, Any]:
    """Verify suite generation and exact ideal bitstring reproduction on qxelarator or Qiskit Statevector."""
    suite = build_suite_files()
    items: list[tuple[str, str, str, int, tuple[tuple[int, int], ...], tuple[int, ...]]] = []
    expected_shots: dict[tuple[str, str], str] = {}
    for case_name, files in suite.items():
        for batch_name in ("batch-00", "batch-01", "batch-02"):
            manifest = json.loads(files[f"{batch_name}/cases.json"])
            nqubits = int(manifest["nqubits"])
            couplers = tuple((int(e[0]), int(e[1])) for e in manifest["couplers"])
            for row in manifest["circuits"]:
                fname = row["file"]
                hubs = tuple(int(h) for h in row["oracle_hubs"])
                items.append(
                    (case_name, f"{batch_name}/{fname}", files[f"{batch_name}/{fname}"], nqubits, couplers, hubs)
                )
                expected_shots[(case_name, f"{batch_name}/{fname}")] = row["ideal_shot_string"]

    outputs = parallel.ordered_map(_run_qxelarator_circuit, items, min_items=1)
    verified = 0
    for case_name, fname, counts in outputs:
        require(
            counts == {expected_shots[(case_name, fname)]: 4},
            f"{case_name}/{fname}: counts {counts} != {{{expected_shots[(case_name, fname)]!r}: 4}}",
        )
        verified += 1
    return {
        "cases_built": len(suite),
        "circuits_built": len(items),
        "qxelarator_verified_circuits": verified,
        "tuna17_batch00_ideal_shots": {
            fname: expected_shots[("demarrais_tuna17_8192d", f"batch-00/{fname}")]
            for fname, _, _ in TUNA17_CIRCUIT_SPECS
        },
        "tuna17_batch01_ideal_shots": {
            fname: expected_shots[("demarrais_tuna17_8192d", f"batch-01/{fname}")]
            for fname, _, _ in TUNA17_BATCH01_SPECS
        },
        "tuna17_batch02_ideal_shots": {
            fname: expected_shots[("demarrais_tuna17_8192d", f"batch-02/{fname}")]
            for fname, _, _ in TUNA17_BATCH02_SPECS
        },
        "qx10_batch00_ideal_shots": {
            fname: expected_shots[("demarrais_qx_1024d", f"batch-00/{fname}")] for fname, _, _ in QX10_CIRCUIT_SPECS
        },
        "qx10_batch01_ideal_shots": {
            fname: expected_shots[("demarrais_qx_1024d", f"batch-01/{fname}")] for fname, _, _ in QX10_BATCH01_SPECS
        },
        "qx10_batch02_ideal_shots": {
            fname: expected_shots[("demarrais_qx_1024d", f"batch-02/{fname}")] for fname, _, _ in QX10_BATCH02_SPECS
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run algebraic + qxelarator self-test")
    parser.add_argument("--build", action="store_true", help="Write QI case directories")
    parser.add_argument("--check", action="store_true", help="Check retained QI case directories")
    parser.add_argument("--analyze", type=Path, help="Analyze a collected QI run directory")
    parser.add_argument("--out", type=Path, help="Optional output path for --analyze")
    args = parser.parse_args(argv)

    if args.self_test:
        print(json.dumps(run_self_test(), indent=2))
        return 0
    if args.build:
        written = write_suite()
        for path in written:
            print(path.relative_to(ROOT))
        return 0
    if args.check:
        check_suite()
        print("qi_demarrais_tower: all retained case files match")
        return 0
    if args.analyze:
        report = analyze_batch_run(args.analyze)
        out_path = args.out or (args.analyze / "analysis.json")
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(out_path)
        return 0
    parser.error("Specify one of --self-test, --build, --check, or --analyze")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
