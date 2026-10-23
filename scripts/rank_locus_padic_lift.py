"""p-adic Hensel lift of the Schur-complement germ at each A_5 rank-locus witness and its excess equations.

At a witness x of A_5 with nullity k and r = 32 - k, a pivot block A = L_x[R, C] of size r is
invertible, and near x the closed rank cone R_k = {y : rank L_y <= r} is the zero set of the k x k
Schur complement S(y) = L_y[R', C'] - L_y[R', C] A(y)^-1 L_y[R, C'] (rank_locus_local_dimension).
The differential of S at x has rank c = 32 - dim T(x). The script picks c entries G of S whose
differentials are independent and c coordinates d on which that c x c Jacobian minor is
invertible; G = 0 cuts out a smooth germ M of dimension dim T(x) parameterized by the remaining
free coordinates, and R_k lies inside M near x. The other k^2 - c entries H decide the germ:
along M they form a power series P(u) = H(phi(u)) with rational coefficients, and since M is a
connected smooth germ, P is identically zero exactly when R_k contains M near x, which is exactly
when the cone has local dimension dim T(x) there, so that D_(5,k) reaches its tangent bound
dim T(x) - 1. If P is not zero, {P = 0} is a proper analytic subset of M and the local dimension
of D_(5,k) at x is at most dim T(x) - 2.

Two routes evaluate P exactly along seeded directions w of the free coordinates.
- p-adic (pyadic 0.3.0): the free coordinates take the values x_f + p^s w in Z_p, and modified
  Newton steps with the Jacobian inverse at x lift the dependent coordinates until G vanishes to
  O(p^N). Hensel's lemma makes that point agree to O(p^N) with a true point of M(Z_p), because the
  pivot block and the Jacobian minor are units modulo p, so H at it is known exactly to O(p^N).
  Its valuation is s m, where m is the order of P along w, and its leading digit is P_m(w) mod p.
- series (python-flint nmod_mat): the same lift over F_p[[t]] / t^order with y_f = x_f + t w,
  solved order by order. The first nonzero coefficient of H(t) is P_m(w) mod p at t^m.
The routes share only the exact chart (R, C, G, d and the Jacobian inverse), and the record
requires the p-adic valuation and leading digits at scale 1 to equal the series order and
coefficients, and at scale 2 to double the valuation with the same digits.

Controls. The zero-divisor families zd-axis, zd-zd-locus and zd-zd-generic have certified local
dimension equal to the tangent bound (rank_locus_local_dimension), so M is the germ there and H
must vanish in both routes. At x0 = e1 + e18 the Bouligand cone of the nullity-12 locus is
A15 union B17 (nullity_twelve_local_geometry.md), of dimension 17 at unit norm, below the tangent
bound 21, so H must be nonzero there, with order 2 because the eight canonical quadrics
(rank_locus_second_order) already obstruct. Seeded velocities at x0 inside A15 and inside
A15 intersect B17, where that order-2 obstruction vanishes, must read a nonzero order above 2 in
both routes, which exercises detection at the orders where a gap witness would first obstruct.
A failed control stops the run. The self-test adds a toy germ whose obstruction starts at order 5.

Falsifier, stated before the run: one nonzero excess entry in either route at a gap witness
(nonzd-axis, zd-nonzd-locus, zd-nonzd-generic, nonzd-nonzd-locus) is an exact certificate that
P is not zero there, refuting a5-nonzero-divisor-two-dimension-gap at that witness and placing
its local dimension at most one above its family. Excess entries that vanish to O(p^N) and
O(t^order) at every sample admit nothing: they bound the order of P from below along the drawn
directions. The weights are drawn uniformly from F_p^* = {1, ..., p - 1}, so if P had order m below
the series order with a leading form P_m nonzero modulo p, a drawn w would miss it with probability
at most m / (p - 1) by the Schwartz-Zippel lemma over that set.

Usage:
    "$PYTHON" scripts/rank_locus_padic_lift.py --out docs/evidence/rank_locus_padic_lift/result.json
    "$PYTHON" scripts/rank_locus_padic_lift.py --check docs/evidence/rank_locus_padic_lift/result.json
    "$PYTHON" scripts/rank_locus_padic_lift.py --self-test

--check recomputes the series route and, where pyadic imports, the p-adic route; without pyadic
it holds the retained p-adic rows to the fresh series orders and coefficients.
"""

from __future__ import annotations

