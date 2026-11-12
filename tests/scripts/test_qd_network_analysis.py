"""The offline CLI refuses malformed input and preserves every bound source byte."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pytest
import qd_network_analysis as cli

import qd_network_records as records


def write_case(directory: Path) -> Path:
    path = directory / "case.json"
    path.write_text(json.dumps(records.case_template("1" * 40)), encoding="utf-8")
    return path


def test_pending_case_report_binds_the_exact_input_snapshot(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_case(tmp_path)
    before = path.read_bytes()
    if cli.main([str(path), "--require-review-ready"]) != 1:
        raise AssertionError("an unresolved case must fail the requested review-readiness gate")
    report = json.loads(capsys.readouterr().out)
    if report["input_sha256"] != hashlib.sha256(before).hexdigest():
        raise AssertionError("the report must bind the bytes that were parsed")
    if report["physical_claim_admitted"] or report["execution_admitted"]:
        raise AssertionError("record validation cannot grant physical or execution authority")
    if report["assessment"]["review_ready"] or not report["assessment"]["missing_or_unresolved"]:
        raise AssertionError("unknown physical requirements must remain visible")
    if path.read_bytes() != before:
        raise AssertionError("inspection changed its source")


def test_case_report_is_atomic_and_default_success_means_report_only(tmp_path: Path) -> None:
    path = write_case(tmp_path)
    destination = tmp_path / "derived" / "assessment.json"
    if cli.main([str(path), "--out", str(destination)]) != 0:
        raise AssertionError("a structurally valid pending case must produce a descriptive report")
    report = json.loads(destination.read_text())
    if report["assessment"]["review_ready"] or list(destination.parent.glob(".assessment.json.*")):
        raise AssertionError("the pending report must leave no temporary output")


@pytest.mark.parametrize(
    "text",
    [
        '{"schema":"qd-network-case-v1","schema":"qd-network-joint-v1"}',
        '{"schema":"qd-network-case-v1","x":NaN}',
        '{"schema":"unsupported"}',
        "[]",
        "{",
    ],
)
def test_invalid_input_writes_no_report(tmp_path: Path, text: str) -> None:
    source = tmp_path / "record.json"
    source.write_text(text)
    destination = tmp_path / "report.json"
    if cli.main([str(source), "--out", str(destination)]) != 2 or destination.exists():
        raise AssertionError("malformed or ambiguous records must not produce an assessment artifact")


def test_output_cannot_replace_the_input_even_through_a_symlink(tmp_path: Path) -> None:
    path = write_case(tmp_path)
    link = tmp_path / "alias.json"
    link.symlink_to(path)
    before = path.read_bytes()
    if cli.main([str(path), "--out", str(link)]) != 2 or path.read_bytes() != before:
        raise AssertionError("an output alias must not replace source bytes")


def test_case_refuses_joint_binding_arguments(tmp_path: Path) -> None:
    path = write_case(tmp_path)
    if cli.main([str(path), "--raw-result", str(path)]) != 2:
        raise AssertionError("joint binding options must not be silently ignored for a case")


def test_missing_input_is_a_refusal(tmp_path: Path) -> None:
    if cli.main([str(tmp_path / "absent.json")]) != 2:
        raise AssertionError("missing input must fail instead of creating an empty record")


def test_read_limit_precedes_json_parsing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "large.json"
    path.write_bytes(b" " * 17)
    monkeypatch.setattr(records, "MAX_JSON_BYTES", 16)
    with pytest.raises(records.NetworkRecordError, match="exceeds"):
        cli.bounded_bytes(path)


def write_joint(directory: Path) -> tuple[Path, Path, Path]:
    """One deliberately partial synthetic cell tests CLI binding without a fabricated acquisition."""
    case = write_case(directory)
    raw = directory / "synthetic-source.bin"
    raw.write_bytes(b"synthetic source identity, not a provider observation\n")
    record: dict[str, Any] = {
        "schema": records.JOINT_SCHEMA,
        "data_origin": "synthetic",
        "representation": "joint_histogram",
        "protocol": "teleportation_A_to_B",
        "protocol_revision": "1" * 40,
        "case_sha256": hashlib.sha256(case.read_bytes()).hexdigest(),
        "payload_sha256": None,
        "raw_result_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "joint_job_id": "synthetic-cli-fixture",
        "joint_platform_id": None,
        "apparatus_ids": ["qpu:ascella", "qpu:belenos"],
        "endpoint_roles": {"bell_station": "qpu:ascella", "receiver": "qpu:belenos"},
        "route_id": None,
        "frame_convention": records.FRAME_CONVENTION,
        "processing_status": "raw_detector_counts",
        "processing_chain": [],
        "evidence": dict.fromkeys(records.ASSUMPTIONS),
        "block_ids": ["synthetic-block"],
        "cells": [
            {
                "setting_id": "synthetic-plus-z-z",
                "block_id": "synthetic-block",
                "calibration_id": None,
                "input_label": "+Z",
                "analyzer_basis": "Z",
                "expected_configuration_id": "synthetic-configuration",
                "applied_configuration_id": None,
                "attempts": {
                    "value": 80,
                    "population": "source_trigger",
                    "status": "modeled",
                    "source": "synthetic fixture",
                    "reason": "exactly enumerated fixture attempts",
                },
                "reported_count": 80,
                "anomalies": {"duplicates": 0, "unmatched": 0, "missing": 0},
                "outcomes": [
                    {"bell_pattern": "1001", "receiver_pattern": [0, 1], "resource_herald": True, "count": 40},
                    {"bell_pattern": "0000", "receiver_pattern": [0, 0], "resource_herald": True, "count": 40},
                ],
            }
        ],
    }
    path = directory / "joint.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path, case, raw


def test_joint_roundtrip_verifies_identity_without_granting_physical_authority(tmp_path: Path) -> None:
    path, case, raw = write_joint(tmp_path)
    snapshots = {source: source.read_bytes() for source in (path, case, raw)}
    destination = tmp_path / "derived.json"
    arguments = [str(path), "--case", str(case), "--raw-result", str(raw), "--out", str(destination)]
    if cli.main([*arguments, "--require-review-ready"]) != 1:
        raise AssertionError("a partial normalized record cannot pass a physical or inferential review gate")
    report = json.loads(destination.read_text())
    analysis, bindings = report["analysis"], report["bindings"]
    if not analysis["partial"] or analysis["scores"]["pooled_conditional_fidelity"] != 1.0:
        raise AssertionError("partial counts must remain inspectable with their bounded descriptive score")
    if analysis["scores"]["equal_prior_success_weighted_fidelity"] is not None:
        raise AssertionError("missing ensemble inputs must prevent an ensemble success-weighted score")
    for name in ("case", "raw_result"):
        if bindings["bindings"][name]["status"] != "byte_verified":
            raise AssertionError(f"supplied {name} bytes must actually be checked")
    if bindings["raw_to_normalized_derivation_verified"] or analysis["physical_claim_admitted"]:
        raise AssertionError("byte identity must not certify count derivation or a quantum claim")
    if any(source.read_bytes() != snapshot for source, snapshot in snapshots.items()):
        raise AssertionError("joint inspection changed a bound source")


@pytest.mark.parametrize("binding", ["case", "raw-result"])
def test_joint_binding_mismatch_preserves_an_existing_output(tmp_path: Path, binding: str) -> None:
    path, case, raw = write_joint(tmp_path)
    changed = case if binding == "case" else raw
    changed.write_bytes(changed.read_bytes() + b"\n")
    destination = tmp_path / "derived.json"
    previous = b"previous derived result\n"
    destination.write_bytes(previous)
    arguments = [str(path), "--case", str(case), "--raw-result", str(raw), "--out", str(destination)]
    if cli.main(arguments) != 2 or destination.read_bytes() != previous:
        raise AssertionError("mismatched source bytes must refuse the analysis and preserve prior output")


class RecordingStream(io.BytesIO):
    """A byte stream that remembers the size argument of every read."""

    sizes: list[int | None]

    def __init__(self, content: bytes) -> None:
        super().__init__(content)
        self.sizes = []

    def read(self, size: int | None = -1) -> bytes:
        self.sizes.append(size)
        return super().read(size)


@pytest.mark.parametrize("reader", ["cli", "records"])
def test_inputs_are_read_with_a_size_bound_not_whole(
    reader: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "large.json"
    path.write_bytes(b" " * 64)
    monkeypatch.setattr(records, "MAX_JSON_BYTES", 16)
    stream = RecordingStream(path.read_bytes())
    monkeypatch.setattr(Path, "open", lambda _self, _mode="r": stream)
    with pytest.raises(records.NetworkRecordError, match="exceeds"):
        cli.bounded_bytes(path) if reader == "cli" else records.load_json(path)
    if stream.sizes != [17]:
        raise AssertionError(f"the reader must request at most the limit plus one byte: {stream.sizes}")


def test_report_replacement_is_one_atomic_rename(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = write_case(tmp_path)
    destination = tmp_path / "report.json"
    previous = b"previous derived result\n"
    destination.write_bytes(previous)

    def failing_replace(_source: object, _target: object) -> None:
        raise OSError("rename refused")

    monkeypatch.setattr(cli.os, "replace", failing_replace)
    if cli.main([str(path), "--out", str(destination)]) != 2:
        raise AssertionError("an unwritable report is a refusal")
    if destination.read_bytes() != previous or list(tmp_path.glob(".report.json.*")):
        raise AssertionError("the previous report survives and no temporary file remains")


def test_report_hash_binds_the_snapshot_that_was_parsed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = write_case(tmp_path)
    expected = hashlib.sha256(path.read_bytes()).hexdigest()

    def forbidden(_self: Path) -> bytes:
        raise AssertionError("the input is read once; a second read could bind different bytes")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    destination = tmp_path / "report.json"
    if cli.main([str(path), "--out", str(destination)]) != 0:
        raise AssertionError("a pending case must produce a report")
    if json.loads(destination.read_text())["input_sha256"] != expected:
        raise AssertionError("the report must bind the parsed bytes")
