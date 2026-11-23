"""Execution seconds of every retained IQM QPU job against schedule-duration terms, and a refit of the billing model.

docs/evidence/iqm-garnet-billing-v3/ fits execution - schedule = fixed + per circuit-shot + per mid-circuit record over
the retained active-reset Garnet jobs and adopts no fourth term. The Emerald third-train-length job 01a2058a
executed 9.505 s where the three-term form expects 3.9 to 4.4 s; the open hypothesis of
docs/notes/iqm/emerald-idle-schedule-third-length-result.md is that execution follows the duration of the longest
circuits per shot. This script reads every retained completed active-reset QPU job of Garnet and Emerald through
iqm_records.read_run, computes the duration of each committed circuit as the as-soon-as-possible critical path of its
instructions under the gate durations of scripts/iqm_signed_probe.py (DURATIONS: cz 40 ns, measure 480 ns; prx 16 ns
on Garnet, and 24 ns on Emerald as scripts/iqm_idle_schedule_probe.py records), and fits v3's three terms and three
duration terms: the shots times the sum of the circuit durations, the shots times the longest circuit duration, and
the circuit-shots times the longest duration (every circuit padded to the longest). Each model also runs with a device
offset, a fixed-term indicator for Emerald. Two leave-one-out criteria (over all jobs, and over the jobs other than the
one with the most mid-circuit records) score the models, the job 01a2058a is predicted with that job left out, and a
case's feature file (the circuit durations of a committed case) is priced under every model. Passive-reset jobs run
another shot loop and are scored only. The script adopts no term.

Usage: "$PYTHON" docs/evidence/iqm-billing-v4/billing_v4.py OUT.json
       "$PYTHON" docs/evidence/iqm-billing-v4/billing_v4.py extract CASE_DIR GIT_COMMIT OUT.json
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import iqm_measurement_sequence as ms  # noqa: E402
from iqm_jobs import CANCEL_MARGIN, JOB_SECONDS, cancel_threshold_seconds, ceiling_credits, ceiling_seconds  # noqa: E402
from iqm_signed_probe import DURATIONS  # noqa: E402

import iqm_records  # noqa: E402
from parallel import ordered_map  # noqa: E402

ROUND = 6
HERE = Path(__file__).resolve().parent
FEATURES = HERE / "grover_plane_mirrored_features.json"
PRX_SECONDS = {"garnet": DURATIONS["r"], "emerald": 24e-9}
PRICE = {"garnet": 0.5, "emerald": 0.75}
MARGIN = 1.5
TARGET_JOB = "01a2058a-01a3"
SPECS = {
    "v3": ["fixed", "per_circuit_shot", "per_mid_record"],
    "v4_sum": ["fixed", "per_circuit_shot", "per_mid_record", "per_shot_duration_sum"],
    "v4_max": ["fixed", "per_circuit_shot", "per_mid_record", "per_shot_duration_max"],
    "v4_pad": ["fixed", "per_circuit_shot", "per_mid_record", "per_padded_shot_max"],
}
TERMS = {**SPECS, **{f"{name}_dev": [*terms, "emerald"] for name, terms in SPECS.items()}}


def circuit_seconds(circuit: dict[str, Any], prx_seconds: float) -> float:
    """The as-soon-as-possible critical path of a circuit: each instruction starts when every qubit it touches is free,
    a barrier aligns its qubits, and the gate durations are DURATIONS plus the device's prx."""
    clock: dict[str, float] = {}
    for op in circuit["instructions"]:
        name = op["name"]
        locus = op["locus"]
        start = max((clock.get(q, 0.0) for q in locus), default=0.0)
        if name in ("prx", "cc_prx"):
            length = prx_seconds
        elif name == "cz":
            length = DURATIONS["cz"]
        elif name == "measure":
            length = DURATIONS["measure"]
        elif name == "delay":
            length = float(op["args"]["duration"])
        elif name == "barrier":
            length = 0.0
        else:
            raise SystemExit(f"{name}: no gate duration")
        for q in locus:
            clock[q] = start + length
    return max(clock.values())


def features_of(circuits: list[dict[str, Any]], prx_seconds: float) -> dict[str, Any]:
    return {
        "durations": [circuit_seconds(c, prx_seconds) for c in circuits],
        "mid_measures": [ms.mid_measures(c) for c in circuits],
    }


