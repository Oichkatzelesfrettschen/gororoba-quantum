"""Run the six universal pre-flight gates over the retained records of a run or case directory.

The gates apply the cross-machine checklist (docs/notes/machine-routing.md) to files already on disk, so the same
check runs before a submission (records of the plan) and after it (records of the run):

1. baseline: a classical, twin or ideal baseline is present, and a digest-bound one matches its file.
2. fresh live read: the plan record holds the provider's live reads (backend inventory, platform status, credit
   balance or queue) taken at plan time.
3. seed provenance: every seed value in the records is a QRNG value the draw records hold, or a value the seed
   ledgers (ci/reproduction_seeds.json, docs/evidence/qrng_seeds/allocations.json) already account for.
4. budget and ceiling: the ceiling is bound and the expected spend stays inside the balance or the limits.
5. health control: the records declare the in-job health control the provider needs.
6. approval and recovery: an approval is recorded, and the receipt names the handle that resumes the job.

A case directory that holds case_meta.json also passes scripts/check_case_contract.py.

Usage: "$PYTHON" scripts/preflight_check.py --provider {ibm,quandela,iqm,qi} RUN_OR_CASE_DIR

Exit 0 when every gate passes, 1 when a gate fails, 2 when the directory holds no record of the provider.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import check_case_contract  # noqa: E402
import seed_provenance  # noqa: E402

import qrng_seeds  # noqa: E402
import run_records  # noqa: E402

PROVIDERS = run_records.PROVIDERS
GATES = (
    "baseline",
    "fresh live read",
    "seed provenance",
    "budget and ceiling",
    "health control",
    "approval and recovery",
)
BASELINE_KEYS = ("ideal", "predict", "baseline", "census", "certificate", "twin", "slos")
# The plan-time reads of an IBM run may trail the plan record by at most this long.
IBM_READ_WINDOW_SECONDS = 3600.0


@dataclass(frozen=True)
class Verdict:
    gate: str
    ok: bool
    detail: str


Check = Callable[[Path], tuple[bool, str]]


def read(directory: Path, name: str) -> dict[str, Any]:
    value = run_records.read_json(directory / name)
    return value if isinstance(value, dict) else {}


def walk(value: Any) -> Iterator[tuple[str, Any]]:
    """Every (key, value) pair of a parsed JSON value at any depth."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def digest_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seconds_between(first: str, second: str) -> float:
    return abs((datetime.fromisoformat(first) - datetime.fromisoformat(second)).total_seconds())


def is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def numbers(*items: Any) -> list[float] | None:
    """The items as floats (a decimal string counts, as a balance records it); None when any is no number."""
    values = []
    for item in items:
        if isinstance(item, str):
            try:
                item = float(item)
            except ValueError:
                return None
        if not is_number(item):
            return None
        values.append(float(item))
    return values


# Gate 1: baseline


def baseline(provider: str, directory: Path) -> tuple[bool, str]:
    if provider == "ibm":
        passed = read(directory, "record.json").get("compiled_ideal_validation", {}).get("all_candidates_passed")
        return (
            passed is True,
            "compiled circuits match the ideal statevector"
            if passed is True
            else "record.json holds no passing compiled_ideal_validation",
        )
    cases = read(directory, "cases.json")
    found = [(key, value) for key, value in walk(cases) if any(token in key.lower() for token in BASELINE_KEYS)]
    if not found:
        return False, "cases.json names no ideal, prediction, census, certificate or twin entry"
    for key, value in found:
        if key == "prediction_sha256":
            prediction = directory / "prediction.json"
            if not prediction.is_file() or digest_of(prediction) != value:
                return False, "prediction.json differs from the digest cases.json binds"
        if isinstance(value, dict) and {"path", "sha256"} <= set(value):
            target = ROOT / str(value["path"])
            if not target.is_file() or digest_of(target) != value["sha256"]:
                return False, f"{value['path']} differs from its recorded sha256"
    return True, f"baseline entries: {sorted({key for key, _ in found})[:4]}"


# Gate 2: fresh live read


