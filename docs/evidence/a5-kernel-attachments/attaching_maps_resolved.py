"""Attaching maps of the eight first-order-resolved A_5 incidences: certificates 0 to 3 of sub-step 3a.

The source closure of each incidence is complex-algebraic, so its transverse germ (Z, 0) at the retained basepoint has a
link L = Z meet S_eps. One blow-up resolves the Gauss map kappa of Z minus 0, and on the exceptional divisor
E = P(C_0 Z) it is the projectivized first-order map phi (rows 2c and 2i of the ledger). This producer reads only
the four retained records of rows 2b (path-supported basepoints), 2c (first-order normal cones), 2i (holomorphic Schur
blow-ups) and 2l (real limit sets), and certifies per incidence, exactly over Q(i) and over F_32009 (i = 10754):

  0. the punctured germ has constant nullity 8: the pivot Pfaffian of the Schur block is a unit, the Schur form has
     rank two, and phi has no zero on the punctured tangent cone, so the form stays nonzero near E;
  1. the conical structure: smooth germs, the A_1 cone of E8-bar to B9 (a Morse quadratic part of rank 3), and the two
     disjoint linear components of the three two-component rows;
  2. phi is linear and injective on each tangent-cone component, so E maps isomorphically onto its image, whose
     invariants equal those of 2i and 2l;
  3. the homotopy data as classes: the Euler class of the circle bundle p: S(O_E(-1)) -> E, the map E -> Lambda on
     H_2, and c_1(S|Lambda) = -H with its evaluation on curve components.

The independent topology checks recompute the Euler number from the degree of E in its span, H_1(L) from the Gysin
sequence, and c_1 = -H from the Pluecker coordinates of 2i. The identification of L with the unit circle bundle of
O_E(-1) (the radial deformation of kappa to phi o p) and the passage from the first-order form to the germ rest on the
cited theorems and stay inferred; the record labels them so.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/attaching_maps_resolved.py [--check |
--self-test]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections.abc import Sequence
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
BORDERED_KERNEL_SHIFT = 1
SCHUR_FORM_RANK = 2

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


# ---------------------------------------------------------------- the cone and its components


@dataclass
class Cone:
    width: int
    linear: list[Vector]
    quadrics: list[Poly]
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
    """Parse the retained tangent-cone generators and find the components of their zero set."""
    cone_row = task.first_order["tangent_cone"]
    texts = list(cone_row["generators"] if generators is None else generators)
    width = task.first_order["slice_dimension"]
    polys = [parse_polynomial(field, text, "t") for text in texts]
    linear = [linear_row(field, p, width) for p in polys if poly_degrees(p) == {1}]
    quadrics = [p for p in polys if poly_degrees(p) == {2}]
    _require(len(linear) + len(quadrics) == len(polys), "a generator is neither linear nor quadratic")
    span = nullspace(field, linear, width)
    restricted = [restrict(field, p, span) for p in quadrics]
    restricted = [p for p in restricted if p]
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    dimension, multiplicity, embedding, components = observed
    _require(len(span) == embedding, "the linear generators leave an embedding dimension other than the recorded one")
    if multiplicity == 1:
        _require(
            not restricted and dimension == embedding and components == 1, "a smooth row has a nonlinear generator"
        )
        return Cone(width, linear, quadrics, span, restricted, [span], "smooth")
    if components == 1:
        _require(len(restricted) >= 1 and dimension == embedding - 1, "the hypersurface row lost its quadric")
        return Cone(width, linear, quadrics, span, restricted, [span], "hypersurface")
    witnesses = [[integer_vector(field, vector) for vector in comp] for comp in COMPONENT_WITNESSES[task.incidence]]
    for comp in witnesses:
        for text_poly in polys:
            vanishing = restrict(field, text_poly, comp)
            _require(
                not vanishing, f"a retained generator does not vanish on a witnessed component of {task.incidence}"
            )
    return Cone(width, linear, quadrics, span, restricted, witnesses, "two-components")


def decide_cone(field: Field, task: Task, cone: Cone) -> dict[str, Any]:
    """Certificate 1."""
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    dimension, multiplicity, embedding, components = observed
    result: dict[str, Any] = {
        "kind": cone.kind,
        "dimension_multiplicity_embedding_components": observed,
    }
    if cone.kind == "smooth":
        result["smooth"] = multiplicity == 1 and dimension == embedding
        result["pass"] = result["smooth"]
    elif cone.kind == "hypersurface":
        # The retained tangent cone restricted to its span is cut out by quadrics, all proportional to one form q.
        base = cone.restricted[0]
        proportional = True
        monomials = sorted(base)
        pivot = monomials[0]
        for other in cone.restricted[1:]:
            ratio = field.mul(other.get(pivot, field.zero), field.inv(base[pivot]))
            proportional = proportional and poly_add(field, other, poly_scale(field, base, field.neg(ratio))) == {}
        matrix = quadric_matrix(field, base, embedding)
        quadratic_rank = rank(field, matrix, embedding)
        result["quadratic_part_rank"] = quadratic_rank
        result["quadrics_proportional"] = proportional
        result["morse"] = proportional and quadratic_rank == embedding
        result["pass"] = result["morse"] and multiplicity == 2 and dimension == embedding - 1
    else:
        spans = [rank(field, comp, cone.width) for comp in cone.components]
        joint = rank(field, [vector for comp in cone.components for vector in comp], cone.width)
        result["component_dimensions"] = spans
        result["components_smooth"] = all(s == dimension for s in spans)
        result["tangent_spaces_joint_rank"] = joint
        result["tangent_spaces_meet_only_at_zero"] = joint == sum(spans)
        result["multiplicity_equals_component_count"] = multiplicity == components == len(cone.components)
        result["pass"] = (
            result["components_smooth"]
            and result["tangent_spaces_meet_only_at_zero"]
            and result["multiplicity_equals_component_count"]
        )
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


def pulled_back_vanishes(field: Field, task: Task, cone: Cone, rows: Sequence[Vector]) -> bool:
    """Every recorded generator of the first-order image, composed with the form coordinates, vanishes on E.

    On the hypersurface row the composite is a multiple of the restricted quadric, which cuts E out of its span."""
    generators = task.first_order["first_order_image"]["generators_in_independent_form_coordinates"]
    outcome = True
    for comp in cone.components:
        images: dict[int, Poly] = {}
        for k, row in enumerate(rows, start=1):
            image: Poly = {}
            for j, vector in enumerate(comp, start=1):
                value = field.zero
                for coefficient, coordinate in zip(row, vector, strict=True):
                    value = field.add(value, field.mul(coefficient, coordinate))
                image = poly_add(field, image, poly_scale(field, poly_variable(field, j), value))
            images[k] = image
        for text in generators:
            pulled = substitute(field, parse_polynomial(field, text, "y"), images)
            if cone.kind == "hypersurface":
                outcome = outcome and multiple_of(field, pulled, cone.restricted[0])
            else:
                outcome = outcome and not pulled
    return outcome


def exceptional_degrees(field: Field, cone: Cone) -> list[int]:
    """The degree of each component of E in its linear span."""
    if cone.kind == "hypersurface":
        _require(poly_degrees(cone.restricted[0]) == {2}, "the hypersurface quadric is not homogeneous of degree 2")
        return [2]
    return [1] * len(cone.components)


def decide_map(
    field: Field, task: Task, cone: Cone, rows_h: Sequence[Vector], rows_c: Sequence[Vector]
) -> dict[str, Any]:
    """Certificate 2."""
    observed = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"]
    dimension = observed[0]
    spans = [len(comp) for comp in cone.components]
    union = [vector for comp in cone.components for vector in comp]
    committed = task.first_order["first_order_image"]
    blowup = task.holomorphic["explicit_blowup"]
    degrees = exceptional_degrees(field, cone)
    result: dict[str, Any] = {"component_span_dimensions": spans}
    for label, rows in (("holomorphic_2i", rows_h), ("first_order_2c", rows_c)):
        per = [image_rank(field, rows, comp) for comp in cone.components]
        joint = image_rank(field, rows, union)
        result[label] = {
            "coordinate_count": len(rows),
            "rank_on_each_component_span": per,
            "injective_on_each_component": per == spans,
            "rank_on_the_sum_of_components": joint,
            "images_meet_only_at_zero": joint == sum(spans),
        }
    result["pulled_back_image_generators_vanish_on_E"] = pulled_back_vanishes(field, task, cone, rows_c)
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
    result["pass"] = (
        result["holomorphic_2i"]["injective_on_each_component"]
        and result["first_order_2c"]["injective_on_each_component"]
        and result["pulled_back_image_generators_vanish_on_E"]
        and result["image_matches_2i"]
        and result["image_matches_2c"]
        and result["image_matches_2l"]
        and result["multiplicity_equals_degree_sum"]
    )
    return result


def decide_nullity(field: Field, task: Task, map_result: dict[str, Any]) -> dict[str, Any]:
    """Certificate 0."""
    schur = task.holomorphic["c_schur_complement"]
    pivot = gaussian_from_record(field, schur["pivot_pfaffian_at_origin"])
    bordered_kernel = schur["boundary_kernel_dimension"] - BORDERED_KERNEL_SHIFT
    complex_kernel = bordered_kernel - SCHUR_FORM_RANK
    blowup = task.holomorphic["explicit_blowup"]
    result = {
        "pivot_pfaffian_is_a_unit": not field.is_zero(pivot),
        "bordered_kernel_dimension_at_the_boundary": bordered_kernel,
        "schur_form_rank_on_the_cone": SCHUR_FORM_RANK,
        "real_nullity_off_the_basepoint": 2 * complex_kernel,
        "rank_four_pfaffians_vanish": bool(
            blowup["modular"]["rank_four_pfaffians_vanish"] and blowup["rational"]["rank_four_pfaffians_vanish"]
        ),
        "exceptional_charts_base_free": bool(
            blowup["modular"]["nonempty_charts_base_free"] and blowup["rational"]["nonempty_charts_base_free"]
        ),
        "degeneracy_locus_empty_in_projective_space": task.first_order["degeneracy_locus"]["projective_dimension"]
        == -1,
        "first_order_form_nonzero_on_the_punctured_cone": map_result["holomorphic_2i"]["injective_on_each_component"]
        and map_result["first_order_2c"]["injective_on_each_component"],
        "inferred": (
            "the form is its first-order part plus O(|z|^2); the first-order part has a lower bound on the "
            "unit sphere of the cone, so the form stays nonzero, hence of rank exactly two, on a punctured "
            "neighborhood in Z"
        ),
    }
    result["pass"] = (
        result["pivot_pfaffian_is_a_unit"]
        and result["real_nullity_off_the_basepoint"] == 8
        and result["rank_four_pfaffians_vanish"]
        and result["exceptional_charts_base_free"]
        and result["degeneracy_locus_empty_in_projective_space"]
        and result["first_order_form_nonzero_on_the_punctured_cone"]
    )
    return result


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


def decide_topology(field: Field, task: Task, cone: Cone, map_result: dict[str, Any]) -> dict[str, Any]:
    """Certificate 3 and the independent topology checks."""
    dimension = task.first_order["germ"]["observed_dimension_multiplicity_embedding_components"][0]
    degrees = exceptional_degrees(field, cone)
    pluecker_degree = task.holomorphic["explicit_blowup"]["rational"]["image_degree"]
    spans = map_result["component_span_dimensions"]
    complete = [
        rank_ == span
        for rank_, span in zip(map_result["holomorphic_2i"]["rank_on_each_component_span"], spans, strict=True)
    ]
    components = []
    for index, degree in enumerate(degrees):
        projective = dimension - 1
        euler = None if projective == 0 else -degree
        h1, link = gysin_h1(projective, euler)
        curve = projective == 1
        evaluation = -pluecker_degree if curve and len(degrees) == 1 else None
        components.append(
            {
                "exceptional_projective_dimension": projective,
                "degree_of_E_in_its_span": degree,
                "euler_class_coefficient": euler,
                "link": link,
                "h1_of_link": h1,
                "phi_on_h2_is_an_isomorphism": map_result["holomorphic_2i"]["injective_on_each_component"],
                "pluecker_pullback_of_the_hyperplane_class_is_h": complete[index],
                "c1_of_S_on_the_component": None if projective == 0 else "-H = -h",
                "c1_of_S_evaluated_on_the_curve": evaluation,
                "euler_class_equals_minus_pluecker_degree": (
                    evaluation == euler if curve and evaluation is not None else None
                ),
            }
        )
    passed = all(
        c["phi_on_h2_is_an_isomorphism"]
        and c["pluecker_pullback_of_the_hyperplane_class_is_h"]
        and c["euler_class_equals_minus_pluecker_degree"] is not False
        for c in components
    )
    return {"components": components, "pass": passed}


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


def analyze(field: Field, task: Task) -> dict[str, Any]:
    cone = build_cone(field, task)
    rows_h = phi_from_holomorphic(field, task)
    rows_c = phi_from_first_order(field, task)
    _require(all(len(row) == cone.width for row in rows_h + rows_c), "a phi row does not span the slice")
    conical = decide_cone(field, task, cone)
    mapped = decide_map(field, task, cone, rows_h, rows_c)
    return {
        "certificate_0_constant_nullity": decide_nullity(field, task, mapped),
        "certificate_1_conical_structure": conical,
        "certificate_2_linear_injective_phi": mapped,
        "certificate_3_homotopy_data": decide_topology(field, task, cone, mapped),
    }


def retained_direction(field: Field, task: Task) -> Vector:
    coordinates = task.first_order["canonical_paths"][0]["normal_coordinates"]
    return [field.lift(Fraction(text), Fraction(0)) for text in coordinates]


def lower_rank_of_phi(field: Field, task: Task, component: int) -> dict[str, Any]:
    """Mutation 1: remove the action of phi on one vector k of a named component and require k as a kernel point."""
    cone = build_cone(field, task)
    rows = phi_from_holomorphic(field, task)
    comp = cone.components[component]
    point = retained_direction(field, task) if cone.kind == "hypersurface" else comp[0]
    on_cone = all(
        field.is_zero(evaluate(field, parse_polynomial(field, text, "t"), point))
        for text in task.first_order["tangent_cone"]["generators"]
    )
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
    kernel_on_cone = [
        all(
            field.is_zero(evaluate(field, parse_polynomial(field, text, "t"), p))
            for text in task.first_order["tangent_cone"]["generators"]
        )
        for p in points
    ]
    mapped = decide_map(field, task, cone, mutated, phi_from_first_order(field, task))
    return {
        "incidence": task.incidence,
        "mutation": "lower_the_rank_of_phi_on_a_component",
        "component": component,
        "baseline_rank_on_component": image_rank(field, rows, comp),
        "mutated_rank_on_component": image_rank(field, mutated, comp),
        "span_dimension": len(comp),
        "kernel_dimension": len(points),
        "projective_kernel_point": [field.render(x) for x in point],
        "kernel_point_on_the_cone": on_cone,
        "mutated_phi_kills_the_point": all(field.is_zero(x) for x in apply(field, mutated, point)),
        "all_kernel_points_on_the_cone": all(kernel_on_cone),
        "certificate_2_passes_on_the_mutated_phi": mapped["pass"],
        "detected": bool(points) and on_cone and not mapped["pass"],
    }


def rank_two_quadratic_part(field: Field, task: Task) -> dict[str, Any]:
    """Mutation 2: drop the t5^2 term of the E8-bar to B9 quadric, a form of rank 2, which must fail the Morse test."""
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


def certify(task: Task) -> dict[str, Any]:
    """Every certificate and control of one incidence, in both fields."""
    per_field = {field.name: analyze(field, task) for field in FIELDS}
    gaussian, modular = per_field[GAUSSIAN.name], per_field[MODULAR.name]
    agree = gaussian == modular
    mutations = []
    for field in FIELDS:
        cone = build_cone(field, task)
        for component in range(len(cone.components)):
            mutations.append({"field": field.name, **lower_rank_of_phi(field, task, component)})
        if task.incidence == "E8bar->B9":
            mutations.append({"field": field.name, **rank_two_quadratic_part(field, task)})
    certificates = dict(gaussian)
    predictions = predict(task, certificates)
    return {
        "incidence": task.incidence,
        "source_orbit": task.first_order["source_orbit"],
        "boundary_orbit": task.first_order["boundary_orbit"],
        "retained_rows_agree": check_records_agree(task),
        "certificates": certificates,
        "modular_certificates_equal_gaussian": agree,
        "predictions": predictions,
        "mutation_controls": mutations,
        "pass": agree
        and all(certificates[k]["pass"] for k in certificates)
        and all(m["detected"] for m in mutations)
        and all(check_records_agree(task).values()),
    }


def predict(task: Task, certificates: dict[str, Any]) -> list[dict[str, Any]]:
    """Each value of the section's table against the computed value."""
    table = PREDICTED[task.incidence]
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
                {
                    "name": name,
                    "applicable": False,
                    "predicted": predicted,
                    "computed": value,
                    "pass": _is_null(value),
                }
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


