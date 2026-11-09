# A_5 exceptional fibers against the Cayley-Dickson tower: conjectures, falsification, survivors (2026-11-09)

Scope. This report reads the A_5 exceptional-fiber program (`docs/notes/topics/a5-exceptional-fiber-findings.md`,
`docs/evidence/a5-exceptional-fibers/ledger.tsv`, `.../forecasts/trends-2026-11-06.md`,
`docs/archive/reviews/findings-deep/`, the strata records `docs/evidence/a5-zero-divisor-strata/` and
`docs/evidence/a5-strata-regularity/`, the producer `docs/evidence/a5-kernel-attachments/`, the retained headers under
`docs/evidence/a5-exceptional-fibers/working/build/inputs/`, `gororoba_quantum/cd_core.py`, `proofs/`) against the
Cayley-Dickson (CD) tower H (4D), O (8D), sedenions (16D), pathions (32D). No tracked file changed. Evidence labels:
**measured** (a retained record or a run of this session on exact integer data), **computed** (a run of this session;
floating point where stated), **hypothesis**.

## 0. Naming collision that has to be named first

The "A_5" of this program is the 5th CD algebra, the 32-dimensional pathions (`cd_core` dimension 32), not the
alternating group of order 60. "E8" and "E8-bar" are labels of an orbit family: the strata record names the pieces W8,
E8, V, B9, N+-, with the letter E and nullity 8 (`docs/evidence/a5-zero-divisor-strata/README.md`, piece table:
"E8 | the G_2-orbit family of {u' = a n + b e, ...}"), not the Lie algebra E8. Any link to the icosahedral group, the
binary icosahedral group, the McKay correspondence or the E8 lattice therefore has no mechanism at the level of names,
and it is tested below at the level of structure (conjecture C9).

## 1. What the analysis looks for

A claim enters the survivors only when it carries a mechanism (a theorem, a proved identity or a computed structure
that forces the number), a prediction made before the check ran, and a falsifier that a stated cheap computation
decides. A match of one small number (4 = 4, 24 = 24, 240 = 240) counts as unsupported until a second independent match
or a mechanism exists. The analysis looks for three kinds of structure: (a) symmetry of the fiber problems that the
CD sign structure forces and that refines the 4-block character grading; (b) tower-level laws (nullity spectrum,
doubling) that tie the A_5 strata to A_3 and A_4; (c) a representation-theoretic origin of the measured ladders (last
jumps (2d+1)^2, closing orders 3d+1 and floor(7d/2)+1). The method is conjecture, cheap decisive check, verdict.

## 2. Atoms: the measured invariants and their sources

All values are F_p statements (p = 32009, and 32029 where the note says so); sources are the findings note unless
named.

