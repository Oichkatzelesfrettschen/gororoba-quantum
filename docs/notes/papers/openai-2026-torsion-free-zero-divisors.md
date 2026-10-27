# OpenAI 2026 -- A torsion-free group algebra with zero divisors (openai/math family 196)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/A-Torsion-Free-Group-Algebra-with-Zero-Divisors-September-23-2026/paper.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-196-torsion-free-zero-divisors.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation; [E] marks an exact computation
retained in this repository. Printed page numbers equal the PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README. The
  manuscript is unrefereed.
- Version read: the manuscript dated 23 September 2026 (the PDF carries no creation date), as held at openai/math commit
  `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). A Crossref bibliographic search by title on
  27 October 2026 returned no record of it.
- Commit-pinned PDF, 26 pages, 463,825 bytes.
- SHA-256: `b9788d4579b317fa2487796338fe3413322e105950880ec5a42bc85188a36bc6`
- Reading scope: pp. 1-4 (introduction, cancellation mechanism, Section 2.1 prescribed types) and p. 24 (the proof of
  Theorem 1.1 in Section 6) in full. Sections 2.2-5 were read for result labels only; no step of the probability
  estimates, the planar extraction or the asphericity argument was checked.

## Transcribed statements

- [P] Theorem 1.1 (p. 1): there exist a finitely presented torsion-free group `G` and nonzero `alpha, beta` in
  `F_2[G]` with `alpha beta = 0`; `G` admits a finite two-dimensional classifying space.
- [P] Torsion obstruction (p. 1): an element `g` of order `m > 1` gives `(1 - g)(1 + g + ... + g^(m-1)) = 0`; the
  conjecture asks whether removing this obstruction suffices.
- [P] Unique products (p. 1): failure of the unique-product property alone does not produce a zero divisor, because
  over `F_2` the representation counts must be even, not merely greater than one.
- [P] Cancellation mechanism (p. 2, equation (1.2)): two finite graphs immersed in one rose, coned off, give labels
  `g_x`, `h_y` and the factors `alpha = sum g_x`, `beta = sum h_y^(-1)`. A simultaneous step of a common label `t`
  preserves `(g_x t)(h_y t)^(-1) = g_x h_y^(-1)`. When every pair has odd `|S_x cap S_y|`, every component of the
  simultaneous-step graph has even size by the degree-sum formula, and its equal contributions cancel over `F_2`.
- [P] Prescribed types (pp. 3-4): `q = 128`, `v = q^2 + q + 1 = 16513`. The ordinary part of each outgoing label set
  is a line of the projective plane over `F_q`; two lines meet in 1 or `q + 1 = 129` points, both odd. Extra parts
  (two of three extras on side A, all three on side B) meet in 0 or 2 letters, so `|S_x cap S_y|` is odd for every
  `x in A`, `y in B` (equation (2.1)), independently of the random matching.
- [P] Proof of Theorem 1.1 (p. 24): the root is the only vertex contributing the identity to each factor
  (Proposition 5.1), so both factors are nonzero; Corollary 5.3 makes the cone complex a classifying space, so `G` is
  torsion-free. "The construction is probabilistic: it proves that suitable finite matchings exist, without
  specifying matchings from which a concrete presentation and zero-divisor factors can be read off."

## Formal statement

- [P] [`lean/docs/196.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/196.md)
  links `ComparatorChallenges/TorsionFreeZeroDivisors.lean`, whose `MainTheorem` asserts a finitely presented group
  with `TorsionFree G`, a finite connected two-dimensional CW classifying space with contractible covering, and
  nonzero `alpha, beta : MonoidAlgebra (ZMod 2) G` with `alpha * beta = 0`. Its JSON names the solution module
  `OAI.Algebra.GroupRing.Main`, the theorem `OAI.TorsionFreeZeroDivisors.main` and the permitted axioms `propext`,
  `Quot.sound` and `Classical.choice`. The Lean build and Comparator run were not run here.

## Mapping to this repository

- [I] Mechanism. A product of two finite sums in a twisted group algebra vanishes exactly when the coefficients on
  every fiber of the support multiplication map sum to zero. This paper makes every fiber even and works over `F_2`;
  the sedenion two-blade zero divisors have fibers of size exactly two that cancel by the Cayley-Dickson sign. The
  [Kaplansky mechanisms note](../topics/kaplansky-mechanisms-cayley-dickson.md) carries the comparison.
- [E] Fano parity. The seven lines of the octonion multiplication table, read from `cd_core.fano_completion`, meet
  pairwise in one point and have three points each, so their incidence Gram matrix is the all-ones matrix modulo 2:
  the `q = 2` instance of the odd line-intersection property this paper uses at `q = 128`
  ([kaplansky-cd-mechanisms](../../evidence/kaplansky-cd-mechanisms/README.md), gate sources-412).
- [I] Explicitness. The sedenion zero divisors are explicit (the 84 two-blade elements of
  `cd_core.sedenion_zero_divisor_corpus`); this paper's zero divisors are proved to exist and are not listed.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: low (a mechanism comparison; no shared theorem).
- [I] Factoring resource estimates: none.

## Boundaries

[I] No proof step outside pp. 1-4 and 24 was checked, the Lean build was not run, and the manuscript is unrefereed.
