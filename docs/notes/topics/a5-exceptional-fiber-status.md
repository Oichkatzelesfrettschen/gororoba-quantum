# A_5 exceptional fibers: goal, status by layer and open theorems

This page states what the A_5 fiber program is for, where each layer stands on 2026-11-23 by the claim ledger
([`ledger.tsv`](../../evidence/a5-exceptional-fibers/ledger.tsv), 585 rows), which theorems remain between the
record and the registry claim, and what the next computations and formal proofs are. The measurements and methods
live in [a5-exceptional-fiber-findings.md](a5-exceptional-fiber-findings.md) and in the evidence directories; this
page counts and orders them. It replaces the status of 2026-11-11 (313 rows), whose open items the rows named below
have since decided.

## The goal

A_5 here is the 32-dimensional Cayley-Dickson algebra (the pathions), not the alternating group. Its zero divisors
form strata by nullity, the dimension of the kernel of left multiplication. The open registry claim
`dimension32-global-topology` asks how those strata are glued: as a point of an orbit closure Y approaches a smaller
orbit Z, which kernels arise as limits. There are 33 incidences Y -> Z between the orbits: 14 from nullity 8 to
nullity 12 plus E8-bar -> VB, 8 from nullity 12 to nullity 16, and 10 from nullity 8 to nullity 16 (the fiber track:
X+, X-, Iso, W8 and E8-bar into N+ and N-). The program answers in four layers:

1. **Directions of approach, degree by degree.** The exceptional fiber of the blowup of Y along the
   kernel-coordinate ideal I at a point of Z has coordinate ring F(I), the fiber cone, with Hilbert function
   h_d = dim_k(I^d / m I^d).
2. **Directions of approach, all degrees at once.** F(I) = k[y] / K2 says the quadric relations K2 generate the
   whole relation ideal L.
3. **Characteristic 0.** The same statements over Q(i), not only over F_32009 and F_32029.
4. **The attaching datum.** The limiting kernel planes as a set of real points: every limit realized by a real arc
   and every other plane excluded, at every point of each boundary orbit, and compatibly along chains Y -> Z -> Z'.

## Status by layer (2026-11-23)

Ledger totals: 218 proved, 119 certified, 117 survives, 62 refuted, 37 superseded, 11 open, 10 stalled, 7 rejected, 4 boundary.
Reproduce with `"$PYTHON" docs/evidence/a5-exceptional-fibers/ledger.py --summary`.

| Layer | State | Deciding rows | Open |
|---|---|---|---|
| 1, per-degree h_d | complete at both primes for the six fiber classes | A5-001, A5-005 to A5-009, A5-335 (E8-bar degree 6, the last cell of the earlier count) | none |
| 2, F(I) = k[y] / K2 in every degree | complete at both primes: VB (A5-005, A5-015, A5-016), same-sign X (A5-304), Iso (A5-067), W8 (A5-066), E8-bar -> N+- on the header slices (A5-559) and by direct Rees saturation on the weight slice at all eight sign, prime and root cells (A5-572, A5-573, A5-587) | as listed | a receipt only: X+ -> N+ at 32009 has no retained K2 file (A5-304) |
| 3, characteristic 0 | all 33 incidences have a fiber cone over Q(i) on a retained slice: the 22 incidences of nullity 8 to 12 and 12 to 16 (A5-402, A5-405, A5-408), opposite-sign X (A5-270), same-sign X (A5-305), Iso, W8 and E8-bar into N+- on the weight slice (A5-446, A5-448, A5-457 with A5-474 and A5-475), and E8-bar -> VB (A5-597) | as listed | the map between the header slice and the weight slice for W8 and Iso (A5-598 gives it for E8-bar over Q(i)); the boost direction of the V and VB orbits |
| 4, real limit sets | proved on the retained slice germ at 26 of 33 incidences: 14 of nullity 8 to 12 (A5-411), 8 of nullity 12 to 16 (A5-412), the four X incidences into N+- (A5-417); G_2(C) x C^* equivariance moves the basepoint on B9, V^a+-, N+ and N- (A5-415) | as listed | E8-bar -> VB; Iso, W8 and E8-bar into N+- (A5-418, survives); the boost direction on V and VB (A5-419, survives); A5-250 stays open for these |
| Kernel bundles and gluing | nullity-8 ordinary classes computed (A5-396, survives); composed limits lie in linear sections (A5-420) | as listed | nullity-4 classification (A5-389, open); the flat-family clause of A5-420; the global attaching maps |
| Machine-checked | the algebra (signs, nullity doubling, two-term nullity, the G_2 derivation span) and the eight W8 arc-matrix ranks (gororoba-math `rocq/quantum/A5W8ArcMatrixRanks.v`) | A5-453, A5-500, A5-448 | no fiber-cone, Rees or Hilbert-function statement is formalized |

