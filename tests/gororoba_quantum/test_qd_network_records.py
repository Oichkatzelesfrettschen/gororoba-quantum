"""Bounded synthetic records exercise scientific denominators, provenance, and admission failures."""

from __future__ import annotations

import copy
import hashlib
import json
import re
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
        ("claim_level", "C6"),
        ("payload_sha256", "3" * 64),
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


def complete_case() -> dict[str, Any]:
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
    return case


def test_complete_case_declarations_allow_review_only() -> None:
    case = complete_case()
    report = records.assess_case(case)
    check(report["review_ready"], "complete declarations can enter physical review")
    check(report["missing_or_unresolved"] == [] and report["unsupported_scope"] == [], "nothing is outstanding")
    check(not report["execution_admitted"] and not report["physical_claim_admitted"], "review is not authorization")
    case["max_jobs"] = True
    with pytest.raises(records.NetworkRecordError):
        records.assess_case(case)


@pytest.mark.parametrize(
    "change,fragment",
    [
        ({"claim_level": "C6"}, "C3 case only"),
        ({"claim_level": "C0"}, "C3 case only"),
        ({"output_capability": "O1"}, "surviving, heralded"),
        ({"output_capability": "O3"}, "surviving, heralded"),
    ],
)
def test_a_documented_case_outside_the_terminal_c3_scope_is_not_review_ready(
    change: dict[str, str], fragment: str
) -> None:
    case = complete_case()
    case.update(change)
    report = records.assess_case(case)
    check(not report["review_ready"], "version 1 reviews a terminal single-hop C3 case only")
    check(report["missing_or_unresolved"] == [], "every declaration is present")
    check(len(report["unsupported_scope"]) == 1 and fragment in report["unsupported_scope"][0], "scope reason")


def test_each_missing_case_field_blocks_review_readiness_by_name() -> None:
    expectations: dict[str, Any] = {
        "joint_platform_id": None,
        "statistical_case": None,
        "max_jobs": None,
        "max_seconds": None,
        "max_credits": None,
        "payload_sha256": None,
        "physical_route_evidence": evidence("unknown"),
        "approval_record": None,
    }
    for name, absent in expectations.items():
        case = complete_case()
        case[name] = absent
        report = records.assess_case(case)
        check(not report["review_ready"] and report["missing_or_unresolved"] == [name], f"{name} is required")
    case = complete_case()
    case["input_ensemble"]["accepted_multiphoton_bound"] = None
    report = records.assess_case(case)
    check(not report["review_ready"], "the multiphoton bound is required")
    check(report["missing_or_unresolved"] == ["accepted_multiphoton_bound"], "the bound is named")
    case = complete_case()
    case["input_ensemble"]["physical_preparation_evidence"] = None
    report = records.assess_case(case)
    check(report["missing_or_unresolved"] == ["physical_preparation_evidence"], "preparation evidence is required")


def _case_change(path: str, value: object) -> dict[str, Any]:
    case = complete_case()
    target: Any = case
    *parents, leaf = path.split(".")
    for key in parents:
        target = target[key]
    target[leaf] = value
    return case


