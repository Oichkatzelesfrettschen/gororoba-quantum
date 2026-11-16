"""Contract for gororoba_quantum/qi_decay_models.py on counts that equal their expectation exactly.

Counts rounded from a known decay carry no random draw, so no seed enters and a fit must recover its generator to the
rounding of a count. The checks run known-good data through the fit (recovery, interval width against the Fisher
information, pinned parameters), known-bad data through the single exponential (a biexponential truth must read
overdispersed) and the likelihood-ratio test of a shared parameter in both directions.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np
import pytest

import qi_decay_models as models

DELAYS = (0.0, 5.0, 10.0, 20.0, 40.0, 80.0)
E01, E11, SHOTS = 0.03, 0.96, 8192


def make(shape: Callable[[float], float], step: float = 0.0) -> models.CountData:
    """Counts at the expected value of a decay shape, rounded to whole counts."""
    ones = tuple(
        round(SHOTS * (E01 + (E11 - E01) * shape(t) + (step if index >= 3 else 0.0))) for index, t in enumerate(DELAYS)
    )
    return models.CountData(
        DELAYS,
        ones,
        (SHOTS,) * 6,
        (E01,) * 6,
        (E11,) * 6,
        (0, 0, 0, 1, 1, 1),
        (round(E01 * 32768), 32768),
        (round(E11 * 32768), 32768),
    )


def single(t_us: float) -> Callable[[float], float]:
    return lambda t: math.exp(-t / t_us)


def fisher_halfwidth(t_us: float) -> float:
    """Standard error of T from the binomial Fisher information of the six points (readout constants known)."""
    information = 0.0
    for t in DELAYS:
        p = E01 + (E11 - E01) * math.exp(-t / t_us)
        slope = (E11 - E01) * math.exp(-t / t_us) * t / t_us**2
        information += SHOTS * slope**2 / (p * (1 - p))
    return 1.0 / math.sqrt(information)


def test_single_exponential_is_recovered_with_its_fisher_interval() -> None:
    data = make(single(22.0))
    result = models.fit("single", data)
    if abs(result.params["T_us"] - 22.0) > 0.05 or result.chi_square / result.freedom > 0.01:
        raise AssertionError((result.params, result.chi_square))
    low, high = models.profile_interval(result, data, "T_us")
    expected = fisher_halfwidth(22.0)
    if low is None or high is None or abs((high - low) / 2 - expected) > 0.05 * expected or not low < 22.0 < high:
        raise AssertionError((low, high, expected))
    wide_low, wide_high = models.profile_interval(result, data, "T_us", delta=4.0)
    if wide_low is None or wide_high is None or abs((wide_high - wide_low) / (high - low) - 2.0) > 0.1:
        raise AssertionError("a deviance rise of 4 is not twice the interval of 1")


def test_joint_fit_widens_the_interval_by_the_readout_covariance() -> None:
    data = make(single(22.0))
    fixed = models.fit("single", data)
    joint = models.fit("single", data, joint=True)
    fixed_low, fixed_high = models.profile_interval(fixed, data, "T_us")
    joint_low, joint_high = models.profile_interval(joint, data, "T_us")
    if fixed_low is None or fixed_high is None or joint_low is None or joint_high is None:
        raise AssertionError("an interval end sits at a bound")
    if not (joint_high - joint_low) > (fixed_high - fixed_low):
        raise AssertionError("readout counts as free parameters left the interval unchanged")
    if abs(joint.params["e01"] - E01) > 1e-3 or abs(joint.params["e11"] - E11) > 1e-3:
        raise AssertionError(joint.params)


def test_pinned_parameter_is_held_and_costs_deviance() -> None:
    data = make(single(22.0))
    pinned = models.fit("single", data, fixed={"T_us": 30.0})
    free = models.fit("single", data)
    if abs(pinned.params["T_us"] - 30.0) > 1e-9 or not pinned.deviance > free.deviance + 1.0:
        raise AssertionError((pinned.params, pinned.deviance, free.deviance))


def test_a_biexponential_truth_reads_overdispersed_under_one_exponential() -> None:
    truth = lambda t: 0.7 * math.exp(-t / 12.0) + 0.3 * math.exp(-t / 70.0)  # noqa: E731
    data = make(truth)
    bad = models.fit("single", data)
    good = models.fit("biexponential", data)
    if bad.chi_square / bad.freedom < 10.0:
        raise AssertionError(f"known-bad data read chi-square/dof {bad.chi_square / bad.freedom}")
    if good.chi_square / good.freedom > 0.05 or abs(good.params["T_fast_us"] - 12.0) > 0.5:
        raise AssertionError(good.params)
    if not good.summary()["bic"] < bad.summary()["bic"] - 20.0:
        raise AssertionError("BIC does not prefer the true two-rate model")


def test_delay_offset_and_step_models_recover_their_generators() -> None:
    offset = make(lambda t: math.exp(-(t + (4.0 if t > 0 else 0.0)) / 20.0))
    found = models.fit("delay_offset", offset)
    if abs(found.params["T_us"] - 20.0) > 0.1 or abs(found.params["t0_us"] - 4.0) > 0.1:
        raise AssertionError(found.params)
    stepped = make(single(22.0), step=0.02)
    found = models.fit("single_step", stepped)
    if abs(found.params["batch_step"] - 0.02) > 1e-3 or abs(found.params["T_us"] - 22.0) > 0.1:
        raise AssertionError(found.params)


def test_amplitude_step_model_reads_the_step_from_its_own_slot() -> None:
    stepped = make(single(22.0), step=0.02)
    found = models.fit("single_amplitude_step", stepped)
    if (
        abs(found.params["batch_step"] - 0.02) > 1e-3
        or abs(found.params["amplitude"] - 1.0) > 1e-3
        or abs(found.params["T_us"] - 22.0) > 0.1
        or found.freedom != 3
    ):
        raise AssertionError(found.params)
    unstepped = make(single(22.0))
    flat = models.fit("single_amplitude_step", unstepped)
    if abs(flat.params["batch_step"]) > 1e-3 or flat.deviance > 1e-3:
        raise AssertionError(flat.params)
    if "single_amplitude_step" in models.MODELS or "single_amplitude_step" not in models.ALL_MODELS:
        raise AssertionError("the step model must stay out of the committed battery")


def test_lognormal_mixture_reduces_to_the_single_exponential_at_zero_width() -> None:
    t = np.asarray(DELAYS)
    mixture = models.MODELS["lognormal"].shape(t, np.asarray([math.log(22.0), 0.01]))
    if np.max(np.abs(mixture - np.exp(-t / 22.0))) > 1e-3:
        raise AssertionError(mixture)
    wide = models.MODELS["lognormal"].shape(t, np.asarray([math.log(22.0), 0.8]))
    if not wide[-1] > 2.0 * math.exp(-80.0 / 22.0):
        raise AssertionError("a wide T1 distribution does not lengthen the tail")


def test_deviance_handles_zero_and_full_counts() -> None:
    value = models.deviance(np.array([0.0, 100.0]), np.array([100.0, 100.0]), np.array([0.5, 0.5]))
    if not math.isfinite(value) or abs(value - 4.0 * 100.0 * math.log(2.0)) > 1e-9:
        raise AssertionError(value)


def test_shared_parameter_test_accepts_a_shared_exponent_and_rejects_a_spread() -> None:
    def stretched(t_us: float, beta: float) -> Callable[[float], float]:
        return lambda t: math.exp(-((t / t_us) ** beta))

    shared = [make(stretched(t, 0.8)) for t in (15.0, 22.0, 30.0)]
    accepted = models.common_parameter(shared, "stretched", "exponent")
    if abs(accepted["value"] - 0.8) > 0.01 or accepted["p_common_vs_free"] < 0.99:
        raise AssertionError(accepted)
    spread = [make(stretched(t, beta)) for t, beta in ((15.0, 0.6), (22.0, 1.0), (30.0, 1.4))]
    rejected = models.common_parameter(spread, "stretched", "exponent")
    if rejected["p_common_vs_free"] > 1e-6:
        raise AssertionError(rejected)


def test_shared_parameter_test_gives_the_serial_value_bit_for_bit_in_the_process_pool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def stretched(t_us: float, beta: float) -> Callable[[float], float]:
        return lambda t: math.exp(-((t / t_us) ** beta))

    datas = [make(stretched(t, 0.8)) for t in (15.0, 22.0, 30.0)]
    found = {}
    for workers in ("1", "2"):
        monkeypatch.setenv("GOROROBA_WORKERS", workers)
        found[workers] = models.common_parameter(datas, "stretched", "exponent")
    if found["1"] != found["2"]:
        raise AssertionError(found)
