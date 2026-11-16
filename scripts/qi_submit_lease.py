"""The account-wide submit lease a hardware submission takes from the owner's token broker.

A device counts the account's queue and hardware pause from its own read of the service and orders its sessions with
qi_platform.SUBMIT_LOCK, a file on that device. Two devices can therefore both pass the checks while the account sits
at its limit, each before the other's batch exists on the service. This module holds the lease's client side, and
scripts/qi_platform_leased.py is the submit route that uses it:

- session() opens a span for the calling thread; take() takes the lease in it, once;
- expired() tells the route's client that the deadline has passed, and the client then dispatches no request other
  than a GET;
- batch_requested() marks the dispatch of the request that creates a batch job, and created() receives the fresh
  read of the batch job once its id is known.

The session's end releases the lease when no request creating a batch job was dispatched, or when a fresh read of
the exact batch job shows it enqueued; the next holder's admission read then sees it. Every other end (a creation
request with no recorded answer, the batch still `planned`, a failed read) keeps the lease until the grantor
expires it.

The deadline is the grantor's `lease_seconds` less MARGIN_SECONDS, counted on this device's boot-time clock from
before the lease was asked for, so no clock offset between devices lengthens it, and time spent suspended counts.
The route checks it immediately before each dispatch of a write; a batch created before it stays `planned` and is
not enqueued after it. The check cannot cover a process suspended between the check and the send: the service takes
no fencing token, so the lease assumes a request leaves within MARGIN_SECONDS of its check.

The broker is reached through the command QI_SUBMIT_LEASE_COMMAND names, split as a shell would split it; the words
`take HOLDER` or `release NONCE` are appended. `take` prints one JSON object with `nonce` (32 hexadecimal digits) and
`lease_seconds` and exits 0, or exits nonzero with a reason on standard error; `release` frees the lease its nonce
names. A device with no command, an unreachable broker and a lease another device holds all refuse the submission
before any write.

Limits. The session belongs to the thread that opened it and does not nest. A submit route that does not call this
module, the provider's web client and every other client of the account enqueue outside the lease
(docs/notes/quantum_inspire/usage.md, "Submit lease").
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import re
import shlex
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterator
from typing import Any

COMMAND_VARIABLE = "QI_SUBMIT_LEASE_COMMAND"
HOLDER_VARIABLE = "QI_SUBMIT_LEASE_HOLDER"
COMMAND_TIMEOUT_SECONDS = 90
# The last write of a submission starts this long before the grantor frees the lease: a request's 60 s timeout, the
# token refresh and the one resend that qi_platform.Client.request makes after an expired-token answer.
MARGIN_SECONDS = 150
HOLDER = re.compile(r"[a-z0-9][a-z0-9-]{0,31}")
NONCE = re.compile(r"[0-9a-f]{32}")
# The batch job statuses that an admission read of another device counts (qi_platform.ENQUEUED_BATCH_STATUSES).
VISIBLE_STATUSES = frozenset({"queued", "reserved", "running", "finished"})


class Session:
    """One span of a submission in one thread: at most one lease and at most one created batch job."""

    def __init__(self) -> None:
        self.thread = threading.get_ident()
        self.nonce: str | None = None
        self.deadline = 0.0
        self.batch_requested = False
        self.batch_status: Callable[[], str] | None = None


_ACTIVE: Session | None = None


def clock() -> float:
    """Seconds since boot, counting suspended time where the platform has CLOCK_BOOTTIME (Linux)."""
    return time.clock_gettime(getattr(time, "CLOCK_BOOTTIME", time.CLOCK_MONOTONIC))


def _mine() -> Session | None:
    session = _ACTIVE
    return session if session is not None and session.thread == threading.get_ident() else None


def holder() -> str:
    """HOLDER_VARIABLE, or this device's host name reduced to the broker's holder alphabet."""
    name = os.environ.get(HOLDER_VARIABLE, "").strip()
    if not name:
        name = re.sub(r"[^a-z0-9-]", "-", socket.gethostname().lower()).strip("-")[:32]
    if HOLDER.fullmatch(name) is None:
        raise SystemExit(f"{HOLDER_VARIABLE} or the host name gives no holder of 1 to 32 lowercase letters or digits")
    return name


def ask(*words: str) -> dict[str, Any]:
    """Run the lease command with the words appended; its one JSON object, or SystemExit with the refusal."""
    command = shlex.split(os.environ.get(COMMAND_VARIABLE, ""))
    if not command:
        raise SystemExit(
            f"a hardware submission takes the account's submit lease first and {COMMAND_VARIABLE} names no lease "
            'command (docs/notes/quantum_inspire/usage.md, "Submit lease")'
        )
    try:
        done = subprocess.run(  # noqa: S603 - the owner's configured lease command and words matched above
            [*command, *words], capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SECONDS, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f"no submit lease: the lease command failed: {type(error).__name__}") from error
    if done.returncode != 0:
        reason = (done.stderr.strip().splitlines() or ["no reason given"])[-1][:200]
        raise SystemExit(f"no submit lease (lease command exit {done.returncode}): {reason}")
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        answer = None
    if not isinstance(answer, dict):
        raise SystemExit("no submit lease: the lease command's answer is not one JSON object")
    return answer


def take() -> None:
    """Take the lease for this thread's open session, once; outside a session the caller takes nothing."""
    session = _mine()
    if session is None or session.nonce is not None:
        return
    started = clock()
    answer = ask("take", holder())
    nonce, seconds = answer.get("nonce"), answer.get("lease_seconds")
    if not isinstance(nonce, str) or NONCE.fullmatch(nonce) is None:
        raise SystemExit("no submit lease: the lease command's answer lacks a nonce")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        seconds = 0.0
    if not math.isfinite(seconds) or not seconds > MARGIN_SECONDS:
        # The grant stands on the broker; hand it back, since no write of this session can fit in it.
        _release(nonce)
        raise SystemExit(f"no submit lease: the answer's lease_seconds is not above {MARGIN_SECONDS}")
    session.nonce, session.deadline = nonce, started + seconds - MARGIN_SECONDS


