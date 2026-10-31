"""Validate the research-state registry and render the state sections it owns.

docs/state/research_state.json is the authoritative list of research claims
and QPU acquisitions. Each claim names one evidence class, a status, its
retained evidence (sha256-pinned data files and prose documents), its CI
gates with the role each plays (replay, freshness, admission, regression or bytes), the
acquisitions it rests on and the claims it depends on, supersedes or is
superseded by. The evidence class fixes what a claim may assert: only a
replay gate re-derives a result, a circuit-conformance check verifies ideal
semantics only, and an exploratory reanalysis never reaches the established
status.

Acquisitions are derived. Each names its provider, and that provider's
adapter in PROVIDERS supplies every retained run, job, backend, status and
charge in the provider's own unit; the registry adds only a family label and
the question the run asked. For each provider the registry's run set and the
adapter's run set agree exactly.

- ibm: the retained-run audit (results/live/qpu-job-retention-audit.json,
  bound to the service inventory by its inventory_sha256) lists every job and
  its settled QPU seconds.
- quantum_inspire: every results/quantum_inspire/runs/*/submission.json is a
  run. Its circuits match their cases.json sha256, results.json records the
  submitted jobs of its batch job, raw/ holds one shot list per completed job
  whose length and histogram equal the recorded result, every charged
  transaction belongs to the run, and the account ledger
  (docs/evidence/quantum_inspire/usage.json) lists every retained job with the
  same backend type, batch job, status, shots done and charge, and exactly the
  transaction rows of those jobs (id, timestamp, domain, change, job and
  backend type, counted with multiplicity). The ledger is account-wide, so a
  job it lists that no run directory of this tree retains belongs to another
  branch's run and is declared by id in the ledger's `unretained` list; a
  ledger job outside both sets, a declared job absent from the ledger and a
  transaction charging a job outside the ledger fail. A job both retained and
  declared passes (the run landed after the snapshot). A failed job is part of
  its run's acquisition.

- quandela: every results/quandela/runs/*/ directory is one job. Its
  circuit matches its cases.json sha256, submission.json records the
  approval, the platform and the cases digest, job-body.json is the body it
  sent, results.json names the same job with a terminal status and no token
  field, and a completed job's raw/result.json keeps the bytes whose counts
  results.json records (qd_platform.run_facts). The charge is shots times
  the platform's price per shot at submission.
- iqm: every results/iqm/runs/*/ directory is one circuit job. Its circuits
  match their cases.json sha256, submission.json records the approval, the
  QC, the cases digest and the price per second, results.json names the same
  job with a terminal status, every raw file keeps its recorded sha256, and a
  completed job returns the case's shots for every circuit
  (iqm_jobs.run_facts). The charge is billed seconds times that price.

A further provider adds one adapter class and one PROVIDERS entry.

The script renders docs/state/RESEARCH_STATE.md in full and the marked
sections of README.md and docs/RESEARCH_ROADMAP.md. --check fails on any
rule violation or rendered difference; --write rewrites the rendered text;
--self-test applies mutations to the registry that each rule must reject;
--add-acquisition ID PROVIDER RUN FAMILY QUESTION appends one acquisition as
text, which scripts/retain_run.sh calls when it retains an IBM run; it holds
every rule except that a claim cite the new acquisition, which --check and
--write require once the operator writes that claim. The flag repeats, and the
entries append and validate together: one inventory observation that retains
two runs of an instance makes the audit list both, so neither registers alone.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
from collections import Counter
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import iqm_jobs  # noqa: E402
import plan_records  # noqa: E402
import qd_platform  # noqa: E402
import qi_platform  # noqa: E402

import parallel  # noqa: E402
import qi_records  # noqa: E402

REGISTRY = ROOT / "docs/state/research_state.json"
STATE_DOCUMENT = ROOT / "docs/state/RESEARCH_STATE.md"
RETENTION_AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
SERVICE_INVENTORY = ROOT / "results/live/qpu-job-inventory.json"
QI_RUNS = ROOT / "results/quantum_inspire/runs"
QI_LEDGER = ROOT / "docs/evidence/quantum_inspire/usage.json"
QI_CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
QD_RUNS = ROOT / "results/quandela/runs"
QD_CATALOGUE = ROOT / "docs/evidence/quandela/catalogue.json"
IQM_RUNS = ROOT / "results/iqm/runs"
IQM_CREDIT = ROOT / "docs/evidence/iqm/account/credit.json"
GATES = ROOT / "ci/gates.json"
SCHEMA = "research-state-v2"
BEGIN = "<!-- research-state:begin (generated by scripts/research_state.py; edit docs/state/research_state.json) -->"
END = "<!-- research-state:end -->"

CLASSES: dict[str, dict[str, Any]] = {
    "mathematical claim": {
        "establishes": "a statement under its assumptions and named proof origin, or an explicit open question",
        "excludes": "machine checking; a separate machine-checked claim carries that",
        "statuses": {"established", "open", "superseded"},
    },
    "exact finite certificate": {
        "establishes": "exact facts about the enumerated or witnessed objects, re-derived by its gates",
        "excludes": "any object outside the certificate",
        "statuses": {"established", "superseded"},
    },
    "machine-checked proof": {
        "establishes": "the statement as kernel-checked by Rocq from the retained source",
        "excludes": "a fresh kernel check: the receipt records an earlier compiler run and CI verifies its bytes",
        "statuses": {"established", "superseded"},
    },
    "numerical or stochastic simulation": {
        "establishes": "model predictions at the stated seeds, precision and noise model",
        "excludes": "hardware behavior",
        "statuses": {"established", "superseded"},
    },
    "circuit-conformance check": {
        "establishes": "ideal circuit semantics: statevector, operator or routed-schedule equality",
        "excludes": "noise suppression or any hardware performance",
        "statuses": {"established", "superseded"},
    },
    "preregistered hardware inference": {
        "establishes": "the registered endpoint decisions on the named acquisitions",
        "excludes": "mechanisms the design does not isolate, and other devices or calibrations",
        "statuses": {"established", "superseded"},
    },
    "preregistered emulator control": {
        "establishes": "the registered exact outcomes of a noiseless emulator twin on the named acquisitions",
        "excludes": "device noise and any hardware behavior; a hardware inference carries those",
        "statuses": {"established", "superseded"},
    },
    "exploratory reanalysis": {
        "establishes": "descriptive or post-selected summaries of retained data",
        "excludes": "confirmation; it motivates a prospective test",
        "statuses": {"exploratory", "superseded"},
    },
    "proposed experiment": {
        "establishes": "a design with its question, controls and falsifier",
        "excludes": "any result; a QPU run needs its own approved case",
        "statuses": {"proposed", "superseded"},
    },
    "withdrawn claim": {
        "establishes": "the record of a statement the evidence does not support",
        "excludes": "the statement itself; its replacement or reason is named",
        "statuses": {"withdrawn"},
    },
}
STATUS_ORDER = ("established", "exploratory", "open", "proposed", "superseded", "withdrawn")
DOMAINS = ("algebra", "geometry", "formal", "implementation", "hardware")
NEEDS_REPRODUCING_GATE = {
    "exact finite certificate",
    "numerical or stochastic simulation",
    "circuit-conformance check",
}
NEEDS_ACQUISITION = {
    "preregistered hardware inference",
    "preregistered emulator control",
    "exploratory reanalysis",
}
# What a gate does for a claim: replay re-derives the claimed result, bytes
# verifies retained files, freshness regenerates a source from its producer,
# admission exercises the replay procedure's failure paths, and regression
# checks active code on bounded inputs without reproducing a retained result.
GATE_ROLES = ("replay", "freshness", "admission", "regression", "bytes")
CHECK_PREFIXES = ("sha256sum -c", "shellcheck ", "ruff ", "mypy ", "MYPYPATH=")
# ci/pinned_tool.py runs ruff or mypy at the CI pin, so a gate it launches is
# the same lint or type check as the bare tool.
PINNED_TOOL = re.compile(r'^"\$PYTHON" (?:\.\./)*ci/pinned_tool\.py ')
CLAIM_KEYS = {
    "id",
    "statement",
    "domain",
    "evidence_class",
    "status",
    "boundary",
    "evidence",
    "documents",
    "gates",
    "acquisitions",
    "assumptions",
    "depends_on",
    "supersedes",
    "superseded_by",
    "kernel_receipt",
    "withdrawn_text",
    "proof_origin",
    "related_claims",
}
ACQUISITION_KEYS = {"id", "provider", "run", "family", "question"}


def _validate_proof_origin(claim: dict[str, Any]) -> None:
    owner = f"claim {claim['id']}"
    if claim["evidence_class"] != "mathematical claim":
        require("proof_origin" not in claim, f"{owner}: proof_origin belongs only to mathematical claims")
        return
    origin = claim.get("proof_origin")
    require(
        isinstance(origin, str) and origin in {"external-source", "repository-written", "unproved-open"},
        f"{owner}: proof_origin must identify an external source, repository proof or open question",
    )
    if claim["status"] == "established":
        require(origin != "unproved-open", f"{owner}: established proof_origin requires a written proof")
    elif claim["status"] == "open":
        require(origin == "unproved-open", f"{owner}: open proof_origin must be unproved-open")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class IbmRuns:
    """IBM Quantum runs: the retained-run audit bound to the service inventory."""

    name = "ibm"
    title = "IBM Quantum"
    charge_unit = "s"
    source = "the retained-run audit"
    absent = "holds no audited job"

    def __init__(self) -> None:
        # The default instance's inventory pairs with the retention audit; each
        # further instance (qpu-job-inventory.<instance_crn_hash>.json) pairs
        # with qpu-job-retention-audit.<instance_crn_hash>.json.
        inventories = [SERVICE_INVENTORY, *sorted(SERVICE_INVENTORY.parent.glob("qpu-job-inventory.*.json"))]
        self.jobs: list[dict[str, Any]] = []
        self.services: list[dict[str, Any]] = []
        self.job_groups: list[list[dict[str, Any]]] = []
        for inventory in inventories:
            audit_file = inventory.with_name(inventory.name.replace("qpu-job-inventory", "qpu-job-retention-audit"))
            audit = load_json(audit_file)
            service = load_json(inventory)
            require(
                audit.get("inventory_sha256") == digest(inventory),
                "the retention audit binds a different service inventory",
            )
            # A run collected after the inventory's observation sits outside the audit's jobs, so the registry
            # cannot match it to an acquisition; the change that retains it observes the instance again.
            require(
                not audit.get("awaiting_observation"),
                f"{audit_file.name}: {', '.join(audit['awaiting_observation'])} await observation; "
                "retain runs with scripts/retain_run.sh, which observes the instance's inventory",
            )
            self.jobs += audit["jobs"]
            self.services.append(service)
            self.job_groups.append(audit["jobs"])
        self.service = self.services[0]
        self.status = {job["job_id"]: job["status"] for service in self.services for job in service["jobs"]}

    def runs(self) -> dict[str, dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for job in self.jobs:
            run = job["run"]
            if run is None:
                require(
                    job.get("provenance") == "unexecuted_cancellation"
                    and job.get("status") == "CANCELLED"
                    and job.get("final_qpu_charge_seconds") == 0,
                    f"audited job {job['job_id']} lacks a retained run",
                )
                continue
            require(isinstance(run, str) and bool(run), f"audited job {job['job_id']} has an invalid run")
            grouped.setdefault(run, []).append(job)
        facts = {}
        for run, jobs in grouped.items():
            jobs = sorted(jobs, key=lambda job: job["created_at"])
            for job in jobs:
                require(job["job_id"] in self.status, f"audited job {job['job_id']} is absent from the inventory")
            facts[run] = {
                "created_at": jobs[0]["created_at"],
                "backends": sorted({job["backend"] for job in jobs}),
                "jobs": len(jobs),
                "circuits": sum(job["pub_count"] for job in jobs),
                "statuses": Counter(self.status[job["job_id"]] for job in jobs),
                "charge": sum(job["final_qpu_charge_seconds"] for job in jobs),
                "detail": "",
            }
        return facts

    def account_line(self) -> str:
        lines = []
        for service, jobs in zip(self.services, self.job_groups, strict=True):
            usage = service["account_usage"]
            charge = sum(job["final_qpu_charge_seconds"] for job in jobs)
            lines.append(
                f"The IBM service inventory observed at {service['observed_at']} holds {len(jobs)} physical "
                f"jobs with {charge} settled seconds; the account then reported {usage['usage_consumed_seconds']} of "
                f"{usage['usage_limit_seconds']} s consumed in the rolling window ending "
                f"{usage['usage_period']['end_time']}. That is an observation, not a current balance or an "
                "authorization."
            )
        return "\n\n".join(lines)


TRANSACTION_FIELDS = ("id", "timestamp", "domain", "change", "job")
# Ids of the +5 and -5 rows the self-test adds to a retained run and to the ledger.
SYNTHETIC_ROW_ID = 10**9 + 1
SYNTHETIC_OFFSET_ID = SYNTHETIC_ROW_ID + 1
SYNTHETIC_JOB_ID = 10**9 + 7


def _ledger_backend(owner: str, row: dict[str, Any]) -> Any:
    require("backend_type_id" in row, f"{owner}: transaction row {row.get('id')} lacks backend_type_id")
    return row["backend_type_id"]


def _transaction_key(owner: str, row: dict[str, Any], backend_type_id: Any) -> tuple[Any, ...]:
    """The ledger fields of one transaction row, compared field by field between a run and the ledger."""
    for field in TRANSACTION_FIELDS:
        require(field in row, f"{owner}: transaction row {row.get('id')} lacks {field}")
    return (*(row[field] for field in TRANSACTION_FIELDS), backend_type_id)


class QuantumInspireRuns:
    """Quantum Inspire runs: the retained run directories bound to the account ledger.

    Loading reads the files; runs() applies every rule to the loaded copy, so
    the self-test reaches each rule by mutating that copy.
    """

    name = "quantum_inspire"
    title = "Quantum Inspire"
    charge_unit = "ledger change"
    source = "the Quantum Inspire run directories"
    absent = "is not a retained Quantum Inspire run"

    def __init__(self) -> None:
        self.ledger: dict[str, Any] = load_json(QI_LEDGER)
        # Every run directory is a retained run, so one without a receipt fails
        # validation instead of leaving the run set.
        self.records: dict[str, dict[str, Any]] = {
            directory.relative_to(ROOT).as_posix(): qi_records.load_run(directory)
            for directory in qi_platform.run_directories(QI_RUNS)
        }
        self.acquisitions: dict[str, qi_records.Acquisition] = {}

    def _run(
        self, run: str, record: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[int, tuple[Any, ...]], Counter[tuple[Any, ...]]]:
        """The shared record rules of qi_records, then the ledger rows: every charge names a job of the run."""
        owner = f"Quantum Inspire run {run}"
        acquisition = qi_records.validate_run(record, owner)
        job_ids = {job.job_id for job in acquisition.jobs}
        charges: Counter[int] = Counter()
        rows: Counter[tuple[Any, ...]] = Counter()
        for transaction in record["results"]["transactions"]:
            require(transaction["job"] in job_ids, f"{owner}: transaction {transaction['id']} charges another job")
            charges[transaction["job"]] += transaction["change"]
            rows[_transaction_key(owner, transaction, acquisition.backend_type_id)] += 1
        jobs: dict[int, tuple[Any, ...]] = {
            job.job_id: (
                acquisition.backend_type_id,
                acquisition.batch_job,
                job.status,
                job.shots_done,
                charges[job.job_id],
            )
            for job in acquisition.jobs
        }
        shots_done = sum(job.shots_done for job in acquisition.jobs)
        requested = len(jobs) * acquisition.shots
        facts = {
            "created_at": acquisition.created_at,
            "backends": [acquisition.backend],
            "jobs": len(jobs),
            "circuits": len(jobs),
            "statuses": acquisition.statuses,
            "charge": sum(charges.values()),
            "detail": f"batch job {acquisition.batch_job}, {shots_done} of {requested} shots done",
        }
        self.acquisitions[run] = acquisition
        return facts, jobs, rows

    def runs(self) -> dict[str, dict[str, Any]]:
        require(self.ledger.get("schema") in qi_platform.USAGE_SCHEMAS, "the Quantum Inspire ledger schema differs")
        facts = {}
        retained: dict[int, tuple[Any, ...]] = {}
        run_rows: Counter[tuple[Any, ...]] = Counter()
        for run, record in self.records.items():
            facts[run], jobs, rows = self._run(run, record)
            run_rows.update(rows)
            require(
                not (set(retained) & set(jobs)),
                f"Quantum Inspire job ids repeat across retained runs: {sorted(set(retained) & set(jobs))}",
            )
            retained.update(jobs)
        ledger_ids = [job["job"] for job in self.ledger["jobs"]]
        require(len(set(ledger_ids)) == len(ledger_ids), "the Quantum Inspire ledger job ids repeat")
        declared = self._declared()
        ledger = {
            job["job"]: (job["backend_type_id"], job["batch_job"], job["status"], job["shots_done"], job["charged"])
            for job in self.ledger["jobs"]
        }
        require(
            not (set(retained) - set(ledger)),
            f"retained Quantum Inspire jobs are missing from the ledger: {sorted(set(retained) - set(ledger))}",
        )
        differing = sorted(job for job in retained if ledger[job] != retained[job])
        require(not differing, f"the ledger rows of retained Quantum Inspire jobs differ from the runs: {differing}")
        orphans = sorted(set(ledger) - set(retained) - set(declared))
        require(
            not orphans,
            f"the Quantum Inspire ledger lists jobs that no run retains and its unretained list omits: {orphans}",
        )
        absent = sorted(set(declared) - set(ledger))
        require(not absent, f"the Quantum Inspire ledger declares unretained jobs that it does not list: {absent}")
        for owner, ids in (
            ("the run results", [key[0] for key in run_rows.elements()]),
            ("the ledger", [row["id"] for row in self.ledger["transactions"]]),
        ):
            repeated = sorted({i for i, count in Counter(ids).items() if count > 1}, key=repr)
            require(
                not repeated, f"Quantum Inspire transaction id {repeated[0] if repeated else None} repeats in {owner}"
            )
        dangling = sorted(
            {row["job"] for row in self.ledger["transactions"] if row["job"] is not None and row["job"] not in ledger}
        )
        require(dangling == [], f"the Quantum Inspire ledger transactions charge jobs outside the ledger: {dangling}")
        ledger_rows = Counter(
            _transaction_key("the Quantum Inspire ledger", row, _ledger_backend("the Quantum Inspire ledger", row))
            for row in self.ledger["transactions"]
            if row["job"] in retained
        )
        require(
            ledger_rows == run_rows,
            "the Quantum Inspire ledger transaction rows of the retained jobs differ from the run results "
            f"(runs only {sorted((run_rows - ledger_rows).elements(), key=repr)}, "
            f"ledger only {sorted((ledger_rows - run_rows).elements(), key=repr)})",
        )
        totals = self.ledger["totals"]
        require(
            totals["shots_done"] == sum(job["shots_done"] for job in self.ledger["jobs"]),
            "the Quantum Inspire ledger aggregate shots_done differs from the sum over its jobs",
        )
        require(
            totals["change"] == sum(row["change"] for row in self.ledger["transactions"]),
            "the Quantum Inspire ledger aggregate change differs from the sum over its transaction rows",
        )
        charged: Counter[int] = Counter()
        for row in self.ledger["transactions"]:
            if row["job"] is not None:
                charged[row["job"]] += row["change"]
        misattributed = sorted(job["job"] for job in self.ledger["jobs"] if job["charged"] != charged[job["job"]])
        require(
            not misattributed,
            f"the Quantum Inspire ledger job charges differ from their transaction rows: {misattributed}",
        )
        return facts

    def _declared(self) -> list[int]:
        """The ledger's declared unretained job ids; a qi-usage-v1 ledger declares none."""
        if self.ledger["schema"] == "qi-usage-v1":
            require("unretained" not in self.ledger, "a qi-usage-v1 ledger carries no unretained list")
            return []
        declared: list[int] = self.ledger["unretained"]
        require(
            isinstance(declared, list) and len(set(declared)) == len(declared),
            "the Quantum Inspire ledger unretained job ids repeat",
        )
        return declared

    def account_line(self) -> str:
        totals = self.ledger["totals"]
        # A declared job whose run landed after the snapshot is retained, not another branch's.
        retained = {job for run, record in self.records.items() for job in self._run(run, record)[1]}
        declared = set(self._declared()) - retained
        names = {row["id"]: row["identifier"] for row in load_json(QI_CATALOGUE)["backend_types"]}
        backends = Counter(
            names.get(job["backend_type_id"], job["backend_type_id"])
            for job in self.ledger["jobs"]
            if job["job"] in declared
        )
        if declared:
            listed = ", ".join(f"{count} on {key}" for key, count in sorted(backends.items(), key=repr))
            membership = (
                f"; {len(declared)} of them are declared unretained, belonging to run directories of other branches "
                f"({listed}), and every other listed job belongs to a retained run directory."
            )
        else:
            membership = ", and every listed job belongs to a retained run directory."
        return (
            f"The Quantum Inspire ledger retrieved at {self.ledger['retrieved_utc']} lists {len(self.ledger['jobs'])} "
            f"jobs with {totals['shots_done']} shots done and a total ledger change of {totals['change']}"
            f"{membership} That is an observation, not a quota or an authorization."
        )


