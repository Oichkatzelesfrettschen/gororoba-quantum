"""Preregistered analysis of the segmented coprime sweep of ibm_fez qubit 143.

The sweep (qpe_diagnostics.n21_segmented_ramsey, live_run --segmented-*)
reads a spectator qubit, 143 in the design, in K segments per shot with its
control in |0>; the analysis reads the spectator from the run. Each
segment is a herald, a preparation, an idle of delay_dt, a basis change and
a readout; a reset of the spectator opens every segment after the first. An "xy"
member alternates X and Y readouts after a |+> preparation (segment 1 X),
so both quadratures of a delay share every shot; a "z" member reads Z after
an X preparation. Members with a pre-idle between herald and preparation
are the herald-backaction controls.

Statistical unit. A shot is the independent unit. A frequency line fixed
within a shot (charge parity, a static mixture, slow telegraph switching)
correlates every segment of the shot, so the static and telegraph models
score each shot's whole readout pattern through a two-state hidden Markov
chain: the line starts stationary at (a, 1 - a), switches at total rate
gamma, and during an idle of t the joint law of the readout and the end
state is linear in exp(W t) and exp(M t), M = 2 pi i diag(f1, f1 + df) + W
(Kubo-Anderson). gamma = 0 is the static mixture a Bin(p1) + (1 - a)
Bin(p2) per shot. An exchange-coupled two-level system (tls) puts both
dressed lines into every shot coherently, so its X and Y segments are
independent; the TLS population p cancels from the qubit's Ramsey signal
(n21_q143_beat_model self-check tls) but sets the Z swap depth
4 a (1 - a) (1 - p), so p0 at shot start is a free nuisance in [0, 1].
Within-shot correlation of the X and Y segments therefore separates a
classical line mixture from a TLS at every p.

Primary data: every X and Y segment of the delay members and segment 1 of
every Z member. Z segments after the first carry the TLS memory (a swap
leaves the TLS excited across the reset), which the z_memory test reads.

Readout. A true mean mu reads (1 - e0 - e1) mu + (e1 - e0); e0 and e1 are
free parameters bounded in [1e-5, 0.1]. The published assignment errors
carry no trial counts, so no calibration likelihood enters.

Frequencies are MHz, times us, phases follow n21_q143_beat_model
(rz(+theta) advances phi by +theta, a level raised by E contributes
exp(-2 pi i E t)). The gcd of the delays sets the unaliased complex band;
alias cells of the retained 836 dt lattice (f0 = 299.04 kHz) index the
candidates, and the alias test fits df inside each cell.

Tests share the family alpha equally (TESTS). Decisions read likelihood
ratios against log(1 / test alpha), an evidential threshold: a model or
alias whose NLL exceeds the best by more than log(1 / alpha) is excluded.

Admission reads the returned scheduler table: every segment's pre-idle,
Ramsey idle and pulse count must equal the member's design, and the dead
gaps between idles enter the model as scheduled.

--design OUT writes the design trade table; RUN_DIR writes
RUN_DIR/segmented-sweep.json and --check requires equal bytes. An analyzer
whose closure differs from the one the record binds writes its amended
analysis beside it as segmented-sweep-<closure digest>.json. The planted
truths live in tests/scripts/test_n21_q143_segmented_sweep.py.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.stats import chi2, norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import n21_orbit_rca as rca  # noqa: E402
import n21_q143_beat_model as beat  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "n21-q143-segmented-sweep-v1"
RETAINED = "segmented-sweep.json"
DT_US = 0.004
F0_MHZ = 1.0 / (836 * DT_US)
BAND_MHZ = 2.0
CELLS = tuple(range(-6, 7))
# The retained 836 dt sweep's residue classes (beat-model.json static fit):
# df = -90.00 kHz and f1 = 24.88 kHz modulo f0. They index alias cells only.
PRIOR_F1_MHZ = 0.02488
PRIOR_DF_MHZ = -0.0900
FAMILY_ALPHA = 0.05
TESTS = (
    "herald_admission",
    "segment_exchangeability",
    "herald_backaction",
    "alias_resolution",
    "model_decision",
    "z_memory",
)
MODELS = ("single", "static", "telegraph", "tls")
COMMON = ("amplitude", "t_us", "phi", "e0", "e1", "t1_us")
SPECIFIC = {
    "single": ("f1_mhz",),
    "static": ("a", "f1_mhz", "df_mhz"),
    "telegraph": ("a", "f1_mhz", "df_mhz", "gamma_per_us"),
    "tls": ("a", "f1_mhz", "df_mhz", "gamma_tls_per_us", "p0"),
}
ERROR_BOUNDS = (1e-5, 0.1)
T_BOUNDS = (1.0, 2000.0)
T1_BOUNDS = (5.0, 2000.0)
GAMMA_BOUNDS = (0.0, 50.0)
GAMMA_TLS_BOUNDS = (0.0, 10.0)
# Dead time between one idle's end and the next idle's start: basis change,
# readout, reset, herald and preparation at the Target durations of qubit
# 143 (measure 415 dt, reset 421 dt, single-qubit pulses 6 to 7 dt).
NOMINAL_GAP_DT = 13 + 415 + 421 + 415


def names(model: str) -> tuple[str, ...]:
    return COMMON + SPECIFIC[model]


def bounds(model: str, df_cell: int | None = None) -> list[tuple[float | None, float | None]]:
    common: list[tuple[float | None, float | None]] = [
        (0.0, 1.0),
        T_BOUNDS,
        (None, None),
        ERROR_BOUNDS,
        ERROR_BOUNDS,
        T1_BOUNDS,
    ]
    df: tuple[float | None, float | None] = (-BAND_MHZ, BAND_MHZ)
    if df_cell is not None:
        center = PRIOR_DF_MHZ + df_cell * F0_MHZ
        df = (center - F0_MHZ / 2.0, center + F0_MHZ / 2.0)
    frequency = (-BAND_MHZ, BAND_MHZ)
    specific: dict[str, list[tuple[float | None, float | None]]] = {
        "single": [frequency],
        "static": [(0.5, 1.0), frequency, df],
        "telegraph": [(0.5, 1.0), frequency, df, GAMMA_BOUNDS],
        "tls": [(0.5, 1.0), frequency, df, GAMMA_TLS_BOUNDS, (0.0, 1.0)],
    }
    return common + specific[model]


# Data ---------------------------------------------------------------------


class Point:
    """One member's shots: readout pattern per shot (0, 1, or -1 for a segment its herald refused) with counts."""

    def __init__(
        self,
        name: str,
        kind: str,
        delay_dt: int,
        pre_dt: int,
        bases: tuple[str, ...],
        gaps_dt: tuple[int, ...],
        patterns: np.ndarray,
        counts: np.ndarray,
    ) -> None:
        self.name = name
        self.kind = kind
        self.delay_dt = delay_dt
        self.pre_dt = pre_dt
        self.bases = bases
        self.gaps_dt = gaps_dt
        self.patterns = np.asarray(patterns, dtype=np.int64).reshape(-1, len(bases))
        self.counts = np.asarray(counts, dtype=float)

    @property
    def idle_us(self) -> float:
        return self.delay_dt * DT_US

    def with_counts(self, patterns: np.ndarray, counts: np.ndarray) -> Point:
        return Point(self.name, self.kind, self.delay_dt, self.pre_dt, self.bases, self.gaps_dt, patterns, counts)


