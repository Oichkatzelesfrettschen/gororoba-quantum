"""Strict offline boundary for proposed network cases and terminal joint histograms.

Version 1 supports the uniform six Pauli inputs, X/Y/Z terminal analyzers,
and the Phi+ resource with the partial Bell analyzer of qd_network_protocol.
It preserves zero-success cells and distinct attempt populations. Declared
evidence and matching byte digests do not establish a physical quantum link,
the preparation/measurement contract, or a provider observation law. Every
report therefore leaves execution and physical-claim admission false.

The normalized joint format is a scientific interchange format, not a
Quandela response adapter. A raw-source digest match establishes identity
only: this module does not prove that normalized counts were derived from
those bytes. It performs no provider operation, inference certificate,
tomographic fit, coincidence reconstruction, or sequential-transfer analysis.

The module imports qd_network_protocol from scripts/ and so runs with both
gororoba_quantum/ and scripts/ on the import path, which scripts/qd_network_analysis.py
and the pytest configuration provide; qrng_seeds and readout_actor_family likewise
import from scripts/. qd_network_protocol is a digest-pinned producer and stays there.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

from qd_network_protocol import SIX_STATES, decode_bit, teleportation_frames

from parallel import ordered_map
from provider_counters import Counter, Population, Status, ratio

CASE_SCHEMA = "qd-network-case-v1"
JOINT_SCHEMA = "qd-network-joint-v1"
FRAME_CONVENTION = "receiver_byproduct_Xx_Zz"
AXES = ("X", "Y", "Z")
INPUTS = tuple(row[0] for row in SIX_STATES)
MATCHING = {label: (axis, 0 if sign == 1 else 1) for label, _, axis, sign in SIX_STATES}
PROTOCOLS = ("teleportation_A_to_B", "teleportation_B_to_A")
EVIDENCE_STATUSES = ("unknown", "documented", "unavailable", "conflicting")
EVIDENCE_KEYS = frozenset(("status", "reference", "sha256", "reason"))
ASSUMPTIONS = (
    "fixed_channel",
    "basis_independent_selection",
    "setting_identity",
    "input_label_isolation",
    "single_copy_input",
    "calibration_validity",
    "raw_event_provenance",
    "physical_route",
    "resource_factory",
    "bell_instrument",
)
MAX_COUNT = (1 << 63) - 1
MAX_JSON_BYTES = 64 << 20
MAX_JSON_DEPTH = 64
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_REVISION = re.compile(r"[0-9a-f]{40}\Z")
_CASE_EVIDENCE = (
    "physical_route_evidence",
    "resource_factory_evidence",
    "bell_instrument_evidence",
    "joint_record_contract",
    "attempt_denominator_contract",
    "effective_processing_contract",
    "calibration_bundle",
    "benchmark_certificate",
    "approval_record",
)


class NetworkRecordError(ValueError):
    """A JSON value falls outside the bounded version-1 record contract."""


def _object(value: object, name: str, keys: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise NetworkRecordError(f"{name} must be an object with string keys")
    actual = set(value)
    if actual != keys:
        raise NetworkRecordError(f"{name}: missing keys {sorted(keys - actual)}; unknown keys {sorted(actual - keys)}")
    return dict(value)


def _text(value: object, name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        raise NetworkRecordError(f"{name} must be a nonempty string")
    return value


def _choice(value: object, name: str, options: tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in options:
        raise NetworkRecordError(f"{name} must be one of {options}")
    return value


def _digest(value: object, name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise NetworkRecordError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _revision(value: object, name: str) -> str:
    if not isinstance(value, str) or not _REVISION.fullmatch(value):
        raise NetworkRecordError(f"{name} must be a full 40-character Git commit identifier")
    return value


def _count(value: object, name: str) -> int:
    if type(value) is not int or not 0 <= value <= MAX_COUNT:
        raise NetworkRecordError(f"{name} must be an integer in [0, {MAX_COUNT}], excluding bool")
    return value


def _number(value: object, name: str, minimum: float, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise NetworkRecordError(f"{name} must be a finite number")
    try:
        numeric = float(value)
    except OverflowError as error:
        raise NetworkRecordError(f"{name} must be finite") from error
    if not math.isfinite(numeric) or numeric < minimum or (maximum is not None and numeric > maximum):
        raise NetworkRecordError(f"{name} lies outside [{minimum}, {maximum}]")
    return numeric


def _list(value: object, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise NetworkRecordError(f"{name} must be an array")
    return value


def _strings(value: object, name: str, *, unique: bool = False) -> tuple[str, ...]:
    items = _list(value, name)
    if any(not isinstance(item, str) or not item.strip() for item in items):
        raise NetworkRecordError(f"{name} must contain nonempty strings")
    if unique and len(set(items)) != len(items):
        raise NetworkRecordError(f"{name} contains duplicate values")
    return tuple(items)


def _evidence(value: object, name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    item = _object(value, name, EVIDENCE_KEYS)
    status = _choice(item["status"], f"{name}.status", EVIDENCE_STATUSES)
    reference = _text(item["reference"], f"{name}.reference", nullable=True)
    digest = _digest(item["sha256"], f"{name}.sha256", nullable=True)
    reason = _text(item["reason"], f"{name}.reason", nullable=True)
    if (reference is None) != (digest is None):
        raise NetworkRecordError(f"{name}: evidence reference and sha256 must be supplied together")
    if status == "documented" and reference is None:
        raise NetworkRecordError(f"{name}: documented evidence needs a reference and digest")
    if status != "documented" and reason is None:
        raise NetworkRecordError(f"{name}: {status} evidence needs a reason")
    return {"status": status, "reference": reference, "sha256": digest, "reason": reason}


def _unique_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise NetworkRecordError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise NetworkRecordError(f"non-finite JSON constant {value}")


def _finite_json_float(value: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise NetworkRecordError(f"JSON number {value} exceeds the finite floating-point domain")
    return numeric


def _check_json_depth(value: dict[str, Any]) -> None:
    # Dependent traversal keeps only one iterator per ancestor, independent of array length.
    stack = [iter((value,))]
    while stack:
        try:
            item = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        if isinstance(item, dict | list):
            if len(stack) >= MAX_JSON_DEPTH:
                raise NetworkRecordError(f"JSON nesting exceeds {MAX_JSON_DEPTH} levels")
            stack.append(iter(item.values() if isinstance(item, dict) else item))


def decode_json(data: bytes) -> dict[str, Any]:
    """Decode the same bounded byte snapshot a caller hashes; reject duplicate keys and non-finite constants."""
    if not isinstance(data, bytes):
        raise NetworkRecordError("JSON source must be bytes")
    if len(data) > MAX_JSON_BYTES:
        raise NetworkRecordError(f"JSON record exceeds {MAX_JSON_BYTES} bytes")
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_json,
            parse_constant=_invalid_constant,
            parse_float=_finite_json_float,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise NetworkRecordError(f"invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise NetworkRecordError("JSON record must be an object")
    _check_json_depth(value)
    return value


def load_json(path: Path) -> dict[str, Any]:
    """Read a bounded UTF-8 JSON object; duplicate keys and non-finite constants are errors."""
    with path.open("rb") as stream:
        return decode_json(stream.read(MAX_JSON_BYTES + 1))


def case_template(source_revision: str) -> dict[str, Any]:
    """Return a non-executing draft with every unestablished physical field null."""
    return {
        "schema": CASE_SCHEMA,
        "status": "draft",
        "admission": "blocked",
        "source_repository": "Oichkatzelesfrettschen/gororoba-quantum",
        "source_revision": _revision(source_revision, "source_revision"),
        "protocol": "teleportation_A_to_B",
        "claim_level": "C3",
        "local_platforms": ["qpu:ascella", "qpu:belenos"],
        "joint_platform_id": None,
        "physical_route_evidence": None,
        "input_ensemble": {
            "name": "uniform_pauli_six",
            "probabilities": ["1/6"] * 6,
            "physical_preparation_evidence": None,
            "accepted_multiphoton_bound": None,
        },
        "output_measurements": list(AXES),
        "base_setting_cells": 18,
        "resource_factory_evidence": None,
        "bell_instrument_evidence": None,
        "logical_frame_convention": FRAME_CONVENTION,
        "output_capability": "O0",
        "joint_record_contract": None,
        "attempt_denominator_contract": None,
        "effective_processing_contract": None,
        "calibration_bundle": None,
        "benchmark_certificate": None,
        "statistical_case": None,
        "max_jobs": None,
        "max_seconds": None,
        "max_credits": None,
        "approval_record": None,
        "payload_sha256": None,
    }


def assess_case(case: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the draft and inventory declared readiness; never authorize execution or a physical claim."""
    item = _object(case, "case", frozenset(case_template("0" * 40)))
    _choice(item["schema"], "case.schema", (CASE_SCHEMA,))
    _choice(item["status"], "case.status", ("draft", "review_candidate"))
    _choice(item["admission"], "case.admission", ("blocked",))
    _text(item["source_repository"], "case.source_repository")
    _revision(item["source_revision"], "case.source_revision")
    _choice(item["protocol"], "case.protocol", PROTOCOLS)
    _choice(item["claim_level"], "case.claim_level", tuple(f"C{i}" for i in range(7)))
    platforms = _strings(item["local_platforms"], "case.local_platforms", unique=True)
    if set(platforms) != {"qpu:ascella", "qpu:belenos"}:
        raise NetworkRecordError("case.local_platforms must name Ascella and Belenos")
    _text(item["joint_platform_id"], "case.joint_platform_id", nullable=True)
    _choice(item["logical_frame_convention"], "case.logical_frame_convention", (FRAME_CONVENTION,))
    _choice(item["output_capability"], "case.output_capability", ("O0", "O1", "O2", "O3"))
    if _strings(item["output_measurements"], "case.output_measurements", unique=True) != AXES:
        raise NetworkRecordError("case.output_measurements must be ['X', 'Y', 'Z']")
    if _count(item["base_setting_cells"], "case.base_setting_cells") != 18:
        raise NetworkRecordError("the supported case has 18 base setting cells")
    ensemble = _object(
        item["input_ensemble"],
        "case.input_ensemble",
        frozenset(("name", "probabilities", "physical_preparation_evidence", "accepted_multiphoton_bound")),
    )
    _choice(ensemble["name"], "case.input_ensemble.name", ("uniform_pauli_six",))
    if ensemble["probabilities"] != ["1/6"] * 6:
        raise NetworkRecordError("case.input_ensemble.probabilities must be six exact '1/6' strings")
    evidence = {key: _evidence(item[key], f"case.{key}") for key in _CASE_EVIDENCE}
    evidence["physical_preparation_evidence"] = _evidence(
        ensemble["physical_preparation_evidence"], "case.input_ensemble.physical_preparation_evidence"
    )
    if ensemble["accepted_multiphoton_bound"] is not None:
        _number(ensemble["accepted_multiphoton_bound"], "accepted_multiphoton_bound", 0.0, 1.0)
    if item["max_jobs"] is not None and _count(item["max_jobs"], "case.max_jobs") == 0:
        raise NetworkRecordError("case.max_jobs must be positive when supplied")
    if item["max_seconds"] is not None and _number(item["max_seconds"], "case.max_seconds", 0.0) == 0:
        raise NetworkRecordError("case.max_seconds must be positive when supplied")
    if item["max_credits"] is not None:
        _number(item["max_credits"], "case.max_credits", 0.0)
    _digest(item["payload_sha256"], "case.payload_sha256", nullable=True)
    if item["statistical_case"] is not None:
        statistical = _object(
            item["statistical_case"],
            "case.statistical_case",
            frozenset(("estimand", "alpha", "systematic_allowance", "stopping_rule", "attempts_per_cell", "block_ids")),
        )
        _choice(statistical["estimand"], "estimand", ("uniform_six_success_weighted_fidelity",))
        alpha = _number(statistical["alpha"], "alpha", 0.0, 1.0)
        if not 0.0 < alpha < 1.0:
            raise NetworkRecordError("alpha must lie strictly between zero and one")
        _number(statistical["systematic_allowance"], "systematic_allowance", 0.0, 1.0)
        _choice(statistical["stopping_rule"], "stopping_rule", ("fixed_attempts",))
        if _count(statistical["attempts_per_cell"], "statistical_case.attempts_per_cell") == 0:
            raise NetworkRecordError("statistical_case.attempts_per_cell must be positive")
        if not _strings(statistical["block_ids"], "statistical_case.block_ids", unique=True):
            raise NetworkRecordError("statistical_case.block_ids must declare at least one block")
    missing = [key for key, value in evidence.items() if value is None or value["status"] != "documented"]
    missing.extend(
        key
        for key in ("joint_platform_id", "statistical_case", "max_jobs", "max_seconds", "max_credits", "payload_sha256")
        if item[key] is None
    )
    if ensemble["accepted_multiphoton_bound"] is None:
        missing.append("accepted_multiphoton_bound")
    unsupported = []
    if item["claim_level"] != "C3":
        unsupported.append("version 1 assesses a terminal single-hop C3 case only")
    if item["output_capability"] != "O0":
        unsupported.append("surviving, heralded, and persistent output require another case contract")
    return {
        "schema": "qd-network-case-assessment-v1",
        "structurally_valid": True,
        "review_ready": not missing and not unsupported,
        "execution_admitted": False,
        "physical_claim_admitted": False,
        "missing_or_unresolved": missing,
        "declared_evidence": evidence,
        "byte_verified_evidence": [],
        "unsupported_scope": unsupported,
        "admission_reason": "declarations require physical evidence review and separate execution authority",
    }


