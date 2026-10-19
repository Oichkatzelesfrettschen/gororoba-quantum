"""Falsify inventory coverage and raw-denominator checks with synthetic archives."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import reconcile_qpu_inventory as audit


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def second_instance_contract(
    audit: Any, root: Path, source: Path, snapshot: dict[str, Any], times: dict[str, str]
) -> None:
    """A second instance's archive needs its own inventory file and reconciles against its own quota."""
    other = "b" * 12
    run = root / "results/live/synthetic-backup"
    raw = run / "raw/backup-job"
    raw.mkdir(parents=True)
    write(
        raw / "pub_00.json",
        {"pub_index": 0, "registers": {"c": {"num_bits": 1, "num_shots": 2, "bitstrings": ["0", "1"]}}},
    )
    write(raw / "result_metadata.json", {})
    write(
        raw / "job_metrics.json", {"usage": {"status": "complete", "qpu_charge_time_seconds": 2}, "timestamps": times}
    )
    write(
        raw / "index.json",
        {
            "job_id": "backup-job",
            "files": {name: audit.digest(raw / name) for name in ("pub_00.json", "result_metadata.json")},
            "metrics": ["job_metrics.json"],
            "metrics_sha256": [audit.digest(raw / "job_metrics.json")],
        },
    )
    write(run / "record.json", {"instance_sha256_12": other})
    write(
        run / "retention.json", {"job_id": "backup-job", "backend": "synthetic-backend", "final_qpu_charge_seconds": 2}
    )
    (run / "submitted-circuits.qpy").write_bytes(b"synthetic backup fixture bytes")
    write(run / "submitted-input.json", {"circuit_archive_sha256": audit.digest(run / "submitted-circuits.qpy")})
    backup = copy.deepcopy(snapshot)
    backup["instance_crn_hash"] = other
    backup["account_usage"] |= {"usage_consumed_seconds": 2, "usage_remaining_seconds": 598}
    backup["jobs"][0] |= {"job_id": "backup-job", "final_qpu_charge_seconds": 2, "shots_per_pub": 2}
    backup_path = source.with_name(f"inventory.{other}.json")
    try:
        audit.reconcile(source)
    except ValueError:
        pass
    else:
        raise RuntimeError("a backup archive without its inventory file was admitted")
    write(backup_path, backup)
    primary_audit = audit.reconcile(source)
    backup_audit = audit.reconcile(backup_path)
    audit.require(primary_audit["job_count"] == 1 and "instance_crn_hash" not in primary_audit, "default audit differs")
    audit.require(
        backup_audit["job_count"] == 1
        and backup_audit["instance_crn_hash"] == other
        and backup_audit["usage_window_charge_seconds"] == "2",
        "backup audit differs",
    )
    audit.require(audit.audit_path(backup_path).name == f"inventory.{other}.json", "audit path pairing differs")
    for mutate in (
        lambda value: value.update(instance_crn_hash="c" * 12),
        lambda value: value["account_usage"].update(usage_consumed_seconds=1, usage_remaining_seconds=599),
        lambda value: value["account_usage"].update(usage_consumed_seconds=545, usage_remaining_seconds=55),
    ):
        mutant = copy.deepcopy(backup)
        mutate(mutant)
        write(backup_path, mutant)
        try:
            audit.reconcile(backup_path)
        except ValueError:
            pass
        else:
            raise RuntimeError("a mutated backup inventory was admitted")
    duplicate = copy.deepcopy(backup)
    duplicate["instance_crn_hash"] = snapshot["instance_crn_hash"]
    write(backup_path, duplicate)
    try:
        audit.reconcile(source)
    except ValueError:
        pass
    else:
        raise RuntimeError("two inventory files for one instance were admitted")
    write(backup_path, backup)