| Atom | Value | Source |
|---|---|---|
| Hilbert function h_d, X (X-, X+ by sign pair) | 15, 51, 122, 240, 417, 665 | note "Methods" table, "What survives", roadmap 1 |
| Iso | 17, 85, 265, 640, 1316, 2422 | same |
| E8-bar -> N+- | 21, 83, 225, 495, 952 (d = 6: lower bound 1526, K2 count 1666) | same, `n18-laptop/` |
| W8 -> N+- | 24, 156, 600, 1725, 4116, 8624, 16416 (d >= 6 from the C30 proof, A5-066) | same |
| E8-bar -> VB | 10, 34, 80, 155, 266, 420 (the Hilbert function of h-vector (1, 6) in Krull dimension 4) | same, k2-hilbert |
| Germ Krull dimension (projective dimension + 1) | X 4, Iso 5, E8-bar -> N 5, W8 6, VB 4; equals dim Y minus dim Z | note "Pairs"; `EXPECTED_GERMS` in `a5-strata-regularity/strata_regularity.py` |
| K2 degree and projective dimension | X (3, 12), Iso (4, 23), W8 (5, 20 + 30), E8-bar -> N (4, 11) and (3, 4), VB (3, 3) and (3, 4) | note "Structure of K2" |
| h-vectors | VB (1, 6); Iso (1, 12, 10); W8 (1, 18, 27, 4) | note "Cohen-Macaulay" |
| Last jump into the K2 count | (2d+1)^2 on Iso, W8, X, with block split (2 floor(d/2)+1)^2, d(d+1), rest in halves; E8-bar follows a different law, (5d+2)(d+1)/2 at the top stratum | A5-244, trends section 1.3 |
| Closing order N | 3d + 1 (Iso, W8); floor(7d/2) + 1 (X through d = 6; E8-bar through d = 5) | note "What survives" |
| Diagonal sign group | Klein four-group; flip sets (t2,t4,t6), (t2,t5,t7), (t4,t5,t6,t7) on W8, X-, Iso; (t2,t4,t6,t8), (t2,t5,t7,t8), (t4,t5,t6,t7) on E8-bar -> N+-; (t1,t3,t4,t7), (t1,t5,t6,t7), (t3,t4,t5,t6) on E8-bar -> VB | note "Diagonal sign group" |
| Generator character counts | W8 (6, 7, 7, 4); Iso (4, 5, 5, 3) | same |
| Strict-transform chart of E8-bar -> VB at t7 = 1 | prime, dimension 4; `normal()` 2,298 s; one ring of 12 variables, 284 relations | `working/build/arc/chart_t7.log` (RESULT lines) |
| Nullity values of A_5 | 0, 4, 8, 12, 16 | pathion-kernel-map README |

## 3. Computations run in this session

Every script is a scratch script (not retained); the recipes are in section 7. The floating-point stabilizer
computations pick a generic algebra element; the scratch scripts used fixed generator seeds and deterministic
square-root-of-prime coefficient streams, which departs from the repository seed rule for retained records (no seed
is retained or cited). Every reported quantity is a dimension, rank, weight multiset or irrep content that came out
identical across the coefficient choices tried (two fixed seeds and the deterministic streams that gave a 3-dimensional
Cartan subalgebra; two streams gave a 4-dimensional generalized zero space of ad, which marks a non-generic element,
and were discarded). The exact replay over Q in section 6 (item 1) removes the dependence.

### 3.1 The Klein group is the stabilizer of the base point in the diagonal automorphisms

Mechanism (proved identity). `basis_mul` in `proofs/CdImaginarySumConference.v` gives e_a e_b = sigma(a, b) e_(a xor b),
so for every character chi of (Z/2)^n the map e_a -> chi(a) e_a is an automorphism of A_n (numerical check, level 3 to
6: 0 violations of chi(a) chi(b) = chi(a xor b) in 512, 4,096, 32,768 and 262,144 triples). The kernel matrix is
C_z[r][c] = z[r xor c] sigma_16(r xor c, c) (`holomorphic_kernel_lemma._c_matrix`), so C_(chi z) = D_chi C_z D_chi,
D_chi = diag chi, and the kernel coordinates (Pfaffians) of the slice at a base point p transform by characters. The
cone structure adds the scalar -1. The group that fixes p is {(s, epsilon) in (Z/2)^4 x {+-1} : epsilon chi_s(k) = 1 on
supp p}, with chi_s(k) = (-1)^popcount(s AND k) on the split indices k = 1..15.

Derivation. The N+- base point (`REPS["Nm"]`, support {1, 3, 9, 11}, a coset of the index span
{0, 2, 8, 10}) has stabilizer of order 4, with elements (s, epsilon) = (1, -1), (4, 1), (5, -1). With the producer's
slice columns for N+- (1..9, `regularity.transverse_columns`), the predicted flip sets on t1..t9 are
{2,4,6,8}, {4,5,6,7}, {2,5,7,8}.

