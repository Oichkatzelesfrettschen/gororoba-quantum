# Explicit equations for the A_5 rank strata and an independent covering

`result.json` is the output of [`rederive_strata_equations.py`](rederive_strata_equations.py) `--out`. The record gives
closed equations for every rank stratum of the A_5 zero-divisor set and re-derives the covering half of the
[strata classification](../a5-zero-divisor-strata/README.md) (its Lemma 5 and Theorem 6) with new code and a second
Groebner engine. It settles the two leads the [independent verification](../a5-zero-divisor-strata/verification.md)
left open: E8-bar now has equations, and the covering no longer rests on the author's python-flint slice certificates.

Four statements are established:

1. **E8-bar equations.** E8-bar = Ehat := {Q = 0, Delta = 0, rank [u; v; u ^ v] <= 2}, an irreducible cone of
   complex dimension 11 whose projectivization has degree 24.
2. **Explicit strata.** R_8 = W8 u Ehat, R_12 = V u B9, R_16 = N_+ u N_-, with the equations of the table below.
3. **Containments without the covering.** Every principal Pfaffian of C_z of order 12 lies in the ideal of Ehat and in
   the ideal of W8, every one of order 10 in the ideals of V and B9, and every one of order 8 in the ideals of N_+ and
   N_-. Singular decides this over Q in the 15 split coordinates z'; the statement holds over C, because ideal
   membership is unchanged by the extension from Q to C, and the change to original coordinates is linear over Q(i).
4. **Incidences.** V and B9 lie in E8-bar, because the Ehat equations vanish on V and B9. This replaces the dense-subset
   argument (V) and the curve argument (B9) of Theorem 7 items 3 and 4 of the strata record.

The statements are about rank C_z. The step from rank C_z to the nullity of L_y is Theorem 2 of the strata record
(nullity L_y = 28 - 2 rank C_z), which imports the transport of gate core-690; this record spot-checks it at six
rational points and does not re-derive it.

## Conventions

The product is the cd_core doubling, e_p e_q = cd_sign(dim, p, q) e_(p XOR q). A doubly pure y of A_5 has
z_k = y_k + i y_(16+k), k = 1..15, with u = z_1..z_7, mu = z_8, v = z_9..z_15. Dot products are complex bilinear, and
x ^ y = Im(x y) is the cd_core octonion cross product. Q = u.u + mu^2 + v.v and Delta = (u.u)(v.v) - (u.v)^2. C_z is
the 15 x 15 Im-block of left multiplication by z in A_4, entry (a, b) = cd_sign(16, a XOR b, b) z_(a XOR b). R_k is
the closed set where rank C_z <= 14 - k / 2, the set of nullity at least k.

**Pieces** (original coordinates):

| Piece | Equations |
| --- | --- |
| W8 | mu = 0, u.u = v.v, u.v = 0 |
| V | rank [u; v] <= 1, Q = 0 |
| B9 | mu = 0, u.u = v.v = u.v = 0, u ^ v = 0 |
| N_+, N_- | mu = 0, u.u = 0, v = +-i u |
| Ehat | Q = 0, Delta = 0, rank [u; v; u ^ v] <= 2 (the 35 maximal minors) |

