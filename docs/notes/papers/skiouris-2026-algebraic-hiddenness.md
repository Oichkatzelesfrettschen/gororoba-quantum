# Skiouris: algebraic hiddenness in the sedenion algebra

## Source copy and license

The unchanged [source PDF](https://zenodo.org/records/22016333) is retained under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) as
[skiouris-2026-algebraic-hiddenness.pdf](../../pdf/skiouris-2026-algebraic-hiddenness.pdf). The grant is the
`metadata.license` field of the author-linked [Zenodo record](https://zenodo.org/api/records/22016333), captured byte for
byte in [zenodo-record-22016333.json](../../evidence/source_rights/zenodo-record-22016333.json). The deposited file's
size and MD5 match the retained bytes. [SOURCES.json](../../SOURCES.json) binds the SHA-256, the evidence hash and the
reading scope. Attribution to Kyriakos John Skiouris applies to every statement below.

Tag convention: [P] marks a statement of the paper; [E] marks a finite check run against `cd_core` for this note; [I]
marks repository interpretation. Printed page numbers equal PDF page indices.

## Citation and provenance

- Title: Algebraic Hiddenness in the Sedenion Algebra: Characterization, Spectral Structure, and Bundle Topology.
- Author: Kyriakos John Skiouris (Agingo Corporation, Charlotte, NC), dated August 2026.
- Publication: Zenodo preprint, DOI 10.5281/zenodo.22016333, published 2026-08-19, licensed CC BY 4.0. The concept DOI
  10.5281/zenodo.22016332 lists this record as its only version (`/versions/latest` resolves to the same record id). No
  journal reference exists; the PDF lists MSC 17A35, 17A75, 53C29, 55R25, 17D05 and arXiv categories math.RA, math.DG,
  math.AT, and this retrieval did not search arXiv for a posting.
- Deposited file: `algebraic_hiddenness_v1g.pdf`, 771773 bytes, 32 pages, MD5 `5ac9d520855917d37a8f40928fad83e7`.
- SHA-256: `48a4b2385b3ef16872c4c4a3e5d2d3972ee752bb8dfe10f091b7b6745553ef7b`.
- Retrieved 2026-10-30 UTC. The Zenodo `versions/latest` response is a registered retrieval receipt.
- Reading scope: the abstract, Sections 1 and 2, Section 3 through the eleven-step proof of Theorem 3.1, the statements and
  proof sketches of Sections 4 and 5, the statements of Sections 6 to 9 and the open frontiers of Section 10, extracted with
  `pdftotext -layout`. The proofs of Theorem 6.4 (Serre spectral sequence), Theorem 7.2, Theorem 8.1 (five-stage
  decomposition) and the exact Pfaffian certificate of Section 5.8 received no line-by-line check. The author's C++17 probe
  archive (`the_aphanic_toy`) was not retrieved or run.
- Status: single-author preprint. The paper classifies each claim as PROVEN (algebraic proof), EMPIRICAL (numerical
  certification) or CONFIRMED (stated by others), and states that probes report PASS, FAIL or CERTIFIED and never PROVEN.

## Conventions

- [P] Eq. 1 (p. 4) and Eq. 2 (p. 8): `(a, b)(c, d) = (ac - conj(d) b, d a + b conj(c))`, conjugation `(a, b)* = (conj(a), -b)`.
  `A_0 = R`, `A_(n+1) = A_n + A_n l_(n+1)` with `l^2 = -1`. Levels: `A_3 = O`, `A_4 = S` (sedenions), `A_5 = P` (pathions),
  `A_6` (chingons). `l = l_4 = e8` in the standard ordered basis `{1, e1, ..., e15}`; `l_5 = e16`, `l_6 = e32`.
- [P] Section 1.2 (p. 4): hand-written Fano-plane multiplication tables differ from the recursive formula in 24 of the
  `2 x 8 x 7 = 112` nonzero products, and which pairs are zero divisors depends on that choice. The recursive product is the
  convention used throughout.
- [P] Section 2.3 (pp. 6-7): `p = (x, y)` with `x, y` in `Im(O)`; `G_p = L_p^T L_p`; `sigma = 2 |x wedge y| =
  2 sqrt(|x|^2 |y|^2 - <x, y>^2)`; the aphanic cone is `|x| = |y|`, `<x, y> = 0`, `x, y` linearly independent; the aphanic
  locus `V` is the slice `|x| = |y| = 1` (`|p|^2 = 2`) and `K -> V` is the rank-4 bundle `K_p = ker L_p`.
- [I] The product equals `cd_core.cd_multiply` with `cd_sign` on the XOR index, as in the convention note of the
  [Levratti note](levratti-2026-sign-parity-zero-divisors.md) and the Lemley convention map in
  [2609.11588](2609.11588.md): the left factor of the second term is `d a`, the right factor is `b conj(c)`.

## Definitions

- [P] Definition 2.1 (p. 7), aphanic element: `p = (x, y)` in `S` with `x, y` in `Im(O)`, `|x| = |y| != 0`, `<x, y> = 0`.
  Definition 2.2: the aphanic locus is the set of all aphanic elements. Definition 2.3: the aphanic twist is the class
  `[K]` in `H^6(V; Z/2) = Z/2`. Remark 2.4 and the name record that an aphanic `p` is annihilated by the operator its own
  system uses to measure it.
- [I] "Aphanic" names the repository's imaginary sedenion zero divisors with both halves imaginary, normalized: the
  criterion of Theorem 3.1 equals the classical criterion of Moreno and of Biss, Dugger and Isaksen for the sedenions.

## Theorem statements

- [P] Theorem 3.1 (p. 8), Aphanic Characterization: for `p = (x, y)` with `x, y` in `Im(O)`, `ker L_p != 0` iff `|x| = |y|`
  and `<x, y> = 0`, and then `dim ker L_p = 4`. The proof is eleven steps through the block form `L_p = [[L_x, -R_y C],
  [L_y C, R_x]]` (Eq. 4), the Gram operator `G_p = |p|^2 I + W` and the keystone identity `(|x|^2 - |y|^2)^2 + 4<x, y>^2 = 0`
  (Eq. 15). Lemma 3.2 gives the associator norm on `Q-perp`; Corollary 3.3: `det(L_p)^2 = det(G) = (|p|^2 - sigma)^4
  (|p|^2)^8 (|p|^2 + sigma)^4`.
- [P] Theorem 4.1 (p. 11), 4-8-4 Spectral Theorem: `Spec(G_p) = {(|p|^2 - sigma)^4, (|p|^2)^8, (|p|^2 + sigma)^4}` for
  linearly independent imaginary `x, y`; for aphanic `p` it reduces to `{0^4, (|p|^2)^8, (2|p|^2)^4}`, and to `{0^4, 2^8,
  4^4}` on the unit locus. Corollary 4.4 gives the spectral projectors. Remark 4.2 reads the multiplicities as the 4 + 8 + 4
  Cayley-Dickson block split; the paper notes equivalence with the eigenvalue computation of Biss, Christensen, Dugger and
  Isaksen for `M_a`.
- [P] Section 5 (pp. 12-17), Sedenion Annihilator Fourfold Theorem. Lemma 5.1: a nonzero real part makes `L_p` invertible.
  Proposition 5.4: for imaginary `p = (a, b)`, `Pf(L_p) = -(|p|^2)^2 T` and `det L_p = (|p|^2)^4 T^2` with `T = 4|a|^2
  Re(b)^2 + 4<a, b>^2 + (|a|^2 - |b|^2)^2`. Theorem 5.6: `ker L_p != 0` iff `Re(b) = 0`, `<a, b> = 0`, `|a| = |b|`. Theorem 5.7:
  the kernel dimension is 4. Theorem 5.12: the nullity of a nonzero `p` is 0 or 4. Theorem 5.13: `dim ker L_p = dim ker R_p`.
  Theorem 5.14 collects these. Section 5.8 certifies the Pfaffian identity by exact finite computation. The paper credits
  Moreno and Khalil-Yiu for the criterion, Moreno and Biss-Dugger-Isaksen for the `{0, 4}` dichotomy, and Koebisu for the
  determinant factorization, and presents its route as independent.
- [P] Section 6 (pp. 19-21): Proposition 6.1, the unit aphanic locus is one `G_2`-orbit diffeomorphic to `G_2/SU(2)`
  (dimension `14 - 3 = 11`), identified with the Stiefel manifold `V_2(R^7)` as in Moreno and Biss et al. Lemma 6.2:
  `G_2`-invariance of `K`. Theorem 6.3: the stabilizer `SU(2)` acts on the fiber as `H`. Theorem 6.4 (Bundle
  Nontriviality, Aphanic Twist): `K = G_2 x_SU(2) H` is topologically nontrivial, detected on the fiber `S^5` of
  `S^5 -> V_2(R^7) -> S^6`, where `K` restricts to the nontrivial quaternionic line bundle. Theorem 6.6 (Berry Phase): the
  canonical Nomizu connection is non-flat, with closed geodesic loops of holonomy `-id`.
- [P] Section 7 (pp. 21-24), Theorem 7.2, Holonomy Decomposition: `hol = u(2) = u(1)_R + su(2)_L`, with `su(2)_L`
  the restriction of the lifted stabilizer action and the `u(1)` factor generated by a commutator of right multiplications
  by `e1` and `e2`. Remark 7.6: no physics claim. Section 8, Theorem 8.1: `[R_l, G_p] = 0` on `R^16` for `x, y` imaginary.
  Section 9: Theorem 9.1, `L_(conj X) L_X = R_(conj X) R_X` on `Im(A_n)` for every `n >= 1` (a flexibility corollary);
  Theorem 9.3, `[R_(l_(n+1)), G_p^(n+1)] = 0` for `n >= 3`; Proposition 9.5, an empirical machine-precision certification at
  dimension 64 with worst residual `3.05e-13` over 8 samples. Section 10 lists persistence of the holonomy classification at
  higher levels, the `SU(2)_L`-Fano identification and global integrability of the kernel distribution as open.

## Repository checks

[E] Each check ran against `gororoba_quantum/cd_core.py` through `cd_multiply`, `cd_sign`, `basis`,
`left_mult_determinant_exact` and `left_mult_matrix_exact`, with a throwaway driver (unretained) started by `python3 -I`.

| Paper statement | Check | Result |
| --- | --- | --- |
| Proposition 5.4, `det L_p = (|p|^2)^4 T^2` for imaginary `p` | exact `Fraction` determinant, 60 random integer `p` with `a_0 = 0`, `b` arbitrary | no mismatch |
| Theorem 5.6 and Theorem 5.7 | exact rank of `L_p` for 26 random integer imaginary `p` meeting the three equalities | nullity 4 on all 26; `p = e1 + e10` has determinant 0 and nullity 4 |
| Theorem 4.1 on the unit locus | eigenvalues of `L_p^T L_p` at `p = e1 + e10` | `{0: 4, 2: 8, 4: 4}` |
| Theorem 4.1 off the aphanic locus | 20 random real `x, y` in `Im(O)`, spectrum against `{(|p|^2 - sigma)^4, (|p|^2)^8, (|p|^2 + sigma)^4}` | maximum deviation `3.9e-14` |
| Theorem 8.1 | 20 random real imaginary `(x, y)`, maximum entry of `[R_l, G_p]` with `l = e8` | `7.1e-15` |

[E] The determinant identity does not hold for `p` with nonzero real part in the first half: 54 of 60 random integer `p`
with `a_0` unrestricted disagree with the formula. The paper states Proposition 5.4 for imaginary `p`, so the disagreement
marks the domain of the statement and refutes nothing.

[E] Not run: Theorem 6.4 and Theorem 6.6 (topology), Theorem 7.2, Theorem 9.3 above dimension 32, Proposition 9.5, and the
author's probe archive.

## Mapping to this repository

- [I] The nullity dichotomy, the kernel dimension 4 and the left-right equality restate results the repository already
  holds from [Biss, Dugger and Isaksen](../math-0511691.md), [Biss, Christensen, Dugger and Isaksen](../0905.2987.md),
  [Moreno](../math-0512517.md) and [Koebisu](2512.13002.md); the paper declares the same attribution. The new content is the
  bundle and holonomy layer (Sections 6 to 9), whose claims the repository neither uses nor has verified.
- [I] The aphanic criterion selects the imaginary sedenion zero divisors whose second component is imaginary; the
  repository's two-support corpus (`cd_core.sedenion_zero_divisor_corpus`, 336 ordered signed rows) is a finite subset of
  that locus. Matching the corpus rows to aphanic pairs is open.
- [I] Pathion-level extension: [Skiouris: aphanics at the pathion level](skiouris-2026-aphanics-pathion.md).
- [I] The paper's U(2) holonomy and the electroweak remark of its companion papers are interpretation; Remark 7.6 of the
  paper disclaims a physics claim, and the repository takes none from this source.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: high for Theorem 3.1, Proposition 5.4 and Theorem 4.1 (checked above), low for the bundle layer.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The related preprint cited as the companion framework paper (Zenodo 10.5281/zenodo.22032281, "Aphanics and Creative
Curvature") is not registered; this retrieval read only its Zenodo metadata. The Section 6 and Section 7 proofs are not
verified here.
