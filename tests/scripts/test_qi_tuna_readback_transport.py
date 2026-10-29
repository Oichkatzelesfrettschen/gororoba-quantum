"""Readback transport must preserve bytes and refuse expired request starts."""

from typing import Any

import pytest


class Response:
    def __init__(self, status: int, body: bytes = b"{}") -> None:
        self.status_code = status
        self.headers = {"Content-Type": "application/json"}
        self.body = body
        self.closed = False

    def iter_content(self, chunk_size: int) -> list[bytes]:
        return [self.body]

    def close(self) -> None:
        self.closed = True


class Session:
    def __init__(self, response: Response) -> None:
        self.response = response
        self.requests: list[tuple[str, str, dict[str, Any]]] = []

    def request(self, method: str, url: str, **options: Any) -> Response:
        self.requests.append((method, url, options))
        return self.response


def test_readback_preserves_duplicate_keys_in_response_bytes() -> None:
    from qi_tuna_readback_transport import read_qi_json

    raw = b'{"id":9,"id":11}'
    response = Response(200, raw)
    session = Session(response)
    receipt = read_qi_json(session, "/jobs/11", {}, lambda _force: None, lambda: None, timeout_seconds=1.0)
    if receipt.body != raw or not response.closed:
        raise AssertionError("the response bytes or response lifetime changed")
    if len(session.requests) != 1 or session.requests[0][0] != "GET":
        raise AssertionError("readback did not send exactly one GET")
    options = session.requests[0][2]
    if options.get("allow_redirects") is not False or options.get("stream") is not True:
        raise AssertionError("transport did not constrain redirects and response streaming")


def test_expiry_during_refresh_prevents_any_request() -> None:
    from qi_tuna_readback_transport import read_qi_json

    expired = False
    session = Session(Response(200))

    def refresh(_force: bool) -> None:
        nonlocal expired
        expired = True

    def check() -> None:
        if expired:
            raise TimeoutError("fixture horizon expired")

    with pytest.raises(TimeoutError):
        read_qi_json(session, "/jobs/11", {}, refresh, check, timeout_seconds=1.0)
    if session.requests:
        raise AssertionError("request started after the clock expired")


def test_expiry_during_401_refresh_refuses_retry_and_closes_response() -> None:
    from qi_tuna_readback_transport import read_qi_json

    expired = False
    response = Response(401)
    session = Session(response)

    def refresh(force: bool) -> None:
        nonlocal expired
        if force:
            expired = True

    def check() -> None:
        if expired:
            raise TimeoutError("fixture horizon expired")

    with pytest.raises(TimeoutError):
        read_qi_json(session, "/jobs/11", {}, refresh, check, timeout_seconds=1.0)
    if len(session.requests) != 1 or not response.closed:
        raise AssertionError("expired retry was sent or rejected response remained open")


def test_401_refresh_retries_once_and_preserves_the_second_body() -> None:
    from qi_tuna_readback_transport import read_qi_json

    rejected = Response(401)
    accepted = Response(200, b'{"id":11}')

    class SequenceSession(Session):
        def request(self, method: str, url: str, **options: Any) -> Response:
            self.requests.append((method, url, options))
            return rejected if len(self.requests) == 1 else accepted

    session = SequenceSession(rejected)
    refreshes: list[bool] = []
    receipt = read_qi_json(session, "/jobs/11", {}, refreshes.append, lambda: None, timeout_seconds=1.0)
    if receipt.body != b'{"id":11}' or refreshes != [False, True] or not rejected.closed or not accepted.closed:
        raise AssertionError("401 recovery did not retain the second response or close both responses")
    if len(session.requests) != 2:
        raise AssertionError("401 recovery did not send exactly one retry")


def test_expiry_during_body_read_discards_receipt_and_closes_response() -> None:
    from qi_tuna_readback_transport import read_qi_json

    expired = False

    class SlowResponse(Response):
        def iter_content(self, chunk_size: int) -> list[bytes]:
            nonlocal expired
            expired = True
            return [self.body]

    response = SlowResponse(200)
    session = Session(response)

    def check() -> None:
        if expired:
            raise TimeoutError("fixture horizon expired")

    with pytest.raises(TimeoutError):
        read_qi_json(session, "/jobs/11", {}, lambda _force: None, check, timeout_seconds=1.0)
    if not response.closed:
        raise AssertionError("expired response remained open")


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/jobs/0", {}),
        ("/jobs/11?x=1", {}),
        ("/jobs/11", {"unexpected": 1}),
        ("/batch_jobs", {"id": True, "page": 1, "size": 100}),
        ("/batch_jobs", {"id": 11, "page": 2, "size": 100}),
        ("/results/job/11", {"page": 1, "size": 99}),
        ("/projects", {}),
    ],
)
def test_unapproved_readback_locator_never_reaches_transport(path: str, params: dict[str, int]) -> None:
    from qi_tuna_readback_transport import read_qi_json

    session = Session(Response(200))
    with pytest.raises(ValueError):
        read_qi_json(session, path, params, lambda _force: None, lambda: None, timeout_seconds=1.0)
    if session.requests:
        raise AssertionError("invalid locator reached the session")


def test_redirect_and_oversized_body_fail_closed() -> None:
    from qi_tuna_readback_transport import read_qi_json

    for response in (Response(302), Response(200, b"x" * (2 * 1024 * 1024 + 1))):
        session = Session(response)
        with pytest.raises(ValueError):
            read_qi_json(session, "/jobs/11", {}, lambda _force: None, lambda: None, timeout_seconds=1.0)
        if len(session.requests) != 1 or not response.closed:
            raise AssertionError("rejected response was retried or left open")