The flip sets of the note were known before the derivation, so this is a derivation checked against known data and
not a blind prediction. Result (computed). The three derived sets equal the measured flip sets of E8-bar -> N+- exactly; with t3 and t8
eliminated by the presolve they equal (t2,t4,t6), (t4,t5,t6,t7), (t2,t5,t7) of W8, X- and Iso. The check applied to every
retained header at p = 32009 (`working/build/inputs/p32009-r10754/`, files w8-nm, w8-np, xm-nm, xp-np, xp-nm, xm-np,
iso-nm, iso-np, e8-nm, e8-np): every J and G generator is a pure character vector under the predicted group (0 impure
generators among all of them); generator counts per character reproduce the note, W8 {6, 7, 7, 4} and Iso {4, 5, 5, 3}
as multisets. Because the note's exhaustive search found no other sign flips, the derived group equals the observed
group on the nine-variable N+- slice.

E8-bar -> VB reproduces once the producer's own boundary point is used. The row of the first-order record that
feeds the VB header (`first-order-normal-cones-result.json`, incidence E8bar->VB) has boundary point
(0, -2, -2, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0) (support {2, 3, 10, 11}, not the census point (n, 0, 0)) and slice
columns 1, 3, 4, 5, 6, 7, 8, 10 (1-based). The stabilizer of that support has order 4, and the derived flip sets
{1,3,4,7}, {1,5,6,7}, {3,4,5,6} equal the measured VB group exactly; the same pure-character test on `e8-vb.sing`
finds exactly these three flip sets and no other. A first attempt with the census point (n, 0, 0) and the standard VB
column order predicted a group of order 8 that contains none of the measured sets (it would have to flip t1, a
shifted coordinate with p != 0, which the derivation forbids), so the sign group depends on the base-point
representative the producer used and not on the orbit alone; the header's own row is the authority.

Verdict for C1: survives (computed) on all six fibers into N+- and VB.

### 3.2 The stabilizer carries a torus and an SL(2) that no diagonal test could see

Setup (computed, double precision, residuals below 1e-9). The 16 tangent generators of H = G_2(C) x SO(2, C) x C^*
(`h_generators`) were built as 15 x 15 matrices from `strata_regularity.DERS`. At the N- base point:

- the stabilizer algebra in H has dimension 10 (orbit dimension 6, as the strata record states); its Cartan subalgebra
  (generalized zero space of ad of a generic element) has dimension 3 and acts diagonalizably on C^15; the 15 weights
  are pairwise distinct; the torus T has rank 3;
- the 6 orbit-tangent weights and 9 normal weights separate; on the 9-dimensional normal space N = C^15 / T_orbit the 9
  weights of T are distinct, and a one-parameter subgroup of T with all 9 normal weights positive exists (linear feasibility on the 9 weights, a
  half-space test that does not depend on the weight basis);
- the identity C(Bz) = B C(z) - C(z) B holds exactly (max error 0) for the 14 derivations B of the split table, so the
  kernel matrix, hence the kernel-coordinate ideal I, is equivariant under G_2(C) x C^*; the boost fails it (error 7.6 to 77 over
  the choices of z) and a random matrix fails it (error 27 to 12,000), which matches the kernel-bundle record ("the split boost has no lift");
- restricted to the kernel-compatible subgroup (no boost) the stabilizer has dimension 9 and a torus T' of rank 2;
  its 9 normal weights form 7 distinct values, two of them occurring twice, with one zero weight (the weight vectors
  depend on the basis; this multiplicity pattern was the same for every coefficient choice);
