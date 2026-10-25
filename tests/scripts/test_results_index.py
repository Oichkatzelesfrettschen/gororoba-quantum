"""results_index joins the registry, provider runs and Kaggle receipts without writing to the tree."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from collections import Counter
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest
import research_state
import results_index

IBM_RUN = "results/live/2026-01-01T000000Z"
QD_RUN = "results/quandela/runs/2026-01-02T000000Z-case"
KAGGLE_DONE = "2026-01-03T000000Z-owner-done"
KAGGLE_OPEN = "2026-01-04T000000Z-owner-open"


class _Provider:
    def __init__(self, runs: dict[str, dict[str, Any]], jobs: list[dict[str, str]] | None = None) -> None:
        self._runs = runs
        self.jobs = jobs or []

    def runs(self) -> dict[str, dict[str, Any]]:
        return self._runs


class _Context:
    def __init__(self) -> None:
        facts = {"backends": ["dev"], "statuses": Counter({"DONE": 1}), "created_at": "2026-01-01T00:00:00+00:00"}
        self.providers = {
            "ibm": _Provider({IBM_RUN: facts}, [{"job_id": "ibm-job", "run": IBM_RUN}]),
            "quandela": _Provider({QD_RUN: facts}),
        }


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> results_index.Index:
    root = tmp_path / "repo"
    _write(root / QD_RUN / "submission.json", {"job_id": "qd-job"})
    (root / IBM_RUN / "raw/ibm-job").mkdir(parents=True)
    (root / IBM_RUN / "raw/ibm-job/pub_00.json").write_text("{}")
    claim = {
        "id": "claim-a",
        "status": "established",
        "evidence_class": "preregistered hardware inference",
        "domain": "hardware",
        "statement": "s",
        "evidence": [{"path": "docs/evidence/x.json", "sha256": "0" * 64}],
        "documents": ["docs/x.md"],
        "gates": {"core-1": "replay"},
        "acquisitions": ["acq-ibm", "acq-qd"],
        "depends_on": [],
    }
    registry = {
        "acquisitions": [
            {"id": "acq-ibm", "provider": "ibm", "run": IBM_RUN, "family": "f", "question": "q"},
            {"id": "acq-qd", "provider": "quandela", "run": QD_RUN, "family": "f", "question": "q"},
        ],
        "claims": [claim],
    }
    _write(root / "docs/state/research_state.json", registry)
    kaggle = root / "results/kaggle"
    for name in (KAGGLE_DONE, KAGGLE_OPEN):
        _write(kaggle / name / "submission.json", {"kernel": "owner/slug", "kernel_version": 1, "machine_shape": "cpu"})
    (kaggle / KAGGLE_DONE / "output").mkdir()
    _write(kaggle / KAGGLE_DONE / "collect.json", {"schema": "kaggle-aer-collect-v1", "state": "COMPLETE", "files": {}})
    monkeypatch.setattr(results_index, "ROOT", root)
    monkeypatch.setattr(results_index, "KAGGLE", kaggle)
    monkeypatch.setattr(research_state, "REGISTRY", root / "docs/state/research_state.json")
    monkeypatch.setattr(research_state, "Context", _Context)
    monkeypatch.chdir(root)
    return results_index.Index()


def test_joins_runs_jobs_acquisitions_and_claims(index: results_index.Index) -> None:
    summary = index.summary()
    if summary["unregistered_runs"] or summary["acquisitions_without_run"]:
        raise RuntimeError(f"coverage gaps: {summary}")
    if summary["kaggle_uncollected"] != [f"results/kaggle/{KAGGLE_OPEN}"]:
        raise RuntimeError(f"uncollected Kaggle runs: {summary['kaggle_uncollected']}")
    if [row["acquisition"] for row in index.job("qd-job")] != ["acq-qd"]:
        raise RuntimeError("a Quandela job resolves through its submission.json")
    if [row["path"] for row in index.job("owner/slug/1")] != sorted(
        f"results/kaggle/{name}" for name in (KAGGLE_DONE, KAGGLE_OPEN)
    ):
        raise RuntimeError("a Kaggle kernel reference resolves to every run that pushed it")
    if sorted(row["path"] for row in index.claim("claim-a")["runs"]) != sorted([IBM_RUN, QD_RUN]):
        raise RuntimeError("a claim resolves to the runs of its acquisitions")
    with pytest.raises(SystemExit, match="no claim"):
        index.claim("absent")


def test_path_lookup_names_owner_and_citing_claims(index: results_index.Index) -> None:
    owner = index.path(f"{IBM_RUN}/raw/ibm-job/pub_00.json")
    if [row["path"] for row in owner["runs"]] != [IBM_RUN] or owner["runs"][0]["claims"] != ["claim-a"]:
        raise RuntimeError(f"raw file owner: {owner}")
    if index.path("docs/evidence/x.json")["claims_citing"] != ["claim-a"]:
        raise RuntimeError("an evidence file names the claim citing it")
    with pytest.raises(SystemExit, match="outside the repository"):
        index.path("/")


def test_sqlite_is_a_cache_outside_the_tree(index: results_index.Index, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="inside the repository"):
        index.write_sqlite(results_index.ROOT / "index.sqlite")
    out = tmp_path / "cache" / "index.sqlite"
    counts = index.write_sqlite(out)
    with pytest.raises(SystemExit, match="exists"):
        index.write_sqlite(out)
    with closing(sqlite3.connect(out)) as db:
        joined = db.execute(
            "SELECT COUNT(*) FROM acquisitions a JOIN runs r ON r.path = a.run AND r.acquisition = a.id"
        ).fetchone()[0]
    if joined != 2 or counts["runs"] != 4 or counts["jobs"] != 4:
        raise RuntimeError(f"sqlite rows {counts}, joined acquisitions {joined}")


@pytest.mark.audit
def test_retained_tree_joins_completely() -> None:
    """Every acquisition owns its run and every job resolves, on the retained tree; the build leaves git clean."""

    def status() -> str:
        return subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=results_index.ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    before = status()
    index = results_index.Index()
    summary = index.summary()
    if summary["acquisitions_without_run"] or summary["unregistered_runs"]:
        raise RuntimeError(f"coverage gaps: {summary}")
    for run in index.runs.values():
        for job in run.jobs:
            if run.path not in [row["path"] for row in index.job(job)]:
                raise RuntimeError(f"job {job} does not resolve to {run.path}")
    for claim in index.claims.values():
        expected = sorted(index.acquisitions[a]["run"] for a in claim["acquisitions"])
        if sorted(row["path"] for row in index.claim(claim["id"])["runs"]) != expected:
            raise RuntimeError(f"{claim['id']} runs differ from its acquisitions")
    if status() != before:
        raise RuntimeError("building the index changed the working tree")
