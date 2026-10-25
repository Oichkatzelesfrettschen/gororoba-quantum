# A_5 Stiefel inclusion and gap-witness germs from the Pfaffian factorization

`result.json` is the output of
[`scripts/a5_stiefel_pfaffian_germs.py`](../../../scripts/a5_stiefel_pfaffian_germs.py) `--out`.
It carries two registry statements, each proved in writing below. The first is that every
nonzero A_5 Stiefel element is a zero divisor (`a5-stiefel-universal`). The second is that
the tangent bound is the local dimension at the twelve gap witnesses
(`a5-nonzero-divisor-two-dimension-gap`). Every decision rests on an exact computation over
Z, Z[i] or Q(i) from `gororoba_quantum/cd_core.py`; no floating-point value and no random
draw enters. Gate core-690 regenerates `result.json` with `--check`, and gate core-691 runs
`--self-test` in normal and `-O` modes.

## Conventions

The product is the cd_core doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), with
e_p e_q = cd_sign(dim, p, q) e_(p XOR q). An element y = (p, q) of A_5 with p, q in A_4 is
doubly pure when y_0 = y_16 = 0. For such a y put z = p + i q in C^15, z_k = y_k + i
y_(16+k) (k = 1..15), where i is a scalar unit that commutes with the algebra. Write u =
z_1..z_7, mu = z_8 and v = z_9..z_15. Every product of two vectors below is complex
bilinear, with no conjugation:

- U = u.u, V = v.v, W = u.v;
- Q = z.z = U + mu^2 + V;
- Delta = U V - W^2 and G = Q^2 - 4 Delta.

C_z is the 15 x 15 Im-block of left multiplication by z on Im (A_4)_C. Its entry (a, b) is
the e_a coefficient of z e_b, which is cd_sign(16, a XOR b, b) z_(a XOR b) for a != b.
A(z, t) = [[0, -t^T], [t, C_z]] is 16 x 16. R_k = {y : rank L_y <= 32 - k} is the closed
rank cone and S_k = {rank L_y = 32 - k} the exact stratum. D_(5,k) is the unit section of
S_k ([local-dimension record](../rank_locus_local_dimension/README.md)).

## Finite computations

Each item is an exact check in the record. Each states what it establishes.

1. **Cofactor identity** (`factorization`). Over Z[z]:
   - C_z is skew and C_z z = 0;
   - for j = 1..15 the signed maximal Pfaffian P_j = (-1)^(j-1) Pf(C_z with row and column
     j removed) equals Q G z_j, coefficient by coefficient (995 terms each);
   - over Z[z, t], Pf A(z, t) = -(z.t) Q G.

   The Pfaffians come from memoized expansion along the first index. The routine is checked
   against Pf^2 = det (flint) on integer skew matrices of orders 2 to 10.
2. **Transport** (`transport`). On all 30 imaginary basis elements y and all 32 basis
   vectors x, the map phi(r, s) = r + i conj(s) satisfies phi(y x) = A(z, conj z)
   conj(phi(x)). Here conj(s) is the Cayley-Dickson conjugate, and the outer conj acts
   coefficientwise. Both sides are real-linear in y and in x, so the identity holds on the
   whole doubly pure space. phi is a real-linear bijection R^32 -> C^16, so rank_R L_y = 2
   rank_C A(z, conj z).
3. **Square-zero cross-check** (`square_zero_route`). Over Z[z], z (z x) = -Q x for the eight
   vectors x in {(h, 0), (0, h) : h = 1, u, v, uv}, where uv is the octonion product. At u =
   e_1, v = 2e_1 + 2e_2, mu = 3i, where Q = 0, the eight vectors have complex rank 8.
4. **Derivations** (`derivations`). The derivations of the cd_core octonions form a
   14-dimensional space, solved exactly. Each, acting as D (+) D on both octonion halves of
   A_4, is a skew derivation of the sedenion table on all 256 basis pairs, and it kills e_0
   and e_8.
