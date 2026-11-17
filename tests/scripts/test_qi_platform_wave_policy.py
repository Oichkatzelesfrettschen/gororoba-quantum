"""The hardware submission policy a case manifest selects (qi_platform_wave): the legacy row, the wave-v1 row, every
refusal and the series driver.

Each refusal test runs `submit` against a fake service that raises on any resource write, so a refusal is proven to
happen before the first remote write. Expected limits are written out in the tests, not read from the policy table.
"""

import hashlib
import json
import sys
import time
import types
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_platform_wave as wave

SOURCE = "version 3.0\nqubit[5] q\nbit[5] b\nb = measure q\n"
NOW = datetime(2026, 11, 14, 12, 0, 0, tzinfo=UTC)
LONG_AGO = (NOW - timedelta(hours=1)).isoformat()


class WriteAttempted(AssertionError):
    pass


class Service:
    """A fake Quantum Inspire client: backend type 7 is hardware, 8 is another hardware type, 1 is an emulator."""

    def __init__(self, backend: dict[str, Any], batches: list[dict[str, Any]], jobs: list[dict[str, Any]], queued: int):
        self.backend = backend
        self.batches = batches
        self.jobs = jobs
        self.queued = queued
        self.member_id = 1
        self.writes: list[str] = []

    def get(self, path: str, *, execution_deadline: float | None = None, **params: Any) -> Any:
        if path == f"/backend_types/{self.backend['id']}":
            return self.backend
        if path.endswith("/queue"):
            return {"number_of_jobs_in_queue": self.queued}
        raise AssertionError(path)

    def pages(self, path: str, *, execution_deadline: float | None = None, **params: Any) -> list[dict[str, Any]]:
        if path == "/backend_types/":
            return [
                {"id": 7, "is_hardware": True},
                {"id": 5, "is_hardware": True},
                {"id": 8, "is_hardware": True},
                {"id": 1, "is_hardware": False},
            ]
        if path == "/batch_jobs":
            return self.batches
        if path == "/jobs":
            return self.jobs
        if path == "/languages":
            return [{"id": 20, "name": "cQASM", "version": "3.0"}]
        raise AssertionError(path)

    def post(self, path: str, body: dict[str, Any], **_kwargs: Any) -> Any:
        self.writes.append(path)
        raise WriteAttempted(path)

    def patch(self, path: str, **_kwargs: Any) -> Any:
        self.writes.append(path)
        raise WriteAttempted(path)


def backend(**changes: Any) -> dict[str, Any]:
    record = {
        "id": 7,
        "identifier": "tuna_17",
        "name": "Tuna-17",
        "status": "idle",
        "enabled": True,
        "is_hardware": True,
        "nqubits": 17,
        "max_jobs_per_batch_job": 5,
        "max_number_of_shots": 131072,
        "batchjobs_per_queue_limit": 5,
    }
    return record | changes


def batch(identifier: int, type_id: int = 7, status: str = "queued") -> dict[str, Any]:
    return {"id": identifier, "backend_type_id": type_id, "status": status, "created_on": LONG_AGO}


def job(identifier: int, batch_id: int, status: str, finished_seconds_ago: float | None = None) -> dict[str, Any]:
    finished = None if finished_seconds_ago is None else (NOW - timedelta(seconds=finished_seconds_ago)).isoformat()
    return {"id": identifier, "batch_job_id": batch_id, "status": status, "finished_at": finished}


def case(tmp_path: Path, circuits: int, **fields: Any) -> Path:
    digest = hashlib.sha256(SOURCE.encode()).hexdigest()
    manifest: dict[str, Any] = {
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": 1024,
        "nqubits": 5,
        "circuits": [{"file": f"c{i}.cq", "sha256": digest} for i in range(circuits)],
    } | fields
    for row in manifest["circuits"]:
        (tmp_path / row["file"]).write_text(SOURCE)
    (tmp_path / "cases.json").write_text(json.dumps(manifest))
    return tmp_path