JOINT_KEYS = frozenset(
    (
        "schema",
        "data_origin",
        "representation",
        "protocol",
        "protocol_revision",
        "case_sha256",
        "payload_sha256",
        "raw_result_sha256",
        "joint_job_id",
        "joint_platform_id",
        "apparatus_ids",
        "route_id",
        "frame_convention",
        "processing_status",
        "processing_chain",
        "evidence",
        "block_ids",
        "cells",
    )
)
CELL_KEYS = frozenset(
    (
        "setting_id",
        "block_id",
        "calibration_id",
        "input_label",
        "analyzer_basis",
        "expected_configuration_id",
        "applied_configuration_id",
        "attempts",
        "reported_count",
        "anomalies",
        "outcomes",
    )
)


@dataclass(frozen=True)
class Outcome:
    bell_pattern: str
    receiver_pattern: tuple[int, int]
    resource_herald: bool
    count: int

    def record(self) -> dict[str, Any]:
        return {
            "bell_pattern": self.bell_pattern,
            "receiver_pattern": list(self.receiver_pattern),
            "resource_herald": self.resource_herald,
            "count": self.count,
        }


@dataclass(frozen=True)
class JointCell:
    setting_id: str
    block_id: str
    calibration_id: str | None
    input_label: str
    analyzer_basis: str
    expected_configuration_id: str
    applied_configuration_id: str | None
    attempts: Counter
    attempt_reason: str | None
    reported_count: int
    anomalies: dict[str, int]
    outcomes: tuple[Outcome, ...]


