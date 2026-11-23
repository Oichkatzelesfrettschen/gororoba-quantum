"""Mechanism-agnostic decision on the depth dependence of the line-native Grover retention.

The primary question is whether the marked probability at depths 1 to 4 departs from the geometric law of the
calibrated model, P_k = 1/8 + a (Q_k(s, 0) - 1/8), against the same law with a rotation eps of the Grover plane per
iteration, P_k = 1/8 + a (Q_k(s, eps) - 1/8) (grover_plane_sim.Response: the calibrated noisy density-matrix path of
the committed circuits, then after each iteration a rotation of the plane by eps and a global depolarizing factor s,
and a depth-independent factor a). Any coherent error of a gate acts on the plane to first order as a rotation, so
eps is the mechanism-free measure of the departure: the reading names no gate. A depth-independent offset (a != 1,
s = 1) is not a per-iteration loss, and a coherent term that is merely unresolved is not "geometric".

Readings of the departure, from T = chi2(a, s) - chi2(a, s, eps) over the depths with the full covariance:
  coherent        T >= delta (calibrated over the box of null truths, worst cell) and the rotation fit adequate
                  (chi2(a, s, eps) below the 0.99 chi-square quantile of its degrees of freedom);
  non-rotation    T >= delta and the rotation fit inadequate: the depths depart from geometric by something a
                  plane rotation does not describe (an incoherent depth-dependent loss, say);
  geometric       T < delta and |eps| + 1.645 SE(eps) <= EPS_EQUIV: the coherent term is bounded by EPS_EQUIV;
  unresolved      otherwise: a coherent term up to EPS_EQUIV is not excluded;
  out of domain   the selected fit sits on a bound of the fitting box, which equals the calibrated truth box.
The per-iteration loss reads "resolved" only when s - 1 is below -3 SE(s) in the fit the departure reading selects;
the offset a is reported with its SE and decides nothing. The mechanism attribution (grover_plane_sim slopes of eps
against a CZ phase, a PRX amplitude and a ZZ coupling) is reported beside and decides nothing.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy import optimize, stats

import grover_plane_sim as sim

Pairs = dict[int, list[Any]]

DEPTHS = (1, 2, 3, 4)
# The fitting box equals the box the calibration covers (grover_plane_calibration.NULL_A and NULL_S).
A_BOX = (0.80, 1.20)
S_BOX = (0.75, 1.15)
E_BOX = (-0.3, 0.3)
FREQUENCY_FLOOR = 1e-4
EPS_EQUIV = 0.01
Z_EQUIV = 1.645
Z_LOSS = 3.0
# Pearson dispersion of the retained copies of one circuit: chi-square 19.02 on 22 degrees of freedom (phi 0.86); the
# 95 % upper bound of chi2 / dof is 1.54, which scales every binomial variance of a pair.
PHI = 1.54
ALPHA = 0.01


class Pair(tuple):  # ((marked_a, kept_a), (marked_b, kept_b)): the two copies of a mirror pair
    __slots__ = ()


def pair_mean(pair: Sequence[Sequence[int]], phi: float = PHI) -> tuple[float, float]:
    """The mean of the two copy frequencies with equal side weights, and its variance: a drift linear in position moves
    the copies by opposite amounts and leaves the mean unchanged whatever the kept shots of each side."""
    freqs, variances = [], []
    for marked, kept in pair:
        f = min(max(marked / kept, FREQUENCY_FLOOR), 1 - FREQUENCY_FLOOR)
        freqs.append(f)
        variances.append(f * (1 - f) / kept)
    return (freqs[0] + freqs[1]) / 2, phi * (variances[0] + variances[1]) / 4


def depth_estimate(pairs: Sequence[Sequence[Sequence[int]]], phi: float = PHI) -> tuple[float, float]:
    """The depth's frequency as the mean of its pair means (equal pair weights) and the variance of that mean."""
    means = [pair_mean(p, phi) for p in pairs]
    return sum(m for m, _ in means) / len(means), sum(v for _, v in means) / len(means) ** 2