@pytest.fixture
def service(monkeypatch: pytest.MonkeyPatch) -> Service:
    fake = Service(backend(), [], [], 0)

    @contextmanager
    def lock(_path: Path):
        yield

    monkeypatch.setattr(qi_platform, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    monkeypatch.setattr(qi_platform, "utc_now", lambda: NOW)
    monkeypatch.setattr(qi_platform, "HARDWARE_PAUSE_SECONDS", 30)
    return fake


def refuses(tmp_path: Path, fake: Service, message: str) -> None:
    """The wave route refuses with `message` and writes nothing to the service."""
    with pytest.raises(SystemExit, match=message):
        wave.submit(tmp_path, 7, "fixture approval")
    if fake.writes:
        raise AssertionError(f"a refused submission wrote {fake.writes}")


def admitted(tmp_path: Path, fake: Service) -> None:
    """The wave route passes every guard, so the first remote write (the project) is attempted."""
    with pytest.raises(WriteAttempted):
        wave.submit(tmp_path, 7, "fixture approval", execution_deadline=time.monotonic() + 1e6)
    for leftover in tmp_path.glob("submission-state.json"):
        leftover.unlink()
    if fake.writes != ["/projects"]:
        raise AssertionError(f"expected one admitted submission, saw {fake.writes}")


def test_table_rows_are_the_two_documented_policies() -> None:
    rows = {name: tuple(row) for name, row in wave.HARDWARE_POLICIES.items()}
    if rows != {"legacy": (3, 1, None), "wave-v1": (5, 3, 60)}:
        raise AssertionError(rows)
    if (qi_platform.HARDWARE_BATCH_CIRCUITS, qi_platform.HARDWARE_QUEUED_BATCHES) != (3, 1):
        raise AssertionError("the legacy constants of qi_platform moved")
    if hasattr(qi_platform, "HARDWARE_POLICIES") or hasattr(qi_platform, "hardware_admission"):
        raise AssertionError("the pinned platform module carries the wave policy")


def test_the_pinned_submit_routes_keep_the_legacy_limits(tmp_path: Path, service: Service) -> None:
    # A wave-v1 manifest reaches qi_platform.submit only as a legacy batch: four circuits exceed its three.
    case(tmp_path, 4, hardware_policy="wave-v1")
    with pytest.raises(SystemExit, match="4 circuits exceed the 3 a hardware batch may hold"):
        qi_platform.submit(tmp_path, 7, "fixture approval")
    if service.writes:
        raise AssertionError(f"a refused submission wrote {service.writes}")


def test_manifest_without_the_field_refuses_a_four_circuit_batch(tmp_path: Path, service: Service) -> None:
    refuses(case(tmp_path, 4), service, "4 circuits exceed the 3 a hardware batch may hold")


def test_legacy_name_refuses_a_four_circuit_batch(tmp_path: Path, service: Service) -> None:
    refuses(case(tmp_path, 4, hardware_policy="legacy"), service, "4 circuits exceed the 3")


def test_legacy_admits_three_circuits(tmp_path: Path, service: Service) -> None:
    admitted(case(tmp_path, 3), service)


def test_legacy_refuses_a_second_queued_batch(tmp_path: Path, service: Service) -> None:
    service.queued = 1
    refuses(case(tmp_path, 3), service, "current-user queue has 1 batches; adding one exceeds the limit 1")


def test_legacy_refuses_any_unfinished_hardware_job(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1)]
    service.jobs = [job(1, 1, "running")]
    refuses(case(tmp_path, 3), service, "hardware job 1 is running")


@pytest.mark.parametrize("name", ["wave-v2", "", "WAVE-V1", "wave-v1 "])
def test_unknown_policy_name_is_refused_before_any_service_read(tmp_path: Path, service: Service, name: str) -> None:
    refuses(case(tmp_path, 3, hardware_policy=name), service, "hardware_policy")


@pytest.mark.parametrize("value", [None, 1, ["wave-v1"]])
def test_non_string_policy_is_refused(tmp_path: Path, service: Service, value: Any) -> None:
    refuses(case(tmp_path, 3, hardware_policy=value), service, "hardware_policy")


def test_wave_refuses_a_six_circuit_batch(tmp_path: Path, service: Service) -> None:
    refuses(case(tmp_path, 6, hardware_policy="wave-v1"), service, "6 circuits exceed")


def test_wave_admits_a_five_circuit_batch(tmp_path: Path, service: Service) -> None:
    admitted(case(tmp_path, 5, hardware_policy="wave-v1"), service)