@dataclass(frozen=True)
class JointRecord:
    """Validated normalized records; metadata still consists of declarations, not verified apparatus facts."""

    metadata: dict[str, Any]
    cells: tuple[JointCell, ...]


def _attempt_counter(value: object, setting: str) -> tuple[Counter, str | None]:
    name = f"cell {setting}.attempts"
    item = _object(value, name, frozenset(("value", "population", "status", "source", "reason")))
    _choice(item["population"], f"{name}.population", (Population.SOURCE_TRIGGER.value,))
    status = Status(_choice(item["status"], f"{name}.status", ("observed", "modeled", "unavailable")))
    _text(item["source"], f"{name}.source")
    reason = _text(item["reason"], f"{name}.reason", nullable=True)
    if status is Status.UNAVAILABLE:
        if item["value"] is not None or reason is None:
            raise NetworkRecordError(f"{name}: unavailable attempts need value null and a reason")
        count = None
    else:
        count = _count(item["value"], f"{name}.value")
        if status is Status.MODELED and reason is None:
            raise NetworkRecordError(f"{name}: modeled attempts need their assumptions in reason")
    assumptions = (reason,) if status is Status.MODELED and reason is not None else ()
    return Counter("attempts", count, Population.SOURCE_TRIGGER, setting, status, item["source"], assumptions), reason


