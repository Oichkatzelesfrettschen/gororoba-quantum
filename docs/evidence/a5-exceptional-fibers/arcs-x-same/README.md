# Arc certificate for the same-sign X incidences: the fiber support of X- -> N- and X+ -> N+ has dimension 4

Result. At p = 32009 and p = 32029 an explicit arc family on the slice of X- -> N- (`xm-nm`) and of X+ -> N+
(`xp-np`) has limit vectors that sweep a cone of dimension 4 inside V(K2). V(K2) has dimension 4 (`../k2-cm.jsonl`),
so the cone is an irreducible component of V(K2) of full dimension, the analytic spread of I is 4, and at p = 32009,
where V(K2) of X- is one irreducible three-fold of degree 12 (ledger A5-022), the reduced fiber E0 equals V_+(K2).
Two ledger rows follow: A5-022 no longer carries "the support may be a proper closed subset", and A5-245 is refuted,
since at analytic spread 4 the certified Hilbert function 15, 51, 122, 240 has the D'Cruz-Raghavan-Verma numerator
1, 11, -3, 4, -1, which a Cohen-Macaulay fiber cone excludes. The statements hold over F_32009 and F_32029; K2 is not
radical (its variety spans a P^11 while K2 holds no linear form), so the support does not decide L = K2 beyond the
certified degrees 1 to 6.

## The parametrization

The slice V(J) of `xm-nm` has 12 generators in t1, t2, t4, t5, t6, t7, t9, none with a linear term, so the germ at
the origin is singular, unlike the opposite-sign slices of [../arcs-x](../arcs-x/README.md). Four generators are the
rank-one relations of that package and give t4 to t7 and t9 from (w, rho, sig) with m = 1 + w. In the coordinate
a = t1 + t9 the remaining generators are linear in (a, t2) and hold on the line t2 = a w (w + 2) / (2 m):

    Phi(w, rho, sig, a):  t4 = (m rho + sig)/2,  t5 = (m rho - sig)/2,  t6 = (m sig + rho)/2,  t7 = (rho - m sig)/2,
                          t9 = s9 T9,  T9 = -w^2/(2 m),  t1 = a - T9,  t2 = a w (w + 2)/(2 m).

s9 = +1 on `xm-nm`; the header of `xp-np` is that of `xm-nm` at -t9, so s9 = -1 there. Every script checks
J(Phi) = 0 as a polynomial identity modulo u m = 1 (0 of 12 generators nonzero). Phi maps the origin to the origin
and the origin is its only preimage, and every generator of I vanishes on w = 0, the linear 3-space
L0 = {t2 = 0, t4 = t6, t5 = t7, t9 = 0}.

## The arcs

Straight arcs w = W s, rho = R s, sig = S s, a = A s have G of order 3 and limit rank 3. The weighted arcs

    w = W s^2,  rho = R s,  sig = S s,  a = A s

have G of order 5, 12 nonzero limit entries and rank 4. `x_same_arcs.py` writes one script per incidence, prime and
control; each runs from the repository root in the global ordering `dp` with W, R, S, A as ring variables (Singular
4.4.1 on the build host, at most 0.3 s and 20 MB per case).

| Case | J on Phi | order of G, lower coefficients | K2 quadrics nonzero on the limit | rank of [dF, F] at two points |
|---|---|---|---|---|
| `xm-nm-arcs-p32009` | 0 of 12 | 5, all zero identically | 0 of 69 | 4, 4 |
| `xm-nm-arcs-p32029` | 0 of 12 | 5, all zero identically | 0 of 69 | 4, 4 |
| `xp-np-arcs-p32009` | 0 of 12 | 5, all zero identically | no K2 file at this prime | 4, 4 |
| `xp-np-arcs-p32029` | 0 of 12 | 5, all zero identically | 0 of 69 | 4, 4 |
| `*-mutated` (t2 doubled) | 8 of 12 nonzero | 5 | 24 of 69 where a K2 file exists | 4, 4 |

