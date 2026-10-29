"""Verify a retained service inventory against every lossless job archive.

The service snapshot records a bounded read-only observation. Offline replay
checks archive coverage and identities; it cannot refresh live account state.
The account's consumed seconds cover a rolling usage_period, so they equal the
final charges of the jobs that ran inside that period, not of every retained
job: a job finished before the period's start has rolled out of the window.

Each IBM Cloud instance has its own quota, usage period and inventory file.
qpu-job-inventory.json holds the default instance; any other instance holds
qpu-job-inventory.<instance_crn_hash>.json. A raw archive belongs to the
instance its run record names (instance_sha256_12), and to the default
instance when the run is a retrospective recovery without one. Coverage, the
usage-window sum and the reserve hold per instance; the historical-job and
campaign accounting bind the default instance only.

A job that ends in ERROR or CANCELLED (a max-time cancellation, a user
error) bills the QPU lock time it consumed and returns no result, so it has
no raw archive. Its inventory row carries the failed status with a settled
positive charge, the run whose collect.json names it with result_unavailable
holds the same settled charge, and its charge enters the usage-window sum.
A job cancelled before it ran carries no running timestamp and a zero
charge; it needs neither an archive nor a collection and adds nothing to
the window.

The inventory is an observation at observed_at. A raw archive whose run's
submission started at or after that instant names a job the observation
cannot hold; it is listed under awaiting_observation and joins coverage at
the next observation. Every archive of a run submitted earlier must match an
inventory job.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

HISTORICAL_JOBS = {"db5qmqclf4us73c4e1ug", "db67fqsvf2bc73d0pk4g", "db67frimb58s738bci4g"}
# The owner's 180-second campaign cap covers the non-historical jobs created
# before this instant; a later program is bounded by its own approved
# --max-total-execution-seconds and is reported separately.
CAMPAIGN_CEILING_SECONDS = 180
CAMPAIGN_CUTOFF = "2026-10-14T00:00:00Z"


ACCOUNT_RESERVE_SECONDS = 60
FAILED_STATUSES = frozenset({"ERROR", "CANCELLED"})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            checksum.update(block)
    return checksum.hexdigest()


def actor_bytes(path: Path, maximum: int) -> bytes:
    """Bound materialization of each actor receipt input before parsing or projection."""
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    require(len(data) <= maximum, f"actor artifact exceeds its byte limit: {path.name}")
    return data


def actor_charge(value: Any) -> Decimal:
    try:
        charge = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("actor charge is not a finite nonnegative number") from error
    require(charge.is_finite() and charge >= 0, "actor charge is not a finite nonnegative number")
    return charge


BINARY_DIGITS = str.maketrans("", "", "01")


def binary_rows(bits: list[str], width: int) -> bool:
    """Whether every shot string holds exactly width characters, each 0 or 1. Joining and translating the strings
    runs in C, where a regular-expression match per shot dominated the audit's run time."""
    return set(map(len, bits)) == {width} and not "".join(bits).translate(BINARY_DIGITS)


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def timestamp(value: Any) -> datetime:
    require(isinstance(value, str), "usage-window timestamp requires text")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.utcoffset() is not None, "usage-window timestamp requires a timezone")
    return parsed


def window_charge(jobs: list[dict[str, Any]], usage: dict[str, Any]) -> Decimal:
    """Final charges of the jobs that ran inside the account's usage_period.

    A job finished before the period's start contributes nothing. A job that
    started before the start and finished inside the period straddles the
    boundary, and its in-window share is not recorded, so it is refused.
    """
    period = usage.get("usage_period")
    if not isinstance(period, dict):
        raise ValueError("account usage period is missing")
    start, end = timestamp(period.get("start_time")), timestamp(period.get("end_time"))
    require(start < end, "account usage period is reversed or empty")
    total = Decimal(0)
    for job in jobs:
        times = job.get("timestamps")
        if not isinstance(times, dict):
            raise ValueError(f"job timestamps are missing for {job.get('job_id')}")
        if unexecuted(job):
            continue
        running, finished = timestamp(times.get("running")), timestamp(times.get("finished"))
        require(running <= finished <= end, "job execution chronology differs from the account observation")
        if finished < start:
            continue
        require(running >= start, "a job straddles the usage-period start; its in-window charge is not recorded")
        total += Decimal(str(job["final_qpu_charge_seconds"]))
    return total


def unexecuted(job: dict[str, Any]) -> bool:
    """A CANCELLED job with no running timestamp and a zero charge never held the QPU."""
    times = job.get("timestamps") or {}
    return (
        job.get("status") == "CANCELLED"
        and not times.get("running")
        and Decimal(str(job.get("final_qpu_charge_seconds"))) == 0
    )


