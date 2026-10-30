"""The hosted repeat enforces the frozen plan and preserves mismatch evidence."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest


def test_ci_plan_checks_manifest_and_bounds(monkeypatch: pytest.MonkeyPatch) -> None:
    checker = importlib.import_module("ascella_transition_ci_check")
    manifest = {"settings": [1]}
    monkeypatch.setattr(checker.repeat, "_reported_case", lambda _: ({}, manifest))
    plan: dict[str, Any] = {
        "cases_sha256": checker.context._sha(checker.context._json_bytes(manifest)),
        "platform": "qpu:ascella",
        "credit_ceiling": checker.context.CREDIT_CEILING,
        "admitted_statuses": ["available", "running"],
    }
    checker.check_plan(plan)
    for field, replacement in (
        ("cases_sha256", "changed"),
        ("platform", "qpu:belenos"),
        ("credit_ceiling", checker.context.CREDIT_CEILING + 1),
        ("admitted_statuses", ["calibration"]),
        ("admitted_statuses", ["available"]),
    ):
        altered = {**plan, field: replacement}
        with pytest.raises(ValueError, match="differs"):
            checker.check_plan(altered)


def test_ci_result_refuses_a_path_outside_run_inventory(tmp_path: Path) -> None:
    checker = importlib.import_module("ascella_transition_ci_check")
    with pytest.raises(ValueError):
        checker.check_result(tmp_path)


def test_timestamped_ci_run_keeps_the_frozen_campaign_run_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checker = importlib.import_module("ascella_transition_ci_check")
    original_run = checker.repeat.RUN
    run = tmp_path / "results/quandela/runs/timestamped-repeat"
    run.mkdir(parents=True)
    (run / "results.json").write_text("{}", encoding="utf-8")
    bundle = tmp_path / checker.repeat.BUNDLE
    bundle.mkdir(parents=True)
    (bundle / "campaign.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(checker.repeat, "ROOT", tmp_path)
    monkeypatch.setattr(checker.repeat, "_reported_case", lambda _: ({"baseline_start_unix": 0}, {}))
    monkeypatch.setattr(checker.repeat.qd, "load_case", lambda _: ({}, None, None))
    monkeypatch.setattr(checker.context, "read_run", lambda _: ({"start_time": 86_400}, [{"name": "setting"}]))
    monkeypatch.setattr(checker.context, "ordered_map", lambda *args, **kwargs: [{"matched_mesh": True}] * 5)
    monkeypatch.setattr(checker, "validate_registration", lambda *args: None)
    checker.check_result(run)
    if checker.repeat.RUN != original_run:
        raise AssertionError("the frozen run identity changed to the scheduler's result path")


def test_ci_window_admits_any_start_24_hours_after_the_baseline() -> None:
    checker = importlib.import_module("ascella_transition_ci_check")
    baseline = 1_793_147_885.339165
    if checker.elapsed_allowed(baseline + 86_399, baseline):
        raise AssertionError("a start under 24 hours after the baseline qualified")
    for hours in (24, 33, 72):
        if not checker.elapsed_allowed(baseline + hours * 3_600, baseline):
            raise AssertionError(f"a start {hours} hours after the baseline was refused")
    if checker.elapsed_allowed(float("nan"), baseline):
        raise AssertionError("a non-finite start qualified")


def test_ci_registration_admits_a_start_33_hours_after_the_baseline() -> None:
    checker = importlib.import_module("ascella_transition_ci_check")
    baseline = 1_793_147_885.339165
    comparisons = [
        {"setting": name, "matched_mesh": True, "simultaneous_total_variation_bounds": [0.0, 0.1]}
        for _, name in checker.context.SELECTION
    ]
    result = {
        "schema": "ascella-transition-day-repeat-analysis-v1",
        "campaign_sha256": "campaign",
        "analysis_source_sha256": "producer",
        "endpoints": 140,
        "confidence": 0.95,
        "baseline": {"start_time": baseline},
        "repeat": {"start_time": baseline + 33 * 3_600},
        "matched_meshes": 5,
        "comparisons": comparisons,
    }
    collected = {"samples": 5 * checker.context.SAMPLES, "status": {"status": "completed", "duration": 20}}
    original = checker.repeat.time_allowed
    checker.validate_registration(result, collected, "campaign", "producer")
    if checker.repeat.time_allowed is not original:
        raise AssertionError("the runner's next-day rule was not restored")
    with pytest.raises(ValueError, match="next-day window"):
        checker.repeat.validate_registration(result, collected, "campaign", "producer")
    early = {**result, "repeat": {"start_time": baseline + 23 * 3_600}}
    with pytest.raises(ValueError, match="next-day window"):
        checker.validate_registration(early, collected, "campaign", "producer")
