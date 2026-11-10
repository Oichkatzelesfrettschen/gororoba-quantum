# Arc certificate for E8-bar -> VB: both components of V(K2) lie in the fiber

Result. At p = 32009 and p = 32029 the slice V(J) of E8-bar -> VB carries two exact arc families. The limits of the
first are dense in the degree-4 component V(P2) of V(K2), and the limits of the second are dense in the degree-3
component V(P1). K2 lies in the ideal L of the fiber cone, so the reduced fiber is E0 = V_+(K2) = V_+(P1) cup
V_+(P2). K2 is the intersection of its two minimal primes (`../k2-cm.jsonl`, `K2_is_intersection`), hence radical,
and k[y]/K2 is Cohen-Macaulay of dimension 4 (ledger A5-010), hence saturated, so L = K2 and F(I) = k[y]/K2 in every
degree at both primes. This decides ledger rows A5-016 (the degree-3 component, open since the first arc report),
A5-015 (the degree-4 component, until now an interpolated family at one prime) and A5-005. The statements hold over
F_32009 and F_32029; the arcs have rational coefficients, and characteristic 0 is not addressed.

## The parametrization

Four generators of J are the rank-one relations of [../arcs-x](../arcs-x/README.md) in (t3, t4, t5, t6, t8) and give
those coordinates from (w, rho, sig) with m = 1 + w. Given them, t2 is linear in t1 and (t1, t7) lies on a conic over
the w-line whose section t7 = 0 splits into two rational points, so a parameter k rationalizes it:

    Phi(w, rho, sig, k):  t3 = -(m rho + sig)/2,  t4 = (m sig + rho)/2,  t5 = (m rho - sig)/2,  t6 = (rho - m sig)/2,
                          t8 = -w^2/(2 m),  t1 = (k^2 a1 - a2)/(4 m^2 (1 + k^2)),  t7 = k w (w + 2)/(m (1 + k^2)),
                          t2 = (t1 w (w + 2) + 2 w^2)/(m^2 + 1),
    a1 = w^4 - 6 w^2 - 4 w,  a2 = w^4 + 8 w^3 + 18 w^2 + 12 w.

Every script checks J(Phi) = 0 as an identity modulo the three unit relations (0 of 17 generators nonzero). Phi maps
the whole line l = {w = rho = sig = 0} to the origin, so an arc through any point (0, 0, 0, k0) of l gives an arc of
V(J) through the origin. On Phi the generators of I have order 2 in (w, rho, sig), with lowest parts spanned by w^2,
w rho and w sig and coefficients depending on k.

## The two families

- Generic point of l (`vb-generic-pP`): w = W s, rho = R s, sig = S s, k = K constant, with v = 1/(1 + K^2) carried
  as a variable modulo v (1 + K^2) = 1. G has order 2, and the limit lies in V(P2).
- The point k0 = -9 (`vb-special-pP`): k = -9 + K s, w = W s^2, rho = R s, sig = S s. At k0 = -9 the 2 x 2 minors of
  the coefficient matrix of (w rho, w sig) vanish, so the pulled-back ideal is no longer (w, rho, sig) times w there.
  G has order 4, and the limit lies in V(P1) and outside V(P2).

`vb_arcs.py` writes the scripts (`--check` requires every file to match); each runs from the repository root as
`Singular -q --no-warn < CASE.sing > CASE.log` in the global ordering `dp` with the arc parameters as ring variables
(Singular 4.4.1 on the build host, under 1 s and 26 MB per case). P1 and P2 are the two minimal primes of K2,
computed in each script by `minAssGTZ` and told apart by degree (3 and 4; 7 and 9 generators). Each script checks that
the generators of the run that produced its K2 file equal the header's up to sign (literally at 32029; modulo J at
32009, where the run input lists them before reduction) and reads every sign as +1.

| Case | J | order of G | K2 quadrics nonzero on the limit | P1 nonzero | P2 nonzero | rank of [dF, F] at two points |
|---|---|---|---|---|---|---|
| `vb-generic-p32009`, `-p32029` | 0 of 17 on Phi | 2 | 0 of 21 | 7 of 7 | 0 of 9 | 4, 4 |
| `vb-special-p32009`, `-p32029` | 0 of 17 on Phi, 0 on the arc through order 12 | 4 | 0 of 21 | 0 of 7 | 8 of 9 | 4, 4 |
| `vb-generic-pP-mutated` (t7 doubled) | 6 of 17 nonzero | 2 | 11 (32009), 12 (32029) | 7 of 7 | 5 of 9 | 4, 4 |
| `vb-special-pP-mutated` (t8 doubled) | 13 nonzero on the arc | 4 | 16 (32009), 17 (32029) | 5 of 7 | 8 of 9 | 4, 4 |
| `vb-special-pP-neighbor` (k0 = -8) | 0 | 3 | 0 | 2 of 7 | 0 of 9 | 2, 2 |
| `vb-special-pP-scan` | 0 on each of 81 arcs | | 0 on all 81 | 0 on all 81 | nonzero on 30 (8 of 9 on 10 arcs, 4 of 9 on 20) | 4 on one, 3 on 8, at most 2 on 72 |

The scan runs the 81 weight vectors with orders 1 to 3 for k + 9, w, rho and sig. Every one of them has its limit in
V(P1), 30 have it outside V(P2), and exactly one, (1, 2, 1, 1), has rank 4; the two primes give the same scan. The
neighbor case shows that the same weights at k0 = -8 stay in V(P2) with rank 2, so the family is tied to the point k0
= -9, and the mutated cases show that K2 separates arcs on the slice from arcs beside it.

## Deduction

1. Each arc is Phi of an arc through a point of l, so it lies on V(J) and passes through the origin.
2. The coefficients of G below order nu vanish identically in the parameters and the coefficient F of s^nu is a
   nonzero polynomial vector, so F is the limit vector on a dense open set and lies in the affine cone over E0.
3. The closure of the image of F is an irreducible cone of dimension at least 4, the rank of [dF, F] at a point.
4. The generic family lies in V(P2) and the special family in V(P1); both primes have dimension 4, so each family is
   dense in its component.
5. E0 lies in V_+(K2) and contains both components, so E0 = V_+(K2); L lies in I(E0) = K2 and contains K2.

## What the earlier searches missed

The arc report of the normalization (`../working/build/arc/arc-report.md`) and the samples of
[../kernel-limits](../kernel-limits/README.md) (finite e0 in six values; e tending to 0 or infinity,
`vb-pole-arcs-result.json`) all had limits in the degree-4 component, because the degree-3 component is the fiber of
the second blowup over one point of l: it needs arcs through k0 = -9 with w of order 2 against order 1 for the other
three parameters. The points k0^2 = -3 of l, where the w^2 coefficients vanish and which the arc report named as an
unexamined stratum, give limits in V(P2) only (probe at 32029, where -3 is a square; not retained).

Scope: both primes; no statement in characteristic 0; the kernel-plane limits along the special family are not
computed (A5-276 covers arcs through a VB point with finite e0).

Check without Singular: [arc_rank_check.py](../arc_rank_check.py) recomputes the ranks of [dF, F] at the same parameter points by
dual-number power series in Python, with the arc rewritten from its formula, and reproduces every rank, the order
of G and the vanishing of J; it shares no code with Singular and shares the series arithmetic and polynomial
evaluator of `kernel-limits/plucker_limits.py` ([arc-rank-check.json](../arc-rank-check.json)).
