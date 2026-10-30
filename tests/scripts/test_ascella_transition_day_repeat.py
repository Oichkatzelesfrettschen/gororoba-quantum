"""The delayed acquisition respects the Pacific day and retained mesh identities."""

from __future__ import annotations

import importlib
import json
import runpy
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import frozen_case_sources
import pytest

ROOT = Path(__file__).resolve().parents[2]
PINS = ROOT / "docs/evidence/quandela/frozen-case-source-pins.json"


def module() -> Any:
    return importlib.import_module("ascella_transition_day_repeat")


def test_local_launcher_selects_the_source_compatible_successor(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = types.ModuleType("ascella_transition_day_repeat")
    runner.main = lambda: 0  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "ascella_transition_day_repeat", runner)
    with pytest.raises(SystemExit) as exited:
        runpy.run_path(str(ROOT / "scripts/ascella_transition_local_repeat.py"), run_name="__main__")
    if exited.value.code != 0 or runner.BUNDLE != Path(
        "docs/evidence/ascella-transition-day-repeat-reviewed-transport"
    ):
        raise AssertionError("the launcher did not select the source-compatible successor")


@pytest.mark.audit
def test_local_launcher_checks_the_source_compatible_successor(tmp_path: Path) -> None:
    frozen_case_sources.run_pinned_audit_test(
        PINS,
        "docs/evidence/ascella-transition-day-repeat-reviewed-transport/campaign.json",
        "tests/scripts/test_ascella_transition_day_repeat.py::test_local_launcher_checks_the_source_compatible_successor",
        tmp_path / "pinned",
    )


def test_repeat_waits_at_least_one_day_and_only_the_next_pacific_date() -> None:
    runner = module()
    baseline = datetime(2026, 10, 28, 0, 40, tzinfo=UTC).timestamp()
    if runner.time_allowed(baseline + timedelta(hours=23).total_seconds(), baseline):
        raise AssertionError("the repeat must wait at least 24 hours")
    if not runner.time_allowed(baseline + timedelta(hours=24).total_seconds(), baseline):
        raise AssertionError("the same local time on the following day should be admitted")
    if runner.time_allowed(baseline + timedelta(hours=48).total_seconds(), baseline):
        raise AssertionError("a missed next-day window must not silently move to a later date")


def test_day_case_retains_every_forward_parameter_and_seed() -> None:
    runner = module()
    source = json.loads((runner.ROOT / runner.SOURCE).read_bytes())
    manifest = runner.make_manifest(source)
    if manifest["iterations"] != 5 or manifest["max_samples"] != 5 * 65_536:
        raise AssertionError("the repeat must carry five complete accepted-sample budgets")
    for original, repeated in zip(source["settings"], manifest["settings"], strict=True):
        for field in ("circuit_params", "compilation_seed", "operator", "column"):
            if original[field] != repeated[field]:
                raise AssertionError(f"the day repeat changed {field}")


def test_existing_submission_checkpoint_cannot_be_retried(tmp_path: Path) -> None:
    runner = module()
    (tmp_path / "submission-state.json").write_text('{"phase":"post_outcome_unknown"}\n', encoding="utf-8")
    if runner.safe_to_post(tmp_path):
        raise AssertionError("an unknown POST outcome must require reconciliation")


def test_early_request_refuses_before_creating_a_case_or_contacting_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = module()
    baseline = datetime(2026, 10, 28, 0, 40, tzinfo=UTC).timestamp()
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "_reported_case", lambda _: ({"baseline_start_unix": baseline}, {}))
    with pytest.raises(ValueError, match="outside"):
        runner.submit(tmp_path, "authorized repeat", now=baseline + 3_600)
    if (tmp_path / runner.RUN).exists():
        raise AssertionError("an early request must leave no provider case directory")


def test_registry_append_preserves_existing_bytes_and_rejects_duplicate_identifiers() -> None:
    runner = module()
    source = (
        '{\n  "schema": "research-state-v2",\n  "acquisitions": [\n    {"id": "old"}\n  ],\n'
        '  "claims": [\n    {"id": "old-claim"}\n  ]\n}\n'
    )
    updated = runner.append_registry(source, {"id": "new"}, {"id": "new-claim"})
    if '{"id": "old"}' not in updated or '{"id": "old-claim"}' not in updated:
        raise AssertionError("registry insertion must preserve existing record formatting")
    with pytest.raises(ValueError, match="already"):
        runner.append_registry(updated, {"id": "new"}, {"id": "another"})


def test_registration_requires_all_five_attributable_comparisons() -> None:
    runner = module()
    baseline = datetime(2026, 10, 28, 0, 40, tzinfo=UTC).timestamp()
    comparison = {"setting": "one", "matched_mesh": True, "simultaneous_total_variation_bounds": [0.0, 0.1]}
    result = {
        "schema": "ascella-transition-day-repeat-analysis-v1",
        "campaign_sha256": "campaign",
        "analysis_source_sha256": "producer",
        "endpoints": 140,
        "confidence": 0.95,
        "baseline": {"start_time": baseline},
        "repeat": {"start_time": baseline + 86_400},
        "matched_meshes": 1,
        "comparisons": [comparison],
    }
    collected = {"samples": 5 * 65_536, "status": {"status": "completed", "duration": 20}}
    with pytest.raises(ValueError, match="five"):
        runner.validate_registration(result, collected, "campaign", "producer")