@pytest.mark.parametrize(
    "path,value,fragment",
    [
        ("schema", "qd-network-case-v2", "case.schema"),
        ("status", "approved", "case.status"),
        ("admission", "open", "case.admission"),
        ("protocol", "teleportation_C_to_D", "case.protocol"),
        ("claim_level", "C7", "case.claim_level"),
        ("local_platforms", ["qpu:ascella"], "Ascella and Belenos"),
        ("local_platforms", ["qpu:ascella", "qpu:ascella"], "duplicate"),
        ("output_measurements", ["X", "Y"], "['X', 'Y', 'Z']"),
        ("base_setting_cells", 17, "18 base setting cells"),
        ("logical_frame_convention", "other", "case.logical_frame_convention"),
        ("output_capability", "O9", "case.output_capability"),
        ("input_ensemble.name", "uniform_pauli_four", "case.input_ensemble.name"),
        ("input_ensemble.probabilities", ["1/6"] * 5 + ["1/7"], "'1/6' strings"),
        ("input_ensemble.probabilities", [1 / 6] * 6, "'1/6' strings"),
        ("input_ensemble.accepted_multiphoton_bound", 1.5, "accepted_multiphoton_bound"),
        ("input_ensemble.accepted_multiphoton_bound", -0.1, "accepted_multiphoton_bound"),
        ("input_ensemble.accepted_multiphoton_bound", float("nan"), "accepted_multiphoton_bound"),
        ("input_ensemble.accepted_multiphoton_bound", True, "accepted_multiphoton_bound"),
        ("max_jobs", 0, "case.max_jobs must be positive"),
        ("max_jobs", -1, "case.max_jobs"),
        ("max_seconds", 0, "case.max_seconds must be positive"),
        ("max_seconds", -1.0, "case.max_seconds"),
        ("max_seconds", float("inf"), "case.max_seconds"),
        ("max_credits", -0.5, "case.max_credits"),
        ("max_credits", "1", "case.max_credits"),
        ("payload_sha256", "ABC", "case.payload_sha256"),
        ("statistical_case.estimand", "pooled_fidelity", "estimand"),
        ("statistical_case.alpha", 0.0, "alpha"),
        ("statistical_case.alpha", 1.0, "alpha"),
        ("statistical_case.alpha", 2.0, "alpha"),
        ("statistical_case.systematic_allowance", 1.5, "systematic_allowance"),
        ("statistical_case.systematic_allowance", -0.01, "systematic_allowance"),
        ("statistical_case.stopping_rule", "sequential", "stopping_rule"),
        ("statistical_case.attempts_per_cell", 0, "attempts_per_cell must be positive"),
        ("statistical_case.attempts_per_cell", 1.5, "attempts_per_cell"),
        ("statistical_case.block_ids", [], "at least one block"),
        ("statistical_case.block_ids", ["b0", "b0"], "duplicate"),
        ("statistical_case.block_ids", ["b0", ""], "nonempty strings"),
        (
            "physical_route_evidence",
            {"status": "documented", "reference": "r", "sha256": None, "reason": None},
            "together",
        ),
        (
            "physical_route_evidence",
            {"status": "documented", "reference": None, "sha256": "1" * 64, "reason": None},
            "together",
        ),
        (
            "physical_route_evidence",
            {"status": "documented", "reference": None, "sha256": None, "reason": None},
            "needs a reference",
        ),
        (
            "physical_route_evidence",
            {"status": "unavailable", "reference": None, "sha256": None, "reason": None},
            "needs a reason",
        ),
        ("physical_route_evidence", {"status": "unknown", "reference": None, "sha256": None, "reason": "  "}, "reason"),
        ("physical_route_evidence", {"status": "assumed", "reference": None, "sha256": None, "reason": "x"}, "status"),
        (
            "physical_route_evidence",
            {"status": "documented", "reference": "r", "sha256": "xyz", "reason": None},
            "sha256",
        ),
        ("physical_route_evidence", {"status": "documented", "reference": "r", "sha256": "1" * 64}, "missing keys"),
        ("calibration_bundle", "documented", "must be an object"),
    ],
)
def test_case_fields_outside_the_version_one_domain_are_rejected(path: str, value: object, fragment: str) -> None:
    with pytest.raises(records.NetworkRecordError, match=re.escape(fragment)):
        records.assess_case(_case_change(path, value))


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
        b'{"x":"\xff"}',
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


def _first(value: dict[str, Any], label: str, basis: str) -> dict[str, Any]:
    return next(row for row in value["cells"] if row["input_label"] == label and row["analyzer_basis"] == basis)


def _set_outcomes(row: dict[str, Any], outcomes: list[tuple[str, list[int], bool, int]], attempts: int = 80) -> None:
    row["outcomes"] = [
        {"bell_pattern": pattern, "receiver_pattern": receiver, "resource_herald": herald, "count": count}
        for pattern, receiver, herald, count in outcomes
    ]
    row["reported_count"] = sum(item[3] for item in outcomes)
    row["attempts"]["value"] = attempts


