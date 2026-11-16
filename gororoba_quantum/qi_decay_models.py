"""Binomial-count fits of a decay against a delay, with the readout offsets of an assignment pair.

A delay point is a count of ones out of a shot total. The excited fraction obeys
P1(t) = e01 + (e11 - e01) * s(t) + step, where e01 and e11 are the readout probabilities of reading 1 from a
prepared 0 and a prepared 1, s(t) is a decay shape that starts at 1, and step is an optional additive offset of the
later batch. Every fit maximizes the binomial likelihood, so the deviance and the Pearson chi-square use the model's
fitted probability in the variance, and a profile likelihood bounds each parameter: the profile fixes the parameter
and refits the others, which carries the correlation of the free parameters into the interval. No random number
enters, so a fit and its intervals reproduce bit for bit on one platform.

Readout handling. With joint=False the readout probabilities are the per-point constants of CountData.e01 and
CountData.e11. With joint=True they are two extra parameters constrained by CountData.readout0 and readout1, the
pooled counts of the readout circuits, so the interval of a decay parameter carries their covariance.

Model comparison at a handful of points uses the deviance as -2 log L up to a constant shared by all models, AICc and
BIC over the number of count cells; a model with k parameters at n cells needs n - k - 1 > 0 for AICc.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import optimize, stats

import parallel

EPSILON = 1e-12
LN_T_BOUNDS = (math.log(0.5), math.log(1.0e4))
LN_RATIO_BOUNDS = (0.0, math.log(1.0e3))


@dataclass(frozen=True)
class CountData:
    """Counts of ones at each delay, the readout probabilities that map a state onto a count, and the readout counts.

    e01 and e11 hold one value per delay point (a constant for a pair measured once, or an interpolation). step is 1 for
    the points that carry the additive offset of the 'single_step' model. readout0 and readout1 are (ones, shots)
    pooled over every readout circuit and are needed only by joint fits.
    """

    delays_us: tuple[float, ...]
    ones: tuple[int, ...]
    shots: tuple[int, ...]
    e01: tuple[float, ...]
    e11: tuple[float, ...]
    step: tuple[int, ...] = ()
    readout0: tuple[int, int] | None = None
    readout1: tuple[int, int] | None = None


Shape = Callable[[np.ndarray, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class Model:
    """Parameter names, bounds, starts and decay shape; log marks a timescale stored as its natural logarithm."""

    name: str
    params: tuple[str, ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]
    log: tuple[bool, ...]
    starts: tuple[tuple[float, ...], ...]
    shape: Shape
    step: bool = False


def _single(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return np.exp(-t / math.exp(theta[0]))


def _amplitude(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return theta[1] * np.exp(-t / math.exp(theta[0]))


def _plateau(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return theta[1] + (1.0 - theta[1]) * np.exp(-t / math.exp(theta[0]))


def _stretched(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return np.exp(-((t / math.exp(theta[0])) ** theta[1]))


def _biexponential(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    fast = math.exp(theta[0])
    slow = fast * math.exp(theta[1])
    return (1.0 - theta[2]) * np.exp(-t / fast) + theta[2] * np.exp(-t / slow)


def _offset(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """Single exponential whose delay carries an extra t0 whenever a wait instruction exists (t > 0)."""
    return np.exp(-(t + theta[1] * (t > 0)) / math.exp(theta[0]))


_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite_e.hermegauss(48)
_GH_WEIGHTS = _GH_WEIGHTS / _GH_WEIGHTS.sum()


def _lognormal(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """Mean of exp(-t / T1) over a lognormal T1 of median exp(theta[0]) and log-width theta[1] (48-node quadrature)."""
    rates = np.exp(-theta[0] - theta[1] * _GH_NODES)
    return np.exp(-np.outer(t, rates)) @ _GH_WEIGHTS


_LN_STARTS = tuple(math.log(value) for value in (3.0, 8.0, 15.0, 30.0, 60.0))
MODELS: dict[str, Model] = {
    "single": Model(
        "single", ("T_us",), (LN_T_BOUNDS[0],), (LN_T_BOUNDS[1],), (True,), tuple((s,) for s in _LN_STARTS), _single
    ),
    "single_amplitude": Model(
        "single_amplitude",
        ("T_us", "amplitude"),
        (LN_T_BOUNDS[0], 0.5),
        (LN_T_BOUNDS[1], 1.5),
        (True, False),
        tuple((s, 1.0) for s in _LN_STARTS),
        _amplitude,
    ),
    "plateau": Model(
        "plateau",
        ("T_us", "plateau"),
        (LN_T_BOUNDS[0], 0.0),
        (LN_T_BOUNDS[1], 1.0),
        (True, False),
        tuple((s, c) for s in _LN_STARTS for c in (0.02, 0.1)),
        _plateau,
    ),
    "stretched": Model(
        "stretched",
        ("T_us", "exponent"),
        (LN_T_BOUNDS[0], 0.2),
        (LN_T_BOUNDS[1], 3.0),
        (True, False),
        tuple((s, b) for s in _LN_STARTS for b in (0.6, 1.0)),
        _stretched,
    ),
    "biexponential": Model(
        "biexponential",
        ("T_fast_us", "slow_over_fast", "slow_weight"),
        (LN_T_BOUNDS[0], LN_RATIO_BOUNDS[0], 0.0),
        (LN_T_BOUNDS[1], LN_RATIO_BOUNDS[1], 1.0),
        (True, True, False),
        tuple((s, r, w) for s in _LN_STARTS for r in (math.log(3.0), math.log(20.0)) for w in (0.1, 0.3)),
        _biexponential,
    ),
    "lognormal": Model(
        "lognormal",
        ("T_us", "sigma"),
        (LN_T_BOUNDS[0], 0.01),
        (LN_T_BOUNDS[1], 2.0),
        (True, False),
        tuple((s, w) for s in _LN_STARTS for w in (0.3, 0.8)),
        _lognormal,
    ),
    "delay_offset": Model(
        "delay_offset",
        ("T_us", "t0_us"),
        (LN_T_BOUNDS[0], 0.0),
        (LN_T_BOUNDS[1], 60.0),
        (True, False),
        tuple((s, t0) for s in _LN_STARTS for t0 in (1.0, 5.0)),
        _offset,
    ),
    "single_step": Model(
        "single_step",
        ("T_us", "batch_step"),
        (LN_T_BOUNDS[0], -0.2),
        (LN_T_BOUNDS[1], 0.2),
        (True, False),
        tuple((s, 0.0) for s in _LN_STARTS),
        _single,
        step=True,
    ),
}


def deviance(ones: np.ndarray, shots: np.ndarray, p: np.ndarray) -> float:
    """Binomial deviance 2 * sum[k ln(k / np) + (n - k) ln((n - k) / n(1 - p))], zero where a count is 0 or n."""
    p = np.clip(p, EPSILON, 1.0 - EPSILON)
    zeros = shots - ones
    first = np.where(ones > 0, ones * np.log(np.where(ones > 0, ones, 1.0) / (shots * p)), 0.0)
    second = np.where(zeros > 0, zeros * np.log(np.where(zeros > 0, zeros, 1.0) / (shots * (1.0 - p))), 0.0)
    return float(2.0 * np.sum(first + second))


def pearson_chi_square(ones: np.ndarray, shots: np.ndarray, p: np.ndarray) -> float:
    """Sum of (k - np)^2 / (n p (1 - p)) with the model probability in the variance."""
    p = np.clip(p, EPSILON, 1.0 - EPSILON)
    return float(np.sum((ones - shots * p) ** 2 / (shots * p * (1.0 - p))))


@dataclass(frozen=True)
class Fit:
    """One fitted model: parameters in report units, fit statistics and the optimizer's full parameter vector."""

    model: str
    joint: bool
    theta: tuple[float, ...]
    params: dict[str, float]
    deviance: float
    chi_square: float
    freedom: int
    cells: int
    free: int

    def summary(self) -> dict[str, Any]:
        aicc_penalty = self.cells - self.free - 1
        aic = self.deviance + 2 * self.free
        return {
            "params": self.params,
            "deviance": self.deviance,
            "chi_square": self.chi_square,
            "freedom": self.freedom,
            "chi_square_per_dof": self.chi_square / self.freedom if self.freedom > 0 else None,
            "chi_square_probability": float(stats.chi2.sf(self.chi_square, self.freedom)) if self.freedom > 0 else None,
            "aicc": aic + 2 * self.free * (self.free + 1) / aicc_penalty if aicc_penalty > 0 else None,
            "bic": self.deviance + self.free * math.log(self.cells),
        }


