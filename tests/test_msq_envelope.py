"""The measurement-sequence envelope: layout rule, plan digest, replan count, fallback trigger and aggregate cap."""

from __future__ import annotations

import math
from typing import Any

import pytest

import msq_envelope as env


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def row(readout: float, **overrides: float | None) -> dict[str, float | None]:
    values: dict[str, float | None] = {
        "readout_error": readout,
        "sx_error": 2e-4,
        "t1_s": 2e-4,
        "t2_s": 1e-4,
        "prob_meas1_prep0": 0.005,
    }
    values.update(overrides)
    return values


def chain(n: int) -> tuple[dict[int, dict[str, float | None]], list[tuple[int, int]]]:
    """A path of n qubits whose readout error rises with the index, so the scan runs 0, 1, 2, ..."""
    return {q: row(0.001 + 1e-5 * q) for q in range(n)}, [(q, q + 1) for q in range(n - 1)]


def test_layout_keeps_graph_distance_three() -> None:
    qubits, edges = chain(60)
    layout = env.layout_rule(qubits, (), edges, 16)
    check(layout == [3 * k for k in range(16)], f"distance-3 scan of a path keeps every third qubit: {layout}")


def test_layout_distance_two_is_refused() -> None:
    qubits, edges = chain(5)
    near = env.coupling_distances(edges, 0, env.RULE_MIN_GRAPH_DISTANCE - 1)
    check(sorted(near) == [0, 1, 2], f"distance-2 neighborhood of a path end: {sorted(near)}")


def test_layout_orders_by_readout_then_index() -> None:
    qubits, edges = chain(60)
    qubits[30]["readout_error"] = 1e-4
    qubits[45]["readout_error"] = 1e-4
    layout = env.layout_rule(qubits, (), edges, 16)
    check(layout[:2] == [30, 45], f"lowest readout error first, ties by index: {layout[:2]}")


@pytest.mark.parametrize(
    "field, value",
    [
        ("readout_error", 0.011),
        ("sx_error", 1.1e-3),
        ("t1_s", 19e-6),
        ("t2_s", 19e-6),
        ("prob_meas1_prep0", 0.021),
        ("prob_meas1_prep0", None),
        ("prob_meas1_prep0", math.nan),
    ],
)
def test_layout_screens_each_threshold(field: str, value: float | None) -> None:
    check(env.qubit_eligibility(row(0.005, **{field: value})) is not None, f"{field}={value} must fail the rule")
    check(env.qubit_eligibility(row(0.005)) is None, "the base row is eligible")


def test_layout_respects_exclusions_and_refuses_short() -> None:
    qubits, edges = chain(60)
    layout = env.layout_rule(qubits, {0}, edges, 16)
    check(0 not in layout and layout[0] == 1, f"an excluded qubit is skipped: {layout[:3]}")
    with pytest.raises(env.EnvelopeError, match="only"):
        env.layout_rule(*chain(40)[:1], (), chain(40)[1], 16)
    with pytest.raises(env.EnvelopeError, match="tier"):
        env.layout_rule(qubits, (), edges, 20)


def plan(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "layout": [1, 4, 7],
        "qpy_sha256": "a" * 64,
        "execution_pubs": [{"name": "p", "components": []}],
        "sampler_options": {"init_qubits": True, "twirling": False},
        "rep_delay": 2e-5,
        "shots": 8192,
        "planner_seconds": 14.2,
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    "field, value",
    [
        ("layout", [1, 4, 8]),
        ("qpy_sha256", "b" * 64),
        ("execution_pubs", [{"name": "q", "components": []}]),
        ("sampler_options", {"init_qubits": True, "twirling": True}),
        ("rep_delay", 5e-5),
        ("planner_seconds", 14.3),
    ],
)
def test_plan_digest_moves_with_every_plan_field(field: str, value: Any) -> None:
    check(env.plan_digest(plan()) != env.plan_digest(plan(**{field: value})), f"{field} must move the digest")
    check(env.plan_digest(plan()) == env.plan_digest(plan()), "the digest is deterministic")


def test_plan_digest_requires_every_field() -> None:
    incomplete = plan()
    del incomplete["sampler_options"]
    with pytest.raises(env.EnvelopeError, match="sampler_options"):
        env.plan_digest(incomplete)


def test_replan_count_counts_any_digest_change() -> None:
    check(env.count_replans(["a", "a", "b", "b", "c", "d"]) == 3, "three changes are allowed")
    with pytest.raises(env.EnvelopeError, match="4 times"):
        env.count_replans(["a", "b", "c", "d", "e"])


@pytest.mark.parametrize(
    "status, code, circuit_ns, billed, permitted",
    [
        ("ERROR", 1305, 0, 2.0, True),  # the zero-delay jobs: no circuit, overhead billed
        ("ERROR", 1305, None, 2.0, True),
        ("ERROR", 1305, 0, 5.0, False),  # billed past the overhead
        ("ERROR", 1305, 1_000_000, 2.0, False),  # executed circuit time: an overrun ceiling
        ("ERROR", 1305, 0, None, False),  # unattributed charge
        ("ERROR", 1602, 1_000_000, 5.0, True),
        ("ERROR", 8030, None, None, True),
        ("ERROR", 8045, 0, 2.0, False),
        ("ERROR", None, 0, 2.0, False),
        ("DONE", None, 1_000_000, 4.0, False),
        ("CANCELLED", 1305, 0, 2.0, False),
    ],
)
def test_fallback_trigger(status: str, code: int | None, circuit_ns: int | None, billed: float | None, permitted: bool):
    check(
        env.fallback_permitted(status, code, circuit_ns, billed) is permitted, f"{status} {code} {circuit_ns} {billed}"
    )


def test_aggregate_cap_bounds_both_attempts() -> None:
    check(env.attempt_admission(1, 400.0, 60.0, 40.0, 20.0) == [], "attempt 1 admitted with the cap available")
    check(env.attempt_admission(1, 90.0, 60.0, 40.0, 20.0) != [], "attempt 1 needs the whole cap")
    check(env.attempt_admission(2, 400.0, 60.0, 40.0, 20.0, 20.0) == [], "attempt 2 within the cap")
    check(env.attempt_admission(2, 400.0, 60.0, 40.0, 20.0, 20.5) != [], "attempt 1 charge plus ceiling past the cap")
    check(env.attempt_admission(2, 75.0, 60.0, 40.0, 20.0, 2.0) != [], "attempt 2 ceiling past the quota")
    check(env.attempt_admission(1, 400.0, 60.0, 40.0, 20.0, 2.0) != [], "attempt 1 has no earlier charge")
    check(env.attempt_admission(3, 400.0, 60.0, 40.0, 20.0) != [], "no third attempt")
    check(env.attempt_admission(1, math.inf, 60.0, 40.0, 20.0) != [], "non-finite input refused")


def test_canonical_snapshot_is_order_free() -> None:
    first = env.canonical_snapshot({"b": 1, "a": [1, 2]}, {"q": {"x": 0.5}}, 3)
    second = env.canonical_snapshot({"a": [1, 2], "b": 1}, {"q": {"x": 0.5}}, 3)
    check(first == second, "key order must not move the canonical bytes")
    with pytest.raises(env.EnvelopeError):
        env.canonical_snapshot({}, {}, -1)
