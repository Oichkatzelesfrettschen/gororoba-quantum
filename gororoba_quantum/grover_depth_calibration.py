"""Calibration of the family rule's threshold delta_resolve and its power, without a random number.

The rule of grover_depth_families.select_family compares the chi-squares of two non-nested, two-parameter fits, so
the difference has no textbook null law, and the rate bounds, the readout covariance and the leave-one-pair-out
influence check change it further. The error rates of a threshold are therefore computed: the corrected marked
frequencies of the four depths are Gaussian at these shots (3,000 or more kept shots per pair and binomial scatter
well inside the normal limit), so the decision's input is a four-dimensional normal vector, y = mu + L z with L the
Cholesky factor of the binomial-plus-readout covariance at the truth and z standard normal, and the probability
of every reading is an integral over z. The integral is evaluated by the unscrambled Sobol' sequence mapped through
the normal quantile (scipy.stats.qmc), a deterministic quadrature that draws nothing at random and takes no seed;
its error is read from the agreement of the first half of the points with all of them.

Truths. The two retained continuations (the retained fits of rho continued to depth 4) and the model itself
(rho = 1, which both families contain, so either family named there is an error).

Threshold. delta_resolve is the smallest candidate (DELTA_GRID) at which every misclassification probability of the
pooled rule is at most the stated rate on the first half of the points and on all of them: the geometric truth
read as coherent, the coherent truth read as geometric, and the model read as either family. The gates (bounds,
heterogeneity, influence) only turn a reading into "out of domain" or "not evaluated", so these probabilities
bound the misclassification of the gated rule from above.

Influence power. A leave-one-pair-out refit drops one mirror pair of depth d, whose n_d pairs are iid at the
planned shots: y_d' = y_d + (y_d - y_pair) / (n_d - 1), with y_d - y_pair independent of the pooled frequencies and
of the readout. The decision stands when the full reading and every refit agree. The probability that the full
reading names the truth and no refit differs is bounded below by P(full names the truth) minus the sum over depths
d of n_d P(full names the truth and the refit of depth d differs) (Bonferroni), computed on a five-dimensional
Sobol' set of the same kind.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

import grover_depth_families as families
from parallel import ordered_map

DELTA_GRID = tuple(float(x) for x in np.arange(1.0, 30.5, 0.5))
STATED_RATE = 0.01
CATEGORIES = families.FAMILY_CATEGORIES
BEND_CATEGORIES = ("beyond", "upward", "none", "not evaluated")


def sobol_normals(dim: int, log2n: int) -> np.ndarray:
    """The Sobol' points 1 to 2^log2n of dimension dim (the first block of the unscrambled sequence without its
    origin) as standard normal vectors."""
    from scipy import stats

    sampler = stats.qmc.Sobol(d=dim, scramble=False)
    return np.asarray(stats.norm.ppf(sampler.random_base2(log2n + 1)[1 : 2**log2n + 1]))


def truth_frequencies(ratios: Sequence[float], model: Sequence[float]) -> np.ndarray:
    """Marked frequency of each depth when the retention is rho_k M_k."""
    return np.array([families.probability_of(r * m, k) for r, m, k in zip(ratios, model, families.DEPTHS, strict=True)])


def frequency_covariance(freq: np.ndarray, kept: Sequence[float], readout: families.ReadoutShift) -> np.ndarray:
    return np.asarray(np.diag(freq * (1 - freq) / np.asarray(kept, dtype=float)) + readout.cov)


@dataclass(frozen=True, eq=False)
class Scan:
    """One point's readings: the bend category and the family category at each threshold of grid."""

    model: Sequence[float]
    retained: dict[str, Any]
    kept: Sequence[float]
    readout: families.ReadoutShift
    grid: Sequence[float]

    def readings(self, freq: np.ndarray, kept: Sequence[float]) -> tuple[int, list[int]]:
        usable = {k: float(f) for k, f in zip(families.DEPTHS, freq, strict=True)}
        sizes = dict(zip(families.DEPTHS, kept, strict=True))
        bend = families.bend_decision(usable, sizes, self.model, self.readout)["reading"]
        geo, coh, _, _ = families.fit_families(usable, sizes, self.model, self.readout)
        family = [CATEGORIES.index(families.category_of(families.select_family(geo, coh, 2, t)[0])) for t in self.grid]
        return BEND_CATEGORIES.index(families.bend_category(bend)), family

    def __call__(self, y: np.ndarray) -> tuple[int, list[int]]:
        return self.readings(y, self.kept)


