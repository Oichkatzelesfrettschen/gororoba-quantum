"""Attaching maps of the eight first-order-resolved A_5 incidences: certificates 0 to 3 of sub-step 3a.

The source closure of each incidence is complex-algebraic, so its transverse germ (Z, 0) at the retained basepoint has a
link L = Z meet S_eps. One blow-up resolves the Gauss map kappa of Z minus 0, and on the exceptional divisor
E = P(C_0 Z) it is the projectivized first-order map phi (rows 2c and 2i of the ledger). This producer reads only
the four retained records of rows 2b (path-supported basepoints), 2c (first-order normal cones), 2i (holomorphic Schur
blow-ups) and 2l (real limit sets), and certifies per incidence, exactly over Q(i) and over F_32009 (i = 10754):

  0. the punctured germ has constant nullity 8: the pivot Pfaffian of the Schur block is a unit, phi has no zero on E
     (so every nonempty exceptional chart is base free and the Schur form is nonzero, of rank at least two, on the
     punctured cone), and the real nullity is at most 8. The vanishing of the rank-four Pfaffians, which makes the
     rank exactly two and the nullity exactly 8, needs entries of the Schur matrix that the retained records do not
     hold; it is carried from the exact 2i and 2c runs over Q(i) and stays undecided modulo 32009;
  1. the conical structure, decided from the generators: a linear space (smooth germs), the A_1 cone of E8-bar to B9
     (one quadric of rank 3 in the span of the linear generators), or the union of two linear components, for which
     the retained generators equal the ideal of the union in degrees 1 and 2, where that ideal is generated;
  2. phi is linear and injective on each tangent-cone component, the image planes of two components meet only at 0,
     the 2i and 2c image generators each vanish on the image of E, and the two coordinate systems agree up to an
     invertible change that carries one image ideal onto the other;
  3. the homotopy data as classes: the Euler class of the circle bundle p: S(O_E(-1)) -> E, the map E -> Lambda on
     H_2, and c_1(S|Lambda) = -H computed from the degree of the pulled-back Plucker coordinates, with its value on
     the generator of H_2 of each component.

The independent topology checks recompute the Euler number from the degree of E in its span, H_1(L) from the Gysin
sequence, and c_1 = -H from the Plucker coordinates of 2i. The identification of L with the unit circle bundle of
O_E(-1) (the radial deformation of kappa to phi o p) and the passage from the first-order form to the germ rest on the
cited theorems and stay inferred; the record labels them so.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/attaching_maps_resolved.py [--check |
--self-test]
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

SCHEMA = "gororoba.a5.attaching-maps-resolved/1"
RECORD = HERE / "attaching-maps-resolved-result.json"
PATH_SUPPORTED = HERE / "path-supported-basepoints-result.json"
FIRST_ORDER = HERE / "first-order-normal-cones-result.json"
HOLOMORPHIC = HERE / "holomorphic-gauss-fibers-result.json"
REAL_LIMITS = HERE / "real-limit-sets-result.json"
PRODUCER = HERE / "attaching_maps_resolved.py"
INCIDENCES = (
    "E8bar->B9",
    "E8bar->V",
    "Iso->B9",
    "W8->B9",
    "X+->B9",
    "X+->Va+",
    "X-->B9",
    "X-->Va-",
)
PRIME = 32009
SQRT_MINUS_ONE = 10754

Elem = Any
Mono = tuple[tuple[int, int], ...]
Poly = dict[Mono, Elem]
Vector = list[Elem]

# The linear components of the three two-component tangent cones, as bases in the slice coordinates t_1, t_2, ...
# (one vector per column of the slice). The producer verifies each claim exactly: every retained generator vanishes on
# the component, its dimension is the recorded dimension, and the recorded component count and multiplicity admit no
# third component.
COMPONENT_WITNESSES: dict[str, tuple[tuple[tuple[int, ...], ...], ...]] = {
    "E8bar->V": (
        ((0, 1, 0, 0, 0, 0, 0), (0, 0, -1, 1, 0, 0, 0), (0, 0, 0, 0, 1, 1, 0)),
        ((1, 0, 0, 0, 0, 0, 0), (0, 0, 1, 0, 1, 0, 0), (0, 0, 0, 1, 0, 1, 0)),
    ),
    "X+->Va+": (
        ((0, 1, -1, 0, 0, 0, 0, 0), (0, 0, 0, 1, -1, 0, 0, 0), (0, 0, 0, 0, 0, 1, 1, 0)),
        ((0, 1, 1, 0, 0, 0, 0, 0), (0, 0, 0, 1, 1, 0, 0, 0), (0, 0, 0, 0, 0, 1, -1, 0)),
    ),
}
COMPONENT_WITNESSES["X-->Va-"] = COMPONENT_WITNESSES["X+->Va+"]

# The predictions of the program section's table, entered by hand and never read from a record.
PREDICTED: dict[str, dict[str, Any]] = {
    "Iso->B9": {
        "germ_dimension": 2,
        "tangent_cone_multiplicity": 1,
        "link": ["S^3"],
        "link_h1": ["0"],
        "euler_class_coefficients": [-1],
        "exceptional_projective_dimensions": [1],
        "image_projective_dimension_degree_components": [1, 1, 1],
        "image_components_disjoint": None,
        "c1_on_curve_components": [-1],
    },
    "W8->B9": {
        "germ_dimension": 3,
        "tangent_cone_multiplicity": 1,
        "link": ["S^5"],
        "link_h1": ["0"],
        "euler_class_coefficients": [-1],
        "exceptional_projective_dimensions": [2],
        "image_projective_dimension_degree_components": [2, 1, 1],
        "image_components_disjoint": None,
        "c1_on_curve_components": [None],
    },
    "X+->B9": {
        "germ_dimension": 1,
        "tangent_cone_multiplicity": 1,
        "link": ["S^1"],
        "link_h1": ["Z"],
        "euler_class_coefficients": [None],
        "exceptional_projective_dimensions": [0],
        "image_projective_dimension_degree_components": [0, 1, 1],
        "image_components_disjoint": None,
        "c1_on_curve_components": [None],
    },
    "E8bar->B9": {
        "germ_dimension": 2,
        "tangent_cone_multiplicity": 2,
        "link": ["RP^3"],
        "link_h1": ["Z/2"],
        "euler_class_coefficients": [-2],
        "exceptional_projective_dimensions": [1],
        "image_projective_dimension_degree_components": [1, 2, 1],
        "image_components_disjoint": None,
        "c1_on_curve_components": [-2],
    },
    "E8bar->V": {
        "germ_dimension": 3,
        "tangent_cone_multiplicity": 2,
        "link": ["S^5", "S^5"],
        "link_h1": ["0", "0"],
        "euler_class_coefficients": [-1, -1],
        "exceptional_projective_dimensions": [2, 2],
        "image_projective_dimension_degree_components": [2, 2, 2],
        "image_components_disjoint": True,
        "c1_on_curve_components": [None, None],
    },
}
PREDICTED["X-->B9"] = PREDICTED["X+->B9"]
PREDICTED["X+->Va+"] = PREDICTED["E8bar->V"]
PREDICTED["X-->Va-"] = PREDICTED["E8bar->V"]


class Field:
    """Arithmetic of one coefficient field; an element of Q(i) is a pair of Fractions, an element of F_p an int."""

    name = ""
    zero: Elem = None
    one: Elem = None

    def lift(self, real: Fraction, imaginary: Fraction) -> Elem:
        raise NotImplementedError

    def add(self, left: Elem, right: Elem) -> Elem:
        raise NotImplementedError

    def mul(self, left: Elem, right: Elem) -> Elem:
        raise NotImplementedError

    def neg(self, value: Elem) -> Elem:
        raise NotImplementedError

    def inv(self, value: Elem) -> Elem:
        raise NotImplementedError

    def is_zero(self, value: Elem) -> bool:
        return bool(value == self.zero)

    def sub(self, left: Elem, right: Elem) -> Elem:
        return self.add(left, self.neg(right))

    def integer(self, value: int) -> Elem:
        return self.lift(Fraction(value), Fraction(0))

    def render(self, value: Elem) -> str:
        raise NotImplementedError


class GaussianRationals(Field):
    name = "Q(i)"
    zero = (Fraction(0), Fraction(0))
    one = (Fraction(1), Fraction(0))

    def lift(self, real: Fraction, imaginary: Fraction) -> Elem:
        return (Fraction(real), Fraction(imaginary))

    def add(self, left: Elem, right: Elem) -> Elem:
        return (left[0] + right[0], left[1] + right[1])

    def mul(self, left: Elem, right: Elem) -> Elem:
        return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])

    def neg(self, value: Elem) -> Elem:
        return (-value[0], -value[1])

    def inv(self, value: Elem) -> Elem:
        norm = value[0] * value[0] + value[1] * value[1]
        if norm == 0:
            raise ZeroDivisionError("inverse of zero in Q(i)")
        return (value[0] / norm, -value[1] / norm)

    def render(self, value: Elem) -> str:
        real, imaginary = value
        if imaginary == 0:
            return str(real)
        if real == 0:
            return f"{imaginary}*I"
        return f"{real}{'+' if imaginary > 0 else '-'}{abs(imaginary)}*I"


class PrimeField(Field):
    name = f"F_{PRIME}"
    zero = 0
    one = 1

    def __init__(self) -> None:
        if SQRT_MINUS_ONE * SQRT_MINUS_ONE % PRIME != PRIME - 1:
            raise RuntimeError("10754 is not a square root of -1 modulo 32009")

    def _residue(self, value: Fraction) -> int:
        if value.denominator % PRIME == 0:
            raise ZeroDivisionError("a denominator is divisible by the prime")
        return value.numerator * pow(value.denominator, -1, PRIME) % PRIME

    def lift(self, real: Fraction, imaginary: Fraction) -> Elem:
        return (self._residue(Fraction(real)) + SQRT_MINUS_ONE * self._residue(Fraction(imaginary))) % PRIME

    def add(self, left: Elem, right: Elem) -> Elem:
        return (left + right) % PRIME

    def mul(self, left: Elem, right: Elem) -> Elem:
        return left * right % PRIME

    def neg(self, value: Elem) -> Elem:
        return -value % PRIME

    def inv(self, value: Elem) -> Elem:
        if value % PRIME == 0:
            raise ZeroDivisionError("inverse of zero modulo the prime")
        return pow(value, -1, PRIME)

    def render(self, value: Elem) -> str:
        return str(value)


GAUSSIAN = GaussianRationals()
MODULAR = PrimeField()
FIELDS: tuple[Field, ...] = (GAUSSIAN, MODULAR)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------- polynomials


def poly_constant(field: Field, value: Elem) -> Poly:
    return {} if field.is_zero(value) else {(): value}


def poly_add(field: Field, left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for monomial, coefficient in right.items():
        total = field.add(result.get(monomial, field.zero), coefficient)
        if field.is_zero(total):
            result.pop(monomial, None)
        else:
            result[monomial] = total
    return result


def poly_scale(field: Field, poly: Poly, factor: Elem) -> Poly:
    return {} if field.is_zero(factor) else {m: field.mul(c, factor) for m, c in poly.items()}


def _monomial_product(left: Mono, right: Mono) -> Mono:
    exponents: dict[int, int] = dict(left)
    for variable, power in right:
        exponents[variable] = exponents.get(variable, 0) + power
    return tuple(sorted(exponents.items()))


def poly_mul(field: Field, left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            term = {_monomial_product(left_monomial, right_monomial): field.mul(left_coefficient, right_coefficient)}
            result = poly_add(field, result, term)
    return result


def poly_degrees(poly: Poly) -> set[int]:
    return {sum(power for _, power in monomial) for monomial in poly}


def poly_variable(field: Field, index: int) -> Poly:
    return {((index, 1),): field.one}


def _evaluate(field: Field, node: ast.expr, prefix: str) -> Poly:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return poly_constant(field, field.integer(node.value))
    if isinstance(node, ast.Name):
        if node.id == "I":
            return poly_constant(field, field.lift(Fraction(0), Fraction(1)))
        match = re.fullmatch(prefix + r"(\d+)", node.id)
        if match is None:
            raise ValueError(f"unexpected name {node.id!r}")
        return poly_variable(field, int(match.group(1)))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        operand = _evaluate(field, node.operand, prefix)
        return poly_scale(field, operand, field.neg(field.one)) if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.BinOp):
        left = _evaluate(field, node.left, prefix)
        if isinstance(node.op, ast.Pow):
            if not (
                isinstance(node.right, ast.Constant) and isinstance(node.right.value, int) and node.right.value >= 0
            ):
                raise ValueError("an exponent must be a non-negative integer literal")
            result = poly_constant(field, field.one)
            for _ in range(node.right.value):
                result = poly_mul(field, result, left)
            return result
        right = _evaluate(field, node.right, prefix)
        if isinstance(node.op, ast.Add):
            return poly_add(field, left, right)
        if isinstance(node.op, ast.Sub):
            return poly_add(field, left, poly_scale(field, right, field.neg(field.one)))
        if isinstance(node.op, ast.Mult):
            return poly_mul(field, left, right)
        if isinstance(node.op, ast.Div):
            if set(right) - {()} or () not in right:
                raise ValueError("a divisor must be a nonzero constant")
            return poly_scale(field, left, field.inv(right[()]))
    raise ValueError(f"unsupported syntax {ast.dump(node)}")


def parse_polynomial(field: Field, text: str, prefix: str) -> Poly:
    """The polynomial of TEXT in the variables PREFIX1, PREFIX2, ...; I is the imaginary unit."""
    return _evaluate(field, ast.parse(text.replace("^", "**"), mode="eval").body, prefix)


def substitute(field: Field, poly: Poly, images: dict[int, Poly]) -> Poly:
    """POLY with variable k replaced by images[k] (a variable without an image is zero)."""
    result: Poly = {}
    for monomial, coefficient in poly.items():
        term = poly_constant(field, coefficient)
        for variable, power in monomial:
            image = images.get(variable, {})
            for _ in range(power):
                term = poly_mul(field, term, image)
        result = poly_add(field, result, term)
    return result


def linear_row(field: Field, poly: Poly, width: int) -> Vector:
    """The coefficient row of a homogeneous linear form."""
    _require(poly_degrees(poly) <= {1}, "a linear form has a monomial of another degree")
    row = [field.zero] * width
    for monomial, coefficient in poly.items():
        ((variable, _),) = monomial
        row[variable - 1] = coefficient
    return row


def quadric_matrix(field: Field, poly: Poly, width: int) -> list[Vector]:
    """The symmetric matrix S of a homogeneous quadratic form q(x) = x^T S x."""
    _require(poly_degrees(poly) <= {2}, "a quadratic form has a monomial of another degree")
    half = field.inv(field.integer(2))
    matrix = [[field.zero] * width for _ in range(width)]
    for monomial, coefficient in poly.items():
        if len(monomial) == 1:
            ((variable, _),) = monomial
            matrix[variable - 1][variable - 1] = coefficient
        else:
            (first, _), (second, _) = monomial
            matrix[first - 1][second - 1] = field.mul(coefficient, half)
            matrix[second - 1][first - 1] = field.mul(coefficient, half)
    return matrix


# ---------------------------------------------------------------- linear algebra


def rref(field: Field, rows: Sequence[Vector], width: int) -> tuple[list[Vector], list[int]]:
    matrix = [list(row) for row in rows]
    pivots: list[int] = []
    top = 0
    for column in range(width):
        pivot = next((r for r in range(top, len(matrix)) if not field.is_zero(matrix[r][column])), None)
        if pivot is None:
            continue
        matrix[top], matrix[pivot] = matrix[pivot], matrix[top]
        scale = field.inv(matrix[top][column])
        matrix[top] = [field.mul(scale, entry) for entry in matrix[top]]
        for r in range(len(matrix)):
            if r != top and not field.is_zero(matrix[r][column]):
                factor = matrix[r][column]
                matrix[r] = [field.sub(a, field.mul(factor, b)) for a, b in zip(matrix[r], matrix[top], strict=True)]
        pivots.append(column)
        top += 1
    return matrix[:top], pivots


def rank(field: Field, rows: Sequence[Vector], width: int) -> int:
    return len(rref(field, rows, width)[1])


def nullspace(field: Field, rows: Sequence[Vector], width: int) -> list[Vector]:
    """A basis of {x : R x = 0}."""
    reduced, pivots = rref(field, rows, width)
    basis: list[Vector] = []
    for free in (c for c in range(width) if c not in pivots):
        vector = [field.zero] * width
        vector[free] = field.one
        for row, pivot in zip(reduced, pivots, strict=True):
            vector[pivot] = field.neg(row[free])
        basis.append(vector)
    return basis


def apply(field: Field, rows: Sequence[Vector], vector: Vector) -> Vector:
    result = []
    for row in rows:
        total = field.zero
        for entry, coordinate in zip(row, vector, strict=True):
            total = field.add(total, field.mul(entry, coordinate))
        result.append(total)
    return result


def image_rank(field: Field, rows: Sequence[Vector], basis: Sequence[Vector]) -> int:
    """The rank of the linear map ROWS on the span of BASIS."""
    images = [apply(field, rows, vector) for vector in basis]
    return rank(field, images, len(rows)) if images else 0


def integer_vector(field: Field, entries: Sequence[int]) -> Vector:
    return [field.integer(entry) for entry in entries]


# ---------------------------------------------------------------- the retained records


def load(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(result, dict), f"{path.name} is not a JSON object")
    return result


def entry(record: dict[str, Any], incidence: str) -> dict[str, Any]:
    matches = [row for row in record["incidences"] if row["incidence"] == incidence]
    _require(len(matches) == 1, f"{incidence} occurs {len(matches)} times in a record")
    return matches[0]


def gaussian_from_record(field: Field, pair: Sequence[str]) -> Elem:
    return field.lift(Fraction(pair[0]), Fraction(pair[1]))


@dataclass(frozen=True)
class Task:
    """The retained rows of one incidence and the columns they must agree on."""

    incidence: str
    path_supported: dict[str, Any]
    first_order: dict[str, Any]
    holomorphic: dict[str, Any]
    real_limits: dict[str, Any]


def tasks() -> list[Task]:
    records = [load(path) for path in (PATH_SUPPORTED, FIRST_ORDER, HOLOMORPHIC, REAL_LIMITS)]
    return [Task(name, *(entry(record, name) for record in records)) for name in INCIDENCES]


# ---------------------------------------------------------------- matrices and the generated ideal


def transpose(rows: Sequence[Vector]) -> list[Vector]:
    return [list(column) for column in zip(*rows, strict=True)] if rows else []


def matmul(field: Field, left: Sequence[Vector], right: Sequence[Vector]) -> list[Vector]:
    columns = transpose(right)
    return [apply(field, columns, row) for row in left]


def inverse(field: Field, matrix: Sequence[Vector]) -> list[Vector]:
    size = len(matrix)
    augmented = [list(row) + [field.one if i == j else field.zero for j in range(size)] for i, row in enumerate(matrix)]
    reduced, pivots = rref(field, augmented, 2 * size)
    _require(pivots == list(range(size)), "a matrix that must be invertible is singular")
    return [row[size:] for row in reduced]


def linear_map_with_values(
    field: Field, width: int, sources: Sequence[Vector], targets: Sequence[Vector]
) -> list[Vector]:
    """The matrix P with P s_i = t_i on the independent vectors s_i and P = 0 on a complementary coordinate set."""
    basis = [list(vector) for vector in sources]
    values = [list(vector) for vector in targets]
    _require(rank(field, basis, width) == len(basis), "the prescribed sources are dependent")
    for k in range(width):
        unit = [field.one if j == k else field.zero for j in range(width)]
        if rank(field, basis + [unit], width) > len(basis):
            basis.append(unit)
            values.append([field.zero] * width)
    return matmul(field, transpose(values), inverse(field, transpose(basis)))


def monomials_of_degree(variable_count: int, degree: int) -> list[Mono]:
    if degree == 1:
        return [((v, 1),) for v in range(1, variable_count + 1)]
    _require(degree == 2, "only degrees 1 and 2 occur")
    return [
        ((p, 2),) if p == q else ((p, 1), (q, 1))
        for p in range(1, variable_count + 1)
        for q in range(p, variable_count + 1)
    ]


def poly_vector(field: Field, poly: Poly, monomials: Sequence[Mono]) -> Vector:
    return [poly.get(monomial, field.zero) for monomial in monomials]


def poly_power(field: Field, poly: Poly, power: int) -> Poly:
    result = poly_constant(field, field.one)
    for _ in range(power):
        result = poly_mul(field, result, poly)
    return result


def ideal_part(field: Field, generators: Sequence[Poly], degree: int, variable_count: int) -> list[Vector]:
    """Spanning vectors of the degree-DEGREE part of the ideal of generators of degree 1 and 2."""
    monomials = monomials_of_degree(variable_count, degree)
    spanning: list[Poly] = []
    for generator in generators:
        degrees = poly_degrees(generator)
        _require(degrees <= {1, 2}, "an ideal generator has a degree other than 1 or 2")
        if degrees == {degree}:
            spanning.append(generator)
        elif degrees == {1} and degree == 2:
            spanning.extend(poly_mul(field, poly_variable(field, v), generator) for v in range(1, variable_count + 1))
    return [poly_vector(field, poly, monomials) for poly in spanning]


def in_ideal(field: Field, poly: Poly, generators: Sequence[Poly], variable_count: int) -> bool:
    """Whether the homogeneous POLY of degree at most 2 lies in the ideal generated by GENERATORS (degrees 1 and 2)."""
    if not poly:
        return True
    degrees = poly_degrees(poly)
    _require(len(degrees) == 1 and degrees <= {1, 2}, "a polynomial tested for membership is not homogeneous")
    (degree,) = degrees
    monomials = monomials_of_degree(variable_count, degree)
    part = ideal_part(field, generators, degree, variable_count)
    vector = poly_vector(field, poly, monomials)
    width = len(monomials)
    return rank(field, part + [vector], width) == rank(field, part, width)


def ideal_dimension_two(field: Field, generators: Sequence[Poly], variable_count: int) -> int:
    part = ideal_part(field, generators, 2, variable_count)
    return rank(field, part, len(monomials_of_degree(variable_count, 2))) if part else 0


def quadrics_vanishing_on(field: Field, components: Sequence[Sequence[Vector]], width: int) -> int:
    """The dimension of the space of quadratic forms that vanish on every component (linear subspaces, as bases)."""
    monomials = monomials_of_degree(width, 2)
    two = field.integer(2)
    conditions: list[Vector] = []
    for comp in components:
        for a, left in enumerate(comp):
            for right in comp[a:]:
                row: Vector = []
                for monomial in monomials:
                    if len(monomial) == 1:
                        ((p, _),) = monomial
                        row.append(field.mul(two, field.mul(left[p - 1], right[p - 1])))
                    else:
                        (p, _), (q, _) = monomial
                        row.append(
                            field.add(field.mul(left[p - 1], right[q - 1]), field.mul(left[q - 1], right[p - 1]))
                        )
                conditions.append(row)
    return len(monomials) - (rank(field, conditions, len(monomials)) if conditions else 0)


# ---------------------------------------------------------------- the cone and its components


@dataclass
class Cone:
    width: int
    linear: list[Vector]
    generators: list[Poly]
    span: list[Vector]
    restricted: list[Poly]
    components: list[list[Vector]]
    kind: str


def restrict(field: Field, poly: Poly, basis: Sequence[Vector]) -> Poly:
    """POLY on the span of BASIS, in the coordinates s_1, ..., s_k of the basis vectors."""
    images: dict[int, Poly] = {}
    for variable in range(1, len(basis[0]) + 1 if basis else 1):
        image: Poly = {}
        for j, vector in enumerate(basis, start=1):
            image = poly_add(field, image, poly_scale(field, poly_variable(field, j), vector[variable - 1]))
        images[variable] = image
    return substitute(field, poly, images)


def build_cone(field: Field, task: Task, generators: Sequence[str] | None = None) -> Cone:
    """Parse the retained tangent-cone generators; the kind follows from the generators and the witness table.

    A row with a witness basis is a union of linear components; otherwise the cone is the linear space cut out by the
    linear generators when every quadric vanishes on it, and a quadric hypersurface in that space when one does not.
    Certificate 1 decides whether the generators cut out exactly what the kind claims."""
    texts = list(task.first_order["tangent_cone"]["generators"] if generators is None else generators)
    width = task.first_order["slice_dimension"]
    polys = [parse_polynomial(field, text, "t") for text in texts]
    linear = [linear_row(field, p, width) for p in polys if poly_degrees(p) == {1}]
    quadrics = [p for p in polys if poly_degrees(p) == {2}]
    _require(len(linear) + len(quadrics) == len(polys), "a generator is neither linear nor quadratic")
    span = nullspace(field, linear, width)
    restricted = [p for p in (restrict(field, q, span) for q in quadrics) if p]
    if task.incidence in COMPONENT_WITNESSES:
        witnesses = [[integer_vector(field, vector) for vector in comp] for comp in COMPONENT_WITNESSES[task.incidence]]
        return Cone(width, linear, polys, span, restricted, witnesses, "two-components")
    kind = "hypersurface" if restricted else "smooth"
    return Cone(width, linear, polys, span, restricted, [span], kind)


def degree_in_span(field: Field, generators: Sequence[Poly], basis: Sequence[Vector]) -> int:
    """The degree of the zero set of GENERATORS inside the span of BASIS: 1 for the whole space, else the degree of the
    single hypersurface the restricted generators define, and 0 when they define no single hypersurface."""
    restricted = [p for p in (restrict(field, g, basis) for g in generators) if p]
    if not restricted:
        return 1
    base = restricted[0]
    degrees = poly_degrees(base)
    if not all(multiple_of(field, p, base) for p in restricted) or len(degrees) != 1:
        return 0
    return next(iter(degrees))


def exceptional_degrees(field: Field, cone: Cone) -> list[int]:
    """The degree of each component of E in its linear span."""
    return [degree_in_span(field, cone.generators, comp) for comp in cone.components]


def component_projective_dimension(cone: Cone, comp: Sequence[Vector]) -> int:
    """The dimension of E on a component: the cone component has dimension len(comp), minus one for the hypersurface."""
    return len(comp) - (2 if cone.kind == "hypersurface" else 1)


def cone_dimension(cone: Cone) -> int:
    return component_projective_dimension(cone, cone.components[0]) + 1


def decide_cone(field: Field, task: Task, cone: Cone) -> dict[str, Any]:
    """Certificate 1: the generators cut out the recorded components, and the invariants follow from the generators."""
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    dimension, multiplicity, embedding, components = observed
    result: dict[str, Any] = {"kind": cone.kind, "dimension_multiplicity_embedding_components": observed}
    derived_embedding = len(cone.span)
    if cone.kind == "smooth":
        linear_space = not cone.restricted
        derived = [derived_embedding, 1, derived_embedding, 1]
        result["every_quadric_vanishes_on_the_linear_span"] = linear_space
        result["generators_cut_out"] = "the linear span of the linear generators (reduced, multiplicity 1)"
        result["pass"] = linear_space and derived == [dimension, multiplicity, embedding, components]
    elif cone.kind == "hypersurface":
        if not cone.restricted:
            result["quadric_present"] = False
            derived = [derived_embedding, 1, derived_embedding, 1]
            result["pass"] = False
        else:
            base = cone.restricted[0]
            proportional = all(multiple_of(field, other, base) for other in cone.restricted[1:])
            quadratic_rank = rank(field, quadric_matrix(field, base, derived_embedding), derived_embedding)
            morse = proportional and quadratic_rank == derived_embedding and derived_embedding >= 3
            derived = [derived_embedding - 1, 2, derived_embedding, 1]
            result["quadric_present"] = True
            result["quadratic_part_rank"] = quadratic_rank
            result["quadrics_proportional"] = proportional
            result["morse"] = morse
            result["generators_cut_out"] = "an irreducible quadric cone in the linear span (reduced, multiplicity 2)"
            result["pass"] = morse and derived == [dimension, multiplicity, embedding, components]
    else:
        spans = [rank(field, comp, cone.width) for comp in cone.components]
        joint = rank(field, [vector for comp in cone.components for vector in comp], cone.width)
        vanish = all(not restrict(field, g, comp) for comp in cone.components for g in cone.generators)
        linear_rank = rank(field, cone.linear, cone.width) if cone.linear else 0
        linear_ideal_is_the_union_ideal = linear_rank == cone.width - joint
        generated_dimension = ideal_dimension_two(field, cone.generators, cone.width)
        union_dimension = quadrics_vanishing_on(field, cone.components, cone.width)
        meet_only_at_zero = joint == sum(spans)
        generated = vanish and linear_ideal_is_the_union_ideal and generated_dimension == union_dimension
        degrees = exceptional_degrees(field, cone)
        derived = [spans[0], sum(degrees), derived_embedding, len(cone.components)]
        result["component_dimensions"] = spans
        result["components_smooth"] = all(s == len(comp) for s, comp in zip(spans, cone.components, strict=True))
        result["tangent_spaces_joint_rank"] = joint
        result["tangent_spaces_meet_only_at_zero"] = meet_only_at_zero
        result["retained_generators_vanish_on_each_component"] = vanish
        result["linear_generators_span_the_forms_vanishing_on_both"] = linear_ideal_is_the_union_ideal
        result["quadrics_generated_by_the_retained_generators"] = generated_dimension
        result["quadrics_vanishing_on_both_components"] = union_dimension
        result["generators_cut_out_the_union_of_the_components"] = generated
        result["generators_cut_out"] = (
            "the union of the two components: the ideal of two linear spaces that meet only at 0 is generated in "
            "degrees 1 and 2, and the retained generators equal it in those degrees (reduced, multiplicity 2)"
        )
        result["pass"] = bool(
            result["components_smooth"]
            and meet_only_at_zero
            and generated
            and derived == [dimension, multiplicity, embedding, components]
        )
    result["derived_dimension_multiplicity_embedding_components"] = derived
    result["derived_equals_recorded"] = derived == [dimension, multiplicity, embedding, components]
    return result


# ---------------------------------------------------------------- the first-order map


def phi_from_holomorphic(field: Field, task: Task) -> list[Vector]:
    schur = task.holomorphic["c_schur_complement"]
    return [[gaussian_from_record(field, pair) for pair in row] for row in schur["linear_coordinate_matrix"]]


def phi_from_first_order(field: Field, task: Task) -> list[Vector]:
    width = task.first_order["slice_dimension"]
    forms = task.first_order["effective_form"]["coordinate_forms"]
    return [linear_row(field, parse_polynomial(field, text, "t"), width) for text in forms]


def evaluate(field: Field, poly: Poly, point: Vector) -> Elem:
    total = field.zero
    for monomial, coefficient in poly.items():
        term = coefficient
        for variable, power in monomial:
            for _ in range(power):
                term = field.mul(term, point[variable - 1])
        total = field.add(total, term)
    return total


def multiple_of(field: Field, poly: Poly, base: Poly) -> bool:
    """Whether POLY is a scalar multiple of the nonzero polynomial BASE."""
    if not poly:
        return True
    pivot = sorted(base)[0]
    ratio = field.mul(poly.get(pivot, field.zero), field.inv(base[pivot]))
    return poly_add(field, poly, poly_scale(field, base, field.neg(ratio))) == {}


def pullback_images(field: Field, rows: Sequence[Vector], comp: Sequence[Vector]) -> dict[int, Poly]:
    """Each coordinate y_k of phi as a linear form in the coordinates s_1, ... of the component basis."""
    images: dict[int, Poly] = {}
    for k, row in enumerate(rows, start=1):
        image: Poly = {}
        for j, vector in enumerate(comp, start=1):
            value = field.zero
            for coefficient, coordinate in zip(row, vector, strict=True):
                value = field.add(value, field.mul(coefficient, coordinate))
            image = poly_add(field, image, poly_scale(field, poly_variable(field, j), value))
        images[k] = image
    return images


def pulled_back_vanishes(field: Field, cone: Cone, rows: Sequence[Vector], generators: Sequence[str]) -> bool:
    """Every recorded image generator, composed with the coordinate forms, vanishes on E.

    On the hypersurface row the composite is a multiple of the restricted quadric, which cuts E out of its span."""
    outcome = True
    for comp in cone.components:
        images = pullback_images(field, rows, comp)
        for text in generators:
            pulled = substitute(field, parse_polynomial(field, text, "y"), images)
            if cone.kind == "hypersurface":
                outcome = outcome and bool(cone.restricted) and multiple_of(field, pulled, cone.restricted[0])
            else:
                outcome = outcome and not pulled
    return outcome


def coordinate_change(
    field: Field,
    rows_h: Sequence[Vector],
    rows_c: Sequence[Vector],
    generators_h: Sequence[str],
    generators_c: Sequence[str],
) -> dict[str, Any]:
    """The invertible matrix A with rows_h = A rows_c, and the two image ideals compared through it.

    y^h = A y^c as coordinates of the image point. The image ideals agree up to this change of coordinates exactly
    when every 2i generator, written in y^c, lies in the 2c ideal and every 2c generator, written in y^h, lies in the
    2i ideal (both ideals are generated in degrees 1 and 2, which the membership test covers)."""
    count = len(rows_c)
    width = len(rows_c[0])
    result: dict[str, Any] = {"coordinate_count": count}
    independent = len(rows_h) == count and rank(field, rows_c, width) == count and rank(field, rows_h, width) == count
    result["both_coordinate_systems_independent"] = independent
    if not independent:
        result["pass"] = False
        return result
    pivots = rref(field, rows_c, width)[1]
    columns_c = [[row[j] for j in pivots] for row in rows_c]
    columns_h = [[row[j] for j in pivots] for row in rows_h]
    change = matmul(field, columns_h, inverse(field, columns_c))
    consistent = matmul(field, change, rows_c) == [list(row) for row in rows_h]
    invertible = rank(field, change, count) == count
    result["rows_h_equal_A_times_rows_c"] = consistent
    result["A_invertible"] = invertible
    if not (consistent and invertible):
        result["pass"] = False
        return result
    back = inverse(field, change)
    parsed_h = [parse_polynomial(field, text, "y") for text in generators_h]
    parsed_c = [parse_polynomial(field, text, "y") for text in generators_c]
    to_c: dict[int, Poly] = {}
    to_h: dict[int, Poly] = {}
    for k in range(count):
        to_c[k + 1] = {}
        to_h[k + 1] = {}
        for j in range(count):
            to_c[k + 1] = poly_add(field, to_c[k + 1], poly_scale(field, poly_variable(field, j + 1), change[k][j]))
            to_h[k + 1] = poly_add(field, to_h[k + 1], poly_scale(field, poly_variable(field, j + 1), back[k][j]))
    h_in_c = all(in_ideal(field, substitute(field, g, to_c), parsed_c, count) for g in parsed_h)
    c_in_h = all(in_ideal(field, substitute(field, g, to_h), parsed_h, count) for g in parsed_c)
    result["2i_generators_lie_in_the_2c_ideal"] = h_in_c
    result["2c_generators_lie_in_the_2i_ideal"] = c_in_h
    result["pass"] = h_in_c and c_in_h
    return result


def decide_map(
    field: Field,
    task: Task,
    cone: Cone,
    rows_h: Sequence[Vector],
    rows_c: Sequence[Vector],
    generators_h: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Certificate 2."""
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    dimension = cone_dimension(cone)
    spans = [len(comp) for comp in cone.components]
    union = [vector for comp in cone.components for vector in comp]
    committed = task.first_order["first_order_image"]
    blowup = task.holomorphic["explicit_blowup"]
    degrees = exceptional_degrees(field, cone)
    image_generators_c = committed["generators_in_independent_form_coordinates"]
    image_generators_h = blowup["rational"]["image_generators"] if generators_h is None else list(generators_h)
    result: dict[str, Any] = {"component_span_dimensions": spans}
    for label, rows, generators in (
        ("holomorphic_2i", rows_h, image_generators_h),
        ("first_order_2c", rows_c, image_generators_c),
    ):
        per = [image_rank(field, rows, comp) for comp in cone.components]
        joint = image_rank(field, rows, union)
        result[label] = {
            "coordinate_count": len(rows),
            "rank_on_each_component_span": per,
            "injective_on_each_component": per == spans,
            "rank_on_the_sum_of_components": joint,
            "images_meet_only_at_zero": joint == sum(spans),
            "pulled_back_image_generators_vanish_on_E": pulled_back_vanishes(field, cone, rows, generators),
        }
    result["coordinate_change_2i_to_2c"] = coordinate_change(
        field, rows_h, rows_c, image_generators_h, image_generators_c
    )
    image = [dimension - 1, sum(degrees), len(cone.components)]
    triple_2c = [committed["projective_dimension"], committed["degree"], committed["component_count"]]
    triples_2i = [
        [
            blowup[part]["image_projective_dimension"],
            blowup[part]["image_degree"],
            blowup[part]["image_component_count"],
        ]
        for part in ("rational", "modular")
    ]
    result["image_projective_dimension_degree_components"] = image
    result["image_2i_rational_and_modular"] = triples_2i
    result["image_2c"] = triple_2c
    result["fiber_2l"] = task.real_limits["fiber_projective_dimension_degree_components"]
    result["image_matches_2i"] = all(image == triple for triple in triples_2i)
    result["image_matches_2c"] = image == triple_2c
    result["image_matches_2l"] = image == result["fiber_2l"]
    result["multiplicity_equals_degree_sum"] = (
        observed[1] == sum(degrees) == task.first_order["tangent_cone"]["multiplicity"]
    )
    result["pass"] = bool(
        all(
            result[label]["injective_on_each_component"]
            and result[label]["images_meet_only_at_zero"]
            and result[label]["pulled_back_image_generators_vanish_on_E"]
            for label in ("holomorphic_2i", "first_order_2c")
        )
        and result["coordinate_change_2i_to_2c"]["pass"]
        and result["image_matches_2i"]
        and result["image_matches_2c"]
        and result["image_matches_2l"]
        and result["multiplicity_equals_degree_sum"]
    )
    return result


