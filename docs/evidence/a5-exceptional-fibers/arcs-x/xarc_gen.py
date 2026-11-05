"""Write the Singular scripts of the X+ -> N- / X- -> N+ arc runs of one prime into sing/pPRIME/.

Every ring uses a global ordering (dp). Per incidence slug the scripts are
  SLUG_phi.sing      J(Phi) = 0 as an identity, G(Phi) = h * G'', h = gcd, initial forms of G''
  SLUG_limit.sing    the leading coefficient vector of G(x(s)) for x(s) = Phi(W s, R s, S s, K s), symbolic in W,R,S,K
  SLUG_ctl.sing      negative control on the identity J(Phi) = 0 (the t9 term of J[12] reversed)
  SLUG_explore.sing  dimension, Jacobian rank at the origin and minimal primes of J
  SLUG_quot.sing     colength ladders of (J + G) : t2 and of J + t2 against the maximal-ideal powers
  model_colength.sing colength of x1*(x1,x2,x3) + m^n in k[x1..x4] against the measured Hilbert-Samuel ladder
Phi (parameters w, rho, sig, s1; m = 1 + w, u = 1/m):
  t1 = s1, t4 = (m rho + sig)/2, t5 = (m rho - sig)/2, t6 = (m sig + rho)/2, t7 = (rho - m sig)/2,
  t9 = -sgn w^2 u / 2 (sgn = +1 for X+ -> N-, -1 for X- -> N+),
  t2 = lam (t1 - t9xp + 2) with lam = w (2 + w) u / 2 and t9xp = -w^2 u / 2.
The scripts read no file; each starts with the four header lines. Run them from this directory: the phi script writes
work/pPRIME/gn_SLUG.txt and work/pPRIME/h_SLUG.txt relative to it.
"""

from __future__ import annotations

from xarc_common import FLIPPED_GENERATOR, SIGN9, T9_KEY, Header, prime_dir

PHI_TEXT = """
number half=1/2;
poly m=1+w;
poly T9xp=-half*w^2*u;
poly T9=({sgn})*T9xp;
poly T4=(m*rho+sig)*half; poly T5=(m*rho-sig)*half; poly T6=(m*sig+rho)*half; poly T7=(rho-m*sig)*half;
poly T2=half*w*(2+w)*u*(s1-T9xp+2);
poly T1=s1;
"""

CLEAR = """
proc clear(poly g) {
  if (g==0) { return(g); }
  int N=deg(g,intvec(0,0,0,0,1)); int k; poly res=0;
  matrix C=coeffs(g,u);
  for (k=1;k<=nrows(C);k++) { res=res+C[k,1]*m^(N-(k-1)); }
  return(res);
}
"""


def signed(c: int, p: int) -> int:
    """The representative of c modulo p in (-p/2, p/2]."""
    c %= p
    return c - p if c > p // 2 else c


def t9_coefficient(h: Header) -> int:
    """The signed coefficient of the monomial t9 in the generator J[12] that the control reverses."""
    c = h.j[FLIPPED_GENERATOR].get(T9_KEY, 0)
    if c == 0:
        raise ValueError(f"{h.path.name}: J[{FLIPPED_GENERATOR + 1}] has no t9 term to reverse")
    return signed(c, h.prime)