def expired() -> bool:
    """Whether this thread's session holds a lease whose deadline has passed; a write is then refused unsent."""
    session = _mine()
    return session is not None and session.nonce is not None and clock() >= session.deadline


def batch_requested() -> None:
    """Record that the request creating a batch job is being dispatched; its outcome is unknown until created()."""
    session = _mine()
    if session is not None and session.nonce is not None:
        session.batch_requested = True


def created(batch_status: Callable[[], str]) -> None:
    """Record the fresh-read of the batch job this session just created; the session's end calls it."""
    session = _mine()
    if session is not None and session.nonce is not None:
        session.batch_status = batch_status


def _release(nonce: str) -> None:
    try:
        ask("release", nonce)
    except SystemExit as error:
        print(f"submit lease not released, it expires by itself: {error}", file=sys.stderr)


def _close(session: Session) -> None:
    if session.nonce is None:
        return
    if session.batch_requested and session.batch_status is None:
        print("submit lease kept until it expires: the batch job's creation has no recorded answer", file=sys.stderr)
        return
    if session.batch_status is not None:
        try:
            status = session.batch_status()
        except BaseException as error:  # noqa: BLE001 - any failed read leaves the lease to expire
            print(f"submit lease kept until it expires: the batch read failed: {type(error).__name__}", file=sys.stderr)
            return
        if status not in VISIBLE_STATUSES:
            print(f"submit lease kept until it expires: the created batch job reads {status!r}", file=sys.stderr)
            return
    _release(session.nonce)


@contextlib.contextmanager
def session() -> Iterator[Session]:
    """Open the span in which take() acts for the calling thread."""
    global _ACTIVE  # noqa: PLW0603 - one session per process, guarded by the caller's SUBMIT_LOCK
    if _ACTIVE is not None:
        raise RuntimeError("a submit-lease session is open; sessions do not nest")
    _ACTIVE = opened = Session()
    try:
        yield opened
    finally:
        _ACTIVE = None
        _close(opened)