def row_of(directory: Path) -> dict[str, Any] | None:
    """The row of one retained non-mock run, or None for a run that is not a completed QPU job with a compile
    estimate."""
    submission = json.loads((directory / "submission.json").read_bytes())
    qc = submission["qc"]
    if qc not in PRX_SECONDS:
        return None
    run = iqm_records.read_run(directory)
    metrics = run.job.get("metrics") or {}
    estimate = (run.job.get("compilation") or {}).get("execution_runtime_estimate_seconds")
    if run.results["status"] != "completed" or metrics.get("execution_seconds") is None or estimate is None:
        return None
    options = run.row.get("options", {})
    circuits = [json.loads((directory / entry["file"]).read_bytes()) for entry in run.row["circuits"]]
    feats = features_of(circuits, PRX_SECONDS[qc])
    shots = run.row["shots"]
    count = len(circuits)
    longest = max(feats["durations"])
    return {
        "run": directory.name,
        "job_id": submission["job_id"][:13],
        "qc": qc,
        "active_reset": (options.get("active_reset_cycles") or 0) >= 1,
        "circuits": count,
        "shots": shots,
        "schedule": estimate - JOB_SECONDS,
        "execution": metrics["execution_seconds"],
        "runtime": metrics["runtime_seconds"],
        "circuit_shots": count * shots,
        "mid_records": shots * sum(feats["mid_measures"]),
        "sum_duration": sum(feats["durations"]),
        "max_duration": longest,
        "per_shot_duration_sum": shots * sum(feats["durations"]),
        "per_shot_duration_max": shots * longest,
        "per_padded_shot_max": count * shots * longest,
        "emerald": 1.0 if qc == "emerald" else 0.0,
        "compilation": metrics.get("compilation_seconds"),
    }


def jobs() -> list[dict[str, Any]]:
    directories = sorted(
        p for p in (ROOT / "results/iqm/runs").iterdir() if p.is_dir() and (p / "submission.json").exists()
    )
    return [r for r in ordered_map(row_of, directories, min_items=1) if r is not None]


def design(rows: list[dict[str, Any]], terms: list[str]) -> np.ndarray:
    column = {
        "fixed": lambda r: 1.0,
        "per_circuit_shot": lambda r: float(r["circuit_shots"]),
        "per_mid_record": lambda r: float(r["mid_records"]),
        "per_shot_duration_sum": lambda r: float(r["per_shot_duration_sum"]),
        "per_shot_duration_max": lambda r: float(r["per_shot_duration_max"]),
        "per_padded_shot_max": lambda r: float(r["per_padded_shot_max"]),
        "emerald": lambda r: float(r["emerald"]),
    }
    return np.array([[column[t](r) for t in terms] for r in rows])


def leave_one_out_residual(item: tuple[np.ndarray, np.ndarray, int]) -> float:
    """The residual of job i under the least-squares fit of the other jobs."""
    x, target, i = item
    keep = [j for j in range(len(target)) if j != i]
    c = np.linalg.lstsq(x[keep], target[keep], rcond=None)[0]
    return float(target[i] - x[i] @ c)


