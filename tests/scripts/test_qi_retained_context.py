"""Contract for scripts/qi_retained_context.py on a two-qubit record and three retained jobs built in a temporary
tree: every figure keeps its run's instant, days group by job creation, and an unfinished job is left out.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import qi_retained_context as retained

RUN_A = "results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17"
RUN_B = "results/quantum_inspire/runs/2026-10-17T032034Z-readout_ringdown_tuna_17_P-batch-00"


def job(created: str, finished: str | None, seconds: float, status: str = "completed") -> dict[str, Any]:
    body = {"created_on": created, "finished_at": finished, "number_of_shots": 1024, "status": status}
    return {"file": "x.cq", "job": body, "results": [{"execution_time_in_seconds": seconds}]}


def tree(root: Path) -> None:
    context = {
        "profile": "tuna_17",
        "coupler_map": {"runs": ["results/quantum_inspire/runs/2026-10-16T224924Z-coupler_zz_tuna_17-batch-00"]},
        "qubits": {
            "10": {"coupler_map": None, "readout": {"runs": [], "implied_t1": None}},
            "2": {
                "coupler_map": {
                    "omega_hz": 18478.123456,
                    "omega_se_hz": 1452.0,
                    "visibility_delays_us": [0.5, 2.0],
                    "visibility_zero_sector": [0.9741234, 0.755],
                    "max_abs_j_hz": 7902.75,
                    "couplers": [{}, {}],
                },  # fmt: skip
                "readout": {
                    "runs": [
                        {
                            "run": RUN_A,
                            "shots": 16384,
                            "wait_before_readout_us": 0.0,
                            "p1_given_0": 0.0161743,
                            "p1_given_1": 0.970398,
                        },
                        {
                            "run": RUN_B,
                            "shots": 16384,
                            "wait_before_readout_us": 2.0,
                            "p1_given_0": 0.02,
                            "p1_given_1": 0.84,
                        },
                    ],
                    "implied_t1": {"us": 14.18471234, "wait_us": 2.0, "wait_run": RUN_B, "no_wait_run": RUN_A},
                },
            },
        },
    }
    target = root / retained.CONTEXT
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(context), encoding="utf-8")
    run = root / RUN_A
    run.mkdir(parents=True)
    (run / "cases.json").write_text(json.dumps({"backend": "tuna_17"}), encoding="utf-8")
    rows = [
        job("2026-10-16T22:11:40Z", "2026-10-16T22:11:52.500000Z", 11.0),
        job("2026-10-16T23:59:50Z", "2026-10-17T00:00:20Z", 9.0),
        job("2026-10-17T00:10:00Z", None, 0.0, status="failed"),
    ]
    (run / "results.json").write_text(json.dumps({"jobs": rows}), encoding="utf-8")
    (root / retained.RUNS / "no-results").mkdir()


def test_summary_dates_every_figure_and_groups_jobs_by_creation_day(tmp_path: Path) -> None:
    tree(tmp_path)
    found = retained.summary(tmp_path)
    first, second = found["qubits"]
    if first["qubit"] != 2 or second != {"qubit": 10}:
        raise AssertionError(found["qubits"])
    if first["readout"]["utc"] != "2026-10-17T03:20:34+00:00" or first["readout"]["p1_given_1"] != 0.84:
        raise AssertionError(first["readout"])
    want = {
        "us": 14.1847,
        "wait_us": 2.0,
        "wait_run_utc": "2026-10-17T03:20:34+00:00",
        "no_wait_run_utc": "2026-10-16T22:11:33+00:00",
    }
    if first["implied_t1"] != want:
        raise AssertionError(first["implied_t1"])
    if first["coupler_map"]["detuning_hz"] != 18478.1 or first["coupler_map"]["couplers"] != 2:
        raise AssertionError(first["coupler_map"])
    if found["sources"]["coupler_map_runs_utc"] != ["2026-10-16T22:49:24+00:00"]:
        raise AssertionError(found["sources"])
    day = found["jobs"]["tuna_17"]
    if day != [
        {
            "day": "2026-10-16",
            "jobs": 2,
            "shots": 2048,
            "median_turnaround_seconds": 21.25,
            "max_turnaround_seconds": 30.0,
            "median_execution_seconds": 10.0,
        },  # fmt: skip
    ]:
        raise AssertionError(day)


def test_render_is_reproducible(tmp_path: Path) -> None:
    tree(tmp_path)
    if retained.render(tmp_path) != retained.render(tmp_path) or not retained.render(tmp_path).endswith("\n"):
        raise AssertionError("two renders of one tree differ")
