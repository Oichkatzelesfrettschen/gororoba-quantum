"""Shared helpers of the offline residual-structure pass over retained Tuna-17 and Quandela records.

Every script in this directory imports this module, so the repository paths, the exact interval and
multiple-testing helpers and the test-ledger row format live in one place. No random generator is drawn
anywhere in the pass: nulls are analytic (binomial, chi-square, normal) or deterministic enumerations.

Run as: GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1 GOROROBA_WORKERS=4
        systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 "$PYTHON" -B SCRIPT.py
Self-test of the weighted chi-square tail (`weighted_chi2_log10_sf` against scipy.stats.chi2.logsf), from this
directory: `"$PYTHON" -B common.py --self-test` (exit 0 on success, a message and exit 1 on failure).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for extra in (ROOT / "scripts", ROOT / "gororoba_quantum"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

QI_RUNS = ROOT / "results" / "quantum_inspire" / "runs"
QD_RUNS = ROOT / "results" / "quandela" / "runs"
Z95 = 1.959963984540054
ALPHA = 0.05
SADDLEPOINT_TOLERANCE_LOG10 = 0.07


def rel(path: Path) -> str:
    """A path relative to the repository root, so no absolute path enters an output."""
    return str(path.resolve().relative_to(ROOT))


def write_json(name: str, value: Any) -> Path:
    path = HERE / name
    path.write_text(json.dumps(value, indent=1, sort_keys=True, default=_default) + "\n")
    return path


def _default(value: Any) -> Any:
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except ImportError:
        pass
    raise TypeError(f"not serializable: {type(value)}")


def sig(value: float, digits: int = 5) -> float:
    return float(f"{value:.{digits}g}")


def wilson(k: int, n: int, z: float = Z95) -> list[float]:
    """Wilson score interval of a binomial proportion."""
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [sig(max(0.0, c - h)), sig(min(1.0, c + h))]


def normal_two_sided_log10(z: float) -> float:
    """log10 of the two-sided normal tail, finite for large |z|."""
    from scipy.special import log_ndtr

    return float((math.log(2.0) + log_ndtr(-abs(z))) / math.log(10.0))


def log10_p_text(log10_p: float) -> str:
    if log10_p > -4:
        return f"{10**log10_p:.3g}"
    return f"1e{log10_p:.1f}"


def ledger_row(
    test_id: str,
    analysis: int,
    description: str,
    log10_p: float,
    effect: Any,
    ci: Any = None,
    note: str = "",
    dependent: str = "",
    alternatives: dict[str, float] | None = None,
) -> dict[str, Any]:
    """One hypothesis test in the pass-wide ledger; p enters as log10 so astronomically small tails stay finite.

    `dependent` is empty when the p-value rests on independent units and otherwise names the shared structure
    (shots, jobs of one series, overlapping runs) that makes the p-value a statement about a larger effective sample
    than the data hold; such a row stays in the ledger and is excluded from the dependence-safe survivor family.
    `alternatives` maps a method name to the log10 p-value another method gave for the same test; the key
    `prior_method` holds the value the ledger carried before the method of this row replaced it.
    """
    return {
        "test_id": test_id,
        "analysis": analysis,
        "description": description,
        "log10_p": sig(min(0.0, log10_p), 6),
        "effect": effect,
        "ci95": ci,
        "note": note,
        "dependent": dependent,
        "alternatives": {k: sig(min(0.0, v), 6) for k, v in (alternatives or {}).items()},
    }


def benjamini_hochberg(log10_ps: list[float], q: float = ALPHA) -> list[bool]:
    """BH step-up decisions at FDR q for p-values given as log10."""
    m = len(log10_ps)
    order = sorted(range(m), key=lambda i: log10_ps[i])
    cutoff = -1
    for rank, i in enumerate(order, start=1):
        if log10_ps[i] <= math.log10(q * rank / m):
            cutoff = rank
    keep = [False] * m
    for rank, i in enumerate(order, start=1):
        if rank <= cutoff:
            keep[i] = True
    return keep


def benjamini_yekutieli(log10_ps: list[float], q: float = ALPHA) -> list[bool]:
    """BY step-up decisions at FDR q: BH at q / sum_{i<=m} 1/i, valid under any dependence among the p-values."""
    m = len(log10_ps)
    harmonic = sum(1.0 / i for i in range(1, m + 1))
    return benjamini_hochberg(log10_ps, q / harmonic) if m else []


def bonferroni(log10_ps: list[float], q: float = ALPHA) -> list[bool]:
    """Bonferroni decisions: valid under any dependence when each p-value is valid."""
    m = len(log10_ps)
    return [p <= math.log10(q / m) for p in log10_ps]


def survivors(log10_ps: list[float]) -> dict[str, list[bool]]:
    """Bonferroni, BH and BY decisions over one family of tests."""
    return {
        "bonferroni": bonferroni(log10_ps),
        "bh": benjamini_hochberg(log10_ps),
        "by": benjamini_yekutieli(log10_ps),
    }


def summarize_ledger(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Within-analysis Bonferroni, BH and BY over the ledger rows of one script."""
    ps = [row["log10_p"] for row in rows]
    decisions = survivors(ps)
    m = len(rows)
    return {
        "tests": m,
        "bonferroni_alpha": sig(ALPHA / m) if m else None,
        "rows": [
            {**row, "bh_significant": a, "bonferroni_significant": b, "by_significant": y}
            for row, a, b, y in zip(rows, decisions["bh"], decisions["bonferroni"], decisions["by"], strict=True)
        ],
    }


