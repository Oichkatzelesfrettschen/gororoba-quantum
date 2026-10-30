"""Check the requested-slot contrast and manifest identities."""

from __future__ import annotations

import json

import ascella_target_slot_drift as case
import pytest
import qd_platform


def test_requested_contrast_cancels_quadratic_index_drift() -> None:
    indices = range(8)
    for degree in range(3):
        if sum(weight * index**degree for index, weight in zip(indices, case.WEIGHTS, strict=True)) != 0:
            raise AssertionError("requested index contrast does not cancel the declared polynomial")
    if sum(weight for label, weight in zip(case.LABELS, case.WEIGHTS, strict=True) if label == "A") != 4:
        raise AssertionError("the target contrast does not have unit A-versus-B gain")
    if sum(weight * index**3 for index, weight in zip(indices, case.WEIGHTS, strict=True)) == 0:
        raise AssertionError("the cubic drift falsifier disappeared")


def test_simulator_and_hardware_requests_match_settings() -> None:
    simulator = case.documents("sim:ascella")
    hardware = case.documents("qpu:ascella")
    sim_case = json.loads(simulator["cases.json"])
    hardware_case = json.loads(hardware["cases.json"])
    if simulator["circuit.json"] != hardware["circuit.json"] or sim_case["settings"] != hardware_case["settings"]:
        raise AssertionError("simulator and hardware settings differ")
    if len(sim_case["settings"]) != 16 or hardware_case["max_duration"] != 300 or hardware_case["max_credits"] != 2:
        raise AssertionError("hardware request exceeds the stated case")


def test_review_rejects_changed_drift_sources() -> None:
    manifest = json.loads(case.documents("qpu:ascella")["cases.json"])
    qd_platform.acquisition_sources(manifest)
    if not qd_platform.requires_acquisition_review({"family": "ascella_target_slot_drift"}):
        raise AssertionError("the drift family must require the reviewed packet")
    historical = json.loads(json.dumps(manifest))
    del historical["analysis_sources"]["scripts/ascella_target_slot_drift.py"]
    with pytest.raises(qd_platform.PlatformError, match="complete constructor/analyzer"):
        qd_platform.acquisition_sources(historical)
    for name in ("scripts/ascella_target_slot_drift.py", "scripts/ascella_target_slot_drift_analysis.py"):
        changed = json.loads(json.dumps(manifest))
        changed["analysis_sources"][name] = "0" * 64
        with pytest.raises(qd_platform.PlatformError, match="reviewed source changed"):
            qd_platform.acquisition_sources(changed)
