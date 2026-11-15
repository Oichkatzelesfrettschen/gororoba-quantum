"""The account-wide submit lease a hardware submission takes from the owner's token broker.

A device counts the account's queue and hardware pause from its own read of the service and orders its sessions with
qi_platform.SUBMIT_LOCK, a file on that device. Two devices can therefore both pass the checks while the account sits
at its limit, each before the other's batch exists on the service. The lease closes that window among the devices that
run this repository: qi_platform.token_lock opens a session while it holds SUBMIT_LOCK, qi_platform.hardware_pause_left
takes the lease inside that session before it reads the account, and the session's end releases the lease once a fresh
read of the account shows no hardware batch in planning, so the next holder's read sees every batch this one created.

The broker is reached through the command QI_SUBMIT_LEASE_COMMAND names, split as a shell would split it; the words
`take HOLDER` or `release NONCE` are appended. `take` prints one JSON object with `nonce` (32 hexadecimal digits) and
`lease_seconds` and exits 0, or exits nonzero with a reason on standard error; `release` frees the lease its nonce
names. A device with no command, an unreachable broker and a lease another device holds all refuse the submission
before any resource request.

Outside the lease: a session ends without a release when its fresh read fails or shows a hardware batch still in
planning, and the lease then expires on the broker's clock; hardware_pause_left refuses every other submission while
that batch is younger than qi_platform.ABANDONED_PLANNING_SECONDS. A submission that outlasts lease_seconds is covered
by the same rule from its first batch request on. The provider's web client and any client that does not run this
module enqueue outside the lease (docs/notes/quantum_inspire/usage.md, "Submit lease").
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import shlex
import socket
import subprocess
import sys
from collections.abc import Callable, Iterator
from typing import Any

COMMAND_VARIABLE = "QI_SUBMIT_LEASE_COMMAND"
HOLDER_VARIABLE = "QI_SUBMIT_LEASE_HOLDER"
COMMAND_TIMEOUT_SECONDS = 90
HOLDER = re.compile(r"[a-z0-9][a-z0-9-]{0,31}")
NONCE = re.compile(r"[0-9a-f]{32}")


class Session:
    """One span of SUBMIT_LOCK: at most one lease, taken on the first hardware admission read."""

    def __init__(self) -> None:
        self.nonce: str | None = None
        self.planning: Callable[[], bool] | None = None


_ACTIVE: Session | None = None


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


def take(planning: Callable[[], bool]) -> None:
    """Take the lease for the open session, once; outside a session the caller only reads and takes nothing.

    `planning` reads the account afresh and answers whether a hardware batch is still in planning; the session's end
    calls it before the release.
    """
    session = _ACTIVE
    if session is None or session.nonce is not None:
        return
    answer = ask("take", holder())
    nonce, seconds = answer.get("nonce"), answer.get("lease_seconds")
    if not isinstance(nonce, str) or NONCE.fullmatch(nonce) is None:
        raise SystemExit("no submit lease: the lease command's answer lacks a nonce")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not seconds > 0:
        raise SystemExit("no submit lease: the lease command's answer lacks a positive lease_seconds")
    session.nonce, session.planning = nonce, planning


def _close(session: Session) -> None:
    if session.nonce is None or session.planning is None:
        return
    try:
        planning = session.planning()
    except BaseException as error:  # noqa: BLE001 - any failed read leaves the lease to expire
        print(f"submit lease kept until it expires: the account read failed: {type(error).__name__}", file=sys.stderr)
        return
    if planning:
        print("submit lease kept until it expires: a hardware batch is still in planning", file=sys.stderr)
        return
    try:
        ask("release", session.nonce)
    except SystemExit as error:
        print(f"submit lease not released, it expires by itself: {error}", file=sys.stderr)


@contextlib.contextmanager
def session() -> Iterator[Session]:
    """Open the span in which take() acts; a nested span joins the outer one."""
    global _ACTIVE  # noqa: PLW0603 - one session per process, guarded by the caller's SUBMIT_LOCK
    if _ACTIVE is not None:
        yield _ACTIVE
        return
    _ACTIVE = opened = Session()
    try:
        yield opened
    finally:
        _ACTIVE = None
        _close(opened)
