"""A hardware admission read under SUBMIT_LOCK takes the submit lease, writes stop at its deadline, and the lease is
freed only after the created batch job reads as enqueued."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_submit_lease

NONCE = "0123456789abcdef" * 2
BROKER = """
import json, sys
from pathlib import Path
log = Path(sys.argv[1])
log.write_text((log.read_text() if log.exists() else "") + " ".join(sys.argv[2:]) + "\\n")
if sys.argv[2] == "refuse":
    print("broker.py: lease held by lab-a1 for 400 more seconds", file=sys.stderr)
    raise SystemExit(3)
print(json.dumps({"nonce": sys.argv[3], "lease_seconds": float(sys.argv[2]), "released": True}))
"""


class Response:
    def __init__(self, payload: Any) -> None:
        self.status_code = 200
        self.content = b"x"
        self.text = ""
        self.payload = payload

    def json(self) -> Any:
        return self.payload


class Http:
    """The service as Client.request sees it: list reads, one batch job whose status the fixture sets."""

    def __init__(self, batch_status: str = "queued") -> None:
        self.batch_status = batch_status
        self.sent: list[tuple[str, str]] = []

    def request(self, method: str, url: str, **_: Any) -> Response:
        path = url.removeprefix(qi_platform.HOST)
        self.sent.append((method, path))
        if path == "/backend_types/":
            return Response({"items": [{"id": 1, "is_hardware": False}, {"id": 7, "is_hardware": True}], "pages": 1})
        if path == "/batch_jobs" and method == "POST":
            return Response({"id": 31})
        if path == "/batch_jobs/31":
            if self.batch_status == "unreadable":
                raise ConnectionError("fixture read failure")
            return Response({"id": 31, "status": self.batch_status})
        return Response({"items": [], "pages": 1})


def client(http: Http) -> qi_platform.Client:
    made = object.__new__(qi_platform.Client)
    made.expires = float("inf")
    made.session = http  # type: ignore[assignment]
    return made


def same(found: object, wanted: object) -> None:
    if found != wanted:
        raise AssertionError(f"{found!r} differs from {wanted!r}")


@pytest.fixture
def broker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    script, log = tmp_path / "broker.py", tmp_path / "broker.log"
    script.write_text(BROKER, encoding="utf-8")
    monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, f"{sys.executable} -I {script} {log} 600 {NONCE}")
    monkeypatch.setenv(qi_submit_lease.HOLDER_VARIABLE, "fixture-host")
    monkeypatch.setattr(qi_platform, "SUBMIT_LOCK", tmp_path / "submit.lock")
    return log


def words(log: Path) -> list[str]:
    return [line.split(" ", 2)[2] for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def test_the_pause_read_takes_one_lease_and_the_lock_releases_it(broker: Path) -> None:
    http = Http()
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        same(qi_platform.hardware_pause_left(client(http)), 0)
        same(http.sent[0], ("GET", "/backend_types/"))
        same(qi_platform.hardware_pause_left(client(http)), 0)
        same(words(broker), ["take fixture-host"])
    same(words(broker), ["take fixture-host", f"release {NONCE}"])


def test_a_pause_read_outside_the_submit_lock_takes_no_lease(broker: Path) -> None:
    same(qi_platform.hardware_pause_left(client(Http())), 0)
    with qi_platform.token_lock():
        same(qi_platform.hardware_pause_left(client(Http())), 0)
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        client(Http()).post("/batch_jobs", {"backend_type_id": 1})
    same(words(broker), [])


@pytest.mark.parametrize(("status", "released"), [("queued", True), ("planned", False), ("unreadable", False)])
def test_the_lease_is_released_only_after_the_created_batch_reads_as_enqueued(
    broker: Path, status: str, released: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    http = Http(status)
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        qi_submit_lease.take()
        client(http).post("/batch_jobs", {"backend_type_id": 7})
    same(http.sent[-1], ("GET", "/batch_jobs/31"))
    same(words(broker), ["take fixture-host", f"release {NONCE}"] if released else ["take fixture-host"])
    same("submit lease kept until it expires" in capsys.readouterr().err, not released)


def test_a_write_after_the_deadline_is_refused_unsent_and_a_read_still_passes(
    broker: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = Http()
    now = [1000.0]
    monkeypatch.setattr(qi_submit_lease, "clock", lambda: now[0])
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        qi_submit_lease.take()
        now[0] = 1000.0 + 600 - qi_submit_lease.MARGIN_SECONDS - 1
        client(http).post("/projects", {})
        now[0] += 1
        for method, path in (("POST", "/batch_jobs"), ("PATCH", "/batch_jobs/31/enqueue")):
            with pytest.raises(qi_platform.RequestNotDispatched, match="submit lease passed its deadline"):
                client(http).request(method, path)
        client(http).get("/batch_jobs/31")
    same(http.sent, [("POST", "/projects"), ("GET", "/batch_jobs/31")])
    same(words(broker), ["take fixture-host", f"release {NONCE}"])


def test_a_refused_or_absent_lease_stops_before_the_account_read(
    broker: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = Http()
    command = f"{sys.executable} -I {tmp_path / 'broker.py'} {broker} refuse"
    refusals = ((command, "lease held by lab-a1"), ("", "names no lease command"), ("/nonexistent/x", "failed"))
    for value, message in refusals:
        monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, value)
        with pytest.raises(SystemExit, match=message), qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
            qi_platform.hardware_pause_left(client(http))
    same(http.sent, [])


@pytest.mark.parametrize(
    "answer",
    ["", "[]", json.dumps({"nonce": "short", "lease_seconds": 600}), json.dumps({"nonce": NONCE, "lease_seconds": 90})],
)
def test_a_malformed_or_too_short_lease_answer_is_no_lease(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: str
) -> None:
    script = tmp_path / "answer.py"
    script.write_text(f"print({answer!r})\n", encoding="utf-8")
    monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, f"{sys.executable} -I {script}")
    monkeypatch.setattr(qi_platform, "SUBMIT_LOCK", tmp_path / "submit.lock")
    http = Http()
    with pytest.raises(SystemExit, match="no submit lease"), qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        qi_platform.hardware_pause_left(client(http))
    same(http.sent, [])


def test_another_thread_and_a_nested_session_stay_outside_the_lease(broker: Path) -> None:
    import threading

    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        worker = threading.Thread(target=qi_submit_lease.take)
        worker.start()
        worker.join()
        same(words(broker), [])
        with pytest.raises(RuntimeError, match="not re-entrant"), qi_submit_lease.session():
            pass


def test_the_holder_is_reduced_to_the_broker_alphabet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(qi_submit_lease.HOLDER_VARIABLE, raising=False)
    monkeypatch.setattr(qi_submit_lease.socket, "gethostname", lambda: "Lab_A1.example")
    same(qi_submit_lease.holder(), "lab-a1-example")
    monkeypatch.setenv(qi_submit_lease.HOLDER_VARIABLE, "Bad Holder")
    with pytest.raises(SystemExit, match="gives no holder"):
        qi_submit_lease.holder()
