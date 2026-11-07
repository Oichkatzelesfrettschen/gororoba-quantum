"""The ensemble case's settings, schedule, scores, tests and binding on bounded fixtures."""

from __future__ import annotations

import copy
from typing import Any

import ascella_cz_ensemble_case as case
import ascella_cz_tomography_case as tomo
import numpy as np
import pytest


def test_every_setting_has_one_correct_outcome_and_matches_its_permanents() -> None:
    for row in case.base_settings():
        outcome = case.correct_outcome(row)
        conditional, accepted = case.exact_outcomes(row)
        if abs(conditional[outcome] - 1.0) > 1e-9 or abs(accepted - 1.0 / 9.0) > 1e-9:
            raise AssertionError(f"{row['name']}: the Ralph CZ misses the ideal outcome {outcome} or 1/9 success")


def test_hofmann_scores_of_the_design_counterexample() -> None:
    """The design's Kraus operator (CZ / 3) diag(1, 0.1, 0.1, 0.1): F' = 0.7995 on both tables violates the bound
    around its process fidelity 0.410, while the rate-weighted scores give [0.214, 0.607]."""
    kraus = tomo.ideal_cz() @ np.diag([1.0, 0.1, 0.1, 0.1]) / 3
    scores = case.map_scores(kraus)
    lower = scores["F_ZX"] + scores["F_XZ"] - 1
    upper = min(scores["F_ZX"], scores["F_XZ"])
    for name, value, expected in (
        ("F'_ZX", scores["F_prime_ZX"], 0.7995),
        ("F'_XZ", scores["F_prime_XZ"], 0.7995),
        ("process fidelity", scores["process_fidelity"], 0.410),
        ("lower", lower, 0.214),
        ("upper", upper, 0.607),
    ):
        if abs(value - expected) > 5e-4:
            raise AssertionError(f"{name} reads {value}, the design states {expected}")
    if not lower <= scores["process_fidelity"] <= upper or scores["F_prime_ZX"] + scores["F_prime_XZ"] - 1 <= 0.410:
        raise AssertionError("the rate-weighted interval misses the fidelity or the per-input bound holds")
    ideal = case.map_scores(tomo.ideal_cz())
    if any(abs(value - 1.0) > 1e-12 for value in ideal.values()):
        raise AssertionError(f"the ideal CZ scores {ideal}")


@pytest.mark.parametrize("job", case.JOBS)
def test_schedule_holds_anchor_positions_balance_and_seed_identity(job: str) -> None:
    case.check_schedule(job)
    rows = case.job_schedule(job)
    other = case.job_schedule(case.JOBS[1 - case.JOBS.index(job)])
    anchors = {(r["setting"], r["compilation_seed"]) for r in rows if r["role"] == "anchor"}
    if anchors != {(r["setting"], r["compilation_seed"]) for r in other if r["role"] == "anchor"} or len(anchors) != 4:
        raise AssertionError("the anchors do not request one seed each, the same in both jobs")
    seeds = {r["compilation_seed"] for r in rows if r["role"] == "ensemble"}
    if seeds & {r["compilation_seed"] for r in other if r["role"] == "ensemble"}:
        raise AssertionError("an ensemble seed serves both jobs")


def test_homogeneity_separates_one_law_from_two() -> None:
    generator = np.random.default_rng(7)
    same = np.asarray([[900, 30, 40, 30]] * 5)
    split = np.asarray([[900, 30, 40, 30]] * 4 + [[700, 230, 40, 30]])
    held = case.homogeneity(same, generator, tables=2000)
    moved = case.homogeneity(split, generator, tables=2000)
    if held["p"] < 0.5 or moved["p"] != 1 / 2001:
        raise AssertionError(f"homogeneity reads p {held['p']} for one law and {moved['p']} for two")
    sparse = case.homogeneity(np.asarray([[500, 0, 3, 0], [480, 0, 5, 0]]), generator, tables=2000)
    if sparse["rows"] != 2 or not 0 < sparse["p"] <= 1:
        raise AssertionError("an empty outcome column breaks the test")


def tally(row: dict[str, Any], eligible: list[int], shots: int = 200000, digest: str = "mesh") -> dict[str, Any]:
    return {
        "setting": row["setting"],
        "role": row["role"],
        "seed_index": row.get("seed_index"),
        "correct_outcome": case.correct_outcome(row),
        "eligible": eligible,
        "shots": shots,
        "digest": f"{digest}-{row['setting']}",
    }


def synthetic_runs(ensemble_law: dict[str, list[int]] | None = None) -> dict[str, list[dict[str, Any]]]:
    """Both jobs at one law per setting; `ensemble_law` replaces the ensemble iterations' counts of named settings."""
    runs = {}
    for job in case.JOBS:
        rows = []
        for row in case.job_schedule(job):
            counts = [0, 0, 0, 0]
            counts[case.correct_outcome(row)] = 1800
            counts[(case.correct_outcome(row) + 1) % 4] = 200
            if ensemble_law and row["role"] == "ensemble" and row["setting"] in ensemble_law:
                counts = ensemble_law[row["setting"]]
            rows.append(tally(row, counts))
        runs[job] = rows
    return runs