def retained_direction(field: Field, task: Task) -> Vector:
    coordinates = task.first_order["canonical_paths"][0]["normal_coordinates"]
    return [field.lift(Fraction(text), Fraction(0)) for text in coordinates]


def cone_point(field: Field, task: Task, cone: Cone) -> Vector:
    """A nonzero point of the tangent cone: the retained path direction on the hypersurface, else a component vector."""
    return retained_direction(field, task) if cone.kind == "hypersurface" else cone.components[0][0]


def on_cone(field: Field, cone: Cone, point: Vector) -> bool:
    return all(field.is_zero(evaluate(field, g, point)) for g in cone.generators)


PFAFFIAN_UNDECIDED = (
    "the rank-four Pfaffians need the full skew Schur matrix; the retained records hold only a basis of its entry "
    "forms (the 2c record 7 of 15, the 2i record 7 of 21 coordinates), so the vanishing is not recomputable here"
)


def decide_nullity(
    field: Field, task: Task, cone: Cone, rows_h: Sequence[Vector], rows_c: Sequence[Vector]
) -> dict[str, Any]:
    """Certificate 0: what the retained inputs decide in this field, and what the exact 2i and 2c runs carry."""
    schur = task.holomorphic["c_schur_complement"]
    blowup = task.holomorphic["explicit_blowup"]
    pivot = gaussian_from_record(field, schur["pivot_pfaffian_at_origin"])
    kernel = schur["boundary_kernel_dimension"]
    bordered_kernel = schur["boundary_c_rank"] + kernel + 1 - schur["boundary_bordered_rank"]
    point = cone_point(field, task, cone)
    injective = all(image_rank(field, rows, comp) == len(comp) for rows in (rows_h, rows_c) for comp in cone.components)
    nonzero_at_point = all(any(not field.is_zero(x) for x in apply(field, rows, point)) for rows in (rows_h, rows_c))
    nonempty = [
        any(not field.is_zero(vector[k]) for comp in cone.components for vector in comp) for k in range(cone.width)
    ]
    recorded_nonempty = [chart["nonempty"] for chart in blowup["rational"]["charts"]]
    degeneracy_empty = task.first_order["degeneracy_locus"]["projective_dimension"] == -1
    rank_bound = 2 if injective and nonzero_at_point else 0
    decided = {
        "pivot_pfaffian_is_a_unit": not field.is_zero(pivot),
        "bordered_kernel_dimension_at_the_boundary": bordered_kernel,
        "schur_coordinate_count_matches_kernel_dimension": schur["coordinate_count"] == kernel * (kernel - 1) // 2,
        "cone_point_lies_on_the_tangent_cone": on_cone(field, cone, point),
        "first_order_form_nonzero_at_the_cone_point": nonzero_at_point,
        "phi_has_no_zero_on_E": injective,
        "exceptional_charts_nonempty": nonempty,
        "exceptional_charts_nonempty_match_2i": nonempty == recorded_nonempty,
        "exceptional_charts_base_free": injective,
        "degeneracy_locus_empty_matches_2c": degeneracy_empty == injective,
        "schur_form_rank_lower_bound": rank_bound,
        "real_nullity_upper_bound": 2 * (bordered_kernel - rank_bound),
    }
    decided["pass"] = bool(
        decided["pivot_pfaffian_is_a_unit"]
        and decided["schur_coordinate_count_matches_kernel_dimension"]
        and decided["cone_point_lies_on_the_tangent_cone"]
        and nonzero_at_point
        and injective
        and decided["exceptional_charts_nonempty_match_2i"]
        and decided["degeneracy_locus_empty_matches_2c"]
        and decided["real_nullity_upper_bound"] == 8
    )
    specific: dict[str, Any]
    if field.name == GAUSSIAN.name:
        flags = {
            "2i_rational_run": bool(blowup["rational"]["rank_four_pfaffians_vanish"]),
            "2c_effective_form_run": bool(
                task.first_order["effective_form"]["rank_four_pfaffians_vanish_on_tangent_cone"]
            ),
        }
        carried = all(flags.values())
        exact_rank = 2 if carried and rank_bound == 2 else None
        specific = {
            "rank_four_pfaffians_vanish_carried_from_retained_exact_runs": flags,
            "recomputed_here": False,
            "reason": PFAFFIAN_UNDECIDED,
            "schur_form_rank": exact_rank,
            "real_nullity_off_the_basepoint": None if exact_rank is None else 2 * (bordered_kernel - exact_rank),
            "inferred": (
                "the form is its first-order part plus O(|z|^2); the first-order part has a lower bound on the "
                "unit sphere of the cone, so the form stays nonzero near E and its rank is exactly the first-order "
                "rank wherever the Pfaffian ideal contains the higher terms"
            ),
        }
        specific["pass"] = carried and specific["real_nullity_off_the_basepoint"] == 8
    else:
        specific = {
            "rank_four_pfaffians_vanish": None,
            "not_decided": PFAFFIAN_UNDECIDED + "; the 2i modular run is modulo 32003, not " + str(PRIME),
            "schur_form_rank": None,
            "real_nullity_off_the_basepoint": None,
            "pass": None,
        }
    return {
        "decided_in_this_field": decided,
        "field_specific": specific,
        "pass": bool(decided["pass"] and (specific["pass"] is not False)),
    }


