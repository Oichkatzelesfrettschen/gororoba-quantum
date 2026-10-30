"""Exercise attempt retention with synthetic responses and no provider access."""

from collections.abc import Iterator
from typing import Any

import pytest


class Response:
    headers = {"Content-Type": "application/json"}

    def __init__(self, status: int, chunks: tuple[bytes, ...], fail_stream: bool = False) -> None:
        self.status_code = status
        self.chunks = chunks
        self.fail_stream = fail_stream
        self.closed = False

    def iter_content(self, chunk_size: int) -> Iterator[bytes]:
        yield from self.chunks
        if self.fail_stream:
            raise OSError("synthetic stream failure")

    def close(self) -> None:
        self.closed = True


def test_unauthorized_attempt_is_retained_before_retry() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    events: list[tuple[str, Any]] = []
    rejected = Response(401, (b'{"error":"expired"}',))
    accepted = Response(200, (b'{"id":11}',))

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            count = sum(kind == "intent" for kind, _event in events)
            if count == 2 and [kind for kind, _event in events] != ["intent", "outcome", "intent"]:
                raise AssertionError("retry started before its preceding outcome was retained")
            return rejected if count == 1 else accepted

    result = read_journaled_qi_json(
        Session(),
        "/jobs/11",
        {},
        lambda _force: None,
        lambda: None,
        lambda event: events.append(("intent", event)),
        lambda event: events.append(("outcome", event)),
        timeout_seconds=1.0,
    )
    if result.readback.body != b'{"id":11}' or [kind for kind, _event in events] != [
        "intent",
        "outcome",
        "intent",
        "outcome",
    ]:
        raise AssertionError("retry or ordered attempt evidence differs")
    first_outcome = events[1][1]
    if first_outcome.status != 401 or first_outcome.body != b'{"error":"expired"}' or not first_outcome.complete:
        raise AssertionError("unauthorized response was not retained")
    if not rejected.closed or not accepted.closed:
        raise AssertionError("response was left open")


def test_partial_stream_failure_retains_prefix_before_raising() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    outcome: list[Any] = []
    response = Response(200, (b'{"partial":',), fail_stream=True)

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            return response

    with pytest.raises(OSError, match="synthetic stream failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            outcome.append,
            timeout_seconds=1.0,
        )
    if len(outcome) != 1 or outcome[0].body != b'{"partial":' or outcome[0].complete or not response.closed:
        raise AssertionError("stream failure did not retain its exact partial prefix")


def test_outcome_retention_failure_prevents_retry() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    response = Response(401, (b"{}",))
    requests = 0

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal requests
            requests += 1
            return response

    def refuse(_event: object) -> None:
        raise OSError("synthetic retention failure")

    with pytest.raises(OSError, match="synthetic retention failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            refuse,
            timeout_seconds=1.0,
        )
    if requests != 1 or not response.closed:
        raise AssertionError("failed retention permitted retry or leaked a response")