import argparse
import copy
import functools
import importlib.metadata
import json
import math
import random
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from rank_locus_local_dimension import tangent_bound, witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-padic-lift-v1"
DIM = 32
SEED = 20_261_024
# pyadic.primes.primes[:2], the two largest primes below 2^31.
PRIMES = (2_147_483_647, 2_147_483_629)
SAMPLES = 2
SERIES_ORDER = 64
PADIC_DIGITS = 12
X0_WITNESS = 29
SMOOTH_CONTROLS = ("zd-axis", "zd-zd-locus", "zd-zd-generic")
GAP_FAMILIES = ("nonzd-axis", "zd-nonzd-locus", "zd-nonzd-generic", "nonzd-nonzd-locus")
X0_FAMILY = "x0-two-piece-cone"
# The pyadic release the retained p-adic rows were computed with (scripts/kaggle_run.py PIN_GROUPS).
PYADIC_VERSION = "0.3.0"
X0_ORDER = 2
CONTROL_PLANES = ("A15", "A15 intersect B17")
RETAINED = ROOT / "docs/evidence/rank_locus_padic_lift/result.json"

SIGNS = [[cd_sign(DIM, i, j) for j in range(DIM)] for i in range(DIM)]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_padic_lift: {message}")


def left(y: list[Any]) -> list[list[Any]]:
    """L_y with (k, j) entry the coefficient of e_k in y e_j, for any coefficient ring with negation."""
    return [[y[k ^ j] if SIGNS[k ^ j][j] == 1 else -y[k ^ j] for j in range(DIM)] for k in range(DIM)]


def fmpq(rows: list[list[Fraction]]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[flint.fmpq(v.numerator, v.denominator) for v in row] for row in rows])


def fractions(matrix: flint.fmpq_mat) -> list[list[Fraction]]:
    return [
        [Fraction(int(matrix[i, j].p), int(matrix[i, j].q)) for j in range(matrix.ncols())]
        for i in range(matrix.nrows())
    ]


def pivots(rows: list[list[Fraction]]) -> list[int]:
    """Pivot columns of the reduced row echelon form."""
    reduced, rank = fmpq(rows).rref()
    found: list[int] = []
    column = 0
    for row in range(rank):
        while reduced[row, column] == 0:
            column += 1
        found.append(column)
    return found


def block(matrix: list[list[Any]], rows: list[int], columns: list[int]) -> list[list[Any]]:
    return [[matrix[i][j] for j in columns] for i in rows]


def unit_mod(value: Fraction, p: int) -> bool:
    return value.numerator % p != 0 and value.denominator % p != 0


def all_rows() -> list[dict[str, Any]]:
    """The certified witnesses followed by the x0 = e1 + e18 control."""
    rows = [{"witness": row["witness"], "family": row["family"], "x": row["x"]} for row in witnesses()]
    x0 = [Fraction(0)] * DIM
    x0[1] = x0[18] = Fraction(1)
    _require(len(rows) == X0_WITNESS, "the witness list changed length")
    return [*rows, {"witness": X0_WITNESS, "family": X0_FAMILY, "x": x0}]


def role(family: str) -> str:
    if family in SMOOTH_CONTROLS:
        return "smooth control"
    if family == X0_FAMILY:
        return "obstructed control"
    if family in GAP_FAMILIES:
        return "gap"
    return "upper bound only"


