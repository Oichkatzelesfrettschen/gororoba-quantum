"""The preregistered replication score: its acquisition rule, labels and reference share."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_new_mesh_score as base  # noqa: E402
import ascella_replication_score as replication  # noqa: E402

FROZEN = {name: f"digest-{name}" for name in ("job-06", "job-07-i88", "job-07-i96")}


def summary(job: str, complete: bool = True) -> dict[str, object]:
    return {"job": job, "duration": 287.0, "complete": complete, "cases_sha256": f"digest-{job}"}


def test_job_07_follows_job_06_completion() -> None:
    design = replication.REPLICATION
    base.acquisition([summary("job-06"), summary("job-07-i96")], FROZEN, design)
    base.acquisition([summary("job-06", complete=False), summary("job-07-i88")], FROZEN, design)
    for runs in (
        [summary("job-06")],
        [summary("job-06"), summary("job-07-i88")],
        [summary("job-06", complete=False), summary("job-07-i96")],
        [summary("job-07-i96")],
        [summary("job-04"), summary("job-05-i88")],
    ):
        with pytest.raises(ValueError):
            base.acquisition(runs, FROZEN, design)


def test_outcomes_name_the_replication_predictors() -> None:
    design = replication.REPLICATION
    carried = {"reading": "carried", "share_upper": 0.3, "r_upper": 0.5}
    missed = {"reading": "not carried", "share_upper": 0.05, "r_upper": 0.2}
    cases = (
        ({"all-meshes": carried, "all-served": missed}, "R-B carried only"),
        ({"all-meshes": missed, "all-served": carried}, "R-C carried only"),
        ({"all-meshes": missed, "all-served": missed}, "bounded"),
    )
    for readings, expected in cases:
        if base.outcome(readings, True, 0.105, design) != expected:
            raise AssertionError(f"{readings} must read {expected}")


def test_the_design_excludes_every_retained_mesh_and_compares_against_p_b() -> None:
    design = replication.REPLICATION
    if design.reference_jobs != ("job-00", "job-02", "job-03", "job-04", "job-05-i88"):
        raise AssertionError("the replication excludes every mesh the retained runs served")
    if (design.baseline_job, design.reference_label, design.first_partial_unread) != ("job-05-i88", "P-B", False):
        raise AssertionError("job-05-i88 sets the baseline, P-B's share the bound, and a partial job-06 is descriptive")
