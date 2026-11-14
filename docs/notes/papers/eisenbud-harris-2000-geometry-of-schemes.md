# Eisenbud and Harris 2000: The Geometry of Schemes (Graduate Texts in Mathematics 197)

## Source copy and license

The [source PDF](https://doi.org/10.1007/b97680) remains external to the published library. It is a copy of the Springer edition (cover, series pages, title page, imprint page, contents, Chapters I to VI, the references and the index),
acquired from a third-party mirror and held as a private reading copy. PDF page 5 (the imprint page) carries the line "(c) 2000 Springer-Verlag New York, Inc.", the sentence "All rights reserved" with the publisher's permission terms, and the ISBNs
0-387-98637-5 (softcover) and 0-387-98638-3 (hardcover); the PDF holds no redistribution grant, so the registry records it as external-only under `NOASSERTION` with the imprint page as the rights locator. The Crossref record of the DOI lists one license entry,
the Springer text-mining terms (`http://www.springer.com/tdm`), which are Springer's own terms and no Creative Commons or public-domain grant; the registry does not rely on them for rehosting. The reading copy is the ignored
`docs/local_source_cache/eisenbud-harris-2000-geometry-of-schemes.pdf`, with a second copy in the owner's private documents repository. [SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope.
Attribution to David Eisenbud and Joe Harris applies to every statement below.

Tag convention: [P] marks a statement of the book; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index minus 7 in Section IV.2 (PDF page 169 is printed page 162 and PDF page 183 is printed page 176). The contents pages carry Roman numerals equal to the PDF index (PDF page 8 is page viii and PDF page 10 is page x).

## Citation and provenance

- Authors: David Eisenbud (Mathematical Sciences Research Institute, Berkeley) and Joe Harris (Harvard University). Title page: The Geometry of Schemes, with 40 illustrations; Graduate Texts in Mathematics 197, Springer (PDF pages 2, 4 and 5).
- DOI [10.1007/b97680](https://doi.org/10.1007/b97680). The Crossref record (title, publisher Springer-Verlag, print ISBN 0387986383, year 2000, series title Graduate Texts in Mathematics) is a registered retrieval receipt; the record lists no
  authors and no volume number, so the authors and the volume come from the title page and the series page of the PDF.
- Retained PDF: 300 pages, 3569503 bytes, SHA-256 `5a82206a220e17140f389b5c5dd3617d4f947c0fc6085517c08e9feae917850d`.
- Reading scope (each page opened as an image, no text extraction): PDF pages 1 to 10 (cover, series pages, title page, imprint page, epigraph and the contents, pages vii to x); printed pages 162 to 176 (PDF pages 169 to 183: Section IV.2 from its
  opening through Section IV.2.1 and Section IV.2.2 up to Exercise IV-30). The rest of the book was not read: Chapters I to III, Section IV.1, Section IV.2 from page 177 (the rest of Section IV.2.2 and Sections IV.2.3 to IV.2.5), Sections IV.3 and IV.4,
  Chapters V and VI, the references and the index.
- Status: published book.

## Definition of the blow-up and the affine construction (Section IV.2.1, pp. 162-169)

- [P] Opening of Section IV.2 (p. 162): the section defines the blow-up of an arbitrary (Noetherian) scheme along an arbitrary closed subscheme, and refers to Hartshorne, Theorem II.7.17, for the statement that every projective birational morphism of
  varieties is a blow-up ([Hartshorne 1977](hartshorne-1977-algebraic-geometry.md)).
- [P] Example IV-14 (pp. 163-164): the blow-up `Z` of the origin of `A^2_K` over a field `K`, glued from two affine planes with coordinates `(x, y/x)` and `(x/y, y)`; the inverse image `E` of the origin is isomorphic to `P^1_K`, the map is an
  isomorphism off `E`, and the map `(a, b) -> [a, b]` on the complement of the origin extends to a regular map on `Z`.
- [P] Definition IV-15 (p. 165): a subscheme `Y` of a scheme `X` is a Cartier subscheme when it is locally the zero locus of a single nonzerodivisor, and a regular subscheme when it is locally the zero locus of a regular sequence.
- [P] Definition IV-16 (p. 165): the blow-up of `X` along `Y` is the morphism `phi : Bl_Y(X) -> X` such that (1) the inverse image of `Y` is a Cartier subscheme and (2) every morphism `f : W -> X` for which the inverse image of `Y` is Cartier
  factors uniquely through `phi`. The inverse image `E` of `Y` is the exceptional divisor and `Y` the center.
- [P] Example IV-17 (pp. 165-166), for any ring `A` and `A^n_A = Spec A[x_1, ..., x_n]`: `Z` is the union of the affine spaces `U_i = Spec A[x_1/x_i, ..., x_n/x_i, x_i]`. (1) With `U` the complement of `V(x_1, ..., x_n)` and
  `alpha : U -> P^(n-1)_A` the morphism given by `(x_1, ..., x_n)`, `Z` is the closure in `A^n_A x_A P^(n-1)_A` of the graph of `alpha`. (2) The preimage `E` of `V(x_1, ..., x_n)` is isomorphic to `P^(n-1)_A`, and `Z minus E` maps
  isomorphically to `U`. (3) `E` is locally defined by a single equation.
- [P] Proposition IV-18 (p. 166): the morphism `Z -> A^n_A` is the blow-up of `A^n_A` along `V(x_1, ..., x_n)`. The proof (pp. 166-167) treats a local ring first, by Nakayama's lemma, and then glues.
- [P] Lemma IV-19 (p. 167): if `X` is a Cartier subscheme of a scheme `Y`, then `Y minus X` is dense in `Y`, as schemes and not only as topological spaces. Exercise IV-20 (p. 167): the conclusion fails for `V(x)` in
  `Spec K[x, y]/(xy, y^2)`; it characterizes Cartier subschemes among locally principal ones; `Bl_Y` is empty if and only if `supp Y = supp X`.
- [P] Proposition IV-21 (pp. 167-168): for the blow-up `phi : Bl_Y(X) -> X`, a morphism `nu : X' -> X` and `Y'` the inverse image of `Y`, the closure `W` in the fiber product `X' x_X Bl_Y X` of the inverse image of `X' minus Y'` is, with
  its projection to `X'`, the blow-up of `X'` along `Y'`. Remarks on p. 168: for `X' = X` the inverse image of `X minus Y` is dense in the blow-up; for a closed subscheme `X'` of `X` the closure `W` is the strict (proper) transform of `X'`; for an open
  subscheme `X'` the blow-up restricts to the blow-up of `X'` along `X' intersect Y`, so blow-ups are determined locally.
- [P] Proposition IV-22 (p. 169): for an affine scheme `X = Spec A` and the closed subscheme `Y = V(f_1, ..., f_n)`, the blow-up of `Y` in `X` is the closure in `X x_A P^(n-1)_A = P^(n-1)_A` of the graph of the morphism
  `alpha_(f_1, ..., f_n) : X minus Y -> P^(n-1)_A`. The proof embeds `X` in `A^n_A` by `x_i -> f_i` and applies Propositions IV-18 and IV-21. The paragraph after it says that the restriction to finitely many `f_i` is unnecessary.

## The blow-up as Proj and regular subschemes (pp. 170-173)

- [P] Theorem IV-23 (p. 170): for a scheme `X`, a closed subscheme `Y` with ideal sheaf `I` and the sheaf of graded `O_X`-algebras `A = O_X + I + I^2 + ...`, the scheme `Proj(A) -> X` is the blow-up of `X` along `Y`. The proof (pp. 170-171) shows that
  `I O_B = O_B(1)` is invertible on `B = Proj(A)`, and uses the surjection `Sym(I) -> A` to realize `B` as a closed subscheme of `P(I) = Proj Sym(I)`; it assumes `I` coherent for simplicity and says the quasicoherent case follows by a generalization
  of Theorem III-44.
- [P] Exercise IV-24 (p. 171): the exceptional divisor of the blow-up of a scheme `X` at a point `p` is the projectivized tangent cone to `X` at `p`. The book states this as an exercise.
- [P] Page 171 calls `A = sum of t^n I^n` inside `O_X[t]` the Rees algebra and remarks that its relations are hard to find in general. Proposition IV-25 (p. 172): for a Noetherian ring `A` and a regular sequence `x, y`, the Rees algebra
  `A[xt, yt]` is `A[X, Y]/(yX - xY)`. Exercise IV-26 (p. 173): for an ideal generated by a regular sequence `x_1, ..., x_n`, the Rees algebra is `A[X_1, ..., X_n]` modulo the `2 x 2` minors of the matrix with rows `x_i` and `X_i`.
- [P] Section IV.2.2 (pp. 173-176): Example IV-27, the blow-ups of the quadric cone `V(xy - z^2)` at its vertex and along a line; Exercise IV-28; Example IV-29 and Exercise IV-30, the three blow-ups of the cone over a quadric surface at its vertex
  and along the planes of its two rulings.

## Mapping to this repository

- [I] Graph closure. The A_5 fiber-cone program (`docs/evidence/a5-exceptional-fibers/ledger.tsv`, rows A5-416 and A5-418) studies the blow-up of a germ along an ideal `I = (a_1, ..., a_n)` through the map
  `x -> [a_1(x) : ... : a_n(x)]` on the complement of `V(I)`. Proposition IV-22 (p. 169) is that description for an affine scheme over any ring: the blow-up is the closure of the graph of that map in `Spec A x P^(n-1)`. Theorem IV-23 (p. 170)
  identifies the same scheme with `Proj` of the Rees algebra, so the defining ideal of the graph closure is the ideal of forms vanishing on the generators that
  [Huneke and Swanson 2006](huneke-swanson-2006-integral-closure-ideals-rings-modules.md) present on p. 110; the two books together give the statement that neither gives alone.
- [I] Density. Lemma IV-19 and the case `X' = X` of Proposition IV-21 give that the complement of the exceptional divisor is scheme-theoretically dense in the blow-up, which is the algebraic form of "the blow-up is the closure of its open part".
  The comparison of that Zariski closure with a closure in the complex topology is a separate statement
  ([Mumford 1999](mumford-1999-red-book-varieties-schemes.md), Section I.10, Corollary 1).
- [I] Strict transform. For a closed subscheme `X'` of `X`, Proposition IV-21 identifies the blow-up of `X'` along `X' intersect Y` with the closure of the preimage of `X' minus Y`; this is the statement that lets a blow-up of a subvariety be computed
  inside the blow-up of an ambient affine space.
- [I] What the pages read do not give. (a) No general description of the fiber of the blow-up over a point of the center; the pages give worked cases only (Examples IV-14, IV-17 (2), IV-27 and IV-29, and Exercises IV-24 and IV-30 (c)); the exceptional
  divisor as a projective normal cone is in [Fulton 1998](fulton-1998-intersection-theory.md), B.6.3. (b) No statement on fiber cones, analytic spread or integral closure. (c) No statement over a non-affine base in Proposition IV-22, and no
  comparison between characteristics.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Only the pages listed under the reading scope were opened. The note asserts nothing about Chapters I to III (including Theorem III-44 and Exercise III-46, which the proof of Theorem IV-23 cites), Section IV.1, the part of Section IV.2 from page 177,
Sections IV.3 and IV.4 or Chapters V and VI. Proofs were read through and are not re-derived here, and no claim in this note rests on a computation in this repository.
