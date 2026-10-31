"""Contracts of the Belenos in-situ visibility request: the frozen cases, their seeds and the windowed analysis."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
        iterations.append(
            {
                "iteration": {
                    "circuit_params": setting["circuit_params"],
                    "compilation_seed": setting["compilation_seed"],
                },
                "counts": counts,
            }
        )
    run = tmp_path / job
    run.mkdir(parents=True)
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


def _rewrite(run: Path, edit: Callable[[list[dict[str, Any]]], None]) -> Path:
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    edit(results["iterations"])
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    return run


def test_analysis_refuses_a_seed_that_binds_twice(tmp_path: Path) -> None:
    def duplicate(iterations: list[dict[str, Any]]) -> None:
        iterations[1] = json.loads(json.dumps(iterations[0]))

    with pytest.raises(RuntimeError, match="binds a second result iteration"):
        case.analyze(_rewrite(_run(tmp_path, "job-00", 0.9), duplicate))


def test_analysis_refuses_echoed_parameters_of_another_setting(tmp_path: Path) -> None:
    def swap(iterations: list[dict[str, Any]]) -> None:
        first = iterations[0]["iteration"]
        other = next(
            it["iteration"] for it in iterations if it["iteration"]["circuit_params"] != first["circuit_params"]
        )
        first["circuit_params"] = other["circuit_params"]

    with pytest.raises(RuntimeError, match="echoes other circuit_params"):
        case.analyze(_rewrite(_run(tmp_path, "job-00", 0.9), swap))


def test_an_incomplete_control_block_reports_no_visibility(tmp_path: Path) -> None:
    manifest = json.loads((case.CASES / "job-00" / "cases.json").read_text(encoding="utf-8"))
    control = {s["compilation_seed"] for s in manifest["settings"] if s["block"] == "control"}

    def drop(iterations: list[dict[str, Any]]) -> None:
        index = next(i for i, it in enumerate(iterations) if it["iteration"]["compilation_seed"] in control)
        iterations[index] = {"missing": True}

    record = case.analyze(_rewrite(_run(tmp_path, "job-00", 0.9), drop))
    if record["in_situ_visibility"] is not None or not record["overlap_reading"].startswith("undecided"):
        raise AssertionError((record["in_situ_visibility"], record["overlap_reading"]))


def test_homogeneous_meshes_pass_and_the_overlap_reading_follows_the_fit(tmp_path: Path) -> None:
    high = case.analyze(_run(tmp_path / "high", "job-00", 0.879))
    if high["control"]["mesh_heterogeneity"]["chi2"] > 1e-6 or high["control"]["mesh_heterogeneity"]["dof"] != 3:
        raise AssertionError(high["control"]["mesh_heterogeneity"])
    if not high["overlap_reading"].startswith("overlap high"):
        raise AssertionError(high["overlap_reading"])
    low = case.analyze(_run(tmp_path / "low", "job-00", 0.81))
    if not low["overlap_reading"].startswith("unresolved"):
        raise AssertionError(low["overlap_reading"])


def test_one_control_mesh_off_the_others_raises_the_spread(tmp_path: Path) -> None:
    manifest = json.loads((case.CASES / "job-00" / "cases.json").read_text(encoding="utf-8"))
    control = {s["compilation_seed"] for s in manifest["settings"] if s["block"] == "control"}
    window = manifest["window"]

    def shift(iterations: list[dict[str, Any]]) -> None:
        target = next(it for it in iterations if it["iteration"]["compilation_seed"] in control)
        law = case.base.two_click_law(case.base.route_operator("control", "LaLb"), 0.6)
        target["counts"] = {
            _state((int(p[0]) + window, int(p[1]) + window)): round(100000 * v) for p, v in law.items() if v > 1e-12
        }

    record = case.analyze(_rewrite(_run(tmp_path, "job-00", 0.879), shift))
    spread = record["control"]["mesh_heterogeneity"]
    if spread["p"] > 1e-6 or spread["birge_ratio"] <= 1:
        raise AssertionError(spread)
    visibility = record["in_situ_visibility"]
    if visibility["se_with_mesh_spread"] <= visibility["se"]:
        raise AssertionError(visibility)