def fresh_read(provider: str, directory: Path) -> tuple[bool, str]:
    if provider == "ibm":
        record = read(directory, "record.json")
        started = record.get("started")
        planned = record.get("submission", {}).get("planned_backends", [])
        if not planned or not isinstance(started, str):
            return False, "record.json names no planned backend or start time"
        for backend in planned:
            entry = record.get("backends", {}).get(backend, {})
            fetched = entry.get("fetched_at")
            if not isinstance(fetched, str) or entry.get("operational") is not True:
                return False, f"{backend}: no operational fetched_at read in the plan record"
            if seconds_between(fetched, started) > IBM_READ_WINDOW_SECONDS:
                return False, f"{backend}: the read at {fetched} is stale against the plan at {started}"
        if not record.get("revalidation"):
            return False, "record.json holds no revalidation read"
        if not is_number(record.get("budget_plan", {}).get("remaining_seconds")):
            return False, "record.json holds no usage read (budget_plan.remaining_seconds)"
        return (
            True,
            f"backend reads {planned} within {IBM_READ_WINDOW_SECONDS:g} s of the plan, usage and revalidation present",
        )
    submission = read(directory, "submission.json")
    if provider == "quandela":
        missing = [
            key for key in ("availability_at_plan", "platform_at_plan", "perfs_at_plan") if not submission.get(key)
        ]
        if missing:
            return False, f"submission.json lacks {missing}"
        platform = submission["platform_at_plan"]
        if platform.get("bookable") is not True or platform.get("is_locked") is not False:
            return False, "the platform read says unbookable or locked"
        status = submission.get("status_at_plan")
        if isinstance(status, dict) and status.get("processor") not in submission.get("admitted_statuses", []):
            return False, f"processor status {status.get('processor')} is outside admitted_statuses"
        return True, "availability, platform and performance reads at plan time"
    if provider == "iqm":
        bound = numbers(submission.get("credit_before", {}).get("currentBalance"))
        if bound is None:
            return False, "submission.json holds no credit_before balance read"
        return True, f"credit balance {bound[0]:g} read before submission"
    status = submission.get("backend_status_at_submit")
    queue = submission.get("queue_at_submit")
    if (
        status not in ("idle", "executing")
        or not isinstance(queue, dict)
        or submission.get("queue_user_only") is not True
    ):
        return False, "submission.json lacks an idle or executing backend status with the own-queue read"
    return True, f"backend {status}, own queue read"


# Gate 3: seed provenance


def ledger_values() -> set[int]:
    """Every seed value the reproduction ledger and the QRNG allocations account for."""
    rows = seed_provenance.load(seed_provenance.BASELINE, "seeds")
    for field in ("allocations", "runtime", "reserved"):
        rows += seed_provenance.load(seed_provenance.ALLOCATIONS, field)
    return {row["value"] for row in rows if isinstance(row.get("value"), int)}


def seed_values(documents: list[Any]) -> list[tuple[str, int]]:
    return [
        (key, value)
        for document in documents
        for key, value in walk(document)
        if seed_provenance.seed_name(key) and isinstance(value, int) and not isinstance(value, bool)
    ]


def qrng_values(texts: list[str]) -> tuple[set[int], list[str]]:
    """The values the qrng:<draw>#<index> references of these texts resolve to, and the references that fail."""
    values: set[int] = set()
    broken: list[str] = []
    for text in texts:
        for match in qrng_seeds.REF.finditer(text):
            path, index = match.group(1), int(match.group(2))
            try:
                record = qrng_seeds.read_record(path, ROOT)
                seed_provenance.SOURCES[path.rpartition("/")[0]](record)
                values.add(record["values"][index])
            except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
                broken.append(f"{match.group(0)}: {error}")
    return values, broken


