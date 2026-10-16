"""The Albert algebra H3(O) from cd_core against SageMath's exceptional Jordan algebra.

- --extract (local, needs SageMath) runs one `sage -c` program that writes the 27 x 27 Jordan
  product table of `JordanAlgebra(OctonionAlgebra(QQ))` and the 8 x 8 table of that octonion
  algebra, with the Sage version and the program text, to sage_albert_table.json beside this file.
- --check (CI) imports cd_core alone. It builds H3(O) over the cd_core octonions: an element is
  (alpha, beta, gamma, x, y, z) for the Hermitian matrix [[alpha, x, y], [x*, beta, z], [y*, z*, gamma]],
  the product is X o Y = (XY + YX) / 2 with octonion products from cd_core.cd_sign, and the basis is
  Sage's order: E11, E22, E33, then e_0 ... e_7 in slot x (entry 12), slot y (entry 13), slot z
  (entry 23). It tests four entrywise maps T from Sage's coordinates to cd_core's on all 729 basis
  pairs, T(B_i o_Sage B_j) == T(B_i) o_cd T(B_j) in exact rationals: the identity, the sign flip on
  e3, e5, e6 (the octonion isomorphism Sage -> cd_core), entrywise conjugation (the transpose, which
  absorbs Sage's opposite octonion product), and the flip composed with conjugation. One failing pair
  refutes a map. It also checks commutativity and the Jordan identity
  (X o Y) o (X o X) == X o (Y o (X o X)) on seeded random rational elements of H3(O), and, as a
  control with teeth, the same identity on the Hermitian 3 x 3 matrices over the cd_core sedenions.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402

EVIDENCE = HERE / "sage_albert_table.json"
SCHEMA = "sage-albert-table-v1"
Vec = list[Fraction]
Element = tuple[Fraction, Fraction, Fraction, Vec, Vec, Vec]

SAGE_PROGRAM = """
import json
from sage.all import QQ, OctonionAlgebra, JordanAlgebra
from sage.version import version
O = OctonionAlgebra(QQ)
J = JordanAlgebra(O)
B = list(J.basis())
OB = list(O.basis())
def coords(X):
    d = X._data
    return [d[0], d[1], d[2]] + [c for k in (3, 4, 5) for c in d[k].vector()]
def sparse(v):
    return [[k, str(c)] for k, c in enumerate(v) if c]
