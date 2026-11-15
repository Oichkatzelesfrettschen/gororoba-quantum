"""The E8-bar degree-11 component is a rational fourfold: the weighted initial-form map is birational onto it.

At N- or N+ the parametrization phi of `e8_relation_ideal_orders.py` and the weights (1, 1, 2, 1, 2) on the
parameters (pa, pb, pl, pz, pm) send a point p to the 21 initial forms V_k(p), the weight-5 parts of phi^* G_k
(A5-457, whose kernel of y_k -> V_k is the degree-11 prime P5). The map V from the affine space of the parameters to
C^21 has degree 5 over its image, and the map it induces from P(1, 1, 2, 1, 2) to P^20 is birational onto V(P5).

Step A. Of the 21 initial forms 17 are nonzero and each is divisible by pl. After the graded change of variable
pm = s pz^2 - m (s = 4 at N-, s = -4 at N+) the 17 quotients V_k / pl span 12 monomials of weighted degree 3, the
set A, and their coefficient matrix has rank 12 over Q(i). The change of variable removes pb pz^2 and pa pz^2 from
the 14 monomials of the unchanged quotients.

Step B. Let V(p) = V(p') with pa pl nonzero. The rank makes the monomial vector mu(p) of the quotients, hence
V(p) / pl, determine mu(p) = mu(p') up to the factor pl' / pl; the five monomials a^3, a^2 b, a^2 z, a l, a m of A
give b/a, z/a, l/a^2 and m/a^2, so p' = (t a, t b, t^2 l, t z, t^2 m) with t = a'/a, and V(t.p) = t^5 V(p) forces
t^5 = 1.

Step C. On pa pl != 0 a fiber of V is one orbit of the fifth roots of unity on five distinct points, so V has degree
5, the induced map from P(1, 1, 2, 1, 2) is generically injective in characteristic 0 and hence birational onto its
image, which is irreducible of dimension 4 inside V(P5), irreducible of the same dimension, and so equals it. The
component is birational to a weighted projective space and is rational. The monomials of A span a toric variety of
degree 11 (the normalized volume of conv(A) in the lattice w^perp, summed over a unimodular triangulation that this
module verifies in exact integers), the degree of P5, and the difference lattice of A is all of w^perp, which gives
the same map degree 1 on the torus.

Step D. In ten parameters (p, q) the ideal I of the 17 differences V_k(p) - V_k(q), saturated by pa pl qa ql,
equals the ideal of the five graphs q = zeta . p (zeta^5 = 1) over Q(i). A component of dimension 5 of V(I) that
dominates a factor meets pa pl qa ql != 0: a general point of that factor has pa pl != 0, and V(p) = V(q) with the
rank 12 of step A gives ql qa^3 = pl pa^3, so ql and qa are nonzero; the component is then one of the five graphs.
The record names ideal containments: `graph_ideal_in_saturation` says the ideal of the graphs lies in the saturated
ideal (the variety of the saturation lies in the graphs) and `saturation_in_graph_ideal` says the converse. Two
controls reject: a mutated difference gives a saturated ideal that strictly contains the ideal of the graphs, a
variety of dimension 4 strictly inside them, and the four fourth roots of unity give an ideal that neither contains
the saturated ideal nor lies in it.

The fixture holds the 17 nonzero forms per basepoint as exact Q(i) coefficients. `--check` verifies steps A to C on
the fixture in exact integer and rational arithmetic and binds the record to the fixture, the producers and the
weight-slice record. `--check --replay` reruns Singular and compares the record bit for bit. Without a flag the
module regenerates the forms from the slice, requires them to equal the fixture, runs step D and writes the record.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_birational_degree.py [--check [--replay]]
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from math import comb, gcd
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e8_relation_ideal_orders as orders  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

# Exponents of (pa, pb, pl, pz, pm); a term is (real part, imaginary part, exponents) of a Gaussian integer coefficient.
Exponents = tuple[int, int, int, int, int]
Term = tuple[int, int, Exponents]
Form = tuple[Term, ...]

RECORD = HERE / "e8-birational-degree-result.json"
SCHEMA = "gororoba.a5.e8-birational-degree/1"
INPUTS = (
    "e8_birational_degree.py",
    "e8_relation_ideal_orders.py",
    "e8_quadric_nilradical.py",
    "weight_slice_fiber_relations.py",
)
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
ORBITS = orders.ORBITS
GENERATORS = orders.GENERATORS
PARAMETERS = orders.PARAMETERS
WEIGHTS: tuple[int, ...] = orders.ORDER_FUNCTIONS["prime5"][0]
DEGREE: int = orders.EXPECTED_ORDERS["prime5"]["ideal_order"]
COMPONENT_DEGREE: int = orders.EXPECTED_ORDERS["prime5"]["target"][1]
LENGTH = 5
QUOTIENT_DEGREE = DEGREE - WEIGHTS[2]
# The generators of the slice whose weight-5 part vanishes; the same at both basepoints.
ZERO_FORMS = (3, 5, 6, 7)
# pm = SHIFT * pz^2 - m is the graded change of variable of weight 2.
SHIFT = {"N-": 4, "N+": -4}
# The monomial set A of the quotients V_k / pl, in the order a^3, a^2 b, a b^2, b^3, a^2 z, a b z, b^2 z, a l, b l,
# z l, a m, b m.
MONOMIALS: tuple[Exponents, ...] = (
    (3, 0, 0, 0, 0),
    (2, 1, 0, 0, 0),
    (1, 2, 0, 0, 0),
    (0, 3, 0, 0, 0),
    (2, 0, 0, 1, 0),
    (1, 1, 0, 1, 0),
    (0, 2, 0, 1, 0),
    (1, 0, 1, 0, 0),
    (0, 1, 1, 0, 0),
    (0, 0, 1, 1, 0),
    (1, 0, 0, 0, 1),
    (0, 1, 0, 0, 1),
)
# A triangulation of conv(A) by 11 unimodular simplices; indices into MONOMIALS.
TRIANGULATION: tuple[tuple[int, ...], ...] = (
    (0, 1, 5, 7, 10),
    (0, 4, 5, 7, 10),
    (1, 2, 5, 8, 11),
    (1, 5, 7, 8, 10),
    (1, 5, 8, 10, 11),
    (2, 3, 6, 8, 11),
    (2, 5, 6, 8, 11),
    (4, 5, 7, 9, 10),
    (5, 6, 8, 9, 11),
    (5, 7, 8, 9, 10),
    (5, 8, 9, 10, 11),
)
EXPECTED_TORIC: dict[str, int] = {
    "quotient_degree": QUOTIENT_DEGREE,
    "points": len(MONOMIALS),
    "simplices": len(TRIANGULATION),
    "normalized_volume": COMPONENT_DEGREE,
    "difference_lattice_index": 1,
}
EXPECTED_CELL: dict[str, Any] = {
    "generators": GENERATORS,
    "nonzero_forms": GENERATORS - len(ZERO_FORMS),
    "zero_forms": list(ZERO_FORMS),
    "divisible_by_pl": GENERATORS - len(ZERO_FORMS),
    "monomials_before_change": 14,
    "monomials_after_change": len(MONOMIALS),
    "rank": len(MONOMIALS),
    "unsaturated_dimension": 8,
    "saturated_dimension": 5,
    "saturated_multiplicity": LENGTH,
    "graphs_dimension": 5,
    "graphs_multiplicity": LENGTH,
    "graph_ideal_in_saturation": True,
    "saturation_in_graph_ideal": True,
    # [dimension, degree, dominates the p factor, dominates the q factor]: over Q(i) the four primitive roots
    # form one Galois orbit of degree 4 and the diagonal has degree 1.
    "components": [[5, 1, True, True], [5, 4, True, True]],
    "controls": {
        "mutated_difference": {"dimension": 4, "graph_ideal_in_saturation": True, "saturation_in_graph_ideal": False},
        "fourth_roots": {"graph_ideal_in_saturation": False, "saturation_in_graph_ideal": False},
    },
}

# The 17 nonzero initial forms (and the four zero ones) of the 21 generators at each basepoint, extracted by the
# stage of `extraction_stage` over Q(i) and listed in generator order.
FIXTURE: dict[str, tuple[Form, ...]] = {
    "N-": (
        ((67108864, 0, (0, 3, 1, 0, 0)),),
        ((134217728, 0, (0, 2, 1, 1, 0)),),
        (),
        ((-67108864, 0, (1, 2, 1, 0, 0)),),
        (),
        (),
        (),
        ((0, 33554432, (0, 1, 2, 0, 0)),),
        ((67108864, 0, (0, 1, 1, 2, 0)), (-16777216, 0, (0, 1, 1, 0, 1))),
        ((0, -67108864, (0, 0, 2, 1, 0)),),
        ((134217728, 0, (1, 1, 1, 1, 0)), (67108864, 0, (0, 0, 2, 1, 0))),
        ((0, 33554432, (1, 0, 2, 0, 0)),),
        ((-67108864, 0, (2, 1, 1, 0, 0)), (-33554432, 0, (1, 0, 2, 0, 0))),
        ((0, 67108864, (0, 1, 1, 2, 0)), (0, -16777216, (0, 1, 1, 0, 1))),
        ((-134217728, 0, (1, 1, 1, 1, 0)), (67108864, 0, (0, 0, 2, 1, 0))),
        ((0, 67108864, (0, 0, 2, 1, 0)),),
        ((67108864, 0, (2, 1, 1, 0, 0)), (-33554432, 0, (1, 0, 2, 0, 0))),
        ((-67108864, 0, (1, 0, 1, 2, 0)), (16777216, 0, (1, 0, 1, 0, 1))),
        ((0, -67108864, (1, 0, 1, 2, 0)), (0, 16777216, (1, 0, 1, 0, 1))),
        ((134217728, 0, (2, 0, 1, 1, 0)),),
        ((-67108864, 0, (3, 0, 1, 0, 0)),),
    ),
    "N+": (
        ((67108864, 0, (0, 3, 1, 0, 0)),),
        ((134217728, 0, (0, 2, 1, 1, 0)),),
        (),
        ((-67108864, 0, (1, 2, 1, 0, 0)),),
        (),
        (),
        (),
        ((0, -33554432, (0, 1, 2, 0, 0)),),
        ((67108864, 0, (0, 1, 1, 2, 0)), (16777216, 0, (0, 1, 1, 0, 1))),
        ((0, 67108864, (0, 0, 2, 1, 0)),),
        ((134217728, 0, (1, 1, 1, 1, 0)), (67108864, 0, (0, 0, 2, 1, 0))),
        ((0, -33554432, (1, 0, 2, 0, 0)),),
        ((-67108864, 0, (2, 1, 1, 0, 0)), (-33554432, 0, (1, 0, 2, 0, 0))),
        ((0, -67108864, (0, 1, 1, 2, 0)), (0, -16777216, (0, 1, 1, 0, 1))),
        ((-134217728, 0, (1, 1, 1, 1, 0)), (67108864, 0, (0, 0, 2, 1, 0))),
        ((0, -67108864, (0, 0, 2, 1, 0)),),
        ((67108864, 0, (2, 1, 1, 0, 0)), (-33554432, 0, (1, 0, 2, 0, 0))),
        ((-67108864, 0, (1, 0, 1, 2, 0)), (-16777216, 0, (1, 0, 1, 0, 1))),
        ((0, 67108864, (1, 0, 1, 2, 0)), (0, 16777216, (1, 0, 1, 0, 1))),
        ((134217728, 0, (2, 0, 1, 1, 0)),),
        ((-67108864, 0, (3, 0, 1, 0, 0)),),
    ),
}


# ---------------------------------------------------------------------------------------------------------------------
# Steps A to C in exact arithmetic


def weighted_degree(exponents: Exponents) -> int:
    return sum(weight * exponent for weight, exponent in zip(WEIGHTS, exponents, strict=True))


def fixture_digest(forms: tuple[Form, ...]) -> str:
    return hashlib.sha256(json.dumps(forms, separators=(",", ":")).encode("utf-8")).hexdigest()


def change_variable(form: Form, shift: int | None) -> dict[Exponents, tuple[int, int]]:
    """The form after pm = shift * pz^2 - m, with m named pm again; `None` leaves the form unchanged."""
    result: dict[Exponents, tuple[int, int]] = {}
    for real, imaginary, (ea, eb, el, ez, em) in form:
        if shift is None:
            expansion = [(1, (ea, eb, el, ez, em))]
        else:
            expansion = [
                (comb(em, power) * shift**power * (-1) ** (em - power), (ea, eb, el, ez + 2 * power, em - power))
                for power in range(em + 1)
            ]
        for factor, key in expansion:
            old = result.get(key, (0, 0))
            result[key] = (old[0] + factor * real, old[1] + factor * imaginary)
    return {key: value for key, value in result.items() if value != (0, 0)}


def quotients(forms: tuple[Form, ...], shift: int | None) -> list[dict[Exponents, tuple[int, int]]]:
    """The nonzero forms divided by pl after the change of variable; every form must be divisible by pl."""
    return [
        {(ea, eb, el - 1, ez, em): value for (ea, eb, el, ez, em), value in change_variable(form, shift).items()}
        for form in forms
        if form
    ]


def _rank_over_q(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((index for index in range(rank, len(rows)) if rows[index][column] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][column] != 0:
                factor = rows[index][column] / rows[rank][column]
                rows[index] = [x - factor * y for x, y in zip(rows[index], rows[rank], strict=True)]
        rank += 1
    return rank


def gaussian_rank(matrix: list[list[tuple[int, int]]]) -> int:
    """The rank over Q(i) of a matrix of Gaussian integers: half the rank over Q of [[X, -Y], [Y, X]] for X + iY."""
    width = len(matrix[0])
    real = [[Fraction(0)] * (2 * width) for _ in range(2 * len(matrix))]
    for row, entries in enumerate(matrix):
        for column, (x, y) in enumerate(entries):
            real[2 * row][column], real[2 * row][width + column] = Fraction(x), Fraction(-y)
            real[2 * row + 1][column], real[2 * row + 1][width + column] = Fraction(y), Fraction(x)
    return _rank_over_q(real) // 2


def fixture_stats(forms: tuple[Form, ...], shift: int | None) -> dict[str, Any]:
    """Counts the checks of steps A and B read; the rank is None when a form is not divisible by pl."""
    nonzero = [form for form in forms if form]
    divisible = sum(1 for form in nonzero if all(term[2][2] >= 1 for term in form))
    stats: dict[str, Any] = {
        "generators": len(forms),
        "nonzero_forms": len(nonzero),
        "zero_forms": [index for index, form in enumerate(forms, 1) if not form],
        "divisible_by_pl": divisible,
        "monomials_before_change": None,
        "monomials_after_change": None,
        "rank": None,
    }
    if divisible != len(nonzero):
        return stats
    stats["monomials_before_change"] = len({key for q in quotients(forms, None) for key in q})
    changed = quotients(forms, shift)
    monomials = sorted({key for q in changed for key in q})
    stats["monomials_after_change"] = len(monomials)
    if set(monomials) == set(MONOMIALS):
        stats["rank"] = gaussian_rank([[q.get(key, (0, 0)) for key in MONOMIALS] for q in changed])
    return stats


def fixture_problems(orbit: str, forms: tuple[Form, ...], shift: int | None = None) -> list[str]:
    """Every way the forms of one basepoint fail steps A and B; `shift` replaces the change of variable of the orbit."""
    found: list[str] = []
    stats = fixture_stats(forms, SHIFT[orbit] if shift is None else shift)
    for key in ("generators", "nonzero_forms", "zero_forms", "divisible_by_pl"):
        if stats[key] != EXPECTED_CELL[key]:
            found.append(f"{orbit}: {key} is {stats[key]}, not {EXPECTED_CELL[key]}")
    for index, form in enumerate(forms, 1):
        exponents = [term[2] for term in form]
        if len(set(exponents)) != len(exponents) or any((term[0], term[1]) == (0, 0) for term in form):
            found.append(f"{orbit}: form {index} repeats a monomial or holds a zero coefficient")
        degrees = {weighted_degree(exponent) for exponent in exponents}
        if degrees - {DEGREE}:
            found.append(f"{orbit}: form {index} has weighted degree {sorted(degrees)}, not {DEGREE}")
    if found:
        return found
    if stats["monomials_before_change"] != EXPECTED_CELL["monomials_before_change"]:
        found.append(f"{orbit}: the unchanged quotients carry {stats['monomials_before_change']} monomials")
    if stats["monomials_after_change"] != EXPECTED_CELL["monomials_after_change"] or stats["rank"] is None:
        found.append(f"{orbit}: the changed quotients carry {stats['monomials_after_change']} monomials, not the set A")
    elif stats["rank"] != EXPECTED_CELL["rank"]:
        found.append(f"{orbit}: the coefficient matrix has rank {stats['rank']}, not {EXPECTED_CELL['rank']}")
    return found


def ratio_problems(monomials: tuple[Exponents, ...] = MONOMIALS) -> list[str]:
    """Step B: a^3 and the four monomials a^3 e_c / a^(w_c) of A give the ratios c / a^(w_c) of the coordinates."""
    found: list[str] = []
    if WEIGHTS[0] != 1 or monomials[0] != (QUOTIENT_DEGREE, 0, 0, 0, 0):
        found.append("the first coordinate has weight 1 and a^3 leads the monomials")
    for column in range(1, LENGTH):
        expected = [QUOTIENT_DEGREE, 0, 0, 0, 0]
        expected[0] -= WEIGHTS[column]
        expected[column] += 1
        if tuple(expected) not in monomials:
            found.append(f"the monomial {tuple(expected)} that fixes the ratio of coordinate {column} is missing")
    return found


def _determinant(matrix: list[list[int]]) -> int:
    rows = [[Fraction(x) for x in row] for row in matrix]
    value = Fraction(1)
    for column in range(len(rows)):
        pivot = next((index for index in range(column, len(rows)) if rows[index][column] != 0), None)
        if pivot is None:
            return 0
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            value = -value
        value *= rows[column][column]
        for index in range(column + 1, len(rows)):
            factor = rows[index][column] / rows[column][column]
            rows[index] = [x - factor * y for x, y in zip(rows[index], rows[column], strict=True)]
    if value.denominator != 1:
        raise ValueError("a determinant of integers is an integer")
    return int(value)


def _lattice(exponents: Exponents) -> list[int]:
    # The first coordinate has weight 1, so the other four coordinates are lattice coordinates on w . e = const.
    return list(exponents[1:])


def _side(facet: tuple[int, ...], other: int, points: list[list[int]]) -> int:
    base = points[facet[0]]
    rows = [[x - y for x, y in zip(points[index], base, strict=True)] for index in facet[1:]]
    rows.append([x - y for x, y in zip(points[other], base, strict=True)])
    return _determinant(rows)


def lattice_problems(
    monomials: tuple[Exponents, ...] = MONOMIALS, simplices: tuple[tuple[int, ...], ...] = TRIANGULATION
) -> tuple[list[str], dict[str, int]]:
    """Step C in the lattice w^perp: the triangulation is exact, its volume is 11 and its edges span the lattice.

    The pseudomanifold test is the exact content of the claim that the simplices triangulate conv(A): every interior
    facet lies in two simplices on opposite sides, and every boundary facet carries all 12 points on one side, so the
    simplices cover the hull once.
    """
    found: list[str] = []
    if any(weighted_degree(m) != QUOTIENT_DEGREE for m in monomials):
        found.append("a monomial of A leaves the hyperplane of weighted degree 3")
    points = [_lattice(m) for m in monomials]
    volumes = [
        abs(_determinant([[x - y for x, y in zip(points[v], points[s[0]], strict=True)] for v in s[1:]]))
        for s in simplices
    ]
    if 0 in volumes:
        found.append("a simplex of the triangulation is degenerate")
    facets: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for position, simplex in enumerate(simplices):
        for dropped in simplex:
            facets.setdefault(tuple(v for v in simplex if v != dropped), []).append((position, dropped))
    for facet, owners in facets.items():
        if len(owners) == 2:
            first, second = (_side(facet, dropped, points) for _, dropped in owners)
            if first * second >= 0:
                found.append(f"the simplices at the facet {facet} lie on one side")
        elif len(owners) == 1:
            signs = {
                _side(facet, index, points) > 0 for index in range(len(points)) if _side(facet, index, points) != 0
            }
            if len(signs) > 1:
                found.append(f"the boundary facet {facet} does not support the hull")
        else:
            found.append(f"the facet {facet} lies in {len(owners)} simplices")
    index = 0
    for volume in volumes:
        index = gcd(index, volume)
    summary = {
        "quotient_degree": QUOTIENT_DEGREE,
        "points": len(monomials),
        "simplices": len(simplices),
        "normalized_volume": sum(volumes),
        "difference_lattice_index": index,
    }
    return found, summary


def toric_problems() -> list[str]:
    found, summary = lattice_problems()
    for key, expected in EXPECTED_TORIC.items():
        if summary[key] != expected:
            found.append(f"toric {key} is {summary[key]}, not {expected}")
    return found + ratio_problems()


def all_fixture_problems() -> list[str]:
    found = toric_problems()
    for orbit in ORBITS:
        found += fixture_problems(orbit, FIXTURE[orbit])
    return found


# ---------------------------------------------------------------------------------------------------------------------
# Extraction of the forms and the ideal test of step D in Singular


def parse_form(text: str) -> Form:
    """A Singular polynomial in (pa, pb, pl, pz, pm) over Q(i) as exact Gaussian-integer terms in canonical order."""
    if text.strip() == "0":
        return ()
    symbols = sp.symbols(PARAMETERS)
    names: dict[str, Any] = {str(symbol): symbol for symbol in symbols}
    names["i"] = sp.I
    polynomial = sp.Poly(sp.expand(sp.sympify(text.replace("^", "**"), locals=names)), *symbols)
    terms: list[Term] = []
    for monomial, coefficient in sorted(polynomial.terms(), reverse=True):
        real, imaginary = coefficient.as_real_imag()
        if not (real.is_integer and imaginary.is_integer):
            raise ValueError(f"the coefficient {coefficient} is not a Gaussian integer")
        exponents = tuple(int(exponent) for exponent in monomial)
        if len(exponents) != LENGTH:
            raise ValueError("a monomial of the forms has five exponents")
        terms.append(
            (int(real), int(imaginary), (exponents[0], exponents[1], exponents[2], exponents[3], exponents[4]))
        )
    return tuple(terms)


EXTRACTION = """
ring P=(0,i),(pa,pb,pl,pz,pm),dp; minpoly=i^2+1; option(redSB);
map ph=r,$mapping;
ideal gp=ph(G);
intvec wv=$weights; ideal V; int k;
for(k=1;k<=$generators;k++){ V[k]=jet(gp[k],$degree,wv); }
for(k=1;k<=$generators;k++){ print("RESULT form "+string(k)+" "+string(V[k])); }
"""


def extraction_stage(orbit: str) -> str:
    """The Singular statements, appended to the weight-slice script, that print the initial forms of weight 5."""
    return ws.SELECTION_STAGE + (
        EXTRACTION.replace("$mapping", ",".join(orders.PARAMETRIZATION[orbit]))
        .replace("$weights", ",".join(str(weight) for weight in WEIGHTS))
        .replace("$generators", str(GENERATORS))
        .replace("$degree", str(DEGREE))
    )


def _polynomial(form: Form, names: tuple[str, ...]) -> str:
    terms = []
    for real, imaginary, exponents in form:
        monomial = "*".join(f"{name}^{exponent}" for name, exponent in zip(names, exponents, strict=True) if exponent)
        terms.append(f"(({real})+({imaginary})*i)*{monomial or '1'}")
    return "+".join(terms)


FIRST = ("pa", "pb", "pl", "pz", "pm")
SECOND = ("qa", "qb", "ql", "qz", "qm")
GRAPH = "qa-t*pa,qb-t*pb,ql-t^2*pl,qz-t*pz,qm-t^2*pm"
SATURATION_FACTOR = "pa*pl*qa*ql"
MUTATION = "pa*pl*qa*qb*qz"
IDEAL_STAGE = """LIB "elim.lib"; LIB "primdec.lib";
ring R=(0,i),(pa,pb,pl,pz,pm,qa,qb,ql,qz,qm),dp; minpoly=i^2+1; option(redSB);
ideal I=$differences;
poly h=$factor;
print("RESULT unsaturated_dimension "+string(dim(std(I))));
print("RESULT saturation_type "+typeof(sat(ideal(1),ideal(1))));
ideal S=sat(I,h); ideal sS=std(S);
print("RESULT saturated "+string(dim(sS))+","+string(mult(sS)));
ring T=(0,i),(pa,pb,pl,pz,pm,qa,qb,ql,qz,qm,t),dp; minpoly=i^2+1; option(redSB);
ideal Gt=$graph,t^$length-1; ideal Gam=eliminate(Gt,t);
ideal Gt4=$graph,t^$wrong-1; ideal Gam4=eliminate(Gt4,t);
setring R;
ideal Gm=std(fetch(T,Gam)); ideal Gm4=std(fetch(T,Gam4));
print("RESULT graphs "+string(dim(Gm))+","+string(mult(Gm)));
print("RESULT graph_ideal_in_saturation "+string(size(reduce(Gm,sS))==0));
print("RESULT saturation_in_graph_ideal "+string(size(reduce(S,Gm))==0));
ideal I3=I; I3[3]=I3[3]+$mutation; ideal S3=std(sat(I3,h));
print("RESULT mutated_difference "+string(dim(S3))+","+string(size(reduce(Gm,S3))==0)
  +","+string(size(reduce(S3,Gm))==0));
