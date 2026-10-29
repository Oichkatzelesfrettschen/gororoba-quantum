"""Private attempt journals must preserve ordered intent and outcome bytes."""

import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest


def test_attempt_journal_reloads_exact_order_and_rejects_body_replacement(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    first = AttemptIntent(1, "/jobs/11", ())
    second = AttemptIntent(2, "/jobs/11", ())
    rejected = AttemptOutcome(first, True, 401, "application/json", b"{}", True, None, None)
    accepted = AttemptOutcome(second, True, 200, "application/json", b'{"id":11}', True, None, None)
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(first)
            journal.retain_outcome(rejected)
            journal.retain_intent(second)
            journal.retain_outcome(accepted)
        replay = load_attempt_journal(directory)
        if replay.events != ((first, rejected), (second, accepted)) or replay.lifecycle != "terminal":
            raise AssertionError("journal did not reproduce its exact ordered events")
        (path / "attempt-02.body").write_bytes(b'{"id":22}')
        with pytest.raises(ValueError):
            load_attempt_journal(directory)
    finally:
        os.close(directory)


def test_out_of_order_or_failed_intent_latches_the_journal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    outcome = AttemptOutcome(intent, False, None, None, b"", False, "TimeoutError", None)
    try:
        with PrivateAttemptJournal(directory) as journal:
            with pytest.raises(ValueError):
                journal.retain_outcome(outcome)
            with pytest.raises(ValueError):
                journal.retain_intent(intent)
    finally:
        os.close(directory)

    second_path = tmp_path / "sync-failure"
    second_path.mkdir(mode=0o700)
    second_directory = os.open(second_path, os.O_RDONLY | os.O_DIRECTORY)

    def fail_sync(_descriptor: int) -> None:
        raise OSError("synthetic sync failure")

    try:
        with PrivateAttemptJournal(second_directory) as journal:
            monkeypatch.setattr(os, "fsync", fail_sync)
            with pytest.raises(OSError, match="synthetic sync failure"):
                journal.retain_intent(intent)
            with pytest.raises(ValueError):
                journal.retain_intent(intent)
    finally:
        os.close(second_directory)


@pytest.mark.parametrize("status,error_type", [(200, None), (401, "TimeoutError")])
def test_retry_requires_a_complete_error_free_unauthorized_outcome(
    tmp_path: Path, status: int, error_type: str | None
) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    first = AttemptIntent(1, "/jobs/11", ())
    outcome = AttemptOutcome(first, True, status, "application/json", b"{}", True, error_type, None)
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(first)
            journal.retain_outcome(outcome)
            with pytest.raises(ValueError):
                journal.retain_intent(AttemptIntent(2, "/jobs/11", ()))
    finally:
        os.close(directory)


def test_transport_attempts_are_retained_and_reloaded(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import read_journaled_qi_json

    class Response:
        headers = {"Content-Type": "application/json"}

        def __init__(self, status: int, body: bytes) -> None:
            self.status_code = status
            self.body = body

        def iter_content(self, chunk_size: int) -> Iterator[bytes]:
            yield self.body

        def close(self) -> None:
            pass

    class Session:
        def __init__(self) -> None:
            self.calls = 0

        def request(self, method: str, url: str, **options: Any) -> Response:
            self.calls += 1
            return Response(401, b"{}") if self.calls == 1 else Response(200, b'{"id":11}')

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with PrivateAttemptJournal(directory) as journal:
            receipt = read_journaled_qi_json(
                Session(),
                "/jobs/11",
                {},
                lambda _force: None,
                lambda: None,
                journal.retain_intent,
                journal.retain_outcome,
                timeout_seconds=1.0,
            )
        replay = load_attempt_journal(directory)
        if (
            replay.lifecycle != "terminal"
            or [outcome.status for _intent, outcome in replay.events] != [401, 200]
            or replay.events[-1][1].body != receipt.readback.body
        ):
            raise AssertionError("journal did not retain the transport's complete attempt sequence")
    finally:
        os.close(directory)


def test_incomplete_intent_is_not_a_complete_replay(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(AttemptIntent(1, "/jobs/11", ()))
        with pytest.raises((ValueError, OSError)):
            load_attempt_journal(directory)
    finally:
        os.close(directory)


def test_boolean_outcome_attempt_cannot_alias_integer_one(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            journal.retain_outcome(AttemptOutcome(intent, True, 200, "application/json", b"{}", True, None, None))
        outcome_path = path / "attempt-01.outcome"
        metadata = json.loads(outcome_path.read_text())
        metadata["attempt"] = True
        outcome_path.write_text(json.dumps(metadata))
        with pytest.raises(ValueError):
            load_attempt_journal(directory)
    finally:
        os.close(directory)


def test_boolean_outcome_intent_cannot_alias_integer_one(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    false_alias = AttemptIntent(True, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            with pytest.raises(ValueError):
                journal.retain_outcome(
                    AttemptOutcome(false_alias, True, 200, "application/json", b"{}", True, None, None)
                )
    finally:
        os.close(directory)


def test_empty_failure_body_replays_and_retry_cannot_change_locator(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    outcome = AttemptOutcome(intent, True, 401, "application/json", b"", True, None, None)
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            journal.retain_outcome(outcome)
            with pytest.raises(ValueError):
                journal.retain_intent(AttemptIntent(2, "/jobs/12", ()))
        replay = load_attempt_journal(directory)
        if replay.events != ((intent, outcome),) or replay.lifecycle != "retry_pending":
            raise AssertionError("empty outcome body did not replay")
    finally:
        os.close(directory)


@pytest.mark.parametrize("case", ["uncalled_response", "statusless_body", "silent_incomplete", "silent_close_error"])
def test_journal_rejects_contradictory_outcome_states(tmp_path: Path, case: str) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    outcomes = {
        "uncalled_response": AttemptOutcome(intent, False, 200, "application/json", b"{}", True, None, None),
        "statusless_body": AttemptOutcome(intent, True, None, None, b"{}", False, "OSError", None),
        "silent_incomplete": AttemptOutcome(intent, True, 200, "application/json", b"{", False, None, None),
        "silent_close_error": AttemptOutcome(intent, True, 200, "application/json", b"{}", True, None, "OSError"),
    }
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            with pytest.raises(ValueError):
                journal.retain_outcome(outcomes[case])
    finally:
        os.close(directory)


def test_reload_rejects_coherent_but_contradictory_outcome(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            journal.retain_outcome(AttemptOutcome(intent, True, 200, "application/json", b"{}", True, None, None))
        outcome_path = path / "attempt-01.outcome"
        metadata = json.loads(outcome_path.read_text())
        metadata["request_called"] = False
        outcome_path.write_text(json.dumps(metadata))
        with pytest.raises(ValueError):
            load_attempt_journal(directory)
    finally:
        os.close(directory)


def test_oversized_outcome_metadata_fails_before_body_write(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome
    from qi_tuna_readback_transport import MAX_BODY

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    oversized = AttemptOutcome(intent, True, 200, "x" * MAX_BODY, b"{}", True, "ValueError", None)
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            with pytest.raises(ValueError):
                journal.retain_outcome(oversized)
        if {item.name for item in path.iterdir()} != {"attempt-01.intent"}:
            raise AssertionError("oversized metadata produced outcome or body files")
    finally:
        os.close(directory)


@pytest.mark.parametrize(
    "field,value", [("status", True), ("body_length", True), ("request_called", 1), ("complete", 1)]
)
def test_reload_rejects_boolean_integer_aliases(tmp_path: Path, field: str, value: object) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            journal.retain_outcome(AttemptOutcome(intent, True, 200, "application/json", b"{}", True, None, None))
        outcome_path = path / "attempt-01.outcome"
        metadata = json.loads(outcome_path.read_text())
        metadata[field] = value
        outcome_path.write_text(json.dumps(metadata))
        with pytest.raises(ValueError):
            load_attempt_journal(directory)
    finally:
        os.close(directory)


def test_intent_rejects_boolean_query_identifier(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with PrivateAttemptJournal(directory) as journal:
            with pytest.raises(ValueError):
                journal.retain_intent(AttemptIntent(1, "/batch_jobs", (("id", True), ("page", 1), ("size", 100))))
    finally:
        os.close(directory)


@pytest.mark.parametrize("media_type,body", [("application/json", b""), ("text/plain", b"{}")])
def test_error_free_success_requires_nonempty_json_body(tmp_path: Path, media_type: str, body: bytes) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    intent = AttemptIntent(1, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(intent)
            with pytest.raises(ValueError):
                journal.retain_outcome(AttemptOutcome(intent, True, 200, media_type, body, True, None, None))
    finally:
        os.close(directory)


def test_second_unauthorized_response_cannot_be_error_free(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal
    from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome

    path = tmp_path / "private"
    path.mkdir(mode=0o700)
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    first = AttemptIntent(1, "/jobs/11", ())
    second = AttemptIntent(2, "/jobs/11", ())
    try:
        with PrivateAttemptJournal(directory) as journal:
            journal.retain_intent(first)
            journal.retain_outcome(AttemptOutcome(first, True, 401, "application/json", b"{}", True, None, None))
            journal.retain_intent(second)
            with pytest.raises(ValueError):
                journal.retain_outcome(AttemptOutcome(second, True, 401, "application/json", b"{}", True, None, None))
    finally:
        os.close(directory)
