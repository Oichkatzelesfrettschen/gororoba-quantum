"""Identify Skiouris's sedenion kernel bundle K with xi_R = G2 x_SU(2) H^perp under the cd_core convention.

Usage: skiouris_intertwiner.py --check

Skiouris (Zenodo record 22016333, equation (25) and Theorem 6.3) takes p0 = e1 + e2 l = e1 + e10 and the kernel
basis v = (e7 + e12, -e6 + e13, e5 + e14, -e4 + e15) of L_p0. The stabilizer in Der(O) of (e1, e2) acts on the
sedenions as diag(D, D). The check raises unless L_p0 has nullity 4, v spans ker L_p0, the stabilizer is
three-dimensional, and each stabilizer derivation acts on v by the same 4 x 4 matrix it induces on
H^perp = span(e4, e5, e6, e7); then e4, e5, e6, e7 -> v1, v2, v3, v4 is an SU(2)-equivariant isomorphism and
K = G2 x_SU(2) K0 equals xi_R.
"""

import sys
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "gororoba_quantum"))
from cd_core import cd_multiply_exact, left_mult_matrix_exact  # noqa: E402


def unit(i: int, dim: int) -> list[int]:
    v = [0] * dim
    v[i] = 1
    return v


TABLE = {(i, j): cd_multiply_exact(8, unit(i, 8), unit(j, 8)) for i in range(8) for j in range(8)}


def octonion_product(a: list, b: list) -> list:
    """Bilinear expansion over the exact cd_core basis table, so symbolic coordinates are allowed."""
    out: list = [0] * 8
    for i in range(8):
        for j in range(8):
            if a[i] != 0 and b[j] != 0:
                for k, c in enumerate(TABLE[(i, j)]):
                    out[k] += a[i] * b[j] * c
    return out


def stabilizer_derivations() -> list[sp.Matrix]:
    """Basis of {D in Der(O) : D e1 = D e2 = 0}, solved exactly from the cd_core octonion table."""
    d = sp.Matrix(8, 8, lambda i, j: sp.Symbol(f"d{i}_{j}"))
    eqs: list = []
    for i in range(8):
        for j in range(8):
            lhs = d * sp.Matrix(octonion_product(unit(i, 8), unit(j, 8)))
            rhs = sp.Matrix(octonion_product(list(d[:, i]), unit(j, 8))) + sp.Matrix(
                octonion_product(unit(i, 8), list(d[:, j]))
            )
            eqs += list(lhs - rhs)
    eqs += list(d[:, 1]) + list(d[:, 2])
    (sol,) = sp.linsolve(eqs, list(d))
    free = sorted(set().union(*[x.free_symbols for x in sol]), key=str)
    return [sp.Matrix(8, 8, [x.subs({f: int(f == g) for f in free}) for x in sol]) for g in free]


def main() -> int:
    if sys.argv[1:] != ["--check"]:
        print(__doc__, file=sys.stderr)
        return 2
    p0 = [a + b for a, b in zip(unit(1, 16), unit(10, 16), strict=True)]
    lp = sp.Matrix(left_mult_matrix_exact(16, p0))
    if 16 - lp.rank() != 4:
        raise SystemExit(f"nullity of L_p0 is {16 - lp.rank()}, expected 4")
    cols = [(7, 12, 1), (13, 6, -1), (5, 14, 1), (15, 4, -1)]
    v = sp.Matrix.hstack(*[sp.Matrix(unit(a, 16)) + s * sp.Matrix(unit(b, 16)) for a, b, s in cols])
    if not (lp * v).is_zero_matrix or v.rank() != 4:
        raise SystemExit("v does not span ker L_p0")
    gens = stabilizer_derivations()
    if len(gens) != 3:
        raise SystemExit(f"stabilizer of (e1, e2) has dimension {len(gens)}, expected 3")
    for g in gens:
        image = sp.diag(g, g) * v
        coords = (v.T * v).inv() * v.T * image
        if v * coords != image:
            raise SystemExit("span(v) is not invariant under the stabilizer")
        if coords != g[4:8, 4:8]:
            raise SystemExit("the stabilizer acts on v and on H^perp by different matrices")
    print("nullity 4; v spans ker L_p0; stabilizer dimension 3; actions on v and on H^perp agree: K = xi_R")
    return 0


if __name__ == "__main__":
    sys.exit(main())
