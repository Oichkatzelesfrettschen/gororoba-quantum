"""Exact refutation of the half-rotation composite as a 15-dimensional piece of D_(5,12) through {e_i, 0}.

At the nonzd-axis witnesses x0 = {e_i, 0} = (e_i, -e_8 e_i), i = 1, 2, 3, of
rank_locus_local_dimension.py, rank_locus_second_order.rotation_curve turns
one half of x = (p, q) toward that half's e_8 and keeps nullity 12. The
candidate piece composes both turns over the {a, 0} family. On the slice
a = ((1 - beta^2 - gamma^2) e_i + 2 beta e_(i+8) + 2 gamma e_(j+8)) / n,
n = 1 + beta^2 + gamma^2, of unit vectors, |p| = |q| = n before division
and sigma = n s, tau = n t give

    Psi = ((1 - sigma^2)(1 + tau^2) p + 2 n sigma (1 + tau^2) e_8,
           (1 + sigma^2)(1 - tau^2) q + 2 n tau (1 + sigma^2) e_24),

which at tau = 0 or sigma = 0 equals rotation_curve(x, 0) or
rotation_curve(x, 1) at u = sigma / n or tau / n.

Rank L_Psi above 20 at one rational point exhibits a nonzero 21-minor, a
polynomial in (beta, gamma, sigma, tau), so the composite leaves D_(5,12)
on an open dense set of its parameters. The record retains:

- the composite at x0 (beta = gamma = 0, sigma = 2, tau = 3): exact rank;
- each single turn at the same parameter: rank 20, the certified curves;
- single turns from slice points with u and v parallel (gamma = 0) and
  from generic slice points: exact ranks;
- the tangent bound 31 - rank(y -> U^T L_y V) at generic {a, 0} points,
  which places the two-dimension gap on the whole family.

Falsifier, stated before the run: rank 20 at every composite point would
leave the composite a candidate piece; the record requires rank above 20 at
x0.

Usage:
    "$PYTHON" scripts/rank_locus_rotation_composite.py --out PATH
    "$PYTHON" scripts/rank_locus_rotation_composite.py --check PATH
    "$PYTHON" scripts/rank_locus_rotation_composite.py --self-test
    "$PYTHON" scripts/rank_locus_rotation_composite.py --audit-out PATH
    "$PYTHON" scripts/rank_locus_rotation_composite.py --audit-check PATH

--audit-out runs on the build host: hyprat and python-hypercomplex rebuild
L at every retained point and annihilate the kernel at x0 (docs/notes/packages/),
and SageMath 10.10 recomputes der(O) and the related-triple algebra of A_5
with its orbit dimensions on the family. --audit-check recomputes the
cd_core side of every retained comparison without importing any package.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import rank_locus_gap_directions as gap  # noqa: E402
from d_locus_nullity import bracket, left_rational  # noqa: E402
from rank_locus_local_dimension import tangent_bound  # noqa: E402
from rank_locus_second_order import rotation_curve  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-rotation-composite-v1"
AUDIT_SCHEMA = "rank-locus-rotation-composite-audit-v1"
AUDIT_PATH = ROOT / "docs/evidence/rank_locus_rotation_composite/audit.json"
DIM = 32
HALF = 16
I4 = 8
EXIT = (8, 24)
NULLITY = 12
RANK = DIM - NULLITY
WITNESS_UNITS = (1, 2, 3)
COMPOSITE = (Fraction(2), Fraction(3))
TURN = Fraction(5, 3)
PARALLEL_SLICE = ((Fraction(1), Fraction(0)), (Fraction(-2, 5), Fraction(0)))
GENERIC_SLICE = ((Fraction(1), Fraction(2)), (Fraction(1, 3), Fraction(-2, 7)))
GENERIC_FAMILY = (
    (0, 1, 2, -1, 3, 1, 0, 2, 0, 1, -2, 1, 1, 3, -1, 2),
    (0, Fraction(1, 3), -2, 0, 5, 0, 1, -1, 0, 0, 3, -1, 0, 2, Fraction(1, 2), 1),
    (0, -3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0),
)
Vector = list[Fraction]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_rotation_composite: {message}")


def partner(unit: int) -> int:
    """The slice's second octonion unit j != i."""
    return unit % 7 + 1


