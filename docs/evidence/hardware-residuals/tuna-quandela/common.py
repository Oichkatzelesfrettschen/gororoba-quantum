"""Shared helpers of the offline residual-structure pass over retained Tuna-17 and Quandela records.

Every script in this directory imports this module, so the repository paths, the exact interval and
multiple-testing helpers and the test-ledger row format live in one place. No random generator is drawn
anywhere in the pass: nulls are analytic (binomial, chi-square, normal) or deterministic enumerations.

Run as: GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1 GOROROBA_WORKERS=4
        systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 "$PYTHON" -B SCRIPT.py
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
) -> dict[str, Any]:
    """One hypothesis test in the pass-wide ledger; p enters as log10 so astronomically small tails stay finite."""
    return {
        "test_id": test_id,
        "analysis": analysis,
        "description": description,
        "log10_p": sig(min(0.0, log10_p), 6),
        "effect": effect,
        "ci95": ci,
        "note": note,
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


def bonferroni(log10_ps: list[float], q: float = ALPHA) -> list[bool]:
    m = len(log10_ps)
    return [p <= math.log10(q / m) for p in log10_ps]


def summarize_ledger(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Within-analysis BH and Bonferroni over the ledger rows of one script."""
    ps = [row["log10_p"] for row in rows]
    bh = benjamini_hochberg(ps)
    bf = bonferroni(ps)
    m = len(rows)
    return {
        "tests": m,
        "bonferroni_alpha": sig(ALPHA / m) if m else None,
        "rows": [
            {**row, "bh_significant": a, "bonferroni_significant": b} for row, a, b in zip(rows, bh, bf, strict=True)
        ],
    }


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