- the stabilizer contains an SL(2) inside G_2 (sl2 triple built from the one opposite root pair of ad, the boost
  coefficient of E and F is 0, |[E,F] - H| = 7e-15, E p = F p = H p = 0); ad of a generic element has 3 zero and 7
  nonzero eigenvalues (the SL(2) pair and five more; the nilradical dimension 5 is inferred, not computed). Under this
  SL(2), C^15 = 4 V_1 + 7 V_0, the normal space N = 2 V_1 + 5 V_0, the kernel K = ker C_p (9-dimensional) =
  3 V_1 + 3 V_0, and each of u' and v' carries 7 = 2 V_1 + 3 V_0 with mu' trivial. By the standard branching
  G_2 > SU(2) x SU(2), 7 = (3,1) + (2,2), this is the SU(2) factor of SO(4) = Stab(H) that acts on the complement of a
  quaternion subalgebra in O = H + H l and trivially on Im H, that is the complexified unit-quaternion group Sp(1)
  (computed check of the identification: the SL(2)-fixed subspace of u' has dimension 3 and, together with e'_0, closes
  under the split-octonion product `eq.omul` with associator 3e-15, i.e. a 4-dimensional associative subalgebra; this
  replicates the standard structure of the stabilizer of a null vector of the 7-dimensional G_2 module, a parabolic
  whose Levi contains the long-root SL(2)). The quaternionic 4D layer of the tower is therefore present in the fibers as
  this SL(2);
- the Klein group and the torus. The two-torsion T'[2] of the computed T' has eigenvalue -1 on exactly 4 of the 9
  normal weights and on 8, 7, 7 of the 15 ambient weights, the same sign statistics as the Klein elements (which flip
  4, 4, 4 of 9 slice coordinates and 8, 7, 7 of 15). The statistics are a necessary condition only: the three diagonal
  Klein matrices in split coordinates do not commute with the computed Cartan of H nor with T' (max commutator 1.0 to
  1.4), so the Klein group is not T'[2] of that torus. The centralizer of the Klein group in the 10-dimensional
  stabilizer algebra is 3-dimensional and abelian, and its generic element has 11 distinct eigenvalues on C^15 (four
  doubled), so a torus compatible with the Klein blocks exists only inside that centralizer and may have smaller
  rank than 3 (a nilpotent central element is possible). Whether a weight grading refines the four character blocks in
  common coordinates is open;

Consequence (hypothesis, testable). In a slice spanned by weight vectors of T (instead of coordinate directions), J is
weight-homogeneous for T because Y is H-invariant and the slice is T-invariant; a contracting one-parameter subgroup
exists, so the germ (Y, N-) is quasi-homogeneous with positive weights and the local jet computations equal graded
computations in a weighted polynomial ring. I is homogeneous for T' (weights above, with one zero weight, so a
non-negative but not strictly positive grading). Falsifier: any J generator with two distinct T-weights, or any G
generator with two distinct T'-weights, in a weight-adapted slice. The existing diagonal-scaling test (Smith form
1, ..., 1, 2, 2) is silent on this because in coordinate slices T acts non-diagonally.

