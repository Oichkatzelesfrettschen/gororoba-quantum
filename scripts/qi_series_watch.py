"""One line per change of a Quantum Inspire BDSC Pauli case series, with timing and stop metrics.

Reads the run directories of SERIES under results/quantum_inspire/runs and the live job records
(read-only GETs) every --interval seconds, and prints:

- each job's status change, with its queue wait (queued_at - created_on: the platform sets queued_at
  when the job starts executing) and its run time (finished_at - queued_at);
- each collected batch: per-job execution_time_in_seconds and shots_done from results.json, the pause
  its series-gate.json records, the idle gap between the previous batch's last finish and this batch's
  creation, and the stop metrics over every collected batch (worst P(1|0) and P(0|1) of a patch qubit
  across the references, the largest bracket drift, and whether a stop fired);
- the backend's status and the all-users queue length when they change.

A failed read prints one line and the watch continues.

Usage: "$QI_PYTHON" scripts/qi_series_watch.py SERIES [--interval SECONDS]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qi_bdsc_pauli_cases  # noqa: E402
import qi_platform  # noqa: E402


def stamp(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text)


def say(line: str) -> None:
    print(f"{datetime.datetime.now(datetime.UTC):%H:%M:%SZ} {line}", flush=True)


def worst_rates(report: dict[str, Any]) -> dict[str, tuple[str, float]]:
    """The largest P(1|0) and P(0|1) over every patch qubit of every loaded reference."""
    worst: dict[str, tuple[str, float]] = {}
    for row in report["instances"]:
        for kind in ("e01", "e10"):
            for qubit, rate in row[kind].items():
                if rate > worst.get(kind, ("", -1.0))[1]:
                    worst[kind] = (str(qubit), rate)
    return worst


class Watch:
    def __init__(self, series: str, runs: Path) -> None:
        self.series = series
        self.runs = runs
        self.client = qi_platform.Client()
        self.jobs: dict[str, str] = {}
        self.collected: set[str] = set()
        self.backend: tuple[str, int] | None = None

    def job_line(self, key: str, job: dict[str, Any]) -> str:
        line = f"{key} job {job['id']} {job['status']}"
        if job.get("queued_at"):
            line += f" waited {(stamp(job['queued_at']) - stamp(job['created_on'])).total_seconds():.0f} s"
        if job.get("queued_at") and job.get("finished_at"):
            line += f" ran {(stamp(job['finished_at']) - stamp(job['queued_at'])).total_seconds():.1f} s"
        return line

    def batch_line(self, batch: str, run_dir: Path, done: list[Path], previous: datetime.datetime | None) -> str:
        results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
        gate_path = run_dir / "series-gate.json"
        gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
        created = min(stamp(row["job"]["created_on"]) for row in results["jobs"])
        gap = f"{(created - previous).total_seconds():.0f} s" if previous else "n/a"
        runs = "; ".join(
            f"{row['file']} {row['results'][0]['execution_time_in_seconds']:.1f} s/{row['results'][0]['shots_done']}"
            if row["results"]
            else f"{row['file']} {row['job']['status']}"
            for row in results["jobs"]
        )
        cases, raw, _ = qi_bdsc_pauli_cases.load_series(done)
        report = qi_bdsc_pauli_cases.reference_report(cases, raw)
        worst = worst_rates(report)
        drift = report["bracket_drift"]
        fired = bool(report["stop_condition_batch_00"]) or bool(drift["flagged"])
        rates = ", ".join(f"worst {kind} q{q} {rate:.4f}" for kind, (q, rate) in sorted(worst.items()))
        return (
            f"{batch} collected: {runs}; pause {gate.get('pause_seconds', 'not recorded')} s, idle gap {gap}; "
            f"{rates}; max drift {drift['max_abs_delta']:.4f} (stop {drift['threshold']}); "
            f"stops {'FIRED' if fired else 'clear'}"
        )

    def poll(self) -> None:
        dirs = sorted(self.runs.glob(f"*-{self.series}-batch-*"))
        previous: datetime.datetime | None = None
        backend_id = None
        for run_dir in dirs:
            batch = "batch-" + run_dir.name.rsplit("-", 1)[-1]
            submission = run_dir / "submission.json"
            if not submission.exists():
                continue
            record = json.loads(submission.read_text(encoding="utf-8"))
            backend_id = record["backend_type_id"]
            for row in record["jobs"]:
                job = self.client.get(f"/jobs/{row['job']}")
                key = f"{batch}/{row['file']}"
                if self.jobs.get(key) != job["status"]:
                    self.jobs[key] = job["status"]
                    say(self.job_line(key, job))
            if not (run_dir / "results.json").exists():
                continue
            if batch not in self.collected:
                done = [d for d in dirs if (d / "results.json").exists()]
                say(self.batch_line(batch, run_dir, done, previous))
                # A read that fails leaves the batch unmarked, so the next poll reports it again.
                self.collected.add(batch)
            results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
            finished = [stamp(row["job"]["finished_at"]) for row in results["jobs"] if row["job"]["finished_at"]]
            previous = max(finished) if finished else previous
        if backend_id is not None:
            status = self.client.get(f"/backend_types/{backend_id}")["status"]
            queued = self.client.get(f"/backend_types/{backend_id}/queue")["number_of_jobs_in_queue"]
            if (status, queued) != self.backend:
                self.backend = (status, queued)
                say(f"backend type {backend_id} {status}, all-users queue {queued}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("series", help="series name, the case directory under results/quantum_inspire/cases")
    parser.add_argument("--interval", type=float, default=30.0)
    parser.add_argument("--runs", type=Path, default=ROOT / "results/quantum_inspire/runs")
    args = parser.parse_args()
    watch = Watch(args.series, args.runs)
    while True:
        try:
            watch.poll()
        except (OSError, ValueError, KeyError, qi_platform.PlatformError) as error:
            say(f"read failed: {error!r}")
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