def chart(row: dict[str, Any]) -> dict[str, Any]:
    """Pivot block, independent Schur entries G, dependent coordinates d and the Jacobian inverse, all exact."""
    x = row["x"]
    lx = left(x)
    columns = pivots(lx)
    pivot_rows = pivots([list(column) for column in zip(*lx, strict=True)])
    rest_rows = [i for i in range(DIM) if i not in pivot_rows]
    rest_columns = [j for j in range(DIM) if j not in columns]
    nullity = len(rest_columns)
    a = fmpq(block(lx, pivot_rows, columns))
    a_inverse = a.inv()
    right = a_inverse * fmpq(block(lx, pivot_rows, rest_columns))
    left_factor = fmpq(block(lx, rest_rows, columns)) * a_inverse
    schur_x = fmpq(block(lx, rest_rows, rest_columns)) - left_factor * fmpq(block(lx, pivot_rows, rest_columns))
    _require(all(value == 0 for value in schur_x.entries()), f"witness {row['witness']}: S(x) is not zero")
    jacobian_columns = []
    for m in range(DIM):
        unit = left([Fraction(int(i == m)) for i in range(DIM)])
        derivative = (
            fmpq(block(unit, rest_rows, rest_columns))
            - fmpq(block(unit, rest_rows, columns)) * right
            - left_factor * fmpq(block(unit, pivot_rows, rest_columns))
            + left_factor * fmpq(block(unit, pivot_rows, columns)) * right
        )
        jacobian_columns.append([Fraction(int(v.p), int(v.q)) for v in derivative.entries()])
    jacobian = [list(entry) for entry in zip(*jacobian_columns, strict=True)]
    independent = pivots(jacobian_columns)
    dependent = pivots([jacobian[q] for q in independent])
    minor = fmpq([[jacobian[q][m] for m in dependent] for q in independent])
    tangent_dimension = DIM - len(independent)
    bound = tangent_bound(x)
    _require(bound["nullity"] == nullity, f"witness {row['witness']}: chart nullity {nullity}")
    _require(
        bound["dimension_upper_bound"] == tangent_dimension - 1,
        f"witness {row['witness']}: exact Jacobian rank disagrees with the tangent bound",
    )
    determinants = (Fraction(int(a.det().p), int(a.det().q)), Fraction(int(minor.det().p), int(minor.det().q)))
    for p in PRIMES:
        _require(all(unit_mod(v, p) for v in x if v != 0), f"witness {row['witness']}: x is not {p}-integral")
        _require(all(unit_mod(v, p) for v in determinants), f"witness {row['witness']}: a pivot is not a {p}-unit")
    return {
        "witness": row["witness"],
        "family": row["family"],
        "x": x,
        "nullity": nullity,
        "pivot_rows": pivot_rows,
        "pivot_columns": columns,
        "rest_rows": rest_rows,
        "rest_columns": rest_columns,
        "independent": independent,
        "dependent": dependent,
        "free": [m for m in range(DIM) if m not in dependent],
        "excess": [q for q in range(nullity * nullity) if q not in independent],
        "jacobian_inverse": fractions(minor.inv()),
        "independent_rows": [jacobian[q] for q in independent],
        "tangent_dimension": tangent_dimension,
    }


# Series route over F_p[[t]].


def nmod(rows: list[list[int]], p: int) -> flint.nmod_mat:
    return flint.nmod_mat(rows, p)


def reduce_mod(value: Fraction, p: int) -> int:
    return value.numerator * pow(value.denominator, -1, p) % p


def recurrence_length(sequence: list[int], p: int) -> int:
    """Berlekamp-Massey: the length of the shortest linear recurrence over F_p that generates the sequence."""
    current, previous = [1], [1]
    length, gap, last = 0, 1, 1
    for n, value in enumerate(sequence):
        discrepancy = value
        for i in range(1, length + 1):
            discrepancy = (discrepancy + current[i] * sequence[n - i]) % p
        if discrepancy == 0:
            gap += 1
            continue
        factor = discrepancy * pow(last, -1, p) % p
        saved = list(current)
        current = current + [0] * (len(previous) + gap - len(current))
        for i, coefficient in enumerate(previous):
            current[i + gap] = (current[i + gap] - factor * coefficient) % p
        if 2 * length <= n:
            length, previous, last, gap = n + 1 - length, saved, discrepancy, 1
        else:
            gap += 1
    return length


