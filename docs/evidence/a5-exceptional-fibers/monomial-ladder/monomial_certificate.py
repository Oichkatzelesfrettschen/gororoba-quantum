"""Certificate that the ideal of the same-sign X slice is the monomial ideal M, and the fiber cone it presents.

P = k[[a, rho, sig, w]], R = k[[t]] + (a, rho, sig) P with t = w^2 / (1 + w), I = (G_1, ..., G_15) R, and
M = w^2 (a, rho, sig) + w (rho, sig) (a, rho, sig)^2, an ideal of P. Since P = R + w R, M is a finite R-module, and
m_R M = (t, a, rho, sig) M = q M with q = (w^2, a, rho, sig) P.

1. G_j lies in M. The header's G_j on the parametrization is a polynomial in a, rho, sig, w and u = 1 / (1 + w);
   H_j = (1 + w)^K G_j is a polynomial, 1 + w is a unit of P, and H_j lies in the monomial ideal M exactly when each
   of its monomials does.
2. I + q M = M. The monomials of M outside q M are among g and w g for the minimal generators g of M, so M / q M
   has a finite monomial basis; G_j = (1 + w)^(-K) H_j acts through P / q = k[w] / (w^2), so its class is that of
   (1 - K w) H_j. The classes of G_1, ..., G_15 span M / q M exactly when their matrix has rank dim M / q M.
3. Nakayama's lemma over the local ring R then gives I = M, hence I^d = M^d, m_R I^d = q M^d and
   F(I) = k + sum_(d >= 1) M^d / q M^d, the subalgebra generated in degree 1 of P[M T] / q P[M T].

The script checks 1 and 2 exactly over F_p and writes a Singular script that computes the kernel L of
k[y_1, ..., y_15] -> P[M T] / q P[M T], y_j -> class of G_j, by elimination, and compares L with the retained
quadrics K2.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/monomial_certificate.py --slug xm-nm --prime 32009 \
        --relations PATH/relations-upto-d2.rel --out records/monomial-certificate-xm-nm-p32009.json \
        --singular records/monomial-certificate-xm-nm-p32009.sing
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy
import x_same_ladder as ladder
from flint import Ordering, nmod_mat, nmod_mpoly_ctx
from monomial_model import GENS, MAX, add, divides

Mono = tuple[int, ...]


def exact_generators(slug: str, prime: int) -> tuple[list[dict[Mono, int]], int]:
    """H_j = (1 + w)^K G_j as polynomials in (a, rho, sig, w), and K."""
    ctx = nmod_mpoly_ctx.get(("a", "rho", "sig", "w", "u"), ordering=Ordering.degrevlex, modulus=prime)
    a, rho, sig, w, u = ctx.gens()
    half = pow(2, -1, prime)
    m = 1 + w
    t9 = -(w * w) * u * half
    values = {
        "t1": a - t9,
        "t2": a * w * (w + 2) * u * half,
        "t4": (m * rho + sig) * half,
        "t5": (m * rho - sig) * half,
        "t6": (m * sig + rho) * half,
        "t7": (rho - m * sig) * half,
        "t9": t9 * ladder.SIGN[slug],
    }
    variables, _, ideal_g = ladder.limits.header(slug, prime)
    symbols = sympy.symbols(variables)
    raw = []
    for text in ideal_g:
        polynomial = sympy.Poly(sympy.parse_expr(text.replace("^", "**")), *symbols)
        total = ctx.from_dict({})
        for exponents, coefficient in polynomial.terms():
            term = ctx.from_dict({(0,) * 5: int(coefficient.p) * pow(int(coefficient.q), -1, prime) % prime})
            for name, exponent in zip(variables, exponents, strict=True):
                term = term * values[name] ** int(exponent)
            total = total + term
        raw.append(ladder.plain(total))
    top = max((e[4] for g in raw for e in g), default=0)
    ctx4 = nmod_mpoly_ctx.get(ladder.NAMES, ordering=Ordering.degrevlex, modulus=prime)
    one_plus_w = ctx4.from_dict({(0, 0, 0, 0): 1, (0, 0, 0, 1): 1})
    out = []
    for g in raw:
        total = ctx4.from_dict({})
        for e, c in g.items():
            total = total + ctx4.from_dict({e[:4]: c}) * one_plus_w ** (top - e[4])
        out.append(ladder.plain(total))
    return out, top


def in_ideal(generators: list[Mono], monomial: Mono) -> bool:
    return any(divides(g, monomial) for g in generators)


def certificate(slug: str, prime: int) -> dict[str, Any]:
    q_m = [add(x, g) for x in MAX for g in GENS]
    w = (0, 0, 0, 1)
    basis = sorted({m for g in GENS for m in (g, add(g, w)) if not in_ideal(q_m, m)})
    # Every monomial of M is g times a monomial v; v = 1 or v = w, or v is divisible by a, rho, sig or w^2.
    h, top = exact_generators(slug, prime)
    outside = sum(1 for g in h for e in g if not in_ideal(GENS, e))
    rows = []
    for g in h:
        row = [0] * len(basis)
        for e, c in g.items():
            for shifted, factor in ((e, 1), (add(e, w), -top)):
                if in_ideal(GENS, shifted) and not in_ideal(q_m, shifted):
                    k = basis.index(shifted)
                    row[k] = (row[k] + factor * c) % prime
        rows.append(row)
    rank = int(nmod_mat(rows, prime).rank())
    return {
        "schema": "a5-monomial-certificate-v1",
        "slug": slug,
        "prime": prime,
        "generators": len(h),
        "denominator_power": top,
        "terms_of_H": sum(len(g) for g in h),
        "terms_of_H_outside_M": outside,
        "basis_of_M_mod_qM": [list(m) for m in basis],
        "classes_of_G": rows,
        "rank_of_classes": rank,
        "I_equals_M": outside == 0 and rank == len(basis) == len(h),
    }


def singular_script(record: dict[str, Any], relations: str) -> str:
    prime, basis, rows = record["prime"], record["basis_of_M_mod_qM"], record["classes_of_G"]
    names = ("a", "r", "s", "w")

    def mono(e: list[int] | Mono) -> str:
        return "*".join(f"{n}^{k}" for n, k in zip(names, e, strict=True) if k) or "1"

    reps = []
    for m in basis:
        direct = [i for i, g in enumerate(GENS) if tuple(m) == g]
        lifted = [i for i, g in enumerate(GENS) if tuple(m) == add(g, (0, 0, 0, 1))]
        reps.append(f"z({direct[0] + 1})" if direct else f"w*z({lifted[0] + 1})")
    images = ["+".join(f"{c}*{reps[k]}" for k, c in enumerate(row) if c) for row in rows]
    lines = [
        f"// Kernel L of k[y] -> P[M T] / q P[M T] for the same-sign X slice {record['slug']}, p = {prime}.",
        "option(redSB);",
        f"ring B={prime},(T,a,r,s,w,z(1..{len(GENS)}),y(1..{len(rows)})),dp;",
        "ideal Z=" + ",".join(f"z({i + 1})-T*{mono(g)}" for i, g in enumerate(GENS)) + ";",
        "ideal J=eliminate(Z,T);",
        "ideal Q=J,w^2,a,r,s," + ",".join(f"y({j + 1})-({image})" for j, image in enumerate(images)) + ";",
        f"ideal E=eliminate(Q,T*a*r*s*w*{'*'.join(f'z({i + 1})' for i in range(len(GENS)))});",
        f"ring Y={prime},(y(1..{len(rows)})),dp;",
        "ideal L=std(imap(B,E));",
        f'execute("ideal K="+read("{relations}")+";");',
        "ideal S=std(K);",
        '"RESULT L generators", size(minbase(L)), "maximal degree", deg(minbase(L)[size(minbase(L))]), '
        '"dim", dim(L), "mult", mult(L);',
        "int i; intvec D; for(i=1;i<=size(minbase(L));i++){ D[i]=deg(minbase(L)[i]); }",
        '"RESULT degrees of the minimal generators of L", string(D);',
        '"RESULT K2 inside L", size(simplify(reduce(K,L),2))==0, "L inside K2", size(simplify(reduce(L,S),2))==0;',
        '"RESULT hilbert numerator of L", hilb(L,2);',
        '"RESULT hilbert numerator of K2", hilb(S,2);',
        "quit;",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--slug", choices=tuple(ladder.SIGN), default="xm-nm")
    parser.add_argument("--prime", type=int, choices=tuple(ladder.limits.PRIMES), default=32009)
    parser.add_argument("--relations", required=True, help="path of the retained degree-2 relations, as Singular reads")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--singular", type=Path, required=True)
    args = parser.parse_args()
    record = certificate(args.slug, args.prime)
    script = singular_script(record, args.relations)
    args.singular.write_text(script, encoding="utf-8")
    record["singular_sha256"] = hashlib.sha256(script.encode()).hexdigest()
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k not in ("classes_of_G", "basis_of_M_mod_qM")}))
    if not record["I_equals_M"]:
        raise SystemExit(f"{args.slug} p={args.prime}: the certificate fails")


if __name__ == "__main__":
    main()