def test_wave_circuits_are_capped_by_the_backend_record(tmp_path: Path, service: Service) -> None:
    service.backend = backend(max_jobs_per_batch_job=4)
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "5 circuits exceed")


@pytest.mark.parametrize("earlier", [1, 2])
def test_wave_admits_the_second_and_third_batch(tmp_path: Path, service: Service, earlier: int) -> None:
    service.batches = [batch(i) for i in range(1, earlier + 1)]
    service.jobs = [job(i, i, "queued") for i in range(1, earlier + 1)]
    service.queued = earlier
    admitted(case(tmp_path, 5, hardware_policy="wave-v1"), service)


def test_wave_refuses_a_fourth_queued_batch(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1), batch(2), batch(3)]
    service.jobs = [job(1, 1, "running"), job(2, 2, "queued"), job(3, 3, "queued")]
    service.queued = 3
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "limit 3")


def test_wave_counts_a_queued_batch_whose_jobs_the_job_read_omits(tmp_path: Path, service: Service) -> None:
    # Three batches the service lists as queued, running or reserved, none with a listed job yet.
    service.batches = [batch(1, status="queued"), batch(2, status="running"), batch(3, status="reserved")]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "3 batches in flight")
    service.batches = [batch(1, status="queued"), batch(2, status="finished")]
    service.jobs = [job(2, 2, "completed", finished_seconds_ago=100)]
    admitted(case(tmp_path, 5, hardware_policy="wave-v1"), service)


def test_wave_refuses_when_the_service_queue_holds_three(tmp_path: Path, service: Service) -> None:
    service.queued = 3
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "current-user queue has 3 batches")


def test_wave_counts_a_running_batch_that_the_service_queue_omits(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1), batch(2), batch(3)]
    service.jobs = [job(1, 1, "running"), job(2, 2, "queued"), job(3, 3, "queued")]
    service.queued = 2
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "3 batches in flight")


def test_wave_queue_limit_is_capped_by_the_backend_record(tmp_path: Path, service: Service) -> None:
    service.backend = backend(batchjobs_per_queue_limit=2)
    service.batches = [batch(1), batch(2)]
    service.jobs = [job(1, 1, "running"), job(2, 2, "queued")]
    service.queued = 2
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "limit 2")


def test_wave_refuses_an_unfinished_job_on_another_hardware_type(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, type_id=8)]
    service.jobs = [job(1, 1, "running")]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "hardware job 1 is running")


def test_wave_keeps_the_pause_of_a_finished_batch(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, status="finished"), batch(2)]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=10), job(2, 2, "queued")]
    service.queued = 1
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "wait 50 more seconds")


def test_wave_first_batch_waits_for_the_pause_after_the_previous_wave(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, status="finished")]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=5)]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "wait 55 more seconds")
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=61)]
    admitted(case(tmp_path, 5, hardware_policy="wave-v1"), service)


def test_wave_refuses_an_active_batch_of_another_type_that_the_job_read_omits(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, type_id=8, status="running")]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "hardware batch 1 is running without a listed job")


def test_legacy_refuses_an_active_batch_that_the_job_read_omits(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, status="queued")]
    refuses(case(tmp_path, 3), service, "hardware batch 1 is queued without a listed job")


def test_wave_still_refuses_a_batch_being_planned(tmp_path: Path, service: Service) -> None:
    recent = (NOW - timedelta(seconds=5)).isoformat()
    service.batches = [{**batch(1, status="planned"), "created_on": recent}]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "being planned")


def test_pause_state_without_a_wave_counts_no_batch_in_flight(service: Service) -> None:
    service.batches = [batch(1)]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=0)]
    state = wave.hardware_pause_state(service, 30)  # type: ignore[arg-type]
    if state != (30, 0):
        raise AssertionError(state)


# Ry (type 5) is flagged is_hardware, so it shares the hardware rules and one pause clock with Tuna-17 (type 7).


def admit(service: Service, type_id: int, circuits: int = 5, **fields: Any) -> tuple[int, int]:
    manifest = {"hardware_policy": "wave-v1", **fields}
    return wave.hardware_admission(
        service,  # type: ignore[arg-type]
        manifest,
        backend(id=type_id),
        type_id,
        circuits,
        backend()["batchjobs_per_queue_limit"],
    )


