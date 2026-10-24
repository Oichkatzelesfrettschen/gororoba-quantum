"""Contract for ascella_coherence_run_analysis.attributed and analyze_run: collected results.json iterations reach the
registered estimators only at their own positions, as twelve-mode single-photon counts, with exclusions tallied.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import ascella_coherence_analysis as analysis
import ascella_coherence_run as run_analysis
import pytest

EVENTS = 8192


def state(mode: int, photons: int = 1) -> str:
    return ",".join(str(photons if index == mode else 0) for index in range(analysis.MODES))


def ideal_results(manifest: dict[str, Any]) -> dict[str, Any]:
    """A completed results.json whose counts reproduce every registered ideal statistic to 1/8192."""
    iterations = []
    for setting in manifest["settings"]:
        if setting["readout"] == "direct":
            dark = round(EVENTS * setting["ideal"]["dark"])
            counts = {state(0): EVENTS - dark, state(2): dark}
        else:
            bright = round(EVENTS * (1 + setting["ideal"]["z"]) / 2)
            counts = {state(0): bright, state(3): EVENTS - bright}
        counts = {key: value for key, value in counts.items() if value}
        iterations.append({"iteration": {"circuit_params": dict(setting["circuit_params"])}, "counts": counts})
    return {"job_id": "synthetic", "status": {"status": "completed"}, "partial": False, "iterations": iterations}


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return json.loads(run_analysis.FROZEN.read_text(encoding="utf-8"))


def test_ideal_counts_qualify_every_endpoint(manifest: dict[str, Any]) -> None:
    rows, exclusions = run_analysis.attributed(manifest, ideal_results(manifest))
    record = analysis.analyze(manifest, rows)
    if not record["complete"] or record["verdicts"] != {"qualifies": 27, "falsified": 0, "inconclusive": 0}:
        raise AssertionError(record.get("verdicts", record.get("reason")))
    if any(exclusions["vacuum"]) or any(exclusions["multiple"]):
        raise AssertionError(exclusions)


def test_missing_and_errored_iterations_carry_no_decisions(manifest: dict[str, Any]) -> None:
    results = ideal_results(manifest)
    results["iterations"][40] = {"iteration": results["iterations"][40]["iteration"], "error": "worker error"}
    results["iterations"][63] = {"missing": True}
    rows, _ = run_analysis.attributed(manifest, results)
    record = analysis.analyze(manifest, rows)
    if record["complete"] or rows[40] is not None or rows[63] is not None:
        raise AssertionError(record)


def test_count_less_terminal_result_carries_no_decisions(manifest: dict[str, Any]) -> None:
    # The shape collect writes for a worker error answered without counts.
    results = {"job_id": "e", "status": {"status": "error"}, "partial": True, "counts": {}, "samples": 0}
    rows, _ = run_analysis.attributed(manifest, results)
    record = analysis.analyze(manifest, rows)
    if record["complete"] or any(row is not None for row in rows):
        raise AssertionError(record)


def test_counts_at_another_settings_position_raise(manifest: dict[str, Any]) -> None:
    results = ideal_results(manifest)
    results["iterations"][16], results["iterations"][20] = results["iterations"][20], results["iterations"][16]
    with pytest.raises(ValueError, match="iteration 16"):
        run_analysis.attributed(manifest, results)


def test_four_mode_states_raise(manifest: dict[str, Any]) -> None:
    results = ideal_results(manifest)
    results["iterations"][0]["counts"] = {"1,0,0,0": EVENTS}
    with pytest.raises(ValueError, match="spans 4 modes"):
        run_analysis.attributed(manifest, results)


def test_exclusions_leave_the_denominator_and_outside_modes_stay_in(manifest: dict[str, Any]) -> None:
    results = ideal_results(manifest)
    counts = results["iterations"][5]["counts"]
    counts[state(0, 0)] = 3
    counts[state(1, 2)] = 2
    counts[state(9)] = 7
    rows, exclusions = run_analysis.attributed(manifest, results)
    if exclusions["vacuum"][5] != 3 or exclusions["multiple"][5] != 2:
        raise AssertionError(exclusions)
    row = rows[5]
    if row is None or row[9] != 7 or sum(row) != EVENTS + 7:
        raise AssertionError(row)


def test_run_directory_requires_the_frozen_request_and_reproduces(manifest: dict[str, Any]) -> None:
    with TemporaryDirectory() as directory:
        run = Path(directory)
        shutil.copy(run_analysis.FROZEN, run / "cases.json")
        (run / "results.json").write_text(json.dumps(ideal_results(manifest)), encoding="utf-8")
        (run / "submission.json").write_text("{}", encoding="utf-8")
        if run_analysis.main(["--run", str(run)]) != 0 or run_analysis.main(["--run", str(run)]) != 0:
            raise AssertionError("a rerun must reproduce analysis.json")
        if not json.loads((run / "analysis.json").read_text(encoding="utf-8"))["analysis"]["complete"]:
            raise AssertionError("the ideal run is incomplete")
        altered = copy.deepcopy(manifest)
        altered["settings"][0]["name"] = "altered"
        (run / "cases.json").write_text(json.dumps(altered), encoding="utf-8")
        with pytest.raises(ValueError, match="frozen request"):
            run_analysis.analyze_run(run)
