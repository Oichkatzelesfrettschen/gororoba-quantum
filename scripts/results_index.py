"""Read-only joins over the research registry, the provider run sets and the Kaggle receipts.

The index composes the validated provider adapters of research_state.py
(IBM retained-run audit, Quantum Inspire, Quandela and IQM run directories),
the registry's acquisitions and claims, and kaggle_run.receipt_chain. It
writes nothing under the repository: every answer is computed from the
retained files at call time, so it cannot go stale against them.

Subcommands:

- ``summary``: counts per provider and the coverage gaps below.
- ``runs [--provider P]``: every provider run and Kaggle run with its
  acquisition, backends, job ids and the claims citing it.
- ``job ID``: the run, acquisition and claims that hold a provider job id.
- ``claim ID``: a claim's acquisitions, their runs and job ids, its evidence
  files, documents and gates.
- ``path PATH``: the run, acquisition and claims a repository file belongs to.
- ``ledger``: the complete claim qualifications, artifact census, source metadata,
  A5 findings and unresolved links; ``--markdown`` renders the claim table.
- ``observation FILE --pointer /path``: an exact JSON value with its byte identity
  and citing claims; the command performs no statistical reanalysis.
- ``sqlite OUT``: the same relations as SQLite tables at OUT, a path outside
  the repository (default under ``${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum``),
  for ad hoc joins; the database is a cache rebuilt by this command.

``--json`` prints machine-readable output. Coverage gaps are provider runs
that no acquisition registers, acquisitions whose run the adapter does not
hold, and Kaggle submissions without a collection receipt.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from collections.abc import Iterable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import evidence_closure
import kaggle_run
import research_state

import quantum_ledger
from parallel import ordered_map

ROOT = research_state.ROOT
KAGGLE = kaggle_run.RESULTS


@dataclass
class Run:
    """One retained run directory and the facts its provider adapter or Kaggle receipts report."""

    path: str
    provider: str
    backends: list[str]
    statuses: dict[str, int]
    jobs: list[str]
    acquisition: str | None = None
    claims: list[str] = field(default_factory=list)
    created_at: str | None = None

    def row(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "provider": self.provider,
            "acquisition": self.acquisition,
            "created_at": self.created_at,
            "backends": self.backends,
            "statuses": self.statuses,
            "jobs": self.jobs,
            "claims": self.claims,
        }


def _claim_defaults() -> dict[str, Any]:
    """The empty values research_state.validate gives a claim's omitted optional fields."""
    fields = ("documents", "acquisitions", "assumptions", "depends_on", "supersedes", "related_claims", "evidence")
    return {**{name: [] for name in fields}, "gates": {}}


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_jobs(name: str, provider: Any, run: str) -> list[str]:
    """Provider job ids of one run, from the records the adapter validated."""
    if name == "ibm":
        return sorted(str(job["job_id"]) for job in provider.jobs if job["run"] == run)
    if name == "quantum_inspire":
        return [str(job.job_id) for job in provider.acquisitions[run].jobs]
    return [str(_json(ROOT / run / "submission.json")["job_id"])]


def _kaggle_runs() -> list[Run]:
    runs = []
    for submission_path in sorted(KAGGLE.glob("*/submission.json")):
        run_dir = submission_path.parent
        submission = _json(submission_path)
        states: dict[str, int] = {}
        for receipt in kaggle_run.receipt_chain(run_dir):
            state = _json(receipt)["state"]
            states[state] = states.get(state, 0) + 1
        runs.append(
            Run(
                path=run_dir.relative_to(ROOT).as_posix(),
                provider="kaggle",
                backends=[str(submission.get("machine_shape") or submission.get("machine") or "")],
                statuses=states or {"UNCOLLECTED": 1},
                jobs=[kaggle_run.kernel_ref(submission)],
            )
        )
    return runs


def _execution_candidate(item: tuple[Path, str]) -> dict[str, Any]:
    root, reference = item
    path = quantum_ledger.local_file(root, reference)
    content = path.read_bytes()
    record = json.loads(content)
    if reference.startswith("results/live/") and path.name == "record.json" and isinstance(record, dict):
        classification = evidence_closure.classify_record(record, (path.parent / "collect.json").is_file())
    else:
        classification = {
            "classification": "schema requires a provider-specific reader",
            "state": record.get("state") if isinstance(record, dict) else None,
        }
    return {"path": reference, "sha256": hashlib.sha256(content).hexdigest(), **classification}