def phi_script(h: Header) -> str:
    sgn = SIGN9[h.slug]
    return f"""{h.preamble}
ring R={h.prime},(w,rho,sig,s1,u),dp;
{PHI_TEXT.format(sgn=sgn)}
{CLEAR}
map phi=r,T1,T2,T4,T5,T6,T7,T9;
ideal Jp=phi(J); ideal Gp=phi(G);
int i; int nz=0;
for (i=1;i<=ncols(Jp);i++) {{ if (clear(Jp[i])!=0) {{ nz++; }} }}
"J generators:", ncols(Jp), "nonzero images:", size(Jp), "nonzero numerators of J(Phi):", nz;
poly uw=u*m-1;
"inverse relation u*m-1:", uw;
list Gn; for (i=1;i<=3;i++) {{ Gn[i]=clear(Gp[i]); "G",i,"cleared numerator degree",deg(Gn[i]),"terms",size(Gn[i]); }}
poly h=gcd(Gn[1],gcd(Gn[2],Gn[3]));
"gcd h of the three numerators:"; h;
list fh=factorize(h);
"factors of h:"; fh;
for (i=1;i<=3;i++) {{
  poly q(i)=Gn[i]/h;
  "G'' ",i," exact division remainder h*q-G:", h*q(i)-Gn[i], " degree", deg(q(i)), "terms", size(q(i));
  "G'' ",i," jet of degree 1:", jet(q(i),1);
  "G'' ",i," constant term:", subst(q(i),w,0,rho,0,sig,0,s1,0);
}}
"gcd12 =", gcd(Gn[1],Gn[2]) == h, " gcd23 =", gcd(Gn[2],Gn[3]) == h;
write(":w work/p{h.prime}/gn_{h.slug}.txt", string(Gn[1])+";"+string(Gn[2])+";"+string(Gn[3]));
write(":w work/p{h.prime}/h_{h.slug}.txt", string(h));
quit;
"""


def limit_script(h: Header) -> str:
    sgn = SIGN9[h.slug]
    return f"""{h.preamble}
ring R={h.prime},(W,Rr,S,K,s),dp;
ideal rel=std(s^4);
number half=1/2;
poly w=W*s; poly rho=Rr*s; poly sig=S*s; poly s1=K*s;
poly m=1+w;
poly u=reduce(1-w+w^2-w^3,rel);
"inverse check m*u-1 mod s^4:", reduce(m*u-1,rel);
poly T9xp=reduce(-half*w^2*u,rel);
poly T9=({sgn})*T9xp;
poly T4=reduce((m*rho+sig)*half,rel); poly T5=reduce((m*rho-sig)*half,rel);
poly T6=reduce((m*sig+rho)*half,rel); poly T7=reduce((rho-m*sig)*half,rel);
poly T2=reduce(half*w*(2+w)*u*(s1-T9xp+2),rel);
poly T1=s1;
map phi=r,T1,T2,T4,T5,T6,T7,T9;
"x(s) = Phi(W s, R s, S s, K s) mod s^4:";
"t1",T1; "t2",T2; "t4",T4; "t5",T5; "t6",T6; "t7",T7; "t9",T9;
int j; int k; poly g; ideal Gp=phi(G);
for (j=1;j<=3;j++) {{
  g=reduce(Gp[j],rel);
  "G",j,"(x(s)) coefficients of s^0..s^3:";
  for (k=0;k<=3;k++) {{ "  s^",k,":", coeffs(g,s)[k+1,1]; }}
}}
quit;
"""


def ctl_script(h: Header) -> str:
    # Control: reverse the sign of the t9 term of the last generator of J; the cleared numerators of J'(Phi) must not
    # all vanish.
    sgn = SIGN9[h.slug]
    c = t9_coefficient(h)
    n = FLIPPED_GENERATOR + 1
    return f"""{h.preamble}
ideal Jc=J; Jc[{n}]=Jc[{n}]-2*({c}*t9);
"control J[{n}] term {c:+d}*t9 flipped to {-c:+d}*t9: J[{n}] =", Jc[{n}];
ring R={h.prime},(w,rho,sig,s1,u),dp;
{PHI_TEXT.format(sgn=sgn)}
{CLEAR}
map phi=r,T1,T2,T4,T5,T6,T7,T9;
ideal Jp=phi(Jc); int i; int nz=0;
for (i=1;i<=ncols(Jp);i++) {{ if (clear(Jp[i])!=0) {{ nz++; }} }}
"nonzero numerators of J'(Phi) (control must be > 0):", nz;
quit;
"""