**Split coordinates.** z_k = i^popcount(k) z'_k are the coefficients on e'_k = i^popcount(k) e_k, and u' = z'_1..z'_7,
mu' = z'_8, v' = z'_9..z'_15. On that basis the products are e'_p e'_q = (-1)^popcount(p AND q) cd_sign(dim, p, q)
e'_(p XOR q), since popcount p + popcount q - popcount(p XOR q) = 2 popcount(p AND q). Those are the split octonions and
sedenions, with the invariant form eta(x, y) = sum_j eta_j x_j y_j given by e'_j e'_j = -eta_j. M(z') = D C_(D z') D,
with D = diag(i^popcount), is a skew matrix over Z[z'] with the rank of C_z. The script builds every piece polynomial
from its original-coordinate definition by substitution over Z[i] and divides out the unit, so none of the split forms
is typed in. All Singular computations run in split coordinates over Q.

## Computations

Each part of `result.json` is an exact computation; `pass` requires every listed value.

1. **Tables** (`tables`). cd_sign agrees with cd_multiply_exact and left_mult_matrix_exact on every basis pair of
   dimensions 8, 16 and 32, and the popcount identity above holds for all pairs below 32.
2. **Identities** (`identities`), over Z[x, y] in split coordinates:
   - eta(x ^ y, x) = eta(x ^ y, y) = 0 and x ^ y = -(y ^ x);
   - x ^ (x ^ y) = eta(x, y) x - eta(x) y;
   - eta(x ^ y) = eta(x) eta(y) - eta(x, y)^2.
3. **G_2 facts** (`g2`), from the split octonion table alone:
   - The derivations D(e'_p e'_q) = D(e'_p) e'_q + e'_p D(e'_q) form a space of dimension 14. Each fixes e'_0,
     preserves Im and is skew for eta.
   - The 49 inner derivations D_(e'_p, e'_q) = [L, L] + [L, R] + [R, R] lie in that span, and over Z[x, y]
     D_(x,y) x = 4 (eta(x) y - eta(x, y) x).
   - The stabilizer of e'_1 has dimension 8 and commutes with K = e'_1 ^ -, with K^2 = 1 on e'_1-perp. The
     eigenspaces V_+ and V_- of K have dimension 3, are totally null and are paired with rank 3. The stabilizer
     preserves V_+, where its image has rank 8 and trace 0, which is sl_3.
   - Slice frames: eta(e'_1) = eta(e'_2) = -1 and eta(e'_1, e'_2) = 0, with e'_2 meeting both eigenspaces. The radical
     vectors e'_2 + e'_3, e'_2 - e'_3 and e'_2 + e'_3 + e'_4 - e'_5 are null, perpendicular to e'_1 and lie in V_+, in
     V_- and in neither. The last splits as (e'_2 + e'_3) + (e'_4 - e'_5) with pairing 0.
   - The three radical vectors have orbits of dimension 6 (rank of the 14 derivations on the vector).
   - n0 = e'_1 + e'_3 is null with a stabilizer H of dimension 8. L = ker(n0 ^ -) has dimension 3, contains n0, is
     totally null, lies in n0-perp and is H-invariant. The trace-free parts of the 8 induced endomorphisms of
     L / n0 span a space of dimension 3, so the image of H in pgl(L / n0) is all of pgl_2, which acts transitively on
     P(L / n0). e'_4 + e'_6 is a special partner of n0 (null, perpendicular, n0 ^ B = 0) and e'_2 + e'_5 a generic one
     (n0 ^ B != 0).
   - Equivariance: the split sedenions also have a derivation space of dimension 14. Every lift D + D on the halves
     (a, b) is one of those derivations, and for each of the 14 lifts and all z',
     M(D z') = -(D^T M(z') + M(z') D) over Z[z'].
4. **Isotropic planes** (`isotropic`). Over Q in x_1..x_7, the four linear forms that cut out L lie in the radical of
   the ideal of the 5 x 5 minors of [h_1 x, .., h_8 x, n0, x], together with eta(x) and eta(n0, x). So for null x in
   n0-perp outside L the matrix has rank 5, and the H-orbit of the plane span(n0, x) has dimension 3.
5. **Slices** (`slices`). A slice is a plane (A, B) of the table below, with the point u' = a A + b B, mu' = m,
   v' = c A + d B. For each of the 18 pairs of a slice and an order k in {12, 10, 8}, Singular over Q in a, b, c, d, m
   decides two inclusions by reduction modulo a standard basis of a radical:
   - every Pfaffian of order k vanishes on each named piece: the Pfaffian ideal lies in the radical of each piece
     ideal;
   - the Pfaffian variety lies in the union: the intersection of the two piece ideals lies in the radical of the
     Pfaffian ideal.

   Order 12 names W8 and Ehat, order 10 names V and B9, and order 8 names N_+ and N_-. All 18 pass.
6. **Global** (`global`), Singular over Q in z'_1..z'_15:
   - The order-12 (455), order-10 (3003) and order-8 (6435) principal Pfaffians reduce to 0 modulo standard bases of
     the ideals of Ehat and W8, of V and B9, and of N_+ and N_-, respectively. The script computes a radical only
     where that reduction fails, and here it never does.
   - std of the Ehat ideal has dimension 11 and degree 24.
   - The piece ideals of W8, V, B9, N_+ and N_- have dimensions 12, 8, 9, 6 and 6.
   - The Ehat generators lie in the radicals of the ideals of V and of B9.
   - The saturation of the Ehat ideal by f = mu' (u'_1 v'_2 - u'_2 v'_1) reduces to 0 modulo the Ehat standard basis,
     so (Ehat : f^infinity) = Ehat.
7. **Points** (`points`). At six rational split points the nullity of the 32 x 32 rational matrix L_y equals the
   nullity its piece predicts (8, 8, 12, 12, 16, 16), and each point satisfies its piece equations. The E8 point
   (a, b, c, d, m) = (1, 3, 2, 5, 4) of P3a lies in Ehat and outside W8, and the hyperbolic W8 point lies outside
   Ehat. The Jacobian of the 37 Ehat generators has rank 4 at the E8 point. Q restricted to P3a is d^2 - b^2 - m^2.

| Slice | A | B | Pfaffians of order 12, 10, 8 | Minimal primes over Q, dimensions per order |
| --- | --- | --- | --- | --- |
| P2 | e'_1 | e'_2 | 80, 274, 379 | 2 3; 3; 1 1 |
| P3a | e'_2 + e'_3 | e'_1 | 82, 332, 520 | 4; 3; 1 1 |
| P3b | e'_2 - e'_3 | e'_1 | 72, 318, 488 | 4; 3; 1 1 |
| P3c | e'_2 + e'_3 + e'_4 - e'_5 | e'_1 | 150, 960, 1739 | 3; 3; 1 1 |
| P4s | e'_1 + e'_3 | e'_4 + e'_6 | 59, 342, 556 | 4; 4; 2 2 |
| P4g | e'_1 + e'_3 | e'_2 + e'_5 | 218, 1770, 2966 | 4; 3; 2 2 |

The prime dimensions count affine dimension in (a, b, c, d, m). The script reports them; the admission reads only the
two radical inclusions.

`--self-test` runs nine controls, in normal mode and under `-O`. Each of these mutations must fail its check:
- Ehat without Q on P3a;
- W8 with u.u = -v.v, on P2 and globally;
- the P3c radical moved into V_+;
- Ehat with the W8 component added, under saturation;
- the isotropic-plane ideal without eta(x) = 0;
- a derivation lift D + (-D);
- the P2 order-12 union with Ehat dropped, which leaves the Pfaffian variety outside W8 alone.

A slice that reads no W8 equation must still pass under the W8 mutation.

## Lemma A: the covering

Every z' is carried by G_2(C), acting on u' and v' by the same automorphism and fixing mu', to a point of one of the
six slices.

*Group action.* The derivations integrate to the connected group G_2(C) of automorphisms of the split octonions, which
preserves eta and the cross product. Their lifts D + D are derivations of the split sedenions that fix e'_8, so G_2
acts on z' = (u', mu', v') by (g u', mu', g v'). The congruence M(D z') = -(D^T M + M D) integrates to
M(g z') = g^-T M(z') g^-1, so rank C_z, and with it every R_k, is G_2-stable. Every piece equation is a polynomial in
eta, the cross product and mu' (the table above, read in split coordinates). So every piece, Ehat included, is G_2-stable
and a cone.

