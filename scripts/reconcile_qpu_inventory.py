"""Verify a retained service inventory against every lossless job archive.

The service snapshot records a bounded read-only observation. Offline replay
checks archive coverage and identities; it cannot refresh live account state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORICAL_JOBS = {"db5qmqclf4us73c4e1ug", "db67fqsvf2bc73d0pk4g", "db67frimb58s738bci4g"}


ACCOUNT_RESERVE_SECONDS = 60


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def reconcile(snapshot_path: Path) -> dict[str, Any]:
    snapshot = read(snapshot_path)
    require(snapshot["schema"] == "completed-qpu-job-inventory-v1", "inventory schema differs")
    require(snapshot["complete_service_inventory"] is True, "inventory observation is partial")
    require(snapshot["new_qpu_submissions"] == 0, "inventory contains submissions")
    require(bool(re.fullmatch(r"[0-9a-f]{12}", snapshot["instance_crn_hash"])), "instance hash differs")
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
        archives[identity] = index_path
    require(set(archives) == set(identities), "service jobs and retained archive identities differ")
    require(HISTORICAL_JOBS <= set(identities), "historical accounting identities missing")
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
    require(total == Decimal(consumed), "summed final job charges differ from the account's consumed seconds")
    historical = sum(Decimal(str(row["final_qpu_charge_seconds"])) for row in rows if row["job_id"] in HISTORICAL_JOBS)
    campaign = total - historical
    require(campaign <= 180, "new campaign exceeds authorized 180-second ceiling")
    return {
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
        "new_campaign_ceiling_seconds": 180,
        "unallocated_campaign_seconds": str(Decimal(180) - campaign),
        "account_reserve_seconds": ACCOUNT_RESERVE_SECONDS,
        "account_usage_observation": snapshot["account_usage"],
        "jobs": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=ROOT / "results/live/qpu-job-inventory.json")
    parser.add_argument("--out", type=Path, default=ROOT / "results/live/qpu-job-retention-audit.json")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        payload = json.dumps(reconcile(arguments.snapshot), indent=2, sort_keys=True) + "\n"
        if arguments.check:
            require(arguments.out.read_text() == payload, "retention audit differs from offline replay")
        else:
            for index_path in (ROOT / "results/live").glob("*/raw/*/index.json"):
                require(
                    not arguments.out.resolve().is_relative_to(index_path.parents[2]),
                    "inventory output must stay outside every immutable run archive",
                )
            with arguments.out.open("x") as stream:
                stream.write(payload)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"QPU inventory audit failed: {error}\n")
    print("QPU inventory and every raw shot denominator verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
