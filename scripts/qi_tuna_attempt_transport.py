"""Present bounded readback attempt evidence to caller-owned retention callbacks.

The caller supplies an authenticated session, bounded refresh and clock checks,
durable private retention and cross-restart quarantine. Callback return does not
prove persistence, provider identity, effective URL, observation time or
admission. Refresh operations are outside this attempt stream. This interface
is not wired to a provider dispatcher.
"""

import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qi_tuna_readback_transport import HOST, MAX_BODY, Readback, _validate_target


@dataclass(frozen=True)
class AttemptIntent:
    attempt: int
    path: str
    query: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class AttemptOutcome:
    intent: AttemptIntent
    request_called: bool
    status: int | None
    content_type: str | None
    body: bytes
    complete: bool
    error_type: str | None
    close_error_type: str | None


@dataclass(frozen=True)
class UnadmittedReadback:
    """A local receipt whose admission requires separate adjudication."""

    readback: Readback


def read_journaled_qi_json(
    session: Any,
    path: str,
    params: dict[str, int],
    refresh: Callable[[bool], None],
    check_clock: Callable[[], None],
    retain_intent: Callable[[AttemptIntent], None],
    retain_outcome: Callable[[AttemptOutcome], None],
    *,
    timeout_seconds: float,
) -> UnadmittedReadback:
    """Read one allowed resource, retaining each attempt before any retry."""
    query = _validate_target(path, params)
    if type(timeout_seconds) not in (int, float):
        raise ValueError("request timeout must be a finite positive number")
    try:
        valid_timeout = math.isfinite(timeout_seconds) and timeout_seconds > 0
    except OverflowError:
        valid_timeout = False
    if not valid_timeout or any(not callable(item) for item in (refresh, check_clock, retain_intent, retain_outcome)):
        raise ValueError("request timeout or callbacks are invalid")
    for attempt in range(1, 3):
        check_clock()
        refresh(attempt == 2)
        check_clock()
        intent = AttemptIntent(attempt, path, query)
        retain_intent(intent)
        response: Any = None
        request_called = False
        status: int | None = None
        content_type: str | None = None
        body = bytearray()
        complete = False
        error: BaseException | None = None
        close_error: BaseException | None = None
        try:
            check_clock()
            request_called = True
            response = session.request(
                "GET", HOST + path, params=dict(query), timeout=timeout_seconds, stream=True, allow_redirects=False
            )
            if type(response.status_code) is not int:
                raise ValueError("provider status is invalid")
            status = response.status_code
            observed_content_type = response.headers.get("Content-Type")
            if type(observed_content_type) is str:
                content_type = observed_content_type
            check_clock()
            for chunk in response.iter_content(chunk_size=65536):
                if type(chunk) is not bytes:
                    raise ValueError("provider body chunk is invalid")
                remaining = MAX_BODY - len(body)
                body.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    raise ValueError("provider body is oversized")
                check_clock()
            complete = True
            check_clock()
            if status != 200 and not (status == 401 and attempt == 1):
                raise ValueError("provider readback did not return HTTP 200")
            if status == 200 and (
                content_type is None or content_type.split(";", 1)[0].strip().lower() != "application/json" or not body
            ):
                raise ValueError("provider readback has invalid JSON media type or empty body")
        except BaseException as caught:
            error = caught
        finally:
            if response is not None:
                try:
                    response.close()
                except BaseException as caught:
                    close_error = caught
                    if error is None:
                        error = caught
            try:
                retain_outcome(
                    AttemptOutcome(
                        intent,
                        request_called,
                        status,
                        content_type,
                        bytes(body),
                        complete,
                        type(error).__name__ if error is not None else None,
                        type(close_error).__name__ if close_error is not None else None,
                    )
                )
            except BaseException as retention_error:
                if error is not None and close_error is not None and error is not close_error:
                    raise retention_error from BaseExceptionGroup(
                        "attempt and response close failed", [error, close_error]
                    )
                if error is not None:
                    raise retention_error from error
                raise
        if error is not None:
            raise error.with_traceback(error.__traceback__)
        if status == 401:
            continue
        exact = bytes(body)
        if status != 200 or content_type is None:
            raise ValueError("provider response did not produce a receipt")
        return UnadmittedReadback(Readback(path, query, status, content_type, exact, hashlib.sha256(exact).hexdigest()))
    raise ValueError("provider readback authorization failed")
