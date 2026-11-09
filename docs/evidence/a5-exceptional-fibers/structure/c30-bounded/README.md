# C30 in the W8 exceptional fiber: linear planes over the base locus of the point blowup

Result. At p = 32009 and p = 32029 the degree-30 component C30 of V(K2) for W8 -> N- (C30 = V(K2 : P) at 32009; at
32029 the component of V(K2) other than C20, `../w8-kp/README.md` steps 5 and 6) lies in the fiber E0 = Proj F(I) over
the origin. With C20 in E0 (arcs-iso-w8/README.md), E0 = V(K2) set-theoretically. K2 lies in the defining ideal L of
F(I) (degree-2 receipts) and is radical (A5-061) and saturated (k[y]/K2 is Cohen-Macaulay of dimension 6), so the projective
Nullstellensatz gives L = K2 and F(I) = k[y]/K2 in every degree at both primes (step 8 below). The W8 degree-6 rank
run (N = 19, 17 to 20 h) does not decide the Hilbert function of F(I); it remains an independent test of the rank
engine and of the convergence rule N = 3d + 1. Two adversarial reviews (Codex and Grok, 2026-11-08,
[docs/archive/reviews/c30-w8](../../../../archive/reviews/c30-w8/README.md)) found two sentences whose stated reasons
were insufficient, the unit claim of step 2 and the truncation argument of step 4; both steps below carry the
corrected arguments, and the exact identity that step 4 needs is retained in `l0/`. The ledger rows A5-066, A5-236 and
A5-237 record the result.

## Decision criterion, from the records

- E0 lies in V(K2) because K2 lies in L (arcs-iso-w8/README.md, first paragraph). C20 = V(P) lies in E0 by the arc
  certificate of the same README. F(I) = k[y]/K2 holds in every degree exactly when V(K2 : P) = C30 also lies in E0
  ([w8-kp/README.md](../w8-kp/README.md), ledger row A5-066).
- C30 lies in E0 when a parametrized family of limit points of the graph of [G] has cone dimension 6 (Jacobian rank 6)
  and lies in V(K2 : P) outside V(P). The review `docs/archive/reviews/fold-32d/review-codex-final-report.md`
  ("Next computations", item 1) names the same test: a limit outside C20 with rank 6 supports inclusion of C30, and a
  branch count of degree 20 only, or a relation outside K2 in some degree, falsifies it.
- The t-space slice ladder cannot decide it: a generic slice of codimension 5 meets E0 through C20 whether or not C30
  belongs to it (ledger row A5-218, `rejected`; its README names a branch-count variant as untested).

## Reduction: why the planes lie in E0

Notation. t1, t2, t4, t5, t6, t7, t9 are the coordinates of the W8 header `w8-nm.sing`; J is the quartic of V(J), a
hypersurface whose tangent cone at the origin is a nondegenerate quadric (rank 7); G_1, ..., G_24 generate I; 21 of
the 24 have a nonzero degree-2 part and every one vanishes on the linear 3-space L0 = {t2 = 0, t4 = t6, t5 = t7,
t9 = 0}.

1. Point blowup. B = Bl_0 V(J) has the chart t1 = s, t_i = s u_i. There J(s, s u) = s^2 J'(s, u) and
   G_j(s, s u) = s^2 G'_j(s, u) (exact division, checked by every plane script), so I O_B = s^2 I' with
   I' = (G'_1, ..., G'_24). B is smooth along {s = 0} because J' has a nonzero linear part at the points used. The
   exceptional divisor {s = 0} is the quadric Q^5 of tangent directions.
