"""External replay of the star-lattice symmetry groups through SageMath's nauty and GAP interfaces.

For n = 2, 4, 8, 16 it computes the full automorphism group of the lattice graph S_n and its SmallGroup id. For
n = 4 through 128 it computes the signed-permutation centralizer of the arc matrix W_n as the automorphism group of
a labeled digraph on the 2n signed units: arcs (a, s) -> (a XOR b, s cd_sign(n, a, b)) labeled "w", and the pairs
(a, +) <-> (a, -) labeled "neg". An automorphism preserving the "neg" pairing commutes with negation, so it is a
signed permutation, and preserving the "w" arcs makes it commute with W_n. The output records each order, the orbit
sizes on signed units, the SmallGroup id where GAP's library holds the order, and whether the group is isomorphic to
the one of dimension 16.

Usage, from the repository root, with SAGE_PYTHON an interpreter that imports sage.all:

    "$SAGE_PYTHON" docs/evidence/cd-star-lattice/external/nauty_replay.py \
        > docs/evidence/cd-star-lattice/external/nauty_replay.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import sage.all  # noqa: E402
import sage.version  # noqa: E402
from cd_star_lattice import ball, cd_boundary, unit_edges  # noqa: E402
from sage.all import DiGraph, Graph, PermutationGroup  # noqa: E402

from cd_core import cd_sign  # noqa: E402

GROUP_ID_ORDERS = (4, 24, 336, 672)


def signed_centralizer(n: int) -> PermutationGroup:
    def unit(a: int, s: int) -> int:
        return 2 * a + (0 if s == 1 else 1)

    digraph = DiGraph(2 * n)
    for a in range(n):
        digraph.add_edge(unit(a, 1), unit(a, -1), "neg")
        digraph.add_edge(unit(a, -1), unit(a, 1), "neg")
        for b in range(1, n):
            for s in (1, -1):
                digraph.add_edge(unit(a, s), unit(a ^ b, s * cd_sign(n, a, b)), "w")
    return digraph.automorphism_group(edge_labels=True)


def describe(group: PermutationGroup) -> str:
    order = int(group.order())
    identity = list(group.group_id()) if order in GROUP_ID_ORDERS else "-"
    return f"order {order} smallgroup {identity}"


def main() -> int:
    print(f"sage {sage.version.version} gap {sage.all.libgap.eval('GAPInfo.Version')}")
    for n in (2, 4, 8, 16):
        points = sorted(ball(n) | cd_boundary(n))
        index = {p: i for i, p in enumerate(points)}
        graph = Graph([list(range(len(points))), [(index[p], index[q]) for p, q in unit_edges(set(points))]])
        group = graph.automorphism_group()
        print(f"graph S_{n}: vertices {len(points)} {describe(group)} orbits {sorted(len(o) for o in group.orbits())}")
    sedenion = signed_centralizer(16)
    for n in (4, 8, 16, 32, 64, 128):
        group = signed_centralizer(n)
        same = int(group.order()) == 672 and group.is_isomorphic(sedenion)
        orbits = sorted(len(o) for o in group.orbits())
        print(f"signed centralizer W_{n}: {describe(group)} orbits {orbits} isomorphic_to_dimension_16 {same}")
    gap_group = sedenion.gap()
    print(
        "dimension 16: sylow-2",
        gap_group.SylowSubgroup(2).StructureDescription(),
        "center order",
        gap_group.Centre().Size(),
        "involutions",
        sum(1 for g in gap_group.Elements() if g.Order() == 2),
        "quotient by center",
        gap_group.FactorGroup(gap_group.Centre()).IdGroup(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