def explore_script(h: Header) -> str:
    return f"""{h.preamble}
ideal sJ=std(J); "dim V(J)", dim(sJ), "global degree", mult(sJ), "J generators", ncols(J);
matrix M=jacob(J);
matrix M0=subst(M,t1,0); M0=subst(M0,t2,0); M0=subst(M0,t4,0); M0=subst(M0,t5,0);
M0=subst(M0,t6,0); M0=subst(M0,t7,0); M0=subst(M0,t9,0);
"rank of the Jacobian of J at the origin", rank(M0);
print(M0);
LIB "primdec.lib";
list pr=minAssGTZ(J);
"minimal primes of J", size(pr);
int k; for (k=1;k<=size(pr);k++) {{ "prime",k,"dim",dim(std(pr[k])),"global degree",mult(std(pr[k])); }}
"J equals its minimal prime:", size(reduce(pr[1],sJ))==0 and size(reduce(J,std(pr[1])))==0;
quit;
"""


def quot_script(h: Header) -> str:
    return f"""{h.preamble}
// f = t2 equals w times a unit at the origin (t2 = w (2+w) u (s1 - t9xp + 2) / 2 on V(J)).
option(redSB);
ideal IJ=J+G;
ideal Q=quotient(std(IJ),ideal(t2));
Q=std(Q);
"I'=(J+G):t2 computed, generators", ncols(Q), "global dim", dim(Q);
int n;
for (n=1; n<=8; n++) {{
  ideal Qn=std(Q+maxideal(n)); "n", n, "colength of I' + m^n:", vdim(Qn), " (smooth curve germ: n)"; kill Qn;
}}
ideal Q2=std(J+ideal(t2)); ideal R2=std(Q2+maxideal(2));
"colength of (J+t2) + m^n for n=1..6 (smooth 3-fold germ: C(n+2,3)):";
for (n=1; n<=6; n++) {{ ideal Rn=std(J+ideal(t2)+maxideal(n)); "n", n, vdim(Rn); kill Rn; }}
"G inside (J+t2) globally (number of nonzero remainders; the other branch t2 = 0, w = -2 lies off the origin):",
  size(reduce(G,std(J+ideal(t2))));
"colength of (J+t2+G) + m^n against (J+t2) + m^n (equal: G lies in (J+t2) modulo m^n):";
for (n=1; n<=8; n++) {{
  ideal A1=std(J+ideal(t2)+G+maxideal(n)); ideal A2=std(J+ideal(t2)+maxideal(n));
  "n", n, vdim(A1), vdim(A2); kill A1; kill A2;
}}
quit;
"""


def model_script(prime: int) -> str:
    return f"""ring r={prime},(x1,x2,x3,x4),dp;
ideal I=x1*x1,x1*x2,x1*x3;
int n;
for (n=2; n<=14; n=n+2) {{ ideal Q=std(I+maxideal(n)); "n", n, "colength", vdim(Q); kill Q; }}
quit;
"""


def scripts(headers: dict[str, Header]) -> dict[str, str]:
    """{file name: Singular script} for the two incidences of one prime."""
    primes = {h.prime for h in headers.values()}
    if len(primes) != 1:
        raise ValueError("the headers differ in prime")
    out = {}
    for slug, h in headers.items():
        out[f"{slug}_phi.sing"] = phi_script(h)
        out[f"{slug}_limit.sing"] = limit_script(h)
        out[f"{slug}_ctl.sing"] = ctl_script(h)
        out[f"{slug}_quot.sing"] = quot_script(h)
        out[f"{slug}_explore.sing"] = explore_script(h)
    out["model_colength.sing"] = model_script(primes.pop())
    return out


def write_scripts(headers: dict[str, Header]) -> list[str]:
    """Write the scripts of one prime into sing/pPRIME/ and create work/pPRIME/; returns the script names."""
    prime = next(iter(headers.values())).prime
    texts = scripts(headers)
    directory = prime_dir("sing", prime)
    directory.mkdir(parents=True, exist_ok=True)
    prime_dir("work", prime).mkdir(parents=True, exist_ok=True)
    for name, text in texts.items():
        (directory / name).write_text(text)
    return sorted(texts)