class Index:
    """Runs, acquisitions and claims joined by run path and job id."""

    def __init__(self) -> None:
        self.registry: dict[str, Any] = _json(research_state.REGISTRY)
        context = research_state.Context()
        research_state.validate(self.registry, context)
        self.gates = context.gates
        self.account_only_jobs = [
            {
                "provider": "ibm",
                "job_id": job["job_id"],
                "status": job["status"],
                "provenance": job.get("provenance"),
                "final_qpu_charge_seconds": job.get("final_qpu_charge_seconds"),
            }
            for job in cast(research_state.IbmRuns, context.providers["ibm"]).jobs
            if job.get("run") is None
        ]
        self.runs: dict[str, Run] = {}
        for name, provider in context.providers.items():
            for path, facts in provider.runs().items():
                self.runs[path] = Run(
                    path=path,
                    provider=name,
                    backends=sorted(facts.get("backends", [])),
                    statuses=dict(facts["statuses"]),
                    jobs=_provider_jobs(name, provider, path),
                    created_at=facts.get("created_at"),
                )
        for run in _kaggle_runs():
            self.runs[run.path] = run
        self.claims: dict[str, dict[str, Any]] = {
            claim["id"]: {**_claim_defaults(), **claim} for claim in self.registry["claims"]
        }
        self.acquisitions: dict[str, dict[str, Any]] = {a["id"]: a for a in self.registry["acquisitions"]}
        self.unheld: list[str] = []
        for acquisition in self.acquisitions.values():
            held = self.runs.get(acquisition["run"])
            if held is None:
                self.unheld.append(acquisition["id"])
                continue
            held.acquisition = acquisition["id"]
        for claim in self.claims.values():
            for acquisition_id in claim["acquisitions"]:
                if acquisition_id not in self.acquisitions:
                    raise SystemExit(
                        f"claim {claim['id']} cites acquisition {acquisition_id}, which the registry lacks"
                    )
                run_path = self.acquisitions[acquisition_id]["run"]
                if run_path in self.runs:
                    self.runs[run_path].claims.append(claim["id"])
        self.job_runs: dict[str, list[str]] = {}
        for run in self.runs.values():
            for job in run.jobs:
                self.job_runs.setdefault(job, []).append(run.path)

    def summary(self) -> dict[str, Any]:
        providers: dict[str, dict[str, int]] = {}
        for run in self.runs.values():
            entry = providers.setdefault(run.provider, {"runs": 0, "jobs": 0, "registered": 0})
            entry["runs"] += 1
            entry["jobs"] += len(run.jobs)
            entry["registered"] += run.acquisition is not None
        return {
            "claims": len(self.claims),
            "acquisitions": len(self.acquisitions),
            "unclaimed_acquisitions": sorted(
                acquisition
                for acquisition in self.acquisitions
                if not any(acquisition in claim["acquisitions"] for claim in self.claims.values())
            ),
            "providers": providers,
            "unregistered_runs": sorted(
                run.path for run in self.runs.values() if run.acquisition is None and run.provider != "kaggle"
            ),
            "acquisitions_without_run": sorted(self.unheld),
            "kaggle_uncollected": sorted(
                run.path for run in self.runs.values() if run.provider == "kaggle" and "UNCOLLECTED" in run.statuses
            ),
        }

    def job(self, job_id: str, provider: str | None = None) -> list[dict[str, Any]]:
        return [
            self.runs[path].row()
            for path in self.job_runs.get(job_id, [])
            if provider is None or self.runs[path].provider == provider
        ]

    def claim(self, claim_id: str) -> dict[str, Any]:
        claim = self.claims.get(claim_id)
        if claim is None:
            raise SystemExit(f"no claim {claim_id} in {research_state.REGISTRY.relative_to(ROOT)}")
        paths = {a: self.acquisitions[a]["run"] for a in claim["acquisitions"]}
        missing = [f"acquisition {a} names run {path}" for a, path in paths.items() if path not in self.runs]
        if missing:
            raise SystemExit(f"claim {claim_id} cites runs the tree does not hold: {'; '.join(missing)}")
        runs = [self.runs[path].row() for path in paths.values()]
        return {
            **claim,
            "id": claim_id,
            "status": claim["status"],
            "evidence_class": claim["evidence_class"],
            "statement": claim["statement"],
            "evidence": [entry["path"] for entry in claim["evidence"]],
            "evidence_bindings": claim["evidence"],
            "documents": claim["documents"],
            "gates": claim["gates"],
            "runs": runs,
            "depends_on": claim["depends_on"],
        }

    def path(self, target: str) -> dict[str, Any]:
        resolved = (Path.cwd() / target).resolve()
        if not resolved.is_relative_to(ROOT):
            raise SystemExit(f"{target} lies outside the repository")
        rel = resolved.relative_to(ROOT).as_posix()
        owners = [run.row() for path, run in self.runs.items() if rel == path or rel.startswith(path + "/")]
        citing = sorted(
            claim["id"]
            for claim in self.claims.values()
            if rel in {entry["path"].partition("#")[0] for entry in claim["evidence"]} or rel in claim["documents"]
        )
        return {"path": rel, "runs": owners, "claims_citing": citing}

    def ledger(self) -> dict[str, Any]:
        paths = (
            subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split("\0")
        )
        view = quantum_ledger.build(
            ROOT,
            list(self.claims.values()),
            list(self.acquisitions.values()),
            [run.row() for run in self.runs.values()],
            self.gates,
            [path for path in paths if path],
        )
        findings_path = ROOT / "docs/evidence/a5-exceptional-fibers/ledger.tsv"
        with findings_path.open(encoding="utf-8", newline="") as stream:
            findings = list(csv.DictReader(stream, delimiter="\t"))
        view["algebra_findings"] = {
            "path": findings_path.relative_to(ROOT).as_posix(),
            "sha256": research_state.digest(findings_path),
            "rows": findings,
            "boundary": (
                "A5 statuses and field restrictions retain the algebra ledger's meanings. "
                "A shared evidence path does not establish a physical claim or an equivalence of claims."
            ),
        }
        view["summary"]["algebra_findings"] = len(findings)
        candidates = ordered_map(
            _execution_candidate,
            [(ROOT, reference) for reference in view["gaps"]["execution_records_outside_indexed_runs"]],
        )
        for candidate in candidates:
            matched = [job for job in self.account_only_jobs if job["job_id"] in candidate.get("job_ids", [])]
            candidate["account_jobs"] = matched
            if (
                matched
                and len(matched) == len(candidate.get("job_ids", []))
                and all(job["provenance"] == "unexecuted_cancellation" for job in matched)
            ):
                candidate["classification"] = "audited unexecuted cancellation"
        view["execution_candidates"] = candidates
        view["account_only_jobs"] = self.account_only_jobs
        view["summary"]["execution_classifications"] = {
            category: sum(row["classification"] == category for row in candidates)
            for category in sorted({row["classification"] for row in candidates})
        }
        return view

    def observation(self, reference: str, pointer: str) -> dict[str, Any]:
        if "#" in reference:
            raise ValueError("observation takes a file path and a separate JSON Pointer")
        reference = quantum_ledger.local_file(ROOT, reference).relative_to(ROOT.resolve()).as_posix()
        observed = quantum_ledger.inspect(ROOT, reference, pointer)
        citing = [
            claim
            for claim in self.claims.values()
            if any(entry["path"].partition("#")[0] == reference for entry in claim["evidence"])
        ]
        observed["claims_citing_file"] = [self.claim(claim["id"]) for claim in citing]
        observed["runs_holding_file"] = [
            run.row() for run in self.runs.values() if reference.startswith(run.path + "/")
        ]
        observed["citation_boundary"] = (
            "A file citation locates potentially relevant claims; it does not establish that a claim uses this field."
        )
        return observed

    def write_sqlite(self, out: Path) -> dict[str, int]:
        """Write every relation to a new SQLite file at OUT; OUT must lie outside the repository."""
        out = out.resolve()
        if out.is_relative_to(ROOT):
            raise SystemExit(f"{out} lies inside the repository; the database is a cache kept outside it")
        if out.exists():
            raise SystemExit(f"{out} exists; choose a new path")
        out.parent.mkdir(parents=True, exist_ok=True)
        tables: dict[str, tuple[str, Iterable[tuple[Any, ...]]]] = {
            "runs": (
                "path TEXT PRIMARY KEY, provider TEXT, acquisition TEXT, created_at TEXT, backends TEXT, statuses TEXT",
                (
                    (r.path, r.provider, r.acquisition, r.created_at, json.dumps(r.backends), json.dumps(r.statuses))
                    for r in self.runs.values()
                ),
            ),
            "jobs": (
                "job TEXT, run TEXT, provider TEXT",
                ((job, run.path, run.provider) for run in self.runs.values() for job in run.jobs),
            ),
            "acquisitions": (
                "id TEXT PRIMARY KEY, provider TEXT, run TEXT, family TEXT, question TEXT",
                ((a["id"], a["provider"], a["run"], a["family"], a["question"]) for a in self.acquisitions.values()),
            ),
            "claims": (
                "id TEXT PRIMARY KEY, status TEXT, evidence_class TEXT, domain TEXT, statement TEXT",
                (
                    (c["id"], c["status"], c["evidence_class"], c["domain"], c["statement"])
                    for c in self.claims.values()
                ),
            ),
            "claim_acquisitions": (
                "claim TEXT, acquisition TEXT",
                ((c["id"], a) for c in self.claims.values() for a in c["acquisitions"]),
            ),
            "claim_evidence": (
                "claim TEXT, path TEXT, sha256 TEXT",
                ((c["id"], e["path"], e["sha256"]) for c in self.claims.values() for e in c["evidence"]),
            ),
            "claim_gates": (
                "claim TEXT, gate TEXT, role TEXT",
                ((c["id"], gate, role) for c in self.claims.values() for gate, role in c["gates"].items()),
            ),
            "claim_dependencies": (
                "claim TEXT, depends_on TEXT",
                ((c["id"], d) for c in self.claims.values() for d in c["depends_on"]),
            ),
            "claim_qualifications": (
                "claim TEXT PRIMARY KEY, boundary TEXT, assumptions TEXT, supersedes TEXT, "
                "superseded_by TEXT, related_claims TEXT, numerical_replay TEXT",
                (
                    (
                        claim["id"],
                        claim["boundary"],
                        json.dumps(claim["assumptions"]),
                        json.dumps(claim["supersedes"]),
                        claim.get("superseded_by"),
                        json.dumps(claim["related_claims"]),
                        "not-run-by-ledger",
                    )
                    for claim in self.claims.values()
                ),
            ),
        }
        counts = {}
        with closing(sqlite3.connect(out)) as db, db:
            for name, (columns, rows) in tables.items():
                materialized = list(rows)
                db.execute(f"CREATE TABLE {name} ({columns})")
                if materialized:
                    marks = ",".join("?" * len(materialized[0]))
                    db.executemany(f"INSERT INTO {name} VALUES ({marks})", materialized)
                counts[name] = len(materialized)
        return counts


