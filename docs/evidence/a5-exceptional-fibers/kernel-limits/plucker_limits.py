"""Exact limits of ker L_a along the arcs of the opposite-sign X incidences (ledger A5-272).

An arc x(s) = Phi(w(s), rho(s), sig(s), s1(s)) of the slice of X+ -> N- or X- -> N+ (Phi of ../arcs-x) is completed
by the producer's eliminated slice variables, mapped to the 32 coordinates of A_5 and fed to the left-multiplication
matrix of cd_core. The kernel of L_x(s) over the field of Laurent series has dimension 8, and its saturation in
k[[s]]^32 reduced modulo s is the limiting plane. Elimination over the discrete valuation ring k[[s]] with pivots of
least valuation and column operations only keeps the transformation unimodular, so the columns left without a pivot
form a saturated basis of the kernel and their constant terms span the limit; the series are truncated at order
ORDER and the pivot valuations sum to less than ORDER, so the constant terms of the truncated transformation
equal those of the exact one. The kernel dimension is at least 8 because the arc lies on the slice (J vanishes on
it to order ORDER), and at most 8 by the 24 pivots.

Fields: F_32009, F_32029 (the arcs of ../arcs-x) and Q, where an arc with rational coefficients is a real arc. The
record states, per incidence and field, whether every arc with one first-order direction (W : R : S) has one limiting
plane whatever its remaining first-order and second-order coefficients, how many distinct planes the directions
give, and whether each plane over Q reduces to the plane modulo each prime.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE.parent / "a5-kernel-attachments"))
sys.path.insert(0, str(EVIDENCE.parents[2] / "gororoba_quantum"))

import fiber_inputs  # noqa: E402
import nullity16_basepoints as basepoints  # noqa: E402
import nullity16_rees_fibers as rees  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-plucker-limits-v1"
RESULT = HERE / "x-opposite-result.json"
INPUTS = EVIDENCE / "working" / "build" / "inputs"
ORDER = 12
DIM = 32
SOURCE_NULLITY = 8
PRIMES = {32009: 10754, 32029: 9115}
INCIDENCES = {"xp-nm": ("X+->N-", 1), "xm-np": ("X-->N+", -1)}
HEADER_VARIABLES = ("t1", "t2", "t4", "t5", "t6", "t7", "t9")
# First-order directions (W, R, S) of the arc, W nonzero; each is one point of the fiber P^2.
DIRECTIONS = ((1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 2, 3), (1, -1, 2), (2, 1, 1), (2, 3, -1), (3, 1, 5), (1, 4, -3))
# Remaining arc coefficients (K, W2, R2, S2, K2): s1 = K s + K2 s^2, w = W s + W2 s^2 and so on.
VARIANTS = ((0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (5, 0, 0, 0, 7), (-2, 3, -1, 4, 1))

Scalar = Any  # int modulo a prime, or Fraction
Vector = tuple[Scalar, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class Series:
    """Power series over F_p (prime given) or Q (prime None), known modulo s^ORDER."""

    __slots__ = ("c", "p")

    def __init__(self, coefficients: Vector, prime: int | None) -> None:
        self.p = prime
        padded = tuple(coefficients[:ORDER]) + (0,) * (ORDER - len(coefficients))
        self.c: Vector = tuple(v % prime for v in padded) if prime else tuple(Fraction(v) for v in padded)

    def _lift(self, other: Series | int | Fraction) -> Series:
        return other if isinstance(other, Series) else Series((other,), self.p)

    def __add__(self, other: Series | int | Fraction) -> Series:
        return Series(tuple(a + b for a, b in zip(self.c, self._lift(other).c, strict=True)), self.p)

    __radd__ = __add__

    def __neg__(self) -> Series:
        return Series(tuple(-a for a in self.c), self.p)

    def __sub__(self, other: Series | int | Fraction) -> Series:
        return self + (-self._lift(other))

    def __rsub__(self, other: Series | int | Fraction) -> Series:
        return (-self) + other

    def __mul__(self, other: Series | int | Fraction) -> Series:
        right = self._lift(other).c
        out = [0] * ORDER
        for i, a in enumerate(self.c):
            if a:
                for j in range(ORDER - i):
                    out[i + j] += a * right[j]
        return Series(tuple(out), self.p)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Series:
        out = Series((1,), self.p)
        for _ in range(exponent):
            out = out * self
        return out

    def valuation(self) -> int:
        return next((k for k, v in enumerate(self.c) if v), ORDER)

    def shift(self, k: int) -> Series:
        """self / s^k for k at most the valuation."""
        return Series(self.c[k:], self.p)

    def inverse(self) -> Series:
        """Inverse of a unit."""
        lead = pow(self.c[0], -1, self.p) if self.p else 1 / self.c[0]
        out = [lead]
        for n in range(1, ORDER):
            out.append(-lead * sum(self.c[k] * out[n - k] for k in range(1, n + 1)))
        return Series(tuple(out), self.p)


def scalar(value: sympy.Expr, prime: int | None) -> Scalar:
    fraction = Fraction(int(value.p), int(value.q))
    return fraction.numerator * pow(fraction.denominator, -1, prime) % prime if prime else fraction


def evaluate(text: str, values: dict[str, Series], prime: int | None) -> Series:
    """Evaluate a polynomial in Singular notation at series."""
    names = tuple(values)
    polynomial = sympy.Poly(sympy.parse_expr(text.replace("^", "**")), *sympy.symbols(names))
    total = Series((), prime)
    for exponents, coefficient in polynomial.terms():
        term = Series((scalar(coefficient, prime),), prime)
        for name, exponent in zip(names, exponents, strict=True):
            if exponent:
                term = term * values[name] ** exponent
        total = total + term
    return total


def slice_data(slug: str, prime: int | None) -> dict[str, Any]:
    """Base point, slice columns and the producer's eliminated slice variables, over F_prime or over Q(i)."""
    task = fiber_inputs._task(INCIDENCES[slug][0])
    base = rees._base_task(task)
    data = basepoints._schur_coordinates(base)
    root = PRIMES[prime] if prime else None
    lines = (
        *rees._local_germ_lines(root, task, data, prime or rees.MODULAR_PRIME),
        'LIB "presolve.lib";',
        "list EP=elimpart(J);",
        'for(int i=1;i<=nvars(basering);i++){"RESULT ep_"+string(i),EP[5][i];}',
        "quit;",
    )
    outcome = rees._run_singular("\n".join(lines), "eliminated_slice_variables", 900)
    _require(outcome.status == "completed", f"{slug} elimpart {outcome.status}: {outcome.diagnostic}")
    substitutions = {name: outcome.results[f"ep_{i}"] for i, name in enumerate(data.slice_names, start=1)}
    _require(all("I" not in text for text in substitutions.values()), f"{slug}: a substitution involves I")
    kept = tuple(name for name, text in substitutions.items() if text == name)
    _require(kept == HEADER_VARIABLES, f"{slug}: kept slice variables {kept} differ from the header's")
    return {
        "slug": slug,
        "prime": prime,
        "boundary_point": [str(value) for value in base.boundary_point],
        "slice_columns": list(data.slice_columns),
        "slice_names": list(data.slice_names),
        "substitutions": substitutions,
    }


