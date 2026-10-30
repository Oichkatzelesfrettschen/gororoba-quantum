"""Exact arithmetic for a stated actor-reporter execution-cost scenario.

The provider's sub-job overhead and initialization semantics are estimates.
The arithmetic cannot establish a charge ceiling, authorize a job, or infer
missing pilot and reference allocations.
"""

from fractions import Fraction

STAGES = ("pilot", "discovery", "references", "confirmation")


def estimate_mixed_cost(
    allocations: dict[str, list[tuple[int, int, int, int]]], *, subjobs: int, overhead_ns: int
) -> dict[str, object]:
    """Estimate stages with per-batch executions, repetition, circuit and initialization durations."""
    if (
        type(allocations) is not dict
        or set(allocations) != set(STAGES)
        or any(type(batches) is not list for batches in allocations.values())
        or any(
            type(batch) is not tuple
            or len(batch) != 4
            or any(type(value) is not int or not 0 <= value <= 10**12 for value in batch)
            or batch[0] == 0
            or batch[0] > 10**9
            for batches in allocations.values()
            for batch in batches
        )
        or not any(allocations.values())
        or type(subjobs) is not int
        or not 1 <= subjobs <= 10**6
        or type(overhead_ns) is not int
        or not 0 <= overhead_ns <= 10**12
    ):
        raise ValueError("supply all stages with explicit bounded nonempty batches and sub-job assumptions")
    repetition_delays = {batch[1] for batches in allocations.values() for batch in batches}
    if subjobs < len(repetition_delays):
        raise ValueError("each distinct repetition delay requires a separate job and at least one sub-job")
    stage_seconds = {
        stage: Fraction(
            sum(
                count * (repetition + circuit + initialization)
                for count, repetition, circuit, initialization in allocations[stage]
            ),
            10**9,
        )
        for stage in STAGES
    }
    overhead_seconds = Fraction(subjobs * overhead_ns, 10**9)
    return {
        "stage_seconds": stage_seconds,
        "overhead_seconds": overhead_seconds,
        "total_seconds": sum(stage_seconds.values(), overhead_seconds),
        "boundary": "Scenario estimate only; provider charge, runtime ceiling and admission remain unverified.",
    }


def estimate_cost(
    executions: dict[str, int],
    *,
    repetition_ns: int,
    circuit_ns: int,
    initialization_ns: int,
    subjobs: int,
    overhead_ns: int,
) -> dict[str, object]:
    """Calculate a fixed per-execution and per-subjob scenario in exact seconds."""
    if (
        type(executions) is not dict
        or set(executions) != set(STAGES)
        or any(type(count) is not int or not 0 <= count <= 10**9 for count in executions.values())
        or sum(executions.values()) == 0
        or any(
            type(value) is not int or not 0 <= value <= 10**12
            for value in (repetition_ns, circuit_ns, initialization_ns, overhead_ns)
        )
        or type(subjobs) is not int
        or not 1 <= subjobs <= 10**6
    ):
        raise ValueError("supply all four nonnegative execution counts and bounded integer timing assumptions")
    per_execution_ns = repetition_ns + circuit_ns + initialization_ns
    stage_seconds = {stage: Fraction(executions[stage] * per_execution_ns, 10**9) for stage in STAGES}
    overhead_seconds = Fraction(subjobs * overhead_ns, 10**9)
    return {
        "stage_seconds": stage_seconds,
        "overhead_seconds": overhead_seconds,
        "total_seconds": sum(stage_seconds.values(), overhead_seconds),
        "boundary": "Scenario estimate only; provider charge, runtime ceiling and admission remain unverified.",
    }
