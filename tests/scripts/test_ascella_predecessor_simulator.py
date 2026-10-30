"""The sim:ascella qualification reads only the frozen case with its job name and platform substituted."""

import json
import shutil
from pathlib import Path

import ascella_predecessor_simulator as simulator
import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/quandela/runs/2026-10-30T010726Z-sim_ascella-ascella_predecessor-source-compatible"
EVIDENCE = ROOT / "docs/evidence/ascella-predecessor-admission/simulator-qualification.json"


def test_the_retained_qualification_reproduces_its_evidence() -> None:
    if simulator.describe_run(RUN) != json.loads(EVIDENCE.read_text(encoding="utf-8")):
        raise AssertionError("the retained simulator run no longer reproduces simulator-qualification.json")


def test_a_case_beyond_the_two_substituted_fields_is_refused(tmp_path: Path) -> None:
    copy = tmp_path / "run"
    shutil.copytree(RUN, copy)
    manifest = json.loads((copy / "cases.json").read_text(encoding="utf-8"))
    manifest["max_duration"] += 1
    (copy / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not the simulator qualification"):
        simulator.describe_run(copy)
