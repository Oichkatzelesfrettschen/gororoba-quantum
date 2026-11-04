"""Emit and run a Singular script computing the leading limit vector of an arc family symbolically.

Parameter arcs of Phi (README.md): w = W s^a, zeta = Z s^d,
  rho = R s^b, sigma = S s^c                                   (coordinates "rs")
  rho = (R s^b + S s^c)/2, sigma = (R s^b - S s^c)/2           (coordinates "pq", sum and difference)
  E = E0 s^k with |k| <= a, E0 symbolic, V = 1/E0              (type "k")
  E = e0 + E1 s^j with e0 a fixed nonzero integer, E1 symbolic (type "near"; the symbol E carries E1).
x(s) = Phi(...) truncated mod s^(n+1); the limit F is the coefficient of s^nu in (G_j(x(s))) at the first order nu
where some coefficient is a nonzero polynomial in the symbols. Global dp ordering; s is truncated by reduction.
For type "k" the output vector is E^n F (a polynomial in W, R, S, Z, E); for type "near" it is F.

usage: gen_family.py TARGET TAG A B C D N K COORDS      (type "k")
       gen_family.py TARGET TAG A B C D N E0 J COORDS   (type "near")
The script and its log are written to the current directory's fam/ subdirectory.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arc_targets import ROOT, TARGETS, Target, load_primes

SINGULAR_TIMEOUT = 900
EVAL_POINT = (3, 5, 7, 11, 2)


@dataclass(frozen=True)
class Family:
    """Monomial arc family: valuations a (w), b and c (the rho/sigma coordinates), d (zeta), jet order n.

    `etype` is ("k", k) for E = E0 s^k or ("near", e0, j) for E = e0 + E1 s^j.
    """

    tag: str
    a: int
    b: int
    c: int
    d: int
    n: int
    etype: tuple[Any, ...]
    coords: str


P2_FAMILY = Family("p2_first_order_n2", 1, 1, 1, 1, 2, ("k", 0), "rs")
P1_FAMILY = Family("near_e-1_j2_a2_b1_c1_d1_n5", 2, 1, 1, 1, 5, ("near", -1, 2), "pq")


def make_script(target: Target, fam: Family, p1: str, p2: str, k2: str, pt: tuple[int, ...] = EVAL_POINT) -> str:
    """The Singular input for one family; the only path it names is the repository-relative header."""
    a, b, c, d, n = fam.a, fam.b, fam.c, fam.d, fam.n
    if fam.etype[0] == "k":
        k = fam.etype[1]
        q = abs(k)
        if a < q:
            raise ValueError("need a >= |k|")
        rel = f"ideal rel=std(ideal(s^{n + 1},E*V-1));"
        if k > 0:
            nu_t = f"(E*s^{2 * k}+2*s^{k}+V)*quarter"
            om_t = f"(E*s^{2 * k}-V)*quarter"
        elif k == 0:
            nu_t = "(E+2+V)*quarter"
            om_t = "(E-V)*quarter"
        else:
            nu_t = f"(E+2*s^{q}+V*s^{2 * q})*quarter"
            om_t = f"(E-V*s^{2 * q})*quarter"
        epre = ""
        mult = f"E^{n}*"
        etag = f"E = E0 s^{k}"
    else:
        e0, j = fam.etype[1], fam.etype[2]
        q = 0
        rel = f"ideal rel=std(ideal(s^{n + 1}));"
        epre = (
            f"number ie0=1; ie0=ie0/({e0}); poly Ev={e0}+E*s^{j}; poly Vv=0; poly pwv=1;"
            f" poly er=-E*s^{j}*ie0; int ii;\n"
            f"for (ii=0;ii<={n};ii++) {{ Vv=Vv+pwv; pwv=reduce(pwv*er,rel); }} Vv=Vv*ie0;\n"
        )
        nu_t = "(Ev+2+Vv)*quarter"
        om_t = "(Ev-Vv)*quarter"
        mult = ""
        etag = f"E = {e0} + E1 s^{j}"
    if fam.coords == "pq":
        rho_def = f"half*(R*s^{b}+S*s^{c})"
        sig_def = f"half*(R*s^{b}-S*s^{c})"
    else:
        rho_def = f"R*s^{b}"
        sig_def = f"S*s^{c}"
    t9_expr = "-(w*w)*minv*half" if target.sign9 == 1 else "(w*w)*minv*half"
    gens = ",".join(f"F[1,{i}]" for i in range(1, 22))
    return f"""// Arc family {fam.tag}: w = W s^{a}, zeta = Z s^{d}, rho/sigma coordinates {fam.coords} (R s^{b}, S s^{c}), {etag}; order n = {n}.
