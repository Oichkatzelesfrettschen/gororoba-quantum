"""Contracts of the Belenos in-situ visibility request: the frozen cases, their seeds and the windowed analysis."""

from __future__ import annotations

import json
from pathlib import Path

import belenos_associator_visibility as case
import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_retained_requests_rebuild_bind_and_reach_the_ideal() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen requests do not check")


@pytest.mark.parametrize(("job", "start"), [("job-00", 0), ("job-01", 8)])
def test_compilation_seeds_are_the_registered_draw_values_in_index_order(job: str, start: int) -> None:
    values = json.loads((ROOT / case.SEED_DRAW).read_text(encoding="utf-8"))["values"]
    seeds = case.CASE_SEEDS[job]
    if list(seeds) != values[start : start + len(seeds)]:
        raise AssertionError(f"{job} does not take indices {start} onward of {case.SEED_DRAW}")
    name = f"{job.upper().replace('-', '_')}_COMPILATION_SEEDS"
    rows = [
        (row["record"], row["index"], row["value"])
        for row in json.loads((ROOT / "docs/evidence/qrng_seeds/allocations.json").read_text(encoding="utf-8"))[
            "allocations"
        ]
        if row["path"] == "scripts/belenos_associator_visibility.py" and row["name"] == name
    ]
    if rows != [(case.SEED_DRAW, start + i, seed) for i, seed in enumerate(seeds)]:
        raise AssertionError(f"the allocation rows differ from {name}")
    manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
    if [s["compilation_seed"] for s in manifest["settings"]] != list(seeds):
        raise AssertionError(f"{job}: the retained settings carry other seeds")


def test_windows_put_the_photons_on_the_teleportation_source_pairs() -> None:
    if case.photon_modes(case.WINDOWS["job-00"]) != (18, 20) or case.photon_modes(case.WINDOWS["job-01"]) != (20, 22):
        raise AssertionError("the windows moved off the teleportation sources")


def _state(occupied: tuple[int, ...]) -> str:
    return "|" + ",".join("1" if mode in occupied else "0" for mode in range(case.MODES)) + ">"


def _run(tmp_path: Path, job: str, visibility: float) -> Path:
    """A run whose counts follow the mixture law of each setting on its window, plus events the analysis excludes."""
    manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
    window = manifest["window"]
    iterations = []
    for setting in reversed(manifest["settings"]):
        law = case.base.two_click_law(case.base.route_operator(setting["block"], setting["route"]), visibility)
        counts = {
            _state((int(p[0]) + window, int(p[1]) + window)): round(100000 * v) for p, v in law.items() if v > 1e-12
        }
        counts[_state((window - 1, window))] = 7
        counts[_state((window, window + 1, window + 2))] = 3
        iterations.append({"iteration": {"compilation_seed": setting["compilation_seed"]}, "counts": counts})
    run = tmp_path / job
    run.mkdir()
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "results.json").write_text(json.dumps({"iterations": iterations}), encoding="utf-8")
    return run


@pytest.mark.parametrize("job", sorted(case.WINDOWS))
@pytest.mark.parametrize("visibility", [1.0, 0.86, 0.81])
def test_analysis_recovers_the_visibility_on_each_window(tmp_path: Path, job: str, visibility: float) -> None:
    record = case.analyze(_run(tmp_path, job, visibility))
    if abs(record["in_situ_visibility"]["V_eff"] - visibility) > 1e-4:
        raise AssertionError(record["in_situ_visibility"])
    if record["excluded_by_cause"] != {
        "three_or_more_clicks": 24,
        "two_clicks_outside_window": 56,
        "fewer_than_two_clicks": 0,
    }:
        raise AssertionError(record["excluded_by_cause"])
    decisions = record["decisions"]
    if decisions["associator_realised"] is not True or decisions["visibility_closure"] is not True:
        raise AssertionError(decisions)


def test_analysis_refuses_a_result_iteration_outside_the_case(tmp_path: Path) -> None:
    run = _run(tmp_path, "job-00", 0.9)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    results["iterations"][0]["iteration"]["compilation_seed"] = 1
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(RuntimeError, match="outside the case"):
        case.analyze(run)
