"""Place every hardware-measured A_5 operand on the H-orbit diagram of the rank strata.

The rank strata of A_5 are unions of orbits of H = G_2(C) x SO(2, C) x C^* on the doubly pure coordinates z' in C^15
(split coordinates; `docs/evidence/a5-strata-regularity/`). This script takes each A_5 element a = sum c_i e_i that a
hardware case measured (IBM pathion kernel map, coset map, parallel coset blocks, the IBM rank-sector path, the Tuna-17
coset-block and coin series, the Ascella four-term, two-block and kernel-slice cases), computes

- the nullity of L_a from `cd_core` (through `rederive_strata_equations.nullity`, the equations record's function);
- the split coordinates z' = (u', mu', v') with z_k = a_k + i a_(16+k) and z'_k = i^(-popcount k) z_k, the inverse of
  the equations record's `y_from_split`;
- the membership of z' in the twelve closures of `strata_regularity.closure_ideals` and in V(Q), V(G), evaluated
  exactly over Q(i);
- the orbit dimension, the rank of the 16 tangent vectors of `strata_regularity.h_generators` over Q(i);

and names the orbit as the one whose representative has the same membership pattern. A nullity that differs from the
orbit's nullity, a pattern that matches no representative, or an orbit rank that differs from the orbit's dimension
stops the run. For each incidence Y -> Z of the fiber program it lists the measured operands in the closure of Y and
in the orbit of Z, and searches straight lines a(s) = a_Z + s b (b a basis vector or a basis-pair operand) that stay in
the closure of Y for every s, with the nullity along them.

Usage:
    "$PYTHON" -B -W error docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py --self-test
    "$PYTHON" -B -W error docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py \
        --out docs/evidence/a5-exceptional-fibers/hardware-orbits
"""

from __future__ import annotations

import argparse
import csv
import functools
import itertools
import json
import re
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs/evidence/a5-strata-regularity"))
sys.path.insert(0, str(ROOT / "docs/evidence/a5-rank-strata-equations"))

import rederive_strata_equations as eq  # noqa: E402
import strata_regularity as sr  # noqa: E402

import parallel  # noqa: E402

Terms = dict[int, Fraction]
DIM = 32
ORBITS = tuple(sr.DIMS)
# Phase i^(-popcount k) that takes z_k to z'_k, as (re, im) for popcount mod 4 = 0, 1, 2, 3.
INV_PHASE = ((1, 0), (0, -1), (-1, 0), (0, 1))
# Incidences Y -> Z of the fiber program (ledger `fibers` column): the closure of Y contains the orbit of Z.
INCIDENCES: tuple[tuple[str, str], ...] = (
    ("W8", "Nm"),
    ("Ehat", "Np"),
    ("Ehat", "Nm"),
    ("Ehat", "VB"),
    ("Iso", "Nm"),
    ("Xp", "Nm"),
    ("Xm", "Np"),
)
DISPLAY = {
    "W8": "W8",
    "Ehat": "E8-bar",
    "Iso": "Iso",
    "Xp": "X+",
    "Xm": "X-",
    "B9": "B9",
    "V": "V",
    "VB": "VB",
    "Vap": "V^a+",
    "Vam": "V^a-",
    "Np": "N+",
    "Nm": "N-",
}
# s values of the straight-line test: the generators of every closure have degree at most 4 in z', so a polynomial
# in s of degree at most 4 that vanishes at nine values is zero.
LINE_S = tuple(Fraction(x) for x in (1, 2, 3, -1, -2, Fraction(1, 2), Fraction(-1, 2), 5, 7))
GENERIC_S = tuple(Fraction(x) for x in (2, 3, 5, 7, 11, 13, -3))
NULLITY_S = (Fraction(0), Fraction(1), Fraction(2), Fraction(1, 2), Fraction(-1))


class Gauss:
    """An exact element of Q(i), enough arithmetic for polynomial evaluation and the H tangent vectors."""

    __slots__ = ("im", "re")

    def __init__(self, re: Any = 0, im: Any = 0) -> None:
        self.re = Fraction(re)
        self.im = Fraction(im)

    @staticmethod
    def lift(x: Any) -> Gauss:
        return x if isinstance(x, Gauss) else Gauss(x)

    def __add__(self, other: Any) -> Gauss:
        o = Gauss.lift(other)
        return Gauss(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, other: Any) -> Gauss:
        o = Gauss.lift(other)
        return Gauss(self.re - o.re, self.im - o.im)

    def __rsub__(self, other: Any) -> Gauss:
        return Gauss.lift(other) - self

    def __mul__(self, other: Any) -> Gauss:
        o = Gauss.lift(other)
        return Gauss(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> Gauss:
        return Gauss(-self.re, -self.im)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, int | Fraction | Gauss):
            return NotImplemented
        o = Gauss.lift(other)
        return self.re == o.re and self.im == o.im

    def __hash__(self) -> int:
        return hash((self.re, self.im))

    def __repr__(self) -> str:
        return f"({self.re}{'+' if self.im >= 0 else '-'}{abs(self.im)}i)"

    def iszero(self) -> bool:
        return self.re == 0 and self.im == 0

    def text(self) -> str:
        if self.im == 0:
            return str(self.re)
        if self.re == 0:
            return f"{self.im}i"
        return f"{self.re}{'+' if self.im > 0 else '-'}{abs(self.im)}i"


