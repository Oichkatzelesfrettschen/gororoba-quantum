"""Offline QX proposals bind explicit immutable catalogue and Tuna sources."""

import json
from pathlib import Path

import pytest
from qi_zz_map_qx import ROOT, build, digest

CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue-submission-deadline-proposal.json"
SOURCE_PLAN = ROOT / "results/quantum_inspire/cases/zz-map-tuna17-deadline-recovery/plan.json"


def test_qx_builder_binds_explicit_catalogue_and_source_plan() -> None:
    files = build(SOURCE_PLAN, catalogue=CATALOGUE)
    plan = json.loads(files["plan.json"])
    if plan["source_digests"]["catalogue_sha256"] != digest(CATALOGUE.read_bytes()):
        raise RuntimeError("the explicit archived catalogue lost its content identity")
    if plan["source_digests"]["source_tuna_plan_sha256"] != digest(SOURCE_PLAN.read_bytes()):
        raise RuntimeError("the explicit reviewed Tuna source lost its content identity")
    original = ROOT / "results/quantum_inspire/cases/zz_map_qx"
    circuits = [name for name in files if name.endswith(".cq")]
    if len(circuits) != 416 or any(files[name].encode() != (original / name).read_bytes() for name in circuits):
        raise RuntimeError("source-binding refresh changed compact scientific circuit bytes")


def test_qx_builder_checks_selected_catalogue_capacity(tmp_path: Path) -> None:
    catalogue = json.loads(CATALOGUE.read_text())
    backend = next(row for row in catalogue["backend_types"] if row["identifier"] == "QXsinglenodesimulator")
    backend["nqubits"] = 7
    selected = tmp_path / "catalogue.json"
    selected.write_text(json.dumps(catalogue))
    with pytest.raises(ValueError, match="QX capacity changed"):
        build(SOURCE_PLAN, catalogue=selected)


def test_toolchain_successor_preserves_original_rows_and_covers_current_cases() -> None:
    from qi_toolchain_check import RECORD, case_files

    predecessor = json.loads((ROOT / "docs/evidence/quantum_inspire/toolchain_check.json").read_text())
    successor = json.loads(RECORD.read_text())
    current = case_files()
    # A case file rebuilt at its path carries new bytes and a new row; every row of unchanged bytes is preserved.
    old_rows = {
        row["case"]: row for row in predecessor["circuits"] if current.get(row["case"], ("",))[0] == row["sha256"]
    }
    new_rows = {row["case"]: row for row in successor["circuits"]}
    if any(new_rows.get(path) != row for path, row in old_rows.items()):
        raise RuntimeError("the toolchain successor changed original compilation evidence")
    if set(new_rows) != set(current):
        raise RuntimeError("the toolchain successor omitted retained case circuits")
