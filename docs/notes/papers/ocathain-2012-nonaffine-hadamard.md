# O Cathain 2012 -- Difference sets and doubly transitive actions on Hadamard matrices

## Source copy and license

The [DORAS PDF](https://doras.dcu.ie/29113/1/NonaffineHadamard.pdf) is a repository deposit, not the version of
record: it carries the date 27 February 2012 and the Galway affiliation of the author, and the
[DORAS record](https://doras.dcu.ie/29113/) lists the item as the published Journal of Combinatorial Theory,
Series A article with the notices "Copyright Information: (c) 2012 Elsevier" and a Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 license for the deposited file. The two statements disagree on their
face, and the record does not say which text the license covers, so the PDF stays external under a manual audit:
its optional personal reading copy is `docs/local_source_cache/ocathain-2012-nonaffine-hadamard.pdf`, and
[SOURCES.json](../../SOURCES.json) records the SHA-256 of the bytes read, the SHA-256 of the DORAS record page
and the reading scope. The repository retains no capture of the record page.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Page numbers are the printed
page numbers of the deposited text, which equal the PDF page indices.

## Citation and provenance

- Author: Padraig O Cathain (National University of Ireland, Galway at the date of the deposited text).
- Version of record: Journal of Combinatorial Theory, Series A 119(6), 1235-1249 (August 2012), DOI
  10.1016/j.jcta.2012.02.011 (Crossref receipt below, which names the Elsevier user license and lists a single
  author). The deposited text has 20 pages, so its pagination differs from the journal's.
- PDF read: https://doras.dcu.ie/29113/1/NonaffineHadamard.pdf, 20 pages.
- SHA-256: `9753fda50325ac57bdc98ab5bd18c669f7482771e93a2e8d7b8ae02934ab66db`
- Reading scope: abstract, Sections 1 to 6 through Theorem 50 (pp. 1-17) including the statements of Theorems 33
  and 42; the proofs of Lemmas 35 to 46 (the regular subgroups of `AGammaL_1(q)`), Section 7 on Hall's sextic
  residues and Corollary 51 onward read as statements or headings only.

| Source | URL | SHA-256 of retrieved bytes | Read for |
|---|---|---|---|
| Crossref record of the version of record | https://api.crossref.org/works/10.1016/j.jcta.2012.02.011 | `161004531beeb370d49427d1451345e174b2cab7e83d27e252e8b84d44344ac7` | Bibliographic identity |

## Transcribed statements

Conventions [P]: Definition 1 (p. 2): Hadamard matrices `H` and `H'` are equivalent if `P H Q^T = H'` for
`{+-1}`-monomial matrices `P, Q`; `Aut(H)` is the group of pairs `(P, Q)` of `{+-1}`-monomial matrices with
`P H Q^T = H`, and `PermAut(H)` its subgroup with `P` and `Q` permutation matrices. Definition 2 (p. 2): a
`{+-1}`-monomial matrix factors uniquely as a diagonal matrix times a permutation matrix `E_X`; `nu(P, Q) = E_P`
is a homomorphism, and `A(H) = nu(Aut(H))` is the permutation group on the rows of `H`.

- [P] Lemma 7 (p. 4): a symmetric `2-(4n - 1, 2n - 1, n - 1)` design with incidence matrix `M`, `T = 2M - J`, gives
  the Hadamard matrix `H = [[1, 1^T], [1, T]]`; Remark 8 (p. 5) gives the converse through the core of a normalized
  matrix.
- [P] Theorem 10 (Ito, p. 5): if `A(H)` is non-affine and doubly transitive, its action is one of `M_12` on 12
  points, a group `PSL_2(p^k)` normal in `A(H)` acting naturally on `p^k + 1` points for `p^k = 3 mod 4` and
  `p^k != 3, 11`, or `Sp_6(2)` on 36 points.
- [P] Theorem 11 (pp. 5-6): `Aut(S)` of the design is isomorphic to `PermAut(H)`.
- [P] Definition 20 (p. 8): for a prime power `q = 3 mod 4` the quadratic residues of `F_q` form a difference set in
  the additive group of `F_q`, the Paley difference set; its design is a Paley design and a Hadamard matrix
  developed from it a Paley Hadamard matrix (Type I).
- [P] Theorem 21 (Kantor; de Launey and Stafford, p. 9): for a Paley Hadamard matrix `H` of order `p^n + 1 > 12`,
  `Aut(H)` is an extension of `C_2` by `P Sigma L_2(p^n)`, that is `PSL_2(p^n)` extended by field automorphisms.
- [P] Theorem 23 (p. 9): for a normalized Hadamard matrix of order `q + 1`, `q = 3 mod 4`, `q > 11`,
  `PSL_2(q)` in its natural doubly transitive action is normal in `A(H)` if and only if `H` is equivalent to a
  Paley Hadamard matrix.
- [P] Corollary 24 (p. 9): `A(H)` is non-affine and doubly transitive if and only if `H` has order 12, or lies in the
  unique equivalence class of order 36 on which `Sp_6(2)` acts, or has order greater than 12 and is equivalent to
  a Paley Hadamard matrix. Remark 25 (p. 10): the Paley matrices of order below 12 are excluded because their
  automorphism groups are affine doubly transitive; they are equivalent to Sylvester matrices.
- [P] Theorem 28 (de Launey and Stafford, p. 10): a Paley Hadamard matrix of order `q + 1` is cocyclic over the
  dihedral group of order `q + 1` with dicyclic extension group, with additional extension groups only for
  `q in {3, 7, 11, 23, 59}`.
- [P] Theorem 33 (p. 12): for the Paley Hadamard matrix of order `q + 1`, `q = p^(np)`, `n` coprime to `p`, the
  stabilizer `A(H)_1` has `e + 1` conjugacy classes of regular subgroups, one normal elementary abelian and the
  others non-normal and non-abelian.
- [P] Definition 44 (p. 15): a difference set `D` is skew if `D cap D^(-1)` is empty and `G = D cup D^(-1) cup {1}`;
  skew difference sets have parameters `(4n - 1, 2n - 1, n - 1)`. Lemma 48 (p. 16): with `M` the `+-1` matrix of the
  difference set, `M + I` is skew-symmetric if and only if `D` is skew-Hadamard. Theorem 49 (p. 17): the group `T_1`
  contains a skew-Hadamard difference set, the first triply infinite family of skew difference sets inequivalent
  to the Paley family and the first known in non-abelian `p`-groups of unbounded exponent. Theorem 50 (p. 17): a
  Hadamard matrix of order greater than 8 with affine doubly transitive automorphism group is not developed from a
  skew-Hadamard difference set.

## Mapping to this repository

- [I] Overlap with [cd-star-lattice-tower](../topics/cd-star-lattice-tower.md#the-boundary-as-a-paley-matrix): the
  repository records `G_8 = SL(2, 7)` acting on the projective line over `F_7` through `PSL(2, 7)` for the
  octonion boundary, and the Paley matrix of order 8 (`q = 7`). Theorems 21 and 23 and Corollary 24 apply to orders
  above 12, so they do not cover the order-8 matrix: by Remark 25 that matrix is equivalent to a Sylvester
  matrix with an affine doubly transitive group. Theorem 10 as printed excludes `p^k = 3, 11` and not 7, so the
  list in Theorem 10 and the order bound of Theorem 21 together leave the order-8 case to Remark 25; the repository
  takes no `PSL(2, 7)`-normal claim for order 8 from this paper.
- [I] The paper states no octonion, sedenion or Cayley-Dickson fact, no `PSL(2, 7)` order, and no signed-permutation
  automorphism of a `cd_core` matrix. The `{+-1}`-monomial pairs `(P, Q)` of Definition 1 are the object the
  repository counts as "automorphism pairs" for `I + W_16` (86016 pairs in the star-lattice note), so Definition 1
  fixes that counting convention: pairs `(P, Q)` with `P H Q^T = H`, counted with `(-I, -I)`.
- [I] `I + W_n` is skew in the sense of Lemma 48. Theorem 50 would bear on it only for orders above 8 and only if
  its automorphism group were affine doubly transitive; this note runs no transitivity check, and the
  star-lattice note places order 16 outside the Paley list because 15 is not a prime power.

## Relevance

- [I] Cayley-Dickson structure: low to medium (Paley and `PSL_2(q)` statements and the definition of the
  automorphism pairs counted in the star-lattice note).
- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The proofs of the regular-subgroup lemmas (35 to 46) and of Theorem 54 on Hall matrices were not read. The
statements are those of the deposited 2012 text, whose numbering may differ from the journal's. The record page
shows a license for the deposited file and an Elsevier copyright notice and the repository settles neither
into a redistribution grant.