Verdict for C2 (the four blocks are the reduction mod 2 of a weight grading): the sign statistics match and the
commutation test fails for the computed torus, so C2 is not established and stays open; C3 (hidden T, T', SL(2)) is
computed; its consequences (finer blocks, quasi-homogeneity) are untested.

### 3.3 Tower nullity spectra and the doubling rule

cd_core sign table, exhaustive over supports, entries +-1; ranks computed exactly with `flint.fmpz_mat.rank` (a float SVD
run gave identical counts); the A_5 two-term counts equal `two_term_nullity_counts` of
`docs/evidence/pathion-kernel-map/census.json` (0: 342, 4: 168, 8: 168, 12: 252):

| Level (dimension) | Operand class | Nullity: count |
|---|---|---|
| A_3 (8) | 1 to 4 terms | 0 only |
| A_4 (16) | 2 terms (210 operands) | 0: 126; 4: 84 |
| A_4 | 4 terms | 0: 9,156; 4: 1,764 (3 terms: 0 only) |
| A_5 (32) | 2 terms (930) | 0: 342; 4: 168; 8: 168; 12: 252 |
| A_5 | 4 terms | 0: 153,188; 4: 64,512; 8: 25,872; 12: 7,980; 16: 168 (3 terms: 0 only) |
| A_6 (64) | 2 terms (3,906) | 0: 870; 4: 504; 8, 12, 16, 20: 336 each; 24: 504; 28: 684 |

Reading (computed, exact ranks). Nonzero nullities are multiples of 4 at levels 4 to 6; two-term operands reach at most
2^(n-1) - 4 (4, 12, 28); the 84 two-term sedenion operands of nullity 4 match the "84 first operands" of
`docs/notes/algebra_circuit_rules.md` (line 48). Doubling rule: for the 420 two-term operands (a, 0) and (0, a) of A_5
built from two-term a of A_4, nullity(A_5) = 2 nullity(A_4) with 0 violations (consistent with the left-nullity doubling of PR 266 and the zero-lower-half companion of roadmap item 11 of the
findings note). No count has a pattern beyond these; 168 = |GL(3, 2)| and 84 = 168 / 2
are unsupported coincidences until a mechanism appears.

### 3.4 Falsification checks on numerology and ring identifications

- Small-number base rate. Of the 30 values h_d for d <= 6 across the five fibers, 5 equal a number from a list of 39
  tower-flavored constants (powers of two and neighbors, 12, 24, 48, 60, 120, 168, 192, 240, 336, 672, 7, 14, 21, 28, 35,
  56, 84, 252): 15, 17, 21, 24, 240. Shifting every value by k = -8..8 (k != 0) gives 1 to 6 hits (mean 3.4). The
  observed 5 is inside the null spread. Verdict: 240 = h_4(X) = 240 roots of E8 and 24 = h_1(W8) = 24 Hurwitz units are
  unsupported.
- 24 distinct weights. The 126 principal 4-Pfaffian coordinates (Lambda^4 K) carry exactly 24 distinct T'-weights (6 weights occur once, 4 twice, 3 four times, 5 six times, 2 nine times and 4 thirteen times). The tempting reading h_1(W8) = 24 (one generator
  per weight) predicts the four Klein classes of the 24 weights to hold (6, 7, 7, 4) generators; they split (6, 6, 6, 6)
  (126 forms: 33, 33, 27, 33). Refuted.
- Chart dimension 4. The t7 = 1 chart is the strict transform of a prime germ of dimension 4 (E8-bar -> VB germ is
  (4, 2, 7)); a strict transform has the dimension of the variety, so "dimension 4 = quaternions" holds by
  construction and carries no tower content.
- Last jump (2d+1)^2 as a bigraded ring. The closed form reproduces all six measured splits (1,2,3,3), (9,6,5,5),
  (9,12,14,14), (25,20,18,18), (25,30,33,33), (49,42,39,39). A search over tensor products of up to 6 variables with
  Z2^2 weights on each variable, degree functions in {d, 2d, d-1, 2d-1, 2d+1, d+1, 2d-2}, factor shapes (2,2), (3,1),
  (3,2), (3,3), (2,3), (4,2), (4,1), finds 0 matches (so P^1 x P^1 at bidegree (2d, 2d), the box
  k[x, y]/(x^(2d+1), y^(2d+1)) and Segre-Veronese variants are excluded, consistent with the Grok finding in
  `docs/archive/reviews/findings-deep/`). Restricting a spin-d irrep of SO(3) to its Klein subgroup gives
  (0,1,1,1), (1,1,1,2), (1,2,2,2), ... : wrong. The SL(2) of 3.2 bounds the highest weight of a degree-d class by 3d
  (Lambda^4 K has highest SL(2)-weight 3), while V_(2d) tensor V_(2d) has weight 4d, so the top stratum is not the
  SL(2) tensor square. The closed form itself is the parity count of the lattice box [-d, d]^2: with E = 2 floor(d/2) + 1 even and O = 2d + 1 - E
