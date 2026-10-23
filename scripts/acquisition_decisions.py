"""Validate future decision statements and job-specific cancellation receipts.

This local preflight does not submit, cancel, approve, or contact any service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

OUTCOMES = (
    "objective established within scope",
    "specified alternative supported",
    "implementation route unavailable",
    "inconclusive within budget",
    "protocol inadmissible",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_decision(case: dict[str, Any]) -> None:
    require(case.get("schema") == "acquisition-decision-v1", "decision schema differs")
    for field in (
        "case_id",
        "provider",
        "backend",
        "simulation_justification",
        "objective",
        "discriminating_observable",
        "trial_definition",
        "observation_chain",
        "dependence_model",
        "layout_timing_identity",
        "processing_policy",
        "end_without_retry",
    ):
        require(nonempty(case.get(field)), f"{field} unavailable")
    alternatives = case.get("alternatives")
    require(
        isinstance(alternatives, list)
        and all(nonempty(v) for v in alternatives)
        and len({v.strip() for v in alternatives}) >= 2,
        "At least two distinct named alternatives are required",
    )
    require(set(case.get("stopping_outcomes", {})) == set(OUTCOMES), "All five terminal decisions must be specified")
    require(all(nonempty(v) for v in case["stopping_outcomes"].values()), "A terminal decision is unspecified")
    require(case.get("power_model", {}).get("status") == "qualified", "Power/covariance model is not qualified")
    require(nonempty(case["power_model"].get("evidence")), "Power qualification evidence missing")
    for field in ("shot_ceiling", "seconds_ceiling", "credits_ceiling", "reserve_seconds"):
        value = case.get(field)
        require(
            isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value) and value >= 0,
            f"{field} must be a finite nonnegative ceiling",
        )
    require(
        isinstance(case["shot_ceiling"], int) and case["shot_ceiling"] > 0, "Shot ceiling must be a positive integer"
    )
    require(case["seconds_ceiling"] > 0, "Seconds ceiling must be positive")
    require(case.get("retry_authorized") is False, "An automatic retry is not a terminal decision")


def validate_cancellation(receipt: dict[str, Any], provider: str, job: str, submit_receipt: bytes) -> None:
    require(receipt.get("schema") == "job-cancellation-authority-v1", "cancellation authority schema differs")
    require(
        receipt.get("provider") == provider and receipt.get("job_id") == job,
        "Cancellation authority does not name this exact provider/job",
    )
    require(nonempty(receipt.get("authority")), "Cancellation authority is not recorded")
    require(
        receipt.get("submission_receipt_sha256") == hashlib.sha256(submit_receipt).hexdigest(),
        "Cancellation authority names a different submission receipt",
    )
    require(bool(re.fullmatch(r"[0-9a-f]{64}", receipt["submission_receipt_sha256"])), "Invalid receipt digest")
    require(
        receipt.get("queue_scope_authorizes_other_jobs") is False, "Shared queue scope grants no cancellation authority"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    decision = commands.add_parser("decision")
    decision.add_argument("case", type=Path)
    cancel = commands.add_parser("cancellation")
    cancel.add_argument("authority", type=Path)
    cancel.add_argument("--provider", required=True)
    cancel.add_argument("--job-id", required=True)
    cancel.add_argument("--submission-receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "decision":
        validate_decision(json.loads(args.case.read_text()))
    else:
        validate_cancellation(
            json.loads(args.authority.read_text()), args.provider, args.job_id, args.submission_receipt.read_bytes()
        )
    print("Local preflight passed; this neither grants execution approval nor changes provider state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