def _arrays(data: CountData) -> tuple[np.ndarray, ...]:
    return (
        np.asarray(data.delays_us, dtype=float),
        np.asarray(data.ones, dtype=float),
        np.asarray(data.shots, dtype=float),
        np.asarray(data.e01, dtype=float),
        np.asarray(data.e11, dtype=float),
        np.asarray(data.step if data.step else (0,) * len(data.ones), dtype=float),
    )


def _objective(model: Model, data: CountData, joint: bool) -> Callable[[np.ndarray], float]:
    t, ones, shots, e01_fixed, e11_fixed, step = _arrays(data)
    width = len(model.params)
    readout = None
    if joint:
        if data.readout0 is None or data.readout1 is None:
            raise ValueError("a joint fit needs the pooled readout counts")
        readout = (
            np.asarray([data.readout0[0], data.readout1[0]], dtype=float),
            np.asarray([data.readout0[1], data.readout1[1]], dtype=float),
        )

    def value(theta: np.ndarray) -> float:
        e01 = theta[width] if joint else e01_fixed
        e11 = theta[width + 1] if joint else e11_fixed
        shape = model.shape(t, theta[:width])
        p = e01 + (e11 - e01) * shape
        if model.step:
            p = p + theta[1] * step
        total = deviance(ones, shots, p)
        if readout is not None:
            total += deviance(readout[0], readout[1], np.asarray([theta[width], theta[width + 1]]))
        return total

    return value


