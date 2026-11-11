"""results_index joins the registry, provider runs and Kaggle receipts without writing to the tree."""

from __future__ import annotations

import hashlib
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
    absent = "is absent from the fixture"
    source = "the fixture"

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
        self.gates = {"core-1": '"$PYTHON" scripts/replay.py'}
        self.digest = research_state.digest


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
        "boundary": "The fixture establishes a descriptive result on its named runs.",
        "evidence": [{"path": "results/analysis.json", "sha256": hashlib.sha256(b"{}").hexdigest()}],
        "documents": ["docs/x.md"],
        "gates": {"core-1": "replay"},
        "acquisitions": ["acq-ibm", "acq-qd"],
        "depends_on": [],
    }
    registry = {
        "schema": research_state.SCHEMA,
        "acquisitions": [
            {"id": "acq-ibm", "provider": "ibm", "run": IBM_RUN, "family": "f", "question": "q"},
            {"id": "acq-qd", "provider": "quandela", "run": QD_RUN, "family": "f", "question": "q"},
        ],
        "claims": [
            claim,
            {
                "id": "claim-bare",
                "status": "proposed",
                "evidence_class": "proposed experiment",
                "domain": "algebra",
                "statement": "s",
                "boundary": "A proposed design has no measured outcome.",
            },
        ],
    }
    _write(root / "results/analysis.json", {})
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs/x.md").write_text("Fixture documentation.")
    _write(root / "docs/state/research_state.json", registry)
    kaggle = root / "results/kaggle"
    for name in (KAGGLE_DONE, KAGGLE_OPEN):
        _write(kaggle / name / "submission.json", {"kernel": "owner/slug", "kernel_version": 1, "machine_shape": "cpu"})
    (kaggle / KAGGLE_DONE / "output").mkdir()
    _write(kaggle / KAGGLE_DONE / "collect.json", {"schema": "kaggle-aer-collect-v1", "state": "COMPLETE", "files": {}})
    monkeypatch.setattr(results_index, "ROOT", root)
    monkeypatch.setattr(results_index, "KAGGLE", kaggle)
    monkeypatch.setattr(research_state, "REGISTRY", root / "docs/state/research_state.json")
    monkeypatch.setattr(research_state, "ROOT", root)
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
    bare = index.claim("claim-bare")
    if bare["runs"] or bare["evidence"] or bare["gates"] or bare["depends_on"] or bare["documents"]:
        raise RuntimeError(f"a claim omitting its optional fields reads them empty: {bare}")
    with pytest.raises(SystemExit, match="no claim"):
        index.claim("absent")


def test_claim_names_missing_runs_and_unknown_acquisitions(index: results_index.Index) -> None:
    del index.runs[QD_RUN]
    with pytest.raises(
        SystemExit, match=f"claim claim-a cites runs the tree does not hold: acquisition acq-qd names run {QD_RUN}$"
    ):
        index.claim("claim-a")
    registry = json.loads(research_state.REGISTRY.read_text(encoding="utf-8"))
    registry["claims"][0]["acquisitions"].append("acq-ghost")
    _write(research_state.REGISTRY, registry)
    with pytest.raises(ValueError, match="claim claim-a: acquisition acq-ghost is not registered"):
        results_index.Index()


def test_path_lookup_names_owner_and_citing_claims(index: results_index.Index) -> None:
    owner = index.path(f"{IBM_RUN}/raw/ibm-job/pub_00.json")
    if [row["path"] for row in owner["runs"]] != [IBM_RUN] or owner["runs"][0]["claims"] != ["claim-a"]:
        raise RuntimeError(f"raw file owner: {owner}")
    if index.path("results/analysis.json")["claims_citing"] != ["claim-a"]:
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
    with closing(sqlite3.connect(out)) as db:
        boundary, replay = db.execute(
            "SELECT boundary, numerical_replay FROM claim_qualifications WHERE claim='claim-a'"
        ).fetchone()
    if boundary != index.claims["claim-a"]["boundary"] or replay != "not-run-by-ledger":
        raise RuntimeError("SQLite drops the inference boundary or invents a replay")