5. **Witness rows** (`witnesses`). These are the twelve rows of the
   [local-dimension record](../rank_locus_local_dimension/README.md) whose family has a
   non-zero-divisor entry: witnesses 1, 8 and 15 (nonzd-axis); 4, 11 and 18
   (zd-nonzd-locus); 5, 12 and 19 (zd-nonzd-generic); 6, 13 and 20 (nonzd-nonzd-locus).
   The script regenerates them and requires them to equal the retained coordinates. At each
   it computes, by exact integer kernels:
   - the nullity;
   - the rank of the Schur differential h -> N_l^T L_h N_r, giving the cone dimension of
     T(x);
   - whether e_8 and e_24 lie in T(x);
   - dim T(x) cap H_5^perp, where H_5 = span{e_0, e_8, e_16, e_24}.

   It also records the family-specific data that the proofs below cite.
6. **Controls** (`controls`). These are structured points with no random draw.
   - e_1 and e_1 + e_2 + e_18 have Q G != 0 and nullity 0.
   - e_1 + e_18 has Q = 0 and nullity 12.
   - Moreno's e_1 + e_10 + 2 e_24 has G = 0, Q = -2 and nullity 4.
   - In the incidence pair e_1 + e_10 + e_25 + e_27 (nullity 8) and e_1 + e_10 + e_25 + e_28
     (nullity 4), both points have Q = G = 0. The curve test of the nullity-8 proof passes at
     the first and fails at the second.

The self-test breaks each identity:
- a flipped e_3 e_12 structure constant leaves C_z non-skew;
- a skew sign flip of one C_z entry pair breaks the cofactor and bordered identities;
- no cofactor equals G z_j or Q z_j, so both factors are needed;
- transport without conj(s) fails;
- z (z e_m) = -Q e_m fails on 14 of the 16 basis vectors;
- the G.I9 nullity-4 point fails the curve test.

It also rejects eight corrupted witness rows.

## Theorem 1: every nonzero A_5 Stiefel element is a zero divisor

Let y = (a, b) with a, b pure in A_4, <a, b> = 0 and |a| = |b|, y != 0.

*Proof.* y is doubly pure, and z = a + i b has Q(z) = |a|^2 - |b|^2 + 2i<a, b> = 0. By item
1, Pf A(z, conj z) = -(z.conj z) Q(z) G(z) = 0. Then det A = (Pf A)^2 = 0. The rank of a
skew matrix is even, so rank_C A <= 14. Item 2 gives rank_R L_y <= 28, so L_y has a kernel
of dimension at least 4. A nonzero x with y x = 0 makes y a zero divisor. QED.

The proof uses no density or genericity step. It covers every Stiefel point, including
those where u and v are dependent or isotropic. By `a5-stiefel-pfaffian-reduction`,
|det L_(a,b)| = |Pf(L_a + i R_b)|^4. Theorem 1 therefore says Pf(L_a + i R_b) vanishes on
the whole Stiefel set, which is the condition the registry boundary of
`a5-stiefel-universal` names. The same identity gives det_R L_y = |Pf A|^4 = N^4 |Q G|^4
with N = z.conj z for every doubly pure y. A doubly pure y is therefore a zero divisor
exactly when Q(z) G(z) = 0.

**Independent cross-check (item 3).** This route does not use item 1.
- For pure z with Q(z) = 0, left multiplication L_z on (A_4)_C squares to zero on the span
  X(z) of the eight vectors. So L_z X(z) lies in ker L_z, and dim ker L_z >= 4 wherever X(z)
  has rank 8.
- That set is Zariski open in the quadric Q = 0. It is nonempty by the exact point of item
  3, and Q = 0 is irreducible, since a quadratic form of rank 15 is not a product of linear
  forms. So the set is dense, and the 13 x 13 minors of L_z vanish on the whole quadric.
- ker L_z cap Im (A_4)_C lies in ker C_z and has dimension at least 3. So rank C_z <= 12 and
  rank A(z, t) <= 14 for every t.

The route is a computational form of the companion's alternativity argument (its Theorem
G10) and reaches the same bound.

## Theorem 2: the tangent bound is the local dimension at the twelve gap witnesses

At each witness x of the four families below, the germ of R_k at x is a smooth manifold P
of cone dimension dim T(x). Hence S_k = R_k = P near x. D_(5,k) has local dimension dim
T(x) - 1, which is the unit tangent bound and two above the family. T(x) is the direct sum
of the family tangent and span{e_8, e_24}.

