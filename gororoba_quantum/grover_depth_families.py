"""Retention families for Grover depth on a three-qubit line, and the preregistered verdict between them.

A Grover iteration on eight states marked at one string rotates the amplitude by 2 asin(1 / sqrt 8), so the ideal
marked probability after k iterations is P_k = sin^2((2k + 1) asin(1 / sqrt 8)). A noisy run reads a marked
frequency p_k, whose retention is lambda_k = (p_k - 1/8) / (P_k - 1/8). The exact density-matrix model of the case's
calibration (incoherent depolarizing, idle decay and readout, no coherent error) gives a reference retention M_k
that is not itself geometric in k, so the families describe the ratio rho_k = lambda_k / M_k, which is 1 at every
depth when the model holds:

- geometric: rho_k = a s^k, an incoherent loss beyond the model that compounds per iteration, with free amplitude a
  and rate s;
- coherent: rho_k = s^k (Q_k(eps) - 1/8) / (P_k - 1/8), where Q_k(eps) is the marked probability when the oracle's
  phase of pi carries a fixed error eps per iteration (the rotation of the Grover subspace then departs from the
  ideal angle by an amount that grows with k) and s is an incoherent rate. eps = 0 gives s^k.

Both families have two parameters, so a fit to four depths leaves two degrees of freedom. verdict() applies the
preregistered rule: the difference of the two chi-squares decides at the calibrated threshold delta_resolve
(grover_depth_calibration.py fixes it for a stated misclassification rate), and a family whose chi-square exceeds
ADEQUACY (the 0.99 quantile at two degrees of freedom) does not describe the data.

Readout. The case's model carries the assignment matrix of its calibration. The eight readout preparations of the job
measure the marked row of the job's own matrix, r_j = P(marked read | state j prepared); the model's depth-k
distribution decomposes over the preparations as p_k = sum_j q_kj r_j with q_k = A^-1 (model distribution of depth
k), A the matrix of the model's readout predictions. The marked frequency of each depth is corrected to the model's
readout by y_k = p_k - sum_j q_kj (r_j - r_j model), and the binomial variances of the depths gain the common-mode
covariance sum_j q_kj q_lj r_j (1 - r_j) / n_j of the eight measured rows; every statistic below takes the full
covariance of the four depths, never four independent standard errors.
"""

from __future__ import annotations

import functools
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from parallel import ordered_map

THETA = math.asin(1 / math.sqrt(8))
DEPTHS = (1, 2, 3, 4)
Z_RESOLVE = 3.0
# chi-square 0.99 quantile at two degrees of freedom: -2 ln 0.01.
ADEQUACY = -2 * math.log(0.01)
# chi-square 0.99 quantiles at one and two degrees of freedom: the fits of three and four usable depths.
ADEQUACY_BY_DOF = {1: 6.634897, 2: ADEQUACY}
# Parameter domains of the two fits: the families of the preregistered rule are these boxes. A fit whose optimum
# sits on a rate bound is the box's best, not the family's, so it blocks a reading only when it would be the reading
# (select_family). The offset eps of the coherent family is periodic over (-pi, pi], so its grid ends are no bound.
GEOMETRIC_RATE = (0.30, 1.20)
COHERENT_RATE = (0.50, 1.10)
BOUND_TOLERANCE = 1e-9
# A copy that keeps fewer than this fraction of its planned kept shots, and the copy at its mirrored position,
# leave the pooled depth together.
COPY_FLOOR = 0.5
# Significance level of the pair-heterogeneity gate (chi-square of every depth's mirror pairs about its pooled
# frequency).
HETEROGENEITY_ALPHA = 0.01
FREQUENCY_FLOOR = 1e-9
# Grid of the coherent fit: 1571 steps of the whole period of eps (the half period is searched), then a fine grid
# around the minimum.
COARSE_EPS = 1571
COARSE_RATE = 241


def ideal_marked(k: int) -> float:
    return math.sin((2 * k + 1) * THETA) ** 2


def retention_scale(k: int) -> float:
    """P_k - 1/8, the span between the ideal marked probability and the uniform floor."""
    return ideal_marked(k) - 1 / 8


def retention(p: float, k: int) -> float:
    return (p - 1 / 8) / retention_scale(k)


def probability_of(lam: float, k: int) -> float:
    """Marked frequency that retention lam reads at depth k."""
    return 1 / 8 + lam * retention_scale(k)