def test_drift_reads_only_the_anchor_repeats(monkeypatch: pytest.MonkeyPatch) -> None:
    """An anchor setting's ensemble iterations, served by other meshes, never enter its drift tests."""
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    streams = [np.random.default_rng(k) for k in range(case.DRIFT_TESTS)]
    moved = synthetic_runs({name: [1000, 1000, 0, 0] for name in case.ANCHORS})
    result = case.drift(moved, streams)
    if not result["pooled"] or not all(test["p"] > result["threshold"] for test in result["tests"]):
        raise AssertionError("ensemble iterations of an anchor setting entered its drift tests")
    rows = {len(case.ANCHOR_STARTS)} | {2}
    if {test.get("rows") for test in result["tests"] if "rows" in test} != rows:
        raise AssertionError("a drift table does not hold five positions or two jobs")


def test_drift_unpools_on_a_recalibrated_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    runs = synthetic_runs()
    for t in runs[case.JOBS[1]]:
        if t["role"] == "anchor" and t["setting"] == case.ANCHORS[0]:
            t["digest"] = "recompiled"
    result = case.drift(runs, [np.random.default_rng(k) for k in range(case.DRIFT_TESTS)])
    if result["pooled"] or result["same_mesh_across_jobs"][case.ANCHORS[0]]:
        raise AssertionError("an anchor served by another mesh in job-01 still pools the jobs")


def test_scores_and_bound_follow_the_rate_weighting() -> None:
    runs = synthetic_runs()
    groups = case.ensemble_groups(runs)
    prediction = {table: {"F": 0.9} for table in case.TABLES}
    scores = case.score_estimates(groups, True, prediction)["pooled"]
    for table in case.TABLES:
        f = scores["tables"][table]["F"]
        if abs(f["mean"] - 0.9) > 1e-12 or f["df"] != 9:
            raise AssertionError(f"{table}: F reads {f['mean']} on {f['df']} degrees of freedom")
        if scores["tables"][table]["difference_from_tomography"]["reading"] != "contains_zero":
            raise AssertionError(f"{table}: a zero difference does not read contains_zero")
    bound = scores["hofmann_interval"]
    if abs(bound["L"] - 0.8) > 1e-12 or abs(bound["U"] - 0.9) > 1e-12:
        raise AssertionError(f"a constant table bounds to {bound}")
    split = case.score_estimates(groups, False, prediction)
    if set(split) != set(case.JOBS) or "hofmann_interval" in split[case.JOBS[0]]:
        raise AssertionError("unpooled jobs report a pooled bound")


def manifest_entries(job: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    settings: list[dict[str, Any]] = []
    for row in case.job_schedule(job):
        settings.append(
            {**row, "correct_outcome": case.correct_outcome(row), "circuit_params": {"x0": float(len(settings))}}
        )
    for setting in settings:
        if setting["role"] == "anchor":
            first = next(s for s in settings if s["role"] == "anchor" and s["setting"] == setting["setting"])
            setting["circuit_params"] = first["circuit_params"]
    entries = [
        {
            "counts": {"1,0,1,0,0,0,0,0,0,0,0,0": 300, "1,0,0,0,0,0,0,0,0,0,0,0": 50},
            "iteration": {"compilation_seed": s["compilation_seed"], "circuit_params": s["circuit_params"]},
            "result_fields": {"nb_shots_used": 9000, "computed_circuit": f"mesh-{s['setting']}"},
        }
        for s in settings
    ]
    return settings, entries


def test_binding_takes_five_anchor_repeats_and_refuses_a_sixth() -> None:
    settings, entries = manifest_entries(case.JOBS[0])
    tallies, missing = case.bind_entries("run", settings, list(reversed(entries)))
    if missing or len(tallies) == 0 or len(tallies) != case.ITERATIONS:
        raise AssertionError(f"{len(tallies)} tallies and {missing} missing from a complete run")
    anchor = next(e for e, s in zip(entries, settings, strict=True) if s["role"] == "anchor")
    ensemble = next(i for i, s in enumerate(settings) if s["role"] == "ensemble")
    extra = [*entries[:ensemble], copy.deepcopy(anchor), *entries[ensemble + 1 :]]
    with pytest.raises(RuntimeError, match="unbound or spent"):
        case.bind_entries("run", settings, extra)
    changed = copy.deepcopy(entries)
    changed[ensemble]["iteration"]["circuit_params"] = {"x0": -1.0}
    with pytest.raises(RuntimeError, match="echoes other params"):
        case.bind_entries("run", settings, changed)
    partial = copy.deepcopy(entries)
    partial[ensemble]["counts"] = {}
    tallies, missing = case.bind_entries("run", settings, partial)
    if missing != 1 or len(tallies) != case.ITERATIONS - 1:
        raise AssertionError("an iteration without counts is not counted as missing")


def test_a_short_iteration_leaves_the_case_undecided() -> None:
    runs = synthetic_runs()
    runs[case.JOBS[0]][7]["eligible"] = [100, 50, 0, 0]
    loaded = [
        {"job": job, "cases_sha256": "0" * 64, "tallies": runs[job], "uncounted": 0, "perfs": None} for job in case.JOBS
    ]
    record = case.summarize(loaded)
    if record["status"] != "undecided":
        raise AssertionError("an iteration below the eligible floor still decides the case")