def tally(shots: list[tuple[int, ...]]) -> tuple[np.ndarray, np.ndarray]:
    counted = sorted(Counter(shots).items())
    if not counted:
        return np.zeros((0, 0), dtype=np.int64), np.zeros(0)
    return np.array([key for key, _ in counted], dtype=np.int64), np.array([value for _, value in counted], float)


def primary(points: list[Point]) -> list[Point]:
    """The delay members (no pre-idle): xy whole, z through segment 1 alone."""
    chosen = []
    for point in points:
        if point.pre_dt:
            continue
        if point.kind == "z":
            first: Counter[tuple[int, ...]] = Counter()
            for pattern, count in zip(point.patterns, point.counts, strict=True):
                first[(int(pattern[0]),)] += count
            patterns = np.array(sorted(first), dtype=np.int64).reshape(-1, 1)
            counts = np.array([first[tuple(row)] for row in patterns.tolist()], dtype=float)
            chosen.append(Point(point.name, "z", point.delay_dt, 0, ("z",), (), patterns, counts))
        else:
            chosen.append(point)
    return chosen


def first_of_each_basis(point: Point) -> Point:
    """An xy member reduced to its first X and first Y segment, the fallback when segments are not exchangeable."""
    keep = [point.bases.index("x"), point.bases.index("y")]
    merged: Counter[tuple[int, ...]] = Counter()
    for pattern, count in zip(point.patterns, point.counts, strict=True):
        merged[tuple(int(pattern[k]) for k in keep)] += count
    patterns = np.array(sorted(merged), dtype=np.int64).reshape(-1, 2)
    counts = np.array([merged[tuple(row)] for row in patterns.tolist()], dtype=float)
    gap = point.gaps_dt[0] if point.gaps_dt else NOMINAL_GAP_DT
    return Point(point.name, point.kind, point.delay_dt, point.pre_dt, ("x", "y"), (gap,), patterns, counts)


# Models -------------------------------------------------------------------


def unpack(model: str, params: np.ndarray) -> dict[str, float]:
    values = dict(zip(names(model), (float(x) for x in params), strict=True))
    if model == "single":
        values |= {"a": 1.0, "df_mhz": 0.0}
    values.setdefault("gamma_per_us", 0.0)
    return values


def readout(mu: Any, values: dict[str, float]) -> Any:
    """Probability of reading 0 at true mean mu."""
    return 0.5 * (1.0 + (1.0 - values["e0"] - values["e1"]) * mu + (values["e1"] - values["e0"]))


def rates(values: dict[str, float]) -> np.ndarray:
    gamma, a = values["gamma_per_us"], values["a"]
    return np.array([[-gamma * (1.0 - a), gamma * a], [gamma * (1.0 - a), -gamma * a]])


def segment_operators(values: dict[str, float], basis: str, t_us: float) -> np.ndarray:
    """[O_0, O_1, P]: joint law of read 0 / read 1 / no read and the end line given the start line (columns)."""
    w = rates(values)
    f1, f2 = values["f1_mhz"], values["f1_mhz"] + values["df_mhz"]
    transition = expm(w * t_us)
    generator = np.diag([2j * math.pi * f1, 2j * math.pi * f2]) + w
    amplitude = values["amplitude"] * np.exp(1j * values["phi"] - t_us / values["t_us"])
    weighted = amplitude * expm(generator * t_us)
    mu = weighted.real if basis == "x" else weighted.imag
    zero = 0.5 * ((1.0 + values["e1"] - values["e0"]) * transition + (1.0 - values["e0"] - values["e1"]) * mu)
    return np.array([zero, transition - zero, transition])


def hmm_log_likelihood(values: dict[str, float], point: Point) -> np.ndarray:
    """log P(pattern) of every pattern of an xy member under the line chain (static at gamma = 0)."""
    w = rates(values)
    operators = [segment_operators(values, basis, point.idle_us) for basis in point.bases]
    gaps = [expm(w * gap * DT_US) for gap in point.gaps_dt]
    state = np.tile(np.array([values["a"], 1.0 - values["a"]]), (point.patterns.shape[0], 1))
    for s in range(len(point.bases)):
        index = np.where(point.patterns[:, s] < 0, 2, point.patterns[:, s])
        state = np.einsum("nij,nj->ni", operators[s][index], state)
        if s < len(point.bases) - 1:
            state = state @ gaps[s].T
    total = state.sum(axis=1)
    with np.errstate(divide="ignore"):
        return np.asarray(np.log(np.clip(total, 0.0, None)))


def tls_values(values: dict[str, float]) -> tuple[float, float, float]:
    return beat.tls_hamiltonian(values["a"], values["f1_mhz"], values["df_mhz"])


def tls_means(values: dict[str, float], points: list[Point]) -> dict[tuple[str, int], complex]:
    """tls Ramsey coherence (TLS population 0, which cancels) and <Z> at p0 of every member's idle, one call each."""
    fq, ft, coupling = tls_values(values)
    found: dict[tuple[str, int], complex] = {}
    for kind, basis, population in (("xy", "ramsey", 0.0), ("z", "z", values["p0"])):
        delays = sorted({point.delay_dt for point in points if point.kind == kind})
        if not delays:
            continue
        signal = beat.tls_signal(
            fq,
            ft,
            coupling,
            values["t_us"],
            values["t1_us"],
            values["gamma_tls_per_us"],
            population,
            np.array(delays) * DT_US,
            basis=basis,
        )
        scale = values["amplitude"] * np.exp(1j * values["phi"]) if kind == "xy" else 1.0
        found |= {(kind, delay): complex(scale * value) for delay, value in zip(delays, signal, strict=True)}
    return found


def z_mean(values: dict[str, float], t_us: float) -> float:
    """<Z> after the X preparation under the line models: T1 decay."""
    return 1.0 - 2.0 * math.exp(-t_us / values["t1_us"])


