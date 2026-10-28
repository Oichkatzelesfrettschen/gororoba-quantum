"""Acquisition admission requires complete predecessors and bounded pilot packing."""

from __future__ import annotations

import importlib
from typing import Any

import ascella_experiment_request as request
import pytest


def runner() -> Any:
    return importlib.import_module("ascella_experiment_run")


def complete_predecessors(campaign: dict[str, Any], count: int, duration: float) -> dict[str, Any]:
    rows = [
        {"setting_id": setting_id, "interface_complete": True, "accepted_events": request.SAMPLES}
        for case in campaign["cases"][:count]
        for setting_id in case["settings"]
    ]
    return {
        "settings": rows,
        "jobs": [
            {"directory": case["directory"], "status": "collected", "duration_seconds": duration}
            for case in campaign["cases"][:count]
        ],
    }


def test_missing_dark_result_blocks_bright_job() -> None:
    import json

    campaign = json.loads(request.build_files()["campaign.json"])
    with pytest.raises(ValueError, match="predecessor"):
        runner().prerequisite_decision(campaign, 1, {"settings": [], "jobs": []})


def test_large_measured_duration_blocks_twelve_setting_packing() -> None:
    import json

    campaign = json.loads(request.build_files()["campaign.json"])
    report = complete_predecessors(campaign, 5, 21.0)
    with pytest.raises(ValueError, match="packing"):
        runner().prerequisite_decision(campaign, 5, report)


def test_negative_scientific_result_keeps_diagnostic_controls_eligible() -> None:
    import json

    campaign = json.loads(request.build_files()["campaign.json"])
    report = complete_predecessors(campaign, 1, 4.0)
    report["settings"][0]["qualification"] = "fail"
    decision = runner().prerequisite_decision(campaign, 1, report)
    if decision["admitted"] is not True:
        raise AssertionError("a complete negative scientific result still needs the bright diagnostic control")


def test_finite_duration_and_full_sample_target_bind_admission() -> None:
    import json

    campaign = json.loads(request.build_files()["campaign.json"])
    report = complete_predecessors(campaign, 1, float("nan"))
    with pytest.raises(ValueError, match="duration"):
        runner().prerequisite_decision(campaign, 1, report)
    report = complete_predecessors(campaign, 1, 4.0)
    report["settings"][0]["accepted_events"] -= 1
    with pytest.raises(ValueError, match="predecessor"):
        runner().prerequisite_decision(campaign, 1, report)


def test_body_binding_ignores_only_process_identity() -> None:
    import uuid

    first = {"process_id": str(uuid.uuid4()), "payload": {"compilation": "frozen"}, "max_duration": 300}
    fresh = {**first, "process_id": str(uuid.uuid4())}
    if runner().body_projection(first) != runner().body_projection(fresh):
        raise AssertionError("a fresh SDK process identity changes no scientific request field")
    for key, value in (
        ("max_duration", 301),
        ("payload", {"compilation": "changed"}),
        ("platform_name", "sim:ascella"),
    ):
        if runner().body_projection(first) == runner().body_projection({**fresh, key: value}):
            raise AssertionError(f"the request projection must retain {key}")
    with pytest.raises(ValueError):
        runner().body_projection({**first, "process_id": "invalid"})
