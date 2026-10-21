"""scripts/n21_q143_line_switching.py: each batched bootstrap draw equals its single-draw computation bit for bit, a
planted two-state telegraph's switching time is recovered through noisy labels, and independent labels carry no
lag correlation.
"""

from __future__ import annotations

import n21_q143_line_switching as switching
import numpy as np


def telegraph(columns: int, tau_columns: float, weight: float, rng: np.random.Generator) -> np.ndarray:
    """A stationary two-state chain sampled once per column, with total switching rate 1 / tau_columns."""
    leave_one = (1.0 - weight) / tau_columns
    leave_two = weight / tau_columns
    state = np.empty(columns, dtype=bool)
    state[0] = rng.random() < weight
    for k in range(1, columns):
        rate = leave_one if state[k - 1] else leave_two
        state[k] = state[k - 1] ^ (rng.random() < 1.0 - np.exp(-rate))
    return state


def labels(state: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Log-likelihood labels of mean +-9 with unit-scale noise, NaN on one shot in fifty."""
    values = np.where(state, 9.0, -9.0) + rng.normal(0.0, 4.0, state.size)
    values[rng.random(state.size) < 0.02] = np.nan
    return values


def test_batched_draws_equal_single_draws() -> None:
    rng = np.random.default_rng(3)
    series = np.stack([labels(telegraph(1536, 3.0, 0.53, rng), rng) for _ in range(3)])
    index = switching.block_index(1536, 6, rng)
    batched = switching.switching_fit(series, index, 9.656)
    for draw in range(index.shape[0]):
        single = switching.switching_fit(series, index[draw : draw + 1], 9.656)
        for many, one in zip(batched, single, strict=True):
            if not np.array_equal(many[draw], one[0], equal_nan=True):
                raise AssertionError(f"draw {draw}: {many[draw]} against {one[0]}")


def test_planted_switching_time_is_recovered() -> None:
    rng = np.random.default_rng(11)
    tau_columns = 3.0
    series = np.stack([labels(telegraph(20000, tau_columns, 0.53, rng), rng) for _ in range(5)])
    tau, reliability, _mean = switching.switching_fit(series, np.arange(20000)[None, :], 1.0)
    if abs(tau[0] - tau_columns) > 0.15 * tau_columns or not 0.6 < reliability[0] < 1.0:
        raise AssertionError(f"tau {tau[0]:.3f} columns, reliability {reliability[0]:.3f}")


def test_independent_labels_carry_no_lag_correlation() -> None:
    rng = np.random.default_rng(17)
    series = labels(rng.random(20000) < 0.53, rng)[None, :]
    for lag in switching.REPORT_LAGS:
        r = switching.batched_autocorrelation(series, np.arange(20000)[None, :], lag)[0, 0]
        if abs(r) > 4.0 / np.sqrt(20000):
            raise AssertionError(f"lag {lag}: r = {r:.4f}")