def seeds(provider: str, directory: Path) -> tuple[bool, str]:
    names = ["record.json"] if provider == "ibm" else ["cases.json", "submission.json"]
    paths = [directory / name for name in [*names, "case_meta.json"] if (directory / name).is_file()]
    if not paths:
        return False, "no record to scan"
    texts = [path.read_text(encoding="utf-8") for path in paths]
    drawn, broken = qrng_values(texts)
    if broken:
        return False, f"unresolved QRNG references: {broken[:2]}"
    known = ledger_values() | drawn
    found = seed_values([json.loads(text) for text in texts])
    unaccounted = sorted({(key, value) for key, value in found if value not in known})
    if unaccounted:
        return False, f"seed values outside the ledgers and the draws: {unaccounted[:3]}"
    return True, f"{len(found)} seed values accounted, {len(drawn)} QRNG values resolved"


# Gate 4: budget and ceiling


def budget(provider: str, directory: Path) -> tuple[bool, str]:
    if provider == "ibm":
        plan = read(directory, "record.json").get("budget_plan", {})
        bound = numbers(
            plan.get("max_total_execution_seconds"),
            plan.get("remaining_seconds"),
            plan.get("reserve_seconds"),
            plan.get("combined_ceiling_seconds"),
        )
        if bound is None:
            return False, "budget_plan lacks max_total_execution_seconds, remaining, reserve or the combined ceiling"
        total, remaining, reserve, combined = bound
        if plan.get("admitted") is not True or total > remaining - reserve or combined > total:
            return (
                False,
                f"budget_plan: total {total} against remaining {remaining} less reserve {reserve}, combined {combined}",
            )
        return True, f"max_total_execution_seconds {total:g} within remaining {remaining:g} less reserve {reserve:g}"
    submission, cases = read(directory, "submission.json"), read(directory, "cases.json")
    if provider == "quandela":
        bound = numbers(
            submission.get("credit_ceiling"),
            submission.get("max_credits"),
            submission.get("estimated_credits"),
            submission.get("expected_seconds"),
            submission.get("platform_at_plan", {}).get("max_duration"),
        )
        if bound is None:
            return (
                False,
                "submission.json lacks a credit ceiling, estimate, expected seconds or platform duration limit",
            )
        ceiling, maximum, estimated, seconds, limit = bound
        if not estimated <= ceiling <= maximum or seconds > limit or cases.get("max_duration", 0) > limit:
            return (
                False,
                f"estimate {estimated} ceiling {ceiling} max {maximum}, seconds {seconds} against limit {limit}",
            )
        return True, f"credit_ceiling {ceiling:g} within max_credits {maximum:g}, {seconds:g} s within {limit:g} s"
    if provider == "iqm":
        bound = numbers(
            submission.get("max_credits"), submission.get("expected_seconds"), submission.get("price_per_second")
        )
        if bound is None:
            return False, "submission.json lacks max_credits, expected seconds or price"
        maximum, seconds, price = bound
        # The balance read belongs to gate 2; a missing read fails there and the ceiling check stands alone here.
        balance = numbers(submission.get("credit_before", {}).get("currentBalance"))
        if seconds * price > maximum or (balance is not None and maximum > balance[0]):
            return False, f"{seconds} s x {price} against max_credits {maximum} and balance {balance}"
        return True, f"{seconds * price:.4g} credits expected within max_credits {maximum:g}"
    bound = numbers(
        submission.get("queue_limit_at_submit"),
        submission.get("queue_at_submit", {}).get("number_of_jobs_in_queue"),
    )
    if bound is None or not isinstance(submission.get("shots"), int):
        return False, "submission.json lacks the queue limit, own queue count or shot count"
    limit, jobs = bound
    if limit < 1 or jobs >= limit:
        return False, f"own queue {jobs:g} reaches the limit {limit:g}"
    return True, f"own queue {jobs:g} below the limit {limit:g}"


# Gate 5: health control


