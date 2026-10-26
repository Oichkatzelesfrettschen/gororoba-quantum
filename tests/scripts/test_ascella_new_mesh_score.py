"""The preregistered new-seed score: mesh exclusion, within-job centering, degrees of freedom and outcome branches."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_new_mesh_score as score  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
EVIDENCE = ROOT / "docs/evidence/ascella-order-coefficients"
JOB_00 = RUNS / "2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00"
JOB_02 = RUNS / "2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02"
JOB_03 = RUNS / "2026-10-26T035018Z-qpu_ascella-ascella_signed_coherence-job-03"


@pytest.mark.audit
def test_retained_runs_score_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    """Job-02 stands in for a new job against job-00; job-03 repeats every job-02 mesh and so scores nothing."""
    monkeypatch.setattr(score, "BASELINE_JOB", "job-00")
    record = score.score(
        EVIDENCE / "new-mesh-offsets.json",
        EVIDENCE / "fixed-mesh-confirmation.json",
        [JOB_00],
        [JOB_02, JOB_03],
        enforce=False,
    )
    first, second = record["jobs"]
    if (first["scored"], first["distinct_perturbed_meshes"], first["previously_served"]) != (True, 56, 0):
        raise AssertionError(f"job-02 must score its 56 perturbed meshes: {first}")
    if (second["scored"], second["previously_served"]) != (False, 56):
        raise AssertionError(f"job-03's meshes repeat job-02's and must not score: {second}")
    rows = record["rows"]
    if len(rows) != 56 or {row["job"] for row in rows} != {"job-02"}:
        raise AssertionError("the anchors or the repeated meshes entered the primary")
    observed = np.array([row["observed"] for row in rows])
    for name, label in score.LABELS.items():
        reading = record["primary"][label]
        expected = float(np.corrcoef([row[f"predicted_{name}"] for row in rows], observed)[0, 1])
        if abs(reading["pearson_r"] - expected) > 1e-12 or reading["degrees_of_freedom"] != 54:
            raise AssertionError(f"{label}: one job's centered r is Pearson r on n - 2 degrees of freedom")


def test_centering_removes_a_job_shift_and_spends_one_degree_per_job() -> None:
    predicted = np.array([0.1, 0.2, 0.3, 0.4, 0.15, 0.25, 0.35, 0.45])
    noise = np.array([0.01, -0.02, 0.015, -0.005, -0.01, 0.02, -0.015, 0.005])
    jobs = np.array(["a"] * 4 + ["b"] * 4)
    observed = predicted + noise + np.where(jobs == "b", 0.5, 0.0)
    shifted = score.primary(predicted, observed, jobs, 1.0)
    plain = score.primary(predicted, observed - np.where(jobs == "b", 0.5, 0.0), jobs, 1.0)
    if abs(shifted["pearson_r"] - plain["pearson_r"]) > 1e-12 or shifted["degrees_of_freedom"] != 5:
        raise AssertionError("a per-job shift must leave r unchanged, on n - 1 - J degrees of freedom")
    error = 1 / math.sqrt(8 - 2 - 2)
    if abs(math.atanh(shifted["r_upper"]) - math.atanh(shifted["pearson_r"]) - 2.5758293035489 * error) > 1e-9:
        raise AssertionError("the Fisher-z bound uses 1 / sqrt(n - J - 2)")


def test_too_few_meshes_or_flat_predictions_are_not_read() -> None:
    jobs = np.array(["a", "a", "b", "b"])
    if score.primary(np.array([0.1, 0.2, 0.3, 0.4]), np.array([0.1, 0.3, 0.2, 0.4]), jobs, 1.0)["reading"] != (
        "not read"
    ):
        raise AssertionError("n - J - 2 < 1 must not be read")
    jobs = np.array(["a"] * 5)
    if score.primary(np.full(5, 0.3), np.arange(5.0), jobs, 1.0)["reading"] != "not read":
        raise AssertionError("constant predictions must not be read")


@pytest.mark.parametrize(
    ("a", "b", "steady", "expected"),
    [
        ("carried", "carried", False, "both carried"),
        ("carried", "not carried", True, "P-A carried only"),
        ("not carried", "carried", False, "P-B carried only"),
        ("not carried", "not carried", False, "inconclusive: anchors moved"),
        ("not carried", "not carried", True, "bounded"),
    ],
)
def test_outcome_branches_are_disjoint(a: str, b: str, steady: bool, expected: str) -> None:
    readings = {
        "exploration": {"reading": a, "share_upper": 0.05, "r_upper": 0.2},
        "all-meshes": {"reading": b, "share_upper": 0.08, "r_upper": 0.25},
    }
    if score.outcome(readings, steady, 0.1055) != expected:
        raise AssertionError(f"{a}, {b}, steady {steady} must read {expected}")


def test_an_upper_share_at_the_reference_reads_inconclusive() -> None:
    readings = {
        "exploration": {"reading": "not carried", "share_upper": 0.05, "r_upper": 0.2},
        "all-meshes": {"reading": "not carried", "share_upper": 0.1055, "r_upper": 0.3},
    }
    if score.outcome(readings, True, 0.1055) != "inconclusive":
        raise AssertionError("a bound at the held-out point estimate excludes nothing")


@pytest.mark.parametrize(
    ("duration", "complete", "expected"),
    [(186, True, 96), (232.5, True, 96), (240, True, 88), (253.6, True, 88), (260, True, 80), (279, True, 80)]
    + [(279.5, True, None), (200, False, None), (None, True, None)],
)
def test_job_05_size_follows_job_04_duration_alone(
    duration: float | None, complete: bool, expected: int | None
) -> None:
    if score.job_05_iterations({"duration": duration, "complete": complete}) != expected:
        raise AssertionError(f"job-04 at {duration} s, complete {complete}, must admit {expected}")


@pytest.mark.audit
def test_a_truncated_retained_run_is_partial(tmp_path: Path) -> None:
    run = tmp_path / "truncated"
    run.mkdir()
    (run / "cases.json").write_bytes((JOB_02 / "cases.json").read_bytes())
    results = json.loads((JOB_02 / "results.json").read_text(encoding="utf-8"))
    results["iterations"] = results["iterations"][:40]
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    summary = score.returned(run)
    if summary["complete"] or summary["returned_iterations"] != 40 or summary["requested_iterations"] != 64:
        raise AssertionError(f"a run returning 40 of 64 iterations must read partial: {summary}")


@pytest.mark.audit
def test_a_score_without_scored_meshes_replays() -> None:
    """Job-02's meshes all repeat job-03's, so nothing scores, and the record still replays against itself."""
    record = score.score(
        EVIDENCE / "new-mesh-offsets.json",
        EVIDENCE / "fixed-mesh-confirmation.json",
        [JOB_00, JOB_03],
        [JOB_02],
        enforce=False,
    )
    if record["rows"] or record["outcome"] != "not read" or record["ceiling"]["squared"] is not None:
        raise AssertionError("a score with no admitted mesh must read not read with no ceiling")
    text = json.dumps(record, indent=1, sort_keys=True)
    score.models.replay(json.loads(text), json.loads(text), "empty score")


def test_admission_excludes_served_meshes_and_counts_a_repeat_once() -> None:
    seen = {"m0", "m1"}
    old, keep = score.admitted(["m0", "m2", "m3", "m1"], [1, 2, 3], seen)
    if (old, keep) != ([3], [1, 2]):
        raise AssertionError("served meshes leave the primary and new ones enter it")
    seen.update(["m0", "m2", "m3", "m1"])
    if score.admitted(["m2", "m4"], [0, 1], seen) != ([0], [1]):
        raise AssertionError("a mesh a first new job served counts in that job alone")


def test_a_run_without_counts_is_partial(tmp_path: Path) -> None:
    run = tmp_path / "empty"
    run.mkdir()
    manifest = {"job": "job-04", "iterations": 2, "settings": [{"name": "a"}, {"name": "b"}]}
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "results.json").write_text(json.dumps({"partial": True, "status": {"status": "error"}}), encoding="utf-8")
    summary = score.returned(run)
    if summary["complete"] or summary["returned_iterations"] != 0 or summary["status"] != "error":
        raise AssertionError(f"a run returning no counts must read partial: {summary}")


def test_an_anticorrelated_predictor_never_reads_bounded() -> None:
    readings = {
        "exploration": {"reading": "not carried", "share_upper": 0.0, "r_upper": -0.4},
        "all-meshes": {"reading": "not carried", "share_upper": 0.02, "r_upper": 0.1},
    }
    if score.outcome(readings, True, 0.1055) != "inconclusive: anticorrelated":
        raise AssertionError("an upper bound of r below zero refutes the signed predictor, not its share")


@pytest.mark.parametrize("sign", [1.0, -1.0])
def test_a_perfect_correlation_reads_at_its_endpoint(sign: float) -> None:
    predicted = np.array([0.1, 0.4, 0.2, 0.5, 0.3, 0.6])
    reading = score.primary(predicted, sign * predicted, np.array(["a"] * 6), 1.0)
    if reading["t"] is not None or reading["r_upper"] != sign or reading["p_one_sided"] != (0.0 if sign > 0 else 1.0):
        raise AssertionError(f"r = {sign} must read at the endpoint without dividing by zero: {reading}")


def test_a_non_finite_input_is_not_read() -> None:
    observed = np.array([0.1, 0.4, np.nan, 0.5, 0.3, 0.6])
    if score.primary(np.arange(6.0), observed, np.array(["a"] * 6), 1.0)["reading"] != "not read":
        raise AssertionError("a NaN statistic must never reach a verdict")


def synthetic_run(tmp_path: Path, counts: list[dict[str, int]], seeds: list[int], echoed: list[int]) -> Path:
    run = tmp_path / "run"
    run.mkdir()
    settings = [
        {"name": f"s{i}", "circuit_params": {"x0": 0.0}, "compilation_seed": seed} for i, seed in enumerate(seeds)
    ]
    manifest = {"job": "job-04", "iterations": len(seeds), "settings": settings}
    entries = [
        {"counts": c, "iteration": {"circuit_params": {"x0": 0.0}, "compilation_seed": e}}
        for c, e in zip(counts, echoed, strict=True)
    ]
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    results = {"iterations": entries, "status": {"status": "completed", "duration": 200}}
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    return run


LOGICAL = "1,0,0,0,0,0,0,0,0,0,0,0"
OUTSIDE = "0,0,0,0,1,0,0,0,0,0,0,0"


def test_a_setting_without_logical_block_counts_makes_the_run_partial(tmp_path: Path) -> None:
    summary = score.returned(synthetic_run(tmp_path, [{LOGICAL: 5}, {OUTSIDE: 7}], [0, 11], [0, 11]))
    if summary["complete"] or summary["empty_logical_block"] != 1:
        raise AssertionError(f"an iteration with no logical-block count must make the run partial: {summary}")


def test_a_swapped_compilation_seed_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="compilation_seed"):
        score.returned(synthetic_run(tmp_path, [{LOGICAL: 5}, {LOGICAL: 7}], [0, 11], [11, 0]))


def summary(job: str, duration: float = 200.0, complete: bool = True) -> dict[str, object]:
    return {"job": job, "duration": duration, "complete": complete, "cases_sha256": f"digest-{job}"}


FROZEN = {name: f"digest-{name}" for name in ("job-04", "job-05-i80", "job-05-i88", "job-05-i96")}


def test_the_acquisition_requires_the_admitted_job_05() -> None:
    score.acquisition([summary("job-04", 240.0), summary("job-05-i88")], FROZEN)
    score.acquisition([summary("job-04", 290.0)], FROZEN)
    score.acquisition([summary("job-04", 200.0, complete=False)], FROZEN)
    for runs in (
        [summary("job-04", 200.0)],
        [summary("job-04", 240.0), summary("job-05-i96")],
        [summary("job-05-i88")],
        [summary("job-04", 290.0), summary("job-05-i80")],
        [summary("job-04", 240.0), summary("job-05-i88"), summary("job-05-i88")],
    ):
        with pytest.raises(ValueError):
            score.acquisition(runs, FROZEN)
    with pytest.raises(ValueError, match="frozen case"):
        score.acquisition([{**summary("job-04", 290.0), "cases_sha256": "edited"}], FROZEN)