*Orbit facts*, each from computation 3 or 4 together with a standard fact:
- (F1) G_2 is transitive on every quadric {eta(e) = kappa}, kappa != 0. D_(e, y) e = 4 (eta(e) y - eta(e, y) e) runs
  over all of e-perp as y varies, so every orbit in the smooth irreducible quadric has dimension 6 and is open.
  Hence there is one orbit.
- (F2) The identity component of the stabilizer of e'_1 maps onto SL(V_+) and acts on V_- = V_+^* contragrediently. So
  it is transitive on V_+ minus 0, on pairs (x, xi) with xi(x) = c for each c != 0, and on pairs with xi(x) = 0,
  x != 0, xi != 0. Here xi(x) is eta(x, xi), and eta(x + xi) = 2 eta(x, xi).
- (F3) G_2 is transitive on null vectors. A null n is perpendicular to some e with eta(e) = -1, because the radical of
  n-perp is span(n). F1 sends e to e'_1, and n then lies in one of the three types of F2, each of which has an orbit of
  dimension 6. The null cone minus 0 is irreducible of dimension 6, so each of those orbits is open and they coincide.
- (F4) The isotropic planes through n0 form the smooth quadric threefold of null lines of n0-perp / n0, which is
  irreducible. Off the line P(L / n0) every H-orbit has dimension 3 (computation 4), so it is open, and the complement
  of that line is one orbit, the orbit of P4g. On P(L / n0), H acts through SL_2, which is transitive: the orbit of P4s.