def test_every_rejection_category_counts_only_its_own_outcomes() -> None:
    value, _, _, _ = fixture()
    row = _first(value, "+Z", "Z")
    _set_outcomes(
        row,
        [
            ("1100", [1, 0], False, 3),  # resource herald failed, otherwise a valid accepted pattern
            ("1100", [0, 0], True, 4),  # Bell pattern accepted, receiver silent
            ("0000", [1, 0], True, 5),  # receiver click behind a pattern outside the partial analyzer
            ("1100", [1, 1], True, 6),  # two photons in two modes
            ("0011", [2, 0], True, 7),  # two photons in one mode
            ("1100", [1, 0], True, 8),  # accepted; frame (1, 0) decodes Z bit 0 xor 1, wrong for +Z
            ("1001", [0, 1], True, 9),  # accepted; frame (1, 1) decodes Z bit 1 xor 1 = 0, correct for +Z
            ("0000", [0, 0], False, 10),  # a failed herald outranks the Bell-pattern rejection
        ],
    )
    cell_report = next(
        item for item in records.analyze_joint(value)["cells"] if item["setting_id"] == row["setting_id"]
    )
    check(
        cell_report["rejection_counts"]
        == {
            "resource_herald_failed": 13,
            "bell_pattern_rejected": 5,
            "receiver_no_click": 4,
            "receiver_multiple_occupation": 13,
        },
        f"each outcome lands in exactly one rejection category: {cell_report['rejection_counts']}",
    )
    check(cell_report["eligible_outputs"] == 17, "only the accepted rows enter the matching denominator")
    check(cell_report["bell_branches"]["1100"] == {"recorded": 21, "accepted": 8, "correct": 0}, "frame 1100")
    check(cell_report["bell_branches"]["1001"] == {"recorded": 9, "accepted": 9, "correct": 9}, "frame 1001")
    check(cell_report["bell_branches"]["0000"] == {"recorded": 15, "accepted": 0, "correct": 0}, "outside the analyzer")
    check(cell_report["conditional_fidelity"] == 9 / 17, "wrong-frame outcomes count as incorrect")


def test_a_failed_resource_herald_removes_the_cell_from_the_accepted_branch() -> None:
    value, _, _, _ = fixture()
    for row in value["cells"]:
        if row["input_label"] in ("+Z", "-Z"):
            for outcome in row["outcomes"]:
                outcome["resource_herald"] = False
    report = records.analyze_joint(value)
    for row in report["cells"]:
        if row["input_label"] in ("+Z", "-Z"):
            check(row["eligible_outputs"] == 0, "no output is accepted without the resource herald")
            check(row["rejection_counts"]["resource_herald_failed"] == row["reported_count"], "all rows fail")
    scores = report["scores"]
    check(scores["per_input"]["+Z"]["accepted"] == 0, "the failed input has no accepted output")
    check(scores["equal_prior_success_weighted_fidelity"] == 1.0, "remaining inputs keep fidelity one")
    check(scores["equal_prior_success_probability"] == 4 * 0.5 / 6, "two inputs contribute zero success")
    check(scores["mean_conditional_fidelity"] is None, "an input without accepted outputs has no conditional fidelity")


def test_nonmatching_analyzer_cells_report_no_fidelity_and_no_correct_counts() -> None:
    value, _, _, _ = fixture()
    report = records.analyze_joint(value)
    for row in report["cells"]:
        matching = row["analyzer_basis"] == row["input_label"][1]
        check(row["matching_basis"] == matching, "matching basis")
        if matching:
            check(row["conditional_fidelity"] == 1.0 and row["correct_outputs"] == 20 + 20, "matching cell")
            check(all(branch["correct"] is not None for branch in row["bell_branches"].values()), "branch counts")
        else:
            check(row["conditional_fidelity"] is None and row["correct_outputs"] is None, "no fidelity off axis")
            check(all(branch["correct"] is None for branch in row["bell_branches"].values()), "no branch score")


def test_measured_records_cannot_take_a_per_attempt_rate_from_modeled_attempts() -> None:
    value, _, _, _ = fixture()
    synthetic = records.analyze_joint(value)
    value["data_origin"] = "measured"
    report = records.analyze_joint(value)
    row = next(item for item in report["cells"] if item["setting_id"] == "b0:+Z:Z")
    check(row["success_per_attempt"] is None, "a modeled denominator gives no measured per-attempt rate")
    check("modeled attempts do not establish a measured" in row["success_per_attempt_reason"], "cell reason")
    scores = report["scores"]
    check(scores["equal_prior_success_weighted_fidelity"] is None, "no measured success weighting")
    check(scores["equal_prior_success_probability"] is None, "no measured success probability")
    check(
        "modeled attempts cannot establish measured success weighting" in scores["equal_prior_success_weighted_reason"],
        "reason",
    )
    check(scores["per_input"]["+Z"]["matching_attempts"] is None, "matching attempts stay unresolved")
    synthetic_row = next(item for item in synthetic["cells"] if item["setting_id"] == "b0:+Z:Z")
    check(synthetic_row["success_per_attempt"] == 0.5, "the same counts keep their modeled rate when synthetic")
    check(synthetic["scores"]["equal_prior_success_weighted_fidelity"] == 1.0, "synthetic weighting")


