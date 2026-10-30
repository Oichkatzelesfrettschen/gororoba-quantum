"""The local submission lock must not wait beyond its initiation horizon."""

import fcntl
from pathlib import Path

import pytest


def test_real_lock_contention_expires_before_entering_guard(tmp_path: Path) -> None:
    from qi_tuna_bounded_lock import bounded_lock

    path = tmp_path / "lock"
    path.touch()
    entered = False
    with path.open("r+") as holder, path.open("r+") as contender:
        fcntl.flock(holder.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(TimeoutError):
            with bounded_lock(contender.fileno(), 0.03, lambda: None):
                entered = True
        if entered:
            raise AssertionError("contended lock entered after the wait horizon")


def test_acquired_lock_excludes_a_second_descriptor_and_releases(tmp_path: Path) -> None:
    from qi_tuna_bounded_lock import bounded_lock

    path = tmp_path / "lock"
    path.touch()
    with path.open("r+") as owner, path.open("r+") as contender:
        with bounded_lock(owner.fileno(), 1.0, lambda: None):
            with pytest.raises(BlockingIOError):
                fcntl.flock(contender.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(contender.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_expiry_immediately_after_acquisition_releases_the_lock(tmp_path: Path) -> None:
    from qi_tuna_bounded_lock import bounded_lock

    path = tmp_path / "lock"
    path.touch()
    checks = 0

    def clock_check() -> None:
        nonlocal checks
        checks += 1
        if checks == 2:
            raise TimeoutError("fixture clock expired")

    with path.open("r+") as owner, path.open("r+") as contender:
        with pytest.raises(TimeoutError):
            with bounded_lock(owner.fileno(), 1.0, clock_check):
                raise AssertionError("expired clock entered the guard")
        fcntl.flock(contender.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_exception_inside_guard_releases_the_lock(tmp_path: Path) -> None:
    from qi_tuna_bounded_lock import bounded_lock

    path = tmp_path / "lock"
    path.touch()
    with path.open("r+") as owner, path.open("r+") as contender:
        with pytest.raises(RuntimeError):
            with bounded_lock(owner.fileno(), 1.0, lambda: None):
                raise RuntimeError("fixture failure inside guard")
        fcntl.flock(contender.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
