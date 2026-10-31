"""Analyze retained QX preflight acquisitions of the Tuna-17 ZZ map against their reviewed plan.

The retained plan binds scripts/qi_zz_map_qx.py byte for byte through
qx_builder_sha256, so that module stays the pinned producer of the proposal
and this module succeeds its --analyze mode. Record reading and the rules
every Quantum Inspire consumer shares (receipt binding, circuit digests, job
identities, raw shots against the histogram) come from
gororoba_quantum/qi_records.py. This module keeps the design's own
conditions: the reviewed plan's batches and circuit roles, the QX backend
and shot count, completed digest-bound v2 receipts, and the fixed marginal
criteria of qi_zz_map_qx.check_counts. An acquisition that fails a design
condition is reported by name and never read under another design's
assumptions.

Usage: "$PYTHON" scripts/qi_zz_map_qx_analysis.py --plan PLAN --runs RUNS_ROOT --out NEWFILE
       "$PYTHON" scripts/qi_zz_map_qx_analysis.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_zz_map import json_text  # noqa: E402
from qi_zz_map_qx import PLAN_SCHEMA, POLICY, SHOTS, check_counts  # noqa: E402

import qi_records  # noqa: E402
from parallel import ordered_map  # noqa: E402
from qi_records import require  # noqa: E402

ANALYSIS_SCHEMA = "qi-zz-map-qx-preflight-analysis-v2"
BACKEND = "QXsinglenodesimulator"
SOURCES = {
    "analyzer": Path(__file__),
    "reader": ROOT / "gororoba_quantum/qi_records.py",
    "criteria": ROOT / "scripts/qi_zz_map_qx.py",
}


def read_batch(task: dict[str, Any]) -> dict[str, Any]:
    """Read one batch directory through qi_records, then hold it to the plan's design conditions."""
    batch = task["batch"]
    directory = Path(task["runs_root"]) / batch["directory"]
    record = qi_records.load_run(directory)
    require(record["cases_sha256"] == batch["cases_sha256"], "QX manifest differs from reviewed plan")
    acquisition = qi_records.validate_run(record, f"QX batch {batch['directory']}")
    require(acquisition.schema == "qi-submission-v2", "QX preflight requires a digest-bound v2 receipt")
    require(
        acquisition.backend == BACKEND and acquisition.backend_type_id == task["backend_type_id"],
        "wrong backend",
    )
    require(acquisition.shots == SHOTS, "QX denominator differs from preflight")
    rows = task["rows"]
    expected = [{k: v for k, v in row.items() if k != "batch_directory"} for row in rows]
    require(record["cases"]["circuits"] == expected, "QX circuit roles differ from plan")
    require(acquisition.completed, f"QX job incomplete: {dict(acquisition.statuses)}")
    by_file = {job.file: job for job in acquisition.jobs}
    require(set(by_file) == {row["file"] for row in rows}, "QX acquisition file set mismatch")
    checked = []
    for row in rows:
        job = by_file[row["file"]]
        require(job.raw is not None, "QX raw output was not retained")
        failures = check_counts(row, Counter(job.raw), SHOTS)
        checked.append({"file": row["file"], "job": job.job_id, "failures": failures})
    return {
        "circuits": checked,
        "input_sha256": {f"{batch['directory']}/{name}": value for name, value in record["digests"].items()},
    }


def analyze(plan_path: Path, runs_root: Path) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    require(plan["schema"] == PLAN_SCHEMA and plan["sanity_policy"] == POLICY, "unrecognized QX plan or criteria")
    tasks = [
        {
            "runs_root": str(runs_root),
            "batch": batch,
            "backend_type_id": plan["backend_type_id"],
            "rows": [row for row in plan["circuits"] if row["batch_directory"] == batch["directory"]],
        }
        for batch in plan["batches"]
    ]
    results = ordered_map(read_batch, tasks)
    checked = [row for result in results for row in result["circuits"]]
    expected_jobs = plan["cost"]["total_jobs"]
    require(
        len(checked) == expected_jobs and len({row["job"] for row in checked}) == expected_jobs,
        "missing or reused QX acquisition",
    )
    return {
        "schema": ANALYSIS_SCHEMA,
        "plan_sha256": qi_records.digest(plan_bytes),
        "source_digests": {name: qi_records.digest(path.read_bytes()) for name, path in SOURCES.items()},
        "sanity_policy": POLICY,
        "passes": all(not row["failures"] for row in checked),
        "circuits": checked,
        "input_sha256": {k: v for result in results for k, v in result["input_sha256"].items()},
        "scope": "QX ideal native-gate/wiring sanity only; no physical ZZ or hardware timing validation",
    }


