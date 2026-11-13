# Vasconcelos 1994: Arithmetic of Blowup Algebras (London Mathematical Society Lecture Note Series 195)

## Source copy and license

The [source PDF](https://doi.org/10.1017/cbo9780511574726) remains external to the published library. It is a scan of the Cambridge
University Press paperback (series list, title page, copyright page, dedication, contents, foreword, Introduction, Chapters 1 to 10,
the bibliography and the index), acquired from a third-party mirror, converted from a DjVu scan to PDF, and held as a private reading copy;
every page is a bitmap image. PDF page 4 (the imprint page) reads "(c) Cambridge University Press 1994" and "This publication is in
copyright", states that no part may be reproduced without the written permission of Cambridge University Press, and prints the paperback ISBN-13
978-0-521-45484-1 and "Transferred to digital printing 2006". The PDF holds no redistribution grant, so the registry records it as external-only under
`NOASSERTION` with the imprint page as the rights locator. The Crossref record of the DOI lists one license entry, the Cambridge Core terms
(`https://www.cambridge.org/core/terms`), which are Cambridge University Press's own terms and no Creative Commons or public-domain grant; the
registry does not rely on them for rehosting. The reading copy is the ignored
`docs/local_source_cache/vasconcelos-1994-arithmetic-blowup-algebras.pdf`, with a second copy in the owner's private documents repository.
[SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope. Attribution to Wolmer V. Vasconcelos applies to every statement below.

Tag convention: [P] marks a statement of the book; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index minus 10 (PDF page 11 is printed page 1, the first page of the Introduction; PDF
page 140 is printed page 130 and PDF page 263 is printed page 253). The front matter before the Introduction carries no page numbers in the scan.

## Citation and provenance

- Author: Wolmer V. Vasconcelos (Department of Mathematics, Rutgers University, on the title page). Title: Arithmetic of Blowup
  Algebras. Series: London Mathematical Society Lecture Note Series 195, Cambridge University Press, first published 1994.
- DOI [10.1017/CBO9780511574726](https://doi.org/10.1017/CBO9780511574726). The Crossref record (title, author, publisher, type `monograph`, issue date 25
  February 1994, print ISBN 9780521454841, electronic ISBN 9780511574726, edition number 1) is a registered retrieval receipt; the record carries no
  series name or volume number, so the series and its number come from the title page of the PDF.
- Retained PDF: 339 pages, 11014031 bytes, SHA-256 `49431544db5530d32e4ec3c6621eb1aa3ec7fa1c607548155e3d59936d65e334`.
- Reading scope (each page opened as an image, no text extraction): PDF pages 1 to 10 (series list, title page, imprint page, dedication, contents
  and foreword) and PDF pages 11 to 16 (the Introduction, printed pages 1 to 6); printed pages 99 to 101 (PDF pages 109 to 111: the opening of Chapter 5 and the start of Section 5.1, with Definitions 5.1.1 and 5.1.2); printed pages 130 to 137 (PDF pages 140 to 147: the end of
  Section 5.4 and Section 5.5 on the construction of Rees algebras, with the opening of Section 5.6); printed pages 195 to 198 (PDF pages
  205 to 208: the opening of Chapter 8 and the start of Section 8.1); printed pages 253 to 266 (PDF pages 263 to 276: Chapter 10 from
  its opening through Section 10.2 and the start of Section 10.3); printed pages 327 to 329 (PDF pages 337 to 339: the index, searched for the entries special fiber, fiber cone, saturation and homogenization). The rest of the book was not read: Chapters 1 to 4, Section 5.1 beyond page 101, Sections 5.2 to 5.4 and 5.6 to 5.7, Chapters 6, 7 and 9, Sections 8.1 to 8.4 beyond page 198, Sections 10.3 to 10.6 beyond page 266, the bibliography and the index.
- Status: published book (Cambridge University Press, 1994; the scan is a later digital printing of the same text).

## Contents recorded from the table of contents

- [P] The contents list ten chapters: 1 Krull Dimension, 2 Syzygetic Sequences, 3 Approximation Complexes, 4 Linkage and Koszul Homology, 5 Arithmetic of Rees Algebras
  (Sections 5.1 Reduction Modules through 5.7 The Canonical Module; 5.5 Construction of Rees Algebras opens on page 130), 6 Factoriality, 7 Ideal Transforms, 8 The Equations of Rees
  Algebras (8.1 Almost Complete Intersections, 8.2 Codimension Two, 8.3 Higher Codimension, 8.4 Ideals with Linear Presentation), 9 Commuting Varieties of Algebras and 10 Computational
  Methods in Commutative Algebra (10.1 Generalized Division Algorithms, 10.2 Basic Methods, 10.3 Nullstellensatze, 10.4 Primary Decomposition, 10.5 Ideal Transforms, 10.6 Integral Closure).

## Blowup algebras, symmetric algebra and Rees algebra (Introduction, pp. 1-5)

- [P] Pages 1-2: a multiplicative filtration `{R_n}` of a ring has the Rees algebra `R(F) = sum R_n t^n`; for the `I`-adic filtration `R_n = I^n` it is the Rees algebra
  `R(I) = R[It]` of the ideal `I`, which the book describes as the algebraic form of blowing up a subvariety; a decreasing filtration also gives the extended Rees algebra `R(F)[t^-1]`
  and the associated graded ring.
- [P] Page 2: the symmetric algebra `S(E)` of a module `E` with presentation `R^m -> R^n -> E -> 0` given by a matrix `phi = (a_ij)` is the quotient of the polynomial ring
  `R[T_1, ..., T_n]` by the ideal generated by the `m` one-forms `f_j = a_1j T_1 + ... + a_nj T_n`; every quotient of a polynomial ring by an ideal generated by one-forms arises this way.
- [P] Page 3: for an ideal `I` of `R` there is a canonical surjection `alpha : S(I) -> R(I)`; when `R` is an integral domain its kernel is the `R`-torsion submodule of `S(I)`.
- [P] Page 5 (description of the chapters): Chapter 8 seeks the equations of Rees algebras of ideals that are not necessarily of linear type, by several ad hoc approaches
  including computer-assisted ones, and Chapter 10 treats computer algebra methods (Buchberger's algorithm, Noether normalization, Nullstellensatz forms, primary decomposition,
  ideal transforms and integral closure).

## The equations of the Rees algebra (Chapter 8, pp. 195-196)

- [P] Page 195 (opening of Chapter 8): for an ideal generated by `a_1, ..., a_n` the Rees algebra is the image of `B = R[T_1, ..., T_n]` under the map `phi` with `phi(T_i) = a_i t`;
  its kernel `L = ker(phi)` is the ideal of equations of `R(I)`. `L` is graded, `L = sum_(t >= 1) L_t`, the part `L_1` consists of the linear forms `sum c_i T_i` with `sum c_i a_i = 0`
  (the first-order syzygies of `I`), and `L_t` is the module of first-order syzygies of `I^t`. The methods of the chapter are incremental: they focus on the modules
  `tau_t(I) = L_t / sum_(i<t) L_i B_(t-i)`, the new generators that degree `t` adds to the ideal generated by the lower degrees.
- [P] Page 195-196: from a presentation `R^m -> R^n -> I -> 0` the part `L_1` is generated by the entries of the row vector `T` times the presentation matrix, and the book rewrites it as `x B(phi)`
  with `x` the vector of entries of `phi` and `B(phi)` an `r x m` matrix of linear forms in the `T_i` (the Jacobian dual).
- [P] Page 196: the quotient `R[T]/(L_1)` is the symmetric algebra of `I`, and with `A = L/(L_1)` there is an exact sequence `0 -> A -> S(I) -> R(I) -> 0`. Over an integral domain `R`
  the module `A` is the `R`-torsion submodule of `S(I)`; the book states that there is a nonzero `f` in `I` with `f A = 0`. An application of Cramer's rule puts the `r x r` minors of `B(phi)`
  into `L` (they are conducted into `(L_1)` by nonzero elements of `R`). The text adds that in some cases `B(phi)` is skew-symmetric and the Pfaffians play a clear role, without stating a theorem about them on the pages read.

## Basic computational methods (Chapter 10, pp. 253-266)

- [P] Definition 10.1.1 (p. 256): a set `{g_1, ..., g_r}` of elements of an ideal `I` of `k[x_1, ..., x_n]` is a Groebner basis for a term order if the exponent vectors of the leading monomials generate
  the exponent semigroup of `I`; Theorem 10.1.3 (p. 257, Macaulay): the normal form map is an isomorphism of `k`-vector spaces `R/I -> R/init(I)`; Theorem 10.1.6 (p. 258): a finite generating set is a Groebner
  basis exactly when all S-polynomials of pairs reduce to zero (Algorithm 10.1.7, p. 259, is the Buchberger loop).
- [P] Proposition 10.2.1 (p. 259): for a lexicographic order with `t` greater than the `x_i`, the elements of a Groebner basis `F` of an ideal `I` of `R[t]` that lie in `R` form a Groebner basis of `I` intersect `R`.
  Corollary 10.2.2 (p. 260): `I intersect J = (I t, J (1 - t)) intersect R`.
- [P] Proposition 10.2.3 (p. 260): an element `f` is regular modulo `I` if and only if `((I t, (1 - t) f) intersect R) f^-1 = I`, or if and only if `(I, 1 - f t) intersect R = I`. The text states that the first formula computes
  the colon ideal `I :_R f` and that the second determines the union of the colon ideals `I :_R f^n`. Proposition 10.2.4 (p. 260): `I : J = (I R[x] : f) intersect R` for the generic combination
  `f = a_1 + a_2 x + ... + a_n x^(n-1)` of generators of `J`. Proposition 10.2.5 (p. 260): the saturation `I : J^infinity` (the union of the `I : J^k`) equals `((I, y - f) : y^infinity) intersect R` for a further variable `y`
  and the same `f`; the book attributes this device to its reference [15].
- [P] Homogenization (p. 264): for `f` in `k[x_1, ..., x_n]` the homogenization with a new variable `T` is `f^H = T^(deg f) f(x_1/T, ..., x_n/T)`. For an ideal `I = (f_1, ..., f_m)` the book defines two homogenizations,
  `J = (f_1^H, ..., f_m^H)` and `L = (f_1^H, ..., f_m^H) : T^infinity`; the first depends on the generating set and the second does not, and both specialize to `I` at `T = 1`.
- [P] Proposition 10.2.11 (p. 265): for `I = (f_1, ..., f_m)` in the ring `A = R[T_1, ..., T_m, t]`, the ideal `L` generated by the polynomials `T_j - t f_j` has the property that `R[It] = A/J` with `J` the
  contraction of `L` to `B = R[T_1, ..., T_m]`; `J` is graded in the `T_j`, with `J_n` giving the syzygies of `I^n`. Proposition 10.2.12 (p. 265): if the columns of `phi` generate the syzygies of `I`, `J_0` is the ideal generated by
  the entries of `[T_1, ..., T_m] phi` (the defining ideal of the symmetric algebra) and `f` is a nonzero element of `I`, then the Rees ideal is `J = (J_0, 1 - f t) intersect R[T_1, ..., T_m]`.
  Remark 10.2.13 (p. 265) allows replacing `J_0` by the ideal generated by `f_1 T_j - f_j T_1` for `j >= 2` with `f = f_1` and calls the result the rational closure of `J_0`.

## Reduction number and the special fiber (Chapter 5, pp. 99-101)

- [P] Page 99 (opening of Chapter 5): an ideal `J` contained in `I` is a reduction of `I` when `J I^r = I^(r+1)` for some `r` (the notion is attributed to Northcott and Rees); equivalently `R[Jt]` embeds in `R[It]` as a finite morphism of graded algebras.
- [P] Definition 5.1.1 (p. 100): the reduction number `r_J(I)` is the least such `r`, and the reduction number of `I` is its minimum over all reductions `J` of `I`; it equals the infimum of the top degrees of homogeneous generating sets of `R[It]` over `R[Jt]`.
- [P] Definition 5.1.2 (p. 100): for a Noetherian local ring `(R, m)` the special fiber of the Rees algebra `R[It]` is `F(I) = R[It] tensor_R R/m`; its Krull dimension is the analytic spread `ell(I)`. For `I = m` the ring `F(m)` is the tangent cone of `R`, and `F(I)` is also called the fiber cone of `I`.
  Proposition 5.1.3 (p. 100): when the residue field is infinite, lifts `a_1, ..., a_ell` of a Noether normalization `k[z_1, ..., z_ell] -> F(I)` with the `z_j` in degree 1 generate a reduction `J` of `I`, and `r_J(I)` is the largest degree of a minimal homogeneous module generator of `F(I)` over `k[z]`.
  Corollary 5.1.4 (p. 101): `ht I <= ell(I) <= dim R`.
- [P] Index (pp. 327-329): `special fiber` and `fiber cone` and `analytic spread` and `tangent cone` all point to page 100, `saturation of an ideal` to page 260, `homogenization` to page 264, `elimination of variables` to page 259 and `dimension of Rees algebras` to page 17 (not read).

## Other pages read

- [P] Section 5.5 (pp. 130-137): Definition 5.5.1 (p. 130) calls two ideals transversal when `I intersect J = I J`; Propositions 5.5.2 and 5.5.3 (p. 131) and Theorem 5.5.5 (p. 132) concern Serre's condition `(S_r)` of affine algebras and
  its stability under extension of the base field; Proposition 5.5.7 (p. 133) presents the Rees algebra of `(I_1, I_2)` in a tensor product of algebras by gluing, with Theorems 5.5.9 and 5.5.10 (p. 135) giving the Cohen-Macaulay
  property of the glued Rees algebra when the factors are Cohen-Macaulay. Theorem 5.4.15 (p. 130) concerns equimultiple ideals of codimension `g` in a Cohen-Macaulay ring whose Rees algebra satisfies `(S_2)`.
  These pages treat sums of ideals and product varieties; they contain no statement on Pfaffian ideals.
- [P] Section 8.1 (pp. 197-198): the section opens with almost complete intersection primes of dimension one and their second symbolic power; Proposition 8.1.1 (p. 197) and Corollary 8.1.2 (p. 197) recover
  the intersection of the primary components of height `g` of a power `I^n` as the annihilator of `Ext^g(R/I^n, R)` over a Gorenstein ring; page 198 begins "The content of syzygies". These pages
  concern symbolic Rees algebras and carry no statement used below.

## Mapping to this repository

- [I] Presentation step of the A_5 fiber-cone program ([run rulebook](../../runbooks/run-rulebook.md), ledger rows A5-416 and A5-418 in `docs/evidence/a5-exceptional-fibers/ledger.tsv`): the program writes the Rees
  algebra `R[It]` as a quotient of a polynomial ring in the generators of `I`. Page 195 states this presentation with its kernel `L`, and page 196 gives the exact sequence `0 -> A -> S(I) -> R(I) -> 0`
  whose middle term is the quotient by the linear part `L_1` read from a presentation matrix (the degree-one relations of the program).
- [I] Saturation or elimination step. Proposition 10.2.12 gives the Rees ideal as `(J_0, 1 - f t)` contracted to `R[T]`, an elimination of the variable `t`, with `J_0` the symmetric algebra ideal and `f` any nonzero element of `I`;
  Proposition 10.2.11 gives it as the contraction of `(T_j - t f_j)`. The sentence after Proposition 10.2.3 identifies `(I, 1 - f t) intersect R` with the saturation `I : f^infinity`, so the Rees ideal is the saturation of `J_0` by `f` when the
  setting of Proposition 10.2.12 applies, which is the saturation route of the runbook. The page proves that identification in neither direction, and Proposition 10.2.12 does not restate its hypotheses
  on `R` (Section 10.2 works over a polynomial ring over a field `k`); for a domain `R` the repository's own derivation is that `A` is killed by a power of `f` because `S(I)_f = R(I)_f` (both are `R_f[T]`
  once `f` is a unit), which uses the torsion statement of page 196 and is not printed in the book. Saturation by one variable `y` of an ideal in `R[y]` (Proposition 10.2.5) and the
  homogenization `L = (f^H) : T^infinity` (page 264) are the same device with the saturating element `y` or `T`; [Greuel and Pfister 2008](greuel-pfister-2008-singular-introduction-commutative-algebra.md) gives the
  Singular algorithms and the correctness statements for saturation and elimination.
- [I] Degree-by-degree reading of the relations. The grading of `L` and the modules `tau_t(I) = L_t / sum L_i B_(t-i)` (page 195) are the book's formulation of "the new relations that degree `t` adds", which is the procedure of
  the ledger rows (degree-2 relations first, then higher degrees up to 7 for E8-bar). The book does not bound the degree at which `tau_t` vanishes for the program's ideals; the ledger's degree bound is a measured one.
- [I] Special fiber. Definition 5.1.2 (p. 100) defines the special fiber `F(I) = R[It] tensor_R R/m` of a Noetherian local ring, the same object as the fiber cone of [Definition 5.1.5 of Huneke and Swanson](huneke-swanson-2006-integral-closure-ideals-rings-modules.md),
  and names its dimension the analytic spread; Corollary 5.1.4 bounds `ell(I)` between `ht I` and `dim R`. This is the definition behind the ledger's special fiber `F(I) = R[It]/m R[It]`. The book's index has no further entry for it, and the pages read state neither a presentation of `F(I)` nor that `Proj F(I)` is the fiber of the blowup over the closed point.
- [I] Pfaffians. Page 196 remarks that a skew-symmetric `B(phi)` makes Pfaffians play a role in the equations of `R(I)`; the pages read contain no theorem on Pfaffian ideals. The program's ideals
  are Pfaffian-type ideals (specializations of generic Pfaffian ideals), for which [Baetica 1998](baetica-1998-rees-algebra-pfaffians.md) and
  [Jozefiak and Pragacz 1979](jozefiak-pragacz-1979-ideals-generated-pfaffians.md) are the registered sources.
- [I] Fields and rings. Proposition 10.2.1 and the computational sections work over a field `k` and a polynomial ring; the pages read state no hypothesis on the characteristic, but Theorem 10.1.6 and Proposition 10.2.1
  are the exact division-algorithm statements for any field, which covers `Q(i)` and `F_p`. Statements about local rings or the origin of a germ are outside the pages read.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Only the pages listed under the reading scope were opened. The note asserts nothing about Chapters 1 to 4, Section 5.1 beyond page 101 and Sections 5.2 to 5.4 and 5.6 to 5.7 (the Sally module, Hilbert functions of local rings, Koszul homology of reductions,
Jacobian criteria, the f-number, the canonical module), Chapters 6, 7 and 9, Sections 8.1 to 8.4 beyond page 198 (the symbolic powers and equations of Rees algebras of codimension two and higher, ideals with linear presentation), or
Sections 10.3 to 10.6 (Nullstellensatze, primary decomposition, ideal transforms, integral closure). The bitmap scan was read at page resolution; proofs were read through and are not re-derived here, and no claim in this note rests on a computation in this repository.