def fit(rows: list[dict[str, Any]], terms: list[str], held_out: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    target = np.array([r["execution"] - r["schedule"] for r in rows])
    x = design(rows, terms)
    coefficients = np.linalg.lstsq(x, target, rcond=None)[0]
    residuals = target - x @ coefficients
    loo = ordered_map(leave_one_out_residual, [(x, target, i) for i in range(len(rows))], min_items=1)
    anchor = max(range(len(rows)), key=lambda i: rows[i]["mid_records"])
    others = [abs(v) for i, v in enumerate(loo) if i != anchor]
    # A held-out job is predicted by the fit of the rows alone; the band is the largest leave-one-out residual of the
    # rows other than the anchor. A job inside the rows is predicted with itself left out, and its band excludes it.
    focus = next((i for i, r in enumerate(rows) if r["job_id"] == TARGET_JOB), None)
    if focus is None:
        band = max(others)
        extra = [r for r in held_out or [] if r["job_id"] == TARGET_JOB]
    else:
        band = max(abs(v) for i, v in enumerate(loo) if i not in (anchor, focus))
        extra = []
    predicted = [float(r["schedule"] + design([r], terms)[0] @ coefficients) for r in extra]
    result = {
        "terms": dict(zip(terms, (float(c) for c in coefficients), strict=True)),
        "largest_residual": float(np.max(np.abs(residuals))),
        "largest_leave_one_out_residual": float(np.max(np.abs(loo))),
        "mid_record_anchor": rows[anchor]["job_id"],
        "largest_leave_one_out_residual_without_anchor": max(others),
        "rms_leave_one_out_residual_without_anchor": math.sqrt(sum(v * v for v in others) / len(others)),
        "residuals": {r["job_id"]: float(v) for r, v in zip(rows, residuals, strict=True)},
        "leave_one_out": {r["job_id"]: v for r, v in zip(rows, loo, strict=True)},
    }
    if focus is not None:
        result["focus_job"] = {
            "job_id": TARGET_JOB,
            "leave_one_out_residual": float(loo[focus]),
            "predicted_execution": float(rows[focus]["execution"] - loo[focus]),
            "executed": rows[focus]["execution"],
            "band": band,
            "within_band": bool(abs(loo[focus]) <= band),
        }
    elif extra:
        result["focus_job"] = {
            "job_id": TARGET_JOB,
            "leave_one_out_residual": float(extra[0]["execution"] - predicted[0]),
            "predicted_execution": predicted[0],
            "executed": extra[0]["execution"],
            "band": band,
            "within_band": bool(abs(extra[0]["execution"] - predicted[0]) <= band),
        }
    result["held_out"] = {
        r["job_id"]: float(r["execution"] - r["schedule"] - design([r], terms)[0] @ coefficients)
        for r in held_out or []
    }
    return result


def schedule_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The server's compile estimate (less JOB_SECONDS) as shots times (a per circuit + b per second of circuit
    duration): the schedule a case prices when no mock compile is at hand."""
    x = np.array([[float(r["circuit_shots"]), float(r["per_shot_duration_sum"])] for r in rows])
    target = np.array([r["schedule"] for r in rows])
    c = np.linalg.lstsq(x, target, rcond=None)[0]
    loo = ordered_map(leave_one_out_residual, [(x, target, i) for i in range(len(rows))], min_items=1)
    relative = [abs(v) / r["schedule"] for v, r in zip(loo, rows, strict=True)]
    grover = [x for x, r in zip(relative, rows, strict=True) if "grover" in r["run"]]
    return {
        "terms": {"per_circuit_shot": float(c[0]), "per_duration_second": float(c[1])},
        "largest_leave_one_out_residual": float(max(abs(v) for v in loo)),
        "largest_leave_one_out_relative": float(max(relative)),
        "largest_leave_one_out_relative_grover_jobs": float(max(grover)),
        "leave_one_out": {r["job_id"]: v for r, v in zip(rows, loo, strict=True)},
    }


def case_features(case_dir: Path, commit: str) -> dict[str, Any]:
    case, row, digest = iqm_records.load_job(case_dir, "grover")
    circuits = [json.loads((case_dir / e["file"]).read_bytes()) for e in row["circuits"]]
    feats = features_of(circuits, PRX_SECONDS["garnet"])
    return {
        "case": case["case"],
        "branch_commit": commit,
        "cases_sha256": digest,
        "qc": "garnet",
        "shots": row["shots"],
        "circuits": len(circuits),
        "expected_seconds": row["expected_seconds"],
        "case_max_credits": row["max_credits"]["garnet"],
        "heralding_mode": row["options"]["heralding_mode"],
        "durations": feats["durations"],
        "mid_measures": feats["mid_measures"],
    }


def case_prediction(
    rows: list[dict[str, Any]], fits: dict[str, Any], sched: dict[str, Any], feat: dict[str, Any]
) -> dict[str, Any]:
    shots, count = feat["shots"], feat["circuits"]
    durations = feat["durations"]
    longest = max(durations)
    sched_pred = sched["terms"]["per_circuit_shot"] * count * shots + sched["terms"][
        "per_duration_second"
    ] * shots * sum(durations)
    sched_band = sched["largest_leave_one_out_relative"] * sched_pred
    sched_band_grover = sched["largest_leave_one_out_relative_grover_jobs"] * sched_pred
    values = {
        "fixed": 1.0,
        "per_circuit_shot": float(count * shots),
        "per_mid_record": float(shots * sum(feat["mid_measures"])),
        "per_shot_duration_sum": float(shots * sum(durations)),
        "per_shot_duration_max": float(shots * longest),
        "per_padded_shot_max": float(count * shots * longest),
        "emerald": 0.0,
    }
    garnet = [r for r in rows if r["qc"] == "garnet" and r["active_reset"]]
    over = max(r["runtime"] - r["execution"] for r in rows if r["active_reset"])
    price = PRICE["garnet"]
    out: dict[str, Any] = {}
    for name, f in fits.items():
        excess = sum(c * values[t] for t, c in f["terms"].items())
        execution = sched_pred + excess
        band = f["largest_leave_one_out_residual_without_anchor"] + sched_band
        worst = execution + band + over
        seconds = math.ceil(MARGIN * worst)
        credits = price * (seconds + CANCEL_MARGIN)
        narrow = f["largest_leave_one_out_residual_without_anchor"] + sched_band_grover
        narrow_credits = price * (math.ceil(MARGIN * (execution + narrow + over)) + CANCEL_MARGIN)
        out[name] = {
            "max_credits_for_margin_grover_schedule_band": narrow_credits,
            "band_seconds_grover_schedule_band": narrow,
            "schedule_seconds": sched_pred,
            "excess_seconds": excess,
            "execution_seconds": execution,
            "band_seconds": band,
            "worst_case_runtime_seconds": worst,
            "max_credits_for_margin": credits,
            "cancel_threshold_seconds": cancel_threshold_seconds(credits, price),
            "ceiling_credits_of_execution": ceiling_credits(execution + band, price),
        }
    out["garnet_active_jobs"] = len(garnet)
    out["runtime_over_execution_seconds"] = over
    out["longest_circuit_seconds"] = longest
    out["ceiling_seconds_check"] = ceiling_seconds(feat["case_max_credits"], price)
    return out


def padding_reading(fits: dict[str, Any], suffix: str) -> dict[str, Any]:
    within = {k: fits[f"{k}{suffix}"]["focus_job"]["within_band"] for k in ("v3", "v4_sum", "v4_max", "v4_pad")}
    if within["v4_max"] and not within["v4_sum"]:
        verdict = "padding survives, per-shot duration sum falsified"
    elif within["v4_sum"] and not within["v4_max"]:
        verdict = "padding falsified, per-shot duration sum survives"
    elif within["v4_sum"] and within["v4_max"]:
        verdict = "both duration terms predict the job within the band"
    else:
        verdict = "neither duration term predicts the job within the band"
    return {"within_band": within, "verdict": verdict}


def rounded(value: Any) -> Any:
    if isinstance(value, float):
        return float(f"{value:.{ROUND}g}")
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    return value


def main(out: Path) -> None:
    every = jobs()
    rows = [r for r in every if r["active_reset"]]
    passive = [r for r in every if not r["active_reset"]]
    garnet = [r for r in rows if r["qc"] == "garnet"]
    emerald = [r for r in rows if r["qc"] == "emerald"]
    fits = {name: fit(rows, terms) for name, terms in TERMS.items()}
    garnet_fits = {name: fit(garnet, terms, emerald) for name, terms in SPECS.items()}
    sched = schedule_model(garnet)
    record: dict[str, Any] = {
        "definition": (
            "schedule = execution_runtime_estimate_seconds - JOB_SECONDS; residual = execution - schedule - model; "
            "completed active-reset QPU jobs of Garnet and Emerald; durations are as-soon-as-possible critical paths"
        ),
        "gate_seconds": {"garnet_prx": PRX_SECONDS["garnet"], "emerald_prx": PRX_SECONDS["emerald"], **DURATIONS},
        "jobs": rows,
        "passive_jobs": passive,
        "fits": fits,
        "garnet_fits": garnet_fits,
        "schedule_model_garnet": sched,
        "padding_hypothesis": {
            "device_pooled": padding_reading(fits, ""),
            "device_offset": padding_reading(fits, "_dev"),
            "garnet_fit_held_out": padding_reading(garnet_fits, ""),
        },
        "largest_runtime_over_execution": max(r["runtime"] - r["execution"] for r in rows),
        "note": "descriptive refit; BILLING_MODELS changes in the change that first sizes a case from it",
    }
    if FEATURES.exists():
        feat = json.loads(FEATURES.read_bytes())
        record["case"] = {
            "features_sha256": hashlib.sha256(FEATURES.read_bytes()).hexdigest(),
            "case": feat["case"],
            "branch_commit": feat["branch_commit"],
            "cases_sha256": feat["cases_sha256"],
            "shots": feat["shots"],
            "circuits": feat["circuits"],
            "prediction": case_prediction(
                rows, {**garnet_fits, **{f"pooled_{k}": v for k, v in fits.items()}}, sched, feat
            ),
        }
    out.write_text(json.dumps(rounded(record), indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "extract":
        Path(sys.argv[4]).write_text(
            json.dumps(case_features(Path(sys.argv[2]), sys.argv[3]), indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif len(sys.argv) == 2:
        main(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