def campaign_split(rows: list[dict[str, Any]]) -> tuple[Decimal, Decimal, Decimal]:
    """Final charges of the historical jobs, the capped campaign, and later programs."""
    cutoff = timestamp(CAMPAIGN_CUTOFF)
    historical = campaign = later = Decimal(0)
    for row in rows:
        charge = Decimal(str(row["final_qpu_charge_seconds"]))
        if row["job_id"] in HISTORICAL_JOBS:
            historical += charge
        elif timestamp(row["created_at"]) < cutoff:
            campaign += charge
        else:
            later += charge
    return historical, campaign, later


def inventory_family(snapshot_path: Path) -> tuple[Path, list[Path]]:
    """The default inventory file and every per-instance file beside it."""
    match = re.fullmatch(r"(.+?)(?:\.[0-9a-f]{12})?\.json", snapshot_path.name)
    if match is None:
        raise ValueError("inventory filename differs")
    stem = match.group(1)
    default = snapshot_path.parent / f"{stem}.json"
    others = sorted(
        path
        for path in snapshot_path.parent.glob(f"{stem}.*.json")
        if re.fullmatch(r"[0-9a-f]{12}", path.suffixes[0][1:])
    )
    return default, others


def archive_instance(run: Path, default_instance: str) -> str:
    """The instance that owns a run's raw archives: its record's, else the default instance's."""
    record = run / "record.json"
    recorded = read(record).get("instance_sha256_12") if record.is_file() else None
    return recorded if isinstance(recorded, str) else default_instance


def submitted_after(run: Path, observed_at: str) -> bool:
    """Whether run's submission started at or after the inventory observation."""
    record = run / "record.json"
    started = (read(record).get("submission") or {}).get("started") if record.is_file() else None
    return isinstance(started, str) and timestamp(started) >= timestamp(observed_at)


def failed_collections(instance: str, default_instance: str) -> dict[str, Path]:
    """Each run that collected a failed job of the instance, keyed by that job's identity."""
    runs: dict[str, Path] = {}
    for collection in sorted((ROOT / "results/live").glob("*/collect.json")):
        run = collection.parent
        if archive_instance(run, default_instance) != instance:
            continue
        for identity, entry in read(collection)[0].get("jobs", {}).items():
            if "result_unavailable" in entry:
                require(identity not in runs, f"two runs collect failed job {identity}")
                runs[identity] = run
    for record_path in sorted((ROOT / "results/live").glob("*/record.json")):
        run = record_path.parent
        record = read(record_path)
        if record.get("schema_version") != "readout-actor-run-v1" or not record.get("submission", {}).get("jobs"):
            continue
        if archive_instance(run, default_instance) != instance:
            continue
        if not actor_anchor_path(run).is_file():
            continue
        _, actor_result, _ = actor_collection(run)
        for identity, entry in actor_result["jobs"].items():
            if entry.get("status") in FAILED_STATUSES:
                require(identity not in runs, f"two runs collect failed job {identity}")
                runs[identity] = run
    return runs


def actor_anchor_path(run: Path) -> Path:
    return (
        ROOT
        / "docs/evidence/readout-actor-acquisition-review/retention-anchors"
        / f"{digest(run / 'record.json')}.json"
    )


def retention_family(run: Path, *, allow_recovered: bool = False) -> str:
    """Select only known acquisition schemas or the uncollected retrospective archive."""
    record_path = run / "record.json"
    if not record_path.is_file():
        require(
            allow_recovered and not (run / "collect.json").exists() and not (run / "actor-case.json").exists(),
            "run record is missing",
        )
        return "recovered"
    record = read(record_path)
    require(isinstance(record, dict), "run record must be an object")
    schema = record.get("schema_version")
    configuration = record.get("family_configuration")
    family_name = configuration.get("name") if isinstance(configuration, dict) else None
    actor_marker = (run / "actor-case.json").exists() or "reviewed_record_sha256" in record
    if schema == "readout-actor-run-v1" and family_name == "readout-actor":
        return "actor"
    if type(schema) is int and schema in (6, 7) and family_name != "readout-actor" and not actor_marker:
        return "legacy"
    raise ValueError("unsupported or inconsistent retention record schema")