class Fitter:
    """Least squares of the four depth frequencies on the response of a Response, over the table of
    Q_k(s, eps) - 1/8 on a grid of the boxes, refined by a local search; a follows in closed form at each (s, eps)."""

    def __init__(self, response: sim.Response, s_points: int = 91, e_points: int = 121) -> None:
        self.response = response
        self.s = np.linspace(*S_BOX, s_points)
        self.e = np.linspace(*E_BOX, e_points)
        self.zero = int(np.argmin(np.abs(self.e)))
        self.table = np.array([[response.centered(s, e) for e in self.e] for s in self.s])

    def best_a(self, d: np.ndarray, w: np.ndarray, q: np.ndarray) -> np.ndarray:
        num = np.einsum("...i,ij,j->...", q, w, d)
        den = np.einsum("...i,ij,...j->...", q, w, q)
        return np.clip(num / np.maximum(den, 1e-300), *A_BOX)

    def chi2_grid(self, d: np.ndarray, w: np.ndarray, table: np.ndarray) -> np.ndarray:
        a = self.best_a(d, w, table)
        resid = d - a[..., None] * table
        return np.einsum("...i,ij,...j->...", resid, w, resid)

    def value(self, d: np.ndarray, w: np.ndarray, s: float, e: float) -> tuple[float, float]:
        q = self.response.centered(s, e)
        a = float(self.best_a(d, w, q))
        r = d - a * q
        return float(r @ w @ r), a

    def fit(self, y: np.ndarray, cov: np.ndarray, free_eps: bool) -> dict[str, Any]:
        w = np.linalg.inv(cov)
        d = y - 1 / 8
        if free_eps:
            grid = self.chi2_grid(d, w, self.table)
            i, j = np.unravel_index(int(np.argmin(grid)), grid.shape)
            result = optimize.minimize(
                lambda x: self.value(d, w, x[0], x[1])[0],
                [self.s[i], self.e[j]],
                method="L-BFGS-B",
                bounds=[S_BOX, E_BOX],
                options={"ftol": 1e-12, "gtol": 1e-8, "eps": 1e-6},
            )
            s, e = float(result.x[0]), float(result.x[1])
        else:
            grid = self.chi2_grid(d, w, self.table[:, self.zero, :])
            low = int(np.argmin(grid))
            lo, hi = self.s[max(low - 1, 0)], self.s[min(low + 1, len(self.s) - 1)]
            result = optimize.minimize_scalar(
                lambda x: self.value(d, w, x, 0.0)[0], bounds=(lo, hi), method="bounded", options={"xatol": 1e-9}
            )
            s, e = float(result.x), 0.0
        chi2, a = self.value(d, w, s, e)
        return {"a": a, "s": s, "eps": e, "chi2": max(chi2, 0.0), "free_eps": free_eps}

    def errors(self, fit: dict[str, Any], cov: np.ndarray) -> dict[str, float]:
        """Standard errors of (a, s, eps) from the Jacobian of the response at the fit (nan where a parameter sits on
        its bound)."""
        w = np.linalg.inv(cov)
        names = ["a", "s", "eps"] if fit["free_eps"] else ["a", "s"]
        base = np.array([fit["a"], fit["s"], fit["eps"]])
        cols = []
        for n, name in enumerate(["a", "s", "eps"]):
            if name not in names:
                continue
            h = 1e-5
            up, down = base.copy(), base.copy()
            up[n] += h
            down[n] -= h
            cols.append((self.response.probabilities(*up) - self.response.probabilities(*down)) / (2 * h))
        jac = np.column_stack(cols)
        sd = np.sqrt(np.diag(np.linalg.inv(jac.T @ w @ jac)))
        out = dict(zip(names, (float(x) for x in sd), strict=True))
        for name, value, box in (("s", fit["s"], S_BOX), ("eps", fit["eps"], E_BOX), ("a", fit["a"], A_BOX)):
            if name in out and (value <= box[0] + 1e-9 or value >= box[1] - 1e-9):
                out[name] = float("nan")
        return out


RESPONSE_DECIMALS = 6


