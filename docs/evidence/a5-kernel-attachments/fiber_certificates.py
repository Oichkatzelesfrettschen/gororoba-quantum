"""Completion certificates for a fiber-cone relation ideal K; each status stands alone and none implies another.

``candidate-ideal`` (status ``scheme-equal``): K is lifted to L = H + (lifts) in k[t,y], H = J + (g y_j - G_j y_q) for a
pivot G_q = g that is a nonzerodivisor modulo J. The script checks H in L, L in ker(y_j -> a G_j) by substitution,
and L : g = L. Every element f of the Rees ideal ker(phi) satisfies g^N f in H (g y_j = G_j y_q
modulo H and phi(f) = 0),
so ker(phi) is contained in H : g^inf; and H : g^inf is contained in L because g^N f in H in L with L : g = L gives f
in L. With L in ker(phi) this gives L = ker(phi) = H : g^inf, and the special fiber is k[y]/(L restricted to t = 0),
which the script compares with (K).

``dense-family`` (status ``support lower bound`` or ``refuted``): exact containment of supplied genuine limit points
in the components of V(K). Finitely many points bound the limit support from below; ``support-equal`` needs a
verified dimension of the sampled locus in each component, which no function here computes. The random arc sampler
is not implemented: a sampler needs seeds from a QRNG draw registered in the seed ledger, and no draw is allocated
to this tool. Points arrive as a file.

``bounded Hilbert function`` is a scope cut: the tree holds no proven bound on the degrees of the relations of F(I).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import fiber_cone_driver as drv

SCHEMA = "a5-fiber-certificate-v1"


def _lifts_block(i: int, ring: str, degree: int, ntargets: int, nrel: int, coeffs: str, previous: str) -> str:
    """Lift each degree-d relation to a polynomial of k[t,y] that maps into J under y_j -> G_j."""
    prev = f'execute("ideal K{i}="+read("{previous}")+";");' if previous else f"ideal K{i}=0;"
    return f"""
setring Y; {prev} ideal sK{i}=std(K{i}); ideal kb{i}=kbase(sK{i},{degree}); int nT{i}=ncols(kb{i});
if(nT{i}!={ntargets}){{ "RESULT lift_error target_count",nT{i}; quit; }}
setring {ring}; ideal P{i};
for(ii=1;ii<=nT{i};ii++){{ setring Y; ev=leadexp(kb{i}[ii]); setring {ring}; q=1;
  for(f=1;f<=n;f++){{ for(e=1;e<=ev[f];e++){{ q=reduce(q*G[f],sJ); }} }} P{i}[ii]=q; }}
ideal Mid{i}=sJ; for(k=1;k<=nt;k++){{ for(ii=1;ii<=nT{i};ii++){{ Mid{i}=Mid{i},var(k)*P{i}[ii]; }} }}
if(ncols(Mid{i})!=size(sJ)+nt*nT{i}){{ "RESULT lift_error zero_product"; quit; }}
ideal sMid{i}=std(Mid{i});
intmat C{i}[{nrel}][{ntargets}]={coeffs};
setring R; ideal kbR{i}=imap(Y,kb{i}); setring {ring};
ideal FR; for(r1=1;r1<={nrel};r1++){{
  fr=0; for(b=1;b<=nT{i};b++){{ fr=fr+C{i}[r1,b]*P{i}[b]; }}
  if(reduce(fr,sMid{i})!=0){{ "RESULT lift_error not_in_J_plus_mP"; quit; }}
  FR[r1]=fr; }}