# ---------------------------------------------------------------- topology


def gysin_h1(base_dimension: int, coefficient: int | None) -> tuple[str, str]:
    """H_1 and the name of the circle bundle over P^n with Euler class COEFFICIENT times the hyperplane generator.

    The Gysin sequence of the bundle gives H^1 = ker(cup e on H^0) and H^2 = coker(cup e : H^0 -> H^2(P^n)); H_1 is
    the free part of H^1 plus the torsion of H^2."""
    if base_dimension == 0 or coefficient is None:
        return "Z", "S^1"
    size = abs(coefficient)
    _require(size > 0, "a zero Euler class does not occur among the eight incidences")
    if size == 1:
        return "0", f"S^{2 * base_dimension + 1}"
    name = "RP^3" if (base_dimension, size) == (1, 2) else f"L({size};1) of dimension {2 * base_dimension + 1}"
    return f"Z/{size}", name


def decide_topology(
    field: Field, task: Task, cone: Cone, map_result: dict[str, Any], rows_h: Sequence[Vector], plucker_power: int = 1
) -> dict[str, Any]:
    """Certificate 3 and the independent topology checks.

    The Plucker coordinates of 2i are the rows of rows_h; their pullback to a component is a family of forms of one
    degree, and phi^*H is that degree times h once the family has no common zero on the component. The class
    c_1(S|Lambda) = -H therefore pulls back to minus that degree times h, and its value on the generator of H_2 of the
    component is minus the degree times the degree of that generator curve in the span. PLUCKER_POWER replaces each
    coordinate by its power (a control)."""
    degrees = exceptional_degrees(field, cone)
    recorded_degree = task.holomorphic["explicit_blowup"]["rational"]["image_degree"]
    components = []
    for index, comp in enumerate(cone.components):
        projective = component_projective_dimension(cone, comp)
        forms = [poly_power(field, p, plucker_power) for p in pullback_images(field, rows_h, comp).values()]
        form_degrees: set[int] = set().union(*(poly_degrees(p) for p in forms)) if forms else set()
        no_base_point = map_result["holomorphic_2i"]["rank_on_each_component_span"][index] == len(comp)
        coefficient = next(iter(form_degrees)) if no_base_point and len(form_degrees) == 1 else None
        euler: int | None = None
        c1_on_generator: int | None = None
        generator_degree: int | None = None
        if projective >= 1:
            generator_degree = degrees[index] if projective == 1 else degree_in_span(field, cone.generators, comp[:2])
            euler = -generator_degree
            c1_on_generator = None if coefficient is None else -coefficient * generator_degree
        h1, link = gysin_h1(projective, euler)
        curve = projective == 1
        recorded_check = (
            None
            if not (curve and len(degrees) == 1 and c1_on_generator is not None)
            else -recorded_degree == c1_on_generator
        )
        isomorphism = map_result["holomorphic_2i"]["rank_on_each_component_span"][index] == len(comp) and map_result[
            "first_order_2c"
        ]["rank_on_each_component_span"][index] == len(comp)
        euler_comparison = None if projective == 0 else (c1_on_generator is not None and c1_on_generator == euler)
        components.append(
            {
                "exceptional_projective_dimension": projective,
                "degree_of_E_in_its_span": degrees[index],
                "degree_of_the_generator_curve_of_H2": generator_degree,
                "euler_class_coefficient": euler,
                "link": link,
                "h1_of_link": h1,
                "phi_on_h2_is_an_isomorphism": isomorphism,
                "plucker_forms_degree": coefficient,
                "pluecker_pullback_of_the_hyperplane_class_is_h": coefficient == 1,
                "c1_of_S_on_the_component": None if projective == 0 else f"-{coefficient}*h",
                "c1_of_S_evaluated_on_the_generator_of_H2": c1_on_generator,
                "euler_class_equals_c1_on_the_generator": euler_comparison,
                "c1_of_S_evaluated_on_the_curve": c1_on_generator if curve and len(degrees) == 1 else None,
                "euler_class_equals_minus_pluecker_degree": recorded_check,
                "h2_of_E_is_zero": projective == 0,
            }
        )
    passed = all(
        c["phi_on_h2_is_an_isomorphism"]
        and c["pluecker_pullback_of_the_hyperplane_class_is_h"]
        and (c["h2_of_E_is_zero"] or c["euler_class_equals_c1_on_the_generator"] is True)
        and c["euler_class_equals_minus_pluecker_degree"] is not False
        for c in components
    )
    return {"components": components, "pass": bool(passed)}


