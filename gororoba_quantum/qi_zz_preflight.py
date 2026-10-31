"""Analyze retained QX preflight acquisitions of a ZZ-map design against their reviewed plan.

Record reading and the rules every Quantum Inspire consumer shares come from
qi_records. A Design names what the experiment itself requires: the plan
schema and sanity policy it was reviewed under, the backend, the shot count
and the marginal criteria that judge one circuit's counts. analyze holds
every batch of the plan to the design and reports per circuit; an
acquisition that fails a design condition is named and never read under
another design's assumptions, and a plan without circuits is rejected
rather than passed empty. The entry point that binds a design and parses
arguments lives in scripts/ (scripts/qi_zz_map_qx_analysis.py for the
Tuna-17 ZZ map).
"""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import qi_records
from parallel import ordered_map
from qi_records import require

ANALYSIS_SCHEMA = "qi-zz-map-qx-preflight-analysis-v2"


@dataclass(frozen=True)
class Design:
    """The reviewed experiment's own conditions; check_counts(row, counts, shots) lists a circuit's failures."""

    plan_schema: str
    policy: dict[str, Any]
    backend: str
    shots: int
    check_counts: Callable[[dict[str, Any], Counter[str], int], list[str]]
    sources: dict[str, Path]


def read_batch(task: dict[str, Any]) -> dict[str, Any]:
    """Read one batch directory through qi_records, hold it to the design's record conditions, return counts."""
    batch = task["batch"]
    directory = Path(task["runs_root"]) / batch["directory"]
    record = qi_records.load_run(directory)
    require(record["cases_sha256"] == batch["cases_sha256"], "QX manifest differs from reviewed plan")
    acquisition = qi_records.validate_run(record, f"QX batch {batch['directory']}")
    require(acquisition.schema == "qi-submission-v2", "QX preflight requires a digest-bound v2 receipt")
    require(
        acquisition.backend == task["backend"] and acquisition.backend_type_id == task["backend_type_id"],
        "wrong backend",
    )
    require(acquisition.shots == task["shots"], "QX denominator differs from preflight")
    rows = task["rows"]
    expected = [{k: v for k, v in row.items() if k != "batch_directory"} for row in rows]
    require(record["cases"]["circuits"] == expected, "QX circuit roles differ from plan")
    require(acquisition.completed, f"QX job incomplete: {dict(acquisition.statuses)}")
    by_file = {job.file: job for job in acquisition.jobs}
    require(set(by_file) == {row["file"] for row in rows}, "QX acquisition file set mismatch")
    counts = []
    for row in rows:
        job = by_file[row["file"]]
        require(job.raw is not None, "QX raw output was not retained")
        counts.append({"file": row["file"], "job": job.job_id, "counts": dict(Counter(job.raw))})
    return {
        "counts": counts,
        "input_sha256": {f"{batch['directory']}/{name}": value for name, value in record["digests"].items()},
    }


