"""A rational chart of SL(3, C) in G_2(C) holds a real algebraic point of V(G) minus V(Q) with dim L = 4.

Setting (nullity4_real_polar_rational_charts.py, rc). z_0 is the normal form (s, v_1, mu) = (4, 3, 5 i), l its polar
plane and C(l) = span(k_0, k_1, k_2) with z_0 = i k_0 + 3 k_1 + 5 k_2. For g in G_2(C) and Pi = g^* g the point
g z_0 has kernel plane g l exactly when F = z_0^* Pi l vanishes, and then dim L = 2 (3 - rank R) for
R = [k_0, k_1, k_2]^* Pi l. Since F = -i R_0 + 3 R_1 + 5 R_2 (rows of R), where F = 0 the rank of R is the rank of
its rows R_1, R_2, so a point with F = 0, m = det [R_1; R_2] = 0 and a nonzero entry of R has dim L = 4.

1. Chart (exact over Q(i)(d_2, x_21, y_31)). With W = [e_1 + i e_5, e_2 + i e_6, e_3 + i e_7] and A = L D L^*,
   L unit lower triangular with entries L_21 = x_21, L_31 = i y_31, L_32 = -i / 2 and D = diag(1, d_2, 1 / d_2),
   the matrix g = e_4 e_4^T + (W A W^* + conj(W) A^(-T) conj(W)^*) / 2 is Hermitian for real parameters, and
   M(G t) = G M(t) G^T holds for G = diag(g, 1, g) as an identity in the parameters at each of the 15 basis
   vectors t, so for every t: g lies in the subgroup of G_2(C) that fixes e_4.
2. Equations. For Pi = diag(g^2, 1, g^2) the two entries of F and the minor m have identically zero imaginary
   parts, and their real parts are p_0 / (32 d_2^2), p_1 / (32 d_2^2), p_2 / (1024 d_2^4) with p_0, p_1, p_2 in
   Z[d_2, x_21, y_31] of total degrees 8, 8, 16 (40, 42, 126 terms).
3. Certificate (python-flint arb). The Krawczyk operator of (p_0, p_1, p_2) maps the box of radius 2^-30 around
   MIDPOINT / 2^40 into its interior, at 200 and at 400 bits; d_2 is positive on the box and the entry R_01 has
   modulus above 2^4 on it. So the box holds exactly one real zero, the Jacobian is invertible there, the zero is
   an isolated point of a variety defined over Q and its coordinates are algebraic numbers: an exact real point
   with F = 0 and rank R = 1, so dim L = 4. A second box of radius 2^-300 around a Newton refinement lies inside
   the first and passes the same test at 1500 bits, so it holds the same zero.
4. Degree (computed outside this file, checked here in part). msolve 0.9.4 on (p_0, p_1, p_2, w d_2 - 1) in
   Q[w, x_21, y_31, d_2] returns dimension 0, a quotient of dimension 164 (Singular 4.4.1 gives the same vdim) and
   an eliminating polynomial of degree 140 for the form t = w + 2 x_21 + 3 y_31 + 4 d_2, retained in
   nullity4-real-polar-sl3-chart-eliminant.json. This file factors that polynomial over Q (degrees 2, 2, 2, 4, 6,
   36, 88, each once) and evaluates each factor on the second box: the ball of the factor of degree 88 contains
   0 and the ball of every other factor excludes it. Granted that the retained polynomial vanishes at the point
   (the output of msolve, not recomputed here), t has degree 88 over Q, and so does the field of the point, whose
   degree is a multiple of 88 and at most 164.

Evidence classes. Items 1 and 2 are exact identities; item 3 is a certified interval statement, repeated at two
precisions; item 4 is a computed degree that rests on msolve for the eliminant and on this file for the factor that
holds the point. The point is not written in closed form.

--write writes nullity4-real-polar-sl3-chart-result.json beside this file; --check recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_sl3_chart.py --check
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import sympy as sp
from flint import arb, arb_mat, ctx, fmpq, fmpz_poly

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_real_polar_rational_charts as rc  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-real-polar-sl3-chart-v1"
RECORD = HERE / "nullity4-real-polar-sl3-chart-result.json"
ELIMINANT = HERE / "nullity4-real-polar-sl3-chart-eliminant.json"
SOURCE_PATHS = (
    HERE / "nullity4_real_polar_sl3_chart.py",
    ELIMINANT,
    HERE / "nullity4_real_polar_rational_charts.py",
    HERE / "nullity4_real_polar_fiber_four.py",
    HERE / "nullity4_real_polar_line.py",
    HERE / "nullity4_orbit_normal_forms.py",
)
FIELD = "Q(i)(d2, x21, y31); arb balls at the listed precisions; factorization over Q"
IU = sp.I
D2, X21, Y31 = sp.symbols("d2 x21 y31", real=True)
VARIABLES = (D2, X21, Y31)
L32 = sp.Rational(-1, 2)

CHART = {"hermitian": True, "equivariant": True, "point_in_the_basis": True, "incidence_is_a_row_combination": True}
EQUATIONS = {
    "imaginary_parts_zero": [True, True, True],
    "denominators": ["32*d2**2", "32*d2**2", "1024*d2**4"],
    "degrees": [8, 8, 16],
    "terms": [40, 42, 126],
    "values_at_2_3_5": ["7109568", "1666304", "6466059776000"],
}
# The coarse box: midpoint MIDPOINT / 2^GRID_BITS, radius 2^-RADIUS_BITS. The fine box: radius 2^-FINE_RADIUS_BITS
# around the Newton refinement of that midpoint, rounded to the grid 2^-FINE_GRID_BITS.
MIDPOINT = (1452753013313, -184301525366, 775217672282)
GRID_BITS = 40
RADIUS_BITS = 30
PRECISIONS = (200, 400)
FINE_GRID_BITS = 400
FINE_RADIUS_BITS = 300
FINE_PRECISION = 1500
NEWTON_STEPS = 12
PAIRING_ENTRY = (0, 1)
BOX_JOBS = (
    ("coarse", PRECISIONS[0]),
    ("coarse", PRECISIONS[1]),
    ("fine", FINE_PRECISION),
)
_COARSE = {"interior": True, "contraction_bits": 11, "d2_positive": True, "pairing_bound_bits": 4}
BOXES: dict[str, dict[str, Any]] = {
    "coarse": {str(PRECISIONS[0]): dict(_COARSE), str(PRECISIONS[1]): dict(_COARSE)},
    "fine": {
        str(FINE_PRECISION): {
            "interior": True,
            "contraction_bits": 101,
            "d2_positive": True,
            "pairing_bound_bits": 4,
            "inside_the_coarse_box": True,
        }
    },
}
# The linear form of the eliminant: t = w + 2 x21 + 3 y31 + 4 d2 with w = 1 / d2.
FORM = (1, 2, 3, 4)
DEGREE: dict[str, Any] = {
    "tools": {"msolve": "0.9.4", "singular": "4.4.1"},
    "quotient_dimension": 164,
    "eliminant_degree": 140,
    "factor_degrees": [[2, 1], [2, 1], [2, 1], [4, 1], [6, 1], [36, 1], [88, 1]],
    "degrees_of_the_factors_whose_ball_holds_zero": [88],
    "vanishing_bits": 253,
}
FACT_JOBS = ("chart", "equations", *(f"box {name} {precision}" for name, precision in BOX_JOBS), "degree")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def lower_triangle() -> sp.Matrix:
    return sp.Matrix([[1, 0, 0], [X21, 1, 0], [IU * Y31, IU * L32, 1]])


@functools.cache
def chart() -> sp.Matrix:
    """g of item 1 as a 7 x 7 matrix over Q(i)(d2, x21, y31)."""
    w = sp.zeros(7, 3)
    for k in range(3):
        w[k, k] = 1
        w[k + 4, k] = IU
    lower = lower_triangle()
    inverse = lower.inv().applyfunc(sp.expand)
    _require((lower * inverse).applyfunc(sp.expand) == sp.eye(3), "the inverse of the triangular factor is wrong")
    a = (lower * sp.diag(1, D2, 1 / D2) * lower.H).applyfunc(sp.expand)
    a_inverse_transpose = (inverse.T * sp.diag(1, 1 / D2, D2) * inverse.conjugate()).applyfunc(sp.expand)
    e4 = sp.eye(7)[:, 3]
    wb = w.conjugate()
    half = sp.Rational(1, 2)
    return (e4 * e4.T + half * w * a * w.H + half * wb * a_inverse_transpose * wb.H).applyfunc(sp.expand)


@functools.cache
def _pairings() -> tuple[sp.Matrix, sp.Matrix]:
    """F = z_0^* Pi l (1 x 2) and R = C(l)^* Pi l (3 x 2) for Pi = diag(g^2, 1, g^2)."""
    z0, line, kernel = rc.polar()
    g = chart()
    square = (g * g).applyfunc(sp.expand)
    pi = sp.diag(square, sp.Matrix([[1]]), square)
    return (z0.H * pi * line).applyfunc(sp.expand), (kernel.H * pi * line).applyfunc(sp.expand)


def _equivariance_fails(index: int) -> bool:
    """Whether M(G e) = G M(e) G^T fails at the basis vector e of the given index, for G = diag(g, 1, g)."""
    g = chart()
    big = sp.diag(g, sp.Matrix([[1]]), g)
    unit = [1 if k == index else 0 for k in range(15)]
    moved = forms.block(list(big[:, index]), forms.ALL, forms.ALL)
    difference = moved - big * forms.block(unit, forms.ALL, forms.ALL) * big.T
    return any(difference.applyfunc(sp.expand))


def chart_facts() -> dict[str, bool]:
    """Per CHART: g Hermitian; diag(g, 1, g) equivariant; z_0 = i k_0 + 3 k_1 + 5 k_2; F = -i R_0 + 3 R_1 + 5 R_2.

    M is linear in its argument, so the identity M(G t) = G M(t) G^T holds for every t when it holds on a basis.
    """
    g = chart()
    z0, _, kernel = rc.polar()
    f, r = _pairings()
    combination = -IU * r[0, :] + 3 * r[1, :] + 5 * r[2, :]
    values = (
        (g - g.H).applyfunc(sp.expand) == sp.zeros(7, 7),
        not any(parallel.ordered_map(_equivariance_fails, list(range(15)))),
        z0 == IU * kernel[:, 0] + 3 * kernel[:, 1] + 5 * kernel[:, 2],
        not any((f - combination).applyfunc(sp.expand)),
    )
    return dict(zip(CHART, [bool(value) for value in values], strict=True))


def _split(expression: Any) -> tuple[sp.Poly, sp.Poly, Any]:
    """Real and imaginary parts of the numerator, as polynomials over Z, and the factored denominator."""
    numerator, denominator = sp.fraction(sp.together(expression))
    real, imaginary = sp.expand(numerator).as_real_imag()
    return (
        sp.Poly(sp.expand(real), *VARIABLES, domain="ZZ"),
        sp.Poly(sp.expand(imaginary), *VARIABLES, domain="ZZ"),
        sp.factor(denominator),
    )


@functools.cache
def _system() -> tuple[tuple[tuple[sp.Poly, sp.Poly, Any], ...], tuple[sp.Poly, sp.Poly, Any]]:
    """The split entries F_0, F_1 and m, and the split entry PAIRING_ENTRY of R."""
    f, r = _pairings()
    minor = sp.expand(r[1, 0] * r[2, 1] - r[1, 1] * r[2, 0])
    return tuple(_split(entry) for entry in (f[0, 0], f[0, 1], minor)), _split(r[PAIRING_ENTRY[0], PAIRING_ENTRY[1]])


@functools.cache
def polynomials() -> tuple[sp.Poly, sp.Poly, sp.Poly]:
    """p_0, p_1, p_2 of item 2."""
    parts, _ = _system()
    _require(all(part[1].is_zero for part in parts), "an equation has a nonzero imaginary part")
    return parts[0][0], parts[1][0], parts[2][0]


def equation_facts() -> dict[str, Any]:
    parts, _ = _system()
    point = dict(zip(VARIABLES, (2, 3, 5), strict=True))
    return {
        "imaginary_parts_zero": [bool(part[1].is_zero) for part in parts],
        "denominators": [str(part[2]) for part in parts],
        "degrees": [int(part[0].total_degree()) for part in parts],
        "terms": [len(part[0].terms()) for part in parts],
        "values_at_2_3_5": [str(part[0].as_expr().subs(point)) for part in parts],
    }


Terms = tuple[tuple[tuple[int, int, int], int], ...]


def _terms(polynomial: sp.Poly) -> Terms:
    return tuple(
        ((int(monomial[0]), int(monomial[1]), int(monomial[2])), int(coefficient))
        for monomial, coefficient in polynomial.terms()
    )


@functools.cache
def _evaluators() -> tuple[tuple[Terms, ...], tuple[tuple[Terms, ...], ...], tuple[Terms, Terms, Terms]]:
    """The terms of p_0, p_1, p_2, of their Jacobian, and of the parts and the denominator of the entry of R."""
    system = polynomials()
    jacobian = tuple(tuple(_terms(p.diff(v)) for v in VARIABLES) for p in system)
    _, entry = _system()
    denominator = sp.Poly(sp.expand(entry[2]), *VARIABLES, domain="ZZ")
    return tuple(_terms(p) for p in system), jacobian, (_terms(entry[0]), _terms(entry[1]), _terms(denominator))


def _value(terms: Terms, point: list[Any]) -> Any:
    """The polynomial with the given terms at a point of arb balls."""
    total = arb(0)
    for monomial, coefficient in terms:
        term = arb(coefficient)
        for value, exponent in zip(point, monomial, strict=True):
            if exponent:
                term *= value**exponent
        total += term
    return total


def _dyadic(numerator: int, bits: int) -> Any:
    return arb(fmpq(numerator, 1 << bits))


@functools.cache
def fine_midpoint() -> tuple[int, int, int]:
    """Numerators over 2^FINE_GRID_BITS of the Newton refinement of the coarse midpoint (a guess; item 3 tests it)."""
    system, jacobian, _ = _evaluators()
    saved = ctx.prec
    ctx.prec = FINE_PRECISION
    try:
        point = [_dyadic(n, GRID_BITS) for n in MIDPOINT]
        for _ in range(NEWTON_STEPS):
            values = arb_mat([[_value(terms, point).mid()] for terms in system])
            matrix = arb_mat([[_value(terms, point).mid() for terms in row] for row in jacobian])
            step = matrix.solve(values)
            point = [(point[c] - step[c, 0]).mid() for c in range(3)]
        scale = arb(2) ** FINE_GRID_BITS
        numerators = tuple(int((value * scale + arb(fmpq(1, 2))).floor().unique_fmpz()) for value in point)
    finally:
        ctx.prec = saved
    return numerators[0], numerators[1], numerators[2]


def _box(name: str) -> tuple[tuple[int, int, int], int, int]:
    """Midpoint numerators, grid bits and radius bits of the named box."""
    _require(name in ("coarse", "fine"), f"unknown box {name}")
    if name == "coarse":
        return MIDPOINT, GRID_BITS, RADIUS_BITS
    return fine_midpoint(), FINE_GRID_BITS, FINE_RADIUS_BITS


def _largest_power(value: Any, below: bool, cap: int) -> int:
    """The largest k up to cap with value < 2^-k (below) or value > 2^k (not below); -1 when there is none."""
    best = -1
    for k in range(cap + 1):
        bound = arb(2) ** (-k if below else k)
        if (value < bound) if below else (value > bound):
            best = k
        elif not below:
            break
    return best


def _nested() -> bool:
    """Whether the fine box lies in the interior of the coarse box."""
    fine, fine_grid, fine_radius = _box("fine")
    for coarse_numerator, fine_numerator in zip(MIDPOINT, fine, strict=True):
        distance = abs(fmpq(fine_numerator, 1 << fine_grid) - fmpq(coarse_numerator, 1 << GRID_BITS))
        if not distance + fmpq(1, 1 << fine_radius) < fmpq(1, 1 << RADIUS_BITS):
            return False
    return True


def krawczyk(job: tuple[str, int]) -> dict[str, Any]:
    """The Krawczyk test of (p_0, p_1, p_2) on the named box at the precision of the job (name, precision)."""
    name, precision = job
    _require(precision >= 64, f"the precision {precision} is below 64 bits")
    midpoint, grid, radius_bits = _box(name)
    _require(radius_bits >= 1, "the radius selects the point evaluation")
    system, jacobian, entry = _evaluators()
    ctx.prec = precision
    center = [_dyadic(n, grid) for n in midpoint]
    radius = arb(fmpq(1, 1 << radius_bits))
    box = [value + arb(0, fmpq(1, 1 << radius_bits)) for value in center]
    f0 = arb_mat([[_value(terms, center)] for terms in system])
    j0 = arb_mat([[_value(terms, center).mid() for terms in row] for row in jacobian])
    inverse = j0.inv().mid()
    jx = arb_mat([[_value(terms, box) for terms in row] for row in jacobian])
    identity = arb_mat([[arb(1 if a == b else 0) for b in range(3)] for a in range(3)])
    offset = arb_mat([[arb(0, fmpq(1, 1 << radius_bits))] for _ in range(3)])
    image = -(inverse * f0) + (identity - inverse * jx) * offset
    interior = all(image[c, 0].lower() > -radius and image[c, 0].upper() < radius for c in range(3))
    worst = max((image[c, 0].abs_upper() for c in range(3)), key=lambda x: float(x.mid()))
    denominator = _value(entry[2], box)
    positive = bool(box[0] > 0) and bool(denominator.abs_lower() > 0)
    modulus = arb(0)
    if positive:
        real, imaginary = _value(entry[0], box), _value(entry[1], box)
        modulus = max(real.abs_lower(), imaginary.abs_lower(), key=lambda x: float(x.mid())) / denominator.abs_upper()
    result = {
        "interior": bool(interior),
        "contraction_bits": _largest_power(worst / radius, True, 400) if interior else -1,
        "d2_positive": positive,
        "pairing_bound_bits": _largest_power(modulus, False, 64),
    }
    if name == "fine":
        result["inside_the_coarse_box"] = _nested()
    _require(ctx.prec == precision, "the working precision changed during the Krawczyk test")
    return result


@functools.cache
def _eliminant() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(ELIMINANT.read_text(encoding="utf-8"))
    _require(tuple(data["form"]) == FORM, "the retained eliminant belongs to another linear form")
    return data


def _factor_ball(job: tuple[list[int], Any]) -> tuple[bool, int]:
    """For (coefficients, t): whether the ball of the factor at t holds 0, and its size against the height in bits."""
    coefficients, form = job
    value = arb(0)
    for coefficient in reversed(coefficients):
        value = value * form + coefficient
    if not value.contains(0):
        return False, -1
    return True, _largest_power(value.abs_upper() / max(abs(c) for c in coefficients), True, 400)


def degree_facts() -> dict[str, Any]:
    """Item 4: the factor degrees of the retained eliminant and the factors whose ball on the fine box holds 0."""
    data = _eliminant()
    polynomial = fmpz_poly([int(text) for text in data["eliminant"]])
    _, factors = polynomial.factor()
    ordered = sorted(factors, key=lambda pair: (pair[0].degree(), [int(c) for c in pair[0].coeffs()]))
    midpoint, grid, radius_bits = _box("fine")
    ctx.prec = FINE_PRECISION
    box = [_dyadic(n, grid) + arb(0, fmpq(1, 1 << radius_bits)) for n in midpoint]
    form = FORM[0] / box[0] + FORM[1] * box[1] + FORM[2] * box[2] + FORM[3] * box[0]
    balls = parallel.ordered_map(_factor_ball, [([int(c) for c in factor.coeffs()], form) for factor, _ in ordered])
    holding = [int(factor.degree()) for (factor, _), ball in zip(ordered, balls, strict=True) if ball[0]]
    vanishing = max((ball[1] for ball in balls if ball[0]), default=-1)
    return {
        "tools": dict(data["tools"]),
        "quotient_dimension": int(data["quotient_dimension"]),
        "eliminant_degree": int(polynomial.degree()),
        "factor_degrees": [[int(factor.degree()), int(multiplicity)] for factor, multiplicity in ordered],
        "degrees_of_the_factors_whose_ball_holds_zero": holding,
        "vanishing_bits": vanishing,
    }


def fact(job: str) -> Any:
    if job == "chart":
        return chart_facts()
    if job == "equations":
        return equation_facts()
    if job == "degree":
        return degree_facts()
    parts = job.split()
    _require(len(parts) == 3 and parts[0] == "box", f"unknown fact {job}")
    return krawczyk((parts[1], int(parts[2])))


def msolve_input() -> str:
    """The input of msolve for item 4: variables, characteristic 0, then p_0, p_1, p_2 and w d2 - 1."""
    system = [str(p.as_expr()).replace("**", "^") for p in polynomials()]
    return "w,x21,y31,d2\n0\n" + ",\n".join([*system, "w*d2-1"]) + "\n"


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def _boxes(values: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {name: {str(p): values[f"box {name} {p}"] for n, p in BOX_JOBS if n == name} for name in ("coarse", "fine")}


def compute() -> dict[str, Any]:
    values = dict(zip(FACT_JOBS, parallel.ordered_map(fact, list(FACT_JOBS), min_items=2), strict=True))
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "chart": values["chart"],
        "equations": values["equations"],
        "midpoint": {"numerators": list(MIDPOINT), "grid_bits": GRID_BITS, "radius_bits": RADIUS_BITS},
        "boxes": _boxes(values),
        "degree": values["degree"],
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
        "chart": dict(CHART),
        "equations": json.loads(json.dumps(EQUATIONS)),
        "midpoint": {"numerators": list(MIDPOINT), "grid_bits": GRID_BITS, "radius_bits": RADIUS_BITS},
        "boxes": json.loads(json.dumps(BOXES)),
        "degree": json.loads(json.dumps(DEGREE)),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "chart": "the chart is not Hermitian and equivariant, or the incidence is not the row combination",
        "equations": "the equations have other imaginary parts, denominators, degrees, terms or values",
        "midpoint": "the box differs",
        "boxes": "a Krawczyk test differs",
        "degree": "the factor degrees of the eliminant or the factor that holds the point differ",
    }
    for group, message in messages.items():
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, recompute and compare its text with --check, or print the msolve input."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--msolve-input", action="store_true")
    args = parser.parse_args()
    if args.msolve_input:
        sys.stdout.write(msolve_input())
        return
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    held = record["degree"]["degrees_of_the_factors_whose_ball_holds_zero"]
    print(f"pass: {len(BOX_JOBS)} Krawczyk tests, the point on the factor of degree {held}")


if __name__ == "__main__":
    main()
