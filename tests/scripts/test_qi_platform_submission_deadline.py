"""Deadline crossings between resource writes preserve checkpoints and block later requests."""

import json
import math
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_platform_submission_deadline as guarded


class Response:
    def __init__(self, payload: Any, status: int = 200) -> None:
        self.payload = payload
        self.status_code = status
        self.content = b"response"
        self.text = "fixture response"

    def json(self) -> Any:
        return self.payload


class Session:
    def __init__(self, clock: list[float], expires_after: tuple[str, str] | None = None) -> None:
        self.clock = clock
        self.expires_after = expires_after
        self.calls: list[tuple[str, str]] = []
        self.headers: dict[str, str] = {}
        self.backend = {
            "id": 7,
            "identifier": "tuna_17",
            "name": "Tuna-17",
            "status": "idle",
            "enabled": True,
            "is_hardware": True,
            "nqubits": 17,
            "max_jobs_per_batch_job": 3,
            "max_number_of_shots": 4096,
            "batchjobs_per_queue_limit": 1,
        }
        self.rejection: tuple[str, str] | None = None
        self.lose_enqueue_response = False
        self.shots = ["0" * 20] * 2048 + ["1" * 20] * 2048
        self.job: dict[str, Any] = {
            "id": 15,
            "batch_job_id": 11,
            "number_of_shots": 4096,
            "status": "completed",
            "raw_data_enabled": True,
            "created_on": "2026-10-27T00:00:00.100000+00:00",
            "queued_at": "2026-10-27T00:00:00.200000+00:00",
            "finished_at": "2026-10-27T00:00:00.800000+00:00",
        }

    def request(self, method: str, url: str, **_kwargs: Any) -> Response:
        path = url.removeprefix(qi_platform.HOST)
        self.calls.append((method, path))
        if (method, path) == self.expires_after:
            self.clock[0] = 100.0
        if (method, path) == self.rejection:
            return Response({}, 401)
        if method == "GET":
            if path == "/jobs/15":
                return Response(self.job)
            if path == "/results/job/15":
                return Response(
                    {
                        "items": [
                            {
                                "job_id": 15,
                                "shots_done": 4096,
                                "shots_requested": 4096,
                                "execution_time_in_seconds": 0.6,
                                "results": dict(Counter(self.shots)),
                                "raw_data": self.shots,
                            }
                        ]
                    }
                )
            if path == "/backend_types/7":
                return Response(self.backend)
            if path == "/backend_types/7/queue":
                return Response({"number_of_jobs_in_queue": 0})
            if path == "/languages":
                return Response({"items": [{"id": 20, "name": "cQASM", "version": "3.0"}], "pages": 1})
            rows = [self.backend] if path == "/backend_types/" else []
            return Response({"items": rows, "pages": 1})
        if method == "PATCH":
            if self.lose_enqueue_response:
                raise TimeoutError("enqueue response lost")
            return Response(None)
        identities = {"/projects": 10, "/batch_jobs": 11, "/algorithms": 12, "/commits": 13, "/files": 14, "/jobs": 15}
        return Response({"id": identities[path]})


@pytest.fixture
def environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, list[float], Session, str]:
    clock = [0.0]
    session = Session(clock)
    monkeypatch.setattr(qi_platform.time, "monotonic", lambda: clock[0])

    def initialize(client: qi_platform.Client) -> None:
        client.session = session
        client.expires = math.inf
        client.member_id = 99

    @contextmanager
    def lock(_path: Path):
        yield

    monkeypatch.setattr(qi_platform.Client, "__init__", initialize)
    monkeypatch.setattr(qi_platform, "token_lock", lock)
    source = "version 3.0\nqubit[17] q\nbit[17] b\nb = measure q\n"
    source_hash = qi_platform.hashlib.sha256(source.encode()).hexdigest()
    manifest = {
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": 4096,
        "nqubits": 17,
        "circuits": [{"file": "control.cq", "sha256": source_hash}],
    }
    (tmp_path / "control.cq").write_text(source)
    content = json.dumps(manifest)
    (tmp_path / "cases.json").write_text(content)
    return tmp_path, clock, session, qi_platform.hashlib.sha256(content.encode()).hexdigest()