def header_ideals(slug: str, prime: int) -> tuple[list[str], list[str]]:
    lines = (INPUTS / f"p{prime}-r{PRIMES[prime]}" / f"{slug}.sing").read_text(encoding="utf-8").splitlines()
    _require(lines[1] == f"number I={PRIMES[prime]};", f"{slug}: header root differs")
    return tuple(line.split("=", 1)[1].rstrip(";").split(",") for line in lines[2:4])  # type: ignore[return-value]


def arc(sign: int, prime: int | None, direction: tuple[int, ...], variant: tuple[int, ...]) -> dict[str, Series]:
    """Phi of ../arcs-x at w = W s + W2 s^2, rho = R s + R2 s^2, sig = S s + S2 s^2, s1 = K s + K2 s^2."""
    big_w, big_r, big_s = direction
    k1, w2, r2, s2, k2 = variant
    w, rho, sig, s1 = (Series((0, a, b), prime) for a, b in ((big_w, w2), (big_r, r2), (big_s, s2), (k1, k2)))
    half = Series((pow(2, -1, prime) if prime else Fraction(1, 2),), prime)
    m = w + 1
    u = m.inverse()
    t9xp = -(w * w) * u * half
    return {
        "t1": s1,
        "t2": w * (w + 2) * u * half * (s1 - t9xp + 2),
        "t4": (m * rho + sig) * half,
        "t5": (m * rho - sig) * half,
        "t6": (m * sig + rho) * half,
        "t7": (rho - m * sig) * half,
        "t9": t9xp * sign,
    }


