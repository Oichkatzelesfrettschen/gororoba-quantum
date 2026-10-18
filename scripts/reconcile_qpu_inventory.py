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
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORICAL_JOBS = {"db5qmqclf4us73c4e1ug", "db67fqsvf2bc73d0pk4g", "db67frimb58s738bci4g"}
# The owner's 180-second campaign cap covers the non-historical jobs created
# before this instant; a later program is bounded by its own approved
# --max-total-execution-seconds and is reported separately.
CAMPAIGN_CEILING_SECONDS = 180
CAMPAIGN_CUTOFF = "2026-10-14T00:00:00Z"


ACCOUNT_RESERVE_SECONDS = 60


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        running, finished = timestamp(times.get("running")), timestamp(times.get("finished"))
        require(running <= finished <= end, "job execution chronology differs from the account observation")
        if finished < start:
            continue
        require(running >= start, "a job straddles the usage-period start; its in-window charge is not recorded")
        total += Decimal(str(job["final_qpu_charge_seconds"]))
    return total


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
    for index_path in sorted((ROOT / "results/live").glob("*/raw/*/index.json")):
        index = read(index_path)
        identity = index["job_id"]
        require(identity == index_path.parent.name, "raw directory and job identity differ")
        require(identity not in archives, "duplicate raw archive for a physical job")
        owner = archive_instance(index_path.parent.parent.parent, default_instance)
        require(owner in known, f"raw archive {identity} belongs to an instance without an inventory file: {owner}")
        if owner == instance:
            archives[identity] = index_path
    require(set(archives) == set(identities), "service jobs and retained archive identities differ")
    require(not is_default or HISTORICAL_JOBS <= set(identities), "historical accounting identities missing")
    rows = []
    for job in jobs:
        identity = job["job_id"]
        require(job["status"] == "DONE" and job["usage_status"] == "complete", f"unsettled job {identity}")
        charge = Decimal(str(job["final_qpu_charge_seconds"]))
        require(charge.is_finite() and charge > 0, f"physical charge missing for {identity}")
        index_path = archives[identity]
        directory = index_path.parent
        run = directory.parent.parent
        index = read(index_path)
        sources = {str(index_path.relative_to(ROOT)): digest(index_path)}
        require("result_metadata.json" in index["files"], "indexed result metadata is missing")
        indexed = set(index["files"]) | set(index["metrics"]) | {"index.json"}
        present = {path.name for path in directory.iterdir() if path.is_file()}
        require(present == indexed, f"raw files and index differ: {sorted(present ^ indexed)}")
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
                require(
                    width > 0 and all(re.fullmatch(r"[01]+", value) and len(value) == width for value in bits),
                    "register width or binary data differs",
                )
        collection = run / "collect.json"
        if collection.exists():
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
            require(
                retention["final_qpu_charge_seconds"] == job["final_qpu_charge_seconds"], "retention charge differs"
            )
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
        rows.append(
            {
                **job,
                "run": str(run.relative_to(ROOT)),
                "provenance": provenance,
                "submitted_pub_shots": job["pub_count"] * job["shots_per_pub"],
                "raw_data_files": len(index["files"]),
                "metrics_snapshots": len(names),
                "source_files": sources,
            }
        )
    total = sum(Decimal(str(row["final_qpu_charge_seconds"])) for row in rows)
    in_window = window_charge(rows, usage)
    require(in_window == Decimal(consumed), "final charges inside the usage period differ from the consumed seconds")
    if is_default:
        historical, campaign, later = campaign_split(rows)
    else:
        historical, campaign, later = Decimal(0), Decimal(0), Decimal(total)
    require(campaign <= CAMPAIGN_CEILING_SECONDS, "new campaign exceeds authorized 180-second ceiling")
    payload = {
        "schema": "qpu-job-retention-audit-v1",
        "observed_at": snapshot["observed_at"],
        "inventory_sha256": digest(snapshot_path),
        "replay_source_sha256": digest(Path(__file__)),
        "scope": (
            "All jobs in the retained service inventory have lossless raw archives. "
            "Offline replay establishes retained coverage at the observation time; "
            "subsequent live jobs require a fresh inventory."
        ),
        "job_count": len(rows),
        "acquisition_count": len({row["run"] for row in rows}),
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
    arguments = parser.parse_args()
    try:
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