@pytest.mark.parametrize(
    ("path", "retained"),
    [
        ("/projects", {"project": 10}),
        ("/batch_jobs", {"project": 10, "batch_job": 11}),
        ("/algorithms", {"algorithm": 12}),
        ("/commits", {"algorithm": 12, "commit": 13}),
        ("/files", {"algorithm": 12, "commit": 13, "file": 14}),
        ("/jobs", {"algorithm": 12, "commit": 13, "file": 14, "job": 15}),
    ],
)
def test_expiry_after_each_resource_blocks_next_request_and_retains_returned_ids(
    environment: tuple[Path, list[float], Session, str], path: str, retained: dict[str, int]
) -> None:
    case, _clock, session, digest = environment
    session.expires_after = ("POST", path)
    with pytest.raises(qi_platform.RequestNotDispatched):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    if session.calls[-1] != ("POST", path):
        raise AssertionError("a later resource request crossed the deadline")
    checkpoint = json.loads((case / "submission-state.json").read_text())
    container = checkpoint if path in {"/projects", "/batch_jobs"} else checkpoint["created_resources"][0]
    if any(container.get(key) != value for key, value in retained.items()):
        raise AssertionError("the checkpoint lost an already created resource identity")
    previous_calls = list(session.calls)
    with pytest.raises((SystemExit, TimeoutError)):
        guarded.submit(case, 7, "retry", execution_deadline=200.0, expected_cases_sha256=digest)
    if session.calls != previous_calls or (case / "submission.json").exists():
        raise AssertionError("a partial creation admitted a retry or a completed receipt")


@pytest.mark.parametrize("path", ["/backend_types/7", "/backend_types/7/queue", "/backend_types/", "/languages"])
def test_expiry_in_validation_reads_blocks_resource_creation(
    environment: tuple[Path, list[float], Session, str], path: str
) -> None:
    case, _clock, session, digest = environment
    session.expires_after = ("GET", path)
    with pytest.raises((TimeoutError, qi_platform.RequestNotDispatched)):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    if any(method != "GET" for method, _path in session.calls):
        raise AssertionError("expired validation reached resource creation")


