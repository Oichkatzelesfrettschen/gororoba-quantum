"""Three generic arcs on the E8-bar header slices: the relation ideal of the fiber cone equals K2 in every degree.

On the header slice of E8-bar -> N- or N+ at p = 32009 or 32029 (a target of `arc_targets.py`) let O be the local
ring of the slice germ, m its maximal ideal, I = (G_1, ..., G_21), L the relation ideal of the fiber cone (a form F
of degree d lies in L when F(G) lies in m I^d) and K2 the ideal of the 148 retained quadrics. A monomial family of
`gen_family.py` is a generic arc: Phi of README.md with w = W s^a, rho, sigma at s^b, s^c, zeta = Z s^d and e
constant or e = e0 + E1 s^j defines a ring map from O to k(W, R, S, Z, E)[[s]], since Phi(0, 0, 0, e, 0) is the origin
and the denominators m, m^2 + 1 and e are units there. The s-adic valuation v is additive on products and at least
the minimum on sums. With nu = min v(G_a) and e_min = min v(t_i) >= 1, every element of m I^d has valuation at least
d nu + e_min, so a form F of L vanishes on the limit vector V (the coefficient of s^nu): L lies in the prime
Q = ker(y -> V). Q equals a prime P of K2 when every generator of P vanishes on V and the Jacobian matrix of V in the
five parameters has rank dim P at one point: r forms with independent differentials are algebraically independent
over the perfect field F_p (a relation of least degree would have all partial derivatives in the relation ideal,
hence zero, hence be a p-th power of a relation of lower degree), so dim S/Q >= dim S/P, and P inside Q forces Q = P.

Three families per target:

- `scroll`: the P2 family of README.md (nu = 2): Q = P2, the minimal prime of dimension 4 and degree 4;
- `top`: the P1 family of README.md (nu = 5): Q = P1, the minimal prime of dimension 5 and degree 11;
- `embedded`: w = W s, rho = R s^2, sigma = S s^2, zeta = Z s^2, e = -1 + E1 s (nu = 4, e_min = 2), the
  (1, 2, 2, 2, near, 1) family of the arc-jet runs: Q = A = K2 : rad(K2), the embedded prime of dimension 4 and
  degree 2, and every one of the five nilpotent linear forms l of rad(K2) has v(l(G)) = nu + 1 < nu + e_min.

The embedded run also computes in the ring of K2: the radical R, its linear forms N, A = K2 : R, and the primary
decomposition of K2 by primdecGTZ, with each associated prime compared with P1, P2 and A.

Deduction recorded in the ledger (as in A5-457 on the weight slice): L lies in P1 and P2, so in R, and L / K2 is a
submodule of R / K2. Every associated prime of R / K2 is an associated prime of K2 that contains Ann(R / K2) = A, and
of P1, P2 and A only A does, so R / K2 is torsion free over the domain S / A, of rank one by the Hilbert identity of
A5-547. For a nilpotent form l, the class of l in R / K2 is nonzero (K2 is generated in degree 2); a nonzero class
of L / K2 and the class of l are dependent over S / A with both coefficients nonzero, which gives c outside A with
c l in L; then v(c(G)) > deg(c) nu, so c vanishes on V of the embedded family and lies in A. Hence L = K2, given K2
inside L (the degree-2 receipts).

Every run also evaluates the 16 generators of J on its arc modulo s^(n+1) (`JNONVAN`, zero; every loop over an
ideal runs to `ncols`, since Singular's `size` counts only the nonzero generators), and the embedded run
checks that the primary components intersect to K2 and that the first Hilbert numerators satisfy
N_K2 - N_R = N_A - (1 - t)^21 with the numerators of A5-547 (rank one of R / K2 over S / A). Two controls run on the
scroll family: the embedded prime A must leave a residue on its limits, and the arc with t9 + s^2 must leave a residue
in J.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/arcs/relation_ideal_orders.py OUT.json
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "structure"))
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import gen_family as gf  # noqa: E402
import quadric_and_germ_probes as qp  # noqa: E402
from arc_targets import TARGETS, load_primes  # noqa: E402

import parallel  # noqa: E402

TIMEOUT_SECONDS = 1800
EMBEDDED = gf.Family("embedded_e-1_j1_a1_b2_c2_d2_n7", 1, 2, 2, 2, 7, ("near", -1, 1), "rs")
FAMILIES = {"scroll": gf.P2_FAMILY, "top": gf.P1_FAMILY, "embedded": EMBEDDED}
NGEN = 21

# Appended to the family script after its rank line; the script is then in the parameter ring Q with the limit
# vector F, the coefficient matrix Cf, the order nu, the map g1 from the ring Y of K2 and the truncation ideal rel.
STRUCTURE = (
    """LIB "primdec.lib";
