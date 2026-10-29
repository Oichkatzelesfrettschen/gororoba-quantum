"""Acquire a local kernel lock with a suspend-aware wait limit.

The caller owns and validates the lock namespace, filesystem, descriptor, and
account binding. The caller supplies a fresh unlocked descriptor and an external
admission-clock check that performs only bounded local clock sampling. A blocked
callback can exceed the wait limit. The caller must keep the descriptor open and
prevent reuse, duplication or inheritance while the context runs. Context entry
does not admit later provider requests; each request needs its own fresh check.
This helper does not coordinate independent hosts.
"""

import fcntl
import math
import os
import stat
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager


@contextmanager
def bounded_lock(descriptor: int, wait_seconds: float, check_clock: Callable[[], None]) -> Iterator[None]:
    """Hold an exclusive lock after checking the caller's clock and local wait."""
    if type(descriptor) is not int or descriptor < 0 or not stat.S_ISREG(os.fstat(descriptor).st_mode):
        raise ValueError("lock descriptor must name a regular file")
    if type(wait_seconds) not in (int, float):
        raise ValueError("lock wait must be a finite positive number")
    try:
        valid_wait = math.isfinite(wait_seconds) and wait_seconds > 0
    except OverflowError:
        valid_wait = False
    if not valid_wait or not callable(check_clock):
        raise ValueError("lock wait or clock check is invalid")
    start = time.clock_gettime(time.CLOCK_BOOTTIME)
    deadline = start + wait_seconds
    if not math.isfinite(deadline):
        raise ValueError("lock wait deadline is invalid")
    while True:
        check_clock()
        remaining = deadline - time.clock_gettime(time.CLOCK_BOOTTIME)
        if remaining <= 0:
            raise TimeoutError("lock acquisition horizon expired")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            time.sleep(min(remaining, 0.05))
            continue
        try:
            check_clock()
            if time.clock_gettime(time.CLOCK_BOOTTIME) >= deadline:
                raise TimeoutError("lock acquisition horizon expired")
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        return