The mutated arc doubles t2 and leaves V(J); K2 then fails on 24 quadrics. A reversed t9 is no control for K2 on this
arc: t9 has order 4 and enters the coefficient of s^5 through its products with the order-1 coordinates, so the
reversal changes 5 entries of F and takes the arc off V(J), yet all 69 quadrics still vanish on the new limit (the
reversed arc is the arc of the other same-sign incidence, whose header is this one at -t9). Each unmutated log also holds the scan of the 27
weight vectors with weights 1 to 3 for w, for (rho, sig) and for a (`RESULT scan weights`): (2, 1, 1) is the only one
with rank 4, and the scans agree across the four cases.

## Deduction

1. Phi(arc) lies on V(J) and passes through the origin.
2. The coefficients of s^0 to s^4 of every G_j vanish identically in (W, R, S, A) and the coefficient F of s^5 is a
   nonzero polynomial vector, so F is the limit vector on a dense open set and lies in the affine cone over E0.
3. The cone over the image of F, the closure of the image of (lambda, u) -> lambda F(u), is irreducible of dimension
   at least 4, the rank at a point of [dF, F], the Jacobian of that map at lambda = 1, and it lies in V(K2) because
   K2 lies in L. dim V(K2) = 4, so the cone is a component of V(K2) and dim F(I) = 4.
4. At p = 32009 V(K2) of X- is irreducible (A5-022), so E0 = V_+(K2) there.

The arcs have rational coefficients, so they are real arcs. The Python series engine of
[../kernel-limits/](../kernel-limits/README.md) evaluates them with separate code: the header's J vanishes on each
arc through order 39 and G has order 5.

Scope: irreducibility of V(K2) is recorded at 32009 for X- only; at 32029 and for X+ the statement is "a component of
dimension 4". Characteristic 0 is not addressed.

Check without Singular: [arc_rank_check.py](../arc_rank_check.py) recomputes the ranks of [dF, F] at the same parameter points by
dual-number power series in Python, with the arc rewritten from its formula, and reproduces every rank, the order
of G and the vanishing of J; it shares no code with Singular and shares the series arithmetic and polynomial
evaluator of `kernel-limits/plucker_limits.py` ([arc-rank-check.json](../arc-rank-check.json)).

## Census of the quadric ideal: one minimal prime, not radical (A5-297)

`xm-nm-quadric-census-p32009.sing` and `xm-nm-quadric-census-p32029.sing` read the 69 quadrics K2 of X- -> N- from
the retained degree-2 relations and compute, in Singular 4.4.1, the Hilbert series, the minimal free resolution and
the minimal primes (`minAssChar`). The two logs agree line for line.

| quantity | k[y]/K2 | k[y]/P, P the minimal prime |
|---|---|---|
| minimal generators | 69 quadrics | 3 linear forms (y1, y5, y6) and 33 quadrics |
| dimension, multiplicity | 4, 12 | 4, 12 |
| numerator of the Hilbert series over (1 - t)^4 | 1, 11, -3, 4, -1 | 1, 8, 3 |
| Hilbert function in degrees 1, 2, 3 | 15, 51, 122 | 12, 45, 112 |
| projective dimension, depth | 14, 1 | 11, 4 (Cohen-Macaulay) |
| rows of the Betti table | 1 and 2 (regularity of the quotient 2) | 0, 1 and 2 |

K2 has exactly one minimal prime P, K2 lies in P and P does not lie in K2. The quadric locus V(K2) is therefore
irreducible of dimension 3 and degree 12 in the linear space y1 = y5 = y6 = 0, and K2 differs from P by embedded
structure: y1, y5 and y6 are nilpotent modulo K2. The weighted arcs of this directory span 12 coordinates and 45
quadrics in the fiber-to-Grassmannian fit of [kernel-limits](../kernel-limits/README.md), the Hilbert function of
k[y]/P, so those arcs sample the whole reduced fiber. Scope: two primes; X+ -> N+ is not computed; the embedded
primes of K2 and the equality of K2 with the ideal L of the fiber cone in every degree stay open. Each run takes
280 s and 0.5 GB:

    Singular -q --no-warn < docs/evidence/a5-exceptional-fibers/arcs-x-same/xm-nm-quadric-census-p32009.sing