def test_a_wave_counts_its_batches_per_backend_type_and_not_across_ry_and_tuna(service: Service) -> None:
    # Two Ry batches in flight leave a Tuna wave refused (another hardware type is unfinished), not counted: the
    # three-batch count holds per backend type, and a wave on one type needs every other hardware type idle.
    service.batches = [batch(1, type_id=5), batch(2, type_id=5)]
    service.jobs = [job(1, 1, "running"), job(2, 2, "queued")]
    with pytest.raises(SystemExit, match="hardware job 1 is running"):
        admit(service, 7)
    # The Ry wave itself admits its third batch and refuses a fourth.
    if admit(service, 5)[1] != 0:
        raise AssertionError("the third Ry batch is admitted without a pause")
    service.batches.append(batch(3, type_id=5))
    service.jobs.append(job(3, 3, "queued"))
    with pytest.raises(SystemExit, match="3 batches in flight"):
        admit(service, 5)


def test_the_pause_of_a_finished_ry_batch_holds_the_first_tuna_batch_of_a_wave(service: Service) -> None:
    service.batches = [batch(1, type_id=5, status="finished")]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=10)]
    with pytest.raises(SystemExit, match="wait 50 more seconds"):
        admit(service, 7)
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=65)]
    if admit(service, 7) != (3, 0):
        raise AssertionError("the pause has passed")


@pytest.mark.parametrize(("ladder", "pause"), [(30, 60), (60, 60), (90, 90), (120, 120)])
def test_the_wave_pause_is_the_row_raised_to_the_ladder_step(
    service: Service, monkeypatch: pytest.MonkeyPatch, ladder: int, pause: int
) -> None:
    monkeypatch.setattr(qi_platform, "HARDWARE_PAUSE_SECONDS", ladder)
    service.batches = [batch(1, status="finished")]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=40)]
    with pytest.raises(SystemExit, match=f"wait {pause - 40} more seconds"):
        admit(service, 7)


def test_a_finished_batch_without_listed_jobs_keeps_its_pause_through_the_batch_finish_time(service: Service) -> None:
    finished = (NOW - timedelta(seconds=15)).isoformat()
    service.batches = [batch(1, status="finished") | {"finished_at": finished}]
    service.jobs = []
    with pytest.raises(SystemExit, match="wait 45 more seconds"):
        admit(service, 7)


def test_three_jobless_queued_batches_refuse_a_fourth(service: Service) -> None:
    service.batches = [batch(i, status="queued") for i in range(1, 4)]
    service.jobs = []
    with pytest.raises(SystemExit, match="3 batches in flight"):
        admit(service, 7)


def test_the_legacy_pause_is_the_ladder_step(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1, status="finished")]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=10)]
    refuses(case(tmp_path, 3), service, "wait 20 more seconds")


# Mutation test: each refusal is a line of qi_platform_wave.py. A copy of the module with that line disabled admits the
# scenario that the line refuses, so the scenario tests above fail without the line.
MUTATIONS = [
    ("circuits", "if circuits > limits.batch_circuits:", 6, "wave-v1", {"backend": {"max_jobs_per_batch_job": 6}}),
    ("unknown policy", "if type(name) is not str or name not in HARDWARE_POLICIES:", 3, "wave-v2", {}),
    ("in flight", "if in_flight + 1 > limits.queued_batches:", 5, "wave-v1", {"in_flight": 3}),
    ("service queue", "if queued + 1 > queue_limit:", 5, "wave-v1", {"queued": 3}),
    (
        "batch rows",
        "if row_status in IN_FLIGHT_BATCH_STATUSES and batches[batch_id] == wave_backend_type_id",
        5,
        "wave-v1",
        {"in_flight_rows": 3},
    ),
    (
        "jobless active batch",
        "if row_status in IN_FLIGHT_BATCH_STATUSES and batch_id not in listed and not own_type:",
        5,
        "wave-v1",
        {"other_type_rows": 1},
    ),
    ("legacy default", 'DEFAULT_HARDWARE_POLICY = "legacy"', 4, None, {}),
    (
        "backend queue cap",
        'queued_batches=min(policy.queued_batches, backend_type["batchjobs_per_queue_limit"]),',
        5,
        "wave-v1",
        {"backend": {"batchjobs_per_queue_limit": 2}, "in_flight": 2},
    ),
    ("pause", "if left > 0:", 5, "wave-v1", {"finished_seconds_ago": 10}),
    (
        "batch finish pause",
        "if finished_at is not None:",
        5,
        "wave-v1",
        {"batch_finished_seconds_ago": 10},
    ),
]