def failed_job_contract(audit: Any, root: Path, source: Path, snapshot: dict[str, Any]) -> None:
    """A failed job binds its settled charge to the collection that names it and keeps no raw archive."""
    run = root / "results/live/synthetic-failed"
    run.mkdir(parents=True)
    (run / "isa.qpy").write_bytes(b"synthetic failed-job circuit bytes")
    write(run / "record.json", {"submission": {"qpy_archive_sha256": audit.digest(run / "isa.qpy")}})
    times = {"running": "2026-10-12T01:00:00Z", "finished": "2026-10-12T01:00:03Z"}
    entry = {
        "backend": "synthetic-backend",
        "usage": {"job_status": "ERROR", "usage_status": "final", "qpu_charge_time_seconds": 3},
        "result_unavailable": "RuntimeJobMaxTimeoutError: ran longer than the maximum execution time",
    }
    collection: list[Any] = [{"submission_complete": True, "jobs": {"failed-job": entry}}]
    write(run / "collect.json", collection)
    failed = copy.deepcopy(snapshot)
    failed["account_usage"] |= {"usage_consumed_seconds": 4, "usage_remaining_seconds": 596}
    failed["jobs"].append(
        snapshot["jobs"][0]
        | {"job_id": "failed-job", "status": "ERROR", "final_qpu_charge_seconds": 3, "timestamps": times}
    )
    write(source, failed)
    result = audit.reconcile(source)
    audit.require(
        result["failed_job_count"] == 1 and result["failed_charge_seconds"] == "3" and result["job_count"] == 2,
        "failed-job audit differs",
    )
    inventory_mutants: list[tuple[Any, str]] = [
        (lambda value: value["jobs"][1].update(usage_status="pending"), "unsettled job failed-job"),
        (lambda value: value["jobs"][1].update(final_qpu_charge_seconds=0), "collection charge differs"),
        (lambda value: value["jobs"][1].update(final_qpu_charge_seconds=-1), "physical charge missing"),
        (lambda value: value["jobs"][1].update(status="RUNNING"), "unfinished service jobs"),
        (lambda value: value["jobs"][1].update(status="CANCELLED"), "collection status differs"),
        (
            lambda value: value["account_usage"].update(usage_consumed_seconds=1, usage_remaining_seconds=599),
            "differ from the consumed seconds",
        ),
    ]
    for mutate, reason in inventory_mutants:
        mutant = copy.deepcopy(failed)
        mutate(mutant)
        write(source, mutant)
        rejects(audit, source, reason)
    zero = copy.deepcopy(failed)
    zero["account_usage"] |= {"usage_consumed_seconds": 1, "usage_remaining_seconds": 599}
    zero["jobs"][1]["final_qpu_charge_seconds"] = 0
    zero_collection = copy.deepcopy(collection)
    zero_collection[0]["jobs"]["failed-job"]["usage"]["qpu_charge_time_seconds"] = 0
    write(source, zero)
    write(run / "collect.json", zero_collection)
    result = audit.reconcile(source)
    audit.require(
        result["failed_job_count"] == 1 and result["failed_charge_seconds"] == "0",
        "a finalized zero-charge ERROR job is refused",
    )
    write(run / "collect.json", collection)
    write(source, failed)
    collection_mutants: list[tuple[Any, str]] = [
        (lambda value: value["jobs"]["failed-job"].pop("result_unavailable"), "has no collection naming it"),
        (lambda value: value["jobs"]["failed-job"].update(result_unavailable=""), "lacks the reason"),
        (lambda value: value["jobs"]["failed-job"]["usage"].update(usage_status="pending"), "usage is unsettled"),
        (lambda value: value["jobs"]["failed-job"]["usage"].update(job_status="DONE"), "collection status differs"),
        (lambda value: value["jobs"]["failed-job"]["usage"].update(qpu_charge_time_seconds=2), "charge differs"),
        (lambda value: value["jobs"]["failed-job"].update(backend="other-backend"), "backend differs"),
        (lambda value: value.update(submission_complete=False), "collection is incomplete"),
    ]
    for mutate, reason in collection_mutants:
        broken = copy.deepcopy(collection)
        mutate(broken[0])
        write(run / "collect.json", broken)
        rejects(audit, source, reason)
    write(run / "collect.json", collection)
    (run / "isa.qpy").write_bytes(b"altered failed-job circuit bytes")
    rejects(audit, source, "isa.qpy differs")
    (run / "isa.qpy").write_bytes(b"synthetic failed-job circuit bytes")
    twin = root / "results/live/synthetic-failed-twin"
    twin.mkdir()
    write(twin / "collect.json", collection)
    rejects(audit, source, "two runs collect failed job")
    (twin / "collect.json").unlink()
    twin.rmdir()
    raw = run / "raw/failed-job"
    raw.mkdir(parents=True)
    write(raw / "index.json", {"job_id": "failed-job", "files": {}, "metrics": [], "metrics_sha256": []})
    rejects(audit, source, "retained archive identities differ")
    (raw / "index.json").unlink()
    raw.rmdir()
    (run / "collect.json").unlink()
    rejects(audit, source, "has no collection naming it")
    write(run / "collect.json", collection)
    write(source, snapshot)
    (run / "collect.json").unlink()


