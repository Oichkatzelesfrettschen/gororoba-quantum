# A Lorentzian slice of A_5: Clifford-defect operators, so(6,1) relations and the kernel on the null cone

`result.json` is the output of [`scripts/a5_null_slice_boost_algebra.py`](../../../scripts/a5_null_slice_boost_algebra.py)
`--out`. The record restricts the zero-divisor invariants of
[the rank-strata classification](../a5-zero-divisor-strata/README.md) to a real seven-dimensional slice of A_5 on which
the quadratic invariant is a Lorentzian form, and determines the left-multiplication operators on that slice exactly.
Every decision is an identity of integer matrices or polynomials, or a FLINT rank over Z; no random draw enters and
every test point is an explicit integer vector. `--check` recomputes the record and compares its bytes, and
`--self-test` runs nine controls, each a property that holds on the record's input and fails on a mutant, in
normal and `-O` modes.

## Conventions

The product is the cd_core doubling, e_p e_q = cd_sign(dim, p, q) e_(p XOR q). The slice is

    y = x_1 e_1 + x_3 e_3 + x_4 e_4 + x_5 e_5 + x_6 e_6 + x_7 e_7 + t e_26,    r^2 = sum of x_a^2,

with S = {1, 3, 4, 5, 6, 7}. A_a = L_(e_a) and J = L_(e_26) are the 32 x 32 integer matrices of left multiplication,
and the Clifford defect of the direction a is

    K_a = -(A_a J + J A_a) / 2,    K(x) = sum of x_a K_a.

The six A_a anticommute and square to -I, and J^2 = -I; K_a records the failure of A_a to anticommute with J.
In the coordinates z = p + i q of the strata record the slice is u = (x_1, 0, x_3, .., x_7), mu = 0, v = i t e_2: the
spatial directions are the imaginary octonion units orthogonal to e_2 in the u block, and the time axis is the
direction e_2 of the v block of the second half (index 26 = 16 + 8 + 2).

## Statements

Each statement is computed: an exact check of the record, named in parentheses, with a `require` in the script's
`validate`.

1. **Invariants** (`invariants`, `real_slice_nullities`). On the slice Q = r^2 - t^2, Delta = -r^2 t^2 and
   G = (r^2 + t^2)^2. The nonzero zero divisors of the slice are the nonzero points of the cone r^2 = t^2, each of
   nullity 4 (by statement 2). With one more spatial coordinate s on e_2 or on e_8, Q = r^2 + s^2 - t^2 and
   G = ((t - s)^2 + r^2)((t + s)^2 + r^2): the zero divisors are again the points of the larger cone
   r^2 + s^2 = t^2, and the nullity rises to 12 on its rays r = 0 (e_2 + e_26 and e_8 + e_26). With both
   coordinates at once, 3 e_2 + 4 e_8 + 5 e_26 has nullity 12 as well. The six directions of S are the ones with nullity 4 for e_j + e_26;
   the eight others below 16 give 12, and e_10 + e_26 is invertible.
2. **Gram identity** (`operator_identities`, `determinant`). L_y^T L_y = (r^2 + t^2) I + 2 t K(x). Each K_a is
   symmetric, integer, traceless and of rank 8, trace(K_a K_b) = 8 delta_ab, and K(x)^3 = r^2 K(x) on all 56 cubic
   coefficients. Hence K(x) has eigenvalues r, 0, -r with multiplicities 4, 24, 4, the Gram operator has
   eigenvalues (r + t)^2, r^2 + t^2, (r - t)^2 with the same multiplicities, and

       det L_y = (r^2 - t^2)^4 (r^2 + t^2)^12.

   The square of the determinant follows from the spectrum, and the sign from the value 1 at y = e_1; six exact
   integer determinants agree with the formula. In the notation of arXiv 2608.08232 (Theorem 5.3,
   det L_x = N(x)^2 D_14(x)^2 on A_5) the slice gives D_14 = (r^2 - t^2)^2 (r^2 + t^2)^5. The determinant has the
   roots t = +-r and t = +-i r, so the operator pencil t J + sum of x_a A_a is not hyperbolic.
