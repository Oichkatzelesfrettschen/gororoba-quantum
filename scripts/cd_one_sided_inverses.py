"""Left and right annihilators agree in every Cayley-Dickson algebra of cd_core, so a b = 1 forces b a = 1.

The trace form is <x, y> = sum_i x_i y_i and conj negates every imaginary
coordinate. Three identities, each multilinear in its arguments, are checked
on every basis tuple of the dimensions in IDENTITY_DIMENSIONS, which proves
them on every element of those algebras:

    (L1) a conj(a) = conj(a) a = <a, a> 1            (basis pairs, polarized)
    (L2) <a x, y> = <x, conj(a) y>                   (basis triples)
    (L2') <x a, y> = <x, y conj(a)>                  (basis triples)

The theorem of [the note](../docs/notes/topics/cd-one-sided-inverses.md)
follows: an element with a nonzero left or right annihilator is pure, its
annihilated elements are pure, conjugation carries ker L_a onto ker R_a, and
b = conj(a) / <a, a> + z with z in ker L_a is the only solution of a b = 1,
so b a = 1. The record checks the kernel equality and the inverse identity
on every element of three deterministic families, at the dimensions in
KERNEL_DIMENSIONS:

- every signed two-blade e_i + s e_j, 1 <= i < j < D, s = +-1;
- every three-unit sum e_i + e_j + e_k with 1 <= i < j < k < min(D, 16);
- every doubly pure grid element u + v with u in span(e_1 .. e_(D/2-1)) and v
  in span(e_(D/2+1) .. e_(D-1)), integer coordinates in {-1, 0, 1}, at most
  DOUBLY_PURE_SUPPORT[D] nonzero coordinates per half, the first nonzero
  coordinate of u equal to 1 and <u, u> = <v, v>.

Each element is an independent pool item mapped through parallel.ordered_map.
A worker builds L_a and R_a from cd_core.cd_sign, takes both kernels by exact
Gauss-Jordan elimination over Fraction, and requires: the two kernels span the
same subspace; every kernel vector and, when the kernel is nonzero, a itself
are pure; and for every kernel basis vector z the element b = conj(a)/<a, a> + z
satisfies a b = b a = 1 through cd_core.cd_multiply_exact. The record keeps
integer counts only (elements per family, elements with a kernel, the kernel
dimension histogram), so pooled and serial runs write the same bytes, and any
violated identity raises before a record is written.

Usage: "$PYTHON" scripts/cd_one_sided_inverses.py (--write PATH | --check PATH | --self-test)
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign  # noqa: E402

SCHEMA = "cd-one-sided-inverses-v1"
IDENTITY_DIMENSIONS = (2, 4, 8, 16, 32, 64, 128)
KERNEL_DIMENSIONS = (16, 32)
THREE_UNIT_LIMIT = 16
DOUBLY_PURE_SUPPORT = {16: 2, 32: 1}
SIGNS = (1, -1)


class ContractError(ValueError):
    """An identity the theorem rests on fails on a concrete element."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


@functools.cache
def sign_table(dim: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(cd_sign(dim, p, q) for q in range(dim)) for p in range(dim))


def conj_sign(index: int) -> int:
    return 1 if index == 0 else -1


def identity_record(dim: int) -> dict[str, Any]:
    """L1, L2 and L2' on every basis pair and triple; each is multilinear, so the basis checks decide them."""
    s = sign_table(dim)
    for i in range(dim):
        for j in range(dim):
            # (L1) e_i conj(e_j) + e_j conj(e_i) = 2 [i = j] e_0, and the same with conj on the left.
            lhs = conj_sign(j) * s[i][j] + conj_sign(i) * s[j][i]
            lhs_left = conj_sign(i) * s[i][j] + conj_sign(j) * s[j][i]
            require(lhs == lhs_left == (2 if i == j else 0), f"D={dim}: L1 fails on the basis pair ({i}, {j})")
            # (L2) <e_i e_j, e_k> = <e_j, conj(e_i) e_k> at the only k = i XOR j carrying either side.
            k = i ^ j
            require(s[i][j] == conj_sign(i) * s[i][k], f"D={dim}: L2 fails on the basis triple ({i}, {j}, {k})")
            # (L2') <e_j e_i, e_k> = <e_j, e_k conj(e_i)>.
            require(s[j][i] == conj_sign(i) * s[k][i], f"D={dim}: L2' fails on the basis triple ({j}, {i}, {k})")
    return {"dimension": dim, "basis_pairs": dim * dim, "identities": ["L1", "L2", "L2'"]}


def left_matrix(dim: int, a: tuple[int, ...]) -> list[list[Fraction]]:
    """Matrix of x -> a x: a x = sum_(j, i) a_j x_i sigma(j, i) e_(j XOR i)."""
    s = sign_table(dim)
    m = [[Fraction(0)] * dim for _ in range(dim)]
    for j, aj in enumerate(a):
        if aj:
            for i in range(dim):
                m[j ^ i][i] += aj * s[j][i]
    return m


def right_matrix(dim: int, a: tuple[int, ...]) -> list[list[Fraction]]:
    """Matrix of x -> x a: x a = sum_(i, j) x_i a_j sigma(i, j) e_(i XOR j)."""
    s = sign_table(dim)
    m = [[Fraction(0)] * dim for _ in range(dim)]
    for j, aj in enumerate(a):
        if aj:
            for i in range(dim):
                m[i ^ j][i] += aj * s[i][j]
    return m


def reduce(mat: list[list[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    """Reduced row echelon form and pivot columns by exact Gauss-Jordan elimination."""
    m = [row[:] for row in mat]
    rows, cols = len(m), len(m[0])
    pivots: list[int] = []
    r = 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inv = 1 / m[r][c]
        m[r] = [x * inv for x in m[r]]
        for i in range(rows):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r], strict=True)]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return m, pivots