def series_lift(item: tuple[dict[str, Any], int, list[int], int]) -> dict[str, Any]:
    """First nonzero order of H(phi(t w)) in F_p[[t]] / t^order and its coefficients there.

    When H vanishes through the order, each dependent coordinate's coefficients t^1 .. t^(order-1)
    also get their Berlekamp-Massey recurrence length: a coordinate that is a rational function of t
    of degree below half the order would show a length below half the order.
    """
    ch, p, weights, order = item
    rows, columns, rest_rows, rest_columns = ch["pivot_rows"], ch["pivot_columns"], ch["rest_rows"], ch["rest_columns"]
    inverse = [[reduce_mod(v, p) for v in row] for row in ch["jacobian_inverse"]]
    blocks: list[tuple[flint.nmod_mat, ...]] = []
    a_inverse: list[flint.nmod_mat] = []
    right: list[flint.nmod_mat] = []

    def coefficient(vector: list[int]) -> tuple[tuple[flint.nmod_mat, ...], flint.nmod_mat, flint.nmod_mat, list[int]]:
        lv = [[value % p for value in line] for line in left(vector)]
        parts = tuple(
            nmod(block(lv, a, b), p)
            for a, b in ((rows, columns), (rows, rest_columns), (rest_rows, columns), (rest_rows, rest_columns))
        )
        # Coefficient j of A^-1, A^-1 B and S, from the stored coefficients below j and this one.
        j = len(blocks)
        if j == 0:
            ai = parts[0].inv()
            z = ai * parts[1]
            s = parts[3] - parts[2] * z
            return parts, ai, z, [int(v) for v in s.entries()]
        total = parts[0] * a_inverse[0]
        for i in range(1, j):
            total = total + blocks[i][0] * a_inverse[j - i]
        ai = -(a_inverse[0] * total)
        z = ai * blocks[0][1] + a_inverse[0] * parts[1]
        for i in range(1, j):
            z = z + a_inverse[i] * blocks[j - i][1]
        s = parts[3] - blocks[0][2] * z - parts[2] * right[0]
        for i in range(1, j):
            s = s - blocks[i][2] * right[j - i]
        return parts, ai, z, [int(v) for v in s.entries()]

    first: int | None = None
    leading: list[list[int]] = []
    kept: list[list[int]] = []
    for j in range(order):
        vector = [0] * DIM
        if j == 0:
            vector = [reduce_mod(v, p) for v in ch["x"]]
        elif j == 1:
            for m, w in zip(ch["free"], weights, strict=True):
                vector[m] = w
        parts, ai, z, s = coefficient(vector)
        g = [s[q] for q in ch["independent"]]
        if j == 0:
            _require(not any(s), f"witness {ch['witness']}: S(x) is not zero modulo {p}")
        elif any(g):
            for a, m in enumerate(ch["dependent"]):
                vector[m] = -sum(inverse[a][b] * g[b] for b in range(len(g))) % p
            parts, ai, z, s = coefficient(vector)
            _require(not any(s[q] for q in ch["independent"]), f"witness {ch['witness']}: order {j} lift failed")
        kept.append(vector)
        blocks.append(parts)
        a_inverse.append(ai)
        right.append(z)
        nonzero = [[q, s[q]] for q in ch["excess"] if s[q]]
        if nonzero and first is None:
            first, leading = j, nonzero
            break
    lengths = (
        [recurrence_length([kept[j][m] for j in range(1, order)], p) for m in ch["dependent"]] if first is None else []
    )
    return {"prime": p, "weights": weights, "order": first, "leading": leading, "recurrence_lengths": lengths}


# p-adic route with pyadic.


def padic_zero(value: Any, digits: int) -> bool:
    """pyadic stores a zero as k = 0 digits with its guaranteed absolute precision in n."""
    return bool(value.k == 0 and value.n >= digits)


def padic_hensel(
    evaluate: Callable[[list[Any]], list[Any]],
    start: list[Any],
    independent: list[int],
    dependent: list[int],
    inverse: list[list[Any]],
    digits: int,
) -> tuple[list[Any], int]:
    """Modified Newton steps on the dependent coordinates until every independent equation is O(p^digits)."""
    y = list(start)
    for step in range(digits + 3):
        values = evaluate(y)
        g = [values[q] for q in independent]
        if all(padic_zero(v, digits) for v in g):
            return values, step
        for a, m in enumerate(dependent):
            correction = inverse[a][0] * g[0]
            for b in range(1, len(g)):
                correction = correction + inverse[a][b] * g[b]
            y[m] = y[m] - correction
    raise SystemExit("rank_locus_padic_lift: the p-adic Newton iteration did not converge")


def padic_schur(ch: dict[str, Any], p: int, digits: int, y: list[Any]) -> list[Any]:
    """S(y) flattened row-major, by Gaussian elimination over Z_p with a unit pivot in every column."""
    from pyadic import PAdic

    ly = left(y)
    rows, columns, rest_rows, rest_columns = ch["pivot_rows"], ch["pivot_columns"], ch["rest_rows"], ch["rest_columns"]
    r = len(columns)
    augmented = [[ly[i][j] for j in columns] + [ly[i][j] for j in rest_columns] for i in rows]
    for c in range(r):
        units = [i for i in range(c, r) if augmented[i][c].k > 0 and augmented[i][c].n == 0]
        _require(bool(units), f"witness {ch['witness']}: no unit pivot in column {c}")
        pivot = units[0]
        augmented[c], augmented[pivot] = augmented[pivot], augmented[c]
        scale = PAdic(1, p, digits) / augmented[c][c]
        augmented[c] = [v * scale for v in augmented[c]]
        for i in range(r):
            if i != c:
                factor = augmented[i][c]
                augmented[i] = [a - factor * b for a, b in zip(augmented[i], augmented[c], strict=True)]
    values = []
    for i in rest_rows:
        for jj, j in enumerate(rest_columns):
            total = ly[i][j]
            for t, column in enumerate(columns):
                total = total - ly[i][column] * augmented[t][r + jj]
            values.append(total)
    return values


