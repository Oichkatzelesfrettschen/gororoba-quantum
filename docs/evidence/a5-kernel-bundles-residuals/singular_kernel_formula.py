"""Five kernel vectors of M(z) at the singular points of V(G) off V(Q), by a formula with integer coefficients.

V, M(z) v = Im(z v), Q and G are those of `kernel_plane_identities.py`; z = (a, t_8, b) with a and b imaginary
octonions, N the octonion norm, N(u, v) its polar form with N(u, u) = N(u). The singular points of V(G) off V(Q)
are the points with t_8 = 0, N(a, b) = 0 and N(a) = N(b) = nu nonzero (ledger row A5-493).

Formula. For an octonion y let x = [a, b, y] = (a b) y - a (b y), the associator, and
k(y) = (nu x, 0, -(b x) a). Then M(z) k(y) = 0, and z with the vectors k(y) spans a space of dimension 5.

Proof over a field of characteristic other than 2. The octonions are alternative, so the associator alternates,
and u w = -w u for orthogonal imaginary u, w. H = span(1, a, b, a b) is a quaternion subalgebra on which the norm
is diag(1, nu, nu, nu^2), so its orthogonal complement has dimension 4, and x = [a, b, y] runs through that
complement: the associator vanishes on H and is 2 (a b) y on the complement, an invertible map. For x in the
complement, the alternating associator gives (a b) x = -a (b x) = (x a) b, and b x is orthogonal to a, so
phi = -(b x) a / nu = -(a b) x / nu is imaginary and
- phi a - b x = -((b x) a) a / nu - b x = b x - b x = 0, the part of z (x, phi) along e_8;
- a x + phi b = a x - ((x a) b) b / nu = a x + x a = 0, the part along the first octonion.
With the product (a, b)(c, d) = (a c - conj(d) b, d a + b conj(c)) of `cd_core` these are the two components of
z (x, phi) for imaginary x and phi, so z (x, phi) = 0. The map x -> (x, phi) is injective and z = (a, b) has
first component outside the complement, which gives dimension 5 and rank M(z) at most 10.

The record holds the exact integer check of the formula at every pair (a, b) with entries in {-1, 0, 1},
N(a, b) = 0, N(a) = N(b) = nu in `NORMS` and the first nonzero entry of a and of b positive (`points`): the count
of points, of those where M(z) k(e_j) = 0 over the integers for j = 1, ..., 7 with k(e_j) of zero t_8, of those
where z and the k(e_j) span dimension 5 over Q, of those where rank M(z) = 10 over Q, and for each prime of
`PRIMES` the count of points with nu nonzero modulo the prime, of those where the span has dimension 5 modulo
the prime and of those where rank M(z) is 10 modulo the prime. An integer identity at a point holds modulo every
prime, so the modular counts test the dimension claim alone. `control` holds one pair off the locus, where the
formula fails.

`verdict` compares the fields and value types of a record with those of the record that the constants of this
module determine, then the input digests, then each group by name, then the serialized text.

The points run through `parallel.ordered_map`.

`--write` writes singular-kernel-formula-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/singular_kernel_formula.py --check
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

from sympy import GF, QQ
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "a5-kernel-bundles"))

from kernel_plane_identities import apply, block, octonion_product  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-singular-kernel-formula-v1"
RECORD = HERE / "singular-kernel-formula-result.json"
SOURCE_PATHS = (
    HERE / "singular_kernel_formula.py",
    HERE / "kernel_plane_identities.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)
NORMS = (1, 2, 3)
PRIMES = (3, 5, 7)
POINT_FIELDS = ("formula_holds", "span_dimension_five", "rank_ten")
PRIME_FIELDS = ("norm_nonzero", "span_dimension_five", "rank_ten")
POINTS = {"points": 6524, "formula_holds": 6524, "span_dimension_five": 6524, "rank_ten": 6524}
# Modulo 3 the pairs of norm 3 leave the locus, which keeps the 924 pairs of norm 1 and 2.
MODULAR = {
    "3": dict.fromkeys(PRIME_FIELDS, 924),
    "5": dict.fromkeys(PRIME_FIELDS, 6524),
    "7": dict.fromkeys(PRIME_FIELDS, 6524),
}
# a = e_1 + e_2 and b = e_1: N(a, b) = 1, off the locus.
CONTROL_PAIR = ((1, 1, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0, 0))


def kernel_vectors(first: Sequence[int], second: Sequence[int]) -> list[list[int]]:
    """For j = 1, ..., 7 the 16 integers (nu x, -(b x) a) with x = [a, b, e_j], each octonion with its real part.

    Position 0 holds the real part of x and position 8 the real part of -(b x) a, the coordinate t_8;
    `formula_holds` requires both to vanish, and the frame vector of length 15 drops position 0.
    """
    a, b = [0, *first], [0, *second]
    norm = sum(value * value for value in first)
    vectors = []
    for index in range(1, 8):
        unit = [1 if k == index else 0 for k in range(8)]
        left = octonion_product(octonion_product(a, b, 0), unit, 0)
        right = octonion_product(a, octonion_product(b, unit, 0), 0)
        x = [p - q for p, q in zip(left, right, strict=True)]
        phi = [-value for value in octonion_product(octonion_product(b, x, 0), a, 0)]
        vectors.append([x[0], *(norm * value for value in x[1:]), *phi])
    return vectors


def formula_holds(first: Sequence[int], second: Sequence[int]) -> bool:
    """x and phi are imaginary and M(z) k(e_j) = 0 over the integers for every j."""
    point = [*first, 0, *second]
    matrix = block(point, 0)
    return all(
        vector[0] == 0 and vector[8] == 0 and not any(apply(matrix, vector[1:], 0))
        for vector in kernel_vectors(first, second)
    )


def _rank(rows: Sequence[Sequence[int]], prime: int | None) -> int:
    """The rank of an integer matrix over Q, or modulo a prime."""
    domain = QQ if prime is None else GF(prime)
    return int(
        DomainMatrix([[domain.convert(x) for x in row] for row in rows], (len(rows), len(rows[0])), domain).rank()
    )


def point_row(pair: tuple[tuple[int, ...], tuple[int, ...]]) -> list[Any]:
    """At one pair: the statements of `POINT_FIELDS`, then per prime the statements of `PRIME_FIELDS`."""
    first, second = pair
    point = [*first, 0, *second]
    norm = sum(value * value for value in first)
    matrix = block(point, 0)
    span = [point, *(vector[1:] for vector in kernel_vectors(first, second))]
    row: list[Any] = [formula_holds(first, second), _rank(span, None) == 5, _rank(matrix, None) == 10]
    for prime in PRIMES:
        live = norm % prime != 0
        row.append([live, live and _rank(span, prime) == 5, live and _rank(matrix, prime) == 10])
    return row


def _leads_positive(vector: Sequence[int]) -> bool:
    return next((value for value in vector if value), 0) > 0


def pairs() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """The pairs of the module docstring, in lexicographic order."""
    box = [v for v in itertools.product((-1, 0, 1), repeat=7) if _leads_positive(v)]
    by_norm: dict[int, list[tuple[int, ...]]] = {norm: [] for norm in NORMS}
    for vector in box:
        norm = sum(value * value for value in vector)
        if norm in by_norm:
            by_norm[norm].append(vector)
    return [
        (a, b)
        for norm in NORMS
        for a in by_norm[norm]
        for b in by_norm[norm]
        if sum(x * y for x, y in zip(a, b, strict=True)) == 0
    ]


def point_record() -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    """The counts over all pairs: over the integers and Q, and per prime."""
    rows = parallel.ordered_map(point_row, pairs(), min_items=2)
    exact = {"points": len(rows)} | {field: sum(row[index] for row in rows) for index, field in enumerate(POINT_FIELDS)}
    modular = {
        str(prime): {field: sum(row[3 + which][index] for row in rows) for index, field in enumerate(PRIME_FIELDS)}
        for which, prime in enumerate(PRIMES)
    }
    return exact, modular


def _inputs() -> dict[str, str]:
    """The sha256 of every file whose bytes define the product, the block or this computation."""
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    """The whole record with the verdict."""
    exact, modular = point_record()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": _inputs(),
        "norms": list(NORMS),
        "points": exact,
        "modular": modular,
        "control": {
            "pair": [list(CONTROL_PAIR[0]), list(CONTROL_PAIR[1])],
            "formula_holds": formula_holds(*CONTROL_PAIR),
        },
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "inputs": _inputs(),
        "norms": list(NORMS),
        "points": dict(POINTS),
        "modular": {prime: dict(counts) for prime, counts in MODULAR.items()},
        "control": {"pair": [list(CONTROL_PAIR[0]), list(CONTROL_PAIR[1])], "formula_holds": False},
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
    """The reasons the record fails its own rules; empty when it passes."""
    expected = expected_record()
    if _shape(record) != _shape(expected):
        return ["the record has other fields or value types than the record the constants determine"]
    problems = []
    if record["inputs"] != expected["inputs"]:
        problems.append("the input digests differ from the files")
    if record["pass"] is not True:
        problems.append("the record states that it fails")
    messages = {
        "points": "the kernel formula, the span dimension or the rank fails at an integer point, or the counts differ",
        "modular": "the span dimension or the rank modulo a prime differs from the pinned counts",
        "control": "the control pair off the locus differs from its pinned fact",
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
    print(
        f"pass: the kernel formula holds at {record['points']['formula_holds']} of {record['points']['points']} points"
    )


if __name__ == "__main__":
    main()
