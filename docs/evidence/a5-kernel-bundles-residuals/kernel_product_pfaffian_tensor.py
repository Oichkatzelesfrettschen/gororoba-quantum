"""The kernel product on V(Q) as a polynomial tensor: T(z) = -2 G(z) z (x) z, exact over Q(i).

V, M(z), K(z) = ker M(z), Q and G are those of `kernel_plane_identities.py`: V is the 15-dimensional space of
imaginary sedenions with coordinates t_1, ..., t_15, M(z) v = Im(z v) is skew, and G = Q^2 - 4 (N1 N3 - p^2).

For a triple I = (i_1 < i_2 < i_3) of indices, P_I(z) = eps(I) Pf(M(z) with the rows and columns of I removed),
eps(I) the sign of the permutation (I, complement of I in increasing order). P(z) = sum_I P_I(z) e_I is a
three-vector whose coordinates are polynomials of degree 6 in z. With omega = sum_(r<c) M_rc t_r ^ t_c the
two-form of M(z), omega^6 / 6! = sum_J Pf(M_J) t_J over the 12-subsets J, and P(z) is its dual under the volume
form: omega^6 is nonzero exactly when rank M(z) >= 12, and when the rank is 12 every vector of K(z) contracts
omega^6 to zero, so P(z) is a nonzero multiple of k_1 ^ k_2 ^ k_3 for a basis of K(z).

tau: Lambda^3 V -> V (x) V sends a ^ b ^ c to Im(a b) (x) c + Im(b c) (x) a + Im(c a) (x) b, and T(z) = tau(P(z)),
a 15 x 15 array of polynomials of degree 6 in z. At a rank-12 point of V(Q) the point z is central in K(z) and
M(k) k' = mu(k, k') z (ledger row A5-479), so with K(z) = C z + C k_1 + C k_2 and P(z) = c z ^ k_1 ^ k_2, c nonzero,
T(z) = c mu(k_1, k_2) z (x) z: T(z) vanishes exactly when the product on K(z) does.

The record holds four groups of exact computations over Q(i).

1. `calibration`: the Pfaffian routine on a 4 x 4 integer matrix against a_12 a_34 - a_13 a_24 + a_14 a_23, and
   Pf^2 = det on the first 12 x 12 principal block of M(z) with a nonzero Pfaffian at one grid point.
2. `grid`: the identity T(z) = -2 G(z) z (x) z, all 225 entries, at the 49 points of the family `FQ` of
   `kernel_plane_identities.py` with C = 1 and A, B in `GRID_VALUES`. Each coordinate of the `FQ` point has degree
   at most 1 in each of A, B and C, so each entry of T + 2 G z (x) z has degree at most 6 in each of them; the
   scaling (B, C) -> (t B, t C) scales z by t and the entry by t^6, so an entry that vanishes at C = 1 vanishes for
   every nonzero C; and a polynomial of degree at most 6 in A and in B that vanishes on a 7 x 7 grid is zero. The
   49 points therefore decide the identity on the whole family, as polynomials in A, B and C.
3. `null_points`: two exact points of V(Q) minus V(G) with N1(z) = 0, outside the orbits that the family meets,
   with Q, G, N1, dim K(z), whether the identity holds, whether T vanishes and whether P is a nonzero multiple of
   the three-vector of a basis of K(z).
4. `fixtures`: the same three statements at the 66 exact fixtures of `nullity4-kernel-gauss-result.json`, counted
   per stratum, with two more: whether T = w (x) z for a vector w (every row of T is a multiple of z, which holds
   wherever z is central in a three-dimensional K(z), since then tau(c z ^ k_1 ^ k_2) = c Im(k_1 k_2) (x) z), and
   whether the polar form of Q vanishes on K(z).

`verdict` compares the fields and value types of a record with those of the record that the constants of this
module determine, then the input digests, then the serialized text; a record passes exactly when it is that
record.

The grid points and the fixtures run through `parallel.ordered_map`.

`--write` writes kernel-product-pfaffian-tensor-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_product_pfaffian_tensor.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp
from sympy import QQ_I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BUNDLES))

from kernel_plane_identities import SEDENION, _frame, block, family_point, form  # noqa: E402
from kernel_three_plane_zero_divisors import _exact_block, _exact_kernel  # noqa: E402
from nullity4_gauss_image import FIXTURES, STRATA, _fixture_splits  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-kernel-product-pfaffian-tensor-v1"
RECORD = HERE / "kernel-product-pfaffian-tensor-result.json"
SOURCE_PATHS = (
    HERE / "kernel_product_pfaffian_tensor.py",
    HERE / "kernel_plane_identities.py",
    HERE / "nullity4_gauss_image.py",
    HERE / "kernel_three_plane_zero_divisors.py",
    FIXTURES,
    ROOT / "gororoba_quantum" / "cd_core.py",
)
FIELD = "Q(i)"

IMAGINARY = 15
TRIPLES = tuple(itertools.combinations(range(IMAGINARY), 3))
# T(z) = CONSTANT * G(z) * z (x) z on V(Q), under the sign eps(I) of the module docstring.
CONSTANT = -2
CALIBRATION_MATRIX = ((0, 1, 2, 3), (-1, 0, 4, 5), (-2, -4, 0, 6), (-3, -5, -6, 0))
CALIBRATION = {"pfaffian_4x4": "8", "pfaffian_squared_is_determinant": True}
# The family FQ at C = 1 and A, B in these values; the diagonal A = B is the locus s = 0, where G = 0.
GRID_VALUES = (1, 2, 3, 4, 5, 6, 7)
GRID = {
    "family": "FQ",
    "C": 1,
    "values": list(GRID_VALUES),
    "points": 49,
    "on_quadric": 49,
    "identity_holds": 49,
    "rank_twelve": 42,
    "quartic_zero": 7,
    "tensor_zero": 7,
}
# z = (a, beta, b) with a = e_1 + i e_2 a null vector of Im O, so N1(z) = 0, and N1(a, b) = 1.
NULL_POINTS = (
    ["1", "I", "0", "0", "0", "0", "0", "I", "1", "0", "0", "0", "0", "0", "0"],
    ["1", "I", "0", "0", "0", "0", "0", "0", "1", "0", "0", "I", "0", "0", "0"],
)
NULL_POINT_FACTS = {
    "Q": "0",
    "G": "4",
    "N1": "0",
    "kernel_dimension": 3,
    "identity_holds": True,
    "tensor_zero": False,
    "three_vector_spans_kernel": True,
}
# Per stratum: fixtures, those at which T = -2 G z (x) z, those at which T = 0, those at which P is a nonzero
# multiple of the three-vector of K(z), those at which T = w (x) z and those at which Q vanishes on K(z).
FIXTURE_FIELDS = (
    "identity_holds",
    "tensor_zero",
    "three_vector_spans_kernel",
    "right_factor_is_point",
    "kernel_is_null",
)
FIXTURE_COUNTS = {
    STRATA[0]: dict(zip(("fixtures", *FIXTURE_FIELDS), (12, 12, 0, 12, 12, 12), strict=True)),
    STRATA[1]: dict(zip(("fixtures", *FIXTURE_FIELDS), (52, 0, 0, 52, 52, 0), strict=True)),
    STRATA[2]: dict(zip(("fixtures", *FIXTURE_FIELDS), (2, 2, 2, 2, 2, 2), strict=True)),
}


def _require(condition: bool, message: str) -> None:
    """Raise when an internal invariant fails; unlike `assert` it survives `python -O`."""
    if not condition:
        raise RuntimeError(message)


def pfaffian(matrix: Sequence[Sequence[Any]]) -> Any:
    """The Pfaffian of a skew matrix of even order over Q(i), by simultaneous row and column elimination.

    At step k the pivot a[k][k+1] is brought in by one simultaneous swap (the Pfaffian changes sign), and the
    congruence that adds a multiple of row and column k+1 to row and column i > k+1 clears a[k][i] and keeps the
    Pfaffian; the Pfaffian is the product of the pivots with the sign of the swaps.
    """
    a = [list(row) for row in matrix]
    size = len(a)
    _require(size % 2 == 0, "the Pfaffian needs an even order")
    result = QQ_I.one
    for k in range(0, size, 2):
        pivot = next((j for j in range(k + 1, size) if a[k][j]), None)
        if pivot is None:
            return QQ_I.zero
        if pivot != k + 1:
            a[k + 1], a[pivot] = a[pivot], a[k + 1]
            for row in a:
                row[k + 1], row[pivot] = row[pivot], row[k + 1]
            result = -result
        result = result * a[k][k + 1]
        for i in range(k + 2, size):
            if a[k][i]:
                factor = a[k][i] / a[k][k + 1]
                for c in range(k, size):
                    a[i][c] = a[i][c] - factor * a[k + 1][c]
                for r in range(k, size):
                    a[r][i] = a[r][i] - factor * a[r][k + 1]
    return result


def complement_sign(triple: Sequence[int]) -> int:
    """eps(I): the sign of the permutation that lists I and then its complement, each in increasing order.

    Moving i_1 < i_2 < i_3 (zero-based) to the front crosses i_1 + (i_2 - 1) + (i_3 - 2) smaller indices.
    """
    return -1 if (sum(triple) - 3) % 2 else 1


def three_vector(point: Sequence[Any]) -> dict[tuple[int, ...], Any]:
    """P_I(z) for every triple I: eps(I) times the Pfaffian of M(z) without the rows and columns of I."""
    matrix = block(point, QQ_I.zero)
    vector: dict[tuple[int, ...], Any] = {}
    for triple in TRIPLES:
        rest = [k for k in range(IMAGINARY) if k not in triple]
        vector[triple] = complement_sign(triple) * pfaffian([[matrix[r][c] for c in rest] for r in rest])
    return vector


def product_tensor(vector: dict[tuple[int, ...], Any]) -> list[list[Any]]:
    """T = tau(P): the entry (r, c) collects sign(e_i e_j) P_I over the cyclic splittings (i, j; c) of I with
    e_i e_j = sign e_r, since Im(e_i e_j) = sign e_(i xor j) for distinct imaginary units."""
    tensor = [[QQ_I.zero] * IMAGINARY for _ in range(IMAGINARY)]
    for triple, value in vector.items():
        if not value:
            continue
        for x, y, w in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            i, j = triple[x] + 1, triple[y] + 1
            row = (i ^ j) - 1
            tensor[row][triple[w]] = tensor[row][triple[w]] + SEDENION[i][j] * value
    return tensor


def invariants(point: Sequence[Any]) -> tuple[Any, Any, Any]:
    """Q, G and N1 at a point."""
    zero = QQ_I.zero
    squares = [form(index, point, point, zero) for index in range(3)]
    pairing = sum((point[k] * point[k + 8] for k in range(7)), zero)
    norm = sum(squares, zero)
    return norm, norm * norm - 4 * (squares[0] * squares[2] - pairing * pairing), squares[0]


def spans_kernel(vector: dict[tuple[int, ...], Any], kernel: Sequence[Sequence[Any]]) -> bool:
    """P is a nonzero multiple of k_1 ^ k_2 ^ k_3 for the basis of a three-dimensional K(z)."""
    if len(kernel) != 3 or not any(vector.values()):
        return False
    minors = {
        triple: DomainMatrix([[k[index] for index in triple] for k in kernel], (3, 3), QQ_I).det() for triple in TRIPLES
    }
    anchor = next(triple for triple in TRIPLES if minors[triple])
    return all(vector[triple] * minors[anchor] == vector[anchor] * minors[triple] for triple in TRIPLES)


def point_facts(point: Sequence[Any]) -> dict[str, Any]:
    """Q, G, N1, dim K(z), the identity T = CONSTANT G z (x) z, T = 0, `spans_kernel`, whether every row of T is a
    multiple of z and whether the polar form of Q vanishes on K(z), at one exact point."""
    norm, quartic, first = invariants(point)
    kernel = _exact_kernel(_exact_block(list(point)))
    vector = three_vector(point)
    tensor = product_tensor(vector)
    count = range(IMAGINARY)
    return {
        "Q": norm,
        "G": quartic,
        "N1": first,
        "kernel_dimension": len(kernel),
        "identity_holds": all(tensor[r][c] == CONSTANT * quartic * point[r] * point[c] for r in count for c in count),
        "tensor_zero": not any(x for row in tensor for x in row),
        "three_vector_spans_kernel": spans_kernel(vector, kernel),
        "right_factor_is_point": all(
            not (row[c] * point[d] - row[d] * point[c])
            for row in tensor
            for c in count
            for d in range(c + 1, IMAGINARY)
        ),
        "kernel_is_null": all(
            not sum((x * y for x, y in zip(first, second, strict=True)), QQ_I.zero)
            for first in kernel
            for second in kernel
        ),
    }


def _text(value: Any) -> str:
    """The exact value of a Q(i) element as text."""
    return str(QQ_I.to_sympy(value))


def grid_point(values: tuple[int, int]) -> list[Any]:
    """The `FQ` point at (A, B, C) = (values, 1) as elements of Q(i)."""
    polynomials, generators = family_point("FQ")
    at = dict(zip(generators, (*values, 1), strict=True))
    return [QQ_I.from_sympy(sp.expand(sp.sympify(x).subs(at))) for x in polynomials]


def grid_row(values: tuple[int, int]) -> list[bool]:
    """At one grid point: Q = 0, the identity, rank M(z) = 12, G = 0 and T = 0."""
    facts = point_facts(grid_point(values))
    return [
        not facts["Q"],
        facts["identity_holds"],
        facts["kernel_dimension"] == 3,
        not facts["G"],
        facts["tensor_zero"],
    ]


def grid_record() -> dict[str, Any]:
    """The counts of `grid_row` over the 7 x 7 grid."""
    rows = parallel.ordered_map(grid_row, list(itertools.product(GRID_VALUES, repeat=2)), min_items=2)
    names = ("on_quadric", "identity_holds", "rank_twelve", "quartic_zero", "tensor_zero")
    counts = {name: sum(row[index] for row in rows) for index, name in enumerate(names)}
    return {"family": "FQ", "C": 1, "values": list(GRID_VALUES), "points": len(rows), **counts}


def calibration_record() -> dict[str, Any]:
    """The Pfaffian of the 4 x 4 calibration matrix, and Pf^2 = det on the first 12 x 12 principal block of M(z)
    with a nonzero Pfaffian at the grid point (A, B) = (1, 2)."""
    small = [[QQ_I.convert(x) for x in row] for row in CALIBRATION_MATRIX]
    matrix = block(grid_point((GRID_VALUES[0], GRID_VALUES[1])), QQ_I.zero)
    squares = False
    for triple in TRIPLES:
        rest = [k for k in range(IMAGINARY) if k not in triple]
        minor = [[matrix[r][c] for c in rest] for r in rest]
        value = pfaffian(minor)
        if value:
            squares = value * value == DomainMatrix(minor, (12, 12), QQ_I).det()
            break
    return {"pfaffian_4x4": _text(pfaffian(small)), "pfaffian_squared_is_determinant": squares}


def null_point_record(strings: Sequence[str]) -> dict[str, Any]:
    """`point_facts` at one of `NULL_POINTS`, with the exact values as text."""
    facts = point_facts([QQ_I.from_sympy(sp.sympify(x)) for x in strings])
    return {"point": list(strings), **{key: _text(facts[key]) for key in ("Q", "G", "N1")}} | {
        key: facts[key] for key in ("kernel_dimension", "identity_holds", "tensor_zero", "three_vector_spans_kernel")
    }


def fixture_row(job: tuple[int, str, list[int]]) -> list[Any]:
    """At one fixture: the stratum and the statements of `FIXTURE_FIELDS`."""
    _, stratum, split = job
    facts = point_facts(_frame(split))
    return [stratum, *(facts[field] for field in FIXTURE_FIELDS)]


def fixture_record() -> dict[str, dict[str, int]]:
    """Per stratum: the count of fixtures and of those with each property of `fixture_row`."""
    rows = parallel.ordered_map(fixture_row, _fixture_splits(), min_items=2)
    record = {}
    for stratum in STRATA:
        mine = [row for row in rows if row[0] == stratum]
        record[stratum] = {"fixtures": len(mine)} | {
            field: sum(row[index + 1] for row in mine) for index, field in enumerate(FIXTURE_FIELDS)
        }
    return record


def _inputs() -> dict[str, str]:
    """The sha256 of every file whose bytes define the points, the blocks or this computation."""
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    """The whole record: calibration, grid, null points and fixtures, with the verdict."""
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "constant": CONSTANT,
        "calibration": calibration_record(),
        "grid": grid_record(),
        "null_points": [null_point_record(strings) for strings in NULL_POINTS],
        "fixtures": fixture_record(),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "constant": CONSTANT,
        "calibration": dict(CALIBRATION),
        "grid": {**GRID, "values": list(GRID_VALUES)},
        "null_points": [{"point": list(strings), **NULL_POINT_FACTS} for strings in NULL_POINTS],
        "fixtures": {stratum: dict(counts) for stratum, counts in FIXTURE_COUNTS.items()},
        "pass": True,
    }


def _shape(value: Any) -> Any:
    """The fields and value types of a record: keys of every mapping, lengths of every list, type names of leaves."""
    if isinstance(value, dict):
        return {str(key): _shape(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        return [_shape(item) for item in value]
    return type(value).__name__


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes.

    The comparison of fields and value types comes first and ends the verdict on a difference, since `==` holds
    True equal to 1; past it each group is compared with the constants by name and last the serialized text.
    """
    expected = expected_record()
    if _shape(record) != _shape(expected):
        return ["the record has other fields or value types than the record the constants determine"]
    problems = []
    if record["inputs"] != expected["inputs"]:
        problems.append("the input digests differ from the files")
    if record["pass"] is not True:
        problems.append("the record states that it fails")
    messages = {
        "calibration": "the Pfaffian routine fails its calibration",
        "grid": "the identity T = -2 G z (x) z does not hold on the whole grid, or the grid tallies differ",
        "null_points": "a point with N1(z) = 0 differs from its pinned facts",
        "fixtures": "the fixture tallies differ from the pinned counts",
    }
    for group, message in messages.items():
        if record[group] != expected[group]:
            problems.append(message)
    if _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    grid = record["grid"]
    print(f"pass: T = {CONSTANT} G z (x) z at {grid['identity_holds']} of {grid['points']} grid points")


if __name__ == "__main__":
    main()
