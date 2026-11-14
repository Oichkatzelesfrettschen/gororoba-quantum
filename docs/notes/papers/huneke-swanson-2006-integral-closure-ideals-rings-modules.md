# Huneke and Swanson 2006: Integral Closure of Ideals, Rings, and Modules (London Mathematical Society Lecture Note Series 336)

## Source copy and license

The [source PDF](https://www.math.purdue.edu/~iswanso/book/SwansonHuneke.pdf) remains external to the published library. It is the
authors' own typeset copy of the book, downloaded from the author's web page and held as a private reading copy. The first 14 PDF
pages (series title page, title page, contents, table of basic properties, notation, preface) carry no copyright page, no
imprint page, no publisher license and no rights statement; the PDF prints neither the publication year nor an ISBN in those pages.
The title page names the series (London Mathematical Society Lecture Note Series 336), the authors (Craig Huneke, University of
Kansas; Irena Swanson, Reed College, Portland) and Cambridge University Press. The registry records the copy as external-only
under `NOASSERTION` and names the absence of a rights statement on PDF pages 1 to 14 as the rights locator; the copy's relation
to the printed edition is not established by the PDF, and it shows that it differs from an earlier version: on printed pages 163 and 164 (PDF pages 177 and 178) the margin of Theorem 8.3.5 reads "(was Theorem 8.3.6)" and that of
Corollary 8.3.6 reads "(was 8.3.5)". Page and item numbers in this note are the numbers of this copy; a citation against the Cambridge University Press printing needs its own check, since pagination and numbering may differ. The reading copy is the ignored
`docs/local_source_cache/huneke-swanson-2006-integral-closure-ideals-rings-modules.pdf`, with a second copy in the owner's private
documents repository. [SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope. Attribution to Craig Huneke and
Irena Swanson applies to every statement below.

Tag convention: [P] marks a statement of the book; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers equal the PDF page index minus 14 for the Arabic-numbered pages (PDF page 113 is printed page 99 and PDF page
217 is printed page 203); the front matter carries Roman numerals equal to the PDF page index (PDF page 5 is page v).

## Citation and provenance

- Authors: Craig Huneke and Irena Swanson. Title: Integral Closure of Ideals, Rings, and Modules. Series: London Mathematical
  Society Lecture Note Series 336, Cambridge University Press. The retained PDF prints no publication year and no ISBN. The year 2006 is the year under which the Cambridge University Press edition is cited; neither the PDF nor a registered retrieval receipt confirms it.
- Crossref: a bibliographic search for the title and authors (retrieval receipt in [SOURCES.json](../../SOURCES.json)) returned
  three records, two papers of Delfino and Swanson on integral closure in excellent local rings (1997 and its 2004 erratum) and a 2019
  chapter of Aberbach and Huneke; none is the book, so the registry carries no DOI for it.
- Retained PDF: 463 pages, 3521018 bytes, SHA-256 `a12705f066aee67648768bc37b58a37c661907dc3918a71974c1441bc551a18b`.
- Reading scope (each page opened as an image, no text extraction): PDF pages 1 to 14 (title pages, contents pages v to viii, the
  table of basic properties on pages ix and x, the notation on pages xi and xii, the preface on pages xiii and xiv); printed pages 99
  to 102 (PDF pages 113 to 116: the opening of Chapter 5 with Section 5.1 and the start of Section 5.2); printed pages 110 to 118
  (PDF pages 124 to 132: the end of Section 5.4, Section 5.5, Section 5.6 and the exercises 5.1 to 5.28 of Section 5.7); printed
  pages 157 to 166 (PDF pages 171 to 180: Chapter 8 from its opening through the start of Section 8.4); printed pages 195 to 203
  (PDF pages 209 to 217: Chapter 10 from its opening through Corollary 10.2.7); printed pages 439 to 449 (PDF pages 453 to 463: the index, searched for the entries blowup, Proj, fiber cone and special fiber). The rest of the book was not read: Chapters 1 to 4,
  the remaining pages of Chapter 5 (103 to 109), Chapters 6, 7 and 9, the remainder of Chapter 8 (pages 167 to 184), the remainder of
  Chapter 10, Chapters 11 to 19, both appendices and the references.
- Status: published book (authors' copy; see the license section).

## Setting and conventions

- [P] Notation page xi: every ring is commutative with identity and most are Noetherian; `(R, m)` is a local ring. Notation page xii:
  `R[It]` and `R[It, t^-1]` are the Rees and extended Rees algebras (Chapter 5), `gr_I(R)` the associated graded ring and
  `F_I(R)` the fiber cone (both Definition 5.1.5), `ell(I)` the analytic spread (Definition 5.1.5), `I : J^infinity` the union of the
  colon ideals `I : J^n`, `r_J(I)` the reduction number (Definition 8.2.3) and `RV(I)` the set of Rees valuations.
- [P] Table of basic properties, items (20) and (21) (p. x): for a Noetherian local ring `ht(I) <= ell(I) <= dim R`
  (Corollary 8.3.9), and with an infinite residue field a minimal reduction exists and is generated by `ell(I)` elements
  (Proposition 8.3.7).

## Rees algebra, fiber cone and analytic spread (Section 5.1, pp. 99-101)

- [P] Definition 5.1.1 (p. 99): the Rees algebra `R[It]` of an ideal `I` is the subring of `R[t]` formed by the polynomials whose
  coefficient of `t^i` lies in `I^i`, that is the direct sum of the `I^n t^n`; the extended Rees algebra `R[It, t^-1]` is the
  analogous subring of `R[t, t^-1]` with `I^n = R` for `n <= 0`. For every ideal `J` of `R` the ideal `J R[It]` meets `R` in `J`.
- [P] Theorem 5.1.4 (pp. 99-100): for a Noetherian ring, `dim R` is finite exactly when the dimension of either Rees algebra is finite;
  then `dim R[It, t^-1] = dim R + 1`, and `dim R[It]` is `dim R + 1` when `I` lies outside some prime `P` with `dim R/P = dim R`
  and `dim R` otherwise.
- [P] Definition 5.1.5 (p. 100): the associated graded ring is `gr_I(R) = R[It]/I R[It]`, the direct sum of the `I^n/I^(n+1)`. For
  a Noetherian local ring `(R, m)` the fiber cone is `F_I(R) = R[It]/m R[It]`, isomorphic to the direct sum of the
  `I^n/m I^n`; the book writes it `F_I` and calls its Krull dimension the analytic spread `ell(I)`. The page records `F_I = gr_I(R)/m gr_I(R)`.
- [P] Proposition 5.1.6 (pp. 100-101): `ell(I) = dim F_I <= dim gr_I(R) = dim R` for an ideal of a local ring. Proposition 5.1.7
  (p. 101): `ell(I)` is the maximum of `ell(I(R/P))` over the minimal primes `P` of `R`.
- [P] Page 101 (after Proposition 5.1.7): the associated graded ring can be thought of as the special fiber of the extended Rees algebra, that is the ring obtained by setting `t^-1 = 0` in it; this is the book's only use of the words special fiber on the pages read (the fiber cone is the object of Definition 5.1.5).
- [P] Proposition 5.2.1 (pp. 101-102): the integral closure of `R[It]` in `R[t]` is the graded ring `R + (closure of I) t + (closure of
  I^2) t^2 + ...`; this is the Rees algebra form of the integral closure of the powers.

## Defining equations of the Rees algebra (Section 5.5, pp. 110-114)

- [P] Page 110 (opening of Section 5.5): for `I = (x_1, ..., x_n)` the Rees algebra is the image of the polynomial ring
  `R[T_1, ..., T_n]` under the map `pi` that sends `T_i` to `x_i t`; its kernel `A` is the ideal of defining equations. The map has degree 0, so
  `A` is generated by homogeneous forms `F` with `F(x_1 t, ..., x_n t) = 0`, equivalently `F(x_1, ..., x_n) = 0`. From a presentation
  `R^m -> R^n -> I -> 0` with `n x m` matrix `A_mat`, the entries of the row vector `T A_mat` are linear forms that vanish
  under `T_i -> x_i`; the ideal `L` they generate lies in `A` and equals the part `A_1` of `A` generated by all linear forms of `A`
  (left to the reader as Exercise 5.23, p. 118). `R[T]/A_1` is the symmetric algebra of `I`.
- [P] Definition 5.5.1 (p. 110): `I` is of linear type when `A_1 = A`. Definition 5.5.2 (pp. 110-111): a d-sequence, with the two
  equivalent colon conditions (the second is `((x_0, ..., x_i) : x_(i+1)) intersect (x_1, ..., x_n) = (x_1, ..., x_i)`).
  Theorem 5.5.4 (p. 111) and Corollary 5.5.5 (p. 112): an ideal generated by a d-sequence, in particular by a regular sequence,
  is of linear type. Corollary 5.5.6 (p. 112): for a regular sequence `x_1, ..., x_n` the defining ideal of the Rees algebra is
  generated by the `2 x 2` minors of the matrix with rows `x_i` and `T_i`.
- [P] Proposition 5.5.7 (p. 112): for a Noetherian ring `R`, with `S = R[T_1, ..., T_n]` and `S/A` the Rees algebra, the extended Rees algebra is the quotient
  of `S[y]` by `A S[y] + (y T_i - x_i)`, where `y` maps to `t^-1`. Proposition 5.5.8 (p. 113), for a Noetherian ring `R`: inverting `T_1` gives the
  isomorphism of `(R[T]/A)[T_1^-1]` with `R[x_1 t, ..., x_n t, (x_1 t)^-1]`, and the affine chart `R[x_2/x_1, ..., x_n/x_1]` is the
  quotient of `R[Y_2, ..., Y_n]` by the ideal generated by the dehomogenizations `T_1^(-d_i) F_i` of generators `F_i` of `A`.
  Corollary 5.5.9 (pp. 113-114): the corresponding statements for a regular sequence.
- [P] Exercises of Section 5.7 (pp. 116-118): Exercise 5.12 (p. 116) defines the relation type of `I` as the least `n` such that the
  elements of the kernel `ker(phi)` of degree at most `n` generate it, and remarks, citing reference [319], that over a Noetherian local
  ring the relation type of `I^n` is 2 for large `n`; Exercise 5.23 (p. 118) asks the reader to prove `A_1 = L` for the ideal `L` generated
  by the entries of `T A_mat` (the statement of page 110).

## Blowing up (Section 5.6, pp. 114-115)

- [P] Definition 5.6.1 (p. 114): for a graded ring `R = direct sum of R_i`, `Proj(R)` is the set of homogeneous primes not containing
  the irrelevant ideal `R_+`, with the basic open sets `D_+(f)` and the structure sheaf given by the degree-zero parts `[R_f]_0`.
  Definition 5.6.2 (p. 114): the blowup of `I` is `Bl_I(R) := Proj(R[It])` with the grading `deg t = 1`; when `I = (a_1, ..., a_n)`
  the blowup is covered by the spectra of the rings `R[I/a_i]`. Page 115 states the Cech complex of this cover and the Sancho de Salas
  exact sequence relating the cohomology of the blowup to local cohomology.
- [I] Absence record. The book states neither that the fiber of `Proj R[It]` over the closed point of `Spec R` is `Proj` of the fiber cone nor that the blowup is the closure of the graph of the rational map given by the generators of `I`, on
  any page read. Section 5.6 consists of pages 114 and 115 and was read in full; the index (pages 439 to 449, read in full) lists `blowup` on pages 114, 116, 118 and 200 (`Bl_I(R)` refers to it, and `blowup of a blowup` is on 116), `Proj` on page 114 and `fiber cone` on pages 100 and 161,
  all of them pages read, and carries no entry `special fiber`. An index entry is not a complete record of the statements of a book, so this is a bounded negative result.
- [P] Exercise 5.10 (p. 116): the blowup of a blowup is a blowup, in the form that for a Noetherian domain `R`, an ideal `I` of `R`, a nonzero `x` in `I`, an ideal `J` of the affine piece `S = R[I/x]` and a nonzero `y` in `J` there are an ideal `K` of `R` and a nonzero `z` in `K` with `R[K/z] = R[I/x][J/y]`.

## Reductions, minimal reductions and the fiber cone (Chapter 8, pp. 157-166)

- [P] Proposition 8.1.1 (p. 157): `J` is a reduction of `I` when `J I^n = I^(n+1)` for some `n` (Definition 1.2.1, recalled on p. 157); the
  property localizes at multiplicatively closed sets, at primes and at maximal ideals, and the last implies the first when `R` is Noetherian.
  Lemma 8.1.3 (p. 158): reductions are preserved by ring homomorphisms and reflected by faithfully flat ones. Lemma 8.1.4 (p. 159):
  for a Noetherian ring, `J` is a reduction of `I` exactly when `J(R/P)` is a reduction of `I(R/P)` for every minimal prime `P`.
  Lemma 8.1.10 (p. 160): a reduction `J` of `I` has the same radical, the same minimal primes and the same height as `I`.
- [P] Theorem 8.2.1 (p. 161): for ideals `J` contained in `I` of a Noetherian ring, `J` is a reduction of `I` if and only if `R[It]` is a
  finitely generated module over `R[Jt]`. Corollary 8.2.2: the least `n` with `J I^n = I^(n+1)` is the largest degree of an element in a minimal homogeneous generating set
  of `R[It]` over `R[Jt]`. Definition 8.2.3: this least `n` is the reduction number `r_J(I)`, and the absolute reduction number is its
  minimum over minimal reductions `J`.
- [P] Page 161 (displayed after Definition 8.2.3): over a Noetherian local ring `(R, m)` the fiber cone `F_I(R) = R[It]/m R[It]` is isomorphic
  to `R/m + I/mI + I^2/mI^2 + ...`. Proposition 8.2.4 (pp. 161-162): for `J` contained in `I^n` over a Noetherian local ring, with `B` the subalgebra of `F_(I^n)(R)`
  generated over `R/m` by the image of `J`, `J` is a reduction of `I^n` if and only if `F_I(R)` is a finitely generated module over `B`
  (the page stresses that the module is `F_I(R)` and not `F_(I^n)(R)`); the reduction number of `I^n` with respect to `J` is then the
  largest degree of an element of a minimal homogeneous generating set of `F_(I^n)` over `B`.
- [P] Corollary 8.2.5 (p. 162): for a reduction `J` of `I` in a Noetherian local ring, the minimal number of generators `mu(J)` is at least
  `ell(I)`; the sentence before it records that `ell(I)` is the dimension of `F_I`.
- [P] Definition 8.3.1 (p. 162): a reduction is minimal when no ideal strictly inside it is a reduction. Proposition 8.3.3 (p. 163): for a minimal reduction
  `J` of `I` over a Noetherian local ring, `J intersect mI = mJ`. Theorem 8.3.5 (p. 163): every reduction in a Noetherian local ring contains a minimal reduction.
  Corollary 8.3.6 (p. 164): if `J` is a reduction of `I` with `mu(J) = ell(I)` then `J` is a minimal reduction, `F_J` is the subalgebra of
  `F_I` generated by the image of `J` and is a polynomial ring in `ell(I)` variables over `R/m`, and `J^k intersect mI^k = mJ^k` for all `k`.
- [P] Proposition 8.3.7 (p. 164): over a Noetherian local ring with infinite residue field every minimal reduction of `I` is minimally generated by exactly `ell(I)` elements (the proof applies Noether normalization to `F_I`). Proposition 8.3.8 (p. 165): without that hypothesis some power of `I`
  has a minimal reduction generated by `ell(I)` elements. Corollary 8.3.9 (p. 165): `dim R >= ell(I) >= ht I`.
- [P] Lemma 8.4.2 (p. 166): with `R(X) = R[X]_(m R[X])` (Definition 8.4.1, a faithfully flat extension of `R` with infinite residue
  field), `mu(I) = mu(I R(X))` and `ell(I) = ell(I R(X))`, and `J` is a reduction of `I` exactly when `J R(X)` is a reduction of `I R(X)`.

## Rees valuations (Chapter 10, pp. 195-203)

- [P] Definition 10.1.1 (p. 195): the Rees valuation rings of an ideal `I` are a minimal finite set of rank-one discrete valuation rings `V_i`, each
  between `R/P` and the fraction field of `R/P` for a minimal prime `P`, such that the integral closure of `I^n` is the intersection of the contractions of
  `I^n V_i` for every `n`. Remark 10.1.4 (p. 197): equivalently `r` lies in the integral closure of `I^n` if and only if `v(r) >= n v(I)` for every Rees valuation `v`.
- [P] Theorem 10.1.6 (p. 198): when the Rees valuations exist they are unique up to equivalence of valuations (for an ideal contained in no minimal prime).
  Theorem 10.2.2 (p. 200), existence (attributed to Rees): every ideal of a Noetherian ring has a set of Rees valuations; for an
  integral domain and `I = (a_1, ..., a_d)` the Rees valuation rings are the localizations at height-one primes over `a_i` of the integral closures
  of the affine pieces `R[I/a_i]`. Corollary 10.2.4 (p. 202): the union of the associated primes of the `R/(I^n closure)` equals the set of
  centers of the Rees valuations and is finite. Proposition 10.2.5 (p. 202): for a nonzero proper ideal `I` of a Noetherian domain `R` with enough units (for example an infinite field in `R`) one affine piece `R[I/a]` suffices. Proposition 10.2.6 (p. 203): for a Noetherian formally equidimensional local ring `(R, m)` of dimension `d` and an ideal `I` generated by elements `x_1, ..., x_d` that are analytically independent modulo each minimal prime of `R`,
  a Rees valuation ring `V` of `I` with center on `m` satisfies `x_i V = I V` for every `i` and is, for every `i`, a localization of the integral closure of `R'[I'/x_i']` at a height one prime minimal over `x_i'`, the prime marking images in `R/P` for the minimal prime `P` with `R/P` inside `V`.
  Corollary 10.2.7 (p. 203, attributed to Sally): for a Noetherian formally equidimensional local domain of dimension `d > 0` and an `m`-primary ideal `I = (a_1, ..., a_d)` with `mu(I) = d`, every Rees valuation ring of `I` is, for every `i`, the localization of the normalization of `R[I/a_i]` at a height one prime minimal over `a_i`.

## Mapping to this repository

- [I] The A_5 fiber-cone program (`docs/evidence/a5-exceptional-fibers/ledger.tsv`, rows A5-416 and A5-418, and
  [the run rulebook](../../runbooks/run-rulebook.md)) takes the special fiber of the Rees algebra of the ideal `I` generated by
  the selected Pfaffian generators `G`, namely `F(I) = R[It]/m R[It]` with `R` the local ring or the graded polynomial ring at the
  origin of the germ. Definition 5.1.5 (p. 100) is that object for a Noetherian local ring, with the same
  quotient and the identification `F_I = direct sum of I^n/m I^n`. For a graded ideal in a polynomial ring with the origin as `m`
  the repository applies the same quotient; the book proves its dimension statements for local rings, and the passage between the
  local ring and the graded polynomial ring is outside the pages read.
- [I] Presentation step. The method writes `R[It]` as `R[T_1, ..., T_n]/A` for generators `x_1, ..., x_n` of `I` (here the
  Nakayama generators of the selected Pfaffians); this is the map `pi` of page 110, with `A` generated by homogeneous forms
  `F(T)` such that `F(x) = 0`. Since `m R[It]` is the image of `m R[T]`, `F(I) = (R/m)[T]/(image of A)`, so the relations of `F(I)` in
  degree `d` are the images in `(R/m)[T]` of the elements of `A` of degree `d`, equivalently the classes of forms `q` of degree `d` with `q(G)`
  in `m I^d`, the form in which the ledger rows state the degree-2 relations. This reduction follows from the definitions on pages 100 and
  110 and is not a numbered statement of the book. The linear part `A_1` is read from a presentation matrix (page 110, Exercise 5.23 on page
  118); for a minimal generating set over a local ring the presentation matrix has entries in `m`, so `A_1` maps to zero in `(R/m)[T]`.
  Consequently, if `I` were of linear type (Definition 5.5.1, `A = A_1`), `F(I)` would be the polynomial ring `(R/m)[T]`; a fiber cone with
  nonzero quadrics, as in the ledger rows for W8, E8-bar, Iso and same-sign X, therefore belongs to an ideal that is not of linear type, and
  by Corollary 5.5.5 its generators are not a d-sequence. This deduction rests on the minimality of the generators and the locality of `R`; the book does not state it.
- [I] Dimension and degree of the fiber. `ell(I) = dim F_I` (Definition 5.1.5), `ht I <= ell(I) <= dim R` (Corollary 8.3.9) and
  `mu(J) >= ell(I)` for every reduction `J` (Corollary 8.2.5) bound the dimension of the fiber cones that the ledger reports as `Proj`
  of dimension `ell(I) - 1` (for example `P^2` for three independent generators, a polynomial ring in three variables, as in Corollary
  8.3.6 (2)); the step from `dim F_I` to `dim Proj F_I = dim F_I - 1` for a standard graded algebra over a field is
  not a statement of the pages read. Proposition 8.3.7 requires an infinite residue field, so for the residue fields `F_32009` and
  `F_32029` of the modular computations its generator-count statement needs the extension `R(X)` of Lemma 8.4.2, which preserves `ell`
  and `mu` (the book proves `ell(I) = ell(I R(X))` there); Corollary 8.3.9 and Corollary 8.2.5 carry no residue-field hypothesis.
- [I] Rees valuations (Chapter 10) supply the definition and the finiteness of the divisorial valuations of an ideal and their
  construction from the normalized affine blowup charts (Theorem 10.2.2 (3)); the repository's arc and valuation leads
  ([0803.2369](0803.2369.md) and [math-0303268](math-0303268.md)) rest on the same objects, and this note records only the book's definitions
  and existence statements, which hold for any Noetherian ring and hence over `Q(i)` and over `F_p`.
- [I] What the pages read do not give. (a) The book has no statement that the defining ideal `A` of the Rees algebra is a saturation or an
  elimination ideal of the symmetric algebra, nor an algorithm; [Vasconcelos 1994](vasconcelos-1994-arithmetic-blowup-algebras.md) states the elimination form
  and [Greuel and Pfister 2008](greuel-pfister-2008-singular-introduction-commutative-algebra.md) the saturation and elimination algorithms. (b) No statement on the pages read, in Section 5.6 or in the
  index entries listed above, says that the fiber of `Proj R[It]` over the closed point is `Proj F_I` or that the blowup is the closure of the graph of the map
  given by the generators. (c) Pfaffian-specific statements (Gorenstein property,
  normality of the Rees algebra of Pfaffian ideals) are not in the pages read; see [Baetica 1998](baetica-1998-rees-algebra-pfaffians.md) and
  [Jozefiak and Pragacz 1979](jozefiak-pragacz-1979-ideals-generated-pfaffians.md). (d) The pages read give no statement on a specialization of a
  generic ideal, which the program's ideals are.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Only the pages listed under the reading scope were opened. The note asserts nothing about Section 5.3 and 5.4 (powers and formal equidimensionality,
printed pages 103 to 109), Chapters 6 and 7, Sections 8.5 to 8.9 (superficial elements and later), Chapter 9, Sections 10.3 to 10.6 (examples,
properties of Rees valuations, rational powers), Chapter 11 (multiplicity), Chapter 15 on computing integral closure or any later chapter. Proofs were read through and are not re-derived here, and no
claim in this note rests on a computation in this repository.
