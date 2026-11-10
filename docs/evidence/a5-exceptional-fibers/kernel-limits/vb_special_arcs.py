"""Limits of ker L_a along arcs of the closure of E8-bar through the VB point that carries the degree-3 component.

Phi(w, rho, sigma, e, zeta) of ../arcs and Phi(w, rho, sigma, k) of ../arcs-vb describe the same slice: the conic
coordinate of the second is k / (1 + k^2) = i omega with omega = (e^2 - 1) / (4 e). With e = (1 + i kappa) /
(1 - i kappa), i omega = -kappa / (1 + kappa^2), so the VB coordinate is k = -kappa: the VB point k0 = -9 is
kappa0 = 9 here. The degree-3 component V(P1) of the fiber of E8-bar -> VB is reached only by
arcs through k0 = -9 with w of order 2 against order 1 for rho and sigma (../arcs-vb). vb_limit_span.py and
vb_pole_arcs.py sample other points of the line w = rho = sigma = 0 and reach Plucker span 22.

If the Plucker vector of the limiting plane is quadratic in the fiber coordinates y, the span over the degree-4
component has rank HF(k[y]/P2, 2) = 22, over the degree-3 component 18, and over the whole fiber 34 (A5-020). The
record holds the span of the finite-e family of vb_pole_arcs.py, then the rank after each pattern through
e0 = (1 + i k0) / (1 - i k0) joins, for k0 = 9 (kappa0 = 9, the special VB point k = -9), its mirror
k0 = -9 and the neighbor k0 = 8: a rank of 34 after the special patterns, with no growth from the mirror and the
neighbor, shows limits over the degree-3 component and a span equal to the quadratic prediction.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/vb_special_arcs.py
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import plucker_limits as limits
import vb_limit_span as span
import vb_pole_arcs as pole

import parallel

SCHEMA = "a5-vb-special-arcs-v1"
HERE = Path(__file__).resolve().parent
ARCS = 96
# Leading orders of (w, rho, sigma); (2, 1, 1) is the weight of the certified arc family of ../arcs-vb.
ORDERS = ((2, 1, 1), (3, 1, 1), (2, 2, 1), (1, 1, 1), (2, 2, 2))
# Controls first, so growth at the special point is measured against everything the other points give.
K0_VALUES = (-9, 8, 9)
QUADRATIC_PREDICTION = {"degree_4_component": 22, "degree_3_component": 18, "fiber": 34}


def e_of(k0: int, prime: int) -> int:
    i = limits.PRIMES[prime]
    return (1 + i * k0) * pow(1 - i * k0, -1, prime) % prime


def build(item: tuple[int, dict[str, Any]]) -> dict[str, Any]:
    prime, data = item
    base = [(pattern, None, span.ARCS_PER_PATTERN) for pattern in pole.BASE_PATTERNS]
    through = [((*orders, e_of(k0, prime)), k0, ARCS) for k0 in K0_VALUES for orders in ORDERS]
    patterns = base + through
    items = [(data, pattern, arc) for pattern, _, count in patterns for arc in range(count)]
    results = parallel.ordered_map(span.one_arc, items, min_items=1)
    bounds = list(itertools.accumulate((count for _, _, count in patterns), initial=0))
    groups = [results[bounds[i] : bounds[i + 1]] for i in range(len(patterns))]
    vectors = [[a["plucker"] for a in arcs if a["plucker"] is not None] for arcs in groups]
    prefixes = list(itertools.accumulate(vectors, lambda seen, new: seen + new))
    spans = parallel.ordered_map(
        pole.ranks, [(own, prefix, prime) for own, prefix in zip(vectors, prefixes, strict=True)]
    )
    rows = []
    for index, ((pattern, k0, count), arcs) in enumerate(zip(patterns, groups, strict=True)):
        rows.append(
            {
                "k0": k0,
                "leading_orders_w_rho_sigma": list(pattern[:3]),
                "e0": pattern[3],
                "arcs": count,
                "arcs_with_limit": len(vectors[index]),
                "base_nullities": sorted({a["base_nullity"] for a in arcs}),
                "arc_nullities": sorted({a["arc_nullity"] for a in arcs}),
                "pivot_valuation_sums": sorted({a["pivot_valuation_sum"] for a in arcs}),
                "distinct_planes": len({a["plane_sha256"] for a in arcs if a["plucker"] is not None}),
                "span_rank": spans[index][0],
                "rank_before": spans[index - 1][1] if index else 0,
                "rank_after": spans[index][1],
            }
        )
    last_control = len(base) + len(ORDERS) * (len(K0_VALUES) - 1) - 1
    special = rows[last_control + 1 :]
    special_vectors = [v for group in vectors[last_control + 1 :] for v in group]
    return {
        "schema": SCHEMA,
        "prime": prime,
        "order": span.ORDER,
        "quadratic_prediction": QUADRATIC_PREDICTION,
        "finite_e_rank": rows[len(base) - 1]["rank_after"],
        "rank_after_controls": rows[last_control]["rank_after"],
        "special_span_rank": span.rank(special_vectors, prime),
        "total_rank": spans[-1][1],
        "special_patterns_with_limit": sum(row["arcs_with_limit"] for row in special),
        "patterns": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "vb-special-arcs-result.json")
    args = parser.parse_args()
    slices = parallel.ordered_map(
        limits.slice_of, [(span.SLUG, limits.Field(prime, span.ORDER)) for prime in span.PRIMES], min_items=1
    )
    cases = [build(item) for item in zip(span.PRIMES, slices, strict=True)]
    verdict = all(
        case["finite_e_rank"] == case["rank_after_controls"] == QUADRATIC_PREDICTION["degree_4_component"]
        and case["special_span_rank"] == QUADRATIC_PREDICTION["degree_3_component"]
        and case["total_rank"] == QUADRATIC_PREDICTION["fiber"]
        for case in cases
    )
    record = {"schema": SCHEMA, "verdict": "matches_quadratic_prediction" if verdict else "differs", "cases": cases}
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for case in cases:
        print("prime", case["prime"], {k: v for k, v in case.items() if k not in ("patterns", "schema")})
        for row in case["patterns"]:
            print(" ", row)
    print("verdict", record["verdict"])


if __name__ == "__main__":
    main()