def awaiting_observation_contract(audit: Any, root: Path, source: Path, snapshot: dict[str, Any]) -> None:
    """An archive submitted after the observation awaits it; one submitted before must be inventoried."""
    run = root / "results/live/synthetic-later"
    raw = run / "raw/later-job"
    raw.mkdir(parents=True)
    write(raw / "index.json", {"job_id": "later-job", "files": {}, "metrics": [], "metrics_sha256": []})
    observed = copy.deepcopy(snapshot)
    observed["observed_at"] = "2026-10-12T12:00:00+00:00"
    write(source, observed)
    write(run / "record.json", {"submission": {"started": "2026-10-12T12:00:00+00:00"}})
    result = audit.reconcile(source)
    audit.require(
        result["awaiting_observation"] == ["results/live/synthetic-later/raw/later-job"] and result["job_count"] == 1,
        "an archive submitted after the observation is not declared awaiting",
    )
    write(run / "record.json", {"submission": {"started": "2026-10-12T11:59:59+00:00"}})
    rejects(audit, source, "retained archive identities differ")
    (run / "record.json").unlink()
    rejects(audit, source, "retained archive identities differ")
    (raw / "index.json").unlink()
    raw.rmdir()
    write(source, snapshot)


def unexecuted_cancellation_contract(audit: Any, source: Path, snapshot: dict[str, Any]) -> None:
    """A zero-charge CANCELLED job without a running timestamp needs no archive; any execution trace refuses."""
    cancelled = copy.deepcopy(snapshot)
    cancelled["jobs"].append(
        snapshot["jobs"][0]
        | {
            "job_id": "cancelled-job",
            "status": "CANCELLED",
            "usage_status": None,
            "final_qpu_charge_seconds": 0,
            "timestamps": {"created": "2026-10-12T02:00:00Z"},
        }
    )
    write(source, cancelled)
    result = audit.reconcile(source)
    audit.require(
        result["job_count"] == 2 and result["usage_window_charge_seconds"] == "1",
        "an unexecuted cancellation changed the audit",
    )
    for mutate, reason in (
        (lambda value: value.update(final_qpu_charge_seconds=1), "unsettled job cancelled-job"),
        (lambda value: value["timestamps"].update(running="2026-10-12T02:00:01Z"), "unsettled job cancelled-job"),
        (lambda value: value.update(status="ERROR"), "unsettled job cancelled-job"),
    ):
        mutant = copy.deepcopy(cancelled)
        mutate(mutant["jobs"][1])
        write(source, mutant)
        rejects(audit, source, reason)
    write(source, snapshot)


def rejects(audit: Any, source: Path, reason: str) -> None:
    """reconcile refuses source with a message naming reason, so a mutant fails for the intended rule."""
    try:
        audit.reconcile(source)
    except ValueError as error:
        audit.require(reason in str(error), f"refused for {error!r}, not {reason!r}")
        return
    raise RuntimeError(f"a mutant expected to fail with {reason!r} was admitted")