@pytest.mark.parametrize("expire_after_end", [False, True])
def test_expired_stream_retains_observed_bytes_and_completion_state(expire_after_end: bool) -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    expired = False
    outcomes: list[Any] = []

    class ExpiringResponse(Response):
        def iter_content(self, chunk_size: int) -> Iterator[bytes]:
            nonlocal expired
            if not expire_after_end:
                expired = True
            yield b'{"id":11}'
            expired = True

    response = ExpiringResponse(200, ())

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            return response

    def check_clock() -> None:
        if expired:
            raise TimeoutError("synthetic deadline")

    with pytest.raises(TimeoutError, match="synthetic deadline"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            check_clock,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if (
        len(outcomes) != 1
        or outcomes[0].body != b'{"id":11}'
        or outcomes[0].complete is not expire_after_end
        or outcomes[0].error_type != "TimeoutError"
        or not response.closed
    ):
        raise AssertionError("expired stream lost its bytes or completeness state")


def test_deadline_after_intent_retains_not_called_outcome() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    expired = False
    outcomes: list[Any] = []
    calls = 0

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal calls
            calls += 1
            return Response(200, (b"{}",))

    def intent(_event: object) -> None:
        nonlocal expired
        expired = True

    def check_clock() -> None:
        if expired:
            raise TimeoutError("synthetic deadline")

    with pytest.raises(TimeoutError, match="synthetic deadline"):
        read_journaled_qi_json(
            Session(), "/jobs/11", {}, lambda _force: None, check_clock, intent, outcomes.append, timeout_seconds=1.0
        )
    if calls or len(outcomes) != 1 or outcomes[0].request_called or outcomes[0].error_type != "TimeoutError":
        raise AssertionError("deadline after intent did not retain the not-called outcome")


def test_intent_retention_failure_prevents_request() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    calls = 0
    outcomes: list[object] = []

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal calls
            calls += 1
            return Response(200, (b"{}",))

    def refuse(_event: object) -> None:
        raise OSError("synthetic intent retention failure")

    with pytest.raises(OSError, match="synthetic intent retention failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            refuse,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if calls or outcomes:
        raise AssertionError("failed intent retention reached the provider request")


def test_expired_response_keeps_observed_status_and_media_type() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    expired = False
    outcomes: list[Any] = []
    response = Response(200, (b"{}",))

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal expired
            expired = True
            return response

    def check_clock() -> None:
        if expired:
            raise TimeoutError("synthetic deadline")

    with pytest.raises(TimeoutError, match="synthetic deadline"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            check_clock,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if len(outcomes) != 1 or outcomes[0].status != 200 or outcomes[0].content_type != "application/json":
        raise AssertionError("deadline check discarded the received response envelope")


def test_oversized_response_retains_only_the_bounded_prefix() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json
    from qi_tuna_readback_transport import MAX_BODY

    response = Response(200, (b"x" * (MAX_BODY - 2), b"abcde"))
    outcomes: list[Any] = []

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            return response

    with pytest.raises(ValueError, match="oversized"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if len(outcomes) != 1 or outcomes[0].body != b"x" * (MAX_BODY - 2) + b"ab" or outcomes[0].complete:
        raise AssertionError("oversized response did not retain its bounded prefix")


def test_close_failure_is_retained_and_prevents_retry() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    outcomes: list[Any] = []
    calls = 0

    class CloseFailure(Response):
        def close(self) -> None:
            raise OSError("synthetic close failure")

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal calls
            calls += 1
            return CloseFailure(401, (b"{}",))

    with pytest.raises(OSError, match="synthetic close failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if calls != 1 or len(outcomes) != 1 or not outcomes[0].complete or outcomes[0].error_type != "OSError":
        raise AssertionError("close failure was not retained or allowed a retry")


def test_stream_and_close_failures_are_both_retained() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    outcomes: list[Any] = []

    class CloseFailure(Response):
        def close(self) -> None:
            raise RuntimeError("synthetic close failure")

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            return CloseFailure(200, (b"prefix",), fail_stream=True)

    with pytest.raises(OSError, match="synthetic stream failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if len(outcomes) != 1 or outcomes[0].error_type != "OSError" or outcomes[0].close_error_type != "RuntimeError":
        raise AssertionError("combined stream and close errors were not retained")


def test_request_exception_records_ambiguous_called_attempt() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    outcomes: list[Any] = []

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            raise OSError("synthetic request failure")

    with pytest.raises(OSError, match="synthetic request failure"):
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            outcomes.append,
            timeout_seconds=1.0,
        )
    if (
        len(outcomes) != 1
        or not outcomes[0].request_called
        or outcomes[0].status is not None
        or outcomes[0].body != b""
        or outcomes[0].complete
        or outcomes[0].error_type != "OSError"
    ):
        raise AssertionError("request exception lost its ambiguous attempt outcome")


def test_returned_readback_is_not_accepted_as_a_decodable_capture() -> None:
    from qi_tuna_attempt_transport import UnadmittedReadback, read_journaled_qi_json
    from qi_tuna_readback_collection import ReadbackCapture, decode_captured_complete

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            return Response(200, (b"{}",))

    result = read_journaled_qi_json(
        Session(),
        "/jobs/11",
        {},
        lambda _force: None,
        lambda: None,
        lambda _event: None,
        lambda _event: None,
        timeout_seconds=1.0,
    )
    if type(result) is not UnadmittedReadback:
        raise AssertionError("attempt transport returned an ordinary decodable receipt")
    unchecked: Any = result
    capture = ReadbackCapture(b'{"job":11,"file":12,"batch":14,"result":21}', (unchecked,) * 4)
    with pytest.raises(ValueError):
        decode_captured_complete(capture, b"catalogue", "digest", 1, "baseline", b"manifest", b"source")


def test_retention_error_preserves_stream_and_close_failures_without_retry() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    calls = 0

    class CloseFailure(Response):
        def close(self) -> None:
            raise RuntimeError("synthetic close failure")

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal calls
            calls += 1
            return CloseFailure(200, (b"prefix",), fail_stream=True)

    def refuse(_event: object) -> None:
        raise OSError("synthetic retention failure")

    with pytest.raises(OSError, match="synthetic retention failure") as caught:
        read_journaled_qi_json(
            Session(),
            "/jobs/11",
            {},
            lambda _force: None,
            lambda: None,
            lambda _event: None,
            refuse,
            timeout_seconds=1.0,
        )
    cause = caught.value.__cause__
    if not isinstance(cause, BaseExceptionGroup) or len(cause.exceptions) != 2:
        raise AssertionError("retention error did not preserve both underlying failures")
    if not isinstance(cause.exceptions[0], OSError) or not isinstance(cause.exceptions[1], RuntimeError) or calls != 1:
        raise AssertionError("underlying failures or fail-stop request count differ")


def test_request_options_and_retry_refresh_order() -> None:
    from qi_tuna_attempt_transport import read_journaled_qi_json

    events: list[str] = []

    class TracedResponse(Response):
        def close(self) -> None:
            events.append("close")
            super().close()

    class Session:
        def __init__(self) -> None:
            self.calls = 0

        def request(self, method: str, url: str, **options: Any) -> Response:
            self.calls += 1
            events.append("request")
            expected = {
                "params": {"id": 14, "page": 1, "size": 100},
                "timeout": 2.5,
                "stream": True,
                "allow_redirects": False,
            }
            if method != "GET" or url != "https://api.quantum-inspire.com/batch_jobs" or options != expected:
                raise AssertionError("request method, locator or transport options differ")
            return TracedResponse(401, (b"{}",)) if self.calls == 1 else TracedResponse(200, (b"{}",))

    result = read_journaled_qi_json(
        Session(),
        "/batch_jobs",
        {"id": 14, "page": 1, "size": 100},
        lambda force: events.append("refresh-forced" if force else "refresh"),
        lambda: events.append("clock"),
        lambda _event: events.append("intent"),
        lambda _event: events.append("outcome"),
        timeout_seconds=2.5,
    )
    expected_events = [
        "clock",
        "refresh",
        "clock",
        "intent",
        "clock",
        "request",
        "clock",
        "clock",
        "clock",
        "close",
        "outcome",
        "clock",
        "refresh-forced",
        "clock",
        "intent",
        "clock",
        "request",
        "clock",
        "clock",
        "clock",
        "close",
        "outcome",
    ]
    if events != expected_events or result.readback.body != b"{}":
        raise AssertionError("attempt ordering or returned bytes differ")