def mutant(old: str, new: str) -> types.ModuleType:
    source = Path(wave.__file__).read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise AssertionError(f"{old!r} must occur once in qi_platform_wave.py")
    module = types.ModuleType("qi_platform_wave_mutant")
    module.__file__ = wave.__file__
    sys.modules["qi_platform_wave_mutant"] = module
    try:
        exec(compile(source.replace(old, new), wave.__file__, "exec"), module.__dict__)
    finally:
        del sys.modules["qi_platform_wave_mutant"]
    return module


@pytest.mark.parametrize(("label", "line", "circuits", "policy", "state"), MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_each_refusal_fails_when_its_line_is_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    service: Service,
    label: str,
    line: str,
    circuits: int,
    policy: str | None,
    state: dict[str, Any],
) -> None:
    replacements = {
        "legacy default": 'DEFAULT_HARDWARE_POLICY = "wave-v1"',
        "batch rows": "if False",
        "backend queue cap": "queued_batches=policy.queued_batches,",
    }
    module = mutant(line, replacements.get(label, "if False:"))
    fake = Service(backend(**state.get("backend", {})), [], [], state.get("queued", 0))
    if "in_flight_rows" in state:
        fake.batches = [batch(i, status="queued") for i in range(1, state["in_flight_rows"] + 1)]
    if "other_type_rows" in state:
        fake.batches = [batch(1, type_id=8, status="running")]
    if "in_flight" in state:
        fake.batches = [batch(i) for i in range(1, state["in_flight"] + 1)]
        fake.jobs = [job(i, i, "queued") for i in range(1, state["in_flight"] + 1)]
    if "finished_seconds_ago" in state:
        fake.batches = [batch(1, status="finished")]
        fake.jobs = [job(1, 1, "completed", finished_seconds_ago=state["finished_seconds_ago"])]
    if "batch_finished_seconds_ago" in state:
        finished = (NOW - timedelta(seconds=state["batch_finished_seconds_ago"])).isoformat()
        fake.batches = [batch(1, status="finished") | {"finished_at": finished}]
    monkeypatch.setattr(qi_platform, "Client", lambda *_a, **_k: fake)
    fields = {} if policy is None else {"hardware_policy": policy}
    directory = case(tmp_path, circuits, **fields)
    # A removed policy-name check leaves a KeyError at the table lookup, not the named refusal.
    with pytest.raises((WriteAttempted, KeyError) if label == "unknown policy" else WriteAttempted):
        module.submit(directory, 7, "fixture approval")
    # The same scenario on the real module is refused before any write.
    fake.writes.clear()
    (directory / "submission-state.json").unlink(missing_ok=True)
    with pytest.raises(SystemExit):
        wave.submit(directory, 7, "fixture approval")
    if fake.writes:
        raise AssertionError("the unmutated module wrote before refusing")


# The series driver: waves of back-to-back submissions, every wave collected before the next is submitted.


def series(tmp_path: Path, waves: list[list[str]], policy: str = "wave-v1") -> Path:
    directory = tmp_path / "series"
    directory.mkdir()
    for name in sorted({n for w in waves for n in w}):
        (directory / name).mkdir()
        (directory / name / "cases.json").write_text("{}")
    (directory / "cases.json").write_text(json.dumps({"hardware_policy": policy, "waves": waves}))
    return directory


def drive(
    monkeypatch: pytest.MonkeyPatch,
    directory: Path,
    tmp_path: Path,
    refuse: dict[str, int] | None = None,
    **kwargs: Any,
) -> tuple[list[str], list[float]]:
    events: list[str] = []
    sleeps: list[float] = []
    pending = dict(refuse or {})

    def fake_submit(run: Path, backend_type_id: int, approval: str, **_k: Any) -> dict[str, Any]:
        batch_name = run.name.rsplit("-", 1)[-1]
        if pending.get(run.name, 0) > 0:
            pending[run.name] -= 1
            raise wave.PauseRefused("wait 12 more seconds", 12)
        events.append(f"submit {run.name.split('-', 2)[-1]}")
        return {"batch_job": 1, "jobs": [], "name": batch_name}

    monkeypatch.setattr(wave, "submit", fake_submit)
    monkeypatch.setattr(
        wave, "collect", lambda run, poll, timeout, **_k: events.append(f"collect {run.name.split('-', 2)[-1]}")
    )
    wave.run_series(directory, tmp_path / "runs", "STAMP", 7, "approval", sleep=sleeps.append, sanity=None, **kwargs)
    return events, sleeps


