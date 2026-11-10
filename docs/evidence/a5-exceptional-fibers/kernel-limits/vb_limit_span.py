"""Limits of ker L_a along arcs of the closure of E8-bar through a point of the orbit VB (ledger A5-016, A5-276).

The parametrization Phi(w, rho, sigma, e, zeta) of the slice of E8-bar -> N- (../arcs) meets the orbit VB on the
curve w = rho = sigma = 0, zeta nonzero, where e drops out of Phi. An arc w = sum W_k s^k, rho = sum R_k s^k,
sigma = sum S_k s^k, zeta = Z0 + sum Z_k s^k, e = E0 + sum E_k s^k therefore runs in the closure of E8-bar through
the VB point b = Phi(0, 0, 0, E0, Z0), with free coefficients at every order, and plucker_limits computes the limit
of the 8-dimensional kernel inside the 12-dimensional kernel of L_b. Each limiting plane is written in a fixed basis
of ker L_b and sent to the 495 maximal minors of its annihilator, its Plucker vector. A pattern fixes the leading
order of w, rho and sigma and the value E0; the record holds, per pattern, the rank of the span of its Plucker
vectors, the rank of the span of all patterns before it joined with it, and the rank of the whole sample.

V(K2) of E8-bar -> VB spans P^9 and its two components span a P^6 and a P^5 meeting in a P^2 (A5-020). If Plucker
vectors are linear in the fiber coordinates y, a pattern dense in one component has span rank 7 or 6 and the whole
fiber has rank 10; if they are quadratic in y the ranks are HF(2) = 22, 18 and 34.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/vb_limit_span.py
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import plucker_limits as limits
from flint import nmod_mat

import parallel

SCHEMA = "a5-vb-limit-span-v1"
HERE = Path(__file__).resolve().parent
ORDER = 24
PRIMES = tuple(limits.PRIMES)
ZETA0 = 1
E0_VALUES = (2, -1, 1, 3, 5, 7)
LEADING_ORDERS = tuple(itertools.product((1, 2, 3), repeat=3))
ARCS_PER_PATTERN = 24
TERMS = 3
KERNEL_AT_VB = 12


def coefficient(arc: int, series: int, term: int) -> int:
    """A fixed nonzero integer in 1..101 for each arc, series and term."""
    return (arc * 31 + series * 17 + term * 5 + 3) * 7919 % 101 + 1


def arc_values(field: limits.Field, pattern: tuple[int, int, int, int], arc: int) -> dict[str, limits.Series]:
    """Phi of ../arcs on E8-bar -> N- with the pattern's leading orders and E0."""
    a_w, a_rho, a_sigma, e0 = pattern
    w, rho, sigma, zeta = (
        limits.monomials(field, *(coefficient(arc, i, k) for k in range(TERMS)), start=start)
        for i, start in enumerate((a_w, a_rho, a_sigma, 1))
    )
    zeta = zeta + ZETA0
    e = limits.Series((e0, *(coefficient(arc, 4, k) for k in range(TERMS))), field)
    half = Fraction(1, 2)
    m = w + 1
    m_inverse = m.inverse()
    below, above = m * m - 1, m * m + 1
    e_inverse = (e * 4).inverse()
    nu = (e + 1) * (e + 1) * e_inverse
    omega = (e * e - 1) * e_inverse
    t2 = (below * nu * 2 + below * zeta) * above.inverse()
    return {
        "t1": (-below * t2 + above * zeta + w * w) * m_inverse * half,
        "t2": t2,
        "t3": zeta,
        "t4": (m * rho + sigma) * half,
        "t5": (m * rho - sigma) * half,
        "t6": (m * sigma + rho) * half,
        "t7": (rho - m * sigma) * half,
        "t8": -(below * omega * m_inverse * limits.PRIMES[field.prime or 0]),
        "t9": -(w * w) * m_inverse * half,
    }