odd coordinates, block 0 is E^2, block 1 is E O = d(d + 1) for every d, and blocks 2 and 3 are the two halves of the
O (2d + 1) points with odd first coordinate. This holds for every d by counting, so a description of the splits by a
mod-4 twisted parity of the box (which splits the odd rows into equal halves) agrees with all six d without being
evidence for a structure. A lattice homomorphism to Z2^2 cannot produce the equal halves (every such map gives the
four plain parity classes, (9,6,6,4) at d = 2), which is the one informative fact: the top stratum is not graded by a
box under a mod-2 lattice map.

## 4. Conjecture table

| # | Conjecture | Mechanism | Falsifier (cheap) | Check run | Verdict |
|---|---|---|---|---|---|
| C1 | The Klein sign group is the stabilizer of the N+- base point in (Z/2)^4 x {+-1}, i.e. a CD character effect | `basis_mul`; C_(chi z) = D C D; flip sets follow from supp p and slice columns | a pair into N- whose flip sets differ from {2,4,6,8}, {4,5,6,7}, {2,5,7,8} (restricted to surviving variables), or an impure generator | derived from support and slice columns, then compared with the note; 11 headers (10 into N+-, 1 into VB), 0 impure generators; flip sets equal the measured ones, VB included once the row's own base point is used | survives (computed) on all six fibers |
| C2 | The four blocks are the mod-2 reduction of a finer torus grading; Klein = 2-torsion of a torus of the stabilizer | reductive stabilizer; commuting involutions lie in a torus | sign statistics of T'[2] differ from the Klein flips, or the Klein matrices commute with the torus | statistics match; the Klein matrices do not commute with the computed Cartan or T'; Klein centralizer is a 3-dimensional abelian algebra | open: not established for the computed torus |
| C3 | The stabilizer of N- has a rank-3 torus (rank 2 kernel-compatible), 9 distinct normal weights, a contracting 1-PS for J, and an SL(2) Levi factor | H-orbit geometry; G_2 equivariance of C_z | torus rank or weights differ in an exact replay over Q; a weight-slice J or G generator with two weights | torus, weights, sl2 triple, equivariance identity computed in floating point | survives (computed); consequence untested |
| C4 | The tower's quaternion layer is the Levi SL(2) = Sp(1)_C of the stabilizer; the (7,1,7) split is O + l + l O | G_2 = Aut(O), SO(4) = Stab(H), branching 7 = (3,1) + (2,2) | SL(2) not trivial on a 3-dimensional subspace of each C^7 | u' = v' = 2 V_1 + 3 V_0, mu' trivial; fixed 3-space plus e'_0 closes as an associative 4-dimensional subalgebra | survives (computed, floating point); standard G_2 parabolic structure replicated |
| C5 | Nullity spectra recur up the tower (multiples of 4; two-term maximum 2^(n-1) - 4; doubling rule) | left-nullity doubling (roadmap item 11 of the findings note) and the sign involutions `sigma_left_involution`, `sigma_right_involution` in `proofs/CdImaginarySumConference.v` | a level-6 operand with nonzero nullity not divisible by 4; a doubling violation | levels 3 to 6 two-term exhaustive, level 4 and 5 four-term exhaustive, exact ranks; 420 doubling cases; A_5 counts equal `census.json` | survives (computed, exact); no count pattern beyond it |
| C6 | Closing orders 3d+1 (Iso, W8) and floor(7d/2)+1 (X, E8-bar) come from the order of the top generator classes | generator m-adic orders 2 and 3 (Iso, W8); E8-bar and X carry an order-7 class in degree 2 (T(d) = T(d-2) + 7) | X- degree 7 closing at N other than 25 | measured through d = 6 (X) and d = 5 (E8-bar), no new run | survives as a measured law; mechanism hypothesis |
| C7 | Last jump (2d+1)^2 = dimension of V_(2d) tensor V_(2d), or P^1 x P^1 at bidegree (2d, 2d) | none identified | any ring model with Z2^2 weights reproducing the splits | 0 matches in the model search; SL(2) weight bound 3d against 4d | refuted in these forms; the lattice-box parity description with a mod-4 twist fits and carries no mechanism |
| C8 | The last jump depends only on the target base point (N-) | same normal weights for every fiber into N- | a fiber into N- with a different last-jump law | E8-bar -> N- has last jumps 55 (d = 4), 81 (d = 5), a different law | refuted (fibers with the same base point differ); X, Iso, W8 share it because they share the order-3 generators |
| C9 | A link to the icosahedral group, the binary icosahedral group 2I, the McKay correspondence and E8 | none: A_5 is the algebra; E8 is a piece label; SL(2) in the stabilizer contains 2I, but every finite subgroup of SL(2) acts the same way, and the germ table has no E-type singularity (the only multiplicity-2 surface germ in C^3, E8-bar along B9, has tangent quadric of rank 3, an A_1 singularity) | an action of 2I that distinguishes it from other finite subgroups of SL(2); a germ with a rank-1 tangent quadric in C^3 | germ table of the record read against `EXPECTED_GERMS` | refuted as a mechanism; the name overlap is accidental |
| C10 | Numerology: h_4(X) = 240, h_1(W8) = 24, chart dimension 4, 12 variables, 9 slice variables = 9 nodes of affine E8 | none | the shifted-value null and the weight-class split | shifted null mean 3.4 hits against 5 observed; (6,6,6,6) against (6,7,7,4); strict transform dimension is automatic | unsupported / refuted |
| C11 | Dimension chain: nullities 4, 8, 12, 16 and orbit dimensions 10 to 12, 8, 7, 6 follow the sizes 4, 8, 16, 32 | orbit dimensions are dim Y - dim Z from G_2 x C^* geometry on C^7 + C + C^7; N+- is the 6-dimensional null cone of C^7 | any pair of tower dimensions entering a germ dimension | germ dimensions are differences of H-orbit dimensions; no tower dimension enters | unsupported: the tower enters through G_2 = Aut(O) and the index group (Z/2)^4, not through 16 or 32 |
| C12 | The analogue of the A_5 fiber structure at level A_6 repeats with the same group G_2 and a (Z/2)^5 character group | Aut(A_n) contains G_2 for n >= 3 and (Z/2)^n diagonal | nullity strata or stabilizer of an A_6 base point with a different Levi factor | not run (needs the A_6 strata census; reason: no A_6 strata record exists) | untested |
| C13 | Quasi-homogeneity of the germs lets the Singular export (97 percent of E8-bar and X- cost) run as a weighted-homogeneous standard basis | contracting 1-PS exists for J (3.2) | the weighted std of J in a weight slice at X- N = 17 takes longer than the retained 201 s, or J is not weight-homogeneous | not run (reason: needs the weight-adapted slice, section 6, item 1) | untested |