def _outcome(value: object, setting: str) -> Outcome:
    name = f"cell {setting}.outcome"
    item = _object(value, name, frozenset(("bell_pattern", "receiver_pattern", "resource_herald", "count")))
    pattern = item["bell_pattern"]
    if not isinstance(pattern, str) or not re.fullmatch(r"[01]{4}", pattern):
        raise NetworkRecordError(f"{name}.bell_pattern must be four threshold bits in c0,c1,d0,d1 order")
    receiver = _list(item["receiver_pattern"], f"{name}.receiver_pattern")
    if len(receiver) != 2:
        raise NetworkRecordError(f"{name}.receiver_pattern needs two nonnegative occupations")
    occupation = tuple(_count(count, f"{name}.receiver_pattern") for count in receiver)
    if type(item["resource_herald"]) is not bool:
        raise NetworkRecordError(f"{name}.resource_herald must be a JSON boolean")
    return Outcome(pattern, (occupation[0], occupation[1]), item["resource_herald"], _count(item["count"], name))


def _cell(value: object) -> JointCell:
    item = _object(value, "cell", CELL_KEYS)
    for key in ("setting_id", "block_id", "expected_configuration_id"):
        _text(item[key], f"cell.{key}")
    for key in ("calibration_id", "applied_configuration_id"):
        _text(item[key], f"cell.{key}", nullable=True)
    _choice(item["input_label"], "cell.input_label", INPUTS)
    _choice(item["analyzer_basis"], "cell.analyzer_basis", AXES)
    attempts, reason = _attempt_counter(item["attempts"], item["setting_id"])
    reported = _count(item["reported_count"], "cell.reported_count")
    anomalies = _object(item["anomalies"], "cell.anomalies", frozenset(("duplicates", "unmatched", "missing")))
    checked_anomalies = {key: _count(value, f"cell.anomalies.{key}") for key, value in anomalies.items()}
    outcomes = tuple(_outcome(value, item["setting_id"]) for value in _list(item["outcomes"], "cell.outcomes"))
    keys = [(row.bell_pattern, row.receiver_pattern, row.resource_herald) for row in outcomes]
    if len(set(keys)) != len(keys):
        raise NetworkRecordError(f"cell {item['setting_id']}: duplicate joint outcome key")
    if sum(row.count for row in outcomes) != reported:
        raise NetworkRecordError(f"cell {item['setting_id']}: outcomes do not conserve reported_count")
    if attempts.value is not None and reported > attempts.value:
        raise NetworkRecordError(f"cell {item['setting_id']}: reported joint events exceed source triggers")
    return JointCell(
        item["setting_id"],
        item["block_id"],
        item["calibration_id"],
        item["input_label"],
        item["analyzer_basis"],
        item["expected_configuration_id"],
        item["applied_configuration_id"],
        attempts,
        reason,
        reported,
        checked_anomalies,
        outcomes,
    )