def operand_vector(terms: Terms) -> list[Fraction]:
    y = [Fraction(0)] * DIM
    for index, coefficient in terms.items():
        y[index] += Fraction(coefficient)
    return y


def to_split(y: Sequence[Fraction]) -> list[Gauss]:
    """z'_k = i^(-popcount k) (y_k + i y_(16+k)) for k = 1..15; y_0 = y_16 = 0 is required."""
    if y[0] != 0 or y[16] != 0:
        raise ValueError("the operand is not doubly pure (y_0 or y_16 is nonzero)")
    out = []
    for k in range(1, 16):
        re, im = INV_PHASE[eq.popcount(k) % 4]
        out.append(Gauss(re, im) * Gauss(y[k], y[16 + k]))
    return out


def from_split(zp: Sequence[Gauss]) -> list[Fraction]:
    """Inverse of `to_split`: y_k + i y_(16+k) = i^(popcount k) z'_k."""
    y = [Fraction(0)] * DIM
    for k in range(1, 16):
        re, im = ((1, 0), (0, 1), (-1, 0), (0, -1))[eq.popcount(k) % 4]
        z = Gauss(re, im) * zp[k - 1]
        y[k], y[16 + k] = z.re, z.im
    return y


@functools.cache
def ideal_terms() -> dict[str, list[list[tuple[tuple[tuple[int, int], ...], int]]]]:
    """Generators of the twelve closures, V(Q) and V(G) as lists of ((variable, exponent), ...), coefficient."""
    out: dict[str, list[list[tuple[tuple[tuple[int, int], ...], int]]]] = {}
    for name, gens in sr.closure_ideals().items():
        rows = []
        for gen in gens:
            terms = []
            for exps, coeff in gen.terms():
                terms.append((tuple((v, int(e)) for v, e in enumerate(exps) if e), int(coeff)))
            rows.append(terms)
        out[name] = rows
    return out


def evaluate(terms: Sequence[tuple[tuple[tuple[int, int], ...], int]], powers: Sequence[Sequence[Gauss]]) -> Gauss:
    total = Gauss()
    for monomial, coeff in terms:
        value = Gauss(coeff)
        for var, exp in monomial:
            value = value * powers[var][exp]
        total = total + value
    return total


def power_table(zp: Sequence[Gauss], top: int = 6) -> list[list[Gauss]]:
    table = []
    for z in zp:
        row = [Gauss(1)]
        for _ in range(top):
            row.append(row[-1] * z)
        table.append(row)
    return table


def membership(zp: Sequence[Gauss]) -> tuple[tuple[str, ...], bool, bool]:
    """Closures among the twelve that contain z', and membership in V(Q) and V(G)."""
    powers = power_table(zp)
    ideals = ideal_terms()
    inside = [name for name in ORBITS if all(evaluate(gen, powers).iszero() for gen in ideals[name])]
    in_q = all(evaluate(gen, powers).iszero() for gen in ideals["VQ"])
    in_g = all(evaluate(gen, powers).iszero() for gen in ideals["VG"])
    return tuple(inside), in_q, in_g


def complex_rank(rows: Sequence[Sequence[Gauss]]) -> int:
    """Rank over Q(i) of a matrix with Gaussian entries: half the rank of its real embedding [[A, -B], [B, A]]."""
    real_rows: list[list[Fraction]] = []
    for row in rows:
        real_rows.append([x.re for x in row] + [-x.im for x in row])
        real_rows.append([x.im for x in row] + [x.re for x in row])
    twice = eq.qrank(real_rows)
    if twice % 2:
        raise ArithmeticError("the real embedding of a complex matrix has even rank")
    return twice // 2


def orbit_rank(zp: Sequence[Gauss]) -> int:
    """Complex dimension of the H-orbit: the rank of `strata_regularity.h_generators` over Q(i)."""
    return complex_rank([[Gauss.lift(x) for x in row] for row in sr.h_generators(list(zp))])


@functools.cache
def representative_patterns() -> dict[str, tuple[str, ...]]:
    return {name: membership([Gauss(x) for x in point])[0] for name, point in sr.REPS.items()}


def nullity(terms: Terms) -> int:
    return int(eq.nullity(operand_vector(terms)))


def orbit_mismatch(nul: int, rank: int, orbit: str) -> str | None:
    """The disagreement between the cd_core nullity and H-orbit rank of a point and those of its named orbit."""
    expect = sr.NULLITY.get(orbit, 16)
    if nul != expect:
        return f"nullity mismatch: cd_core {nul}, orbit {orbit} has nullity {expect}"
    if rank != sr.DIMS[orbit]:
        return f"orbit rank {rank} differs from the dimension {sr.DIMS[orbit]} of orbit {orbit}"
    return None