class QuandelaRuns:
    """Quandela Cloud runs: one job per retained run directory, checked by qd_platform.run_facts.

    The token usage report carries no per-job row yet (its usage list is
    empty at every retained snapshot), so runs are bound to their own receipts
    and raw results; the report's total stays an account observation.
    """

    name = "quandela"
    title = "Quandela Cloud"
    charge_unit = "credits"
    source = "the Quandela run directories"
    absent = "is not a retained Quandela run"

    def __init__(self) -> None:
        self.directories = qd_platform.run_directories(QD_RUNS)
        self.catalogue: dict[str, Any] = load_json(QD_CATALOGUE)

    def runs(self) -> dict[str, dict[str, Any]]:
        facts = {}
        for directory in self.directories:
            try:
                run = qd_platform.run_facts(directory)
            except (qd_platform.PlatformError, OSError, KeyError) as error:
                raise ValueError(str(error)) from None
            facts[directory.relative_to(ROOT).as_posix()] = {**run, "statuses": Counter(run["statuses"])}
        return facts

    def account_line(self) -> str:
        total = sum(row.get("total_jobs", 0) for row in self.catalogue["account"]["token_usage"])
        return (
            f"The Quandela token usage report retrieved at {self.catalogue['retrieved_utc']} counts {total} jobs, "
            f"and {len(self.directories)} Quandela run directories are retained. That is an observation, not a "
            "credit balance or an authorization."
        )


