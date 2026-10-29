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
    if first[1].get("cpu") is None or "numpy_dispatch" not in first[1]:
        raise AssertionError(f"part platform {first[1]}")
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


def test_parts_only_refuses_to_evaluate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = counting(monkeypatch)
    try:
        falsifier.evaluate_with_parts(RUN, {}, tmp_path, falsifier.part_identity(), parts_only=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("a missing part was evaluated under parts_only")
    if calls:
        raise AssertionError(f"evaluations {calls}")


def test_largest_deviation_reads_floats_and_rejects_structure() -> None:
    retained = {"run": "r", "replicas": 2, "mean_difference": -0.5, "per_replica": {"m": [{"law": [0.25, 0.75]}]}}
    shifted = {
        "run": "r",
        "replicas": 2,
        "mean_difference": -0.5,
        "per_replica": {"m": [{"law": [0.25, 0.75 + 4e-10]}]},
    }
    if not 3e-10 < falsifier.largest_deviation(shifted, retained) <= falsifier.TOLERANCE:
        raise AssertionError("a last-digit shift is not read as a small deviation")
    if falsifier.largest_deviation({**retained, "replicas": 3}, retained) != float("inf"):
        raise AssertionError("an integer change is not a structural mismatch")
    if falsifier.largest_deviation({**retained, "run": "s"}, retained) != float("inf"):
        raise AssertionError("a string change is not a structural mismatch")


def test_inserted_estimate_keeps_only_acting_replicas() -> None:
    rows = [
        {"difference": -0.2, "inserted_dt": {"0": 8}, "padded_law": [0.5, 0.5], "unpadded_law": [0.6, 0.4]},
        {"difference": 0.0, "inserted_dt": {"0": 8}, "padded_law": [1.0, 0.0], "unpadded_law": [1.0, 0.0]},
        {"difference": 0.0, "inserted_dt": {}, "padded_law": [1.0, 0.0], "unpadded_law": [1.0, 0.0]},
    ]
    estimate = falsifier.inserted_estimate({"runs": [{"run": "r", "per_replica": {"m": rows}}, {"run": "out"}]})
    (run,) = estimate["runs"]
    if (run["replicas"], run["inserted_replicas"], run["acting_replicas"]) != (3, 2, 1):
        raise AssertionError(f"counts {run}")
    if run["mean_difference"] != -0.2 or run["standard_error"] is not None:
        raise AssertionError(f"estimate {run}")
    if (estimate["runs_with_acting_replicas"], estimate["runs_lower"]) != (1, 1):
        raise AssertionError(f"totals {estimate}")
