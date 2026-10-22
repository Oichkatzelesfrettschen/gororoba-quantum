"""Dark-subspace certificate of a binary photonic effect built from the sedenion zero divisor x = (e1 + e10)/sqrt2.

The target effect is E0 = L_x^T L_x / 2 on C^16 in cd_core's basis and doubling
(a, b)(c, d) = (ac - conj(d) b, da + b conj(c)). L_x^T L_x = I + (N + N^T)/2 with
the signed permutation N = L_e1^T L_e10, which pairs e_k with e_(k xor 11):
on the pairs (4, 15), (5, 14), (6, 13), (7, 12) the block is [[1/2, s/2],
[s/2, 1/2]] and on the other four pairs it is diag(1/2, 1/2). The spectrum is
therefore {0^4, (1/2)^8, 1^4}, and the frozen frame below diagonalizes E0.

Frame. K holds k_1..k_4 = (e7 + e12, e6 - e13, e5 + e14, e4 - e15)/sqrt2,
the kernel of L_x; Q holds f_1..f_12 = e0, e1, e2, e3, e8, e9, e10, e11
(eigenvalue 1/2) and (e7 - e12, e6 + e13, e5 - e14, e4 + e15)/sqrt2
(eigenvalue 1). [V_K V_Q] is orthogonal.

Certificate. For any physical effect 0 <= F <= I with blocks A = V_K^T F V_K
and C = V_Q^T F V_Q, a = lambda_max(A) <= a_U and C >= gamma_L I with
a_U < gamma_L give lambda_4(F) <= a_U (Courant-Fischer on span K),
lambda_5(F) >= gamma_L (every 5-space meets the 12-space Q), and, with P~
the projector on the four lowest eigenvectors, F >= gamma_L (I - P~)
compressed to K bounds sin^2 theta_max <= a_U / gamma_L. The cross block
V_Q^T F V_K never enters. Tr A <= l_U bounds a as well (A >= 0).

Bank. Each block of dimension m is reconstructed from its m basis
preparations f_i, the real pairs (f_i + f_j)/sqrt2 and the imaginary pairs
(f_i + i f_j)/sqrt2, i < j: 16 settings for A and 144 for C. With
H_ij = <f_i|H|f_j>, Re H_ij = p_R - (p_i + p_j)/2 and
Im H_ij = (p_i + p_j)/2 - p_I. The estimator is linear, H^ = sum_s p^_s D_s,
and both confidence radii below act on the fixed coefficient matrices D_s.

Confidence. A block's failure budget alpha splits evenly between two
procedures, and the reported radius is the smaller one; the union bound
covers that selection. (1) Clopper-Pearson intervals at alpha/2 shared by
Bonferroni over the block's settings, propagated deterministically to the
operator norm through the Gershgorin row sum of |Delta_ij| <= sum_s w_s
|D_s[i, j]| and through sum_s w_s ||D_s||, whichever is smaller. (2) Matrix
Bernstein (Tropp 2012, Theorem 1.4) with variance proxy ||sum_s D_s^2 /
(4 n_s)|| and range max_s ||D_s|| / n_s at alpha/2. With alpha = 0.025 per
block this reproduces the planning radii 0.409805, 0.157552, 0.049664 and
0.015689 of the 144-setting complex C block at 1500 to 10^6 trials.

Systematics add deterministically: an additive per-probability bias bound
b_s (preparation and implementation error) and a conditioning deviation
delta, the bound (1 - delta) tau I <= D <= (1 + delta) tau I on the
acceptance effect, under which the conditional probability p_c and the
effect probability p_F = Tr(G_A rho)/tau obey |p_F - p_c| <= delta p_c.
Both enter as extra weights on the same |D_s| row sums. G_A <= D bounds the
reconstructed effect F = G_A/tau only by 0 <= F <= (1 + delta) I, so the
a priori caps on a_U and l_U are 1 + delta and 4 (1 + delta); the
certificate inequalities use F >= 0 alone and hold unchanged.

Disposition. "inadmissible" when a record check or a declared premise
fails; "inconsistent" when an estimated block eigenvalue lies farther than
its radius outside [0, 1 + delta], so the confidence event contradicts the
effect range; "certified" when min(a_U, l_U) < gamma_L and the angle bound is at
most ANGLE_LIMIT_DEG; "alternative_structure" when the complement's
brightest direction has a positive certified response c_L (the lower bound
on lambda_max(C)) and either the upper bound gamma_U on lambda_min(C) is at
most DARK_RATIO c_L (a certified low-response direction inside the target
complement Q) or the lower bound on lambda_max(A) is at least TARGET_RATIO
c_L (a certified bright direction inside the target space); otherwise
"not_certified". A low complement direction alone leaves lambda_5(F)
unbounded below the bright level: A = 0.09 I_4, C = diag(0.09, 1, ..., 1)
and a single cross entry 0.09 coupling k_1 to that direction give a valid
effect with spectrum {0, 0.09^3, 0.18, 1^11}. Positivity bounds the cross
block by |u^T B v|^2 <= (u^T A u)(v^T C v), so lambda_5(F) <= a_U + gamma_U
is the global fifth-eigenvalue bound such a record supports. Both criteria are
ratios, so a scale factor common to every response, such as the
transmittance under an emitted-photon denominator, changes no disposition.
gamma_L = 0 alone identifies nothing, since it can mean insufficient
precision; the complement-direction claim rests on the upper bound gamma_U, which
holds on the same confidence event.

Census. The disposition is a compatibility summary; spectral_census reports
the scientific findings independently on the same event. Interlacing and
the positivity bound give mu_j <= lambda_(4+j)(F) <= a + mu_j for the
eigenvalues mu_j of C, so each of lambda_5..lambda_16 gets an interval, with
U_5 = min(L, a_* + mu_1U) and L_6 = mu_2L. With c = lambda_max(C) in
[c_L, c_U] and low meaning at most LOW_RATIO c: complement_low (mu_1U <=
0.1 c_L), at_least_five_low (U_5 <= 0.1 c_L), exactly_five_low (that and
L_6 > 0.1 c_U), target_bright (a_L >= 0.1 c_U) and
target_bright_lower_reference (a_L >= 0.1 c_L, the weaker reading the
alternative_structure branch uses) each read supported, refuted or
inconclusive, and unavailable without c_L > 0. target_alignment reads
supported exactly when the disposition is certified. A certified alignment
and a supported fifth low eigenvalue coexist on diag(0^4, 0.05, 1^11).

The "cal" share of an allocation covers the calibration that supports a
record's declared preparation bias bound and acceptance delta; analyze
spends only the A and C shares.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

DIM = 16
KERNEL_DIM = 4
COMPLEMENT_DIM = 12
X_LABELS = (1, 10)
# (plus label, minus label, sign) for k_j = (e_a + s e_b)/sqrt2; the bright partner is (e_a - s e_b)/sqrt2.
KERNEL_PAIRS = ((7, 12, 1), (6, 13, -1), (5, 14, 1), (4, 15, -1))
MIDDLE_LABELS = (0, 1, 2, 3, 8, 9, 10, 11)
ANGLE_LIMIT_DEG = 10.0
DARK_RATIO = 0.1
TARGET_RATIO = 0.1
# "Low" in every spectral finding means lambda <= LOW_RATIO lambda_max(C), an engineering definition fixed before
# acquisition; a finite threshold is never an exact null.
LOW_RATIO = 0.1
FINDINGS_SCHEMA = "bdsc-spectral-findings-v1"
CONSISTENCY_MARGIN = 0.05
ALPHA_ALLOCATIONS = {
    "two-block": {"A": 0.025, "C": 0.025, "cal": 0.0},
    "with-calibration": {"A": 0.02, "C": 0.02, "cal": 0.01},
}
PLANNING_TRIALS = (1_500, 10_000, 100_000, 1_000_000)
PLANNING_RADII = (0.409805, 0.157552, 0.049664, 0.015689)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# --- frame -------------------------------------------------------------------------------


def unit(*terms: tuple[float, int]) -> np.ndarray:
    v = np.zeros(DIM)
    for coefficient, label in terms:
        v[label] = coefficient
    return v / np.linalg.norm(v)


def kernel_frame() -> np.ndarray:
    """V_K, 16 x 4, columns k_1..k_4."""
    return np.column_stack([unit((1, a), (s, b)) for a, b, s in KERNEL_PAIRS])


def complement_frame() -> np.ndarray:
    """V_Q, 16 x 12, columns f_1..f_12 in the frozen order."""
    middle = [unit((1, label)) for label in MIDDLE_LABELS]
    bright = [unit((1, a), (-s, b)) for a, b, s in KERNEL_PAIRS]
    return np.column_stack(middle + bright)


def full_frame() -> np.ndarray:
    return np.column_stack([kernel_frame(), complement_frame()])


def ideal_eigenvalues() -> np.ndarray:
    """E0 in the [V_K V_Q] frame: diag(0^4, (1/2)^8, 1^4)."""
    return np.array([0.0] * 4 + [0.5] * 8 + [1.0] * 4)


def ideal_effect() -> np.ndarray:
    v = full_frame()
    return np.asarray(v @ np.diag(ideal_eigenvalues()) @ v.T, dtype=complex)


def projector() -> np.ndarray:
    k = kernel_frame()
    return np.asarray(k @ k.T)


def blocks(effect: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    k, q = kernel_frame(), complement_frame()
    return k.T @ effect @ k, q.T @ effect @ q


# --- preparation bank ----------------------------------------------------------------------


@dataclass(frozen=True)
class Setting:
    """One preparation: block "A" (frame K) or "C" (frame Q), kind basis/real/imag, frame indices i < j."""

    block: str
    kind: str
    i: int
    j: int

    @property
    def name(self) -> str:
        if self.kind == "basis":
            return f"{self.block}-basis-{self.i:02d}"
        return f"{self.block}-{self.kind}-{self.i:02d}-{self.j:02d}"


def block_settings(block: str, real_only: bool = False) -> list[Setting]:
    m = KERNEL_DIM if block == "A" else COMPLEMENT_DIM
    out = [Setting(block, "basis", i, i) for i in range(m)]
    pairs = list(itertools.combinations(range(m), 2))
    out += [Setting(block, "real", i, j) for i, j in pairs]
    if not real_only:
        out += [Setting(block, "imag", i, j) for i, j in pairs]
    return out


def bank(real_only: bool = False) -> list[Setting]:
    """The 160-setting complex bank (88 settings when real_only)."""
    return block_settings("A", real_only) + block_settings("C", real_only)


def frame_vector(setting: Setting) -> np.ndarray:
    """The preparation in its block's frame coordinates."""
    m = KERNEL_DIM if setting.block == "A" else COMPLEMENT_DIM
    v = np.zeros(m, dtype=complex)
    if setting.kind == "basis":
        v[setting.i] = 1
        return v
    v[setting.i] = 1 / math.sqrt(2)
    v[setting.j] = (1 if setting.kind == "real" else 1j) / math.sqrt(2)
    return v


