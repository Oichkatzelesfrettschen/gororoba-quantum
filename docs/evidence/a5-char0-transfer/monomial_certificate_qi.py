"""The same-sign X slice over Q(i): I equals the monomial ideal M, and the fiber cone is cut out by 69 quadrics.

The modular certificate (`../a5-exceptional-fibers/monomial-ladder/monomial_certificate.py`) is repeated in
characteristic 0 with the G of the Q(i) producer (`reduction_check._script`). With P = Q(i)[[a, rho, sig, w]],
R = Q(i)[[t]] + (a, rho, sig) P, t = w^2 / (1 + w), M = w^2 (a, rho, sig) + w (rho, sig) (a, rho, sig)^2 and
q = (w^2, a, rho, sig) P, one Singular run over Q(i) checks

1. that the producer's J vanishes on the parametrization (modulo u (1 + w) = 1, u standing for 1 / (1 + w));
2. that H_j = (1 + w)^K G_j, a polynomial, reduces to zero modulo the monomial ideal M;
3. that the classes of G_j = (1 - K w) H_j in M / q M have rank dim M / q M = 15, so I = M by Nakayama's lemma;
4. the kernel L of Q(i)[y] -> P[M T] / q P[M T], y_j -> class of G_j, by elimination, with its saturation at the
   irrelevant ideal and the nilpotents y1, y5, y6.

A second run per prime reduces the generators of L at (p, i -> r) and compares the result with the retained K2.
Writes monomial-certificate-qi.json beside this file.

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/monomial_certificate_qi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent / "a5-exceptional-fibers"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EVIDENCE / "monomial-ladder"))

import reduction_check as rc  # noqa: E402
from monomial_model import GENS, MAX, add, divides  # noqa: E402

import parallel  # noqa: E402

NAMES = ("va", "vr", "vs", "vw")
SIGN = {"xm-nm": 1, "xp-np": -1}
# The parametrization of ../a5-exceptional-fibers/arcs-x-same, with vu = 1 / (1 + vw).
IMAGES = {
    "t1": "va+vw^2*vu/2",
    "t2": "va*vw*(vw+2)*vu/2",
    "t4": "((1+vw)*vr+vs)/2",
    "t5": "((1+vw)*vr-vs)/2",
    "t6": "((1+vw)*vs+vr)/2",
    "t7": "(vr-(1+vw)*vs)/2",
    "t9": "{sign}*(-vw^2*vu/2)",
}
# slug: prime: (root of -1, retained K2 under working/)
K2 = {
    "xm-nm": {
        32009: (10754, "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel"),
        32029: (9115, "distribute/out/a5-p2-small/xm_p2/d2/relations-upto-d2.rel"),
    },
    "xp-np": {32029: (9115, "distribute/out/a5-p2-small/xp_p2/d2/relations-upto-d2.rel")},
}


def mono(e: tuple[int, ...]) -> str:
    return "*".join(f"{n}^{k}" for n, k in zip(NAMES, e, strict=True) if k) or "1"


def basis() -> list[tuple[int, ...]]:
    q_m = [add(x, g) for x in MAX for g in GENS]
    w = (0, 0, 0, 1)
    return sorted({m for g in GENS for m in (g, add(g, w)) if not any(divides(h, m) for h in q_m)})


def script(slug: str, variables: list[str]) -> str:
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    images = ",".join(IMAGES.get(v, "0").format(sign=SIGN[slug]) for v in variables)
    base = basis()
    reps = []
    for m in base:
        direct = [i for i, g in enumerate(GENS) if m == g]
        lifted = [i for i, g in enumerate(GENS) if m == add(g, (0, 0, 0, 1))]
        reps.append(f"z({direct[0] + 1})" if direct else f"vw*z({lifted[0] + 1})")
    q_m = ",".join(mono(add(x, g)) for x in MAX for g in GENS)
    lines = (
        "def R0=basering;",
        'LIB "matrix.lib";',
        f"ring S=(0,I),({','.join(NAMES)},vu),dp;minpoly=I2+1;",
        f"map phi=R0,{images};",
        "ideal U=std(ideal(vu*(1+vw)-1));",
        '"RESULT j_nonzero",size(simplify(reduce(phi(ReducedJ),U),2));',
        "ideal Gp=phi(ReducedG); int n=ncols(Gp); int j; int k; int K=0; intvec uw=0,0,0,0,1;",
        "for(j=1;j<=n;j++){ if(deg(Gp[j],uw)>K){K=deg(Gp[j],uw);} }",
        "ideal H; matrix c; poly h;",
        "for(j=1;j<=n;j++){ c=coeffs(Gp[j],vu); h=0; for(k=1;k<=nrows(c);k++){ h=h+c[k,1]*(1+vw)^(K-k+1); } H[j]=h; }",
        f"ideal M=std(ideal({','.join(mono(g) for g in GENS)}));",
        f"ideal QM=std(ideal({q_m}));",
        '"RESULT generators",n; "RESULT denominator_power",K;',
        '"RESULT outside_m",size(simplify(reduce(H,M),2));',
        "ideal C; for(j=1;j<=n;j++){ C[j]=reduce((1-K*vw)*H[j],QM); }",
        f"ideal Bm={','.join(mono(m) for m in base)};",
        "proc cf(poly f, poly m){ poly g=f; while(g!=0){ if(leadmonom(g)==m){ return(leadcoef(g)); } g=g-lead(g); }"
        " return(0); }",
        f"matrix Cm[n][{len(base)}]; poly rest;",
        f"for(j=1;j<=n;j++){{ rest=C[j]; for(k=1;k<={len(base)};k++){{ Cm[j,k]=cf(C[j],Bm[k]);"
        ' rest=rest-Cm[j,k]*Bm[k]; } if(rest!=0){ "RESULT stray_class_term",j; } }',
        '"RESULT basis",ncols(Bm); "RESULT rank",rank(Cm);',
        f"ring B=(0,I),(T,{','.join(NAMES)},z(1..{len(GENS)}),y(1..n)),dp;minpoly=I2+1;",
        "matrix Cb=imap(S,Cm);",
        "ideal Z=" + ",".join(f"z({i + 1})-T*{mono(g)}" for i, g in enumerate(GENS)) + ";",
        f"ideal Rep={','.join(reps)};",
        "ideal Q=eliminate(Z,T),vw^2,va,vr,vs; poly im;",
        f"for(j=1;j<=n;j++){{ im=0; for(k=1;k<={len(base)};k++){{ im=im+Cb[j,k]*Rep[k]; }} Q=Q,y(j)-im; }}",
        f"ideal E=eliminate(Q,T*{'*'.join(NAMES)}*{'*'.join(f'z({i + 1})' for i in range(len(GENS)))});",
        "ring Y=(0,I),(y(1..n)),dp;minpoly=I2+1; option(redSB);",
        "ideal L=std(imap(B,E)); ideal Lm=minbase(L);",
        '"RESULT l_generators",size(Lm); "RESULT l_max_degree",deg(Lm[size(Lm)]); "RESULT l_min_degree",deg(Lm[1]);',
        '"RESULT l_dim",dim(L); "RESULT l_mult",mult(L); "RESULT l_hilbert",hilb(L,2);',
        'for(j=1;j<=size(Lm);j++){ "RESULT l_"+string(j),Lm[j]; }',
        'LIB "elim.lib";',
        '"RESULT l_saturated",size(simplify(reduce(sat_with_exp(L,maxideal(1))[1],L),2))==0;',
        "ideal N=y(1),y(5),y(6);",
        '"RESULT nilpotents_outside_l",size(simplify(reduce(N,L),2));',
        '"RESULT squares_in_l",size(simplify(reduce(N^2,L),2))==0;',
        "quit;",
    )
    return body + "\n".join(lines) + "\n"


def reduce_at(job: tuple[str, int, int, str, list[str], int]) -> dict[str, Any]:
    slug, prime, root, relations, generators, count = job
    path = EVIDENCE / "working" / relations
    text = "\n".join(
        (
            f"ring Y={prime},(y(1..{count})),dp; number I={root}; option(redSB);",
            f"ideal L={','.join(generators)};",
            f'execute("ideal K="+read("{path}")+";");',
            "ideal SL=std(L); ideal SK=std(K);",
            '"RESULT l_in_k2",size(simplify(reduce(L,SK),2))==0; "RESULT k2_in_l",size(simplify(reduce(K,SL),2))==0;',
            '"RESULT l_nonzero",size(simplify(L,2));',
            "quit;",
        )
    )
    outcome = rc.rees._run_singular(text + "\n", f"monomial_qi_{prime}", rc.TIMEOUT_SECONDS)
    rc._require(outcome.status == "completed", f"{slug} at {prime}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    return {
        "prime": prime,
        "root": root,
        "k2_source": f"working/{relations}",
        "nonzero_generators": int(res["l_nonzero"]),
        "l_in_k2": res["l_in_k2"] == "1",
        "k2_in_l": res["k2_in_l"] == "1",
    }


def certify(slug: str) -> dict[str, Any]:
    probe = rc.rees._run_singular(
        rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
        + '"RESULT vs",varstr(basering);\nquit;\n',
        "monomial_qi_vars",
        rc.TIMEOUT_SECONDS,
    )
    rc._require(probe.status == "completed", f"{slug} variable probe: {probe.status} {probe.diagnostic}")
    outcome = rc.rees._run_singular(script(slug, probe.results["vs"].split(",")), "monomial_qi", 8 * rc.TIMEOUT_SECONDS)
    rc._require(outcome.status == "completed", f"{slug}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    count = int(res["l_generators"])
    generators = [res[f"l_{i}"] for i in range(1, count + 1)]
    row: dict[str, Any] = {
        "slug": slug,
        "j_nonzero": int(res["j_nonzero"]),
        "generators": int(res["generators"]),
        "denominator_power": int(res["denominator_power"]),
        "terms_outside_m": int(res["outside_m"]),
        "stray_class_term": "stray_class_term" in res,
        "basis_of_m_mod_qm": int(res["basis"]),
        "rank_of_classes": int(res["rank"]),
        "l_generators": count,
        "l_degrees": [int(res["l_min_degree"]), int(res["l_max_degree"])],
        "l_dim": int(res["l_dim"]),
        "l_mult": int(res["l_mult"]),
        "l_hilbert_numerator": res["l_hilbert"],
        "l_has_imaginary_part": any("I" in g for g in generators),
        "l_saturated": res["l_saturated"] == "1",
        "y1_y5_y6_outside_l": int(res["nilpotents_outside_l"]),
        "y1_y5_y6_squared_in_l": res["squares_in_l"] == "1",
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "peak_rss_kib": outcome.peak_rss_kib,
    }
    row["i_equals_m"] = (
        row["j_nonzero"] == 0
        and row["terms_outside_m"] == 0
        and not row["stray_class_term"]
        and row["rank_of_classes"] == row["basis_of_m_mod_qm"] == row["generators"]
    )
    jobs = [(slug, prime, root, rel, generators, row["generators"]) for prime, (root, rel) in K2[slug].items()]
    row["reductions"] = parallel.ordered_map(reduce_at, jobs, min_items=2)
    row["verdict"] = (
        "certified"
        if row["i_equals_m"]
        and all(r["l_in_k2"] and r["k2_in_l"] and r["nonzero_generators"] == count for r in row["reductions"])
        else "failed"
    )
    return row


def main() -> None:
    rows = parallel.ordered_map(certify, list(SIGN), min_items=2)
    record = {"schema": "a5-monomial-certificate-qi-v1", "field": "Q(i)", "cases": rows}
    (HERE / "monomial-certificate-qi.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps({k: v for k, v in row.items()}))
    failed = [row["slug"] for row in rows if row["verdict"] != "certified"]
    if failed:
        raise SystemExit(f"certificate over Q(i) fails on {', '.join(failed)}")


if __name__ == "__main__":
    main()
