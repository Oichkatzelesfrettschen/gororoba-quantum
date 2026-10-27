# OpenAI 2026 -- A torsion-free group algebra that is not directly finite (openai/math family 197)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-197-torsion-free-not-directly-finite.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation; [E] marks an exact computation
retained in this repository. Printed page numbers equal the PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README. The
  manuscript is unrefereed.
- Version read: the manuscript dated 4 October 2026 (PDF creation date 4 October 2026, 00:00 UTC), as held at openai/math
  commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). A Crossref bibliographic search by title on
  27 October 2026 returned no record of it.
- Commit-pinned PDF, 31 pages, 517,870 bytes.
- SHA-256: `7950476863f21811aaccb99ab12f24f81741e5077ca290394d029063024aaee8`
- Reading scope: pp. 1-5 (introduction, Proposition 2.1 with its proof, Section 3.1 and Proposition 3.1) and p. 30
  (the proof of Theorem 1.1) in full. Sections 3.2-6 were read for result labels only.

## Transcribed statements

- [P] Theorem 1.1 (p. 1): there exist a finitely presented torsion-free group `G` and `a, b, c` in `F_2[G]` with
  `ab = 1`, `ac = 0` and `c != 0`, so `ba != 1`; `G` admits a finite two-dimensional classifying complex. If
  `ba = 1`, then `c = (ba)c = b(ac) = 0`.
- [P] History (p. 1): in characteristic zero every group algebra is directly finite; Elek and Szabo proved stable
  finiteness for sofic groups, so the group of Theorem 1.1 is not sofic.
- [P] Proposition 2.1, parity criterion (pp. 3-4): for immersed graphs with roots `x_A`, `x_B`, if
  `|S_x cap S_x'|` is odd for every pair in `A' x A'` other than `(x_A, x_A)`, `|S_(x_A)|` is even, and
  `|S_x cap S_y|` is odd on `A' x B'`, and the roots are protected, then `a = sum g_x`, `b = sum g_x^(-1)`,
  `c = sum h_y^(-1)` satisfy `ab = 1`, `ac = 0`, `c != 0`. The proof is the simultaneous-step graph of family 196,
  with one even-degree vertex `(x_A, x_A)` leaving one surviving contribution, the identity.
- [P] Fano labels (p. 5): seven extra letters are identified with the points of the projective plane over `F_2`, and
  `D` consists of the complements of its seven lines. "Each D in D has four elements, and distinct members of D
  intersect in two elements. Each extra letter belongs to four members of D"; each pair of distinct extra letters
  belongs to two members. The root `x_A` carries all seven extras; prescribed vertices carry extra part exactly `D`.
- [P] Proposition 3.1 (p. 5): the prescribed sets satisfy the parity identities (3.3) and `129 <= |S_x| <= 136`.
- [P] Proof of Theorem 1.1 (p. 30): Theorem 5.2 excludes reduced spherical arrangements with probability tending to
  one; Proposition 6.1 gives asphericity, torsion-freeness and root protection; the argument "selects a finite
  matching outcome rather than listing its edges".

## Formal statement

- [P] [`lean/docs/197.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/197.md)
  links the companion characteristic-two, odd-characteristic and group-ring determinant manuscripts, not this one.
  Its two characteristic-two Comparator statements (solution modules under `OAI.RingTheory.DirectFiniteness`) are
  `KaplanskyDirectFiniteness.lean`, a finite field of characteristic two, a finitely generated group and
  `a * b = 1`, `b * a != 1` in `MonoidAlgebra K G`, with no torsion clause; and `KaplanskyFinitelyPresented.lean`,
  a finitely presented group containing an element of odd prime order. Neither asserts torsion-freeness, and
  `formalization.yaml` at the pinned commit lists no entry for this manuscript, so its torsion-free Theorem 1.1 is
  unformalized.

## Mapping to this repository

- [E] Fano complements. In `cd_core`'s index convention the seven complements of the octonion Fano lines are the
  nontrivial cosets `x xor (L cup {0})` of the order-4 subgroups of `Z_2^3`, the index sets of `O` minus a quaternion
  subalgebra `H_L` in the doubling `O = H_L + H_L e_x`. The replay confirms the paper's counts: four elements each,
  pairwise intersections two, four complements per point, two per pair of points
  ([kaplansky-cd-mechanisms](../../evidence/kaplansky-cd-mechanisms/README.md), gate sources-412). The paper uses
  the Fano plane only as this incidence design; the octonion signs play no role there.
- [I] Opposite outcome. Every Cayley-Dickson algebra over the reals is directly finite: the
  [Kaplansky mechanisms note](../topics/kaplansky-mechanisms-cayley-dickson.md#direct-finiteness) proves it from
  the purity of annihilators, a mechanism independent of associativity.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: low (a shared incidence design and an opposite answer; no shared theorem).
- [I] Factoring resource estimates: none.

## Boundaries

[I] No proof step outside pp. 1-5 and 30 was checked, and the manuscript is unrefereed.
