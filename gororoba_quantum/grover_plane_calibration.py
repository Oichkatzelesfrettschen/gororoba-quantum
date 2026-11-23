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

# The null box is the fitting box of grover_plane_decision (A_BOX, S_BOX). Power is claimed over the region around the
# retained fits, a in POWER_A and s in POWER_S, which lies inside it.
NULL_A = (0.80, 1.20)
NULL_S = (0.75, 1.15)
POWER_A = (0.90, 1.10)
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
    cells += [(a, 1.0) for a in (0.8, 0.9, 0.95, 0.98, 1.0, 1.02, 1.05, 1.1, 1.2)]
    return cells


def covariance(truth: np.ndarray, kept: Sequence[float], readout_cov: np.ndarray) -> np.ndarray:
    var = np.clip(truth, dec.FREQUENCY_FLOOR, 1 - dec.FREQUENCY_FLOOR)
    return np.asarray(np.diag(dec.PHI * var * (1 - var) / np.asarray(kept, dtype=float)) + readout_cov)


def run_cell(item: tuple[Any, ...]) -> dict[str, Any]:
    """T, eps and its standard error at every normal point for one truth: (fitter, truth, kept, readout_cov, points)."""
    fitter, truth, kept, readout_cov, points = item
    cov = covariance(truth, kept, readout_cov)
    factor = np.linalg.cholesky(cov)
    t, eps, se, chi1 = [], [], [], []
    for z in points:
        y = truth + factor @ z
        f0 = fitter.fit(y, cov, False)
        f1 = fitter.fit(y, cov, True)
        t.append(f0["chi2"] - f1["chi2"])
        chi1.append(f1["chi2"])
        eps.append(f1["eps"])
        se.append(fitter.errors(f1, cov).get("eps", float("nan")))
    return {"T": np.array(t), "eps": np.array(eps), "se": np.array(se), "chi1": np.array(chi1), "dof": len(truth) - 3}


def readings(cell: dict[str, np.ndarray], delta: float) -> dict[str, float]:
    t, eps, se = cell["T"], cell["eps"], cell["se"]
    dof = cell.get("dof", 1)
    adequate = cell["chi1"] <= stats.chi2.isf(dec.ALPHA, dof) if "chi1" in cell and dof > 0 else np.ones_like(t, bool)
    departs = t >= delta
    geometric = ~departs & np.isfinite(se) & (np.abs(eps) + dec.Z_EQUIV * se <= dec.EPS_EQUIV)
    return {
        "coherent": float(np.mean(departs & adequate)),
        "non_rotation": float(np.mean(departs & ~adequate)),
        "geometric": float(np.mean(geometric)),
        "unresolved": float(np.mean(~departs & ~geometric)),
    }


def block_stats(values: np.ndarray, blocks: int) -> tuple[float, float]:
    """Mean and standard error of an indicator's rate over consecutive blocks of the unscrambled Sobol' points: each
    block is a deterministic low-discrepancy set, and the spread of the block rates is the error estimate (an
    estimate, not a bound)."""
    rates = np.asarray(values, dtype=float).reshape(blocks, -1).mean(axis=1)
    return float(rates.mean()), float(rates.std(ddof=1) / math.sqrt(blocks))


def cell_report(a: float, s: float, run: dict[str, Any], delta: float, blocks: int) -> dict[str, Any]:
    t = run["T"]
    adequate = run["chi1"] <= stats.chi2.isf(dec.ALPHA, run["dof"])
    coherent, coherent_se = block_stats((t >= delta) & adequate, blocks)
    non_rotation, non_rotation_se = block_stats((t >= delta) & ~adequate, blocks)
    return {
        "a": a,
        "s": s,
        "coherent": coherent,
        "coherent_se": coherent_se,
        "non_rotation": non_rotation,
        "non_rotation_se": non_rotation_se,
        "quantile": float(np.quantile(t, 1 - dec.ALPHA)),
    }


def perimeter(t: float) -> tuple[float, float]:
    """The point of the null box boundary at parameter t in [0, 4): the four edges in turn from the corner
    (a low, s low), counterclockwise."""
    edge, u = int(t) % 4, t - math.floor(t)
    (a0, a1), (s0, s1) = NULL_A, NULL_S
    if edge == 0:
        return a0 + u * (a1 - a0), s0
    if edge == 1:
        return a1, s0 + u * (s1 - s0)
    if edge == 2:
        return a1 - u * (a1 - a0), s1
    return a0, s1 - u * (s1 - s0)