print(json.dumps({
    "sage_version": version,
    "algebra": str(J),
    "octonion_basis": [str(b) for b in OB],
    "octonion_products": [[sparse(list((a * b).vector())) for b in OB] for a in OB],
    "jordan_products": [[sparse(coords(a * b)) for b in B] for a in B],
}))
"""


def octonion_mul(dim: int, a: Vec, b: Vec) -> Vec:
    out = [Fraction(0)] * dim
    for p, ap in enumerate(a):
        if ap:
            for q, bq in enumerate(b):
                if bq:
                    out[p ^ q] += cd_sign(dim, p, q) * ap * bq
    return out


def conj(a: Vec) -> Vec:
    return [a[0]] + [-c for c in a[1:]]


def scalar(dim: int, s: Fraction) -> Vec:
    return [s] + [Fraction(0)] * (dim - 1)


def matrix(dim: int, x: Element) -> list[list[Vec]]:
    alpha, beta, gamma, a, b, c = x
    return [
        [scalar(dim, alpha), a, b],
        [conj(a), scalar(dim, beta), c],
        [conj(b), conj(c), scalar(dim, gamma)],
    ]


def jordan(dim: int, x: Element, y: Element) -> Element:
    """X o Y = (XY + YX) / 2, read back from its upper triangle after checking it is Hermitian."""
    mx, my = matrix(dim, x), matrix(dim, y)
    half = Fraction(1, 2)
    prod = [[[Fraction(0)] * dim for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            for k in range(3):
                for left, right in ((mx[r][k], my[k][c]), (my[r][k], mx[k][c])):
                    term = octonion_mul(dim, left, right)
                    prod[r][c] = [u + half * v for u, v in zip(prod[r][c], term, strict=True)]
    for r in range(3):
        if any(prod[r][r][1:]):
            raise RuntimeError("X o Y has a nonreal diagonal entry")
        for c in range(r + 1, 3):
            if prod[c][r] != conj(prod[r][c]):
                raise RuntimeError("X o Y is not Hermitian")
    return (prod[0][0][0], prod[1][1][0], prod[2][2][0], prod[0][1], prod[0][2], prod[1][2])


def flatten(x: Element) -> Vec:
    return [x[0], x[1], x[2], *x[3], *x[4], *x[5]]


def unflatten(v: Vec, dim: int = 8) -> Element:
    return (v[0], v[1], v[2], list(v[3 : 3 + dim]), list(v[3 + dim : 3 + 2 * dim]), list(v[3 + 2 * dim :]))


def basis_element(k: int) -> Element:
    v = [Fraction(0)] * 27
    v[k] = Fraction(1)
    return unflatten(v)


# Entrywise maps on Sage coordinates: (octonion coefficient sign by index, conjugate the slot).
FLIP = (3, 5, 6)
MAPS: dict[str, tuple[tuple[int, ...], bool]] = {
    "identity": ((), False),
    "flip e3 e5 e6": (FLIP, False),
    "entrywise conjugation": ((), True),
    "flip e3 e5 e6 then conjugation": (FLIP, True),
}


def apply_map(v: Vec, flips: tuple[int, ...], conjugate: bool) -> Vec:
    out = list(v)
    for slot in range(3):
        for t in range(8):
            k = 3 + 8 * slot + t
            sign = -1 if t in flips else 1
            if conjugate and t > 0:
                sign = -sign
            out[k] = sign * out[k]
    return out


def dense(entries: list[list[Any]], size: int) -> Vec:
    out = [Fraction(0)] * size
    for k, text in entries:
        out[k] = Fraction(text)
    return out


def random_element(rng: random.Random, dim: int) -> Element:
    def r() -> Fraction:
        return Fraction(rng.randint(-9, 9), rng.randint(1, 5))

    return (r(), r(), r(), [r() for _ in range(dim)], [r() for _ in range(dim)], [r() for _ in range(dim)])


def jordan_identity_failures(dim: int, seed: str, trials: int) -> tuple[int, int]:
    """(commutativity failures, Jordan identity failures) on seeded random rational elements."""
    rng = random.Random(seed)
    comm = ident = 0
    for _ in range(trials):
        x, y = random_element(rng, dim), random_element(rng, dim)
        comm += flatten(jordan(dim, x, y)) != flatten(jordan(dim, y, x))
        xx = jordan(dim, x, x)
        left = jordan(dim, jordan(dim, x, y), xx)
        right = jordan(dim, x, jordan(dim, y, xx))
        ident += flatten(left) != flatten(right)
    return comm, ident


def check(data: dict[str, Any]) -> list[str]:
    if data.get("schema") != SCHEMA:
        raise RuntimeError("unknown evidence schema")
    lines = [f"sage {data['sage_version']}: {data['algebra']}"]
    sage_oct = [[dense(entry, 8) for entry in row] for row in data["octonion_products"]]
    opposite = all(
        sage_oct[a][b] == [Fraction(cd_sign(8, b, a)) if k == a ^ b else Fraction(0) for k in range(8)]
        for a in range(8)
        for b in range(8)
    )
    if not opposite:
        raise RuntimeError("the retained Sage octonion table is not the opposite of cd_core")
    lines.append("sage octonion basis " + " ".join(data["octonion_basis"]) + ": opposite of cd_core on 64 pairs")
    sage = [[dense(entry, 27) for entry in row] for row in data["jordan_products"]]
    basis = [basis_element(k) for k in range(27)]
    cd = [[flatten(jordan(8, basis[i], basis[j])) for j in range(27)] for i in range(27)]
    results = {}
    for name, (flips, conjugate) in MAPS.items():
        failures = 0
        for i in range(27):
            ti = apply_map(flatten(basis[i]), flips, conjugate)
            for j in range(27):
                tj = apply_map(flatten(basis[j]), flips, conjugate)
                image = apply_map(sage[i][j], flips, conjugate)
                failures += image != flatten(jordan(8, unflatten(ti), unflatten(tj)))
        results[name] = failures
        lines.append(f"map {name}: {failures} of 729 basis pairs fail")
    expected = {
        "identity": False,
        "flip e3 e5 e6": True,
        "entrywise conjugation": True,
        "flip e3 e5 e6 then conjugation": False,
    }
    for name, holds in expected.items():
        if (results[name] == 0) != holds:
            raise RuntimeError(f"map {name}: {results[name]} failures, expected it to {'hold' if holds else 'fail'}")
    differs = sum(sage[i][j] != cd[i][j] for i in range(27) for j in range(27))
    lines.append(f"untransformed tables differ on {differs} of 729 basis pairs")
    comm, ident = jordan_identity_failures(8, "albert:octonions", 40)
    if comm or ident:
        raise RuntimeError(f"H3(O): {comm} commutativity and {ident} Jordan identity failures")
    lines.append("H3(O) over cd_core: commutative and Jordan identity on 40 of 40 seeded rational pairs")
    comm, ident = jordan_identity_failures(16, "albert:sedenions", 10)
    if comm or not ident:
        raise RuntimeError(f"H3(S) control: {comm} commutativity and {ident} Jordan identity failures")
    lines.append(f"H3(S) control: commutative, Jordan identity fails on {ident} of 10 seeded rational pairs")
    return lines


def extract() -> dict[str, Any]:
    run = subprocess.run(["sage", "-c", SAGE_PROGRAM], capture_output=True, text=True, check=True)
    data: dict[str, Any] = json.loads(run.stdout.strip().splitlines()[-1])
    return {"schema": SCHEMA, "sage_program": SAGE_PROGRAM, **data}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract", action="store_true", help="export the Sage tables through sage -c")
    mode.add_argument("--check", action="store_true", help="verify the retained Sage tables against cd_core")
    args = parser.parse_args()
    if args.extract:
        EVIDENCE.write_text(json.dumps(extract(), indent=None, separators=(",", ":"), sort_keys=True) + "\n")
        print(f"wrote {EVIDENCE.relative_to(ROOT)}")
    print("\n".join(check(json.loads(EVIDENCE.read_text()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
