# Mumford 1999: The Red Book of Varieties and Schemes, second edition (Lecture Notes in Mathematics 1358)

## Source copy and license

The [source PDF](https://doi.org/10.1007/b62130) remains external to the published library. It is a scan of the Springer
second, expanded edition (cover, series page, title page, copyright page, preface, table of contents, Chapters I to III, the
appendix on curves and their Jacobians, the references and Arbarello's supplementary bibliography), acquired from a third-party
mirror and held as a private reading copy. PDF page 5 (printed page IV, the copyright page) reads "This work is subject to
copyright. All rights are reserved" and carries the line "(c) Springer-Verlag Berlin Heidelberg 1999"; the chapter-opening
page of Chapter I (PDF page 12, printed page 1) repeats "(c) Springer-Verlag Berlin Heidelberg 1999". The PDF holds no
redistribution grant, so the registry records it as external-only under `NOASSERTION` with the copyright page as the rights
locator. The Crossref record of the DOI lists one license entry, the Springer text-mining terms (`http://www.springer.com/tdm`),
which are Springer's own terms and no Creative Commons or public-domain grant; the registry does not rely on them for
rehosting. The reading copy is the ignored `docs/local_source_cache/mumford-1999-red-book-varieties-schemes.pdf`, with a second
copy in the owner's private documents repository. [SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope.
Attribution to David Mumford applies to every statement below.

Tag convention: [P] marks a statement of the book; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index minus 11 through printed page 63 (PDF page 12 is printed page 1 and PDF page 74 is
printed page 63); the scan omits printed page 64, so Chapter II opens at PDF page 75 (printed page 65) and PDF page 76 is printed
page 66. The front matter is numbered in Roman numerals (PDF page 5 is printed page IV).

## Citation and provenance

- Author: David Mumford (Division of Applied Mathematics, Brown University, at the time of printing). The second edition adds
  the 1974 Michigan lectures on curves and their Jacobians (the appendix) and Enrico Arbarello's survey and supplementary
  bibliography on the Schottky problem (title page and table of contents).
- Edition and identity: second, expanded edition, Lecture Notes in Mathematics 1358, Springer-Verlag Berlin Heidelberg 1999,
  ISBN 3-540-63293-X (print), ISSN 0075-8434, DOI [10.1007/b62130](https://doi.org/10.1007/b62130). The Crossref record (title,
  author, publisher, container title `Lecture Notes in Mathematics`, year 1999, the print ISBN 9783540632931 and the electronic
  ISBN 9783540460213) is a registered retrieval receipt; the record carries no series volume number and no edition statement,
  so the volume 1358 and the edition come from the cover and the copyright page of the PDF.
- Retained PDF: 312 pages, 52454837 bytes, SHA-256 `28a2ca3ac335162ce26faa3f6e8a081a548e82dc7e8426e8f2b81bd626d2f00b`.
- Reading scope (each page opened as an image, no text extraction): PDF pages 1 to 12 (cover, series page, imprint page, title
  page, copyright page, both prefaces, the table of contents and the first page of Chapter I, printed pages up to X and 1);
  PDF pages 27 to 29 and 31 to 38 (printed pages 16 to 18 and 20 to 27: sheaves, Definitions 4 to 6 and Propositions 1 to 4 of
  Section I.4 on affine varieties, and Definitions 1 to 4 and Propositions 1 to 5 of Section I.5 on prevarieties); PDF pages 44,
  45, 47 to 50 (printed pages 33, 34 and 36 to 39: products of affine varieties, Theorem 3, the Hausdorff axiom and Propositions
  4 to 6 of Section I.6); PDF pages 61 to 65 (printed pages 50 to 54: the end of Theorem 3, Definition 2 of constructible sets,
  Corollaries 2 and 3, Theorem 4 of Section I.8 and the opening of Section I.9); PDF pages 68 to 76 (printed pages 57 to 63 and
  65 to 66: Section I.10 in full, from its heading on printed page 57 through the end of the proof of Chow's lemma on printed
  page 63, then the opening of Chapter II). The rest of the book was not read: in Chapter I the printed pages 2 to 15, 19, 28 to 32, 35, 40 to 49 and
  55 to 56 (Sections I.1 to I.3, the rest of I.4 to I.6, I.7, most of I.8 and the body of I.9), and every page of Chapters II and III, the
  appendix, the references and the supplementary bibliography.
- Status: published book (second edition of the Springer lecture notes).

## Setting and conventions

- [P] Page 1 (opening of Chapter I): the ground field `k` is algebraically closed and fixed throughout the chapter; the chapter
  treats varieties by the elementary geometric operations only, with no specialization and no generic points.
- [P] Definition 5 of Section I.4 (p. 22): an affine variety is a topological space with a sheaf of `k`-valued functions that is
  isomorphic to an irreducible algebraic subset of some `k^n` with its sheaf. Definition 4 (p. 20) defines the sheaf of an
  irreducible algebraic set `X` from the coordinate ring `R = k[X]`, a domain, as the intersections of the local rings.
- [P] Definition 1 and Proposition 1 of Section I.5 (p. 25): a prevariety is a topological space with a sheaf of `k`-valued
  functions that is connected and has a finite open cover by affine varieties, and every prevariety is an irreducible topological
  space. Proposition 4 (p. 27): an open subset of a prevariety is a prevariety; Propositions 4 and 5 together give a prevariety
  structure to the locally closed subsets (p. 27).
- [P] Definition 2 of Section I.6 (p. 37): a variety is a prevariety `X` that satisfies the Hausdorff axiom (for all prevarieties
  `Y` and morphisms `f, g : Y -> X`, the set where `f` and `g` agree is closed); Proposition 4 (p. 37) states that this holds
  if and only if the diagonal of `X x X` is closed. Remark II (p. 38): an affine variety is a variety; Remark I: a subvariety of a
  variety and a product of two varieties are varieties; the Corollary on p. 39: every projective variety is a variety. Theorem 3
  (p. 36): the product of two projective varieties is a projective variety (the Segre embedding).
- [P] Definition 2 of Section I.8 (p. 51): a subset of a variety is constructible if it is a finite union of locally closed
  subsets; the constructible sets form a Boolean algebra, the smallest one containing the open sets. Corollary 2 (Chevalley,
  p. 51): the image of a morphism `f : X -> Y` is constructible in `Y`, and `f` maps constructible sets in `X` to constructible
  sets in `Y`.

## Section I.10, complex varieties

- [P] Strong topology (p. 57, opening of Section 10): for an algebraically closed ground field `k` given a topology that makes it
  a topological field, the book asserts a unique way to give every variety over `k` a topology, the strong topology, subject to
  five properties: (i) it is finer than the Zariski topology, so a Zariski-closed (open) subset is strongly closed (open); (ii)
  all morphisms are strongly continuous; (iii) on a locally closed subvariety `Z` of `X` the strong topology is the one induced
  from `X`; (iv) the strong topology on `X x Y` is the product topology; (v) on the affine line it is the given topology of
  `k`. The text leaves the existence of such a family to the reader, states that at most one exists, and derives from (i) and
  (iv) that every variety is Hausdorff in its strong topology.
- [P] Page 57 (end of the opening): "From now on, suppose k = C with its usual topology." The strong topologies are then the
  structure of a complex analytic space (footnote 3 defines it as a Hausdorff space with a sheaf of `C`-valued functions locally
  isomorphic to the zero locus of holomorphic functions in a polydisc), and p. 58 lists the properties of the sheaf `Omega_X`
  of strongly continuous `C`-valued functions: it contains the Zariski structure sheaf, every morphism is holomorphic, it
  restricts to locally closed subvarieties, and on `C^n` it is the sheaf of holomorphic functions.
- [P] Theorem 1 (p. 58): for a variety `X` over `C` and a nonempty open subvariety `U` of `X`, the set `U` is dense in `X` in the
  strong topology. The proof (pp. 58 to 60, attributed to suggestions of G. Stolzenberg) reduces to affine `X` because the
  statement is local in the Zariski topology, takes a finite surjective morphism `pi : X -> A^n` from Noether normalization, and
  picks a nonzero polynomial `g` that vanishes on `pi(X - U)`. For a point `x` of `X - U`, the proof joins `pi(x)` to a point
  `y^(1)` with `g(y^(1))` different from 0 by a complex line, giving points `y^(i)` of that line with `g(y^(i))` nonzero that converge to
  `pi(x)` in the strong topology, lifts them in two steps to points `z^(i)` of `X` over `y^(i)` (the book reuses the letter `g` on p. 59 for a second function, called `h` here: a regular function on `X` that vanishes at `x` and at no other point of its fiber; the irreducible equation of `h` over the polynomial ring
  controls the roots, and the integrality of the coordinate functions confines the preimage of a relatively compact set to a
  relatively compact set), and shows that a limit point of the lifts is `x` itself. These points lie in `U` because
  `pi(Z)` lies in the zero set of `g`.
- [P] Corollary 1 (p. 60), stated directly after the end of the proof of Theorem 1 with no further proof printed: "If Z ⊂ X is a
  constructible subset of a variety, then the Zariski closure and the strong closure of Z are the same." The variety is a
  variety over `C` in the sense of Definition 2 of Section I.6, and the strong topology is the one of the opening of Section
  10 for `k = C`.
- [P] Theorem 2 (p. 60): a variety `X` over `C` is complete if and only if it is compact in the strong topology. In the proof of
  the direction from compact to complete the book takes a strongly closed image under a proper projection, observes that it is
  constructible by the Chevalley theorem of Section I.8 (the text cites "Th. 3, Cor. 3" of Section 8, while the Chevalley
  corollary stands on p. 51 as Corollary 2 and Corollary 3 states upper semicontinuity of the fiber dimension), and concludes that
  it is Zariski closed "by the Cor. to Theorem 1". The book therefore uses Corollary 1 in the form that a constructible set that
  is strongly closed is Zariski closed.
- [P] Chow's lemma and the sublemma (pp. 60 to 63) complete Section I.10; they bear on the passage from complete to projective
  varieties and carry no statement about closures.

## Mapping to this repository

- [I] Ledger rows A5-411, A5-412 and A5-417 of `docs/evidence/a5-exceptional-fibers/ledger.tsv` cite this book, directly or
  through row A5-411, for the equality of the Zariski closure and the Euclidean closure of a complex constructible set. The book
  states that equality as Corollary 1 on printed page 60 (PDF page 71), resting on Theorem 1 on printed page 58 (PDF page 69);
  Theorem 1 itself asserts the density of a nonempty open subvariety. A row that names "I.10 Theorem 1" for the closure equality
  means Corollary 1, and this note supplies the inspected locator.
- [I] What the rows may cite: for a constructible subset `Z` of a variety `X` over `C` in the book's sense (irreducible, Hausdorff
  axiom), the Zariski closure of `Z` equals its closure in the classical topology. The inclusion of the strong closure in the
  Zariski closure is property (i) of Section 10 (a Zariski-closed set is strongly closed); the reverse inclusion is the content of
  Theorem 1, in three steps: for a locally closed piece `L` of `Z`, pass to each irreducible component `W` of the Zariski closure
  of `L`; the intersection of `L` with `W` is a nonempty open subvariety of `W`, since `L` is open and dense in its closure, so
  Theorem 1 makes it strongly dense in `W`; and property (iii) of Section 10 (the strong topology of a locally closed subvariety
  is the induced one) carries that density into `X`. The corollary has no proof printed, and this reduction is the repository's
  reading of the statement and is not a quotation of a proof.
- [I] Hypotheses the rows meet or must meet. The ambient space is a variety in the book's sense, so it is irreducible: an affine
  space `C^15` times a Grassmannian embedded in a projective space is such a variety, since `C^15` is an affine variety (Remark II,
  p. 38), a projective variety is a variety (the Corollary on p. 39) and a product of two varieties is a variety (Remark I, p. 38), where the Pluecker embedding of the Grassmannian is a fact outside the pages read. A reducible ambient algebraic set
  is covered component by component (Zariski closure and strong closure of a finite union are the unions of the closures).
  The constructibility of the graph of `z -> ker C_z` over its source stratum is the rows' own claim; Corollary 2 of Section I.8
  (p. 51), the Chevalley theorem for the image of a morphism, is the book's route to constructibility of such sets.
- [I] What the corollary does not give. (a) It holds over `C` only: the section defines the strong topology for any algebraically
  closed topological field but proves Theorem 1 and Corollary 1 after fixing `k = C`; it gives no statement over `Q(i)`, over
  `F_p` or over `R` without a base change to `C`, and the rows' statements about the fiber cones over `Q(i)` and modulo primes
  are separate records. (b) It describes the complex points; the real semialgebraic realization of a limit by a path, which the
  rows take from curve selection ([Basu and Roy](../1803.00505.md)), is not part of it. (c) It requires a constructible set: a
  Zariski-dense set that is not constructible, such as the integer lattice points of `C^n`, is strongly closed, so its two closures
  differ. (d) It states equality of closures and gives neither a path nor a sequence in `Z` that converges to a given point of
  the closure.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Only the pages listed under the reading scope were opened. The note asserts nothing about Chapters II and III, the appendix
on curves and their Jacobians, Sections I.1 to I.3 and I.7, or the printed pages of Sections I.4 to I.9 outside the pages listed
(including printed pages 55 and 56 of Section I.9, on completeness, and the earlier results of Section I.8 on dimension of
fibers); the definitions of Sections I.4 to I.8 enter only as read on those pages. The proof of Theorem 1 was read through and is not
re-derived here, and no claim in this note rests on a computation in this repository.
