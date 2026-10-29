"""Contracts of the falsifier's per-run parts: a matching part is reused, any identity change re-evaluates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import local_idle_falsifier as falsifier
import pytest

RUN = "results/live/2026-10-21T064222.721454Z"


def counting(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def evaluate(name: str, index: dict[str, Any], plan: bool = False) -> dict[str, Any]:
        calls.append(name)
        return {"run": name, "replicas": 2, "mean_difference": -0.5, "standard_error": None, "per_replica": {}}

    monkeypatch.setattr(falsifier, "evaluate", evaluate)
    return calls


def test_matching_part_is_reused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = counting(monkeypatch)
    identity = falsifier.part_identity()
    first = falsifier.evaluate_with_parts(RUN, {}, tmp_path, identity)
    second = falsifier.evaluate_with_parts(RUN, {}, tmp_path, identity)
    if first != second:
        raise AssertionError("the reused part differs from the fresh summary")
    if calls != [RUN]:
        raise AssertionError(f"evaluations {calls}")
    if sorted(p.name for p in tmp_path.iterdir()) != ["2026-10-21T064222.721454Z.json"]:
        raise AssertionError("parts directory holds more than the run's part")


def test_changed_identity_reevaluates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = counting(monkeypatch)
    identity = falsifier.part_identity()
    falsifier.evaluate_with_parts(RUN, {}, tmp_path, identity)
    changed = {**identity, "sources": {**identity["sources"], "gororoba_quantum/dynamic_density.py": "0" * 64}}
    falsifier.evaluate_with_parts(RUN, {}, tmp_path, changed)
    if calls != [RUN, RUN]:
        raise AssertionError(f"evaluations {calls}")


def test_identity_covers_every_part_source() -> None:
    identity = falsifier.part_identity()
    if set(identity["sources"]) != set(falsifier.PART_SOURCES):
        raise AssertionError("identity sources differ from PART_SOURCES")
    if not all(len(digest) == 64 for digest in identity["sources"].values()):
        raise AssertionError("a source digest is not a sha256")