def fit(
    model_name: str,
    data: CountData,
    joint: bool = False,
    fixed: dict[str, float] | None = None,
    warm: tuple[float, ...] | None = None,
) -> Fit:
    """Maximum-likelihood fit by L-BFGS-B from the starts of the model; fixed pins named parameters (log ones in us).

    warm is an optimizer vector of an earlier fit, tried first; with it only every fifth default start follows, which
    keeps a profile refit cheap while a second basin still gets a trial.
    """
    model = MODELS[model_name]
    names = list(model.params) + (["e01", "e11"] if joint else [])
    lower = list(model.lower) + ([0.0, 0.0] if joint else [])
    upper = list(model.upper) + ([1.0, 1.0] if joint else [])
    logs = list(model.log) + ([False, False] if joint else [])
    pinned: dict[int, float] = {}
    for name, value in (fixed or {}).items():
        index = names.index(name)
        pinned[index] = math.log(value) if logs[index] else value
    free_index = [i for i in range(len(names)) if i not in pinned]
    starts = [list(start) for start in model.starts]
    if joint:
        if data.readout0 is None or data.readout1 is None:
            raise ValueError("a joint fit needs the pooled readout counts")
        tail = [data.readout0[0] / data.readout0[1], data.readout1[0] / data.readout1[1]]
        starts = [start + tail for start in starts]
    if warm is not None:
        starts = [list(warm)] + starts[::5]
    objective = _objective(model, data, joint)
    best_theta: np.ndarray | None = None
    best_value = math.inf

    def expand(reduced: np.ndarray) -> np.ndarray:
        theta = np.empty(len(names))
        for i, value in pinned.items():
            theta[i] = value
        for slot, i in enumerate(free_index):
            theta[i] = reduced[slot]
        return theta

    if not free_index:
        best_theta = expand(np.empty(0))
        best_value = objective(best_theta)
    else:
        bounds = [(lower[i], upper[i]) for i in free_index]
        seen: set[tuple[float, ...]] = set()
        for start in starts:
            x0 = np.array([min(max(start[i], lower[i]), upper[i]) for i in free_index])
            key = tuple(np.round(x0, 9))
            if key in seen:
                continue
            seen.add(key)
            result = optimize.minimize(
                lambda x: objective(expand(x)),
                x0,
                method="L-BFGS-B",
                bounds=bounds,
                options={"ftol": 1e-15, "gtol": 1e-10, "maxiter": 2000},
            )
            if result.fun < best_value:
                best_value, best_theta = float(result.fun), expand(result.x)
    if best_theta is None:
        raise ValueError(f"no start of {model_name} produced a fit")
    t, ones, shots, e01_fixed, e11_fixed, step = _arrays(data)
    width = len(model.params)
    e01 = best_theta[width] if joint else e01_fixed
    e11 = best_theta[width + 1] if joint else e11_fixed
    p = e01 + (e11 - e01) * model.shape(t, best_theta[:width])
    if model.step:
        p = p + best_theta[1] * step
    cells = len(ones) + (2 if joint else 0)
    chi_square = pearson_chi_square(ones, shots, p)
    if joint and data.readout0 is not None and data.readout1 is not None:
        chi_square += pearson_chi_square(
            np.asarray([data.readout0[0], data.readout1[0]], dtype=float),
            np.asarray([data.readout0[1], data.readout1[1]], dtype=float),
            np.asarray([best_theta[width], best_theta[width + 1]]),
        )
    free = len(free_index)
    params = {name: (math.exp(best_theta[i]) if logs[i] else float(best_theta[i])) for i, name in enumerate(names)}
    return Fit(
        model_name,
        joint,
        tuple(float(x) for x in best_theta),
        params,
        best_value,
        chi_square,
        cells - free,
        cells,
        free,
    )


