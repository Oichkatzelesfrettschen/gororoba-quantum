"""Live package cross-checks for the retained Tuna disagreement analysis."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/qi_tuna_joint_package_runtime.py"
pytestmark = pytest.mark.audit


def test_archive_bound_packages_analyze_retained_joint_records(tmp_path: Path) -> None:
    """Catch changed package source, basis mapping, split control or data-derived algebra."""
    archive_dir = os.environ.get("TUNA_PACKAGE_ARCHIVES")
    if not archive_dir:
        pytest.skip("TUNA_PACKAGE_ARCHIVES is unset")
    output = tmp_path / "package-runtime.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--archives", archive_dir, "--out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"runtime package audit failed: {process.stderr}")
    record = json.loads(output.read_bytes())
    if [item["basis_pairs_per_implementation"] for item in record["dimension_tables"]] != [64, 256]:
        raise AssertionError("the full 8D and 16D basis maps must be checked")
    if record["split_control"] != {
        "associator_triples_checked": 512,
        "ordinary_e4_square": -1,
        "split_e4_square": 1,
    }:
        raise AssertionError("the split-algebra negative control differs")
    if sum(item["byte_identical_to_release"] for item in record["archive_bindings"].values()) != 32:
        raise AssertionError("every installed algebra module must bind to its release archive")
    if len(record["jobs"]) != 6 or record["exact_nominal_one_response"] != "183/4096":
        raise AssertionError("package analysis must cover the six retained cases and exact response")
    distance = record["descriptive_distances"]["nominal_one"]
    if distance["jensen_shannon_distance_sqrt_bits_decimal_12_places"] != "0.063710980845":
        raise AssertionError("the Jensen-Shannon distance must identify its square-root-bit units")


def test_runtime_audit_refuses_missing_registered_release_archives(tmp_path: Path) -> None:
    """Missing source archives cannot produce an attested package observation."""
    archive_dir = tmp_path / "empty-archives"
    archive_dir.mkdir()
    output = tmp_path / "untrusted.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--archives", str(archive_dir), "--out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode == 0 or output.exists() or "0 archives match" not in process.stderr:
        raise AssertionError("the package probe must refuse missing pinned archives before writing evidence")


def test_runtime_audit_does_not_replace_existing_observation(tmp_path: Path) -> None:
    """An existing local observation retains its bytes when a capture is repeated."""
    archive_dir = os.environ.get("TUNA_PACKAGE_ARCHIVES")
    if not archive_dir:
        pytest.skip("TUNA_PACKAGE_ARCHIVES is unset")
    output = tmp_path / "existing.json"
    output.write_text("original\n")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--archives", archive_dir, "--out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode == 0 or output.read_text() != "original\n":
        raise AssertionError("the runtime probe must preserve an existing observation")
