"""Singular inputs of the arc certificate for one target, written from the tracked header and K2 relation file.

Every script names at most the repository-relative header and runs from the repository root in a global monomial
ordering (`dp`, and the block orderings that `eliminate` builds). No script writes a file or prints a timing.
"""

from __future__ import annotations

from arc_targets import Target, header_ideals, k2_ideal

HILBERT_DEGREES = 6


def k2_primes_script(target: Target) -> str:
    """Radical and minimal primes of K2, the Hilbert functions of k[y]/K2 and k[y]/sqrt(K2)."""
    return f"""// Minimal primes of sqrt(K2), {target.name}, global dp ordering.
LIB "primdec.lib"; option(redSB);
ring Y={target.prime},(y(1..21)),dp;
ideal K=
{k2_ideal(target)};
K=std(K); "K gens", size(K), "dim", dim(K), "deg", mult(K);
int d;
for (d=1;d<={HILBERT_DEGREES};d++) {{ "HF_K2", d, size(kbase(K,d)); }}
ideal R=radical(K); R=std(R); "radical dim", dim(R), "deg", mult(R);
list P=minAssChar(R); "minimal primes", size(P);
int i; ideal Q;
for (i=1;i<=size(P);i++) {{
  Q=std(P[i]); "prime", i, "proj dim", dim(Q)-1, "deg", mult(Q), "linear gens", size(jet(Q,1))-size(jet(Q,0));
  "PRIME_GENS", i, string(minbase(P[i]));
}}
if (size(P)==2) {{
  ideal Z=std(intersect(P[1],P[2])); "radical == P1 cap P2 :", size(reduce(Z,R))==0 and size(reduce(R,Z))==0;
  for (d=1;d<={HILBERT_DEGREES};d++) {{ "HF_sqrtK2", d, size(kbase(Z,d)); }}
}}
quit;
"""  # noqa: E501


def verify_phi_script(target: Target) -> str:
    """J(Phi) = 0 as an identity in the function field, with two corrupted maps as negative controls."""
    j_text = ",".join(header_ideals(target)[0])
    t9 = "-(m-1)^2/(2*m)" if target.sign9 == 1 else "(m-1)^2/(2*m)"
    return f"""// J(Phi) = 0 as an identity in the function field F_{target.prime}(m, rho, sigma, e, zeta); J is the header's J.
// Phi: t4..t7 from the rank-one matrix [[m rho, m sigma],[rho, sigma]], t9 = {t9}, and on the conic
// Z (Z - 2(m^2-1)) = W^2 with Z = (m^2+1) t2 - (m^2-1) t3, W = 2 i m t8 (see README.md).
ring R=({target.prime},m,rho,sigma,e,zeta),(t1,t2,t3,t4,t5,t6,t7,t8,t9),dp;
number I={target.root};
"i^2+1 =", I^2+1;
ideal J={j_text};
number nu=(e+1)^2/(4*e); number om=(e^2-1)/(4*e);
poly T9={t9};
poly T4=(m*rho+sigma)/2; poly T5=(m*rho-sigma)/2; poly T6=(m*sigma+rho)/2; poly T7=(rho-m*sigma)/2;
poly Zc=2*(m^2-1)*nu; poly Wc=2*(m^2-1)*om;
poly T8=-I*Wc/(2*m);
poly T3=zeta;
poly T2=(Zc+(m^2-1)*zeta)/(m^2+1);
poly T1=((1-m^2)*T2+(m^2+1)*T3+(m-1)^2)/(2*m);
map ph=R,T1,T2,T3,T4,T5,T6,T7,T8,T9;
ideal Jp=ph(J);
int k; int nvan=0; for (k=1;k<=size(J);k++) {{ "J["+string(k)+"] on Phi vanishes:", Jp[k]==0; if (Jp[k]==0) {{ nvan++; }} }}
"generators vanishing identically:", nvan, "of", size(J);
poly T9bad=T9+1;
map phbad=R,T1,T2,T3,T4,T5,T6,T7,T8,T9bad;
ideal Jb=phbad(J); int nbad=0;
for (k=1;k<=size(J);k++) {{ if (Jb[k]!=0) {{ nbad++; }} }}
"mutation (t9 -> t9+1): nonzero residues in", nbad, "of", size(J);
poly T9flip=-T9;
map phflip=R,T1,T2,T3,T4,T5,T6,T7,T8,T9flip;
ideal Jf=phflip(J); int nflip=0;
for (k=1;k<=size(J);k++) {{ if (Jf[k]!=0) {{ nflip++; }} }}
"mutation (t9 -> -t9): nonzero residues in", nflip, "of", size(J);
quit;
"""  # noqa: E501