def main() -> None:
    with TemporaryDirectory(prefix="qpu-inventory-contract-") as temporary:
        root = Path(temporary)
        run = root / "results/live/synthetic-retention"
        raw = run / "raw/synthetic-job"
        raw.mkdir(parents=True)
        pub = {"pub_index": 0, "registers": {"c": {"num_bits": 2, "num_shots": 2, "bitstrings": ["00", "11"]}}}
        write(raw / "pub_00.json", pub)
        write(raw / "result_metadata.json", {})
        times = {"running": "2026-10-12T00:00:00Z", "finished": "2026-10-12T00:00:01Z"}
        metrics = {"usage": {"status": "complete", "qpu_charge_time_seconds": 1}, "timestamps": times}
        write(raw / "job_metrics.json", metrics)
        index: dict[str, Any] = {
            "job_id": "synthetic-job",
            "files": {name: audit.digest(raw / name) for name in ("pub_00.json", "result_metadata.json")},
            "metrics": ["job_metrics.json"],
            "metrics_sha256": [audit.digest(raw / "job_metrics.json")],
        }
        write(raw / "index.json", index)
        write(
            run / "retention.json",
            {"job_id": "synthetic-job", "backend": "synthetic-backend", "final_qpu_charge_seconds": 1},
        )
        (run / "submitted-circuits.qpy").write_bytes(b"synthetic fixture bytes; circuit replay is separate")
        write(run / "submitted-input.json", {"circuit_archive_sha256": audit.digest(run / "submitted-circuits.qpy")})
        snapshot: dict[str, Any] = {
            "schema": "completed-qpu-job-inventory-v1",
            "complete_service_inventory": True,
            "new_qpu_submissions": 0,
            "instance_crn_hash": "a" * 12,
            "observed_at": "synthetic",
            "account_usage": {
                "usage_limit_seconds": 600,
                "usage_consumed_seconds": 1,
                "usage_remaining_seconds": 599,
                "usage_period": {"start_time": "2026-09-15T00:00:00Z", "end_time": "2026-10-13T00:00:00Z"},
            },
            "jobs": [
                {
                    "job_id": "synthetic-job",
                    "status": "DONE",
                    "usage_status": "complete",
                    "backend": "synthetic-backend",
                    "final_qpu_charge_seconds": 1,
                    "pub_count": 1,
                    "shots_per_pub": 2,
                    "timestamps": dict(times),
                    "created_at": "2026-10-12T00:00:00Z",
                }
            ],
        }
        source = root / "inventory.json"
        write(source, snapshot)
        with patch.object(audit, "ROOT", root), patch.object(audit, "HISTORICAL_JOBS", {"synthetic-job"}):
            baseline = audit.reconcile(source)
            audit.require(baseline["job_count"] == 1 and baseline["submitted_pub_shots"] == 2, "fixture failed")
            before = {
                str(path.relative_to(run)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in run.rglob("*")
                if path.is_file()
            }
            mutants = []
            for field, value in (
                ("status", "RUNNING"),
                ("usage_status", "pending"),
                ("final_qpu_charge_seconds", 0),
                ("final_qpu_charge_seconds", 2),
                ("pub_count", 2),
                ("shots_per_pub", 3),
                ("backend", "other-backend"),
            ):
                mutant = copy.deepcopy(snapshot)
                mutant["jobs"][0][field] = value
                mutants.append(mutant)
            row_variants: list[list[dict[str, Any]]] = [[], snapshot["jobs"] * 2]
            for rows in row_variants:
                mutant = copy.deepcopy(snapshot)
                mutant["jobs"] = rows
                mutants.append(mutant)
            mutant = copy.deepcopy(snapshot)
            mutant["complete_service_inventory"] = False
            mutants.append(mutant)
            for usage in (
                {},
                {"usage_limit_seconds": 600, "usage_consumed_seconds": 1, "usage_remaining_seconds": 600},
                {"usage_limit_seconds": 600, "usage_consumed_seconds": 550, "usage_remaining_seconds": 50},
                {"usage_limit_seconds": 600, "usage_consumed_seconds": 1.5, "usage_remaining_seconds": 598.5},
                {"usage_limit_seconds": 600, "usage_consumed_seconds": 2, "usage_remaining_seconds": 598},
            ):
                mutant = copy.deepcopy(snapshot)
                mutant["account_usage"] = usage | {"usage_period": snapshot["account_usage"]["usage_period"]}
                mutants.append(mutant)
            mutant = copy.deepcopy(snapshot)
            del mutant["account_usage"]["usage_period"]
            mutants.append(mutant)
            # Chronology: straddling the period start, finishing after the observation,
            # an expired job against nonzero consumption, and a timestamp off the metrics.
            for running, finished in (
                ("2026-09-14T00:00:00Z", "2026-09-16T00:00:00Z"),
                ("2026-10-14T00:00:00Z", "2026-10-14T00:00:01Z"),
                ("2026-09-14T00:00:00Z", "2026-09-14T00:00:01Z"),
                ("2026-10-12T00:00:00Z", "2026-10-12T00:00:02Z"),
            ):
                mutant = copy.deepcopy(snapshot)
                mutant["jobs"][0]["timestamps"] = {"running": running, "finished": finished}
                mutants.append(mutant)
            for number, mutant in enumerate(mutants):
                write(source, mutant)
                try:
                    audit.reconcile(source)
                except ValueError:
                    pass
                else:
                    raise RuntimeError(f"inventory mutant {number} admitted")
            write(source, snapshot)
            usage = snapshot["account_usage"]
            audit.require(audit.window_charge(snapshot["jobs"], usage) == 1, "in-window charge differs")
            split_rows = [
                {"job_id": "synthetic-job", "final_qpu_charge_seconds": 1, "created_at": "2026-10-12T00:00:00Z"},
                {"job_id": "campaign", "final_qpu_charge_seconds": 170, "created_at": "2026-10-13T23:59:59Z"},
                {"job_id": "later", "final_qpu_charge_seconds": 146, "created_at": "2026-10-14T00:00:00Z"},
            ]
            audit.require(audit.campaign_split(split_rows) == (1, 170, 146), "campaign cutoff split differs")
            expired = copy.deepcopy(snapshot["jobs"][0])
            expired["timestamps"] = {"running": "2026-09-14T00:00:00Z", "finished": "2026-09-14T00:00:01Z"}
            audit.require(audit.window_charge([expired], usage) == 0, "an expired job contributes a rolling charge")
            for running, finished in (
                ("2026-10-12T00:00:01Z", "2026-10-12T00:00:00Z"),
                ("2026-10-12T00:00:00", "2026-10-12T00:00:01Z"),
            ):
                invalid = copy.deepcopy(snapshot["jobs"][0])
                invalid["timestamps"] = {"running": running, "finished": finished}
                try:
                    audit.window_charge([invalid], usage)
                except ValueError:
                    pass
                else:
                    raise RuntimeError("an invalid usage-window chronology was admitted")
            after = {
                str(path.relative_to(run)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in run.rglob("*")
                if path.is_file()
            }
            audit.require(before == after, "replay altered retained inputs")
            second_instance_contract(audit, root, source, snapshot, times)
            failed_job_contract(audit, root, source, snapshot)
            awaiting_observation_contract(audit, root, source, snapshot)
            unexecuted_cancellation_contract(audit, source, snapshot)
            duplicated = copy.deepcopy(index)
            duplicated["metrics"] = ["job_metrics.json", "job_metrics.json"]
            duplicated["metrics_sha256"] = [index["metrics_sha256"][0]] * 2
            duplicated["metrics_latest"] = "job_metrics.json"
            write(raw / "index.json", duplicated)
            try:
                audit.reconcile(source)
            except ValueError:
                pass
            else:
                raise RuntimeError("a repeated metrics snapshot was admitted")
            write(raw / "index.json", index)
            (raw / "pub_00.json").write_bytes(b"corrupted raw fixture")
            try:
                audit.reconcile(source)
            except ValueError:
                pass
            else:
                raise RuntimeError("raw digest mutation admitted")
    print(
        "Synthetic inventory contract: 20 inventory mutations, two window chronology mutations, "
        "a repeated metrics snapshot and raw corruption rejected; a failed job, zero-charge ERROR included, "
        "binds its settled charge to its collection under 17 mutations, each refused by its own rule; "
        "an archive submitted after the "
        "observation awaits it; a zero-charge unexecuted cancellation passes and three execution traces refuse; "
        "the campaign cutoff splits charges; "
        "replay preserves bytes"
    )


if __name__ == "__main__":
    main()