def calibrate(
    fitter: dec.Fitter,
    kept: Sequence[float],
    readout_cov: np.ndarray,
    log2n: int = 10,
    cell_log2n: int = 6,
    blocks: int = 8,
    search_log2n: int | None = None,
    nodes: int = 24,
    refinements: int = 5,
) -> dict[str, Any]:
    """The reading rates of the null truths, the offset line, the four corners of the box and a search of its boundary.

    Every cell evaluates the same unscrambled Sobol' points (2^log2n, in blocks for an error estimate); the boundary
    search evaluates nodes cells at equal steps of the perimeter at 2^search_log2n points, then bisects the bracket of
    each of the three highest false-alarm rates refinements times at the same points (common points make the rate a
    deterministic function of the cell). delta is the 0.99 quantile of T of the cell with the largest one over every
    cell evaluated, rounded up to a half unit and never below the chi-square(1) quantile. The reported maximum is the
    largest rate over the evaluated cells with its error estimate: the integral is estimated at those cells and is not
    bounded over the continuous box."""
    search_log2n = log2n - 2 if search_log2n is None else search_log2n
    points = sobol_normals(len(kept), log2n)
    cells = null_cells(cell_log2n) + [(a, s) for a in NULL_A for s in NULL_S]
    labels = ["null"] * (len(cells) - 4) + ["corner"] * 4
    runs = ordered_map(
        run_cell,
        [(fitter, fitter.response.probabilities(a, s, 0.0), kept, readout_cov, points) for a, s in cells],
        min_items=1,
    )
    floor = float(stats.chi2.isf(dec.ALPHA, 1))

    def delta_of(quantiles: Sequence[float]) -> float:
        return max(floor, math.ceil(max(quantiles) / DELTA_STEP) * DELTA_STEP)

    delta0 = delta_of([float(np.quantile(r["T"], 1 - dec.ALPHA)) for r in runs])
    boundary: dict[float, tuple[tuple[float, float], dict[str, Any]]] = {}
    search_points = sobol_normals(len(kept), search_log2n)

    def evaluate(ts: list[float]) -> None:
        todo = [t for t in ts if t not in boundary]
        cell_list = [perimeter(t) for t in todo]
        done = ordered_map(
            run_cell,
            [
                (fitter, fitter.response.probabilities(a, s, 0.0), kept, readout_cov, search_points)
                for a, s in cell_list
            ],
            min_items=1,
        )
        for t, cell, run in zip(todo, cell_list, done, strict=True):
            boundary[t] = (cell, run)

    def false_alarm(t: float) -> float:
        run = boundary[t][1]
        return float(np.mean((run["T"] >= delta0) & (run["chi1"] <= stats.chi2.isf(dec.ALPHA, run["dof"]))))

    step = 4.0 / nodes
    evaluate([i * step for i in range(nodes)])
    for depth in range(1, refinements + 1):
        top = sorted(boundary, key=lambda t: -false_alarm(t))[:3]
        evaluate([(t + sign * step / 2**depth) % 4 for t in top for sign in (-1, 1)])
    for t in boundary:
        cells.append(boundary[t][0])
        labels.append("boundary")
        runs.append(boundary[t][1])
    delta = delta_of([float(np.quantile(r["T"], 1 - dec.ALPHA)) for r in runs])
    reports = []
    for (a, s), label, run in zip(cells, labels, runs, strict=True):
        n_blocks = blocks if len(run["T"]) >= 64 * blocks else 1
        rep = cell_report(a, s, run, delta, n_blocks) if n_blocks > 1 else cell_report_single(a, s, run, delta)
        reports.append({**rep, "kind": label, "points": len(run["T"])})
    worst_alarm = max(reports, key=lambda r: r["coherent"])
    worst_quantile = max(reports, key=lambda r: r["quantile"])
    at_offset = [r for r in reports if r["s"] == 1.0]
    return {
        "method": "unscrambled Sobol' quadrature in blocks, no seed; rates are estimates at the evaluated cells",
        "points": 2**log2n,
        "blocks": blocks,
        "boundary_points": 2**search_log2n,
        "cells": len(cells),
        "cells_by_kind": {k: labels.count(k) for k in ("null", "corner", "boundary")},
        "delta_resolve": delta,
        "delta_from_first_cells": delta0,
        "chi2_1_quantile": floor,
        "chi2_1_tail_at_delta": float(stats.chi2.sf(delta, 1)),
        "worst_cell": {k: worst_quantile[k] for k in ("a", "s", "quantile", "kind")},
        "false_coherent_max": worst_alarm["coherent"],
        "false_coherent_max_se": worst_alarm["coherent_se"],
        "false_coherent_max_cell": {k: worst_alarm[k] for k in ("a", "s", "kind")},
        "false_coherent_max_plus_3se": worst_alarm["coherent"] + 3 * worst_alarm["coherent_se"],
        "false_coherent_offset_line_max": max(r["coherent"] for r in at_offset),
        "non_rotation_false_alarm_max": max(r["non_rotation"] for r in reports),
        "non_rotation_false_alarm_mean": float(np.mean([r["non_rotation"] for r in reports])),
        "non_rotation_false_alarm_max_cell": {
            k: max(reports, key=lambda r: r["non_rotation"])[k] for k in ("a", "s", "kind")
        },
        "geometric_reading_min_over_null_cells": min(
            readings(r, delta)["geometric"] for (a, s), r in zip(cells, runs, strict=True)
        ),
        "corners": [r for r in reports if r["kind"] == "corner"],
    }


