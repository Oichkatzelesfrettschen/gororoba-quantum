"""Check complete stage accounting for the actor-reporter cost scenario."""

import json
from fractions import Fraction
from pathlib import Path

import pytest
import readout_actor_cost_model as cost_model
from readout_actor_cost_model import estimate_cost

import readout_actor_family as actor_family


def test_complete_delay_qualification_allocation_and_ceiling() -> None:
    """The fixed pilot accounts for every PUB, stage and submission tier."""
    path = Path(__file__).resolve().parents[2] / "docs/design/readout-actor-delay-qualification.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    actor_family.validate_case(case)
    if (case["width"], case["reporters"], case["actors"], case["pairs"]) != (156, [0, 1], [2], [[0, 1]]):
        raise AssertionError("the pilot must retain the frozen full-register intervention and reporter pair")
    if (
        Fraction(str(case["initialization_seconds"])) != Fraction(2212, 10**9)
        or case["job_overhead_seconds"] != 2
        or case["reserve_seconds"] != 48
    ):
        raise AssertionError("the cost scenario must bind its initialization proxy, job overhead and reserve")
    batches = actor_family._batches(case)
    if len(batches) != 3 or [len(batch) for batch in batches] != [8, 8, 8]:
        raise AssertionError("the pilot must account for three complete delay tiers")
    expected = [(30_000, 4096, "pilot"), (50_000, 4096, "pilot"), (250_000, 1024, "references")]
    allocation: dict[str, list[tuple[int, int, int, int]]] = {stage: [] for stage in cost_model.STAGES}
    batch_seconds = []
    for batch, (delay_ns, shots, stage) in zip(batches, expected, strict=True):
        conditions = {(row["arm"], row["input"]) for row in batch}
        if conditions != {(arm, bits) for arm in ("idle", "active") for bits in range(4)}:
            raise AssertionError("a delay tier loses a preparation or actor arm")
        if any(
            row["shots"] != shots
            or row["stage"] != stage
            or Fraction(str(row["rep_delay_seconds"])) != Fraction(delay_ns, 10**9)
            for row in batch
        ):
            raise AssertionError("the operational case differs from the frozen allocation")
        allocation[stage].append((8 * shots, delay_ns, 2212, 2212))
        batch_seconds.append(Fraction(8 * shots * (delay_ns + 4424), 10**9) + 2)
    result = cost_model.estimate_mixed_cost(allocation, subjobs=len(batches), overhead_ns=2_000_000_000)
    if result["total_seconds"] != Fraction(10_995_612_672, 10**9):
        raise AssertionError("the complete pilot cost differs from exact nanosecond arithmetic")
    if sum(row["shots"] for row in case["allocations"]) != 73728:
        raise AssertionError("the pilot must retain all 73728 full-register shots")
    if any(seconds > case["max_execution_seconds"] for seconds in batch_seconds):
        raise AssertionError("a modeled job exceeds the pilot ceiling")
    if len(batches) * case["max_execution_seconds"] != 18 or case["max_total_execution_seconds"] != 20:
        raise AssertionError("the pilot must fit the complete 20-second program envelope")
    if case["inference"] != "descriptive" or allocation["confirmation"] or allocation["discovery"]:
        raise AssertionError("the pilot cannot silently acquire confirmatory or discovery data")


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