@dataclass(frozen=True, eq=False)
class Joint:
    """The readings of the full data and of every leave-one-pair-out refit at one standard normal vector.

    The vector holds the four pooled frequencies' coordinates (their binomial and readout covariance) and, for each
    depth of n pairs, n - 1 coordinates of the pairs' deviations from the pooled frequency (the pairs are iid
    normal about it, so their deviations have the covariance s^2 (I - 11^T / n)); the refit that leaves pair i of
    depth d moves the pooled frequency to y_d - e_i / (n - 1) and the depth's kept shots down by one pair."""

    scan: Scan
    pairs: Sequence[int]
    pair_kept: float
    mean: np.ndarray
    factor: np.ndarray
    gate: float

    def __call__(self, z: np.ndarray) -> tuple[list[int], list[int], bool]:
        from scipy import linalg

        y = self.mean + self.factor @ z[:4]
        at = 4
        bend, family = [], []
        heterogeneity = 0.0
        full = self.scan.readings(y, self.scan.kept)
        bend.append(full[0])
        family.append(full[1][0])
        for depth, n in zip(families.DEPTHS, self.pairs, strict=True):
            if n < 2:
                continue
            f = self.mean[depth - 1]
            scatter = math.sqrt(f * (1 - f) / self.pair_kept) * (linalg.helmert(n).T @ z[at : at + n - 1])
            heterogeneity += float(np.sum(z[at : at + n - 1] ** 2))
            at += n - 1
            kept = list(self.scan.kept)
            kept[depth - 1] -= self.pair_kept
            for deviation in scatter:
                refit = np.array(y)
                refit[depth - 1] -= deviation / (n - 1)
                part = self.scan.readings(refit, kept)
                bend.append(part[0])
                family.append(part[1][0])
        return bend, family, heterogeneity <= self.gate


def calibrate(
    model: Sequence[float],
    retained: dict[str, Any],
    truths: Mapping[str, Sequence[float]],
    readout: families.ReadoutShift,
    kept: Sequence[float],
    log2n: int = 15,
) -> dict[str, Any]:
    """Misclassification probabilities of every threshold of DELTA_GRID under each truth (ratios rho_1..rho_4 of
    truths), and the smallest threshold whose probabilities stay within STATED_RATE on the first half of the points
    and on all of them."""
    points = sobol_normals(4, log2n)
    tables: dict[str, Any] = {}
    for name, ratios in truths.items():
        mean = truth_frequencies(ratios, model)
        factor = np.linalg.cholesky(frequency_covariance(mean, kept, readout))
        scan = Scan(model, retained, kept, readout, DELTA_GRID)
        rows = ordered_map(scan, list(mean + points @ factor.T), min_items=1)
        family = np.array([r[1] for r in rows])
        tables[name] = {
            "family": family,
            "bend": np.array([r[0] for r in rows]),
            "truth_frequencies": mean,
        }
    half = 2 ** (log2n - 1)

    def rates(name: str, sel: slice) -> dict[str, np.ndarray]:
        fam = tables[name]["family"][sel]
        return {c: np.mean(fam == CATEGORIES.index(c), axis=0) for c in CATEGORIES}

    wrong = {"geometric": "coherent", "coherent": "geometric"}
    chosen = None
    for j in range(len(DELTA_GRID)):
        ok = True
        for sel in (slice(0, half), slice(0, 2**log2n)):
            for name in truths:
                r = rates(name, sel)
                miss = (r["coherent"][j] + r["geometric"][j]) if name == "model" else r[wrong[name]][j]
                ok = ok and bool(miss <= STATED_RATE)
        if ok:
            chosen = j
            break
    if chosen is None:
        raise ValueError(f"no threshold up to {DELTA_GRID[-1]} holds every misclassification at {STATED_RATE}")
    full = slice(0, 2**log2n)
    first = slice(0, half)

    def wrong_by_grid(name: str, r: dict[str, np.ndarray]) -> list[float]:
        if name == "model":
            return [float(x) for x in r["coherent"] + r["geometric"]]
        return [float(x) for x in r[wrong[name]]]

    out: dict[str, Any] = {
        "method": (
            "unscrambled Sobol' quadrature (scipy.stats.qmc, points 1 to 2^n, mapped through the normal quantile) "
            "of the four corrected marked frequencies, Gaussian with the binomial and readout covariance at each truth"
        ),
        "stated_rate": STATED_RATE,
        "points": 2**log2n,
        "delta_resolve": DELTA_GRID[chosen],
        "grid": list(DELTA_GRID),
        "truths": {},
    }
    for name in truths:
        r_full, r_half = rates(name, full), rates(name, first)
        bend = tables[name]["bend"]
        out["truths"][name] = {
            "ratios": list(truths[name]),
            "frequencies": [float(x) for x in tables[name]["truth_frequencies"]],
            "at_delta_resolve": {c: float(r_full[c][chosen]) for c in CATEGORIES},
            "first_half_at_delta_resolve": {c: float(r_half[c][chosen]) for c in CATEGORIES},
            "wrong_family_by_grid": wrong_by_grid(name, r_full),
            "first_half_wrong_family_by_grid": wrong_by_grid(name, r_half),
            "bend_at_planned_shots": {c: float(np.mean(bend == BEND_CATEGORIES.index(c))) for c in BEND_CATEGORIES},
        }
    return out