*Proof.* Let P = span(u', v').
- P = 0: the point lies on every slice.
- P is a line spanned by p with eta(p) != 0: scale p to eta(p) = -1. F1 sends it to e'_1, which lies on P2.
- P is a plane of Gram rank 2: take a basis p, q with eta(p) = eta(q) = -1 and eta(p, q) = 0. F1 sends p to e'_1, and
  q becomes x + xi in V_+ + V_- with 2 eta(x, xi) = -1. F2 sends (x, xi) to the components of e'_2, giving P2.
- P is a plane of Gram rank 1: P = span(n, e) with n the radical, and e scaled to eta(e) = -1. F1 sends e to e'_1, and
  n = x + xi then has eta(x, xi) = 0. F2 sends n to e'_2 + e'_3 (xi = 0: P3a), to e'_2 - e'_3 (x = 0: P3b) or to
  (e'_2 + e'_3) + (e'_4 - e'_5) (both nonzero: P3c).
- P is a null line or a totally null plane: P lies in an isotropic plane through a null vector n, since n-perp / n is
  nondegenerate of dimension 5 and has null vectors. F3 sends n to n0, and F4 sends the plane to P4g or P4s.

In every case the pair (u', v') becomes (a A + b B, c A + d B) on that slice, with mu' unchanged. QED.

## Theorem B: the strata have the equations of the table

R_8 = W8 u Ehat, R_12 = V u B9 and R_16 = N_+ u N_-.

*Proof.* The pieces lie in R_k by computation 6: each Pfaffian of order k lies in each piece ideal, so it vanishes on
the piece. For the reverse inclusion take z' in R_k. By Lemma A, some g sends z' to a slice point g z' in R_k.
Computation 5 puts g z' in one of the two named pieces, and that piece is G_2-stable, so z' lies in it too. The
inclusions on a slice hold over C because radical membership over Q is unchanged by the extension to C. QED.

## Theorem C: Ehat = E8-bar, irreducible of dimension 11 and degree 24

E8 is the G_2-orbit family of the P3a points with Q = 0, as in the strata record: the closure of
G_2 . {u' = a (e'_2 + e'_3) + b e'_1, mu' = m, v' = c (e'_2 + e'_3) + d e'_1, Q = 0}.

*Proof.*
1. *E8-bar lies in Ehat.* On the P3a plane, n ^ e'_1 is a multiple of n for n = e'_2 + e'_3 in V_+. So u' ^ v' lies in
   the plane, the minors vanish and the Gram determinant is 0. Q = 0 by definition. Ehat is closed and G_2-stable, so
   E8-bar lies in it.
2. *The open part of Ehat lies in E8.* Let z' be in Ehat with f(z') != 0, so mu' != 0 and u', v' are independent. The
   plane P = span(u', v') has Delta = 0, so its Gram rank is at most 1. Gram rank 0 would give Q = -mu'^2 != 0, so the
   Gram rank is exactly 1: P = span(n, e) with n the radical and eta(e) = -1 after scaling.
   - u' ^ v' is a nonzero multiple of n ^ e, and the rank condition puts it in P, so n ^ e = alpha n + beta e.
   - Pairing with e gives beta eta(e) = 0 (computation 2), so beta = 0. If alpha were 0, then e ^ (e ^ n) = -eta(e) n
     = n would be 0. So n is an eigenvector of e ^ - with a nonzero eigenvalue, which is +-1 because K^2 = 1.
   - F1 sends e to e'_1 and F2 sends n to a multiple of e'_2 + e'_3 (in V_+) or of e'_2 - e'_3 (in V_-).
   - An element g of G_2 with g e'_1 = -e'_1 exists by F1. It maps V_+ to V_-, since e'_1 ^ g w = -g(e'_1 ^ w). With F2
     it carries the second case to the first.
   - Q is G_2-invariant, so z' is G_2-equivalent to a point of the P3a family with Q = 0, that is, z' lies in E8.
