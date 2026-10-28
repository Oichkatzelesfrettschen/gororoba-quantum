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
