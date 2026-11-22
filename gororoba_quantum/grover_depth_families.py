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
preregistered rule: the difference of the two chi-squares decides at DELTA_RESOLVE (9, the square of Z_RESOLVE), and a
family whose chi-square exceeds ADEQUACY (the 0.99 quantile at two degrees of freedom) does not describe the data.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

THETA = math.asin(1 / math.sqrt(8))
DEPTHS = (1, 2, 3, 4)
Z_RESOLVE = 3.0
DELTA_RESOLVE = Z_RESOLVE**2
# chi-square 0.99 quantile at two degrees of freedom: -2 ln 0.01.
ADEQUACY = -2 * math.log(0.01)
# chi-square 0.99 quantiles at one and two degrees of freedom: the fits of three and four usable depths.
ADEQUACY_BY_DOF = {1: 6.634897, 2: ADEQUACY}
# Parameter domains of the two fits. A fit whose optimum sits on a rate bound is cut off by the search box, so
# its chi-square exceeds the one the family reaches outside the box and the comparison reads "out of domain".
# The offset eps of the coherent family is periodic over (-pi, pi], so its grid ends are no bound.
GEOMETRIC_RATE = (0.30, 1.20)
COHERENT_RATE = (0.50, 1.10)
BOUND_TOLERANCE = 1e-9
# A copy that keeps fewer than this fraction of its planned kept shots, and the copy at its mirrored position,
# leave the pooled depth together.
COPY_FLOOR = 0.5
# Significance level of the copy-heterogeneity gate (chi-square over every depth's copies about its pooled frequency).
HETEROGENEITY_ALPHA = 0.01


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


def on_bound(rate: float, domain: tuple[float, float]) -> bool:
    return min(abs(rate - domain[0]), abs(rate - domain[1])) <= BOUND_TOLERANCE