def classify(terms: Terms) -> dict[str, Any]:
    """Nullity, split coordinates, closures, orbit and orbit rank of one operand."""
    y = operand_vector(terms)
    zp = to_split(y)
    nul = int(eq.nullity(y))
    inside, in_q, in_g = membership(zp)
    rank = orbit_rank(zp)
    row: dict[str, Any] = {
        "nullity": nul,
        "split": [z.text() for z in zp],
        "closures": list(inside),
        "in_VQ": in_q,
        "in_VG": in_g,
        "orbit_rank": rank,
    }
    if nul >= 8:
        matches = [name for name, pattern in representative_patterns().items() if pattern == inside]
        if len(matches) != 1:
            raise SystemExit(f"nullity {nul} operand with closures {inside} matches representatives {matches}")
        orbit = matches[0]
        problem = orbit_mismatch(nul, rank, orbit)
        if problem:
            raise SystemExit(problem)
        row["orbit"] = orbit
    elif nul == 4:
        if inside:
            raise SystemExit(f"nullity 4 operand lies in the closures {inside}")
        row["orbit"] = {(True, False): "S4_VQ", (False, True): "S4_VG", (True, True): "S4_VQ_VG"}.get((in_q, in_g))
        if row["orbit"] is None:
            raise SystemExit("nullity 4 operand outside V(Q) and V(G)")
    else:
        if nul != 0 or in_q or in_g:
            raise SystemExit(f"nullity {nul} operand with Q = 0 {in_q}, G = 0 {in_g}")
        row["orbit"] = "S0"
    return row


def two_term(i: int, j: int, t: int = 1) -> Terms:
    return {i: Fraction(1), j: Fraction(t)}


def rank_path(t: Fraction) -> Terms:
    """The dimension-32 rank path of `rank_attachments.path_coefficients`, support (1, 10, 18, 25)."""
    terms = {1: Fraction(1), 10: (t - 1) ** 2, 18: t * (3 - t) / 2, 25: -t * (t - 1) / 2}
    return {index: c for index, c in terms.items() if c != 0}


def label(terms: Terms) -> str:
    out = ""
    for index, coefficient in sorted(terms.items()):
        if coefficient == 0:
            continue
        sign = "-" if coefficient < 0 else "+"
        magnitude = abs(coefficient)
        body = f"e{index}" if magnitude == 1 else f"{magnitude}*e{index}"
        out += (f" {sign} " if out else ("-" if sign == "-" else "")) + body
    return out.replace("+ -", "- ")


# Operands by key. The key is the name that the case files use where one exists.
OPERANDS: dict[str, Terms] = {
    "e1+e17": two_term(1, 17),
    "e1+e26": two_term(1, 26),
    "e2+e27": two_term(2, 27),
    "e1+e10": two_term(1, 10),
    "e1+e18": two_term(1, 18),
    "e1+e24": two_term(1, 24),
    "e17-e10": two_term(17, 10, -1),
    "e17-e2": two_term(17, 2, -1),
    "e1+e9": two_term(1, 9),
    "e1-e10": two_term(1, 10, -1),
    "B12": {1: Fraction(1), 10: Fraction(1), 20: Fraction(1), 31: Fraction(1)},
    "C8": {1: Fraction(1), 8: Fraction(1), 18: Fraction(1), 27: Fraction(1)},
    "A16": {1: Fraction(1), 10: Fraction(1), 18: Fraction(1), 25: Fraction(-1)},
    "path t=1/2": rank_path(Fraction(1, 2)),
    "path t=3/2": rank_path(Fraction(3, 2)),
}


def classify_all() -> dict[str, dict[str, Any]]:
    keys = list(OPERANDS)
    rows = parallel.ordered_map(classify, [OPERANDS[k] for k in keys], min_items=1)
    out = {}
    for key, row in zip(keys, rows, strict=True):
        row["terms"] = {str(i): str(c) for i, c in sorted(OPERANDS[key].items()) if c != 0}
        out[key] = row
    return out


# ---------------------------------------------------------------------------------------------------------------
# Gate on the split-coordinate map


def map_gate() -> dict[str, Any]:
    """Every representative maps through `y_from_split` and back to itself, classifies as itself, and the opposite
    phase direction mislabels a sign-paired orbit."""
    rows = []
    ok = True
    for name, point in sr.REPS.items():
        y = eq.y_from_split([Fraction(x) for x in point])
        zp = to_split(y)
        back_ok = all(z == x for z, x in zip(zp, point, strict=True))
        again = from_split(zp)
        again_ok = all(a == b for a, b in zip(again, y, strict=True))
        inside = membership(zp)[0]
        name_ok = [n for n, pattern in representative_patterns().items() if pattern == inside] == [name]
        nul = int(eq.nullity(y))
        rank = orbit_rank(zp)
        row_ok = back_ok and again_ok and name_ok and nul == sr.NULLITY.get(name, 16) and rank == sr.DIMS[name]
        rows.append(
            {"orbit": name, "round_trip": back_ok and again_ok, "named_back": name_ok, "nullity": nul, "rank": rank}
        )
        ok = ok and row_ok
    return {"pass": ok, "rows": rows}


