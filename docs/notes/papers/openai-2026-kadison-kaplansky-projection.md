# OpenAI 2026 -- A torsion-free counterexample to the Kadison-Kaplansky projection conjecture (openai/math family 285)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/A-Torsion-Free-Counterexample-to-the-Kadison-Kaplansky-Projection-Conjecture-September-23-2026/paper.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-285-kadison-kaplansky-projection.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Printed page numbers equal the
PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README. The
  manuscript is unrefereed.
- Version read: the manuscript dated 23 September 2026 (PDF creation date 6 October 2026, 09:38 UTC), as held at openai/math
  commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). A Crossref bibliographic search by title on
  27 October 2026 returned no record of it.
- Commit-pinned PDF, 76 pages, 662,684 bytes.
- SHA-256: `df6227b61598580506210a8236216e043d1acd4ba062a9901b3063559ff62a5a`
- Reading scope: pp. 1-4 (contents, introduction, proof strategy, Section 2 opening and Proposition 2.2 statement) in
  full. Sections 3-11 were read for section titles only.

## Transcribed statements

- [P] Conjecture (p. 2): the projection form of the Kadison-Kaplansky conjecture asserts that the reduced group
  C*-algebra of a torsion-free discrete group contains no projections other than zero and the identity.
- [P] Theorem 1.1 (p. 2): there exist a finitely generated torsion-free discrete group `G_proj` and a projection
  `e` in `C*_r(G_proj)` with `0 < tau(e) < 1/2`, where `tau(x) = <x delta_1, delta_1>` is the canonical trace.
- [P] Group ring versus completion (p. 2): the complex group ring `C[G_proj]` has no idempotents other than zero and
  one (companion manuscript, Corollary 1.2(ii)), so `e` lies in the reduced completion and not in the group ring.
- [P] Strategy (p. 3): a finite self-adjoint matrix `T` over the group algebra of a torsion-free group has a regular
  spectrum with a band near `+1` separated from the rest, so continuous functional calculus places its upper
  projection in `M_N(C*_r)`; Proposition 2.2 (p. 4) compresses a matrix projection of unnormalized trace in
  `(0, 1/2)` to a scalar projection after a free product with a free group.

## Formal statement

- [P] The pinned commit holds no `lean/docs/285.md` (HTTP 404 on 27 October 2026), and `formalization.yaml` lists no
  entry for this manuscript, so Theorem 1.1 is unformalized at that commit.

## Mapping to this repository

- [I] Algebraic core. The finite-dimensional analog of a scalar projection is an idempotent of the algebra itself.
  A real Cayley-Dickson algebra has no idempotents other than 0 and 1 at any dimension, and no nonzero nilpotents
  (proof in the [Kaplansky mechanisms note](../topics/kaplansky-mechanisms-cayley-dickson.md#idempotents-and-nilpotents)).
  The untwisted group algebra `R[Z_2^k]` has the idempotents `(1 +- g)/2`, which the Cayley-Dickson sign removes.
- [I] Completion. The paper's projection exists only after the operator-norm completion of an infinite group's
  algebra; a finite-dimensional algebra is its own completion, so no analog of that gap arises here.

- [I] Measurement contracts. The [projection-estimand investigation](../../design/quantum-experiment-conformance.md)
  retains exact finite examples separating expectation, return probability and normalized LCU success. Those
  examples diagnose the proposed measurement equation; they supply no finite realization of the paper's
  infinite-group completion mechanism.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: low (a contrast in the idempotent property; no shared theorem).
- [I] Factoring resource estimates: none.

## Boundaries

[I] No proof step was checked, and the manuscript is unrefereed.
