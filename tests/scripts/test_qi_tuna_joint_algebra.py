"""Check exact algebraic summaries of retained six-job disagreement data."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/qi_tuna_joint_algebra.py"


def test_exact_package_table_analysis_preserves_split_counterexample(tmp_path: Path) -> None:
    """Catch inconsistent package mappings or a false identification from associator signs."""
    destination = tmp_path / "joint-algebra.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"joint algebra replay failed: {process.stderr}")
    result = json.loads(destination.read_bytes())
    one = result["cases"]["nominal_one"]
    zero = result["cases"]["nominal_zero_prefix"]
    if [job["associator_norm_squared"] for job in one] != [
        "764037/1048576",
        "1434981/2097152",
        "3101879/4194304",
    ]:
        raise AssertionError("exact nominal-one coefficient-associator norms differ")
    if [job["associator_sign_mean"] for job in zero] != ["-65/512", "-245/2048", "-21/128"]:
        raise AssertionError("nominal-zero prefix associator-sign means differ")
    if result["split_control"] != {
        "associator_triples_checked": 512,
        "ordinary_e4_square": -1,
        "split_e4_square": 1,
    }:
        raise AssertionError("split and ordinary algebra negative control differs")


def test_retained_package_analysis_is_exact_and_exclusive(tmp_path: Path) -> None:
    """Catch changed algebra evidence and accidental replacement of retained output."""
    retained = ROOT / "docs/evidence/tuna-projector-geometry/joint-algebra-analysis.json"
    for flags in ([], ["-O"]):
        process = subprocess.run(
            [sys.executable, *flags, str(SCRIPT), "--check", str(retained)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise AssertionError(f"package-table replay failed: {process.stderr}")
    destination = tmp_path / "existing.json"
    destination.write_bytes(retained.read_bytes())
    before = destination.read_bytes()
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(destination)], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if process.returncode == 0 or destination.read_bytes() != before:
        raise AssertionError("an existing algebra record must remain unchanged")
    record = json.loads(before)
    record["cases"]["nominal_one"][0]["associator_norm_squared"] = "0"
    destination.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode == 0:
        raise AssertionError("a changed exact algebraic value must be refused")


def test_corrupted_package_basis_table_is_refused(tmp_path: Path, monkeypatch: object) -> None:
    """Catch a changed octonion sign even when the package-table JSON is parseable."""
    import pytest
    import qi_tuna_joint_algebra as algebra

    tables = json.loads(algebra.PACKAGE_TABLES.read_bytes())
    tables["packages"]["hypercomplex"]["tables"]["8"]["signs"][1][6] *= -1
    changed = tmp_path / "tables.json"
    changed.write_text(json.dumps(tables))
    monkeypatch.setattr(algebra, "PACKAGE_TABLES", changed)  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError, match="not identical"):
        algebra.analyze()
