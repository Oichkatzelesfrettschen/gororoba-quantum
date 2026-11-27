# A_5 null slice: connections, formal targets and the next computations

This program note joins the two null-slice records
([boost algebra](../evidence/a5-null-slice-boost-algebra/README.md), ledger rows A5-612 to A5-621;
[associator envelope](../evidence/a5-null-slice-associator-envelope/README.md), rows A5-622 to A5-630; the [complex kernel map](../evidence/a5-complex-kernel-map/README.md), rows A5-630 to A5-632) to the rest of
the repository. Each connection names its mechanism, evidence class, status and falsifier. Status uses the ledger
words; "no link found" records a search with its scope.

## First principles, in order

1. **Signs.** `cd_core.cd_sign` fixes e_p e_q = s(p, q) e_(p XOR q). Each left table L_(e_k) is a signed
   permutation, skew for k != 0, with square -I.
2. **Anticommutation and the associator.** Distinct imaginary units anticommute, so the symmetrized left associator
   of e_a and e_t equals -(L_a L_t + L_t L_a) = 2 K_a (A5-622). For imaginary y, L_y^T L_y = -L_y^2 = N(y) I + [y, y, .]:
   the Gram operator is the norm plus the left associator (Moreno's L^2 = -G).
3. **The slice.** On y = sum x_a e_a + t e_26 the associator is linear in x and t, 2 t K(x), and K(x)^3 = r^2 K(x)
   gives the spectrum 4, 24, 4 and det L_y = (r^2 - t^2)^4 (r^2 + t^2)^12 (A5-612).
4. **Lie structure.** Disjoint stars make each K_a a boost on four seven-dimensional modules (A5-613, A5-617), and the
   same mechanism runs to dimension 4096 (A5-626).
5. **Strata.** L_y^2 = -(r^2 + t^2) I - 2 t K(x) decides the kernels: nullity 4 on the Lorentzian cone over the
   reals, and over F_p also 12 on the Euclidean cone, where y is nilpotent (y^2 = 0), and 16 on the null space of
   the spatial form (A5-623).
6. **Envelope.** The seven tables generate M_16(R), with seven anticommuting units inside (A5-624, A5-625).

## Connections

| Area | Mechanism | Evidence class | Status | Falsifier or next check |
|---|---|---|---|---|
| Zero-divisor strata (Biss, Dugger and Isaksen) | the slice meets the annihilator dimensions 4, 12 and 16 of A_5, and misses 8 | computed over F_32009, F_32003 (A5-623) | certified | a slice point of nullity 8 over any field |
| Two-term pairs (Skiouris Proposition 2.2) | x = e_a, t = +-1 gives the nullity-4 stratum; the record recounts all 225 pairs and checks the index criterion on each | documented and computed (A5-627) | proved | none |
| de Marrais struts | every nullity-4 two-term pair has strut s > 8, the range `demarrais_structures.py` marks sparse (`is_dmz_sparse`); the slice uses the struts 9, 11 to 15 | computed (A5-627) | proved for the implication; the full 4-versus-12 rule is Skiouris's | a nullity-4 pair with s <= 8 |
| Quantum runs | the coset-block map read e_1 + e_26 at N_hat = 4.25 and 4.28 (4.02 and 4.05 after readout correction) on two Heron r2 devices; the full map left it unresolved; the module's aligned pairs are the support of K_1 | measured (`results/live/PATHION_KERNEL_MAP_FINDINGS.md`) | measured | a retained replica outside the reported interval |
| Tower to 4096 | both families hold from 256 to 4096 | computed (A5-626, A5-637) | direct relation checks at every level to 4096 for both families | a sign row that differs from cd_core; stars that meet |
| Clifford and Cayley-Dickson | the six spatial tables, J eta and U_8 = L_(e_2) D_8 are eight anticommuting units whose monomials span the envelope M_16(R), the image of Cl(0,8); gororoba-math's Lean `Clifford/ZeroEight.lean` maps Cl(0,8) to 16 x 16 matrices from sedenion tables | computed (A5-624, A5-625) | proved | none |
| Cayley-Dickson and Lie | defects close on so(m,1); covariance algebras su(3) and G_2 | computed (A5-613, A5-619) | proved: the octonion-space covariance algebra is G_2 at every n >= 6 (A5-642) and the A_5 one the e_2 stabilizer su(3) ([covariance blocks](../evidence/a5-null-slice-covariance/README.md)) | a covariant generator outside the derivations |
| Nilpotents | y^2 = 0 on the Euclidean cone; L_y is square-zero on ker K(x) there and L_y^2 = 0 on the null space | computed over F_p (A5-623) | certified | a Euclidean-cone point with L_y^2 of rank other than 8 |
| p-adic fields | the seven-variable form is isotropic over every Q_p, so the Euclidean cone has Q_p points, where nullity >= 12 holds (characteristic 0) | cited theorem and the README argument | the bound proved; equality a hypothesis | the nullity at a Q_p point by a Hensel lift of an F_p point |
| Albert and Jordan algebras | the chain su(3) in G_2 in F_4 = Der(J_3(O)) would join the slice covariance (A5-615, A5-619) to the Albert algebra; dim Der(J_3(O)) = 52 over F_32009 and F_32003 was computed in review ([review record](../archive/reviews/a5-null-slice-associator-envelope/review.md)) and is not recorded | computed in review | hypothesis | a recorded derivation count other than 52 over Q, or a covariance algebra outside G_2 |
| Hopf algebras and fibrations | Adams's Hopf-invariant-one theorem closes sphere fibrations past the octonions; Hopf algebras were searched only in the document manifests | documented (fibrations); read (manifests, algebras) | fibrations closed; algebras unsearched | a coproduct compatible with the slice tables |
| arXiv 2611.34924 | one abelian unitary boost generator | read on pages 28 and 39 (A5-628) | boundary | a non-abelian boost algebra in the paper |

## Proved for every dimension, and checked only up to a bound

| Statement | By argument (scope in the cell) | Finite checks |
|---|---|---|
| 2 K_a = symmetrized associator; Gram = N(y) I + [y, y, .] (A5-622) | yes: anticommuting distinct units and L_y^T = -L_y | dimensions 16, 32, 64 |
| Gram of L_(e_a + i e_b) = 2 (I - i L_a L_b) for anticommuting tables, nullity half the dimension (A5-629) | every dimension: the Witt-basis identity and trace H = 0 | identity, trace and kernel on every anticommuting pair at 16, 32, 64 |
| nullity(e_a + i e_b) = D/2 - nullity(e_a + e_b) for two-term operands (A5-629) | every dimension: the sector split of singular_sector_dynamics.md read on S+ and S- | all 465 pairs of A_5 |
| Gram identity, spectrum, determinant, so(6,1) relations, kernel frame, covariance on the A_5 slice (A5-612 to A5-615) | yes for that slice: polynomial or matrix identities checked exactly | the A_5 slice only |
| nullity >= 12 on the Euclidean cone (A5-623) | yes, over fields of characteristic 0 or above 32 | equality at two primes, seven Q(i) points, six other imaginary quadratic fields and 10 Q_p points (A5-635) |
| Disjoint stars imply the so(m,1) relations (A5-617) | the sufficient direction | the converse on 51 slices and the families |
| The two families carry so(m,1) (A5-618, A5-626, A5-636, A5-637) | every n: the commutation-set lemma (L_a and L_tau commute exactly on T u (T ^ a ^ tau)) from the cd_sign recursion ([family proof](../evidence/a5-null-slice-family-proof/README.md)), then disjoint stars | lemma at n = 4 to 12; the first family: direct relations to 4096; the octonion-space family: direct relations to 4096 |
| Octonion-space covariance algebra is G_2 for every n >= 6 (A5-642) | derivation extension (inside); four anchor cosets with n-independent signs (outside) | anchor tables and block signs n = 6 to 12; full coset intersection n = 6 to 10 |
| Left tables of A_n generate M_(2^n)(Q) for n >= 3 (A5-633) | from scalar commutant and closure under transposition | commutant n = 1 to 10 |
| (D - 2)(D - 4)(D + 6)/2 non-associating ordered basis triples (A5-634) | open | D = 4 to 1024 |
| Envelope M_16(R) and Cl(0,8) of the seven slice tables (A5-624, A5-625) | the A_5 slice (exact ranks) | dimension 32 only; other levels unchecked |
| Two-term strata 15, 84, 126 and the strut criterion (A5-627) | A_5 (exhaustive) | other dimensions unchecked |

## Hardware observables for the complex strata

The nullity-12 and nullity-16 strata need complex or modular coefficients, so a real operand on the device never
reaches them; their kernels are still eigenspaces of operators the devices already compile. When the tables L_a and
L_b anticommute, L_a L_b is a skew signed XOR permutation with square -I, so i L_a L_b is a Hermitian involution whose
+1 eigenspace is the kernel of L_(e_a + i e_b) (A5-629): the nullity-16 point e_1 + i e_3 is that case. L_1 and J do not
anticommute: on the 8-dimensional support of K_1 the product L_1 J squares to +I and i L_1 J is not Hermitian there,
and the involution property holds only after restriction to ker K_1, where the Euclidean-cone kernel of
L_(e_1 + i e_26) is ker K_1 n ker(i L_1 J - I), with K_1 the symmetric part of the module's signed permutation
L_1^T L_26.

- The kernel map of `gororoba_quantum/pathion_kernel_map.py` with the selector phase i (an S gate) in place of the
  sign t = -1, and orientation phases +-i s_k on the upper pair members (s_k the pair sign of L_i^T L_j), reads
  N = 16 at e_1 + i e_3 and N = 12 at e_1 + i e_26, against N = 4 at e_1 + e_26 and 0 at e_1 + e_3; plain +-i reads
  -14 and -2 (A5-630, proved by exact statevector in the
  [complex kernel map record](../evidence/a5-complex-kernel-map/README.md)). The oracle phase t s_k puts t^2 = -1
  into the pair interference, so the map counts misaligned pairs, which the complement law equates with the nullity
  over C; the record checks it on all 465 pairs (A5-631). The complex map is the real one with two S gates and the
  same cz count.
- hypothesis (A5-632): a Heron device reads 16 and 12 with the complex map. Falsifier: corrected estimates that
  exclude them. A device run needs its own written case.

## Formal targets and the prover for each



gororoba-math holds Lean 4.35 with Mathlib (pinned `56a005855ea1`) and Rocq 9.3 with MathComp 2.6. An Agda
cross-check of the octonion Moufang loop is in preparation there under an owner decision of 2026-11-26; it runs on
demand and no gate reads it.

| Target | Statement | Prover | Reason |
|---|---|---|---|
| F1 | the signed-permutation identities: 2 K_a equals the symmetrized associator, the Gram identity on the slice, K(x)^3 = r^2 K(x) | Rocq, `vm_compute` over Z | finite integer matrices, the pattern of `A5W8ArcMatrixRanks.v` and `CdTowerTwoTermNullity.v` |
| F2 | the so(6,1) relations of the six K_a as a Lie-algebra map into `LieAlgebra.Orthogonal.so'` with p = 6, q = 1 | Lean with Mathlib | Mathlib defines `so'` (`Mathlib/Algebra/Lie/Classical.lean`, line 180 at the pin); the installed Rocq libraries name no Lie-algebra package |
| F3 | the kernel frame (t - K(x)) T on the cone, over any commutative ring | Lean, with a Rocq bridge | the pattern of `KernelCertificate.lean` and `CdTowerKernelCertificate.v` |
| F4 | the disjoint-star criterion implies the so(m,1) relations, for every m | Lean | a structural statement over finite index sets, the only target that reaches every dimension |
| F5 | the eight anticommuting units of A5-625 and the Cl(0,8) image | Lean | `CliffordAlgebra.lift` and `Clifford/ZeroEight.lean` already map Cl(0,8) to 16 x 16 matrices built from sedenion tables |
| F6 | nullity >= 12 on the Euclidean cone over a field of characteristic 0 or above 32 | Lean | needs rank and trace of an idempotent matrix over a field, which Mathlib's linear algebra supplies |

Agda adds a third kernel for a statement already proved in Lean or Rocq. For the null slice its use would be a
cross-check of F1, whose content is finite; the owner's pilot decision governs any extension, and no Agda work is
proposed here.

## Exhaustive tables

The decision record `docs/archive/reviews/2026-10-25-results-catalog-opposition.md` defers Parquet until a measured
query over raw shots is slow, and DuckDB reads the retained JSON and JSON Lines directly. The null-slice records stay
far below the GitHub size limits (`result.json` of a few kilobytes). An exhaustive table of every two-term pair or
every slice at dimensions 1024 to 4096 is the first input of this program that could approach them: at dimension
4096 the two-term pairs number about 8.4 million. Such a table, when a question needs it, goes to JSON Lines with a
digest reference in the record (a digest reference per table, the pattern of the workspace's results-store design), and the Parquet decision is reopened only with a measured query time.

## Next computations, with acceptance checks

1. **Nilpotent variety.** hypothesis: over F_p (p odd) the nilpotents of A_n are the nonzero pure imaginary vectors of norm 0, and
   their number is p^(2^n - 2) - 1 (the Euclidean cone of A5-623 is the slice's part of that variety). Accept: a record
   that counts nilpotents and idempotents of A_2, A_3 over F_3, F_5, F_7 by brute force and matches both formulas.
2. **Albert anchor.** dim Der(J_3(O)) = 52 over Q under the cd_core octonion convention, and the su(3) and G_2
   covariance algebras of A5-615 and A5-619 as stabilizers inside it. Accept: the derivation rank over Q, and the
   inclusions as rank equalities.
3. **Relations above 512.** Done for n = 10, 11 and 12 (A5-637,
   [family relations](../evidence/a5-null-slice-family-relations/README.md)). What remains for
   every n is the commutation-set lemma of A5-636 ([census](../evidence/a5-left-table-census/README.md), statement 6).
4. **Formal F1 and F4.** Briefs to gororoba-math. Accept: the repository's `ci/check.sh` and `ci/check_rocq.sh`
   green with the new sources listed.
5. **Octonion-space covariance (A5-619, A5-642).** Done: G_2 with no boost at every n >= 6 (four anchor cosets), and su(3) at A_5, by XOR-block and coset decomposition
   ([covariance blocks](../evidence/a5-null-slice-covariance/README.md)).