def test_mixed_attempt_statuses_leave_the_weighted_estimand_undefined() -> None:
    value, _, _, _ = fixture()
    second = copy.deepcopy(value["cells"])
    for row in second:
        row["setting_id"] = row["setting_id"].replace("b0:", "b1:")
        row["block_id"] = "b1"
    value["block_ids"].append("b1")
    value["cells"].extend(second)
    check(records.analyze_joint(value)["scores"]["equal_prior_success_weighted_fidelity"] == 1.0, "uniform statuses")
    _first(value, "+Z", "Z")["attempts"].update(status="observed", reason=None)
    scores = records.analyze_joint(value)["scores"]
    check(scores["equal_prior_success_weighted_fidelity"] is None, "one observed cell among modeled ones")
    reason = scores["equal_prior_success_weighted_reason"]
    check("+Z: matching cells mix observed, modeled, or unavailable attempt statuses" in reason, reason)
    check(scores["per_input"]["+Z"]["matching_attempts"] is None, "no pooled attempts across statuses")
    check(scores["per_input"]["-Z"]["matching_attempts"] == 160, "unaffected inputs keep their attempts")


@pytest.mark.parametrize(
    "fault,match",
    [
        ("count", "conserve reported_count"),
        ("attempts", "exceed source triggers"),
        ("blocks", "undeclared block"),
        ("apparatus", "apparatus_ids"),
        ("apparatus-extra", "apparatus_ids"),
        ("setting", "duplicate setting"),
        ("identity", "duplicate setting or block/input/analyzer"),
        ("empty-blocks", "at least one acquisition block"),
        ("origin", "data_origin"),
        ("digest", "case_sha256"),
        ("payload", "payload_sha256"),
        ("frame", "frame_convention"),
        ("processing", "processing_status"),
        ("job", "joint_job_id"),
        ("evidence", "evidence"),
        ("anomaly", "cell.anomalies.missing"),
        ("anomaly-key", "cell.anomalies"),
        ("input", "cell.input_label"),
        ("basis", "cell.analyzer_basis"),
        ("attempt-reason", "unavailable attempts need value null"),
        ("modeled-reason", "modeled attempts need their assumptions"),
        ("attempt-status", "cell b0:+Z:X.attempts.status"),
        ("pattern", "bell_pattern"),
        ("receiver", "receiver_pattern needs two"),
    ],
)
def test_joint_record_faults_are_rejected_with_their_own_diagnostic(fault: str, match: str) -> None:
    value, _, _, _ = fixture()
    row = value["cells"][0]
    if fault == "count":
        row["reported_count"] -= 1
    elif fault == "attempts":
        row["attempts"]["value"] = row["reported_count"] - 1
    elif fault == "blocks":
        row["block_id"] = "undeclared"
    elif fault == "apparatus":
        value["apparatus_ids"] = ["qpu:ascella"]
    elif fault == "apparatus-extra":
        value["apparatus_ids"] = ["qpu:ascella", "qpu:belenos", "qpu:other"]
    elif fault == "setting":
        value["cells"][1]["setting_id"] = row["setting_id"]
    elif fault == "identity":
        value["cells"][1].update(input_label=row["input_label"], analyzer_basis=row["analyzer_basis"])
    elif fault == "empty-blocks":
        value["block_ids"] = []
    elif fault == "origin":
        value["data_origin"] = "simulated"
    elif fault == "digest":
        value["case_sha256"] = "G" * 64
    elif fault == "payload":
        value["payload_sha256"] = "abc"
    elif fault == "frame":
        value["frame_convention"] = "sender_byproduct"
    elif fault == "processing":
        value["processing_status"] = "calibrated"
    elif fault == "job":
        value["joint_job_id"] = " "
    elif fault == "evidence":
        value["evidence"] = {"fixed_channel": None}
    elif fault == "anomaly":
        row["anomalies"]["missing"] = -1
    elif fault == "anomaly-key":
        row["anomalies"] = {"duplicates": 0, "unmatched": 0}
    elif fault == "input":
        row["input_label"] = "+W"
    elif fault == "basis":
        row["analyzer_basis"] = "W"
    elif fault == "attempt-reason":
        row["attempts"].update(status="unavailable", reason=None)
    elif fault == "modeled-reason":
        row["attempts"]["reason"] = None
    elif fault == "attempt-status":
        row["attempts"]["status"] = "estimated"
    elif fault == "pattern":
        row["outcomes"][0]["bell_pattern"] = "1100x"
    else:
        row["outcomes"][0]["receiver_pattern"] = [1, 0, 0]
    with pytest.raises(records.NetworkRecordError, match=re.escape(match)):
        records.parse_joint_record(value)