2. The fibers. Near a point of {s = 0} the divisor s = 0 is Cartier (B is smooth there), so (s^2) is an invertible
   ideal sheaf; s^2 itself vanishes on {s = 0} and is no unit. Multiplication by s^{2n} identifies the graded pieces of
   the Rees algebras of I' and of s^2 I' = I O_B, so Bl_{I'} B = Bl_{I O_B} B, and on it both (s^2) and I' pull back
   to invertible ideals, hence so does I O_B. The composite with B -> V(J) therefore factors through Bl_I V(J) by the
   universal property of the blowup of I. The factor map is
   proper and birational, hence onto, and it preserves the projective coordinate, since [G] = [s^2 G'] = [G']. The fiber
   of Bl_{I'} B over any point p of {s = 0} therefore maps into E0.
3. The base locus. The 24 quadrics G_2 = G'|_{s = 0} cut Q^5 in P(L0) = P^2 set-theoretically (arcs-iso-w8/README.md,
   "the degree-2 parts of G cut the tangent cone in L0 doubled"). Over Q^5 minus P(L0) the map u -> [G_2(u)] has image
   C20; the on control below reproduces its rank 6. A piece of E0 beyond C20 lies over P(L0), where the fiber over p is Proj F(I'_p) (fiber
   cone of I' at p). The proof below uses only the inclusion of step 2 and not this localization.
4. The slice. At a point p = [1 : 0 : b : c : b : c : 0] of P(L0), the slice B_4 = B cap {v6 = v7 = 0} (v_i = u_i minus
   the coordinate of p) is smooth of dimension 4 and transversal to P(L0). F(I'_{B,p}) maps onto F(I'|_{B_4}), so
   Proj F(I'|_{B_4}) embeds in the fiber over p. On B_4 the generators G'_2 and G'_11 have independent linear
   parts. The equations G'_2 = G'_11 = J' = 0 have an invertible Jacobian in (v4, v5, v9) at p (the Newton
   determinant), so the formal implicit function theorem gives a unique solution (v4, v5, v9) = x(s, v2) in
   k[[s, v2]]^3 with x(0, 0) = 0: the smooth surface S. Divisibility by v2 is exact, not a truncation statement. J and
   all 24 G_j vanish identically on L0, and in the chart they vanish on the curve (s, v2 = v4 = v5 = v9 = 0) for every
   (b, c) (`l0/l0-identity-*.log`, polynomial identities with symbolic b and c at both primes). That curve solves the
   same three equations at v2 = 0, so by uniqueness x(s, 0) = 0, and G'_j|_S (s, 0) = G'_j(s, 0, 0, 0, 0) = 0: every
   G'_j|_S is divisible by v2 in k[[s, v2]]. Newton iteration to order 10 computes the 2-jets of G'_j|_S exactly
   (orders up to 10 of the composition depend only on orders up to 10 of x), hence the exact 1-jets of the quotients
   G'_j|_S / v2; their linear parts span m/m^2 for m = (s, v2) (zero constant terms and a 24 x 2 linear-coefficient matrix of rank 2, read in the global
   ordering dp), and Nakayama gives
   that the quotients generate m. Modulo (G'_2, G'_11) the image of I' is therefore v2 m = (v2 s, v2^2), so
   I'|_{B_4} = (G'_2, G'_11, v2 s, v2^2) in the coordinates (G'_2, G'_11, s, v2), a monomial ideal whose four
   generators have affinely independent exponents. The products x^a y^b (v2 s)^c (v2^2)^e with a + b + c + e = n are
   therefore distinct monomials and a basis of I^n / m I^n: a monomial of I^n is a product of n generators times a
   monomial, and it lies in m I^n exactly when that cofactor is not 1, so dim I^n / m I^n = binom(n + 3, 3) and the
   fiber cone is the polynomial ring k[Z1, Z2, Z3, Z4]. A Singular recomputation of the minimal basis of
   (x, y, s v, v^2)^n in dp gives 4, 10, 20, 35, 56, 84 for n = 1 to 6 (Grok review, 2026-11-09).
5. The plane. Write G'_j = c_j1 G'_2 + c_j2 G'_11 + v2 (alpha_j s + beta_j v2) modulo m I'. The 24 x 4 matrix
   M(p) with rows (c_j1, c_j2, alpha_j, beta_j) (rows 2 and 11 are unit vectors) maps Proj k[Z] to a linear 3-space
   Pi_p = column space of M(p) in P^23, and Pi_p lies in E0. The coefficients c_jk(p) come from the linear parts of
   G'_j and alpha_j, beta_j from the linear parts of G'_j|_S / v2.
6. The family. M(p) is a rational function of (b, c) on an open set U of P(L0) that contains the points used (the
   determinants of the Newton block and of the (v4, v5) block are nonzero there, and the conditions of step 4 are open).
   The set T = closure of the union of Pi_p over U is irreducible (U x A^4 is irreducible and M is rational on it)
   and lies in E0, because steps 4 and 5 hold at every point of U. Dual-number arithmetic over
   F_p[eps]/eps^2 gives the derivatives of M(p) in b and c; the matrix [M(p) | dM/db Y0 | dM/dc Y0] for a random
   vector Y0 has rank 6. The map f(p, Z) = M(p) Z from the open set of (p, Z) to the affine cone over T has differential
   of rank at most the dimension of the cone at a general point, since the differential lands in the tangent space of the
   closure of the image at a smooth point of it (a statement that holds in every characteristic). Rank is lower
   semicontinuous, so the generic rank is at least the rank 6 read at one point. The affine cone over T therefore has
   dimension at least 6, and T has projective dimension at least 5.
   T lies in V(K2) because E0 does (K2 lies in L); the vanishing of the 144 quadrics of K2 on each computed plane is a
   control of the pipeline, not a premise. T does not lie in C20 (a plane is not in V(P) at 32009, and is outside V(Lambda)
   at 32029, where C20 lies in V(Lambda)); V(K2) = C20 cup C30 and the irreducibility of T give T in C30. C30 is
   irreducible of dimension 5, so T = C30, and C30 lies in E0.
7. The Hilbert function. HF(k[y]/K2, d) for d = 1 to 7 (`kbase` of the standard basis of K2, at 32009 and at 32029)
   is 24, 156, 600, 1,725, 4,116, 8,624, 16,416 (`hf/hf-k2-p*.log`, from the receipt-bound degree-2 relations). The certified values h_1 to h_5 of the W8 -> N- rows A5-138 to A5-142
   (32009) and A5-144 to A5-148 (32029) equal the first five, so no certified value lies below HF(k[y]/K2, d). The
   result gives h_6 = 8,624, the receipt-bound upper bound of rows A5-143 and A5-149, and h_7 = 16,416; the doubling
   automorphism (`../README.md`, ledger row A5-013) carries the whole fiber to W8 -> N+, so rows A5-131 and A5-137
   take the same values. A degree-6 element of L outside K2, which a degree-6 membership receipt would show as a
   membership failure, would falsify the reduction. A truncated rank is a lower bound (r_N <= h_6), so no rank value
   below 8,624 contradicts h_6 = 8,624; such a value bounds the engine or the N = 3d + 1 law instead.
8. The ideal. K2 is radical (A5-061: eight QRNG sections, each a squarefree eliminant of degree 50) and, k[y]/K2 being Cohen-Macaulay of positive dimension, saturated; F_p is perfect, so K2
   is geometrically radical and K2 = I(V_+(K2)) over an algebraic closure, contracted back. E0 = V_+(L) contains
   V_+(K2) = C20 cup C30, so L lies in I(V_+(K2)) = K2; with K2 in L, L = K2. L need not be assumed radical.

## Computation

`c30_gen.py` writes `points.json` (every coefficient as [index, value] of the ANU draw
`docs/evidence/anu_qrng/draw-2026-11-08T182935Z.json`, values in [1, 32008] in index order) and `sing/*.sing` from the Singular
templates in `templates/`; `run.sh CASE [LIMIT_S]` runs one script in a cgroup scope with `MemoryMax=8G`,
`MemorySwapMax=0` (or `prlimit --as` where no user bus answers), `timeout`, keeps `logs/CASE.log`, `.result`, `.err`,
`.time`, `.rss`, and fails a run whose log carries a Singular error line. Singular 4.4.1, one thread: the control and
global-slice logs on the build host (passagemath-singular 10.8.13); the five plane logs on the OCI A1 host (aarch64,
distribution Singular 4.4.1), rerun on 2026-11-09 after the quotient-ideal check moved from the local ordering `ds` to
the global-order rank test, with every other result line equal to the build-host run. The `sing/c30-plane-pP-ptN.sing` scripts hold the dual-number pipeline of steps 4 to 6 and the tests below;
`kp-p32009.sing` is the ring Y with K2 and P copied from `../w8-kp/check.sing`; K2 : P is `../w8-kp/quotient.txt`, K2 at
32029 is `working/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel`, Lambda is the nine linear forms of `check.sing`.

Each plane script reports, in `logs/*.result`: exact divisibility of J and G by s^2; the Newton residual (0);
divisibility of G'_j|_S by v2; the linear-part consistency of c_jk (the v2 coefficient of every G'_j agrees with
c_j1 and c_j2); the constant terms (none) and linear-coefficient rank (2) of the quotient ideal; the number of K2, Lambda, P and K2 : P generators that do not vanish on
Pi_p; the rank of M(p); and the Jacobian rank.

