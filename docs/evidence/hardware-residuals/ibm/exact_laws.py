"""Exact conditional laws of the order statistics used by the IBM residual-structure analyses.

Every law conditions on the margins of the data and treats the order of the shots as a uniform arrangement.
The module holds closed forms or integer arithmetic only; no random draw enters. `python exact_laws.py` runs
the self-test and prints the result.

Self-test coverage. Each check counts a statistic over every arrangement with Python integers and compares:
- the adjacency law, n 2..10, every k; the runs-of-length-at-least-L law (pmf, tail, mean), n 3..12, every k,
  L in 1, 2, 3, 5; the mean closed form E_L at four large sizes;
- the same-shot hypergeometric law, n 1..8, every (K_i, K_j), pmf and two-sided log10 p at every observed count,
  and one far tail (n 16384) against an exact integer sum;
- the pooled convolution of two units, n 1..6, every k (k = 0, 1 and n included), for the adjacency law and for
  the run law at L in 1, 2, 3, with the pmf and the upper, lower and two-sided log10 tails at every observed count
  from 0 beyond the largest attainable count;
- the cross-lag mean and variance, n 2..5 for every margin triple (K_j, K_i, J) and n 8 for six margin sets;
- the Chernoff bound at least the exact pooled tail at every count of five small cases (one with zero
  binomial-moment numerators) and at three (L, count) pairs of one larger column set;
- the support cap of the run-count pmf (the dropped mass stays below 1e-300).
The circular-shift law of `a2_burst.py`, the Poisson tails, the periodogram laws and the t tests are outside it.
The run exits non-zero when a check reads `holds: false` or `bound_holds: false`.

Laws.

- Adjacent ones. A column of n reads with k ones, uniformly arranged, has R runs of ones with
  P(R = r) = C(k-1, r-1) C(n-k+1, r) / C(n, k), and the count of adjacent (1, 1) pairs is k - R.
- Runs of length at least L. The n-k zeros cut the arrangement into g = n-k+1 gaps and the k ones fill the
  gaps as a uniform weak composition. With M the number of gaps that hold at least L ones, the binomial moments
  are S_t = E[C(M, t)] = C(g, t) C(k - L t + g - 1, g - 1) / C(k + g - 1, g - 1), and
  P(M >= m) = sum_{t >= m} (-1)^(t-m) C(t-1, m-1) S_t. The alternating sum runs in Python integers, so it
  carries no cancellation error.
- Same-shot pair count. With the margins K_i, K_j fixed over n shots, the joint count of two columns is
  hypergeometric (n, K_i, K_j); the pooled count over independent PUBs is the convolution of the laws.
- Cross-lag count. C_ji = sum_n a_n b_(n+1) over a uniform arrangement of whole rows has the exact mean
  (K_j K_i - J) / N and the exact variance of `lag1_cross_moments`, which measures the departure of the Poisson
  approximation (variance equal to the mean) used for ordered pairs of distinct columns.
"""

from __future__ import annotations

import heapq
import itertools
import math
from fractions import Fraction
from typing import Any

import numpy as np
from scipy.special import gammaln
from scipy.stats import hypergeom

LN10 = math.log(10.0)
FLOOR = -300.0  # log10 p written for a probability below the double-precision range


# --- adjacent ones -------------------------------------------------------------------------


def adjacency_pmf(n: int, k: int) -> np.ndarray:
    """pmf of the number of adjacent (1, 1) pairs of a uniform arrangement of k ones among n reads."""
    if k == 0 or n <= 0:
        return np.array([1.0])
    r = np.arange(1, min(k, n - k + 1) + 1)
    with np.errstate(over="ignore", under="ignore"):
        logp = (
            gammaln(k) - gammaln(r) - gammaln(k - r + 1)
            + gammaln(n - k + 2) - gammaln(r + 1) - gammaln(n - k + 2 - r)
            - (gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1))
        )  # fmt: skip
    pmf = np.zeros(k)
    pmf[k - r] = np.exp(logp)  # adjacency = k - R
    return pmf


def convolve(pmfs: list[np.ndarray]) -> np.ndarray:
    """pmf of the sum of independent counts; direct convolution keeps the relative accuracy of every tail.

    The two shortest laws merge first, which bounds the cost of a long list by its total support.
    """
    heap: list[tuple[int, int, np.ndarray]] = [(pmf.size, i, pmf) for i, pmf in enumerate(pmfs)]
    heapq.heapify(heap)
    counter = len(heap)
    if not heap:
        return np.array([1.0])
    while len(heap) > 1:
        _, _, a = heapq.heappop(heap)
        _, _, b = heapq.heappop(heap)
        merged = np.convolve(a, b)
        nz = np.nonzero(merged)[0]
        if nz.size:
            merged = merged[: nz[-1] + 1]
        heapq.heappush(heap, (merged.size, counter, merged))
        counter += 1
    return heap[0][2]