## Completion by incidence

D done, P partial, O open; the cell names the deciding row. Sign-conjugate incidences share a row.

| Incidence | Layers 1 and 2 | Layer 3 | Layer 4 |
|---|---|---|---|
| E8-bar, Iso, W8, X+- -> B9; X+ -> V^a+, X- -> V^a- (7) | D A5-402 | D A5-402 | D A5-411, A5-415 |
| E8-bar -> V (1) | D A5-402 | D A5-402 | P A5-411; boost open (A5-414) |
| X+-, Iso, W8 -> VB (4) | D A5-405 | D A5-405 | P A5-411; boost sampled (A5-419) and argued for every value (A5-603) |
| E8-bar -> V^a+- (2) | D A5-405 | D A5-405, A5-413 | D A5-411, A5-415 |
| E8-bar -> VB (1) | D A5-005 | D A5-597 at the retained basepoint; boost sampled modulo 32029 (A5-428) | O A5-250 |
| B9, V, VB -> N+-; V^a+ -> N+, V^a- -> N- (8) | D A5-408 | D A5-408 | D A5-412, A5-415 |
| X opposite sign -> N+- (2) | D A5-001 | D A5-270 | D A5-417 |
| X same sign -> N+- (2) | D A5-304 (X+ -> N+ at 32009 without a retained K2 file) | D A5-305 | D A5-417 |
| Iso -> N+- (2) | D A5-067 at N-, N+ by the sign isomorphism A5-013 | D on the weight slice, A5-446, A5-475 | P A5-418 |
| W8 -> N+- (2) | D A5-066 at N-, N+ by A5-013 | D on the weight slice, A5-448, A5-475 | P A5-418 |
| E8-bar -> N+- (2) | D A5-559, A5-587 | D on the weight slice, A5-457; induced slice map over Q(i), A5-598 | P A5-418 |
| Nullity-4 kernel bundles | not a fiber-cone question | | O A5-389 |

## What separates the record from the registry claim

| Theorem | Content | Missing |
|---|---|---|
| T1 | characteristic-0 fiber cones for all 33 incidences, independent of the transverse slice | for E8-bar, A5-598 computes the induced slice map over Q(i) and checks it at three primes; open: the same map for the W8 and Iso cells (X is decided on the header slice, A5-270 and A5-305), and a machine-checked form of the Pfaffian-ideal step that makes it the induced map |
| T2 | the fibers along each whole boundary orbit | for the four incidences of W8, Iso, X+ and X- into VB the ten-Pfaffian ideal is stable under the boost derivation modulo the closure ideal over Q(i) (A5-602), from which A5-603 argues that the fiber cone is constant along the boost in every degree (the argument is not machine-checked and rests on identifying each retained generating set with the ten-Pfaffian ideal); for E8-bar the ideal is not stable, so E8-bar -> VB rests on twelve sampled values (A5-600) and E8-bar -> V is undecided (A5-414, A5-605) |
| T3 | the two-sided real limit theorem at all 33 incidences (A5-250) | E8-bar -> VB; A5-418 for Iso, W8 and E8-bar into N+-; the boost direction |
| T4 | compatibility of composed limits 8 -> 12 -> 16 | the flat-family clause of A5-420 |
| T5 | classification of the kernel bundles | nullity 4 (A5-389; the degree-2 part of the Gauss images is measured at two primes, A5-460 and A5-601); the ordinary class in nullity 8 (A5-396) |
| T6 | the global attaching maps | not started; consumes T1 to T5 |
| T7 | formal certificates in gororoba-math | every fiber-cone statement |

Order: T1 feeds T2 and T3; T5 runs beside them; T1, T3 and T5 feed T4, then T6. T7 can certify each node when it
closes and removes the dependence on one computer-algebra system.

## Results of 2026-11-22

