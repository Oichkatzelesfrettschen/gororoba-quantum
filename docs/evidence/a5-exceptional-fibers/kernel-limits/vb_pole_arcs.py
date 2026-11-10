"""Limits of ker L_a along arcs of the closure of E8-bar through a VB point on which e tends to 0 or to infinity.

vb_limit_span.py keeps e = E0 + ... at a finite nonzero value. Phi(w, rho, sigma, e, zeta) of ../arcs depends on e
through nu = (e + 1)^2 / (4 e) and omega = (e^2 - 1) / (4 e), which enter only multiplied by m^2 - 1 = w (w + 2), so
Phi extends to arcs with e = E s^k (1 + ...) whenever w has order above k: with q = w (w + 2) / e the products are
(m^2 - 1) nu = q (e + 1)^2 / 4 and (m^2 - 1) omega = q (e^2 - 1) / 4. Such an arc still ends at the VB point
w = rho = sigma = 0, and e -> 1/e keeps nu and reverses omega, so the arcs with e -> infinity are the same arcs with
omega reversed (`flip`). A pattern fixes k, the leading orders of w, rho and sigma and the flip. The record holds the
span of the Plucker vectors of the finite-e patterns with all leading orders 1 and 2 (rank 22 in
vb-limit-span-result.json), then the rank after each pole pattern joins: a rank above 22 shows a limit outside the
span of the finite-e family.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/vb_pole_arcs.py
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import plucker_limits as limits
import vb_limit_span as span

import parallel

SCHEMA = "a5-vb-pole-arcs-v1"
HERE = Path(__file__).resolve().parent
BASE_PATTERNS = tuple((a, a, a, e0) for e0 in span.E0_VALUES for a in (1, 2))
# (k, order of w above k, order of rho, order of sigma, flip)
POLE_PATTERNS = tuple(itertools.product((1, 2), (1, 2), (1, 2, 3), (1, 2, 3), (0, 1)))


def pole_values(field: limits.Field, pattern: tuple[int, ...], arc: int) -> dict[str, limits.Series]:
    """Phi on an arc with e = E s^k (1 + ...) and w of order k + extra; flip reverses omega (e -> 1/e)."""
    k, extra, a_rho, a_sigma, flip = pattern
    w, rho, sigma, zeta, e = (
        limits.monomials(field, *(span.coefficient(arc, i, j) for j in range(span.TERMS)), start=start)
        for i, start in enumerate((k + extra, a_rho, a_sigma, 1, k))
    )
    zeta = zeta + span.ZETA0
    half, quarter = Fraction(1, 2), Fraction(1, 4)
    m = w + 1
    m_inverse = m.inverse()
    below, above = w * (w + 2), m * m + 1
    q = below.shift(k) * e.shift(k).inverse()
    below_nu = q * (e + 1) * (e + 1) * quarter
    below_omega = q * (e * e - 1) * quarter * (-1 if flip else 1)
    t2 = (below_nu * 2 + below * zeta) * above.inverse()
    return {
        "t1": (-below * t2 + above * zeta + w * w) * m_inverse * half,
        "t2": t2,
        "t3": zeta,
        "t4": (m * rho + sigma) * half,
        "t5": (m * rho - sigma) * half,
        "t6": (m * sigma + rho) * half,
        "t7": (rho - m * sigma) * half,
        "t8": -(below_omega * m_inverse * limits.PRIMES[field.prime or 0]),
        "t9": -(w * w) * m_inverse * half * limits.INCIDENCES[span.SLUG][1],
    }


def one_arc(item: tuple[dict[str, Any], tuple[int, ...], int, bool]) -> dict[str, Any]:
    data, pattern, arc, pole = item
    if not pole:
        return span.one_arc((data, pattern, arc))  # type: ignore[arg-type]
    original = span.arc_values
    span.arc_values = pole_values
    try:
        record = span.one_arc((data, pattern, arc))  # type: ignore[arg-type]
    finally:
        span.arc_values = original
    field = limits.Field(data["prime"], span.ORDER)
    values = pole_values(field, pattern, arc)
    _, ideal_j, _ = limits.header(span.SLUG, data["prime"])
    with_root = dict(values, I=limits.Series((limits.PRIMES[data["prime"]],), field))
    record["j_nonzero"] = sum(limits.evaluate(text, with_root, field).valuation() < field.order - 2 for text in ideal_j)
    return record


def ranks(item: tuple[list[list[int]], list[list[int]], int]) -> tuple[int, int]:
    """Span rank of one pattern's Plucker vectors and of every vector through that pattern."""
    own, prefix, prime = item
    return span.rank(own, prime), span.rank(prefix, prime)


def build(item: tuple[int, dict[str, Any]]) -> dict[str, Any]:
    prime, data = item
    patterns = [(p, False) for p in BASE_PATTERNS] + [(p, True) for p in POLE_PATTERNS]
    items = [(data, pattern, arc, pole) for pattern, pole in patterns for arc in range(span.ARCS_PER_PATTERN)]
    results = parallel.ordered_map(one_arc, items, min_items=1)
    groups = [
        results[index * span.ARCS_PER_PATTERN : (index + 1) * span.ARCS_PER_PATTERN] for index in range(len(patterns))
    ]
    vectors = [[a["plucker"] for a in arcs if a["plucker"] is not None] for arcs in groups]
    prefixes = list(itertools.accumulate(vectors, lambda seen, new: seen + new))
    # Each pattern's own span and the span of every pattern through it are independent rank computations.
    spans = parallel.ordered_map(ranks, [(own, prefix, prime) for own, prefix in zip(vectors, prefixes, strict=True)])
    rows = []
    for index, ((pattern, pole), arcs) in enumerate(zip(patterns, groups, strict=True)):
        rows.append(
            {
                "pole": pole,
                "pattern": list(pattern),
                "arcs_with_limit": len(vectors[index]),
                "base_nullities": sorted({a["base_nullity"] for a in arcs}),
                "arc_nullities": sorted({a["arc_nullity"] for a in arcs}),
                "j_nonzero": sorted({a["j_nonzero"] for a in arcs}) if pole else None,
                "distinct_planes": len({a["plane_sha256"] for a in arcs if a["plucker"] is not None}),
                "span_rank": spans[index][0],
                "rank_before": spans[index - 1][1] if index else 0,
                "rank_after": spans[index][1],
            }
        )
    return {
        "schema": SCHEMA,
        "prime": prime,
        "order": span.ORDER,
        "arcs_per_pattern": span.ARCS_PER_PATTERN,
        "finite_e_rank": rows[len(BASE_PATTERNS) - 1]["rank_after"],
        "total_rank": spans[-1][1],
        "patterns": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "vb-pole-arcs-result.json")
    args = parser.parse_args()
    slices = parallel.ordered_map(
        limits.slice_of, [(span.SLUG, limits.Field(prime, span.ORDER)) for prime in span.PRIMES], min_items=1
    )
    cases = [build(item) for item in zip(span.PRIMES, slices, strict=True)]
    args.out.write_text(json.dumps({"schema": SCHEMA, "cases": cases}, indent=1) + "\n", encoding="utf-8")
    for case in cases:
        print("prime", case["prime"], "finite_e_rank", case["finite_e_rank"], "total_rank", case["total_rank"])
        for row in case["patterns"]:
            print(" ", row)


if __name__ == "__main__":
    main()
