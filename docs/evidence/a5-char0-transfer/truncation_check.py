"""Good reduction of the truncated germ ideal J + m^N of an A_5 fiber pair at the closing order of a degree.

Conjecture (check 3 of the characteristic-0 transfer): the monic reduced standard basis of J + m^N over Q(i) (dp, the
producer's presolved slice ring, m the ideal of the slice variables) has every coefficient integral at the prime
(i -> r) of Z[i] over p, and its reduction equals the monic reduced standard basis of J + m^N computed from the retained
header at (p, r). The truncated rank r_N lives in k[t]/(J + m^N), so with this and check 2 a set of degree-d classes
independent modulo p stays independent over Q(i). Falsifier: a denominator divisible by p, or a reduced basis that
differs. Mutation: adding 1 to one coefficient of the Q(i) basis must break the equality.

Writes truncation-<slug>-n<N>.json beside this file. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/truncation_check.py --slug xm-nm --order 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reduction_check as rc  # noqa: E402

rees = rc.rees


def _extra(order: int, slice_vars: list[str]) -> str:
    # m is the ideal of the slice variables: the producer's ring still carries the presolve-eliminated variables
    return "\n".join(
        (
            f"option(redSB);option(redTail);ideal SliceM={','.join(slice_vars)};",
            f"ideal RJ=std(ReducedJ+SliceM^{order});",
            '"RESULT rj_count",size(RJ);',
            'for(int i=1;i<=size(RJ);i++){"RESULT rj_"+string(i),RJ[i];}',
        )
    )


def _basis(script: str, label: str) -> tuple[list[str], float]:
    outcome = rees._run_singular(script, label, rc.TIMEOUT_SECONDS)
    if outcome.status != "completed":
        raise SystemExit(f"{label}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    return [res[f"rj_{i}"] for i in range(1, int(res["rj_count"]) + 1)], round(outcome.wall_nanoseconds / 1e9, 1)


def check(slug: str, order: int) -> dict[str, Any]:
    body = rc._script(slug, None, rees.MODULAR_PRIME).replace("\nquit;\n", "\n")
    first_header = (rc.HEADERS / f"p{rc.PRIMES[0][0]}-r{rc.PRIMES[0][1]}" / f"{slug}.sing").read_text(encoding="utf-8")
    ring_line = first_header.splitlines()[0]
    slice_vars = ring_line[ring_line.index("(") + 1 : ring_line.index(")")].split(",")
    qi_text, qi_wall = _basis(body + _extra(order, slice_vars) + "\nquit;\n", "truncation_qi")
    rows = []
    names: list[str] = []
    qi_polys: list[rc.Coefficients] = []
    for prime, root in rc.PRIMES:
        header = (rc.HEADERS / f"p{prime}-r{root}" / f"{slug}.sing").read_text(encoding="utf-8").replace("quit;", "")
        hd_text, hd_wall = _basis(
            header + "\nideal ReducedJ=J;\n" + _extra(order, slice_vars) + "\nquit;\n", f"truncation_{prime}"
        )
        if not names:
            names = rc.fiber_inputs._variables(qi_text)
            qi_polys = [rc._poly_qi(text, names) for text in qi_text]
        same_vars = rc.fiber_inputs._variables(hd_text) == names
        reduced, bad = rc._image(qi_polys, prime, root, monic=True)
        modular = sorted(sorted(rc._monic(rc._poly_fp(t, names, prime), prime).items()) for t in hd_text)
        corrupted = [dict(poly) for poly in qi_polys]
        target = next(i for i, poly in enumerate(corrupted) if len(poly) > 1)
        first = next(iter(corrupted[target]))
        a, b = corrupted[target][first]
        corrupted[target][first] = (a + 1, b)
        mutated, _ = rc._image(corrupted, prime, root, monic=True)
        rows.append(
            {
                "prime": prime,
                "root": root,
                "same_variables": same_vars,
                "bad_denominators": bad,
                "header_basis_size": len(hd_text),
                "bases_equal": same_vars and not bad and sorted(reduced) == modular,
                "mutation_detected": sorted(mutated) != modular,
                "header_wall_seconds": hd_wall,
            }
        )
    return {
        "slug": slug,
        "order": order,
        "conjecture": "good reduction of J + m^N at each split prime",
        "qi_basis_size": len(qi_text),
        "qi_terms": sum(len(p) for p in qi_polys),
        "qi_max_denominator": max(
            (max(a.denominator, b.denominator) for p in qi_polys for a, b in p.values()), default=1
        ),
        "qi_has_imaginary_part": any(b != 0 for p in qi_polys for _, b in p.values()),
        "qi_wall_seconds": qi_wall,
        "primes": rows,
        "verdict": "survives" if all(r["bases_equal"] for r in rows) else "refuted",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=[spec.slug for spec in rc.fiber_inputs.SPECS])
    parser.add_argument("--order", required=True, type=int)
    arguments = parser.parse_args()
    result = check(arguments.slug, arguments.order)
    out = HERE / f"truncation-{arguments.slug}-n{arguments.order}.json"
    out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
