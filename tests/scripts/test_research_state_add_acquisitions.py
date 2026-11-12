"""Acquisitions appended together validate together, keeping every other entry's text."""

import json
from pathlib import Path
from typing import Any

import pytest
import research_state

LAYOUT = """{
  "schema": "SCHEMA",
  "acquisitions": [
    {"id": "old", "provider": "ibm", "run": "results/live/old", "family": "f", "question": "q"}
  ],
  "claims": [
  ]
}
"""


def entry(name: str) -> dict[str, str]:
    return {"id": name, "provider": "ibm", "run": f"results/live/{name}", "family": "f", "question": "q"}


@pytest.fixture
def registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[tuple[Any, frozenset[str]]]]:
    path = tmp_path / "research_state.json"
    path.write_text(LAYOUT, encoding="utf-8")
    seen: list[tuple[Any, frozenset[str]]] = []
    monkeypatch.setattr(research_state, "REGISTRY", path)
    monkeypatch.setattr(research_state, "Context", lambda: None)
    monkeypatch.setattr(research_state, "validate", lambda data, context, uncited: seen.append((data, uncited)))
    return path, seen


def test_two_runs_register_in_one_validation(registry: tuple[Path, list[tuple[Any, frozenset[str]]]]) -> None:
    path, seen = registry
    research_state.add_acquisitions([entry("first"), entry("second")])
    text = path.read_text(encoding="utf-8")
    ids = [row["id"] for row in json.loads(text)["acquisitions"]]
    if ids != ["old", "first", "second"] or not text.startswith(LAYOUT.split("\n  ],")[0]):
        raise AssertionError(f"the appended registry reads {ids} or rewrote the earlier entries")
    if [uncited for _, uncited in seen] != [frozenset({"first", "second"})]:
        raise AssertionError(f"the entries validated as {seen!r} rather than once, together")


def test_a_repeated_run_is_refused_before_writing(registry: tuple[Path, list[tuple[Any, frozenset[str]]]]) -> None:
    path, seen = registry
    twin = entry("twin") | {"run": "results/live/first"}
    with pytest.raises(ValueError, match="is registered"):
        research_state.add_acquisitions([entry("first"), twin])
    if path.read_text(encoding="utf-8") != LAYOUT or seen:
        raise AssertionError("a refused entry still wrote or validated the registry")


def test_quandela_discovers_submitted_cases_without_promoting_plans(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    cases = tmp_path / "cases"
    retained = runs / "retained"
    submitted = cases / "experiment/job-00"
    planned = cases / "experiment/job-01"
    for directory in (retained, submitted, planned):
        directory.mkdir(parents=True)
    (submitted / "submission.json").write_text("{}")
    (planned / "cases.json").write_text("{}")
    catalogue = tmp_path / "catalogue.json"
    catalogue.write_text("{}")
    monkeypatch.setattr(research_state, "QD_RUNS", runs)
    monkeypatch.setattr(research_state, "QD_CASES", cases)
    monkeypatch.setattr(research_state, "QD_CATALOGUE", catalogue)
    provider = research_state.QuandelaRuns()
    if set(provider.directories) != {retained, submitted}:
        raise AssertionError("submitted case discovery loses a retained receipt or admits an unsubmitted plan")
