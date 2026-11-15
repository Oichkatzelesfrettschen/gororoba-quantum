"""A hardware admission read under SUBMIT_LOCK takes the submit lease first and frees it after a fresh account read."""

from __future__ import annotations

import datetime
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
print(json.dumps({"nonce": sys.argv[3], "lease_seconds": 600, "released": True}))
"""


class Account:
    """The two list reads of the hardware pause; `planned` adds one hardware batch that is not enqueued."""

    def __init__(self, planned: bool = False, fail_second_read: bool = False) -> None:
        self.planned = planned
        self.fail_second_read = fail_second_read
        self.reads: list[str] = []

    def pages(self, path: str) -> list[dict[str, Any]]:
        self.reads.append(path)
        if self.fail_second_read and self.reads.count("/batch_jobs") > 1:
            raise qi_platform.PlatformError("fixture read failure")
        if path == "/backend_types/":
            return [{"id": 1, "is_hardware": False}, {"id": 7, "is_hardware": True}]
        if path == "/batch_jobs" and self.planned and self.reads.count("/batch_jobs") > 1:
            created = datetime.datetime.now(datetime.UTC).isoformat()
            return [{"id": 3, "backend_type_id": 7, "status": "planned", "created_on": created}]
        return []


@pytest.fixture
def broker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    script, log = tmp_path / "broker.py", tmp_path / "broker.log"
    script.write_text(BROKER, encoding="utf-8")
    monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, f"{sys.executable} -I {script} {log} grant {NONCE}")
    monkeypatch.setenv(qi_submit_lease.HOLDER_VARIABLE, "fixture-host")
    monkeypatch.setattr(qi_platform, "SUBMIT_LOCK", tmp_path / "submit.lock")
    return log


def same(found: object, wanted: object) -> None:
    if found != wanted:
        raise AssertionError(f"{found!r} differs from {wanted!r}")


def words(log: Path) -> list[str]:
    return [line.split(" ", 2)[2] for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def test_the_pause_read_takes_one_lease_and_the_lock_releases_it(broker: Path) -> None:
    account = Account()
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        same(qi_platform.hardware_pause_left(account), 0)  # type: ignore[arg-type]
        same(qi_platform.hardware_pause_left(account), 0)  # type: ignore[arg-type]
        same(words(broker), ["take fixture-host"])
    same(words(broker), ["take fixture-host", f"release {NONCE}"])
    same(account.reads.count("/batch_jobs"), 3)


def test_a_pause_read_outside_the_submit_lock_takes_no_lease(broker: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    same(qi_platform.hardware_pause_left(Account()), 0)  # type: ignore[arg-type]
    with qi_platform.token_lock():
        same(qi_platform.hardware_pause_left(Account()), 0)  # type: ignore[arg-type]
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        pass
    same(words(broker), [])


@pytest.mark.parametrize("account", [Account(planned=True), Account(fail_second_read=True)])
def test_a_batch_in_planning_or_a_failed_read_keeps_the_lease(
    broker: Path, account: Account, capsys: pytest.CaptureFixture[str]
) -> None:
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        same(qi_platform.hardware_pause_left(account), 0)  # type: ignore[arg-type]
    same(words(broker), ["take fixture-host"])
    same("submit lease kept until it expires" in capsys.readouterr().err, True)


def test_a_refused_or_absent_lease_stops_before_the_account_read(
    broker: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    account = Account()
    command = f"{sys.executable} -I {tmp_path / 'broker.py'} {broker} refuse"
    refusals = ((command, "lease held by lab-a1"), ("", "names no lease command"), ("/nonexistent/x", "failed"))
    for value, message in refusals:
        monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, value)
        with pytest.raises(SystemExit, match=message), qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
            qi_platform.hardware_pause_left(account)  # type: ignore[arg-type]
    same(account.reads, [])


@pytest.mark.parametrize(
    "answer",
    ["", "[]", json.dumps({"nonce": "short", "lease_seconds": 600}), json.dumps({"nonce": NONCE, "lease_seconds": 0})],
)
def test_a_malformed_lease_answer_is_no_lease(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: str) -> None:
    script = tmp_path / "answer.py"
    script.write_text(f"print({answer!r})\n", encoding="utf-8")
    monkeypatch.setenv(qi_submit_lease.COMMAND_VARIABLE, f"{sys.executable} -I {script}")
    monkeypatch.setattr(qi_platform, "SUBMIT_LOCK", tmp_path / "submit.lock")
    account = Account()
    with pytest.raises(SystemExit, match="no submit lease"), qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        qi_platform.hardware_pause_left(account)  # type: ignore[arg-type]
    same(account.reads, [])


def test_the_holder_is_reduced_to_the_broker_alphabet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(qi_submit_lease.HOLDER_VARIABLE, raising=False)
    monkeypatch.setattr(qi_submit_lease.socket, "gethostname", lambda: "Lab_A1.example")
    same(qi_submit_lease.holder(), "lab-a1-example")
    monkeypatch.setenv(qi_submit_lease.HOLDER_VARIABLE, "Bad Holder")
    with pytest.raises(SystemExit, match="gives no holder"):
        qi_submit_lease.holder()