< "{target.header}";
matrix Gn[1][21]; int j; for (j=1;j<=21;j++) {{ Gn[1,j]=jet(G[j],{n}); }}
ring Q={target.prime},(W,R,S,Z,E,V,s),dp;
number I={target.root};
{rel}
number half=1/2; number quarter=1/4;
poly w=W*s^{a}; poly rho={rho_def}; poly sig={sig_def}; poly zeta=Z*s^{d};
poly m=1+w; poly mm=reduce(m*m,rel);
poly minv=1; poly pw=1; int i;
for (i=1;i<={n};i++) {{ pw=reduce(-pw*w,rel); minv=minv+pw; }}
poly u=w+half*w*w; poly qinv=1; pw=1;
for (i=1;i<={n};i++) {{ pw=reduce(-pw*u,rel); qinv=qinv+pw; }}
qinv=half*qinv;
"inverse checks:", reduce(m*minv-1,rel), reduce((mm+1)*qinv-1,rel);
{epre}poly nuT={nu_t}; poly omT={om_t};
poly m2m1q=W*s^{a - q}*(2+w);
poly Zc=reduce(2*m2m1q*nuT,rel); poly Wc=reduce(2*m2m1q*omT,rel);
poly mm1=reduce(mm-1,rel);
poly T9=reduce({t9_expr},rel);
poly T4=reduce((m*rho+sig)*half,rel); poly T5=reduce((m*rho-sig)*half,rel); poly T6=reduce((m*sig+rho)*half,rel); poly T7=reduce((rho-m*sig)*half,rel);
poly T8=reduce(-I*Wc*minv*half,rel);
poly T3=zeta;
poly T2=reduce((Zc+mm1*zeta)*qinv,rel);
poly T1=reduce(((1-mm)*T2+(mm+1)*T3+w*w)*minv*half,rel);
"X0", subst(T1,s,0), subst(T2,s,0), subst(T3,s,0), subst(T4,s,0), subst(T5,s,0), subst(T6,s,0), subst(T7,s,0), subst(T8,s,0), subst(T9,s,0);
map f=r,T1,T2,T3,T4,T5,T6,T7,T8,T9;
matrix GXm=f(Gn);
matrix Cf[{n + 1}][21]; poly g; matrix cm; int o; int nrr;
for (j=1;j<=21;j++) {{
  g=reduce(GXm[1,j],rel);
  if (g!=0) {{ cm=coeffs(g,s); nrr=nrows(cm); for (o=1;o<=nrr and o<={n + 1};o++) {{ Cf[o,j]=reduce({mult}cm[o,1],rel); }} }}
}}
int nu=-1; int found=0;
for (o=1;o<={n + 1} and found==0;o++) {{ for (j=1;j<=21;j++) {{ if (Cf[o,j]!=0) {{ found=1; nu=o-1; }} }} }}
"NU", nu;
if (nu<0) {{ "NOFOUND"; quit; }}
matrix F[1][21]; for (j=1;j<=21;j++) {{ F[1,j]=Cf[nu+1,j]; }}
for (j=1;j<=21;j++) {{ if (F[1,j]!=0) {{ "FJ", j, string(F[1,j]); }} }}
ring Y={target.prime},(y(1..21)),dp;
ideal P1={p1};
ideal P2={p2};
ideal K2={k2};
setring Q;
map g1=Y,{gens};
ideal P2F=g1(P2); ideal P1F=g1(P1); ideal K2F=g1(K2); int jj;
for (jj=1;jj<=size(P2F);jj++) {{ P2F[jj]=reduce(P2F[jj],rel); }}
for (jj=1;jj<=size(P1F);jj++) {{ P1F[jj]=reduce(P1F[jj],rel); }}
for (jj=1;jj<=size(K2F);jj++) {{ K2F[jj]=reduce(K2F[jj],rel); }}
"P2NONVAN", size(P2F);
"P1NONVAN", size(P1F);
"K2NONVAN", size(K2F);
matrix Jac[21][5]; for (j=1;j<=21;j++) {{ Jac[j,1]=diff(F[1,j],W); Jac[j,2]=diff(F[1,j],R); Jac[j,3]=diff(F[1,j],S); Jac[j,4]=diff(F[1,j],Z); Jac[j,5]=diff(F[1,j],E); }}
int cc; matrix Jv[21][5];
for (j=1;j<=21;j++) {{ for (cc=1;cc<=5;cc++) {{ Jv[j,cc]=subst(subst(subst(subst(subst(Jac[j,cc],W,{pt[0]}),R,{pt[1]}),S,{pt[2]}),Z,{pt[3]}),E,{pt[4]}); }} }}
"RANK5", rank(Jv);
quit;
"""  # noqa: E501


def run_singular(script: Path, timeout: int = SINGULAR_TIMEOUT) -> str:
    """Run a Singular script from the repository root with stdin closed (Singular reads stdin when it is not a tty)."""
    try:
        done = subprocess.run(
            ["Singular", "-q", str(script)],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{script.name}: Singular exceeded {timeout} s") from exc
    return done.stdout + done.stderr


def run(target: Target, fam: Family, workdir: Path, timeout: int = SINGULAR_TIMEOUT) -> str:
    """Write fam_TAG.sing and fam_TAG.log under workdir/fam and return the Singular output."""
    p1, p2, k2 = load_primes(target)
    out = workdir / "fam"
    out.mkdir(parents=True, exist_ok=True)
    script = out / f"fam_{fam.tag}.sing"
    script.write_text(make_script(target, fam, p1, p2, k2))
    text = run_singular(script, timeout)
    (out / f"fam_{fam.tag}.log").write_text(text)
    return text


def parse(out: str) -> dict[str, object] | None:
    """The counts of a family log, or None when no order nu was found."""
    m = re.search(r"NU (-?\d+)", out)
    if not m or int(m.group(1)) < 0:
        return None
    row: dict[str, object] = {"nu": int(m.group(1))}
    for key in ("P2NONVAN", "P1NONVAN", "K2NONVAN", "RANK5"):
        mm = re.search(key + r" (\d+)", out)
        row[key] = int(mm.group(1)) if mm else None
    row["nonzero"] = [int(x) for x in re.findall(r"FJ (\d+) ", out)]
    x0 = re.search(r"X0 (.*)", out)
    row["x0_zero"] = x0 is not None and all(t.strip() == "0" for t in x0.group(1).split())
    return row


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    tag = argv[2]
    a, b, c, d, n = (int(x) for x in argv[3:8])
    coords = argv[-1]
    etype: tuple[Any, ...]
    if len(argv) == 10:
        etype = ("k", int(argv[8]))
    else:
        etype = ("near", int(argv[8]), int(argv[9]))
    print(run(target, Family(tag, a, b, c, d, n, etype, coords), Path.cwd()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