# ---------------------------------------------------------------- the incidence driver


def check_records_agree(task: Task) -> dict[str, bool]:
    tangent_2b = task.path_supported["germ"]["tangent_generators"]
    tangent_2c = task.first_order["tangent_cone"]["generators"]
    tangent_2i = task.holomorphic["tangent_cone"]["generators"]
    observed_2b = task.path_supported["germ"]["observed_dimension_multiplicity_embedding_components"]
    observed_2c = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    cone_2c = task.first_order["tangent_cone"]
    return {
        "tangent_generators_equal_in_2b_2c_2i": tangent_2b == tangent_2c == tangent_2i,
        "germ_invariants_equal_in_2b_2c": observed_2b == observed_2c,
        "cone_summary_matches_germ": [cone_2c["dimension"], cone_2c["multiplicity"], cone_2c["component_count"]]
        == [observed_2c[0], observed_2c[1], observed_2c[3]],
        "slice_columns_equal_in_2b_2c_2i": task.path_supported["slice_columns_zero_based"]
        == task.first_order["slice_columns_zero_based"]
        == task.holomorphic["slice_columns_zero_based"],
        "source_and_boundary_equal": task.path_supported["source_orbit"] == task.first_order["source_orbit"]
        and task.path_supported["boundary_orbit"] == task.first_order["boundary_orbit"],
    }