| Prime | Draw indices of b, c and Y0 (four values) | K2 nonzero on Pi_p | Lambda nonzero | P nonzero | K2 : P nonzero | rank M | Jacobian rank | Time, peak |
|---|---|---|---|---|---|---|---|---|
| 32009 | pt1: 4, 5; 7, 12, 13, 15 | 0 of 144 | 9 of 9 | 23 of 48 | 0 of 131 | 4 | 6 | 45 to 52 s, 26 MiB |
| 32009 | pt2: 16, 19; 20, 22, 23, 24 | 0 of 144 | 9 of 9 | 23 of 48 | 0 of 131 | 4 | 6 | 45 to 52 s, 26 MiB |
| 32009 | pt3: 25, 26; 29, 32, 35, 36 | 0 of 144 | 9 of 9 | 23 of 48 | 0 of 131 | 4 | 6 | 45 to 52 s, 26 MiB |
| 32029 | pt1: 37, 38; 41, 43, 47, 50 | 0 of 144 | 9 of 9 | not available | not available | 4 | 6 | 45 to 52 s, 26 MiB |
| 32029 | pt2: 51, 60; 62, 63, 64, 69 | 0 of 144 | 9 of 9 | not available | not available | 4 | 6 | 45 to 52 s, 26 MiB |