def parse_joint_record(record: Mapping[str, Any]) -> JointRecord:
    """Parse one declared joint histogram without manufacturing coincidences from separate marginals."""
    item = _object(record, "joint record", JOINT_KEYS)
    _choice(item["schema"], "schema", (JOINT_SCHEMA,))
    _choice(item["data_origin"], "data_origin", ("synthetic", "measured"))
    _choice(item["representation"], "representation", ("joint_histogram",))
    _choice(item["protocol"], "protocol", PROTOCOLS)
    _revision(item["protocol_revision"], "protocol_revision")
    for key in ("case_sha256", "raw_result_sha256"):
        _digest(item[key], key)
    _digest(item["payload_sha256"], "payload_sha256", nullable=True)
    _text(item["joint_job_id"], "joint_job_id")
    for key in ("joint_platform_id", "route_id"):
        _text(item[key], key, nullable=True)
    apparatus = _strings(item["apparatus_ids"], "apparatus_ids", unique=True)
    if set(apparatus) != {"qpu:ascella", "qpu:belenos"}:
        raise NetworkRecordError("apparatus_ids must identify the two declared Ascella/Belenos partitions")
    _choice(item["frame_convention"], "frame_convention", (FRAME_CONVENTION,))
    _choice(item["processing_status"], "processing_status", ("raw_detector_counts", "processed_counts", "unknown"))
    _strings(item["processing_chain"], "processing_chain")
    evidence = _object(item["evidence"], "evidence", frozenset(ASSUMPTIONS))
    item["evidence"] = {key: _evidence(value, f"evidence.{key}") for key, value in evidence.items()}
    blocks = _strings(item["block_ids"], "block_ids", unique=True)
    if not blocks:
        raise NetworkRecordError("block_ids must declare at least one acquisition block")
    cells = tuple(ordered_map(_cell, _list(item["cells"], "cells")))
    declared = set(blocks)
    identities: set[tuple[str, str, str]] = set()
    settings: set[str] = set()
    for cell in cells:
        if cell.block_id not in declared:
            raise NetworkRecordError(f"cell {cell.setting_id}: undeclared block {cell.block_id}")
        identity = (cell.block_id, cell.input_label, cell.analyzer_basis)
        if identity in identities or cell.setting_id in settings:
            raise NetworkRecordError(f"cell {cell.setting_id}: duplicate setting or block/input/analyzer cell")
        identities.add(identity)
        settings.add(cell.setting_id)
    item.pop("cells")
    return JointRecord(item, cells)


