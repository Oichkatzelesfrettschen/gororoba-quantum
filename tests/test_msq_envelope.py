"""The measurement-sequence envelope: layout rule, plan digest, replan count, fallback trigger and aggregate cap."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
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


def envelope_groups(qubits: list[int]) -> list[Any]:
    import diagnostic_experiments as de

    per = {q: 545 for q in qubits}
    return de.msqe_groups(
        qubits, per, {q: 500 for q in qubits}, {q: 500 for q in qubits}, [0, 5000, 12500, 25000, 50000]
    )


def test_envelope_new_members_match_their_exact_oracle() -> None:
    """The reset controls, the patterns and a terminal-reset member of each arm against the exact oracle; planning
    proves every compiled member (qpu_planning.check_compiled_ideals), the 16-step members included."""
    import qpu_planning

    groups = envelope_groups([3, 9])
    for group in groups:
        for member in group.members:
            if member.circuit.num_clbits > 3:
                continue
            law = qpu_planning.ideal_compiled_probabilities(member.circuit)
            check(
                bool(np.allclose(law, member.ideal, rtol=0, atol=1e-10)),
                f"{member.name}: exact oracle {law} differs from the labeled ideal {member.ideal}",
            )


def test_envelope_members_are_dynamic_and_end_in_reset() -> None:
    import local_compute

    for group in envelope_groups([3, 9]):
        for member in group.members:
            check(local_compute.is_dynamic(member.circuit), f"{member.name} must run in the dynamic job")
            last = member.circuit.data[-1].operation.name
            check(last == "reset", f"{member.name} must end in a reset, ends in {last}")


def test_envelope_rows_align_across_qubits() -> None:
    import diagnostic_experiments as de

    groups = envelope_groups([3, 9, 27])
    base = 4 * len(de.MSQ_STEPS) + 4 + 1 + len(de.MSQ_T1_MICROSECONDS) + 4 * len(de.MSQ_DYNAMIC_STEPS) + 4
    patterns = de.MSQE_PATTERN_DESIGNS[16][0]
    lengths = {len(group.members) for group in groups}
    check(lengths == {base + 2 + patterns}, f"members per qubit {lengths}")
    for row in range(base + 2 + patterns):
        stems = {group.members[row].name.rsplit("_q", 1)[0] for group in groups}
        check(len(stems) == 1, f"row {row} fuses different members {stems}")


@pytest.mark.parametrize("width", [16, 24, 32, 5])
def test_envelope_patterns_are_an_orthogonal_design(width: int) -> None:
    """Every column holds K / 2 ones and every two columns agree in exactly K / 2 rows, so within either own state
    every other qubit sits in |1> in exactly K / 4 patterns; identical or complementary columns cannot occur."""
    import diagnostic_experiments as de

    bits = np.asarray(de.msqe_pattern_bits(width))
    order = de.MSQE_PATTERN_DESIGNS[de.msqe_pattern_tier(width)][0]
    check(bits.shape == (order, width), f"shape {bits.shape}")
    signs = 1 - 2 * bits
    check(bool((signs.sum(axis=0) == 0).all()), "a column is unbalanced")
    gram = signs.T @ signs
    check(bool((gram == order * np.eye(width, dtype=np.int64)).all()), "two columns are not orthogonal")
    for target in range(width):
        for state in (0, 1):
            rows = bits[:, target] == state
            for other in range(width):
                if other != target:
                    ones = int(bits[rows, other].sum())
                    check(ones == order // 4, f"rank {other} is in |1> {ones} times at rank {target} state {state}")


def test_envelope_pattern_design_refuses_bad_inputs() -> None:
    import diagnostic_experiments as de

    with pytest.raises(ValueError):
        de.msqe_pattern_bits(de.MSQE_MAX_WIDTH + 1)
    with pytest.raises(ValueError):
        de.paley_hadamard(1, 13)


def test_envelope_leaves_the_main_family_unchanged() -> None:
    import diagnostic_experiments as de

    static, dynamic = de.msq_members(5, 545, 500, 500, (0, 5000, 12500, 25000, 50000))
    check(
        all(m.circuit.data[-1].operation.name == "measure" for m in (*static, *dynamic)),
        "the main family gained a reset",
    )