def padic_lift(item: tuple[dict[str, Any], int, list[int], int, int]) -> dict[str, Any]:
    """Valuation, absolute precision and leading digits of H at the Hensel lift of x_f + p^scale w."""
    from pyadic import PAdic

    ch, p, weights, scale, digits = item
    start = [PAdic(v, p, digits) for v in ch["x"]]
    for m, w in zip(ch["free"], weights, strict=True):
        start[m] = PAdic(ch["x"][m] + p**scale * w, p, digits)
    inverse = [[PAdic(v, p, digits) for v in row] for row in ch["jacobian_inverse"]]
    evaluate = functools.partial(padic_schur, ch, p, digits)
    values, steps = padic_hensel(evaluate, start, ch["independent"], ch["dependent"], inverse, digits)
    excess = [(q, values[q]) for q in ch["excess"]]
    nonzero = [(q, v) for q, v in excess if v.k > 0]
    valuation = min((v.n for _, v in nonzero), default=None)
    # Every input is an exact p-adic integer given to O(p^digits) and every division is by a unit,
    # so each digit below p^digits is exact. pyadic's __add__ counts the leading zero digits of the
    # unreduced sum and can report a cancelled zero beyond that, so the claim stops at p^digits.
    return {
        "prime": p,
        "scale": scale,
        "valuation": valuation,
        "leading": [[q, int(v.as_tuple[0])] for q, v in nonzero if v.n == valuation],
        "absolute_precision": min(digits, *(v.n + v.k for _, v in excess)),
        "newton_steps": steps,
    }


def pyadic_version() -> str | None:
    try:
        import pyadic  # noqa: F401
    except ImportError:
        return None
    return importlib.metadata.version("pyadic")


def control_directions(ch: dict[str, Any]) -> list[dict[str, Any]]:
    """Seeded integer velocities at x0 inside A15 and inside A15 intersect B17.

    nullity_twelve_locus certifies that the order-2 obstruction at x0 vanishes exactly on A15 union B17,
    so along these velocities the first nonzero order of H is at least 3, and both routes must read it.
    The velocity's free part enters the p-adic route as exact integers: its residue modulo p would leave
    an order-2 term divisible by p, whose carry would shift the order-3 digit.
    """
    from nullity_twelve_locus import certify_nullity_twelve_locus

    certificate = certify_nullity_twelve_locus()
    basis = certificate.ambient_tangent_basis
    a15, b17 = (set(plane.zero_coordinates) for plane in certificate.planes)
    rng = random.Random(SEED + X0_WITNESS + 1000)
    found = []
    for plane, zero in zip(CONTROL_PLANES, (a15, a15 | b17), strict=True):
        weights = [0 if i in zero else rng.randint(-9, 9) for i in range(len(basis[0]))]
        velocity = [
            sum((Fraction(basis[r][c]) * weights[c] for c in range(len(weights))), Fraction(0)) for r in range(DIM)
        ]
        scale = math.lcm(1, *(value.denominator for value in velocity))
        integers = [int(value * scale) for value in velocity]
        _require(
            all(sum(row[m] * integers[m] for m in range(DIM)) == 0 for row in ch["independent_rows"]),
            f"the {plane} control velocity is not in T(x0)",
        )
        found.append({"plane": plane, "tangent_weights": weights, "velocity": integers})
    return found


def higher_order_controls(ch: dict[str, Any], order: int, digits: int, padic: bool) -> list[dict[str, Any]]:
    controls = control_directions(ch)
    p = PRIMES[0]
    free = [[c["velocity"][m] for m in ch["free"]] for c in controls]
    series = parallel.ordered_map(series_lift, [(ch, p, [w % p for w in f], order) for f in free], min_items=2)
    lifts: list[dict[str, Any]] = []
    if padic:
        items = [(ch, p, f, scale, digits) for f in free for scale in (1, 2)]
        lifts = parallel.ordered_map(padic_lift, items, min_items=2)
    return [
        {**control, "series": s, "padic": lifts[2 * index : 2 * index + 2]}
        for index, (control, s) in enumerate(zip(controls, series, strict=True))
    ]


