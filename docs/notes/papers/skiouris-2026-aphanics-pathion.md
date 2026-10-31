# Skiouris: aphanics at the pathion level

## Source copy and license

The unchanged [source PDF](https://zenodo.org/records/22082732) is retained under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) as
[skiouris-2026-aphanics-pathion.pdf](../../pdf/skiouris-2026-aphanics-pathion.pdf). The grant is the `metadata.license`
field of the author-linked [Zenodo record](https://zenodo.org/api/records/22082732), captured byte for byte in
[zenodo-record-22082732.json](../../evidence/source_rights/zenodo-record-22082732.json); the deposited file's size and MD5
match the retained bytes. [SOURCES.json](../../SOURCES.json) binds the SHA-256, the evidence hash and the reading scope.
Attribution to Kyriakos John Skiouris applies to every statement below.

Tag convention: [P] marks a statement of the paper; [E] marks a finite check run against `cd_core` for this note; [I]
marks repository interpretation. Printed page numbers equal PDF page indices.

## Citation and provenance

- Title: Aphanics at the Pathion Level: Spectrum Stratification and the Universal Clifford Triad.
- Author: Kyriakos John Skiouris (Agingo Corporation, Charlotte, NC), dated August 2026.
- Publication: Zenodo preprint, DOI 10.5281/zenodo.22082732, published 2026-08-24, licensed CC BY 4.0; the concept DOI
  10.5281/zenodo.22082731 lists this record as its only version. The record cites the sedenion paper
  ([Skiouris: algebraic hiddenness](skiouris-2026-algebraic-hiddenness.md), DOI 10.5281/zenodo.22016333) and a second
  preprint, DOI 10.5281/zenodo.22032281 ("Aphanics and Creative Curvature", not registered here). No journal reference exists.
- Deposited file: `aphanics_pathion_clifford_triad_v2.pdf`, 616626 bytes, 33 pages, MD5
  `283f1d83e42afcf6a68a5d81297b8839`. The file name carries `v2`, while the Zenodo record shows one version.
- SHA-256: `5e715063e9d1eeb6f4746034f14fd67e9e5c31d85e648f92812e6d161cd6c81d`.
- Retrieved 2026-10-30 UTC; the Zenodo `versions/latest` response is a registered retrieval receipt.
- Reading scope: the abstract, Section 1, Section 2 (conventions, Proposition 2.2, Definition 2.3), Section 3
  (Proposition 3.1), the statements of Theorems 4.1 and 4.3, Theorem 5.1 with Lemma 5.2, Proposition 5.3 and Theorem 5.4,
  Theorem 6.3 and Theorem 7.17, extracted with `pdftotext -layout`. The proofs of the Section 7 lemmas (7.5 to 7.14), the
  octonion four-block analysis behind Theorem 5.7 and Appendix A were not read line by line.
- Status: single-author preprint. The paper reserves "proved" for symbolic arguments and states that the necessity directions
  of Theorems 4.1 and 4.3 are numerical certifications; it cites an unpublished "research ledger" for some promoted results
  (Section 2.3), which this retrieval does not have.

## Conventions

- [P] Eq. 1 (p. 2): `(a, b)(c, d) = (ac - conj(d) b, d a + b conj(c))`, `(a, b)* = (conj(a), -b)`; tower `R, C, H, O, S, P`
  of dimensions 1 to 32. `l16 = (0, 1)` with `l16^2 = -1`; `iota_1(x) = (x, 0)`, `iota_2(y) = (0, y)`.
- [P] Pathion basis indices: the pathion slot `i` in `1..15` is a sedenion direction in the first half, and slot `j` in
  `17..31` encodes the sedenion direction `j - 16` in the second half (Proposition 2.2).
- [I] The product and the XOR index layout equal `cd_core.cd_multiply` and `cd_sign` at dimension 32: `l16` is the basis
  vector `e16`.

## Definitions

- [P] Definition 2.1 (p. 3): `p` in `P` is aphanic if `dim ker L_p > 0`; `P_aph` is the locus of imaginary aphanic points.
  Definition 2.3: the kill set `K(p) = {a in Im(P) : C_(a,b)(p) = 0 for all b in Im(P)}`, where the Berry curvature operator
  `C_(a,b)(p) = pi_p (L_b G_p^+ L_a - L_a G_p^+ L_b) pi_p` (Eq. 2, from the companion paper) uses the Moore-Penrose pseudoinverse
  `G_p^+` of `G_p = L_p^T L_p` and the projector `pi_p = I - G_p G_p^+` onto `ker L_p`.
- [P] Section 7: dyadic basepoints (Definition 7.1), the canonical Stratum-II and CD-aligned subfamilies (Definition 7.2),
  the antisymmetric kill-set basis (Definition 7.3) and half-embedded operators (Definition 7.4).

## Theorem statements

- [P] Proposition 2.2 (p. 3), Pathion Aphanic Stratification: for `p = e_i + e_j` with `i` in `1..15`, `j` in `17..31` and
  sedenion directions `s1 != s2`, `p` is aphanic; in Stratum I (the pair lies in a common octonion sub-copy) `dim ker L_p = 12`
  and `Spec(G_p) = {0^12, 2^8, 4^12}`; otherwise (Stratum II) `dim ker L_p = 4` and `Spec(G_p) = {0^4, 2^24, 4^4}`. At generic
  aphanic basepoints the spectrum has eight distinct values with multiplicity 4 each.
- [P] Proposition 3.1 (p. 4), Spectrum Non-Invariance: two aphanic `p, p'` with `dim K = 4` and equal norm can have unequal
  Gram spectra; at dyadic basepoints (canonical representative `p = e1 + e26`) the spectrum is `{0^4, |p|^2 [24], 2|p|^2 [4]}`
  and the pseudoinverse is a Lagrange-3 polynomial in `G_p`; see the boundary note below.
- [P] Theorem 4.1 (p. 9), Pathion Universal Kill Set: at every aphanic `p` with `dim K_p = 4`, `K(p) = span{p, l16, l16 p}` of
  dimension 3; sufficiency is symbolic and necessity (`dim ker Gamma_C = 3`, 16 random aphanic basepoints) is a numerical
  certification. Lemma 4.2 (Centralization Chain) links `[L_a, G_p] = 0`, `[L_a, pi_p] = 0` and `C_(a,b)(p) = 0`.
- [P] Theorem 4.3 (p. 10), Q-Centralizer Vanishing at Dyadic Basepoint: with three-valued Gram spectrum, `K(p)` is the
  five-dimensional `iota_1(V_p) + R l16 + iota_2(V_p)` with `V_p = span{s1, s2}`; necessity is certified at canonical
  Stratum-II basepoints.
- [P] Theorem 5.1 (p. 11), Pathion Clifford Triad: `L_p`, `L_(l16)`, `L_(l16 p)` are skew-symmetric, mutually orthogonal and
  pairwise anti-commute; they do not satisfy `L_a^2 = -|a|^2 I` since the pathions are not alternative. The proof uses
  Lemma 5.2 (Lemma A), Proposition 5.3 (Delta-reduction), Theorem 5.4 (Sedenion Delta Identity: for `a, b` in `Im(S)`,
  `{L_a, L_b} - {R_a, R_b} = 0` on `S`, with Remark 5.5 noting that orthogonality is unnecessary), and Theorem 5.7 (Octonion
  Omega Identity: for `A, B, c` in `O`, `conj(A)(Bc) + conj(B)(Ac) - (c conj(B))A - (c conj(A))B = 0`), reached through a
  four-block decomposition and Artin's theorem.
- [P] Theorem 6.3 (p. 14), Z2-Graded Clifford Sublattice: the universal triple space and its image under the automorphism
  `sigma(x, y) = (x, -y)` (Lemma 6.2) are each pairwise anti-commuting, and mixed pairs do not in general anti-commute.
- [P] Theorem 7.17 (p. 28), Two-Regime Dyadic Closure: `[L_a, G_p] = 0` for `a` in the antisymmetric summand at every dyadic
  basepoint, by Lemma 7.6 (the `u`-side) and Theorem 7.13 or Lemma 7.14 (the `w`-side at canonical Stratum-II or CD-aligned
  basepoints).

## Repository checks

[E] Each check ran against `gororoba_quantum/cd_core.py` (`cd_multiply`, `basis`) with a throwaway driver (unretained)
started by `python3 -I`.

| Paper statement | Check | Result |
| --- | --- | --- |
| Proposition 2.2 | eigenvalues of `L_p^T L_p` at all 225 basis pairs `e_i + e_j`, `i` in `1..15`, `j` in `17..31` | 15 pairs with `s1 = s2` give `{2: 32}` (not aphanic); 126 pairs give `{0: 12, 2: 8, 4: 12}` (Stratum I); 84 pairs give `{0: 4, 2: 24, 4: 4}` (Stratum II) |
| Proposition 3.1 | canonical `p = e1 + e26` | distinct eigenvalues `{0, 2, 4}` |
| Theorem 5.1 | skew-symmetry and pairwise anti-commutation of `L_p`, `L_(l16)`, `L_(l16 p)` at 40 Stratum-II basis pairs | skew-symmetry holds; maximum anti-commutator entry 0.0 |
| Theorem 5.7 | 200 random real octonion triples `(A, B, c)` | maximum residual `1.6e-14` |
| Theorem 5.4 | 50 random imaginary sedenion pairs | maximum residual `7.1e-15` |

[E] Not run: Theorems 4.1 and 4.3 (kill-set dimension, which needs the Berry operator `C_(a,b)(p)` of the companion paper),
Theorem 6.3, Theorem 7.17 and Appendix A. The check of Proposition 2.2 covers basis-pair basepoints only, and the "common
octonion sub-copy" criterion of the paper was not compared with the 126/84 split.

## Mapping to this repository

- [I] The 84 Stratum-II basis pairs equal the number of sedenion-level zero-divisor rows per sign class in the repository
  (84 first operands in [algebra_circuit_rules.md](../algebra_circuit_rules.md)); whether the correspondence is structural
  is open. The 126 Stratum-I pairs have nullity 12; this note does not compare them with any repository stratum.
- [I] The `l16`-multiplication triad is the pathion-level instance of the sedenion `R_l` centrality of
  [the sedenion paper](skiouris-2026-algebraic-hiddenness.md) (Theorem 8.1, Theorem 9.3).
- [I] The kill-set and Berry-curvature layer depends on the companion paper's operator and on the unpublished research
  ledger; the repository takes no claim from it.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: medium (the stratified spectra and the anticommutation checks are exact consequences of
  `cd_core`; the kill-set theorems are unchecked).
- [I] Factoring resource estimates: none.

## Boundaries

[I] The pseudoinverse polynomial of Proposition 3.1 was not transcribed or re-derived here; read it from the PDF.
