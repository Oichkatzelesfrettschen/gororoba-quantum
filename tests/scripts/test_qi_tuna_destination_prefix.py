"""Retained incomplete acquisitions preserve refusal while descriptive counts replay."""

import json
import shutil
from pathlib import Path

import pytest
from qi_tuna_destination_prefix import ROOT, analyze, replay

RETAINED = ROOT / "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response"


def test_retained_deadline_prefix_replays() -> None:
    primary = json.loads((RETAINED / "analysis.json").read_text())
    if analyze(RETAINED) != primary or primary["outcome"] != "implementation route unavailable":
        raise AssertionError("incomplete case must retain its frozen refusal")
    retained = json.loads((RETAINED / "nominal-zero-prefix-receipt-validation.json").read_text())
    if replay(RETAINED) != retained or retained["statistical_acceptance_admitted"] is not False:
        raise AssertionError("prefix counts must replay without promoting the incomplete case")
    original = json.loads((RETAINED / "nominal-zero-prefix-descriptive.json").read_text())
    for field in ("comparisons", "jobs", "shots_total", "execution_seconds_decimal", "primary_case_outcome"):
        if retained[field] != original[field]:
            raise AssertionError("receipt validation changed retained numerical results or primary outcome")


def test_missing_prefix_completion_refuses(tmp_path: Path) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    (run / "prepared-zero-baseline-after/completion-admission.json").unlink()
    with pytest.raises(FileNotFoundError):
        replay(run)


def test_reordered_retained_shots_refuse(tmp_path: Path) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    path = run / "prepared-zero-baseline-before/raw/baseline-before.cq.json"
    shots = json.loads(path.read_text())
    if shots == list(reversed(shots)):
        raise AssertionError("retained fixture must distinguish shot order")
    path.write_text(json.dumps(list(reversed(shots))))
    with pytest.raises(ValueError):
        replay(run)


@pytest.mark.parametrize(
    "fault",
    ["schema", "job", "job-type", "case", "state-digest", "completion-digest", "creation", "resume", "chronology"],
)
def test_recovery_semantics_refuse(tmp_path: Path, fault: str) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    intent_path = run / "read-only-recovery-intent.json"
    receipt_path = run / "read-only-recovery-receipt.json"
    intent = json.loads(intent_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    if fault == "schema":
        intent["schema"] = receipt["schema"] = "unsupported"
    elif fault == "job":
        intent["job"] = receipt["job"] = 1
    elif fault == "job-type":
        receipt["job"] = float(receipt["job"])
    elif fault == "case":
        intent["case"] = receipt["case"] = "prepared-zero-baseline-before"
    elif fault == "state-digest":
        intent["original_execution_state_sha256"] = receipt["original_execution_state_sha256"] = "0" * 64
    elif fault == "completion-digest":
        receipt["completion_admission_sha256"] = "0" * 64
    elif fault == "creation":
        intent["provider_resource_creation_authorized"] = receipt["provider_resource_creation_authorized"] = True
    elif fault == "resume":
        receipt["automatic_executor_resumed"] = True
    else:
        intent["started_utc"] = receipt["started_utc"] = "2026-10-27T20:00:00+00:00"
    intent_path.write_text(json.dumps(intent))
    receipt_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        replay(run)


@pytest.mark.parametrize("fault", ["schema", "job", "digest", "match", "timestamp", "fields"])
def test_source_readback_semantics_refuse(tmp_path: Path, fault: str) -> None:
    run = tmp_path / "run"
    shutil.copytree(RETAINED, run)
    path = run / "prepared-zero-baseline-before/stored-source-observation.json"
    record = json.loads(path.read_text())
    observed = record["jobs"][0]
    if fault == "schema":
        record["schema"] = "unsupported"
    elif fault == "job":
        observed["job"] = 1
    elif fault == "digest":
        observed["stored_source_sha256"] = "0" * 64
    elif fault == "match":
        observed["source_matches"] = False
    elif fault == "timestamp":
        record["observed_utc"] = "2026-10-27T00:00:00+00:00"
    else:
        observed["response_field_names"] = "content"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        replay(run)