def analyze(
    field: Field,
    task: Task,
    *,
    cone: Cone | None = None,
    rows_h: Sequence[Vector] | None = None,
    rows_c: Sequence[Vector] | None = None,
    generators_h: Sequence[str] | None = None,
    plucker_power: int = 1,
) -> dict[str, Any]:
    cone = build_cone(field, task) if cone is None else cone
    rows_h = phi_from_holomorphic(field, task) if rows_h is None else rows_h
    rows_c = phi_from_first_order(field, task) if rows_c is None else rows_c
    _require(all(len(row) == cone.width for row in list(rows_h) + list(rows_c)), "a phi row does not span the slice")
    conical = decide_cone(field, task, cone)
    mapped = decide_map(field, task, cone, rows_h, rows_c, generators_h)
    return {
        "certificate_0_constant_nullity": decide_nullity(field, task, cone, rows_h, rows_c),
        "certificate_1_conical_structure": conical,
        "certificate_2_linear_injective_phi": mapped,
        "certificate_3_homotopy_data": decide_topology(field, task, cone, mapped, rows_h, plucker_power),
    }


def certificates_pass(certificates: dict[str, Any]) -> bool:
    return all(certificate["pass"] for certificate in certificates.values())


def comparable(certificates: dict[str, Any]) -> dict[str, Any]:
    """The certificates without the entries that only one field decides."""
    shared = dict(certificates)
    nullity = dict(shared["certificate_0_constant_nullity"])
    nullity.pop("field_specific")
    nullity.pop("pass")
    shared["certificate_0_constant_nullity"] = nullity
    return shared