@lru_cache(maxsize=1)
def _frames() -> dict[str, tuple[int, int]]:
    """Reuse the frozen producer's derived frame convention without changing its source identity."""
    return teleportation_frames("phi+").frames


def _score_cell(task: tuple[JointCell, str]) -> dict[str, Any]:
    cell, origin = task
    frames = _frames()
    matching_axis, expected = MATCHING[cell.input_label]
    accepted = correct = 0
    rejected = {
        key: 0
        for key in (
            "resource_herald_failed",
            "bell_pattern_rejected",
            "receiver_no_click",
            "receiver_multiple_occupation",
        )
    }
    branches: dict[str, dict[str, Any]] = {}
    for row in cell.outcomes:
        branch = branches.setdefault(row.bell_pattern, {"recorded": 0, "accepted": 0, "correct": 0})
        branch["recorded"] += row.count
        if not row.resource_herald:
            rejected["resource_herald_failed"] += row.count
        elif row.bell_pattern not in frames:
            rejected["bell_pattern_rejected"] += row.count
        elif sum(row.receiver_pattern) == 0:
            rejected["receiver_no_click"] += row.count
        elif sum(row.receiver_pattern) != 1:
            rejected["receiver_multiple_occupation"] += row.count
        else:
            accepted += row.count
            branch["accepted"] += row.count
            bit = decode_bit(cell.analyzer_basis, row.receiver_pattern[1], *frames[row.bell_pattern])
            if cell.analyzer_basis == matching_axis and bit == expected:
                correct += row.count
                branch["correct"] += row.count
    if cell.analyzer_basis != matching_axis:
        for branch in branches.values():
            branch["correct"] = None
    numerator = Counter(
        "eligible_outputs",
        accepted,
        Population.LOGICAL_ACCEPTED,
        cell.setting_id,
        Status.MODELED if origin == "synthetic" else Status.OBSERVED,
        "normalized joint outcomes",
        ("synthetic fixture counts",) if origin == "synthetic" else (),
    )
    success = ratio(numerator, cell.attempts, "resource herald, accepted Bell pattern, one receiver occupation")
    success_value: float | None
    success_reason: str | None
    if origin == "measured" and cell.attempts.status is Status.MODELED:
        success_value, success_reason = None, "modeled attempts do not establish a measured per-attempt rate"
    else:
        success_value, success_reason = success.value, success.reason
    return {
        "setting_id": cell.setting_id,
        "block_id": cell.block_id,
        "calibration_id": cell.calibration_id,
        "input_label": cell.input_label,
        "analyzer_basis": cell.analyzer_basis,
        "expected_configuration_id": cell.expected_configuration_id,
        "applied_configuration_id": cell.applied_configuration_id,
        "attempts": {**cell.attempts.record(), "reason": cell.attempt_reason},
        "reported_count": cell.reported_count,
        "eligible_outputs": accepted,
        "matching_basis": cell.analyzer_basis == matching_axis,
        "correct_outputs": correct if cell.analyzer_basis == matching_axis else None,
        "conditional_fidelity": correct / accepted if accepted and cell.analyzer_basis == matching_axis else None,
        "success_per_attempt": success_value,
        "success_per_attempt_reason": success_reason,
        "rejection_counts": rejected,
        "anomalies": dict(cell.anomalies),
        "bell_branches": branches,
        "joint_outcomes": [row.record() for row in cell.outcomes],
    }