## 5. What survives

- The Klein four-group of diagonal sign changes is a CD character effect. It is the stabilizer of the base point N+-
  in the diagonal automorphism group of the pathions times scalars (computed; mechanism proved by `basis_mul`), it
  explains why the same group appears on every pair into N+-, and it fixes the character of each slice variable in
  advance (t8 flips with t2 only where t8 survives the presolve). The group depends on the base-point representative
  the producer row uses (N+- with support {1, 3, 9, 11}; the VB row with support {2, 3, 10, 11}).
- The stabilizer of the nullity-16 base point carries a rank-3 torus (rank 2 compatible with the kernel structure) and
  a quaternionic SL(2) acting as 2 V_1 + 3 V_0 on each octonionic block (computed, floating point; the SL(2) fixes a
  quaternion subalgebra of the split octonions pointwise). The tower enters through this structure and through the
  sign cocycle: H (4D) gives the SL(2), O (8D) gives G_2 and the C^7 module, A_4 supplies the 7 + 1 + 7 doubling, A_5
  supplies the (Z/2)^4 characters. It predicts that the germs of the nullity-8 closures along N+- are quasi-homogeneous
  for the torus of H and that every fiber cone into N+- carries a weight grading beyond degree (untested; section 6).
- The nullity spectra and the doubling rule hold up the tower (computed, exact ranks).
- The ladders (last jumps, closing orders) stay measured laws; their origin is open.