| Result | Row | Evidence |
|---|---|---|
| The eight E8-bar weight-slice cells by direct Rees saturation, the modulo colon, the conjugation map Phi and the closed forms of det B and the unit polynomials | A5-587 to A5-592 | [e8-rees-fibers-v3-open-cells](../../evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v3-open-cells/README.md) |
| An invertible 21 x 21 map carries the weight-slice quadric ideal of E8-bar onto the header-slice ideal, at N- and N+ modulo 32009; found through the maximal tori of the two symmetry algebras, verified by mutual reduction with two controls | A5-583, certified | [e8-slice-equivalence-p32009](../../evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/README.md) |
| Each of the 126 Pfaffian generators equals Pf(B)^3 times a 10-Pfaffian of T over Q(i), which derives the unit polynomials of A5-592; modulo 32009 the fourth factor of generators 10 and 16 comes from the 10-Pfaffian | A5-593, A5-594 | [e8-pfaffian-schur-identity](../../evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity/README.md) |
| E8-bar -> VB over Q(i): the 21 quadrics, K2 = P1 n P2, both arc families with rank 4 and a neighbor family of rank 2 as control, so L = K2 in characteristic 0 at the retained basepoint | A5-597 | [a5-char0-transfer](../../evidence/a5-char0-transfer/README.md) |
| The modular weight-slice cells of E8-bar -> N+ and Iso -> N- regenerate with the digests of the runs | A5-577, certified | [a5-kernel-attachments](../../evidence/a5-kernel-attachments/README.md) |
| The degree-2 receipt of the E8-bar -> N+ header at the second root 21255 of 32009: 148 relations, 0 failures, dimension 5, multiplicity 11 | A5-571, certified | [e8np-d2-receipt-p32009-r21255](../../evidence/a5-exceptional-fibers/working/runs/e8np-d2-receipt-p32009-r21255/README.md) |
| Reduced Hilbert numerators (1, 12, 10), (1, 18, 27, 4) and (1, 16, -12, 10, -5, 1); the E8-bar numerator as the sum of its two primes, their intersection and the nilradical module | A5-595 | [coefficient-structure](../../evidence/a5-exceptional-fibers/coefficient-structure/README.md) |
| The block splits of the last jump are the characters of a conic ring and of its Segre product with a nodal conic, with no twist; the characters leave the first conic nodal or smooth; a hypothesis for the final layer | A5-596, survives | the same |
The reviews that selected these computations, with each finding checked against the ledger, are in
[a5-fiber-status](../../archive/reviews/a5-fiber-status/reconciliation.md).

## Results of 2026-11-23

| Result | Row | Evidence |
|---|---|---|
| The map that the change of slice induces on the 21 generators of E8-bar -> N+-, over Q(i): each header Pfaffian is a constant combination of the weight-slice generators modulo J + m I, and the transported weight-slice ideal reduces to the retained header ideal at 32009 (both roots), 32029 and 32057, six cells of six, with three rejecting controls; that it is the induced map rests on a deduction in prose | A5-598, certified | [e8-induced-slice-map](../../evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map/README.md) |
| Macaulay2 1.25.11 reproduces the invariants, minimal primes, three primary components and nilradical data of the E8-bar quadric ideals on both slices and the primality of the Iso ideal, modulo 32009 | A5-599, certified | [quadric-ideals-macaulay2-p32009](../../evidence/a5-exceptional-fibers/working/runs/quadric-ideals-macaulay2-p32009/README.md) |
| E8-bar -> VB at twelve values of the boost parameter modulo 32029: the same invariants and one normal form of the quadric ideal | A5-600, certified | [e8-vb-boost-family-p32029](../../evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-family-p32029/README.md) |
| The ten-Pfaffian ideal is stable under the boost derivation modulo the closure ideals of W8, Iso, X+ and X- and not modulo that of E8-bar; on W8 and Iso the linear symmetries of the pair are G_2, the scaling and the boost | A5-602 proved, A5-603 survives, A5-604 certified, A5-605 stalled | [pfaffian-boost-derivation-stability](../../evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/README.md) |
| The degree-2 ranks 3,887 and 4,022 of the two open nullity-4 Gauss images at a second prime, from the kernel of the bordered matrix; the differential has rank 15 | A5-601, survives | [a5-kernel-bundles-residuals](../../evidence/a5-kernel-bundles-residuals/README.md) |

The review of these records is in [a5-induced-slice-map](../../archive/reviews/a5-induced-slice-map/reconciliation.md).

## Results of 2026-11-26: a Lorentzian slice of A_5

