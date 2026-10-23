"""Exact billing arithmetic and circuit-batch ceilings, independent of guessed device timing.

IQM durations are supplied observations or justified bounds, never inferred from
shot count alone. Open Quantum rates are supplied quote-checked tariffs. These
functions neither submit jobs nor establish a provider-enforced spending cap.
"""

from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal


def nonnegative(*values: Decimal) -> None:
    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("prices and durations must be finite and nonnegative")


def iqm_credits(rate: Decimal, compilation_seconds: Decimal, execution_seconds: Decimal) -> Decimal:
    nonnegative(rate, compilation_seconds, execution_seconds)
    return rate * (compilation_seconds + execution_seconds).to_integral_value(rounding=ROUND_CEILING)


def circuit_batches(circuits: int, shots: int, max_circuits: int, max_executions: int) -> list[int]:
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in (circuits, shots, max_circuits, max_executions)
    ):
        raise ValueError("circuit, shot and execution counts must be positive integers")
    capacity = min(max_circuits, max_executions // shots)
    if capacity == 0:
        raise ValueError("one circuit exceeds the execution ceiling")
    full, remainder = divmod(circuits, capacity)
    return [capacity] * full + ([remainder] if remainder else [])


def oq_credits(shots: int, task_rate: Decimal, shot_rate: Decimal) -> int:
    nonnegative(task_rate, shot_rate)
    if isinstance(shots, bool) or not isinstance(shots, int) or shots <= 0:
        raise ValueError("shots must be a positive integer")
    return int((task_rate + shots * shot_rate).to_integral_value(rounding=ROUND_CEILING))


def max_oq_shots(credit_ceiling: int, task_rate: Decimal, shot_rate: Decimal, minimum: int, maximum: int) -> int | None:
    nonnegative(task_rate, shot_rate)
    if credit_ceiling <= 0 or minimum <= 0 or maximum < minimum or shot_rate == 0:
        raise ValueError("a positive credit/shot bound and rate are required")
    limit = min(
        maximum, int(((Decimal(credit_ceiling) - task_rate) / shot_rate).to_integral_value(rounding=ROUND_FLOOR))
    )
    return limit if limit >= minimum else None
