"""The hardware submission policy a case manifest selects: the legacy rows, the wave-v1 row and every refusal.

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
import qi_platform_submission_deadline as guarded

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
    monkeypatch.setattr(guarded, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    monkeypatch.setattr(guarded, "token_lock", lock, raising=False)
    monkeypatch.setattr(qi_platform, "utc_now", lambda: NOW)
    monkeypatch.setattr(qi_platform, "HARDWARE_PAUSE_SECONDS", 30)
    return fake


def refuses(tmp_path: Path, fake: Service, message: str) -> None:
    """Both submit routes refuse with `message` and neither writes to the service."""
    with pytest.raises(SystemExit, match=message):
        qi_platform.submit(tmp_path, 7, "fixture approval")
    with pytest.raises(SystemExit, match=message):
        guarded.submit(tmp_path, 7, "fixture approval", execution_deadline=time.monotonic() + 1e6)
    if fake.writes:
        raise AssertionError(f"a refused submission wrote {fake.writes}")


def admitted(tmp_path: Path, fake: Service) -> None:
    """Both submit routes pass every guard, so the first remote write (the project) is attempted."""
    for route in (
        lambda: qi_platform.submit(tmp_path, 7, "fixture approval"),
        lambda: guarded.submit(tmp_path, 7, "fixture approval", execution_deadline=time.monotonic() + 1e6),
    ):
        with pytest.raises(WriteAttempted):
            route()
        for leftover in tmp_path.glob("submission-state.json"):
            leftover.unlink()
    if fake.writes != ["/projects", "/projects"]:
        raise AssertionError(f"expected two admitted submissions, saw {fake.writes}")


def test_table_rows_are_the_two_documented_policies() -> None:
    rows = {name: tuple(row) for name, row in qi_platform.HARDWARE_POLICIES.items()}
    if rows != {"legacy": (3, 1), "wave-v1": (5, 3)}:
        raise AssertionError(rows)
    if (qi_platform.HARDWARE_BATCH_CIRCUITS, qi_platform.HARDWARE_QUEUED_BATCHES) != (3, 1):
        raise AssertionError("the legacy constants moved")


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
    service.batches = [batch(1), batch(2)]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=10), job(2, 2, "queued")]
    service.queued = 1
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "wait 20 more seconds")


def test_wave_first_batch_waits_for_the_pause_after_the_previous_wave(tmp_path: Path, service: Service) -> None:
    service.batches = [batch(1)]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=5)]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "wait 25 more seconds")
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=31)]
    admitted(case(tmp_path, 5, hardware_policy="wave-v1"), service)


def test_wave_still_refuses_a_batch_being_planned(tmp_path: Path, service: Service) -> None:
    recent = (NOW - timedelta(seconds=5)).isoformat()
    service.batches = [{**batch(1, status="planned"), "created_on": recent}]
    refuses(case(tmp_path, 5, hardware_policy="wave-v1"), service, "being planned")


def test_pause_state_without_a_wave_counts_no_batch_in_flight(service: Service) -> None:
    service.batches = [batch(1)]
    service.jobs = [job(1, 1, "completed", finished_seconds_ago=0)]
    state = qi_platform.hardware_pause_state(service)  # type: ignore[arg-type]
    if state != (30, 0):
        raise AssertionError(state)


# Mutation test: each refusal is a line of qi_platform.py. A copy of the module with that line disabled admits the
# scenario that the line refuses, so the scenario tests above fail without the line.
MUTATIONS = [
    ("circuits", "if circuits > limits.batch_circuits:", 6, "wave-v1", {"backend": {"max_jobs_per_batch_job": 6}}),
    ("unknown policy", "if type(name) is not str or name not in HARDWARE_POLICIES:", 3, "wave-v2", {}),
    ("in flight", "if in_flight + 1 > limits.queued_batches:", 5, "wave-v1", {"in_flight": 3}),
    ("service queue", "if queued + 1 > queue_limit:", 5, "wave-v1", {"queued": 3}),
    ("legacy default", 'DEFAULT_HARDWARE_POLICY = "legacy"', 4, None, {}),
    (
        "backend queue cap",
        'queued_batches=min(policy.queued_batches, backend_type["batchjobs_per_queue_limit"])',
        5,
        "wave-v1",
        {"backend": {"batchjobs_per_queue_limit": 2}, "in_flight": 2},
    ),
]


def mutant(old: str, new: str) -> types.ModuleType:
    source = Path(qi_platform.__file__).read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise AssertionError(f"{old!r} must occur once in qi_platform.py")
    module = types.ModuleType("qi_platform_mutant")
    module.__file__ = qi_platform.__file__
    sys.modules["qi_platform_mutant"] = module
    try:
        exec(compile(source.replace(old, new), qi_platform.__file__, "exec"), module.__dict__)
    finally:
        del sys.modules["qi_platform_mutant"]
    return module


@pytest.mark.parametrize(("label", "line", "circuits", "policy", "state"), MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_each_refusal_fails_when_its_line_is_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    label: str,
    line: str,
    circuits: int,
    policy: str | None,
    state: dict[str, Any],
) -> None:
    replacement = 'DEFAULT_HARDWARE_POLICY = "wave-v1"' if label == "legacy default" else "if False:"
    if label == "backend queue cap":
        replacement = "queued_batches=policy.queued_batches"
    module = mutant(line, replacement)
    fake = Service(backend(**state.get("backend", {})), [], [], state.get("queued", 0))
    if "in_flight" in state:
        fake.batches = [batch(i) for i in range(1, state["in_flight"] + 1)]
        fake.jobs = [job(i, i, "queued") for i in range(1, state["in_flight"] + 1)]
    monkeypatch.setattr(module, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(module, "utc_now", lambda: NOW)

    @contextmanager
    def lock(_path: Path):
        yield

    monkeypatch.setattr(module, "token_lock", lock)
    fields = {} if policy is None else {"hardware_policy": policy}
    directory = case(tmp_path, circuits, **fields)
    # A removed policy-name check leaves a KeyError at the table lookup, not the named refusal.
    with pytest.raises((WriteAttempted, KeyError) if label == "unknown policy" else WriteAttempted):
        module.submit(directory, 7, "fixture approval")
    # The same scenario on the real module is refused before any write.
    fake.writes.clear()
    (directory / "submission-state.json").unlink(missing_ok=True)
    monkeypatch.setattr(qi_platform, "Client", lambda *_a, **_k: fake)
    monkeypatch.setattr(qi_platform, "utc_now", lambda: NOW)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    with pytest.raises(SystemExit):
        qi_platform.submit(directory, 7, "fixture approval")
    if fake.writes:
        raise AssertionError("the unmutated module wrote before refusing")