def _summarize_scores(scores: list[dict[str, Any]], blocks: tuple[str, ...], origin: str) -> dict[str, Any]:
    """Reduce matching cells only; preserve per-input attempt normalization before combining priors."""
    per_input: dict[str, Any] = {}
    issues: list[str] = []
    numerator = Fraction(0)
    denominator = Fraction(0)
    total_correct = total_accepted = 0
    conditional: list[Fraction] = []
    for label in INPUTS:
        selected = [row for row in scores if row["input_label"] == label and row["matching_basis"]]
        accepted = sum(row["eligible_outputs"] for row in selected)
        correct = sum(row["correct_outputs"] for row in selected)
        total_accepted += accepted
        total_correct += correct
        if accepted:
            conditional.append(Fraction(correct, accepted))
        reasons = []
        if {row["block_id"] for row in selected} != set(blocks):
            reasons.append("missing matching cell in a declared block")
        statuses = {row["attempts"]["status"] for row in selected}
        if any(row["attempts"]["value"] in (None, 0) for row in selected):
            reasons.append("a matching cell has unavailable or zero attempts")
        if len(statuses) > 1:
            reasons.append("matching cells mix observed, modeled, or unavailable attempt statuses")
        if origin == "measured" and "modeled" in statuses:
            reasons.append("modeled attempts cannot establish measured success weighting")
        attempts = None if reasons else sum(row["attempts"]["value"] for row in selected)
        if attempts is not None and attempts > 0:
            numerator += Fraction(correct, attempts)
            denominator += Fraction(accepted, attempts)
        else:
            issues.extend(f"{label}: {reason}" for reason in reasons)
        per_input[label] = {
            "correct": correct,
            "accepted": accepted,
            "matching_attempts": attempts,
            "conditional_fidelity": correct / accepted if accepted else None,
            "success_per_attempt": accepted / attempts if attempts else None,
            "attempt_reason": "; ".join(reasons) if reasons else None,
        }
    success_probability = float(denominator / 6) if not issues else None
    if not issues and denominator == 0:
        issues.append("the declared ensemble has zero accepted outputs")
    weighted = None if issues else float(numerator / denominator)
    return {
        "per_input": per_input,
        "mean_conditional_fidelity": float(sum(conditional) / 6) if len(conditional) == 6 else None,
        "mean_conditional_reason": None
        if len(conditional) == 6
        else "at least one input has no accepted matching outcomes",
        "pooled_conditional_fidelity": total_correct / total_accepted if total_accepted else None,
        "equal_prior_success_weighted_fidelity": weighted,
        "equal_prior_success_weighted_reason": "; ".join(issues) if issues else None,
        "equal_prior_success_probability": success_probability,
        "confidence_interval": None,
        "confidence_interval_reason": "this format establishes no sampling law or uncertainty certificate",
    }