def state(setting: Setting) -> np.ndarray:
    """The preparation in the sedenion basis e_0..e_15."""
    frame = kernel_frame() if setting.block == "A" else complement_frame()
    return np.asarray(frame @ frame_vector(setting))


def probabilities(effect: np.ndarray, settings: Sequence[Setting]) -> np.ndarray:
    out = []
    for s in settings:
        psi = state(s)
        out.append(float(np.real(np.conj(psi) @ effect @ psi)))
    return np.array(out)


# --- linear reconstruction -----------------------------------------------------------------


def coefficients(settings: Sequence[Setting], real_only: bool = False) -> list[np.ndarray]:
    """D_s with H^ = sum_s p_s D_s for one block's settings; real_only sets every Im H_ij to 0."""
    require(len({s.block for s in settings}) == 1, "coefficients take one block")
    m = KERNEL_DIM if settings[0].block == "A" else COMPLEMENT_DIM
    index = {(s.kind, s.i, s.j): k for k, s in enumerate(settings)}
    out = [np.zeros((m, m), dtype=complex) for _ in settings]

    def unit_pair(i: int, j: int) -> tuple[np.ndarray, np.ndarray]:
        e = np.zeros((m, m), dtype=complex)
        e[i, j] = 1
        return e + e.T, 1j * (e - e.T)

    for i in range(m):
        out[index[("basis", i, i)]][i, i] += 1
    for i, j in itertools.combinations(range(m), 2):
        sym, anti = unit_pair(i, j)
        # Re H_ij = p_R - (p_i + p_j)/2 enters H through Re H_ij (E_ij + E_ji).
        out[index[("real", i, j)]] += sym
        out[index[("basis", i, i)]] -= sym / 2
        out[index[("basis", j, j)]] -= sym / 2
        if real_only:
            continue
        # Im H_ij = (p_i + p_j)/2 - p_I enters H through Im H_ij i (E_ij - E_ji).
        out[index[("imag", i, j)]] -= anti
        out[index[("basis", i, i)]] += anti / 2
        out[index[("basis", j, j)]] += anti / 2
    return out