def build() -> dict[str, Any]:
    incidences = parallel.ordered_map(certify, tasks(), min_items=2)
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
        "inferred": [
            "the germ of E8-bar to B9 is analytically the A_1 cone (holomorphic Morse lemma) and the other germs "
            "are analytically their tangent cones",
            "the radial deformation of kappa on the link to phi o p, which identifies L with the unit circle bundle "
            "of O_E(-1) and gives the attaching datum its homotopy class",
        ],
        "pass": False,
    }
    record["pass"] = bool(
        record["summary"]["certificates_pass"]
        and all(row["pass"] for row in incidences)
        and record["summary"]["mutation_controls_detected"] == record["summary"]["mutation_controls"]
    )
    return record


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


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
    _require(gysin_h1(1, -2) == ("Z/2", "RP^3"), "Gysin: Euler number -2 over P^1 is RP^3")
    _require(gysin_h1(1, -1) == ("0", "S^3"), "Gysin: Euler number -1 over P^1 is S^3")
    _require(gysin_h1(2, -1) == ("0", "S^5"), "Gysin: Euler number -1 over P^2 is S^5")
    _require(gysin_h1(0, None) == ("Z", "S^1"), "Gysin: a point gives the circle")
    items = tasks()
    by_name = {task.incidence: task for task in items}
    broken = Task(
        "E8bar->V",
        by_name["E8bar->V"].path_supported,
        by_name["E8bar->V"].first_order,
        by_name["E8bar->V"].holomorphic,
        by_name["E8bar->V"].real_limits,
    )
    original = COMPONENT_WITNESSES["E8bar->V"]
    COMPONENT_WITNESSES["E8bar->V"] = (
        original[0],
        ((1, 0, 0, 0, 0, 0, 0), (0, 0, 1, 0, 1, 0, 0), (0, 0, 0, 1, 0, 2, 0)),
    )
    try:
        build_cone(GAUSSIAN, broken)
    except RuntimeError:
        failed = True
    else:
        failed = False
    finally:
        COMPONENT_WITNESSES["E8bar->V"] = original
    _require(failed, "a wrong component witness passed the vanishing test")
    record = build()
    summary = record["summary"]
    _require(summary["mutation_controls"] > 0, "no mutation ran")
    _require(summary["mutation_controls_detected"] == summary["mutation_controls"], "a mutation survived")
    _require(summary["certificates_pass"] and record["pass"], "a certificate failed")
    return f"self-test: {summary['mutation_controls']} mutations detected, record pass={record['pass']}"


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
    text = render(build())
    if args.check:
        if RECORD.read_text(encoding="utf-8") != text:
            print(f"{RECORD.name}: differs from a fresh run", file=sys.stderr)
            return 1
        print(f"{RECORD.name}: byte-exact replay")
        return 0
    args.out.write_text(text, encoding="utf-8")
    record = json.loads(text)
    print(json.dumps({"pass": record["pass"], "summary": record["summary"]}, indent=1))
    return 0 if record["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
