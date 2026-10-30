"""Exercise journaled collection with local files and a synthetic session."""

import json
import os
from contextlib import ExitStack
from pathlib import Path
from typing import Any

import pytest


class Response:
    status_code = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, fail_stream: bool = False) -> None:
        self.fail_stream = fail_stream

    def iter_content(self, chunk_size: int) -> Any:
        yield b"{}"
        if self.fail_stream:
            raise OSError("synthetic partial stream")

    def close(self) -> None:
        pass


class Session:
    def __init__(self, fail_position: int | None = None) -> None:
        self.fail_position = fail_position
        self.paths: list[str] = []

    def request(self, method: str, url: str, **options: Any) -> Response:
        self.paths.append(url.removeprefix("https://api.quantum-inspire.com"))
        return Response(len(self.paths) == self.fail_position)


def _directories(root: Path, stack: ExitStack) -> list[int]:
    descriptors: list[int] = []
    for index in range(5):
        path = root / str(index)
        path.mkdir(mode=0o700)
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        stack.callback(os.close, descriptor)
        descriptors.append(descriptor)
    return descriptors


def test_journaled_collection_retains_each_response_without_admission(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, UnadmittedCapture, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks
    from qi_tuna_readback_collection import decode_captured_complete

    checkpoint = b'{"job":11,"file":12,"batch":14,"result":21}'
    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)
        session = Session()
        result = capture_journaled_readbacks(
            checkpoint,
            session,
            lambda _force: None,
            lambda: None,
            store.retain_checkpoint,
            store.retain_readback,
            callbacks,
            timeout_seconds=1.0,
        )
        if type(result) is not UnadmittedCapture or session.paths != [
            "/jobs/11",
            "/batch_jobs",
            "/files/12",
            "/results/job/11",
        ]:
            raise AssertionError("journaled collection changed its request sequence or admission type")
        if load_private_readbacks(directories[0]) != result.capture:
            raise AssertionError("retained capture differs from the returned local capture")
        for descriptor, receipt in zip(directories[1:], result.capture.readbacks, strict=True):
            replay = load_attempt_journal(descriptor)
            if replay.lifecycle != "terminal" or len(replay.events) != 1 or replay.events[0][1].body != receipt.body:
                raise AssertionError("attempt journal differs from the returned readback")
        unchecked: Any = result
        with pytest.raises(ValueError):
            decode_captured_complete(unchecked, b"catalogue", "digest", 1, "baseline", b"manifest", b"source")


def test_partial_second_readback_stops_and_retains_its_attempt(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore

    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)
        session = Session(fail_position=2)
        with pytest.raises(OSError, match="synthetic partial stream"):
            capture_journaled_readbacks(
                b'{"job":11,"file":12,"batch":14,"result":21}',
                session,
                lambda _force: None,
                lambda: None,
                store.retain_checkpoint,
                store.retain_readback,
                callbacks,
                timeout_seconds=1.0,
            )
        replay = load_attempt_journal(directories[2])
        if (
            session.paths != ["/jobs/11", "/batch_jobs"]
            or replay.events[0][1].body != b"{}"
            or replay.events[0][1].complete
        ):
            raise AssertionError("collection failed to stop or retain the partial attempt")


@pytest.mark.parametrize("timeout", [True, 0.0, float("inf"), float("nan")])
def test_invalid_timeout_refuses_before_checkpoint_or_request(timeout: float) -> None:
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks

    writes: list[object] = []
    session = Session()
    callback = JournalCallbacks(lambda _event: None, lambda _event: None)
    with pytest.raises(ValueError):
        capture_journaled_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            lambda: None,
            writes.append,
            writes.append,
            (callback,) * 4,
            timeout_seconds=timeout,
        )
    if writes or session.paths:
        raise AssertionError("invalid timeout produced checkpoint or provider activity")