@pytest.mark.parametrize("mutation", ["bytes", "class", "cycle"])
def test_index_refuses_invalid_registry(index: results_index.Index, mutation: str) -> None:
    registry = json.loads(research_state.REGISTRY.read_text(encoding="utf-8"))
    if mutation == "bytes":
        (results_index.ROOT / "results/analysis.json").write_text('{"changed": true}')
    elif mutation == "class":
        registry["claims"][0]["status"] = "exploratory"
    else:
        registry["claims"][0]["depends_on"] = ["claim-a"]
    _write(research_state.REGISTRY, registry)
    with pytest.raises(ValueError):
        results_index.Index()


def test_provider_qualifies_colliding_job_ids(index: results_index.Index) -> None:
    index.runs[QD_RUN].jobs = ["ibm-job"]
    index.job_runs["ibm-job"].append(QD_RUN)
    if len(index.job("ibm-job")) != 2:
        raise RuntimeError("an unqualified lookup loses a provider occurrence")
    if [row["path"] for row in index.job("ibm-job", "ibm")] != [IBM_RUN]:
        raise RuntimeError("a provider-qualified lookup mixes providers")


def test_claim_preserves_qualifications_and_observation_scope(index: results_index.Index) -> None:
    claim = index.claim("claim-a")
    if claim["boundary"] != index.claims["claim-a"]["boundary"]:
        raise RuntimeError("claim lookup loses its inference boundary")
    if claim["evidence_bindings"] != index.claims["claim-a"]["evidence"]:
        raise RuntimeError("claim lookup loses pinned evidence digests")
    observed = index.observation("results/analysis.json", "")
    if observed["value"] != {} or observed["claims_citing_file"][0]["id"] != "claim-a":
        raise RuntimeError("the source value loses its claim context")
    if observed["runs_holding_file"]:
        raise RuntimeError("an external analysis is incorrectly assigned to an acquisition directory")
    with pytest.raises(ValueError, match="separate JSON Pointer"):
        index.observation("results/analysis.json#rows/id=first", "")


def test_complete_ledger_keeps_algebra_scope_and_tracked_denominator(
    index: results_index.Index, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = results_index.ROOT
    algebra = root / "docs/evidence/a5-exceptional-fibers/ledger.tsv"
    algebra.parent.mkdir(parents=True)
    algebra.write_text("id\tstatus\tprimes\tclaim\nA5-001\tproved\t32009\tfinite-field identity\n")
    _write(root / "results/live/unindexed/record.json", {"state": "planned"})
    _write(root / "results/live/canceled/record.json", {"submission": {"jobs": [{"job_id": "canceled"}]}})
    _write(
        root / "results/live/mixed/record.json",
        {"submission": {"jobs": [{"job_id": "canceled"}, {"job_id": "unknown"}]}},
    )
    index.account_only_jobs = [
        {"provider": "ibm", "job_id": "canceled", "status": "CANCELLED", "provenance": "unexecuted_cancellation"}
    ]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", "results", "docs"], cwd=root, check=True)
    _write(root / "results/scratch.json", {"status": "untracked"})
    view = index.ledger()
    if view["algebra_findings"]["rows"][0]["primes"] != "32009":
        raise RuntimeError("a finite-field finding loses its field restriction")
    if any(row["path"] == "results/scratch.json" for row in view["artifacts"]):
        raise RuntimeError("untracked scratch enters the artifact denominator")
    if view["gaps"]["untracked_claim_artifacts"]:
        raise RuntimeError("tracked claim documents outside evidence roots are incorrectly labeled untracked")
    if len(view["gaps"]["execution_records_outside_indexed_runs"]) != 3:
        raise RuntimeError("a planned record outside the adapters disappears")
    classifications = {row["path"]: row["classification"] for row in view["execution_candidates"]}
    if classifications["results/live/unindexed/record.json"] != "planning-only":
        raise RuntimeError("explicit planning state becomes an execution")
    if classifications["results/live/canceled/record.json"] != "audited unexecuted cancellation":
        raise RuntimeError("the audited cancellation loses its terminal observation")
    if classifications["results/live/mixed/record.json"] != "dispatched with a provider identity":
        raise RuntimeError("one canceled job erases another job's unresolved execution")
    monkeypatch.setattr(results_index, "Index", lambda: index)
    capsys.readouterr()
    if results_index.main(["--json", "ledger", "--summary"]) != 0:
        raise RuntimeError("the ledger command failed")
    summary = json.loads(capsys.readouterr().out)
    if summary != view["summary"]:
        raise RuntimeError("CLI summary differs from the complete ledger's denominator")


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