setring Y;
ideal sK=std(K2); ideal Rd=std(radical(sK)); ideal N=simplify(jet(Rd,1),2);
ideal A=std(quotient(sK,Rd)); ideal sP1=std(P1); ideal sP2=std(P2);
proc same(ideal X, ideal Y0){ return(size(reduce(X,std(Y0)))==0 && size(reduce(Y0,std(X)))==0); }
"ANNIHILATOR", dim(A), mult(A), size(N), same(Rd, intersect(P1,P2));
"NUMK", hilb(sK,1); "NUMR", hilb(Rd,1); "NUMA", hilb(A,1);
list PD=primdecGTZ(K2); int pk; ideal pp; ideal pq;
ideal Icap=1;
for (pk=1;pk<=size(PD);pk++) { pq=std(PD[pk][1]); pp=std(PD[pk][2]); Icap=intersect(Icap,PD[pk][1]);
  "PRIMARY", dim(pp), mult(pp), mult(pq), same(pp,sP1), same(pp,sP2), same(pp,A); }
"DECOMPOSITION", same(Icap,sK);
int nN=size(N); list NS; int qq; for (qq=1;qq<=nN;qq++) { NS[qq]=string(N[qq]); }
setring Q;
ideal AF=g1(A); for (jj=1;jj<=ncols(AF);jj++) { AF[jj]=reduce(AF[jj],rel); } "ANONVAN", size(AF);
matrix Fn[1][21]; for (j=1;j<=21;j++) { Fn[1,j]=Cf[nu+2,j]; }
map gn=Y,"""
    + ",".join(f"Fn[1,{i}]" for i in range(1, NGEN + 1))
    + """;
ideal NL=g1(N); ideal NN=gn(N);
for (jj=1;jj<=nN;jj++) { "NILPOTENT", NS[jj], reduce(NL[jj],rel)==0, reduce(NN[jj],rel)!=0; }
poly TT; int em=100; matrix ct; int oo; list TL=T1,T2,T3,T4,T5,T6,T7,T8,T9;
for (jj=1;jj<=9;jj++) { TT=TL[jj];
  if (TT!=0) { ct=coeffs(TT,s); oo=1; while (ct[oo,1]==0) { oo++; } if (oo-1<em) { em=oo-1; } } }