def test_the_series_submits_a_wave_back_to_back_and_collects_it_before_the_next_wave(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = series(tmp_path, [["batch-00", "batch-01", "batch-02"], ["batch-03"]])
    events, sleeps = drive(monkeypatch, directory, tmp_path)
    expected = [
        "submit batch-00",
        "submit batch-01",
        "submit batch-02",
        "collect batch-00",
        "collect batch-01",
        "collect batch-02",
        "submit batch-03",
        "collect batch-03",
    ]
    if events != expected or sleeps:
        raise AssertionError((events, sleeps))


def test_the_series_sleeps_the_pause_remainder_and_retries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    directory = series(tmp_path, [["batch-00"], ["batch-01"]])
    events, sleeps = drive(monkeypatch, directory, tmp_path, refuse={"STAMP-series-batch-01": 2})
    if sleeps != [13, 13] or events[-2:] != ["submit batch-01", "collect batch-01"]:
        raise AssertionError((events, sleeps))


def test_the_series_stops_after_the_tenth_consecutive_pause_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = series(tmp_path, [["batch-00"]])
    with pytest.raises(wave.PauseRefused):
        drive(monkeypatch, directory, tmp_path, refuse={"STAMP-series-batch-00": 99})


def test_the_series_checks_every_destination_before_its_first_submission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = series(tmp_path, [["batch-00", "batch-01", "batch-02"]])
    (tmp_path / "runs" / "STAMP-series-batch-02").mkdir(parents=True)
    events: list[str] = []
    monkeypatch.setattr(wave, "submit", lambda *_a, **_k: events.append("submit"))
    with pytest.raises(SystemExit, match="never resubmitted"):
        wave.run_series(directory, tmp_path / "runs", "STAMP", 7, "approval")
    if events or (tmp_path / "runs" / "STAMP-series-batch-00").exists():
        raise AssertionError(f"a later destination was checked after a submission: {events}")


def test_the_series_never_resubmits_an_existing_run_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    directory = series(tmp_path, [["batch-00"]])
    (tmp_path / "runs" / "STAMP-series-batch-00").mkdir(parents=True)
    with pytest.raises(SystemExit, match="never resubmitted"):
        drive(monkeypatch, directory, tmp_path)


@pytest.mark.parametrize(
    ("waves", "policy", "message"),
    [
        ([["batch-00", "batch-01", "batch-02", "batch-03"]], "wave-v1", "more than the 3 batches"),
        ([["batch-00", "batch-01"]], "legacy", "more than the 1 batches"),
        ([["batch-00"]], "wave-v2", "hardware_policy"),
        ([["batch-00"], ["batch-00"]], "wave-v1", "waves list"),
    ],
)
def test_the_series_refuses_a_wave_list_beyond_its_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, waves: list[list[str]], policy: str, message: str
) -> None:
    directory = series(tmp_path, waves, policy)
    with pytest.raises(SystemExit, match=message):
        drive(monkeypatch, directory, tmp_path)


class Rival(Service):
    """A service that accepts every write; once the submitter's last job exists, a rival client enqueues `arrival`."""

    OWN_BATCH = 900

    def __init__(
        self, *args: Any, arrival: list[dict[str, Any]], arrival_jobs: list[dict[str, Any]], queued_after: int
    ):
        super().__init__(*args)
        self.arrival = arrival
        self.arrival_jobs = arrival_jobs
        self.queued_after = queued_after
        self.created_jobs = 0
        self.patched: list[str] = []
        self.counter = 1000

    def post(self, path: str, body: dict[str, Any], **_kwargs: Any) -> Any:
        self.writes.append(path)
        self.counter += 1
        if path == "/batch_jobs":
            self.batches.append({**batch(self.OWN_BATCH, 7, "planned"), "created_on": NOW.isoformat()})
            return {"id": self.OWN_BATCH}
        if path == "/jobs":
            self.created_jobs += 1
            if self.created_jobs == 1:
                self.batches.extend(self.arrival)
                self.jobs.extend(self.arrival_jobs)
                self.queued = self.queued_after
        return {"id": self.counter}

    def patch(self, path: str, **_kwargs: Any) -> Any:
        self.patched.append(path)
        return {}