[a5-null-slice-boost-algebra](../../evidence/a5-null-slice-boost-algebra/README.md) restricts the strata invariants
to the real slice y = sum x_a e_a + t e_26, a in {1, 3, 4, 5, 6, 7}, where Q = r^2 - t^2 is a Lorentzian form. Every
row below is an exact check of `scripts/a5_null_slice_boost_algebra.py --check`; statuses are those of the ledger.

| Row | Statement | Status |
|---|---|---|
| A5-612 | L_y^T L_y = (r^2 + t^2) I + 2 t K(x) with the Clifford defect K_a = -(A_a J + J A_a)/2, K(x)^3 = r^2 K(x), spectrum 4, 24, 4 and det L_y = (r^2 - t^2)^4 (r^2 + t^2)^12; the zero divisors of the slice are the cone r^2 = t^2 at nullity 4 | proved |
| A5-613 | the six defects satisfy the so(6,1) relations (90 relations, Lie dimension 21); R^32 is four Minkowski vector modules on T = span(e_2, e_8, e_18, e_24) plus the common kernel H = span(e_0, e_10, e_16, e_26), with T = e_2 H | proved |
| A5-614 | on the cone, ker L_y = (t - K(x)) T, from y (t - K(x)) e_m = +-(r^2 - t^2) e_m'; the four vectors frame a trivial kernel bundle over the punctured cone | proved |
| A5-615 | the covariance algebra has dimension 8, inside the rotations; no boost acts covariantly on L_y | proved |
| A5-616 | over the 51 clean slices of dimensions 16, 32 and 64 the cone and the fourfold kernel exist at every level; only the seven slices of A_5 carry both a Clifford space and the so(n,1) relations | proved |
| A5-617 | the relations hold exactly when the defects have disjoint stars | survives |
| A5-618 | two families: so(2^(n-2) - 2, 1) at time index 7 * 2^(n-3), computed for n = 4 to 7, and so(7,1) on the octonion-space slice, computed for n = 6 and 7; proved for every n ([family proof](../../evidence/a5-null-slice-family-proof/README.md)) | proved |
| A5-619 | the covariance algebras are su(3) on A_5 and the G_2 derivations on the octonion-space slice of A_n for every n >= 6 (A5-640) ([covariance blocks](../../evidence/a5-null-slice-covariance/README.md)) | proved |
| A5-620 | a bracket-preserving map from the corner boost data of arXiv 2611.34924 (equations 3.41 to 3.43, 3.61 to 3.64) to (P_T, K_a) | superseded by A5-628 |
| A5-621 | the Lorentzian cone with a fourfold kernel distinguishes A_5 in the tower | refuted |

The second record, [a5-null-slice-associator-envelope](../../evidence/a5-null-slice-associator-envelope/README.md)
(`scripts/a5_null_slice_associator_envelope.py --check`), adds:

| Row | Statement | Status |
|---|---|---|
| A5-622 | 2 K_a is the symmetrized left associator of e_a and e_26, and L_y^T L_y = N(y) I + [y, y, .]: the Gram identity of A5-612 is the norm plus the left associator, an elementary identity | proved |
| A5-623 | over F_32009 and F_32003 the slice meets three null strata: nullity 4 on r^2 = t^2, 12 on r^2 + t^2 = 0 (y^2 = 0 there, and Q != 0, outside the real containment of nullity 12 in V(Q) n V(G)) and 16 on r^2 = 0 with t = 0; the bound 12 holds over every field of characteristic 0 or above 32 | certified |
| A5-624 | the seven slice tables generate M_16(R) (dimension 256, commutant M_2(R)); R^32 is two copies of one irreducible 16-dimensional module | proved |
| A5-625 | U_8 = L_(e_2) D_8 completes A_a, J eta to eight anticommuting units whose monomials span the envelope: the image of Cl(0,8) | proved |
| A5-626 | both families hold from dimension 256 to 4096, by direct relation checks at 256 and 512 and by disjoint stars above; A5-637 adds direct checks of the first family at 1024, 2048 and 4096; the proof of A5-636 covers every n | proved |
| A5-627 | the 225 two-term pairs of A_5 split 15, 84, 126 at nullity 0, 4, 12; every nullity-4 pair has strut above 8 | proved |
| A5-628 | the paper's corner boost is one unitary one-parameter group; no non-abelian Lorentz algebra appears | boundary |
| A5-629 | complex two-term operands of anticommuting tables have Gram 2 (I - i L_a L_b): kernels are eigenspaces of Hermitian involutions, nullity half the dimension; on the slice the Euclidean-cone kernel is ker K_1 n ker(i L_1 J - I) | proved |
| A5-630 | the kernel map with selector phase i and orientation phases +-i s_k reads N = 16 and N = 12 on the complex strata in an exact statevector; plain +-i reads -14 and -2 ([record](../../evidence/a5-complex-kernel-map/README.md)) | proved |
| A5-631 | the complex map reads the nullity over C on all 465 pairs of A_5, and it is the real map with two S gates and the same cz count | proved |
| A5-632 | a Heron device reads 16 and 12 with the complex map | open |
| A5-633 | the left tables of A_n have scalar commutant for n = 3 to 10 and generate M_(2^n)(Q) ([census](../../evidence/a5-left-table-census/README.md)) | proved |
| A5-634 | (D - 2)(D - 4)(D + 6)/2 ordered basis triples have nonzero associator, D = 4 to 1024 | certified |
| A5-635 | nullity 12 on the Euclidean cone over Q(sqrt(-d)), d = 1, 2, 3, 5, 6, 7, 11, and at 10 Q_p points | certified |
| A5-636 | the families of A5-618 reduce to one commutation-set lemma, proved for every n by the cd_sign recursion (Lemmas T, U and the peel R) | proved |
| A5-637 | the first family's relations hold by direct check at n = 10, 11 and 12, every level to 4096 ([record](../../evidence/a5-null-slice-family-relations/README.md)) | proved |
| A5-640 | the octonion-space covariance algebra is G_2 with no boost for every n >= 6: derivations extend (inside), four anchor cosets with n-independent signs intersect in G_2 (outside) ([covariance blocks](../../evidence/a5-null-slice-covariance/README.md)) | proved |