def analyze(plan_path: Path, runs_root: Path, design: Design) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    require(
        plan["schema"] == design.plan_schema and plan["sanity_policy"] == design.policy,
        "unrecognized QX plan or criteria",
    )
    circuits = plan["circuits"]
    batches = plan["batches"]
    directories = [batch["directory"] for batch in batches]
    require(
        circuits and batches and plan["cost"]["total_jobs"] == len(circuits) and len(set(directories)) == len(batches),
        "empty or inconsistent preflight design",
    )
    require({row["batch_directory"] for row in circuits} == set(directories), "circuits name batches the plan lacks")
    tasks = [
        {
            "runs_root": str(runs_root),
            "batch": batch,
            "backend": design.backend,
            "backend_type_id": plan["backend_type_id"],
            "shots": design.shots,
            "rows": [row for row in circuits if row["batch_directory"] == batch["directory"]],
        }
        for batch in batches
    ]
    results = ordered_map(read_batch, tasks)
    rows = {row["file"]: row for row in circuits}
    checked = [
        {
            "file": entry["file"],
            "job": entry["job"],
            "failures": design.check_counts(rows[entry["file"]], Counter(entry["counts"]), design.shots),
        }
        for result in results
        for entry in result["counts"]
    ]
    require(
        len(checked) == len(circuits) and len({row["job"] for row in checked}) == len(circuits),
        "missing or reused QX acquisition",
    )
    return {
        "schema": ANALYSIS_SCHEMA,
        "plan_sha256": qi_records.digest(plan_bytes),
        "source_digests": {name: qi_records.digest(path.read_bytes()) for name, path in design.sources.items()},
        "sanity_policy": design.policy,
        "passes": all(not row["failures"] for row in checked),
        "circuits": checked,
        "input_sha256": {k: v for result in results for k, v in result["input_sha256"].items()},
        "scope": "QX ideal native-gate/wiring sanity only; no physical ZZ or hardware timing validation",
    }


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def synthetic_case(
    root: Path, design: Design, *, histogram: dict[str, int] | None = None, status: str = "completed"
) -> tuple[Path, Path]:
    """Write a one-batch, one-circuit plan and its acquisition under root; return (plan path, runs root).

    The circuit is a two-wire Y-quadrature conditional Ramsey row: the neighbor
    q1 reads 1 and the probe q0 splits evenly, so the ideal histogram is half
    `10` and half `11`. A failed job holds no result and no raw file.
    """
    shots = design.shots
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
    cases = {"backend": design.backend, "backend_type_id": 1, "shots": shots, "circuits": [row]}
    cases_text = _json_text(cases)
    (directory / "cases.json").write_text(cases_text, encoding="utf-8")
    receipt = {
        "schema": "qi-submission-v2",
        "state": "enqueued",
        "approval": "synthetic fixture",
        "batch_job": "synthetic-batch",
        "backend": design.backend,
        "backend_type_id": 1,
        "shots": shots,
        "cases_sha256": qi_records.digest(cases_text.encode()),
        "jobs": [{"file": name, "job": "synthetic-job", "sha256": row["sha256"]}],
    }
    (directory / "submission.json").write_text(_json_text(receipt), encoding="utf-8")
    job = {
        "id": "synthetic-job",
        "batch_job_id": "synthetic-batch",
        "created_on": "2026-01-01T00:00:00Z",
        "number_of_shots": shots,
        "status": status,
        "raw_data_enabled": True,
    }
    results = []
    if status == "completed":
        if histogram is None:
            histogram = {"10": shots // 2, "11": shots - shots // 2}
        results = [{"job_id": job["id"], "shots_requested": shots, "shots_done": shots, "results": histogram}]
        raw = [key for key, count in histogram.items() for _ in range(count)]
        (directory / "raw" / f"{name}.json").write_text(_json_text(raw), encoding="utf-8")
    collected = {
        "schema": "qi-collection-v1",
        "transactions": [],
        "jobs": [{"file": name, "job": job, "results": results}],
    }
    (directory / "results.json").write_text(_json_text(collected), encoding="utf-8")
    plan = {
        "schema": design.plan_schema,
        "backend": design.backend,
        "backend_type_id": 1,
        "shots": shots,
        "cost": {"total_jobs": 1},
        "sanity_policy": design.policy,
        "circuits": [{**row, "batch_directory": "batch-000"}],
        "batches": [{"directory": "batch-000", "cases_sha256": receipt["cases_sha256"]}],
    }
    plan_path = root / "plan.json"
    plan_path.write_text(_json_text(plan), encoding="utf-8")
    return plan_path, runs_root


def _rejects(plan_path: Path, runs_root: Path, design: Design, text: str) -> None:
    try:
        analyze(plan_path, runs_root, design)
    except ValueError as error:
        require(text in str(error), f"rejected for another reason: {error}")
    else:
        raise AssertionError(f"accepted an acquisition that should fail with {text!r}")


def self_test(design: Design) -> None:
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        plan_path, runs_root = synthetic_case(root / "a", design)
        verdict = analyze(plan_path, runs_root, design)
        require(verdict["passes"] and verdict["circuits"][0]["failures"] == [], "ideal fixture rejected")
        plan_b, runs_b = synthetic_case(root / "b", design)
        require(
            analyze(plan_b, runs_b, design)["circuits"] == verdict["circuits"], "relocated fixture read differently"
        )
        raw_path = runs_root / "batch-000/raw/fixture.cq.json"
        raw_path.write_text(_json_text(["11"] * design.shots), encoding="utf-8")
        _rejects(plan_path, runs_root, design, "outcome histogram")
        failed_plan, failed_runs = synthetic_case(root / "c", design, status="failed")
        require(qi_records.read_run(failed_runs / "batch-000").completed is False, "failed job read as completed")
        _rejects(failed_plan, failed_runs, design, "QX job incomplete")
        roles_plan, roles_runs = synthetic_case(root / "d", design)
        plan = json.loads(roles_plan.read_bytes())
        plan["circuits"][0]["quadrature"] = "x"
        roles_plan.write_text(_json_text(plan), encoding="utf-8")
        _rejects(roles_plan, roles_runs, design, "circuit roles differ")
        empty_plan, _ = synthetic_case(root / "e", design)
        plan = json.loads(empty_plan.read_bytes())
        plan.update(circuits=[], batches=[], cost={"total_jobs": 0})
        empty_plan.write_text(_json_text(plan), encoding="utf-8")
        _rejects(empty_plan, root / "absent", design, "empty or inconsistent preflight design")
        biased_plan, biased_runs = synthetic_case(root / "f", design, histogram={"11": design.shots})
        require(
            not analyze(biased_plan, biased_runs, design)["passes"],
            "a Y probe pinned to one outcome passed the familywise bound",
        )
    print("QX ZZ preflight analysis: reader rules, design conditions, empty-design guard and relocation pass")