def synthetic_case(
    root: Path, *, histogram: dict[str, int] | None = None, status: str = "completed"
) -> tuple[Path, Path]:
    """Write a one-batch, one-circuit plan and its acquisition under root; return (plan path, runs root).

    The circuit is a two-wire Y-quadrature conditional Ramsey row: the neighbor
    q1 reads 1 and the probe q0 splits evenly, so the ideal histogram is half
    `10` and half `11`. A failed job holds no result and no raw file.
    """
    runs_root = root / "runs"
    directory = runs_root / "batch-000"
    (directory / "raw").mkdir(parents=True)
    name = "fixture.cq"
    code = (
        "version 3.0\nqubit[2] q\nbit[2] b\ninit q\nbarrier q\n"
        "X90 q[0]\nmY90 q[1]\nwait(25) q\nbarrier q\nb = measure q\n"
    )
    (directory / name).write_text(code, encoding="utf-8")
    row = {
        "kind": "conditional_ramsey",
        "quadrature": "y",
        "nqubits": 2,
        "pairs": [{"edge": [0, 1], "probe": 0, "neighbor": 1, "neighbor_state": 1}],
        "file": name,
        "sha256": qi_records.digest(code.encode()),
    }
    cases = {"backend": BACKEND, "backend_type_id": 1, "shots": SHOTS, "circuits": [row]}
    cases_text = json_text(cases)
    (directory / "cases.json").write_text(cases_text, encoding="utf-8")
    receipt = {
        "schema": "qi-submission-v2",
        "state": "enqueued",
        "approval": "synthetic fixture",
        "batch_job": "synthetic-batch",
        "backend": BACKEND,
        "backend_type_id": 1,
        "shots": SHOTS,
        "cases_sha256": qi_records.digest(cases_text.encode()),
        "jobs": [{"file": name, "job": "synthetic-job", "sha256": row["sha256"]}],
    }
    (directory / "submission.json").write_text(json_text(receipt), encoding="utf-8")
    job = {
        "id": "synthetic-job",
        "batch_job_id": "synthetic-batch",
        "created_on": "2026-01-01T00:00:00Z",
        "number_of_shots": SHOTS,
        "status": status,
        "raw_data_enabled": True,
    }
    results = []
    if status == "completed":
        if histogram is None:
            histogram = {"10": SHOTS // 2, "11": SHOTS - SHOTS // 2}
        results = [{"job_id": job["id"], "shots_requested": SHOTS, "shots_done": SHOTS, "results": histogram}]
        shots = [key for key, count in histogram.items() for _ in range(count)]
        (directory / "raw" / f"{name}.json").write_text(json_text(shots), encoding="utf-8")
    collected = {
        "schema": "qi-collection-v1",
        "transactions": [],
        "jobs": [{"file": name, "job": job, "results": results}],
    }
    (directory / "results.json").write_text(json_text(collected), encoding="utf-8")
    plan = {
        "schema": PLAN_SCHEMA,
        "backend": BACKEND,
        "backend_type_id": 1,
        "shots": SHOTS,
        "cost": {"total_jobs": 1},
        "sanity_policy": POLICY,
        "circuits": [{**row, "batch_directory": "batch-000"}],
        "batches": [{"directory": "batch-000", "cases_sha256": receipt["cases_sha256"]}],
    }
    plan_path = root / "plan.json"
    plan_path.write_text(json_text(plan), encoding="utf-8")
    return plan_path, runs_root


def _rejects(plan_path: Path, runs_root: Path, text: str) -> None:
    try:
        analyze(plan_path, runs_root)
    except ValueError as error:
        require(text in str(error), f"rejected for another reason: {error}")
    else:
        raise AssertionError(f"accepted an acquisition that should fail with {text!r}")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        plan_path, runs_root = synthetic_case(root / "a")
        verdict = analyze(plan_path, runs_root)
        require(verdict["passes"] and verdict["circuits"][0]["failures"] == [], "ideal fixture rejected")
        plan_b, runs_b = synthetic_case(root / "b")
        require(analyze(plan_b, runs_b)["circuits"] == verdict["circuits"], "relocated fixture read differently")
        raw_path = runs_root / "batch-000/raw/fixture.cq.json"
        raw_path.write_text(json_text(["11"] * SHOTS), encoding="utf-8")
        _rejects(plan_path, runs_root, "outcome histogram")
        failed_plan, failed_runs = synthetic_case(root / "c", status="failed")
        require(qi_records.read_run(failed_runs / "batch-000").completed is False, "failed job read as completed")
        _rejects(failed_plan, failed_runs, "QX job incomplete")
        roles_plan, roles_runs = synthetic_case(root / "d")
        plan = json.loads(roles_plan.read_bytes())
        plan["circuits"][0]["quadrature"] = "x"
        roles_plan.write_text(json_text(plan), encoding="utf-8")
        _rejects(roles_plan, roles_runs, "circuit roles differ")
        biased_plan, biased_runs = synthetic_case(root / "e", histogram={"11": SHOTS})
        require(
            not analyze(biased_plan, biased_runs)["passes"],
            "a Y probe pinned to one outcome passed the familywise bound",
        )
    print("QX ZZ preflight analysis: reader rules, design conditions and relocation independence pass")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--runs", type=Path, metavar="RUNS_ROOT")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.plan is None or args.out is None:
        parser.error("--runs requires --plan PLAN and --out NEWFILE")
    text = json_text(analyze(args.plan, args.runs))
    with args.out.open("x", encoding="utf-8") as handle:
        handle.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