def _require_finite(pmf: np.ndarray) -> None:
    if not bool(np.all(np.isfinite(pmf))):
        raise ValueError("pmf holds a non-finite entry")


def log10_upper(pmf: np.ndarray, obs: int) -> float:
    """log10 P(X >= obs); FLOOR where the tail is exactly zero (obs beyond the support)."""
    _require_finite(pmf)
    if obs <= 0:
        return 0.0
    tail = float(np.sum(pmf[obs:][::-1])) if obs < pmf.size else 0.0
    return math.log10(tail) if tail > 0 else FLOOR


def log10_lower(pmf: np.ndarray, obs: int) -> float:
    """log10 P(X <= obs); FLOOR where the head is exactly zero."""
    _require_finite(pmf)
    head = float(np.sum(pmf[: obs + 1])) if obs >= 0 else 0.0
    return math.log10(min(head, 1.0)) if head > 0 else FLOOR


def log10_two_sided(pmf: np.ndarray, obs: int) -> float:
    """log10 min(1, 2 min(P(X >= obs), P(X <= obs))), the convention of the Poisson tests it replaces."""
    return min(0.0, math.log10(2.0) + min(log10_upper(pmf, obs), log10_lower(pmf, obs)))


def poisson_binomial_log10_upper(probs: list[float], k: int) -> float:
    """log10 P(number of successes >= k) over independent trials with the given success probabilities."""
    pmf = convolve([np.array([1.0 - q, q]) for q in probs])
    return log10_upper(pmf, k)


# --- runs of length at least L -------------------------------------------------------------


def _binomial_moment_numerators(n: int, k: int, big_l: int, t_max: int) -> list[int]:
    """Integers N_t = C(g, t) C(k - L t + g - 1, g - 1) for t = 0 ... t_max, g = n - k + 1.

    N_(t+1) (t+1) prod_{i<L} (u - i + g - 1) = N_t (g - t) prod_{i<L} (u - i) with u = k - L t, so each
    term follows from its predecessor by one exact integer division.
    """
    g = n - k + 1
    out = [math.comb(g, 0) * math.comb(k + g - 1, g - 1)]
    for t in range(t_max):
        u = k - big_l * t
        num = out[-1] * (g - t)
        den = t + 1
        for i in range(big_l):
            num *= u - i
            den *= u - i + g - 1
        quotient, remainder = divmod(num, den)
        if remainder:
            raise ArithmeticError("binomial-moment recurrence left a remainder")
        out.append(quotient)
    return out


def _tail_numerator(nums: list[int], t_max: int, obs: int) -> int:
    """Numerator of P(M >= obs) over the denominator C(k + g - 1, g - 1), for obs >= 1."""
    total = 0
    for t in range(obs, t_max + 1):
        term = math.comb(t - 1, obs - 1) * nums[t]
        total += term if (t - obs) % 2 == 0 else -term
    return total


def runs_ge_l_tail(n: int, k: int, big_l: int, obs: int) -> Fraction:
    """P(M >= obs) for the count M of runs of at least L ones, as an exact fraction."""
    if obs <= 0:
        return Fraction(1)
    t_max = k // big_l
    if obs > t_max:
        return Fraction(0)
    g = n - k + 1
    nums = _binomial_moment_numerators(n, k, big_l, t_max)
    return Fraction(_tail_numerator(nums, t_max, obs), math.comb(k + g - 1, g - 1))


def support_cap(n: int, k: int, big_l: int, nums: list[int] | None = None) -> int:
    """Smallest m with P(M >= m + 1) <= 1e-300, found by bisection on the exact tail.

    The pmf of a column stops at this count, so the mass it drops stays below the double-precision range.
    """
    t_max = k // big_l
    if t_max == 0:
        return 0
    g = n - k + 1
    if nums is None:
        nums = _binomial_moment_numerators(n, k, big_l, t_max)
    denom = math.comb(k + g - 1, g - 1)
    low, high = 0, t_max
    while low < high:
        mid = (low + high) // 2
        if mid + 1 > t_max or _tail_numerator(nums, t_max, mid + 1) * 10**300 <= denom:
            high = mid
        else:
            low = mid + 1
    return low