def operand(split: list[Series], prime: int | None) -> list[Series]:
    """The 32 coordinates of the operand with z_k = i^popcount(k) split_k and z_k = x_k + i x_(16+k)."""
    zero = Series((), prime)
    x = [zero] * DIM
    for k, value in enumerate(split, start=1):
        power = k.bit_count() % 4
        x[k + (16 if power % 2 else 0)] = value if power < 2 else -value
    return x


def left_matrix(x: list[Series]) -> list[list[Series]]:
    return [[x[row ^ column] * cd_sign(DIM, row ^ column, column) for column in range(DIM)] for row in range(DIM)]


def saturated_kernel(matrix: list[list[Series]], prime: int | None) -> tuple[list[Vector], list[int]]:
    """Constant terms of a saturated kernel basis over k[[s]], and the pivot valuations."""
    size = len(matrix)
    one, zero = Series((1,), prime), Series((), prime)
    transform = [[one if i == j else zero for j in range(size)] for i in range(size)]
    columns = list(range(size))
    rows = list(range(size))
    valuations: list[int] = []
    while columns:
        best = min(((matrix[i][j].valuation(), i, j) for i in rows for j in columns), default=(ORDER, 0, 0))
        if best[0] >= ORDER - sum(valuations):
            break
        value, i, j = best
        unit_inverse = matrix[i][j].shift(value).inverse()
        for c in columns:
            if c != j and matrix[i][c].valuation() < ORDER:
                factor = matrix[i][c].shift(value) * unit_inverse
                for r in range(size):
                    matrix[r][c] = matrix[r][c] - factor * matrix[r][j]
                    transform[r][c] = transform[r][c] - factor * transform[r][j]
        valuations.append(value)
        columns.remove(j)
        rows.remove(i)
    return [tuple(transform[r][c].c[0] for r in range(size)) for c in columns], valuations


def rref(vectors: list[Vector], prime: int | None) -> list[Vector]:
    rows = [list(v) for v in vectors]
    out: list[list[Scalar]] = []
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((r for r in rows if r[column]), None)
        if pivot is None:
            continue
        rows.remove(pivot)
        inverse = pow(pivot[column], -1, prime) if prime else 1 / pivot[column]
        pivot = [v * inverse % prime if prime else v * inverse for v in pivot]
        for other in (*rows, *out):
            factor = other[column]
            if factor:
                other[:] = [
                    (a - factor * b) % prime if prime else a - factor * b for a, b in zip(other, pivot, strict=True)
                ]
        out.append(pivot)
    return [tuple(r) for r in sorted(out, key=lambda r: next(i for i, v in enumerate(r) if v))]


def plane_text(plane: list[Vector]) -> list[list[str]]:
    return [[str(v) for v in row] for row in plane]


def one_arc(item: tuple[dict[str, Any], int, tuple[int, ...], tuple[int, ...], bool]) -> dict[str, Any]:
    data, sign, direction, variant, mutate = item
    prime = data["prime"]
    values = arc(-sign if mutate else sign, prime, direction, variant)
    full = dict(values)
    for name in data["slice_names"]:
        if name not in full:
            full[name] = evaluate(data["substitutions"][name], values, prime)
    base = [Fraction(v) for v in data["boundary_point"]]
    split = [
        full[data["slice_names"][data["slice_columns"].index(k)]] + scalar(sympy.Rational(base[k]), prime)
        if k in data["slice_columns"]
        else Series((scalar(sympy.Rational(base[k]), prime),), prime)
        for k in range(len(base))
    ]
    matrix = left_matrix(operand(split, prime))
    base_matrix = [[Series((entry.c[0],), prime) for entry in row] for row in matrix]
    base_kernel = rref(saturated_kernel(base_matrix, prime)[0], prime)
    kernel, valuations = saturated_kernel(matrix, prime)
    plane = rref(kernel, prime)
    record: dict[str, Any] = {
        "direction": list(direction),
        "variant": list(variant),
        "mutated": mutate,
        "base_nullity": len(base_kernel),
        "arc_nullity": len(kernel),
        "pivot_valuations": sorted(valuations),
        "limit_dimension": len(plane),
        "limit_in_base_kernel": len(rref([*base_kernel, *plane], prime)) == len(base_kernel),
        "plane": plane_text(plane),
        "plane_sha256": hashlib.sha256(json.dumps(plane_text(plane)).encode()).hexdigest(),
    }
    if prime:
        ideal_j, ideal_g = header_ideals(data["slug"], prime)
        record["j_nonzero"] = sum(evaluate(text, values, prime).valuation() < ORDER for text in ideal_j)
        forms = [evaluate(text, values, prime) for text in ideal_g]
        order = min(form.valuation() for form in forms)
        record["g_order"] = order
        record["g_limit"] = [form.c[order] for form in forms] if order < ORDER else None
    return record