def test_a_repeated_outcome_key_is_rejected_even_when_the_counts_conserve() -> None:
    value, _, _, _ = fixture()
    row = value["cells"][0]
    _set_outcomes(row, [("1100", [1, 0], True, 5), ("1100", [1, 0], True, 5)])
    with pytest.raises(records.NetworkRecordError, match="duplicate joint outcome key"):
        records.parse_joint_record(value)
    row["outcomes"][1]["receiver_pattern"] = [0, 1]
    records.parse_joint_record(value)


def test_unavailable_identities_and_scope_limits_are_named_as_integrity_issues() -> None:
    value, _, _, _ = fixture()
    clean = records.analyze_joint(value)["integrity_and_scope_issues"]
    check(clean == ["synthetic counts are calculations, not measured evidence"], f"synthetic fixture issues: {clean}")
    value["data_origin"] = "measured"
    for row in value["cells"]:
        row["attempts"].update(status="observed", reason=None)
    check(records.analyze_joint(value)["integrity_and_scope_issues"] == [], "a complete measured record has no issue")
    _first(value, "+Z", "Z")["calibration_id"] = None
    _first(value, "-Z", "Z")["applied_configuration_id"] = None
    value["route_id"] = None
    issues = records.analyze_joint(value)["integrity_and_scope_issues"]
    check(
        issues
        == [
            "b0: calibration identity unavailable",
            "b0:-Z:Z: applied configuration is unknown",
            "the declared physical route or joint platform is unavailable",
        ],
        f"issues: {issues}",
    )
    value["route_id"] = "synthetic-route"
    value["joint_platform_id"] = None
    check(
        "the declared physical route or joint platform is unavailable"
        in records.analyze_joint(value)["integrity_and_scope_issues"],
        "joint platform",
    )
    value["block_ids"].append("empty-block")
    check(
        "empty-block: calibration identity unavailable" in records.analyze_joint(value)["integrity_and_scope_issues"],
        "a planned block without cells has no calibration identity",
    )


def test_a_cell_with_a_different_declared_configuration_is_named() -> None:
    value, _, _, _ = fixture()
    value["data_origin"] = "measured"
    for row in value["cells"]:
        row["attempts"].update(status="observed", reason=None)
    _first(value, "+X", "Y")["applied_configuration_id"] = "predecessor"
    issues = records.analyze_joint(value)["integrity_and_scope_issues"]
    check(issues == ["b0:+X:Y: frozen and applied configuration identities differ"], f"issues: {issues}")


def test_unresolved_assumptions_list_only_undocumented_evidence() -> None:
    value, _, _, _ = fixture()
    value["evidence"] = {name: evidence() for name in records.ASSUMPTIONS}
    value["evidence"]["fixed_channel"] = None
    value["evidence"]["raw_event_provenance"] = evidence("unknown")
    check(records.analyze_joint(value)["unresolved_assumptions"] == ["fixed_channel", "raw_event_provenance"], "names")


def test_block_summary_lists_each_missing_cell_and_distinct_calibrations() -> None:
    value, _, _, _ = fixture()
    value["cells"] = [row for row in value["cells"] if (row["input_label"], row["analyzer_basis"]) != ("-Y", "X")]
    _first(value, "+X", "X")["calibration_id"] = "calibration-9"
    report = records.analyze_joint(value)
    block = report["blocks"]["b0"]
    check(block["missing_cells"] == [{"input_label": "-Y", "analyzer_basis": "X"}], "one named missing cell")
    check(block["calibration_ids"] == ["calibration-0", "calibration-9"], "sorted distinct calibrations")
    check(not block["complete_18_cells"] and report["partial"], "partial")
    check(report["blocks"]["b0"]["scores"] == report["scores"], "a single block reports the same scores")


def test_binding_scope_rejects_a_case_that_names_other_blocks_or_disagrees_in_payload() -> None:
    value, case_bytes, _, _ = fixture()
    case = records.decode_json(case_bytes)
    case["payload_sha256"] = "3" * 64
    altered = encoded(case)
    value["case_sha256"] = hashlib.sha256(altered).hexdigest()
    with pytest.raises(records.NetworkRecordError, match="payload_sha256 differs"):
        records.verify_bindings(value, case_bytes=altered)
