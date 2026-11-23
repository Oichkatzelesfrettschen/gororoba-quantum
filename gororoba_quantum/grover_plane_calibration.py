"""Calibration of the departure test and its power over the box of truths, without a random number.

The pair means of the four depths are Gaussian at the planned shots (3,000 or more kept shots per pair), so the
reading of every truth is an integral over standard normal vectors, evaluated at the points of the unscrambled Sobol'
sequence (scipy.stats.qmc, points 1 to 2^n) mapped through the normal quantile; the case takes no seed.

Null box. delta is the largest, over the cells (a, s) of the box and the depth-independent-offset line s = 1, of the
0.99 quantile of T = chi2(a, s) - chi2(a, s, eps), rounded up to a half unit and never below the chi-square(1)
quantile. The worst cell is reported with the cell's own quantile.

Power. Each truth is the exact noisy response of the committed circuits to a coherent mechanism (a CZ conditional
phase, a PRX amplitude, a rotating-frame ZZ coupling of the two couplers) or to the plane rotation itself, with the
excess factor s and the offset a of the cell; the fit still uses the plane family. The reading of a truth is the
fraction of points reading each departure category at delta.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy import stats

import grover_plane_decision as dec
from parallel import ordered_map

NULL_A = (0.90, 1.10)
NULL_S = (0.85, 1.10)
POWER_S = (0.90, 1.05)
DELTA_STEP = 0.5


def sobol_normals(dim: int, log2n: int) -> np.ndarray:
    sampler = stats.qmc.Sobol(d=dim, scramble=False)
    return np.asarray(stats.norm.ppf(sampler.random_base2(log2n + 1)[1 : 2**log2n + 1]))


def sobol_box(low: Sequence[float], high: Sequence[float], log2n: int) -> np.ndarray:
    sampler = stats.qmc.Sobol(d=len(low), scramble=False)
    unit = sampler.random_base2(log2n + 1)[1 : 2**log2n + 1]
    return np.asarray(np.array(low) + unit * (np.array(high) - np.array(low)))


def null_cells(log2n: int = 6) -> list[tuple[float, float]]:
    """Sobol' cells of the null box plus the offset line (a, s = 1) and the model."""
    cells = [(float(a), float(s)) for a, s in sobol_box((NULL_A[0], NULL_S[0]), (NULL_A[1], NULL_S[1]), log2n)]
    cells += [(a, 1.0) for a in (0.9, 0.95, 0.98, 1.0, 1.02, 1.05, 1.1)]
    return cells


def covariance(truth: np.ndarray, kept: Sequence[float], readout_cov: np.ndarray) -> np.ndarray:
    var = np.clip(truth, dec.FREQUENCY_FLOOR, 1 - dec.FREQUENCY_FLOOR)
    return np.asarray(np.diag(dec.PHI * var * (1 - var) / np.asarray(kept, dtype=float)) + readout_cov)


def run_cell(item: tuple[Any, ...]) -> dict[str, np.ndarray]:
    """T, eps and its standard error at every normal point for one truth: (fitter, truth, kept, readout_cov, points)."""
    fitter, truth, kept, readout_cov, points = item
    cov = covariance(truth, kept, readout_cov)
    factor = np.linalg.cholesky(cov)
    t, eps, se = [], [], []
    for z in points:
        y = truth + factor @ z
        f0 = fitter.fit(y, cov, False)
        f1 = fitter.fit(y, cov, True)
        t.append(f0["chi2"] - f1["chi2"])
        eps.append(f1["eps"])
        se.append(fitter.errors(f1, cov).get("eps", float("nan")))
    return {"T": np.array(t), "eps": np.array(eps), "se": np.array(se)}


def readings(cell: dict[str, np.ndarray], delta: float) -> dict[str, float]:
    t, eps, se = cell["T"], cell["eps"], cell["se"]
    coherent = t >= delta
    geometric = ~coherent & np.isfinite(se) & (np.abs(eps) + dec.Z_EQUIV * se <= dec.EPS_EQUIV)
    return {
        "coherent": float(np.mean(coherent)),
        "geometric": float(np.mean(geometric)),
        "unresolved": float(np.mean(~coherent & ~geometric)),
    }


