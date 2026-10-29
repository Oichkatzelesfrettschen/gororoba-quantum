"""Compare supplied UTC and boot-clock observations against the dispatch horizon."""

from typing import cast

import pytest


def test_utc_horizon_expires_at_equality() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1010.0, 10.0, 1.0)
    with pytest.raises(TimeoutError):
        clock.check(Observation("boot-a", 1010.0, 110.0))


def test_clock_rejects_changed_boot_identity_and_inconsistent_readings() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    for invalid in (
        Observation("boot-b", 1001.0, 101.0),
        Observation("boot-a", 999.0, 101.0),
        Observation("boot-a", 1001.0, 99.0),
        Observation("boot-a", 1005.0, 101.0),
    ):
        clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
        with pytest.raises(ValueError):
            clock.check(invalid)


def test_clock_rejects_backward_wall_step_after_a_valid_check() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    clock.check(Observation("boot-a", 1002.0, 102.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.5, 102.1))


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), True])
def test_clock_rejects_invalid_numeric_observations(invalid: float) -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", invalid, 101.0))


def test_clock_refusal_is_permanent_for_the_attempt() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation("boot-b", 1001.0, 101.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1002.0, 102.0))


def test_elapsed_limit_expires_even_when_utc_deadline_is_later() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1030.0, 10.0, 1.0)
    with pytest.raises(TimeoutError):
        clock.check(Observation("boot-a", 1010.0, 110.0))


def test_oversized_integer_refuses_and_latches_the_attempt() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 10**1000, 101.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_malformed_observation_refuses_and_latches_the_attempt() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(cast(Observation, None))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_normal_assignment_cannot_extend_horizon_or_clear_refusal() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1010.0, 20.0, 1.0)
    for name in ("utc_deadline", "_utc_deadline", "_initial", "_previous", "_elapsed_limit", "_tolerance", "_refused"):
        with pytest.raises(AttributeError):
            setattr(clock, name, 1020.0)
    with pytest.raises(TimeoutError):
        clock.check(Observation("boot-a", 1011.0, 111.0))
    for name in ("refused", "_refused"):
        with pytest.raises(AttributeError):
            setattr(clock, name, False)
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_boot_identity_subclass_cannot_override_comparison() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    class DeceptiveIdentity(str):
        def __ne__(self, other: object) -> bool:
            return False

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation(DeceptiveIdentity("boot-b"), 1001.0, 101.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_boot_identity_subclass_cannot_raise_an_unlatched_comparison_error() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    class RaisingIdentity(str):
        def __ne__(self, other: object) -> bool:
            raise TypeError("comparison must not execute")

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation(RaisingIdentity("boot-b"), 1001.0, 101.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_normal_attribute_deletion_cannot_remove_clock_state() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    for name in ("_initial", "_previous", "_utc_deadline", "_elapsed_limit", "_tolerance", "_refused"):
        with pytest.raises(AttributeError):
            delattr(clock, name)
    clock.check(Observation("boot-a", 1001.0, 101.0))


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), True, 10**1000])
def test_invalid_boot_reading_latches_refusal(invalid: float) -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, invalid))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1001.0, 101.0))


def test_invalid_initial_observations_and_bounds_cannot_construct_clock() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    for initial, deadline, elapsed, tolerance in (
        (Observation("", 1000.0, 100.0), 1020.0, 20.0, 1.0),
        (Observation("boot-a", 1000.0, -1.0), 1020.0, 20.0, 1.0),
        (Observation("boot-a", 1000.0, 100.0), 1000.0, 20.0, 1.0),
        (Observation("boot-a", 1000.0, 100.0), 1020.0, 0.0, 1.0),
        (Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, -1.0),
        (Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, float("nan")),
    ):
        with pytest.raises(ValueError):
            DispatchClock(initial, deadline, elapsed, tolerance)


@pytest.mark.parametrize("utc,boot", [(1002.0, 101.0), (1001.0, 102.0)])
def test_clock_accepts_exact_tolerance_and_rejects_greater_disagreement(utc: float, boot: float) -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    initial = Observation("boot-a", 1000.0, 100.0)
    DispatchClock(initial, 1020.0, 20.0, 1.0).check(Observation("boot-a", utc, boot))
    excessive_utc = utc + 0.125 if utc - 1000.0 > boot - 100.0 else utc
    excessive_boot = boot + 0.125 if boot - 100.0 > utc - 1000.0 else boot
    with pytest.raises(ValueError):
        DispatchClock(initial, 1020.0, 20.0, 1.0).check(Observation("boot-a", excessive_utc, excessive_boot))


def test_boot_clock_rollback_after_valid_check_latches_refusal() -> None:
    from qi_tuna_dispatch_clock import DispatchClock, Observation

    clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1020.0, 20.0, 1.0)
    clock.check(Observation("boot-a", 1002.0, 102.0))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1002.1, 101.5))
    with pytest.raises(ValueError):
        clock.check(Observation("boot-a", 1003.0, 103.0))