def standard_error(lam: float, k: int, kept: float) -> float:
    """Binomial standard error of the retention at depth k from kept shots, at the frequency lam implies."""
    p = probability_of(lam, k)
    return math.sqrt(p * (1 - p) / kept) / abs(retention_scale(k))


def oracle_phase_probability(k: int, eps: np.ndarray) -> np.ndarray:
    """Marked probability after k iterations whose oracle phase is pi + eps (eps an array), from the uniform
    start: the Grover subspace of the marked string and its orthogonal complement carries the whole state."""
    s, c = math.sin(THETA), math.cos(THETA)
    marked = np.full(eps.shape, s, dtype=complex)
    rest = np.full(eps.shape, c, dtype=complex)
    phase = np.exp(1j * (math.pi + eps))
    for _ in range(k):
        marked = marked * phase
        overlap = s * marked + c * rest
        marked = marked - 2 * s * overlap
        rest = rest - 2 * c * overlap
    return np.asarray(np.abs(marked) ** 2)


def coherent_retention(r: np.ndarray, eps: np.ndarray, k: int) -> np.ndarray:
    return np.asarray(r**k * (oracle_phase_probability(k, eps) - 1 / 8) / retention_scale(k))


def chi2(model: np.ndarray, lam: Sequence[float] | np.ndarray, se: Sequence[float] | np.ndarray) -> np.ndarray:
    """Sum over the last axis of ((model - lam) / se)^2."""
    return np.asarray(np.sum(((model - np.asarray(lam)) / np.asarray(se)) ** 2, axis=-1))


def precision(err: Sequence[float] | np.ndarray) -> np.ndarray:
    """The inverse covariance of a fit's inputs: err is a vector of standard errors or a covariance matrix."""
    arr = np.asarray(err, dtype=float)
    if arr.ndim == 1:
        return np.asarray(np.diag(1 / arr**2))
    return np.asarray(np.linalg.inv(arr))


def coherent_surface(
    basis: np.ndarray, rates: np.ndarray, ks: np.ndarray, lam: np.ndarray, weight: np.ndarray
) -> np.ndarray:
    """chi-square (lam - basis r^k)^T weight (lam - basis r^k) on the grid of basis rows (eps) and rates r, as two
    matrix products: the quadratic term over the products of basis columns and the cross term over the basis."""
    power = rates[:, None] ** ks[None, :]
    n = len(ks)
    second = (weight[None, :, :] * power[:, :, None] * power[:, None, :]).reshape(len(rates), n * n)
    pairs = (basis[:, :, None] * basis[:, None, :]).reshape(len(basis), n * n)
    cross = basis @ ((weight @ lam)[None, :] * power).T
    return np.asarray(pairs @ second.T - 2 * cross + lam @ weight @ lam)


def on_bound(rate: float, domain: tuple[float, float]) -> bool:
    return min(abs(rate - domain[0]), abs(rate - domain[1])) <= BOUND_TOLERANCE