def independent_log_likelihood(
    model: str, values: dict[str, float], point: Point, cache: dict[tuple[str, int], complex] | None = None
) -> np.ndarray:
    """log P(pattern) with independent segments: tls X and Y, and every model's Z segment 1."""
    if model == "tls":
        signal = (cache if cache is not None else tls_means(values, [point]))[(point.kind, point.delay_dt)]
        means = {"z": signal.real} if point.kind == "z" else {"x": signal.real, "y": signal.imag}
    else:
        means = {"z": z_mean(values, point.idle_us)}
    total = np.zeros(point.patterns.shape[0])
    for s, basis in enumerate(point.bases):
        zero = float(readout(means[basis], values))
        if not 0.0 < zero < 1.0:
            return np.full(point.patterns.shape[0], -np.inf)
        column = point.patterns[:, s]
        total += np.where(column == 0, math.log(zero), np.where(column == 1, math.log1p(-zero), 0.0))
    return total


def point_log_likelihood(
    model: str, values: dict[str, float], point: Point, cache: dict[tuple[str, int], complex] | None = None
) -> np.ndarray:
    if point.kind == "z" or model == "tls":
        return independent_log_likelihood(model, values, point, cache)
    return hmm_log_likelihood(values, point)


def negative_log_likelihood(params: np.ndarray, model: str, points: list[Point]) -> float:
    values = unpack(model, params)
    cache = tls_means(values, points) if model == "tls" else None
    total = 0.0
    for point in points:
        logs = point_log_likelihood(model, values, point, cache)
        weighted = point.counts * logs
        if not np.all(np.isfinite(weighted[point.counts > 0])):
            return 1e18
        total -= float(weighted[point.counts > 0].sum())
    return total


def pattern_probabilities(model: str, values: dict[str, float], point: Point) -> tuple[np.ndarray, np.ndarray]:
    """Every full pattern of a member (no refused segment) and its probability under a model."""
    size = len(point.bases)
    patterns = np.array([[(k >> s) & 1 for s in range(size)] for k in range(1 << size)], dtype=np.int64)
    probe = point.with_counts(patterns, np.ones(len(patterns)))
    return patterns, np.exp(point_log_likelihood(model, values, probe))


# Fitting ------------------------------------------------------------------


class Fit:
    """Bounded L-BFGS-B fit of one model from one start; pool-picklable."""

    def __call__(self, item: tuple[str, list[float], list[Point], int | None]) -> tuple[float, list[float]]:
        model, start, points, cell = item
        limits = bounds(model, cell)
        clipped = [
            min(max(value, low if low is not None else -math.inf), high if high is not None else math.inf)
            for value, (low, high) in zip(start, limits, strict=True)
        ]
        result = minimize(
            negative_log_likelihood,
            np.array(clipped, dtype=float),
            args=(model, points),
            method="L-BFGS-B",
            bounds=limits,
            options={"maxiter": 2000, "ftol": 1e-12, "gtol": 1e-8},
        )
        best, params = float(result.fun), np.asarray(result.x)
        return best, [float(x) for x in params]


def cell_center(cell: int) -> float:
    return PRIOR_DF_MHZ + cell * F0_MHZ


def static_start(f1: float, df: float) -> list[float]:
    return [0.98, 130.0, 0.0, 0.005, 0.01, 110.0, 0.64, f1, df]


def extend(model: str, static: list[float]) -> list[float]:
    common, a, f1, df = static[:6], static[6], static[7], static[8]
    if model == "single":
        return [*common, f1]
    if model == "telegraph":
        return [*common, a, f1, df, 0.01]
    if model == "tls":
        return [*common, a, f1, df, 0.02, 0.0]
    return [*common, a, f1, df]


def f1_starts() -> list[float]:
    return [PRIOR_F1_MHZ + m * F0_MHZ for m in CELLS if abs(PRIOR_F1_MHZ + m * F0_MHZ) <= BAND_MHZ]


def cell_fits(points: list[Point], model: str = "static") -> dict[int, tuple[float, list[float]]]:
    """Per df alias cell, the best fit with df inside the cell over every f1 cell start."""
    items = [
        (model, extend(model, static_start(f1, cell_center(cell))), points, cell)
        for cell in CELLS
        for f1 in f1_starts()
    ]
    found = parallel.ordered_map(Fit(), items, min_items=2)
    best: dict[int, tuple[float, list[float]]] = {}
    for (_model, _start, _points, cell), result in zip(items, found, strict=True):
        if cell is not None and (cell not in best or result[0] < best[cell][0]):
            best[cell] = result
    return best


def model_fits(points: list[Point], static_cells: dict[int, tuple[float, list[float]]]) -> dict[str, Any]:
    """Every model at the static fit's best cell (single from every f1 start)."""
    cell = min(static_cells, key=lambda key: static_cells[key][0])
    static = static_cells[cell]
    items: list[tuple[str, list[float], list[Point], int | None]] = [
        ("single", extend("single", static_start(f1, 0.0)), points, None) for f1 in f1_starts()
    ]
    items += [("telegraph", extend("telegraph", static[1][:6] + static[1][6:]), points, cell)]
    for gamma in (0.002, 0.03, 0.3):
        start = [*static[1], gamma]
        items.append(("telegraph", start, points, cell))
    for p0 in (0.0, 0.5, 0.95):
        items.append(("tls", [*static[1], 0.02, p0], points, cell))
    found = parallel.ordered_map(Fit(), items, min_items=2)
    fits: dict[str, tuple[float, list[float]]] = {"static": static}
    for (model, _start, _points, _cell), result in zip(items, found, strict=True):
        if model not in fits or result[0] < fits[model][0]:
            fits[model] = result
    return {"cell": cell, "fits": fits}


# Tests --------------------------------------------------------------------