def _print(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=1, sort_keys=True))
        return
    if isinstance(value, list):
        for item in value:
            _print(item, False)
            print()
        return
    for key, item in value.items():
        if isinstance(item, list) and item and isinstance(item[0], dict):
            print(f"{key}:")
            for entry in item:
                print("  " + json.dumps(entry, sort_keys=True))
        else:
            print(f"{key}: {json.dumps(item, sort_keys=True) if not isinstance(item, str) else item}")


def default_sqlite() -> Path:
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return cache / "gororoba-quantum" / "results-index.sqlite"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")
    runs = sub.add_parser("runs")
    runs.add_argument("--provider", choices=[*research_state.PROVIDERS, "kaggle"])
    job = sub.add_parser("job")
    job.add_argument("job_id")
    job.add_argument("--provider", choices=[*research_state.PROVIDERS, "kaggle"])
    sub.add_parser("claim").add_argument("claim_id")
    sub.add_parser("path").add_argument("target")
    sub.add_parser("sqlite").add_argument("out", nargs="?", type=Path, default=None)
    ledger = sub.add_parser("ledger")
    projection = ledger.add_mutually_exclusive_group()
    projection.add_argument("--summary", action="store_true")
    projection.add_argument("--markdown", action="store_true")
    observation = sub.add_parser("observation")
    observation.add_argument("reference", help="repository-relative JSON file")
    observation.add_argument("--pointer", default="", help="RFC 6901 pointer, e.g. /conditions/0")
    args = parser.parse_args(argv)
    index = Index()
    if args.command == "summary":
        _print(index.summary(), args.json)
    elif args.command == "runs":
        rows = [r.row() for r in index.runs.values() if args.provider in (None, r.provider)]
        _print(sorted(rows, key=lambda row: row["path"]), args.json)
    elif args.command == "job":
        found = index.job(args.job_id, args.provider)
        if not found:
            raise SystemExit(f"no retained run holds job {args.job_id}")
        _print(found, args.json)
    elif args.command == "claim":
        _print(index.claim(args.claim_id), args.json)
    elif args.command == "path":
        _print(index.path(args.target), args.json)
    elif args.command == "ledger":
        view = index.ledger()
        if args.markdown:
            print(quantum_ledger.markdown(view), end="")
        else:
            _print(view["summary"] if args.summary else view, args.json)
    elif args.command == "observation":
        _print(index.observation(args.reference, args.pointer), args.json)
    else:
        out = args.out or default_sqlite()
        _print({"database": str(out), "rows": index.write_sqlite(out)}, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