At 32029 the ideals P and K2 : P are not retained (`../w8-kp/README.md` names the two components without coefficient
ideals), so the placement in C30 rests on V(K2) = C20 cup C30 and C20 in V(Lambda).

Tangent consistency (independent of the dual-number code). The tangent space of V(K2) at y0 = M(p) Y0 is the kernel of
the Jacobian of the 144 generators of K2, of rank 18 at a smooth point of the 6-dimensional cone. At every point the
six vectors (four columns of M(p) and the two derivative columns) lie in that kernel, and at 32009 also in the kernel of
the Jacobian of the 131 generators of K2 : P (rank 18, a smooth point of C30). A wrong derivative would leave the
tangent space with overwhelming probability, so these zero entries check dM/db and dM/dc.

## Controls

| Control | Expectation | Reading |
|---|---|---|
| on: the point blowup family u -> [G_2(u)] on Q^5 (`c30-control-emq-pP`) | Jacobian rank 6, in V(K2), V(P) (so in V(Lambda)), off V(K2 : P) | rank 6 at both primes; K2 0 of 144, Lambda 0 of 9; at 32009 P 0 of 48 and K2 : P 58 of 131 nonzero |
| off: the plane over a point of the strict transform of L0 outside the exceptional quadric (`c30-control-base-pP`) | gradient rank 3; K2 does not vanish over a point off the origin | rank 3; K2 nonzero 56 of 144 at 32009 and 83 of 144 at 32029 |
| consistency: all 144 K2 generators vanish on every plane | holds only if the plane coordinates are the y coordinates of K2 and Pi_p lies in E0's ambient V(K2) | 0 of 144 at five points |

The on control reproduces the known C20 certificate (rank 6, V(P)) with this code path's Jacobian method, and the K2 : P
test reads positive there, so the two component tests discriminate. The off control shows that K2 vanishing on Pi_p is
specific to the fiber over the origin.

## Cost and the obstruction of the global slice

The five planes cost 45 to 52 s and 26 MiB each (the global slice ran beside them); the controls cost under 0.4 s. The route before this one, the global t-space
slice of codimension 5 for W8 (`c30-global-slice-k5-p32009`, five QRNG forms of G saturated by t2 through the homogenized
standard basis), did not finish its first standard basis in 900 s (exit 124; peak resident set 0.61 GiB sampled every 30 s in
`logs/c30-global-slice-k5-p32009.rss`, pair set of 1536 at the largest in the `option(prot)` trace of `.log`).
The ideal (J, l_1(G), ..., l_5(G)) has the Bezout bound
4 * 8^5 = 131,072 for its degree (J has degree 4, G degree 8), against 20 or 50 for the branch count the test needs; the
chart route of `../arcs-iso-w8/README.md` exceeded 23.5 h and 25.7 GiB. The local route is cheap because the fiber
over a point of P(L0) is read from the local ring there (four variables after the slice, two after the surface), not
from the global variety.

## Scope and falsifiers

- Fields. Exact over F_32009 and F_32029; the statements say nothing about characteristic 0.
- Points. Five rational points of P(L0), chosen from a QRNG draw, with Jacobian rank 6 at each. The rank at one point
  bounds the generic rank from below, so T has projective dimension at least 5 as soon as one point reads 6; equality
  comes from T lying in C30. A further point of lower rank lies on the rank-drop locus and falsifies nothing. Both
  reviewers reproduced the RESULT lines of the plane script at one further point of P(L0) at 32009 (rank 6, K2
  0 of 144, Lambda 9 of 9); its coordinates reuse draw values already assigned to controls in `points.json`, so it
  is a reproduction, not a retained sixth point.
- Dependence. Steps 1 to 8 are proof steps; two adversarial reviewers read them and the two repaired steps (2 and 4)
  carry the corrected arguments. The computed inputs are the exact divisibilities by s^2, the L0 identities of `l0/`,
  the nonzero Newton and (v4, v5) determinants, the rank-2 linear parts of the quotient ideal and the Jacobian rank 6, at five
  points. The vanishing of K2 on the planes, the tangent consistency and the two controls check the pipeline.
- Falsifiers. (a) A plane that fails any K2 generator at a point where the pipeline reports success. (b) Jacobian rank
  below 6 at every point of a larger sample. (c) A relation of L outside K2 in some degree, for instance a membership
  failure in a degree-6 receipt. (d) A J or G_j that fails to vanish on the chart curve of L0, or a vanishing Newton
  determinant at every point of P(L0).
- Not claimed. The multiplicity statement e(F(I)) = 50 follows from F(I) = k[y]/K2 and the Cohen-Macaulay property of
  K2 recorded in `../w8-kp/README.md`; this directory runs no multiplicity computation.