def slice_point(unit: int, beta: Fraction, gamma: Fraction) -> tuple[Vector, Fraction]:
    """n times the stereographic unit a(beta, gamma), and n."""
    a = [Fraction(0)] * HALF
    a[unit] = 1 - beta * beta - gamma * gamma
    a[unit + I4] = 2 * beta
    a[partner(unit) + I4] = 2 * gamma
    return a, 1 + beta * beta + gamma * gamma


def psi(unit: int, beta: Fraction, gamma: Fraction, sigma: Fraction, tau: Fraction) -> Vector:
    a, n = slice_point(unit, beta, gamma)
    x = bracket(a, [Fraction(0)] * HALF)
    for half in (x[:HALF], x[HALF:]):
        _require(sum((v * v for v in half), Fraction(0)) == n * n, "a half of {a, 0} does not have norm n")
    out = [(1 - sigma * sigma) * (1 + tau * tau) * v for v in x[:HALF]]
    out += [(1 + sigma * sigma) * (1 - tau * tau) * v for v in x[HALF:]]
    out[EXIT[0]] += 2 * n * sigma * (1 + tau * tau)
    out[EXIT[1]] += 2 * n * tau * (1 + sigma * sigma)
    return out


def single_turn(x: Vector, half: int, u: Fraction) -> Vector:
    v, w, _ = rotation_curve(x, half)
    return [a + u * b + u * u * c for a, b, c in zip(x, v, w, strict=True)]


def left(v: Vector) -> list[Fraction]:
    """L_v row-major: L_v[r][c] = sign(r ^ c, c) v[r ^ c] (cd_core.cd_sign)."""
    return [cd_sign(DIM, r ^ c, c) * v[r ^ c] for r in range(DIM) for c in range(DIM)]


def operator(v: Vector) -> flint.fmpq_mat:
    return flint.fmpq_mat(DIM, DIM, [flint.fmpq(value.numerator, value.denominator) for value in left(v)])


def rank(v: Vector) -> int:
    return int(operator(v).rank())


def encode(v: Vector) -> list[str]:
    return [str(value) for value in v]


def points(unit: int) -> list[dict[str, Any]]:
    """Every retained point of one witness, labeled, with its parameters."""
    zero = Fraction(0)
    sigma, tau = COMPOSITE
    out = [
        {"label": "witness", "params": [zero, zero, zero, zero]},
        {"label": "composite", "params": [zero, zero, sigma, tau]},
        {"label": "upper-turn", "params": [zero, zero, sigma, zero]},
        {"label": "lower-turn", "params": [zero, zero, zero, tau]},
    ]
    for kind, nodes in (("parallel", PARALLEL_SLICE), ("generic", GENERIC_SLICE)):
        for beta, gamma in nodes:
            out.append({"label": f"{kind}-family", "params": [beta, gamma, zero, zero]})
            out.append({"label": f"{kind}-upper-turn", "params": [beta, gamma, TURN, zero]})
            out.append({"label": f"{kind}-lower-turn", "params": [beta, gamma, zero, TURN]})
    return out