"EMIN", em;
quit;
"""
)
JCHECK = """ideal JX=f(J); for (jj=1;jj<=ncols(JX);jj++) { JX[jj]=reduce(JX[jj],rel); }
"JNONVAN", size(simplify(JX,2));
"""
CONTROL = """LIB "primdec.lib";
setring Y;
ideal A=std(quotient(std(K2),std(radical(std(K2)))));
setring Q;
ideal AF=g1(A); for (jj=1;jj<=ncols(AF);jj++) { AF[jj]=reduce(AF[jj],rel); } "ANONVAN", size(AF);
poly T9c=T9+s^2; map fc=r,T1,T2,T3,T4,T5,T6,T7,T8,T9c;
ideal JC=fc(J); for (jj=1;jj<=ncols(JC);jj++) { JC[jj]=reduce(JC[jj],rel); } "JCORRUPT", size(JC);
quit;
"""


def script(target_name: str, family: str, tail: str) -> str:
    target = TARGETS[target_name]
    p1, p2, k2 = load_primes(target)
    text = gf.make_script(target, FAMILIES[family], p1, p2, k2)
    return text[: text.rindex("quit;")] + tail


def run(job: tuple[str, str, str, Path]) -> dict[str, Any]:
    target_name, family, mode, logs = job
    tail = JCHECK + {"structure": STRUCTURE, "control": CONTROL, "plain": "quit;\n"}[mode]
    out = logs / target_name
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{family}-{mode}.sing"
    path.write_text(script(target_name, family, tail), encoding="utf-8")
    text = gf.run_singular(path, TIMEOUT_SECONDS)
    path.with_suffix(".log").write_text(text, encoding="utf-8")
    if any(line.lstrip().startswith("?") for line in text.splitlines()):
        raise RuntimeError(f"{target_name} {family} {mode}: Singular error")
    row: dict[str, Any] = {"target": target_name, "family": family, "mode": mode, **(gf.parse(text) or {})}
    # The digest puts the log under the record comparison of a replay, which writes its logs beside its own output.
    row["log_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    row.pop("nonzero", None)
    for key in ("ANONVAN", "EMIN", "JNONVAN", "JCORRUPT"):
        m = re.search(key + r" (\d+)", text)
        if m:
            row[key] = int(m.group(1))
    m = re.search(r"ANNIHILATOR (\d+) (\d+) (\d+) (\d+)", text)
    if m:
        row["annihilator"] = [int(m.group(i)) for i in (1, 2)]
        row["nilpotent_count"] = int(m.group(3))
        row["radical_is_P1_meet_P2"] = m.group(4) == "1"
    for key, field in (("NUMK", "numK"), ("NUMR", "numR"), ("NUMA", "numA")):
        m = re.search(key + r" ([-0-9,]+)", text)
        if m:
            row[field] = [int(x) for x in m.group(1).split(",")][:-1]
    m = re.search(r"DECOMPOSITION (\d)", text)
    if m:
        row["decomposition_complete"] = m.group(1) == "1"
    row["primary"] = [[int(x) for x in g] for g in re.findall(r"PRIMARY (\d+) (\d+) (\d+) (\d) (\d) (\d)", text)]
    row["nilpotent"] = [
        {"form": f, "vanishes_on_limit": a == "1", "next_coefficient_nonzero": b == "1"}
        for f, a, b in re.findall(r"NILPOTENT (\S+) (\d) (\d)", text)
    ]
    return row


def problems(rows: list[dict[str, Any]]) -> list[str]:
    """Departures from the statement; an empty list is a pass."""
    bad: list[str] = []
    by = {(r["target"], r["family"], r["mode"]): r for r in rows}
    for t in TARGETS:
        scroll, top = by[(t, "scroll", "plain")], by[(t, "top", "plain")]
        emb, ctl = by[(t, "embedded", "structure")], by[(t, "scroll", "control")]
        for name, row, prime_key, rank in (("scroll", scroll, "P2NONVAN", 4), ("top", top, "P1NONVAN", 5)):
            if not row.get("x0_zero") or row.get(prime_key) != 0 or row.get("RANK5") != rank:
                bad.append(f"{t} {name}: limit off its prime or Jacobian rank {row.get('RANK5')} != {rank}")
        if not emb.get("x0_zero") or emb.get("ANONVAN") != 0 or emb.get("RANK5") != 4:
            bad.append(f"{t} embedded: limit off A or Jacobian rank {emb.get('RANK5')} != 4")
        if emb.get("annihilator") != [4, 2] or not emb.get("radical_is_P1_meet_P2"):
            bad.append(f"{t} embedded: annihilator {emb.get('annihilator')} or radical differs from P1 meet P2")
        primary = sorted(tuple(p) for p in emb.get("primary", []))
        if primary != [(4, 2, 4, 0, 0, 1), (4, 4, 4, 0, 1, 0), (5, 11, 11, 1, 0, 0)]:
            bad.append(f"{t} embedded: associated primes {primary} differ from P1, P2 and A")
        nil = emb.get("nilpotent", [])
        nu, emin = emb.get("nu"), emb.get("EMIN")
        if emb.get("nilpotent_count") != 5 or len(nil) != 5 or nu is None or emin is None:
            bad.append(f"{t} embedded: nilpotent forms or orders missing")
        elif emin < 2 or not all(n["vanishes_on_limit"] and n["next_coefficient_nonzero"] for n in nil):
            bad.append(f"{t} embedded: a nilpotent form without order nu + 1 < nu + e_min")
        if not ctl.get("ANONVAN"):
            bad.append(f"{t} control: A vanishes on the scroll limits, so the test does not separate")
        if not ctl.get("JCORRUPT"):
            bad.append(f"{t} control: the arc with t9 + s^2 still satisfies J, so the J test does not separate")
        for row in (scroll, top, emb, ctl):
            if row.get("JNONVAN") != 0:
                bad.append(f"{t} {row['family']} {row['mode']}: J leaves a residue on the arc")
        if not emb.get("decomposition_complete"):
            bad.append(f"{t} embedded: the primary components do not intersect to K2")
        if (
            emb.get("numK") != qp.NUM_K_E8
            or emb.get("numA") != qp.NUM_A_E8
            or not qp.numerator_identity(emb, "numR", NGEN)
        ):
            bad.append(f"{t} embedded: N_K2 - N_R differs from N_A - (1 - t)^21 or a numerator from A5-547")
    return bad


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    # The per-target scripts and logs land beside the output record, so a replay into a scratch path leaves the
    # retained relation-ideal-orders/ directory untouched.
    logs = Path(sys.argv[1]).resolve().parent / "relation-ideal-orders"
    jobs = [(t, "embedded", "structure", logs) for t in TARGETS]
    jobs += [(t, f, "plain", logs) for t in TARGETS for f in ("scroll", "top")]
    jobs += [(t, "scroll", "control", logs) for t in TARGETS]
    rows = parallel.ordered_map(run, jobs, min_items=1)
    found = problems(rows)
    record = {
        "check": "e8-header-relation-ideal-orders",
        "families": {k: [f.a, f.b, f.c, f.d, f.n, list(f.etype), f.coords] for k, f in FAMILIES.items()},
        "rows": rows,
        "problems": found,
        "pass": not found,
    }
    Path(sys.argv[1]).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