T=lift(Mid{i},FR);
setring R; TR=imap({ring},T); setring {ring};
for(r1=1;r1<={nrel};r1++){{
  setring R; lf=0;
  for(kk=1;kk<=nt;kk++){{ for(b=1;b<=nT{i};b++){{
    lf=lf+TR[jl+(kk-1)*nT{i}+b,r1]*var(kk)*kbR{i}[b]; }} }}
  setring Y; rel=0; for(b=1;b<=nT{i};b++){{ rel=rel+C{i}[r1,b]*kb{i}[b]; }}
  setring R; Lifts=Lifts,imap(Y,rel)-lf; setring {ring};
}}
"RESULT lifted_degree",{degree},{nrel};
"""


def candidate_ideal(header_path: Path, manifest: list[dict[str, Any]], prime: int, out: Path, memory_gib: int = 3,
                    timeout: int = 900) -> dict[str, Any]:  # fmt: skip
    """Run the candidate-ideal certificate. Each manifest entry names a degree, the relations of all lower degrees
    ('previous_relations', or null for degrees 1 and 2), the degree's relation file and its target-monomial file
    (the driver writes both)."""
    header = drv.read_header(header_path, prime)
    ring = header.ring
    out.mkdir(parents=True, exist_ok=True)
    blocks: list[str] = []
    kall: list[str] = []
    for index, spec in enumerate(sorted(manifest, key=lambda s: int(s["degree"])), start=1):
        degree = int(spec["degree"])
        prev = spec.get("previous_relations")
        prev_name = ""
        if degree >= 3 and prev:
            prev_name = f"cert-previous-{index}.rel"
            (out / prev_name).write_text(Path(prev).read_text().strip() or "0")
        keys = [next(iter(drv.parse_poly(t, prime))) for t in drv.split_ideal(Path(spec["targets"]).read_text())]
        rels = [drv.parse_poly(r, prime) for r in drv.split_ideal(Path(spec["relations"]).read_text())]
        if not rels:
            continue
        position = {k: j for j, k in enumerate(keys)}
        flat: list[int] = []
        for rel in rels:
            drv._require(set(rel) <= set(position), "relation uses a monomial outside the target list")
            row = [0] * len(keys)
            for key, value in rel.items():
                row[position[key]] = value
            flat.extend(row)
        kall.append(Path(spec["relations"]).read_text().strip())
        blocks.append(_lifts_block(index, ring, degree, len(keys), len(rels), ",".join(map(str, flat)), prev_name))
    drv._require(bool(blocks), "no relations to certify")
    (out / "cert-k.rel").write_text(",\n".join(kall))
    script = (
        header.text
        + f"""option(redSB); system("--ticks-per-sec",1000); int tm0=rtimer;
ideal sJ=std(J); int n=ncols(G); int nt=nvars({ring}); int i; int k; int f; int e; int ii; int r1; int b; int kk;
for(i=1;i<=n;i++){{G[i]=reduce(G[i],sJ);}}
int qv=1; int best=-1;
for(i=1;i<=n;i++){{
  if(size(reduce(quotient(sJ,ideal(G[i])),sJ))==0){{
    if(best<0 or size(G[i])<size(G[qv])){{qv=i;best=1;}} }} }}
if(best<0){{ "RESULT no_nonzerodivisor_pivot"; quit; }}
"RESULT pivot",qv,"terms",size(G[qv]);
string sv=varstr({ring}); int jl=size(sJ); intvec ev; poly q; poly fr; matrix T;
ring Y={prime},(y(1..n)),dp;
execute("ring R={prime},("+sv+",y(1..n)),dp;");
ideal Lifts; poly lf; matrix TR;
setring Y; poly rel; setring R;
setring {ring};
"""
        + "".join(blocks)
        + f"""
