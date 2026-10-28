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
        "admitted_statuses": ["available"],
    }
    checker.check_plan(plan)
    for field, replacement in (
        ("cases_sha256", "changed"),
        ("platform", "qpu:belenos"),
        ("credit_ceiling", checker.context.CREDIT_CEILING + 1),
        ("admitted_statuses", ["calibration"]),
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
    monkeypatch.setattr(checker.context, "read_run", lambda _: ({"start_time": 1}, [{"name": "setting"}]))
    monkeypatch.setattr(checker.repeat, "time_allowed", lambda *_: True)
    monkeypatch.setattr(checker.context, "ordered_map", lambda *args, **kwargs: [{"matched_mesh": True}] * 5)
    monkeypatch.setattr(checker.repeat, "validate_registration", lambda *args: None)
    checker.check_result(run)
    if checker.repeat.RUN != original_run:
        raise AssertionError("the frozen run identity changed to the scheduler's result path")
