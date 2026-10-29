"""Frozen response analysis for three nominal-one Tuna destination jobs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from decimal import ROUND_CEILING, Decimal, localcontext
from pathlib import Path
from typing import Any

import acquisition_decisions
import numpy as np
from qi_projector_compiler_admission import normalized_instructions
from qi_projector_live_admission import STRUCTURAL_FIELDS, json_digest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-readout-destination-one"
SHOTS = 4096
ANCILLAS = (4, 11, 6)
ARMS = ("baseline-before", "rotated-destinations", "baseline-after")
BATCHES = tuple(f"prepared-one-{arm}" for arm in ARMS)
MARGIN = Decimal("0.10")
ALPHA = Decimal("0.01")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_positive_integer(value: Any, label: str) -> int:
    """Preserve the API distinction between integer identifiers/counts and JSON numbers."""
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive JSON integer")
    return value


def validate_execution_seconds(value: Any) -> Decimal:
    """Accept finite JSON numbers only; booleans and numeric strings are malformed."""
    if type(value) not in (int, float):
        raise ValueError("execution time must be a JSON number excluding Boolean")
    seconds = Decimal(str(value))
    if not seconds.is_finite() or not 0 <= seconds <= 300:
        raise ValueError("execution time violates the finite 0-to-300-second bound")
    return seconds


def validate_zero_transactions(rows: Any, job_id: int) -> None:
    """Require distinct identified transactions with exact integer zero changes."""
    if type(job_id) is not int or job_id <= 0 or not isinstance(rows, list):
        raise ValueError("transactions require a list and a positive integer job identity")
    identities = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("transaction row must be an object")
        identity = row.get("id")
        if type(identity) is not int or identity <= 0 or identity in identities:
            raise ValueError("transaction identities must be distinct positive integers")
        if type(row.get("job")) is not int or row["job"] != job_id:
            raise ValueError("transaction job differs from the acquired identity")
        if type(row.get("change")) is not int or row["change"] != 0:
            raise ValueError("transaction changes must be exact integer zero")
        identities.add(identity)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def validate_approval(run: Path, campaign: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    approval = json.loads((run / "approval.json").read_text())
    if (
        approval.get("schema") != "qi-tuna-destination-one-approval-v1"
        or not isinstance(approval.get("approval"), str)
        or not approval["approval"].strip()
    ):
        raise ValueError("bound owner approval receipt is malformed")
    bindings = {
        key: approval[key]
        for key in (
            "campaign_sha256",
            "written_case_sha256",
            "decision_sha256",
            "terms_sha256",
            "analysis_contract_sha256",
        )
    }
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in bindings.values()):
        raise ValueError("approval bindings must be SHA-256 strings")
    if (
        bindings["campaign_sha256"] != digest(run / "sequence-plan.json")
        or bindings["analysis_contract_sha256"] != hashlib.sha256(json_bytes(campaign["analysis_contract"])).hexdigest()
    ):
        raise ValueError("owner approval differs from frozen campaign or analyzer")
    for name, key in (
        ("written-case-at-approval.md", "written_case_sha256"),
        ("decision-at-approval.json", "decision_sha256"),
        ("terms-at-approval.json", "terms_sha256"),
    ):
        if digest(run / name) != bindings[key]:
            raise ValueError("retained approval attachment differs from its bound digest")
    decision = json.loads((run / "decision-at-approval.json").read_text())
    acquisition_decisions.validate_decision(decision)
    expected = {
        "status": "admitted-for-owner-approval",
        "campaign_sha256": bindings["campaign_sha256"],
        "written_case_sha256": bindings["written_case_sha256"],
        "analysis_contract_sha256": bindings["analysis_contract_sha256"],
        "expected_credits": 0,
        "execution_authorized": False,
        "provider": "quantum_inspire",
        "backend": "tuna_17",
        "shot_ceiling": campaign["shots_total"],
        "seconds_ceiling": campaign["provider_execution_ceiling_seconds"],
        "credits_ceiling": 0,
        "reserve_seconds": 0,
        "retry_authorized": False,
        "expected_execution_seconds_decimal": campaign["expected_execution_seconds_decimal"],
    }
    if any(type(decision.get(key)) is not type(value) or decision[key] != value for key, value in expected.items()):
        raise ValueError("approved decision scope differs from frozen campaign")
    terms = json.loads((run / "terms-at-approval.json").read_text())
    validate_terms(terms)
    return bindings, approval


def validate_terms(receipt: Any) -> None:
    """Admit only the retained three-page normalized public-policy contract."""
    if not isinstance(receipt, dict) or receipt.get("schema") != "qi-readout-destination-terms-text-v1":
        raise ValueError("public policy receipt schema differs")
    pages = receipt.get("pages")
    expected_urls = {
        "https://www.quantum-inspire.com/faq/",
        "https://www.quantum-inspire.com/kbase/managing-your-account/",
        "https://www.quantum-inspire.com/terms-and-conditions/",
    }
    if not isinstance(pages, list) or len(pages) != 3 or any(not isinstance(page, dict) for page in pages):
        raise ValueError("public policy receipt requires three page objects")
    if any(not isinstance(page.get("url"), str) for page in pages):
        raise ValueError("public policy page URLs must be strings")
    if {page.get("url") for page in pages} != expected_urls:
        raise ValueError("approved terms must bind all three policy pages")
    for page in pages:
        value = page.get("text")
        if (
            not isinstance(value, str)
            or not value.strip()
            or hashlib.sha256(value.encode()).hexdigest() != page.get("text_sha256")
        ):
            raise ValueError("approved policy text differs from retained digest")
        timestamp(page.get("observed_utc"))
        if not isinstance(page.get("html_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", page["html_sha256"]):
            raise ValueError("public policy page response digest is malformed")


def validate_admission_structure(
    admission: dict[str, Any], directory: Path, campaign: dict[str, Any], observed: dt.datetime
) -> None:
    """Require the same complete frozen backend and account state at each admission boundary."""
    snapshot_path = directory / "backend.json"
    manifest = json.loads((directory / "cases.json").read_text())
    if digest(snapshot_path) != manifest["backend_snapshot"]["sha256"]:
        raise ValueError("frozen backend snapshot differs")
    frozen = json.loads(snapshot_path.read_text())
    for key in STRUCTURAL_FIELDS:
        actual = admission["backend"].get(key)
        if key == "job_execution_time_limit":
            matches = validate_execution_seconds(actual) == Decimal(str(frozen[key]))
        else:
            matches = type(actual) is type(frozen[key]) and actual == frozen[key]
        if not matches:
            raise ValueError("admitted backend structure differs from frozen snapshot")
    if (
        admission["enabled"] is not True
        or admission["status"] not in ("idle", "executing")
        or admission["topology"] != frozen["topology"]
        or set(admission["gateset"]) != set(frozen["gateset"])
        or admission["compiler_config_sha256"] != json_digest(frozen["default_compiler_config"])
        or admission["queue_user_only"] is not True
        or type(admission["queued_batches"]) is not int
        or admission["queued_batches"] != 0
        or type(admission["hardware_pause_left_seconds"]) is not int
        or admission["hardware_pause_left_seconds"] != 0
        or type(admission["account_transaction_rows"]) is not int
        or admission["account_transaction_rows"] < 0
        or admission["all_transaction_changes_zero"] is not True
    ):
        raise ValueError("successful admission contradicts recorded structure, queue, pause or ledger")
    expected_limits = {
        "batch_circuits": 1,
        "shots_per_circuit": SHOTS,
        "account_hardware_queued_batches": 1,
        "hardware_pause_seconds": 30,
    }
    if set(admission["limits"]) != set(expected_limits) or any(
        type(admission["limits"][key]) is not int or admission["limits"][key] != value
        for key, value in expected_limits.items()
    ):
        raise ValueError("admission limits differ from the case")
    if admission["heartbeat_max_age_seconds"] != campaign["heartbeat_max_age_seconds"] or not admission["instances"]:
        raise ValueError("hardware heartbeat evidence is absent or scoped incorrectly")
    for instance in admission["instances"]:
        age = (observed - timestamp(instance["last_heartbeat"])).total_seconds()
        if (
            instance["status"] not in ("idle", "executing")
            or not 0 <= age <= campaign["heartbeat_max_age_seconds"]
            or type(instance["age_seconds"]) not in (int, float)
            or instance["age_seconds"] != age
        ):
            raise ValueError("hardware heartbeat was stale at admission")


def validate_locked_admission(directory: Path, campaign: dict[str, Any], created: dt.datetime) -> None:
    """Consume the decisive under-lock observation as mandatory per-job evidence."""
    locked = json.loads((directory / "locked-admission.json").read_text())
    initial = json.loads((directory / "admission.json").read_text())
    producers = campaign["producer_inputs"]
    if (
        not isinstance(locked, dict)
        or locked.get("schema") != "qi-tuna-destination-one-locked-admission-v1"
        or locked.get("admitted") is not True
        or locked.get("failures") != []
        or locked.get("cases_sha256") != digest(directory / "cases.json")
        or locked.get("runner_sha256") != producers["scripts/qi_tuna_destination_one_run.py"]
        or locked.get("submission_helper_sha256") != producers["scripts/qi_platform_submission_deadline.py"]
    ):
        raise ValueError("locked admission lacks successful matching case and producer identities")
    observed = timestamp(locked["observed_utc"])
    started = timestamp(initial["request_started_utc"])
    initial_observed = timestamp(initial["observed_utc"])
    window = json.loads((directory.parent / "execution-window.json").read_text())
    window_start = timestamp(window["started_utc"])
    window_deadline = timestamp(window["request_deadline_utc"])
    if (
        window.get("schema") != "qi-tuna-destination-one-window-v1"
        or type(window.get("request_initiation_timeout_seconds")) is not int
        or window["request_initiation_timeout_seconds"] != campaign["campaign_request_initiation_timeout_seconds"]
        or window_deadline - window_start != dt.timedelta(seconds=window["request_initiation_timeout_seconds"])
        or not window_start <= started <= window_deadline
        or not started <= initial_observed <= observed <= created
        or (created - started).total_seconds() > campaign["admission_max_age_seconds"]
    ):
        raise ValueError("locked admission chronology contradicts the fresh preceding observation or campaign window")
    validate_admission_structure(locked, directory, campaign, observed)


def validate_admission(
    directory: Path, campaign: dict[str, Any], bindings: dict[str, str], created: dt.datetime
) -> None:
    admission = json.loads((directory / "admission.json").read_text())
    if (
        admission.get("schema") != "qi-tuna-destination-one-admission-v1"
        or admission.get("admitted") is not True
        or admission.get("failures") != []
        or admission.get("bindings") != bindings
    ):
        raise ValueError("job lacks a matching successful admission receipt")
    runner = "scripts/qi_tuna_destination_one_run.py"
    if admission["producer_sha256"] != campaign["producer_inputs"][runner]:
        raise ValueError("admission producer differs from frozen runner")
    started, observed = (timestamp(admission[key]) for key in ("request_started_utc", "observed_utc"))
    window = json.loads((directory.parent / "execution-window.json").read_text())
    window_start = timestamp(window["started_utc"])
    window_deadline = timestamp(window["request_deadline_utc"])
    if (
        window.get("schema") != "qi-tuna-destination-one-window-v1"
        or type(window.get("request_initiation_timeout_seconds")) is not int
        or window["request_initiation_timeout_seconds"] != campaign["campaign_request_initiation_timeout_seconds"]
        or window_deadline - window_start != dt.timedelta(seconds=window["request_initiation_timeout_seconds"])
        or not window_start <= started <= window_deadline
    ):
        raise ValueError("admission request falls outside the frozen campaign initiation window")
    if (
        not started <= observed <= created
        or (created - started).total_seconds() > campaign["admission_max_age_seconds"]
    ):
        raise ValueError("job creation lacks a fresh preceding admission")
    validate_admission_structure(admission, directory, campaign, observed)
    terms = json.loads((directory.parent / "terms-at-approval.json").read_text())
    expected_pages = {page["url"]: page["text_sha256"] for page in terms["pages"]}
    pages = admission["public_policy_pages"]
    if len(pages) != len(expected_pages) or {page["url"]: page["text_sha256"] for page in pages} != expected_pages:
        raise ValueError("admission policy pages differ from approved terms")
    if any(
        not isinstance(page["html_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", page["html_sha256"])
        for page in pages
    ):
        raise ValueError("policy observation lacks complete response digests")


def contract() -> dict[str, Any]:
    with localcontext() as context:
        context.prec = 60
        logarithm = (Decimal(48) / ALPHA).ln()
        response = (Decimal(3) * logarithm / (4 * SHOTS)).sqrt()
        baseline = (logarithm / SHOTS).sqrt()
        quantum = Decimal("0.000000000001")
        response = response.quantize(quantum, rounding=ROUND_CEILING)
        baseline = baseline.quantize(quantum, rounding=ROUND_CEILING)
    return {
        "schema": "qi-destination-one-predictable-response-contract-v1",
        "shots_per_job": SHOTS,
        "jobs": 3,
        "selected_response_cells": 12,
        "simultaneously_bounded_contrasts": 24,
        "familywise_alpha_decimal": str(ALPHA),
        "response_margin_decimal": str(MARGIN),
        "baseline_margin_decimal": str(MARGIN),
        "response_radius_decimal": str(response),
        "baseline_radius_decimal": str(baseline),
        "response_weight_squared_sum": [3, 2 * SHOTS],
        "baseline_weight_squared_sum": [2, SHOTS],
        "uniform_response_equivalence_separation_decimal": str(MARGIN - 2 * response),
        "uniform_response_departure_separation_decimal": str(MARGIN + 2 * response),
        "uniform_baseline_admission_separation_decimal": str(MARGIN - 2 * baseline),
        "target": "Realized averages of each next-shot cell probability conditional on the entire preceding history.",
        "response_contrast": "Rotated predictable response minus the arithmetic mean of bracketing baselines.",
        "assumptions": [
            "Binary outcomes with trusted shot order, complete fixed-size jobs and fixed feature/weight definitions.",
            "The filtration contains all earlier outcomes, jobs and preparation choices; no IID premise is used.",
            "All three nominal-one jobs finish before classification; earlier stopping permits invalidity only.",
        ],
        "attribution_status": "unresolved",
        "attribution_boundary": "Baseline endpoints cannot bound a transient or counterfactual during rotation.",
        "sensitivity_drift_bounds_decimal": ["0", "0.02", "0.05"],
        "sensitivity_status": "Unverified assumptions; sensitivity intervals never change the primary decision.",
    }


def cells(arguments: tuple[str, list[str], list[int]]) -> dict[str, Any]:
    name, shots, early_bits = arguments
    if len(shots) != SHOTS or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots):
        raise ValueError("raw shots must contain exactly 4096 width-20 binary strings")
    bits = np.array([list(shot[::-1]) for shot in shots], dtype=np.int64)
    labels = 2 * bits[:, early_bits] + bits[:, ANCILLAS]
    indicator = labels[:, :, None] == np.arange(4)[None, None, :]
    return {
        "batch": name,
        "joint_counts": indicator.sum(axis=0).tolist(),
        "block_joint_counts": indicator.reshape(16, 256, 3, 4).sum(axis=1).tolist(),
    }


def timestamp(value: Any) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("a recorded timezone-aware timestamp is required")
    result = dt.datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("timestamp lacks a timezone")
    return result


def validate_batch(
    task: tuple[Path, Path, dict[str, Any], dict[str, Any], dict[str, str], dict[str, Any]],
) -> dict[str, Any]:
    run, proposal, batch, campaign, bindings, approval = task
    name = batch["name"]
    if name not in BATCHES:
        raise ValueError("unexpected batch identity")
    directory = run / name
    reference = proposal / name
    manifest_path = directory / "cases.json"
    if (
        manifest_path.read_bytes() != (reference / "cases.json").read_bytes()
        or digest(manifest_path) != batch["cases_sha256"]
    ):
        raise ValueError("run manifest differs from the frozen campaign")
    manifest = json.loads(manifest_path.read_text())
    if (
        validate_positive_integer(manifest["shots"], "manifest shots") != SHOTS
        or validate_positive_integer(manifest["backend_type_id"], "backend ID") != 7
        or len(manifest["circuits"]) != 1
    ):
        raise ValueError("manifest must specify one 4096-shot Tuna circuit")
    entry = manifest["circuits"][0]
    filename = entry["file"]
    if Path(filename).name != filename:
        raise ValueError("circuit filename must be a basename")
    source_path = directory / filename
    if source_path.read_bytes() != (reference / filename).read_bytes() or digest(source_path) != entry["sha256"]:
        raise ValueError("source differs from frozen manifest")
    early = (19, 17, 18) if name.endswith("rotated-destinations") else (17, 18, 19)
    expected_map = [["measure", [qubit], bit] for qubit, bit in zip(ANCILLAS, early, strict=True)]
    expected_map.extend(["measure", [qubit], qubit] for qubit in range(17))
    actual_map = [
        row for row in normalized_instructions(source_path.read_text())["instructions"] if row[0] == "measure"
    ]
    metadata = entry["analysis_metadata"]
    if (
        actual_map != expected_map
        or type(metadata["width"]) is not int
        or metadata["width"] != 20
        or metadata["canonical_early_qubit_order"] != list(ANCILLAS)
        or metadata["bit_order"] != "classical bit zero is the rightmost character"
        or metadata["index_convention"] != "zero-based string offsets from the left"
        or metadata["terminal_classical_bits"] != list(range(17))
        or metadata["canonical_early_classical_bits"] != list(early)
        or metadata["canonical_early_string_offsets"] != [19 - bit for bit in early]
    ):
        raise ValueError("source and decoder disagree with the frozen physical measurement map")
    submission_path = directory / "submission.json"
    result_path = directory / "results.json"
    submission = json.loads(submission_path.read_text())
    collection = json.loads(result_path.read_text())
    if (
        submission.get("schema") != "qi-submission-v2"
        or collection.get("schema") != "qi-collection-v1"
        or submission.get("approval") != approval["approval"]
        or validate_positive_integer(submission["backend_type_id"], "submission backend ID") != 7
        or submission["backend"] != "tuna_17"
        or validate_positive_integer(submission["shots"], "submission shots") != SHOTS
        or submission["cases_sha256"] != batch["cases_sha256"]
        or submission["state"] != "enqueued"
        or len(submission["jobs"]) != 1
        or len(collection["jobs"]) != 1
    ):
        raise ValueError("submission or collection scope differs")
    submitted = submission["jobs"][0]
    collected = collection["jobs"][0]
    job = collected["job"]
    if (
        submitted["file"] != filename
        or submitted["sha256"] != entry["sha256"]
        or collected["file"] != filename
        or type(submitted["job"]) is not int
        or submitted["job"] <= 0
        or type(job["id"]) is not int
        or job["id"] != submitted["job"]
        or type(job["batch_job_id"]) is not int
        or job["batch_job_id"] <= 0
        or type(submission["batch_job"]) is not int
        or job["batch_job_id"] != submission["batch_job"]
        or job["status"] != "completed"
        or validate_positive_integer(job["number_of_shots"], "job shots") != SHOTS
        or job["raw_data_enabled"] is not True
        or len(collected["results"]) != 1
    ):
        raise ValueError("matching completed full-shot raw-enabled job required")
    result = collected["results"][0]
    if (
        validate_positive_integer(result["job_id"], "result job ID") != job["id"]
        or validate_positive_integer(result["shots_requested"], "requested shots") != SHOTS
        or validate_positive_integer(result["shots_done"], "completed shots") != SHOTS
    ):
        raise ValueError("partial or wrong-job result")
    execution = validate_execution_seconds(result["execution_time_in_seconds"])
    validate_zero_transactions(collection["transactions"], job["id"])
    raw_path = directory / "raw" / f"{filename}.json"
    shots = json.loads(raw_path.read_text())
    if not isinstance(shots, list) or any(type(shot) is not str for shot in shots):
        raise ValueError("ordered raw string list required")
    histogram = result["results"]
    if any(type(count) is not int or count <= 0 for count in histogram.values()) or dict(Counter(shots)) != histogram:
        raise ValueError("histogram differs from retained raw shots")
    created, queued, finished = (timestamp(job[key]) for key in ("created_on", "queued_at", "finished_at"))
    if not created <= queued <= finished:
        raise ValueError("job timestamps contradict execution ordering")
    collected_at = timestamp(collection["collected_utc"])
    if collected_at < finished:
        raise ValueError("raw collection precedes the provider-reported job finish")
    validate_admission(directory, campaign, bindings, created)
    validate_locked_admission(directory, campaign, created)
    intent_path = directory / "execution-intent.json"
    intent = json.loads(intent_path.read_text())
    expected_intent = {
        "schema": "qi-campaign-intent-v1",
        "plan_sha256": bindings["campaign_sha256"],
        "cases_sha256": batch["cases_sha256"],
    }
    if intent != expected_intent:
        raise ValueError("execution intent differs from approved campaign and case")
    completion_path = directory / "completion-admission.json"
    completion = json.loads(completion_path.read_text())
    expected_completion = {
        "schema": "qi-tuna-destination-one-completion-v1",
        "batch": name,
        "job": job["id"],
        "batch_job": job["batch_job_id"],
        "created_on": job["created_on"],
        "queued_at": job["queued_at"],
        "finished_at": job["finished_at"],
        "collected_utc": collection["collected_utc"],
        "execution_seconds_decimal": str(execution),
        "inputs": {
            path.relative_to(directory).as_posix(): digest(path)
            for path in (
                manifest_path,
                source_path,
                submission_path,
                result_path,
                raw_path,
                directory / "locked-admission.json",
            )
        },
    }
    if json_bytes(completion) != json_bytes(expected_completion):
        raise ValueError("completion admission differs from acquired identities, timing or raw hashes")
    result_row = cells((name, shots, list(early)))
    result_row.update(
        {
            "job": job["id"],
            "batch_job": job["batch_job_id"],
            "created_utc": created.isoformat(),
            "queued_utc": queued.isoformat(),
            "finished_utc": finished.isoformat(),
            "collected_utc": collected_at.isoformat(),
            "execution_seconds_decimal": str(execution),
            "inputs": {
                path.relative_to(run).as_posix(): digest(path)
                for path in (
                    manifest_path,
                    source_path,
                    submission_path,
                    result_path,
                    raw_path,
                    directory / "backend.json",
                    directory / "admission.json",
                    directory / "locked-admission.json",
                    intent_path,
                    completion_path,
                )
            },
        }
    )
    return result_row


def classify(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if [row["batch"] for row in rows] != list(BATCHES):
        raise ValueError("classification requires all three nominal-one fixed-order jobs")
    for row in rows:
        counts = row["joint_counts"]
        if len(counts) != 3 or any(
            len(cells) != 4 or any(type(value) is not int or value < 0 for value in cells) or sum(cells) != SHOTS
            for cells in counts
        ):
            raise ValueError("joint tables must partition all 4096 shots")
    rule = contract()
    radius = Decimal(rule["response_radius_decimal"])
    drift_radius = Decimal(rule["baseline_radius_decimal"])
    comparisons = []
    for prepared in (1,):
        before, rotated, after = rows
        for ancilla_index, qubit in enumerate(ANCILLAS):
            for cell in range(4):
                counts = [row["joint_counts"][ancilla_index][cell] for row in (before, rotated, after)]
                difference = Decimal(2 * counts[1] - counts[0] - counts[2]) / (2 * SHOTS)
                drift = Decimal(counts[2] - counts[0]) / SHOTS
                lower, upper = max(Decimal(-1), difference - radius), min(Decimal(1), difference + radius)
                baseline_admitted = abs(drift) + drift_radius <= MARGIN
                sensitivity = [
                    {
                        "assumed_transient_bound_decimal": bound,
                        "lower_decimal": str(max(Decimal(-1), lower - Decimal(bound))),
                        "upper_decimal": str(min(Decimal(1), upper + Decimal(bound))),
                        "verified": False,
                    }
                    for bound in rule["sensitivity_drift_bounds_decimal"]
                ]
                comparisons.append(
                    {
                        "prepared_label": prepared,
                        "ancilla_qubit": qubit,
                        "early_label": cell // 2,
                        "terminal_label": cell % 2,
                        "counts_before_rotated_after": counts,
                        "difference_decimal": str(difference),
                        "interval_decimal": [str(lower), str(upper)],
                        "baseline_difference_decimal": str(drift),
                        "baseline_interval_decimal": [
                            str(max(Decimal(-1), drift - drift_radius)),
                            str(min(Decimal(1), drift + drift_radius)),
                        ],
                        "baseline_admitted": baseline_admitted,
                        "equivalent_within_margin": lower >= -MARGIN and upper <= MARGIN,
                        "departure_exceeds_margin": lower > MARGIN or upper < -MARGIN,
                        "unverified_attribution_sensitivity": sensitivity,
                    }
                )
    if not all(row["baseline_admitted"] for row in comparisons):
        outcome = "inconclusive within budget"
        reason = "The simultaneous intervals cannot certify every before/after baseline difference within the margin."
    elif any(row["departure_exceeds_margin"] for row in comparisons):
        outcome = "specified alternative supported"
        reason = "At least one selected realized predictable response contrast exceeds the margin."
    elif all(row["equivalent_within_margin"] for row in comparisons):
        outcome = "objective established within scope"
        reason = "All selected realized predictable response contrasts lie within the margin."
    else:
        outcome = "inconclusive within budget"
        reason = "The simultaneous intervals overlap the decision boundaries."
    return {
        "outcome": outcome,
        "reason": reason,
        "comparisons": comparisons,
        "contract": rule,
        "attribution_status": "unresolved",
        "physical_continuation_admitted": False,
    }


def analyze(run: Path, proposal: Path = PROPOSAL) -> dict[str, Any]:
    """Produce a refusal artifact for malformed or incomplete evidence without altering raw inputs."""
    provenance: dict[str, str] = {}
    try:
        campaign_path = run / "sequence-plan.json"
        frozen_path = proposal / "campaign.json"
        if campaign_path.read_bytes() != frozen_path.read_bytes():
            raise ValueError("campaign differs from frozen proposal")
        campaign = json.loads(campaign_path.read_text())
        expected_scope = {
            "schema": "qi-tuna-destination-one-campaign-v1",
            "circuits_total": 3,
            "shots_per_circuit": SHOTS,
            "shots_total": 3 * SHOTS,
            "provider_execution_ceiling_seconds": 900,
            "minimum_interjob_pause_seconds": 30,
            "admission_max_age_seconds": 60,
            "heartbeat_max_age_seconds": 120,
            "expected_credits": 0,
            "campaign_request_initiation_timeout_seconds": 7200,
        }
        if any(
            type(campaign.get(key)) is not type(value) or campaign[key] != value
            for key, value in expected_scope.items()
        ):
            raise ValueError("campaign scope differs from the three nominal-one jobs")
        provenance["sequence-plan.json"] = digest(campaign_path)
        marker_path = run / "campaign.json"
        marker = json.loads(marker_path.read_text())
        expected_marker = {
            "schema": "qi-campaign-v1",
            "plan_sha256": digest(campaign_path),
            "batches": {batch["name"]: batch["cases_sha256"] for batch in campaign["batches"]},
        }
        if marker != expected_marker:
            raise ValueError("native campaign marker differs from sequence plan")
        provenance["campaign.json"] = digest(marker_path)
        binding = campaign["analysis_contract"]
        note = ROOT / "docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md"
        expected_binding = {
            "file": Path(__file__).relative_to(ROOT).as_posix(),
            "sha256": digest(Path(__file__)),
            "mathematical_note": {"file": note.relative_to(ROOT).as_posix(), "sha256": digest(note)},
        }
        if binding != expected_binding:
            raise ValueError("campaign analyzer binding differs")
        batches = campaign["batches"]
        if [batch["name"] for batch in batches] != list(BATCHES):
            raise ValueError("campaign order differs from fixed statistical design")
        bindings, approval = validate_approval(run, campaign)
        for name in (
            "approval.json",
            "written-case-at-approval.md",
            "decision-at-approval.json",
            "terms-at-approval.json",
            "execution-window.json",
        ):
            provenance[name] = digest(run / name)
        rows = ordered_map(validate_batch, [(run, proposal, batch, campaign, bindings, approval) for batch in batches])
        if len({row["job"] for row in rows}) != 3 or len({row["batch_job"] for row in rows}) != 3:
            raise ValueError("job identities repeat across the campaign")
        for before, after in zip(rows, rows[1:], strict=False):
            if timestamp(after["created_utc"]) < timestamp(before["finished_utc"]) + dt.timedelta(seconds=30):
                raise ValueError("successor job violates preceding completion plus the minimum 30-second pause")
            if timestamp(after["created_utc"]) < timestamp(before["collected_utc"]):
                raise ValueError("successor job was created before the preceding job's raw collection")
        report = classify(rows)
        report["jobs"] = rows
        for row in rows:
            provenance.update(row["inputs"])
    except FileNotFoundError:
        report = {
            "outcome": "implementation route unavailable",
            "reason": "A required acquisition artifact is absent.",
            "attribution_status": "unresolved",
            "physical_continuation_admitted": False,
        }
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, ArithmeticError) as error:
        report = {
            "outcome": "protocol inadmissible",
            "reason": str(error),
            "attribution_status": "unresolved",
            "physical_continuation_admitted": False,
        }
    report.update(
        {
            "schema": "qi-destination-one-predictable-response-analysis-v1",
            "inputs": provenance,
            "analyzer_sha256": digest(Path(__file__)),
            "retry_authorized": False,
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    report = analyze(arguments.run)
    content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained destination analysis differs from byte replay")
    else:
        with arguments.out.open("x") as destination:
            destination.write(content)
    print(report["outcome"])
    if report["outcome"] in {"protocol inadmissible", "implementation route unavailable"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
