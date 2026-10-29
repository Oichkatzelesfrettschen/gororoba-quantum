"""Retain bounded Quantum Inspire readback body bytes before JSON decoding.

The caller authenticates the session, supplies bounded clock and refresh checks,
retains the receipt, and validates its association and timing. The HTTP library
may decode transfer/content encodings; the retained body is not raw wire bytes.
This transport issues only the listed read-only GET requests and grants no job
or upload authority.
"""

import hashlib
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

HOST = "https://api.quantum-inspire.com"
MAX_BODY = 2 * 1024 * 1024


@dataclass(frozen=True)
class Readback:
    path: str
    query: tuple[tuple[str, int], ...]
    status: int
    content_type: str
    body: bytes
    body_sha256: str


def _validate_target(path: str, params: dict[str, int]) -> tuple[tuple[str, int], ...]:
    if type(path) is not str or len(path) > 256 or type(params) is not dict:
        raise ValueError("readback locator is invalid")
    identifier = r"[1-9][0-9]*"
    if path == "/batch_jobs":
        if set(params) != {"id", "page", "size"} or type(params.get("id")) is not int or params["id"] < 1:
            raise ValueError("batch readback requires an exact positive ID filter")
    elif re.fullmatch(rf"/results/job/{identifier}", path):
        if set(params) != {"page", "size"}:
            raise ValueError("result readback requires page and size")
    elif re.fullmatch(rf"/(jobs|files|members)/{identifier}", path):
        if params:
            raise ValueError("object readback accepts no query")
        return ()
    else:
        raise ValueError("readback path is not admitted")
    if type(params.get("page")) is not int or params["page"] != 1:
        raise ValueError("readback must request the first page")
    if type(params.get("size")) is not int or params["size"] != 100:
        raise ValueError("readback must request the approved page size")
    return tuple(sorted(params.items()))


def read_qi_json(
    session: Any,
    path: str,
    params: dict[str, int],
    refresh: Callable[[bool], None],
    check_clock: Callable[[], None],
    *,
    timeout_seconds: float,
) -> Readback:
    """Read one admitted GET, retrying at most one rejected 401 after refresh."""
    query = _validate_target(path, params)
    if type(timeout_seconds) not in (int, float):
        raise ValueError("request timeout must be a finite positive number")
    try:
        valid_timeout = math.isfinite(timeout_seconds) and timeout_seconds > 0
    except OverflowError:
        valid_timeout = False
    if not valid_timeout or not callable(refresh) or not callable(check_clock):
        raise ValueError("request timeout or callbacks are invalid")
    for attempt in range(2):
        check_clock()
        refresh(attempt == 1)
        check_clock()
        response = session.request(
            "GET", HOST + path, params=dict(query), timeout=timeout_seconds, stream=True, allow_redirects=False
        )
        try:
            check_clock()
            status = response.status_code
            if type(status) is not int:
                raise ValueError("provider status is invalid")
            if status == 401 and attempt == 0:
                continue
            if status != 200:
                raise ValueError("provider readback did not return HTTP 200")
            content_type = response.headers.get("Content-Type")
            if type(content_type) is not str or content_type.split(";", 1)[0].strip().lower() != "application/json":
                raise ValueError("provider readback content type is not JSON")
            body = bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                check_clock()
                if type(chunk) is not bytes or len(body) + len(chunk) > MAX_BODY:
                    raise ValueError("provider readback body is invalid or oversized")
                body.extend(chunk)
            check_clock()
            if not body:
                raise ValueError("provider readback body is empty")
            exact = bytes(body)
            return Readback(path, query, status, content_type, exact, hashlib.sha256(exact).hexdigest())
        finally:
            response.close()
    raise ValueError("provider readback authorization failed")