def witness_row(unit: int) -> dict[str, Any]:
    x0 = psi(unit, Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    sigma, tau = COMPOSITE
    curves_agree = psi(unit, Fraction(0), Fraction(0), sigma, Fraction(0)) == single_turn(x0, 0, sigma) and psi(
        unit, Fraction(0), Fraction(0), Fraction(0), tau
    ) == single_turn(x0, 1, tau)
    rows = []
    for entry in points(unit):
        point = psi(unit, *entry["params"])
        rows.append({"label": entry["label"], "params": [str(v) for v in entry["params"]], "rank": rank(point)})
    return {
        "unit": unit,
        "partner": partner(unit),
        "x0": encode(x0),
        "turns_equal_rotation_curve": curves_agree,
        "differential_rank_cone": differential_rank(unit),
        "points": rows,
    }


def differential_rank(unit: int) -> int:
    """Exact rank on the cone of the candidate's differential at x0: 14 family directions and both turn velocities.

    Psi is quadratic in sigma and in tau, so (Psi(1) - Psi(-1)) / 2 is its
    exact partial derivative at 0.
    """
    zero = [Fraction(0)] * HALF
    one, half = Fraction(1), Fraction(1, 2)
    columns = [bracket([Fraction(int(k == m)) for k in range(HALF)], zero) for m in range(HALF) if m not in (0, I4)]
    for plus, minus in (
        (psi(unit, Fraction(0), Fraction(0), one, Fraction(0)), psi(unit, Fraction(0), Fraction(0), -one, Fraction(0))),
        (psi(unit, Fraction(0), Fraction(0), Fraction(0), one), psi(unit, Fraction(0), Fraction(0), Fraction(0), -one)),
    ):
        columns.append([half * (a - b) for a, b in zip(plus, minus, strict=True)])
    entries = [flint.fmpq(v.numerator, v.denominator) for column in columns for v in column]
    return int(flint.fmpq_mat(len(columns), DIM, entries).rank())


def family_row(index: int) -> dict[str, Any]:
    a = [Fraction(v) for v in GENERIC_FAMILY[index]]
    a_rank = flint.fmpq_mat(
        HALF, HALF, [flint.fmpq(v.numerator, v.denominator) for row in left_rational(HALF, a) for v in row]
    ).rank()
    return {"a": encode(a), "a4_rank": int(a_rank), **tangent_bound(bracket(a, [Fraction(0)] * HALF))}


def _task(item: tuple[str, int]) -> dict[str, Any]:
    kind, index = item
    return witness_row(index) if kind == "witness" else family_row(index)


def run() -> dict[str, Any]:
    items = [("witness", unit) for unit in WITNESS_UNITS] + [("family", k) for k in range(len(GENERIC_FAMILY))]
    rows = parallel.ordered_map(_task, items, min_items=2)
    return {
        "schema": SCHEMA,
        "composite": [str(v) for v in COMPOSITE],
        "turn": str(TURN),
        "witnesses": rows[: len(WITNESS_UNITS)],
        "family_tangent_bounds": rows[len(WITNESS_UNITS) :],
    }


def verdicts(record: dict[str, Any]) -> list[str]:
    """Every rule the record must satisfy; an empty list is a passing record."""
    failures = []
    for row in record["witnesses"]:
        ranks = {(p["label"], tuple(p["params"])): p["rank"] for p in row["points"]}
        by_label: dict[str, list[int]] = {}
        for (label, _), value in ranks.items():
            by_label.setdefault(label, []).append(value)
        unit = row["unit"]
        if not row["turns_equal_rotation_curve"]:
            failures.append(f"{unit}: a single turn differs from rotation_curve")
        if row["differential_rank_cone"] != 16:
            failures.append(f"{unit}: the differential at x0 does not have rank 16 on the cone")
        for label in (
            "witness",
            "upper-turn",
            "lower-turn",
            "parallel-family",
            "generic-family",
            "parallel-upper-turn",
            "parallel-lower-turn",
        ):
            if not by_label.get(label) or any(value != RANK for value in by_label[label]):
                failures.append(f"{unit}: {label} does not have rank {RANK}")
        composite = by_label.get("composite", [])
        if not composite or any(value <= RANK for value in composite):
            failures.append(f"{unit}: the composite keeps nullity {NULLITY}")
        generic = by_label.get("generic-upper-turn", []) + by_label.get("generic-lower-turn", [])
        if len(generic) != 2 * len(GENERIC_SLICE) or any(value <= RANK for value in generic):
            failures.append(f"{unit}: a turn from a generic family point keeps nullity {NULLITY}")
    for row in record["family_tangent_bounds"]:
        if row["a4_rank"] != HALF or row["nullity"] != NULLITY or row["dimension_upper_bound"] != 15:
            failures.append(f"family point {row['a']}: not a nullity-12 point with tangent bound 15")
    return failures


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1) + "\n"