def response_grid_digest(fitter: Fitter) -> dict[str, Any]:
    """The plane response over the table the fit and the calibration search: Q_k(s, eps) - 1/8 at every (s, eps) of the
    fitter's grid (S_BOX by E_BOX), rounded to RESPONSE_DECIMALS and hashed, so a change of the response anywhere in
    the fitting box changes the digest."""
    table = np.round(fitter.table, RESPONSE_DECIMALS) + 0.0
    return {
        "s_box": list(S_BOX),
        "eps_box": list(E_BOX),
        "s_points": len(fitter.s),
        "eps_points": len(fitter.e),
        "depths": int(table.shape[-1]),
        "decimals": RESPONSE_DECIMALS,
        "sha256": hashlib.sha256(json.dumps(table.tolist()).encode()).hexdigest(),
    }


NON_ROTATION = "non-geometric, not a rotation"
OUT_OF_DOMAIN = "out of domain: a fit sits on a bound of the calibrated box"


def departure(
    fit0: dict[str, Any], fit1: dict[str, Any], err1: dict[str, float], delta: float, adequate: bool = True
) -> tuple[str, float]:
    """The reading of the departure from the geometric law and the statistic T."""
    t = fit0["chi2"] - fit1["chi2"]
    if t >= delta:
        return ("coherent" if adequate else NON_ROTATION), t
    se = err1.get("eps", float("nan"))
    if math.isfinite(se) and abs(fit1["eps"]) + Z_EQUIV * se <= EPS_EQUIV:
        return "geometric", t
    return "unresolved", t


def on_bound(value: float, box: tuple[float, float]) -> bool:
    return bool(value <= box[0] + 1e-6 or value >= box[1] - 1e-6)


def decide(fitter: Fitter, y: np.ndarray, cov: np.ndarray, delta: float) -> dict[str, Any]:
    """The preregistered readings on four depth frequencies y (corrected to the model's readout) with covariance cov."""
    fit0 = fitter.fit(y, cov, False)
    fit1 = fitter.fit(y, cov, True)
    err1 = fitter.errors(fit1, cov)
    dof = len(y) - 3
    adequate = dof <= 0 or fit1["chi2"] <= float(stats.chi2.isf(ALPHA, dof))
    reading, t = departure(fit0, fit1, err1, delta, adequate)
    chosen, err = (fit1, err1) if reading in ("coherent", NON_ROTATION) else (fit0, fitter.errors(fit0, cov))
    if any(on_bound(chosen[n], box) for n, box in (("a", A_BOX), ("s", S_BOX))):
        reading = OUT_OF_DOMAIN
    s_se = err.get("s", float("nan"))
    loss = math.isfinite(s_se) and (chosen["s"] - 1) <= -Z_LOSS * s_se
    w = np.linalg.inv(cov)
    d = y - 1 / 8
    residual = d - fitter.response.centered(1.0, 0.0)
    model_chi2 = float(residual @ w @ residual)
    return {
        "departure": reading,
        "T": t,
        "delta": delta,
        "chi2_model": model_chi2,
        "chi2_geometric": fit0["chi2"],
        "chi2_rotation": fit1["chi2"],
        "geometric": {k: fit0[k] for k in ("a", "s")},
        "rotation": {k: fit1[k] for k in ("a", "s", "eps")},
        "rotation_se": err1,
        "per_iteration_loss": "resolved" if loss else "not resolved",
        "offset_a": chosen["a"],
        "offset_a_se": err.get("a", float("nan")),
        "rotation_adequate": adequate,
    }


COPY_FLOOR = 0.5
# A depth with one surviving mirror pair has no pair heterogeneity and no leave-one-pair-out refit, so a displaced
# circuit in it reaches the fit unchecked: every depth keeps at least this many pairs after the shot floor.
MIN_PAIRS = 2
INFLUENCE_FAIL = "not evaluated: the reading depends on one mirror pair"
NO_PAIRS = "not evaluated: a depth keeps fewer than two mirror pairs, so its pairs cannot be tested against one another"


def heterogeneity_thresholds(max_dof: int = 8) -> dict[str, float]:
    return {str(d): float(stats.chi2.isf(ALPHA, d)) for d in range(1, max_dof + 1)}


