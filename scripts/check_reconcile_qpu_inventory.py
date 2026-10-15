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
        "a repeated metrics snapshot and raw corruption rejected; the campaign cutoff splits charges; "
        "replay preserves bytes"
    )


if __name__ == "__main__":
    main()