def measure(
    row_ids: list[int] | None = None, order: int = SERIES_ORDER, digits: int = PADIC_DIGITS, controls: bool = True
) -> dict[str, Any]:
    rows = [row for row in all_rows() if row_ids is None or row["witness"] in row_ids]
    charts = parallel.ordered_map(chart, rows, min_items=2)
    weights = []
    for ch in charts:
        rng = random.Random(SEED + ch["witness"])
        weights.append([[rng.randrange(1, p) for _ in ch["free"]] for p in PRIMES for _ in range(SAMPLES)])
    series_items = [
        (ch, PRIMES[index // SAMPLES], drawn[index], order)
        for ch, drawn in zip(charts, weights, strict=True)
        for index in range(len(PRIMES) * SAMPLES)
    ]
    series = parallel.ordered_map(series_lift, series_items, min_items=2)
    per_row = len(PRIMES) * SAMPLES
    version = pyadic_version()
    padic: list[list[dict[str, Any]]] = [[] for _ in charts]
    if version is not None:
        padic_items = []
        for index, ch in enumerate(charts):
            obstructed = any(s["order"] is not None for s in series[index * per_row : (index + 1) * per_row])
            for scale in (1, 2) if obstructed else (1,):
                padic_items.append((index, (ch, PRIMES[0], weights[index][0], scale, digits)))
        results = parallel.ordered_map(padic_lift, [item for _, item in padic_items], min_items=2)
        for (index, _), result in zip(padic_items, results, strict=True):
            padic[index].append(result)
    out = []
    for index, ch in enumerate(charts):
        samples = series[index * per_row : (index + 1) * per_row]
        orders = [s["order"] for s in samples]
        out.append(
            {
                "witness": ch["witness"],
                "family": ch["family"],
                "role": role(ch["family"]),
                "nullity": ch["nullity"],
                "tangent_dimension": ch["tangent_dimension"],
                "pivot_rows": ch["pivot_rows"],
                "pivot_columns": ch["pivot_columns"],
                "independent_entries": ch["independent"],
                "dependent_coordinates": ch["dependent"],
                "excess_entries": len(ch["excess"]),
                "series": samples,
                "padic": padic[index],
                "obstructed": any(o is not None for o in orders),
            }
        )
    record = {
        "schema": SCHEMA,
        "seed": SEED,
        "primes": list(PRIMES),
        "samples": SAMPLES,
        "series_order": order,
        "padic_digits": digits,
        "rows": out,
        "higher_order_controls": [],
        "versions": {"python-flint": flint.__version__, "pyadic": version or "not run: pyadic does not import"},
    }
    if controls:
        x0_chart = next(ch for ch in charts if ch["witness"] == X0_WITNESS)
        record["higher_order_controls"] = higher_order_controls(x0_chart, order, digits, version is not None)
    problems = consistency(record)
    _require(not problems, f"the measurement is inconsistent: {problems}")
    return record


def route_agreement(label: str, first: dict[str, Any], padic: list[dict[str, Any]], digits: int) -> list[str]:
    """Each p-adic lift against the series sample of the same prime and direction."""
    found = []
    for entry in padic:
        expected = first.get("order")
        if expected is not None and expected * entry.get("scale", 0) >= digits:
            expected = None
        valuation = entry.get("valuation")
        want = None if expected is None else expected * entry.get("scale", 0)
        if valuation != want:
            found.append(f"{label} p-adic valuation {valuation} at scale {entry.get('scale')}, series wants {want}")
        elif valuation is not None and entry.get("leading") != first.get("leading"):
            found.append(f"{label} p-adic leading digits differ from the series coefficients")
        if entry.get("absolute_precision", -1) < digits:
            found.append(f"{label} p-adic absolute precision below {digits} digits")
        if entry.get("prime") != PRIMES[0] or entry.get("prime") != first.get("prime"):
            found.append(f"{label} p-adic prime")
    return found


def consistency(record: dict[str, Any]) -> list[str]:
    """Controls, the two-route agreement and each row's internal arithmetic."""
    found = []
    digits = record.get("padic_digits", PADIC_DIGITS)
    padic_run = not record.get("versions", {}).get("pyadic", "").startswith("not run")
    for control in record.get("higher_order_controls", []):
        label = f"{control.get('plane')} control"
        order = control.get("series", {}).get("order")
        if order is None or order <= X0_ORDER:
            found.append(f"{label} reads order {order}, not above {X0_ORDER}")
        if padic_run:
            if [entry.get("scale") for entry in control.get("padic", [])] != [1, 2]:
                found.append(f"{label} p-adic scales")
            found += route_agreement(label, control.get("series", {}), control.get("padic", []), digits)
    for row in record.get("rows", []):
        label = f"witness {row.get('witness')}"
        series, padic = row.get("series", []), row.get("padic", [])
        orders = [s.get("order") for s in series]
        if len(series) != len(PRIMES) * SAMPLES:
            found.append(f"{label} series sample count")
        if row.get("obstructed") != any(o is not None for o in orders):
            found.append(f"{label} obstruction flag disagrees with its series orders")
        if row.get("excess_entries", -1) + len(row.get("independent_entries", [])) != row.get("nullity", 0) ** 2:
            found.append(f"{label} independent and excess entries do not fill the Schur complement")
        if DIM - len(row.get("independent_entries", [])) != row.get("tangent_dimension"):
            found.append(f"{label} tangent dimension is not 32 minus the independent entries")
        if row.get("role") == "smooth control" and row.get("obstructed"):
            found.append(f"{label} smooth control is obstructed")
        if row.get("role") == "obstructed control" and orders and set(orders) != {X0_ORDER}:
            found.append(f"{label} obstructed control has orders {orders}")
        if not padic_run:
            continue
        scales = [entry.get("scale") for entry in padic]
        if scales != ([1, 2] if row.get("obstructed") else [1]):
            found.append(f"{label} p-adic scales {scales}")
        found += route_agreement(label, series[0] if series else {}, padic, digits)
    return found


def padic_declaration(record: dict[str, Any]) -> list[str]:
    """A retained record must carry p-adic rows from the pinned pyadic release."""
    if record.get("versions", {}).get("pyadic") == PYADIC_VERSION:
        return []
    return [f"versions: the retained p-adic rows are not from pyadic {PYADIC_VERSION}"]


def verdicts(record: dict[str, Any], fresh: dict[str, Any]) -> list[str]:
    """Fields that differ from the fresh measurement, plus every consistency failure of the record."""
    padic_fresh = not fresh["versions"]["pyadic"].startswith("not run")
    skip = {"rows", "versions", "higher_order_controls"}
    found = [
        key for key in sorted(record.keys() | fresh.keys()) if key not in skip and record.get(key) != fresh.get(key)
    ]
    versions = dict(record.get("versions", {}))
    expected_versions = dict(fresh["versions"])
    if not padic_fresh:
        versions.pop("pyadic", None)
        expected_versions.pop("pyadic", None)
    if versions != expected_versions:
        found.append("versions")
    controls = record.get("higher_order_controls", [])
    if len(controls) != len(fresh["higher_order_controls"]):
        found.append("higher_order_controls")
    else:
        for control, expected in zip(controls, fresh["higher_order_controls"], strict=True):
            keys = sorted(control.keys() | expected.keys())
            if not padic_fresh:
                keys = [key for key in keys if key != "padic"]
            found += [f"{expected['plane']} control {key}" for key in keys if control.get(key) != expected.get(key)]
    rows = record.get("rows", [])
    if len(rows) != len(fresh["rows"]):
        return [*found, "rows"]
    for row, expected in zip(rows, fresh["rows"], strict=True):
        keys = sorted(row.keys() | expected.keys())
        if not padic_fresh:
            keys = [key for key in keys if key != "padic"]
        found += [f"witness {expected['witness']} {key}" for key in keys if row.get(key) != expected.get(key)]
    return found + consistency(record)


def toy_order() -> int | None:
    """Valuation of H = y1 - y0^2 + y0^5 on the parabola G = y1 - y0^2 = 0 at y0 = 3p, through padic_hensel."""
    from pyadic import PAdic

    p, digits = PRIMES[0], 8

    def evaluate(y: list[Any]) -> list[Any]:
        square = y[0] * y[0]
        return [y[1] - square, y[1] - square + square * square * y[0]]

    start = [PAdic(3 * p, p, digits), PAdic(0, p, digits)]
    values, _ = padic_hensel(evaluate, start, [0], [1], [[PAdic(1, p, digits)]], digits)
    return int(values[1].n) if values[1].k > 0 else None


def self_test() -> str:
    """Corrupted orders, digits, flags, charts and controls are rejected; the toy obstruction reads order 5."""
    record = measure([5, X0_WITNESS], order=6, digits=5, controls=False)
    retained = json.loads(RETAINED.read_text())
    planes = [control.get("plane") for control in retained.get("higher_order_controls", [])]
    _require(planes == list(CONTROL_PLANES), f"the retained record carries controls {planes}")
    _require(not consistency(retained), f"the retained record fails: {consistency(retained)}")
    _require(not padic_declaration(retained), "the retained record does not declare the pinned pyadic release")
    stripped = copy.deepcopy(retained)
    stripped["versions"]["pyadic"] = "not run: pyadic does not import"
    for row in stripped["rows"]:
        row["padic"] = []
    _require(bool(padic_declaration(stripped)), "a record with its p-adic rows stripped passes")
    retained_mutations: dict[str, Callable[[dict[str, Any]], Any]] = {
        "control order 2": lambda r: r["higher_order_controls"][0]["series"].__setitem__("order", 2),
        "control read zero": lambda r: r["higher_order_controls"][1]["series"].__setitem__("order", None),
    }
    if not retained["versions"]["pyadic"].startswith("not run"):
        retained_mutations |= {
            "control valuation off its order": lambda r: r["higher_order_controls"][1]["padic"][1].__setitem__(
                "valuation", 7
            ),
            "control digit changed": lambda r: r["higher_order_controls"][0]["padic"][0]["leading"][0].__setitem__(
                1, 5
            ),
        }
    for label, change in retained_mutations.items():
        bad = copy.deepcopy(retained)
        change(bad)
        if not consistency(bad):
            raise SystemExit(f"rank_locus_padic_lift: the retained {label} mutation passes")
    if verdicts(record, record):
        raise SystemExit(f"rank_locus_padic_lift: the honest record fails: {verdicts(record, record)}")
    has_padic = not record["versions"]["pyadic"].startswith("not run")
    mutations: dict[str, Callable[[dict[str, Any]], Any]] = {
        "gap witness obstructed": lambda r: r["rows"][0]["series"][0].__setitem__("order", 4),
        "control order shifted": lambda r: r["rows"][1]["series"][1].__setitem__("order", 3),
        "series coefficient changed": lambda r: r["rows"][1]["series"][0]["leading"][0].__setitem__(1, 1),
        "obstruction flag cleared": lambda r: r["rows"][1].__setitem__("obstructed", False),
        "weight changed": lambda r: r["rows"][0]["series"][2]["weights"].__setitem__(0, 7),
        "tangent dimension shifted by 1": lambda r: r["rows"][0].__setitem__("tangent_dimension", 27),
        "dependent coordinate changed": lambda r: r["rows"][0]["dependent_coordinates"].__setitem__(0, 31),
        "role relabeled": lambda r: r["rows"][1].__setitem__("role", "gap"),
        "sample dropped": lambda r: r["rows"][0]["series"].pop(),
        "witness dropped": lambda r: r["rows"].pop(),
        "schema changed": lambda r: r.__setitem__("schema", "rank-locus-padic-lift-v0"),
    }
    if has_padic:
        mutations |= {
            "p-adic valuation changed": lambda r: r["rows"][1]["padic"][1].__setitem__("valuation", 3),
            "p-adic digit changed": lambda r: r["rows"][1]["padic"][0]["leading"][0].__setitem__(1, 2),
            "p-adic precision lowered": lambda r: r["rows"][0]["padic"][0].__setitem__("absolute_precision", 3),
            "p-adic scale dropped": lambda r: r["rows"][1]["padic"].pop(),
        }
    for label, change in mutations.items():
        bad = copy.deepcopy(record)
        change(bad)
        if not verdicts(bad, record):
            raise SystemExit(f"rank_locus_padic_lift: the {label} mutation passes")
    total = len(mutations) + len(retained_mutations) + 1
    if not has_padic:
        return f"{total} corruptions rejected; p-adic route and toy not run: pyadic does not import"
    toy = toy_order()
    _require(toy == 5, f"the toy obstruction reads order {toy}, not 5")
    return f"{total} corruptions rejected; toy obstruction at order 5"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"rank_locus_padic_lift self-test: {self_test()}")
        return 0
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = verdicts(retained, data)
        # Without pyadic the retained p-adic rows are held to the fresh series route, which
        # consistency() does only for a record that declares the pinned pyadic release.
        if data["versions"]["pyadic"].startswith("not run"):
            differing += padic_declaration(retained)
        if differing:
            raise SystemExit(f"rank_locus_padic_lift: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    for row in data["rows"]:
        padic = ", ".join(f"s{e['scale']} v{e['valuation']} O(p^{e['absolute_precision']})" for e in row["padic"])
        print(
            f"witness {row['witness']:2d} {row['family']:20s} k {row['nullity']:2d} "
            f"dim T {row['tangent_dimension']:2d} "
            f"series orders {[s['order'] for s in row['series']]} p-adic [{padic}]"
        )
    for control in data["higher_order_controls"]:
        padic = ", ".join(f"s{e['scale']} v{e['valuation']}" for e in control["padic"])
        print(f"x0 control {control['plane']:18s} series order {control['series']['order']} p-adic [{padic}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