def retained_points(record: dict[str, Any]) -> list[tuple[int, list[Fraction]]]:
    return [(row["unit"], [Fraction(v) for v in p["params"]]) for row in record["witnesses"] for p in row["points"]]


def l_digest(v: Vector) -> str:
    return hashlib.sha256(json.dumps(encode(left(v))).encode()).hexdigest()


def kernel_basis(point: Vector) -> list[Vector]:
    rref, found = operator(point).rref()
    _require(found == RANK, "the witness operator does not have rank 20")
    entries = [[Fraction(int(rref[r, c].p), int(rref[r, c].q)) for c in range(DIM)] for r in range(found)]
    pivots = [next(c for c in range(DIM) if entries[r][c]) for r in range(found)]
    basis = []
    for free in (c for c in range(DIM) if c not in pivots):
        v = [Fraction(0)] * DIM
        v[free] = Fraction(1)
        for r, p in enumerate(pivots):
            v[p] = -entries[r][free]
        basis.append(v)
    return basis


def product_cd(x: Vector, y: Vector) -> Vector:
    table = left(x)
    return [sum((table[r * DIM + c] * y[c] for c in range(DIM)), Fraction(0)) for r in range(DIM)]


def _kernel_task(unit: int) -> dict[str, Any]:
    x0 = psi(unit, Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    basis = kernel_basis(x0)
    _require(all(not any(product_cd(x0, v)) for v in basis), "a cd_core kernel vector is not annihilated")
    return {
        "dimension": len(basis),
        "sha256": hashlib.sha256(json.dumps([encode(v) for v in basis]).encode()).hexdigest(),
    }


def _digest_task(item: tuple[int, list[Fraction]]) -> dict[str, Any]:
    unit, params = item
    return {"unit": unit, "params": [str(v) for v in params], "l_sha256": l_digest(psi(unit, *params))}


def audit_core(record: dict[str, Any]) -> dict[str, Any]:
    """The cd_core side of every package comparison: L digests at each retained point and the kernel at x0."""
    nodes = parallel.ordered_map(_digest_task, retained_points(record), min_items=2)
    kernels = parallel.ordered_map(_kernel_task, list(WITNESS_UNITS), min_items=2)
    return {"nodes": nodes, "kernels": {str(unit): k for unit, k in zip(WITNESS_UNITS, kernels, strict=True)}}


def package_product(name: str) -> Any:
    """x * y in hyprat or python-hypercomplex, exact over Q, each bound to its installed distribution."""
    from algebra_package_tables import require_bound

    if name == "hyprat":
        import hyprat

        require_bound(hyprat, "hyprat")
        return lambda x, y: [Fraction(v) for v in (hyprat.Hy.from_array(x) * hyprat.Hy.from_array(y)).to_array()]
    import hypercomplex

    require_bound(hypercomplex, "hypercomplex")
    algebra = hypercomplex.cayley_dickson_algebra(5, Fraction)
    return lambda x, y: [Fraction(v) for v in (algebra(*x) * algebra(*y)).coefficients()]


def _package_task(item: tuple[str, str, dict[str, Any] | int]) -> bool:
    """One package check: an L table at a retained node equals cd_core's digest, or x0's kernel is annihilated."""
    name, kind, payload = item
    product = package_product(name)
    if kind == "kernel":
        assert isinstance(payload, int)
        x0 = psi(payload, Fraction(0), Fraction(0), Fraction(0), Fraction(0))
        return all(not any(product(x0, v)) for v in kernel_basis(x0))
    assert isinstance(payload, dict)
    point = psi(payload["unit"], *[Fraction(v) for v in payload["params"]])
    columns = [product(point, [Fraction(int(k == c)) for k in range(DIM)]) for c in range(DIM)]
    table = [columns[c][r] for r in range(DIM) for c in range(DIM)]
    return hashlib.sha256(json.dumps(encode(table)).encode()).hexdigest() == payload["l_sha256"]


def audit_packages(core: dict[str, Any]) -> dict[str, Any]:
    """hyprat and python-hypercomplex rebuild L at each retained point and annihilate the kernel at x0."""
    out: dict[str, Any] = {}
    for name in ("hyprat", "hypercomplex"):
        tables = parallel.ordered_map(_package_task, [(name, "node", node) for node in core["nodes"]], min_items=2)
        kernels = parallel.ordered_map(_package_task, [(name, "kernel", unit) for unit in WITNESS_UNITS], min_items=2)
        out[name] = {"l_tables_equal_cd_core": all(tables), "kernel_annihilated": all(kernels)}
    return out


def audit_sage() -> dict[str, Any]:
    """SageMath: der(O) from OctonionAlgebra(QQ), and the related triples of A_5 with their orbits on the family.

    A related triple (D1, D2, D3) satisfies D1(x y) = D2(x) y + x D3(y); the
    flow of D2 multiplies L_x by invertible maps on both sides, so it
    preserves nullity. The orbit dimension at a family point is the rank of
    {D2 x}.
    """
    import hypercomplex
    import sage.version
    from sage.all import QQ, OctonionAlgebra, matrix, vector

    basis = OctonionAlgebra(QQ).basis()
    n = 8
    coords = {(i, j): list((basis[i] * basis[j]).vector()) for i in range(n) for j in range(n)}
    equations: dict[tuple[int, int], int] = {}
    row = 0
    for i in range(n):
        for j in range(n):
            for r in range(n):
                for c in range(n):
                    if coords[i, j][c]:
                        equations[row, r * n + c] = equations.get((row, r * n + c), 0) + coords[i, j][c]
                for k in range(n):
                    if coords[k, j][r]:
                        equations[row, k * n + i] = equations.get((row, k * n + i), 0) - coords[k, j][r]
                    if coords[i, k][r]:
                        equations[row, k * n + j] = equations.get((row, k * n + j), 0) - coords[i, k][r]
                row += 1
    sage_der = matrix(QQ, row, n * n, equations, sparse=True).right_kernel_matrix()
    flip = [(-1 if k in (3, 5, 6) else 1) for k in range(n)]
    repo_der = matrix(
        QQ, [[flip[r] * d[r][c] * flip[c] for r in range(n) for c in range(n)] for d in gap.derivations()]
    )
    der_equal = sage_der.rank() == repo_der.rank() == sage_der.stack(repo_der).rank()

    algebra = hypercomplex.cayley_dickson_algebra(5)
    sign = {}
    for i in range(DIM):
        for j in range(DIM):
            coeffs = [int(v) for v in (algebra.e(i) * algebra.e(j)).coefficients()]
            _require([k for k in range(DIM) if coeffs[k]] == [i ^ j], f"hypercomplex e{i} e{j} is not e{i ^ j}")
            sign[i, j] = coeffs[i ^ j]
    size = DIM * DIM
    triples: dict[tuple[int, int], int] = {}
    row = 0
    for i in range(DIM):
        for j in range(DIM):
            for r in range(DIM):
                for key, value in (
                    ((row, r * DIM + (i ^ j)), sign[i, j]),
                    ((row, size + (r ^ j) * DIM + i), -sign[r ^ j, j]),
                    ((row, 2 * size + (i ^ r) * DIM + j), -sign[i, i ^ r]),
                ):
                    triples[key] = triples.get(key, 0) + value
                row += 1
    kernel = matrix(QQ, row, 3 * size, triples, sparse=True).right_kernel_matrix()
    middle = [matrix(QQ, DIM, DIM, list(k[size : 2 * size])) for k in kernel.rows()]
    span = matrix(QQ, [m.list() for m in middle])
    diag = []
    for d in gap.derivations():
        full = [[0] * DIM for _ in range(DIM)]
        for r in range(HALF):
            for c in range(HALF):
                full[r][c] = full[r + HALF][c + HALF] = d[r][c]
        diag.append(sum(full, []))
    named = matrix(QQ, diag + [[int(r == c) for r in range(DIM) for c in range(DIM)]])
    extras = []
    grown = named
    for m in middle:
        if grown.stack(matrix(QQ, [m.list()])).rank() > grown.rank():
            grown = grown.stack(matrix(QQ, [m.list()]))
            extras.append(
                [[r, c, str(m[r, c])] for r in range(DIM) for c in EXIT if m[r, c] and (r < HALF) != (c < HALF)]
            )
    zero = [Fraction(0)] * HALF
    family = matrix(
        QQ, [bracket([Fraction(int(k == m)) for k in range(HALF)], zero) for m in range(HALF) if m not in (0, I4)]
    )
    orbits = {}
    for label, beta, gamma in (("witness", Fraction(0), Fraction(0)),) + tuple(
        (f"generic-{k}", b, g) for k, (b, g) in enumerate(GENERIC_SLICE)
    ):
        a, _ = slice_point(1, beta, gamma)
        point = vector(QQ, [QQ(v) for v in bracket(a, zero)])
        orbit = matrix(QQ, [m * point for m in middle])
        orbits[label] = {"dimension": int(orbit.rank()), "inside_family_cone": orbit.stack(family).rank() == 14}
    return {
        "sage_version": sage.version.version,
        "der_o_dimension": int(sage_der.nrows()),
        "der_o_equals_cd_core_under_sign_flip_e3_e5_e6": der_equal,
        "related_triples_dimension": int(kernel.nrows()),
        "middle_projection_dimension": int(span.rank()),
        "middle_contains_der_and_identity": span.stack(named).rank() == span.rank(),
        "extra_generator_cross_half_exit_entries": extras,
        "orbits_unit_1": orbits,
    }


def audit() -> dict[str, Any]:
    core = audit_core(run())
    return {"schema": AUDIT_SCHEMA, "core": core, "packages": audit_packages(core), "sage": audit_sage()}


def audit_verdicts(record: dict[str, Any], core: dict[str, Any]) -> list[str]:
    """Every rule the retained audit must satisfy against a fresh cd_core side; empty means it passes."""
    failures = []
    if record.get("schema") != AUDIT_SCHEMA:
        failures.append("audit schema differs")
    if record.get("core") != core:
        failures.append("the cd_core side of the audit differs from the retained record")
    for name in ("hyprat", "hypercomplex"):
        entry = record.get("packages", {}).get(name, {})
        if not (entry.get("l_tables_equal_cd_core") and entry.get("kernel_annihilated")):
            failures.append(f"{name} disagrees with cd_core")
    sage = record.get("sage", {})
    expected = {
        "der_o_dimension": len(gap.derivations()),
        "der_o_equals_cd_core_under_sign_flip_e3_e5_e6": True,
        "related_triples_dimension": 18,
        "middle_projection_dimension": 17,
        "middle_contains_der_and_identity": True,
    }
    for key, value in expected.items():
        if sage.get(key) != value:
            failures.append(f"Sage {key} is not {value}")
    extras = sage.get("extra_generator_cross_half_exit_entries", [])
    if len(extras) != 2 or not all(extras):
        failures.append("Sage does not record two extra generators that move e_8 or e_24 across the halves")
    orbits = sage.get("orbits_unit_1", {})
    dims = {label: (o.get("dimension"), o.get("inside_family_cone")) for label, o in orbits.items()}
    if dims != {"witness": (8, True), "generic-0": (13, True), "generic-1": (13, True)}:
        failures.append(f"Sage orbit dimensions differ: {dims}")
    return failures


def audit_check(path: Path) -> None:
    """Recompute the cd_core side of the retained audit and require every package and Sage value."""
    failures = audit_verdicts(json.loads(path.read_text(encoding="utf-8")), audit_core(run()))
    _require(not failures, f"the audit fails: {failures}")


def _point(record: dict[str, Any], witness: int, label: str) -> dict[str, Any]:
    return next(p for p in record["witnesses"][witness]["points"] if p["label"] == label)


def self_test() -> str:
    """Corrupted ranks, turns, differentials, family bounds and audit values are each rejected."""
    record = run()
    _require(not verdicts(record), f"the honest record fails: {verdicts(record)}")
    mutations = {
        "composite rank 20": lambda r: _point(r, 0, "composite").__setitem__("rank", RANK),
        "composite missing": lambda r: r["witnesses"][1].__setitem__(
            "points", [p for p in r["witnesses"][1]["points"] if p["label"] != "composite"]
        ),
        "turn rank 21": lambda r: _point(r, 1, "upper-turn").__setitem__("rank", RANK + 1),
        "parallel turn rank 28": lambda r: _point(r, 0, "parallel-lower-turn").__setitem__("rank", 28),
        "generic turn rank 20": lambda r: _point(r, 2, "generic-lower-turn").__setitem__("rank", RANK),
        "turn differs from rotation_curve": lambda r: r["witnesses"][0].__setitem__(
            "turns_equal_rotation_curve", False
        ),
        "differential rank 15": lambda r: r["witnesses"][2].__setitem__("differential_rank_cone", 15),
        "family bound 13": lambda r: r["family_tangent_bounds"][0].__setitem__("dimension_upper_bound", 13),
        "family nullity 4": lambda r: r["family_tangent_bounds"][2].__setitem__("nullity", 4),
        "family point a zero divisor": lambda r: r["family_tangent_bounds"][1].__setitem__("a4_rank", 12),
    }
    for label, change in mutations.items():
        bad = copy.deepcopy(record)
        change(bad)
        _require(bool(verdicts(bad)), f"the {label} mutation passes")
    retained = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    core = audit_core(record)
    _require(not audit_verdicts(retained, core), f"the retained audit fails: {audit_verdicts(retained, core)}")
    audit_mutations = {
        "hyprat table": lambda a: a["packages"]["hyprat"].__setitem__("l_tables_equal_cd_core", False),
        "hypercomplex kernel": lambda a: a["packages"]["hypercomplex"].__setitem__("kernel_annihilated", False),
        "core digest": lambda a: a["core"]["nodes"][3].__setitem__("l_sha256", "0" * 64),
        "triples 17": lambda a: a["sage"].__setitem__("related_triples_dimension", 17),
        "one extra": lambda a: a["sage"]["extra_generator_cross_half_exit_entries"].pop(),
        "orbit 12": lambda a: a["sage"]["orbits_unit_1"]["generic-0"].__setitem__("dimension", 12),
        "der(O) map": lambda a: a["sage"].__setitem__("der_o_equals_cd_core_under_sign_flip_e3_e5_e6", False),
    }
    for label, change in audit_mutations.items():
        bad = copy.deepcopy(retained)
        change(bad)
        _require(bool(audit_verdicts(bad, core)), f"the {label} audit mutation passes")
    return (
        f"rank locus rotation composite self-test: {len(mutations)} record and "
        f"{len(audit_mutations)} audit corruptions rejected"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--audit-out", type=Path)
    mode.add_argument("--audit-check", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.audit_out:
        args.audit_out.parent.mkdir(parents=True, exist_ok=True)
        args.audit_out.write_text(render(audit()), encoding="utf-8")
        audit_check(args.audit_out)
        print("rank locus rotation composite audit: hyprat, hypercomplex and SageMath agree with cd_core")
        return 0
    if args.audit_check:
        audit_check(args.audit_check)
        print("rank locus rotation composite audit: retained package and Sage verdicts match cd_core")
        return 0
    record = run()
    text = render(record)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        _require(args.check.read_text(encoding="utf-8") == text, "the retained file differs from the recomputed text")
    _require(not verdicts(record), f"the record fails: {verdicts(record)}")
    for row in record["witnesses"]:
        print(json.dumps({"unit": row["unit"], "ranks": {p["label"]: p["rank"] for p in row["points"]}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