# ---------------------------------------------------------------- mutations


def altered(task: Task, edit: Callable[[Task], None]) -> Task:
    copy_ = Task(
        task.incidence,
        copy.deepcopy(task.path_supported),
        copy.deepcopy(task.first_order),
        copy.deepcopy(task.holomorphic),
        copy.deepcopy(task.real_limits),
    )
    edit(copy_)
    return copy_


def lower_rank_of_phi(field: Field, task: Task, component: int) -> dict[str, Any]:
    """Mutation: remove the action of phi on one vector k of a named component and require k as a kernel point."""
    cone = build_cone(field, task)
    rows = phi_from_holomorphic(field, task)
    comp = cone.components[component]
    point = cone_point(field, task, cone) if cone.kind == "hypersurface" else comp[0]
    column = next(c for c, value in enumerate(point) if not field.is_zero(value))
    shift = apply(field, rows, point)
    scale = field.inv(point[column])
    mutated = [list(row) for row in rows]
    for r, row in enumerate(mutated):
        row[column] = field.sub(row[column], field.mul(shift[r], scale))
    images = [apply(field, mutated, vector) for vector in comp]
    transposed = [[images[j][r] for j in range(len(comp))] for r in range(len(rows))]
    coefficients = nullspace(field, transposed, len(comp))
    points = []
    for combination in coefficients:
        vector = [field.zero] * cone.width
        for weight, base in zip(combination, comp, strict=True):
            vector = [field.add(a, field.mul(weight, b)) for a, b in zip(vector, base, strict=True)]
        points.append(vector)
    certificates = analyze(field, task, cone=cone, rows_h=mutated)
    topology = certificates["certificate_3_homotopy_data"]["components"]
    pattern = [c["phi_on_h2_is_an_isomorphism"] for c in topology]
    expected = [index != component for index in range(len(topology))]
    return {
        "incidence": task.incidence,
        "mutation": "lower_the_rank_of_phi_on_a_component",
        "component": component,
        "baseline_rank_on_component": image_rank(field, rows, comp),
        "mutated_rank_on_component": image_rank(field, mutated, comp),
        "span_dimension": len(comp),
        "kernel_dimension": len(points),
        "projective_kernel_point": [field.render(x) for x in point],
        "kernel_point_on_the_cone": on_cone(field, cone, point),
        "mutated_phi_kills_the_point": all(field.is_zero(x) for x in apply(field, mutated, point)),
        "all_kernel_points_on_the_cone": all(on_cone(field, cone, p) for p in points),
        "certificate_2_passes_on_the_mutated_phi": certificates["certificate_2_linear_injective_phi"]["pass"],
        "certificate_0_phi_has_no_zero_on_E": certificates["certificate_0_constant_nullity"]["decided_in_this_field"][
            "phi_has_no_zero_on_E"
        ],
        "phi_on_h2_is_an_isomorphism_per_component": pattern,
        "detected": bool(
            points
            and on_cone(field, cone, point)
            and not certificates["certificate_2_linear_injective_phi"]["pass"]
            and not certificates["certificate_0_constant_nullity"]["decided_in_this_field"]["phi_has_no_zero_on_E"]
            and pattern == expected
        ),
    }