def influence_power(
    model: Sequence[float],
    retained: dict[str, Any],
    truths: Mapping[str, Sequence[float]],
    readout: families.ReadoutShift,
    kept: Sequence[float],
    pairs: Sequence[int],
    pair_kept: float,
    threshold: float,
    log2n: int = 13,
) -> dict[str, Any]:
    """Power of the pooled rule at the threshold behind the pair-heterogeneity gate (a run whose pair chi-square
    exceeds its 0.99 quantile reads "not evaluated"), and with the influence check as well (the reading stands only
    when every leave-one-pair-out refit agrees), for each truth. The reading a truth names is the one the noise-free
    data read (geometric, coherent and unresolved for the two retained continuations and the model; the bend
    likewise). The pairs of every depth are iid at the planned shots, so one Sobol' set of dimension
    4 + sum(n_d - 1) carries the full data and all its refits together; the first half of the
    points is reported beside as the quadrature's own check."""
    dim = 4 + sum(n - 1 for n in pairs if n >= 2)
    points = sobol_normals(dim, log2n)
    scan = Scan(model, retained, kept, readout, (threshold,))
    gate = families.heterogeneity_threshold(sum(n - 1 for n in pairs if n >= 2))
    out: dict[str, Any] = {"points": 2**log2n, "dimension": dim, "threshold": threshold, "heterogeneity_gate": gate}
    for name, ratios in truths.items():
        mean = truth_frequencies(ratios, model)
        factor = np.linalg.cholesky(frequency_covariance(mean, kept, readout))
        expected_bend, expected_family = scan.readings(mean, kept)
        rows = ordered_map(Joint(scan, pairs, pair_kept, mean, factor, gate), list(points), min_items=1)
        passed = np.array([r[2] for r in rows])
        bend = np.array([r[0] for r in rows])
        family = np.array([r[1] for r in rows])
        entry: dict[str, Any] = {
            "expected_family": CATEGORIES[expected_family[0]],
            "expected_bend": BEND_CATEGORIES[expected_bend],
        }
        for label, readings, want in (("family", family, expected_family[0]), ("bend", bend, expected_bend)):
            hit = readings == want
            for tag, sel in (("", slice(None)), ("_first_half", slice(0, len(readings) // 2))):
                pooled = hit[sel, 0] & passed[sel]
                every = pooled & hit[sel].all(axis=1)
                entry[f"{label}_power_pooled{tag}"] = float(np.mean(pooled))
                entry[f"{label}_power_with_every_leave_one_out{tag}"] = float(np.mean(every))
            entry[f"{label}_refits_that_differ"] = {
                str(d): float(np.mean(hit[:, 0] & passed & ~hit[:, lo:hi].all(axis=1)))
                for d, (lo, hi) in zip(
                    (d for d, n in zip(families.DEPTHS, pairs, strict=True) if n >= 2), spans(pairs), strict=True
                )
            }
        out[name] = entry
    return out


def spans(pairs: Sequence[int]) -> list[tuple[int, int]]:
    """Column ranges of the refits of each depth in a Joint row (column 0 is the full data)."""
    out, at = [], 1
    for n in pairs:
        if n >= 2:
            out.append((at, at + n))
            at += n
    return out