def weighted_chi2_log10_sf(x: float, weights: list[float], dofs: list[int]) -> dict[str, float]:
    """Upper tail of sum_i weights[i] * chi2(dofs[i]) at x, as log10 p, in the far tail.

    The Chernoff bound (`chernoff`) is a guaranteed upper bound on the tail, so it is a valid conservative
    p-value; the Lugannani-Rice saddlepoint approximation (`saddlepoint`) is the accurate reading. Both use the
    cumulant K(t) = -1/2 sum_i dofs[i] ln(1 - 2 t weights[i]) solved at K'(t) = x. A value at or below the mean
    returns 0 for both.

    The saddlepoint tail is P = 1 - Phi(w) + phi(w) (1/u - 1/w) with w = sqrt(2 (t x - K(t))) and
    u = t sqrt(K''(t)). The correction 1/u - 1/w takes either sign: a positive one is added and a negative one
    subtracted, both in log space. When the subtraction would leave no positive tail (the correction at least as
    large as 1 - Phi(w)), `saddlepoint` falls back to the Chernoff bound. For equal weights the value agrees with
    scipy.stats.chi2.logsf of x / weight to 0.06 in log10 (measured maximum 0.058, at dof 1 and x = 1000, over
    dofs 1 to 10 and x from the mean to 1000; the error grows with x and shrinks with the dof), and `self_test`
    raises beyond 0.07.
    """
    from scipy.optimize import brentq
    from scipy.special import log_ndtr

    lam = [w for w in weights if w > 0]
    dof = [d for w, d in zip(weights, dofs, strict=True) if w > 0]
    mean = sum(w * d for w, d in zip(lam, dof, strict=True))
    if x <= mean:
        return {"chernoff": 0.0, "saddlepoint": 0.0}
    top = 1.0 / (2.0 * max(lam))

    def k0(t: float) -> float:
        return -0.5 * sum(d * math.log1p(-2.0 * t * w) for w, d in zip(lam, dof, strict=True))

    def k1(t: float) -> float:
        return sum(d * w / (1.0 - 2.0 * t * w) for w, d in zip(lam, dof, strict=True))

    def k2(t: float) -> float:
        return 2.0 * sum(d * w * w / (1.0 - 2.0 * t * w) ** 2 for w, d in zip(lam, dof, strict=True))

    t_hat = float(brentq(lambda t: k1(t) - x, 0.0, top * (1.0 - 1e-15), xtol=1e-18, rtol=1e-14, maxiter=500))
    log_chernoff = k0(t_hat) - t_hat * x
    w_stat = math.sqrt(2.0 * (t_hat * x - k0(t_hat)))
    u_stat = t_hat * math.sqrt(k2(t_hat))
    log_phi = -0.5 * w_stat * w_stat - 0.5 * math.log(2.0 * math.pi)
    correction = 1.0 / u_stat - 1.0 / w_stat
    log_p = float(log_ndtr(-w_stat))
    if correction > 0:
        log_extra = log_phi + math.log(correction)
        high, low = max(log_p, log_extra), min(log_p, log_extra)
        log_p = high + math.log1p(math.exp(low - high))
    elif correction < 0:
        log_extra = log_phi + math.log(-correction)
        if log_extra < log_p:
            log_p += math.log1p(-math.exp(log_extra - log_p))
        else:
            log_p = log_chernoff
    ln10 = math.log(10.0)
    return {"chernoff": min(0.0, log_chernoff / ln10), "saddlepoint": min(0.0, log_p / ln10)}