def analyze_joint(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return lossless descriptive scores and unresolved contracts; never emit a quantum certificate."""
    joint = parse_joint_record(record)
    metadata = joint.metadata
    origin = metadata["data_origin"]
    blocks = tuple(metadata["block_ids"])
    scores = ordered_map(_score_cell, [(cell, origin) for cell in joint.cells])
    block_reports: dict[str, Any] = {}
    issues: list[str] = []
    complete = True
    by_block: dict[str, list[dict[str, Any]]] = {block: [] for block in blocks}
    for row in scores:
        by_block[row["block_id"]].append(row)
    for block in blocks:
        selected = by_block[block]
        present = {(row["input_label"], row["analyzer_basis"]) for row in selected}
        missing = [
            {"input_label": label, "analyzer_basis": axis}
            for label in INPUTS
            for axis in AXES
            if (label, axis) not in present
        ]
        complete = complete and not missing
        calibrations = {row["calibration_id"] for row in selected}
        if None in calibrations or not calibrations:
            issues.append(f"{block}: calibration identity unavailable")
        if len(calibrations - {None}) > 1:
            issues.append(f"{block}: calibration changes within the declared block")
        block_reports[block] = {
            "complete_18_cells": not missing,
            "missing_cells": missing,
            "calibration_ids": sorted(value for value in calibrations if value is not None),
            "scores": _summarize_scores(selected, (block,), origin),
        }
    for cell in joint.cells:
        if cell.applied_configuration_id is None:
            issues.append(f"{cell.setting_id}: applied configuration is unknown")
        elif cell.applied_configuration_id != cell.expected_configuration_id:
            issues.append(f"{cell.setting_id}: frozen and applied configuration identities differ")
        for kind, count in cell.anomalies.items():
            if count:
                issues.append(f"{cell.setting_id}: {count} {kind} events")
    unresolved = [
        key for key, value in metadata["evidence"].items() if value is None or value["status"] != "documented"
    ]
    if metadata["processing_status"] != "raw_detector_counts":
        issues.append("the observation law is processed or unknown")
    if origin == "synthetic":
        issues.append("synthetic counts are calculations, not measured evidence")
    if metadata["route_id"] is None or metadata["joint_platform_id"] is None:
        issues.append("the declared physical route or joint platform is unavailable")
    return {
        "schema": "qd-network-joint-analysis-v1",
        "structurally_valid": True,
        "analysis_status": "descriptive_only",
        "data_origin": origin,
        "complete_18_cells_per_block": complete,
        "partial": not complete,
        "review_ready": False,
        "execution_admitted": False,
        "physical_claim_admitted": False,
        "quantum_certificate": None,
        "admission_reason": "normalized counts and declarations do not establish the C2-C6 prerequisites",
        "declared_bindings": {
            key: metadata[key] for key in ("protocol_revision", "case_sha256", "payload_sha256", "raw_result_sha256")
        },
        "byte_verified_bindings": [],
        "raw_to_normalized_derivation_verified": False,
        "declared_evidence": metadata["evidence"],
        "unresolved_assumptions": unresolved,
        "integrity_and_scope_issues": issues,
        "metadata": metadata,
        "blocks": block_reports,
        "cells": scores,
        "scores": _summarize_scores(scores, blocks, origin),
        "aggregation_scope": "per-input matching cells across supplied blocks; channel equivalence remains unverified",
        "unsupported_scope": [
            "provider raw-response normalization and physical-event provenance",
            "coincidence reconstruction or pairing independent job marginals",
            "additional detector channels beyond the declared four Bell and two receiver outputs",
            "witness, tomography, confidence bounds, and classical-benchmark certification",
            "reference-assisted, live-output, or sequential-transfer claims",
        ],
    }


def verify_bindings(
    record: Mapping[str, Any],
    *,
    case_bytes: bytes | None = None,
    raw_result_bytes: bytes | None = None,
    payload_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Check supplied immutable byte identities and case scope; never attest the source-to-count derivation."""
    joint = parse_joint_record(record)
    metadata = joint.metadata
    inputs = {"case": case_bytes, "raw_result": raw_result_bytes, "payload": payload_bytes}
    bindings: dict[str, Any] = {}
    for name, data in inputs.items():
        expected = metadata[f"{name}_sha256"]
        if data is None:
            bindings[name] = {
                "status": "unverified",
                "declared_sha256": expected,
                "reason": "source bytes not supplied",
            }
            continue
        if not isinstance(data, bytes):
            raise NetworkRecordError(f"{name} source must be bytes")
        digest = hashlib.sha256(data).hexdigest()
        if expected is None or digest != expected:
            raise NetworkRecordError(f"{name} bytes differ from the declared SHA-256")
        bindings[name] = {"status": "byte_verified", "declared_sha256": expected, "observed_sha256": digest}
    case_assessment = None
    attempt_targets = None
    if case_bytes is not None:
        case = decode_json(case_bytes)
        case_assessment = assess_case(case)
        for left, right in (
            ("source_revision", "protocol_revision"),
            ("protocol", "protocol"),
            ("logical_frame_convention", "frame_convention"),
            ("joint_platform_id", "joint_platform_id"),
            ("payload_sha256", "payload_sha256"),
        ):
            if case[left] != metadata[right]:
                raise NetworkRecordError(f"bound case {left} differs from joint record {right}")
        if set(case["local_platforms"]) != set(metadata["apparatus_ids"]):
            raise NetworkRecordError("bound case apparatus scope differs from the joint record")
        if case["claim_level"] != "C3" or case["output_capability"] != "O0":
            raise NetworkRecordError("bound case is outside the supported terminal single-hop scope")
        statistical = case["statistical_case"]
        if statistical is not None:
            if set(statistical["block_ids"]) != set(metadata["block_ids"]):
                raise NetworkRecordError("bound case planned block identities differ from the declared joint blocks")
            target = statistical["attempts_per_cell"]
            attempt_targets = {
                "attempts_per_cell": target,
                "block_ids": statistical["block_ids"],
                "recorded_cells": [
                    {
                        "setting_id": cell.setting_id,
                        "recorded_attempts": cell.attempts.value,
                        "recorded_status": cell.attempts.status.value,
                        "difference_from_target": None if cell.attempts.value is None else cell.attempts.value - target,
                    }
                    for cell in joint.cells
                ],
                "scope": "target comparison is descriptive and grants no execution authority",
            }
    return {
        "schema": "qd-network-binding-verification-v1",
        "bindings": bindings,
        "case_assessment": case_assessment,
        "attempt_targets": attempt_targets,
        "raw_to_normalized_derivation_verified": False,
        "raw_to_normalized_reason": "no provider adapter verifies the conversion from bound raw bytes to these counts",
        "physical_claim_admitted": False,
        "execution_admitted": False,
    }