Refuted or unsupported: McKay, icosahedral and E8 links; every single-number match; the weight-class reading of
h_1 = 24; V_(2d) tensor V_(2d) and P^1 x P^1 models of the top stratum; the claim that the last jump depends only on the
target base point; "dimension 4 of the chart" as a tower fact.

## 6. Next decisive computations, ranked by information per hour

| Rank | Computation | Decides | Host class | Cost |
|---|---|---|---|---|
| 1 | Exact replay over Q (and at p = 32009) of the stabilizer torus with rational coefficients: pick the torus inside the centralizer of the Klein group, rational weight basis of the 9 normal directions, regenerate J and G for W8 -> N- (smallest) and X- through a successor slice function (a linear, weight-adapted slice; the digest-bound producers keep their bytes), test T-homogeneity of J and homogeneity of G | C2, C3 and their consequences; whether weight blocks beyond the four character blocks exist | laptop CPU | 1 to 3 h including the successor function; the polynomial phase is flint, minutes |
| 2 | Weighted standard basis of J in the weight slice (Singular, ordering a(w), dp, global) for X- at N = 17 against the retained 201 s, then E8-bar -> N- at N = 11 against 3,535 s | C13: whether the export bottleneck (97 percent of E8-bar and X- wall) disappears | OCI 2-core 9.5 GiB (Singular only) or laptop CPU | minutes per case after item 1 |
| 3 | Weight-block rank engine pilot: split the closure and ranks of `fiber_rank` engine v11 by weight (acceptance: W8 degree-4 ranks byte-equal to the retained 1,725 and per-weight ranks add up) | whether degree 6 and 7 for E8-bar, X and W8 become laptop-sized | laptop CPU, then laptop GPU only after the CPU form wins | 1 to 2 days of engineering |
| 4 | Kernel-plane limits along the arcs (roadmap item 9), organized by SL(2) orbits: one arc per orbit class, normalized by weight | whether the limiting 8-planes form SL(2)-orbits, which would settle path dependence cheaply | laptop CPU | hours |
| 5 | X- degree 7 closing order (predicted N = 25) and E8-bar -> VB degree 7 | C6, the 7/2 law | laptop CPU | hours to a day |
| 6 | A_6 base-point stabilizer and nullity census at the analogous points | C12: whether the mechanism is tower-wide | laptop CPU | hours |

No computation in the list needs a GPU, a Kaggle session or a paid VM before item 3 succeeds. The engine v12 GPU path
shortens the products and closure stages and does not help the export-bound fibers (E8-bar, X-); items 1 and 2 test
whether a graded formulation removes that bound.

## 7. Recipes (scratch scripts, not retained)

- Klein prediction: import `strata_regularity` (`REPS["Nm"]`, `transverse_columns`), form the stabilizer as above, flip
  sets on slice columns; header purity: parse each polynomial in `working/build/inputs/p32009-r10754/*.sing`, assign
  each monomial the parity of the exponent sum over flipped variables.
- Stabilizer: 14 matrices from `strata_regularity.DERS` acting on u' and v' alike, scaling, boost; nullspace of
  sum c_i A_i p; Cartan from the generalized zero space of ad(x) for a generic x; simultaneous diagonalization; normal
  weights from eigenvectors outside the orbit tangent space; kernel K from `holomorphic_kernel_lemma._c_matrix` at the
  original coordinates z = i^popcount z'.
- Spectra: `cd_core.cd_sign` table, L_v[k, j] = v[k xor j] sigma(k xor j, j), exact rank by `flint.fmpz_mat.rank`.
- Falsification of ring models: enumerate tensor products of symmetric powers with Z2^2 weights, compare block counts
  as multisets with the six measured splits.
