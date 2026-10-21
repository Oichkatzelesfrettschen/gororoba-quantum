"""Planted truths for scripts/n21_q143_segmented_sweep.py: the one-segment chain is the binomial, every
telegraph segment marginal is the beat kernel, a refused segment marginalizes, a later-segment offset breaks
exchangeability, a herald backaction plant is detected, and segment correlation separates a line mixture
from an exchange-coupled TLS in both directions.
"""

from __future__ import annotations

import math

import n21_q143_segmented_sweep as sweep
import numpy as np
import pytest

beat = sweep.beat
TRUTH_STATIC = sweep.TRUTH_STATIC
TEST_ALPHA = sweep.FAMILY_ALPHA / len(sweep.TESTS)


def test_one_segment_chain_is_the_binomial() -> None:
    values = sweep.unpack("static", np.array(TRUTH_STATIC))
    point = sweep.Point("x", "xy", 2079, 0, ("x",), (), np.array([[0], [1]]), np.ones(2))
    logs = sweep.hmm_log_likelihood(values, point)
    t = point.idle_us
    signal = (
        values["amplitude"]
        * np.exp(1j * values["phi"] - t / values["t_us"])
        * (
            values["a"] * np.exp(2j * math.pi * values["f1_mhz"] * t)
            + (1 - values["a"]) * np.exp(2j * math.pi * (values["f1_mhz"] + values["df_mhz"]) * t)
        )
    )
    zero = sweep.readout(signal.real, values)
    gap = abs(math.exp(logs[0]) - zero) + abs(math.exp(logs[1]) - (1 - zero))
    if gap >= 1e-12:
        raise AssertionError(f"one-segment HMM law differs from the binomial by {gap}")


def test_telegraph_marginals_are_the_beat_kernel() -> None:
    params = [*TRUTH_STATIC, 0.05]
    values = sweep.unpack("telegraph", np.array(params))
    point = sweep.Point(
        "x", "xy", 1386, 0, ("x", "y", "x", "y"), (sweep.NOMINAL_GAP_DT,) * 3, np.zeros((0, 4)), np.zeros(0)
    )
    patterns, probability = sweep.pattern_probabilities("telegraph", values, point)
    t = point.idle_us
    kernel = beat.telegraph_kernel(values["a"], values["f1_mhz"], values["df_mhz"], 0.05, np.array([t]))[0]
    signal = values["amplitude"] * np.exp(1j * values["phi"] - t / values["t_us"]) * kernel
    worst = 0.0
    for s, basis in enumerate(point.bases):
        marginal = float(probability[patterns[:, s] == 0].sum())
        expected = sweep.readout(signal.real if basis == "x" else signal.imag, values)
        worst = max(worst, abs(marginal - expected))
    if worst >= 1e-10:
        raise AssertionError(f"telegraph segment marginals differ from the kernel by {worst}")


def test_refused_segment_marginalizes() -> None:
    # The pattern with a -1 equals the sum over both reads of that segment.
    values = sweep.unpack("telegraph", np.array([*TRUTH_STATIC, 0.05]))
    point = sweep.Point(
        "x",
        "xy",
        693,
        0,
        ("x", "y", "x", "y"),
        (sweep.NOMINAL_GAP_DT,) * 3,
        np.array([[0, -1, 1, 0], [0, 0, 1, 0], [0, 1, 1, 0]]),
        np.ones(3),
    )
    logs = sweep.hmm_log_likelihood(values, point)
    gap = abs(math.exp(logs[0]) - math.exp(logs[1]) - math.exp(logs[2]))
    if gap >= 1e-12:
        raise AssertionError(f"a refused segment does not marginalize: {gap}")


def test_later_segment_offset_breaks_exchangeability() -> None:
    # Static draws pass; residual excitation after reset in segments 3 to 6 fails and forces the fallback.
    rng = np.random.default_rng(7)
    points = [p for p in sweep.design_points(6, 2048) if not p.pre_dt and p.kind == "xy"]
    clean = sweep.sample("static", TRUTH_STATIC, points, rng)
    passed = sweep.exchangeability(clean, TEST_ALPHA)["status"]
    biased = []
    for point in clean:
        patterns = point.patterns.copy()
        flip = rng.random(patterns.shape) < 0.04
        flip[:, :2] = False
        patterns[flip] = 1
        biased.append(
            point.with_counts(
                *sweep.tally(
                    [
                        tuple(row)
                        for row, count in zip(patterns.tolist(), point.counts, strict=True)
                        for _ in range(int(count))
                    ]
                )
            )
        )
    failed = sweep.exchangeability(biased, TEST_ALPHA)["status"]
    if passed != "exchangeable" or failed != "not_exchangeable":
        raise AssertionError(f"exchangeability read {passed}, {failed}")