def cell_report_single(a: float, s: float, run: dict[str, Any], delta: float) -> dict[str, Any]:
    """cell_report for a run too short to split into blocks: the rates carry no error estimate."""
    rates = readings(run, delta)
    return {
        "a": a,
        "s": s,
        "coherent": rates["coherent"],
        "coherent_se": float("nan"),
        "non_rotation": rates["non_rotation"],
        "non_rotation_se": float("nan"),
        "quantile": float(np.quantile(run["T"], 1 - dec.ALPHA)),
    }


def power(
    fitter: dec.Fitter,
    truths: Sequence[tuple[str, np.ndarray]],
    kept: Sequence[float],
    readout_cov: np.ndarray,
    delta: float,
    log2n: int = 9,
    blocks: int = 8,
) -> list[dict[str, Any]]:
    """Reading rates of every labeled truth (label, probabilities of the four depths) at delta, each with the error
    estimate of its coherent rate over blocks of the Sobol' points (an estimate, not a bound)."""
    points = sobol_normals(len(kept), log2n)
    runs = ordered_map(run_cell, [(fitter, p, kept, readout_cov, points) for _, p in truths], min_items=1)
    out = []
    for (label, _), r in zip(truths, runs, strict=True):
        adequate = r["chi1"] <= stats.chi2.isf(dec.ALPHA, r["dof"])
        mean, se = block_stats((r["T"] >= delta) & adequate, blocks)
        out.append({"truth": label, **readings(r, delta), "coherent_se": se, "coherent_blocks": mean})
    return out


def run_pair_cell(item: tuple[Any, ...]) -> dict[str, Any]:
    """Readings of dec.read_pairs on simulated mirror pairs of one truth: (fitter, truth, pairs per depth, shots per
    copy, readout_cov, delta, points, noise_phi, gate_phi). The four depths share the readout common-mode draw; the
    dimension of a point is the two sides of every pair plus the four depths."""
    fitter, truth, pairs_per_depth, kept, readout_cov, delta, points, noise_phi, gate_phi = item
    n_depths = len(pairs_per_depth)
    factor = np.linalg.cholesky(readout_cov + 1e-18 * np.eye(n_depths))
    counts = {"coherent": 0, "non_rotation": 0, "geometric": 0, "unresolved": 0, "other": 0}
    for z in points:
        common = factor @ z[:n_depths]
        cursor = n_depths
        pairs: dict[int, list[Any]] = {}
        for i, k in enumerate(range(1, n_depths + 1)):
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
        out = dec.read_pairs(fitter, pairs, np.zeros(n_depths), readout_cov, kept, delta, gate_phi)
        reading = out["departure"]
        reading = "non_rotation" if reading == dec.NON_ROTATION else reading
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
    gate_phi: float = dec.PHI,
) -> list[dict[str, Any]]:
    """The reading rates of every labeled truth through the pair gates: the two-pair floor, the heterogeneity gate at
    dispersion gate_phi, the full reading and the leave-one-pair-out refits (a reading that changes with one pair
    leaves the "other" bucket). The pair frequencies carry the binomial variance times noise_phi; the rule's covariance
    always carries dec.PHI. The readout gates are not simulated here (see readout_gate_rates)."""
    dim = len(pairs_per_depth) + 2 * sum(pairs_per_depth)
    points = sobol_normals(dim, log2n)
    runs = ordered_map(
        run_pair_cell,
        [(fitter, p, list(pairs_per_depth), kept, readout_cov, delta, points, noise_phi, gate_phi) for _, p in truths],
        min_items=1,
    )
    return [{"truth": label, **r} for (label, _), r in zip(truths, runs, strict=True)]