3. *Ehat is the closure of its open part.* (Ehat : f^infinity) = Ehat (computation 6), and the variety of a
   saturation is the Zariski closure of V(Ehat) minus V(f) over C. So Ehat is the closure of a subset of E8, and
   Ehat lies in E8-bar. With step 1, Ehat = E8-bar.
4. *Irreducible.* On P3a, Q = d^2 - b^2 - m^2 (computation 7), a form of rank 3, so {Q = 0} is an irreducible quadric
   cone times C^2. E8 is the image of the irreducible G_2 x {Q = 0} under the action map, so E8 and its closure are
   irreducible.
5. *Dimension and degree.* std of the Ehat ideal has dimension 11 (computation 6). At the E8 point of computation 7 the
   Jacobian of the generators has rank 4, the codimension, so the ideal is reduced at the generic point of E8-bar,
   which is its only component of dimension 11. The ideal is homogeneous, so its Hilbert multiplicity 24 is the degree
   of the projective variety P(E8-bar). QED.

   The independent review corroborates the degree by a second route. Modulo 32003, the Ehat ideal plus 10 random
   linear forms and one affine form is zero-dimensional of vector-space dimension 24, and so is its radical: 24
   reduced points.

Whether the Ehat ideal is radical, that is, the full ideal of E8-bar with no embedded components, is not decided here.
Delta is redundant set-theoretically. If u', v' are dependent, Delta = 0 because the Gram determinant of a line
vanishes. If they are independent and u' ^ v' lies in their span, it is perpendicular to both (computation 2), so
eta(u' ^ v') = 0, which is Delta up to sign by the Lagrange identity. The record keeps
Delta among the generators.

*Corollary (Theorem 7 items 3 and 4 of the strata record).* V and B9 lie in E8-bar, since the Ehat equations vanish on
both (computation 6).

## Independence and imports

The case split of Lemma A and the six slice planes are the definitions of Lemma 5 of the strata record. The code,
the Groebner engine (Singular 4.4.1 in place of python-flint's Buchberger) and the certificates are new:
- radical equality over Q replaces both the author's radical-power certificates and the verifier's enumeration over
  F_11 and F_13;
- F1 comes from D_(x,y) x in place of the author's quadric certificate;
- F4's rank locus comes from a Singular radical in place of 917 flint minors.

The script imports nothing from `scripts/a5_zero_divisor_strata.py` or from the earlier verifier.

Inherited from the strata record and its verification:
- the dimensions and irreducibility of W8, V, B9, N_+ and N_- (Theorem 6). This record recomputes the dimensions of
  their ideals (12, 8, 9, 6, 6) but not their irreducibility;
- the zero-divisor criterion and the nullity identity (Theorems 1 to 3).

Imported standard facts:
- the connected group generated by exp of a derivation algebra acts with orbit dimension equal to the rank of the
  algebra at the point;
- SL_3 and SL_2 transitivity on the sets named in F2 and F4;
- irreducibility of a quadric of rank at least 3, and of the image of an irreducible variety;
- V(I : f^infinity) = closure(V(I) minus V(f)) over C;
- stability of radical membership and of saturation under the field extension from Q to C;
- Singular's std, radical, intersect, sat and minor.

## Falsifiers and scope

Each of the following refutes the statement where it occurs:
- a derivation dimension other than 14;
- a failed identity of computation 2 or 3;
- a radical vector of the wrong eigenspace type;
- an isotropic plane off L whose orbit rank is below 3;
- a Pfaffian outside a piece ideal;
- a slice point of R_k outside the two named pieces, or a piece point on a slice outside R_k;
- a saturation larger than the Ehat ideal;
- a Jacobian rank other than 4 at the E8 point.

None occurred.

Out of scope: radicality of the Ehat ideal; the singular loci, normal links, kernel bundles, attachments and homology
of the pieces (roadmap items 4 to 8); a Rocq formalization.

## Replay

Singular 4.4.1 must be on PATH. It is not in the hosted CI image, so this record is a retained replay rather than a
gate.

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py \
    --out docs/evidence/a5-rank-strata-equations/result.json
```

The full run measured 13 to 31 s on 12 workers, depending on host load. The self-test measured 8 s.
`result.json` records the Python, python-flint and Singular versions and the script's sha256. Its `seconds` and
`timings_s` fields vary from run to run; every other field is deterministic.