def fit_geometric(lam: Sequence[float], err: Sequence[float] | np.ndarray, ks: Sequence[int]) -> dict[str, Any]:
    """Generalized least squares of lam_k = A r^k, err the standard errors or the covariance of lam: A solves in
    closed form at each r of a fine grid."""
    lam_a, w = np.asarray(lam, dtype=float), precision(err)
    k = np.asarray(ks, dtype=float)

    def profile(r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        basis = r[:, None] ** k[None, :]
        wb = basis @ w
        cross = wb @ lam_a
        amplitude = cross / np.einsum("ri,ri->r", wb, basis)
        return amplitude, float(lam_a @ w @ lam_a) - amplitude * cross

    low, high = GEOMETRIC_RATE
    r = np.linspace(low, high, 9001)
    best = float(r[int(np.argmin(profile(r)[1]))])
    r = np.linspace(max(low, best - 2e-4), min(high, best + 2e-4), 4001)
    amplitude, value = profile(r)
    i = int(np.argmin(value))
    return {
        "A": float(amplitude[i]),
        "r": float(r[i]),
        "chi2": max(0.0, float(value[i])),
        "at_bound": on_bound(float(r[i]), GEOMETRIC_RATE),
    }


def coarse_eps() -> np.ndarray:
    """The coarse grid of the offset eps: the half period [0, pi], since Q_k(-eps) = Q_k(eps) (the start state is
    real, so the oracle phase and its conjugate give conjugate amplitudes), which fixes the sign of a fit."""
    return np.linspace(0.0, math.pi, COARSE_EPS // 2 + 1)


@functools.lru_cache(maxsize=8)
def coarse_basis(k: int) -> np.ndarray:
    """(Q_k(eps) - 1/8) / (P_k - 1/8) on the coarse eps grid, which depends on neither the rate nor the data."""
    return np.asarray((oracle_phase_probability(k, coarse_eps()) - 1 / 8) / retention_scale(k))


def fit_coherent(lam: Sequence[float], err: Sequence[float] | np.ndarray, ks: Sequence[int]) -> dict[str, Any]:
    """Generalized least squares of the coherent family over a coarse grid of (eps, r) on the half period of eps
    (the family is even in eps), then a fine grid around the minimum."""
    lam_a, w = np.asarray(lam, dtype=float), precision(err)
    k = np.asarray(ks, dtype=float)
    low, high = COHERENT_RATE
    eps = coarse_eps()
    r = np.linspace(low, high, COARSE_RATE)
    basis = np.stack([coarse_basis(int(x)) for x in ks], axis=-1)
    surface = coherent_surface(basis, r, k, lam_a, w)
    i, j = np.unravel_index(int(np.argmin(surface)), surface.shape)
    eps = np.linspace(eps[i] - 0.005, eps[i] + 0.005, 401)
    r = np.linspace(max(low, r[j] - 0.0025), min(high, r[j] + 0.0025), 401)
    basis = np.stack([(oracle_phase_probability(int(x), eps) - 1 / 8) / retention_scale(int(x)) for x in ks], axis=-1)
    fine = coherent_surface(basis, r, k, lam_a, w)
    i, j = np.unravel_index(int(np.argmin(fine)), fine.shape)
    return {
        "eps": float(eps[i]),
        "r": float(r[j]),
        "chi2": max(0.0, float(fine[i, j])),
        "at_bound": on_bound(float(r[j]), COHERENT_RATE),
    }


def geometric_values(fit: dict[str, Any], ks: Sequence[int]) -> list[float]:
    return [fit["A"] * fit["r"] ** k for k in ks]


def coherent_values(fit: dict[str, Any], ks: Sequence[int]) -> list[float]:
    eps, r = np.asarray(fit["eps"]), np.asarray(fit["r"])
    return [float(coherent_retention(r, eps, k)) for k in ks]


@dataclass(frozen=True, eq=False)
class ReadoutShift:
    """The job's readout against the case model's: shift[k] is the marked-frequency correction of depth k + 1
    (subtracted from the observed frequency) and cov the 4 x 4 common-mode covariance of the corrected
    frequencies that the eight measured rows of the assignment matrix carry."""

    shift: np.ndarray = field(default_factory=lambda: np.zeros(len(DEPTHS)))
    cov: np.ndarray = field(default_factory=lambda: np.zeros((len(DEPTHS), len(DEPTHS))))


def readout_shift(
    q: Sequence[Sequence[float]] | np.ndarray,
    r_model: Sequence[float] | np.ndarray,
    r_hat: Sequence[float] | np.ndarray,
    shots: Sequence[float] | np.ndarray,
) -> ReadoutShift:
    """The correction of the four depths from the marked row of the job's assignment matrix: q[k][j] is the weight
    of prepared state j in the model's depth k + 1 distribution, r_model[j] and r_hat[j] the model's and the job's
    marked row, shots[j] the kept shots of preparation j. A row at 0 or 1 carries variance 0."""
    q_a, model, hat = np.asarray(q, dtype=float), np.asarray(r_model, dtype=float), np.asarray(r_hat, dtype=float)
    variance = hat * (1 - hat) / np.asarray(shots, dtype=float)
    return ReadoutShift(q_a @ (hat - model), (q_a * variance) @ q_a.T)


def lambda_covariance(
    freq: Sequence[float], ks: Sequence[int], kept: Sequence[float], readout: ReadoutShift | None
) -> np.ndarray:
    """Covariance of the retentions lambda_k at the depths ks: the binomial variance of each depth's corrected
    frequency freq at its kept shots plus the readout covariance, scaled by the retention spans."""
    var = [min(max(f, FREQUENCY_FLOOR), 1 - FREQUENCY_FLOOR) for f in freq]
    cov = np.diag([v * (1 - v) / n for v, n in zip(var, kept, strict=True)])
    if readout is not None:
        index = [k - 1 for k in ks]
        cov = cov + readout.cov[np.ix_(index, index)]
    scale = np.array([retention_scale(k) for k in ks])
    return np.asarray(cov / np.outer(scale, scale))


def ratio_inputs(
    lam: Sequence[float], kept: Sequence[float], model: Sequence[float], readout: ReadoutShift | None = None
) -> tuple[list[float], np.ndarray]:
    """rho_k = lambda_k / M_k and its covariance: the binomial one of lambda_k and the readout's, over M_k M_l."""
    ks = DEPTHS[: len(lam)]
    rho = [x / m for x, m in zip(lam, model, strict=False)]
    cov = lambda_covariance([probability_of(x, k) for x, k in zip(lam, ks, strict=True)], ks, kept, readout)
    m = np.asarray(model[: len(lam)], dtype=float)
    return rho, np.asarray(cov / np.outer(m, m))


def continuations(lam: Sequence[float], kept: Sequence[float], model: Sequence[float]) -> dict[str, Any]:
    """Both families fitted to the ratios rho_1 to rho_len(lam), and each one's value at the next depth."""
    ks = DEPTHS[: len(lam)]
    rho, cov = ratio_inputs(lam, kept, model)
    geo, coh = fit_geometric(rho, cov, ks), fit_coherent(rho, cov, ks)
    nxt = len(lam) + 1
    return {
        "depths": list(ks),
        "rho": rho,
        "se": [float(x) for x in np.sqrt(np.diag(cov))],
        "geometric": geo,
        "coherent": coh,
        "next_depth": nxt,
        "geometric_next": geometric_values(geo, [nxt])[0],
        "coherent_next": coherent_values(coh, [nxt])[0],
    }


def separation(
    truth_geo: dict[str, Any],
    truth_coh: dict[str, Any],
    kept: Sequence[float],
    model: Sequence[float],
    readout: ReadoutShift | None = None,
) -> dict[str, Any]:
    """What the preregistered rule sees when the four retentions equal M_k times each family's ratio at the given
    kept shots: the separation of the two at the last depth in standard errors of rho (binomial and readout), and
    the chi-square the other family leaves."""
    ks = DEPTHS[: len(kept)]
    out: dict[str, Any] = {}
    ratios = {"geometric": geometric_values(truth_geo, ks), "coherent": coherent_values(truth_coh, ks)}
    covs = {}
    for name, rho in ratios.items():
        lam = [r * m for r, m in zip(rho, model, strict=True)]
        covs[name] = ratio_inputs(lam, kept, model, readout)[1]
    last = ratios["geometric"][-1] - ratios["coherent"][-1]
    out["last_depth_difference"] = last
    out["last_depth_z"] = last / max(math.sqrt(c[-1, -1]) for c in covs.values())
    out["chi2_geometric_on_coherent_data"] = fit_geometric(ratios["coherent"], covs["coherent"], ks)["chi2"]
    out["chi2_coherent_on_geometric_data"] = fit_coherent(ratios["geometric"], covs["geometric"], ks)["chi2"]
    return out


def bend(lam: Sequence[float], kept: Sequence[float], readout: ReadoutShift | None = None) -> tuple[float, float]:
    """f = lam_3 - lam_2^2 / lam_1 over the first three depths, zero under lam_k = A r^k, and its delta-method
    standard error from the covariance of the three depths (binomial, and the readout's when given)."""
    l1, l2, l3 = lam[:3]
    cov = lambda_covariance(
        [probability_of(x, k) for x, k in zip(lam[:3], DEPTHS, strict=False)], DEPTHS[:3], kept[:3], readout
    )
    gradient = np.array([l2**2 / l1**2, -2 * l2 / l1, 1.0])
    return l3 - l2**2 / l1, math.sqrt(float(gradient @ cov @ gradient))


FAMILY_CATEGORIES = ("coherent", "geometric", "unresolved", "neither family fits", "out of domain", "not evaluated")


def category_of(reading: str) -> str:
    """The category a reading string names: the text before its first colon."""
    return reading.split(":", 1)[0]


def select_family(geo: dict[str, Any], coh: dict[str, Any], dof: int, delta_resolve: float) -> tuple[str, list[str]]:
    """The family reading from the two fits, and the names of the fits that end on a rate bound.

    Selection. 'neither family fits' when both chi-squares exceed ADEQUACY_BY_DOF[dof]; else 'coherent' when the
    geometric chi-square minus the coherent one reaches delta_resolve, 'geometric' when it reaches -delta_resolve,
    else 'unresolved'.

    Bounds. A rate bound blocks a reading only when the bound-limited fit is what the reading rests on: the
    selected family's own fit sits on its bound ('out of domain: the X fit ends on its rate bound'), or no family is
    selected ('neither family fits', 'unresolved') while a fit sits on a bound, since the box rather than the data
    may have ended that fit's search and its unbounded chi-square could have decided the comparison. A bound-limited
    fit that loses to an adequate interior fit by delta_resolve does not block; it is named in the returned list and
    reported beside the reading."""
    bounded = [name for name, fit in (("geometric", geo), ("coherent", coh)) if fit["at_bound"]]
    delta = geo["chi2"] - coh["chi2"]
    if min(geo["chi2"], coh["chi2"]) > ADEQUACY_BY_DOF[dof]:
        reading = "neither family fits"
    elif delta >= delta_resolve:
        reading = "coherent"
    elif delta <= -delta_resolve:
        reading = "geometric"
    else:
        reading = "unresolved"
    if reading in bounded or (bounded and reading in ("neither family fits", "unresolved")):
        subject = (
            "the geometric and coherent fits end on their rate bounds"
            if len(bounded) == 2
            else f"the {bounded[0]} fit ends on its rate bound"
        )
        return f"out of domain: {subject}", bounded
    return reading, bounded


def bend_reading(z: float) -> str:
    if z <= -Z_RESOLVE:
        return "the retention law bends beyond the model at mirrored positions"
    if z >= Z_RESOLVE:
        return "the retention law bends upward of the model at mirrored positions"
    return "no bend beyond the model resolved at mirrored positions"


def bend_decision(
    freq: Mapping[int, float], kept: Mapping[int, float], model: Sequence[float], readout: ReadoutShift | None
) -> dict[str, Any]:
    """The bend of the retention law at depths 1, 2 and 3 against the model's, or 'not evaluated' without all three."""
    if not all(k in freq for k in (1, 2, 3)):
        return {"reading": "not evaluated: a depth of 1, 2 or 3 is unusable"}
    l1, l2, l3 = (retention(freq[k], k) for k in (1, 2, 3))
    cov = lambda_covariance([freq[k] for k in (1, 2, 3)], (1, 2, 3), [kept[k] for k in (1, 2, 3)], readout)
    gradient = np.array([l2**2 / l1**2, -2 * l2 / l1, 1.0])
    f = l3 - l2**2 / l1
    f_se = math.sqrt(float(gradient @ cov @ gradient))
    m1, m2, m3 = model[:3]
    z_bend = (f - (m3 - m2**2 / m1)) / f_se
    return {
        "f": round(f, 6),
        "se": round(f_se, 6),
        "z_against_model": round(z_bend, 4),
        "reading": bend_reading(z_bend),
    }


def fit_families(
    freq: Mapping[int, float], kept: Mapping[int, float], model: Sequence[float], readout: ReadoutShift | None
) -> tuple[dict[str, Any], dict[str, Any], list[float], np.ndarray]:
    """Both families fitted to the ratios rho_k = lambda_k / M_k of the usable depths in freq, with the covariance
    of the ratios: the geometric fit, the coherent fit, rho and its covariance."""
    usable = sorted(freq)
    at = {k: i for i, k in enumerate(DEPTHS)}
    cov_lam = lambda_covariance([freq[k] for k in usable], usable, [kept[k] for k in usable], readout)
    m = np.array([model[at[k]] for k in usable])
    rho = [retention(freq[k], k) / model[at[k]] for k in usable]
    cov_rho = cov_lam / np.outer(m, m)
    return fit_geometric(rho, cov_rho, usable), fit_coherent(rho, cov_rho, usable), rho, np.asarray(cov_rho)


def decide(
    freq: Mapping[int, float],
    kept: Mapping[int, float],
    model: Sequence[float],
    retained: Mapping[str, Any],
    delta_resolve: float,
    readout: ReadoutShift | None = None,
) -> dict[str, Any]:
    """The preregistered decisions on the corrected marked frequencies freq[k] of the usable depths (those in freq)
    and their kept shots, against the model's retentions M_1 to M_4. verdict() builds freq from pooled counts;
    the calibration of delta_resolve calls this function on sampled frequencies."""
    usable = sorted(freq)
    lam = {k: retention(freq[k], k) for k in usable}
    cov_lam = lambda_covariance([freq[k] for k in usable], usable, [kept[k] for k in usable], readout)
    se = {k: math.sqrt(float(cov_lam[i, i])) for i, k in enumerate(usable)}
    out: dict[str, Any] = {
        "usable_depths": usable,
        "lambda": {str(k): round(x, 6) for k, x in lam.items()},
        "se": {str(k): round(x, 6) for k, x in se.items()},
    }
    out["bend"] = bend_decision(freq, kept, model, readout)
    if len(usable) < 3:
        out["family"] = "not evaluated: fewer than three usable depths"
        return out
    geo, coh, rho, cov_rho = fit_families(freq, kept, model, readout)
    delta = geo["chi2"] - coh["chi2"]
    family, bounded = select_family(geo, coh, len(usable) - 2, delta_resolve)
    out |= {
        "rho": [round(x, 6) for x in rho],
        "geometric": rounded_fit(geo),
        "coherent": rounded_fit(coh),
        "delta_chi2": round(delta, 4),
        "family": family,
        "beside": {
            "retention_decreases_with_depth": all(lam[a] > lam[b] for a, b in zip(usable, usable[1:], strict=False)),
            "fits_on_a_rate_bound": bounded,
        },
    }
    if 4 in lam:
        i4 = usable.index(4)
        r4, s4 = lam[4] / model[3], math.sqrt(float(cov_rho[i4, i4]))
        out["beside"] |= {
            "rho4_against_retained_geometric_z": round((r4 - retained["geometric_next"]) / s4, 4),
            "rho4_against_retained_coherent_z": round((r4 - retained["coherent_next"]) / s4, 4),
        }
    return out


def verdict(
    marked: Sequence[int],
    kept: Sequence[int],
    model: Sequence[float],
    retained: Mapping[str, Any],
    delta_resolve: float,
    readout: ReadoutShift | None = None,
) -> dict[str, Any]:
    """The preregistered decisions on pooled counts at depths 1 to 4 (the marked count and the kept shots of each
    depth, usable copies pooled; a depth with no kept shot is unusable and reads 0 and 0) against the model's
    retentions M_1 to M_4, with the readout correction and covariance of the job's readout preparations.

    Gating. Each decision uses the depths it needs and no others, so one unusable depth removes only what needs it:
    the bend needs depths 1, 2 and 3; the family comparison fits the usable depths and needs three of the four, with
    n - 2 degrees of freedom for n usable depths (ADEQUACY_BY_DOF). A decision whose depths are unusable reads
    "not evaluated" and leaves the other decision standing.

    bend: f = lam_3 - lam_2^2 / lam_1 against the model's f, resolved at |z| >= Z_RESOLVE; a negative resolved f
    means the retention law bends beyond the model with every depth arm at positions mirrored about the center.
    family: chi-square of the geometric and coherent fits to the usable ratios rho_k = lam_k / M_k, read by
    select_family at delta_resolve. Both fits read the same counts, so their chi-squares covary through the data and
    the difference is taken on that one data set; the depth arms are separate circuits, so the binomial parts of lam_k
    are independent, and the readout correction ties them through its covariance. The retained continuations of rho
    at depth 4 and the monotonicity of the retention are reported beside and decide nothing."""
    if not (len(marked) == len(kept) == len(model) == len(DEPTHS)) or any(
        m < 0 or n < 0 or m > n for m, n in zip(marked, kept, strict=True)
    ):
        raise ValueError("the verdict needs the marked count and the kept shots of each of four depths")
    shift = np.zeros(len(DEPTHS)) if readout is None else readout.shift
    freq = {k: marked[i] / kept[i] - float(shift[i]) for i, k in enumerate(DEPTHS) if kept[i] > 0}
    return decide(freq, {k: float(kept[k - 1]) for k in freq}, model, retained, delta_resolve, readout)


def rounded_fit(fit: dict[str, Any]) -> dict[str, Any]:
    return {key: value if isinstance(value, bool) else round(value, 6) for key, value in fit.items()}


def model_retention(arms: Mapping[str, Any]) -> list[float]:
    """The model's retention at depths 1 to 4, from the mean predicted marked probability of each depth's copies
    in the case's prediction arms (names m101-kK-cN)."""
    out = []
    for k in DEPTHS:
        marked = [a["predicted_marked"] for name, a in arms.items() if name.startswith(f"m101-k{k}-c")]
        if not marked:
            raise ValueError(f"the prediction has no arm of depth {k}")
        out.append(retention(float(np.mean(marked)), k))
    return out


# One copy of a depth: its position in the job, its marked count and its kept shots.
Copy = tuple[int, int, int]
Pair = tuple[Copy, Copy]


def mirror_pairs(copies: Sequence[Copy], total: int) -> list[Pair]:
    """The copies of one depth as pairs of positions p and total - 1 - p, the images of each other about the job's
    center. A copy without its image, or at the center, leaves the design unpaired and raises."""
    at = {c[0]: c for c in copies}
    if len(at) != len(copies):
        raise ValueError("two copies share a position")
    pairs = []
    for position in sorted(at):
        partner = total - 1 - position
        if partner not in at or partner == position:
            raise ValueError(f"the copy at position {position} has no mirror image at {partner}")
        if position < partner:
            pairs.append((at[position], at[partner]))
    return pairs


def heterogeneity_threshold(dof: int, alpha: float = HETEROGENEITY_ALPHA) -> float:
    """The chi-square quantile of level 1 - alpha at dof degrees of freedom, which prediction.json records for
    every dof the gate can meet."""
    from scipy import stats

    return float(stats.chi2.isf(alpha, dof))


def pair_heterogeneity(pairs: Sequence[Pair]) -> tuple[float, int]:
    """Chi-square of the mirror pairs of one depth about the pooled frequency, with len(pairs) - 1 degrees of
    freedom: the sum over pairs of (M - N p)^2 / (N p (1 - p)), with M and N the marked count and kept shots of the
    pair's two copies and p the pooled marked frequency. A drift linear in position moves the copy at position q and
    its image at total - 1 - q in opposite directions, so it leaves every pair's frequency, and this statistic,
    unchanged. A pooled frequency of 0 or 1 leaves no variance to test and reads 0."""
    marked = sum(a[1] + b[1] for a, b in pairs)
    kept = sum(a[2] + b[2] for a, b in pairs)
    if not pairs or kept <= 0:
        return 0.0, 0
    p = marked / kept
    if p <= 0.0 or p >= 1.0:
        return 0.0, len(pairs) - 1
    chi2_sum = sum((a[1] + b[1] - (a[2] + b[2]) * p) ** 2 / ((a[2] + b[2]) * p * (1 - p)) for a, b in pairs)
    return chi2_sum, len(pairs) - 1


def pooled_counts(
    surviving: Mapping[int, Sequence[Pair]], leave: tuple[int, int] | None = None
) -> tuple[list[int], list[int]]:
    """Marked counts and kept shots of the four depths over the surviving pairs, without the pair leave = (depth,
    index of the pair in its depth) when given."""
    marked, kept = [], []
    for k in DEPTHS:
        pairs = [p for i, p in enumerate(surviving[k]) if leave != (k, i)]
        marked.append(sum(a[1] + b[1] for a, b in pairs))
        kept.append(sum(a[2] + b[2] for a, b in pairs))
    return marked, kept


def refit(task: tuple[Any, ...]) -> dict[str, Any]:
    """verdict() of one leave-one-pair-out task (marked, kept, model, retained, delta_resolve, readout)."""
    return verdict(*task)


def read_copies(
    copies: Mapping[int, Sequence[Copy]],
    total: int,
    planned_kept: float,
    model: Sequence[float],
    retained: dict[str, Any],
    gate: Mapping[str, Any],
    delta_resolve: float,
    readout: ReadoutShift | None = None,
) -> dict[str, Any]:
    """The preregistered decisions on the copies of every depth.

    Mirror pairs. A pair leaves its depth when either copy keeps fewer than gate["copy_floor"] times planned_kept
    shots, so the surviving positions of every depth stay centered on the job and a drift linear in position
    leaves each pooled frequency unchanged. A depth without a surviving pair is unusable.

    Heterogeneity. The chi-square of the surviving mirror pairs of every depth about that depth's pooled frequency
    (pair_heterogeneity), summed over depths, has sum(pairs - 1) degrees of freedom and is compared with
    gate["threshold_by_dof"][dof], the 1 - alpha chi-square quantile fixed in prediction.json. The statistic is
    blind to a drift linear in position, which the pairing cancels from the pooled frequencies, and sees what the
    pairing leaves: a copy that departs from its image's partner pairs, a symmetric (quadratic) drift, a step.
    Above the threshold the pairs of a depth differ by more than their binomial scatter, a pooled frequency no
    longer describes the depth, and the bend and family decisions read "not evaluated". A design with no depth of
    two surviving pairs has no test and reads "not evaluated" as well.

    Influence. The pooled frequencies pass the heterogeneity gate by their sum, which a single defective pair can
    stay under while it moves a decision. Each decision therefore stands only when every leave-one-pair-out refit
    (the pooled verdict without one surviving pair, each refit with the same readout correction) reads the same
    category: the family category of select_family, and the bend's resolved direction or none. A reading that
    changes when one pair leaves is "not evaluated: the reading depends on one mirror pair" and the full reading is
    kept beside it. A depth with one surviving pair cannot lose it without becoming unusable, so its refit reads
    "not evaluated" and the decisions that need that depth do not stand either.

    Otherwise verdict() decides on the pooled counts."""
    if set(copies) != set(DEPTHS):
        raise ValueError(f"copies cover depths {sorted(copies)}, not {list(DEPTHS)}")
    floor = float(gate["copy_floor"]) * planned_kept
    surviving: dict[int, list[Pair]] = {}
    dropped: dict[str, list[list[int]]] = {}
    for k in DEPTHS:
        keep: list[Pair] = []
        for first, second in mirror_pairs(copies[k], total):
            if first[2] >= floor and second[2] >= floor:
                keep.append((first, second))
            else:
                dropped.setdefault(str(k), []).append([first[0], second[0]])
        surviving[k] = keep
    stats_by_depth = {k: pair_heterogeneity(surviving[k]) for k in DEPTHS}
    statistic = sum(s for s, _ in stats_by_depth.values())
    dof = sum(d for _, d in stats_by_depth.values())
    threshold = gate["threshold_by_dof"].get(str(dof)) if dof else None
    block: dict[str, Any] = {
        "per_depth": {
            str(k): {"chi2": round(s, 6), "dof": d, "pairs": len(surviving[k])} for k, (s, d) in stats_by_depth.items()
        },
        "chi2": round(statistic, 6),
        "dof": dof,
        "threshold": threshold,
    }
    if threshold is None:
        block["passed"] = False
        reason = "not evaluated: no depth keeps two mirror pairs, so pair heterogeneity cannot be tested"
    elif statistic > threshold:
        block["passed"] = False
        reason = "not evaluated: the mirror pairs of a depth differ by more than their binomial scatter"
    else:
        block["passed"] = True
        reason = ""
    marked, kept = pooled_counts(surviving)
    out: dict[str, Any] = {"dropped_pairs": dropped, "heterogeneity": block}
    if reason:
        out |= {
            "usable_depths": [k for k, n in zip(DEPTHS, kept, strict=True) if n > 0],
            "bend": {"reading": reason},
            "family": reason,
        }
        return out
    full = verdict(marked, kept, model, retained, delta_resolve, readout)
    leaves = [(k, i) for k in DEPTHS for i in range(len(surviving[k]))]
    refits = ordered_map(
        refit,
        [(*pooled_counts(surviving, leave), model, retained, delta_resolve, readout) for leave in leaves],
        min_items=1,
    )
    rows = [
        {
            "depth": k,
            "positions": [surviving[k][i][0][0], surviving[k][i][1][0]],
            "bend": bend_category(r["bend"]["reading"]),
            "family": category_of(r["family"]),
        }
        for (k, i), r in zip(leaves, refits, strict=True)
    ]
    bend_full = bend_category(full["bend"]["reading"])
    family_full = category_of(full["family"])
    bend_stands = all(row["bend"] == bend_full for row in rows)
    family_stands = all(row["family"] == family_full for row in rows)
    out |= full
    out["influence"] = {
        "refits": rows,
        "bend_stands": bend_stands,
        "family_stands": family_stands,
    }
    changed = "not evaluated: the reading depends on one mirror pair"
    if not bend_stands:
        out["influence"]["bend_before"] = full["bend"]["reading"]
        out["bend"] = {**full["bend"], "reading": changed}
    if not family_stands:
        out["influence"]["family_before"] = full["family"]
        out["family"] = changed
    return out


def bend_category(reading: str) -> str:
    """The direction a bend reading resolves, or 'none' or 'not evaluated'."""
    if reading.startswith("not evaluated"):
        return "not evaluated"
    if "beyond" in reading and "no bend" not in reading:
        return "beyond"
    return "upward" if "upward" in reading else "none"
