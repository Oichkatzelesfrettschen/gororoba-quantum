"""Check complete stage accounting for the actor-reporter cost scenario."""

from fractions import Fraction

import pytest
import readout_actor_cost_model as cost_model
from readout_actor_cost_model import estimate_cost


def test_each_stage_and_subjob_contributes_to_the_total() -> None:
    result = estimate_cost(
        {"pilot": 0, "discovery": 80000, "references": 0, "confirmation": 240000},
        repetition_ns=30000,
        circuit_ns=2212,
        initialization_ns=2212,
        subjobs=2,
        overhead_ns=2000000000,
    )
    if result["stage_seconds"] != {
        "pilot": Fraction(0),
        "discovery": Fraction(8606, 3125),
        "references": Fraction(0),
        "confirmation": Fraction(25818, 3125),
    }:
        raise AssertionError("stage execution costs differ from the exact nanosecond accounting")
    if result["total_seconds"] != Fraction(46924, 3125):
        raise AssertionError("the total must include every execution and both sub-job overheads")


def test_missing_stages_and_boolean_counts_are_rejected() -> None:
    for counts in (
        {"discovery": 1, "references": 0, "confirmation": 1},
        {"pilot": 0, "discovery": True, "references": 0, "confirmation": 1},
        {"pilot": 0, "discovery": -1, "references": 0, "confirmation": 1},
    ):
        with pytest.raises(ValueError):
            estimate_cost(
                counts, repetition_ns=30000, circuit_ns=2212, initialization_ns=2212, subjobs=2, overhead_ns=2000000000
            )


def test_references_are_added_and_estimate_is_not_an_admission() -> None:
    common = {
        "repetition_ns": 50000,
        "circuit_ns": 2212,
        "initialization_ns": 2212,
        "subjobs": 1,
        "overhead_ns": 2000000000,
    }
    without_reference = estimate_cost({"pilot": 0, "discovery": 1, "references": 0, "confirmation": 0}, **common)
    with_reference = estimate_cost({"pilot": 0, "discovery": 1, "references": 100, "confirmation": 0}, **common)
    baseline = without_reference["total_seconds"]
    if not isinstance(baseline, Fraction) or with_reference["total_seconds"] != baseline + Fraction(54424, 10000000):
        raise AssertionError("reference executions must enter the estimate")
    if "admission remain unverified" not in str(with_reference["boundary"]):
        raise AssertionError("an estimate must explicitly withhold admission")


def test_mixed_cost_uses_each_stage_delay_and_circuit_duration() -> None:
    result = cost_model.estimate_mixed_cost(
        {
            "pilot": [(1000, 50000, 2212, 2212)],
            "discovery": [(80000, 30000, 2212, 2212)],
            "references": [(1000, 30000, 5000, 2212)],
            "confirmation": [(240000, 30000, 2212, 2212)],
        },
        subjobs=3,
        overhead_ns=2000000000,
    )
    if result["total_seconds"] != Fraction(4276829, 250000):
        raise AssertionError("mixed duration stages and all overhead must be counted exactly")
    if "admission remain unverified" not in str(result["boundary"]):
        raise AssertionError("the mixed calculation must remain a scenario, not an admission")


def test_mixed_cost_refuses_unspecified_or_malformed_allocations() -> None:
    invalid_allocations: list[dict[str, list[tuple[int, int, int, int]]]] = [
        {"pilot": [], "discovery": [], "confirmation": []},
        {"pilot": [], "discovery": [], "references": [(True, 30000, 2212, 2212)], "confirmation": []},
        {"pilot": [], "discovery": [], "references": [(100, 30000, -1, 2212)], "confirmation": []},
    ]
    for allocations in invalid_allocations:
        with pytest.raises(ValueError):
            cost_model.estimate_mixed_cost(allocations, subjobs=1, overhead_ns=2000000000)


def test_mixed_cost_refuses_fewer_subjobs_than_distinct_repetition_delays() -> None:
    allocations = {
        "pilot": [(1, 50000, 2212, 2212)],
        "discovery": [(1, 30000, 2212, 2212)],
        "references": [],
        "confirmation": [],
    }
    with pytest.raises(ValueError):
        cost_model.estimate_mixed_cost(allocations, subjobs=1, overhead_ns=2000000000)