def test_herald_backaction_is_detected() -> None:
    rng = np.random.default_rng(11)
    points = sweep.design_points(6, 2048)
    drawn = sweep.sample("static", TRUTH_STATIC, points, rng)
    clean = sweep.backaction(drawn, TEST_ALPHA)["status"]
    # Herald backaction plant: the controls lose 10 % of their coherence.
    dephased = [0.9 * TRUTH_STATIC[0], *TRUTH_STATIC[1:]]
    shifted = [point for point in drawn if not point.pre_dt]
    shifted += sweep.sample("static", dephased, [point for point in points if point.pre_dt], rng)
    moved = sweep.backaction(shifted, TEST_ALPHA)["status"]
    if clean != "no_backaction" or moved != "backaction":
        raise AssertionError(f"backaction read {clean}, {moved}")


def test_backaction_null_holds_its_level() -> None:
    # The static plant's line, fixed within a shot, correlates its X and Y
    # segments; without backaction the test rejects at about its level.
    rng = np.random.default_rng(29)
    points = sweep.design_points(6, 2048)
    paired = [p for p in points if p.pre_dt or (p.kind == "xy" and p.delay_dt in sweep.BACKACTION_DELAYS)]
    draws = [sweep.sample("static", TRUTH_STATIC, paired, rng) for _ in range(200)]
    rejected = sum(sweep.backaction(drawn, 0.05)["status"] == "backaction" for drawn in draws)
    if rejected > 20:
        raise AssertionError(f"the backaction null rejects {rejected} of 200 draws at level 0.05")


def test_backaction_without_reads_is_not_evaluable() -> None:
    points = sweep.design_points(6, 64)
    refused = []
    for point in points:
        patterns = np.zeros((1, len(point.bases)), dtype=np.int64)
        if point.pre_dt:
            patterns[:, [k for k, basis in enumerate(point.bases) if basis == "y"]] = -1
        refused.append(point.with_counts(patterns, np.array([64.0])))
    if sweep.backaction(refused, TEST_ALPHA)["status"] != "not_evaluable":
        raise AssertionError("a control without a Y read was evaluated")


def correlation_plants() -> tuple[list[sweep.Point], list[sweep.Point]]:
    """The static and tls plants, drawn in that order from one generator."""
    rng = np.random.default_rng(20261021)
    points = [p for p in sweep.design_points(6, 1024) if not p.pre_dt]
    static = sweep.primary(sweep.sample("static", TRUTH_STATIC, points, rng))
    tls = sweep.primary(sweep.sample("tls", sweep.extend("tls", TRUTH_STATIC), points, rng))
    return static, tls


# The best tls optimum over its starts clears the threshold exactly when every start's optimum does, so
# each start is its own test and the fits run on separate workers.
@pytest.mark.parametrize("p0", (0.0, 0.5, 0.95))
def test_static_plant_rejects_tls(p0: float) -> None:
    # A static truth correlates segments, so the independent-segment tls fit loses to the line mixture.
    drawn, _ = correlation_plants()
    static = sweep.Fit()(("static", TRUTH_STATIC, drawn, 0))
    tls = sweep.Fit()(("tls", [*TRUTH_STATIC, 0.02, p0], drawn, 0))
    margin = tls[0] - static[0]
    if margin <= math.log(1.0 / TEST_ALPHA):
        raise AssertionError(f"a static plant favors tls started at p0={p0} by {margin}")


@pytest.mark.parametrize("p0", (0.0, 0.5))
def test_tls_plant_rejects_the_line_mixture(p0: float) -> None:
    # A tls truth reads its segments independently, so the line mixture loses to the tls fit.
    _, drawn = correlation_plants()
    line = sweep.Fit()(("static", TRUTH_STATIC, drawn, 0))
    own = sweep.Fit()(("tls", [*TRUTH_STATIC, 0.02, p0], drawn, 0))
    reverse = line[0] - own[0]
    if reverse <= math.log(1.0 / TEST_ALPHA):
        raise AssertionError(f"a tls plant started at p0={p0} favors the line mixture by {reverse}")