def fit_geometric(lam: Sequence[float], se: Sequence[float], ks: Sequence[int]) -> dict[str, Any]:
    """Weighted least squares of lam_k = A r^k: A solves in closed form at each r of a fine grid."""
    lam_a, w = np.asarray(lam, dtype=float), 1 / np.asarray(se, dtype=float) ** 2
    k = np.asarray(ks, dtype=float)

    def profile(r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        basis = r[:, None] ** k[None, :]
        amplitude = np.sum(w * lam_a * basis, axis=1) / np.sum(w * basis**2, axis=1)
        return amplitude, chi2(amplitude[:, None] * basis, lam_a, 1 / np.sqrt(w))

    low, high = GEOMETRIC_RATE
    r = np.linspace(low, high, 9001)
    best = float(r[int(np.argmin(profile(r)[1]))])
    r = np.linspace(max(low, best - 2e-4), min(high, best + 2e-4), 4001)
    amplitude, value = profile(r)
    i = int(np.argmin(value))
    return {
        "A": float(amplitude[i]),
        "r": float(r[i]),
        "chi2": float(value[i]),
        "at_bound": on_bound(float(r[i]), GEOMETRIC_RATE),
    }


def fit_coherent(lam: Sequence[float], se: Sequence[float], ks: Sequence[int]) -> dict[str, Any]:
    """Weighted least squares of the coherent family over a coarse grid of (eps, r) on the whole period of eps,
    then a fine grid around the minimum."""
    lam_a, se_a = np.asarray(lam, dtype=float), np.asarray(se, dtype=float)

    def surface(eps: np.ndarray, r: np.ndarray) -> np.ndarray:
        e, rr = np.meshgrid(eps, r, indexing="ij")
        model = np.stack([coherent_retention(rr, e, k) for k in ks], axis=-1)
        return chi2(model, lam_a, se_a)

    low, high = COHERENT_RATE
    eps = np.linspace(-math.pi, math.pi, 1571)
    r = np.linspace(low, high, 241)
    i, j = np.unravel_index(int(np.argmin(surface(eps, r))), (eps.size, r.size))
    eps = np.linspace(eps[i] - 0.005, eps[i] + 0.005, 401)
    r = np.linspace(max(low, r[j] - 0.0025), min(high, r[j] + 0.0025), 401)
    fine = surface(eps, r)
    i, j = np.unravel_index(int(np.argmin(fine)), fine.shape)
    return {
        "eps": float(eps[i]),
        "r": float(r[j]),
        "chi2": float(fine[i, j]),
        "at_bound": on_bound(float(r[j]), COHERENT_RATE),
    }


def geometric_values(fit: dict[str, Any], ks: Sequence[int]) -> list[float]:
    return [fit["A"] * fit["r"] ** k for k in ks]


def coherent_values(fit: dict[str, Any], ks: Sequence[int]) -> list[float]:
    eps, r = np.asarray(fit["eps"]), np.asarray(fit["r"])
    return [float(coherent_retention(r, eps, k)) for k in ks]


def ratio_inputs(
    lam: Sequence[float], kept: Sequence[float], model: Sequence[float]
) -> tuple[list[float], list[float]]:
    """rho_k = lambda_k / M_k and its standard error, the binomial one of lambda_k over M_k."""
    ks = DEPTHS[: len(lam)]
    rho = [x / m for x, m in zip(lam, model, strict=False)]
    se = [standard_error(x, k, n) / m for x, k, n, m in zip(lam, ks, kept, model, strict=False)]
    return rho, se


def continuations(lam: Sequence[float], kept: Sequence[float], model: Sequence[float]) -> dict[str, Any]:
    """Both families fitted to the ratios rho_1 to rho_len(lam), and each one's value at the next depth."""
    ks = DEPTHS[: len(lam)]
    rho, se = ratio_inputs(lam, kept, model)
    geo, coh = fit_geometric(rho, se, ks), fit_coherent(rho, se, ks)
    nxt = len(lam) + 1
    return {
        "depths": list(ks),
        "rho": rho,
        "se": se,
        "geometric": geo,
        "coherent": coh,
        "next_depth": nxt,
        "geometric_next": geometric_values(geo, [nxt])[0],
        "coherent_next": coherent_values(coh, [nxt])[0],
    }


def separation(
    truth_geo: dict[str, Any], truth_coh: dict[str, Any], kept: Sequence[float], model: Sequence[float]
) -> dict[str, Any]:
    """What the preregistered rule sees when the four retentions equal M_k times each family's ratio at the given
    kept shots: the separation of the two at the last depth in standard errors of rho, and the chi-square the
    other family leaves."""
    ks = DEPTHS[: len(kept)]
    out: dict[str, Any] = {}
    ratios = {"geometric": geometric_values(truth_geo, ks), "coherent": coherent_values(truth_coh, ks)}
    ses = {}
    for name, rho in ratios.items():
        lam = [r * m for r, m in zip(rho, model, strict=True)]
        ses[name] = ratio_inputs(lam, kept, model)[1]
    last = ratios["geometric"][-1] - ratios["coherent"][-1]
    out["last_depth_difference"] = last
    out["last_depth_z"] = last / max(ses["geometric"][-1], ses["coherent"][-1])
    out["chi2_geometric_on_coherent_data"] = fit_geometric(ratios["coherent"], ses["coherent"], ks)["chi2"]
    out["chi2_coherent_on_geometric_data"] = fit_coherent(ratios["geometric"], ses["geometric"], ks)["chi2"]
    return out


def bend(lam: Sequence[float], kept: Sequence[float]) -> tuple[float, float]:
    """f = lam_3 - lam_2^2 / lam_1 over the first three depths, zero under lam_k = A r^k, and its delta-method
    standard error over the three independent depths."""
    l1, l2, l3 = lam[:3]
    se = [standard_error(x, k, n) for x, k, n in zip(lam[:3], DEPTHS, kept, strict=False)]
    gradient = (l2**2 / l1**2, -2 * l2 / l1, 1.0)
    return l3 - l2**2 / l1, math.sqrt(sum((g * s) ** 2 for g, s in zip(gradient, se, strict=True)))


def verdict(
    marked: Sequence[int], kept: Sequence[int], model: Sequence[float], retained: dict[str, Any]
) -> dict[str, Any]:
    """The preregistered decisions on pooled counts at depths 1 to 4 (the marked count and the kept shots of each
    depth, usable copies pooled; a depth with no kept shot is unusable and reads 0 and 0) against the model's
    retentions M_1 to M_4.

    Gating. Each decision uses the depths it needs and no others, so one unusable depth removes only what needs it:
    the bend needs depths 1, 2 and 3; the family comparison fits the usable depths and needs three of the four, with
    n - 2 degrees of freedom for n usable depths (ADEQUACY_BY_DOF). A decision whose depths are unusable reads
    "not evaluated" and leaves the other decision standing.

    bend: f = lam_3 - lam_2^2 / lam_1 against the model's f, resolved at |z| >= Z_RESOLVE; a negative resolved f
    means the retention law bends beyond the model with every depth arm at positions mirrored about the center.
    family: chi-square of the geometric and coherent fits to the usable ratios rho_k = lam_k / M_k. "neither family
    fits" when both exceed ADEQUACY_BY_DOF; else "coherent" when geometric minus coherent reaches DELTA_RESOLVE,
    "geometric" when it reaches -DELTA_RESOLVE, else "unresolved"; a fit whose rate sits on its domain bound
    (GEOMETRIC_RATE, COHERENT_RATE) reads "out of domain" and decides nothing, since the bound, not the data, ended
    its search and the other chi-square comparison would then favor the other family. Both fits read the same
    counts, so their chi-squares covary through the data and the difference is taken on that one data set; the
    depth arms are separate circuits, so lam_k are independent. The retained continuations of rho at depth 4 and the
    monotonicity of the retention are reported beside and decide nothing."""
    if not (len(marked) == len(kept) == len(model) == len(DEPTHS)) or any(
        m < 0 or n < 0 or m > n for m, n in zip(marked, kept, strict=True)
    ):
        raise ValueError("the verdict needs the marked count and the kept shots of each of four depths")
    usable = [k for k, n in zip(DEPTHS, kept, strict=True) if n > 0]
    at = {k: i for i, k in enumerate(DEPTHS)}
    lam = {k: retention(marked[at[k]] / kept[at[k]], k) for k in usable}
    se = {k: standard_error(lam[k], k, kept[at[k]]) for k in usable}
    out: dict[str, Any] = {
        "usable_depths": usable,
        "lambda": {str(k): round(x, 6) for k, x in lam.items()},
        "se": {str(k): round(x, 6) for k, x in se.items()},
    }
    if all(k in lam for k in (1, 2, 3)):
        triple = [lam[1], lam[2], lam[3]]
        f, f_se = bend(triple, [kept[0], kept[1], kept[2]])
        z_bend = (f - bend(list(model[:3]), [kept[0], kept[1], kept[2]])[0]) / f_se
        reading = (
            "the retention law bends beyond the model at mirrored positions"
            if z_bend <= -Z_RESOLVE
            else "the retention law bends upward of the model at mirrored positions"
            if z_bend >= Z_RESOLVE
            else "no bend beyond the model resolved at mirrored positions"
        )
        out["bend"] = {"f": round(f, 6), "se": round(f_se, 6), "z_against_model": round(z_bend, 4), "reading": reading}
    else:
        out["bend"] = {"reading": "not evaluated: a depth of 1, 2 or 3 is unusable"}
    if len(usable) < 3:
        out["family"] = "not evaluated: fewer than three usable depths"
        return out
    rho = [lam[k] / model[at[k]] for k in usable]
    rho_se = [se[k] / model[at[k]] for k in usable]
    geo, coh = fit_geometric(rho, rho_se, usable), fit_coherent(rho, rho_se, usable)
    delta = geo["chi2"] - coh["chi2"]
    bounded = [name for name, fit in (("geometric", geo), ("coherent", coh)) if fit["at_bound"]]
    if bounded:
        subject = (
            "the geometric and coherent fits end on their rate bounds"
            if len(bounded) == 2
            else f"the {bounded[0]} fit ends on its rate bound"
        )
        family = f"out of domain: {subject}"
    elif min(geo["chi2"], coh["chi2"]) > ADEQUACY_BY_DOF[len(usable) - 2]:
        family = "neither family fits"
    elif delta >= DELTA_RESOLVE:
        family = "coherent"
    elif delta <= -DELTA_RESOLVE:
        family = "geometric"
    else:
        family = "unresolved"
    out |= {
        "rho": [round(x, 6) for x in rho],
        "geometric": rounded_fit(geo),
        "coherent": rounded_fit(coh),
        "delta_chi2": round(delta, 4),
        "family": family,
        "beside": {
            "retention_decreases_with_depth": all(lam[a] > lam[b] for a, b in zip(usable, usable[1:], strict=False)),
        },
    }
    if 4 in lam:
        r4, s4 = lam[4] / model[3], se[4] / model[3]
        out["beside"] |= {
            "rho4_against_retained_geometric_z": round((r4 - retained["geometric_next"]) / s4, 4),
            "rho4_against_retained_coherent_z": round((r4 - retained["coherent_next"]) / s4, 4),
        }
    return out


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


def mirror_pairs(copies: Sequence[Copy], total: int) -> list[tuple[Copy, Copy]]:
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


def copy_heterogeneity(copies: Sequence[Copy]) -> tuple[float, int]:
    """Chi-square of the copies of one depth about the pooled frequency, with len(copies) - 1 degrees of freedom:
    the sum of (marked - kept p)^2 / (kept p (1 - p)) with p the pooled marked frequency. A pooled frequency of 0
    or 1 leaves no variance to test and reads 0."""
    marked, kept = sum(c[1] for c in copies), sum(c[2] for c in copies)
    if not copies or kept <= 0:
        return 0.0, 0
    p = marked / kept
    if p <= 0.0 or p >= 1.0:
        return 0.0, len(copies) - 1
    return sum((m - n * p) ** 2 / (n * p * (1 - p)) for _, m, n in copies), len(copies) - 1


def read_copies(
    copies: Mapping[int, Sequence[Copy]],
    total: int,
    planned_kept: float,
    model: Sequence[float],
    retained: dict[str, Any],
    gate: Mapping[str, Any],
) -> dict[str, Any]:
    """The preregistered decisions on the copies of every depth.

    Mirror pairs. A pair leaves its depth when either copy keeps fewer than gate["copy_floor"] times planned_kept
    shots, so the surviving positions of every depth stay centered on the job and a drift linear in position
    leaves each pooled frequency unchanged. A depth without a surviving pair is unusable.

    Heterogeneity. The chi-square of the surviving copies of every depth about that depth's pooled frequency,
    summed over depths, has sum(copies - 1) degrees of freedom and is compared with
    gate["threshold_by_dof"][dof], the 1 - alpha chi-square quantile fixed in prediction.json. Above it the copies
    of a depth differ by more than their binomial scatter, a pooled frequency no longer describes the depth, and
    the bend and family decisions read "not evaluated". A design with no depth of two surviving copies has no
    test and reads "not evaluated" as well.

    Otherwise verdict() decides on the pooled counts."""
    if set(copies) != set(DEPTHS):
        raise ValueError(f"copies cover depths {sorted(copies)}, not {list(DEPTHS)}")
    floor = float(gate["copy_floor"]) * planned_kept
    surviving: dict[int, list[Copy]] = {}
    dropped: dict[str, list[list[int]]] = {}
    for k in DEPTHS:
        keep: list[Copy] = []
        for first, second in mirror_pairs(copies[k], total):
            if first[2] >= floor and second[2] >= floor:
                keep += [first, second]
            else:
                dropped.setdefault(str(k), []).append([first[0], second[0]])
        surviving[k] = keep
    stats_by_depth = {k: copy_heterogeneity(surviving[k]) for k in DEPTHS}
    statistic = sum(s for s, _ in stats_by_depth.values())
    dof = sum(d for _, d in stats_by_depth.values())
    threshold = gate["threshold_by_dof"].get(str(dof)) if dof else None
    block: dict[str, Any] = {
        "per_depth": {
            str(k): {"chi2": round(s, 6), "dof": d, "copies": len(surviving[k])} for k, (s, d) in stats_by_depth.items()
        },
        "chi2": round(statistic, 6),
        "dof": dof,
        "threshold": threshold,
    }
    if threshold is None:
        block["passed"] = False
        reason = "not evaluated: no depth keeps two copies, so copy heterogeneity cannot be tested"
    elif statistic > threshold:
        block["passed"] = False
        reason = "not evaluated: the copies of a depth differ by more than their binomial scatter"
    else:
        block["passed"] = True
        reason = ""
    pooled = [(sum(c[1] for c in surviving[k]), sum(c[2] for c in surviving[k])) for k in DEPTHS]
    out: dict[str, Any] = {"dropped_pairs": dropped, "heterogeneity": block}
    if reason:
        out |= {
            "usable_depths": [k for k, (_, n) in zip(DEPTHS, pooled, strict=True) if n > 0],
            "bend": {"reading": reason},
            "family": reason,
        }
        return out
    return out | verdict([m for m, _ in pooled], [n for _, n in pooled], model, retained)
