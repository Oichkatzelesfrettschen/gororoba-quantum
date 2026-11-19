"""Probe: kernel-plane limits along E8-bar arcs through the VB point with e0 = (1 + i k0)/(1 - i k0), k0 = -9, +9, -8."""
import sys, json
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "docs/evidence/a5-exceptional-fibers/kernel-limits"))
sys.path.insert(0, str(root / "gororoba_quantum"))
import plucker_limits as limits
import vb_limit_span as span
import parallel

def main():
    prime = int(sys.argv[2])
    i = limits.PRIMES[prime]
    def e_of(k):
        return (1 + i * k) * pow(1 - i * k, -1, prime) % prime
    data = limits.slice_data(span.SLUG, limits.Field(prime, span.ORDER))
    base = [(a, a, a, e0) for e0 in span.E0_VALUES for a in (1, 2)]
    special = [(orders, k) for k in (-9, 9, -8) for orders in ((2, 1, 1), (1, 1, 1), (2, 2, 1), (3, 1, 1), (2, 2, 2))]
    patterns = base + [(*orders, e_of(k)) for orders, k in special]
    items = [(data, p, arc) for p in patterns for arc in range(span.ARCS_PER_PATTERN)]
    results = parallel.ordered_map(span.one_arc, items, min_items=1)
    n = span.ARCS_PER_PATTERN
    seen = []
    for idx, p in enumerate(patterns):
        arcs = results[idx * n:(idx + 1) * n]
        vec = [a["plucker"] for a in arcs if a["plucker"] is not None]
        before = span.rank(seen, prime)
        seen.extend(vec)
        label = ("base", p) if idx < len(base) else ("k0", special[idx - len(base)])
        print(label, "limits", len(vec), "nullity", sorted({a["arc_nullity"] for a in arcs}), "base", sorted({a["base_nullity"] for a in arcs}),
              "valsum", sorted({a["pivot_valuation_sum"] for a in arcs}), "own", span.rank(vec, prime), "before", before, "after", span.rank(seen, prime), flush=True)

if __name__ == "__main__":
    main()
