# Rank strata of the A_5 zero-divisor set: components, dimensions, incidences and connected components

`result.json` is the output of [`scripts/a5_zero_divisor_strata.py`](../../../scripts/a5_zero_divisor_strata.py) `--out`
and `explore.json` the output of its `--explore` mode. The record classifies the nullity strata of A_5 (dimension 32) as
algebraic sets and settles roadmap item 3 of
[the global classification](../../notes/rank_locus_two_dimension_gap.md#route-to-the-global-classification-roadmap-items-3-8)
for the components and connected components of D_(5,4), D_(5,8), D_(5,12) and D_(5,16). It establishes eight
statements and leaves roadmap items 4 to 8 open:

1. every zero divisor of A_5 is doubly pure, y_0 = y_16 = 0 (established);
2. for doubly pure y != 0, nullity L_y = 28 - 2 rank C_z, so nullity 4, 8, 12, 16 means rank C_z = 12, 10, 8, 6
   (established);
3. the zero-divisor set is V(Q) u V(G) in C^15, two absolutely irreducible hypersurfaces of complex dimension 14
   (unit dimension 27) with connected unit sections (established);
4. C_z satisfies C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0 and has characteristic polynomial
   l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2 (established);
5. every pair (u, v) of C^7 lies in a G_2-translate of one of six slice families of at most five parameters, and on each
   slice the Pfaffian ideals of orders 12, 10, 8 have exact varieties (established);
6. R_16 = N_+ u N_-, R_12 = V u B9 and R_8 = W8 u E8-bar, with the irreducible pieces of the table below (established);
7. the incidences V < E8-bar, B9 < W8, B9 < E8-bar, N_+, N_- < V n B9 and the memberships in V(Q) and V(G) hold
   (established);
8. D_(5,4) is connected, D_(5,8) has two connected components, D_(5,12) is connected and D_(5,16) has two connected
   components (established);
9. smoothness and singular loci of the pieces, normal links, kernel bundles, attachments and homology (open).

Every decision rests on an exact computation over Z or Q: integer matrices and ranks, polynomial identities over Z[z],
Groebner bases over Q (python-flint Buchberger with `is_groebner` re-verified), or a sympy identity over Z[x, a, s, m].
No random draw enters; every point is an explicit integer vector. Gate `--check` recomputes `result.json` and
`--self-test` runs the mutation controls in normal and `-O` modes.

## Conventions

The product is the cd_core doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), e_p e_q = cd_sign(dim, p, q)
e_(p XOR q). An element y = (p, q) of A_5 with p, q in A_4 is doubly pure when y_0 = y_16 = 0. Put z = p + i q in C^15,
z_k = y_k + i y_(16+k) for k = 1..15, with i a scalar unit and every product of vectors complex bilinear. Write
u = z_1..z_7, mu = z_8 and v = z_9..z_15; U = u.u, V = v.v, W = u.v; Q = U + mu^2 + V = z.z; Delta = U V - W^2;
G = Q^2 - 4 Delta. C_z is the 15 x 15 Im-block of left multiplication by z on Im (A_4)_C, with entry (a, b) equal to
cd_sign(16, a XOR b, b) z_(a XOR b). R_k = {y : rank L_y <= 32 - k} is the closed rank cone, S_k = R_k minus R_(k+4) the
stratum of nullity exactly k, and D_(5,k) its unit section. The coordinate mu = z_8 is the pair (y_8, y_24), so
H_5^perp = {y_0 = y_8 = y_16 = y_24 = 0} is the locus of doubly pure y with mu = 0.

**Split coordinates.** The scaling e'_k = i^popcount(k) e_k changes the cd_core table to split(p, q) =
(-1)^popcount(p AND q) cd_sign(16, p, q), a table of +-1 over Q, and z'_k = i^(-popcount(k)) z_k. The matrix eta C'
with entry (a, b) equal to eps_a split(k, b) z'_k, k = a XOR b, eps_a = (-1)^popcount(a), is skew and equals D C_z D with
D = diag(i^popcount). It has the same rank and, on principal submatrices, the same Pfaffians up to the units
i^(sum of popcount). All rank and Pfaffian questions about C_z are therefore questions about a skew matrix with entries
linear in z' over Z. Block 1..7 (u'), coordinate 8 (mu') and block 9..15 (v') carry the 14 derivations of the split
table, the Lie algebra of G_2(C): each derivation fixes e'_0 and e'_8 and acts on u' and v' by the same 7 x 7 matrix
(`derivation_data`). The 7-dimensional module has the invariant form eta = diag(-, -, +, -, +, +, -) on e'_1..e'_7 and
the cross product x ^ y = Im(x y) of the split octonions. In split coordinates

