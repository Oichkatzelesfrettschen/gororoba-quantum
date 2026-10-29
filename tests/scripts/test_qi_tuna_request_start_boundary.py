"""Characterize the gap between a clock check and HTTP request initiation."""

from typing import Any

import pytest


def test_preemption_after_clock_check_can_start_a_request_after_boundary() -> None:
    from qi_tuna_readback_transport import read_qi_json

    time_after_boundary = False
    clock_checks = 0
    request_started_late = False

    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def close(self) -> None:
            pass

    class Session:
        def request(self, method: str, url: str, **options: Any) -> Response:
            nonlocal request_started_late
            request_started_late = time_after_boundary
            return Response()

    def check_clock() -> None:
        nonlocal time_after_boundary, clock_checks
        clock_checks += 1
        if time_after_boundary:
            raise TimeoutError("fixture boundary expired")
        if clock_checks == 2:
            # The clock observation succeeds, then scheduling advances beyond
            # the boundary before the caller can invoke session.request.
            time_after_boundary = True

    with pytest.raises(TimeoutError, match="fixture boundary expired"):
        read_qi_json(Session(), "/jobs/11", {}, lambda _force: None, check_clock, timeout_seconds=1.0)
    if not request_started_late:
        raise AssertionError("fixture did not reach the check-to-request preemption gap")