def kernel(mat: list[list[Fraction]]) -> list[list[Fraction]]:
    m, pivots = reduce(mat)
    cols = len(mat[0])
    basis = []
    for free in (c for c in range(cols) if c not in pivots):
        v = [Fraction(0)] * cols
        v[free] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -m[i][free]
        basis.append(v)
    return basis


def rank(vectors: list[list[Fraction]]) -> int:
    return len(reduce(vectors)[1]) if vectors else 0


def same_span(left: list[list[Fraction]], right: list[list[Fraction]]) -> bool:
    return len(left) == len(right) and rank(left + right) == len(left)


def conj(a: list[Fraction]) -> list[Fraction]:
    return [a[0]] + [-x for x in a[1:]]


def element_check(item: tuple[int, tuple[int, ...]]) -> dict[str, Any]:
    """Pool worker: kernels of L_a and R_a, their equality, purity, and the two-sided inverse law."""
    dim, a = item
    left = kernel(left_matrix(dim, a))
    right = kernel(right_matrix(dim, a))
    require(same_span(left, right), f"D={dim}: ker L_a and ker R_a differ for a = {a}")
    if left:
        require(a[0] == 0, f"D={dim}: a = {a} has a kernel and a nonzero real part")
        require(all(z[0] == 0 for z in left + right), f"D={dim}: a kernel vector of a = {a} has a real part")
        norm = Fraction(sum(x * x for x in a))
        inverse = [x / norm for x in conj([Fraction(x) for x in a])]
        one = tuple([Fraction(1)] + [Fraction(0)] * (dim - 1))
        for z in left:
            b = [p + q for p, q in zip(inverse, z, strict=True)]
            require(cd_multiply_exact(dim, a, b) == one, f"D={dim}: a b != 1 for a = {a}")
            require(cd_multiply_exact(dim, b, a) == one, f"D={dim}: a b = 1 but b a != 1 for a = {a}")
    return {"kernel_dimension": len(left)}


def two_blades(dim: int) -> list[tuple[int, ...]]:
    out = []
    for i, j in itertools.combinations(range(1, dim), 2):
        for s in SIGNS:
            a = [0] * dim
            a[i], a[j] = 1, s
            out.append(tuple(a))
    return out


def three_units(dim: int) -> list[tuple[int, ...]]:
    out = []
    for i, j, k in itertools.combinations(range(1, min(dim, THREE_UNIT_LIMIT)), 3):
        a = [0] * dim
        a[i] = a[j] = a[k] = 1
        out.append(tuple(a))
    return out


def pure_grid(half: int, support: int, lead_positive: bool) -> list[tuple[int, ...]]:
    """Pure elements of the half algebra with at most `support` coordinates in {-1, 1}."""
    out = []
    for size in range(1, support + 1):
        for indices in itertools.combinations(range(1, half), size):
            for signs in itertools.product(SIGNS, repeat=size):
                if lead_positive and signs[0] != 1:
                    continue
                u = [0] * half
                for index, sign in zip(indices, signs, strict=True):
                    u[index] = sign
                out.append(tuple(u))
    return out


def doubly_pure(dim: int) -> list[tuple[int, ...]]:
    half = dim // 2
    support = DOUBLY_PURE_SUPPORT[dim]
    out = []
    for u in pure_grid(half, support, lead_positive=True):
        for v in pure_grid(half, support, lead_positive=False):
            if sum(x * x for x in u) == sum(x * x for x in v):
                out.append(u + (0,) + v[1:])
    return out


FAMILIES = (("two_blade", two_blades), ("three_unit", three_units), ("doubly_pure", doubly_pure))


def family_record(dim: int, name: str, elements: list[tuple[int, ...]]) -> dict[str, Any]:
    results = parallel.ordered_map(element_check, [(dim, a) for a in elements])
    histogram = Counter(r["kernel_dimension"] for r in results if r["kernel_dimension"])
    return {
        "family": name,
        "elements": len(elements),
        "with_kernel": sum(histogram.values()),
        "kernel_dimension_histogram": {str(k): v for k, v in sorted(histogram.items())},
    }


def record() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "identities": [identity_record(dim) for dim in IDENTITY_DIMENSIONS],
        "kernels": [
            {
                "dimension": dim,
                "families": [family_record(dim, name, build(dim)) for name, build in FAMILIES],
                "annihilators_agree": True,
                "one_sided_inverses": 0,
            }
            for dim in KERNEL_DIMENSIONS
        ],
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def self_test() -> None:
    """A conjugation fixing e_1 breaks L2 at D = 4; e_1 - e_10 and e_1 + e_10 have distinct kernels of one dimension."""
    s = sign_table(4)
    fixed = [1, 1, -1, -1]
    if all(s[i][j] == fixed[i] * s[i][i ^ j] for i in range(4) for j in range(4)):
        raise ContractError("a conjugation fixing e_1 passes L2 at D = 4")
    a = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    partner = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0)
    left, other = kernel(left_matrix(16, a)), kernel(right_matrix(16, partner))
    if len(left) != len(other) or same_span(left, other):
        raise ContractError("e_1 + e_10 and e_1 - e_10 share a kernel, or their kernel dimensions differ")
    if element_check((16, a))["kernel_dimension"] != 4:
        raise ContractError("e_1 + e_10 has annihilator dimension 4")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test passed")
        return 0
    text = render(record())
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"wrote {args.write}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print(f"{args.check} departs from the recomputed record")
        return 1
    print(f"{args.check}: record reproduces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