What the slice changes for the program:

- **The prediction that failed.** The script first required the so(n,1) relations in dimension 32 alone; the scan
  refuted it with 15 slices of dimension 64 (time index 49 to 63). The family predictions for levels 4 and 7 and for
  the octonion-space slices at levels 6 and 7 were written before their first run and held, up to so(30,1) in
  dimension 128.
- **A closed-form kernel frame.** A5-614 gives the nullity-4 kernel on the cone as an explicit linear frame in the
  coordinates. It is related to the open nullity-4
  classification A5-389, whose Gauss map is certified only at fixture level; the frame does not meet the statement of
  that row.
- **The paper.** arXiv 2611.34924 contains no Cayley-Dickson, Clifford or zero-divisor structure, and its boost is
  one abelian generator (A5-628); the slice is an exact algebraic testbed beside it.
- **Prior art.** The two-term case x = e_a, t = +-1 is known: Skiouris, Aphanics at the pathion level (2026),
  Proposition 2.2 and Proposition 3.1, states the nullity-4 stratum and the spectrum 0, 2, 4 at multiplicities 4, 24,
  4 with e_1 + e_26 as canonical representative. The determinant agrees with arXiv 2608.08232 Theorem 5.3; the
  kernel is related to arXiv math/0511691 Proposition 11.1, whose hypotheses the record checks. The extension to the
  whole seven-dimensional slice, the so(n,1) relations of the defects, the envelope and the families have no source
  in the documents read.
- **Hardware.** e_1 + e_26 is the cone point x = e_1, t = 1. The full kernel map on ibm_fez left it unresolved (23 of
  32 signs); the coset-block map read N_hat = 4.25 on ibm_fez and 4.28 on ibm_marrakesh, 4.02 and 4.05 after readout
  correction, with 32 of 32 signs ([findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)).
- **Machine-checked.** The two-term kernels, e_a + e_26 included, are formal in gororoba-math
  (`rocq/quantum/CdTowerTwoTermNullity.v`, `lean/GororobaMath/CayleyDickson/TwoTermNullity.lean`); the
  multi-direction statements A5-612 to A5-618 and A5-622 to A5-626 are not formalized.

## Next computations

