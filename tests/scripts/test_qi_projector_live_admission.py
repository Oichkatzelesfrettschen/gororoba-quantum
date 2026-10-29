"""Frozen Tuna admission rejects structural, queue, heartbeat and cost changes."""

import copy
import datetime
import json
from pathlib import Path

import pytest
from qi_projector_live_admission import PROPOSAL, bound_inputs, structural_check


@pytest.fixture
def observations() -> tuple:
    frozen = json.loads((PROPOSAL / "tuna-qualification/backend.json").read_text())
    live = copy.deepcopy(frozen)
    observed_at = datetime.datetime.fromisoformat("2026-10-27T15:35:45+00:00")
    return frozen, live, live["backend_instances"], {"number_of_jobs_in_queue": 0}, [], 0, observed_at, 120


def test_bound_inputs() -> None:
    frozen, bound = bound_inputs(PROPOSAL / "tuna-qualification", PROPOSAL / "tuna-qualification/cases.json")
    if frozen["id"] != 7 or len(bound["circuits"]) != 3:
        raise AssertionError("qualification binding changed")


def test_good_observation(observations: tuple) -> None:
    result = structural_check(*observations)
    if not result["admitted"] or result["failures"]:
        raise AssertionError(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("enabled", False),
        ("status", "offline"),
        ("supports_raw_data", False),
        ("max_number_of_shots", 2048),
        ("default_compiler_config", {}),
        ("topology", []),
        ("gateset", ["H"]),
        ("protocol_version", 3),
        ("nqubits", 16),
    ],
)
def test_backend_changes(observations: tuple, field: str, value: object) -> None:
    observations[1][field] = value
    if structural_check(*observations)["admitted"]:
        raise AssertionError(f"admitted changed {field}")


@pytest.mark.parametrize(
    "heartbeat", [None, "bad", "2026-10-27T15:35:45", "2026-10-27T15:30:00Z", "2026-10-27T15:36:00Z"]
)
def test_heartbeat(observations: tuple, heartbeat: str | None) -> None:
    observations[2][0]["last_heartbeat"] = heartbeat
    if structural_check(*observations)["admitted"]:
        raise AssertionError("admitted invalid heartbeat")


@pytest.mark.parametrize("count", [1, True, -1, None])
def test_queue(observations: tuple, count: object) -> None:
    observations[3]["number_of_jobs_in_queue"] = count
    if structural_check(*observations)["admitted"]:
        raise AssertionError("admitted invalid queue")


def test_pause_and_nonoffsetting_charges(observations: tuple) -> None:
    changed = list(observations)
    changed[5] = 1
    if structural_check(*changed)["admitted"]:
        raise AssertionError("admitted remaining pause")
    observations[4].extend([{"change": 1, "member_id": 999}, {"change": -1}])
    result = structural_check(*observations)
    if result["admitted"] or "member_id" in json.dumps(result):
        raise AssertionError("charges or private identifiers admitted")


def test_tampered_source(tmp_path: Path) -> None:
    import shutil

    case_dir = tmp_path / "case"
    shutil.copytree(PROPOSAL / "tuna-qualification", case_dir)
    (case_dir / "geometry.cq").write_text("wrong")
    with pytest.raises(ValueError, match="source circuit"):
        bound_inputs(case_dir, case_dir / "cases.json")


def test_absent_instances(observations: tuple) -> None:
    observations[2].clear()
    if structural_check(*observations)["admitted"]:
        raise AssertionError("admitted absent hardware")


@pytest.mark.parametrize("seconds", [300, 300.0])
def test_execution_time_numeric_equivalence(observations: tuple, seconds: int | float) -> None:
    observations[1]["job_execution_time_limit"] = seconds
    if not structural_check(*observations)["admitted"]:
        raise AssertionError("equivalent numeric execution limit refused")


@pytest.mark.parametrize("seconds", [True, False, float("nan"), float("inf"), float("-inf"), 301.0, "300"])
def test_execution_time_rejects_invalid_numbers(observations: tuple, seconds: object) -> None:
    observations[1]["job_execution_time_limit"] = seconds
    if structural_check(*observations)["admitted"]:
        raise AssertionError("invalid execution limit admitted")


@pytest.mark.parametrize(
    "field", ["nqubits", "max_number_of_shots", "max_jobs_per_batch_job", "batchjobs_per_queue_limit"]
)
def test_counts_keep_integer_types(observations: tuple, field: str) -> None:
    observations[1][field] = float(observations[1][field])
    if structural_check(*observations)["admitted"]:
        raise AssertionError("float count admitted")


def test_changed_manifest_refused_before_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_platform
    from qi_projector_live_admission import MANIFEST_SHA256

    (tmp_path / "cases.json").write_text("{}\n")

    def reject_client() -> None:
        raise AssertionError("manifest refusal must precede client creation")

    monkeypatch.setattr(qi_platform, "Client", reject_client)
    with pytest.raises(SystemExit, match="differs from the approved manifest digest"):
        qi_platform._submit(tmp_path, 7, "approved frozen case", expected_cases_sha256=MANIFEST_SHA256)