def reconstruct(p: np.ndarray, d: Sequence[np.ndarray]) -> np.ndarray:
    return np.asarray(sum(pk * dk for pk, dk in zip(p, d, strict=True)))


# --- confidence ----------------------------------------------------------------------------


def clopper_pearson(k: np.ndarray, n: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """Exact two-sided binomial intervals at level 1 - alpha for each (k, n)."""
    from scipy.stats import beta

    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    lo = np.where(k > 0, beta.ppf(alpha / 2, k, n - k + 1), 0.0)
    hi = np.where(k < n, beta.ppf(1 - alpha / 2, k + 1, n - k), 1.0)
    return np.asarray(lo, dtype=float), np.asarray(hi, dtype=float)


def propagated_radius(weights: np.ndarray, d: Sequence[np.ndarray]) -> float:
    """sup ||sum_s delta_s D_s|| over |delta_s| <= w_s, bounded by Gershgorin and by the triangle inequality."""
    entry = sum(w * np.abs(dk) for w, dk in zip(weights, d, strict=True))
    gershgorin = float(np.max(np.sum(entry, axis=1)))
    triangle = float(sum(w * np.linalg.norm(dk, 2) for w, dk in zip(weights, d, strict=True)))
    return min(gershgorin, triangle)


def bernstein_radius(d: Sequence[np.ndarray], n: np.ndarray, alpha: float) -> float:
    """Matrix Bernstein radius R h/3 + sqrt(2 v h + (R h/3)^2), h = log(2 m / alpha)."""
    m = d[0].shape[0]
    v = float(np.linalg.norm(sum(dk @ dk / (4 * nk) for dk, nk in zip(d, n, strict=True)), 2))
    r = max(float(np.linalg.norm(dk, 2)) / nk for dk, nk in zip(d, n, strict=True))
    h = math.log(2 * m / alpha)
    return r * h / 3 + math.sqrt(2 * v * h + (r * h / 3) ** 2)


def trace_radius(weights: np.ndarray, d: Sequence[np.ndarray]) -> float:
    return float(sum(w * abs(np.trace(dk)) for w, dk in zip(weights, d, strict=True)))


@dataclass(frozen=True)
class BlockBound:
    estimate: np.ndarray
    radius: float
    radius_cp: float
    radius_bernstein: float
    radius_systematic: float
    trace_upper: float
    trace_lower: float


def block_bound(
    k: np.ndarray,
    n: np.ndarray,
    d: Sequence[np.ndarray],
    alpha: float,
    bias: np.ndarray | None = None,
    conditioning: float = 0.0,
) -> BlockBound:
    """Simultaneous operator-norm radius of one block at failure probability alpha."""
    require(math.isfinite(conditioning) and conditioning >= 0, "conditioning delta must be finite and nonnegative")
    require(bias is None or bool(np.all(np.isfinite(bias)) and np.all(np.asarray(bias) >= 0)), "bias must be >= 0")
    p = k / n
    count = len(d)
    lo, hi = clopper_pearson(k, n, alpha / 2 / count)
    w = np.maximum(hi - p, p - lo)
    radius_cp = propagated_radius(w, d)
    radius_b = bernstein_radius(d, n, alpha / 2)
    sys_w = (np.zeros(count) if bias is None else np.asarray(bias)) + conditioning * hi
    radius_sys = propagated_radius(sys_w, d) if np.any(sys_w > 0) else 0.0
    estimate = reconstruct(p, d)
    tr = float(np.real(np.trace(estimate)))
    tr_w = trace_radius(w + sys_w, d)
    return BlockBound(
        estimate=estimate,
        radius=min(radius_cp, radius_b) + radius_sys,
        radius_cp=radius_cp,
        radius_bernstein=radius_b,
        radius_systematic=radius_sys,
        trace_upper=tr + tr_w,
        trace_lower=tr - tr_w,
    )


# --- certificate ---------------------------------------------------------------------------


def angle_bound_deg(upper: float, floor: float) -> float | None:
    if floor <= 0 or upper >= floor:
        return None
    return math.degrees(math.asin(math.sqrt(max(upper, 0.0) / floor)))


def exact_bound(block: np.ndarray) -> BlockBound:
    """A zero-radius bound on a known block, for the algebraic layer of the spectral census."""
    tr = float(np.real(np.trace(block)))
    return BlockBound(np.asarray(block), 0.0, 0.0, 0.0, 0.0, tr, tr)


def _finding(supported: bool, refuted: bool, available: bool = True) -> str:
    if not available:
        return "unavailable"
    return "supported" if supported else "refuted" if refuted else "inconclusive"


def spectral_census(a: BlockBound, c: BlockBound, effect_upper: float = 1.0) -> dict[str, Any]:
    """Intervals on lambda_5..lambda_16 of F and the independent spectral findings, on one confidence event.

    With a = lambda_max(A) and mu_1 <= ... <= mu_12 the eigenvalues of C, mu_j <= lambda_(4+j)(F) <= a + mu_j:
    the lower bound is Cauchy interlacing with the 12-dimensional compression, the upper bound is min-max on span K
    plus the first j eigenvectors of C, where |u^dagger B^dagger v|^2 <= (u^dagger A u)(v^dagger C v) bounds the
    cross term by 2 sqrt(a mu_j) |u| |v| <= (a + mu_j)(|u|^2 + |v|^2) - a |u|^2 - mu_j |v|^2. Weyl's inequality
    moves every eigenvalue of a block by at most its operator-norm radius, so all twelve intervals hold on the event
    that bounds ||C^ - C|| and ||A^ - A||, with no further multiplicity charge. 0 <= F <= effect_upper I clamps
    each bound; an estimate farther than its radius outside [0, effect_upper] contradicts that range, and the
    census then reads inconsistent and issues no finding.
    """
    eig_a = np.linalg.eigvalsh(a.estimate)
    eig_c = np.linalg.eigvalsh(c.estimate)
    top = effect_upper
    consistent = bool(
        eig_a[0] + a.radius >= 0
        and eig_a[-1] - a.radius <= top
        and eig_c[0] + c.radius >= 0
        and eig_c[-1] - c.radius <= top
        and a.trace_upper >= 0
        and a.trace_lower <= KERNEL_DIM * top
    )
    a_upper = min(top, float(eig_a[-1]) + a.radius)
    a_lower = max(0.0, float(eig_a[-1]) - a.radius)
    a_star = min(a_upper, a.trace_upper, top)
    mu_lower = [max(0.0, float(m) - c.radius) for m in eig_c]
    mu_upper = [min(top, float(m) + c.radius) for m in eig_c]
    upper = [min(top, a_star + m) for m in mu_upper]
    c_lower, c_upper = mu_lower[-1], mu_upper[-1]
    u5, l6, u6 = upper[0], mu_lower[1], upper[1]
    ratio = consistent and c_lower > 0
    low_lo, low_hi = LOW_RATIO * c_lower, LOW_RATIO * c_upper
    at_least_five = _finding(u5 <= low_lo, mu_lower[0] > low_hi, ratio)
    findings = {
        "complement_low": _finding(mu_upper[0] <= low_lo, mu_lower[0] > low_hi, ratio),
        "at_least_five_low": at_least_five,
        "exactly_five_low": _finding(u5 <= low_lo and l6 > low_hi, at_least_five == "refuted" or u6 <= low_lo, ratio),
        "target_bright": _finding(a_lower >= low_hi, a_upper < low_lo, ratio),
        "target_bright_lower_reference": _finding(a_lower >= low_lo, a_upper < low_lo, ratio),
    }
    return {
        "schema": FINDINGS_SCHEMA,
        "effect_upper": top,
        "low_ratio": LOW_RATIO,
        "consistent": consistent,
        "a_star": a_star,
        "c_L": c_lower,
        "c_U": c_upper,
        "mu_L": mu_lower,
        "mu_U": mu_upper,
        "lambda_5_to_16": [[lo, hi] for lo, hi in zip(mu_lower, upper, strict=True)],
        "U_5": u5,
        "L_6": l6,
        "U_6": u6,
        "findings": findings,
    }


def certificate(a: BlockBound, c: BlockBound, effect_upper: float = 1.0) -> dict[str, Any]:
    """Certificate from the block bounds of an effect F with 0 <= F <= effect_upper I."""
    eig_a = np.linalg.eigvalsh(a.estimate)
    eig_c = np.linalg.eigvalsh(c.estimate)
    census = spectral_census(a, c, effect_upper)
    a_upper = min(effect_upper, float(eig_a[-1]) + a.radius)
    a_lower = float(eig_a[-1]) - a.radius
    l_upper = min(KERNEL_DIM * effect_upper, a.trace_upper)
    gamma_lower = max(0.0, float(eig_c[0]) - c.radius)
    gamma_upper = float(eig_c[0]) + c.radius
    bound = min(a_upper, l_upper)
    angle = angle_bound_deg(bound, gamma_lower)
    bright_lower = float(eig_c[-1]) - c.radius
    if not census["consistent"]:
        disposition = "inconsistent"
    elif angle is not None and angle <= ANGLE_LIMIT_DEG:
        disposition = "certified"
    elif bright_lower > 0 and (gamma_upper <= DARK_RATIO * bright_lower or a_lower >= TARGET_RATIO * bright_lower):
        disposition = "alternative_structure"
    else:
        disposition = "not_certified"
    fields = {
        "lambda_max_A_hat": float(eig_a[-1]),
        "trace_A_hat": float(np.real(np.trace(a.estimate))),
        "lambda_min_C_hat": float(eig_c[0]),
        "radius_A": a.radius,
        "radius_A_cp": a.radius_cp,
        "radius_A_bernstein": a.radius_bernstein,
        "radius_A_systematic": a.radius_systematic,
        "radius_C": c.radius,
        "radius_C_cp": c.radius_cp,
        "radius_C_bernstein": c.radius_bernstein,
        "radius_C_systematic": c.radius_systematic,
        "a_U": a_upper,
        "a_L": a_lower,
        "l_U": l_upper,
        "gamma_L": gamma_lower,
        "gamma_U": gamma_upper,
        "c_L": bright_lower,
        "gap_L": gamma_lower - bound,
    }
    out: dict[str, Any] = {key: float(value) for key, value in fields.items()}
    out["theta_max_bound_deg"] = angle
    out["disposition"] = disposition
    census["findings"] = {
        "target_alignment": _finding(disposition == "certified", False, census["consistent"]),
        **census["findings"],
    }
    out["census"] = census
    return out


def analyze(
    counts: dict[str, tuple[int, int]],
    alpha: dict[str, float],
    real_only: bool = False,
    bias: float = 0.0,
    conditioning: float = 0.0,
) -> dict[str, Any]:
    """Certificate from {setting name: (selected k, eligible n)} over the frozen bank."""
    settings = bank(real_only)
    names = [s.name for s in settings]
    require(sorted(counts) == sorted(names), "the record does not hold exactly the frozen bank's settings")
    for name, (k, n) in counts.items():
        require(isinstance(k, int) and isinstance(n, int) and 0 <= k <= n and n > 0, f"invalid counts at {name}")
    out: dict[str, BlockBound] = {}
    for block in ("A", "C"):
        rows = block_settings(block, real_only)
        d = coefficients(rows, real_only)
        selected = np.array([counts[s.name][0] for s in rows], dtype=float)
        eligible = np.array([counts[s.name][1] for s in rows], dtype=float)
        out[block] = block_bound(selected, eligible, d, alpha[block], np.full(len(rows), bias), conditioning)
    return certificate(out["A"], out["C"], 1.0 + conditioning)


def sample_counts(effect: np.ndarray, n: int, seed: int, real_only: bool = False) -> dict[str, tuple[int, int]]:
    """Independent binomial draws at each bank setting's probability under effect."""
    settings = bank(real_only)
    p = np.clip(probabilities(effect, settings), 0.0, 1.0)
    k = np.random.default_rng(seed).binomial(n, p)
    return {s.name: (int(ki), n) for s, ki in zip(settings, k, strict=True)}


# --- subspace geometry ---------------------------------------------------------------------


def low_projector(effect: np.ndarray, dim: int = KERNEL_DIM) -> np.ndarray:
    _, vec = np.linalg.eigh(effect)
    low = vec[:, :dim]
    return np.asarray(low @ low.conj().T)


def max_principal_angle_deg(p1: np.ndarray, p2: np.ndarray) -> float:
    """Largest principal angle between the ranges of two rank-4 projectors.

    sin theta_max is the largest singular value of (I - p2) U1, U1 an
    orthonormal basis of p1's range. The eigenvalues of p1 (I - p2) p1 are
    sin^2 theta, whose square root lifts a rounding residue of 1e-16 to an
    angle of 1e-8 rad; the singular value carries it at 1e-16.
    """
    basis = np.linalg.eigh(p1)[1][:, -KERNEL_DIM:]
    sines = np.linalg.svd((np.eye(len(p1)) - p2) @ basis, compute_uv=False)
    return math.degrees(math.asin(min(1.0, float(sines[0]))))


def theorem_holds(effect: np.ndarray) -> dict[str, Any]:
    """Exact quantities of the certificate theorem on one effect: a, gamma, lambda_4, lambda_5, theta, bound."""
    a_block, c_block = blocks(effect)
    a = float(np.linalg.eigvalsh(a_block)[-1])
    gamma = float(np.linalg.eigvalsh(c_block)[0])
    eig = np.linalg.eigvalsh(effect)
    theta = max_principal_angle_deg(projector().astype(complex), low_projector(effect))
    bound = angle_bound_deg(a, gamma)
    ok = (
        eig[3] <= a + 1e-12
        and eig[4] >= gamma - 1e-12
        and (bound is None or theta <= bound + 1e-7)
        and (a >= gamma or math.sin(math.radians(theta)) ** 2 <= a / gamma + 1e-12)
    )
    return {"a": a, "gamma": gamma, "lambda_4": float(eig[3]), "lambda_5": float(eig[4]), "theta": theta, "ok": ok}


# --- detection conditioning ----------------------------------------------------------------


def acceptance(unitary: np.ndarray, selected: Sequence[int], efficiency: Sequence[float]) -> dict[str, np.ndarray]:
    """G_A and D on the 16 logical inputs of a 24-mode measurement unitary with per-detector efficiencies."""
    u = unitary[:, :DIM]
    eta = np.asarray(efficiency, dtype=float)
    mask = np.zeros(len(eta))
    mask[list(selected)] = 1
    g = u.conj().T @ np.diag(eta * mask) @ u
    d = u.conj().T @ np.diag(eta) @ u
    return {"G": g, "D": d}


def thinned_acceptance(transfer: np.ndarray, efficiency: Sequence[float] | np.ndarray) -> np.ndarray:
    """Acceptance effect after retaining each mode-m event with q_m = eta_* / eta_m, eta_* = min_m eta_m.

    A detected mode-m event has probability eta_m |(T psi)_m|^2 through the possibly lossy transfer T, so the
    retained acceptance is eta_* T^dagger T: scalar only when T^dagger T = tau I on the inputs. Terminal balancing
    equalizes detector efficiencies and leaves internal mode-dependent loss in place.
    """
    eta = np.asarray(efficiency, dtype=float)
    keep = eta.min() / eta
    return np.asarray(transfer.conj().T @ np.diag(eta * keep) @ transfer)


def thin_histogram(counts: np.ndarray, keep: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """N'_m ~ Binomial(N_m, q_m): equal in law to keeping each genuine event independently, so no event order is
    needed. Counts converted from a probability estimate stay converted after thinning."""
    return np.asarray(rng.binomial(np.asarray(counts, dtype=np.int64), keep))


def scalar_deviation(d: np.ndarray) -> tuple[float, float]:
    """(tau, delta) minimizing delta in (1 - delta) tau I <= D <= (1 + delta) tau I."""
    w = np.linalg.eigvalsh(d)
    tau = float(w[0] + w[-1]) / 2
    return tau, float((w[-1] - w[0]) / (w[-1] + w[0]))


# --- acquisition records -------------------------------------------------------------------

RECORD_SCHEMA = "bdsc-acquisition-v1"
# Each premise must read "supported" before a record reaches the certificate: the common linear effect over
# every preparation label, the independent fixed-n Bernoulli sampling law, and the acceptance model (scalar
# acceptance, or the declared conditioning bound delta). real_effect is required only by the 88-setting bank.
PREMISES = ("common_effect", "bernoulli_sampling", "acceptance_model", "preparation_bound")
STOPPING = "fixed-n"


def _count(value: Any) -> bool:
    return type(value) is int


def _bound(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def evaluate(record: dict[str, Any], frozen: dict[str, Any]) -> dict[str, Any]:
    """Disposition of one acquisition record against the frozen target identity, bank digest, mask and bank.

    The bank digest binds each setting name to its preparation state, so counts recorded under one bank
    never reach the reconstruction of another bank that reuses the setting names.
    """
    reasons: list[str] = []

    def check(condition: bool, reason: str) -> None:
        if not condition:
            reasons.append(reason)

    if not isinstance(record, dict):
        return {"disposition": "inadmissible", "reasons": ["record is not an object"]}
    check(record.get("schema") == RECORD_SCHEMA, "schema differs")
    check(record.get("target_sha256") == frozen["target_sha256"], "target identity differs from the frozen target")
    check(record.get("bank_sha256") == frozen["bank_sha256"], "bank identity differs from the frozen bank")
    check(record.get("selected_modes") == frozen["selected_modes"], "selected-output map differs from the frozen map")
    check(record.get("stopping") == STOPPING, "stopping rule is not the frozen fixed-n rule")
    real_only = record.get("real_only", False)
    check(isinstance(real_only, bool), "real_only is not a boolean")
    real_only = real_only is True
    premises = record.get("premises", {})
    check(isinstance(premises, dict), "premises is not an object")
    premises = premises if isinstance(premises, dict) else {}
    needed = PREMISES + (("real_effect",) if real_only else ())
    for name in needed:
        check(premises.get(name) == "supported", f"premise {name} is not supported")
    bias = record.get("preparation_bias_bound", 0.0)
    conditioning = record.get("conditioning_delta", 0.0)
    check(_bound(bias), "preparation_bias_bound is not a finite nonnegative number")
    check(_bound(conditioning), "conditioning_delta is not a finite nonnegative number")
    rows = record.get("rows", [])
    check(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), "rows are not a list of objects")
    rows = [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    names = [row.get("setting") for row in rows]
    check(all(isinstance(n, str) for n in names), "a preparation identity is not a string")
    check(len(names) == len(set(map(str, names))), "a preparation identity repeats")
    expected = sorted(s.name for s in bank(real_only))
    check(sorted(n for n in names if isinstance(n, str)) == expected, "preparation identities differ from the bank")
    n_fixed = frozen.get("trials_per_setting")
    counts: dict[str, tuple[int, int]] = {}
    for row in rows:
        k, n = row.get("selected"), row.get("eligible")
        valid = _count(k) and _count(n) and 0 <= k <= n and n > 0
        check(valid, f"invalid trial counts at {row.get('setting')}")
        check(n_fixed is None or n == n_fixed, f"eligible trials at {row.get('setting')} differ from the frozen n")
        if valid and isinstance(row.get("setting"), str):
            counts[row["setting"]] = (k, n)
    if reasons:
        return {"disposition": "inadmissible", "reasons": reasons}
    allocation = ALPHA_ALLOCATIONS[frozen["alpha_allocation"]]
    out = analyze(counts, allocation, real_only, bias=float(bias), conditioning=float(conditioning))
    out["reasons"] = []
    return out


def record_from_counts(
    counts: dict[str, tuple[int, int]],
    frozen: dict[str, Any],
    premises: dict[str, str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    support = {name: "supported" for name in (*PREMISES, "real_effect")}
    return {
        "schema": RECORD_SCHEMA,
        "target_sha256": frozen["target_sha256"],
        "bank_sha256": frozen["bank_sha256"],
        "selected_modes": list(frozen["selected_modes"]),
        "stopping": STOPPING,
        "premises": support if premises is None else premises,
        "rows": [{"setting": name, "selected": k, "eligible": n} for name, (k, n) in sorted(counts.items())],
        **extra,
    }


# --- pilot ---------------------------------------------------------------------------------

PILOT_ANGLES = {"0": 0.0, "pi/2": math.pi / 2, "+pi/4": math.pi / 4, "-pi/4": -math.pi / 4}
PILOT_HELD_OUT = {"+pi/12": math.pi / 12, "-pi/12": -math.pi / 12}
PILOT_PHASES = {"+i": 1j, "-i": -1j}
# y0 = k_1 against its bright partner f_9 (C = 1), a middle vector f_1 (C = 1/2) and the bright partner of
# another kernel vector f_10 (C = 1): the three complement classes one kernel direction meets.
PILOT_PAIRS = ((0, 8), (0, 0), (0, 9))


def pilot_settings() -> list[dict[str, Any]]:
    """y(theta) = cos(theta) k_i + phase sin(theta) f_j over the angles, held-out angles and phase probes."""
    k, q = kernel_frame(), complement_frame()
    out = []
    for i, j in PILOT_PAIRS:
        grid = [(name, theta, 1.0 + 0j) for name, theta in {**PILOT_ANGLES, **PILOT_HELD_OUT}.items()]
        grid += [(f"pi/4{label}", math.pi / 4, phase) for label, phase in PILOT_PHASES.items()]
        for name, theta, phase in grid:
            psi = math.cos(theta) * k[:, i] + phase * math.sin(theta) * q[:, j]
            out.append({"name": f"pilot-k{i + 1:02d}-f{j + 1:02d}-{name}", "pair": [i, j], "angle": name, "state": psi})
    return out


def residual_interval(plus: Sequence[float], minus: Sequence[float]) -> tuple[float, float]:
    """Interval on p_a + p_b - p_c - p_d from simultaneous bounds given as flat tuples
    plus = (lower_a, upper_a, lower_b, upper_b) and minus = (lower_c, upper_c, lower_d, upper_d)."""
    return plus[0] + plus[2] - minus[1] - minus[3], plus[1] + plus[3] - minus[0] - minus[2]


def equivalence(interval: tuple[float, float], margin: float) -> str:
    """compatible: the interval lies inside [-margin, margin]; violated: it misses that band; else inconclusive.
    An interval that merely contains zero establishes nothing."""
    lo, hi = interval
    if -margin <= lo and hi <= margin:
        return "compatible"
    if lo > margin or hi < -margin:
        return "violated"
    return "inconclusive"


CONSISTENCY_LABELS = ("f", "g", "+", "-", "+i", "-i")


def consistency_states(f: np.ndarray, g: np.ndarray) -> dict[str, np.ndarray]:
    """f, g, (f +- g)/sqrt2 and (f +- i g)/sqrt2 for orthonormal f, g."""
    r = 1 / math.sqrt(2)
    return {"f": f, "g": g, "+": r * (f + g), "-": r * (f - g), "+i": r * (f + 1j * g), "-i": r * (f - 1j * g)}


def consistency_readout(
    counts: dict[str, tuple[int, int]], alpha: float, margin: float = CONSISTENCY_MARGIN
) -> dict[str, Any]:
    """Delta_R = p_+ + p_- - p_f - p_g and Delta_I = p_+i + p_-i - p_f - p_g, zero for every fixed linear effect.

    Clopper-Pearson at alpha/6 per probability makes both residual intervals simultaneous at 1 - alpha; each is
    judged against the preregistered margin, never against zero alone.
    """
    require(sorted(counts) == sorted(CONSISTENCY_LABELS), "a consistency bank holds exactly f, g, +-, +-i")
    names = list(CONSISTENCY_LABELS)
    k = np.array([counts[x][0] for x in names], dtype=float)
    n = np.array([counts[x][1] for x in names], dtype=float)
    lo, hi = clopper_pearson(k, n, alpha / len(names))
    b = {x: (float(lo[i]), float(hi[i])) for i, x in enumerate(names)}
    p = {x: float(k[i] / n[i]) for i, x in enumerate(names)}
    out: dict[str, Any] = {}
    for key, (a1, a2) in (("R", ("+", "-")), ("I", ("+i", "-i"))):
        interval = residual_interval((*b[a1], *b[a2]), (*b["f"], *b["g"]))
        out[f"delta_{key}"] = p[a1] + p[a2] - p["f"] - p["g"]
        out[f"delta_{key}_interval"] = list(interval)
        out[f"delta_{key}_status"] = equivalence(interval, margin)
        out[f"delta_{key}_excludes_zero"] = interval[0] > 0 or interval[1] < 0
    out["margin"] = margin
    return out


Contrast = tuple[str, float, tuple[tuple[int, float], ...]]


def contrast_readout(
    selected: np.ndarray,
    eligible: np.ndarray,
    contrasts: Sequence[Contrast],
    alpha: float,
    admitted: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """Intervals and statuses of prespecified linear contrasts sum_j c_j p_j on one simultaneous event.

    Clopper-Pearson at alpha / P on each of the P observations makes every interval [L_j, U_j] hold at once with
    probability 1 - alpha, and each contrast inherits it: Delta_L = sum_(c_j > 0) c_j L_j + sum_(c_j < 0) c_j U_j and
    Delta_U the mirror image, so no contrast spends its own error. Each contrast is (family, margin, terms) and reads
    compatible, violated or inconclusive against its margin. selected and eligible carry the observations on their
    last axis; a leading replicate axis evaluates many synthetic records with the same arithmetic, term by term in
    the declared order, as one record. admitted marks the observations whose observation contract supports
    Bernoulli trials; a contrast with any term outside it reads not_admitted, and the alpha / P split still counts
    every observation, so admission never re-allocates error.
    """
    k = np.asarray(selected, dtype=float)
    n = np.asarray(eligible, dtype=float)
    lo, hi = clopper_pearson(k, n, alpha / k.shape[-1])
    # Every contrast is a padded row of (index, coefficient) terms, evaluated for all contrasts at once; the terms
    # are added in their declared order, and a padding coefficient of 0 adds an exact zero.
    width = max(len(terms) for _, _, terms in contrasts)
    index = np.zeros((len(contrasts), width), dtype=int)
    coefficient = np.zeros((len(contrasts), width))
    for row, (_, _, terms) in enumerate(contrasts):
        for column, (j, c) in enumerate(terms):
            index[row, column], coefficient[row, column] = j, c
    margin = np.array([m for _, m, _ in contrasts])
    lo_terms, hi_terms = lo[..., index], hi[..., index]
    positive = coefficient > 0
    low_terms = np.where(positive, coefficient * lo_terms, coefficient * hi_terms)
    high_terms = np.where(positive, coefficient * hi_terms, coefficient * lo_terms)
    lower, upper = low_terms[..., 0], high_terms[..., 0]
    for column in range(1, width):
        lower = lower + low_terms[..., column]
        upper = upper + high_terms[..., column]
    inside = (lower >= -margin) & (upper <= margin)
    outside = (lower > margin) | (upper < -margin)
    status = np.where(inside, "compatible", np.where(outside, "violated", "inconclusive")).astype(object)
    if admitted is not None:
        touched = np.asarray(admitted, dtype=bool)[index] | (coefficient == 0)
        status[..., ~touched.all(axis=1)] = "not_admitted"
    return {"lower": lower, "upper": upper, "status": status}


def hoeffding_consistency_trials(margin: float, alpha: float) -> int:
    """Per-preparation n at which a Hoeffding radius sqrt(log(12/alpha)/(2n)) on six probabilities under a union
    bound makes a four-probability residual's half-width equal the margin: n >= 8 log(12/alpha) / margin^2. A
    compatible reading needs |estimate| + half-width <= margin, so this n is a floor with no power; the case's
    power table sets the trials."""
    return math.ceil(8 * math.log(12 / alpha) / margin**2)


def pilot_readout(
    counts: dict[str, tuple[int, int]], alpha: float, margin: float = CONSISTENCY_MARGIN
) -> list[dict[str, Any]]:
    """r0, C_q, Re d_q, Im d_q and the sum rules p(+) + p(-) = p(0) + p(pi/2) = p(+i) + p(-i), judged against margin
    on Bonferroni Clopper-Pearson bounds simultaneous over every pilot setting."""
    bounds: dict[str, tuple[float, float, float]] = {}
    total = len(counts)
    for name, (k, n) in counts.items():
        lo, hi = clopper_pearson(np.array([k]), np.array([n]), alpha / total)
        bounds[name] = (k / n, float(lo[0]), float(hi[0]))
    out = []
    for i, j in PILOT_PAIRS:
        base = f"pilot-k{i + 1:02d}-f{j + 1:02d}-"

        def at(label: str, base: str = base) -> tuple[float, float, float]:
            return bounds[base + label]

        p0, pq, pp, pm = at("0"), at("pi/2"), at("+pi/4"), at("-pi/4")
        pi_plus, pi_minus = at("pi/4+i"), at("pi/4-i")
        reference = (p0[1], p0[2], pq[1], pq[2])
        real = residual_interval((pp[1], pp[2], pm[1], pm[2]), reference)
        imag = residual_interval((pi_plus[1], pi_plus[2], pi_minus[1], pi_minus[2]), reference)
        out.append(
            {
                "pair": [i, j],
                "r0": p0[0],
                "C_q": pq[0],
                "re_d_q": (pp[0] - pm[0]) / 2,
                "im_d_q": (pi_minus[0] - pi_plus[0]) / 2,
                "delta_R": pp[0] + pm[0] - p0[0] - pq[0],
                "delta_R_interval": list(real),
                "delta_R_status": equivalence(real, margin),
                "delta_I": pi_plus[0] + pi_minus[0] - p0[0] - pq[0],
                "delta_I_interval": list(imag),
                "delta_I_status": equivalence(imag, margin),
                "margin": margin,
            }
        )
    return out


def pilot_probabilities(effect: np.ndarray) -> dict[str, float]:
    return {s["name"]: float(np.real(np.conj(s["state"]) @ effect @ s["state"])) for s in pilot_settings()}


# --- five-space witness --------------------------------------------------------------------


def candidate_directions() -> dict[str, np.ndarray]:
    """q_R = (e1 - e2)/sqrt2, the extra null of E_R, and q_I = (e1 + i e2)/sqrt2, the extra null of E_I."""
    r = 1 / math.sqrt(2)
    q_r = np.zeros(DIM, dtype=complex)
    q_r[1], q_r[2] = r, -r
    q_i = np.zeros(DIM, dtype=complex)
    q_i[1], q_i[2] = r, 1j * r
    return {"q_R": q_r, "q_I": q_i}


def five_space_states(q: np.ndarray) -> list[np.ndarray]:
    """k_1..k_4 and a unit q in the complement Q: the range of the rank-5 projector S = P + |q><q|."""
    k = kernel_frame()
    require(abs(np.linalg.norm(q) - 1) < 1e-12, "q is not a unit vector")
    require(float(np.linalg.norm(k.T @ q)) < 1e-12, "q is not in the target complement")
    return [k[:, j].astype(complex) for j in range(KERNEL_DIM)] + [np.asarray(q, dtype=complex)]


def five_space_trace(effect: np.ndarray, q: np.ndarray) -> float:
    """Tr(S F), the upper bound on lambda_5(F) that a uniform five-state ensemble measures as 5 r_5."""
    return float(sum(np.real(np.conj(v) @ effect @ v) for v in five_space_states(q)))


def five_space_witness(
    selected: int, eligible: int, alpha: float, bias: float = 0.0, conditioning: float = 0.0
) -> dict[str, Any]:
    """lambda_5(F) <= lambda_max(S F S) <= Tr(S F) = 5 r_5, at one-sided failure alpha.

    r_5 is the selected probability of the uniform ensemble over the five states, each trial drawing its state
    independently. Under an acceptance bound delta the effect probability is at most (1 + delta) p_c, and the
    preparation bias bound adds; the bound caps at the effect range 1 + delta. A large witness excludes nothing:
    only this candidate's evidence fails.
    """
    require(type(selected) is int and type(eligible) is int and 0 <= selected <= eligible and eligible > 0, "counts")
    require(0 < alpha < 1 and bias >= 0 and conditioning >= 0, "alpha, bias and delta")
    from scipy.stats import beta

    upper = 1.0 if selected == eligible else float(beta.ppf(1 - alpha, selected + 1, eligible - selected))
    r_upper = (1 + conditioning) * upper + bias
    return {"r_5_upper": r_upper, "lambda_5_upper": min(1 + conditioning, 5 * r_upper)}


def zero_event_five_space_trials(threshold: float, alpha: float) -> int:
    """Smallest N at which zero selected events of N give 5 (1 - alpha^(1/N)) <= threshold."""
    return math.ceil(math.log(alpha) / math.log(1 - threshold / 5))


# --- control effects -----------------------------------------------------------------------


def outer(a: int, b: int) -> np.ndarray:
    m = np.zeros((DIM, DIM), dtype=complex)
    m[a, b] = 1
    return m


def extra_real_null() -> np.ndarray:
    return ideal_effect() + 0.5 * (outer(1, 2) + outer(2, 1))


def extra_imag_null() -> np.ndarray:
    return ideal_effect() + 0.5j * (outer(1, 2) - outer(2, 1))


def kernel_other_spectrum() -> np.ndarray:
    v = full_frame()
    w = np.array([0.0] * 4 + list(np.linspace(0.3, 0.9, 12)))
    return np.asarray(v @ np.diag(w) @ v.T, dtype=complex)


def rotated(degrees: float) -> np.ndarray:
    """E0 conjugated by a rotation in the plane of k_1 and its bright partner f_9."""
    k1, f9 = kernel_frame()[:, 0], complement_frame()[:, 8]
    t = math.radians(degrees)
    r = (
        np.eye(DIM)
        + (math.cos(t) - 1) * (np.outer(k1, k1) + np.outer(f9, f9))
        + math.sin(t) * (np.outer(f9, k1) - np.outer(k1, f9))
    )
    return np.asarray(r @ ideal_effect() @ r.T)


def attenuated(tau: float) -> np.ndarray:
    return tau * ideal_effect()


def background(beta: float) -> np.ndarray:
    return beta * np.eye(DIM, dtype=complex) + (1 - beta) * ideal_effect()


def frame_effect(a: np.ndarray, c: np.ndarray, cross: np.ndarray | None = None) -> np.ndarray:
    """The effect with blocks A on K, C on Q and cross block B = V_Q^T F V_K, in the sedenion basis."""
    b = np.zeros((COMPLEMENT_DIM, KERNEL_DIM), dtype=complex) if cross is None else cross
    frame = np.block([[a, b.conj().T], [b, c]])
    v = full_frame()
    return np.asarray(v @ frame @ v.T, dtype=complex)


def diagonal_effect(low: Sequence[float], rest: float, kernel: Sequence[float] = (0.0,) * KERNEL_DIM) -> np.ndarray:
    """diag(kernel, low, rest^(12 - len(low))) in the frozen frame."""
    c = list(low) + [rest] * (COMPLEMENT_DIM - len(low))
    return frame_effect(np.diag(np.asarray(kernel, dtype=complex)), np.diag(np.asarray(c, dtype=complex)))


def coupled_complement_effect() -> np.ndarray:
    """A = 0.09 I_4, C = diag(0.09, 1^11) and B_11 = 0.09: spectrum {0, 0.09^3, 0.18, 1^11}, lambda_5 = a + mu_1."""
    cross = np.zeros((COMPLEMENT_DIM, KERNEL_DIM), dtype=complex)
    cross[0, 0] = 0.09
    c = np.diag(np.array([0.09] + [1.0] * (COMPLEMENT_DIM - 1), dtype=complex))
    return frame_effect(0.09 * np.eye(KERNEL_DIM, dtype=complex), c, cross)


def is_effect(effect: np.ndarray, tolerance: float = 1e-12) -> bool:
    w = np.linalg.eigvalsh(effect)
    return bool(np.allclose(effect, effect.conj().T) and w[0] >= -tolerance and w[-1] <= 1 + tolerance)