def rival_service(
    monkeypatch: pytest.MonkeyPatch,
    earlier: int,
    *,
    arrival: list[dict[str, Any]],
    arrival_jobs: list[dict[str, Any]],
    queued_after: int,
) -> Rival:
    batches = [batch(100 + i) for i in range(earlier)]
    jobs = [job(200 + i, 100 + i, "queued") for i in range(earlier)]
    fake = Rival(
        backend(), batches, jobs, earlier, arrival=arrival, arrival_jobs=arrival_jobs, queued_after=queued_after
    )

    @contextmanager
    def lock(_path: Path):
        yield

    monkeypatch.setattr(qi_platform, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    monkeypatch.setattr(qi_platform, "utc_now", lambda: NOW)
    monkeypatch.setattr(qi_platform, "HARDWARE_PAUSE_SECONDS", 30)
    return fake


def state_phase(tmp_path: Path) -> str:
    return str(json.loads((tmp_path / "submission-state.json").read_text())["phase"])


def test_a_batch_that_a_rival_enqueues_after_admission_is_not_enqueued(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two batches are queued when the admission reads them (two in flight, one slot left); a rival client then fills
    # the slot, so the re-read before the enqueue sees three in flight and refuses to send the PATCH.
    case(tmp_path, 2, hardware_policy="wave-v1")
    fake = rival_service(monkeypatch, 2, arrival=[batch(300)], arrival_jobs=[job(400, 300, "queued")], queued_after=3)
    with pytest.raises(SystemExit, match="3 batches in flight at the enqueue"):
        wave.submit(tmp_path, 7, "fixture approval")
    if fake.patched:
        raise AssertionError(f"a refused batch was still enqueued: {fake.patched}")
    if state_phase(tmp_path) != "enqueue-refused" or (tmp_path / "submission.json").exists():
        raise AssertionError("the refusal left no enqueue-refused state or wrote a receipt")


def test_the_enqueue_recheck_leaves_the_submitters_own_planned_batch_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One earlier batch is queued and a rival enqueues a second after the admission: the fresh read holds two rival
    # batches and the submitter's own planned one, so a recheck that counted its own batch would see three and refuse.
    case(tmp_path, 2, hardware_policy="wave-v1")
    fake = rival_service(monkeypatch, 1, arrival=[batch(300)], arrival_jobs=[job(400, 300, "queued")], queued_after=2)
    rechecks: list[int] = []
    real = wave.recheck_before_enqueue

    def spy(client: Any, cases: dict[str, Any], backend_type: dict[str, Any], type_id: int, own_batch: int) -> None:
        rechecks.append(own_batch)
        real(client, cases, backend_type, type_id, own_batch)

    monkeypatch.setattr(wave, "recheck_before_enqueue", spy)
    record = wave.submit(tmp_path, 7, "fixture approval")
    if rechecks != [Rival.OWN_BATCH]:
        raise AssertionError(f"the fresh recheck ran for batches {rechecks}")
    if fake.patched != [f"/batch_jobs/{Rival.OWN_BATCH}/enqueue"] or record["state"] != "enqueued":
        raise AssertionError(f"patched {fake.patched}, receipt {record['state']}")


def test_the_enqueue_recheck_refuses_a_rival_job_under_the_legacy_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case(tmp_path, 2)
    fake = rival_service(monkeypatch, 0, arrival=[batch(300)], arrival_jobs=[job(400, 300, "running")], queued_after=1)
    with pytest.raises(SystemExit, match="hardware job 400 is running"):
        wave.submit(tmp_path, 7, "fixture approval")
    if fake.patched or state_phase(tmp_path) != "enqueue-refused":
        raise AssertionError(f"patched {fake.patched}, phase {state_phase(tmp_path)}")


def test_the_enqueue_recheck_refuses_when_the_account_queue_filled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case(tmp_path, 2, hardware_policy="wave-v1")
    fake = rival_service(monkeypatch, 0, arrival=[], arrival_jobs=[], queued_after=3)
    with pytest.raises(SystemExit, match="current-user queue has 3 batches at the enqueue"):
        wave.submit(tmp_path, 7, "fixture approval")
    if fake.patched:
        raise AssertionError(f"patched {fake.patched}")


class Live(Service):
    """A service whose queue follows the writes: a created batch is planned, the enqueue PATCH queues it, and
    `finish` completes it at the clock's time, so the real admission and the real series driver run against it."""

    def __init__(self, clock: dict[str, datetime]):
        super().__init__(backend(), [], [], 0)
        self.clock = clock
        self.counter = 1000
        self.max_in_flight = 0

    def get(self, path: str, *, execution_deadline: float | None = None, **params: Any) -> Any:
        if path.endswith("/queue"):
            return {
                "number_of_jobs_in_queue": sum(row["status"] in wave.IN_FLIGHT_BATCH_STATUSES for row in self.batches)
            }
        return super().get(path, execution_deadline=execution_deadline, **params)

    def post(self, path: str, body: dict[str, Any], **_kwargs: Any) -> Any:
        self.counter += 1
        if path == "/batch_jobs":
            row = {
                "id": self.counter,
                "backend_type_id": 7,
                "status": "planned",
                "created_on": self.clock["now"].isoformat(),
            }
            self.batches.append(row)
        elif path == "/jobs":
            self.jobs.append(
                {"id": self.counter, "batch_job_id": body["batch_job_id"], "status": "queued", "finished_at": None}
            )
        return {"id": self.counter}

    def patch(self, path: str, **_kwargs: Any) -> Any:
        identifier = int(path.split("/")[2])
        for row in self.batches:
            if row["id"] == identifier:
                row["status"] = "queued"
        self.max_in_flight = max(
            self.max_in_flight, sum(r["status"] in wave.IN_FLIGHT_BATCH_STATUSES for r in self.batches)
        )
        return {}

    def finish(self, identifier: int) -> None:
        for row in self.batches:
            if row["id"] == identifier:
                row["status"] = "finished"
                row["finished_at"] = self.clock["now"].isoformat()
        for row in self.jobs:
            if row["batch_job_id"] == identifier:
                row.update(status="completed", finished_at=self.clock["now"].isoformat())


def test_a_twelve_wave_series_pays_eleven_pauses_of_the_policy_and_never_queues_a_fourth_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The bracketed case lists 35 batches in 12 waves (eleven of three, one of two) and states 11 pauses of 60 s.
    # Each wave ends with a collection (5 s here) and the driver sleeps the remainder of the 60 s pause plus one second,
    # so every pause from the last finish to the next submit is 61 s: 11 x 61 s = 671 s against the stated 660 s.
    clock = {"now": NOW}
    fake = Live(clock)
    waves = [[f"batch-{3 * w + i:02d}" for i in range(3)] for w in range(11)] + [["batch-33", "batch-34"]]
    directory = tmp_path / "series"
    directory.mkdir()
    for name in sorted({n for group in waves for n in group}):
        (directory / name).mkdir()
        case(directory / name, 2, hardware_policy="wave-v1")
    (directory / "cases.json").write_text(json.dumps({"hardware_policy": "wave-v1", "waves": waves}))

    @contextmanager
    def lock(_path: Path):
        yield

    sleeps: list[float] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock["now"] += timedelta(seconds=seconds)

    def collect(run: Path, poll: float, timeout: float, **_k: Any) -> None:
        fake.finish(json.loads((run / "submission.json").read_text())["batch_job"])
        clock["now"] += timedelta(seconds=5)

    monkeypatch.setattr(qi_platform, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    monkeypatch.setattr(qi_platform, "utc_now", lambda: clock["now"])
    monkeypatch.setattr(qi_platform, "HARDWARE_PAUSE_SECONDS", 30)
    monkeypatch.setattr(wave, "collect", collect)
    runs = wave.run_series(directory, tmp_path / "runs", "STAMP", 7, "approval", sleep=sleep)
    if len(runs) != 35 or fake.max_in_flight != 3:
        raise AssertionError(f"{len(runs)} runs, at most {fake.max_in_flight} batches in flight")
    if sleeps != [56.0] * 11:
        raise AssertionError(f"pauses {sleeps} total {sum(sleeps)} s, the case states 11 x 60 s")