def poisson_binomial_log10_sf(k: int, probs: list[float]) -> float:
    """log10 P(at least k of independent Bernoulli(probs[i]) events), by exact dynamic programming."""
    if k <= 0:
        return 0.0
    dist = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dist) + 1)
        for j, mass in enumerate(dist):
            nxt[j] += mass * (1.0 - p)
            nxt[j + 1] += mass * p
        dist = nxt
    tail = math.fsum(dist[k:])
    return math.log10(max(tail, 1e-300))


def chi2_log10_sf(x: float, dof: int) -> float:
    """log10 P(chi2(dof) > x), finite far into the tail."""
    from scipy.stats import chi2

    value = float(chi2.logsf(x, dof))
    if math.isfinite(value):
        return value / math.log(10.0)
    # asymptotic series of the regularized upper incomplete gamma, as in qi_shot_record_line.chi2_log10_tail
    a, y = dof / 2, x / 2
    series, term = 1.0, 1.0
    for j in range(1, 12):
        term *= (a - j) / y
        series += term
    return float((-y + (a - 1) * math.log(y) - math.lgamma(a) + math.log(series)) / math.log(10.0))


def self_test() -> None:
    """Check `weighted_chi2_log10_sf` against scipy's chi-square tail; raises on a failure.

    Equal weights reduce the weighted sum to w * chi2(sum dofs), whose tail scipy.stats.chi2.logsf supplies to
    double precision. The saddlepoint value must lie within SADDLEPOINT_TOLERANCE_LOG10 of it and not above the
    Chernoff bound, and the Chernoff bound must not fall below the exact tail.
    """
    from scipy.stats import chi2

    cases: list[tuple[list[float], list[int], float]] = [
        ([1.0], [1], 20.0),
        ([1.0], [1], 1000.0),
        ([1.0], [2], 20.0),
        ([1.0], [2], 1000.0),
        ([1.0], [4], 60.0),
        ([1.0], [10], 200.0),
        ([2.0], [2], 40.0),
        ([0.5], [4], 12.0),
        ([3.0, 3.0], [1, 1], 45.0),
        ([1.0, 0.0], [2, 5], 20.0),
    ]
    ln10 = math.log(10.0)
    for weights, dofs, x in cases:
        live = [(w, d) for w, d in zip(weights, dofs, strict=True) if w > 0]
        scale = live[0][0]
        exact = float(chi2.logsf(x / scale, sum(d for _, d in live))) / ln10
        got = weighted_chi2_log10_sf(x, weights, dofs)
        error = got["saddlepoint"] - exact
        if abs(error) > SADDLEPOINT_TOLERANCE_LOG10:
            raise SystemExit(f"saddlepoint {got['saddlepoint']} against exact {exact}: {weights} {dofs} {x}")
        if got["saddlepoint"] > got["chernoff"] + 1e-12 or got["chernoff"] < exact - 1e-12:
            raise SystemExit(f"Chernoff bound ordering fails: {got} against exact {exact}: {weights} {dofs} {x}")
    if weighted_chi2_log10_sf(1.0, [1.0], [2]) != {"chernoff": 0.0, "saddlepoint": 0.0}:
        raise SystemExit("a value at or below the mean must return 0 for both readings")
    print(f"weighted_chi2_log10_sf self-test passed ({len(cases)} cases, tolerance {SADDLEPOINT_TOLERANCE_LOG10})")


if __name__ == "__main__":
    if sys.argv[1:] != ["--self-test"]:
        raise SystemExit("usage: common.py --self-test")
    self_test()