def plucker(plane: list[limits.Vector], basis: list[limits.Vector], prime: int) -> list[int]:
    """Maximal minors of the annihilator of the plane, in coordinates on the basis of ker L_b."""
    pivots = [next(i for i, v in enumerate(row) if v) for row in basis]
    coordinates = nmod_mat([[int(row[c]) for c in pivots] for row in plane], prime)
    annihilator = coordinates.nullspace()[0].transpose()
    rows = [[int(annihilator[i, j]) for j in range(len(basis))] for i in range(len(basis) - len(plane))]
    return [
        int(nmod_mat([[row[c] for c in columns] for row in rows], prime).det())
        for columns in itertools.combinations(range(len(basis)), len(rows))
    ]


def one_arc(item: tuple[dict[str, Any], tuple[int, int, int, int], int]) -> dict[str, Any]:
    data, pattern, arc = item
    field = limits.Field(data["prime"], ORDER)
    values = arc_values(field, pattern, arc)
    base = [Fraction(v) for v in data["boundary_point"]]
    split = [
        values[data["slice_names"][data["slice_columns"].index(k)]] + base[k]
        if k in data["slice_columns"]
        else limits.Series((base[k],), field)
        for k in range(len(base))
    ]
    matrix = limits.left_matrix(limits.operand(split, field))
    base_matrix = [[limits.Series((entry.c[0],), field) for entry in row] for row in matrix]
    base_kernel = limits.rref(limits.saturated_kernel(base_matrix, field)[0], field)
    kernel, valuations = limits.saturated_kernel(matrix, field)
    plane = limits.rref(kernel, field)
    good = (
        len(base_kernel) == KERNEL_AT_VB
        and len(plane) == limits.SOURCE_NULLITY
        and len(limits.rref([*base_kernel, *plane], field)) == KERNEL_AT_VB
    )
    return {
        "pattern": list(pattern),
        "arc": arc,
        "base_nullity": len(base_kernel),
        "arc_nullity": len(kernel),
        "pivot_valuation_sum": sum(valuations),
        "plane_sha256": hashlib.sha256(json.dumps(limits.plane_text(plane)).encode()).hexdigest(),
        "plucker": plucker(plane, base_kernel, data["prime"]) if good else None,
    }


def rank(vectors: list[list[int]], prime: int) -> int:
    return int(nmod_mat(vectors, prime).rank()) if vectors else 0


def build(prime: int) -> dict[str, Any]:
    data = limits.slice_data("e8-nm", limits.Field(prime, ORDER))
    patterns = [(*orders, e0) for e0 in E0_VALUES for orders in LEADING_ORDERS]
    items = [(data, pattern, arc) for pattern in patterns for arc in range(ARCS_PER_PATTERN)]
    results = parallel.ordered_map(one_arc, items, min_items=1)
    seen: list[list[int]] = []
    rows = []
    for index, pattern in enumerate(patterns):
        arcs = results[index * ARCS_PER_PATTERN : (index + 1) * ARCS_PER_PATTERN]
        vectors = [a["plucker"] for a in arcs if a["plucker"] is not None]
        before = rank(seen, prime)
        seen.extend(vectors)
        rows.append(
            {
                "leading_orders_w_rho_sigma": list(pattern[:3]),
                "e0": pattern[3],
                "arcs_with_limit": len(vectors),
                "arc_nullities": sorted({a["arc_nullity"] for a in arcs}),
                "largest_pivot_valuation_sum": max(a["pivot_valuation_sum"] for a in arcs),
                "distinct_planes": len({a["plane_sha256"] for a in arcs if a["plucker"] is not None}),
                "span_rank": rank(vectors, prime),
                "rank_before": before,
                "rank_after": rank(seen, prime),
            }
        )
    return {
        "schema": SCHEMA,
        "prime": prime,
        "order": ORDER,
        "base_parameters": {"w": 0, "rho": 0, "sigma": 0, "zeta": ZETA0, "e0": list(E0_VALUES)},
        "arcs_per_pattern": ARCS_PER_PATTERN,
        "total_rank": rank(seen, prime),
        "patterns": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "vb-limit-span-result.json")
    args = parser.parse_args()
    cases = [build(prime) for prime in PRIMES]
    record = {"schema": SCHEMA, "cases": cases}
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for case in cases:
        print("prime", case["prime"], "total_rank", case["total_rank"])
        for row in case["patterns"]:
            print(" ", row)


if __name__ == "__main__":
    main()