- Q = eta(u') - mu'^2 - eta(v'), Delta = eta(u', v')^2 - eta(u') eta(v'), G = Q^2 - 4 Delta;
- the original blocks, read as module vectors, are u' and i v', and mu = i mu'.

**Pieces.** All are cones in C^15 stable under G_2 and C^*:

| Piece | Equations in split coordinates | Original coordinates |
| --- | --- | --- |
| N_+, N_- | mu' = 0, v' = +-u', eta(u') = 0 | mu = 0, v = +-i u, u.u = 0 |
| W8 | mu' = 0, eta(u') + eta(v') = 0, eta(u', v') = 0 | mu = 0, U = V, W = 0 |
| V | u' ^ v' = 0 (rank at most 1), Q = 0 | the quadric cone of `a5-nullity12-quadric-germ` |
| B9 | mu' = 0, eta(u') = eta(v') = eta(u', v') = 0, u' x v' = 0 | pairs in special isotropic planes |
| E8 | the G_2-orbit family of {u' = a n + b e, v' = c n + d e, mu' = m, Q = 0}, e = e'_1, n = e'_2 + e'_3 | none |

E8-bar is the Zariski closure of E8. W8 is N x N in the variables u' + v' and u' - v', both null for eta. The unit
sections of N_+ and N_- are V_2(R^7), since v = +-i u with u null means u = a + i b with a, b orthogonal of equal norm.

## Finite computations

Each item is an exact check in the record and states what it establishes.

1. **Operator identities** (`doubly_pure`). With J = L_(e_16): J^2 = -I, all 30 matrices L_(e_k), k not 0, are skew, and
   J anticommutes with L_(e_k) for the 30 indices k not in {0, 16}. Flipping one entry of J breaks them.
2. **Split algebra** (`split_algebra`, `split_factorization`). On every basis pair eta C' is skew and eta C' = D C_z D.
   Over Z[z'] the 15 cofactors P_j = (-1)^j Pf(eta C' without j) equal Q G z'_j coefficient by coefficient (995
   terms each), with Q and G of 15 and 141 terms. A flipped constant breaks skewness.
3. **Nullity identity** (`nullity_identity`). At 14 integer points of all strata (the representatives below) the nullity
   of the 32 x 32 integer matrix L_y equals 28 - 2 rank C_z; with offset 26 it fails.
4. **Characteristic identities** (`characteristic_identities`, `orbit_facts`). On the slice
   z' = (x e'_1, m, a e'_1 + s e'_2) the relation C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0 and the characteristic polynomial
   l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2 hold over Z[x, a, s, m]. For all 14 derivations D and the 15 basis vectors z,
   [D, C'_z] = C'_(D z), where C' = split(k, b) z'_k. The differential of (g, x, a, s, m) -> g z' has rank 15 at an
   exact slice point.
5. **Quadric certificate** (`quadric_certificate`). With M(e) = [D_1 e, .., D_14 e], the identity
   M(e) W M(e)^T = eta(e) eta^-1 + beta e e^T has a unique exact solution (W, beta = -1) over Z[e], 784 coefficient
   equations in 197 unknowns. A wrong form has none.
6. **Stabilizer of e'_1** (`sl3_data`). It has dimension 8, commutes with e'_1 x -, and acts on the eigenspaces V_+ and
   V_- (dimension 3, totally null for eta, paired nondegenerately) with image of rank 8 and trace 0 on each: sl_3 on
   V_+ and its dual on V_-.
7. **Null vectors** (`null_orbits`). The three SL_3-types of null vectors of e'_1^perp (in V_+, in V_-, mixed) and
   e'_1 + e'_3 have G_2-orbits of dimension 6.
8. **Isotropic planes** (`isotropic_plane_certificate`). The stabilizer H of n = e'_1 + e'_3 has dimension 8. The 917
   distinct 5 x 5 minors of [h_1 x, .., h_8 x, n, x], with eta(x) = 0, have a Groebner basis (300 minors suffice) in
   which the three linear forms x_2, x_5 - x_7, x_4 - x_6 have radical power 4. These forms cut out
   L = ker(x -> n x x). H leaves L invariant and its traceless action on L has rank 3, all of sl_2.
9. **Plane table** (`plane_table`). Stabilizer dimension, induced rank in gl_2 and ordered-pair orbit dimension of the six
   slice planes: P2 (4, 1, 11), P3a and P3b (7, 2, 9), P3c (5, 2, 11), P4s (9, 4, 9), P4g (7, 4, 11).
10. **Slice certificates** (`slice_certificate`). For the six slices P2, P3a, P3b, P3c, P4s, P4g (below) and the orders
    12, 10, 8 the Pfaffian ideal I has the exact variety recorded in `LEVEL_PIECES`:
    - (i) every principal Pfaffian lies in the ideal of each piece the variety contains;
    - (ii) every product of one generator from each named piece has a power of at most 6 in the ideal of the first
      `prefix` Pfaffians (prefix 8 to 512 of 59 to 2966 generators);
    - the containment table lists, for every piece, whether I lies in its ideal on all six slices. W8, E8, V, B9, N_+,
      N_- lie in R at the orders where they occur and W8, E8 do not at order 10 and W8, V, B9 do not at order 8.
11. **Representatives** (`representative`). At 14 exact integer points: rank C_z, nullity, the dimension of the Zariski
    tangent space of each Pfaffian scheme that contains the point (Jacobian rank from numeric sub-Pfaffians) and the
    rank of the derivations, scaling and family tangent vectors. They pin every piece:

    | Point | Piece | rank C | nullity | tangent dimension | orbit-family rank |
    | --- | --- | --- | --- | --- | --- |
    | u' = e'_1, v' = e'_3 | W8, hyperbolic plane | 10 | 8 | 12 (order 12) | 12 |
    | u' = n, v' = e'_2 + e'_5 | W8, generic isotropic plane | 10 | 8 | 12 (order 12) | 11 |
    | (a, b, c, d, m) = (1, 3, 2, 5, 4) in P3a | E8 | 10 | 8 | 11 (order 12) | 11 |
    | (a, b, c, d) = (1, 2, 3, 5) in P4s | B9 | 8 | 12 | 9 (order 10) | 9 |
    | u' = 3 e'_1, v' = 5 e'_1, mu' = 4 | V | 8 | 12 | 8 (order 10) | 8 |
    | u' = v' = n | N_+ | 6 | 16 | 6 (order 8) | 6 |
    | u' = n, v' = -n | N_- | 6 | 16 | 6 (order 8) | 6 |
    | u' = n, v' = 2 n | V n B9 | 8 | 12 | 11 (order 10) | 7 |
    | u' = e'_1, v' = e'_1 | the {a, 0} family in V | 8 | 12 | 8 (order 10) | 7 |
    | V(G) and V(Q) points | hypersurface | 12 | 4 | 14 (order 14) | |
    | a point of V(Q) n V(G) | | 12 | 4 | | |

    Here n = e'_1 + e'_3. The V(G) point is u' = e'_1, mu' = 3, v' = 5 e'_1 + 3 e'_3, and the nullity-4 point of
    V(Q) n V(G) is in P3c: (a, b, c, d, m) = (1, 3, 0, 5, 4).
12. **Zero-divisor set** (`zero_divisor_set`). Q has Hessian of rank 15. G, as a polynomial of 141 terms in split
    coordinates, is irreducible over Q, is not divisible by Q, and has the smooth rational zero
    u' = e'_1, mu' = 3, v' = 5 e'_1 + 3 e'_3 with Q = 6 and gradient nonzero.
13. **Curve from E8 to B9** (`curve_to_b9`). The polynomial curve z(s) = (4 a n + 16 s e0 + 4 k, 12 s, 4 c n + 20 s e0 +
    5 k) with n = e'_1 + e'_3, k = e'_4 + e'_6, e0 = -e'_2: eta(e0) = -1, e0 perp n, k, e0 x n = n, n x k = 0, and n, k
    are null. All order-12 Pfaffians vanish identically in s while some order-10 Pfaffian does not; the nullity is 8 at
    s = 2 and 12 at s = 0.
14. **Piece identities** (`piece_identities`). Over Z[z']: Delta = -(sum over i < j of eta_i eta_j (u_i v_j - u_j v_i)^2)
    (Binet and Cauchy), G = Q^2 + 4 (eta(u') eta(v') - eta(u', v')^2), and G at mu' = 0 equals
    (eta(u') + eta(v'))^2 - 4 eta(u', v')^2.

The self-test breaks each part: a flipped split constant, a flipped entry of J, the offset 26, the P2 order-12 ideal with
the piece V dropped, with the piece W8 replaced by one without eta(u', v') = 0, and the ideal tested against (m)
alone, a wrong invariant form in the quadric certificate, the curve with e0 reversed, a corrupted tangent dimension and
a corrupted rank in a representative, and the pieces tested at the wrong representatives.

## Slice families

A slice is a plane of the module with an ordered basis (A, B) and the point u' = a A + b B, mu' = m,
v' = c A + d B, parameters (a, b, c, d, m):

| Slice | A | B | Gram form of the plane | Plane orbit dimension |
| --- | --- | --- | --- | --- |
| P2 | e'_1 | e'_2 | nondegenerate | 10 |
| P3a | e'_2 + e'_3 | e'_1 | rank 1, radical vector in V_+ of e'_1 | 7 |
| P3b | e'_2 - e'_3 | e'_1 | rank 1, radical vector in V_- | 7 |
| P3c | e'_2 + e'_3 + e'_4 - e'_5 | e'_1 | rank 1, radical vector in neither | 9 |
| P4s | e'_1 + e'_3 | e'_4 + e'_6 | zero, special (A x B = 0) | 5 |
| P4g | e'_1 + e'_3 | e'_2 + e'_5 | zero, generic (A x B != 0) | 7 |

The exact varieties of the Pfaffian ideals on the slices (item 10), with Delta' = 0 on every slice with Gram rank at most 1:

| Slice | order 12 (R_8) | order 10 (R_12) | order 8 (R_16) |
| --- | --- | --- | --- |
| P2 | W8 u V | V | N_+ u N_- |
| P3a, P3b | {Q = 0} (E8) | V | N_+ u N_- |
| P3c | V | V | N_+ u N_- |
| P4s | {mu' = 0} (W8) | {mu' = 0} (B9) | N_+ u N_- |
| P4g | {mu' = 0} (W8) | V = {mu' = 0, ad = bc} | N_+ u N_- |

## Theorem 1: every zero divisor of A_5 is doubly pure

Let y = y_0 e_0 + y_16 e_16 + d with d in the span of the other 30 basis elements. By item 1, L_y = y_0 I + y_16 J + L_d
with L_d skew, J skew, J^2 = -I and J L_d + L_d J = 0 (linear in d). Then
L_y^T L_y = (y_0 - y_16 J - L_d)(y_0 + y_16 J + L_d) = (y_0^2 + y_16^2) I - y_16 (J L_d + L_d J) - L_d^2
= (y_0^2 + y_16^2) I + L_d^T L_d. This matrix is positive definite when (y_0, y_16) != 0, so L_y is invertible and y is
not a zero divisor. QED. This is the content of Lemmas 9.4 and 9.5 of
[Biss, Dugger and Isaksen](../../notes/math-0511691.md) (every zero divisor is imaginary and orthogonal to C_n)
at n = 5, reproved here from the multiplication table.

## Theorem 2: nullity L_y = 28 - 2 rank C_z

Let y be doubly pure and nonzero. The transport of the
[A_5 Pfaffian record](../a5-stiefel-pfaffian-germs/README.md) (gate core-690) gives rank_R L_y = 2 rank_C A(z, conj z),
with A(z, t) = [[0, -t^T], [t, C_z]]. C_z is skew, and C_z z = 0 because z z = -(z.z) e_0 for pure z (the pure
elements of a Cayley-Dickson algebra satisfy p q + q p = -2 <p, q>), whose Im-part is zero.

*Lemma.* If C is a skew complex matrix with C z = 0 and t^T z != 0 then rank A(z, t) = rank C + 2. Proof: for a skew
matrix im C is the annihilator of ker C under the bilinear pairing, and z lies in ker C, so t lies outside im C and
rank [t C] = rank C + 1. The top row (0, -t^T) of A lies in the row space of [t C] only if C w = t has a solution, which
fails for the same reason; so rank A = rank C + 2.

With t = conj z, t^T z = |z|^2 > 0. Hence rank_R L_y = 2 rank C_z + 4 and nullity L_y = 32 - 2 rank C_z - 4. QED. Item 3
confirms it at 14 points, including the four nullities 4, 8, 12, 16. Since C_z is skew of odd order, rank C_z <= 14 and
nullity 0 occurs exactly when rank C_z = 14.

## Theorem 3: the zero-divisor set

By Theorems 1 and 2 a nonzero y is a zero divisor exactly when it is doubly pure and rank C_z <= 12. A skew matrix has
rank at most 12 exactly when its principal Pfaffians of order 14 vanish; they are the 15 cofactors P_j = Q G z_j
(item 2, equal to the cofactors of C_z up to units). So Z_5 minus 0 corresponds to {z != 0 : Q G = 0} = V(Q) u V(G).

- *Q is absolutely irreducible.* Its Hessian has rank 15, so Q is not a product of two linear forms.
- *G is absolutely irreducible.* G is irreducible over Q (item 12). It has a Q-rational zero P with nonzero gradient.
  Suppose G = prod H_j over the algebraic closure. Galois conjugation permutes the factors; at P only one factor
  vanishes (the gradient is nonzero), and its conjugates also vanish at P, so that factor is stable and defined over
  Q up to a scalar. Irreducibility over Q makes it G. The split coordinates differ from the original by an invertible
  linear map over Q(i), which preserves absolute irreducibility. The real zeros of G in the original coordinates are
  the points of W8 with all coordinates real, where G is singular, which is why the rational point is taken in split
  coordinates.
- *Dimension.* Both are hypersurfaces of C^15 = R^30: complex dimension 14, real cone dimension 28, unit dimension 27.
  Q does not divide G, so the two hypersurfaces differ.
- *Connectedness.* An irreducible complex cone minus the origin is connected, so each unit section is connected.

## Theorem 4: the characteristic polynomial

Item 4 verifies, on the slice, C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0 and the characteristic polynomial. Both sides of each
identity are invariant under z -> g z for g in the group generated by exp(D) (the equivariance of item 4 integrates, as
exp(D) is an automorphism), and the orbit-slice map has rank 15 at a point, so G_2 x slice is dense in C^15 and both
identities hold on all of C^15. The algebraic multiplicity of the eigenvalue 0 of C_z is therefore
1 + 6 [Q = 0] + 4 [G = 0] + 4 [Q = G = 0]: the quartic factor l^4 + 2 Q l^2 + G vanishes at l = 0 to order 2
when only G = 0 and to order 4 when Q = G = 0, and it enters squared, so the multiplicity is 15 on N_+ and N_-. The minimal polynomial has degree 7 at generic points; the rank strata are Jordan-type
strata of the eigenvalue 0 inside this fixed shape.

## Lemma 5: the slice covering

Every (u', v') in C^7 x C^7 is mapped by G_2(C) into one of the slices of the table above, so
R_k = G_2 . (R_k n slices) for k = 8, 12, 16.

*Facts used.* G_2 acts through the group generated by the 14 derivations; the dimension of an orbit is the rank of the
derivations on the point.
- (F1) Every G_2-orbit in a quadric {eta(e) = kappa}, kappa != 0, has dimension 6 by item 5: rank M(e) is at least
  the rank of eta(e) eta^-1 + beta e e^T, which is 6 or more where eta(e) != 0. These orbits are open, the quadric is
  irreducible, so there is one orbit.
- (F2) The stabilizer of e'_1 acts as SL_3 on V_+ and as the dual on V_- (item 6). Hence SL_3 is transitive on V_+
  minus 0, on pairs (x, xi) with xi(x) = c for fixed c != 0, and on pairs (x, xi) with xi(x) = 0, x != 0, xi != 0.
- (F3) The null cone minus 0 is irreducible of dimension 6. A null vector n lies in e^perp for a nonnull e, hence in one
  of three SL_3-types; each type has an open orbit (item 7), so G_2 is transitive on null vectors.
- (F4) The isotropic planes through n = e'_1 + e'_3 form the quadric Q^3 of x null in n^perp mod n. By item 8 the
  H-orbit of every plane outside P(L) has dimension 3 = dim Q^3, so it is open, and Q^3 minus P(L) is irreducible, so
  it is one orbit (P4g). H acts on L through sl_2, transitively on P(L) (P4s).

*Proof of the covering.* Let P = span(u', v') with the Gram form of eta.
- dim P = 0: the point (0, mu', 0) lies in every slice.
- Gram rank 2 on a plane: P has an orthonormal basis (p, q) with eta(p) = eta(q) = -1. F1 maps p to e'_1; then q has
  components (q_+, q_-) with eta(q_+, q_-) = -1/2, and F2 maps q to e'_2. So P goes to span(e'_1, e'_2): slice P2. A
  line P = span(p) with eta(p) != 0 goes to span(e'_1) inside P2.
- Gram rank 1 on a plane: P = span(n, e) with n spanning the radical and eta(e) = -1 after scaling. F1 maps e to
  e'_1. Then n is null in e'_1^perp, so n = n_+ + n_- with eta(n_+, n_-) = 0. F2 maps n to e'_2 + e'_3 (n_- = 0: P3a), to
  e'_2 - e'_3 (n_+ = 0: P3b) or to (e'_2 + e'_3) + (e'_4 - e'_5) (both nonzero: P3c).
- Gram rank 0 or a null line: P lies in an isotropic plane through a null vector n. F3 maps n to e'_1 + e'_3, and F4
  maps the plane to P4g or P4s. QED

## Theorem 6: the strata R_16, R_12, R_8

Piece equations are stable under G_2 and C^*, so Lemma 5 and item 10 give the exact equalities, level by level.
Containment (i) on every slice puts each piece inside R (the containment table); covering (ii) puts R inside the union.

*R_16 = N_+ u N_-.* On every slice the order-8 variety is N_+ u N_-. Each is the null cone of eta in C^7, irreducible of
complex dimension 6 (cone real dimension 12, unit dimension 11). They meet where u' = v' = -v', that is at 0, so
R_16 minus 0 has two components. Their unit sections are V_2(R^7), in agreement with Corollary 8.13 of
[Biss, Christensen, Dugger and Isaksen](../../notes/math-0702075.md) (two copies of V_2(R^7)); the representatives
have tangent dimension 6 = orbit dimension 6.

*R_12 = V u B9.* On every slice the order-10 variety is V (or {mu' = 0} on P4s, the piece B9).
- V is irreducible of complex dimension 8: its open subset {v' = lambda u', u' != 0} is the image of the irreducible
  hypersurface mu'^2 = (1 - lambda^2) eta(u') in (u', lambda, mu'), and V is the closure of that subset because points
  with u' = 0 are limits (u' = eps v0, lambda = 1/eps, mu' = sqrt((eps^2 - 1) eta(v0))). The representative has tangent
  dimension 8 and 8 independent tangent vectors of the parametrization.
- B9 is the G_2-image of the irreducible set P4s n {mu' = 0}, so irreducible; it equals the closed set of its equations
  because an independent pair with u' x v' = 0 spans a special plane and a dependent null pair lies in one. It has
  complex dimension 9 (tangent dimension 9, orbit rank 9, unit dimension 17).
- V is not inside B9 (mu' != 0 at its representative) and B9 is not inside V (dimension), so R_12 has exactly these
  two components. V n B9 = {mu' = 0, u' = alpha n, v' = beta n, n null} has complex dimension 7 (unit dimension 13),
  with lower bound 7 from the representative and the same upper bound from the parametrization.

*R_8 = W8 u E8-bar.* On every slice the order-12 variety is W8, V or {Q = 0} on P3a, P3b (the piece E8 by definition).
V lies in E8-bar (Theorem 7). So R_8 = W8 u E8-bar.
- W8 = N x N is irreducible of complex dimension 12 (unit dimension 23); the hyperbolic representative has tangent
  dimension 12 and orbit-family rank 12.
- E8 is the image of G_2 x {b^2 - d^2 + m^2 = 0}, irreducible; at the representative the tangent dimension and the
  orbit-family rank are both 11, so E8-bar has complex dimension 11 (unit dimension 21).
- Neither contains the other: W8 is inside {mu' = 0} and E8-bar is not (the representative has mu' = 4), and
  dim W8 > dim E8.

*R_4.* V(Q) u V(G) (Theorem 3).

## Theorem 7: closure incidences

1. **B9 < W8.** The equations of B9 imply those of W8.
2. **N_+, N_- < V n B9.** For u' null with v' = +-u', mu' = 0: u' ^ v' = 0, Q = 0 (so V) and eta(u') = eta(v') =
   eta(u', v') = 0 with u' x v' = 0 (so B9).
3. **V < E8-bar.** A point of V with u' ^ v' = 0 and (u', v') spanning a line with eta(p) != 0: F1 maps p to e'_1, the
   point becomes (b e'_1, m, d e'_1) in P3a with Q = 0, which lies in E8. Those points are dense in the irreducible V.
4. **B9 < E8-bar.** For s != 0 the curve of item 13 equals a multiple of the point
   (a n + b e_t, m, c n + d e_t) with the unit vector e_t = e0 + k/(4 s), (b, d, m) = (16 s, 20 s, 12 s) and
   d^2 - b^2 - m^2 = 0. The frame (n, e_t) has e_t x n = n (since n x k = 0), so n lies in V_+ of e_t: by F1 and F2 the
   point is in E8. At s = 0 the point (4 n + 4 k, 0, 8 n + 5 k) is an independent pair in the special plane span(n, k),
   whose G_2-orbit is open in B9 (ordered-pair orbit dimension 9 = dim B9). So B9 lies in the G_2-stable closed set
   E8-bar.
5. **Memberships in V(Q) and V(G).** G = Q^2 + 4 (eta(u') eta(v') - eta(u', v')^2) (item 14).
   - On W8, G = 0 and Q = 2 eta(u') != 0 generically: W8 lies in V(G) and not in V(Q).
   - On V, Q = 0 and the Gram determinant vanishes (Binet and Cauchy), so G = 0. On B9, mu' = 0 and the three forms
     vanish, so Q = G = 0. On the P3 slices the Gram determinant vanishes identically and Q = 0 on E8, so E8-bar, a
     closure of a G_2-stable set inside the closed V(Q) n V(G), lies there.

So every point of nullity at least 8 lies in V(G), every point of nullity at least 12 in V(Q) n V(G), and R_16 lies in
V n B9.

## Theorem 8: connected components of D_(5,k)

D_(5,k) is the quotient of S_k by positive scaling, so S_k and D_(5,k) have the same connected components.

- **k = 4.** S_4 = (V(Q) minus R_8) u (V(G) minus R_8). V(Q) and V(G) are irreducible and R_8 has dimension 12 < 14, so
  each part is connected. The point u' = 3 e'_1 + (e'_2 + e'_3 + e'_4 - e'_5), mu' = 4, v' = 5 e'_1 has Q = G = 0 and
  nullity 4, so the parts meet. D_(5,4) is connected, with two irreducible algebraic pieces of unit dimension 27.
- **k = 8.** S_8 = (W8 minus R_12) u (E8-bar minus R_12), each part connected (an irreducible cone minus a proper
  closed subset). The parts are disjoint: W8 minus R_12 has two G_2 x C^*-orbit types (a pair with Gram matrix
  diag(g, -g), g != 0, one orbit by F1 and F2 and the scaling; an independent pair in a generic isotropic plane, one
  orbit by F4 and the full gl_2 action of item 9). At each representative the Zariski tangent dimension of the order-12
  Pfaffian scheme is 12, so the scheme is regular of dimension 12 there and R_8 is the germ of W8 alone. If E8-bar met
  W8 minus R_12 at p, E8-bar would lie near p inside W8, hence entirely inside W8 by irreducibility, which contradicts
  mu' != 0 on E8. Hence S_8 has exactly two connected components, of unit dimensions 23 and 21.
- **k = 12.** S_12 = (V minus R_16) u (B9 minus R_16), each connected, and u' = n, v' = 2 n, mu' = 0 has rank 8, so it
  lies in V n B9 outside R_16. D_(5,12) is connected, with two irreducible algebraic pieces of unit dimensions 15 and
  17.
- **k = 16.** S_16 = (N_+ minus 0) u (N_- minus 0), disjoint, each connected: two components of unit dimension 11.

## Reconciliation with the registry

The pieces are the local pieces of [the gap record](../a5-stiefel-pfaffian-germs/README.md) and their global closures.
The tangent bound exceeds the family of H_5^perp by exactly 2 because mu' is a complex line (y_8, y_24) transverse to
every piece not contained in H_5^perp:

| Registry family | Witnesses | Piece | Unit dimension of piece | Unit dimension of piece n {mu = 0} | Registry family dimension |
| --- | --- | --- | --- | --- | --- |
| nonzd-axis, nullity 12 | 1, 8, 15 | V | 15 | 13 | 13 |
| zd-nonzd-locus, nullity 8 | 4, 11, 18 | E8-bar | 21 | 19 | 19 |
| zd-nonzd-generic, nullity 4 | 5, 12, 19 | V(G) | 27 | 25 | 25 |
| nonzd-nonzd-locus, nullity 4 | 6, 13, 20 | V(Q) | 27 | 25 | 25 |

A piece P not inside {mu' = 0} meets the hyperplane in complex dimension dim P - 1 (an irreducible cone, Krull's
theorem), so the unit dimension drops by 2.

- **Nullity 12 near e_1 + e_18.** x_0 = e_1 + e_18 is the point u = e_1 + i e_2, v = 0, mu = 0: it lies in V and B9.
  The two pieces of the Bouligand cone `A15 u B17` of
  [the selected-center note](../../notes/nullity_twelve_local_geometry.md) are the tangent cones of V (cone dimension
  16, unit 15) and B9 (cone dimension 18, unit 17, the Biss-Christensen-Dugger-Isaksen D-locus bundle with its length
  ratio), and the stated intersection dimension thirteen is dim V n B9 = 13. The global nullity-12 locus is exactly
  V u B9.
- **The {a, 0} families.** {a, 0} and {0, a} with a not a zero divisor are v' = +-u', mu' = 0, u' non-null: complex
  dimension 7, unit dimension 13, inside V, outside B9 and outside W8.
- **Proposition 8.2 points.** (i_4, e_p) = e_8 + e_(16+p) has mu = 1, u = i e_p, v = 0: it lies in V with mu != 0.
- **Nullity 16 only in H_5^perp.** N_+ and N_- lie in {mu' = 0}, which is Theorem 8.1 of
  [math-0702075](../../notes/math-0702075.md) for A_5.
- **The H_5^perp table.** Inside {mu = 0}: both entries zero divisors outside the D-locus give nullity 8 (W8 minus
  R_12, 23 unit dimensions = 2 x 12 - 1, a pair of zero divisors of A_4); the D-locus pairs of zero divisors give
  nullity 12 (B9); {a, 0} gives 12 (V n {mu = 0}); a zero divisor with a non-zero-divisor in the D-locus gives 8
  (E8-bar n {mu = 0}, 19); a zero divisor with a non-zero-divisor outside the D-locus gives 4 (V(G) n {mu = 0},
  25); two non-zero-divisors in the D-locus give 4 (V(Q) n {mu = 0}, 25).
- **New content.** D_(5,8) has a piece of unit dimension 23, the pairs of zero divisors of A_4 outside the D-locus,
  larger than the families of the gap record, which treat only entries with a non-zero-divisor. The four local pieces
  of the gap record are the germs at the witnesses of the global pieces V, E8-bar, V(G) and V(Q).

## Imported results

- The transport rank_R L_y = 2 rank_C A(z, conj z) (gate core-690 of the Pfaffian record).
- Standard facts: Pf^2 = det and rank of a skew matrix as the largest order of a nonzero principal Pfaffian;
  im C = ann(ker C^T) for a skew matrix; the Lie algebra rank of a connected algebraic group action gives orbit
  dimension; an irreducible complex variety minus a proper closed subset is connected; Krull's hyperplane theorem; the
  group generated by exp of a derivation consists of automorphisms; sl_3 integrates to SL_3 acting on V_+.
- Buchberger's algorithm of python-flint 0.9.0 (`buchberger_naive`), with `is_groebner` re-verified on every output.

## Falsifiers and scope

Any of the following refutes the argument where it occurs: a basis pair where eta C' is not skew or not D C_z D; a cofactor
off Q G z'_j; a nullity off 28 - 2 rank C_z at a representative; a slice whose order-12, 10 or 8 ideal escapes its named
pieces (an uncovered generator, a product outside the radical or a piece not contained in the ideal's variety); a
representative of the wrong rank, tangent dimension or orbit-family rank; a quadric, sl_3, null-orbit or minor
certificate that fails; a Pfaffian of order 12 that fails to vanish on the curve; a nullity-4 point of V(Q) n V(G) that
lies in R_8. None occurred.

The record covers the algebraic and connected-component structure of the strata. It does not cover:

- the singular loci, smoothness and normal links of the pieces (roadmap item 4) beyond the regular points listed;
- the Zariski-closure incidences among pieces other than those of Theorem 7 (for example whether B9 meets E8-bar
  outside the dense orbit, which does not affect the component count);
- kernel bundles, attachments, homology, homotopy type (items 5 to 8);
- a Rocq formalization of any statement.

Items 5 to 8 inherit the components, dimensions and incidences above as their starting data.

## Exploration

`--explore` repeats the order-14 slice certificate (Q G has radical power 2 in the ideal and every order-14 Pfaffian
lies in (Q) or (G) on all six slices) and runs a deterministic numerical search for stray components: for each of the
bounds rank C <= 10, 8, 6 it minimizes the squared small singular values of C_z from 24 starts taken from a Kronecker
sequence, and classifies each converged point. Every converged point lies in W8 (including B9, N_+, N_-) or in V(Q)
with Gram rank at most 1 (E8-bar and V): 8 and 15 points at rank bound 10 with one start not converged, 19 and 2 at bound
8 with three not converged, and 24 in W8 at bound 6. The search is corroboration of the covering and carries no
admission weight.

## Literature

- [Biss, Dugger and Isaksen](../../notes/math-0511691.md), Lemmas 9.4 and 9.5 and Corollary 8.13: zero divisors are
  imaginary and orthogonal to C_n; the top stratum of A_5 is two copies of V_2(R^7).
- [Biss, Christensen, Dugger and Isaksen](../../notes/math-0702075.md), Theorem 1.5, Corollary 7.4, Theorem 7.5: the
  H_5^perp nullity table and the D-locus bundle, which the pieces B9, W8, V and E8-bar reproduce on {mu = 0}.
- [Koebisu](../../notes/2608.08232.md): det L_x = N(x)^2 D_14(x)^2 in A_5. With Theorem 1 the zero set of D_14 in A_5
  is the doubly pure set V(Q) u V(G).

No external literature search was run for this record; the sources above are the registered notes.

## Independent verification

[verification.md](verification.md) re-derives the six claims from `cd_core` alone with
[verify_strata_independent.py](verify_strata_independent.py), which imports nothing from the author's script and writes
[verification.json](verification.json); its seeds and sample points come from the ANU QRNG draws
`docs/evidence/anu_qrng/draw-2026-10-26T012526Z.json` and `draw-2026-10-26T012529Z.json`, which it owns whole. It
refutes nothing across exhaustive integer points, random points on every piece, finite-field enumeration of the six
slices over F_11 and F_13 and full-space finite-field samples. It runs about four minutes on 12 workers and is not a
gate.

Three values of `result.json` are asserted by the script rather than computed, and the verifier supplies their
independent support:

- `topology.intersection_V_B9.complex` is the literal 7; the script records the lower bound only. The verifier proves 7
  from a random-point lower bound and a parametrization count upper bound.
- `PIECE_DIMENSIONS` is a literal table guarded at representative points; the verifier finds tangent dimension equal to
  parametrization rank at random points of N_+, N_-, V, B9, W8 and E8.
- The connected-component counts 1, 2, 1, 2 are literals; the script checks the supporting incidences. The verifier
  derives the two components of D_(5,8) without the two-orbit claim of Theorem 8: hyperbolic W8 points have Q != 0, and
  generic isotropic W8 points lie outside the closed set {Q = 0, Delta = 0, rank[u; v; Im(uv)] <= 2} that contains
  E8-bar, by x x (x x w) = (x.w) x - (x.x) w.

The covering half of Theorem 6 (every point of R_k lies in the listed pieces) rests on the slice Groebner certificates of
Lemma 5, which `--check` recomputes over Q; the verifier corroborates them by exhaustive enumeration over F_11 and F_13
only. Equations for E8-bar are not given; the closed set above contained every nullity-8 point off W8 in the verifier's
searches, which suggests R_8 = W8 u that set, unproved over Q.

## Replay

```sh
"$PYTHON" -B -W error scripts/a5_zero_divisor_strata.py --check docs/evidence/a5-zero-divisor-strata/result.json
"$PYTHON" -B -W error scripts/a5_zero_divisor_strata.py --self-test && "$PYTHON" -B -W error -O scripts/a5_zero_divisor_strata.py --self-test
"$PYTHON" -B -W error scripts/a5_zero_divisor_strata.py --explore docs/evidence/a5-zero-divisor-strata/explore.json
```

The check recomputes everything and compares the record, minus its `versions` field. It measured 3.7 s on 12 CPUs and
5.7 s serially (`GOROROBA_WORKERS=1`), with python-flint 0.9.0 and sympy 1.14.0 on Python 3.14.7. The self-test measured
1.0 s in normal mode and 3.1 s under `-O`; `--explore` measured 11 s.
