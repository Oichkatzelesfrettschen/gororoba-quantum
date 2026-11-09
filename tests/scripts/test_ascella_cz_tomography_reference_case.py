"""The tomography reference case's budgets, time and credit bounds, seed plan and submission gate on bounded
fixtures."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import ascella_cz_tomography_reference_case as case
import pytest
from qd_schedule import body_digest

tomo = case.tomo


def planned_fixture(
    job: str, hom: Any, transmittance: Any = 5.51, status: str = "available", jobs: int = 0
) -> dict[str, Any]:
    policy = case.submission_policy(job)
    perfs = {"HOM (%)": hom, "Transmittance (%)": transmittance}
    return {
        "case": job,
        "platform": case.PLATFORM,
        "credit_ceiling": float(policy["credit_ceiling"]),
        "per_job_credits": float(policy["per_job_credits"]),
        "expected_seconds": float(policy["expected_seconds"]),
        "perfs_at_plan": perfs,
        "perfs_at_estimate": dict(perfs),
        "status_at_plan": {"explorer": status, "processor": "available"},
        "availability_at_plan": {"num_concurrent_jobs": jobs, "num_jobs_in_queue": 0, "num_running_qt_jobs": 0},
    }


def complete_run(job: str = "job-00", status: str = "completed", missing: int = 0, error: int = 0) -> dict[str, Any]:
    names = [row["name"] for row in tomo.job_rows(job)]
    tallies = {name: {"eligible": [1, 1, 1, 1]} for name in names[missing:]}
    return {
        "job": job,
        "status": status,
        "tallies": tallies,
        "uncounted": {"error": error},
        "perfs": {"HOM (%)": 91.0, "Transmittance (%)": 5.51},
        "submitted_utc": SUBMITTED.isoformat(timespec="seconds"),
    }


SUBMITTED = datetime(2026, 11, 10, 6, 0, tzinfo=UTC)
LATER = SUBMITTED + timedelta(minutes=5)


@pytest.mark.parametrize(
    ("hom", "admitted"), [(88.76, False), (90.0, False), (90.000001, True), (91, True), (94.0, True)]
)
def test_hom_is_admitted_strictly_above_the_floor(hom: float, admitted: bool) -> None:
    planned = planned_fixture("job-00", hom)
    if admitted:
        case.admit("job-00", planned, None)
    else:
        with pytest.raises(case.qd_platform.PlatformError, match="is not above"):
            case.admit("job-00", planned, None)


@pytest.mark.parametrize("value", [True, "91", float("nan"), float("inf"), None])
def test_a_non_numeric_figure_is_refused(value: Any) -> None:
    with pytest.raises(case.qd_platform.PlatformError, match="the plan reads HOM"):
        case.admit("job-00", planned_fixture("job-00", value), None)
    with pytest.raises(case.qd_platform.PlatformError, match="the plan reads Transmittance"):
        case.admit("job-00", planned_fixture("job-00", 91.0, value), None)


def test_transmittance_below_the_floor_is_refused() -> None:
    floor = float(case.submission_policy("job-00")["transmittance_percent"]["at_least"])
    case.admit("job-00", planned_fixture("job-00", 91.0, floor), None)
    with pytest.raises(case.qd_platform.PlatformError, match="below the"):
        case.admit("job-00", planned_fixture("job-00", 91.0, floor - 1e-4), None)


@pytest.mark.parametrize("counter", case.IDLE_COUNTERS)
@pytest.mark.parametrize("status", ["available", "running"])
def test_either_status_admits_only_an_idle_token(counter: str, status: str) -> None:
    case.admit("job-00", planned_fixture("job-00", 91.0, status=status), None)
    planned = planned_fixture("job-00", 91.0, status=status)
    planned["availability_at_plan"][counter] = 1
    with pytest.raises(case.qd_platform.PlatformError, match="holds jobs"):
        case.admit("job-00", planned, None)


def test_a_calibration_status_is_refused() -> None:
    with pytest.raises(case.qd_platform.PlatformError, match="status"):
        case.admit("job-00", planned_fixture("job-00", 91.0, status="calibration"), None)


def test_an_estimate_on_other_perfs_is_refused() -> None:
    planned = planned_fixture("job-00", 91.0)
    planned["perfs_at_estimate"] = {"HOM (%)": 90.5, "Transmittance (%)": 5.51}
    with pytest.raises(case.qd_platform.PlatformError, match="shot estimate read other"):
        case.admit("job-00", planned, None)


def test_a_plan_off_the_policy_is_refused() -> None:
    planned = planned_fixture("job-00", 91.0)
    planned["credit_ceiling"] = 2.6
    with pytest.raises(case.qd_platform.PlatformError, match="credit_ceiling"):
        case.admit("job-00", planned, None)


@pytest.mark.parametrize(
    ("predecessor", "match"),
    [
        (None, "requires the collected"),
        (complete_run(status="canceled"), "not completed"),
        (complete_run(missing=1), "counted 71 of 72"),
        (complete_run(error=1), "1 uncounted"),
        (complete_run(job="job-01"), "not job-00"),
    ],
)
def test_job_01_waits_for_a_complete_job_00(predecessor: dict[str, Any] | None, match: str) -> None:
    with pytest.raises(case.qd_platform.PlatformError, match=match):
        case.admit("job-01", planned_fixture("job-01", 91.0), predecessor, LATER)


def test_job_01_admits_after_a_complete_job_00() -> None:
    case.admit("job-01", planned_fixture("job-01", 91.0), complete_run(), LATER)


@pytest.mark.parametrize(
    ("hom", "transmittance", "at", "match"),
    [
        (92.01, 5.51, LATER, "HOM"),
        (91.0, 5.82, LATER, "Transmittance"),
        (91.0, 5.51, SUBMITTED + timedelta(hours=12, seconds=1), "h after"),
        (91.0, 5.51, SUBMITTED - timedelta(seconds=1), "h after"),
    ],
)
def test_job_01_is_refused_outside_the_pooling_tolerances(
    hom: float, transmittance: float, at: datetime, match: str
) -> None:
    """A job-01 plan whose pool with job-00 tomo.pooling would leave descriptive spends no credit."""
    with pytest.raises(case.qd_platform.PlatformError, match=match):
        case.admit("job-01", planned_fixture("job-01", hom, transmittance), complete_run(), at)
    case.admit("job-01", planned_fixture("job-01", 92.0, 5.81), complete_run(), SUBMITTED + timedelta(hours=12))


def test_only_the_bound_gate_carries_the_submission_capability(monkeypatch: pytest.MonkeyPatch) -> None:
    if "submit_wrapper" in vars(case.PolicyGate) or case.SubmissionGate.submit_wrapper != case.SUBMIT_WRAPPER:
        raise AssertionError("the capability is not on the bound gate alone")
    monkeypatch.setattr(case.qd_platform, "load_case", lambda _: ({"submit_wrapper": case.SUBMIT_WRAPPER}, {}, "x"))
    with pytest.raises(case.qd_platform.PlatformError, match="submits only through"):
        case.qd_platform.submit(Path("job-00"), case.PLATFORM, "approval", 1.99, 261, 1.0, verify=lambda _p: None)


def test_a_manifest_policy_other_than_the_generated_one_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    case.require_manifest_policy("job-00")
    original = case.submission_policy
    monkeypatch.setattr(case, "submission_policy", lambda job: {**original(job), "expected_seconds": 1})
    with pytest.raises(RuntimeError, match="another submission policy"):
        case.require_manifest_policy("job-00")


def test_the_live_read_must_repeat_the_plan_and_connect_the_sources() -> None:
    perfs = case.read_perfs()
    planned = {"perfs_at_plan": case.qd_platform.scrub(perfs)}
    processor = {"perfs": perfs, "specs": {"connected_input_modes": list(tomo.SOURCES)}}
    case.live_read("job-00", planned, processor)
    with pytest.raises(RuntimeError, match="moved after the plan"):
        case.live_read("job-00", planned, {**processor, "perfs": {**perfs, "HOM (%)": perfs["HOM (%)"] + 0.01}})
    with pytest.raises(RuntimeError, match="are not all in"):
        case.live_read("job-00", planned, {**processor, "specs": {"connected_input_modes": [tomo.SOURCES[0]]}})


def test_submit_binds_the_admitted_preflight() -> None:
    planned = {"cases_sha256": "c", "body": {"process_id": "a", "payload": {"x": 1}}, "perfs_at_plan": {"HOM (%)": 92}}
    reviewed = {
        "admission": {"admitted": True},
        "cases_sha256": "c",
        "body_sha256_without_process_id": body_digest({"process_id": "b", "payload": {"x": 1}}),
        "perfs_at_plan": {"HOM (%)": 92},
        "predecessor": None,
    }
    case.bind_reviewed("job-00", planned, reviewed, None)
    for change, match in (
        ({"admission": {"admitted": False, "refusal": "HOM"}}, "not admitted"),
        ({"cases_sha256": "d"}, "case changed"),
        ({"body_sha256_without_process_id": body_digest({"payload": {"x": 2}})}, "differs from the preflight"),
        ({"perfs_at_plan": {"HOM (%)": 91.5}}, "perfs moved"),
        ({"predecessor": {"submitted_utc": "t", "sha256": "p"}}, "predecessor differs"),
    ):
        with pytest.raises(RuntimeError, match=match):
            case.bind_reviewed("job-00", planned, {**reviewed, **change}, None)


@pytest.mark.parametrize("estimated", [141191, 254143, 1270715])
def test_samples_fill_the_cap_to_one_quantum(estimated: int) -> None:
    samples = case.samples_for(estimated)
    per_sample = estimated / case.PROBE_SAMPLES
    if samples % case.SAMPLE_QUANTUM or samples * per_sample * tomo.SHOT_MARGIN > case.SHOT_CAP:
        raise AssertionError(f"{samples} samples leave the cap or the quantum")
    if (samples + case.SAMPLE_QUANTUM) * per_sample * tomo.SHOT_MARGIN <= case.SHOT_CAP:
        raise AssertionError(f"{samples} samples leave a quantum unspent")


def test_the_transmittance_floor_puts_the_worst_case_on_max_duration() -> None:
    perfs = case.read_perfs()
    for job in case.JOBS:
        floor = case.transmittance_floor(job, float(perfs["Clock (MHz)"]))
        at_floor = case.worst_case_seconds(job, {**perfs, "Transmittance (%)": floor})
        if abs(at_floor - case.MAX_DURATION) > 1e-6:
            raise AssertionError(f"{job}: the worst case at the floor reads {at_floor} s")
        if case.worst_case_seconds(job, perfs) > case.MAX_DURATION:
            raise AssertionError(f"{job}: the worst case at the read passes max_duration")


def test_the_job_ceiling_bills_one_cap() -> None:
    ceiling = case.credit_ceiling()
    if not math.isclose(ceiling, case.PER_JOB_CREDITS + case.SHOT_CAP * case.PRICE_PER_SHOT):
        raise AssertionError(f"the job ceiling reads {ceiling}")


def test_the_iteration_seconds_come_from_the_retained_runs() -> None:
    if not math.isclose(case.iteration_seconds(), 221 / 72):
        raise AssertionError(f"the iteration seconds read {case.iteration_seconds()}")


def test_the_seed_plan_is_fresh_and_disjoint() -> None:
    plan = case.seed_plan()
    indices = [index for index, _ in [*plan["compilation"], plan["bootstrap"], *plan["forecast"]]]
    if indices != sorted(indices) or len(set(indices)) != len(indices):
        raise AssertionError("the seed plan does not take draw indices in order, each once")
    if {value for _, value in plan["compilation"]} & {value for _, value in tomo.seed_plan()[0]}:
        raise AssertionError("a compilation seed repeats the retained case's")


@pytest.mark.parametrize("job", case.JOBS)
def test_the_retained_request_rebuilds(job: str) -> None:
    case.check_job(job)
