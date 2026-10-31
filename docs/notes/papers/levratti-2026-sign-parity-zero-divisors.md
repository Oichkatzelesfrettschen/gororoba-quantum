# Levratti: sign-parity classification of zero divisors in Cayley-Dickson algebras

## Source copy and license

The unchanged [source PDF](https://zenodo.org/records/20315751) is retained under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) as
[levratti-2026-sign-parity-zero-divisors.pdf](../../pdf/levratti-2026-sign-parity-zero-divisors.pdf). The grant is the
`metadata.license` field of the author-linked [Zenodo record](https://zenodo.org/api/records/20315751), captured byte for
byte in [zenodo-record-20315751.json](../../evidence/source_rights/zenodo-record-20315751.json); the deposited file's size
and MD5 match the retained bytes. [SOURCES.json](../../SOURCES.json) binds the SHA-256, the evidence hash and the reading
scope. Attribution to Giovanni Levratti applies to every statement below.

Tag convention: [P] marks a statement of the paper; [E] marks a finite check run against `cd_core` for this note; [I]
marks repository interpretation. Printed page numbers equal PDF page indices.

## Citation and provenance

- Title (PDF title page): Sign-Parity Classification of Zero Divisors in Cayley-Dickson Algebras. Author: Giovanni
  Levratti (independent researcher), dated May 2026.
- Publication: Zenodo preprint, DOI 10.5281/zenodo.20315751, created 2026-05-20, record updated 2026-05-28, licensed CC BY
  4.0. No journal reference exists.
- Distinct from the two Levratti works already registered, which concern code constructions:
  [active stabilizers](levratti-2026-active-stabilizers.md) and [Fano duality and the CSS bridge](levratti-2026-fano-css.md).
  Both build on the zero-divisor supports that this paper classifies.
- Deposited file: `Zero_Divisor_Structure__Norm_Redistribution__and_Spectral_Theory_in_Cayley_Dickson_Algebras_v1.pdf`,
  521657 bytes, 28 pages, MD5 `6cbfca5cec3deed7f1308e7f0351395b`. The file name carries the earlier working title (zero-divisor
  structure, norm redistribution and spectral theory), while the Zenodo record title and the PDF title page read
  "Sign-Parity Classification of Zero Divisors in Cayley-Dickson Algebras".
- SHA-256: `bd219f4429cc22277f80e06273a6450ff8fbd982ce0176761dab1f533feea9c3`.
- Version family: the concept DOI 10.5281/zenodo.20309808 lists three records. The registered record 20315751 (2026-05-20)
  is the middle one. Record 20309809 (2026-05-20, file without a version suffix, 521741 bytes) precedes it, and record
  21296777 (2026-07-10, file `..._v3.pdf`, 597031 bytes, same title and abstract) follows it and is the latest version.
  The registry retains record 20315751 only; the later record's bytes were neither retrieved nor compared, so the differences
  between versions are unknown. The paper's Section 1.3 refers to a "prior edition" with open problems PA1 to PA5, P5, P6 and
  P8, which this edition resolves.
- Retrieved 2026-10-30 UTC; the Zenodo `versions/latest` response is a registered retrieval receipt.
- Reading scope: the abstract, Sections 1 to 3 in full (including the proofs of Theorems 3.1, 3.6, 3.10, 3.13 and 3.17),
  Definition 4.8 and Theorem 4.9, the statements of Theorems 5.3 to 5.17 and 5.21, Section 7 (Definition 7.2 to Theorem
  7.25), Theorems 8.1, 9.2, 9.6, 10.2 and 10.3, Theorem 12.1, Theorem 14.2 and Section 15, extracted with `pdftotext
  -layout`. The proofs of Sections 5, 12 and 13, the GPU enumeration behind Theorem 14.2, and the variance results of
  Section 13 were not verified line by line.
- Status: single-author preprint. The acknowledgements state that Claude (Anthropic) assisted algebraic verification,
  structural analysis and proof scaffolding and that DeepSeek assisted proof transcription and gap-filling; the paper's
  Remark 5.18 corrects an error in the proof of Lemma 5.14 that the paper had stated earlier.

## Conventions

- [P] Definition 2.1 (p. 3): `A_0 = R`, `(a, b)(c, d) = (ac - conj(d) b, d a + b conj(c))`, `conj((a, b)) = (conj(a), -b)`,
  quadratic norm `N((a, b)) = N(a) + N(b)`, canonical basis `B_n = {e_0, ..., e_(2^n - 1)}` with `e_0 = 1`;
  `epsilon_i = (e_i, 0)` and `f_i = (0, e_i)` name the two halves of `B_(n+1)`.
- [P] Theorem 3.1 (p. 4), XOR Index Theorem: `e_alpha e_beta = epsilon_(alpha beta) e_(alpha XOR beta)` with `epsilon` in
  `{+1, -1}`; Corollary 3.2: left and right multiplication by a basis element are signed permutations of the basis.
- [I] The product and the XOR index convention equal `cd_core.cd_multiply` and `cd_sign` (the basis product is
  `cd_sign(dim, p, q) e_(p XOR q)`), so the paper's signs `epsilon_(ij)` are `cd_sign` values and no sign map is needed.
- [P] Definition 2.3 (p. 4): `C(n) = {e_i + sigma e_j : 0 <= i < j < 2^n, sigma = +-1}`; `ZD(n)` is the set of ordered pairs
  `(a, b)` in `C(n)^2` with `a, b != 0` and `ab = 0`; `VL(n)` the pairs with `N(ab) != N(a) N(b)`; densities `varrho(n) =
  |ZD(n)| / 4^(2n)` and `F(n) = 1 - |VL(n)| / 4^(2n)`. The paper uses a second density `rho(n) = |ZD(n)| / |C*(n)|^2` over
  index-pure elements (Remarks 2.4 and 2.5).

## Theorem statements

- [P] Combinatorial chain (Section 3). Theorem 3.3 (Isometry Lemma, p. 5): `N(a e_k) = N(e_k a) = N(a)`. Corollary 3.4:
  every `(a, b)` in `ZD(n)` has `N(a) = N(b) = 2`. Theorem 3.6 ({0, 4, 8} Trichotomy): for `a = e_i + sigma e_j`, `b = e_k + tau
  e_l`, `N(ab)` is 4 when `i XOR j != k XOR l` (Case A) and lies in `{0, 4, 8}` otherwise (Case B). Theorem 3.7 (XOR Density
  Bound): `varrho(n) <= (2^n - 1)/4^n`. Theorem 3.9: the Case B condition `i XOR j XOR k XOR l = 0` picks the weight-4 minimum
  codewords of `RM(1, n)-perp = RM(n - 2, n)`. Theorem 3.10 (Extended SSNR): `N(ab) + N(ab') = 4 N(a)` for `b' = e_i - sigma
  e_j`. Corollary 3.11: `(a, b) -> (a, b')` is a bijection `ZD(n) -> VL(n) \ ZD(n)`. Theorem 3.13 (NRI Equality): `1 - F(n) =
  2 varrho(n)` for `n >= 4`.
- [P] Operator chain (Sections 3.5 and 5). Proposition 3.15: for a unit zero divisor `a = (e_p + e_q)/sqrt(2)` in `A_n`
  (`n >= 4`), `Spec(M_a) = {0^(2^(n-2)), 1^(2^(n-1)), 2^(2^(n-2))}` with `M_a = L_a^T L_a`. Theorem 3.17 (NRI Balance): for `v`
  uniform on the sphere `S^(2^n - 1)`, `Pr[N(av) < 1 - eps] = Pr[N(av) > 1 + eps]`. Theorem 5.3: `L_a + L_a^T = 2 a_0 I`.
  Theorem 5.4: every eigenvalue of `L_a` has real part `a_0`. Corollary 5.5 (Global Vacuum Protection): a left annihilator
  forces `a_0 = 0`. Theorem 5.6 (Frobenius Identity): `||L_a||_F^2 = 2^n N(a)`. Theorem 5.8 (Analytical Mean): `E_v[N(av)] =
  N(a)`. Theorem 5.16: `M_a b' = 2 b'`. Theorem 5.17: `dim ker L_a = 2^(n-2)` for a unit zero divisor. Theorem 5.21
  (Exchange Symmetry): `av = 0` iff `va = 0` for `a` with `a_0 = 0`.
- [P] Sign-parity framework (Section 7). Definition 7.2: for a 2-flat `F = {i, j, k, l}` (`i XOR j XOR k XOR l = 0`, all `>= 1`)
  and split `(i, j) | (k, l)`, the sign parity is `pi(F, split) = epsilon_(ik) epsilon_(jk) epsilon_(il) epsilon_(jl)`.
  Theorem 7.3 (Sign Parity Criterion): the zero-product conditions have a solution iff `pi = +1`, and then exactly two sign pairs
  `(sigma, tau)` solve them. Corollary 7.4: `|ZD(n)| = 4 x #{(F, split) : pi = +1}`. Proposition 7.6: at `n = 4`, 315
  (flat, split) pairs, 84 with `pi = +1`, so `4 x 84 = 336`. Theorem 7.7: every pair in `ZD(4)` has one `epsilon`-type
  and one `f`-type index in each component. Theorem 7.13: the Fano sub-algebra `B` is isomorphic to `O`. Corollary 7.14: each
  Fano plane contributes 84 active (flat, split) pairs. Theorem 7.16 (p. 17), main count: `|ZD(n)| = 336 x [n-1 choose 3]_2`
  for `n >= 4`, with `[.]_2` the Gaussian binomial. Theorem 7.18: `pi_A pi_B pi_C = -1` for every 2-flat, so each 2-flat has 0
  or 2 active splits (Corollary 7.19). Proposition 7.21: `E_pqrs = 3 - 4 ac` in `{-1, 7}`; Theorem 7.25 (Lemma B) proves
  `ac = -1`.
- [P] Hereditary decomposition and asymptotics. Theorem 8.1: `|ZD(n+1)| = |ZD(n)| + 336 Delta(n)` with `Delta(n) =
  [n choose 3]_2 - [n-1 choose 3]_2`. Theorem 9.2 and Proposition 9.3: `rho` and `varrho` decrease strictly for
  `n >= 4`. Corollary 9.5: `336 | |ZD(n)|`. Theorem 9.6: `rho(n) 2^n = 1/4 - 2/2^n + O(4^(-n))`, increasing to `1/4`.
- [P] Born rule and weight classes. Theorem 10.2: for `f : A_n -> R>=0` with multiplicativity (M), definiteness (D) and
  orthogonal additivity (OA), `f = N` is the unique solution for `n <= 3` and no solution exists for `n >= 4`; Theorem 10.3
  shows homogeneity (I) is redundant. Theorem 12.1: an element with exactly three nonzero real coefficients on distinct
  indices `>= 1` has invertible `L_a`. Theorem 14.2: among the index-pure `+-1`-coefficient elements of `A_4`, the left zero
  divisors number 0 (weight 1), 168 (weight 2, 42 active pairs with 4 signs each), 0 (weight 3), 3528 (weight 4), 9408
  (weight 6), 67872 (weight 8), 142464 (weight 10) and 237440 (weight 12), total 460880, with none at odd weights or at weights
  of 13 and above; the enumeration is a GPU computation, and odd weights beyond 3 are random samples of 500 supports.
  Remark 14.4 lists the even-weight law, the cutoff at weight 12, the universal kernel dimension 4 and the weight-12 parity
  constraint as analytically open.

## Repository checks

[E] Each check ran against `gororoba_quantum/cd_core.py` with a throwaway driver (unretained) started by `python3 -I`.

| Paper statement | Check | Result |
| --- | --- | --- |
| Theorem 7.16 at `n = 4` | count ordered pairs `(e_i + s e_j)(e_k + t e_l) = 0` over all `i < j`, `k < l`, `s, t = +-1` in dimension 16 from `cd_sign` | 336 |
| Theorem 7.16 at `n = 5` | the same count in dimension 32 | 5040, equal to `336 x [4 choose 3]_2 = 336 x 15` |
| Proposition 7.6 and Theorem 4.9 | `cd_core.sedenion_zero_divisor_corpus()` | 336 rows, 42 distinct supports on each side |
| Theorem 14.2, weight 2 | rank of `L_a` for the 210 elements `e_i + s e_j`, `1 <= i < j <= 15` | 84 singular, all with `dim ker = 4`; the paper's 168 counts both overall signs of each |
| Theorem 12.1 | rank of `L_a` for all 3640 elements `s_1 e_i + s_2 e_j + s_3 e_k` with `1 <= i < j < k <= 15` and `s = +-1` | none singular |
| Theorem 5.17 at `n = 5` | rank of `L_a` for `a = e_1 + e_10` in dimension 32 | `dim ker L_a = 8 = 2^(5-2)` |

[E] Not run: the count at `n >= 6` (dimension 64 needs about 66 million products), Theorems 3.17, 5.16, 5.21, 9.2, 9.6 and
10.2, the weight-4 to weight-12 counts of Theorem 14.2, and Section 13.

## Mapping to this repository

- [I] The paper's `ZD(4)` is the repository's 336-row signed two-support corpus
  (`cd_core.sedenion_zero_divisor_corpus`; the [sparse count ledger](../topics/cayley_dickson_sparse_census.md) separates 84
  first operands, 84 table pairs, 168 first-relative-sign-positive rows and 336 ordered signed rows). The two counts
  agree under the shared convention. The paper's Theorem 4.9 (both components index-pure) and the corpus's
  disjoint-support layout state the same condition.
- [I] Theorem 7.16 extends the count to `A_5` as 5040 under `cd_core`, which agrees with the [E] check; the repository's
  dimension-32 notes can cite the closed form for the two-support count and keep the all-weight counts separate.
- [E] Weight-two elements of `A_5` do not share one kernel dimension: exact row reduction of
  `cd_core.left_mult_matrix_exact(32, v)` gives nullity 8 for `e1 + e10`, 12 for `e1 + e18` and 4 for `e1 + e26`. Theorem
  5.17's kernel dimension 8 therefore matches only the subfamily of `e1 + e10`; the other two supports fall in the
  nullity-12 and nullity-4 strata of the [A_5 exceptional fiber findings](../topics/a5-exceptional-fiber-findings.md).
  Which weight-two supports the paper's `ZD(5)` covers, and how they split across the three strata, is open.
- [I] Sign-parity analysis (Theorem 7.3) is an alternative route to the two-support classification of the
  [Moreno](../math-0512517.md) and [Reggiani](2411.18881.md) notes. A comparison of the 84 active (flat, split) pairs with
  the box-kite assessors of the repository is open.
- [I] The Born-rule theorem (10.2) and the NRI balance (3.17) are probabilistic statements about `N(av)` for random `v`; the
  repository's hardware probes do not use them, and this note makes no claim about them.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: high (the closed count agrees with `cd_core` at `n = 4` and `n = 5`).
- [I] Factoring resource estimates: none.

## Boundaries

[I] Stated as theorems by the paper but unchecked here: the full operator chain of Section 5, the E-formula chain of Section
7.11 and the exhaustive weight classification of Section 14. The record title, the PDF title page and the record's file name
differ (see Citation and provenance), and a later version of this work exists on Zenodo; a reading of that version is a
separate registry decision.