class IqmRuns:
    """IQM Resonance runs: one circuit job per retained run directory, checked by iqm_jobs.run_facts.

    The charge is the job's billed seconds times the price per second its submission recorded; the
    account credit is an observation of the retained snapshot.
    """

    name = "iqm"
    title = "IQM Resonance"
    charge_unit = "credits"
    source = "the IQM run directories"
    absent = "is not a retained IQM run"

    def __init__(self) -> None:
        self.directories = iqm_jobs.run_directories(IQM_RUNS)
        self.credit: dict[str, Any] = load_json(IQM_CREDIT)

    def runs(self) -> dict[str, dict[str, Any]]:
        facts = {}
        # One IQM job is one acquisition: a copy of a run directory would count its job and charge twice.
        owners: dict[str, str] = {}
        for directory in self.directories:
            try:
                run = iqm_jobs.run_facts(directory)
                job = json.loads((directory / "submission.json").read_text(encoding="utf-8"))["job_id"]
            except (iqm_jobs.PlatformError, OSError, KeyError, ValueError) as error:
                raise ValueError(str(error)) from None
            name = directory.relative_to(ROOT).as_posix()
            require(job not in owners, f"IQM job {job} is retained by both {owners.get(job)} and {name}")
            owners[job] = name
            facts[name] = {**run, "statuses": Counter(run["statuses"])}
        return facts

    def account_line(self) -> str:
        credit = self.credit["credit"]
        return (
            f"The retained IQM snapshot records {credit['currentBalance']} credits expiring {credit['expiresAt']}, "
            f"and {len(self.directories)} IQM run directories are retained. That is an observation, not an "
            "authorization."
        )


class Provider(Protocol):
    """One acquisition source: its run set, per-run facts and account observation."""

    name: str
    title: str
    charge_unit: str
    source: str
    absent: str

    def runs(self) -> dict[str, dict[str, Any]]: ...

    def account_line(self) -> str: ...


PROVIDERS: dict[str, Callable[[], Provider]] = {
    "ibm": IbmRuns,
    "quantum_inspire": QuantumInspireRuns,
    "quandela": QuandelaRuns,
    "iqm": IqmRuns,
}


class Context:
    """Repository facts the registry is validated against."""

    def __init__(self) -> None:
        self.providers: dict[str, Provider] = {name: adapter() for name, adapter in PROVIDERS.items()}
        gates = load_json(GATES)["gates"]
        self.gates: dict[str, str] = {gate["name"]: gate["cmd"] for gate in gates}
        self.digest: Callable[[Path], str] = digest


def _strings(value: Any, field: str, owner: str) -> list[str]:
    require(
        isinstance(value, list) and all(isinstance(item, str) and item for item in value),
        f"{owner}: {field} must be a list of nonempty strings",
    )
    require(len(set(value)) == len(value), f"{owner}: {field} repeats an entry")
    return list(value)


def _static_check(command: str) -> bool:
    return PINNED_TOOL.sub("", command.strip(), count=1).startswith(CHECK_PREFIXES)