def runs_ge_l_pmf(n: int, k: int, big_l: int, m_max: int | None = None, nums: list[int] | None = None) -> np.ndarray:
    """pmf of M over m = 0 ... m_max (default: every attainable count)."""
    t_max = k // big_l
    top = t_max if m_max is None else min(m_max, t_max)
    g = n - k + 1
    denom = math.comb(k + g - 1, g - 1)
    if nums is None:
        nums = _binomial_moment_numerators(n, k, big_l, t_max)
    pmf = np.zeros(top + 1)
    for m in range(top + 1):
        total = 0
        for t in range(m, t_max + 1):
            term = math.comb(t, m) * nums[t]
            total += term if (t - m) % 2 == 0 else -term
        pmf[m] = float(Fraction(total, denom))
    return pmf


def log10_fraction(value: Fraction) -> float:
    if value <= 0:
        return FLOOR
    return max(FLOOR, math.log10(value.numerator) - math.log10(value.denominator))


EXACT_BUDGET = 2e7  # integer multiply-steps (support x moments per column) above which a pooled law is bounded


def _log_binomial_moments(n: int, k: int, big_l: int) -> np.ndarray:
    """log S_t, t = 0 ... k // L, of the count of runs of at least L ones."""
    g = n - k + 1
    nums = _binomial_moment_numerators(n, k, big_l, k // big_l)
    log_denominator = math.log(math.comb(k + g - 1, g - 1))
    # A numerator is zero where t exceeds the gap count g (C(g, t) = 0); that term of the pgf vanishes.
    return np.array([math.log(v) - log_denominator if v > 0 else -math.inf for v in nums])


def pooled_mode(columns: list[tuple[int, int]], big_l: int) -> str:
    """`exact` while the convolution cost (support x moments over columns) fits EXACT_BUDGET, else `chernoff`."""
    live = [(n, k) for n, k in columns if k >= big_l]
    cost = 0.0
    for n, k in live:
        mean = expected_runs_ge_l(n, k, big_l)
        cost += (mean + 45.0 * math.sqrt(mean) + 50) * (k // big_l)
    return "exact" if len(live) <= 1 or cost <= EXACT_BUDGET else "chernoff"


def column_law(task: tuple[int, int, int, str]) -> np.ndarray:
    """One column's law for a pooled run-count test: its pmf (`exact`) or its log binomial moments (`chernoff`)."""
    n, k, big_l, mode = task
    if mode == "exact":
        t_max = k // big_l
        nums = _binomial_moment_numerators(n, k, big_l, t_max)
        return runs_ge_l_pmf(n, k, big_l, support_cap(n, k, big_l, nums), nums)
    return _log_binomial_moments(n, k, big_l)


def pooled_exact_log10_upper(pmfs: list[np.ndarray], obs: int) -> float:
    """log10 P(total >= obs) for independent columns from their pmfs (each stops below 1e-300 of tail)."""
    return log10_upper(convolve(pmfs), obs) if obs > 0 else 0.0


def pooled_chernoff_log10_upper(logs_per_column: list[np.ndarray], obs: int) -> float:
    """log10 of the Chernoff bound on P(total >= obs), from the columns' exact log binomial moments.

    The pgf of one column is E[z^M] = sum_t S_t (z-1)^t, a sum of positive terms; the bound is
    min over z > 1 of prod_columns E[z^M] / z^obs, a valid upper bound of the exact tail.
    """
    from scipy.optimize import minimize_scalar
    from scipy.special import logsumexp

    if obs <= 0:
        return 0.0

    def log_bound(theta: float) -> float:
        u = math.log(math.expm1(theta))
        total = 0.0
        for logs in logs_per_column:
            total += float(logsumexp(logs + np.arange(logs.size) * u))
        return total - obs * theta

    result = minimize_scalar(log_bound, bounds=(1e-6, 40.0), method="bounded", options={"xatol": 1e-9})
    return max(FLOOR, min(float(result.fun), 0.0) / LN10)


def chernoff_log10_upper(columns: list[tuple[int, int]], big_l: int, obs: int) -> float:
    """Chernoff bound of the pooled tail of columns (n, k); see `pooled_chernoff_log10_upper`."""
    logs = [_log_binomial_moments(n, k, big_l) for n, k in columns if k >= big_l]
    return pooled_chernoff_log10_upper(logs, obs)


def runs_ge_l_log10_upper(columns: list[tuple[int, int]], big_l: int, obs: int) -> float:
    """log10 P(total >= obs) for the summed run counts of independent columns (n, k)."""
    live = [(n, k) for n, k in columns if k >= big_l]
    if obs <= 0:
        return 0.0
    if not live:
        return FLOOR
    if len(live) == 1:
        return log10_fraction(runs_ge_l_tail(live[0][0], live[0][1], big_l, obs))
    return pooled_exact_log10_upper([column_law((n, k, big_l, "exact")) for n, k in live], obs)


def expected_runs_ge_l(n: int, k: int, big_l: int) -> float:
    """E[M] from the binomial moment S_1 (exact)."""
    if k < big_l:
        return 0.0
    g = n - k + 1
    return float(Fraction(g * math.comb(k - big_l + g - 1, g - 1), math.comb(k + g - 1, g - 1)))


# --- same-shot pair count ------------------------------------------------------------------


def hypergeom_log10_two_sided(joint: np.ndarray, n: int, k_i: np.ndarray, k_j: np.ndarray) -> np.ndarray:
    """log10 two-sided p of the joint counts under the hypergeometric (n, K_i, K_j) law."""
    upper = hypergeom.logsf(joint - 1, n, k_i, k_j) / LN10
    lower = hypergeom.logcdf(joint, n, k_i, k_j) / LN10
    return np.minimum(0.0, math.log10(2.0) + np.minimum(upper, lower))


def hypergeom_pmf_grid(n: int, k_i: np.ndarray, k_j: np.ndarray, width: int) -> np.ndarray:
    """(pairs, width) pmf of the hypergeometric (n, K_i, K_j) counts 0 ... width - 1 for each pair."""
    x = np.arange(width)[None, :]
    ki = k_i[:, None].astype(np.float64)
    kj = k_j[:, None].astype(np.float64)
    valid = (x <= np.minimum(ki, kj)) & (kj - x <= n - ki)
    with np.errstate(invalid="ignore", over="ignore"):
        logp = (
            gammaln(ki + 1) - gammaln(x + 1) - gammaln(np.where(valid, ki - x, 0) + 1)
            + gammaln(n - ki + 1) - gammaln(np.where(valid, kj - x, 0) + 1)
            - gammaln(np.where(valid, n - ki - kj + x, 0) + 1)
            - (gammaln(n + 1) - gammaln(kj + 1) - gammaln(n - kj + 1))
        )  # fmt: skip
    return np.where(valid, np.exp(np.where(valid, logp, -np.inf)), 0.0)


def pooled_hypergeom_log10_two_sided(units: list[tuple[int, np.ndarray, np.ndarray]], joint: np.ndarray) -> np.ndarray:
    """Two-sided log10 p of the pooled joint counts of pairs over independent PUBs.

    units holds (n, K_i, K_j) per PUB with K_i, K_j arrays over the pairs; joint is the pooled count per pair.
    The pooled law of a pair is the convolution of its per-PUB hypergeometric laws.
    """
    pairs = joint.size
    width = 1 + int(max(np.minimum(ki, kj).max() for _, ki, kj in units))
    grids = [hypergeom_pmf_grid(n, ki, kj, width) for n, ki, kj in units]
    out = np.empty(pairs)
    for p in range(pairs):
        pmf = convolve([g[p] for g in grids])
        out[p] = log10_two_sided(pmf, int(joint[p]))
    return out


# --- lag-1 cross count: exact first two moments --------------------------------------------


def _ff(x: Any, m: int) -> Any:
    out = 1.0
    for i in range(m):
        out = out * (x - i)
    return out


def lag1_cross_moments(n: int, k_j: Any, k_i: Any, joint: Any) -> tuple[Any, Any]:
    """Exact mean and variance of C_ji = sum_(m=1)^(n-1) a_m b_(m+1) over uniform arrangements of whole rows.

    a, b are the 0/1 columns of K_j and K_i ones whose joint count is `joint` (scalars or arrays of equal shape).
    Row classes: both (J), a only (alpha) and b only (beta); the moments follow from the numbers of ordered
    tuples of distinct rows (t2 pairs, t3 triples, t4 quadruples).
    """
    k_j = np.asarray(k_j, dtype=np.float64)
    k_i = np.asarray(k_i, dtype=np.float64)
    joint = np.asarray(joint, dtype=np.float64)
    alpha = k_j - joint
    beta = k_i - joint
    t2 = k_j * k_i - joint
    t3 = joint * ((k_j - 1) * (k_i - 1) - (joint - 1))
    t4 = 0.0
    for a in range(3):
        for b in range(3):
            t4 = t4 + math.comb(2, a) * math.comb(2, b) * _ff(joint, a + b) * _ff(alpha, 2 - a) * _ff(beta, 2 - b)
    mean = t2 / n
    e_adjacent = t3 / (n * (n - 1) * (n - 2)) if n > 2 else 0.0
    e_far = t4 / (n * (n - 1) * (n - 2) * (n - 3)) if n > 3 else 0.0
    n_pos = n - 1
    n_adjacent = max(n - 2, 0)
    n_far = n_pos * (n_pos - 1) // 2 - n_adjacent
    second = mean + 2 * (n_adjacent * e_adjacent + n_far * e_far)
    return mean, second - mean * mean


# --- verification by enumeration ------------------------------------------------------------


def _check_adjacency() -> dict[str, Any]:
    worst = 0.0
    for n in range(2, 11):
        for k in range(0, n + 1):
            counts: dict[int, int] = {}
            for ones in itertools.combinations(range(n), k):
                col = np.zeros(n, dtype=int)
                col[list(ones)] = 1
                adj = int((col[:-1] * col[1:]).sum())
                counts[adj] = counts.get(adj, 0) + 1
            total = math.comb(n, k)
            pmf = adjacency_pmf(n, k)
            for a in range(max(pmf.size, max(counts) + 1)):
                exact = counts.get(a, 0) / total
                got = pmf[a] if a < pmf.size else 0.0
                worst = max(worst, abs(exact - got))
    return {"cases": "n 2..10, every k", "max_abs_error": worst}


def _check_runs() -> dict[str, Any]:
    worst = 0.0
    worst_mean = 0.0
    for n in range(3, 13):
        for k in range(0, n + 1):
            for big_l in (1, 2, 3, 5):
                counts: dict[int, int] = {}
                for ones in itertools.combinations(range(n), k):
                    col = np.zeros(n + 2, dtype=int)
                    col[[o + 1 for o in ones]] = 1
                    d = np.diff(col)
                    lengths = np.where(d == -1)[0] - np.where(d == 1)[0]
                    m = int((lengths >= big_l).sum())
                    counts[m] = counts.get(m, 0) + 1
                total = math.comb(n, k)
                pmf = runs_ge_l_pmf(n, k, big_l)
                for m in range(max(pmf.size, max(counts) + 1)):
                    exact = counts.get(m, 0) / total
                    got = pmf[m] if m < pmf.size else 0.0
                    worst = max(worst, abs(exact - got))
                    tail_exact = sum(v for kk, v in counts.items() if kk >= m) / total
                    tail = float(runs_ge_l_tail(n, k, big_l, m))
                    worst = max(worst, abs(tail_exact - tail))
                mean_exact = sum(kk * v for kk, v in counts.items()) / total
                worst_mean = max(worst_mean, abs(mean_exact - expected_runs_ge_l(n, k, big_l)))
    return {
        "cases": "n 3..12, every k, L in 1,2,3,5",
        "max_abs_error_pmf_and_tail": worst,
        "max_abs_error_mean": worst_mean,
    }


def _check_mean_formula() -> dict[str, Any]:
    """The mean equals E_L = (N-L+1) F_L - (N-L) F_(L+1) of a5_run_length.py."""

    def falling(n: int, k: int, m: int) -> float:
        out = 1.0
        for i in range(m):
            out *= max(k - i, 0) / (n - i)
        return out

    worst = 0.0
    for n, k, big_l in ((200, 30, 2), (3072, 40, 3), (16384, 900, 5), (32768, 3000, 2)):
        e_l = (n - big_l + 1) * falling(n, k, big_l) - (n - big_l) * falling(n, k, big_l + 1)
        worst = max(worst, abs(e_l - expected_runs_ge_l(n, k, big_l)) / e_l)
    return {"max_relative_difference": worst}


def _check_hypergeom() -> dict[str, Any]:
    # exact sum of math.comb terms against scipy logsf in the far tail (a heavy pair of the state-prep PUBs)
    n, ki, kj, joint = 16384, 420, 350, 120

    def pmf(x: int) -> Fraction:
        return Fraction(math.comb(ki, x) * math.comb(n - ki, kj - x), math.comb(n, kj))

    tail = sum(pmf(x) for x in range(joint, min(ki, kj) + 1))
    exact = math.log10(tail.numerator) - math.log10(tail.denominator)
    got = float(hypergeom.logsf(joint - 1, n, ki, kj) / LN10)
    grid = hypergeom_pmf_grid(n, np.array([ki]), np.array([kj]), min(ki, kj) + 1)[0]
    grid_tail = math.log10(float(np.sum(grid[joint:][::-1])))
    return {"log10_tail_exact": exact, "log10_tail_scipy": got, "log10_tail_grid": grid_tail}


def _check_cross_moments() -> dict[str, Any]:
    worst_mean = 0.0
    worst_var = 0.0
    n = 8
    for k_j, k_i, joint in ((3, 4, 1), (2, 2, 0), (5, 3, 3), (4, 4, 2), (1, 6, 1), (0, 3, 0)):
        rows = [(1, 1)] * joint + [(1, 0)] * (k_j - joint) + [(0, 1)] * (k_i - joint)
        rows += [(0, 0)] * (n - len(rows))
        vals = []
        for perm in set(itertools.permutations(rows)):
            vals.append(sum(perm[m][0] * perm[m + 1][1] for m in range(n - 1)))
        mean_b = float(np.mean(vals))
        var_b = float(np.var(vals))
        mean_f, var_f = lag1_cross_moments(n, k_j, k_i, joint)
        worst_mean = max(worst_mean, abs(mean_b - float(mean_f)))
        worst_var = max(worst_var, abs(var_b - float(var_f)))
    return {
        "cases": "n 8, six margin sets, all distinct row orders",
        "max_abs_mean": worst_mean,
        "max_abs_var": worst_var,
    }


def _check_chernoff() -> dict[str, Any]:
    columns = [(64, 20), (64, 25), (48, 12)]
    rows = []
    for big_l, obs in ((2, 9), (2, 14), (3, 5)):
        pmf = convolve([runs_ge_l_pmf(n, k, big_l) for n, k in columns])
        exact = log10_upper(pmf, obs)
        bound = chernoff_log10_upper(columns, big_l, obs)
        rows.append(
            {"L": big_l, "obs": obs, "log10_exact": exact, "log10_bound": bound, "bound_holds": bound >= exact - 1e-9}
        )
    return {"cases": rows}


def _check_support_cap() -> dict[str, Any]:
    rows = []
    for n, k, big_l in ((32768, 400, 2), (32768, 3000, 3), (4096, 40, 2)):
        cap = support_cap(n, k, big_l)
        dropped = runs_ge_l_tail(n, k, big_l, cap + 1)
        kept = runs_ge_l_tail(n, k, big_l, cap)
        rows.append(
            {
                "n": n,
                "k": k,
                "L": big_l,
                "cap": cap,
                "mean": expected_runs_ge_l(n, k, big_l),
                "log10_dropped_mass": log10_fraction(dropped) if dropped > 0 else None,
                "log10_tail_at_cap": log10_fraction(kept) if kept > 0 else None,
            }
        )
    return {"cases": rows}


# Enumeration references. Each statistic is counted over every arrangement with Python integers, so the
# reference carries no floating-point error and shares no code with the laws under test.

ENUM_TOL = 1e-9  # tolerance on a log10 p-value or a probability; the laws carry about 1e-13 relative error


def _arrangements(n: int, k: int) -> list[np.ndarray]:
    out = []
    for ones in itertools.combinations(range(n), k):
        col = np.zeros(n, dtype=np.int64)
        col[list(ones)] = 1
        out.append(col)
    return out


def _adjacency_counts(n: int, k: int) -> dict[int, int]:
    counts: dict[int, int] = {}
    for col in _arrangements(n, k):
        value = int((col[:-1] * col[1:]).sum())
        counts[value] = counts.get(value, 0) + 1
    return counts


def _runs_counts(n: int, k: int, big_l: int) -> dict[int, int]:
    counts: dict[int, int] = {}
    for col in _arrangements(n, k):
        padded = np.concatenate([[0], col, [0]])
        d = np.diff(padded)
        lengths = np.where(d == -1)[0] - np.where(d == 1)[0]
        value = int((lengths >= big_l).sum())
        counts[value] = counts.get(value, 0) + 1
    return counts


def _convolve_counts(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for x, cx in a.items():
        for y, cy in b.items():
            out[x + y] = out.get(x + y, 0) + cx * cy
    return out


def _exact_log10(num: int, den: int) -> float:
    return max(FLOOR, math.log10(num / den)) if num > 0 else FLOOR


def _tail_errors(counts: dict[int, int], pmf: np.ndarray, upper_fn: Any = None) -> tuple[float, float]:
    """Worst absolute differences of the pmf and of the upper, lower and two-sided log10 tails against counts.

    The observed count runs over 0 ... top + 2, so it covers the lowest count (0), the next (1), the largest
    attainable count and counts beyond the support. `upper_fn` replaces `log10_upper(pmf, obs)` where the law
    under test is a dedicated tail function.
    """
    total = sum(counts.values())
    top = max(counts)
    worst_pmf = 0.0
    for x in range(max(pmf.size, top + 1)):
        got = float(pmf[x]) if x < pmf.size else 0.0
        worst_pmf = max(worst_pmf, abs(counts.get(x, 0) / total - got))
    worst_tail = 0.0
    for obs in range(0, top + 3):
        num_up = sum(v for x, v in counts.items() if x >= obs)
        num_low = sum(v for x, v in counts.items() if x <= obs)
        exact_up = 0.0 if obs <= 0 else _exact_log10(num_up, total)
        exact_low = min(0.0, _exact_log10(num_low, total))
        exact_two = min(0.0, math.log10(2.0) + min(exact_up, exact_low))
        got_up = upper_fn(obs) if upper_fn is not None else log10_upper(pmf, obs)
        got_low = log10_lower(pmf, obs)
        got_two = min(0.0, math.log10(2.0) + min(got_up, got_low))
        worst_tail = max(worst_tail, abs(exact_up - got_up), abs(exact_low - got_low), abs(exact_two - got_two))
        if obs <= top + 1:
            two_sided = log10_two_sided(pmf, obs)
            worst_tail = max(worst_tail, abs(exact_two - two_sided))
    return worst_pmf, worst_tail


def _check_hypergeom_enumeration() -> dict[str, Any]:
    """Joint count of two columns over every arrangement of the second against the hypergeometric (n, K_i, K_j)."""
    worst_pmf = 0.0
    worst_tail = 0.0
    cases = 0
    for n in range(1, 9):
        for k_i in range(0, n + 1):
            for k_j in range(0, n + 1):
                counts: dict[int, int] = {}
                first = np.zeros(n, dtype=np.int64)
                first[:k_i] = 1
                for col in _arrangements(n, k_j):
                    value = int((first * col).sum())
                    counts[value] = counts.get(value, 0) + 1
                total = math.comb(n, k_j)
                width = min(k_i, k_j) + 1
                grid = hypergeom_pmf_grid(n, np.array([k_i]), np.array([k_j]), width)[0]
                for x in range(width):
                    worst_pmf = max(worst_pmf, abs(counts.get(x, 0) / total - float(grid[x])))
                top = max(counts)
                for obs in range(0, top + 2):
                    num_up = sum(v for x, v in counts.items() if x >= obs)
                    num_low = sum(v for x, v in counts.items() if x <= obs)
                    exact = min(
                        0.0, math.log10(2.0) + min(_exact_log10(num_up, total), min(0.0, _exact_log10(num_low, total)))
                    )
                    got = float(hypergeom_log10_two_sided(np.array([obs]), n, np.array([k_i]), np.array([k_j]))[0])
                    # scipy reports -inf for a tail of exactly zero; the reference writes FLOOR there
                    if not math.isfinite(got):
                        got = math.log10(2.0) + FLOOR
                    worst_tail = max(worst_tail, abs(exact - got))
                cases += 1
    return {
        "cases": f"n 1..8, every (K_i, K_j): {cases} margin pairs, every arrangement of one column",
        "max_abs_error_pmf": worst_pmf,
        "max_abs_error_log10_two_sided": worst_tail,
        "holds": worst_pmf < ENUM_TOL and worst_tail < ENUM_TOL,
    }


def _check_pooled_adjacency() -> dict[str, Any]:
    """Convolution of two units' adjacency laws against the pooled count over every pair of arrangements."""
    units = [(n, k) for n in range(1, 7) for k in range(0, n + 1)]
    per_unit = {u: _adjacency_counts(*u) for u in units}
    worst_pmf = 0.0
    worst_tail = 0.0
    for a, b in itertools.combinations_with_replacement(units, 2):
        counts = _convolve_counts(per_unit[a], per_unit[b])
        pmf = convolve([adjacency_pmf(*a), adjacency_pmf(*b)])
        e_pmf, e_tail = _tail_errors(counts, pmf)
        worst_pmf = max(worst_pmf, e_pmf)
        worst_tail = max(worst_tail, e_tail)
    return {
        "cases": "two units, n 1..6, every k each (k = 0, 1 and n included), every observed count 0 .. top + 2",
        "max_abs_error_pmf": worst_pmf,
        "max_abs_error_log10_tails": worst_tail,
        "holds": worst_pmf < ENUM_TOL and worst_tail < ENUM_TOL,
    }


def _check_pooled_runs() -> dict[str, Any]:
    """Convolution of two units' runs-of-length-at-least-L laws against the pooled count over every pair."""
    worst_pmf = 0.0
    worst_tail = 0.0
    for big_l in (1, 2, 3):
        units = [(n, k) for n in range(1, 7) for k in range(0, n + 1)]
        per_unit = {u: _runs_counts(u[0], u[1], big_l) for u in units}
        for a, b in itertools.combinations_with_replacement(units, 2):
            counts = _convolve_counts(per_unit[a], per_unit[b])
            pmf = convolve([runs_ge_l_pmf(a[0], a[1], big_l), runs_ge_l_pmf(b[0], b[1], big_l)])

            def upper(obs: int, a: tuple[int, int] = a, b: tuple[int, int] = b, big_l: int = big_l) -> float:
                return runs_ge_l_log10_upper([a, b], big_l, obs)

            e_pmf, e_tail = _tail_errors(counts, pmf, upper)
            worst_pmf = max(worst_pmf, e_pmf)
            worst_tail = max(worst_tail, e_tail)
    return {
        "cases": "two units, n 1..6, every k each (k = 0, 1 and n included), L in 1, 2, 3, every observed count",
        "max_abs_error_pmf": worst_pmf,
        "max_abs_error_log10_tails": worst_tail,
        "holds": worst_pmf < ENUM_TOL and worst_tail < ENUM_TOL,
    }


def _check_cross_moments_small() -> dict[str, Any]:
    """Mean and variance of the lag-1 cross count against every distinct row order, n = 2 ... 5, every margin triple."""
    worst_mean = 0.0
    worst_var = 0.0
    cases = 0
    for n in range(2, 6):
        for joint in range(0, n + 1):
            for k_j in range(joint, n + 1):
                for k_i in range(joint, n + 1):
                    if k_j + k_i - joint > n:
                        continue
                    rows = [(1, 1)] * joint + [(1, 0)] * (k_j - joint) + [(0, 1)] * (k_i - joint)
                    rows += [(0, 0)] * (n - len(rows))
                    values = [
                        sum(perm[m][0] * perm[m + 1][1] for m in range(n - 1))
                        for perm in sorted(set(itertools.permutations(rows)))
                    ]
                    count = len(values)
                    mean_b = Fraction(sum(values), count)
                    var_b = Fraction(sum(v * v for v in values), count) - mean_b * mean_b
                    mean_f, var_f = lag1_cross_moments(n, k_j, k_i, joint)
                    worst_mean = max(worst_mean, abs(float(mean_b) - float(mean_f)))
                    worst_var = max(worst_var, abs(float(var_b) - float(var_f)))
                    cases += 1
    return {
        "cases": f"n 2..5, every margin triple (K_j, K_i, J): {cases} triples, all distinct row orders",
        "max_abs_mean": worst_mean,
        "max_abs_var": worst_var,
        "holds": worst_mean < ENUM_TOL and worst_var < ENUM_TOL,
    }


def _check_chernoff_every_count() -> dict[str, Any]:
    """The Chernoff bound of a pooled tail is at least the exact tail at every count of small cases.

    The case (6, 6), (6, 6) with L = 2 has binomial-moment numerators of zero (one gap, so C(g, t) = 0 for t > 1).
    """
    cases = [
        ([(6, 6), (6, 6)], 2),
        ([(8, 4), (8, 3)], 2),
        ([(10, 5), (9, 4), (7, 3)], 2),
        ([(10, 6), (8, 5)], 3),
        ([(12, 5), (12, 6), (6, 2)], 1),
    ]
    rows = []
    for columns, big_l in cases:
        pmf = convolve([runs_ge_l_pmf(n, k, big_l) for n, k in columns])
        holds = True
        worst_gap = math.inf
        for obs in range(0, pmf.size + 2):
            exact = log10_upper(pmf, obs)
            bound = chernoff_log10_upper(columns, big_l, obs)
            holds = holds and bound >= exact - ENUM_TOL
            worst_gap = min(worst_gap, bound - exact)
        rows.append({"columns": columns, "L": big_l, "counts": pmf.size + 2, "min_bound_minus_exact": worst_gap})
        rows[-1]["holds"] = holds
    return {"cases": rows, "holds": all(r["holds"] for r in rows)}


def self_test() -> dict[str, Any]:
    return {
        "adjacency_law": _check_adjacency(),
        "runs_at_least_L_law": _check_runs(),
        "runs_mean_equals_E_L": _check_mean_formula(),
        "hypergeometric_far_tail": _check_hypergeom(),
        "lag1_cross_moments": _check_cross_moments(),
        "chernoff_bound": _check_chernoff(),
        "support_cap": _check_support_cap(),
        "hypergeometric_same_shot_enumeration": _check_hypergeom_enumeration(),
        "adjacency_pooled_two_units": _check_pooled_adjacency(),
        "runs_pooled_two_units": _check_pooled_runs(),
        "lag1_cross_moments_n2_to_5": _check_cross_moments_small(),
        "chernoff_bound_every_count": _check_chernoff_every_count(),
    }


def failed_checks(report: Any, path: str = "") -> list[str]:
    """Paths of every `holds` or `bound_holds` flag that reads False in a self-test report."""
    found: list[str] = []
    if isinstance(report, dict):
        for key, value in report.items():
            if key in ("holds", "bound_holds") and value is False:
                found.append(path or key)
            else:
                found += failed_checks(value, f"{path}/{key}")
    elif isinstance(report, list):
        for index, value in enumerate(report):
            found += failed_checks(value, f"{path}[{index}]")
    return found


if __name__ == "__main__":
    import json

    result = self_test()
    print(json.dumps(result, indent=1))
    failures = failed_checks(result)
    if failures:
        raise SystemExit(f"self-test failed: {failures}")