def actor_collection(run: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Read immutable actor anchors outside the analyzed run, independently retained by its operator."""
    record_path = run / "record.json"
    record_sha = digest(record_path)
    anchor_path = actor_anchor_path(run)
    require(anchor_path.is_file(), "actor run lacks an independently retained external retention anchor")
    anchor = read(anchor_path)
    require(
        anchor.get("schema") == "readout-actor-retention-anchor-v1"
        and anchor.get("record_sha256") == record_sha
        and anchor.get("run") == str(run.relative_to(ROOT)),
        "actor retention anchor identity differs",
    )
    collection_sha = anchor.get("collection_sha256")
    require(
        isinstance(collection_sha, str) and bool(re.fullmatch(r"[0-9a-f]{64}", collection_sha)),
        "actor collection anchor is invalid",
    )
    collection_path = run / f"actor-collection-{collection_sha}.json"
    require(collection_path.is_file(), "anchored actor collection is missing")
    require(digest(collection_path) == collection_sha, "actor collection differs from its external anchor")
    record, collection = read(record_path), read(collection_path)
    require(record.get("schema_version") == "readout-actor-run-v1", "unsupported actor acquisition record")
    require(
        collection.get("schema") == "readout-actor-collection-v1"
        and collection.get("record_sha256") == record_sha
        and collection.get("reviewed_record_sha256")
        == record.get("reviewed_record_sha256")
        == anchor.get("reviewed_record_sha256"),
        "actor collection submission binding differs",
    )
    require(
        isinstance(anchor.get("reviewed_record_sha256"), str)
        and bool(re.fullmatch(r"[0-9a-f]{64}", anchor["reviewed_record_sha256"]))
        and type(collection.get("submission_complete")) is bool
        and type(collection.get("all_allocations_retained")) is bool,
        "actor reviewed identity or completeness types differ",
    )
    require(
        record.get("inference")
        == {
            "status": "descriptive",
            "hardware_verdict": None,
            "physical_alignment": "unverified",
            "predecessor_order": "unverified",
        }
        and collection.get("inference") == record.get("inference"),
        "actor inference binding differs",
    )
    require(
        digest(run / "isa.qpy")
        == record.get("qpy_sha256")
        == record["submission"].get("qpy_archive_sha256")
        == collection.get("qpy_sha256"),
        "actor submitted QPY differs",
    )
    submitted = record["submission"]["jobs"]
    require(
        bool(submitted)
        and len({row["job_id"] for row in submitted}) == len(submitted)
        and set(collection["jobs"]) == {row["job_id"] for row in submitted},
        "actor accepted-job coverage differs",
    )
    requested = {row["name"] for row in record["family_configuration"]["case"]["allocations"]}
    submitted_pubs = [pub for row in submitted for pub in row["pubs"]]
    submitted_names = {pub["name"] for pub in submitted_pubs}
    planned = {pub["name"]: pub for pub in record["execution_pubs"]}
    require(
        len(planned) == len(record["execution_pubs"])
        and set(planned) == requested
        and len(submitted_pubs) == len(submitted_names)
        and all(pub == planned.get(pub["name"]) for pub in submitted_pubs),
        "actor submitted PUB manifest differs from the frozen plan",
    )
    observed = [pub["name"] for row in collection["jobs"].values() for pub in row["pubs"]]
    require(
        len(observed) == len(set(observed)) and set(observed) <= submitted_names <= requested,
        "actor retained allocation identities differ",
    )
    complete_submission = bool(record["submission"].get("complete")) and submitted_names == requested
    require(
        collection["submission_complete"] == complete_submission
        and collection["allocations_without_results"] == sorted(requested - set(observed)),
        "actor design-completeness accounting differs",
    )
    complete = (
        complete_submission
        and set(observed) == requested
        and all("collection_error_type" not in row for row in collection["jobs"].values())
    )
    require(collection["all_allocations_retained"] == complete, "actor retention completeness differs")
    sources = {
        str(path.relative_to(ROOT)): digest(path)
        for path in (anchor_path, record_path, collection_path, run / "isa.qpy")
    }
    return record, collection, sources


def actor_pub_evidence(task: tuple[Any, ...]) -> tuple[dict[str, str], set[str]]:
    """Verify one independent PUB against its frozen manifest and indexed evidence."""
    from readout_sparse_receipt import verify_and_project

    position, pub, expected, directory, case, immutable_bytes, archive, shots, root = task
    sources: dict[str, str] = {}
    supplemental: set[str] = set()
    require(
        pub["name"] == expected["name"] and pub["pub_index"] == position,
        "actor retained PUB attribution differs",
    )
    inputs = {}
    for field, prefix, maximum in (
        ("receipt_file", "receipt", 1024 * 1024),
        ("manifest_file", "projection", 4 * 1024 * 1024),
        ("index_file", "index", 4 * 1024 * 1024),
    ):
        name = pub[field]
        require(
            isinstance(name, str) and bool(re.fullmatch(prefix + r"-[0-9a-f]{64}\.json", name)),
            "actor supplemental filename differs",
        )
        path = directory / name
        inputs[field] = actor_bytes(path, maximum)
        checksum = hashlib.sha256(inputs[field]).hexdigest()
        require(checksum == name[len(prefix) + 1 : -5], "actor supplemental digest differs")
        sources[str(path.relative_to(root))] = checksum
        supplemental.add(name)
    index_bytes = inputs["index_file"]
    require(
        index_bytes == immutable_bytes,
        "actor immutable acquisition snapshot differs",
    )
    expected_manifest = {
        "schema": "readout-sparse-projection-v1",
        "condition": expected["name"],
        "pub_name": expected["name"],
        "pub_index": position,
        "registers": {"c": case["width"]},
        "bits": [
            {"register": "c", "index": bit, "logical": bit, "physical": bit, "prepared": value}
            for bit, value in enumerate(expected["prepared_bits"])
        ],
        "pairs": case["pairs"],
        "groups": case["groups"],
    }
    require(
        json.loads(inputs["manifest_file"]) == expected_manifest,
        "actor projection differs from the frozen preparation or mapping",
    )
    projected = verify_and_project(
        actor_bytes(directory / f"pub_{position:02d}.json", 256 * 1024 * 1024),
        index_bytes,
        archive,
        inputs["manifest_file"],
        inputs["receipt_file"],
        pub["receipt_sha256"],
    )
    require(
        projected == pub["result"] and projected["projection"]["num_shots"] == shots,
        "actor sparse projection or shot denominator differs",
    )
    return sources, supplemental


def actor_job_evidence(
    job: dict[str, Any], run: Path, charge: Decimal
) -> tuple[dict[str, Any], dict[str, str], set[str]]:
    """Verify a recorded actor receipt graph without requiring historical source bytes to match today's tree."""
    record, collection, sources = actor_collection(run)
    identity = job["job_id"]
    require(
        isinstance(identity, str)
        and bool(identity)
        and Path(identity).name == identity
        and identity not in (".", ".."),
        "actor job identity is not a local directory name",
    )
    sent = [row for row in record["submission"]["jobs"] if row.get("job_id") == identity]
    require(len(sent) == 1, "actor job is absent or duplicated in the submitted ledger")
    submitted = sent[0]
    require(
        submitted["backend"] == job["backend"]
        and submitted["shots"] == job["shots_per_pub"]
        and len(submitted["pubs"]) == job["pub_count"],
        "actor provider denominator or backend differs",
    )
    entry = collection["jobs"].get(identity)
    require(isinstance(entry, dict) and entry.get("status") == job["status"], "actor collection status differs")
    require(
        entry["usage"].get("job_status") == job["status"]
        and entry["usage"].get("usage_status") == "final"
        and actor_charge(entry["usage"].get("qpu_charge_time_seconds")) == charge,
        "actor settled charge differs",
    )
    supplemental: set[str] = set()
    if job["status"] == "DONE":
        require(len(entry["pubs"]) == job["pub_count"], "actor completed-job PUB retention is incomplete")
        archive = actor_bytes(run / "isa.qpy", 32 * 1024 * 1024)
        directory = run / "raw" / identity
        case = record["family_configuration"]["case"]
        immutable_bytes = actor_bytes(directory / "acquisition-index.json", 4 * 1024 * 1024)
        immutable = json.loads(immutable_bytes)
        expected_files = {"result_metadata.json", *(f"pub_{position:02d}.json" for position in range(job["pub_count"]))}
        require(
            isinstance(immutable, dict)
            and immutable.get("job_id") == identity
            and isinstance(immutable.get("files"), dict)
            and set(immutable["files"]) == expected_files,
            "actor immutable acquisition identity or indexed file set differs",
        )
        for name, checksum in immutable["files"].items():
            require(
                isinstance(checksum, str)
                and bool(re.fullmatch(r"[0-9a-f]{64}", checksum))
                and digest(directory / name) == checksum,
                "actor indexed raw artifact differs",
            )
        tasks = [
            (position, pub, expected, directory, case, immutable_bytes, archive, job["shots_per_pub"], ROOT)
            for position, (pub, expected) in enumerate(zip(entry["pubs"], submitted["pubs"], strict=True))
        ]
        for pub_sources, pub_supplemental in ordered_map(actor_pub_evidence, tasks, min_items=1):
            sources.update(pub_sources)
            supplemental.update(pub_supplemental)
    else:
        require(job["status"] in FAILED_STATUSES and not entry["pubs"], "failed actor job carries invented PUBs")
    return collection, sources, supplemental


def failed_row(job: dict[str, Any], run: Path | None, charge: Decimal) -> dict[str, Any]:
    """The audit row of a failed job, bound to the collection that names it."""
    identity = job["job_id"]
    if run is None:
        raise ValueError(f"failed job {identity} has no collection naming it")
    if retention_family(run) == "actor":
        collection, sources, _ = actor_job_evidence(job, run, charge)
        return {
            **job,
            "run": str(run.relative_to(ROOT)),
            "provenance": "failed_actor_collection",
            "submitted_pub_shots": job["pub_count"] * job["shots_per_pub"],
            "raw_data_files": 0,
            "metrics_snapshots": 0,
            "source_files": sources,
            "design_complete": collection["all_allocations_retained"],
            "result_unavailable": "provider terminal status " + job["status"],
        }
    header = read(run / "collect.json")[0]
    entry = header["jobs"][identity]
    require(header["submission_complete"] is True, "collection is incomplete")
    require(entry["backend"] == job["backend"], "collection backend differs")
    require(
        isinstance(entry["result_unavailable"], str) and bool(entry["result_unavailable"]),
        f"failed job {identity} lacks the reason its result is unavailable",
    )
    require(entry["usage"]["job_status"] == job["status"], f"collection status differs for {identity}")
    require(entry["usage"]["usage_status"] == "final", f"collection usage is unsettled for failed job {identity}")
    require(Decimal(str(entry["usage"]["qpu_charge_time_seconds"])) == charge, "collection charge differs")
    submission = read(run / "record.json")["submission"]
    require(
        any(
            isinstance(sent, dict) and sent.get("job_id") == identity and sent.get("backend") == job["backend"]
            for sent in submission.get("jobs") or []
        ),
        f"failed job {identity} is absent from the jobs its collection's run record submitted",
    )
    require(
        digest(run / "isa.qpy") == submission["qpy_archive_sha256"],
        "isa.qpy differs from the submitted circuit archive",
    )
    return {
        **job,
        "run": str(run.relative_to(ROOT)),
        "provenance": "failed_collection",
        "submitted_pub_shots": job["pub_count"] * job["shots_per_pub"],
        "raw_data_files": 0,
        "metrics_snapshots": 0,
        "source_files": {
            str((run / name).relative_to(ROOT)): digest(run / name)
            for name in ("record.json", "collect.json", "isa.qpy")
        },
    }


def archived_row(task: tuple[dict[str, Any], Path, Decimal]) -> dict[str, Any]:
    """One completed job's audit row after verifying its lossless archive: every indexed raw and metrics digest,
    the settled charge and timestamps, each PUB's order and shot denominator, every register's binary width, and
    the run's collection or retrospective-retention evidence. Archives share no state, so the audit verifies them
    through parallel.ordered_map in inventory order."""
    job, index_path, charge = task
    identity = job["job_id"]
    directory = index_path.parent
    run = directory.parent.parent
    index = read(index_path)
    sources = {str(index_path.relative_to(ROOT)): digest(index_path)}
    actor = retention_family(run, allow_recovered=True) == "actor"
    supplemental: set[str] = set()
    actor_data = None
    if actor:
        actor_data, actor_sources, supplemental = actor_job_evidence(job, run, charge)
        sources.update(actor_sources)
    immutable = directory / "acquisition-index.json"
    if immutable.exists():
        acquisition = read(immutable)
        require(
            acquisition == {"job_id": identity, "files": index["files"]},
            "immutable acquisition index differs from the raw ledger",
        )
        supplemental.add(immutable.name)
        sources[str(immutable.relative_to(ROOT))] = digest(immutable)
    collection_lock = directory / ".collection.lock"
    if collection_lock.exists():
        require(
            not collection_lock.is_symlink() and collection_lock.stat().st_size == 0,
            "collection synchronization file differs",
        )
        supplemental.add(collection_lock.name)
    require("result_metadata.json" in index["files"], "indexed result metadata is missing")
    indexed = set(index["files"]) | set(index["metrics"]) | {"index.json"}
    present = {path.name for path in directory.iterdir() if path.is_file()}
    require(
        present == indexed | supplemental, f"raw files and index differ: {sorted(present ^ (indexed | supplemental))}"
    )
    for name, expected in index["files"].items():
        require(
            name in {"result_metadata.json"} or bool(re.fullmatch(r"pub_[0-9]+\.json", name)),
            "raw filename differs",
        )
        path = directory / name
        require(digest(path) == expected, f"raw data digest differs: {path.name}")
        sources[str(path.relative_to(ROOT))] = expected
    names = index["metrics"]
    hashes = index["metrics_sha256"]
    require(len(names) == len(hashes) and bool(names), "metrics index cardinality differs")
    require(len(set(names)) == len(names), "metrics index repeats a snapshot")
    for name, expected in zip(names, hashes, strict=True):
        require(bool(re.fullmatch(r"job_metrics(?:\.[0-9]+)?\.json", name)), "metrics filename differs")
        path = directory / name
        require(digest(path) == expected, "metrics digest differs")
        sources[str(path.relative_to(ROOT))] = expected
    latest = index.get("metrics_latest")
    if latest is None:
        require(len(names) == 1, "multiple historical metrics require an explicit latest identity")
        latest = names[0]
    require(latest in names, "latest metrics missing from index")
    final_metrics = read(directory / latest)
    require(final_metrics["usage"]["status"] == "complete", "retained usage is unsettled")
    require(Decimal(str(final_metrics["usage"]["qpu_charge_time_seconds"])) == charge, "retained charge differs")
    for stage in ("running", "finished"):
        require(
            timestamp(job["timestamps"][stage]) == timestamp(final_metrics["timestamps"][stage]),
            f"inventory {stage} timestamp differs from the retained final metrics",
        )
    pub_paths = sorted(directory.glob("pub_*.json"), key=lambda path: int(path.stem.split("_")[1]))
    require(len(pub_paths) == job["pub_count"], "decoded service PUB count differs from raw count")
    require(job["shots_per_pub"] > 0 and job["pub_count"] > 0, "empty physical acquisition")
    for pub_number, path in enumerate(pub_paths):
        require(path.name in index["files"], "unindexed raw PUB")
        pub = read(path)
        require(pub["pub_index"] == pub_number, "PUB order differs")
        require(bool(pub["registers"]), "PUB registers missing")
        for register in pub["registers"].values():
            bits = register["bitstrings"]
            require(register["num_shots"] == job["shots_per_pub"] == len(bits), "shot denominator differs")
            width = register["num_bits"]
            require(width > 0 and binary_rows(bits, width), "register width or binary data differs")
    collection = run / "collect.json"
    if actor:
        evidence_names = []
        provenance = "registered_actor_collection"
    elif collection.exists():
        header = read(collection)[0]
        entry = header["jobs"][identity]
        require(header["submission_complete"] is True, "collection is incomplete")
        require(entry["backend"] == job["backend"], "collection backend differs")
        require(entry["usage"]["usage_status"] == "final", "collection usage is unsettled")
        require(Decimal(str(entry["usage"]["qpu_charge_time_seconds"])) == charge, "collection charge differs")
        # Newer collections carry the raw ledger in collect.json; the pilot
        # preserved its ledger in raw/preserved.json, which then must exist
        # and joins the audit's source files.
        if "raw" in entry:
            ledger = entry["raw"]
        else:
            preserved = run / "raw/preserved.json"
            require(preserved.exists(), "collection without an inline raw ledger lacks raw/preserved.json")
            ledger = read(preserved)["jobs"][identity]
            sources[str(preserved.relative_to(ROOT))] = digest(preserved)
        require(
            ledger["directory"] == str(directory.relative_to(run)) and ledger["files"] == index["files"],
            "collection raw ledger differs from the retained index",
        )
        submitted = read(run / "record.json")["submission"]["qpy_archive_sha256"]
        require(digest(run / "isa.qpy") == submitted, "isa.qpy differs from the submitted circuit archive")
        evidence_names = ["record.json", "collect.json", "isa.qpy"]
        provenance = "registered_collection"
    else:
        retention = read(run / "retention.json")
        require(
            retention["job_id"] == identity and retention["backend"] == job["backend"], "retention identity differs"
        )
        require(retention["final_qpu_charge_seconds"] == job["final_qpu_charge_seconds"], "retention charge differs")
        submitted = read(run / "submitted-input.json")
        require(
            digest(run / "submitted-circuits.qpy") == submitted["circuit_archive_sha256"],
            "recovered QPY digest differs",
        )
        evidence_names = ["retention.json", "submitted-input.json", "submitted-circuits.qpy"]
        provenance = "retrospective_descriptive"
    for name in evidence_names:
        path = run / name
        sources[str(path.relative_to(ROOT))] = digest(path)
    return {
        **job,
        "run": str(run.relative_to(ROOT)),
        "provenance": provenance,
        "submitted_pub_shots": job["pub_count"] * job["shots_per_pub"],
        "raw_data_files": len(index["files"]),
        "metrics_snapshots": len(names),
        "source_files": sources,
        **({"design_complete": actor_data["all_allocations_retained"]} if actor_data is not None else {}),
    }


def failure_summary(rows: list[dict[str, Any]]) -> tuple[int, Decimal]:
    """Count settled failures from both supported collection families."""
    failures = [row for row in rows if row["provenance"] in {"failed_collection", "failed_actor_collection"}]
    return len(failures), sum((Decimal(str(row["final_qpu_charge_seconds"])) for row in failures), Decimal(0))


def reconcile(snapshot_path: Path) -> dict[str, Any]:
    default_path, other_paths = inventory_family(snapshot_path)
    snapshot = read(snapshot_path)
    require(snapshot["schema"] == "completed-qpu-job-inventory-v1", "inventory schema differs")
    require(snapshot["complete_service_inventory"] is True, "inventory observation is partial")
    require(snapshot["new_qpu_submissions"] == 0, "inventory contains submissions")
    require(bool(re.fullmatch(r"[0-9a-f]{12}", snapshot["instance_crn_hash"])), "instance hash differs")
    instance = snapshot["instance_crn_hash"]
    default_instance = instance if snapshot_path == default_path else read(default_path)["instance_crn_hash"]
    is_default = instance == default_instance
    require(is_default == (snapshot_path == default_path), "inventory file name and instance hash differ")
    known = {default_instance}
    for path in other_paths:
        other = read(path)["instance_crn_hash"]
        require(path.name.split(".")[-2] == other, "inventory file name and instance hash differ")
        require(other not in known, "two inventory files record one instance")
        known.add(other)
    usage = snapshot["account_usage"]
    quota = [usage.get(key) for key in ("usage_limit_seconds", "usage_consumed_seconds", "usage_remaining_seconds")]
    require(all(type(value) is int and value >= 0 for value in quota), "account usage fields are not whole seconds")
    limit, consumed, remaining = quota
    require(consumed + remaining == limit, "account usage consumed and remaining seconds do not sum to the limit")
    require(remaining >= ACCOUNT_RESERVE_SECONDS, "account remaining seconds fall below the retained reserve")
    jobs = snapshot["jobs"]
    identities = [job["job_id"] for job in jobs]
    require(len(identities) == len(set(identities)), "duplicate service job identity")
    archives: dict[str, Path] = {}
    awaiting: list[str] = []
    for index_path in sorted((ROOT / "results/live").glob("*/raw/*/index.json")):
        index = read(index_path)
        identity = index["job_id"]
        require(identity == index_path.parent.name, "raw directory and job identity differ")
        require(identity not in archives, "duplicate raw archive for a physical job")
        owner = archive_instance(index_path.parent.parent.parent, default_instance)
        require(owner in known, f"raw archive {identity} belongs to an instance without an inventory file: {owner}")
        if owner != instance:
            continue
        run = index_path.parent.parent.parent
        if identity not in identities and submitted_after(run, snapshot["observed_at"]):
            awaiting.append(str(index_path.parent.relative_to(ROOT)))
            continue
        archives[identity] = index_path
    statuses = {job["job_id"]: job["status"] for job in jobs}
    unfinished = sorted(key for key, value in statuses.items() if value != "DONE" and value not in FAILED_STATUSES)
    require(not unfinished, f"unfinished service jobs: {unfinished}")
    completed = {identity for identity, status in statuses.items() if status == "DONE"}
    require(set(archives) == completed, "service jobs and retained archive identities differ")
    collections = failed_collections(instance, default_instance)
    require(not is_default or HISTORICAL_JOBS <= set(identities), "historical accounting identities missing")
    rows: list[dict[str, Any]] = []
    tasks: list[tuple[int, tuple[dict[str, Any], Path, Decimal]]] = []
    for job in jobs:
        identity = job["job_id"]
        if unexecuted(job):
            rows.append(
                {
                    **job,
                    "run": None,
                    "provenance": "unexecuted_cancellation",
                    "submitted_pub_shots": job["pub_count"] * job["shots_per_pub"],
                    "raw_data_files": 0,
                    "metrics_snapshots": 0,
                    "source_files": {},
                }
            )
            continue
        require(job["usage_status"] == "complete", f"unsettled job {identity}")
        charge = Decimal(str(job["final_qpu_charge_seconds"]))
        if job["status"] in FAILED_STATUSES:
            # A system-error failure bills zero, so a finalized failed job admits a zero charge.
            require(charge.is_finite() and charge >= 0, f"physical charge missing for {identity}")
            rows.append(failed_row(job, collections.get(identity), charge))
            continue
        require(charge.is_finite() and charge > 0, f"physical charge missing for {identity}")
        tasks.append((len(rows), (job, archives[identity], charge)))
        rows.append({})
    for (position, _), row in zip(tasks, ordered_map(archived_row, [task for _, task in tasks]), strict=True):
        rows[position] = row
    total = sum(Decimal(str(row["final_qpu_charge_seconds"])) for row in rows)
    in_window = window_charge(rows, usage)
    require(in_window == Decimal(consumed), "final charges inside the usage period differ from the consumed seconds")
    if is_default:
        historical, campaign, later = campaign_split(rows)
    else:
        historical, campaign, later = Decimal(0), Decimal(0), Decimal(total)
    require(campaign <= CAMPAIGN_CEILING_SECONDS, "new campaign exceeds authorized 180-second ceiling")
    failed_count, failed_charge = failure_summary(rows)
    payload = {
        "schema": "qpu-job-retention-audit-v1",
        "observed_at": snapshot["observed_at"],
        "inventory_sha256": digest(snapshot_path),
        "replay_source_sha256": digest(Path(__file__)),
        "scope": (
            "All completed jobs in the retained service inventory have lossless raw archives, and every "
            "failed job's settled charge is bound to the collection that records why it returned no result. "
            "Offline replay establishes retained coverage at the observation time; "
            "subsequent live jobs require a fresh inventory."
        ),
        "job_count": len(rows),
        "acquisition_count": len({row["run"] for row in rows if row["run"] is not None}),
        "pub_count": sum(row["pub_count"] for row in rows),
        "submitted_pub_shots": sum(row["submitted_pub_shots"] for row in rows),
        "indexed_raw_data_files": sum(row["raw_data_files"] for row in rows),
        "indexed_metrics_snapshots": sum(row["metrics_snapshots"] for row in rows),
        "final_charge_seconds": str(total),
        "historical_charge_seconds": str(historical),
        "new_campaign_charge_seconds": str(campaign),
        "new_campaign_ceiling_seconds": CAMPAIGN_CEILING_SECONDS,
        "new_campaign_cutoff": CAMPAIGN_CUTOFF,
        "unallocated_campaign_seconds": str(Decimal(CAMPAIGN_CEILING_SECONDS) - campaign),
        "later_program_charge_seconds": str(later),
        "account_reserve_seconds": ACCOUNT_RESERVE_SECONDS,
        "usage_window_charge_seconds": str(in_window),
        "account_usage_observation": snapshot["account_usage"],
        "awaiting_observation": sorted(awaiting),
        "failed_job_count": failed_count,
        "failed_charge_seconds": str(failed_charge),
        "jobs": rows,
    }
    if not is_default:
        payload["instance_crn_hash"] = instance
    return payload


def audit_path(snapshot_path: Path) -> Path:
    """The retention audit that pairs with an inventory file."""
    return snapshot_path.with_name(snapshot_path.name.replace("qpu-job-inventory", "qpu-job-retention-audit"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot", type=Path, help="one inventory file; default every inventory file beside the default one"
    )
    parser.add_argument("--out", type=Path, help="audit path for --snapshot; default pairs with the inventory name")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--actor-run", type=Path, help="verify externally anchored sparse actor retention before inventory"
    )
    parser.add_argument("--retention-preflight", type=Path, help="route a run to its required retention evidence")
    arguments = parser.parse_args()
    try:
        if arguments.retention_preflight is not None:
            require(
                arguments.actor_run is None
                and arguments.snapshot is None
                and arguments.out is None
                and not arguments.check,
                "retention preflight is a separate offline verification mode",
            )
            run = arguments.retention_preflight.resolve()
            if retention_family(run) == "actor":
                arguments.actor_run = run
            else:
                require((run / "collect.json").is_file(), "run has no collected evidence")
                print("Legacy collection exists; inventory verification remains separate")
                return 0
        if arguments.actor_run is not None:
            require(
                arguments.snapshot is None and arguments.out is None and not arguments.check,
                "--actor-run is a separate offline verification mode",
            )
            run = arguments.actor_run.resolve()
            record, collection, _ = actor_collection(run)
            for entry in record["submission"]["jobs"]:
                identity = entry["job_id"]
                retained = collection["jobs"][identity]
                require(retained.get("status") in {"DONE", *FAILED_STATUSES}, "actor job remains unfinished")
                charge = actor_charge(retained["usage"].get("qpu_charge_time_seconds"))
                job = {
                    "job_id": identity,
                    "backend": entry["backend"],
                    "shots_per_pub": entry["shots"],
                    "pub_count": len(entry["pubs"]),
                    "status": retained["status"],
                }
                if retained["status"] == "DONE":
                    index_path = run / "raw" / identity / "index.json"
                    index = read(index_path)
                    names = index["metrics"]
                    require(isinstance(names, list) and bool(names), "actor metrics index is empty")
                    latest = index.get("metrics_latest")
                    if latest is None:
                        require(len(names) == 1, "actor metrics lack a latest identity")
                        latest = names[0]
                    require(
                        latest in names
                        and isinstance(latest, str)
                        and bool(re.fullmatch(r"job_metrics(?:\.[0-9]+)?\.json", latest)),
                        "actor latest metrics identity differs",
                    )
                    job["timestamps"] = read(index_path.parent / latest)["timestamps"]
                    archived_row((job, index_path, charge))
                else:
                    actor_job_evidence(job, run, charge)
            print("Externally anchored actor retention verified; inventory observation remains separate")
            return 0
        if arguments.snapshot is not None:
            snapshots = [arguments.snapshot]
        else:
            default, others = inventory_family(ROOT / "results/live/qpu-job-inventory.json")
            snapshots = [default, *others]
        require(arguments.out is None or len(snapshots) == 1, "--out requires --snapshot")
        for snapshot_path in snapshots:
            out = arguments.out or audit_path(snapshot_path)
            payload = json.dumps(reconcile(snapshot_path), indent=2, sort_keys=True) + "\n"
            if arguments.check:
                require(out.read_text() == payload, "retention audit differs from offline replay")
            else:
                for index_path in (ROOT / "results/live").glob("*/raw/*/index.json"):
                    require(
                        not out.resolve().is_relative_to(index_path.parents[2]),
                        "inventory output must stay outside every immutable run archive",
                    )
                with out.open("x") as stream:
                    stream.write(payload)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"QPU inventory audit failed: {error}\n")
    print("QPU inventory and every raw shot denominator verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
