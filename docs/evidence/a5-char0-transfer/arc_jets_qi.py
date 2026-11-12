"""The arc-jet ranks of the E8-bar fiber cones are lower bounds for h_d over Q(i).

`../a5-exceptional-fibers/arc-jets/jet_rank.py` evaluates, modulo a split prime p with i -> r, the generators G of
I = (G_1, ..., G_21) on arcs Phi(w, rho, sigma, e, zeta) of the slice V(J), and ranks the functionals
f -> coefficients of s^(d v + k), k < e, of f(G(t(s))) on k[y]_d (v = min val G_j, e = min val t_i). Every arc
parameter is a polynomial in s with integer coefficients, and Phi divides only by 2, by 1 + w, by (1 + w)^2 + 1 and
by the parameter e, whose constant terms are 1, 2 and an integer prime to p. The same integers and the same formulas
therefore define an arc over Q(i) whose series coefficients lie in the localization of Z[i] at P = (p, i - r), and
reduction modulo P is a ring homomorphism that carries it to the modular arc.

Reduction can only raise a valuation: a coefficient that vanishes modulo P may be nonzero over Q(i), in which case
the functionals over Q(i) are other functionals and the modular rank says nothing (the counterexample to the
truncation transfer, A5-316, has this shape). This script closes that gap exactly, in three parts.

1. J(Phi) = 0 over Q(i), as an identity in (w, rho, sigma, e, zeta): Singular substitutes Phi into the J of the
   Q(i) producer (`reduction_check._script`, whose good reduction at both primes A5-247 checks) and reduces modulo
   the three inverse relations. Every arc of the family lies on V(J) over Q(i), so its functionals vanish on L_d.
   A mutated map (t9 + w) must leave a nonzero remainder.
2. For every arc of the retained records (degrees 1 to 7), exact arithmetic over Q(i) to order v + e: each
   coefficient is P-integral and reduces to the modular one; e = min val t_i equals the modular e; every
   coefficient of every G_j(t(s)) below s^v is exactly zero; and the coefficients of s^v, ..., s^(v + e - 1)
   reduce modulo P to the modular ones. The argument uses e and v alone, so a coordinate whose valuation is lower
   over Q(i) than modulo P while e stands is recorded under `coordinate_valuation_drops` and changes no bound.
3. Consequence. The matrix of functionals over Q(i), on any set of column monomials, has P-integral entries and
   reduces entry by entry to the modular matrix, so its rank over Q(i) is at least the modular rank. Every arc of
   every retained record of the target is checked, so each retained rank r_d is a lower bound:
   h_d(F(I) over Q(i)) >= r_d.

The upper bound over Q(i) needs K2 inside L over Q(i), which no record holds for E8-bar; the statement here is the
lower bound alone. Writes arc-jets-qi-<slug>.json beside this file; `--check` recomputes and compares.

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/arc_jets_qi.py --slug e8-nm --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARC_JETS = HERE.parent / "a5-exceptional-fibers" / "arc-jets"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ARC_JETS))

import jet_rank as jr  # noqa: E402
import reduction_check as rc  # noqa: E402
from flint import fmpq, fmpq_poly  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-arc-jets-qi/1"
TARGETS = {"e8-nm": ("e8nm-p32009", "e8nm-p32029"), "e8-np": ("e8np-p32009", "e8np-p32029")}
DEGREES = (1, 2, 3, 4, 5, 6, 7)
Gauss = tuple[Fraction, Fraction]
Coefficients = dict[tuple[int, ...], Gauss]


class Series:
    """A power series over Q(i) modulo s^n: real and imaginary parts as fmpq_poly."""

    __slots__ = ("im", "n", "re")

    def __init__(self, re: Any, im: Any, n: int) -> None:
        self.n = n
        self.re = fmpq_poly(re).truncate(n) if not isinstance(re, fmpq_poly) else re.truncate(n)
        self.im = fmpq_poly(im).truncate(n) if not isinstance(im, fmpq_poly) else im.truncate(n)

    @staticmethod
    def const(a: Fraction | int, b: Fraction | int, n: int) -> Series:
        return Series([_q(a)], [_q(b)], n)

    @staticmethod
    def terms(order: int, coeffs: list[int], n: int) -> Series:
        return Series([0] * order + list(coeffs), [], n)

    def __add__(self, other: Series) -> Series:
        return Series(self.re + other.re, self.im + other.im, self.n)

    def __sub__(self, other: Series) -> Series:
        return Series(self.re - other.re, self.im - other.im, self.n)

    def __neg__(self) -> Series:
        return Series(-self.re, -self.im, self.n)

    def __mul__(self, other: Series) -> Series:
        return Series(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re, self.n)

    def scale(self, a: Fraction | int, b: Fraction | int = 0) -> Series:
        return self * Series.const(a, b, self.n)

    def inv(self) -> Series:
        """The inverse of a series whose constant term is a nonzero rational."""
        if self.im.coeffs()[:1] not in ([], [fmpq(0)]) or not self.re.coeffs() or self.re.coeffs()[0] == 0:
            raise ZeroDivisionError("constant term is not a nonzero rational")
        scale = 1 / self.re.coeffs()[0]
        rest = Series.const(1, 0, self.n) - self.scale(Fraction(int(scale.p), int(scale.q)))
        acc = power = Series.const(1, 0, self.n)
        for _ in range(1, self.n):
            power = power * rest
            acc = acc + power
        return acc.scale(Fraction(int(scale.p), int(scale.q)))

    def coefficient(self, k: int) -> Gauss:
        return _frac(self.re, k), _frac(self.im, k)

    def valuation(self) -> int | None:
        for k in range(self.n):
            if self.coefficient(k) != (0, 0):
                return k
        return None


def _q(value: Fraction | int) -> fmpq:
    value = Fraction(value)
    return fmpq(value.numerator, value.denominator)


def _frac(poly: Any, k: int) -> Fraction:
    coeffs = poly.coeffs()
    if k >= len(coeffs):
        return Fraction(0)
    return Fraction(int(coeffs[k].p), int(coeffs[k].q))


def phi(sign9: int, w: Series, rho: Series, sigma: Series, e: Series, zeta: Series) -> list[Series]:
    """Phi of `laurent.phi_laurent` with i in place of the modular root: [t1, ..., t9]."""
    half = Fraction(1, 2)
    quarter = Fraction(1, 4)
    one = Series.const(1, 0, w.n)
    m = w + one
    minv = m.inv()
    mm = m * m
    mm1 = mm - one
    mp1 = mm + one
    e_inv = e.inv()
    nu = (e + e_inv + one.scale(2)).scale(quarter)
    om = (e - e_inv).scale(quarter)
    t9 = -(w * w * minv).scale(half * sign9)
    t4 = (m * rho + sigma).scale(half)
    t5 = (m * rho - sigma).scale(half)
    t6 = (m * sigma + rho).scale(half)
    t7 = (rho - m * sigma).scale(half)
    z = (mm1 * nu).scale(2)
    wc = (mm1 * om).scale(2)
    t8 = -(wc * minv).scale(0, half)
    t3 = zeta
    t2 = (z + mm1 * zeta) * mp1.inv()
    t1 = ((-(mm1 * t2)) + mp1 * t3 + w * w) * minv.scale(half)
    return [t1, t2, t3, t4, t5, t6, t7, t8, t9]


def arc(prime: int, sign9: int, idx: int, n: int) -> list[Series]:
    """The arc `jet_rank.arc` builds for index IDX at PRIME, with its integer coefficients read in Z."""
    ow, orho, osig, ozeta, kind, k = jr.FAMILIES[idx % len(jr.FAMILIES)]
    w, rho, sig, zeta = (
        Series.terms(o, jr.coefficients(idx, var, prime), n) for var, o in enumerate((ow, orho, osig, ozeta), 1)
    )
    ec = jr.coefficients(idx, 5, prime)
    if kind == "const":
        e_par = Series.const(2 + ec[0] % (prime - 3), 0, n) + Series.terms(1, ec[1:], n)
    else:
        e_par = Series.const(-1, 0, n) + Series.terms(k, ec, n)
    return phi(sign9, w, rho, sig, e_par, zeta)


def evaluate(poly: Coefficients, xs: list[Series]) -> Series:
    n = xs[0].n
    powers: list[list[Series]] = [[Series.const(1, 0, n)] for _ in xs]
    acc = Series([], [], n)
    for exps, (a, b) in poly.items():
        term = Series.const(a, b, n)
        for i, k in enumerate(exps):
            while len(powers[i]) <= k:
                powers[i].append(powers[i][-1] * xs[i])
            if k:
                term = term * powers[i][k]
        acc = acc + term
    return acc


def reduce_gauss(value: Gauss, prime: int, root: int) -> int | None:
    """The image of a + b i modulo (p, i - root), or None when a denominator is divisible by p."""
    a, b = value
    if a.denominator % prime == 0 or b.denominator % prime == 0:
        return None
    return (a.numerator * pow(a.denominator, -1, prime) + b.numerator * pow(b.denominator, -1, prime) * root) % prime


def check_arc(job: tuple[str, int, list[Coefficients], list[Coefficients]]) -> dict[str, Any]:
    """Part 2 for one arc: exact valuations over Q(i) against the modular ones, and the reduction of the jets."""
    name, idx, ideal_j, ideal_g = job
    target = jr.TARGETS[name]
    p, root = target.prime, target.root
    modular = jr.arc(target, idx)
    precision = min(jr.TOP, *(t.top for t in modular))
    mod_vals = [t.val() for t in modular]
    e_mod = min(v if v is not None else precision for v in mod_vals)
    xs_mod = [t.to_series(precision) for t in modular]
    fp_j, fp_g, _ = jr.slice_ideals(name)
    gs_mod = [jr.A.eval_poly(g, xs_mod, precision) for g in fp_g]
    v_mod = min(val for val in (g.val() for g in gs_mod) if val is not None)
    n = v_mod + e_mod
    ts = arc(p, target.sign9, idx, n)
    problems: list[str] = []
    drops: list[str] = []
    exact_vals = []
    for i, (t, mv) in enumerate(zip(ts, mod_vals, strict=True), 1):
        exact = t.valuation()
        exact_vals.append(exact if exact is not None else n)
        if exact_vals[-1] != (mv if mv is not None and mv < n else n):
            drops.append(f"t{i}: valuation {exact} over Q(i), {mv} modulo p")
    # The bound uses e = min val t_i and v = min val G_j alone; a single coordinate may lose valuation in Q(i).
    if min(exact_vals) != e_mod:
        problems.append(f"e = {min(exact_vals)} over Q(i), {e_mod} modulo p")
    for i, t in enumerate(ts, 1):
        for k in range(n):
            image = reduce_gauss(t.coefficient(k), p, root)
            if image is None:
                problems.append(f"t{i}: coefficient of s^{k} is not P-integral")
            elif image != int(xs_mod[i - 1].c.coeffs()[k] if k < len(xs_mod[i - 1].c.coeffs()) else 0):
                problems.append(f"t{i}: coefficient of s^{k} does not reduce to the modular one")
    j_nonzero = sum(1 for g in ideal_j if evaluate(g, ts).valuation() is not None)
    if j_nonzero:
        problems.append(f"{j_nonzero} generators of J are nonzero on the arc modulo s^{n}")
    low_nonzero = 0
    jets_differ = 0
    for j, g in enumerate(ideal_g):
        series = evaluate(g, ts)
        low_nonzero += sum(1 for k in range(v_mod) if series.coefficient(k) != (0, 0))
        for k in range(v_mod, n):
            image = reduce_gauss(series.coefficient(k), p, root)
            if image is None or image != int(gs_mod[j].coeff(k)):
                jets_differ += 1
    if low_nonzero:
        problems.append(f"{low_nonzero} coefficients of G below s^{v_mod} are nonzero over Q(i)")
    if jets_differ:
        problems.append(f"{jets_differ} jet coefficients do not reduce to the modular ones")
    return {"index": idx, "e": e_mod, "v": v_mod, "problems": problems, "drops": drops}


IDENTITY = (
    "def R0=basering;",
    "ring S=(0,I),(w,rho,sig,ee,zeta,minv,einv,pinv),dp;minpoly=I2+1;",
    "poly m=1+w; ideal Rel=m*minv-1,ee*einv-1,(m^2+1)*pinv-1; Rel=std(Rel);",
    "poly nu=(ee+einv+2)/4; poly om=(ee-einv)/4; poly mm1=m^2-1; poly mp1=m^2+1;",
    "poly T9=-({sign})*w^2*minv/2{mutation}; poly T8=-I*mm1*om*minv; poly T3=zeta;",
    "poly T2=(2*mm1*nu+mm1*zeta)*pinv; poly T1=(-mm1*T2+mp1*T3+w^2)*minv/2;",
    "poly T4=(m*rho+sig)/2; poly T5=(m*rho-sig)/2; poly T6=(m*sig+rho)/2; poly T7=(rho-m*sig)/2;",
    "map phi=R0,{images};",
    "ideal Js=reduce(phi(ReducedJ),Rel);",
    '"RESULT j_count",ncols(Js); "RESULT j_nonzero",size(simplify(Js,2));',
    "quit;",
)


def identity(slug: str, variables: list[str], mutate: bool) -> dict[str, int]:
    """Part 1: the number of generators of J over Q(i) that do not vanish on Phi."""
    sign = 1 if slug.endswith("nm") else -1
    images = ",".join(f"T{v[1:]}" for v in variables)
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    script = body + "\n".join(IDENTITY).format(sign=sign, mutation="+w" if mutate else "", images=images) + "\n"
    outcome = rc.rees._run_singular(script, f"arc_jets_qi_identity_{slug}", rc.TIMEOUT_SECONDS)
    rc._require(outcome.status == "completed", f"{slug} identity: {outcome.status} {outcome.diagnostic}")
    return {"generators": int(outcome.results["j_count"]), "nonzero": int(outcome.results["j_nonzero"])}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute(slug: str) -> dict[str, Any]:
    qi = rc._run(slug, None, rc.rees.MODULAR_PRIME)
    names = rc.fiber_inputs._variables(qi["basis"] + qi["generators"])
    rc._require(names == [f"t{i}" for i in range(1, 10)], f"{slug}: slice variables {names}")
    ideal_j = [rc._poly_qi(text, names) for text in qi["basis"]]
    ideal_g = [rc._poly_qi(text, names) for text in qi["generators"]]
    part1 = {"phi": identity(slug, names, False), "mutated": identity(slug, names, True)}
    cells = []
    for name in TARGETS[slug]:
        target = jr.TARGETS[name]
        records = {d: ARC_JETS / "records" / f"{name}-d{d}.json" for d in DEGREES}
        present = {d: path for d, path in records.items() if path.exists()}
        loaded = {d: json.loads(path.read_text(encoding="utf-8")) for d, path in sorted(present.items())}
        indices = sorted({row["index"] for record in loaded.values() for row in record["arcs"]})
        rows = parallel.ordered_map(check_arc, [(name, idx, ideal_j, ideal_g) for idx in indices])
        exact = {row["index"]: (row["v"], row["e"]) for row in rows}
        recorded = {row["index"]: (row["v"], row["e"]) for record in loaded.values() for row in record["arcs"]}
        mismatched = sorted(
            {
                row["index"]
                for record in loaded.values()
                for row in record["arcs"]
                if exact[row["index"]] != (row["v"], row["e"])
            }
        )
        bounds = {}
        for d, path in sorted(present.items()):
            record = loaded[d]
            used = [row["index"] for row in record["arcs"]]
            bounds[str(d)] = {
                "rank": record["rank"],
                "arcs": len(used),
                "arcs_within_checked": set(used) <= set(indices),
                "record": path.relative_to(ROOT).as_posix(),
                "sha256": _sha256(path),
            }
        cells.append(
            {
                "target": name,
                "prime": target.prime,
                "root": target.root,
                "arcs_checked": len(rows),
                "valuations": {f"v={v},e={e}": c for (v, e), c in sorted(Counter(recorded.values()).items())},
                "arcs_with_problems": [{"index": r["index"], "problems": r["problems"]} for r in rows if r["problems"]],
                "coordinate_valuation_drops": [{"index": r["index"], "drops": r["drops"]} for r in rows if r["drops"]],
                "arcs_differing_from_record": mismatched,
                "lower_bounds": bounds,
            }
        )
    holds = (
        part1["phi"]["nonzero"] == 0
        and part1["mutated"]["nonzero"] > 0
        and all(
            not c["arcs_with_problems"]
            and not c["arcs_differing_from_record"]
            and all(b["arcs_within_checked"] for b in c["lower_bounds"].values())
            for c in cells
        )
    )
    return {
        "schema": SCHEMA,
        "slug": slug,
        "field": "Q(i)",
        "statement": "h_d of the fiber cone over Q(i) is at least the retained modular arc-jet rank, d = 1..7",
        "j_on_phi": part1,
        "qi_generators": {"j": len(ideal_j), "g": len(ideal_g)},
        "cells": cells,
        "sha256": {
            "arc_jets_qi": _sha256(Path(__file__)),
            "jet_rank": _sha256(ARC_JETS / "jet_rank.py"),
            "reduction_check": _sha256(HERE / "reduction_check.py"),
        },
        "verdict": "lower_bounds_hold_over_qi" if holds else "failed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=sorted(TARGETS))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    out = HERE / f"arc-jets-qi-{arguments.slug}.json"
    record = compute(arguments.slug)
    text = json.dumps(record, indent=1) + "\n"
    if arguments.write:
        out.write_text(text, encoding="utf-8")
    elif out.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{out.name} differs from the recomputed record")
    print(json.dumps({"slug": arguments.slug, "verdict": record["verdict"]}))
    if record["verdict"] != "lower_bounds_hold_over_qi":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
