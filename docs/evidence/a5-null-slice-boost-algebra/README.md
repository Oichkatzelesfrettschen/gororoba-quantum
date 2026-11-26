# A Lorentzian slice of A_5: Clifford-defect operators, so(6,1) relations and the kernel on the null cone

`result.json` is the output of [`scripts/a5_null_slice_boost_algebra.py`](../../../scripts/a5_null_slice_boost_algebra.py)
`--out`. The record restricts the zero-divisor invariants of
[the rank-strata classification](../a5-zero-divisor-strata/README.md) to a real seven-dimensional slice of A_5 on which
the quadratic invariant is a Lorentzian form, and determines the left-multiplication operators on that slice exactly.
Every decision is an identity of integer matrices or a FLINT rank over Z; no random draw enters and every test point is
an explicit integer vector. `--check` recomputes the record and `--self-test` runs eight mutation controls in
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

Each statement is computed: an exact check of the record, named in parentheses.

1. **Invariants** (`invariants`). On the slice Q = r^2 - t^2, Delta = -r^2 t^2 and G = (r^2 + t^2)^2. The zero
   divisors of the slice are the cone r^2 = t^2, all of nullity 4. Adding the direction e_2 or e_8 keeps the cone as
   the zero-divisor set, since G = ((t - s)^2 + r^2)((t + s)^2 + r^2) with s the added coordinate, and raises the
   nullity to 12 on the rays r = 0, s = +-t (`real_slice_nullities`: e_2 + e_26, e_8 + e_26 and
   3 e_2 + 4 e_8 + 5 e_26 have nullity 12).
2. **Gram identity** (`operator_identities`, `determinant`). L_y^T L_y = (r^2 + t^2) I + 2 t K(x). Each K_a is
   symmetric, integer, traceless and of rank 8, and K(x)^3 = r^2 K(x) on all 56 cubic coefficients, with
   trace K(x)^2 = 8 r^2. Hence K(x) has eigenvalues r, 0, -r with multiplicities 4, 24, 4, the Gram operator has
   eigenvalues (r + t)^2, r^2 + t^2, (r - t)^2 with the same multiplicities, and

       det L_y = (r^2 - t^2)^4 (r^2 + t^2)^12.

   The square of the determinant follows from the spectrum, and the sign from the value 1 at y = e_1; six exact
   integer determinants agree with the formula.