def run_contrast_cell(item: tuple[Any, ...]) -> dict[str, float]:
    """Readings of dec.mark_contrast for one pair of truths (mark 101 and mark 011): the two marks' frequencies are
    independent Gaussians with the binomial variance times PHI and the readout covariance; each mark's fit passes
    through the departure rule at delta, so a fit on a bound of the box or inadequate as a rotation reads
    "not evaluated" (the pair and readout gates are not simulated)."""
    f_a, f_b, truth_a, truth_b, kept_a, kept_b, cov_a, cov_b, ratio, interval, delta, points = item
    cova = covariance(truth_a, kept_a, cov_a)
    covb = covariance(truth_b, kept_b, cov_b)
    la, lb = np.linalg.cholesky(cova), np.linalg.cholesky(covb)
    na = len(truth_a)
    counts = {"CZ-phase-like": 0, "PRX-like": 0, "unresolved": 0, "not evaluated": 0}
    for z in points:
        fits = {
            "101": dec.decide(f_a, truth_a + la @ z[:na], cova, delta),
            "011": dec.decide(f_b, truth_b + lb @ z[na:], covb, delta),
        }
        reading = dec.mark_contrast(fits, ratio, interval)["reading"]
        counts[next((k for k in counts if reading.startswith(k)), "unresolved")] += 1
    return {k: v / len(points) for k, v in counts.items()}


def contrast_power(
    fitter_a: dec.Fitter,
    fitter_b: dec.Fitter,
    truths: Sequence[tuple[str, np.ndarray, np.ndarray]],
    kept_a: Sequence[float],
    kept_b: Sequence[float],
    cov_a: np.ndarray,
    cov_b: np.ndarray,
    ratio: float,
    delta: float,
    interval: Sequence[float] | None = None,
    log2n: int = 8,
) -> list[dict[str, Any]]:
    points = sobol_normals(len(kept_a) + len(kept_b), log2n)
    runs = ordered_map(
        run_contrast_cell,
        [
            (fitter_a, fitter_b, pa, pb, kept_a, kept_b, cov_a, cov_b, ratio, interval, delta, points)
            for _, pa, pb in truths
        ],
        min_items=1,
    )
    return [{"truth": label, **r} for (label, _, _), r in zip(truths, runs, strict=True)]


def readout_gate_rates(plan: dict[str, Any], log2n: int = 12) -> dict[str, Any]:
    """Pass rates of the readout gates of the analysis at the planned shots when the device follows the model:
    the shift tolerance (the corrected depth frequencies move by at most plan["tolerance"]; the shift is Gaussian with
    the planned common-mode covariance) and the two-sides chi-square (the statistic of two sides of one preparation
    is chi-square on sides_dof degrees of freedom times the dispersion of the copies, so its 0.99-quantile gate
    passes with probability P(chi2 <= threshold / phi)). The copy floor (a preparation keeping under half its planned
    shots) is not modeled: it needs the herald loss rate, which the retained jobs bound only from above."""
    cov = np.asarray(plan["planned_covariance"], dtype=float)
    factor = np.linalg.cholesky(cov + 1e-18 * np.eye(len(cov)))
    shifts = sobol_normals(len(cov), log2n) @ factor.T
    tolerance = float(plan["tolerance"])
    dof, threshold = int(plan["sides_dof"]), float(plan["sides_threshold"])
    return {
        "shift_tolerance": tolerance,
        "shift_pass_rate": float(np.mean(np.max(np.abs(shifts), axis=1) <= tolerance)),
        "sides_pass_rate_by_dispersion": {
            f"{phi:g}": float(stats.chi2.cdf(threshold / phi, dof)) for phi in (0.86, 1.0, dec.PHI)
        },
        "copy_floor": "not modeled",
    }