def profile_interval(best: Fit, data: CountData, name: str, delta: float = 1.0) -> tuple[float | None, float | None]:
    """Profile-likelihood interval of one parameter at a deviance rise of delta; None marks an end at a bound.

    The profile refits every other parameter with this one pinned. A deviance rise of 1.00 is the 68.3% interval of
    one parameter; delta = max(1, chi-square / dof) widens it for the overdispersion of a model that does not fit.
    """
    model = MODELS[best.model]
    names = list(model.params) + (["e01", "e11"] if best.joint else [])
    index = names.index(name)
    lower = (list(model.lower) + [0.0, 0.0])[index] if best.joint else model.lower[index]
    upper = (list(model.upper) + [1.0, 1.0])[index] if best.joint else model.upper[index]
    is_log = (list(model.log) + [False, False])[index] if best.joint else model.log[index]
    hat = best.theta[index]

    def gap(x: float) -> float:
        pinned = math.exp(x) if is_log else x
        return fit(best.model, data, best.joint, {name: pinned}, warm=best.theta).deviance - best.deviance - delta

    def side(bound: float) -> float | None:
        if abs(bound - hat) < 1e-9 or gap(bound) < 0.0:
            return None
        return float(optimize.brentq(gap, min(hat, bound), max(hat, bound), xtol=1e-9, rtol=1e-10))

    low, high = side(lower), side(upper)
    convert = math.exp if is_log else float
    return (None if low is None else convert(low), None if high is None else convert(high))


class FitDeviance:
    """Deviance of one dataset under a named model, optionally with parameters pinned.

    A module-level class so that parallel.ordered_map can pickle it for the worker processes.
    """

    def __init__(self, model_name: str, fixed: dict[str, float] | None = None) -> None:
        self.model_name = model_name
        self.fixed = fixed

    def __call__(self, data: CountData) -> float:
        return fit(self.model_name, data, fixed=self.fixed).deviance


def common_parameter(datas: list[CountData], model_name: str, name: str) -> dict[str, float]:
    """Likelihood-ratio test that all datasets share one value of a model parameter, each with its own timescale.

    The common value minimizes the pooled deviance of the model over a bounded scan; the pooled deviance of the
    single exponential and of the model with a free value per dataset bracket it. Freedom of the common-against-free
    ratio is the number of datasets minus one. The datasets are independent, so each deviance sum maps its fits over
    the process pool and adds them in dataset order, which gives the serial sum bit for bit; the scan itself is
    sequential.
    """
    model = MODELS[model_name]
    index = model.params.index(name)
    free_total = sum(parallel.ordered_map(FitDeviance(model_name), datas, min_items=2))
    single_total = sum(parallel.ordered_map(FitDeviance("single"), datas, min_items=2))

    def pooled(value: float) -> float:
        return sum(parallel.ordered_map(FitDeviance(model_name, {name: value}), datas, min_items=2))

    scan = optimize.minimize_scalar(
        pooled, bounds=(model.lower[index], model.upper[index]), method="bounded", options={"xatol": 1e-6}
    )
    common = float(scan.x)
    return {
        "value": common,
        "deviance_single": single_total,
        "deviance_common": float(scan.fun),
        "deviance_free": free_total,
        "lr_common_vs_free": float(scan.fun) - free_total,
        "freedom_common_vs_free": len(datas) - 1,
        "p_common_vs_free": float(stats.chi2.sf(float(scan.fun) - free_total, len(datas) - 1)),
        "lr_single_vs_common": single_total - float(scan.fun),
        "p_single_vs_common": float(stats.chi2.sf(single_total - float(scan.fun), 1)),
    }