print("RESULT fourth_roots "+string(size(reduce(Gm4,sS))==0)+","+string(size(reduce(S,Gm4))==0));
list CS=minAssGTZ(S); int ci; ideal Cc;
for(ci=1;ci<=size(CS);ci++){ Cc=std(CS[ci]);
  print("RESULT component "+string(dim(Cc))+","+string(mult(Cc))
    +","+string(size(simplify(eliminate(Cc,qa*qb*ql*qz*qm),2))==0)
    +","+string(size(simplify(eliminate(Cc,pa*pb*pl*pz*pm),2))==0)); }
print("RESULT done 1");
quit;
"""


def ideal_stage(forms: tuple[Form, ...]) -> str:
    """The Singular script of step D for the nonzero forms of one basepoint."""
    differences = ",\n".join(f"({_polynomial(form, FIRST)})-({_polynomial(form, SECOND)})" for form in forms if form)
    return (
        IDEAL_STAGE.replace("$differences", differences)
        .replace("$factor", SATURATION_FACTOR)
        .replace("$graph", GRAPH)
        .replace("$length", str(LENGTH))
        .replace("$wrong", str(LENGTH - 1))
        .replace("$mutation", MUTATION)
    )


def _integers(text: str) -> list[int]:
    return [int(part) for part in text.split(",")]


def ideal_record(values: dict[str, list[str]]) -> dict[str, Any]:
    """The step D results of one basepoint from the RESULT lines of `ideal_stage`."""
    if values["saturation_type"] != ["ideal"]:
        raise RuntimeError(f"sat returns {values['saturation_type']}, not an ideal")
    saturated, graphs = _integers(values["saturated"][0]), _integers(values["graphs"][0])
    mutated, fourth = _integers(values["mutated_difference"][0]), _integers(values["fourth_roots"][0])
    return {
        "unsaturated_dimension": int(values["unsaturated_dimension"][0]),
        "saturated_dimension": saturated[0],
        "saturated_multiplicity": saturated[1],
        "graphs_dimension": graphs[0],
        "graphs_multiplicity": graphs[1],
        "graph_ideal_in_saturation": values["graph_ideal_in_saturation"] == ["1"],
        "saturation_in_graph_ideal": values["saturation_in_graph_ideal"] == ["1"],
        "components": sorted([c[0], c[1], c[2] == 1, c[3] == 1] for c in map(_integers, values["component"])),
        "controls": {
            "mutated_difference": {
                "dimension": mutated[0],
                "graph_ideal_in_saturation": mutated[1] == 1,
                "saturation_in_graph_ideal": mutated[2] == 1,
            },
            "fourth_roots": {"graph_ideal_in_saturation": fourth[0] == 1, "saturation_in_graph_ideal": fourth[1] == 1},
        },
    }


# ---------------------------------------------------------------------------------------------------------------------
# The record and its checker


def certify(orbit: str) -> dict[str, Any]:
    marker = 'print("RESULT done 1");'
    script = ws.fiber_script(ws.orbit_task(orbit), "e8", 0, 0, through_pfaffians_only=True)
    if script.count(marker) != 1:
        raise RuntimeError("the weight-slice script has no single end marker")
    extraction = ws.run_singular(script.replace(marker, extraction_stage(orbit) + marker))["values"]
    extracted = tuple(parse_form(text.split(" ", 1)[1]) for text in extraction["form"])
    if extracted != FIXTURE[orbit]:
        raise RuntimeError(f"{orbit}: the forms extracted from the slice differ from the fixture")
    stats = fixture_stats(FIXTURE[orbit], SHIFT[orbit])
    ideal = ideal_record(ws.run_singular(ideal_stage(FIXTURE[orbit]))["values"])
    return {
        "orbit": orbit,
        "forms_sha256": fixture_digest(FIXTURE[orbit]),
        "generator_weights": [int(weight) for weight in extraction["generator_weights"][0].split(",")],
        "change_of_variable": SHIFT[orbit],
        **stats,
        **ideal,
    }


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("field") != "Q(i)":
        found.append("the field differs from Q(i)")
    if record.get("toric") != EXPECTED_TORIC:
        found.append(f"toric differs from {EXPECTED_TORIC}")
    cells = record.get("cells", [])
    if [cell.get("orbit") for cell in cells] != list(ORBITS):
        found.append("the cells are not N- and N+ in order")
        return found
    for cell in cells:
        orbit = cell["orbit"]
        for key, expected in EXPECTED_CELL.items():
            if cell.get(key) != expected:
                found.append(f"{orbit}: {key} differs from {expected}")
        if cell.get("change_of_variable") != SHIFT[orbit]:
            found.append(f"{orbit}: change_of_variable differs from {SHIFT[orbit]}")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def binding_problems(record: dict[str, Any]) -> list[str]:
    """The record against the fixture constants: the digest of each basepoint's forms."""
    return [
        f"{cell['orbit']}: forms_sha256 differs from the digest of the fixture"
        for cell in record.get("cells", [])
        if cell.get("forms_sha256") != fixture_digest(FIXTURE[cell["orbit"]])
    ]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice_problems(record: dict[str, Any]) -> list[str]:
    """The generator count and weights against the E8-bar cells over Q(i) of the weight-slice record."""
    retained = {
        cell["orbit"]: (cell["generator_count"], cell["generator_weights"])
        for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0 and cell["source"] == "e8"
    }
    return [
        f"{cell['orbit']}: the generators differ from those of the weight-slice record"
        for cell in record.get("cells", [])
        if (cell.get("generators"), cell.get("generator_weights")) != retained.get(cell["orbit"])
    ]


def build() -> dict[str, Any]:
    _, toric = lattice_problems()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "weight_slice_record_sha256": _digest(WEIGHT_SLICE),
        "toric": toric,
        "cells": parallel.ordered_map(certify, list(ORBITS), min_items=2),
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def check(record: dict[str, Any]) -> list[str]:
    found = problems(record) + binding_problems(record) + slice_problems(record) + all_fixture_problems()
    for name in INPUTS:
        if record.get("inputs", {}).get(name) != _digest(HERE / name):
            found.append(f"input digest of {name} differs")
    if record.get("weight_slice_record_sha256") != _digest(WEIGHT_SLICE):
        found.append("digest of the weight-slice record differs")
    return found


def main() -> None:
    arguments = sys.argv[1:]
    if "--check" in arguments:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = check(record)
        if "--replay" in arguments and build() != record:
            found.append("a fresh run differs from the record")
        if found:
            raise SystemExit("\n".join(found))
        print("e8-birational-degree-result.json: pass")
        return
    record = build()
    found = problems(record) + slice_problems(record) + all_fixture_problems()
    record["pass"] = found == []
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