@pytest.mark.parametrize("failure_site", ["readback_retention", "post_retention_clock"])
@pytest.mark.parametrize("failure_position", [1, 2, 3, 4])
def test_collection_stops_after_retention_or_clock_failure(
    tmp_path: Path, failure_site: str, failure_position: int
) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore
    from qi_tuna_readback_transport import Readback

    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)
        session = Session()
        readbacks_presented = 0

        def retain_readback(readback: Readback) -> None:
            nonlocal readbacks_presented
            readbacks_presented += 1
            if failure_site == "readback_retention" and readbacks_presented == failure_position:
                raise OSError("synthetic retention failure")
            store.retain_readback(readback)

        def check_clock() -> None:
            if failure_site == "post_retention_clock" and readbacks_presented == failure_position:
                raise TimeoutError("synthetic expiry")

        with pytest.raises((OSError, TimeoutError), match="synthetic"):
            capture_journaled_readbacks(
                b'{"job":11,"file":12,"batch":14,"result":21}',
                session,
                lambda _force: None,
                check_clock,
                store.retain_checkpoint,
                retain_readback,
                callbacks,
                timeout_seconds=1.0,
            )
        expected_paths = ["/jobs/11", "/batch_jobs", "/files/12", "/results/job/11"]
        if session.paths != expected_paths[:failure_position]:
            raise AssertionError("failure did not stop collection at the selected readback")
        for descriptor in directories[1 : failure_position + 1]:
            replay = load_attempt_journal(descriptor)
            if replay.lifecycle != "terminal" or replay.events[0][1].body != b"{}":
                raise AssertionError("failure did not retain the completed attempt")
        for descriptor in directories[failure_position + 1 :]:
            if os.listdir(descriptor):
                raise AssertionError("failure allowed a subsequent attempt")


def test_checkpoint_retention_failure_prevents_all_requests() -> None:
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks

    session = Session()
    intents: list[object] = []
    callback = JournalCallbacks(intents.append, lambda _event: None)

    def fail_checkpoint(_checkpoint: bytes) -> None:
        raise OSError("synthetic checkpoint failure")

    with pytest.raises(OSError, match="synthetic checkpoint failure"):
        capture_journaled_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            lambda: None,
            fail_checkpoint,
            lambda _readback: None,
            (callback,) * 4,
            timeout_seconds=1.0,
        )
    if session.paths or intents:
        raise AssertionError("checkpoint failure allowed a readback attempt")


def test_unauthorized_readback_is_journaled_before_refresh_and_retry(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore

    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)

        class UnauthorizedFirstSession(Session):
            def request(self, method: str, url: str, **options: Any) -> Response:
                response = super().request(method, url, **options)
                if len(self.paths) == 1:
                    response.status_code = 401
                return response

        session = UnauthorizedFirstSession()
        forced_refreshes: list[bool] = []

        def refresh(force: bool) -> None:
            forced_refreshes.append(force)
            if force:
                replay = load_attempt_journal(directories[1])
                if replay.lifecycle != "retry_pending" or replay.events[0][1].status != 401:
                    raise AssertionError("forced refresh preceded the unauthorized outcome")

        capture_journaled_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            refresh,
            lambda: None,
            store.retain_checkpoint,
            store.retain_readback,
            callbacks,
            timeout_seconds=1.0,
        )
        replay = load_attempt_journal(directories[1])
        if (
            session.paths != ["/jobs/11", "/jobs/11", "/batch_jobs", "/files/12", "/results/job/11"]
            or forced_refreshes != [False, True, False, False, False]
            or replay.lifecycle != "terminal"
            or [outcome.status for _, outcome in replay.events] != [401, 200]
        ):
            raise AssertionError("collection did not retain the authorized retry sequence")


def test_failed_forced_refresh_leaves_unauthorized_attempt_without_retry(tmp_path: Path) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore

    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)

        class UnauthorizedSession(Session):
            def request(self, method: str, url: str, **options: Any) -> Response:
                response = super().request(method, url, **options)
                response.status_code = 401
                return response

        def refresh(force: bool) -> None:
            if force:
                raise OSError("synthetic refresh failure")

        session = UnauthorizedSession()
        with pytest.raises(OSError, match="synthetic refresh failure"):
            capture_journaled_readbacks(
                b'{"job":11,"file":12,"batch":14,"result":21}',
                session,
                refresh,
                lambda: None,
                store.retain_checkpoint,
                store.retain_readback,
                callbacks,
                timeout_seconds=1.0,
            )
        replay = load_attempt_journal(directories[1])
        if (
            session.paths != ["/jobs/11"]
            or replay.lifecycle != "retry_pending"
            or len(replay.events) != 1
            or replay.events[0][1].status != 401
            or any(os.listdir(descriptor) for descriptor in directories[2:])
        ):
            raise AssertionError("refresh failure did not stop after retaining the unauthorized attempt")