def test_enqueue_started_before_deadline_can_finish_later(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, digest = environment
    session.expires_after = ("PATCH", "/batch_jobs/11/enqueue")
    report = guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    if report["state"] != "enqueued" or session.calls[-1] != session.expires_after:
        raise AssertionError("the initiation guard became a response-completion deadline")


def test_ambiguous_enqueue_preserves_uncertainty_and_blocks_retry(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, digest = environment
    session.lose_enqueue_response = True
    with pytest.raises(TimeoutError, match="response lost"):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    state = json.loads((case / "submission-state.json").read_text())
    if state["phase"] != "enqueue_outcome_unknown" or state["jobs"][0]["job"] != 15:
        raise AssertionError("an ambiguous enqueue lost its durable identity or uncertainty")
    calls = list(session.calls)
    with pytest.raises(SystemExit, match="read-only recovery"):
        guarded.submit(case, 7, "retry", execution_deadline=100.0)
    if session.calls != calls:
        raise AssertionError("an ambiguous enqueue reached the provider twice")


def test_expired_authentication_retry_cannot_dispatch_again(
    environment: tuple[Path, list[float], Session, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    case, clock, session, digest = environment
    session.rejection = ("POST", "/projects")

    def refresh(_client: qi_platform.Client) -> None:
        clock[0] = 100.0

    monkeypatch.setattr(qi_platform.Client, "refresh", refresh)
    with pytest.raises(qi_platform.RequestRejectedBeforeRetry):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    state = json.loads((case / "submission-state.json").read_text())
    if state["phase"] != "resource-request-rejected" or session.calls.count(session.rejection) != 1:
        raise AssertionError("authentication retry crossed the deadline or lost rejection evidence")


def test_locked_admission_refusal_and_disabled_backend_precede_writes(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, digest = environment

    def refuse(_client: guarded.Client, _live: dict, _queue: dict, _pause: int) -> None:
        raise ValueError("fresh contract drift")

    with pytest.raises(ValueError, match="contract drift"):
        guarded.submit(
            case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest, admission_check=refuse
        )
    session.backend["enabled"] = False
    with pytest.raises(SystemExit, match="disabled"):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    if any(method != "GET" for method, _path in session.calls):
        raise AssertionError("a refused locked admission reached resource creation")


def test_explicit_deadline_cannot_extend_intrinsic_client_window(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    _case, clock, session, _digest = environment
    client = guarded.Client(100.0)
    clock[0] = 100.0
    with pytest.raises(qi_platform.RequestNotDispatched):
        client.patch("/batch_jobs/11/enqueue", execution_deadline=200.0)
    if session.calls:
        raise AssertionError("an explicit later deadline extended the client window")


def test_each_pagination_request_checks_the_intrinsic_deadline(
    environment: tuple[Path, list[float], Session, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _case, clock, session, _digest = environment

    def first_page(_method: str, _url: str, **_kwargs: Any) -> Response:
        session.calls.append(("GET", "/jobs"))
        clock[0] = 100.0
        return Response({"items": [], "pages": 2})

    monkeypatch.setattr(session, "request", first_page)
    with pytest.raises(qi_platform.RequestNotDispatched):
        guarded.Client(100.0).pages("/jobs")
    if len(session.calls) != 1:
        raise AssertionError("pagination initiated a second request after expiry")


def test_account_lock_wait_consumes_the_same_deadline(
    environment: tuple[Path, list[float], Session, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    case, clock, session, digest = environment

    @contextmanager
    def wait_until_expired(_path: Path):
        clock[0] = 100.0
        yield

    monkeypatch.setattr(qi_platform, "token_lock", wait_until_expired)
    with pytest.raises(TimeoutError):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    if session.calls:
        raise AssertionError("an expired account-lock wait reached an API request")


def test_manifest_mismatch_precedes_all_remote_requests(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, _digest = environment
    with pytest.raises(SystemExit, match="approved manifest digest"):
        guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256="0" * 64)
    if session.calls:
        raise AssertionError("an altered manifest reached the service")


def test_same_second_fractional_finish_and_collection_preserve_chronology(
    environment: tuple[Path, list[float], Session, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    case, _clock, session, digest = environment
    observed = datetime.fromisoformat("2026-10-27T00:00:00.900000+00:00")
    monkeypatch.setattr(qi_platform, "utc_now", lambda: observed)
    guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    result = json.loads((case / "results.json").read_text())
    if (
        result["collected_utc"] != observed.isoformat()
        or datetime.fromisoformat(session.job["finished_at"]) > datetime.fromisoformat(result["collected_utc"])
        or json.loads((case / "submission.json").read_text())["submitted_utc"] != observed.isoformat()
    ):
        raise AssertionError("successor timestamps truncated valid fractional-second ordering")


def test_recollection_retains_existing_raw_and_collection_bytes(
    environment: tuple[Path, list[float], Session, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    case, _clock, _session, digest = environment
    observed = [datetime.fromisoformat("2026-10-27T00:00:00.900000+00:00")]
    monkeypatch.setattr(qi_platform, "utc_now", lambda: observed[0])
    guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    before = {name: (case / name).read_bytes() for name in ("results.json", "raw/control.cq.json")}
    observed[0] = datetime.fromisoformat("2026-10-27T00:00:01.100000+00:00")
    guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    if any((case / name).read_bytes() != content for name, content in before.items()):
        raise AssertionError("recollection replaced retained bytes when only the observation time changed")


def test_reordered_recollection_refuses_before_any_retained_file_replacement(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, digest = environment
    guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    before = {name: (case / name).read_bytes() for name in ("results.json", "raw/control.cq.json")}
    session.shots.reverse()
    with pytest.raises(qi_platform.PlatformError, match="recollection conflicts"):
        guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    if any((case / name).read_bytes() != content for name, content in before.items()):
        raise AssertionError("a refused shot permutation replaced retained collection bytes")


def test_collection_expiry_blocks_result_request_and_raw_publication(
    environment: tuple[Path, list[float], Session, str],
) -> None:
    case, _clock, session, digest = environment
    guarded.submit(case, 7, "fixture approval", execution_deadline=100.0, expected_cases_sha256=digest)
    session.expires_after = ("GET", "/jobs/15")
    with pytest.raises(qi_platform.RequestNotDispatched):
        guarded.collect(case, poll=15, timeout=100, execution_deadline=100.0)
    if session.calls[-1] != session.expires_after or (case / "raw").exists() or (case / "results.json").exists():
        raise AssertionError("expired collection fetched or published a later result")