def reversed_direction_labels() -> dict[str, str | None]:
    """Mutation control: map each representative's y with the phase i^(+popcount) instead of i^(-popcount)."""
    out: dict[str, str | None] = {}
    for name, point in sr.REPS.items():
        y = eq.y_from_split([Fraction(x) for x in point])
        zp = []
        for k in range(1, 16):
            re, im = ((1, 0), (0, 1), (-1, 0), (0, -1))[eq.popcount(k) % 4]
            zp.append(Gauss(re, im) * Gauss(y[k], y[16 + k]))
        inside = membership(zp)[0]
        match = [n for n, pattern in representative_patterns().items() if pattern == inside]
        out[name] = match[0] if len(match) == 1 else None
    return out


# ---------------------------------------------------------------------------------------------------------------
# Incidences and lines


def in_closure(closure: str, terms: Terms) -> bool:
    """Membership of the operand in the closure; the origin lies in every closure (each generator is homogeneous)."""
    if not terms:
        return True
    powers = power_table(to_split(operand_vector(terms)))
    return all(evaluate(gen, powers).iszero() for gen in ideal_terms()[closure])


def add(a: Terms, b: Terms, s: Fraction) -> Terms:
    out = dict(a)
    for index, coefficient in b.items():
        out[index] = out.get(index, Fraction(0)) + s * coefficient
    return {i: c for i, c in out.items() if c != 0}


def xor_of(indices: Sequence[int]) -> int:
    value = 0
    for index in indices:
        value ^= index
    return value


def is_flat(indices: Sequence[int]) -> bool:
    """A support that a four-term block design realizes: two indices, or four with XOR zero (a 2-flat)."""
    return len(indices) == 2 or (len(indices) == 4 and xor_of(indices) == 0)


def flats_of(terms: Terms) -> list[tuple[int, ...]]:
    """2-flats {i, j, k, l} that contain the support of a two-term or four-term operand; 0 and 16 are excluded."""
    support = sorted(terms)
    if len(support) == 4 and xor_of(support) == 0:
        return [tuple(support)]
    if len(support) != 2:
        return []
    i, j = support
    out = []
    for k in range(1, DIM):
        ell = k ^ i ^ j
        if k < ell and 16 not in (k, ell) and 0 not in (k, ell) and {k, ell}.isdisjoint(support):
            out.append(tuple(sorted((i, j, k, ell))))
    return out


def canonical(vector: Sequence[int]) -> bool:
    """One of the two signs of a direction: the first nonzero coefficient is positive."""
    return next(c for c in vector if c) > 0