@pytest.mark.parametrize("field", ["job", "file", "batch", "result"])
def test_oversized_checkpoint_identifier_refuses_before_retention(field: str) -> None:
    from qi_tuna_capture_commitment import MAX_QUERY_INTEGER_BITS
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks

    checkpoint = {"job": 11, "file": 12, "batch": 14, "result": 21}
    checkpoint[field] = 1 << MAX_QUERY_INTEGER_BITS
    calls: list[object] = []
    session = Session()
    callback = JournalCallbacks(calls.append, calls.append)
    with pytest.raises(ValueError, match="identifier exceeds"):
        capture_journaled_readbacks(
            json.dumps(checkpoint).encode(),
            session,
            lambda _force: calls.append("refresh"),
            lambda: calls.append("clock"),
            calls.append,
            calls.append,
            (callback,) * 4,
            timeout_seconds=1.0,
        )
    if calls or session.paths:
        raise AssertionError("oversized identifier produced an observable collection action")


def test_maximum_identifier_capture_can_be_committed() -> None:
    from qi_tuna_capture_commitment import MAX_QUERY_INTEGER_BITS, capture_commitment
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks

    maximum = (1 << MAX_QUERY_INTEGER_BITS) - 1
    checkpoint = json.dumps({"job": maximum, "file": maximum, "batch": maximum, "result": maximum}).encode()
    callback = JournalCallbacks(lambda _event: None, lambda _event: None)
    result = capture_journaled_readbacks(
        checkpoint,
        Session(),
        lambda _force: None,
        lambda: None,
        lambda _checkpoint: None,
        lambda _readback: None,
        (callback,) * 4,
        timeout_seconds=1.0,
    )
    if len(capture_commitment(result.capture)) != 64:
        raise AssertionError("maximum permitted locator cannot be committed")


@pytest.mark.parametrize(
    ("header_divisor", "failed_position", "character"), [(3, 3, "x"), (4, 4, "x"), (40, 4, "\U0001f600")]
)
def test_oversized_aggregate_response_metadata_never_returns_capture(
    tmp_path: Path, header_divisor: int, failed_position: int, character: str
) -> None:
    from qi_tuna_attempt_journal import PrivateAttemptJournal, load_attempt_journal
    from qi_tuna_journaled_collection import JournalCallbacks, capture_journaled_readbacks
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks
    from qi_tuna_readback_transport import MAX_BODY

    class LargeHeaderSession(Session):
        def request(self, method: str, url: str, **options: Any) -> Response:
            response = super().request(method, url, **options)
            response.headers = {"Content-Type": "application/json;" + character * (MAX_BODY // header_divisor)}
            return response

    with ExitStack() as stack:
        directories = _directories(tmp_path, stack)
        store = stack.enter_context(PrivateReadbackStore(directories[0]))
        journals = [stack.enter_context(PrivateAttemptJournal(descriptor)) for descriptor in directories[1:]]
        callbacks = tuple(JournalCallbacks(journal.retain_intent, journal.retain_outcome) for journal in journals)
        session = LargeHeaderSession()
        with pytest.raises(ValueError, match="metadata is oversized"):
            capture_journaled_readbacks(
                b'{"job":11,"file":12,"batch":14,"result":21}',
                session,
                lambda _force: None,
                lambda: None,
                store.retain_checkpoint,
                store.retain_readback,
                callbacks,
                timeout_seconds=1.0,
            )
        if len(session.paths) != failed_position or any(
            load_attempt_journal(item).lifecycle != "terminal" for item in directories[1 : failed_position + 1]
        ):
            raise AssertionError("fixture did not stop after retaining the oversized response")
        if any(os.listdir(item) for item in directories[failed_position + 1 :]):
            raise AssertionError("oversized response allowed a later request")
        if len(os.listdir(directories[0])) != 1 + 2 * (failed_position - 1):
            raise AssertionError("oversized response reached the private capture store")
        with pytest.raises(ValueError, match="incomplete"):
            load_private_readbacks(directories[0])