**Sandwich lemma.** Let x have nullity k and choose a nonzero (32 - k)-pivot block of L_x.
Near x, rank L_y = 32 - k + rank S(y), where S is the Schur complement, so R_k = {S = 0}.
The differential of S at x is h -> N_l^T L_h N_r for the kernel bases fixed by the pivot.
Another choice of bases changes it by invertible maps. If this map has rank c, then c
entries of S with independent differentials cut out a smooth manifold M of dimension 32 - c
= dim T(x), and R_k lies in M near x. Suppose a smooth manifold P of dimension dim T(x)
passes through x inside R_k. Then the inclusion P -> M is a local diffeomorphism, so P = R_k
= M as germs. The pivot persists near x, so rank L_y >= 32 - k there and S_k = R_k near x.
The cone is transverse to the sphere at x != 0, which subtracts one dimension.

**The four pieces.** Item 5 holds at every witness:
- the recorded nullity equals the family's;
- e_8 and e_24 lie in T(x);
- dim T(x) cap H_5^perp = dim T(x) - 2;
- dim T(x) - 1 = family dimension + 2.

| Family | Witnesses | k | Piece P through x | dim T(x) (cone) | P in R_k by |
| --- | --- | --- | --- | --- | --- |
| nonzd-axis | 1, 8, 15 | 12 | quadric cone V | 16 | `a5-nullity12-quadric-germ` (established) |
| zd-nonzd-locus | 4, 11, 18 | 8 | orbit image below | 22 | curve identity plus automorphism invariance |
| zd-nonzd-generic | 5, 12, 19 | 4 | {y_0 = y_16 = 0, G(z) = 0} | 28 | Theorem 1's identity: G = 0 gives Pf A = 0 |
| nonzd-nonzd-locus | 6, 13, 20 | 4 | Stiefel cone {y_0 = y_16 = 0, Q(z) = 0} | 28 | Theorem 1 |

- *Nullity 4.* At witnesses 6, 13 and 20, Q(z) = 0, and at 5, 12 and 19, G(z) = 0, all
  exactly. Q is nonzero at 5, 12 and 19. The real Jacobian of y_0, y_16, Re F and Im F has
  exact rank 4 at x, for F = Q or G. So P is a smooth 28-manifold near x, and P lies in R_4
  because Pf A(z, conj z) = -N Q G vanishes on it.
- *Nullity 12.* Witnesses 1, 8 and 15 are e_1 + e_25, e_2 + e_26 and e_3 + e_27, which lie
  on V. The established claim proves V = R_12 there. The record repeats the tangent
  dimension 16 and the e_8 and e_24 memberships.
- *Nullity 8.* Let x be a zd-nonzd-locus witness, z its coordinates, lambda = u.v / U and n
  = v - lambda u. The record finds U != 0, mu = 0 and lambda = -i. It also finds n
  isotropic, orthogonal to u and an eigenvector of the octonion cross product of u with
  eigenvalue rho, where rho^2 = -U and rho is in Q(i). The proof uses only U != 0 and mu =
  0. Define the polynomial curve

  z(k) = ((1 + U k^2) u, -2 lambda U k, lambda (1 - U k^2) u + (1 + U k^2) n),

  with z(0) = z. It is the conic mu^2 + (1 + lambda^2) U = 0 through x, scaled to clear
  denominators.
  - *z(k) lies in R_8 for every complex k.* Each order-12 principal Pfaffian of C_(z(k)) is
    a polynomial in k of degree at most 12, since z(k) has degree 2. rank C_(z(k)) = 10 at
    the 13 integers k = 0..12 makes all of them vanish there, hence identically. For a skew
    matrix, vanishing of every order-12 principal Pfaffian is rank <= 10, since a nonzero
    Pfaffian of order 14 expands into order-12 ones. Bordering adds at most 2 to the rank,
    so rank_C A(z(k), conj z(k)) <= 12, and item 2 gives nullity L_y >= 8.
  - *The orbit stays in R_8.* For X in C^14, D_X is a complex combination of the item-4
    derivations. g = exp(D_X) is an automorphism of (A_4)_C, by the Leibniz rule. It fixes
    1 and maps Im (A_4)_C to itself, so C_(g w) = g C_w g^(-1). Scalars s give C_(s w) = s
    C_w. So Psi(X, s, k) = s exp(D_X) z(k) has rank C <= 10 and lies in R_8.
  - *Dimension.* At (0, 1, 0) the complex differential of Psi spans {D_i z} together with z
    and z'(0) = -2 lambda U e_mu, of complex rank 11 (exact). The real differential
    therefore has rank 22 at the base point, and rank at least 22 nearby. The image lies in
    R_8 near x, which lies in the 22-dimensional Schur manifold M, so the rank is at most
    22. By the constant-rank theorem the image of a small neighborhood is an embedded
    22-manifold P in R_8 through x, and the sandwich lemma applies.

  The pieces sit in R_8, so this route needs neither G2(C) transitivity nor the SL_3
  stabilizer.