3. **Boost algebra** (`boost_algebra`). The defects satisfy

       [[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b    (90 relations),

   and the Lie algebra they generate has dimension 21 over Q: the K_a are the six boosts and the 15 commutators
   [K_a, K_b] the rotations of so(6,1). The product K_a^2 K_b^2 is the same diagonal projector P_T for all 15 pairs,
   onto T = span(e_2, e_8, e_18, e_24), and every K_a anticommutes with eta = I - 2 P_T, so the defects lie in the
   orthogonal Lie algebra of a form of signature (28, 4). For each m in {2, 8, 18, 24} the vectors
   e_m, K_1 e_m, .., K_7 e_m are seven distinct signed basis vectors on which K_a acts as the boost
   E_(0a) + E_(a0); the four modules use 28 distinct indices, and the common kernel of the K_a is
   span(e_0, e_10, e_16, e_26). As a module of this so(6,1),

       R^32 = 4 R^(6,1) + 4 R,

   with T = e_2 H for H = span(e_0, e_10, e_16, e_26), the four-dimensional subalgebra that contains the time axis.
4. **Conjugate maps and the kernel** (`conjugate_maps`, `kernel_formula`). For m in {2, 8, 18, 24} the linear
   map Phi_m(y) = (t - K(x)) e_m satisfies, coefficient by coefficient,

       y Phi_m(y) = s_m (r^2 - t^2) e_m',    (m, m', s_m) = (2, 24, +), (8, 18, -), (18, 8, +), (24, 2, -).

   Each Phi_m embeds the slice in one vector module, where it reads (t, -x): the reflected point. On the cone the
   four vectors Phi_m(y) are independent and annihilated, so

       ker L_y = (t - K(x)) T    for r^2 = t^2, y nonzero,

   and each kernel vector is null for eta. Off the cone Phi_m(y) / Q(y) solves y w = s_m e_m'.
5. **Covariance** (`covariance`). The pairs (X, Y) of 32 x 32 matrices and generators w of so(6,1) acting on the
   slice with X L_y + L_y Y = L_(w y) for every slice point form a space whose projection onto w has dimension 8,
   inside the rotations; its projection onto the six boosts has dimension 0 (FLINT ranks of a 7168 x 2069 integer
   system). An independent argument gives the boost half: such a pair makes the logarithmic derivative of det L_y
   along w the constant trace(X + Y), and along the boost of the (t, x_1) plane that derivative is
   48 t x_1 / (r^2 + t^2). The slice carries the Lorentzian cone and an 8-dimensional rotation symmetry; the
   multiplication operator is covariant under no boost.
6. **Tower control** (`tower_control`). For every time axis e_(h+k) of dimensions 16, 32 and 64 (h the half
   dimension) the clean set holds the spatial indices j below h with nullity 4 for e_j + e_(h+k) and e_j - e_(h+k).
   Every clean slice has defects of rank 8, the cubic relation and nullity 4 at a null point. Two properties then
   separate the slices, and they are independent:
   - *Clifford space* (the spatial tables anticommute pairwise). The Gram identity of statement 2 holds on a slice
     exactly when its space is Clifford: on all 7 clean slices of dimension 16, all 14 of dimension 32 and none of
     the 30 of dimension 64.
   - *so(n,1) relations.* They hold on no slice of dimension 16 (42 of 90 fail; Lie dimension 15), on the seven
     slices of dimension 32 with time index 25 to 31 and on none with time index 17 to 23, and on the 15 slices of
     dimension 64 with time index 49 to 63: so(8,1) (Lie dimension 36) on 14 of them and 1274 relations of
     so(14,1) at time index 56.

   Among the full clean slices of the three levels, those of A_5 with time index 25 to 31 are the only ones that
   carry both properties. The cone with a fourfold kernel exists at every level, the sedenions included.
7. **Star criterion** (`disjoint_stars` in every row). Each defect is a symmetric signed partial permutation of
   the basis. The slice has disjoint stars when the defects share one support T, K_a maps T onto a leaf set S_a,
   and the S_a are pairwise disjoint and disjoint from T. Disjoint stars make each K_a the boost E_(0a) + E_(a0) on
   span(e_m, K_b e_m : b) for m in T, which gives the relations of statement 3; on all 44 scanned rows with a clean
   set the criterion holds exactly when the relations hold. The sedenion slice fails by counting, since four
   modules of dimension 7 need 28 basis vectors. The criterion and its counting argument come from the red-team
   review of this record (Gemini 4 Neon); the script checks them independently.
8. **Family controls** (`family_control`, `octonion_space_control`). Two families, each with its prediction written
   into the script before the first run:
   - The slice of A_n with time index 7 * 2^(n-3) and spatial indices 1 .. 2^(n-2) - 1 without 2^(n-3) satisfies
     the so(m,1) relations with m = 2^(n-2) - 2 for n = 4, 5, 6, 7 (2, 90, 1274 and 13050 relations), with ranges
     spanning 2^n - 4 dimensions and a common kernel of dimension 4: so(2,1), so(6,1), so(14,1), so(30,1). Its
     space is Clifford for n = 4 and 5 only.
   - The slice of A_n with time index 2^(n-1) + 2^(n-2) + 8 and the seven octonion units as space has a Clifford
     space, the Gram identity, disjoint stars and the 147 relations of so(7,1), for n = 6 and 7 (the reviewer's
     conjecture, verified by the reviewer at n = 6 and here at both levels).

## Proof sketches the checks support

- *Isomorphism type.* By statement 3 the algebra generated by the K_a acts on each of the four modules as the
  standard generators E_(0a) + E_(a0) and their commutators, preserving a form of signature (6,1), and acts as zero
  on the common kernel. The representation is therefore the direct sum of four copies of the vector representation
  of so(6,1) and a trivial part, and the generated algebra is isomorphic to so(6,1).
- *Conjugate identity* (reviewer's derivation, each step among the checked coefficients). For m in T,
  A_a J e_m = J A_a e_m, so K_a e_m = -J A_a e_m, hence J K(x) e_m = L_x e_m and L_x K(x) e_m = r^2 J e_m, and
  L_y (t - K(x)) e_m = (t^2 - r^2) J e_m.
- *Kernel bundle over the cone.* The four sections Phi_m are linear in y, independent at every nonzero point of
  the slice (their modules are orthogonal), and span the kernel on the cone. The kernel bundle of the slice cone is
  therefore trivial with an explicit global frame, in contrast with the nontrivial bundles over the strata of
  [a5-kernel-bundles](../a5-kernel-bundles/).

## Relation to earlier records

- [Gram-operator witnesses](../a5-gram-operator-witnesses/README.md) ("Coefficients, embeddings and phase") gives the
  spectrum {(alpha + beta)^2: n, (alpha - beta)^2: n, alpha^2 + beta^2: D - 2n} for every two-support operand
  alpha e_i + beta e_j. Statement 2 extends it from one spatial direction to a six-dimensional space, where
  K(x)^3 = r^2 K(x) replaces the block count.
- Row A5-037 of the [exceptional-fibers ledger](../a5-exceptional-fibers/ledger.tsv) refutes a kernel lift of the
  split-coordinate boost. Statement 5 is the same phenomenon on this slice, decided for all six boosts at once.

## What the statements correct

A prior informal analysis of this slice stated the Gram identity, the 4, 24, 4 spectrum, the determinant and the
non-hyperbolicity of the operator pencil (the roots t = +-i r of the determinant). Statements 1 and 2 confirm those
by exact computation. Three of its readings change:

- The cone and its fourfold kernel exist in dimensions 16, 32 and 64 (statement 6), so they distinguish no level
  of the tower. The structure that first appears at A_5 is the so(6,1) module of statement 3: the sedenion slice
  with six directions fails 42 of the 90 relations, and the module recurs above A_5 (statement 8).
- Lorentz equivariance of the multiplication operator on the slice is decided, and negative for every boost
  (statement 5). The so(6,1) of statement 3 is a different object: it acts on the 32-dimensional module with the
  defects as boosts, and its vectors are the kernel directions, while the slice coordinates (x, t) enter L_y
  linearly without a boost symmetry.
- The identity ker(L^T L) = ker L holds for every real matrix and supports no analogy by itself. The content of
  statement 4 is the explicit kernel (t - K(x)) T and the first-order identity y Phi_m(y) = s_m Q(y) e_m'.

## Relation to arXiv 2611.34924

V. Chandrasekaran, "An algebraic quantization of gravity from the null cone", arXiv 2611.34924v1 (2026-11-25),
quantizes the reduced phase space of four-dimensional vacuum gravity on intersecting null cones. Its canonical data
are the conformal metric and shear along the generators and the corner area with its conjugate boost
(equations 3.39 to 3.45); its null states are a rank bound on a Gram matrix of fillings (equation 5.70, page 50).
A full reading of its 83 pages finds no Cayley-Dickson, octonion, Clifford or zero-divisor structure. The table
states what the present record establishes about a relation and what it leaves open.

| Statement | Class | Verdict |
| --- | --- | --- |
| A_5 contains a real slice whose zero divisors form a Lorentzian cone of signature (6,1), and (3,1) on any three of the six directions | computed | established (1) |
| The kernel over the cone is (t - K(x)) T, four copies of the reflected null vector | computed | established (4) |
| The defects of the slice generate so(6,1) and split R^32 as 4 R^(6,1) + 4 R | computed | established (3) |
| The multiplication operator on the slice is Lorentz covariant | computed | refuted for every boost (5) |
| The operator pencil t J + sum x_a A_a is hyperbolic | computed | refuted: det has the roots t = +-i r (2) |
| The cone and its fourfold kernel distinguish A_5 in the tower | computed | refuted (6); the so(n,1) module first appears at A_5 and recurs at A_6 and A_7 (6, 8) |
| The paper's phase space carries A_5 structure | hypothesis | no evidence; no map from its canonical data to slice data is known |
| The Gram bound 5.70 has the finite analogue rank(L_y^T L_y) = 32 - nullity | computed | holds, as a statement of linear algebra with no gravitational content |
| Corner boosts (equations 3.41, 3.61 to 3.64) correspond to the defects K_a | hypothesis | open; the cheapest test is a bracket-preserving map from the pair (corner area, relative boost) to (P_T, K_a) |

## Open items

1. A proof of statements 2 to 4 from the doubling formula, replacing the coefficient checks, and its Rocq
   formalization in gororoba-math `rocq/quantum`.
2. A proof of the star criterion as an equivalence, and of both families of statement 8 for every n from the
   bit structure of the time index.
3. The covariance algebra of the octonion-space slices of statement 8; hypothesis: all 14 derivations of G_2 act,
   since they fix e_8, e_16 and e_32. The exact system has 32768 x 8220 entries at n = 6.
4. The identification of the 8-dimensional covariance algebra of statement 5 with su(3), the stabilizer of e_2 in
   G_2 acting on the six directions (the reviewer reports the eight lifted derivations satisfy it; unverified
   here).
5. The four-dimensional subalgebra H and the role of T = e_2 H in the kernel bundle over the cone; the relation of
   (t - K(x)) T to the kernel bundles of [a5-kernel-bundles](../a5-kernel-bundles/).
6. Prior art. The reviewer names, as leads to verify against the page, Biss, Dugger and Isaksen, "Large
   annihilators in Cayley-Dickson algebras" (2008) for the kernel of statement 4 as an annihilator of a pair of
   alternative elements, and arXiv 2608.08232 for a determinant factorization related to statement 2; it reports
   no source for the so(n,1) relations of the defects. No page of either paper has been read for this record, so
   its novelty claim is bounded by the code and records of this repository.
7. Finite analogues of the paper's constructions that the reviewer proposes, each a hypothesis with a cheap exact
   test: the finite boost exp(s K(n)) = I + sinh(s) K(n) + (cosh(s) - 1) K(n)^2 against the corner boost of
   equation 3.61; the matching condition of equation 3.64 as the joint kernel of K(n) x I - I x K(n) on a pair of
   modules exchanged by J; and the SU(3)-invariant symplectic form <u, L_(e_2) v> on the six spatial directions
   as the input of a Weyl algebra in the sense of equation 4.20.