| Layer | Computation | Decides | Estimate from retained timings |
|---|---|---|---|
| T1 | `induced_slice_map.py` with the header selections of W8 and Iso, each checked against its retained header relation files | the slice map of the four W8 and Iso cells into N+- | 5 s a map and about 70 s a relation script for E8-bar (A5-598) |
| T2 | the relations of E8-bar -> VB over F_p(w), by interpolation in w from point runs or a standard basis with a degree bound, then the arc certificate of A5-597 along the family; the same for the incidences into V | fibers along the whole orbit | 11 s a point (A5-600); the direct standard basis over F_32029(w) reached a 4 h limit at 1.5 GiB; the derivation test of A5-602 takes 9 min over Q(i) and leaves E8-bar alone |
| T3 | the closure argument of A5-417 on the weight-slice fiber cones over Q(i) for Iso, W8 and E8-bar, which needs no header slice, then the product theorem for the boost direction | A5-418, A5-250 | symbolic; unmeasured |
| T5 | the degree-3 part of the Gauss images in Gr(2, 15) and the image of z -> K(z), then charts and transition functions over the moduli | A5-389 | degree 2 takes 4 min at 2.9 GiB for 7,000 points (A5-601); the degree-3 monomials on 105 coordinates number 198,485 |
| A5-596 | retain the final-layer quotient of an existing degree (an engine change) and test the multiplication of the conic model, which also decides nodal against smooth for the first conic | A5-278, A5-596 | minutes at d = 2, 3 once the engine writes the quotient |
| Independence | the W8 quadric ideal and the Q(i) ideals in Macaulay2; the relation computations themselves in a second system | the single-engine risk that A5-599 leaves | 1 min 45 s for five ideals modulo 32009 (A5-599) |

## Formal proof targets (gororoba-math)

Build order, smallest trusted base first. Each lands as a statement, a proof and a comparator configuration under
`lean/Challenge/` or as a source under `rocq/quantum/`, with the computer-algebra system reduced to a producer of
certificates that the kernel checks.

| Order | Target | System | Certifies |
|---|---|---|---|
| 1 | the conjugation map Phi as a ring automorphism of Z[i][s1..s9] with its three matrix identities, and det B in closed form | Rocq | A5-591, A5-592 |
| 2 | the Pfaffian identity Pf_4(det(B) D + X^T adj(B) X) = Pf(B)^3 Pf_10(T) for a skew matrix with a 6 x 6 block B, over a commutative ring | Lean | A5-593 in general |
| 3 | the left-inverse rank certificate extended from Z[i] to its fraction field (the W8 arc ranks); for E8-bar and Iso no arc matrices enter: A5-457 and A5-475 rest on the rank of the Jacobian matrix of an initial-form map V at a rational point (a nonzero maximal minor with its inverse), the vanishing of each prime's generators on V, and the order inequalities of the weight vector | Rocq | the prose step of `A5W8ArcMatrixRanks.v` (A5-448); A5-457, A5-475 |
| 4 | a checker of sparse polynomial cofactor identities q(G) = sum a_k J_k + sum b_ij s_i P_j | Rocq | K inside L (A5-474) from exported cofactors |
| 5 | a checker that a linear substitution carries one finite set of quadrics into the span of another, with the inverse | Rocq | A5-583 from `bridge-CELL.json` |
| 6 | the splitting ker C_z = C z + ker A(z, conj z) | Lean | the mechanism of A5-411 and A5-412 |
| 7 | the lemma that K inside L inside rad K, a rank-one torsion-free nilradical module and a separating order function give L = K | Lean | A5-457 without a primary decomposition by machine |
| 8 | fiber cone, Rees special fiber, Hilbert series and multiplicity | Lean | the statement layer of every row above |

## Weakest links

- **One computer-algebra system.** Ideal, radical, saturation and primary-decomposition claims rest on Singular
  4.4.1; Macaulay2 reproduces the invariants of five quadric ideals modulo 32009 (A5-599), and the relation
  computations that produce the ideals run in Singular alone. Replays on a second host test determinism, not the
  algorithm. The symmetry-algebra numbers 34 and 6 of
  A5-583 are computed in python-flint and agree with the Singular-based rows A5-347 and A5-424; the L = K argument
  of A5-457 depends on `primdecGTZ` returning every associated prime.
- **Slice dependence.** A row marked characteristic 0 for Iso, W8 or E8-bar into N+- is a statement on the weight
  slice. A5-598 joins the two E8-bar presentations over Q(i) by the induced map; its identification of the relation
  ideals is a deduction in prose, and W8 and Iso have no such map yet.
- **Basepoint dependence.** On V and VB the group G_2(C) x C^* misses the boost direction, so a result at the
  retained basepoint is a result at that point of the orbit. A5-603 argues the dependence of the fiber cone away for W8, Iso, X+ and X- into VB, subject to its identification step; limiting kernel planes are not covered. A5-600 samples twelve
  values of the boost for E8-bar -> VB and decides no general value.
- **Ledger wording.** A5-005 to A5-009 read proved with primes `both`: they are modular statements, and the
  characteristic-0 forms are the rows of the table above.