**The e_8, e_24 clause.** T(x) is the tangent space of the germ. It contains e_8 and e_24,
and T(x) cap H_5^perp has dimension dim T(x) - 2. The family lies in S_k cap H_5^perp, so
its tangent space lies in T(x) cap H_5^perp. That space has the family's cone dimension, so
the two coincide, and T(x) = T_family (+) span{e_8, e_24}.

## Imported results

- `a5-nullity12-quadric-germ` (established, gate core-677) for witnesses 1, 8 and 15.
- The family dimensions 13, 19, 25 and 25 of the local-dimension record. They come from
  Theorem 1.5 of math/0702075 and Theorem 15.7 of math/0511691. They enter only the clause
  "two above the family" and the identification of the H_5^perp part of T(x).
- Standard facts:
  - the principal-minor theorem for skew matrices;
  - Pf^2 = det;
  - the Leibniz rule for exp of a derivation;
  - the implicit-function and constant-rank theorems;
  - irreducibility of a nondegenerate quadric, for the cross-check only.

## Falsifiers and scope

Any of the following refutes the argument where it occurs:
- a cofactor coefficient off Q G z_j;
- a transport mismatch on a basis pair;
- a witness off its piece, or a Jacobian rank other than 4;
- a curve point with rank C_z above 10;
- an orbit rank below 11;
- e_8 or e_24 outside T(x);
- a nullity other than the family's.

None occurred. Theorem 1 is universal over the Stiefel set. Theorem 2 is a statement about
local germs at the twelve recorded witnesses only. It does not cover:
- a covering of D_(5,4), D_(5,8) or D_(5,12);
- smoothness elsewhere on the families;
- the Proposition 8.2 and Moreno points outside H_5^perp (Proposition 8.2's are in
  `a5-nullity12-quadric-germ`);
- the U = 0 or n = 0 parts of the incidence equations.

Neither result is formalized in Rocq.

## Relation to the companion and the earlier review

The arguments revise chapters 02 and 03 of the DAS MERGUS companion.
- Theorem G12, the identity P_j = Q G z_j, is recomputed here by independent code.
- G10 appears as the item-3 cross-check.
- G11 and G13's germ step correspond to the nullity-4 rows.
- G16's nullity-8 inclusion is replaced. The companion moves (u, n) to a canonical form by
  G2(C) and SL_3 transitivity and certifies 455 Pfaffians there. This bundle proves
  inclusion only for the orbit of a curve through each witness, which removes both
  transitivity imports. G16's universal statement, that every point of the incidence
  equations with U != 0 lies in R_8, is neither checked nor established here.

The [earlier review](../../archive/reviews/2026-10-25-das-mergus-algebra-review.md)
supported Theorem 1 by randomized identity tests and left the nullity-8 inclusion resting
on imported transitivity. The present computations replace both with exact identities.

## Replay

```sh
"$PYTHON" -B -W error scripts/a5_stiefel_pfaffian_germs.py --check docs/evidence/a5-stiefel-pfaffian-germs/result.json
"$PYTHON" -B -W error scripts/a5_stiefel_pfaffian_germs.py --self-test && "$PYTHON" -B -W error -O scripts/a5_stiefel_pfaffian_germs.py --self-test
```

The check recomputes everything and compares the record, minus its `versions` field. It
measured 1.9 s on 12 CPUs (3.7 s on a cold start) and 1.7 s serially
(`GOROROBA_WORKERS=1`), with python-flint 0.9.0 on Python 3.14.7. The self-test measured
1.2 s in normal mode and 1.4 s under `-O`.