3. **Boost algebra** (`boost_algebra`). The defects satisfy

       [[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b    (90 relations),

   and the Lie algebra they generate has dimension 21 over Q. The product K_a^2 K_b^2 is the same diagonal
   projector P_T for all 15 pairs, onto T = span(e_2, e_8, e_18, e_24), and every K_a anticommutes with
   eta = I - 2 P_T, so the defects lie in the orthogonal Lie algebra of a form of signature (28, 4). For each m in
   {2, 8, 18, 24} the vectors e_m and K_a e_m, a in S, are seven distinct signed basis vectors on which K_a acts as
   the boost E_(0a) + E_(a0); the four modules use 28 distinct indices, and the common kernel of the K_a is
   H = span(e_0, e_10, e_16, e_26), a subalgebra that contains the time axis, with T = e_2 H. The generated algebra
   acts on each module through the standard generators of so(6,1) and has dimension 21 = dim so(6,1), so it is
   so(6,1), with the K_a as boosts and the [K_a, K_b] as rotations, and

       R^32 = 4 R^(6,1) + 4 R.
4. **Conjugate maps and the kernel** (`conjugate_maps`, `kernel_formula`). For m in {2, 8, 18, 24} the linear
   map Phi_m(y) = (t - K(x)) e_m satisfies, coefficient by coefficient,

       y Phi_m(y) = s_m (r^2 - t^2) e_m',    (m, m', s_m) = (2, 24, +), (8, 18, -), (18, 8, +), (24, 2, -).

   Each Phi_m embeds the slice in one vector module, where it reads (t, -x). The four vectors Phi_m(y) lie in
   orthogonal modules and are independent at every nonzero y. On the nonzero cone they are annihilated, and the
   nullity is 4 by statement 2, so

       ker L_y = (t - K(x)) T    for r^2 = t^2, y nonzero,

   each kernel vector is null for eta, and the kernel bundle over the punctured cone of the slice is trivial with
   the global frame Phi_2, Phi_8, Phi_18, Phi_24. Off the cone Phi_m(y) / Q(y) solves y w = s_m e_m'. The pair
   (x, e_10) of A_4 behind a slice point is orthogonal and imaginary with [a, a, b] = [a, b, b] = 0 in the cd_core
   product (`quaternionic_pair`), the hypotheses under which arXiv math/0511691, Proposition 11.1, describes the
   annihilator of a pair. That paper's doubling convention has not been compared with cd_core's, so the kernel is
   recorded as related to that proposition; the linear frame and its module structure are the content added here.
5. **Covariance** (`covariance`). The pairs (X, Y) of 32 x 32 matrices and generators w of so(6,1) acting on the
   slice with X L_y + L_y Y = L_(w y) for every slice point form a space whose projection onto w has dimension 8,
   inside the rotations; its projection onto the six boosts has dimension 0 (FLINT ranks of a 7168 x 2069 integer
   system). An independent argument gives the boost half: such a pair makes the logarithmic derivative of det L_y
   along w the constant trace(X + Y), and along the boost of the (t, x_1) plane that derivative is
   48 t x_1 / (r^2 + t^2). The multiplication operator of the slice is covariant under no boost. The so(6,1) of
   statement 3 is a different object: it acts on the 32-dimensional module with the defects as boosts, while the
   slice coordinates (x, t) enter L_y linearly without a boost symmetry.
6. **Tower control** (`tower_control`). The scan covers dimensions 16, 32 and 64 and every time axis e_(h+k) of
   the upper half (h the half dimension), with the clean set as space: the indices j below h with nullity 4 for
   e_j + e_(h+k) and e_j - e_(h+k). It has 51 slices with a clean set (7, 14 and 30). Every one has skew tables,
   defects of rank 8, the cubic relation and nullity 4 at a null point. Two properties separate the slices, and
   they are independent:
   - *Clifford space* (the spatial tables anticommute pairwise). Given skew tables and J^2 = -I, the Gram identity
     of statement 2 is a polynomial identity exactly when the space is Clifford, since its x_a x_b coefficients
     are the anticommutators. The space is Clifford on all 7 slices of dimension 16, all 14 of dimension 32 and none
     of the 30 of dimension 64; a point evaluation of the Gram identity agrees on every row.
   - *so(n,1) relations.* They hold on no slice of dimension 16 (42 of 90 fail; Lie dimension 15), on the seven
     slices of dimension 32 with time index 25 to 31 and on none with time index 17 to 23, and on the 15 slices of
     dimension 64 with time index 49 to 63: Lie dimension 36 = dim so(8,1) on 14 of them, and the 1274 relations
     of so(14,1) at time index 56.

   Among these full clean slices, those of A_5 with time index 25 to 31 are the only ones that carry both
   properties. The cone with a fourfold kernel exists at every level, the sedenions included.
7. **Star criterion** (`disjoint_stars` in every row). Each defect is a symmetric signed partial permutation of
   the basis. The slice has disjoint stars when the defects share one support T, K_a maps T onto a leaf set S_a,
   and the S_a are pairwise disjoint and disjoint from T. Disjoint stars make each K_a the boost E_(0a) + E_(a0) on
   span(e_m, K_b e_m : b) for m in T, which gives the relations of statement 3 and the isomorphism with so(n,1);
   on all 51 scanned slices the criterion holds exactly when the relations hold. The sedenion slice fails by
   counting, since four modules of dimension 7 need 28 basis vectors.
8. **Family controls** (`family_control`, `octonion_space_control`). Subslices outside the scan of statement 6:
   - The slice of A_n with time index 7 * 2^(n-3) and spatial indices 1 .. 2^(n-2) - 1 without 2^(n-3) has
     disjoint stars and satisfies the so(m,1) relations with m = 2^(n-2) - 2 for n = 4, 5, 6, 7 (2, 90, 1274 and
     13050 relations), with ranges spanning 2^n - 4 dimensions and a common kernel of dimension 4: so(2,1),
     so(6,1), so(14,1), so(30,1). Its space is Clifford for n = 4 and 5 only.
   - The slice of A_n with time index 2^(n-1) + 2^(n-2) + 8 and the seven octonion units as space has a Clifford
     space, the Gram identity, disjoint stars and the 147 relations of so(7,1), for n = 6 and 7.

   So the so(n,1) module of a slice with a Clifford space appears at A_4 on a two-direction subslice, at A_5 on a
   full clean slice, and at A_6 and A_7 on the octonion-space subslice.

## Relation to earlier records

- [Gram-operator witnesses](../a5-gram-operator-witnesses/README.md) ("Coefficients, embeddings and phase") gives the
  spectrum {(alpha + beta)^2: n, (alpha - beta)^2: n, alpha^2 + beta^2: D - 2n} for every two-support operand
  alpha e_i + beta e_j. Statement 2 extends it from one spatial direction to a six-dimensional space, where
  K(x)^3 = r^2 K(x) replaces the block count.
- Row A5-037 of the [exceptional-fibers ledger](../a5-exceptional-fibers/ledger.tsv) refutes a kernel lift of the
  split-coordinate boost by constant kernel-pencil symmetries. Statement 5 is a related negative result on this
  slice, for pairs (X, Y) acting on L_y.
- [a5-kernel-bundles](../a5-kernel-bundles/README.md) computes the K-theory of kernel bundles over strata; the
  frame of statement 4 concerns the cone of this slice only, and its relation to those bundles is open item 5.
- Rows A5-612 to A5-621 of the ledger carry these statements, one finding a row, with the open hypotheses.

## Relation to arXiv 2611.34924

V. Chandrasekaran, "An algebraic quantization of gravity from the null cone", arXiv 2611.34924v1 (2026-11-25),
quantizes the reduced phase space of four-dimensional vacuum gravity on intersecting null cones. Its canonical data
are the conformal metric with the shear along the generators (equation 3.39) and a corner boost charge equal to the
corner area over 8 pi G_N with its conjugate boost angle (equations 3.41 to 3.43); its Weyl relations are
equation 4.20, and its null states are a rank bound on a Gram matrix of fillings (equation 5.70). A reading of its
83 pages finds no Cayley-Dickson, octonion, Clifford or zero-divisor structure. The table states what the present
record establishes about a relation and what it leaves open.

| Statement | Class | Verdict |
| --- | --- | --- |
| A_5 contains a real slice whose zero divisors form a Lorentzian cone of signature (6,1), and (3,1) on any three of the six directions | computed | established (1) |
| The kernel over the punctured cone is (t - K(x)) T, four copies of the reflected null vector | computed | established (4) |
| The defects of the slice generate so(6,1) and split R^32 as 4 R^(6,1) + 4 R | computed | established (3) |
| The multiplication operator on the slice is Lorentz covariant | computed | refuted for every boost (5) |
| The operator pencil t J + sum x_a A_a is hyperbolic | computed | refuted: det has the roots t = +-i r (2) |
| The cone and its fourfold kernel distinguish A_5 in the tower | computed | refuted (6); what distinguishes A_5 is that a full clean slice carries a Clifford space together with the so(n,1) relations (6, 8) |
| The paper's phase space carries A_5 structure | hypothesis | no evidence; no map from its canonical data to slice data is known |
| The Gram bound 5.70 has the finite analogue rank(L_y^T L_y) = 32 - nullity | computed | holds for every real matrix; it carries no gravitational content |
| Corner boosts (equations 3.41, 3.61 to 3.64) correspond to the defects K_a | hypothesis | open; the corner charge of equation 3.43 is positive, while K(n) is traceless with eigenvalues -1, 0, 1 |

## Open items

1. A proof of statements 2 to 4 from the doubling formula, replacing the coefficient checks, and its Rocq
   formalization in gororoba-math `rocq/quantum`.
2. A proof of the star criterion as an equivalence. Both families of statement 8 hold for every n
   ([family proof](../a5-null-slice-family-proof/README.md)).
3. Done: the covariance algebra of the octonion-space slice of A_n is G_2, with no boost, for every n >= 6
   ([covariance blocks](../a5-null-slice-covariance/README.md)).
4. Done: the 8-dimensional covariance algebra of statement 5 is su(3), the stabilizer of e_2 in G_2
   ([covariance blocks](../a5-null-slice-covariance/README.md)).
5. The limits of the frame Phi_m along the larger cones of statement 1 into the nullity-12 rays, and their
   position in the kernel fibers of [a5-kernel-bundles](../a5-kernel-bundles/README.md).
6. Prior art for statement 3. The two sources cited in statements 2 and 4 cover the determinant and the kernel;
   no source for the so(n,1) relations of the defects has been found in the documents read, which bounds the
   novelty claim of this record to that reading.
Items 2 (n = 8 and beyond) and 7 have a successor in
[a5-null-slice-associator-envelope](../a5-null-slice-associator-envelope/README.md): the families to n = 12, and the
paper's corner boost as one abelian generator (ledger row A5-628).

7. Finite analogues of the paper's constructions, each a hypothesis with a cheap exact test: the finite boost
   exp(s K(n)) = I + sinh(s) K(n) + (cosh(s) - 1) K(n)^2 against the corner boost of equation 3.61; the matching
   condition of equation 3.64 as the joint kernel of K(n) x I - I x K(n) on a pair of modules exchanged by J; and
   the symplectic form <u, L_(e_2) v> on the six spatial directions as the input of a Weyl algebra in the sense of
   equation 4.20.