def calibrate(
    fitter: dec.Fitter, kept: Sequence[float], readout_cov: np.ndarray, log2n: int = 10, cell_log2n: int = 6
) -> dict[str, Any]:
    points = sobol_normals(len(kept), log2n)
    cells = null_cells(cell_log2n)
    items = [(fitter, fitter.response.probabilities(a, s, 0.0), kept, readout_cov, points) for a, s in cells]
    runs = ordered_map(run_cell, items, min_items=1)
    quantiles = [float(np.quantile(r["T"], 1 - dec.ALPHA)) for r in runs]
    worst = int(np.argmax(quantiles))
    floor = float(stats.chi2.isf(dec.ALPHA, 1))
    delta = max(floor, math.ceil(max(quantiles) / DELTA_STEP) * DELTA_STEP)
    rates = [readings(r, delta) for r in runs]
    at_offset = [x for (a, s), x in zip(cells, rates, strict=True) if s == 1.0]
    return {
        "method": "unscrambled Sobol' quadrature, no seed",
        "points": 2**log2n,
        "cells": len(cells),
        "delta_resolve": delta,
        "chi2_1_quantile": floor,
        "worst_cell": {"a": cells[worst][0], "s": cells[worst][1], "quantile": quantiles[worst]},
        "false_coherent_max": max(x["coherent"] for x in rates),
        "false_coherent_offset_line_max": max(x["coherent"] for x in at_offset),
        "geometric_reading_min_over_null_cells": min(x["geometric"] for x in rates),
    }


def power(
    fitter: dec.Fitter,
    truths: Sequence[tuple[str, np.ndarray]],
    kept: Sequence[float],
    readout_cov: np.ndarray,
    delta: float,
    log2n: int = 9,
) -> list[dict[str, Any]]:
    """Reading rates of every labeled truth (label, probabilities of the four depths) at delta."""
    points = sobol_normals(len(kept), log2n)
    runs = ordered_map(run_cell, [(fitter, p, kept, readout_cov, points) for _, p in truths], min_items=1)
    return [{"truth": label, **readings(r, delta)} for (label, _), r in zip(truths, runs, strict=True)]


def run_pair_cell(item: tuple[Any, ...]) -> dict[str, Any]:
    """Readings of dec.read_pairs on simulated mirror pairs of one truth: (fitter, truth, pairs per depth, shots per
    copy, readout_cov, delta, points, noise_phi). The four depths share the readout common-mode draw; the dimension of
    a point is the two sides of every pair plus the four depths."""
    fitter, truth, pairs_per_depth, kept, readout_cov, delta, points, noise_phi = item
    factor = np.linalg.cholesky(readout_cov + 1e-18 * np.eye(len(dec.DEPTHS)))
    counts = {"coherent": 0, "geometric": 0, "unresolved": 0, "other": 0}
    for z in points:
        common = factor @ z[: len(dec.DEPTHS)]
        cursor = len(dec.DEPTHS)
        pairs: dict[int, list[Any]] = {}
        for i, k in enumerate(dec.DEPTHS):
            p = float(np.clip(truth[i] + common[i], dec.FREQUENCY_FLOOR, 1 - dec.FREQUENCY_FLOOR))
            sd = math.sqrt(noise_phi * p * (1 - p) / kept)
            pairs[k] = []
            for _ in range(pairs_per_depth[i]):
                sides = []
                for _ in range(2):
                    f = float(np.clip(p + sd * z[cursor], 0.0, 1.0))
                    cursor += 1
                    sides.append((round(f * kept), round(kept)))
                pairs[k].append(tuple(sides))
        out = dec.read_pairs(fitter, pairs, np.zeros(len(dec.DEPTHS)), readout_cov, kept, delta)
        reading = out["departure"]
        counts[reading if reading in counts else "other"] += 1
    n = len(points)
    return {key: value / n for key, value in counts.items()}


def influence_power(
    fitter: dec.Fitter,
    truths: Sequence[tuple[str, np.ndarray]],
    pairs_per_depth: Sequence[int],
    kept: float,
    readout_cov: np.ndarray,
    delta: float,
    log2n: int = 8,
    noise_phi: float = 1.0,
) -> list[dict[str, Any]]:
    """The reading rates of every labeled truth through the whole gated rule: heterogeneity gate, the full reading
    and the leave-one-pair-out refits (a reading that changes with one pair leaves the "other" bucket). The pair
    frequencies carry the binomial variance times noise_phi; the rule's covariance always carries dec.PHI."""
    dim = len(dec.DEPTHS) + 2 * sum(pairs_per_depth)
    points = sobol_normals(dim, log2n)
    runs = ordered_map(
        run_pair_cell,
        [(fitter, p, list(pairs_per_depth), kept, readout_cov, delta, points, noise_phi) for _, p in truths],
        min_items=1,
    )
    return [{"truth": label, **r} for (label, _), r in zip(truths, runs, strict=True)]
