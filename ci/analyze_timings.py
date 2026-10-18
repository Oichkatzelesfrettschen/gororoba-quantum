"""Decompose a GitHub jobs response and run log into reproducible CI timing evidence.

Fetch inputs with gh api .../actions/runs/RUN/jobs --paginate and
 gh run view RUN --log. Gate elapsed time overlaps across subprocesses;
runner step time and workflow elapsed time have separate denominators.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

VERDICT = re.compile(r"\b(PASS|FAIL) ([\w-]+)\s+([\d.]+)s\s")


def seconds(start: str, end: str) -> float:
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()


def analyze(
    jobs: list[dict[str, Any]], log: str, manifest: dict[str, Any], run: dict[str, Any] | None = None
) -> dict[str, Any]:
    estimates = {gate["name"]: gate["seconds"] for gate in manifest["gates"]}
    records = []
    for line in log.splitlines():
        match = VERDICT.search(line)
        if match:
            records.append(
                {
                    "job": line.split("\t", 1)[0],
                    "name": match[2],
                    "status": match[1],
                    "seconds": float(match[3]),
                    "estimated_seconds": estimates.get(match[2]),
                }
            )
    stages: dict[str, float] = defaultdict(float)
    runners = []
    for job in jobs:
        if job["conclusion"] == "skipped" or not job.get("completed_at"):
            continue
        for step in job["steps"]:
            if step.get("started_at") and step.get("completed_at"):
                stages[step["name"]] += seconds(step["started_at"], step["completed_at"])
        runners.append(
            {
                "name": job["name"],
                "conclusion": job["conclusion"],
                "wall_seconds": seconds(job["started_at"], job["completed_at"]),
            }
        )
    first_job = min(job["created_at"] for job in jobs)
    last_job = max(job["completed_at"] for job in jobs if job.get("completed_at"))
    created = run["created_at"] if run else first_job
    return {
        "run": {key: run[key] for key in ("id", "event", "head_sha", "created_at", "run_started_at")} if run else None,
        "created_to_first_job_seconds": seconds(created, first_job),
        "job_span_seconds": seconds(first_job, last_job),
        "schema": "gororoba-ci-analysis-v1",
        "workflow_seconds": seconds(created, last_job),
        "runner_seconds": sum(job["wall_seconds"] for job in runners),
        "stage_runner_seconds": dict(sorted(stages.items())),
        "gate_elapsed_seconds": sum(row["seconds"] for row in records),
        "runners": runners,
        "gates": sorted(records, key=lambda row: (-row["seconds"], row["job"], row["name"])),
    }


def refresh(manifest: dict[str, Any], reports: list[dict[str, Any]]) -> None:
    """Use primary gate-lane samples; the alternate QI interpreter has its own cost."""
    samples: dict[str, list[float]] = defaultdict(list)
    for report in reports:
        for row in report["gates"]:
            if row["job"].startswith("gates ") and row["status"] == "PASS":
                samples[row["name"]].append(row["seconds"])
    for gate in manifest["gates"]:
        if gate["name"] in samples:
            gate["seconds"] = round(statistics.median(samples[gate["name"]]), 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--run", type=Path, help="GitHub run API response, including time before jobs were created")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("gates.json"))
    parser.add_argument(
        "--refresh-estimates", action="store_true", help="update gate seconds from this successful sample"
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    report = analyze(
        json.loads(args.jobs.read_text())["jobs"],
        args.log.read_text(),
        manifest,
        json.loads(args.run.read_text()) if args.run else None,
    )
    report["run_id"] = args.run_id
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    if args.refresh_estimates:
        refresh(manifest, [report])
        args.manifest.write_text(json.dumps(manifest, indent=1) + "\n")
    print(
        f"workflow {report['workflow_seconds']:.1f}s; runners {report['runner_seconds']:.1f}s; "
        f"overlapping gate elapsed {report['gate_elapsed_seconds']:.1f}s"
    )


if __name__ == "__main__":
    main()
