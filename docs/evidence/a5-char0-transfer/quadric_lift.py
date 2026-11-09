"""Degree-2 fiber relations of an A_5 fiber pair over Q(i), compared with the retained K2 at each split prime.

Conjecture (check 2 of the characteristic-0 transfer): the space of quadrics q in k[y] with q(G) in J + m I^2, computed
over Q(i) by the computation the modular degree-2 receipts run (products of the G generators modulo std(J), normal
forms modulo std(J + m * products), constant syzygies of the coefficient matrix), has the dimension of the retained
K2 modulo p, and its reduced row echelon form reduces at the prime (i -> r) to the reduced row echelon form of the
retained relation file. Falsifier: a different dimension, a denominator divisible by p in the Q(i) echelon form, or a
reduced echelon form that differs from the modular one. Mutation: adding 1 to one non-pivot entry of the Q(i) echelon
form must break the equality.

Writes quadrics-<slug>.json beside this file. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/quadric_lift.py --slug xm-nm
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reduction_check  # noqa: E402

rees = reduction_check.rees
FIBERS = HERE.parent / "a5-exceptional-fibers" / "working" / "distribute" / "out"

# slug -> ((prime, root, relation directory under FIBERS), ...); each directory holds the K2 source k2_hilbert.py reads
SOURCES = {
    "xm-nm": ((32009, 10754, "a5-xm-d4/xm_p1/d2"), (32029, 9115, "a5-p2-small/xm_p2/d2")),
}

QUADRICS = (
    "option(redSB);def R0=basering;ideal sJ=std(ReducedJ);ideal GG=ReducedG;",
    "int n=ncols(GG);int i;int k;int f;int e;int b;int j;",
    "for(i=1;i<=n;i++){GG[i]=reduce(GG[i],sJ);}",
    "ring Y=0,(y(1..n)),dp;ideal kb=kbase(std(ideal(0)),2);int c=ncols(kb);",
    'for(i=1;i<=c;i++){"RESULT target_"+string(i),kb[i];}',
    "setring R0;ideal P;poly q;intvec ev;",
    "for(i=1;i<=c;i++){setring Y;ev=leadexp(kb[i]);setring R0;q=1;",
    "for(f=1;f<=n;f++){for(e=1;e<=ev[f];e++){q=reduce(q*GG[f],sJ);}}P[i]=q;}",
    # m is the ideal of the slice variables, as in the receipts; the producer ring still carries t3 and t8
    "ideal SliceM=@SLICE@;ideal Q=sJ;for(k=1;k<=ncols(SliceM);k++){for(i=1;i<=c;i++){Q=Q,SliceM[k]*P[i];}}",
    'ideal sQ=std(Q);"RESULT sq_size",size(sQ);ideal N=reduce(P,sQ);',
    "ideal mons;poly h;for(b=1;b<=c;b++){h=N[b];while(h!=0){mons=mons,leadmonom(h);h=h-lead(h);}}",
    'mons=simplify(mons,6);"RESULT monomials",size(mons);',
    "matrix M=coeffs(N,mons);module S=syz(module(M));",
    '"RESULT targets",c;"RESULT relations",size(S);string row;',
    "for(j=1;j<=size(S);j++){row=string(S[j][1]);",
    'for(b=2;b<=c;b++){row=row+";"+string(S[j][b]);}"RESULT rel_"+string(j),row;}',
)

Gauss = tuple[Fraction, Fraction]


def _g(text: str) -> Gauss:
    value = sympy.sympify(text.replace("^", "**"), locals={"I": sympy.I})
    return reduction_check._gaussian(sympy.nsimplify(value))


def _mul(a: Gauss, b: Gauss) -> Gauss:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def _inv(a: Gauss) -> Gauss:
    norm = a[0] * a[0] + a[1] * a[1]
    return a[0] / norm, -a[1] / norm


def _rref_qi(rows: list[list[Gauss]]) -> tuple[list[list[Gauss]], list[int]]:
    zero = (Fraction(0), Fraction(0))
    work = [list(r) for r in rows]
    pivots: list[int] = []
    rank = 0
    for col in range(len(work[0]) if work else 0):
        pivot = next((r for r in range(rank, len(work)) if work[r][col] != zero), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = _inv(work[rank][col])
        work[rank] = [_mul(x, inverse) for x in work[rank]]
        for r in range(len(work)):
            if r != rank and work[r][col] != zero:
                factor = work[r][col]
                work[r] = [
                    (x[0] - p[0], x[1] - p[1])
                    for x, p in zip(work[r], (_mul(factor, y) for y in work[rank]), strict=True)
                ]
        pivots.append(col)
        rank += 1
    return work[:rank], pivots


def _rref_fp(rows: list[list[int]], prime: int) -> list[list[int]]:
    work = [list(r) for r in rows]
    rank = 0
    for col in range(len(work[0]) if work else 0):
        pivot = next((r for r in range(rank, len(work)) if work[r][col] % prime), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, prime)
        work[rank] = [x * inverse % prime for x in work[rank]]
        for r in range(len(work)):
            if r != rank and work[r][col] % prime:
                factor = work[r][col]
                work[r] = [(x - factor * y) % prime for x, y in zip(work[r], work[rank], strict=True)]
        rank += 1
    return work[:rank]


def _reduce(rows: list[list[Gauss]], prime: int, root: int) -> tuple[list[list[int]], int]:
    bad = 0
    out = []
    for row in rows:
        reduced = []
        for a, b in row:
            if a.denominator % prime == 0 or b.denominator % prime == 0:
                bad += 1
                reduced.append(0)
                continue
            reduced.append(
                (a.numerator * pow(a.denominator, -1, prime) + b.numerator * pow(b.denominator, -1, prime) * root)
                % prime
            )
        out.append(reduced)
    return out, bad


def _monomial(text: str) -> tuple[int, ...]:
    factors: list[int] = []
    for index, power in re.findall(r"y\((\d+)\)(?:\^(\d+))?", text):
        factors.extend([int(index)] * int(power or 1))
    return tuple(sorted(factors))


def _modular_rows(path: Path, columns: dict[tuple[int, ...], int], prime: int) -> list[list[int]]:
    rows = []
    for relation in path.read_text(encoding="utf-8").replace("\n", "").split(","):
        if not relation.strip():
            continue
        row = [0] * len(columns)
        for term in re.split(r"(?=[+-])", relation.replace(" ", "")):
            if not term:
                continue
            match = re.match(r"^([+-]?)(\d*)\*?(.*)$", term)
            if match is None:
                raise SystemExit(f"unparsed term {term!r} in {path}")
            sign, number, monomial = match.groups()
            coefficient = int(number or 1) * (-1 if sign == "-" else 1)
            row[columns[_monomial(monomial)]] = (row[columns[_monomial(monomial)]] + coefficient) % prime
        rows.append(row)
    return rows


def check(slug: str, timeout: int = 4 * reduction_check.TIMEOUT_SECONDS) -> dict[str, Any]:
    body = reduction_check._script(slug, None, rees.MODULAR_PRIME)
    header = (reduction_check.HEADERS / f"p{SOURCES[slug][0][0]}-r{SOURCES[slug][0][1]}" / f"{slug}.sing").read_text()
    ring_line = header.splitlines()[0]
    slice_vars = ring_line[ring_line.index("(") + 1 : ring_line.index(")")]
    script = body.replace("\nquit;\n", "\n") + "\n".join(QUADRICS).replace("@SLICE@", slice_vars) + "\nquit;\n"
    outcome = rees._run_singular(script, "quadrics_qi", timeout)
    if outcome.status != "completed":
        raise SystemExit(f"{slug}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    count = int(res["targets"])
    targets = [_monomial(res[f"target_{i}"]) for i in range(1, count + 1)]
    columns = {monomial: index for index, monomial in enumerate(targets)}
    relations = [[_g(x) for x in res[f"rel_{j}"].split(";")] for j in range(1, int(res["relations"]) + 1)]
    echelon, pivots = _rref_qi(relations)
    rows = []
    for prime, root, directory in SOURCES[slug]:
        modular = _rref_fp(_modular_rows(FIBERS / directory / "relations-upto-d2.rel", columns, prime), prime)
        reduced, bad = _reduce(echelon, prime, root)
        mutated = [list(r) for r in echelon]
        free = next(c for c in range(count) if c not in pivots)
        a, b = mutated[0][free]
        mutated[0][free] = (a + 1, b)
        mutated_reduced, _ = _reduce(mutated, prime, root)
        rows.append(
            {
                "prime": prime,
                "root": root,
                "k2_source": f"working/distribute/out/{directory}/relations-upto-d2.rel",
                "modular_dimension": len(modular),
                "bad_denominators": bad,
                "echelon_equal": bad == 0 and reduced == modular,
                "mutation_detected": mutated_reduced != modular,
            }
        )
    return {
        "slug": slug,
        "conjecture": "the Q(i) degree-2 relation space {q : q(G) in J + m I^2} reduces onto K2 mod p",
        "targets": count,
        "qi_dimension": len(echelon),
        "qi_rank_h2": count - len(echelon),
        "qi_max_denominator": max((max(a.denominator, b.denominator) for r in echelon for a, b in r), default=1),
        "qi_has_imaginary_part": any(b != 0 for r in echelon for _, b in r),
        "sq_size": int(res["sq_size"]),
        "monomials": int(res["monomials"]),
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "peak_rss_kib": outcome.peak_rss_kib,
        "primes": rows,
        "verdict": "survives"
        if all(r["echelon_equal"] and r["modular_dimension"] == len(echelon) for r in rows)
        else "refuted",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=sorted(SOURCES))
    parser.add_argument(
        "--timeout", type=int, default=4 * reduction_check.TIMEOUT_SECONDS, help="seconds for the Singular call"
    )
    arguments = parser.parse_args()
    result = check(arguments.slug, arguments.timeout)
    (HERE / f"quadrics-{arguments.slug}.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
