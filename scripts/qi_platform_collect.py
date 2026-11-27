"""Quantum Inspire collection with a bounded, optional job-log read; the successor route of qi_platform.collect.

    "$QI_PYTHON" scripts/qi_platform_collect.py collect CASE_DIR [--poll S] [--timeout S] [--logs-timeout S]

qi_platform.collect reads GET /jobs/ID/logs for every job that did not complete, and the service answers that read
for a failed job in more than the client's 60 s request timeout (pool row FC-011). The ReadTimeout ends the
collection, so a batch of failed jobs yields no results.json and a runner reports it as a failed collection. Retained
records pin the bytes of scripts/qi_platform.py, so this module changes none of it:

- for the span of the collection, the name qi_platform.Client is bound to BoundedLogsClient, so the collection that
  qi_platform.collect runs reads each logs path under --logs-timeout seconds (default LOGS_TIMEOUT_SECONDS) and
  every other path under the base client's 60 s;
- a logs read that times out returns the text LOGS_UNAVAILABLE, which collect stores as the job's `logs` value in
  results.json; the job record, results, raw shots and transactions are read and written as before.

Limits. A logs read that fails for another reason (an HTTP error, a lost connection) still ends the collection. The
stored text differs from the logs a later read returns, so a recollection of the same case directory that reads the
logs raises qi_platform's recollection conflict and leaves the retained file in place; the case directory keeps the
timeout record as its fact about that read. The binding holds for the process, which runs one collection.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import qi_platform

LOGS_TIMEOUT_SECONDS = 20.0
LOGS_UNAVAILABLE = "logs: unavailable (timeout)"


class BoundedLogsSession:
    """The client's HTTP session with a shorter read timeout on every GET of a job's logs."""

    def __init__(self, inner: Any, logs_timeout: float) -> None:
        self._inner = inner
        self._logs_timeout = logs_timeout

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        if method == "GET" and url.endswith("/logs"):
            kwargs["timeout"] = self._logs_timeout
        return self._inner.request(method, url, **kwargs)


class BoundedLogsClient(qi_platform.Client):
    """A client whose job-log reads stop at logs_timeout seconds and answer LOGS_UNAVAILABLE when they time out."""

    logs_timeout = LOGS_TIMEOUT_SECONDS

    def __init__(self) -> None:
        super().__init__()
        self.session = BoundedLogsSession(self.session, self.logs_timeout)

    def get(self, path: str, *, execution_deadline: float | None = None, **params: Any) -> Any:
        try:
            return super().get(path, execution_deadline=execution_deadline, **params)
        except importlib.import_module("requests").exceptions.Timeout:
            if path.endswith("/logs"):
                return LOGS_UNAVAILABLE
            raise


@contextlib.contextmanager
def _bounded_logs_client(logs_timeout: float) -> Iterator[None]:
    """Bind qi_platform.Client to a BoundedLogsClient of the given log timeout for the block."""

    class Bound(BoundedLogsClient):
        pass

    Bound.logs_timeout = logs_timeout
    original = qi_platform.Client
    qi_platform.Client = Bound  # type: ignore[misc]
    try:
        yield
    finally:
        qi_platform.Client = original  # type: ignore[misc]


def collect(
    case_dir: Path,
    poll: float,
    timeout: float,
    *,
    logs_timeout: float = LOGS_TIMEOUT_SECONDS,
    execution_deadline: float | None = None,
) -> None:
    """qi_platform.collect with the logs read of each non-completed job bounded by logs_timeout seconds."""
    if not logs_timeout > 0:
        raise ValueError("logs_timeout must be positive")
    with _bounded_logs_client(logs_timeout):
        qi_platform.collect(case_dir, poll, timeout, execution_deadline=execution_deadline)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("collect")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--poll", type=float, default=20.0)
    p.add_argument("--timeout", type=float, default=3600.0)
    p.add_argument("--logs-timeout", type=float, default=LOGS_TIMEOUT_SECONDS)
    args = parser.parse_args()
    try:
        collect(args.case_dir, args.poll, args.timeout, logs_timeout=args.logs_timeout)
    except qi_platform.PlatformError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