def rref(rows: Sequence[Terms]) -> tuple[tuple[tuple[int, Fraction], ...], ...]:
    """Reduced row echelon form of operands as rows over Q: a canonical key of their span."""
    matrix = [operand_vector(r) for r in rows]
    pivot_row = 0
    for column in range(DIM):
        pivot = next((r for r in range(pivot_row, len(matrix)) if matrix[r][column] != 0), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        lead = matrix[pivot_row][column]
        matrix[pivot_row] = [x / lead for x in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r != pivot_row and matrix[r][column] != 0:
                factor = matrix[r][column]
                matrix[r] = [x - factor * y for x, y in zip(matrix[r], matrix[pivot_row], strict=True)]
        pivot_row += 1
    return tuple(tuple((i, x) for i, x in enumerate(row) if x != 0) for row in matrix[:pivot_row])


def directions(a_z: Terms) -> list[Terms]:
    """One direction b per plane span(a_Z, b), the plane's simplest: coefficient vectors over a 2-flat containing the
    support of a_Z (entries -2 to 2) and basis-pair operands e_k + sigma e_l anywhere (a support of up to six
    indices). The scaling in C^* maps a_Z + s b to (1 + s' ) a_Z + ... in the same plane, so planes are the
    distinct lines up to H."""
    candidates: list[Terms] = []
    for flat in flats_of(a_z):
        for vector in itertools.product(range(-2, 3), repeat=4):
            if any(vector) and canonical(vector):
                candidates.append({index: Fraction(c) for index, c in zip(flat, vector, strict=True) if c})
    indices = [k for k in range(1, DIM) if k != 16]
    candidates.extend({k: Fraction(1)} for k in indices)
    for k, ell in itertools.combinations(indices, 2):
        candidates.extend({k: Fraction(1), ell: Fraction(sigma)} for sigma in (1, -1))
    candidates.sort(key=lambda b: (len(b), max(abs(c) for c in b.values()), sorted(b.items())))
    seen: set[tuple[tuple[tuple[int, Fraction], ...], ...]] = set()
    out: list[Terms] = []
    for b in candidates:
        key = rref([a_z, b])
        if len(key) == 2 and key not in seen:
            seen.add(key)
            out.append(b)
    return out


def line_job(job: tuple[str, str, Terms, Terms]) -> dict[str, Any] | None:
    """One candidate plane span(a_Z, b), tested along the line a_Z + s b: kept when a(s) lies in the closure at every
    test value of s and the generic point is outside the orbit of Z."""
    closure, z_orbit, a_z, b = job
    if not all(in_closure(closure, add(a_z, b, s)) for s in LINE_S):
        return None
    points = [add(a_z, b, s) for s in GENERIC_S]
    if not all(points):
        return None
    tally: dict[str, int] = {}
    for point in points:
        orbit = classify(point)["orbit"]
        tally[orbit] = tally.get(orbit, 0) + 1
    generic = max(tally, key=lambda o: tally[o])
    if generic == z_orbit:
        return None
    support = sorted(set(a_z) | set(b))
    return {
        "direction": label(b),
        "terms": {str(i): str(c) for i, c in sorted(b.items())},
        "support": support,
        "flat": is_flat(support),
        "generic_orbit": generic,
        "special_points": {o: n for o, n in sorted(tally.items()) if o != generic},
    }


def plane_point(other: Terms, a_z: Terms, b: Terms) -> str | None:
    """The parameter s with other proportional to a_Z + s b (the line's point on the ray of `other`), or None."""
    if len(rref([a_z, b, other])) != 2:
        return None
    # other = alpha a_Z + beta b; solve on two coordinates where a_Z and b are independent.
    for i, j in itertools.combinations(sorted(set(a_z) | set(b)), 2):
        det = a_z.get(i, 0) * b.get(j, 0) - a_z.get(j, 0) * b.get(i, 0)
        if det != 0:
            alpha = (other.get(i, 0) * b.get(j, 0) - other.get(j, 0) * b.get(i, 0)) / det
            beta = (a_z.get(i, 0) * other.get(j, 0) - a_z.get(j, 0) * other.get(i, 0)) / det
            return str(Fraction(beta) / Fraction(alpha)) if alpha != 0 else "infinity"
    return None


def chord_job(job: tuple[str, str, str, Terms, str, Terms]) -> dict[str, Any]:
    """The line through two measured operands a_Z (in Z) and c: a(s) = a_Z + s (c - a_Z), a(1) = c."""
    closure, z_orbit, key, a_z, other, c = job
    b = add(c, a_z, Fraction(-1))
    inside = all(in_closure(closure, add(a_z, b, s)) for s in LINE_S)
    points = [add(a_z, b, s) for s in GENERIC_S]
    tally: dict[str, int] = {}
    if inside:
        for point in points:
            orbit = classify(point)["orbit"]
            tally[orbit] = tally.get(orbit, 0) + 1
    support = sorted(set(a_z) | set(c))
    row: dict[str, Any] = {
        "from": key,
        "to": other,
        "support": support,
        "flat": is_flat(support),
        "in_closure_of_Y": inside,
        "generic_orbit": max(tally, key=lambda o: tally[o]) if tally else None,
    }
    if inside:
        row["nullity_along"] = {str(s): nullity(add(a_z, b, s)) for s in NULLITY_S}
    return row


def incidence_rows(classified: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """For each Y -> Z: measured operands in the closure of Y and in the orbit of Z, and planes from them."""
    rows = []
    for closure, z_orbit in INCIDENCES:
        in_y_closure = [k for k, r in classified.items() if closure in r["closures"]]
        in_y_open = [k for k, r in classified.items() if r.get("orbit") == closure]
        in_z = [k for k, r in classified.items() if r.get("orbit") == z_orbit]
        lines: dict[str, list[dict[str, Any]]] = {}
        for key in in_z:
            jobs = [(closure, z_orbit, OPERANDS[key], b) for b in directions(OPERANDS[key])]
            found = [r for r in parallel.ordered_map(line_job, jobs) if r is not None]
            for r in found:
                b = {int(i): Fraction(c) for i, c in r["terms"].items()}
                points = [add(OPERANDS[key], b, s) for s in NULLITY_S]
                r["nullity_along"] = {str(s): nullity(a) if a else None for s, a in zip(NULLITY_S, points, strict=True)}
                r["measured_in_plane"] = {
                    other: point
                    for other in classified
                    if other != key and (point := plane_point(OPERANDS[other], OPERANDS[key], b)) is not None
                }
            lines[key] = found
        chords = parallel.ordered_map(
            chord_job,
            [
                (closure, z_orbit, key, OPERANDS[key], other, OPERANDS[other])
                for key in in_z
                for other, row in classified.items()
                if other != key and closure in row["closures"] and row["orbit"] != z_orbit
            ],
            min_items=1,
        )
        rows.append(
            {
                "incidence": f"{DISPLAY[closure]} -> {DISPLAY[z_orbit]}",
                "closure": closure,
                "z_orbit": z_orbit,
                "measured_in_open_orbit_of_Y": in_y_open,
                "measured_in_closure_of_Y": in_y_closure,
                "measured_in_Z": in_z,
                "lines": lines,
                "chords": chords,
            }
        )
    return rows


# Named arcs through two measured operands, as (name, base operand, direction, parameters): a(beta) = base + beta b.
NAMED_ARCS: tuple[tuple[str, str, Terms, tuple[Fraction, ...]], ...] = (
    (
        "W8 to N-: e1 + e10 + beta (e18 - e25)",
        "e1+e10",
        {18: Fraction(1), 25: Fraction(-1)},
        tuple(Fraction(x) for x in (-2, -1, Fraction(-1, 2), 0, Fraction(1, 2), 1, 2, 3)),
    ),
    (
        "E8-bar to VB: e1 + e18 + beta (e8 + e27)",
        "e1+e18",
        {8: Fraction(1), 27: Fraction(1)},
        tuple(Fraction(x) for x in (-2, -1, Fraction(-1, 2), 0, Fraction(1, 2), 1, 2, 3)),
    ),
)


def named_arc_rows() -> list[dict[str, Any]]:
    rows = []
    for name, base, b, betas in NAMED_ARCS:
        points = []
        for beta in betas:
            point = add(OPERANDS[base], b, beta)
            row = classify(point)
            points.append(
                {"beta": str(beta), "operand": label(point), "nullity": row["nullity"], "orbit": row["orbit"]}
            )
        rows.append({"arc": name, "points": points})
    return rows


def rank_path_row() -> dict[str, Any]:
    """The measured rank path a(t): orbit at generic t, nullity at the measured parameters."""
    params = (Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2))
    measured = {str(t): {"nullity": nullity(rank_path(t)), "orbit": classify(rank_path(t))["orbit"]} for t in params}
    generic = {}
    for t in (Fraction(3), Fraction(-1), Fraction(5, 2), Fraction(1, 3)):
        row = classify(rank_path(t))
        generic[str(t)] = {"nullity": row["nullity"], "orbit": row["orbit"]}
    return {"measured": measured, "generic": generic}


# ---------------------------------------------------------------------------------------------------------------
# Measured values (read from the retained records)


def interval_text(stat: dict[str, float]) -> str:
    return f"{stat['mean']:.2f} [{stat['lo']:.2f}, {stat['hi']:.2f}]"


def read_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


IBM_FULL = "results/live/2026-11-06T183538.809814Z"
IBM_CMAP_FEZ = "results/live/2026-11-06T201037.234804Z"
IBM_CMAP_MARRAKESH = "results/live/2026-11-06T200832.558771Z"
IBM_PARALLEL_FEZ = "results/live/2026-11-07T042521.359670Z"
IBM_PARALLEL_KINGSTON = "results/live/2026-11-07T042346.084449Z"
IBM_PARALLEL_ANALYSIS = "results/live/pathion_parallel_coset_analysis.json"
IBM_RANK_SECTOR = "results/live/2026-10-13T032011.664435Z"
TUNA_COIN = "results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json"
TUNA_STOPPED = "results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json"
ASCELLA_FOUR = "results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
ASCELLA_PAIRS = "results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
ASCELLA_PERSIST = "results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00"
ASCELLA_SLICE = "results/quandela/runs/2026-10-30T190300Z-qpu_ascella-a5-kernel-slice"
ASCELLA_SLICE_ANALYSIS = "docs/evidence/a5-photonic-crosschecks/ascella-hardware-kernel-slice.json"
FINDINGS = "results/live/PATHION_KERNEL_MAP_FINDINGS.md"
# The findings call these two full-map readings unresolved: the pooled visibility interval reaches zero.
UNRESOLVED_FULL_MAP = {"e1+e26", "e17-e10"}

TAG = {
    "e1+e17": "e1pe17",
    "e1+e26": "e1pe26",
    "e2+e27": "e2pe27",
    "e1+e10": "e1pe10",
    "e1+e18": "e1pe18",
    "e1+e24": "e1pe24",
    "e17-e10": "twin_e17me10",
    "e17-e2": "twin_e17me2",
}


def nhat_stat(path: str, key: str) -> dict[str, float]:
    collect = read_json(f"{path}/collect.json")[1]
    return collect["measured_statistics"]["summary_interval"][key]


def case_rows() -> list[dict[str, Any]]:
    """(operand, case, observable, measured) for every reading of an A_5 operand on hardware."""
    rows: list[dict[str, Any]] = []

    def add_row(operand: str, case: str, record: str, backend: str, observable: str, measured: str) -> None:
        names = ["B12", "C8", "A16"] if operand == "B12, C8, A16 blocks" else [operand]
        rows.append(
            {
                "operands": names,
                "case": case,
                "record": record,
                "backend": backend,
                "observable": observable,
                "measured": measured,
            }
        )

    full_keys = {k: f"kmap_{v}_nullity_estimate" for k, v in TAG.items()}
    for operand, key in full_keys.items():
        text = interval_text(nhat_stat(IBM_FULL, key))
        if operand in UNRESOLVED_FULL_MAP:
            text += " (unresolved in the findings)"
        add_row(
            operand,
            "ibm-fez-pathion-kernel-map",
            IBM_FULL,
            "ibm_fez",
            "N_hat, raw, Student t 95% over 5 replicas",
            text,
        )
    for record, backend, reps in ((IBM_CMAP_FEZ, "ibm_fez", 17), (IBM_CMAP_MARRAKESH, "ibm_marrakesh", 11)):
        for operand, tag in TAG.items():
            if operand == "e17-e10":
                continue
            key = f"cmap_{tag}_nullity_estimate"
            add_row(
                operand,
                "pathion-coset-map",
                record,
                backend,
                f"N_hat, raw, Student t 95% over {reps} replicas",
                interval_text(nhat_stat(record, key)),
            )
    analysis = read_json(IBM_PARALLEL_ANALYSIS)
    for backend, record in (("ibm_fez", IBM_PARALLEL_FEZ), ("ibm_kingston", IBM_PARALLEL_KINGSTON)):
        pooled = analysis["backends"][backend]["operand_nhat"]
        for operand, tag in TAG.items():
            if operand == "e17-e10":
                continue
            stat = pooled[f"cmap_{tag}"]
            add_row(
                operand,
                "pathion-parallel-coset",
                record,
                backend,
                f"N_hat, raw, Student t 95% over {int(stat['n'])} placements",
                interval_text(stat),
            )
        blocks = analysis["backends"][backend]["rules"]["four_term_blocks"]["blocks"]
        for name, operand in (("ftb_B12_c2", "B12"), ("ftb_C8_c5", "C8")):
            block = blocks[name]
            lo, hi = block["visibility_interval"]
            add_row(
                operand,
                "pathion-parallel-coset",
                record,
                backend,
                "four-term block visibility (coset 2 of B12, coset 5 of C8)",
                f"{block['visibility_mean']:.3f} [{lo:.3f}, {hi:.3f}]",
            )
    tuna = read_json(TUNA_COIN)["templates"]
    for operand, template in (("e1+e18", "ba"), ("e1+e26", "bb"), ("e1+e17", "b0")):
        entry = tuna[template]
        add_row(
            operand,
            "tuna-17-coset-coin-series",
            TUNA_COIN,
            "tuna-17",
            f"selector contrast of block {template} (ideal {0.5 if template != 'b0' else 0.0})",
            f"{entry['selector_contrast']:.4f} +- {entry['selector_se']:.4f}",
        )
    pinned = re.search(
        r"^STOPPED_B0_SELECTOR = \(([-0-9.]+), ([-0-9.]+)\)$",
        (ROOT / "scripts/qi_pathion_coset_coin_cases.py").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if pinned is None:
        raise SystemExit("STOPPED_B0_SELECTOR is not pinned in scripts/qi_pathion_coset_coin_cases.py")
    add_row(
        "e1+e17",
        "tuna-17-coset-block-series (stopped)",
        TUNA_STOPPED,
        "tuna-17",
        "selector contrast of block b0 (ideal 0), pinned as STOPPED_B0_SELECTOR",
        f"{float(pinned.group(1)):+.4f} +- {float(pinned.group(2)):.4f}",
    )
    for record, case in ((ASCELLA_FOUR, "ascella-pathion-four-term-blocks"),):
        readings = read_json(f"{record}/analysis.json")["readings"]
        for operand in ("B12", "C8", "A16"):
            levels = [r["a_prime"] for r in readings if r["operand"] == operand and r["arm"] == "T"]
            ideal = sorted({round(r["ideal"], 4) for r in readings if r["operand"] == operand and r["arm"] == "T"})
            add_row(
                operand,
                case,
                record,
                "qpu:ascella",
                f"anchor and dark normalized T level of its blocks (ideal {', '.join(map(str, ideal))})",
                f"{min(levels):.4f} to {max(levels):.4f} over {len(levels)} readings",
            )
    for record, case in (
        (ASCELLA_PAIRS, "ascella-pathion-coset-block-pairs"),
        (ASCELLA_PERSIST, "ascella-pathion-mesh-persistence"),
    ):
        add_row(
            "B12, C8, A16 blocks",
            case,
            record,
            "qpu:ascella",
            "two blocks per photon (a to i, anchors p and q); instrument not admitted at 0.07",
            "see PATHION_KERNEL_MAP_FINDINGS.md",
        )
    slice_obs = read_json(ASCELLA_SLICE_ANALYSIS)["observations"]
    by_name = {o["name"]: o for o in slice_obs}
    for operand, name in (("e1+e9", "control-dark"), ("e1+e10", "kernel-dark"), ("e1-e10", "mutation-dark")):
        o = by_name[name]
        add_row(
            operand,
            "ascella-a5-kernel-slice",
            ASCELLA_SLICE,
            "qpu:ascella",
            f"conditional success of the dark probe (ideal {o['ideal_success']})",
            f"{o['conditional_success']:.4f}",
        )
    add_row(
        "e1+e10",
        "ascella-a5-kernel-slice",
        ASCELLA_SLICE,
        "qpu:ascella",
        f"conditional success of the bright probe (ideal {by_name['kernel-bright']['ideal_success']})",
        f"{by_name['kernel-bright']['conditional_success']:.4f}",
    )
    for operand, name in (("e1+e9", "control-bright"), ("e1-e10", "mutation-bright")):
        o = by_name[name]
        add_row(
            operand,
            "ascella-a5-kernel-slice",
            ASCELLA_SLICE,
            "qpu:ascella",
            f"conditional success of the bright probe (ideal {o['ideal_success']})",
            f"{o['conditional_success']:.4f}",
        )
    for t, operand in (("0", "e1+e10"), ("1/2", "path t=1/2"), ("1", "e1+e18"), ("3/2", "path t=3/2"), ("2", "A16")):
        add_row(
            operand,
            "ibm-fez-rank-sector",
            IBM_RANK_SECTOR,
            "ibm_fez",
            f"selector-success probes of the eight sector blocks of L_a(t) at t = {t} (no nullity estimate)",
            "bright minus dark contrast +0.612 to +0.868 over 8 sectors (CAMPAIGN_FINDINGS.md section 6)"
            if t == "1"
            else "probe success probabilities in the retained raw data (CAMPAIGN_FINDINGS.md section 6)",
        )
    return rows


STRATUM_NAMES = {
    "S0": "S0: nullity 0, outside R_4",
    "S4_VQ": "S4: V(Q) only",
    "S4_VG": "S4: V(G) only",
    "S4_VQ_VG": "S4: V(Q) and V(G)",
}


def orbit_name(orbit: str) -> str:
    return DISPLAY.get(orbit) or STRATUM_NAMES[orbit]


def write_table(path: Path, classified: dict[str, dict[str, Any]], cases: list[dict[str, str]]) -> None:
    columns = [
        "operand",
        "terms",
        "case",
        "backend",
        "cd_core_nullity",
        "observable",
        "measured",
        "orbit",
        "h_orbit_dim",
        "closures",
        "record",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        for case in cases:
            for name in case["operands"]:
                row = classified[name]
                writer.writerow(
                    [
                        name,
                        label(OPERANDS[name]),
                        case["case"],
                        case["backend"],
                        row["nullity"],
                        case["observable"],
                        case["measured"],
                        orbit_name(row["orbit"]),
                        row["orbit_rank"],
                        " ".join(DISPLAY[c] for c in row["closures"]),
                        case["record"],
                    ]
                )


# Readings of sign networks that are not L_a of any element of A_5: no H-orbit applies.
CONTROLS: tuple[dict[str, str], ...] = (
    {
        "control": "cocycle-free e1 + e10 and e1 + e18 (every SELECT sign replaced by the XOR permutation)",
        "cases": (
            "ibm-fez-pathion-kernel-map; pathion-coset-map; pathion-parallel-coset; tuna-17-coset-coin-series (xor_ba)"
        ),
        "reason": "the sign table has no cd_core cocycle, so the matrix is not L_a for any a; ideal N_hat -6 and -2",
    },
    {
        "control": "flipped e1 + e18 (one SELECT sign negated at selector 1, data input 3)",
        "cases": "ibm-fez-pathion-kernel-map",
        "reason": "a single negated entry of the L_(e1+e18) sign table is not a left multiplication; ideal nullity 11",
    },
    {
        "control": "skeleton e1 + e18 (permutation without signs)",
        "cases": "ibm-fez-pathion-kernel-map",
        "reason": "a signless permutation network, not a left multiplication",
    },
    {
        "control": "readout-flip twins and mirrored repeats (X on every qubit before measurement; repeated arms)",
        "cases": "pathion-parallel-coset",
        "reason": "readout and drift controls of the same operand, which keeps the orbit of its parent",
    },
    {
        "control": (
            "mutated four-term arms F, C, N (flipped input sign, all-plus block, one negated entry) "
            "and null arms E0, E1, D"
        ),
        "cases": "ascella-pathion-four-term-blocks; pathion-parallel-coset",
        "reason": (
            "arms of a block of B12, C8 or A16 with a changed input or sign table; "
            "the block itself keeps the parent orbit"
        ),
    },
)


def max_generator_degree() -> int:
    """Largest total degree of a closure or hypersurface generator in z'."""
    return max(
        sum(exp for _, exp in monomial) for gens in ideal_terms().values() for gen in gens for monomial, _ in gen
    )


def build() -> dict[str, Any]:
    degree = max_generator_degree()
    if len(LINE_S) < degree + 1:
        raise SystemExit(f"{len(LINE_S)} test values of s do not decide membership for degree {degree}")
    gate = map_gate()
    if not gate["pass"]:
        raise SystemExit("the split-coordinate map gate failed")
    for t, key in ((0, "e1+e10"), (1, "e1+e18"), (2, "A16")):
        if rank_path(Fraction(t)) != OPERANDS[key]:
            raise SystemExit(f"the rank path at t = {t} differs from {key}")
    classified = classify_all()
    return {
        "generator_degree_max": degree,
        "map_gate": gate,
        "operands": classified,
        "incidences": incidence_rows(classified),
        "rank_path": rank_path_row(),
        "named_arcs": named_arc_rows(),
        "controls": list(CONTROLS),
    }


def self_test() -> list[str]:
    """Controls that must fail: the opposite phase direction mislabels the sign-paired orbits, and a nullity or an
    orbit rank off by one is reported as a mismatch."""
    failures = []
    swapped = {name: got for name, got in reversed_direction_labels().items() if got != name}
    if set(swapped) != {"Xp", "Xm", "Vap", "Vam", "Np", "Nm"}:
        failures.append(f"the opposite phase direction relabeled {sorted(swapped)}, not the three sign pairs")
    if orbit_mismatch(12, 7, "VB") is not None:
        failures.append("the correct nullity and rank of VB read as a mismatch")
    if orbit_mismatch(8, 7, "VB") is None:
        failures.append("a nullity 8 point passed as VB")
    if orbit_mismatch(12, 8, "VB") is None:
        failures.append("an orbit rank 8 point passed as VB")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="directory that receives result.json and table.tsv")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        failures = self_test()
        print("self-test: every control fails as required" if not failures else "\n".join(failures))
        return 1 if failures else 0
    result = build()
    if args.out is None:
        print(json.dumps({k: result[k] for k in ("operands",)}, indent=1, sort_keys=True))
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    cases = case_rows()
    result["cases"] = cases
    (args.out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    write_table(args.out / "table.tsv", result["operands"], cases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