def health(provider: str, directory: Path) -> tuple[bool, str]:
    if provider == "ibm":
        record = read(directory, "record.json")
        planned = record.get("submission", {}).get("planned_backends", [])
        used: dict[str, set[int]] = {}
        for pub in record.get("execution_pubs", []):
            for component in pub.get("components", []):
                used.setdefault(pub["backend"], set()).update(component.get("physical_qubits", []))
        for backend in planned:
            excluded = record.get("backends", {}).get(backend, {}).get("excluded_qubits")
            if not isinstance(excluded, dict):
                return False, f"{backend}: no excluded_qubits read recorded"
            hit = sorted(used.get(backend, set()) & {int(qubit) for qubit in excluded})
            if hit:
                return False, f"{backend}: the layout uses excluded qubits {hit}"
        return True, f"layout avoids every excluded qubit on {planned}"
    cases = read(directory, "cases.json")
    if provider == "quandela":
        preregistered = cases.get("preregistered")
        if not isinstance(preregistered, dict) or not preregistered:
            return False, "cases.json declares no preregistered readings"
        if cases.get("schema") == "qd-hypercomplex-cases-v1" and not isinstance(cases.get("mitigations"), list):
            return False, "cases.json omits the explicit mitigations list"
        return True, f"preregistered readings {sorted(preregistered)[:3]}"
    if provider == "iqm":
        submission = read(directory, "submission.json")
        pinned = [
            job.get("options", {}).get("calibration_set_id", {}).get(submission.get("qc"))
            for job in cases.get("jobs", [])
            if job.get("job") == submission.get("job")
        ]
        observed = read(directory, "results.json").get("compilation", {}).get("calibration_set_id")
        if not pinned or not pinned[0]:
            return False, "the case pins no calibration_set_id for the backend"
        if observed is not None and observed != pinned[0]:
            return False, "the compiled calibration set differs from the pinned one"
        return True, f"calibration set {pinned[0]} pinned and matched"
    readouts = [row for row in cases.get("circuits", []) if str(row.get("file", "")).startswith("readout")]
    guard = cases.get("preregistered", {}).get("guard") if isinstance(cases.get("preregistered"), dict) else None
    if len(readouts) >= 2 or (isinstance(guard, str) and guard):
        return True, f"{len(readouts)} readout circuits, guard declared: {bool(guard)}"
    return False, "the batch holds no readout pair and the case declares no guard"


# Gate 6: approval and recovery


def approval(provider: str, directory: Path) -> tuple[bool, str]:
    if not run_records.approval_present(provider, directory):
        return False, "no approval is recorded"
    if not run_records.recovery_handle(provider, directory):
        return False, "the receipt names no job id to recover from"
    return True, "approval recorded and the receipt names its recovery handle"


CHECKS: tuple[Callable[[str, Path], tuple[bool, str]], ...] = (baseline, fresh_read, seeds, budget, health, approval)


def evaluate(provider: str, directory: Path) -> list[Verdict]:
    """The six gate verdicts of a directory, plus the contract verdict when it holds case_meta.json."""
    if provider not in PROVIDERS:
        raise ValueError(f"provider {provider!r} is not one of {PROVIDERS}")
    verdicts = []
    for number, (name, check) in enumerate(zip(GATES, CHECKS, strict=True), start=1):
        try:
            ok, detail = check(provider, directory)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
            ok, detail = False, f"{type(error).__name__}: {error}"
        verdicts.append(Verdict(f"gate {number} {name}", ok, detail))
    if (directory / check_case_contract.CASE_FILE).is_file():
        problems = check_case_contract.check_case_dir(directory)
        verdicts.append(
            Verdict("case contract", not problems, "; ".join(problems[:3]) or "case_meta.json holds the contract")
        )
    return verdicts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--provider", choices=PROVIDERS, required=True)
    parser.add_argument("directory", type=Path)
    arguments = parser.parse_args()
    marker = "record.json" if arguments.provider == "ibm" else "cases.json"
    if not (arguments.directory / marker).is_file():
        print(f"preflight_check: {arguments.directory} holds no {marker}", file=sys.stderr)
        return 2
    verdicts = evaluate(arguments.provider, arguments.directory)
    for verdict in verdicts:
        print(f"{'PASS' if verdict.ok else 'FAIL'} {verdict.gate}: {verdict.detail}")
    return 0 if all(verdict.ok for verdict in verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
