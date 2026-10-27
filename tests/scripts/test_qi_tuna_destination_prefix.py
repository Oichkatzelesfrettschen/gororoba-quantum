"""Retained incomplete acquisitions preserve refusal while descriptive counts replay."""

import json
import shutil
from pathlib import Path

import pytest
from qi_tuna_destination_prefix import ROOT, analyze, replay

RETAINED = ROOT / "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response"


def test_retained_deadline_prefix_replays() -> None:
    primary = json.loads((RETAINED / "analysis.json").read_text())
    if analyze(RETAINED) != primary or primary["outcome"] != "implementation route unavailable":
        raise AssertionError("incomplete case must retain its frozen refusal")
    retained = json.loads((RETAINED / "nominal-zero-prefix-descriptive.json").read_text())
    if replay(RETAINED) != retained or retained["statistical_acceptance_admitted"] is not False:
        raise AssertionError("prefix counts must replay without promoting the incomplete case")


def test_missing_prefix_completion_refuses(tmp_path: Path) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    (run / "prepared-zero-baseline-after/completion-admission.json").unlink()
    with pytest.raises(FileNotFoundError):
        replay(run)


def test_reordered_retained_shots_refuse(tmp_path: Path) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    path = run / "prepared-zero-baseline-before/raw/baseline-before.cq.json"
    shots = json.loads(path.read_text())
    if shots == list(reversed(shots)):
        raise AssertionError("retained fixture must distinguish shot order")
    path.write_text(json.dumps(list(reversed(shots))))
    with pytest.raises(ValueError):
        replay(run)
