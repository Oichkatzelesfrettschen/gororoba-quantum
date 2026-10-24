"""External replay placing the Hadamard matrix I + W_n among the known Hadamard classes, through SageMath's nauty.

A pair (P, Q) of signed permutation matrices is a Hadamard automorphism of H when P H Q^T = H. Such pairs are the
automorphisms of the graph on vertices (row i, sign s) and (column j, sign t), with (i, s) joined to (j, s H[i][j]),
that keep rows and columns apart; two Hadamard matrices are equivalent exactly when their graphs are isomorphic
under that partition. Every order printed here counts pairs, (-I, -I) included. A boundary symmetry P commutes with
W_n, so (P, P) is such a pair and G_n embeds in Aut(I + W_n).

mckay_had16.txt is the list of the five equivalence classes of order 16 published by Brendan McKay at
https://users.cecs.anu.edu.au/~bdm/data/hadamard/had16.txt: one matrix per line, one hexadecimal word per row, a 0
bit standing for -1. The replay names classes by line number of that file.

Usage, from the repository root, with SAGE_PYTHON an interpreter that imports sage.all:

    "$SAGE_PYTHON" docs/evidence/cd-star-lattice/external/hadamard_replay.py \
        > docs/evidence/cd-star-lattice/external/hadamard_replay.txt
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import sage.all  # noqa: E402
import sage.version  # noqa: E402
from cd_star_lattice import arc_matrix  # noqa: E402
from sage.all import Graph  # noqa: E402

from cd_core import cd_sign  # noqa: E402

MCKAY = Path(__file__).with_name("mckay_had16.txt")
GROUP_ORDERS = {4: 24, 8: 336, 16: 672, 32: 672, 64: 672}

Matrix = list[list[int]]


def load(path: Path) -> list[Matrix]:
    matrices = []
    for line in path.read_text().splitlines():
        words = line.split()
        n = len(words)
        matrices.append([[1 if (int(word, 16) >> (n - 1 - j)) & 1 else -1 for j in range(n)] for word in words])
    return matrices


def is_hadamard(h: Matrix) -> bool:
    n = len(h)
    return all(sum(h[i][k] * h[j][k] for k in range(n)) == (n if i == j else 0) for i in range(n) for j in range(n))


def hadamard_graph(h: Matrix) -> tuple[Graph, list[list[tuple[str, int, int]]]]:
    n = len(h)
    graph = Graph()
    for i in range(n):
        for j in range(n):
            for s in (1, -1):
                graph.add_edge(("r", i, s), ("c", j, s * h[i][j]))
    partition = [[v for v in graph if v[0] == "r"], [v for v in graph if v[0] == "c"]]
    return graph, partition


def canonical(h: Matrix) -> Graph:
    graph, partition = hadamard_graph(h)
    return graph.canonical_label(partition=partition).copy(immutable=True)


def automorphism_pairs(h: Matrix) -> int:
    graph, partition = hadamard_graph(h)
    return int(graph.automorphism_group(partition=partition).order())


def plus_identity(w: Matrix) -> Matrix:
    return [[value + (1 if i == j else 0) for j, value in enumerate(row)] for i, row in enumerate(w)]


def transpose(h: Matrix) -> Matrix:
    return [list(column) for column in zip(*h, strict=True)]


def main() -> int:
    print(f"sage {sage.version.version}")
    print(f"mckay_had16.txt sha256 {hashlib.sha256(MCKAY.read_bytes()).hexdigest()}")
    classes = load(MCKAY)
    labels = [canonical(h) for h in classes]

    def line_of(h: Matrix) -> list[int]:
        label = canonical(h)
        return [k + 1 for k, other in enumerate(labels) if other == label]

    for k, h in enumerate(classes):
        transposed = line_of(transpose(h))
        print(f"line {k + 1}: hadamard {is_hadamard(h)}, |Aut| {automorphism_pairs(h)}, transpose in line {transposed}")
    h16 = plus_identity(arc_matrix(16))
    table = [[cd_sign(16, a, b) for b in range(16)] for a in range(16)]
    print(f"I + W_16: line {line_of(h16)}; transpose: line {line_of(transpose(h16))}")
    print(f"sedenion sign table: line {line_of(table)}; transpose: line {line_of(transpose(table))}")
    for n, order in GROUP_ORDERS.items():
        h = plus_identity(arc_matrix(n))
        pairs = automorphism_pairs(h)
        print(f"n = {n}: I + W_n hadamard {is_hadamard(h)}, |Aut| {pairs}, |G_n| {order}, index {pairs // order}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
