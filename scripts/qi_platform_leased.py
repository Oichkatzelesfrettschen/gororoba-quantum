"""Quantum Inspire batch submission under the account-wide submit lease; the successor route of qi_platform.submit.

    "$QI_PYTHON" scripts/qi_platform_leased.py submit CASE_DIR --backend-type-id N --approval TEXT

qi_platform.submit orders the sessions of one device with a file lock, so two devices sharing the account can both
pass its queue and pause checks before either batch exists on the service
(https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/893). Retained records pin the bytes of
scripts/qi_platform.py, so this module adds the lease around that file's own `_submit` and changes none of it:

- submit() holds qi_platform.SUBMIT_LOCK and a qi_submit_lease session, reads the backend type, and for a type
  flagged `is_hardware` takes the lease before `_submit` reads the queue or the account;
- for the span of `_submit`, the name qi_platform.Client is bound to LeasedClient, so the client `_submit` builds
  refuses every request other than a GET after the lease's deadline, at each transport dispatch, and hands the id
  of the batch job it creates to the session. The binding is restored when `_submit` returns or raises.

Assumptions and limits. The deadline check runs immediately before each dispatch; a process that is suspended
between that check and the send, or whose request stays in flight longer than qi_submit_lease.MARGIN_SECONDS, can
write after the grantor freed the lease, because the service accepts no fencing token. While the binding holds,
another thread of this process that builds qi_platform.Client() (snapshot, reconcile, collect) receives a
LeasedClient; the lease hooks act only for the thread that opened the session, so that client behaves as the base
class, and no caller in the repository runs such a thread beside a submission.

An emulator batch takes no lease and passes through unchanged. Collection and reconciliation stay
qi_platform's. A route that calls qi_platform.submit or qi_platform_submission_deadline.submit directly stays
outside the lease (docs/notes/quantum_inspire/usage.md, "Submit lease").
"""

from __future__ import annotations

import argparse
import contextlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import qi_platform
import qi_submit_lease


class GuardedSession:
    """The client's HTTP session with the lease's deadline checked at each dispatch of a write.

    qi_platform.Client.request refreshes the token and resends once inside one call, so the check sits here, at the
    transport, and runs again for the resend. A refusal before the first dispatch is RequestNotDispatched; a refusal
    of the resend is RequestRejectedBeforeRetry with the status the service sent, the two forms `_submit` records.
    """

    def __init__(self, inner: Any, owner: LeasedClient) -> None:
        self._inner = inner
        self._owner = owner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        owner = self._owner
        if method != "GET" and qi_submit_lease.expired():
            if owner.dispatched:
                raise qi_platform.RequestRejectedBeforeRetry(method, owner.path, owner.status)
            raise qi_platform.RequestNotDispatched(
                "the account's submit lease passed its deadline; the request was not sent"
            )
        if method == "POST" and url == f"{qi_platform.HOST}/batch_jobs":
            # From here the batch job may exist whatever answer arrives.
            qi_submit_lease.batch_requested()
        owner.dispatched += 1
        response = self._inner.request(method, url, **kwargs)
        owner.status = response.status_code
        return response


class LeasedClient(qi_platform.Client):
    """A client whose writes stop at the lease's deadline and whose created batch job the lease session reads."""

    dispatched = 0
    path = ""
    status = 0

    def __init__(self) -> None:
        super().__init__()
        self.session = GuardedSession(self.session, self)

    def request(self, method: str, path: str, *, execution_deadline: float | None = None, **kwargs: Any) -> Any:
        self.dispatched, self.path, self.status = 0, path, 0
        body = super().request(method, path, execution_deadline=execution_deadline, **kwargs)
        if method == "POST" and path == "/batch_jobs" and isinstance(body, dict) and "id" in body:
            created = body["id"]
            qi_submit_lease.created(lambda: self.batch_status(created))
        return body

    def batch_status(self, batch_id: int) -> str:
        """The status of exactly this batch job, read as qi_platform.reconcile reads it: the list with an id filter."""
        rows = self.pages("/batch_jobs", id=batch_id)
        if len(rows) != 1 or rows[0]["id"] != batch_id:
            raise qi_platform.PlatformError("the service did not resolve exactly the created batch job")
        return str(rows[0]["status"])


@contextlib.contextmanager
def _leased_client() -> Iterator[None]:
    """Bind qi_platform.Client to LeasedClient for the block; the caller holds SUBMIT_LOCK."""
    original = qi_platform.Client
    qi_platform.Client = LeasedClient  # type: ignore[misc]
    try:
        yield
    finally:
        qi_platform.Client = original  # type: ignore[misc]


def submit(
    case_dir: Path,
    backend_type_id: int,
    approval: str,
    *,
    expected_cases_sha256: str | None = None,
    execution_deadline: float | None = None,
) -> dict[str, Any]:
    """Submit one case batch under SUBMIT_LOCK and, on a hardware backend type, under the account's submit lease."""
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK), qi_submit_lease.session(), _leased_client():
        if qi_platform.Client().get(f"/backend_types/{backend_type_id}")["is_hardware"]:
            qi_submit_lease.take()
        return qi_platform._submit(
            case_dir,
            backend_type_id,
            approval,
            expected_cases_sha256=expected_cases_sha256,
            execution_deadline=execution_deadline,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("submit")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--backend-type-id", type=int, required=True)
    p.add_argument("--approval", required=True)
    args = parser.parse_args()
    record = submit(args.case_dir, args.backend_type_id, args.approval)
    print(f"batch {record['batch_job']}: jobs {[row['job'] for row in record['jobs']]}")


if __name__ == "__main__":
    main()