def validate(registry: dict[str, Any], context: Context, uncited: frozenset[str] = frozenset()) -> None:
    """Every registry rule. UNCITED names acquisitions exempt from claim coverage: add_acquisitions saves a newly
    retained run's acquisition before the operator writes the claim that cites it, and --check and --write, which
    pass no exemption, keep every acquisition cited."""
    require(registry.get("schema") == SCHEMA, f"registry schema must be {SCHEMA}")
    require(set(registry) == {"schema", "acquisitions", "claims"}, "registry keys differ from the schema")

    acquisitions = registry["acquisitions"]
    acquisition_ids = [entry["id"] for entry in acquisitions]
    require(len(set(acquisition_ids)) == len(acquisition_ids), "acquisition ids repeat")
    for entry in acquisitions:
        require(set(entry) == ACQUISITION_KEYS, f"acquisition {entry.get('id')}: keys differ from the schema")
        require(
            entry["provider"] in context.providers,
            f"acquisition {entry['id']}: unknown provider {entry['provider']!r}; known {sorted(context.providers)}",
        )
    for name, provider in context.providers.items():
        runs = provider.runs()
        members = [entry for entry in acquisitions if entry["provider"] == name]
        for entry in members:
            require(entry["run"] in runs, f"acquisition {entry['id']}: run {entry['run']} {provider.absent}")
        require(
            {entry["run"] for entry in members} == set(runs),
            f"acquisition run set differs from {provider.source}",
        )
    require(len({entry["run"] for entry in acquisitions}) == len(acquisitions), "two acquisitions name one run")

    claims = registry["claims"]
    by_id: dict[str, dict[str, Any]] = {}
    for claim in claims:
        owner = f"claim {claim.get('id')}"
        require(set(claim) <= CLAIM_KEYS, f"{owner}: unknown keys {sorted(set(claim) - CLAIM_KEYS)}")
        for field in ("id", "statement", "domain", "evidence_class", "status", "boundary"):
            require(isinstance(claim.get(field), str) and claim[field], f"{owner}: {field} is required")
        require(claim["id"] not in by_id, f"{owner}: id repeats")
        by_id[claim["id"]] = claim
        require(claim["domain"] in DOMAINS, f"{owner}: domain must be one of {DOMAINS}")
        kind = claim["evidence_class"]
        require(kind in CLASSES, f"{owner}: unknown evidence class {kind!r}")
        require(
            claim["status"] in CLASSES[kind]["statuses"],
            f"{owner}: status {claim['status']!r} is outside {sorted(CLASSES[kind]['statuses'])} for {kind}",
        )
        for field in ("documents", "acquisitions", "assumptions", "depends_on", "supersedes", "related_claims"):
            claim.setdefault(field, [])
            _strings(claim[field], field, owner)
        evidence = claim.setdefault("evidence", [])
        require(isinstance(evidence, list), f"{owner}: evidence must be a list")
        for item in evidence:
            require(
                isinstance(item, dict) and set(item) == {"path", "sha256"},
                f"{owner}: evidence entries carry path and sha256",
            )
            path = ROOT / evidence_file(item["path"])
            require(path.is_file(), f"{owner}: evidence {item['path']} is missing")
            # A FILE.json#COLLECTION/FIELD=VALUE entry binds the digest of the one record it selects, so a record
            # appended to a shared ledger leaves the claim's evidence unchanged.
            found = plan_records.evidence_digest(ROOT, item["path"]) if "#" in item["path"] else context.digest(path)
            require(found == item["sha256"], f"{owner}: evidence {item['path']} digest differs")
        for document in claim["documents"]:
            require((ROOT / document).is_file(), f"{owner}: document {document} is missing")
        gates = claim.setdefault("gates", {})
        require(isinstance(gates, dict), f"{owner}: gates map each gate to its role")
        for gate, role in gates.items():
            require(gate in context.gates, f"{owner}: gate {gate} is not in ci/gates.json")
            require(role in GATE_ROLES, f"{owner}: gate {gate} role must be one of {GATE_ROLES}")
            command = context.gates[gate]
            if role == "bytes":
                require(command.strip().startswith("sha256sum -c"), f"{owner}: bytes gate {gate} is not a checksum")
            else:
                require(not _static_check(command), f"{owner}: {role} gate {gate} is a lint or byte check")
        for acquisition in claim["acquisitions"]:
            require(acquisition in acquisition_ids, f"{owner}: acquisition {acquisition} is not registered")

        if kind in NEEDS_REPRODUCING_GATE:
            require(
                "replay" in gates.values(),
                f"{owner}: a {kind} needs a replay gate; "
                "byte, freshness, admission and regression gates re-derive nothing",
            )
        _validate_proof_origin(claim)
        if kind == "mathematical claim":
            require(claim["assumptions"], f"{owner}: a theorem lists its assumptions")
            require(claim["documents"], f"{owner}: a theorem names the document carrying its proof")
        if kind == "machine-checked proof":
            receipt = claim.get("kernel_receipt")
            require(
                isinstance(receipt, str) and any(item["path"] == receipt for item in evidence),
                f"{owner}: kernel_receipt is required and pinned as evidence",
            )
            require(
                any(item["path"].endswith(".v") for item in evidence),
                f"{owner}: a machine-checked proof pins its Rocq source",
            )
        if kind in NEEDS_ACQUISITION:
            require(claim["acquisitions"], f"{owner}: a {kind} names its acquisitions")
            require(
                any(item["path"].startswith("results/") for item in evidence),
                f"{owner}: a {kind} pins the retained analysis it reads",
            )
        else:
            require(not claim["acquisitions"], f"{owner}: only hardware classes name acquisitions")
        if kind == "withdrawn claim":
            require(
                isinstance(claim.get("withdrawn_text"), str) and claim["withdrawn_text"],
                f"{owner}: a withdrawn claim names where its text appeared",
            )
        if claim["status"] in {"superseded", "withdrawn"}:
            require(isinstance(claim.get("superseded_by"), str), f"{owner}: {claim['status']} needs superseded_by")
        else:
            require(
                claim.get("superseded_by") is None, f"{owner}: only superseded or withdrawn claims carry superseded_by"
            )

    for claim in claims:
        owner = f"claim {claim['id']}"
        for target in claim["related_claims"]:
            require(target in by_id and target != claim["id"], f"{owner}: related_claims names invalid claim {target}")
        replacement = claim.get("superseded_by")
        if replacement is not None:
            require(replacement in by_id, f"{owner}: superseded_by {replacement} is not a claim")
            require(claim["id"] in by_id[replacement]["supersedes"], f"{owner}: {replacement} does not list it")
        for target in claim["supersedes"]:
            require(target in by_id, f"{owner}: supersedes unknown claim {target}")
            require(by_id[target].get("superseded_by") == claim["id"], f"{owner}: {target} names another successor")
        for target in claim["depends_on"]:
            require(target in by_id, f"{owner}: depends on unknown claim {target}")
            if claim["status"] == "established":
                require(
                    by_id[target]["status"] == "established",
                    f"{owner}: established claim depends on {target}, which is {by_id[target]['status']}",
                )

    state: dict[str, int] = {}

    def visit(node: str) -> None:
        if state.get(node) == 2:
            return
        require(state.get(node) != 1, f"claim dependency cycle through {node}")
        state[node] = 1
        for target in by_id[node]["depends_on"]:
            visit(target)
        state[node] = 2

    for node in by_id:
        visit(node)

    # An acquisition is retained the moment it exists; the claim that interprets it is a later change, so an
    # acquisition no claim cites is reported, never refused.
    cited = {acquisition for claim in claims for acquisition in claim["acquisitions"]}
    unclaimed = sorted(acquisition for acquisition in acquisition_ids if acquisition not in cited)
    if unclaimed:
        print(f"unclaimed acquisitions ({len(unclaimed)}): {', '.join(unclaimed)}", file=sys.stderr)


# Rendering


def evidence_file(reference: str) -> str:
    """The repository file an evidence entry names: its path, without a #COLLECTION/FIELD=VALUE record selector."""
    return reference.partition("#")[0]


def _evidence_links(claim: dict[str, Any], origin: Path) -> list[str]:
    """One link per evidence file, labeled with the count of records a claim binds in it."""
    files = Counter(evidence_file(item["path"]) for item in claim["evidence"])
    records = Counter(evidence_file(item["path"]) for item in claim["evidence"] if "#" in item["path"])
    return [
        _link(name, origin, Path(name).name + (f" ({records[name]} records)" if records[name] else ""))
        for name in files
    ]


def _link(target: str, origin: Path, label: str | None = None) -> str:
    relative = os.path.relpath(ROOT / target, origin.parent)
    return f"[{label or target}]({Path(relative).as_posix()})"


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _acquisition_rows(registry: dict[str, Any], context: Context) -> list[dict[str, Any]]:
    runs = {name: provider.runs() for name, provider in context.providers.items()}
    rows = []
    for entry in registry["acquisitions"]:
        provider = context.providers[entry["provider"]]
        rows.append({**entry, **runs[entry["provider"]][entry["run"]], "unit": provider.charge_unit})
    return sorted(rows, key=lambda row: (datetime.fromisoformat(row["created_at"]), row["run"]))


def _claims_for(registry: dict[str, Any], acquisition: str) -> list[str]:
    return [claim["id"] for claim in registry["claims"] if acquisition in claim["acquisitions"]]


def _account_lines(context: Context) -> list[str]:
    lines: list[str] = []
    for provider in context.providers.values():
        lines += [provider.account_line(), ""]
    return lines[:-1]


def _status(statuses: Counter[str]) -> str:
    if len(statuses) == 1:
        return next(iter(statuses))
    return ", ".join(f"{count} {status}" for status, count in sorted(statuses.items()))


def _acquisition_table(
    registry: dict[str, Any], context: Context, origin: Path, with_claims: bool, rows: list[dict[str, Any]]
) -> list[str]:
    header = "| Run | Provider | Family | Backend | Jobs | PUBs or circuits | Status | Charge |"
    rule = "| --- | --- | --- | --- | ---: | ---: | --- | ---: |"
    if with_claims:
        header += " Claims |"
        rule += " --- |"
    lines = [header, rule]
    for row in rows:
        line = (
            f"| {_link(row['run'], origin, Path(row['run']).name)} | {context.providers[row['provider']].title} | "
            f"{_cell(row['family'])} | {', '.join(row['backends'])} | {row['jobs']} | {row['circuits']} | "
            f"{_status(row['statuses'])} | {row['charge']} {row['unit']} |"
        )
        if with_claims:
            line += f" {', '.join(_claims_for(registry, row['id']))} |"
        lines.append(line)
    return lines


