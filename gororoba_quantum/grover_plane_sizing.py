"""Billing v4 sizing of a Garnet case from its circuits: execution seconds, band, credits and cancel threshold.

The coefficients are the three Garnet models of docs/evidence/iqm-billing-v4 (v3, v4_sum, v4_max) and the schedule
model of that record, pinned with the commit and digest of billing_v4.json in billing_v4_inputs.json. A case's
schedule is the schedule model applied to its circuit durations (the as-soon-as-possible critical path of each
circuit, measurement included); each model adds its excess; the band adds the model's largest leave-one-out residual
without the anchor job and the schedule model's relative error times the schedule, under the error of all jobs (the
sizing adopted) and under the error of the Grover jobs (reported beside); the worst case adds the largest retained
runtime over execution; the credits buy 1.5 times the worst case, one second of cancel margin included. The adopted
credits are the largest of the three models under the all-jobs band.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from iqm_jobs import CANCEL_MARGIN, ceiling_credits, ceiling_seconds

INPUTS = Path(__file__).resolve().parent.parent / "docs/evidence/iqm-garnet-grover-plane/billing_v4_inputs.json"
OVERRUNS = (1.0, 1.5, 2.2)


def load_inputs() -> dict[str, Any]:
    return dict(json.loads(INPUTS.read_text(encoding="utf-8")))


def price(inputs: dict[str, Any], seconds: list[float], mid: list[int], shots: int) -> dict[str, Any]:
    """Every model's pricing of a case of circuits with the given durations (seconds) and mid-circuit measure counts."""
    count, longest, total = len(seconds), max(seconds), sum(seconds)
    sched = inputs["schedule_model"]
    schedule = (
        sched["terms"]["per_circuit_shot"] * count * shots + sched["terms"]["per_duration_second"] * shots * total
    )
    values = {
        "fixed": 1.0,
        "per_circuit_shot": float(count * shots),
        "per_mid_record": float(shots * sum(mid)),
        "per_shot_duration_sum": float(shots * total),
        "per_shot_duration_max": float(shots * longest),
    }
    price_garnet = float(inputs["price_garnet"])
    over = float(inputs["runtime_over_execution_seconds"])
    out: dict[str, Any] = {}
    for name, model in inputs["models"].items():
        excess = sum(c * values[t] for t, c in model["terms"].items())
        execution = schedule + excess
        row: dict[str, Any] = {
            "schedule_seconds": schedule,
            "excess_seconds": excess,
            "execution_seconds": execution,
            "expected_runtime_seconds": execution + over,
            "expected_billed_credits": ceiling_credits(execution, price_garnet),
        }
        for tag, relative in (("all_jobs", "relative_error_all_jobs"), ("grover_jobs", "relative_error_grover_jobs")):
            band = model["largest_leave_one_out_residual_without_anchor"] + sched[relative] * schedule
            worst = execution + band + over
            row[f"band_seconds_{tag}"] = band
            row[f"worst_case_runtime_seconds_{tag}"] = worst
            row[f"max_credits_{tag}"] = price_garnet * (math.ceil(inputs["margin"] * worst) + CANCEL_MARGIN)
        out[name] = row
    return out


def adopted(inputs: dict[str, Any], priced: dict[str, Any]) -> dict[str, Any]:
    """The credits adopted (largest over the models, all-jobs band), the billed seconds and cancel threshold they buy,
    and the margin of the threshold over an overrun of the longest expected runtime."""
    price_garnet = float(inputs["price_garnet"])
    credits = max(row["max_credits_all_jobs"] for row in priced.values())
    billed = float(ceiling_seconds(credits, price_garnet))
    threshold = billed - CANCEL_MARGIN
    runtime = max(row["expected_runtime_seconds"] for row in priced.values())
    return {
        "max_credits": credits,
        "max_credits_grover_band": max(row["max_credits_grover_jobs"] for row in priced.values()),
        "billed_seconds_of_ceiling": billed,
        "cancel_threshold_seconds": threshold,
        "expected_execution_seconds": max(row["execution_seconds"] for row in priced.values()),
        "expected_runtime_seconds": runtime,
        "overrun_margins": {
            f"{f:g}x": {
                "runtime_seconds": f * runtime,
                "margin_seconds": threshold - f * runtime,
                "covered": bool(threshold >= f * runtime),
            }
            for f in OVERRUNS
        },
    }
