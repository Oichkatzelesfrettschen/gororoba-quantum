"""Acquisition packing preserves the selected operators and executed-arm boundaries."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest


def request_module() -> Any:
    return importlib.import_module("ascella_experiment_request")


def test_pack_six_jobs_with_seventeen_exact_source_settings(tmp_path: Path) -> None:
    request = request_module()
    files = request.build_files()
    campaign = json.loads(files["campaign.json"])
    if len(campaign["cases"]) != 6 or len(campaign["settings"]) != 17:
        raise AssertionError("the acquisition must preserve five cancellation jobs and twelve pilot settings")
    names = []
    for case in campaign["cases"]:
        manifest = json.loads(files[case["manifest"]])
        expected = len(case["settings"])
        if manifest["iterations"] != expected or manifest["max_samples"] != expected * 65_536:
            raise AssertionError("iterator sample budgets must split equally")
        if manifest["max_shots"] != expected * 131_072 or "compilation_seed" in manifest:
            raise AssertionError("an iterator needs per-setting seeds and summed detected-shot caps")
        if expected == 1 and manifest.get("iterator") is not True:
            raise AssertionError("separate cancellation jobs must use one-entry iterators")
        for row in manifest["settings"]:
            source = request.ROOT / row["source_manifest"]["file"]
            original = json.loads(source.read_bytes())
            if row["operator"] != original["settings"][0]["operator"]:
                raise AssertionError("packing changed a canonical operator")
            if row["compilation_seed"] != original["compilation_seed"]:
                raise AssertionError("base meshes must retain their registered seed identities")
            if len(row["native_probabilities"]) != 12 or "compilation_seed_allocation" not in row:
                raise AssertionError("all physical outputs and seed provenance must survive")
            names.append(row["name"])
    if names[:5] != ["dark", "bright", "bright-repeat", "dark-repeat", "fixture"]:
        raise AssertionError("cancellation jobs lost the frozen temporal order")
    expected_pilot = [f"computational-to-computational-input-{index}" for index in range(6)]
    expected_pilot += [f"product_fourier-to-product_chirped-input-{index}" for index in range(6)]
    if names[5:] != expected_pilot:
        raise AssertionError("the pilot includes a different screening cohort")
    request.write_files(tmp_path)
    request.check_files(tmp_path)


def test_check_refuses_mutated_budget(tmp_path: Path) -> None:
    request = request_module()
    request.write_files(tmp_path)
    case = next((tmp_path / "cases").glob("*/cases.json"))
    manifest = json.loads(case.read_bytes())
    manifest["max_shots"] += 1
    case.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        request.check_files(tmp_path)


def test_profile_reserves_missing_acquisition_endpoints() -> None:
    request = request_module()
    profile = json.loads(request.build_files()["qualification-profile.json"])
    if profile["endpoints"] != 17 * 13 + 17 + 5:
        raise AssertionError("the confidence family must include planned, failed and missing settings")
    if profile["samples_per_setting"] != 65_536 or profile["precision"] != 0.01:
        raise AssertionError("the pilot must meet the frozen conditional precision design")


def test_prepare_refuses_different_existing_successor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request = request_module()
    (tmp_path / "docs").symlink_to(request.ROOT / "docs", target_is_directory=True)
    written_case = tmp_path / "written-case.md"
    written_case.write_text("Bounded acquisition case.\n", encoding="utf-8")
    monkeypatch.setattr(request, "ROOT", tmp_path)
    bundle = tmp_path / "bundle"
    request.write_files(bundle)
    prepared = request.prepare_runs(bundle, written_case)
    manifest_path = prepared[0] / "cases.json"
    manifest = json.loads(manifest_path.read_bytes())
    if manifest["acquisition_admission"] != "ready" or manifest["reviewed_case"]["file"] != "written-case.md":
        raise AssertionError("prepared inputs must bind the written case")
    manifest["max_shots"] += 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="successor differs"):
        request.prepare_runs(bundle, written_case)
