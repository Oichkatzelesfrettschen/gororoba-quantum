"""Good-reduction test of the presolved germ ideal J of an A_5 fiber pair at the split primes of the fiber track.

Conjecture (good reduction): for each split prime p with chosen root r of -1, the monic reduced standard basis of J
over Q(i) (dp, the producer's presolved slice ring) has every coefficient integral at the prime (i -> r) of Z[i] over
p, and its reduction equals the monic reduced standard basis of J computed over F_p from the same producer at
(p, r). The producer is nullity16_rees_fibers' phase-one script, the one fiber_inputs.py specializes into the
headers the rank engine reads. Falsifier: a coefficient whose denominator is divisible by p, a different eliminated
variable set, or a reduced basis over F_p that differs from the reduction of the Q(i) basis. The generators G, reduced
modulo J, are compared the same way. Mutation: adding 1 to one coefficient of the Q(i) basis must break the equality.

Writes reduction-<slug>.json beside this file. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/reduction_check.py --slug xm-nm
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy

HERE = Path(__file__).resolve().parent
ATTACH = HERE.parent / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import fiber_inputs  # noqa: E402
import nullity16_basepoints as basepoints  # noqa: E402
import nullity16_rees_fibers as rees  # noqa: E402

PRIMES = ((32009, 10754), (32029, 9115))
TIMEOUT_SECONDS = 3600
EXTRA = (
    "option(redSB);option(redTail);ideal RJ=std(ReducedJ);",
    '"RESULT rj_count",size(RJ);',
    'for(int i=1;i<=size(RJ);i++){"RESULT rj_"+string(i),RJ[i];}',
    "ideal RG=reduce(ReducedG,RJ);",
    '"RESULT rg_count",size(RG);',
    'for(int i=1;i<=size(RG);i++){"RESULT rg_"+string(i),RG[i];}',
)

Coefficients = dict[tuple[int, ...], tuple[Fraction, Fraction]]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _script(slug: str, root: int | None, prime: int) -> str:
    spec = fiber_inputs.SPEC_BY_SLUG[slug]
    task = fiber_inputs._task(spec.incidence)
    data = basepoints._schur_coordinates(rees._base_task(task))
    cache = fiber_inputs.primary_checkout() / fiber_inputs.LOCAL_BASE / "build" / "inputs" / "survivors"
    candidates = fiber_inputs._candidates(task, data, cache)
    body = rees._phase_one_script(root, task, data, tuple(candidates), prime=prime, embedding=False)
    return body.replace("\nquit;", "") + "\n" + "\n".join(EXTRA) + "\nquit;\n"


def _run(slug: str, root: int | None, prime: int) -> dict[str, Any]:
    outcome = rees._run_singular(_script(slug, root, prime), f"reduction_{prime if root else 'qi'}", TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{slug} root={root}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    count = int(res["rj_count"])
    eliminated = sorted(res[f"eliminated_{i}"] for i in range(1, int(res["eliminated_count"]) + 1))
    return {
        "basis": [res[f"rj_{i}"] for i in range(1, count + 1)],
        "generators": [res[f"rg_{i}"] for i in range(1, int(res["rg_count"]) + 1)],
        "eliminated": eliminated,
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "peak_rss_kib": outcome.peak_rss_kib,
    }


HEADERS = HERE.parent / "a5-exceptional-fibers" / "working" / "build" / "inputs"


def _header(slug: str, prime: int, root: int) -> dict[str, Any]:
    """The retained header the rank certificates bind: its reduced std(J) and G reduced modulo it."""
    path = HEADERS / f"p{prime}-r{root}" / f"{slug}.sing"
    text = path.read_text(encoding="utf-8").replace("quit;", "")
    script = text + "\n" + "\n".join(("ideal ReducedJ=J;ideal ReducedG=G;", *EXTRA)) + "\nquit;\n"
    outcome = rees._run_singular(script, f"header_{prime}", TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{slug} header {prime}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    return {
        "basis": [res[f"rj_{i}"] for i in range(1, int(res["rj_count"]) + 1)],
        "generators": [res[f"rg_{i}"] for i in range(1, int(res["rg_count"]) + 1)],
        "variables": fiber_inputs._variables([text]),
    }


def _gaussian(value: sympy.Expr) -> tuple[Fraction, Fraction]:
    re_part, im_part = sympy.nsimplify(sympy.re(value)), sympy.nsimplify(sympy.im(value))
    return Fraction(str(sympy.Rational(re_part))), Fraction(str(sympy.Rational(im_part)))


def _poly_qi(text: str, names: list[str]) -> Coefficients:
    symbols = sympy.symbols(names)
    expression = sympy.sympify(text.replace("^", "**"), locals={**dict(zip(names, symbols, strict=True)), "I": sympy.I})
    poly = sympy.Poly(sympy.expand(expression), *symbols)
    return {monomial: _gaussian(coefficient) for monomial, coefficient in poly.terms()}


def _poly_fp(text: str, names: list[str], prime: int) -> dict[tuple[int, ...], int]:
    symbols = sympy.symbols(names)
    poly = sympy.Poly(sympy.sympify(text.replace("^", "**"), locals=dict(zip(names, symbols, strict=True))), *symbols)
    return {monomial: int(coefficient) % prime for monomial, coefficient in poly.terms() if int(coefficient) % prime}


def _leading(monomials: list[tuple[int, ...]]) -> tuple[int, ...]:
    # dp: total degree, then reverse lexicographic with the last variable smallest
    return max(monomials, key=lambda m: (sum(m), tuple(-e for e in reversed(m))))


def _reduce(poly: Coefficients, prime: int, root: int) -> tuple[dict[tuple[int, ...], int], list[str]]:
    bad: list[str] = []
    out: dict[tuple[int, ...], int] = {}
    for monomial, (a, b) in poly.items():
        for part in (a, b):
            if part.denominator % prime == 0:
                bad.append(f"{monomial}: denominator {part.denominator}")
        value = (
            a.numerator * pow(a.denominator, -1, prime) + b.numerator * pow(b.denominator, -1, prime) * root
        ) % prime
        if value:
            out[monomial] = value
    return out, bad


def _monic(poly: dict[tuple[int, ...], int], prime: int) -> dict[tuple[int, ...], int]:
    lead = poly[_leading(list(poly))]
    inverse = pow(lead, -1, prime)
    return {m: c * inverse % prime for m, c in poly.items()}


def _image(polys: list[Coefficients], prime: int, root: int, monic: bool) -> tuple[list[list[Any]], list[str]]:
    out, bad = [], []
    for poly in polys:
        image, flags = _reduce(poly, prime, root)
        bad.extend(flags)
        if image:
            out.append(sorted((_monic(image, prime) if monic else image).items()))
    return out, bad


def check(slug: str) -> dict[str, Any]:
    qi = _run(slug, None, rees.MODULAR_PRIME)
    names = fiber_inputs._variables(qi["basis"] + qi["generators"])
    qi_polys = [_poly_qi(text, names) for text in qi["basis"]]
    qi_gens = [_poly_qi(text, names) for text in qi["generators"]]
    rows = []
    for prime, root in PRIMES:
        fp = _run(slug, root, prime)
        same_vars = (
            fp["eliminated"] == qi["eliminated"] and fiber_inputs._variables(fp["basis"] + fp["generators"]) == names
        )
        reduced, bad = _image(qi_polys, prime, root, monic=True)
        gens, gbad = _image(qi_gens, prime, root, monic=False)
        bad.extend(gbad)
        corrupted = [dict(poly) for poly in qi_polys]
        first = next(iter(corrupted[0]))
        a, b = corrupted[0][first]
        corrupted[0][first] = (a + 1, b)
        mutated, _ = _image(corrupted, prime, root, monic=True)
        fp_basis = (
            sorted(sorted(_monic(_poly_fp(t, names, prime), prime).items()) for t in fp["basis"]) if same_vars else []
        )
        fp_gens = [sorted(_poly_fp(t, names, prime).items()) for t in fp["generators"]] if same_vars else []
        key = sorted(reduced)
        fp_key = fp_basis
        hd = _header(slug, prime, root)
        header_vars = hd["variables"] == names
        hd_basis = (
            sorted(sorted(_monic(_poly_fp(t, names, prime), prime).items()) for t in hd["basis"]) if header_vars else []
        )
        hd_gens = [sorted(_poly_fp(t, names, prime).items()) for t in hd["generators"]] if header_vars else []
        rows.append(
            {
                "prime": prime,
                "root": root,
                "same_presolve": same_vars,
                "bad_denominators": bad,
                "fp_basis_size": len(fp["basis"]),
                "reduced_qi_basis_size": len(reduced),
                "bases_equal": same_vars and key == fp_key,
                "generators_equal": same_vars and gens == fp_gens,
                "retained_header_equal": header_vars and hd_basis == key and hd_gens == gens,
                "generator_count": len(fp["generators"]),
                "mutation_corrupted_coefficient_differs": sorted(mutated) != fp_key,
                "fp_wall_seconds": fp["wall_seconds"],
                "fp_peak_rss_kib": fp["peak_rss_kib"],
            }
        )
    return {
        "slug": slug,
        "conjecture": "good reduction of the presolved germ ideal J at each split prime",
        "variables": names,
        "qi_basis_size": len(qi["basis"]),
        "qi_terms": sum(len(p) for p in qi_polys),
        "qi_max_denominator": max(
            (max(a.denominator, b.denominator) for p in qi_polys for a, b in p.values()), default=1
        ),
        "qi_wall_seconds": qi["wall_seconds"],
        "qi_peak_rss_kib": qi["peak_rss_kib"],
        "primes": rows,
        "verdict": (
            "survives"
            if all(
                r["bases_equal"] and r["generators_equal"] and r["retained_header_equal"] and not r["bad_denominators"]
                for r in rows
            )
            else "refuted"
        ),
        "mutation_detected": all(r["mutation_corrupted_coefficient_differs"] for r in rows),
        "j_defined_over_q": all(b == 0 for p in qi_polys for _, b in p.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=[spec.slug for spec in fiber_inputs.SPECS])
    arguments = parser.parse_args()
    result = check(arguments.slug)
    (HERE / f"reduction-{arguments.slug}.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "variables"}, indent=1))


if __name__ == "__main__":
    main()