def _claim_entry(claim: dict[str, Any], origin: Path) -> list[str]:
    lines = [f"- **{claim['id']}** ({claim['evidence_class']}, {claim['domain']}). {claim['statement']}"]
    lines.append(f"  Boundary: {claim['boundary']}")
    if claim.get("proof_origin"):
        lines.append(f"  Proof origin: {claim['proof_origin']}.")
    if claim["assumptions"]:
        lines.append(f"  Assumptions: {'; '.join(claim['assumptions'])}.")
    sources = _evidence_links(claim, origin)
    sources += [_link(document, origin, Path(document).name) for document in claim["documents"]]
    if sources:
        lines.append(f"  Evidence: {', '.join(sources)}.")
    if claim["gates"]:
        verbs = {
            "replay": "replayed by",
            "freshness": "source regenerated by",
            "admission": "replay failure paths checked by",
            "regression": "active code regression checked by",
            "bytes": "bytes verified by",
        }
        parts = [
            f"{verbs[role]} {', '.join(gate for gate, kind in claim['gates'].items() if kind == role)}"
            for role in GATE_ROLES
            if role in claim["gates"].values()
        ]
        lines.append(f"  Gates: {'; '.join(parts)}.")
    if claim.get("kernel_receipt"):
        lines.append(f"  Kernel receipt: {_link(claim['kernel_receipt'], origin, Path(claim['kernel_receipt']).name)}.")
    if claim["acquisitions"]:
        lines.append(f"  Acquisitions: {', '.join(claim['acquisitions'])}.")
    if claim["depends_on"]:
        lines.append(f"  Depends on: {', '.join(claim['depends_on'])}.")
    if claim.get("related_claims"):
        lines.append(f"  Related claims: {', '.join(claim['related_claims'])}.")
    if claim["supersedes"]:
        lines.append(f"  Supersedes: {', '.join(claim['supersedes'])}.")
    if claim.get("superseded_by"):
        lines.append(f"  Superseded by: {claim['superseded_by']}.")
    if claim.get("withdrawn_text"):
        lines.append(f"  Withdrawn text: {claim['withdrawn_text']}")
    return lines


def render_state_document(registry: dict[str, Any], context: Context, rows: list[dict[str, Any]] | None = None) -> str:
    rows = _acquisition_rows(registry, context) if rows is None else rows
    origin = STATE_DOCUMENT
    lines = [
        "# Research state",
        "",
        "Generated by `scripts/research_state.py --write` from",
        f"{_link('docs/state/research_state.json', origin, 'research_state.json')}; gate core-270 fails on any",
        "difference. Edit the registry, never this file. Historical cases, collections",
        "and analyses keep their original bytes; this file states which of their",
        "conclusions stand.",
        "",
        "## Evidence classes",
        "",
        "| Class | Establishes | Does not establish |",
        "| --- | --- | --- |",
    ]
    for name, spec in CLASSES.items():
        lines.append(f"| {name} | {spec['establishes']} | {spec['excludes']} |")
    lines += [
        "",
        "A checksum gate verifies retained bytes, green CI verifies the enabled checks,",
        "and neither establishes a theorem or authorizes a QPU run.",
        "",
        "## Acquisitions",
        "",
        *_account_lines(context),
        "",
        "An IBM job holds PUBs and charges settled QPU seconds; a Quantum Inspire job holds one",
        "circuit and charges the account ledger's change.",
        "",
        *_acquisition_table(registry, context, origin, with_claims=True, rows=rows),
        "",
    ]
    for row in rows:
        detail = f", {row['detail']}" if row["detail"] else ""
        lines.append(f"- **{row['id']}** ({Path(row['run']).name}{detail}): {row['question']}")
    lines.append("")
    for status in STATUS_ORDER:
        members = [claim for claim in registry["claims"] if claim["status"] == status]
        if not members:
            continue
        lines += [f"## {status.capitalize()} claims", ""]
        for domain in DOMAINS:
            for claim in members:
                if claim["domain"] == domain:
                    lines += _claim_entry(claim, origin)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _status_counts(registry: dict[str, Any]) -> str:
    counts = {status: 0 for status in STATUS_ORDER}
    for claim in registry["claims"]:
        counts[claim["status"]] += 1
    return ", ".join(f"{counts[status]} {status}" for status in STATUS_ORDER if counts[status])


def evidence_class_matrix(registry: dict[str, Any]) -> list[str]:
    counts = Counter((claim["evidence_class"], claim["status"]) for claim in registry["claims"])
    lines = ["| Evidence class | Status | Claim records |", "| --- | --- | ---: |"]
    lines.extend(f"| {kind} | {status} | {count} |" for (kind, status), count in sorted(counts.items()))
    lines.extend(
        [
            "",
            "These metadata counts are not summed into a headline of established scientific results.",
            "Independent hardware replication requires an adjudicated replication design, not a job count.",
        ]
    )
    return lines


def render_readme_section(
    registry: dict[str, Any], context: Context, rows: list[dict[str, Any]] | None = None
) -> list[str]:
    rows = _acquisition_rows(registry, context) if rows is None else rows
    origin = ROOT / "README.md"
    return [
        "## Research state",
        "",
        f"{_link('docs/state/RESEARCH_STATE.md', origin, 'RESEARCH_STATE.md')} is the current state of every",
        "registered claim with its evidence class,",
        "boundary, pinned evidence and reproducing gates. Every retained",
        "acquisition of every provider:",
        "",
        *evidence_class_matrix(registry),
        "",
        f"The {_link('docs/evidence/evidence-closure/README.md', origin, 'derived closure view')} preserves",
        "cross-branch coverage, denominator gaps and unresolved dependencies separately from this registry.",
        "",
        *_acquisition_table(registry, context, origin, with_claims=False, rows=rows),
        "",
        *_account_lines(context),
    ]


def render_roadmap_section(registry: dict[str, Any], context: Context) -> list[str]:
    origin = ROOT / "docs/RESEARCH_ROADMAP.md"
    lines = [
        "### Open and proposed claims",
        "",
        f"{_link('docs/state/RESEARCH_STATE.md', origin, 'RESEARCH_STATE.md')} records every registered claim",
        "by evidence class and every executed acquisition. Open and",
        "proposed work, in dependency order:",
        "",
        *evidence_class_matrix(registry),
        "",
    ]
    pending = [claim for claim in registry["claims"] if claim["status"] in {"open", "proposed"}]
    ordered: list[dict[str, Any]] = []
    placed: set[str] = set()
    while len(ordered) < len(pending):
        progress = False
        for claim in pending:
            local = [target for target in claim["depends_on"] if any(item["id"] == target for item in pending)]
            if claim["id"] not in placed and all(target in placed for target in local):
                ordered.append(claim)
                placed.add(claim["id"])
                progress = True
        require(progress, "open and proposed claims form a dependency cycle")
    for claim in ordered:
        after = f" Depends on {', '.join(claim['depends_on'])}." if claim["depends_on"] else ""
        lines.append(f"- **{claim['id']}** ({claim['status']}, {claim['evidence_class']}). {claim['statement']}{after}")
    return lines


def _replace_section(text: str, section: list[str], name: str) -> str:
    require(text.count(BEGIN) == 1 and text.count(END) == 1, f"{name} needs exactly one research-state marker pair")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + "\n".join(section) + "\n" + END + tail


def rendered(registry: dict[str, Any], context: Context) -> dict[Path, str]:
    readme = ROOT / "README.md"
    roadmap = ROOT / "docs/RESEARCH_ROADMAP.md"
    # Every provider adapter re-reads its retained runs on each runs() call, so the views share one read.
    rows = _acquisition_rows(registry, context)
    return {
        STATE_DOCUMENT: render_state_document(registry, context, rows),
        readme: _replace_section(
            readme.read_text(encoding="utf-8"), render_readme_section(registry, context, rows), "README.md"
        ),
        roadmap: _replace_section(
            roadmap.read_text(encoding="utf-8"), render_roadmap_section(registry, context), "RESEARCH_ROADMAP.md"
        ),
    }


# Self-test


