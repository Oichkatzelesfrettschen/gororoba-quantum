# Arcs through the base locus of the point blowup: Iso -> N- and the degree-30 component of W8 -> N-

Result. At p = 32009 and p = 32029 an explicit arc family on the slice V(J) of Iso -> N- has limit vectors that
sweep a cone of dimension 5 inside V(K2), and an explicit arc family on the slice of W8 -> N- has limit vectors that
sweep a cone of dimension 6 inside V(K2) and outside the degree-20 component C20. V(K2) of Iso is irreducible of
dimension 5 (ledger A5-058 to A5-060), so the Iso arcs are dense in it and E0 = V_+(K2); the part of V(K2) of W8
outside C20 is the degree-30 component C30, irreducible of dimension 6 (`../../w8-kp/README.md`), so the W8 arcs are
dense in C30. Both statements were known from the fiber cones of the pullback ideal on the point blowup
([../iso-planes/](../iso-planes/README.md), [../../c30-bounded/](../../c30-bounded/README.md)); the arcs here need no
fiber-cone argument: a limit vector of an arc through the origin of V(J) lies in the affine cone over E0
([../README.md](../README.md), first paragraph). They hold over F_32009 and F_32029 only.

## The family

Both slices carry the split quadric t2^2 + P Q - R T with P = t4 - t6, Q = t4 + t6, R = t5 - t7, T = t5 + t7, and
every generator of I vanishes on L0 = {t2 = 0, P = 0, R = 0} (W8: and t9 = 0). The arc searches of
[../README.md](../README.md) reached rank 4 on these targets because their arcs met L0 in a generic direction or
tangentially with a monomial contact. In the chart of the point blowup where the remaining coordinate is s (t3 on
Iso, t1 on W8) and t_k = s u_k, the arcs here start at a point (b, c) of P(L0) (Q = 2 b, T = 2 c) and leave it along
one first-order direction:

    u2 = V s,  P = c V s + B s^2,  R = b V s + A s^2.

With P = kP s and R = kR s free, the coefficient of s^3 in every G_j lies in the span of kP - c V and kR - b V
(read from a factorization of those coefficients with b, c, V, kP, kR symbolic), so (u2, P, R) = V (1, c, b) is the
transversal direction on which the common linear parts of the generators of the pullback ideal vanish. On it G has
order 4 and the limit mixes the second-order parameters with V^2, which is the plane of
[../iso-planes/](../iso-planes/README.md) (Iso) and the 3-space of [../../c30-bounded/](../../c30-bounded/README.md)
(W8) at the point (b, c).

- Iso: J = t2^2 + P Q - R T = 0 forces B = (2 c A - V^2) / (2 b). The substitution V -> b V, A -> b A clears the
  denominator, so the arc is polynomial with parameters (b, c, V, A): t3 = s, t2 = b V s^2, Q = 2 b s, T = 2 c s,
  R = b^2 V s^2 + b A s^3, P = b c V s^2 + (c A - b V^2 / 2) s^3. Its coefficients are rational, so it is a real arc.
- W8: J = g(t1, t9) - t2^2 - P Q + R T with g = t1^2 t9^2 - 2 t1^2 t9 + 2 t1 t9^2 - 4 t1 t9 determines u9 = t9 / s as
  the unique power series solution of 4 u9 = -u2^2 - P Q + R T - 2 s u9 + 2 s u9^2 + s^2 u9^2 (the right side
  contracts in the s-adic topology), computed by fixed-point iteration through order 8. The parameters are
  (b, c, V, A, B), and the series has rational coefficients. The limit vector is the coefficient of s^4 of G, which
  depends on the arc through its jet of order 3 only, so the truncation does not enter it.

## Computation

`blowup_arcs.py` writes one Singular script per fiber, prime and control (`--check` requires every file to match);
each runs from the repository root as `Singular -q --no-warn < CASE.sing > CASE.log`, in the global ordering `dp`,
with the parameters as ring variables. Singular 4.4.1 on the build host; the largest case took 4.6 s and 194 MB
(`*.time`). The K2 files and the generator signs eps are those of `../arcs_scan.py`.

| Case | J on the arc | order of G, lower coefficients | K2 quadrics nonzero on the limit | C20 tests on the limit | rank of [dF, F] at two points |
|---|---|---|---|---|---|
| `iso-blowup-arcs-p32009` | 0 identically | 4, all zero identically | 0 of 68 | | 5, 5 |
| `iso-blowup-arcs-p32029` | 0 identically | 4, all zero identically | 0 of 68 | | 5, 5 |
| `w8-blowup-arcs-p32009` | 0 through order 9 | 4, all zero identically | 0 of 144 | P: 23 of 48 nonzero; Lam: 9 of 9 nonzero | 6, 6 |
| `w8-blowup-arcs-p32029` | 0 through order 9 | 4, all zero identically | 0 of 144 | Lam: 9 of 9 nonzero | 6, 6 |
| `iso-blowup-arcs-pP-mutated` | nonzero | 4 | 41 (32009), 44 (32029) of 68 | | 5, 5 |
| `w8-blowup-arcs-pP-mutated` | nonzero | 4 | 45 (32009), 81 (32029) of 144 | 9 of 9 | 6, 6 |

The mutated arc drops the V^2 term of the quadric, so it leaves V(J), and K2 stops vanishing on its leading vector:
the K2 test discriminates arcs on the slice from arcs beside it. The two rank points are (b, c, V, A, B) =
(2, 3, 5, 7, 11) and (13, 4, 9, 6, 17), hand chosen, since a rank at any point bounds the generic rank from below.

## Deduction

1. Each arc lies on V(J) (Iso: a polynomial identity; W8: the power series solution exists and is unique by the
   contraction above) and passes through the origin.
2. The coefficients of s^0 to s^3 of every G_j vanish identically in the parameters and the coefficient F of s^4 is
   a nonzero polynomial vector, so for parameters in a dense open set F is the limit vector and lies in the affine
   cone over E0.
3. The closure of the image of F is an irreducible cone whose dimension is at least the rank of [dF, F] at a point:
   5 on Iso, 6 on W8.
4. Iso: the cone lies in V(K2), irreducible of dimension 5, so it is V(K2), and E0 = V_+(K2). With K2 radical and
   k[y]/K2 Cohen-Macaulay of positive dimension (A5-058, A5-059), L = K2 and F(I) = k[y]/K2 in every degree, as in
   step 7 of [../iso-planes/](../iso-planes/README.md).
5. W8: the nine linear forms Lam, which vanish on C20, are nonzero on F, so the cone is not contained in C20; it
   lies in V(K2) = C20 cup C30 and is irreducible of dimension 6, so it is C30. With the C20 arcs of
   [../README.md](../README.md), E0 = V_+(K2), which is ledger row A5-066 by a second route.

The Python series engine of [../../../kernel-limits/](../../../kernel-limits/README.md) evaluates the same arcs with
separate code: the header's J vanishes on them through order 31 and G has order 4 on all of them.

Scope: both primes, no statement in characteristic 0. The K2 counts (68 for Iso, 144 for W8) are the `RESULT K2
generators` lines of the logs.

Independent check: [arc_rank_check.py](../../../arc_rank_check.py) recomputes the ranks of [dF, F] at the same parameter points by
dual-number power series in Python, with the arc rewritten from its formula, and reproduces every rank, the order
of G and the vanishing of J ([arc-rank-check.json](../../../arc-rank-check.json)).