def summarize(data: dict[str, Any], arcs: list[dict[str, Any]]) -> dict[str, Any]:
    kept = [a for a in arcs if not a["mutated"]]
    by_direction: dict[tuple[int, ...], set[str]] = {}
    for a in kept:
        by_direction.setdefault(tuple(a["direction"]), set()).add(a["plane_sha256"])
    return {
        "slug": data["slug"],
        "incidence": INCIDENCES[data["slug"]][0],
        "field": f"F_{data['prime']}" if data["prime"] else "Q",
        "slice": data,
        "arcs": len(kept),
        "base_nullity": sorted({a["base_nullity"] for a in kept}),
        "arc_nullity": sorted({a["arc_nullity"] for a in kept}),
        "limit_dimension": sorted({a["limit_dimension"] for a in kept}),
        "largest_pivot_valuation_sum": max(sum(a["pivot_valuations"]) for a in kept),
        "limit_in_base_kernel": all(a["limit_in_base_kernel"] for a in kept),
        "on_slice": all(a.get("j_nonzero", 0) == 0 for a in kept),
        "one_plane_per_direction": all(len(planes) == 1 for planes in by_direction.values()),
        "directions": len(by_direction),
        "distinct_planes": len({p for planes in by_direction.values() for p in planes}),
        "mutation_columns_without_pivot": sorted({a["arc_nullity"] for a in arcs if a["mutated"]}),
        "records": arcs,
    }


def reduces(rational: dict[str, Any], modular: dict[str, Any]) -> bool:
    """Every plane over Q, reduced modulo the prime, equals the plane of the same arc modulo the prime."""
    prime = modular["slice"]["prime"]
    for q_arc, p_arc in zip(rational["records"], modular["records"], strict=True):
        _require((q_arc["direction"], q_arc["variant"]) == (p_arc["direction"], p_arc["variant"]), "arc order")
        if q_arc["mutated"]:
            continue
        rows = [tuple(scalar(sympy.Rational(v), prime) for v in row) for row in q_arc["plane"]]
        if plane_text(rref(rows, prime)) != p_arc["plane"]:
            return False
    return True


def build() -> dict[str, Any]:
    cases = [(slug, prime) for slug in INCIDENCES for prime in (*PRIMES, None)]
    slices = [slice_data(slug, prime) for slug, prime in cases]
    items = [
        (data, INCIDENCES[data["slug"]][1], direction, variant, mutate)
        for data in slices
        for direction in DIRECTIONS
        for variant, mutate in (*((v, False) for v in VARIANTS), (VARIANTS[1], True))
    ]
    results = parallel.ordered_map(one_arc, items, min_items=1)
    per_case = len(DIRECTIONS) * (len(VARIANTS) + 1)
    summaries = [summarize(data, results[i * per_case : (i + 1) * per_case]) for i, data in enumerate(slices)]
    by_key = {(s["slug"], s["slice"]["prime"]): s for s in summaries}
    reductions = {
        f"{slug}:Q->F_{prime}": reduces(by_key[slug, None], by_key[slug, prime])
        for slug in INCIDENCES
        for prime in PRIMES
    }
    verdict = all(
        s["base_nullity"] == [16]
        and s["arc_nullity"] == [SOURCE_NULLITY]
        and s["limit_dimension"] == [SOURCE_NULLITY]
        and s["limit_in_base_kernel"]
        and s["on_slice"]
        and s["one_plane_per_direction"]
        and s["mutation_columns_without_pivot"] != [SOURCE_NULLITY]
        for s in summaries
    ) and all(reductions.values())
    return {
        "schema": SCHEMA,
        "order": ORDER,
        "directions": DIRECTIONS,
        "variants": VARIANTS,
        "reductions": reductions,
        "verdict": "survives" if verdict else "refuted",
        "cases": summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=RESULT)
    args = parser.parse_args()
    record = build()
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for case in record["cases"]:
        print(
            case["slug"],
            case["field"],
            {k: case[k] for k in case if k not in ("records", "slice", "slug", "field", "incidence")},
        )
    print("reductions", record["reductions"], "verdict", record["verdict"])


if __name__ == "__main__":
    main()
