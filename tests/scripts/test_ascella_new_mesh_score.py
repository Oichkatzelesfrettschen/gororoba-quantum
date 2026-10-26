"""The preregistered new-seed score: mesh exclusion, within-job centering, degrees of freedom and outcome branches."""

from __future__ import annotations

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


def test_retained_runs_score_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    """Job-02 stands in for a new job against job-00; job-03 repeats every job-02 mesh and so scores nothing."""
    monkeypatch.setattr(score, "BASELINE_JOB", "job-00")
    record = score.score(
        EVIDENCE / "new-mesh-offsets.json", EVIDENCE / "fixed-mesh-confirmation.json", [JOB_00], [JOB_02, JOB_03]
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
        "exploration": {"reading": a, "share_upper": 0.05},
        "all-meshes": {"reading": b, "share_upper": 0.08},
    }
    if score.outcome(readings, steady, 0.1055) != expected:
        raise AssertionError(f"{a}, {b}, steady {steady} must read {expected}")


def test_an_upper_share_at_the_reference_reads_inconclusive() -> None:
    readings = {
        "exploration": {"reading": "not carried", "share_upper": 0.05},
        "all-meshes": {"reading": "not carried", "share_upper": 0.1055},
    }
    if score.outcome(readings, True, 0.1055) != "inconclusive":
        raise AssertionError("a bound at the held-out point estimate excludes nothing")