"RESULT lifts_ms",rtimer-tm0; int tm1=rtimer;
setring R;
ideal Jr=imap({ring},sJ); ideal Gr=imap({ring},G); poly g=Gr[qv];
ideal H=Jr; for(i=1;i<=n;i++){{ if(i!=qv){{ H=H,g*y(i)-Gr[i]*y(qv); }} }}
ideal L=H,Lifts; ideal sL=std(L); "RESULT std_L_ms",rtimer-tm1,"size",size(sL);
"RESULT H_in_L",size(reduce(H,sL))==0;
int tm2=rtimer;
"RESULT L_colon_g_equals_L",size(reduce(quotient(sL,ideal(g)),sL))==0; "RESULT colon_ms",rtimer-tm2;
int tm3=rtimer;
execute("ring S={prime},("+sv+",a),dp;");
ideal Js=std(imap({ring},sJ)); ideal Gs=imap({ring},G);
ideal im; for(i=1;i<=nt;i++){{ im[i]=var(i); }} for(i=1;i<=n;i++){{ im[nt+i]=a*Gs[i]; }}
map phi=R,im; ideal Ls=phi(L);
"RESULT L_in_kernel_failures",size(reduce(Ls,Js)); "RESULT subst_ms",rtimer-tm3;
setring Y;
ideal Kall; execute("Kall="+read("cert-k.rel")+";"); ideal sKall=std(Kall);
setring Y; ideal imy; for(i=1;i<=nt;i++){{ imy[i]=0; }} for(i=1;i<=n;i++){{ imy[nt+i]=y(i); }}
map toY=R,imy; ideal F=std(toY(imap(R,L)));
"RESULT fiber_in_K",size(reduce(F,sKall))==0; "RESULT K_in_fiber",size(reduce(Kall,F))==0;
"RESULT total_ms",rtimer-tm0; quit;
"""
    )
    outcome = drv.run_singular(script, "candidate-ideal", out, memory_gib, timeout)
    r = outcome.results
    checks = {
        "pivot": r.get("pivot"),
        "H_in_L": r.get("H_in_L") == "1",
        "L_in_kernel": r.get("L_in_kernel_failures") == "0",
        "L_colon_g_equals_L": r.get("L_colon_g_equals_L") == "1",
        "fiber_equals_K": r.get("fiber_in_K") == "1" and r.get("K_in_fiber") == "1",
    }
    ok = outcome.error is None and all(v for k, v in checks.items() if k != "pivot")
    receipt = {
        "schema": SCHEMA,
        "certificate": "candidate-ideal",
        "status": "scheme-equal" if ok else "candidate-not-verified",
        "checks": checks,
        "singular_error": outcome.error,
        "singular_results": r,
        "wall_seconds": round(outcome.seconds, 3),
        "peak_bytes": outcome.peak_bytes,
        "memory_cap_gib": memory_gib,
        "input_sha256": drv.sha256_file(header_path),
        "input": drv.rel_path(header_path),
        "relations_sha256": drv.hashlib.sha256((out / "cert-k.rel").read_bytes()).hexdigest(),
        "prime": prime,
        "tool_versions": drv.tool_versions(),
    }
    (out / "certificate-candidate-ideal.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def dense_family(points: list[list[int]], components: list[dict[str, Any]], prime: int) -> dict[str, Any]:
    """Exact containment of supplied limit points in V(K).

    components: [{"name", "dimension", "generators": [polynomial text in y(i)]}]. A point lies in a component when
    every generator vanishes at it modulo the prime. Containment of finitely many points bounds the limit support from
    below only, so the verdict is ``support lower bound``; ``support-equal`` needs a verified dimension of the sampled
    locus in every component, which this function does not compute. A point outside every component refutes the
    input (status ``refuted``)."""
    parsed = [[drv.parse_poly(g, prime) for g in comp["generators"]] for comp in components]

    def vanishes(polys: list[dict[drv.Monomial, int]], point: list[int]) -> bool:
        for poly in polys:
            total = 0
            for key, coef in poly.items():
                term = coef
                for name, exp in key:
                    term = term * pow(point[int(name[2:-1]) - 1], exp, prime) % prime
                total = (total + term) % prime
            if total:
                return False
        return True

    counts = [0] * len(components)
    outside = 0
    for point in points:
        hits = [vanishes(polys, point) for polys in parsed]
        for j, hit in enumerate(hits):
            counts[j] += hit
        outside += not any(hits)
    status = "refuted" if outside else "support lower bound"
    return {
        "schema": SCHEMA,
        "certificate": "dense-family",
        "status": status,
        "points": len(points),
        "points_outside_V_K": outside,
        "points_per_component": {c["name"]: counts[j] for j, c in enumerate(components)},
        "prime": prime,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidate-ideal")
    c.add_argument("--header", type=Path, required=True)
    c.add_argument(
        "--manifest", type=Path, required=True, help="JSON list of {degree, previous_relations, relations, targets}"
    )
    c.add_argument("--prime", type=int, required=True)
    c.add_argument("--out", type=Path, required=True)
    c.add_argument("--memory-gib", type=int, default=3)
    c.add_argument("--timeout", type=int, default=900)
    d = sub.add_parser("dense-family")
    d.add_argument("--points", type=Path, required=True, help="JSON list of integer vectors")
    d.add_argument("--components", type=Path, required=True)
    d.add_argument("--prime", type=int, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "candidate-ideal":
        result = candidate_ideal(args.header, json.loads(args.manifest.read_text()), args.prime, args.out,
                                 args.memory_gib, args.timeout)  # fmt: skip
    else:
        result = dense_family(json.loads(args.points.read_text()), json.loads(args.components.read_text()), args.prime)
    print(json.dumps({k: result[k] for k in ("certificate", "status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