def _mutations() -> Iterable[tuple[str, Callable[[dict[str, Any]], None], str]]:
    def claim(registry: dict[str, Any], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
        for entry in registry["claims"]:
            if predicate(entry):
                return entry
        raise AssertionError("the registry lacks the claim a mutation needs")

    def exploratory_established(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "exploratory reanalysis")["status"] = "established"

    def dangling_successor(registry: dict[str, Any]) -> None:
        withdrawn = claim(registry, lambda c: c["status"] == "withdrawn")
        withdrawn["superseded_by"] = "no-such-claim"
        for entry in registry["claims"]:
            entry["supersedes"] = [item for item in entry.get("supersedes", []) if item != withdrawn["id"]]

    def one_sided_supersession(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: bool(c.get("supersedes")))["supersedes"] = []

    def hardware_without_acquisition(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "preregistered hardware inference")["acquisitions"] = []

    def emulator_without_acquisition(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "preregistered emulator control")["acquisitions"] = []

    def emulator_exploratory(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "preregistered emulator control")["status"] = "exploratory"

    def checksum_certificate(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "exact finite certificate")["gates"] = {"sources-242": "bytes"}

    def lint_as_replay(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "exact finite certificate")["gates"] = {
            "sources-120": "replay"
        }

    def lint_as_regression(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "exact finite certificate")["gates"] = {
            "sources-120": "regression"
        }

    def receipt_unpinned(registry: dict[str, Any]) -> None:
        entry = claim(registry, lambda c: c["evidence_class"] == "machine-checked proof")
        entry["evidence"] = [item for item in entry["evidence"] if item["path"] != entry["kernel_receipt"]]

    def unknown_gate(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: bool(c.get("gates")))["gates"] = {"core-9999": "replay"}

    def altered_evidence(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: bool(c.get("evidence")))["evidence"][0]["sha256"] = "0" * 64

    def altered_record_evidence(registry: dict[str, Any]) -> None:
        entry = claim(registry, lambda c: any("#" in item["path"] for item in c["evidence"]))
        next(item for item in entry["evidence"] if "#" in item["path"])["sha256"] = "0" * 64

    def absent_record_evidence(registry: dict[str, Any]) -> None:
        entry = claim(registry, lambda c: any("#" in item["path"] for item in c["evidence"]))
        item = next(item for item in entry["evidence"] if "#" in item["path"])
        item["path"] = evidence_file(item["path"]) + "#jobs/job_id=absent"

    def drop_acquisition(registry: dict[str, Any], provider: str) -> None:
        entries = registry["acquisitions"]
        entries.remove([entry for entry in entries if entry["provider"] == provider][-1])

    def missing_run(registry: dict[str, Any]) -> None:
        drop_acquisition(registry, "ibm")

    def missing_qi_run(registry: dict[str, Any]) -> None:
        drop_acquisition(registry, "quantum_inspire")

    def extra_qi_acquisition(registry: dict[str, Any]) -> None:
        template = next(entry for entry in registry["acquisitions"] if entry["provider"] == "quantum_inspire")
        registry["acquisitions"].append(
            {**template, "id": "qi-unretained", "run": "results/quantum_inspire/runs/2026-10-17T000000Z-tuna_17"}
        )

    def extra_qd_acquisition(registry: dict[str, Any]) -> None:
        template = next(entry for entry in registry["acquisitions"] if entry["provider"] == "quantum_inspire")
        registry["acquisitions"].append(
            {
                **template,
                "id": "qd-unretained",
                "provider": "quandela",
                "run": "results/quandela/runs/2026-10-17T000000Z-sim_belenos-job-00",
            }
        )

    def unknown_provider(registry: dict[str, Any]) -> None:
        registry["acquisitions"][0]["provider"] = "unlisted_cloud"

    def missing_provider(registry: dict[str, Any]) -> None:
        del registry["acquisitions"][0]["provider"]

    def orphan_acquisition(registry: dict[str, Any]) -> None:
        target = registry["acquisitions"][0]["id"]
        for entry in registry["claims"]:
            if target in entry["acquisitions"]:
                entry["acquisitions"] = [item for item in entry["acquisitions"] if item != target] or ["__drop__"]
        for entry in registry["claims"]:
            if entry["acquisitions"] == ["__drop__"]:
                entry["acquisitions"] = [registry["acquisitions"][1]["id"]]

    def established_on_withdrawn(registry: dict[str, Any]) -> None:
        withdrawn = claim(registry, lambda c: c["status"] == "withdrawn")["id"]
        claim(registry, lambda c: c["status"] == "established")["depends_on"] = [withdrawn]

    def dependency_cycle(registry: dict[str, Any]) -> None:
        first = claim(registry, lambda c: c["status"] == "proposed")
        second = claim(registry, lambda c: c["status"] == "proposed" and c["id"] != first["id"])
        first["depends_on"] = [second["id"]]
        second["depends_on"] = [first["id"]]

    def theorem_without_assumptions(registry: dict[str, Any]) -> None:
        claim(registry, lambda c: c["evidence_class"] == "mathematical claim")["assumptions"] = []

    def proof_without_source(registry: dict[str, Any]) -> None:
        entry = claim(registry, lambda c: c["evidence_class"] == "machine-checked proof")
        entry["evidence"] = [item for item in entry["evidence"] if not item["path"].endswith(".v")]

    def conformance_as_hardware(registry: dict[str, Any]) -> None:
        entry = claim(registry, lambda c: c["evidence_class"] == "circuit-conformance check")
        entry["acquisitions"] = [registry["acquisitions"][0]["id"]]

    def missing_proof_origin(registry: dict[str, Any]) -> None:
        claim(registry, lambda entry: entry["evidence_class"] == "mathematical claim").pop("proof_origin")

    def invalid_proof_origin(registry: dict[str, Any]) -> None:
        claim(registry, lambda entry: entry["evidence_class"] == "mathematical claim")["proof_origin"] = "peer-reviewed"

    def finite_proof_origin(registry: dict[str, Any]) -> None:
        claim(registry, lambda entry: entry["evidence_class"] == "exact finite certificate")["proof_origin"] = (
            "external-source"
        )

    def open_proof_origin(registry: dict[str, Any]) -> None:
        claim(registry, lambda entry: entry["evidence_class"] == "mathematical claim" and entry["status"] == "open")[
            "proof_origin"
        ] = "repository-written"

    def unproved_established(registry: dict[str, Any]) -> None:
        claim(
            registry, lambda entry: entry["evidence_class"] == "mathematical claim" and entry["status"] == "established"
        )["proof_origin"] = "unproved-open"

    def dangling_related_claim(registry: dict[str, Any]) -> None:
        registry["claims"][0]["related_claims"] = ["missing-claim"]

    yield "exploratory reanalysis marked established", exploratory_established, "status"
    yield "withdrawn claim names a missing successor", dangling_successor, "is not a claim"
    yield "successor omits the superseded claim", one_sided_supersession, "does not list it"
    yield "hardware inference without an acquisition", hardware_without_acquisition, "names its acquisitions"
    yield "emulator control without an acquisition", emulator_without_acquisition, "names its acquisitions"
    yield "emulator control marked exploratory", emulator_exploratory, "status"
    yield "certificate reproduced only by a checksum", checksum_certificate, "needs a replay gate"
    yield "lint gate counted as replay", lint_as_replay, "is a lint or byte check"
    yield "lint gate counted as regression", lint_as_regression, "is a lint or byte check"
    for kind in sorted(NEEDS_REPRODUCING_GATE):

        def regression_only(registry: dict[str, Any], kind: str = kind) -> None:
            claim(registry, lambda c: c["evidence_class"] == kind)["gates"] = {"core-600": "regression"}

        yield f"{kind} has only a regression gate", regression_only, "needs a replay gate"
    yield "kernel receipt outside the pinned evidence", receipt_unpinned, "pinned as evidence"
    yield "unknown gate", unknown_gate, "is not in ci/gates.json"
    yield "altered evidence bytes", altered_evidence, "digest differs"
    yield "altered record evidence", altered_record_evidence, "digest differs"
    yield "record evidence selecting no record", absent_record_evidence, "digest differs"
    yield "audited run without an acquisition", missing_run, "run set differs from the retained-run audit"
    yield "Quantum Inspire run without an acquisition", missing_qi_run, "run set differs from the Quantum Inspire"
    yield "acquisition naming an unretained Quantum Inspire run", extra_qi_acquisition, "not a retained Quantum Inspire"
    yield "acquisition naming an unretained Quandela run", extra_qd_acquisition, "not a retained Quandela run"
    yield "acquisition from an unknown provider", unknown_provider, "unknown provider"
    yield "acquisition without a provider", missing_provider, "keys differ from the schema"
    yield "established claim on a withdrawn one", established_on_withdrawn, "depends on"
    yield "dependency cycle", dependency_cycle, "cycle"
    yield "theorem without assumptions", theorem_without_assumptions, "assumptions"
    yield "machine-checked proof without its source", proof_without_source, "pins its Rocq source"
    yield "conformance check citing an acquisition", conformance_as_hardware, "only hardware classes"
    yield "missing proof origin", missing_proof_origin, "proof_origin"
    yield "invalid proof origin", invalid_proof_origin, "proof_origin"
    yield "proof origin on a finite certificate", finite_proof_origin, "proof_origin"
    yield "written proof assigned to an open claim", open_proof_origin, "proof_origin"
    yield "unproved established claim", unproved_established, "proof_origin"
    yield "dangling related claim", dangling_related_claim, "related_claims"


def _qi_mutations() -> Iterable[tuple[str, Callable[[dict[str, dict[str, Any]], dict[str, Any]], None], str]]:
    """Mutations of the loaded Quantum Inspire run records and ledger that the run rules must reject."""

    def record(records: dict[str, dict[str, Any]], suffix: str) -> dict[str, Any]:
        return next(value for run, value in records.items() if run.endswith(suffix))

    def bind_v2(target: dict[str, Any]) -> None:
        target["submission"].update(
            {"schema": "qi-submission-v2", "state": "enqueued", "cases_sha256": target["cases_sha256"]}
        )
        for row in target["submission"]["jobs"]:
            row["sha256"] = target["circuits"][row["file"]]

    def circuit_digest(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-tuna_17")["circuits"]["teleport.cq"] = "0" * 64

    def raw_short(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-tuna_17")["raw"]["additivity-A.cq.json"].pop()

    def raw_altered(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        shots = record(records, "-tuna_17")["raw"]["teleport.cq.json"]
        shots[0] = "".join("1" if bit == "0" else "0" for bit in shots[0])

    def raw_missing(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        del record(records, "-QXsinglenodesimulator")["raw"]["teleport.cq.json"]

    def failed_with_raw(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-Rydberg")["raw"]["teleport.cq.json"] = ["0" * 9]

    def uncollected(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-Rydberg-diagnostic")["results"] = None

    def foreign_transaction(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-tuna_17")["results"]["transactions"].append({"id": 1, "job": 1, "change": 0})

    def ledger_extra_job(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["jobs"].append({**ledger["jobs"][0], "job": 1})

    def ledger_duplicate_job(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["jobs"].append(copy.deepcopy(ledger["jobs"][0]))

    def retained_duplicate_job(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        source = next(iter(records))
        records[source + "-duplicate"] = copy.deepcopy(records[source])

    def submitted_duplicate_job(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        jobs = record(records, "-tuna_17")["submission"]["jobs"]
        jobs[1]["job"] = jobs[0]["job"]

    def aggregate_shots(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["totals"]["shots_done"] += 1

    def aggregate_change(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["totals"]["change"] += 1

    def ledger_status(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        job = ledger["jobs"][0]
        job["status"] = "failed" if job["status"] == "completed" else "completed"

    def ledger_charge(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["jobs"][0]["charged"] += 1

    def ledger_missing_job(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["jobs"].pop(0)

    def v1_unretained(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["schema"], ledger["unretained"] = "qi-usage-v1", []

    def receipt_manifest_changed(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-tuna_17")
        bind_v2(target)
        target["cases_sha256"] = "0" * 64

    def receipt_manifest_missing(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-tuna_17")
        bind_v2(target)
        del target["submission"]["cases_sha256"]

    def receipt_not_enqueued(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-tuna_17")
        bind_v2(target)
        target["submission"]["state"] = "created"

    def receipt_job_changed(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-tuna_17")
        bind_v2(target)
        target["submission"]["jobs"][0]["sha256"] = "0" * 64

    def receipt_job_digest_missing(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-tuna_17")
        bind_v2(target)
        del target["submission"]["jobs"][0]["sha256"]

    def receipt_absent(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        target = record(records, "-Rydberg-diagnostic")
        target["submission"], target["interrupted"] = None, True

    def legacy_receipt_manifest_changed(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        record(records, "-tuna_17")["submission"]["cases_sha256"] = "0" * 64

    yield "circuit differing from its cases.json digest", circuit_digest, "digest differs from cases.json"
    yield "run directory without its receipt", receipt_absent, "run qi_platform.py reconcile"
    yield "raw shot list shorter than shots done", raw_short, "length differs"
    yield "raw shots differing from the recorded histogram", raw_altered, "outcome histogram"
    yield "completed job without its raw file", raw_missing, "raw/ holds"
    yield "failed job holding a raw file", failed_with_raw, "raw/ holds"
    yield "submitted run never collected", uncollected, "results.json is missing"
    yield "transaction charging a job outside the run", foreign_transaction, "charges another job"
    yield "ledger job neither retained nor declared", ledger_extra_job, "its unretained list omits"
    yield "ledger repeats a job id", ledger_duplicate_job, "ledger job ids repeat"
    yield "two retained runs repeat a job id", retained_duplicate_job, "job ids repeat across retained runs"
    yield "submission repeats a job id", submitted_duplicate_job, "submitted job ids repeat"
    yield "ledger aggregate shots changed", aggregate_shots, "aggregate shots_done differs"
    yield "ledger aggregate change changed", aggregate_change, "aggregate change differs"
    yield "retained job with another ledger status", ledger_status, "differ from the runs"
    yield "retained job with another ledger charge", ledger_charge, "differ from the runs"
    yield "retained job missing from the ledger", ledger_missing_job, "missing from the ledger"
    yield "v1 ledger carrying an unretained list", v1_unretained, "carries no unretained list"
    yield "v2 receipt with altered manifest", receipt_manifest_changed, "cases.json digest differs from submission"
    yield "v2 receipt without manifest digest", receipt_manifest_missing, "cases.json digest differs from submission"
    yield "v2 receipt never confirmed enqueued", receipt_not_enqueued, "not confirmed enqueued"
    yield "v2 receipt with altered uploaded bytes", receipt_job_changed, "bytes its receipt uploaded"
    yield "v2 receipt without uploaded byte digest", receipt_job_digest_missing, "bytes its receipt uploaded"
    yield "v1 receipt with altered manifest binding", legacy_receipt_manifest_changed, "cases.json digest differs"


def _qi_row_mutations() -> Iterable[tuple[str, Callable[[dict[str, dict[str, Any]], dict[str, Any]], None], str]]:
    """Mutations of the synthetic transaction rows that the run-to-ledger row comparison must reject."""

    def first_row(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
        return next(run for run in records.values() if run["results"]["transactions"])["results"]["transactions"][0]

    def run_id(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        first_row(records)["id"] += 1000

    def run_timestamp(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        first_row(records)["timestamp"] = "2026-01-01T00:00:00Z"

    def run_domain(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        first_row(records)["domain"] = "other"

    def run_field_missing(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        del first_row(records)["domain"]

    def ledger_field_missing(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        del ledger["transactions"][-1]["timestamp"]

    def run_zero_duplicate(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        run = next(run for run in records.values() if run["results"]["transactions"])
        run["results"]["transactions"].append({**first_row(records), "id": 9000, "change": 0})

    def duplicate_everywhere(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        # Both sides repeat one +5 row; the job charge and the totals follow, so only the id rule can reject it.
        run = next(run for run in records.values() if run["results"]["transactions"])
        row = next(row for row in ledger["transactions"] if row["id"] == SYNTHETIC_ROW_ID)
        run["results"]["transactions"].append({key: row[key] for key in TRANSACTION_FIELDS})
        ledger["transactions"].append(copy.deepcopy(row))
        next(job for job in ledger["jobs"] if job["job"] == row["job"])["charged"] += 5
        ledger["totals"]["change"] += 5

    def ledger_zero_duplicate(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["transactions"].append({**ledger["transactions"][-1], "id": 9000, "change": 0})

    def ledger_dropped(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["transactions"].pop()

    def ledger_dangling(records: dict[str, dict[str, Any]], ledger: dict[str, Any]) -> None:
        ledger["transactions"].append({**ledger["transactions"][-1], "id": 9001, "job": 1, "change": 0})

    yield "run transaction id changed", run_id, "transaction rows of the retained jobs differ"
    yield "run transaction timestamp changed", run_timestamp, "transaction rows of the retained jobs differ"
    yield "run transaction domain changed", run_domain, "transaction rows of the retained jobs differ"
    yield "run transaction without its domain", run_field_missing, "lacks domain"
    yield "ledger transaction without its timestamp", ledger_field_missing, "lacks timestamp"
    yield "zero-change row added to a run", run_zero_duplicate, "transaction rows of the retained jobs differ"
    yield (
        "synthetic row repeated in the run and the ledger",
        duplicate_everywhere,
        f"transaction id {SYNTHETIC_ROW_ID} repeats",
    )
    yield "zero-change row added to the ledger", ledger_zero_duplicate, "transaction rows of the retained jobs differ"
    yield "ledger transaction row dropped", ledger_dropped, "transaction rows of the retained jobs differ"
    yield "ledger transaction charging a job outside the ledger", ledger_dangling, "charge jobs outside the ledger"


def _qi_declared_mutations() -> Iterable[tuple[str, Callable[[dict[str, Any]], None], str | None]]:
    """Mutations of a v2 ledger that declares one unretained job; None marks the ones that must pass."""

    def undeclared(ledger: dict[str, Any]) -> None:
        ledger["unretained"].remove(SYNTHETIC_JOB_ID)

    def declared_absent(ledger: dict[str, Any]) -> None:
        ledger["unretained"].append(SYNTHETIC_JOB_ID + 1)

    def declared_repeated(ledger: dict[str, Any]) -> None:
        ledger["unretained"].append(SYNTHETIC_JOB_ID)

    def declared_and_retained(ledger: dict[str, Any]) -> None:
        ledger["unretained"].append(ledger["jobs"][0]["job"])

    def dangling(ledger: dict[str, Any]) -> None:
        ledger["transactions"].append(
            {**ledger["transactions"][-1], "id": SYNTHETIC_ROW_ID + 2, "job": SYNTHETIC_JOB_ID + 1}
        )

    def declared_charge(ledger: dict[str, Any]) -> None:
        ledger["totals"]["change"] += 1

    def declared_job_charge(ledger: dict[str, Any]) -> None:
        next(job for job in ledger["jobs"] if job["job"] == SYNTHETIC_JOB_ID)["charged"] += 1

    yield "declared job also retained", declared_and_retained, None
    yield "ledger job neither retained nor declared (v2)", undeclared, "its unretained list omits"
    yield "declared job absent from the ledger", declared_absent, "declares unretained jobs that it does not list"
    yield "declared job repeated", declared_repeated, "unretained job ids repeat"
    yield "transaction charging a job outside a v2 ledger", dangling, "charge jobs outside the ledger"
    yield "declared job charge outside the totals", declared_charge, "aggregate change differs"
    yield "declared job with another charge than its rows", declared_job_charge, "job charges differ"


def _with_declared_job(ledger: dict[str, Any]) -> dict[str, Any]:
    """A v2 copy of the ledger with one unretained job of another branch and a charged transaction row on it.

    The job and its +3 row sit in the totals and in the declared list, so the
    copy validates while the retained runs stay unchanged.
    """
    ledger = copy.deepcopy(ledger)
    template = ledger["jobs"][0]
    ledger["schema"] = "qi-usage-v2"
    ledger["jobs"].append({**template, "job": SYNTHETIC_JOB_ID, "charged": 3})
    ledger["unretained"] = sorted([*ledger.get("unretained", []), SYNTHETIC_JOB_ID])
    ledger["transactions"].append(
        {
            "id": SYNTHETIC_ROW_ID + 1,
            "timestamp": template["created_on"],
            "domain": "compute",
            "change": 3,
            "job": SYNTHETIC_JOB_ID,
            "backend_type_id": template["backend_type_id"],
        }
    )
    ledger["totals"]["change"] += 3
    ledger["totals"]["shots_done"] += template["shots_done"]
    return ledger


def _with_synthetic_rows(
    records: dict[str, dict[str, Any]], ledger: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Copies of the retained records and ledger plus a synthetic +5/-5 transaction pair.

    The pair charges one retained job a +5 and a -5 row, which leaves every
    per-job charge unchanged while the run results and the ledger carry the
    same two added rows.
    """
    records, ledger = copy.deepcopy(records), copy.deepcopy(ledger)
    run = next(iter(records))
    submission = records[run]["submission"]
    job = submission["jobs"][0]["job"]
    stamp = "2026-10-16T21:16:40.000000Z"
    rows = [
        {"id": SYNTHETIC_ROW_ID, "timestamp": stamp, "domain": "compute", "change": 5, "job": job},
        {"id": SYNTHETIC_OFFSET_ID, "timestamp": stamp, "domain": "compute", "change": -5, "job": job},
    ]
    records[run]["results"]["transactions"].extend(copy.deepcopy(rows))
    ledger["transactions"].extend({**row, "backend_type_id": submission["backend_type_id"]} for row in rows)
    return records, ledger


# One self-test case: name, the rejection text its validation must contain (None
# for a baseline that must pass), the registry, and the quantum_inspire run records
# and ledger to install (None keeps the retained ones).
Case = tuple[str, str | None, dict[str, Any], dict[str, dict[str, Any]] | None, dict[str, Any] | None]


class CaseVerdict:
    """Validates one self-test case and returns the ValueError text, or None when it validates.

    The serial path reuses the caller's context. A pickled copy carries none
    and each pool worker loads its own once, so every process validates against
    the repository facts of its own Context.
    """

    def __init__(self, context: Context | None = None) -> None:
        self._loaded: tuple[Context, QuantumInspireRuns, dict[str, dict[str, Any]], dict[str, Any]] | None = None
        if context is not None:
            self._loaded = self._adopt(context)

    def __getstate__(self) -> dict[str, Any]:
        return {"_loaded": None}

    @staticmethod
    def _adopt(context: Context) -> tuple[Context, QuantumInspireRuns, dict[str, dict[str, Any]], dict[str, Any]]:
        qi = context.providers["quantum_inspire"]
        if not isinstance(qi, QuantumInspireRuns):
            raise ValueError("the quantum_inspire provider is not the run-directory adapter")
        return context, qi, qi.records, qi.ledger

    def __call__(self, case: Case) -> str | None:
        _, _, registry, records, ledger = case
        if self._loaded is None:
            self._loaded = self._adopt(Context())
        context, qi, retained_records, retained_ledger = self._loaded
        qi.records = retained_records if records is None else records
        qi.ledger = retained_ledger if ledger is None else ledger
        try:
            validate(registry, context)
        except ValueError as error:
            return str(error)
        finally:
            qi.records, qi.ledger = retained_records, retained_ledger
        return None


def _cases(registry: dict[str, Any], qi: QuantumInspireRuns) -> list[Case]:
    """Every self-test case in the order the rules are exercised, each on its own deep copies."""
    records, ledger = qi.records, qi.ledger
    cases: list[Case] = [("retained state", None, copy.deepcopy(registry), None, None)]
    for name, mutate, expected in _mutations():
        candidate = copy.deepcopy(registry)
        mutate(candidate)
        cases.append((name, expected, candidate, None, None))
    receipts = copy.deepcopy(records)
    for record in receipts.values():
        record["submission"]["schema"] = "qi-submission-v2"
        record["submission"]["state"] = "enqueued"
        record["submission"]["cases_sha256"] = record["cases_sha256"]
        for row in record["submission"]["jobs"]:
            row["sha256"] = record["circuits"][row["file"]]
    cases.append(("v2 receipts", None, copy.deepcopy(registry), receipts, None))
    for name, mutate_files, expected in _qi_mutations():
        mutated_records, mutated_ledger = copy.deepcopy(records), copy.deepcopy(ledger)
        mutate_files(mutated_records, mutated_ledger)
        cases.append((name, expected, copy.deepcopy(registry), mutated_records, mutated_ledger))
    baseline_records, baseline_ledger = _with_synthetic_rows(records, ledger)
    cases.append(("synthetic transaction rows", None, copy.deepcopy(registry), baseline_records, baseline_ledger))
    for name, mutate_rows, expected in _qi_row_mutations():
        mutated_records, mutated_ledger = copy.deepcopy(baseline_records), copy.deepcopy(baseline_ledger)
        mutate_rows(mutated_records, mutated_ledger)
        cases.append((name, expected, copy.deepcopy(registry), mutated_records, mutated_ledger))
    declared_ledger = _with_declared_job(ledger)
    cases.append(("declared unretained job", None, copy.deepcopy(registry), None, declared_ledger))
    for name, mutate_declared, declared_expected in _qi_declared_mutations():
        mutated_ledger = copy.deepcopy(declared_ledger)
        mutate_declared(mutated_ledger)
        cases.append((name, declared_expected, copy.deepcopy(registry), None, mutated_ledger))
    return cases


def self_test(registry: dict[str, Any], context: Context) -> int:
    qi = context.providers["quantum_inspire"]
    if not isinstance(qi, QuantumInspireRuns):
        raise ValueError("the quantum_inspire provider is not the run-directory adapter")
    cases = _cases(registry, qi)
    verdicts = parallel.ordered_map(CaseVerdict(context), cases, min_items=2)
    for (name, expected, *_), verdict in zip(cases, verdicts, strict=True):
        if expected is None:
            if verdict is not None:
                raise ValueError(verdict)
        elif verdict is None:
            raise ValueError(f"mutation {name!r} passed validation")
        else:
            require(expected in verdict, f"mutation {name!r} failed for another reason: {verdict}")
    _check_declared_retained_summary(qi)
    return sum(1 for case in cases if case[1] is not None)


def _check_declared_retained_summary(qi: QuantumInspireRuns) -> None:
    """A declared job whose run is retained counts as retained in the account statement."""
    ledger = qi.ledger
    retained = next(iter(qi.records.values()))["submission"]["jobs"][0]["job"]
    qi.ledger = {**copy.deepcopy(ledger), "schema": "qi-usage-v2", "unretained": [retained]}
    try:
        line = qi.account_line()
    finally:
        qi.ledger = ledger
    require("declared unretained" not in line, f"a retained declared job enters the unretained summary: {line}")


def add_acquisitions(entries: list[dict[str, str]]) -> None:
    """Append acquisitions to the registry file as text, keeping the hand formatting of every other entry, and
    refuse entries the registry rules reject once all of them are in place."""
    text = REGISTRY.read_text(encoding="utf-8")
    registry = json.loads(text)
    ids = {row["id"] for row in registry["acquisitions"]}
    runs = {row["run"] for row in registry["acquisitions"]}
    blocks = []
    for entry in entries:
        require(set(entry) == ACQUISITION_KEYS and all(entry.values()), "an acquisition needs every field")
        require(entry["id"] not in ids, f"{entry['id']} is registered")
        require(entry["run"] not in runs, f"{entry['run']} is registered")
        ids.add(entry["id"])
        runs.add(entry["run"])
        blocks.append("\n".join("    " + line for line in json.dumps(entry, indent=2, ensure_ascii=False).splitlines()))
    head, separator, tail = text.partition('\n  ],\n  "claims": [\n')
    require(bool(separator), "the registry's acquisitions list ends in an unexpected layout")
    updated = head + "".join(f",\n{block}" for block in blocks) + separator + tail
    validate(json.loads(updated), Context(), uncited=frozenset(entry["id"] for entry in entries))
    REGISTRY.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate and compare every rendered section")
    mode.add_argument("--write", action="store_true", help="validate and rewrite every rendered section")
    mode.add_argument("--self-test", action="store_true", help="apply registry mutations each rule must reject")
    mode.add_argument(
        "--add-acquisition",
        nargs=5,
        action="append",
        metavar=("ID", "PROVIDER", "RUN", "FAMILY", "QUESTION"),
        help="append an acquisition before its claim exists (repeatable; the entries validate together); write the "
        "claim, then --write renders the views",
    )
    arguments = parser.parse_args()
    if arguments.add_acquisition:
        fields = ("id", "provider", "run", "family", "question")
        try:
            add_acquisitions([dict(zip(fields, values, strict=True)) for values in arguments.add_acquisition])
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(f"research state: {error}", file=sys.stderr)
            return 1
        for values in arguments.add_acquisition:
            print(f"research state: registered acquisition {values[0]}")
        return 0
    try:
        registry = load_json(REGISTRY)
        context = Context()
        if arguments.self_test:
            print(f"research state: {self_test(registry, context)} mutations rejected")
            return 0
        validate(registry, context)
        outputs = rendered(registry, context)
        if arguments.write:
            for path, text in outputs.items():
                path.write_text(text, encoding="utf-8")
            return 0
        stale = [
            str(path.relative_to(ROOT)) for path, text in outputs.items() if path.read_text(encoding="utf-8") != text
        ]
        require(not stale, f"rendered state differs in {', '.join(stale)}; run scripts/research_state.py --write")
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"research state: {error}", file=sys.stderr)
        return 1
    print(f"research state: {len(registry['claims'])} claims, {len(registry['acquisitions'])} acquisitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