def rank_two_quadratic_part(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: drop the t5^2 term of the E8-bar to B9 quadric, a form of rank 2, which must fail the Morse test."""
    texts = list(task.first_order["tangent_cone"]["generators"])
    index = next(i for i, text in enumerate(texts) if "^2" in text)
    mutated = texts[index].replace("-t5^2", "")
    _require(mutated != texts[index], "the mutation changed no term")
    texts[index] = mutated
    cone = build_cone(field, task, texts)
    verdict = decide_cone(field, task, cone)
    return {
        "incidence": task.incidence,
        "mutation": "rank_two_quadratic_part",
        "mutated_generator": mutated,
        "quadratic_part_rank": verdict["quadratic_part_rank"],
        "morse_certificate_passes": verdict["pass"],
        "detected": not verdict["pass"] and verdict["quadratic_part_rank"] == 2,
    }


def flip_a_table_entry(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: the table predicts a germ dimension one too large; the row must fail on the prediction alone."""
    table = dict(PREDICTED[task.incidence])
    table["germ_dimension"] = table["germ_dimension"] + 1
    certificates = analyze(field, task)
    predictions = predict(task, certificates, table)
    return {
        "incidence": task.incidence,
        "mutation": "wrong_value_in_the_prediction_table",
        "certificates_pass": certificates_pass(certificates),
        "predictions_hold": all(p["pass"] for p in predictions),
        "detected": certificates_pass(certificates) and not all(p["pass"] for p in predictions),
    }


def overlap_the_images(field: Field, task: Task, label: str) -> dict[str, Any] | None:
    """Mutation: compose phi with the map that sends the second component onto the first; the two image planes meet."""
    cone = build_cone(field, task)
    if len(cone.components) != 2:
        return None
    first, second = cone.components
    projection = linear_map_with_values(field, cone.width, first + second, first + first)
    rows = phi_from_holomorphic(field, task) if label == "holomorphic_2i" else phi_from_first_order(field, task)
    mutated = matmul(field, rows, projection)
    certificates = analyze(
        field,
        task,
        cone=cone,
        rows_h=mutated if label == "holomorphic_2i" else None,
        rows_c=mutated if label == "first_order_2c" else None,
    )
    mapped = certificates["certificate_2_linear_injective_phi"][label]
    return {
        "incidence": task.incidence,
        "mutation": f"image_planes_meet_{label}",
        "injective_on_each_component": mapped["injective_on_each_component"],
        "images_meet_only_at_zero": mapped["images_meet_only_at_zero"],
        "rank_on_the_sum_of_components": mapped["rank_on_the_sum_of_components"],
        "detected": bool(
            mapped["injective_on_each_component"]
            and not mapped["images_meet_only_at_zero"]
            and not certificates["certificate_2_linear_injective_phi"]["pass"]
        ),
    }


def first_generator_variable(generators: Sequence[str]) -> int:
    match = re.fullmatch(r"y(\d+)", generators[0])
    if match is None:
        raise RuntimeError("the first recorded image generator is not a coordinate")
    return int(match.group(1)) - 1


def perturb_a_phi_row(field: Field, task: Task, label: str) -> dict[str, Any]:
    """Mutation: add a coordinate that does not vanish on E to the coordinate the first image generator zeroes."""
    cone = build_cone(field, task)
    rows = phi_from_holomorphic(field, task) if label == "holomorphic_2i" else phi_from_first_order(field, task)
    generators = (
        task.holomorphic["explicit_blowup"]["rational"]["image_generators"]
        if label == "holomorphic_2i"
        else task.first_order["first_order_image"]["generators_in_independent_form_coordinates"]
    )
    target = first_generator_variable(generators)
    source = next(k for k, row in enumerate(rows) if any(image_rank(field, [row], comp) for comp in cone.components))
    mutated = [list(row) for row in rows]
    mutated[target] = [field.add(a, b) for a, b in zip(rows[target], rows[source], strict=True)]
    certificates = analyze(
        field,
        task,
        cone=cone,
        rows_h=mutated if label == "holomorphic_2i" else None,
        rows_c=mutated if label == "first_order_2c" else None,
    )
    mapped = certificates["certificate_2_linear_injective_phi"]
    return {
        "incidence": task.incidence,
        "mutation": f"perturb_a_coordinate_form_{label}",
        "perturbed_coordinate_and_added_coordinate": [target + 1, source + 1],
        "image_generators_vanish_on_E": mapped[label]["pulled_back_image_generators_vanish_on_E"],
        "detected": bool(not mapped[label]["pulled_back_image_generators_vanish_on_E"] and not mapped["pass"]),
    }


def drop_an_image_generator(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: delete the first 2i image generator; the rest vanish on E but no longer cut out its image."""
    kept = list(task.holomorphic["explicit_blowup"]["rational"]["image_generators"])[1:]
    certificates = analyze(field, task, generators_h=kept)
    mapped = certificates["certificate_2_linear_injective_phi"]
    return {
        "incidence": task.incidence,
        "mutation": "delete_an_image_generator",
        "image_generators_vanish_on_E": mapped["holomorphic_2i"]["pulled_back_image_generators_vanish_on_E"],
        "coordinate_change_passes": mapped["coordinate_change_2i_to_2c"]["pass"],
        "detected": bool(
            mapped["holomorphic_2i"]["pulled_back_image_generators_vanish_on_E"]
            and not mapped["coordinate_change_2i_to_2c"]["pass"]
            and not mapped["pass"]
        ),
    }


def delete_cone_generators(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: delete every quadric of the tangent cone, or the last linear generator when it has no quadric."""
    texts = list(task.first_order["tangent_cone"]["generators"])
    parsed = [parse_polynomial(field, text, "t") for text in texts]
    kept = [text for text, poly in zip(texts, parsed, strict=True) if poly_degrees(poly) == {1}]
    if len(kept) == len(texts):
        kept = kept[:-1]
    verdict = decide_cone(field, task, build_cone(field, task, kept))
    return {
        "incidence": task.incidence,
        "mutation": "delete_tangent_cone_generators",
        "generators_deleted": len(texts) - len(kept),
        "cone_kind_of_the_remaining_generators": verdict["kind"],
        "certificate_1_passes": verdict["pass"],
        "detected": not verdict["pass"],
    }


def square_the_plucker_coordinates(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: replace each Plucker coordinate by its square, so phi^*H = 2h and c_1 = -2h."""
    certificates = analyze(field, task, plucker_power=2)
    components = certificates["certificate_3_homotopy_data"]["components"]
    return {
        "incidence": task.incidence,
        "mutation": "square_the_plucker_coordinates",
        "plucker_forms_degree": [c["plucker_forms_degree"] for c in components],
        "c1_on_the_generator": [c["c1_of_S_evaluated_on_the_generator_of_H2"] for c in components],
        "euler_class": [c["euler_class_coefficient"] for c in components],
        "detected": bool(
            not certificates["certificate_3_homotopy_data"]["pass"]
            and all(not c["pluecker_pullback_of_the_hyperplane_class_is_h"] for c in components)
            and all(
                c["euler_class_equals_c1_on_the_generator"] is False
                for c in components
                if c["exceptional_projective_dimension"] >= 1
            )
        ),
    }


def tamper_the_multiplicity(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: the retained germ and cone records state multiplicity one larger than the generators give."""

    def edit(copy_: Task) -> None:
        copy_.first_order["germ"]["observed_dimension_multiplicity_embedding_components"][1] += 1
        copy_.first_order["tangent_cone"]["multiplicity"] += 1

    certificates = analyze(field, altered(task, edit))
    return {
        "incidence": task.incidence,
        "mutation": "tamper_the_recorded_multiplicity",
        "certificate_1_passes": certificates["certificate_1_conical_structure"]["pass"],
        "certificate_2_passes": certificates["certificate_2_linear_injective_phi"]["pass"],
        "detected": bool(
            not certificates["certificate_1_conical_structure"]["pass"]
            and not certificates["certificate_2_linear_injective_phi"]["pass"]
        ),
    }


def tamper_the_bordered_rank(field: Field, task: Task) -> dict[str, Any]:
    """Mutation: the recorded bordered rank is one lower, so the bordered kernel and the nullity bound change."""

    def edit(copy_: Task) -> None:
        copy_.holomorphic["c_schur_complement"]["boundary_bordered_rank"] -= 1

    certificates = analyze(field, altered(task, edit))
    decided = certificates["certificate_0_constant_nullity"]["decided_in_this_field"]
    return {
        "incidence": task.incidence,
        "mutation": "tamper_the_recorded_bordered_rank",
        "real_nullity_upper_bound": decided["real_nullity_upper_bound"],
        "detected": bool(
            not certificates["certificate_0_constant_nullity"]["pass"] and decided["real_nullity_upper_bound"] != 8
        ),
    }


def tamper_the_pfaffian_flag(field: Field, task: Task) -> dict[str, Any]:
    """Mutation (Q(i)): the carried rank-four Pfaffian flag of the 2i rational run reads false."""

    def edit(copy_: Task) -> None:
        copy_.holomorphic["explicit_blowup"]["rational"]["rank_four_pfaffians_vanish"] = False

    certificates = analyze(field, altered(task, edit))
    nullity = certificates["certificate_0_constant_nullity"]
    return {
        "incidence": task.incidence,
        "mutation": "tamper_the_carried_pfaffian_flag",
        "decided_part_passes": nullity["decided_in_this_field"]["pass"],
        "detected": bool(nullity["decided_in_this_field"]["pass"] and not nullity["pass"]),
    }


def pivot_vanishing_modulo_the_prime(field: Field, task: Task) -> dict[str, Any]:
    """Mutation (F_32009): the recorded pivot Pfaffian is 32009, a unit in Q(i) and zero modulo the prime."""

    def edit(copy_: Task) -> None:
        copy_.holomorphic["c_schur_complement"]["pivot_pfaffian_at_origin"] = [str(PRIME), "0"]

    mutated = altered(task, edit)
    certificates = analyze(field, mutated)
    unit_in_gaussian = not GAUSSIAN.is_zero(
        gaussian_from_record(GAUSSIAN, mutated.holomorphic["c_schur_complement"]["pivot_pfaffian_at_origin"])
    )
    return {
        "incidence": task.incidence,
        "mutation": "pivot_pfaffian_divisible_by_the_prime",
        "pivot_is_a_unit_in_Q(i)": unit_in_gaussian,
        "detected": bool(
            unit_in_gaussian
            and not certificates["certificate_0_constant_nullity"]["decided_in_this_field"]["pivot_pfaffian_is_a_unit"]
            and not certificates["certificate_0_constant_nullity"]["pass"]
        ),
    }


def certify(task: Task, table: dict[str, Any] | None = None) -> dict[str, Any]:
    """Every certificate and control of one incidence, in both fields."""
    per_field = {field.name: analyze(field, task) for field in FIELDS}
    gaussian, modular = per_field[GAUSSIAN.name], per_field[MODULAR.name]
    agree = comparable(gaussian) == comparable(modular)
    mutations: list[dict[str, Any]] = []
    for field in FIELDS:
        cone = build_cone(field, task)
        found: list[dict[str, Any] | None] = [
            *(lower_rank_of_phi(field, task, component) for component in range(len(cone.components))),
            rank_two_quadratic_part(field, task) if task.incidence == "E8bar->B9" else None,
            flip_a_table_entry(field, task),
            overlap_the_images(field, task, "holomorphic_2i"),
            overlap_the_images(field, task, "first_order_2c"),
            perturb_a_phi_row(field, task, "holomorphic_2i"),
            perturb_a_phi_row(field, task, "first_order_2c"),
            drop_an_image_generator(field, task),
            delete_cone_generators(field, task),
            square_the_plucker_coordinates(field, task),
            tamper_the_multiplicity(field, task),
            tamper_the_bordered_rank(field, task),
            tamper_the_pfaffian_flag(field, task) if field.name == GAUSSIAN.name else None,
            pivot_vanishing_modulo_the_prime(field, task) if field.name == MODULAR.name else None,
        ]
        mutations.extend({"field": field.name, **item} for item in found if item is not None)
    certificates = dict(gaussian)
    predictions = predict(task, certificates, table)
    records_agree = check_records_agree(task)
    return {
        "incidence": task.incidence,
        "source_orbit": task.first_order["source_orbit"],
        "boundary_orbit": task.first_order["boundary_orbit"],
        "retained_rows_agree": records_agree,
        "certificates": certificates,
        "modular_certificate_0_field_specific": modular["certificate_0_constant_nullity"]["field_specific"],
        "modular_certificates_equal_gaussian_where_both_decide": agree,
        "predictions": predictions,
        "mutation_controls": mutations,
        "pass": bool(
            agree
            and certificates_pass(gaussian)
            and certificates_pass(modular)
            and all(p["pass"] for p in predictions)
            and all(m["detected"] for m in mutations)
            and all(records_agree.values())
        ),
    }


def predict(task: Task, certificates: dict[str, Any], table: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Each value of the section's table against the computed value."""
    table = PREDICTED[task.incidence] if table is None else table
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    topology = certificates["certificate_3_homotopy_data"]["components"]
    mapped = certificates["certificate_2_linear_injective_phi"]
    computed = {
        "germ_dimension": observed[0],
        "tangent_cone_multiplicity": observed[1],
        "link": [c["link"] for c in topology],
        "link_h1": [c["h1_of_link"] for c in topology],
        "euler_class_coefficients": [c["euler_class_coefficient"] for c in topology],
        "exceptional_projective_dimensions": [c["exceptional_projective_dimension"] for c in topology],
        "image_projective_dimension_degree_components": mapped["image_projective_dimension_degree_components"],
        "image_components_disjoint": (
            mapped["holomorphic_2i"]["images_meet_only_at_zero"] if len(topology) == 2 else None
        ),
        "c1_on_curve_components": [c["c1_of_S_evaluated_on_the_curve"] for c in topology],
    }
    rows = []
    for name, predicted in table.items():
        value = computed[name]
        if _is_null(predicted):
            rows.append(
                {"name": name, "applicable": False, "predicted": predicted, "computed": value, "pass": _is_null(value)}
            )
        else:
            rows.append(
                {
                    "name": name,
                    "applicable": True,
                    "predicted": predicted,
                    "computed": value,
                    "pass": predicted == value,
                }
            )
    return rows


def _is_null(value: Any) -> bool:
    return value is None or (isinstance(value, list) and all(item is None for item in value))


# ---------------------------------------------------------------- the record


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble(incidences: list[dict[str, Any]]) -> dict[str, Any]:
    controls = [
        {
            "incidence": row["incidence"],
            "field": mutation["field"],
            "mutation": mutation["mutation"],
            "detected": mutation["detected"],
        }
        for row in incidences
        for mutation in row["mutation_controls"]
    ]
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "fields": [GAUSSIAN.name, MODULAR.name],
        "prime": PRIME,
        "square_root_of_minus_one": SQRT_MINUS_ONE,
        "inputs": {
            path.name: sha256(path) for path in (PRODUCER, PATH_SUPPORTED, FIRST_ORDER, HOLOMORPHIC, REAL_LIMITS)
        },
        "incidences": incidences,
        "summary": {
            "incidence_count": len(incidences),
            "certificates_pass": all(all(c["pass"] for c in row["certificates"].values()) for row in incidences),
            "predictions_applicable": sum(1 for row in incidences for p in row["predictions"] if p["applicable"]),
            "predictions_not_applicable": sum(
                1 for row in incidences for p in row["predictions"] if not p["applicable"]
            ),
            "predictions_hold": all(p["pass"] for row in incidences for p in row["predictions"]),
            "mutation_controls": len(controls),
            "mutation_controls_detected": sum(1 for c in controls if c["detected"]),
        },
        "not_recomputed": [
            "the vanishing of the rank-four Pfaffians of the Schur form, and with it the exact rank two of the form "
            "and the real nullity 8: " + PFAFFIAN_UNDECIDED + ". Over Q(i) the flags of the 2i rational run and the "
            "2c effective-form run are carried and labeled; modulo 32009 the claim is narrowed to the lower bound "
            "rank >= 2 (nullity at most 8), since the 2i modular run is modulo 32003",
        ],
        "inferred": [
            "the germ of E8-bar to B9 is analytically the A_1 cone (holomorphic Morse lemma) and the other germs "
            "are analytically their tangent cones",
            "the identification of the actual germ link L with the unit circle bundle of O_E(-1) through the "
            "radial deformation of kappa on the link to phi o p, which gives the attaching datum its homotopy class; "
            "the record computes the circle-bundle model",
        ],
        "pass": False,
    }
    summary = record["summary"]
    record["pass"] = bool(
        summary["certificates_pass"]
        and summary["predictions_hold"]
        and all(row["pass"] for row in incidences)
        and summary["mutation_controls_detected"] == summary["mutation_controls"]
    )
    return record


def build() -> dict[str, Any]:
    return assemble(parallel.ordered_map(certify, tasks(), min_items=2))


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def exit_status(record: dict[str, Any]) -> int:
    return 0 if record["pass"] else 1


# ---------------------------------------------------------------- self-test and command line


def self_test() -> str:
    """Known-answer cases, the mutations and a failing witness; explicit raises survive python -O."""
    for field in FIELDS:
        poly = parse_polynomial(field, "-222*I*t1/13 - 711*I*t3/26 + 2*t6^2", "t")
        _require(poly_degrees(poly) == {1, 2} and len(poly) == 3, "a sympy-format form lost a term")
        generator = parse_polynomial(field, "845*y4^2+(-754*I)*y4*y5-165*y5^2", "y")
        _require(len(generator) == 3, "a Singular-format generator lost a term")
        square = parse_polynomial(field, "(1+I)^2", "t")
        _require(
            square == poly_constant(field, field.mul(field.integer(2), field.lift(Fraction(0), Fraction(1)))),
            "(1+I)^2 is not 2*I",
        )
        _require(
            field.mul(field.lift(Fraction(0), Fraction(1)), field.lift(Fraction(0), Fraction(1)))
            == field.neg(field.one),
            "I*I is not -1",
        )
        matrix = [[field.integer(1), field.integer(2)], [field.integer(2), field.integer(4)]]
        _require(rank(field, matrix, 2) == 1, "a rank-one matrix has another rank")
        _require(len(nullspace(field, matrix, 2)) == 1, "the kernel of a rank-one matrix is not a line")
        regular = [[field.integer(1), field.integer(2)], [field.integer(3), field.integer(4)]]
        identity = [[field.one, field.zero], [field.zero, field.one]]
        _require(matmul(field, regular, inverse(field, regular)) == identity, "a matrix times its inverse is not 1")
        axes = [[[field.one, field.zero]], [[field.zero, field.one]]]
        _require(quadrics_vanishing_on(field, axes, 2) == 1, "only x1*x2 vanishes on both axes of the plane")
        product = parse_polynomial(field, "y1*y2", "y")
        _require(in_ideal(field, product, [parse_polynomial(field, "y1", "y")], 2), "y1*y2 lies in (y1)")
        _require(not in_ideal(field, product, [parse_polynomial(field, "y1^2", "y")], 2), "y1*y2 is not in (y1^2)")
    _require(gysin_h1(1, -2) == ("Z/2", "RP^3"), "Gysin: Euler number -2 over P^1 is RP^3")
    _require(gysin_h1(1, -1) == ("0", "S^3"), "Gysin: Euler number -1 over P^1 is S^3")
    _require(gysin_h1(2, -1) == ("0", "S^5"), "Gysin: Euler number -1 over P^2 is S^5")
    _require(gysin_h1(0, None) == ("Z", "S^1"), "Gysin: a point gives the circle")
    items = tasks()
    by_name = {task.incidence: task for task in items}
    original = COMPONENT_WITNESSES["E8bar->V"]
    COMPONENT_WITNESSES["E8bar->V"] = (
        original[0],
        ((1, 0, 0, 0, 0, 0, 0), (0, 0, 1, 0, 1, 0, 0), (0, 0, 0, 1, 0, 2, 0)),
    )
    try:
        verdict = decide_cone(GAUSSIAN, by_name["E8bar->V"], build_cone(GAUSSIAN, by_name["E8bar->V"]))
    finally:
        COMPONENT_WITNESSES["E8bar->V"] = original
    _require(
        not verdict["pass"] and not verdict["retained_generators_vanish_on_each_component"],
        "a wrong component witness passed the vanishing test",
    )
    record = build()
    summary = record["summary"]
    _require(summary["mutation_controls"] > 0, "no mutation ran")
    _require(summary["mutation_controls_detected"] == summary["mutation_controls"], "a mutation survived")
    _require(summary["certificates_pass"] and summary["predictions_hold"] and record["pass"], "a certificate failed")
    _require(exit_status(record) == 0, "a passing record has a nonzero exit status")
    wrong = dict(PREDICTED["Iso->B9"])
    wrong["link"] = ["S^5"]
    altered = [(task, wrong if task.incidence == "Iso->B9" else None) for task in items]
    rows = parallel.ordered_map(certify_with, altered, min_items=2)
    failing = assemble(rows)
    _require(
        not failing["summary"]["predictions_hold"] and not failing["pass"] and exit_status(failing) == 1,
        "a failed table prediction left the record passing",
    )
    return f"self-test: {summary['mutation_controls']} mutations detected, record pass={record['pass']}"


def certify_with(item: tuple[Task, dict[str, Any] | None]) -> dict[str, Any]:
    """certify under an altered prediction table when one is given; the unit the self-test dispatches."""
    task, table = item
    return certify(task) if table is None else certify(task, table)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--check", action="store_true", help="rebuild the record and compare it with the retained bytes"
    )
    parser.add_argument("--self-test", action="store_true", help="run the known-answer cases and the mutations")
    parser.add_argument("--out", type=Path, default=RECORD, help="where a fresh record is written")
    args = parser.parse_args(argv)
    if args.self_test:
        print(self_test())
        return 0
    record = build()
    text = render(record)
    if args.check:
        if RECORD.read_text(encoding="utf-8") != text:
            print(f"{RECORD.name}: differs from a fresh run", file=sys.stderr)
            return 1
        print(f"{RECORD.name}: byte-exact replay, pass={record['pass']}")
        return exit_status(record)
    args.out.write_text(text, encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "summary": record["summary"]}, indent=1))
    return exit_status(record)


if __name__ == "__main__":
    raise SystemExit(main())