def readout_variants(task: dict[str, Any]) -> dict[str, tuple[list[float], list[float]]]:
    """Per-point (e01, e11) lists for the opening pair, the closing pair, their mean and their time interpolation."""
    opening, closing = task["opening"], task["closing"]
    o0, o1 = opening["zero"][0] / opening["zero"][1], opening["one"][0] / opening["one"][1]
    c0, c1 = closing["zero"][0] / closing["zero"][1], closing["one"][0] / closing["one"][1]
    count = len(task["ones"])
    span = closing["time_s"] - opening["time_s"]
    weights = (
        [min(1.0, max(0.0, (time - opening["time_s"]) / span)) for time in task["time_s"]]
        if span > 0
        else [0.5] * count
    )
    return {
        "opening": ([o0] * count, [o1] * count),
        "closing": ([c0] * count, [c1] * count),
        "mean": ([(o0 + c0) / 2] * count, [(o1 + c1) / 2] * count),
        "interpolated": (
            [(1 - w) * o0 + w * c0 for w in weights],
            [(1 - w) * o1 + w * c1 for w in weights],
        ),
    }


def build_data(task: dict[str, Any], e01: list[float], e11: list[float], keep: int | None = None) -> CountData:
    cut = len(task["ones"]) if keep is None else keep
    opening, closing = task["opening"], task["closing"]
    return CountData(
        tuple(task["delays_us"][:cut]),
        tuple(task["ones"][:cut]),
        tuple(task["shots"][:cut]),
        tuple(e01[:cut]),
        tuple(e11[:cut]),
        tuple(task["step"][:cut]),
        (opening["zero"][0] + closing["zero"][0], opening["zero"][1] + closing["zero"][1]),
        (opening["one"][0] + closing["one"][0], opening["one"][1] + closing["one"][1]),
    )


def _report(result: Fit, data: CountData) -> dict[str, Any]:
    """Fit summary with the profile interval of each parameter, nominal and widened by max(1, chi-square / dof)."""
    summary = result.summary()
    scale = max(1.0, result.chi_square / result.freedom) if result.freedom > 0 else 1.0
    names = list(MODELS[result.model].params) + (["e01", "e11"] if result.joint else [])
    summary["interval"] = {}
    summary["interval_scaled"] = {}
    for name in names:
        if name in ("e01", "e11"):
            continue
        summary["interval"][name] = list(profile_interval(result, data, name, 1.0))
        summary["interval_scaled"][name] = list(profile_interval(result, data, name, scale))
    summary["interval_scale"] = scale
    return summary


def analyze_decay(task: dict[str, Any]) -> dict[str, Any]:
    """One qubit's battery: every decay model on the mean readout pair, the single exponential under each readout
    choice and jointly with the readout counts, and the tail residual of the early-point fit.

    task holds primitives only (a module-level callable for parallel.ordered_map): delays_us, ones, shots, step (1 on
    the points after the batch boundary) and time_s (finish time of each point's job) lists, and opening and closing,
    each {"zero": [ones, shots], "one": [ones, shots], "time_s": float}.
    """
    variants = readout_variants(task)
    mean = build_data(task, *variants["mean"])
    report: dict[str, Any] = {
        "qubit": task["qubit"],
        "observed": [o / s for o, s in zip(task["ones"], task["shots"], strict=True)],
        "models": {name: _report(fit(name, mean), mean) for name in MODELS},
    }
    readout: dict[str, Any] = {}
    for name, (e01, e11) in variants.items():
        data = build_data(task, e01, e11)
        readout[name] = _report(fit("single", data), data)
    report["single_by_readout"] = readout
    single = fit("single", mean)
    p_single = np.asarray(mean.e01) + (np.asarray(mean.e11) - np.asarray(mean.e01)) * _single(
        np.asarray(mean.delays_us), np.asarray(single.theta)
    )
    shots_all, ones_all = np.asarray(mean.shots, dtype=float), np.asarray(mean.ones, dtype=float)
    report["single_residual_z"] = [
        float(value) for value in (ones_all - shots_all * p_single) / np.sqrt(shots_all * p_single * (1 - p_single))
    ]
    joint = fit("single", mean, joint=True)
    report["single_joint"] = _report(joint, mean)
    early = len(task["ones"]) - 1
    if early >= 3:
        early_data = build_data(task, *variants["mean"], keep=early)
        early_fit = fit("single", early_data)
        p = variants["mean"][0][early] + (variants["mean"][1][early] - variants["mean"][0][early]) * math.exp(
            -task["delays_us"][early] / early_fit.params["T_us"]
        )
        shots, ones = task["shots"][early], task["ones"][early]
        report["tail_residual"] = {
            "fit_points": early,
            "T_us": early_fit.params["T_us"],
            "predicted": p,
            "observed": ones / shots,
            "z": (ones - shots * p) / math.sqrt(shots * p * (1 - p)),
        }
    return report