def scroll_script(target: Target, p2: str) -> str:
    """The scroll parametrization of V(P2) eliminated against P2."""
    return f"""// V(P2) is the cone over a rational normal scroll S(1,1,2) in P^6: eliminate the scroll parameters (s, t, l, mu)
// from the parametrization and compare with P2 (global dp ordering; elimination by the block ordering of eliminate()).
LIB "elim.lib";
ring B={target.prime},(s,t,l,mu,y(1..21)),dp;
number I={target.root};
ideal Par=y(1)+I*y(20), y(2), y(3)-s^2, y(4), y(5)+y(16), y(6), y(7), y(8), y(9), y(10)-I*mu*t, y(11)-l*t, y(12), y(13), y(14),
  y(15)-I*y(16), y(16)-mu*s, y(17)+I*y(18), y(18)-l*s, y(19), y(20)-s*t, y(21)+I*t^2;
ideal Im=eliminate(Par,s*t*l*mu); Im=std(Im);
ring Y={target.prime},(y(1..21)),dp;
ideal P2={p2};
ideal P2s=std(P2);
setring B;
map toB=Y,y(1),y(2),y(3),y(4),y(5),y(6),y(7),y(8),y(9),y(10),y(11),y(12),y(13),y(14),y(15),y(16),y(17),y(18),y(19),y(20),y(21);
ideal P2B=toB(P2); P2B=std(P2B);
"image ideal equals P2:", size(reduce(P2B,Im))==0 and size(reduce(Im,P2B))==0;
"dim of image (affine cone)", dim(Im)-4, "deg", mult(Im);
quit;
"""  # noqa: E501


def j_decomp_script(target: Target) -> str:
    """Dimension, degree and minimal primes of J."""
    return f"""// dimension, degree and minimal primes of J (global dp ordering); the header defines ring r and the ideals J, G.
LIB "primdec.lib";
< "{target.header}";
ideal Js=std(J); "J gens", size(J), "dim", dim(Js), "deg", mult(Js);
list L=minAssChar(J); "minimal primes of J:", size(L);
int i; for (i=1;i<=size(L);i++) {{ ideal Q=std(L[i]); "prime", i, "dim", dim(Q), "deg", mult(Q); kill Q; }}
ideal M=std(maxideal(1)); for (i=1;i<=size(L);i++) {{ ideal Q=L[i]; "prime", i, "contained in the maximal ideal of the origin:", size(reduce(Q,M))==0; kill Q; }}
quit;
"""  # noqa: E501


def compare_script(
    plus: Target, minus: Target, plus_ideals: tuple[str, str, str], minus_ideals: tuple[str, str, str]
) -> str:
    """Ideal equality of the N+ and N- data of one prime; the ideals are (P1, P2, K2) generator lists."""
    if plus.prime != minus.prime:
        raise ValueError("the comparison needs one prime")
    pp1, pp2, kp = plus_ideals
    pm1, pm2, km = minus_ideals
    return f"""// Ideal equality of the N+ and N- data at p = {plus.prime}, global dp ordering.
ring Y={plus.prime},(y(1..21)),dp;
ideal Pp1={pp1}; ideal Pp2={pp2}; ideal Kp={kp};
ideal Pm1={pm1}; ideal Pm2={pm2}; ideal Km={km};
Pp1=std(Pp1); Pp2=std(Pp2); Kp=std(Kp); Pm1=std(Pm1); Pm2=std(Pm2); Km=std(Km);
"P1 equal:", size(reduce(Pp1,Pm1))==0 and size(reduce(Pm1,Pp1))==0;
"P2 equal:", size(reduce(Pp2,Pm2))==0 and size(reduce(Pm2,Pp2))==0;
"K2 equal:", size(reduce(Kp,Km))==0 and size(reduce(Km,Kp))==0;
"K2(N+) contained in K2(N-):", size(reduce(Kp,Km))==0, " K2(N-) contained in K2(N+):", size(reduce(Km,Kp))==0;
"P1(N+) in P1(N-):", size(reduce(Pp1,Pm1))==0, " P1(N+) in P2(N-):", size(reduce(Pp1,Pm2))==0;
quit;
"""  # noqa: E501
