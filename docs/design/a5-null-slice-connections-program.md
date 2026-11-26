# A_5 null slice: connections, formal targets and the next computations

This program note joins the two null-slice records
([boost algebra](../evidence/a5-null-slice-boost-algebra/README.md), ledger rows A5-612 to A5-621;
[associator envelope](../evidence/a5-null-slice-associator-envelope/README.md), rows A5-622 to A5-628) to the rest of
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
| Two-term pairs (Skiouris Proposition 2.2) | x = e_a, t = +-1 gives the nullity-4 stratum; the record recounts all 225 pairs (counts only; the proposition states the criterion) | documented and computed (A5-627) | proved | none |
| de Marrais struts | every nullity-4 two-term pair has strut s > 8, the range `demarrais_structures.py` marks sparse (`is_dmz_sparse`); the slice uses the struts 9, 11 to 15 | computed (A5-627) | proved for the implication; the full 4-versus-12 rule is Skiouris's | a nullity-4 pair with s <= 8 |
| Quantum runs | the coset-block map read e_1 + e_26 at N_hat = 4.25 and 4.28 (4.02 and 4.05 after readout correction) on two Heron r2 devices; the full map left it unresolved; the module's aligned pairs are the support of K_1 | measured (`results/live/PATHION_KERNEL_MAP_FINDINGS.md`) | measured | a retained replica outside the reported interval |
| Tower to 4096 | both families hold from 256 to 4096 | computed (A5-626) | survives above 512 | a sign row that differs from cd_core; stars that meet |
| Clifford and Cayley-Dickson | the six spatial tables are a Clifford space; with J eta they give seven anticommuting units in M_16(R) | computed (A5-624, A5-625) | proved; Cl(0,8) open | an eighth unit, or its exclusion |
| Cayley-Dickson and Lie | defects close on so(m,1); covariance algebras su(3) and G_2 | computed (A5-613), conjecture (A5-619) | proved; A5-619 open | the A_6 covariance computation |
| Nilpotents | y^2 = 0 on the Euclidean cone; L_y is square-zero on ker K(x) there and L_y^2 = 0 on the null space | computed over F_p (A5-623) | certified | a Euclidean-cone point with L_y^2 of rank other than 8 |
| p-adic fields | the seven-variable form is isotropic over every Q_p, so the Euclidean cone has Q_p points | cited theorem (isotropy of forms in five or more variables) | hypothesis for the nullity value over Q_p | the nullity at a Q_p point by a Hensel lift of an F_p point |
| Albert and Jordan algebras | gororoba-open `construction/albert.rs` and `jordan.rs` compute J_3(O) products; the slice uses no Jordan product | read (crate headers) | no link found | a Jordan-triple identity among the K_a |
| Hopf algebras and fibrations | the filed sources hold Adams's Hopf-invariant-one theorem and an introduction to Hopf algebras; neither enters the slice | read (manifests) | no link found | a coproduct or a fibration built from the slice |
| arXiv 2611.34924 | one abelian unitary boost generator | read on pages 28 and 39 (A5-628) | boundary | a non-abelian boost algebra in the paper |

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
| F5 | seven anticommuting units in the envelope, and Cl(0,8) once A5-625 decides | Lean | `CliffordAlgebra.lift` and `Clifford/ZeroEight.lean` already map Cl(0,8) to 16 x 16 matrices built from sedenion tables |
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

1. **Eighth unit (A5-625).** Search the eight-dimensional anticommuting space for an element of square -I. Accept: an
   exhibited unit with the Cl(0,8) relations checked over Z, or a proof of absence from the quadratic form X -> X^2 on
   that space.
2. **Euclidean cone over Q(i).** Rank over Q(i) at e_1 + i e_26 and two further points with FLINT's Gaussian
   rationals. Accept: nullity 12 at each point, matching A5-623.
3. **Relations above 512.** Direct triple checks at n = 10 on the compute workstation (about 8 million triples).
   Accept: zero failures; A5-626 moves to proved for n = 10.
4. **Formal F1 and F4.** Briefs to gororoba-math. Accept: the repository's `ci/check.sh` and `ci/check_rocq.sh`
   green with the new sources listed.
5. **A_6 covariance (A5-619).** Accept: the covariance algebra of the octonion-space slice of A_6 computed and
   compared with the G_2 derivations.
