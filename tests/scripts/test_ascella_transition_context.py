"""The context comparison preserves the prior operators and returned counts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest


def module() -> Any:
    return importlib.import_module("ascella_transition_context")


def test_seven_jobs_preserve_five_source_settings_in_both_orders() -> None:
    runner = module()
    files = runner.build_files()
    inventory = json.loads(files["campaign.json"])
    if len(inventory["jobs"]) != 7 or inventory["endpoints"] != 280:
        raise AssertionError("the seven jobs and prior-pilot family must remain frozen")
    groups = [json.loads(files[row["manifest"]])["settings"] for row in inventory["jobs"]]
    names = [group[0]["name"] for group in groups[:5]]
    if [row["name"] for row in groups[5]] != names or [row["name"] for row in groups[6]] != names[::-1]:
        raise AssertionError("packed requested orders must be the singleton order and its reverse")
    source = json.loads((runner.ROOT / runner.SOURCE).read_bytes())
    original = {row["name"]: row for row in source["settings"]}
    for group in groups:
        for row in group:
            prior = original[row["name"]]
            for field in ("circuit_params", "compilation_seed", "operator", "column"):
                if row[field] != prior[field]:
                    raise AssertionError(f"the diagnostic changed original {field}")


def test_echoed_seed_and_parameter_mutations_are_refused() -> None:
    runner = module()
    case = json.loads(runner.build_files()["cases/single-identity-2/cases.json"])
    setting = case["settings"][0]
    echo = {
        "circuit_params": dict(setting["circuit_params"]),
        "compilation_seed": setting["compilation_seed"],
        "max_samples": runner.SAMPLES,
        "max_shots": runner.SHOTS,
    }
    runner.check_echo(setting, {"iteration": echo})
    altered = {**echo, "compilation_seed": echo["compilation_seed"] + 1}
    with pytest.raises(ValueError, match="echo"):
        runner.check_echo(setting, {"iteration": altered})
    altered = {**echo, "circuit_params": {**echo["circuit_params"], "x0": echo["circuit_params"]["x0"] + 1}}
    with pytest.raises(ValueError, match="echo"):
        runner.check_echo(setting, {"iteration": altered})


def test_report_keeps_invalid_events_and_requires_matching_mesh_for_comparison() -> None:
    runner = module()
    first = {"counts": [90] + [0] * 11 + [10], "leakage": 10, "mesh": ["circuit-a", "input-a"]}
    other = {"counts": [80] + [0] * 11 + [20], "leakage": 20, "mesh": ["circuit-b", "input-a"]}
    contrast = runner.compare(first, other, endpoints=280)
    if contrast["first_events"] != 100 or contrast["second_events"] != 100:
        raise AssertionError("invalid photon numbers must remain in the denominators")
    if contrast["matched_mesh"] or contrast["matched_mesh_interpretation"] != "inconclusive":
        raise AssertionError("a changed returned mesh cannot be a matched-mesh contrast")


def test_build_check_detects_mutated_request(tmp_path: Path) -> None:
    runner = module()
    runner.write_files(tmp_path)
    manifest = tmp_path / "cases/single-identity-2/cases.json"
    data = json.loads(manifest.read_bytes())
    data["max_shots"] += 1
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        runner.check_files(tmp_path)


def test_submitted_manifest_binds_frozen_source_and_written_case() -> None:
    runner = module()
    files = runner.build_files()
    campaign = json.loads(files["campaign.json"])
    job = campaign["jobs"][0]
    frozen = json.loads(files[job["manifest"]])
    binding = {"file": "written-case.md", "sha256": "a" * 64}
    actual = {
        **frozen,
        "acquisition_admission": "ready",
        "source_case_sha256": job["manifest_sha256"],
        "reviewed_case": binding,
    }
    runner.validate_run_manifest(actual, frozen, job, binding)
    actual["min_detected_photons"] = 2
    with pytest.raises(ValueError, match="differs"):
        runner.validate_run_manifest(actual, frozen, job, binding)


def test_parallel_entry_worker_reconstructs_a_retained_provider_mesh() -> None:
    runner = module()
    directory = runner.ROOT / runner.PRIOR_RUN
    manifest = json.loads((directory / "cases.json").read_bytes())
    result = json.loads((directory / "results.json").read_bytes())
    measurement = runner._entry_job((manifest["settings"][0], result["iterations"][0]))
    if sum(measurement["counts"]) != runner.SAMPLES or len(measurement["mesh"]) != 2:
        raise AssertionError("the worker must preserve the accepted count and returned mesh identities")