def surviving_pairs(pairs: Pairs, planned_kept: float) -> tuple[Pairs, dict[str, list[int]]]:
    """A pair leaves its depth when either copy keeps fewer than COPY_FLOOR of the planned kept shots, so the
    surviving pairs stay centered on the job."""
    keep: Pairs = {}
    dropped: dict[str, list[int]] = {}
    for k in sorted(pairs):
        keep[k] = []
        for i, pair in enumerate(pairs[k]):
            if all(kept >= COPY_FLOOR * planned_kept for _, kept in pair):
                keep[k].append(pair)
            else:
                dropped.setdefault(str(k), []).append(i)
    return keep, dropped


def estimates(pairs: Pairs, shift: np.ndarray, readout_cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The four depth frequencies (pair means with equal weights, corrected to the model's readout) and their
    covariance: the pair variances scaled by PHI on the diagonal and the readout common-mode covariance."""
    est = [depth_estimate(pairs[k]) for k in sorted(pairs)]
    y = np.array([e[0] for e in est]) - shift
    return y, np.diag([e[1] for e in est]) + readout_cov


def heterogeneity(pairs: Pairs, phi: float = PHI) -> tuple[float, int]:
    """Chi-square of the pair means of each depth about the depth's mean (binomial variances times phi, the dispersion
    the covariance of the fit assumes): a drift linear in position leaves every pair mean unchanged, so the statistic
    sees what remains: one displaced copy, a symmetric drift, a step. phi = 1 is the binomial gate, which fires on a
    copy of dispersion above 1 whatever the circuit does."""
    total, dof = 0.0, 0
    for k in sorted(pairs):
        means = [pair_mean(p, phi) for p in pairs[k]]
        m = np.array([x[0] for x in means])
        v = float(np.mean([x[1] for x in means]))
        total += float(np.sum((m - m.mean()) ** 2) / v)
        dof += len(means) - 1
    return total, dof


def read_pairs(
    fitter: Fitter,
    pairs: Pairs,
    shift: np.ndarray,
    readout_cov: np.ndarray,
    planned_kept: float,
    delta: float,
    gate_phi: float = PHI,
) -> dict[str, Any]:
    """The preregistered readings on the mirror pairs of the four depths: pair floor, pair-mean heterogeneity gate,
    the readings of decide(), and the leave-one-pair-out influence check (every refit must read the same departure
    category)."""
    keep, dropped = surviving_pairs(pairs, planned_kept)
    out: dict[str, Any] = {"dropped_pairs": dropped}
    depths = tuple(sorted(pairs))
    if any(len(keep[k]) < MIN_PAIRS for k in depths):
        out["departure"] = NO_PAIRS
        return out
    chi2, dof = heterogeneity(keep, gate_phi)
    threshold = float(stats.chi2.isf(ALPHA, dof))
    out["heterogeneity"] = {"chi2": chi2, "dof": dof, "threshold": threshold, "phi": gate_phi}
    if chi2 > threshold:
        out["departure"] = "not evaluated: the mirror pairs of a depth differ by more than their binomial scatter"
        return out
    y, cov = estimates(keep, shift, readout_cov)
    full = decide(fitter, y, cov, delta)
    out |= full
    refits = []
    for k in depths:
        for i in range(len(keep[k])):
            trial = {j: [p for n, p in enumerate(keep[j]) if (j, n) != (k, i)] for j in depths}
            yy, cc = estimates(trial, shift, readout_cov)
            refits.append({"depth": k, "pair": i, "departure": decide(fitter, yy, cc, delta)["departure"]})
    out["influence"] = {"refits": refits, "stands": all(r["departure"] == full["departure"] for r in refits)}
    if not out["influence"]["stands"]:
        fail_gate(out, INFLUENCE_FAIL)
    return out


VALID_READINGS = ("coherent", "geometric", "unresolved")
# T below delta leaves the reading "geometric" or "unresolved" whatever the adequacy of the rotation fit, so the
# contrast tests the adequacy itself.
ADEQUACY_FAIL = "not evaluated: the rotation fit is inadequate (chi-square above its 0.99 quantile)"


def fail_gate(out: dict[str, Any], reason: str) -> dict[str, Any]:
    """A failed gate replaces the departure reading by its reason and keeps the earlier reading beside it."""
    out["departure_before"] = out.get("departure")
    out["departure"] = reason
    return out


def gate_failure(fit: dict[str, Any]) -> str:
    """Why a mark's rotation fit may not enter the contrast: an empty string when every gate passed. The gates are the
    pair floor, readout, pair heterogeneity and influence (each reads "not evaluated"), the box (out of domain) and
    the adequacy of the rotation (non-rotation at T >= delta, ADEQUACY_FAIL below it); the fit of a mark that fails
    one carries no meaning for eps."""
    reading = str(fit.get("departure", "not evaluated: no reading"))
    if reading not in VALID_READINGS:
        return reading
    if "rotation" not in fit or "rotation_se" not in fit:
        return "not evaluated: the rotation fit is missing"
    if fit.get("rotation_adequate") is not True:
        return ADEQUACY_FAIL
    return ""


def mark_contrast(
    fits: dict[str, dict[str, Any]], ratio: float, ratio_interval: Sequence[float] | None = None
) -> dict[str, Any]:
    """The mark contrast of the 101 and 011 fits, read only when both marks pass every gate of gate_failure."""
    if "011" not in fits:
        return {
            "reading": "not evaluated: the case carries no mark 011 arms",
            "z_cz": float("nan"),
            "z_prx": float("nan"),
        }
    failed = {m: gate_failure(fits[m]) for m in ("101", "011")}
    if any(failed.values()):
        why = "; ".join(f"mark {m}: {r}" for m, r in failed.items() if r)
        return {"reading": f"not evaluated: {why}", "z_cz": float("nan"), "z_prx": float("nan"), "ratio": ratio}
    a, b = fits["101"], fits["011"]
    return contrast(
        a["rotation"]["eps"],
        a["rotation_se"].get("eps", float("nan")),
        b["rotation"]["eps"],
        b["rotation_se"].get("eps", float("nan")),
        ratio,
        ratio_interval=ratio_interval,
    )


def contrast(
    eps_a: float,
    se_a: float,
    eps_b: float,
    se_b: float,
    ratio: float,
    z_consistent: float = 2.0,
    z_reject: float = 3.0,
    ratio_interval: Sequence[float] | None = None,
) -> dict[str, Any]:
    """The mark contrast beside the departure: a CZ conditional phase leaves the plane of mark 011 unrotated
    (eps_011 = 0) while a PRX amplitude rotates it by ratio times eps_101. The ratio is a model slope that varies with
    the size of the amplitude error: ratio_interval (low, high) carries that range, a PRX amplitude counts as rejected
    only when it is rejected at every ratio of the interval and as consistent when some ratio of it is consistent.
    It decides nothing."""
    if not all(math.isfinite(x) and x > 0 for x in (se_a, se_b)):
        return {"reading": "unresolved: a standard error is not defined", "z_cz": float("nan"), "z_prx": float("nan")}
    low, high = (ratio, ratio) if ratio_interval is None else (min(ratio_interval), max(ratio_interval))

    def z_at(r: float) -> float:
        return (eps_b - r * eps_a) / math.hypot(se_b, r * se_a)

    z_cz = eps_b / se_b
    z_prx = z_at(ratio)
    grid = [z_at(low + (high - low) * i / 8) for i in range(9)]
    # the ratio of the interval that the data like best (zero when z changes sign inside the interval)
    best = 0.0 if min(grid) < 0 < max(grid) else min(abs(z) for z in grid)
    if abs(z_cz) <= z_consistent and best >= z_reject:
        reading = "CZ-phase-like (PRX amplitude rejected)"
    elif best <= z_consistent and abs(z_cz) >= z_reject:
        reading = "PRX-like (CZ phase rejected)"
    else:
        reading = "unresolved"
    return {
        "reading": reading,
        "z_cz": z_cz,
        "z_prx": z_prx,
        "z_prx_nearest": best,
        "z_prx_range": [min(grid), max(grid)],
        "ratio": ratio,
        "ratio_interval": [low, high],
    }
