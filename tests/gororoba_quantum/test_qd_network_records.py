"""Bounded synthetic records exercise scientific denominators, provenance, and admission failures."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import qd_network_records as records

REVISION = "1" * 40
FRAMES = {"1100": (1, 0), "0011": (1, 0), "1001": (1, 1), "0110": (1, 1)}
INPUTS = ("+Z", "-Z", "+X", "-X", "+Y", "-Y")


def check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def evidence(status: str = "documented") -> dict[str, Any]:
    return {
        "status": status,
        "reference": "synthetic-contract.json" if status == "documented" else None,
        "sha256": hashlib.sha256(b"synthetic contract").hexdigest() if status == "documented" else None,
        "reason": None if status == "documented" else "unresolved synthetic condition",
    }


def cell(label: str, basis: str, attempts: int = 80, accepted: int = 40, correct: int | None = None) -> dict[str, Any]:
    """Exact counts from the stated partial-analyzer convention; all chosen fixtures divide into four branches."""
    if correct is None:
        correct = accepted
    rows = []
    for pattern, (x, z) in FRAMES.items():
        flip = {"X": z, "Y": x ^ z, "Z": x}[basis]
        raw_correct = (0 if label[0] == "+" else 1) ^ flip
        right = correct // 4 if basis == label[1] else accepted // 8
        wrong = accepted // 4 - right
        for raw, count in ((raw_correct, right), (1 - raw_correct, wrong)):
            if count:
                rows.append(
                    {
                        "bell_pattern": pattern,
                        "receiver_pattern": [1 - raw, raw],
                        "resource_herald": True,
                        "count": count,
                    }
                )
    if attempts > accepted:
        rows.append(
            {"bell_pattern": "1000", "receiver_pattern": [0, 0], "resource_herald": True, "count": attempts - accepted}
        )
    return {
        "setting_id": f"b0:{label}:{basis}",
        "block_id": "b0",
        "calibration_id": "calibration-0",
        "input_label": label,
        "analyzer_basis": basis,
        "expected_configuration_id": f"configuration:{label}:{basis}",
        "applied_configuration_id": f"configuration:{label}:{basis}",
        "attempts": {
            "value": attempts,
            "population": "source_trigger",
            "status": "modeled",
            "source": "synthetic fixed-trigger construction",
            "reason": "exact expected counts of the specified ideal instrument",
        },
        "reported_count": attempts,
        "anomalies": {"duplicates": 0, "unmatched": 0, "missing": 0},
        "outcomes": rows,
    }


def fixture() -> tuple[dict[str, Any], bytes, bytes, bytes]:
    raw, payload = b"synthetic raw source", b"synthetic payload"
    case = records.case_template(REVISION)
    case["joint_platform_id"] = "synthetic-joint-platform"
    case["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    case_bytes = encoded(case)
    value = {
        "schema": "qd-network-joint-v1",
        "data_origin": "synthetic",
        "representation": "joint_histogram",
        "protocol": "teleportation_A_to_B",
        "protocol_revision": REVISION,
        "case_sha256": hashlib.sha256(case_bytes).hexdigest(),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "raw_result_sha256": hashlib.sha256(raw).hexdigest(),
        "joint_job_id": "synthetic-joint-job",
        "joint_platform_id": "synthetic-joint-platform",
        "apparatus_ids": ["qpu:ascella", "qpu:belenos"],
        "route_id": "synthetic-route",
        "frame_convention": "receiver_byproduct_Xx_Zz",
        "processing_status": "raw_detector_counts",
        "processing_chain": [],
        "evidence": dict.fromkeys(records.ASSUMPTIONS),
        "block_ids": ["b0"],
        "cells": [cell(label, basis) for label in INPUTS for basis in ("X", "Y", "Z")],
    }
    return value, case_bytes, raw, payload


def test_complete_ideal_joint_histogram_keeps_rejections_and_matching_denominators() -> None:
    value, _, _, _ = fixture()
    report = records.analyze_joint(value)
    check(report["complete_18_cells_per_block"], "the full Cartesian input/analyzer bank is complete")
    check(not report["partial"], "the ideal fixture is not partial")
    scores = report["scores"]
    check(scores["equal_prior_success_weighted_fidelity"] == 1.0, "ideal success-weighted fidelity")
    check(scores["mean_conditional_fidelity"] == 1.0, "all six conditional fidelities")
    check(scores["equal_prior_success_probability"] == 0.5, "partial analyzer succeeds in half of attempts")
    check(all(row["matching_attempts"] == 80 for row in scores["per_input"].values()), "all-basis totals leaked in")
    for row in report["cells"]:
        check(sum(row["rejection_counts"].values()) + row["eligible_outputs"] == row["reported_count"], "conservation")
        check(row["bell_branches"]["1000"]["recorded"] == 40, "rejected Bell branches are retained")
        check(len(row["joint_outcomes"]) > 4, "raw accepted and rejected outcomes remain present")
    check(report["quantum_certificate"] is None, "synthetic scores cannot produce a certificate")


def test_product_resource_zero_success_input_has_the_exact_global_classical_score() -> None:
    value, _, _, _ = fixture()
    rates = {"+Z": (0, 0), "-Z": (80, 80), "+X": (40, 20), "-X": (40, 20), "+Y": (40, 20), "-Y": (40, 20)}
    value["cells"] = [cell(label, basis, 160, *rates[label]) for label in INPUTS for basis in ("X", "Y", "Z")]
    scores = records.analyze_joint(value)["scores"]
    check(scores["per_input"]["+Z"]["conditional_fidelity"] is None, "zero success has no conditional fidelity")
    check(scores["mean_conditional_fidelity"] is None, "do not silently omit the zero-success input")
    check(scores["equal_prior_success_weighted_fidelity"] == 2 / 3, "product resource reaches classical bound")
    check(scores["equal_prior_success_probability"] == 0.25, "global resource-dependent success probability")


def test_unequal_attempts_separate_pooled_and_equal_prior_estimands() -> None:
    value, _, _, _ = fixture()
    designs = {label: (80, 40, 20) for label in INPUTS}
    designs["+Z"] = (160, 80, 80)
    designs["-Z"] = (80, 40, 0)
    value["cells"] = [cell(label, basis, *designs[label]) for label in INPUTS for basis in ("X", "Y", "Z")]
    scores = records.analyze_joint(value)["scores"]
    check(scores["pooled_conditional_fidelity"] == 4 / 7, "pooled acquisition score")
    check(scores["equal_prior_success_weighted_fidelity"] == 0.5, "equal-prior score uses attempts per input")
    check(scores["confidence_interval"] is None, "weighted ratios need their own inferential contract")
    for row in value["cells"]:
        if row["analyzer_basis"] != row["input_label"][1]:
            row["attempts"]["value"] *= 100
    check(records.analyze_joint(value)["scores"] == scores, "nonmatching-axis attempts cannot alter fidelity")


def test_zero_global_success_has_zero_probability_and_undefined_fidelity() -> None:
    value, _, _, _ = fixture()
    value["cells"] = [cell(label, basis, accepted=0, correct=0) for label in INPUTS for basis in ("X", "Y", "Z")]
    scores = records.analyze_joint(value)["scores"]
    check(scores["equal_prior_success_probability"] == 0.0, "zero successes still give a success probability")
    check(scores["equal_prior_success_weighted_fidelity"] is None, "fidelity is undefined on an empty accepted branch")


def test_missing_cell_or_whole_declared_block_remains_partial() -> None:
    value, _, _, _ = fixture()
    value["cells"] = [row for row in value["cells"] if (row["input_label"], row["analyzer_basis"]) != ("+Z", "Z")]
    report = records.analyze_joint(value)
    check(report["partial"], "missing matching endpoint")
    check(report["scores"]["equal_prior_success_weighted_fidelity"] is None, "missing matching denominator")
    value, _, _, _ = fixture()
    value["block_ids"].append("missing-block")
    report = records.analyze_joint(value)
    check(len(report["blocks"]["missing-block"]["missing_cells"]) == 18, "an absent planned block stays visible")


@pytest.mark.parametrize("mode", ["unavailable", "zero"])
def test_unavailable_or_zero_attempts_preserve_descriptive_outcomes(mode: str) -> None:
    value, _, _, _ = fixture()
    target = next(row for row in value["cells"] if row["input_label"] == "+Z" and row["analyzer_basis"] == "Z")
    if mode == "unavailable":
        target["attempts"].update(value=None, status="unavailable", reason="source-trigger count not exported")
    else:
        target["attempts"]["value"] = 0
        target["outcomes"] = []
        target["reported_count"] = 0
    report = records.analyze_joint(value)
    check(report["scores"]["equal_prior_success_weighted_fidelity"] is None, "attempt count is not substituted")
    check("attempts" in report["scores"]["equal_prior_success_weighted_reason"], "undefined estimate states why")


def test_per_block_attempts_and_calibration_identities_survive_aggregation() -> None:
    value, _, _, _ = fixture()
    second = copy.deepcopy(value["cells"])
    for row in second:
        row["setting_id"] = row["setting_id"].replace("b0:", "b1:")
        row["block_id"] = "b1"
        row["calibration_id"] = "calibration-1"
    value["block_ids"].append("b1")
    value["cells"].extend(second)
    report = records.analyze_joint(value)
    check(report["scores"]["per_input"]["+Z"]["matching_attempts"] == 160, "sum only matching cells across blocks")
    check(report["blocks"]["b1"]["calibration_ids"] == ["calibration-1"], "retain distinct calibration epochs")
    check(not report["physical_claim_admitted"], "pooling blocks does not establish a fixed physical channel")


@pytest.mark.parametrize("bad", [True, -1, 0.5, float("nan"), float("inf"), 1 << 63])
def test_counts_reject_bool_fraction_nonfinite_and_out_of_range_values(bad: object) -> None:
    value, _, _, _ = fixture()
    value["cells"][0]["outcomes"][0]["count"] = bad
    with pytest.raises(records.NetworkRecordError, match="integer"):
        records.parse_joint_record(value)


@pytest.mark.parametrize("population", ["detection_event", "photon_filtered_sample", "requested_cap", "billing"])
def test_provider_samples_or_limits_cannot_substitute_for_source_triggers(population: str) -> None:
    value, _, _, _ = fixture()
    value["cells"][0]["attempts"]["population"] = population
    with pytest.raises(records.NetworkRecordError, match="source_trigger"):
        records.parse_joint_record(value)


@pytest.mark.parametrize(
    "field,bad", [("bell_pattern", "110"), ("receiver_pattern", [True, 0]), ("resource_herald", 1)]
)
def test_joint_outcome_domain_is_strict(field: str, bad: object) -> None:
    value, _, _, _ = fixture()
    value["cells"][0]["outcomes"][0][field] = bad
    with pytest.raises(records.NetworkRecordError):
        records.parse_joint_record(value)


@pytest.mark.parametrize("fault", ["outcome", "cell", "block", "count", "attempts", "marginals", "unknown", "revision"])
def test_duplicate_marginal_and_nonconserving_records_are_rejected(fault: str) -> None:
    value, _, _, _ = fixture()
    if fault == "outcome":
        value["cells"][0]["outcomes"].append(copy.deepcopy(value["cells"][0]["outcomes"][0]))
    elif fault == "cell":
        value["cells"].append(copy.deepcopy(value["cells"][0]))
    elif fault == "block":
        value["block_ids"].append("b0")
    elif fault == "count":
        value["cells"][0]["reported_count"] += 1
    elif fault == "attempts":
        value["cells"][0]["attempts"]["value"] = 1
    elif fault == "marginals":
        value["representation"] = "independent_job_marginals"
    elif fault == "unknown":
        value["inference_approved"] = True
    else:
        value["protocol_revision"] = "main"
    with pytest.raises(records.NetworkRecordError):
        records.parse_joint_record(value)


def test_changed_configuration_anomalies_and_processing_block_physical_inference() -> None:
    value, _, _, _ = fixture()
    value["processing_status"] = "processed_counts"
    value["processing_chain"] = ["probability_to_counts"]
    value["cells"][0]["calibration_id"] = "changed-calibration"
    value["cells"][0]["applied_configuration_id"] = "predecessor-configuration"
    value["cells"][0]["anomalies"] = {"duplicates": 1, "unmatched": 2, "missing": 3}
    report = records.analyze_joint(value)
    issues = " ".join(report["integrity_and_scope_issues"])
    for phrase in (
        "calibration changes",
        "configuration identities differ",
        "duplicates",
        "unmatched",
        "missing",
        "processed",
    ):
        check(phrase in issues, f"preserve {phrase}")
    check(report["scores"]["equal_prior_success_weighted_fidelity"] == 1.0, "descriptor score remains visible")
    check(not report["physical_claim_admitted"], "a high descriptor score does not qualify the instrument")


def test_populated_evidence_descriptors_never_certify_a_physical_link() -> None:
    value, _, _, _ = fixture()
    value["data_origin"] = "measured"
    value["evidence"] = {name: evidence() for name in records.ASSUMPTIONS}
    for row in value["cells"]:
        row["attempts"].update(status="observed", reason=None)
    report = records.analyze_joint(value)
    check(report["unresolved_assumptions"] == [], "all assumptions are declared documented")
    check(not report["physical_claim_admitted"], "declarations cannot certify entanglement or teleportation")
    check(not report["raw_to_normalized_derivation_verified"], "there is no provider normalization adapter")
    value["evidence"]["physical_route"] = True
    with pytest.raises(records.NetworkRecordError):
        records.parse_joint_record(value)


def test_raw_byte_binding_verifies_identity_but_not_normalized_data_derivation() -> None:
    value, case, raw, payload = fixture()
    unverified = records.verify_bindings(value)
    check(all(item["status"] == "unverified" for item in unverified["bindings"].values()), "no source bytes supplied")
    report = records.verify_bindings(value, case_bytes=case, raw_result_bytes=raw, payload_bytes=payload)
    check(all(item["status"] == "byte_verified" for item in report["bindings"].values()), "all three digests match")
    check(not report["raw_to_normalized_derivation_verified"], "hash equality does not establish count transformation")
    check(not report["physical_claim_admitted"], "physical support remains separate")
    with pytest.raises(records.NetworkRecordError, match="raw_result bytes differ"):
        records.verify_bindings(value, raw_result_bytes=raw + b"changed")


@pytest.mark.parametrize(
    "field,bad",
    [
        ("source_revision", "2" * 40),
        ("protocol", "teleportation_B_to_A"),
        ("joint_platform_id", "other-joint-platform"),
        ("output_capability", "O1"),
    ],
)
def test_byte_bound_case_must_match_the_declared_protocol_scope(field: str, bad: str) -> None:
    value, case_bytes, _, _ = fixture()
    case = json.loads(case_bytes)
    case[field] = bad
    altered = encoded(case)
    value["case_sha256"] = hashlib.sha256(altered).hexdigest()
    with pytest.raises(records.NetworkRecordError, match="bound case"):
        records.verify_bindings(value, case_bytes=altered)


def test_planned_block_binding_preserves_partial_acquisition_and_numeric_targets() -> None:
    value, case_bytes, _, _ = fixture()
    case = records.decode_json(case_bytes)
    case["statistical_case"] = {
        "estimand": "uniform_six_success_weighted_fidelity",
        "alpha": 0.002,
        "systematic_allowance": 0.02,
        "stopping_rule": "fixed_attempts",
        "attempts_per_cell": 100,
        "block_ids": ["b0", "b1"],
    }
    bound = encoded(case)
    value["case_sha256"] = hashlib.sha256(bound).hexdigest()
    with pytest.raises(records.NetworkRecordError, match="block identities"):
        records.verify_bindings(value, case_bytes=bound)
    value["block_ids"].append("b1")
    verification = records.verify_bindings(value, case_bytes=bound)
    check(verification["attempt_targets"]["attempts_per_cell"] == 100, "retained prospective numeric target")
    for row in verification["attempt_targets"]["recorded_cells"]:
        check(row["difference_from_target"] == -20, "short acquisition remains descriptive")
    report = records.analyze_joint(value)
    check(report["partial"], "planned but unreturned block remains missing")
    check(not verification["execution_admitted"], "a target receipt grants no new execution authority")


def test_case_template_preserves_unknowns_and_requires_exact_evidence_values() -> None:
    case = records.case_template(REVISION)
    report = records.assess_case(case)
    check(report["structurally_valid"], "draft schema is valid with unknown capabilities")
    check(not report["review_ready"], "unknown capabilities remain pending")
    check("physical_route_evidence" in report["missing_or_unresolved"], "physical access is unresolved")
    case["physical_route_evidence"] = evidence("unavailable")
    check(not records.assess_case(case)["review_ready"], "documented limitation cannot become capability")
    case["physical_route_evidence"] = "available"
    with pytest.raises(records.NetworkRecordError):
        records.assess_case(case)


def test_complete_case_declarations_allow_review_only() -> None:
    case = records.case_template(REVISION)
    for name in records._CASE_EVIDENCE:
        case[name] = evidence()
    case["joint_platform_id"] = "synthetic-joint-platform"
    case["input_ensemble"]["physical_preparation_evidence"] = evidence()
    case["input_ensemble"]["accepted_multiphoton_bound"] = 0.0
    case["statistical_case"] = {
        "estimand": "uniform_six_success_weighted_fidelity",
        "alpha": 0.002,
        "systematic_allowance": 0.02,
        "stopping_rule": "fixed_attempts",
        "attempts_per_cell": 100,
        "block_ids": ["b0"],
    }
    case.update(max_jobs=1, max_seconds=300, max_credits=1.0, payload_sha256="2" * 64)
    report = records.assess_case(case)
    check(report["review_ready"], "complete declarations can enter physical review")
    check(not report["execution_admitted"] and not report["physical_claim_admitted"], "review is not authorization")
    case["max_jobs"] = True
    with pytest.raises(records.NetworkRecordError):
        records.assess_case(case)


@pytest.mark.parametrize(
    "data",
    [
        b'{"x":1,"x":2}',
        b'{"x":{"y":1,"y":2}}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":1e999}',
        b"[]",
        '{"x":1}'.encode("utf-16"),
        b'{"x":' + b"[" * 3000 + b"0" + b"]" * 3000 + b"}",
    ],
)
def test_json_boundary_rejects_ambiguous_or_nonfinite_input(data: bytes, tmp_path: Path) -> None:
    path = tmp_path / "input.json"
    path.write_bytes(data)
    with pytest.raises(records.NetworkRecordError):
        records.load_json(path)
    with pytest.raises(records.NetworkRecordError):
        records.decode_json(data)
