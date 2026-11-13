"""Both components of the quadric scheme of E8-bar -> N- and E8-bar -> N+ lie in the exceptional fiber over Q(i).

The modular arc certificate (`../a5-exceptional-fibers/arcs`) substitutes two arc families of the parametrization Phi
of the slice V(J) into the 21 generators G and reads the limit vector F, the first nonzero coefficient vector of
G(x(s)). Here the same two families are substituted into the generators G of the Q(i) producer
(`reduction_check._script`, whose good reduction A5-247 checks), with the family parameters W, R, S, Z, E as ring
variables over Q(i); the slice ideal J enters through the identity J(Phi) = 0 below:

    first-order family:  w = W s, rho = R s, sigma = S s, e = E, zeta = Z s
    order-5 family:      w = W s^2, rho = (R + S) s / 2, sigma = (R - S) s / 2, e = -1 + E s^2, zeta = Z s

Phi satisfies J over Q(i) identically (`arc_jets_qi.identity`, A5-346), so every arc of either family lies on V(J)
and starts at the origin. A relation f of degree d of the fiber cone has f(G) in J + m I^d in the local ring at
the origin, so f(G(x(s))) has order above d nu on an arc of order nu, and f(F) = 0: every limit vector lies in
V(L), L the relation ideal.

Per target and family the record holds the order nu, the nonzero coordinates of F, the rank of [dF | F] at two
integer parameter points (the dimension of the cone over the image of F is at least that rank), the dimension of
the linear span of the image (the rank of the coefficient vectors of F on the parameter monomials, which are
linearly independent functions), and the dimension of the joint span of the two families. The limit vectors reduced
at (32009, i -> 10754) and (32029, i -> 9115) are compared, polynomial by polynomial, with the retained modular
family logs. A control family, the order-5 family recentered at e = 2, has order 3 and rank 2: the order
and the rank of the certified family belong to the center e = -1.

Deduction, stated in the README beside this file: with the quadric ideal K of the fiber cone over Q(i) and its two
minimal primes of dimension 5 and 4 (A5-421), rank 5 puts the closure of the order-5 limits onto the component of
dimension 5, rank 4 together with a first-order limit outside the linear span of the order-5 limits puts the
closure of the first-order limits onto the component of dimension 4, and V(L) is the union of the two.

`--write` writes e8-fiber-components-qi.json beside this file, `--check` recomputes and compares. Both need
Singular 4.4 on PATH.

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/e8_fiber_components_qi.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpq, fmpq_mat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCS = HERE.parent / "a5-exceptional-fibers" / "arcs"
WEIGHT_SLICE = HERE.parent / "a5-kernel-attachments" / "weight-slice-fiber-relations-result.json"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ARCS))

import arc_jets_qi  # noqa: E402
import reduction_check as rc  # noqa: E402
import symfam  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-e8-fiber-components-qi/1"
RECORD = HERE / "e8-fiber-components-qi.json"
GENERATORS = 21
SYMBOLS = sp.symbols("W R S Z E")
POINTS = ((3, 5, 7, 11, 2), (13, 4, 9, 6, 17))
# slug -> (sign of t9, incidence label of the weight-slice record, modular arc targets with their prime and root)
TARGETS = {
    "e8-nm": (1, "E8bar->N-", (("e8nm-p32009", 32009, 10754), ("e8nm-p32029", 32029, 9115))),
    "e8-np": (-1, "E8bar->N+", (("e8np-p32009", 32009, 10754), ("e8np-p32029", 32029, 9115))),
}
# (affine dimension, multiplicity, linear forms) of the two minimal primes of the quadric ideal over Q(i).
EXPECTED_PRIMES = [[4, 4, 14], [5, 11, 9]]
SOURCE_PATHS = (HERE / "e8_fiber_components_qi.py", HERE / "arc_jets_qi.py", HERE / "reduction_check.py")


@dataclass(frozen=True)
class Family:
    """w = W s^a, zeta = Z s; rho and sigma are R s and S s (`mixed` false) or their half sum and half difference;
    e = E (`center` None) or center + E s^2; the limit is read through order n."""

    name: str
    log: str | None
    a: int
    n: int
    mixed: bool
    center: int | None
    expected_order: int
    expected_rank: int


FIRST_ORDER = Family("first_order", "fam_p2_first_order_n2.log", 1, 2, False, None, 2, 4)
ORDER_FIVE = Family("order_five", "fam_near_e-1_j2_a2_b1_c1_d1_n5.log", 2, 5, True, -1, 5, 5)
# Recentered away from e = -1 the order-5 arcs lose order and rank: order 3 and rank 2 in place of 5 and 5.
CONTROL = Family("order_five_recentered_at_2", None, 2, 5, True, 2, 3, 2)
FAMILIES = (FIRST_ORDER, ORDER_FIVE, CONTROL)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def family_script(slug: str, family: Family, variables: list[str]) -> str:
    """The Singular script that prints the order and the limit vector of one family over Q(i).

    The parameters W, R, S, Z, E are the ring variables pW, pR, pS, pZ, pE, and the series variable is x, because the
    producer script holds rings named r and s. For e = E the vector printed is E^n F, a polynomial; pV stands for
    1 / E and is removed by pE pV = 1.
    """
    n = family.n
    sign = TARGETS[slug][0]
    if family.center is None:
        relation = f"ideal rel=std(ideal(x^{n + 1},pE*pV-1));"
        e_series = "poly Ev=pE; poly Vv=pV;"
        multiplier = f"pE^{n}*"
    else:
        relation = f"ideal rel=std(ideal(x^{n + 1}));"
        e_series = (
            f"number ie0=1; ie0=ie0/({family.center}); poly Ev={family.center}+pE*x^2; poly Vv=0; poly pwv=1;"
            f" poly er=-pE*x^2*ie0; for (i=0;i<={n};i++) {{ Vv=Vv+pwv; pwv=reduce(pwv*er,rel); }} Vv=Vv*ie0;"
        )
        multiplier = ""
    if family.mixed:
        rho, sigma = "half*(pR*x+pS*x)", "half*(pR*x-pS*x)"
    else:
        rho, sigma = "pR*x", "pS*x"
    images = ",".join(f"T{name[1:]}" for name in variables)
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    lines = (
        "def R0=basering; short=0;",
        f"ideal Gn=ReducedG; int j; for (j=1;j<=ncols(Gn);j++) {{ Gn[j]=jet(Gn[j],{n}); }}",
        '"RESULT generators",ncols(Gn);',
        "ring Qfam=(0,I),(pW,pR,pS,pZ,pE,pV,x),dp; minpoly=I2+1; short=0;",
        relation,
        "number half=1/2; number quarter=1/4; int i;",
        f"poly w=pW*x^{family.a}; poly rho={rho}; poly sig={sigma}; poly zeta=pZ*x;",
        "poly m=1+w; poly mm=reduce(m*m,rel); poly minv=1; poly pw=1;",
        f"for (i=1;i<={n};i++) {{ pw=reduce(-pw*w,rel); minv=minv+pw; }}",
        "poly u=w+half*w*w; poly qinv=1; pw=1;",
        f"for (i=1;i<={n};i++) {{ pw=reduce(-pw*u,rel); qinv=qinv+pw; }}",
        "qinv=half*qinv;",
        '"RESULT inverse_residues",size(ideal(reduce(m*minv-1,rel),reduce((mm+1)*qinv-1,rel)));',
        e_series,
        '"RESULT e_inverse_residue",size(ideal(reduce(Ev*Vv-1,rel)));',
        "poly nuT=(Ev+2+Vv)*quarter; poly omT=(Ev-Vv)*quarter;",
        "poly mm1=reduce(mm-1,rel);",
        "poly Zc=reduce(2*mm1*nuT,rel); poly Wc=reduce(2*mm1*omT,rel);",
        f"poly T9=reduce(-({sign})*(w*w)*minv*half,rel);",
        "poly T4=reduce((m*rho+sig)*half,rel); poly T5=reduce((m*rho-sig)*half,rel);",
        "poly T6=reduce((m*sig+rho)*half,rel); poly T7=reduce((rho-m*sig)*half,rel);",
        "poly T8=reduce(-I*Wc*minv*half,rel); poly T3=zeta;",
        "poly T2=reduce((Zc+mm1*zeta)*qinv,rel);",
        "poly T1=reduce(((1-mm)*T2+(mm+1)*T3+w*w)*minv*half,rel);",
        '"RESULT origin_residues",size(ideal(subst(T1,x,0),subst(T2,x,0),subst(T3,x,0),subst(T4,x,0),subst(T5,x,0),'
        "subst(T6,x,0),subst(T7,x,0),subst(T8,x,0),subst(T9,x,0)));",
        f"map f=R0,{images};",
        "ideal GX=f(Gn);",
        f"matrix Cf[{n + 1}][{GENERATORS}]; poly g; matrix cm; int o;",
        f"for (j=1;j<={GENERATORS};j++) {{ g=reduce(GX[j],rel); if (g!=0) {{ cm=coeffs(g,x);"
        f" for (o=1;o<=nrows(cm) and o<={n + 1};o++) {{ Cf[o,j]=reduce({multiplier}cm[o,1],rel); }} }} }}",
        "int nu=-1;",
        f"for (o=1;o<={n + 1} and nu<0;o++) {{ for (j=1;j<={GENERATORS};j++) {{ if (Cf[o,j]!=0) {{ nu=o-1; }} }} }}",
        '"RESULT nu",nu;',
        f'if (nu>=0) {{ for (j=1;j<={GENERATORS};j++) {{ "RESULT fj_"+string(j),Cf[nu+1,j]; }} }}',
        "quit;",
    )
    return body + "\n".join(lines) + "\n"


def parse_polynomial(text: str) -> sp.Poly:
    """A Singular polynomial in W, R, S, Z, E over Q(i), printed with short=0, as a polynomial over Q(i)."""
    names = {f"p{name.name}": name for name in SYMBOLS} | {"I": sp.I}
    expression = sp.sympify(text.replace("^", "**"), locals=names)
    return sp.Poly(sp.expand(expression), *SYMBOLS, domain=sp.QQ_I)


def gaussian(value: Any) -> tuple[Fraction, Fraction]:
    real, imaginary = sp.sympify(value).as_real_imag()
    return Fraction(int(real.p), int(real.q)), Fraction(int(imaginary.p), int(imaginary.q))


def coefficients(poly: sp.Poly) -> dict[tuple[int, ...], tuple[Fraction, Fraction]]:
    return {tuple(int(e) for e in monomial): gaussian(value) for monomial, value in poly.as_dict().items()}


def complex_rank(rows: list[list[tuple[Fraction, Fraction]]]) -> int:
    """The rank over Q(i) of a matrix of pairs (real, imaginary): half the FLINT rank of the rational matrix of
    twice the size, [[A, -B], [B, A]] for A + B i."""
    if not rows or not rows[0]:
        return 0
    width = len(rows[0])
    _require(all(len(row) == width for row in rows), "ragged matrix")
    entries = []
    for row in rows:
        entries += [_q(a) for a, _ in row] + [_q(-b) for _, b in row]
    for row in rows:
        entries += [_q(b) for _, b in row] + [_q(a) for a, _ in row]
    doubled = int(fmpq_mat(2 * len(rows), 2 * width, entries).rref()[1])
    _require(doubled % 2 == 0, "the rational rank of a matrix over Q(i) is odd")
    return doubled // 2


def _q(value: Fraction) -> fmpq:
    return fmpq(value.numerator, value.denominator)


def cone_rank(vector: list[sp.Poly], point: tuple[int, ...]) -> int:
    """The rank of [dF/dW, dF/dR, dF/dS, dF/dZ, dF/dE, F] at an integer parameter point."""
    substitution = dict(zip(SYMBOLS, point, strict=True))
    rows = []
    for poly in vector:
        entries = [poly.diff(symbol) for symbol in SYMBOLS] + [poly]
        rows.append([gaussian(entry.as_expr().subs(substitution)) for entry in entries])
    return complex_rank(rows)


def span_rows(vector: list[sp.Poly]) -> list[list[tuple[Fraction, Fraction]]]:
    """One row per parameter monomial: its coefficient in each coordinate of F. The row space is the linear span."""
    tables = [coefficients(poly) for poly in vector]
    zero = (Fraction(0), Fraction(0))
    return [
        [table.get(monomial, zero) for table in tables] for monomial in sorted({m for table in tables for m in table})
    ]


def reduce_polynomial(poly: sp.Poly, prime: int, root: int) -> dict[tuple[int, ...], int]:
    reduced = {}
    for monomial, (real, imaginary) in coefficients(poly).items():
        _require(
            real.denominator % prime != 0 and imaginary.denominator % prime != 0, f"a denominator vanishes mod {prime}"
        )
        value = (
            real.numerator * pow(real.denominator, -1, prime)
            + imaginary.numerator * pow(imaginary.denominator, -1, prime) * root
        ) % prime
        if value:
            reduced[monomial] = value
    return reduced


def modular_comparison(slug: str, family: Family, vector: list[sp.Poly]) -> list[dict[str, Any]]:
    """Each coordinate of F reduced at a split prime against the retained modular family log of the same target."""
    rows = []
    for target, prime, root in TARGETS[slug][2]:
        path = ARCS / target / "families" / str(family.log)
        retained = symfam.load_fj(path.read_text(encoding="utf-8"), prime)
        differing = [
            j for j in range(1, GENERATORS + 1) if reduce_polynomial(vector[j - 1], prime, root) != retained.get(j, {})
        ]
        rows.append(
            {
                "target": target,
                "prime": prime,
                "i_root": root,
                "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "coordinates_that_differ": differing,
            }
        )
    return rows


def run_family(job: tuple[str, Family, list[str]]) -> dict[str, Any]:
    slug, family, variables = job
    outcome = rc.rees._run_singular(
        family_script(slug, family, variables), f"e8_components_{slug}_{family.name}", rc.TIMEOUT_SECONDS
    )
    _require(outcome.status == "completed", f"{slug} {family.name}: {outcome.status} {outcome.diagnostic}")
    results = outcome.results
    row: dict[str, Any] = {
        "family": family.name,
        "generators": int(results["generators"]),
        "series_residues": int(results["inverse_residues"]) + int(results["e_inverse_residue"]),
        "origin_residues": int(results["origin_residues"]),
        "order": int(results["nu"]),
    }
    if row["order"] < 0:
        return row | {"limit": []}
    return row | {"limit": [results[f"fj_{j}"] for j in range(1, GENERATORS + 1)]}


def analyze(slug: str, rows: list[dict[str, Any]], identity: dict[str, dict[str, int]]) -> dict[str, Any]:
    vectors = {row["family"]: [parse_polynomial(text) for text in row["limit"]] for row in rows}
    families = []
    for family, row in zip(FAMILIES, rows, strict=True):
        vector = vectors[family.name]
        entry: dict[str, Any] = {
            key: row[key] for key in ("family", "generators", "series_residues", "origin_residues", "order")
        }
        entry |= {
            "limit_sha256": hashlib.sha256("\n".join(row["limit"]).encode("utf-8")).hexdigest(),
            "nonzero_coordinates": [j for j, poly in enumerate(vector, 1) if not poly.is_zero],
            "cone_ranks": [cone_rank(vector, point) for point in POINTS] if vector else [],
            "span_dimension": complex_rank(span_rows(vector)) if vector else 0,
        }
        if family.log is not None:
            entry["reduction"] = modular_comparison(slug, family, vector)
        families.append(entry)
    first, five = span_rows(vectors[FIRST_ORDER.name]), span_rows(vectors[ORDER_FIVE.name])
    return {
        "slug": slug,
        "incidence": TARGETS[slug][1],
        "phi_identity": identity,
        "families": families,
        "joint_span_dimension": complex_rank(first + five),
    }


def quadric_primes() -> dict[str, list[list[int]]]:
    """Incidence -> the minimal primes (dimension, multiplicity, linear forms) of the quadric ideal over Q(i)."""
    record = json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))
    return {
        cell["incidence"]: cell["hilbert"]["minimal_primes"]
        for cell in record["cells"]
        if cell["source"] == "e8" and cell["characteristic"] == 0
    }


def probe_variables(slug: str) -> list[str]:
    probe = rc.rees._run_singular(
        rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
        + '"RESULT vs",varstr(basering);\nquit;\n',
        "e8_components_vars",
        rc.TIMEOUT_SECONDS,
    )
    _require(probe.status == "completed", f"{slug} variable probe: {probe.status} {probe.diagnostic}")
    return [str(name) for name in probe.results["vs"].split(",")]


def run_job(job: tuple[str, Family | bool, list[str]]) -> dict[str, Any]:
    """One Singular run: a family, or the identity J(Phi) = 0 with (True) or without (False) the mutation."""
    slug, what, variables = job
    if isinstance(what, Family):
        return run_family((slug, what, variables))
    return dict(arc_jets_qi.identity(slug, variables, what))


def compute() -> dict[str, Any]:
    slugs = list(TARGETS)
    variables = dict(zip(slugs, parallel.ordered_map(probe_variables, slugs, min_items=1), strict=True))
    kinds: tuple[Family | bool, ...] = (False, True, *FAMILIES)
    jobs = [(slug, kind, variables[slug]) for slug in slugs for kind in kinds]
    runs = parallel.ordered_map(run_job, jobs, min_items=1)
    primes = quadric_primes()
    targets = []
    for position, slug in enumerate(slugs):
        mine = runs[position * len(kinds) : (position + 1) * len(kinds)]
        row = analyze(slug, mine[2:], {"arc": mine[0], "mutated": mine[1]})
        row["quadric_ideal_minimal_primes"] = primes[TARGETS[slug][1]]
        targets.append(row)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS},
        "weight_slice_record_sha256": hashlib.sha256(WEIGHT_SLICE.read_bytes()).hexdigest(),
        "parameter_points": [list(point) for point in POINTS],
        "targets": targets,
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    if [target.get("slug") for target in record["targets"]] != list(TARGETS):
        problems.append("the record does not hold exactly the two targets")
    for target in record["targets"]:
        name = target["slug"]
        if target["phi_identity"]["arc"]["nonzero"] != 0 or target["phi_identity"]["mutated"]["nonzero"] == 0:
            problems.append(f"{name}: Phi leaves J, or the mutated Phi stays on it")
        primes = target["quadric_ideal_minimal_primes"]
        if primes != EXPECTED_PRIMES:
            problems.append(f"{name}: the quadric ideal has other minimal primes")
            continue
        rows = {row["family"]: row for row in target["families"]}
        if sorted(rows) != sorted(family.name for family in FAMILIES):
            problems.append(f"{name}: the families differ from the three of the script")
            continue
        # The minimal prime of affine dimension d has k linear forms and spans 21 - k dimensions; the family of
        # rank d is dense in it and spans the same.
        span_of_dimension = {prime[0]: GENERATORS - prime[2] for prime in primes}
        for family in FAMILIES:
            row = rows[family.name]
            if row["generators"] != GENERATORS or row["series_residues"] or row["origin_residues"]:
                problems.append(f"{name} {family.name}: generator count or series residues")
            if row["order"] != family.expected_order:
                problems.append(f"{name} {family.name}: order {row['order']}")
            if row["cone_ranks"] != [family.expected_rank] * len(POINTS):
                problems.append(f"{name} {family.name}: cone ranks {row['cone_ranks']}")
        for family in (FIRST_ORDER, ORDER_FIVE):
            row = rows[family.name]
            if row["span_dimension"] != span_of_dimension[family.expected_rank]:
                problems.append(f"{name} {family.name}: span {row['span_dimension']}")
            expected_targets = [(entry[1], entry[2]) for entry in TARGETS[name][2]]
            if [(entry["prime"], entry["i_root"]) for entry in row["reduction"]] != expected_targets:
                problems.append(f"{name} {family.name}: the reduction does not cover both primes")
            if any(entry["coordinates_that_differ"] for entry in row["reduction"]):
                problems.append(f"{name} {family.name}: a reduced limit differs from the modular log")
        if target["joint_span_dimension"] <= rows[ORDER_FIVE.name]["span_dimension"]:
            problems.append(f"{name}: the first-order limits lie in the span of the order-5 limits")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(RECORD.read_text(encoding="utf-8")) != record:
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    for target in record["targets"]:
        print(
            target["slug"],
            [(row["family"], row["order"], row["cone_ranks"], row["span_dimension"]) for row in target["families"]],
            target["joint_span_dimension"],
        )


if __name__ == "__main__":
    main()