def shot_statistic(point: Point, positions: list[int], references: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    """Per kept shot, read(first) - mean(read(later)) for each (first, later) position set; rows of shots."""
    rows = []
    weights = []
    for pattern, count in zip(point.patterns, point.counts, strict=True):
        vector = []
        for first, later in zip(positions, references, strict=True):
            kept = [int(pattern[k]) for k in later if pattern[k] >= 0]
            if pattern[first] < 0 or not kept:
                break
            vector.append(int(pattern[first]) - sum(kept) / len(kept))
        else:
            rows.append(vector)
            weights.append(count)
    return np.array(rows, dtype=float).reshape(-1, len(positions)), np.array(weights, dtype=float)


def mean_and_covariance(rows: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Weighted mean of shot rows and the covariance of that mean."""
    total = weights.sum()
    mean = weights @ rows / total
    centered = rows - mean
    return mean, (centered * weights[:, None]).T @ centered / (total - 1.0) / total


def mean_test(rows: np.ndarray, weights: np.ndarray) -> tuple[float, int]:
    """Wald chi-square of a zero mean vector from weighted shot rows; (statistic, degrees of freedom)."""
    size = rows.shape[1]
    if weights.sum() < size + 2:
        return 0.0, 0
    mean, covariance = mean_and_covariance(rows, weights)
    if np.linalg.matrix_rank(covariance) < size:
        return (0.0, 0) if np.allclose(mean, 0.0) else (math.inf, size)
    return float(mean @ np.linalg.solve(covariance, mean)), size


def exchangeability(points: list[Point], alpha: float) -> dict[str, Any]:
    """Each xy member's first X and first Y read against the mean of its later X and Y reads (Wald, per shot)."""
    statistic, freedom = 0.0, 0
    for point in points:
        if point.kind != "xy" or point.pre_dt or len(point.bases) < 4:
            continue
        xs = [k for k, basis in enumerate(point.bases) if basis == "x"]
        ys = [k for k, basis in enumerate(point.bases) if basis == "y"]
        value, df = mean_test(*shot_statistic(point, [xs[0], ys[0]], [xs[1:], ys[1:]]))
        statistic += value
        freedom += df
    return verdict("exchangeable", "not_exchangeable", statistic, freedom, alpha)


def z_memory(points: list[Point], alpha: float) -> dict[str, Any]:
    """Each z member's segment-1 read against the mean of its later reads; a TLS swap memory moves it."""
    statistic, freedom = 0.0, 0
    for point in points:
        if point.kind != "z" or point.pre_dt or len(point.bases) < 2:
            continue
        value, df = mean_test(*shot_statistic(point, [0], [list(range(1, len(point.bases)))]))
        statistic += value
        freedom += df
    return verdict("no_memory", "memory", statistic, freedom, alpha)


def shot_means(point: Point, bases: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Per shot that keeps a read of every basis, the mean of its kept reads in each; rows of shots."""
    positions = [[k for k, b in enumerate(point.bases) if b == basis] for basis in bases]
    rows = []
    weights = []
    for pattern, count in zip(point.patterns, point.counts, strict=True):
        kept = [[int(pattern[k]) for k in where if pattern[k] >= 0] for where in positions]
        if all(kept):
            rows.append([sum(values) / len(values) for values in kept])
            weights.append(count)
    return np.array(rows, dtype=float).reshape(-1, len(bases)), np.array(weights, dtype=float)


def backaction(points: list[Point], alpha: float) -> dict[str, Any]:
    """Each pre-idle control against the delay member of its delay: Wald test of the per-shot X and Y means.

    The shot is the unit: a frequency line fixed within a shot correlates
    its X and Y segments, so the test reads the full covariance of the two
    quadrature means of each member, and the members' shots are independent.
    """
    by_delay = {(p.kind, p.delay_dt): p for p in points if not p.pre_dt}
    statistic, freedom, pairs = 0.0, 0, []
    for control in (p for p in points if p.pre_dt):
        reference = by_delay.get((control.kind, control.delay_dt))
        if reference is None:
            raise RuntimeError(f"{control.name} has no delay member at {control.delay_dt} dt")
        pairs.append([control.name, reference.name])
        bases = sorted(set(control.bases))
        summaries = []
        for point in (control, reference):
            rows, weights = shot_means(point, bases)
            if weights.sum() < len(bases) + 2:
                return {
                    "status": "not_evaluable",
                    "reason": f"{point.name} keeps {weights.sum():.0f} shots with a read of every basis",
                    "pairs": pairs,
                }
            summaries.append(mean_and_covariance(rows, weights))
        (m1, c1), (m2, c2) = summaries
        difference = m1 - m2
        covariance = c1 + c2
        if np.linalg.matrix_rank(covariance) < len(bases):
            statistic += 0.0 if np.allclose(difference, 0.0) else math.inf
        else:
            statistic += float(difference @ np.linalg.solve(covariance, difference))
        freedom += len(bases)
    return verdict("no_backaction", "backaction", statistic, freedom, alpha) | {"pairs": pairs}


def verdict(null: str, alternative: str, statistic: float, freedom: int, alpha: float) -> dict[str, Any]:
    if freedom == 0:
        return {"status": "not_evaluable", "reason": "no member carries the comparison"}
    critical = float(chi2.ppf(1.0 - alpha, freedom))
    return {
        "status": alternative if statistic > critical else null,
        "statistic": statistic,
        "degrees_of_freedom": freedom,
        "critical": critical,
        "alpha": alpha,
    }


def alias_resolution(cells: dict[int, tuple[float, list[float]]], alpha: float) -> dict[str, Any]:
    ordered = sorted(cells, key=lambda cell: cells[cell][0])
    best, second = ordered[0], ordered[1]
    margin = cells[second][0] - cells[best][0]
    threshold = math.log(1.0 / alpha)
    return {
        "status": "resolved" if margin > threshold else "unresolved",
        "cell": best,
        "df_mhz": cells[best][1][8],
        "second_cell": second,
        "delta_nll_second": margin,
        "threshold_log_inverse_alpha": threshold,
        "cells": {str(cell): {"nll": cells[cell][0], "df_mhz": cells[cell][1][8]} for cell in CELLS},
    }


def model_decision(fits: dict[str, tuple[float, list[float]]], alpha: float) -> dict[str, Any]:
    """Line mixture (static or telegraph, whichever is lower) against tls by log(1 / alpha)."""
    threshold = math.log(1.0 / alpha)
    line = min(fits["static"][0], fits["telegraph"][0])
    tls = fits["tls"][0]
    status = "tls" if line - tls > threshold else "line_mixture" if tls - line > threshold else "undecided"
    return {
        "status": status,
        "nll_line_mixture_minus_tls": line - tls,
        "threshold_log_inverse_alpha": threshold,
        "telegraph_minus_static": fits["telegraph"][0] - fits["static"][0],
        "single_minus_static": fits["single"][0] - fits["static"][0],
    }


# Run reading --------------------------------------------------------------


def register_of(circuit: Any, suffix: str) -> Any:
    found = [register for register in circuit.cregs if register.name.endswith(suffix)]
    if len(found) != 1:
        raise RuntimeError(f"{circuit.name}: {len(found)} registers end with {suffix}")
    return found[0]


def spectator_stages(payload: dict[str, Any], qubit: int) -> list[tuple[int, list[tuple[int, int, str]]]]:
    """The qubit's scheduled stages: each barrier's time with the drive plays up to the next barrier.

    Every play row of the returned scheduler table carries its instruction's
    label (measure_Q, reset_Q, sx_Q); a measure or reset plays several
    contiguous rows, and a measure's acquisition runs past its last drive
    play to the next barrier. INIT and FINI rows bracket the program: an
    INIT row discards the stages before it, a barrier among them included,
    and the first FINI row ends the program. An absent or malformed table
    raises ValueError.
    """
    try:
        timing = payload["metadata"]["compilation"]["scheduler_timing"]["timing"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"scheduler timing is unavailable: {error}") from error
    stages: list[tuple[int, list[tuple[int, int, str]]]] = []
    for line in timing.splitlines():
        row = line.split(",")
        if len(row) < 6:
            raise ValueError("scheduler timing table is malformed")
        if row[2] != f"Qubit {qubit}":
            continue
        if row[1].startswith("INIT"):
            stages = []
            continue
        if row[1].startswith("FINI"):
            break
        start = int(row[3])
        if row[5] == "barrier":
            if not stages or stages[-1][1] or stages[-1][0] != start:
                stages.append((start, []))
        elif row[5] == "play":
            if not stages:
                stages.append((start, []))
            stages[-1][1].append((start, int(row[4]), row[1].split("_")[0]))
    return stages


def schedule_items(stages: list[tuple[int, list[tuple[int, int, str]]]]) -> list[tuple[str, int, int]]:
    """(label, start, end) per scheduled instruction, and ("idle", start, end) per stage without plays.

    Rows of one measure or reset within a stage merge into one instruction;
    adjacent idle stages merge into one idle.
    """
    items: list[tuple[str, int, int]] = []
    for k, (start, plays) in enumerate(stages):
        if not plays:
            if k + 1 < len(stages):
                if items and items[-1][0] == "idle" and items[-1][2] == start:
                    items[-1] = ("idle", items[-1][1], stages[k + 1][0])
                else:
                    items.append(("idle", start, stages[k + 1][0]))
            continue
        first = len(items)
        for play_start, length, label in plays:
            if len(items) > first and items[-1][0] == label and label in ("measure", "reset"):
                items[-1] = (label, items[-1][1], play_start + length)
            else:
                items.append((label, play_start, play_start + length))
    return items


def member_schedule(stages: list[tuple[int, list[tuple[int, int, str]]]], segments: int) -> dict[str, Any]:
    """Per segment the spectator's scheduled pre-idle, Ramsey idle and pulse count, with the dead gaps.

    A segment plays [reset,] herald measure, [pre-idle,] preparation pulse,
    [idle,] basis-change pulse (none for Z) and readout measure. The Ramsey
    idle starts at the item after the preparation, and a gap runs from one
    idle's end to the next idle's start.
    """
    items = schedule_items(stages)
    position = 0

    def take(*labels: str) -> tuple[str, int, int] | None:
        nonlocal position
        if position < len(items) and items[position][0] in labels:
            position += 1
            return items[position - 1]
        return None

    def take_pulse() -> tuple[str, int, int] | None:
        nonlocal position
        if position < len(items) and items[position][0] not in ("measure", "reset", "idle"):
            position += 1
            return items[position - 1]
        return None

    found = []
    for s in range(segments):
        if s and take("reset") is None:
            raise ValueError(f"segment {s + 1} opens without a reset")
        if take("measure") is None:
            raise ValueError(f"segment {s + 1} plays no herald readout")
        pre = take("idle")
        prep = take_pulse()
        if prep is None:
            raise ValueError(f"segment {s + 1} plays no preparation")
        idle_start = items[position][1] if position < len(items) else prep[2]
        idle = take("idle")
        pulses = 1
        while take_pulse() is not None:
            pulses += 1
        if take("measure") is None:
            raise ValueError(f"segment {s + 1} plays no readout")
        found.append((pre[2] - pre[1] if pre else 0, idle_start, idle[2] - idle[1] if idle else 0, pulses))
    # The spectator idles after its last readout until the other qubits finish.
    take("idle")
    if position != len(items):
        raise ValueError(f"the spectator plays {len(items) - position} instructions past segment {segments}")
    return {
        "pre_dt": [entry[0] for entry in found],
        "idle_dt": [entry[2] for entry in found],
        "pulses": [entry[3] for entry in found],
        "gaps_dt": [found[s + 1][1] - (found[s][1] + found[s][2]) for s in range(segments - 1)],
    }


def member_shots(circuit: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """One member's registers and, per shot in shot order, its segment pattern or None.

    A pattern holds per segment 0, 1, or -1 for a segment the spectator's
    herald refused; a shot whose segment-1 herald reads any neighbor excited
    is None. The spectator is the qubit every segment read is written from.
    """
    segments = sum(1 for register in circuit.cregs if register.name.endswith("_read"))
    writer = {
        circuit.find_bit(i.clbits[0]).index: circuit.find_bit(i.qubits[0]).index
        for i in circuit.data
        if i.operation.name == "measure"
    }
    reads = [register_of(circuit, f"s{s + 1}_read") for s in range(segments)]
    heralds = [register_of(circuit, f"s{s + 1}_herald") for s in range(segments)]
    spectators = {writer[circuit.find_bit(register[0]).index] for register in reads}
    if len(spectators) != 1:
        raise RuntimeError(f"{circuit.name} reads qubits {sorted(spectators)}")
    (spectator,) = spectators
    first = heralds[0]
    first_qubits = [writer[circuit.find_bit(bit).index] for bit in first]
    own_bit = first.size - 1 - first_qubits.index(spectator)
    strings = {r.name: payload["registers"][r.name]["bitstrings"] for r in (*reads, *heralds)}
    patterns: list[tuple[int, ...] | None] = []
    for shot in range(len(strings[reads[0].name])):
        initial = strings[first.name][shot]
        if any(initial[first.size - 1 - k] == "1" for k, qubit in enumerate(first_qubits) if qubit != spectator):
            patterns.append(None)
            continue
        pattern = []
        for s in range(segments):
            herald = strings[heralds[s].name][shot]
            spectator_bit = herald[own_bit] if s == 0 else herald[0]
            pattern.append(-1 if spectator_bit == "1" else int(strings[reads[s].name][shot][0]))
        patterns.append(tuple(pattern))
    return {
        "segments": segments,
        "spectator": spectator,
        "first": first,
        "first_qubits": first_qubits,
        "heralds": heralds,
        "strings": strings,
        "patterns": patterns,
    }


def run_points(run: Path) -> tuple[list[Point], dict[str, Any], dict[int, dict[str, Any]]]:
    """Points from the raw shots, the schedule admissibility and per-segment herald bit counts.

    The spectator is the qubit every member reads its segments on, the
    record's pinned layout placing it.
    """
    from qpe_diagnostics import n21_segment_bases, n21_segmented_key

    members = [member["name"] for member in rca._group(run)["members"]]
    points: list[Point] = []
    schedules: dict[str, Any] = {}
    bit_counts: dict[int, dict[str, Any]] = {}
    differing: dict[str, Any] = {}
    spectator: int | None = None
    for name, circuit, payload in zip(members, rca._circuits(run), rca.raw_pubs(run), strict=True):
        key = n21_segmented_key(name)
        if key is None:
            raise RuntimeError(f"{run}: member {name} is not a segmented sweep arm")
        kind, delay, pre = key
        shot = member_shots(circuit, payload)
        segments, strings, first = shot["segments"], shot["strings"], shot["first"]
        first_qubits, heralds = shot["first_qubits"], shot["heralds"]
        bases = n21_segment_bases(kind, segments)
        if spectator is not None and shot["spectator"] != spectator:
            raise RuntimeError(f"{name} reads qubit {shot['spectator']}, the run's spectator is {spectator}")
        spectator = shot["spectator"]
        patterns = [pattern for pattern in shot["patterns"] if pattern is not None]
        # Herald bit counts: bit k of segment 1 per qubit among shots whose
        # other segment-1 bits read 0; key first.size + s - 1, the spectator's
        # reset herald of segment s + 1.
        for k, qubit in enumerate(first_qubits):
            others = [
                value
                for value in strings[first.name]
                if all(value[first.size - 1 - j] == "0" for j in range(first.size) if j != k)
            ]
            entry = bit_counts.setdefault(k, {"qubit": qubit, "segment": 1, "members": {}})
            entry["members"][name] = (sum(value[first.size - 1 - k] == "1" for value in others), len(others))
        for s in range(1, segments):
            values = strings[heralds[s].name]
            entry = bit_counts.setdefault(first.size + s - 1, {"qubit": spectator, "segment": s + 1, "members": {}})
            entry["members"][name] = (sum(value == "1" for value in values), len(values))
        try:
            schedule = member_schedule(spectator_stages(payload, spectator), segments)
        except ValueError as error:
            differing[name] = {"reason": str(error)}
            continue
        schedules[name] = schedule
        expected_pulses = [1 if basis == "z" else 2 for basis in bases]
        if (
            schedule["idle_dt"] != [delay] * segments
            or schedule["pre_dt"] != [pre] * segments
            or schedule["pulses"] != expected_pulses
        ):
            differing[name] = {
                "expected_idle_dt": delay,
                "expected_pre_dt": pre,
                "expected_pulses": expected_pulses,
                "found": schedule,
            }
        patterns_array, counts = tally(patterns)
        points.append(Point(name, kind, delay, pre, bases, tuple(schedule["gaps_dt"]), patterns_array, counts))
    admitted = {"admissible": not differing, "spectator": spectator, "differing": differing, "schedules": schedules}
    return points, admitted, bit_counts


def herald_bound(shots: int, bits: int, alpha: float) -> float:
    """Largest member spread B of the undetected excitation on every herald bit that the admission accepts.

    An undetected excitation u, one its herald bit reads as 0, mixes u of
    another law into the segments it precedes, moving each segment's readout
    probability by at most u. A segment follows bits herald bits (the segment-1
    register, or the neighbors' segment-1 bits with the spectator's reset
    herald), so a spread B on each moves a member difference of readout
    probabilities by at most bits x B. The binomial standard error of one
    readout probability is at most 1 / (2 sqrt(shots)), and the one-sided
    level-alpha test detects with power rca.MAGNITUDE_POWER the deficit
    (z_(1 - alpha) + z_power) / (2 sqrt(shots)); B holds the shift at
    rca.HERALD_MDE_FRACTION of that deficit.
    """
    deficit = float(norm.ppf(1 - alpha) + norm.ppf(rca.MAGNITUDE_POWER)) / (2 * math.sqrt(shots))
    return rca.HERALD_MDE_FRACTION * deficit / bits


def herald_evaluation(
    counts: dict[int, dict[str, Any]], calibrations: dict[str, dict[str, Any]], alpha: float
) -> dict[str, Any]:
    """Whether the heralds refute a member spread of the undetected excitation at most herald_bound on any bit.

    Each herald qubit reads through the assignment channel (prob_meas1_prep0,
    prob_meas0_prep1) of the members' calibration, and a difference of two
    members' rates is their excitation difference times the readout
    contrast r = 1 - p01 - p10 when the members share that channel; a
    differing or unretained channel leaves the heralds not evaluable. A
    shot or segment whose herald reads 1 leaves the data, so an excitation
    eps enters it undetected as eps p01, and a member spread of eps moves
    the data by p01 times that spread. The excitation itself differs by
    design: a reset leaves an excitation that grows with the population
    before it, which a Z member holds near 1. Every ordered member pair on
    every bit gets the Agresti-Caffo interval of p_i - p_j (Agresti and
    Caffo, The American Statistician 54, 280 (2000)) at one-sided level
    alpha / K over the K comparisons, and the run is admissible unless a
    lower limit exceeds the bound times r / p01.
    """
    shots = min(n for entry in counts.values() for _excited, n in entry["members"].values())
    if shots == 0:
        empty = sorted({name for entry in counts.values() for name, (_e, n) in entry["members"].items() if n == 0})
        return {"evaluable": False, "admissible": False, "reason": f"members {empty} keep no herald shot"}
    contrasts: dict[int, float] = {}
    undetected: dict[int, float] = {}
    differing: dict[str, Any] = {}
    for entry in counts.values():
        qubit = entry["qubit"]
        values = {name: calibrations[name]["values"].get(str(qubit), {}) for name in entry["members"]}
        channels = {name: (item.get("prob_meas1_prep0"), item.get("prob_meas0_prep1")) for name, item in values.items()}
        if len(set(channels.values())) > 1 or None in next(iter(channels.values())):
            differing[str(qubit)] = {
                name: {"channel": list(channel), "source": calibrations[name]["source"]}
                for name, channel in channels.items()
            }
            continue
        ((p10, p01),) = set(channels.values())
        contrasts[qubit] = 1 - float(p10) - float(p01)
        undetected[qubit] = float(p01)
    if differing:
        return {
            "evaluable": False,
            "admissible": False,
            "reason": "the members read a herald qubit through differing or unretained assignment channels",
            "differing_channels": differing,
        }
    first_size = sum(1 for entry in counts.values() if entry["segment"] == 1)
    bound = herald_bound(shots, first_size, alpha)
    pairs = sum(len(entry["members"]) * (len(entry["members"]) - 1) for entry in counts.values())
    quantile = float(norm.ppf(1 - alpha / max(1, pairs)))
    bits: dict[str, Any] = {}
    refuted = False
    for k, entry in sorted(counts.items()):
        contrast = contrasts[entry["qubit"]]
        p01 = undetected[entry["qubit"]]
        threshold = bound * contrast / p01 if p01 else math.inf
        adjusted = [((excited + 1) / (n + 2), n + 2) for excited, n in entry["members"].values()]
        lower, upper = -math.inf, 0.0
        for i, (p_first, n_first) in enumerate(adjusted):
            for j, (p_second, n_second) in enumerate(adjusted):
                if i == j:
                    continue
                error = math.sqrt(p_first * (1 - p_first) / n_first + p_second * (1 - p_second) / n_second)
                lower = max(lower, p_first - p_second - quantile * error)
                upper = max(upper, p_first - p_second + quantile * error)
        fails = lower > threshold
        refuted |= fails
        rates = [excited / n for excited, n in entry["members"].values()]
        bits[str(k)] = {
            "qubit": entry["qubit"],
            "segment": entry["segment"],
            "spread": max(rates) - min(rates),
            "readout_contrast": contrast,
            "prob_meas0_prep1": p01,
            "threshold": threshold,
            "spread_lower_limit": lower,
            "excitation_spread_upper_limit": upper / contrast,
            "undetected_spread_upper_limit": upper * p01 / contrast,
            "status": "fail" if fails else "pass",
        }
    return {
        "evaluable": True,
        "admissible": not refuted,
        "shots": shots,
        "excitation_spread_bound": bound,
        "comparisons": pairs,
        "one_sided_quantile": quantile,
        "bits": bits,
    }


def closure_mismatch(design: dict[str, Any], own: dict[str, Any]) -> str | None:
    bound = design.get("segmented_analyzer_closure")
    if not isinstance(bound, dict):
        return "the record's policy.design binds no segmented_analyzer_closure"
    if bound != own:
        return "the analyzer closure differs from the approved one"
    return None


def analyze(points: list[Point], family_alpha: float) -> dict[str, Any]:
    """Every test after admission, on points already read."""
    alpha = family_alpha / len(TESTS)
    output: dict[str, Any] = {}
    output["segment_exchangeability"] = exchangeability(points, alpha)
    fallback = output["segment_exchangeability"]["status"] == "not_exchangeable"
    data = primary(points)
    if fallback:
        data = [first_of_each_basis(point) if point.kind == "xy" else point for point in data]
    output["primary_data"] = "first X and first Y segment per shot" if fallback else "every X and Y segment"
    output["herald_backaction"] = backaction(points, alpha)
    output["z_memory"] = z_memory(points, alpha)
    cells = cell_fits(data)
    output["alias_resolution"] = alias_resolution(cells, alpha)
    fitted = model_fits(data, cells)
    output["model_decision"] = model_decision(fitted["fits"], alpha)
    output["fits"] = {
        model: {"nll": value, "parameters": dict(zip(names(model), params, strict=True))}
        for model, (value, params) in sorted(fitted["fits"].items())
    }
    return output


def report(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    design = record.get("policy", {}).get("design", {})
    from qpu_planning import segmented_analyzer_closure

    own = segmented_analyzer_closure()
    mismatch = closure_mismatch(design, own)
    family_alpha = float(design["alpha"])
    alpha = family_alpha / len(TESTS)
    points, admitted, bit_counts = run_points(run)
    output: dict[str, Any] = {
        "schema_version": SCHEMA,
        "analyzer_closure": own,
        "preregistered": mismatch is None,
        "amendment": mismatch,
        "alpha": {"family_alpha": family_alpha, "tests": list(TESTS), "per_test_alpha": alpha},
        "admissibility": admitted,
        "kept": {p.name: {"shots": float(p.counts.sum()), "patterns": len(p.counts)} for p in points},
    }
    herald = herald_evaluation(bit_counts, rca.execution_calibration(run), alpha)
    output["herald_admission"] = herald
    if not admitted["admissible"] or not herald["admissible"]:
        output["status"] = "not_admissible"
        return output
    return output | analyze(points, family_alpha)


# Design -------------------------------------------------------------------

DESIGN_DELAYS = tuple(sorted({step * k for step, count in ((693, 12), (819, 10)) for k in range(count + 1)}))
BACKACTION_DELAYS = (0, 693)
BACKACTION_PRE_DT = 1250
REP_DELAY_US = 50.0
JOB_OVERHEAD_S = 2.3
INIT_FINI_US = 8.85
# Execution per shot: rep_delay + circuit_duration, with circuit_duration
# INIT (875 dt) + program + FINI (842 dt) on the retained schedule; the
# retained run's charge added 2.62 s to circuits_execution_time.
INIT_DT = 875
FINI_DT = 842
CHARGE_OFFSET_S = 2.62
KEPT_FIRST = 0.983
KEPT_LATER = 0.99


# (segments, shots, alias pairs): the uniform one-segment reference and the
# chosen design score every ordered alias pair; the others score truth cell 0.
DESIGN_TABLE = (
    (1, 2048, "all"),
    (2, 2048, "truth_cell_0"),
    (4, 1536, "truth_cell_0"),
    (6, 1024, "truth_cell_0"),
    (6, 1536, "all"),
)
DESIGN_SEGMENTS = 6
DESIGN_SHOTS = 1536


def design_points(segments: int, shots: int, backaction: bool = True) -> list[Point]:
    from qpe_diagnostics import n21_segment_bases

    chosen = []
    for kind in ("xy", "z"):
        size = 1 if segments == 1 else segments
        bases = ("x",) if size == 1 and kind == "xy" else n21_segment_bases(kind, size) if size > 1 else ("z",)
        for delay in DESIGN_DELAYS:
            if size == 1 and kind == "xy":
                for basis in ("x", "y"):
                    chosen.append(
                        Point(f"{basis}_d{delay}", "xy", delay, 0, (basis,), (), np.zeros((0, 1)), np.zeros(0))
                    )
                continue
            chosen.append(
                Point(
                    f"{kind}_d{delay}",
                    kind,
                    delay,
                    0,
                    bases,
                    (NOMINAL_GAP_DT,) * (size - 1),
                    np.zeros((0, size)),
                    np.zeros(0),
                )
            )
    if backaction and segments > 1:
        for delay in BACKACTION_DELAYS:
            bases = n21_segment_bases("xy", segments)
            chosen.append(
                Point(
                    f"xy_d{delay}_pre",
                    "xy",
                    delay,
                    BACKACTION_PRE_DT,
                    bases,
                    (NOMINAL_GAP_DT,) * (segments - 1),
                    np.zeros((0, segments)),
                    np.zeros(0),
                )
            )
    for point in chosen:
        point.counts = np.array([float(shots)])
    return chosen


def design_cost(points: list[Point], shots: int) -> dict[str, float]:
    circuit = 0.0
    for point in points:
        k = len(point.bases)
        program = (415 + 13 + point.delay_dt + 415 + point.pre_dt) + (k - 1) * (
            421 + 415 + 13 + point.delay_dt + 415 + point.pre_dt
        )
        if k == 1:
            program += 421
        circuit += shots * (REP_DELAY_US + (INIT_DT + program + FINI_DT) * DT_US)
    execution = circuit * 1e-6
    return {
        "execution_s": execution,
        "charge_estimate_s": execution + CHARGE_OFFSET_S,
        "rule_s": JOB_OVERHEAD_S + execution + len(points) * shots * INIT_FINI_US * 1e-6,
    }


def asimov(model: str, params: list[float], points: list[Point]) -> list[Point]:
    """Expected pattern counts: kept shots times each full pattern's probability."""
    values = unpack(model, np.array(params))
    expected = []
    for point in points:
        if point.pre_dt:
            continue
        if point.kind == "z":
            point = Point(point.name, "z", point.delay_dt, 0, ("z",), (), np.zeros((0, 1)), point.counts)
        patterns, probability = pattern_probabilities(model, values, point)
        size = len(point.bases)
        kept = KEPT_FIRST * (KEPT_LATER ** (size - 1))
        expected.append(point.with_counts(patterns, float(point.counts[0]) * kept * probability))
    return expected


class ExpectedLLR:
    """Alternative's minimum NLL minus the truth's NLL on the truth's expected counts; pool-picklable."""

    def __call__(self, item: tuple[str, list[float], str, list[float], int | None, list[Point]]) -> float:
        truth_model, truth, alternative, start, cell, points = item
        expected = asimov(truth_model, truth, points)
        own = negative_log_likelihood(np.array(truth), truth_model, expected)
        return Fit()((alternative, start, expected, cell))[0] - own


# The retained static fit (beat-model.json) at alias cell 0, with T1 of 143
# at that run's execution calibration and the TLS reading of the same alias.
TRUTH_STATIC = [1.0, 134.2, -0.0294, 0.0020, 0.0080, 112.0, 0.6438, 0.02488, -0.0900]


def design_rows(segments: int, shots: int, pairs: str = "all") -> dict[str, Any]:
    points = design_points(segments, shots)
    # One pool item per (comparison, optimizer start); a comparison's
    # expected LLR is its starts' least excess NLL, floored at 0.
    items: list[tuple[str, list[float], str, list[float], int | None, list[Point]]] = []
    labels: list[str] = []
    truths = CELLS if pairs == "all" else (0,)
    for truth_cell in truths:
        truth = TRUTH_STATIC[:8] + [cell_center(truth_cell)]
        for other in CELLS:
            if other != truth_cell:
                start = TRUTH_STATIC[:8] + [cell_center(other)]
                items.append(("static", truth, "static", start, other, points))
                labels.append(f"alias:{truth_cell}:{other}")
    for p0 in (0.0, 0.5, 1.0):
        tls_truth = extend("tls", TRUTH_STATIC)
        tls_truth[-1] = p0
        items.append(("tls", tls_truth, "static", TRUTH_STATIC, 0, points))
        labels.append(f"tls_truth_p0:{p0}")
    for p0 in (0.0, 0.5, 1.0):
        items.append(("static", TRUTH_STATIC, "tls", extend("tls", TRUTH_STATIC)[:-1] + [p0], 0, points))
        labels.append("static_truth_vs_tls")
    for gamma in (0.01, 0.03, 0.1):
        items.append(("telegraph", [*TRUTH_STATIC, gamma], "static", TRUTH_STATIC, 0, points))
        labels.append(f"telegraph_truth:{gamma}")
    found = parallel.ordered_map(ExpectedLLR(), items, min_items=2)
    excess: dict[str, float] = {}
    for label, value in zip(labels, found, strict=True):
        excess[label] = min(excess.get(label, value), value)
    values = {label: max(value, 0.0) for label, value in excess.items()}
    alias = {key: value for key, value in values.items() if key.startswith("alias:")}
    worst = min(alias, key=lambda key: alias[key])
    cost = design_cost(points, shots)
    kept_reads = sum(
        shots * (KEPT_FIRST + KEPT_LATER * (len(point.bases) - 1)) * (1 if point.kind == "xy" else 1)
        for point in points
        if not point.pre_dt
    )
    return {
        "segments": segments,
        "shots": shots,
        "pubs": len(points),
        "segment_reads_kept": kept_reads,
        "shots_total": shots * len(points),
        **cost,
        "alias_pairs": pairs,
        "worst_alias_pair": {"pair": worst, "expected_llr": alias[worst]},
        "tls_truth_vs_line_mixture_llr_by_p0": {k.split(":")[1]: v for k, v in values.items() if k.startswith("tls")},
        "tls_truth_worst_p0_llr": min(v for k, v in values.items() if k.startswith("tls_truth")),
        "static_truth_vs_tls_llr": values["static_truth_vs_tls"],
        "telegraph_truth_vs_static_llr": {k.split(":")[1]: v for k, v in values.items() if k.startswith("telegraph")},
    }


# Self-check ---------------------------------------------------------------


def sample(model: str, params: list[float], points: list[Point], rng: np.random.Generator) -> list[Point]:
    """Shot-level draws: line models draw one line path per shot through the chain; tls draws segments alone."""
    values = unpack(model, np.array(params))
    drawn = []
    for point in points:
        shots = int(point.counts.sum())
        patterns, probability = pattern_probabilities(model, values, point)
        counts = rng.multinomial(shots, probability / probability.sum())
        drawn.append(point.with_counts(patterns, counts.astype(float)))
    return drawn


def retained_name(analysis: dict[str, Any]) -> str:
    """RETAINED for the analyzer the record binds; an amended analyzer's output carries its closure digest.

    An amended analysis is a second reading of the same raw files beside the
    preregistered one, named by the analyzer that wrote it.
    """
    if analysis["preregistered"]:
        return RETAINED
    return f"segmented-sweep-{analysis['analyzer_closure']['sha256'][:12]}.json"


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(beat.rounded(value), indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--design", type=Path, help="write the design trade table here")
    parser.add_argument("--design-check", type=Path, help="require this retained design table to regenerate")
    args = parser.parse_args(argv)
    if args.design is not None or args.design_check is not None:
        rows = [design_rows(k, s, pairs) for k, s, pairs in DESIGN_TABLE]
        table = serialize({"schema_version": SCHEMA + "-design", "rows": rows})
        if args.design_check is not None:
            if args.design_check.read_text() != table:
                raise RuntimeError(f"{args.design_check} differs from a fresh design table")
            return 0
        args.design.write_text(table)
        return 0
    if args.run is None:
        parser.error("name a run directory or --design")
    analysis = report(args.run)
    text = serialize(analysis)
    target = args.run / retained_name(analysis)
    if args.check:
        if target.read_text() != text:
            raise RuntimeError(f"{target} differs from a fresh analysis")
        return 0
    target.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
