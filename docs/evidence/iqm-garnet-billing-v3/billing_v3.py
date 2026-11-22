"""Execution seconds of every retained active-reset Garnet QPU job against the v2 billing model, and a refit.

scripts/iqm_measurement_sequence.py fits BILLING_MODELS["v2"], execution - schedule = fixed + per circuit-shot + per
mid-circuit record, over twelve jobs of October 2026, where schedule is the server's compiled estimate less the
1.6 s job term (JOB_SECONDS). This script scores v2 on every retained active-reset Garnet QPU job, the later ones
included, refits the same three terms over all of them, and fits two candidate fourth terms: one per heralded
circuit-shot and one per squared circuit-shot (a curvature in job size). A term earns its place only when it lowers
the largest leave-one-out residual over the jobs other than the one with the most mid-circuit records, whose
removal leaves the per-record term to extrapolation. It also reports runtime minus execution, which sets the margin
a ceiling needs. Passive-reset jobs run a different shot loop and stay out. It decides nothing: BILLING_MODELS changes in the change
that first sizes a case from a refit.

Usage: "$PYTHON" docs/evidence/iqm-garnet-billing-v3/billing_v3.py OUT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import iqm_measurement_sequence as ms  # noqa: E402

ROUND = 6
TERMS = {
    "v3": ["fixed", "per_circuit_shot", "per_mid_record"],
    "v3_herald": ["fixed", "per_circuit_shot", "per_mid_record", "per_heralded_circuit_shot"],
    "v3_curvature": ["fixed", "per_circuit_shot", "per_mid_record", "per_squared_circuit_shot"],
}


def jobs() -> list[dict[str, Any]]:
    rows = []
    for directory in sorted((ROOT / "results/iqm/runs").glob("*-garnet-*")):
        if not (directory / "raw/job.json").exists() or not (directory / "submission.json").exists():
            continue
        submission = ms.load_json(directory / "submission.json")
        if submission.get("qc") != "garnet":
            continue
        case = ms.load_json(directory / "cases.json")
        job = next(r for r in case["jobs"] if r["job"] == submission["job"])
        options = job.get("options", {})
        if (options.get("active_reset_cycles") or 0) < 1:
            continue
        record = json.loads((directory / "raw/job.json").read_bytes())
        metrics = record.get("metrics") or {}
        estimate = (record.get("compilation") or {}).get("execution_runtime_estimate_seconds")
        if metrics.get("execution_seconds") is None or estimate is None:
            continue
        circuits = [ms.load_json(directory / entry["file"]) for entry in job["circuits"]]
        circuit_shots = len(job["circuits"]) * job["shots"]
        rows.append(
            {
                "run": directory.name,
                "job_id": submission["job_id"][:13],
                "in_v2_fit": submission["job_id"][:13] in ms.BILLING_V2_JOBS,
                "heralding": options.get("heralding_mode", "none"),
                "circuits": len(job["circuits"]),
                "shots": job["shots"],
                "schedule": estimate - ms.JOB_SECONDS,
                "execution": metrics["execution_seconds"],
                "runtime": metrics["runtime_seconds"],
                "circuit_shots": circuit_shots,
                "mid_records": job["shots"] * sum(ms.mid_measures(c) for c in circuits),
                "heralded_circuit_shots": circuit_shots if options.get("heralding_mode", "none") != "none" else 0,
            }
        )
    return rows


def design(rows: list[dict[str, Any]], terms: list[str]) -> np.ndarray:
    column = {
        "fixed": lambda r: 1.0,
        "per_circuit_shot": lambda r: float(r["circuit_shots"]),
        "per_mid_record": lambda r: float(r["mid_records"]),
        "per_heralded_circuit_shot": lambda r: float(r["heralded_circuit_shots"]),
        "per_squared_circuit_shot": lambda r: float(r["circuit_shots"]) ** 2,
    }
    return np.array([[column[t](r) for t in terms] for r in rows])


def fit(rows: list[dict[str, Any]], terms: list[str]) -> dict[str, Any]:
    target = np.array([r["execution"] - r["schedule"] for r in rows])
    x = design(rows, terms)
    coefficients = np.linalg.lstsq(x, target, rcond=None)[0]
    residuals = target - x @ coefficients
    leave_one_out = []
    for i in range(len(rows)):
        keep = [j for j in range(len(rows)) if j != i]
        c = np.linalg.lstsq(x[keep], target[keep], rcond=None)[0]
        leave_one_out.append(float(target[i] - x[i] @ c))
    # The per-record term rests on the one job with many mid-circuit records; leaving it out extrapolates that term,
    # so the comparison of terms reads the largest leave-one-out residual over the other jobs.
    anchor = max(range(len(rows)), key=lambda i: rows[i]["mid_records"])
    others = [abs(v) for i, v in enumerate(leave_one_out) if i != anchor]
    return {
        "terms": dict(zip(terms, (float(c) for c in coefficients), strict=True)),
        "largest_residual": float(np.max(np.abs(residuals))),
        "largest_leave_one_out_residual": float(np.max(np.abs(leave_one_out))),
        "mid_record_anchor": rows[anchor]["job_id"],
        "largest_leave_one_out_residual_without_anchor": max(others),
        "residuals": {r["job_id"]: float(v) for r, v in zip(rows, residuals, strict=True)},
        "leave_one_out": {r["job_id"]: v for r, v in zip(rows, leave_one_out, strict=True)},
    }


def rounded(value: Any) -> Any:
    if isinstance(value, float):
        return float(f"{value:.{ROUND}g}")
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    return value


def main(out: Path) -> None:
    rows = jobs()
    if sum(r["in_v2_fit"] for r in rows) != len(ms.BILLING_V2_JOBS):
        raise SystemExit("a job of the v2 fit is missing from the retained active-reset Garnet runs")
    v2 = ms.BILLING_MODELS["v2"]
    for r in rows:
        predicted = r["schedule"] + v2["fixed"] + v2["per_circuit_shot"] * r["circuit_shots"]
        predicted += v2["per_mid_record"] * r["mid_records"]
        r["v2_residual"] = r["execution"] - predicted
        r["runtime_over_execution"] = r["runtime"] - r["execution"]
    record = {
        "definition": (
            "schedule = execution_runtime_estimate_seconds - JOB_SECONDS; residual = execution - schedule - model; "
            "active-reset Garnet QPU jobs only"
        ),
        "v2": {k: v2[k] for k in ("fixed", "per_circuit_shot", "per_mid_record", "residual", "runtime_over")},
        "jobs": rows,
        "v2_outside_band": [r["job_id"] for r in rows if abs(r["v2_residual"]) > v2["residual"]],
        "largest_runtime_over_execution": max(r["runtime_over_execution"] for r in rows),
        "fits": {name: fit(rows, terms) for name, terms in TERMS.items()},
        "note": "descriptive refit; BILLING_MODELS changes in the change that first sizes a case from it",
    }
    out.write_text(json.dumps(rounded(record), indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
