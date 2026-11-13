# Greuel and Pfister 2008: A Singular Introduction to Commutative Algebra, second, extended edition

## Source copy and license

The [source PDF](https://doi.org/10.1007/978-3-540-73542-7) remains external to the published library. It is a copy of the Springer second,
extended edition (cover, title page, imprint page, dedication, both prefaces, contents, Chapters 1 to 7, the appendices, the references, the
glossary and the index), acquired from a third-party mirror and held as a private reading copy. PDF page 4 (the imprint page) reads "This work is
subject to copyright. All rights are reserved" and carries the line "(c) Springer-Verlag Berlin Heidelberg 2002, 2008" and the ISBN 978-3-540-73541-0; the PDF holds no
redistribution grant, so the registry records it as external-only under `NOASSERTION` with the imprint page as the rights locator. The Crossref
record of the DOI lists one license entry, the Springer text-mining terms (`http://www.springer.com/tdm`), which are Springer's own terms and no Creative
Commons or public-domain grant; the registry does not rely on them for rehosting. The reading copy is the ignored
`docs/local_source_cache/greuel-pfister-2008-singular-introduction-commutative-algebra.pdf`, with a second copy in the owner's private documents repository.
[SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope. Attribution to Gert-Martin Greuel and Gerhard Pfister applies to every statement below.

Tag convention: [P] marks a statement of the book; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index minus 18 through Chapter 1 (PDF page 85 is printed page 67 and PDF page 99 is printed page 81) and minus 17 at Section 7.5 (PDF page 421
is printed page 404, the first page of Section 7.5); the offset changes by one between those chapters, and each page cited here was matched to its own printed number. The front matter is numbered in Roman numerals (PDF page 4, the imprint page, is unnumbered;
PDF page 18, the last contents page, is page XX).

## Citation and provenance

- Authors: Gert-Martin Greuel and Gerhard Pfister (University of Kaiserslautern), with contributions by Olaf Bachmann, Christoph Lossen and Hans Schoenemann; title page: second, extended edition, with 49 figures;
  Springer. The second-edition preface lists the changes (non-commutative Groebner bases, characteristic and triangular sets, an appendix on polynomial factorization, and a new CD with SINGULAR 3-0-3).
- DOI [10.1007/978-3-540-73542-7](https://doi.org/10.1007/978-3-540-73542-7). The Crossref record (title, publisher Springer Berlin Heidelberg, print ISBN 9783540735410, print publication year 2007) is a
  registered retrieval receipt; the record lists no authors and carries no edition statement, so the authors and the edition come from the title page and imprint page of the PDF.
- Retained PDF: 703 pages, 10389124 bytes, SHA-256 `062bfc8e5c828b6cb681fbafc882807c6989dee0e852665bccabac5413cff762`.
- Reading scope (each page opened as an image, no text extraction): PDF pages 1 to 18 (cover, title page, imprint page, dedication, the two prefaces and the contents, pages up to XX); printed pages 67 to 71 (PDF pages 85 to 89:
  Sections 1.8.1 and 1.8.2 on ideal membership and elimination and the opening of Section 1.8.3 on the Zariski closure of the image); printed pages 77 to 86 (PDF pages 95 to 104: Section 1.8.6 from Lemma 1.8.8 on radical membership
  through Sections 1.8.7 to 1.8.10 and the opening of Section 1.8.11); printed pages 404 to 411 (PDF pages 421 to 428: Section 7.5 on flatness and standard bases with Theorem 7.5.1, its exercises and the opening of Section 7.6).
  The rest of the book was not read: Sections 1.1 to 1.7, the rest of Section 1.8.3 and Sections 1.8.4 and 1.8.5 (printed pages 72 to 76), Section 1.9 and Chapters 2 to 6, the printed pages of Chapter 7 before 404 and after 411, the appendices (including Lemma A.5.2 on saturation in
  projective geometry, which Section 1.8.9 cites) and the references.
- Status: published book (second, extended edition).

## Membership, elimination and the kernel of a ring map (Section 1.8, pp. 67-71 and 84-86)

- [P] Section 1.8.1 (p. 67): for ideals of `K[x]_>` (the polynomial ring localized for the monomial ordering `>`, equal to `K[x]` for a global ordering), a standard basis `G` of `I` decides membership: `f` lies in `I` if and only if a weak normal form `NF(f | G)` is zero
  (correctness by Lemma 1.6.7). In a local ring a multiple `u f` with `u` a unit of `K[x]_>` is expressed through the generators; for a global ordering `u = 1` (p. 68).
- [P] Section 1.8.2 (p. 69): the elimination problem asks for generators of `I' = I intersect K[x_(s+1), ..., x_n]`; one computes with a global elimination ordering for `x_1, ..., x_s`, for example the product ordering `(dp(s), dp(n - s))` or an ordering with
  an extra weight vector. Lemma 1.8.3 (p. 70): for an elimination ordering for `x_1, ..., x_s` and a standard basis `S` of `I`, the elements of `S` whose leading monomials lie in `K[x_(s+1), ..., x_n]` form a standard basis of
  `I'`, in particular generate it; for a general ring attached to a monomial ordering the book solves the problem the same way, provided the ordering on the eliminated variables is global. Example 1.8.4 (pp. 70-71) runs `eliminate(I, t)`.
- [P] Section 1.8.3 (p. 71): the Zariski closure of the image of a map of affine varieties over an algebraically closed field is cut out by eliminating the parameters from the graph ideal `<g_i(t), x_j - f_j(t)>`.
- [P] Section 1.8.10 (p. 84): for a ring map `phi : R_1 = (K[x]_(>_1))/I -> R_2 = (K[y]_(>_2))/J` with `phi(x_i) = f_i`, where the orderings satisfy `1 >_2 LM(f_i)` whenever `1 >_1 x_i`, `J_0 = J intersect K[y]` is generated by `g_1, ..., g_s` and
  `I_0 = I intersect K[x]` by `h_1, ..., h_t`: the solution forms `H = <h_1, ..., h_t, g_1, ..., g_s, x_1 - f_1, ..., x_n - f_n>` in `K[x, y]` and eliminates `y_1, ..., y_m`. Lemma 1.8.16 (p. 84): the kernel of the induced map `phi-bar` on
  `K[x]/I_0` is `(I_0 + <g_1, ..., g_s, x_1 - f_1, ..., x_n - f_n> intersect K[x]) mod I_0`, `Ker(phi) = Ker(phi-bar) R_1`, and for a global ordering `Ker(phi) = Ker(phi-bar)`. Footnote 11 (p. 84), where `f_1, ..., f_m` denote polynomial generators of an ideal `I` of `K[x]_>` and not the images of the map: for a global ordering the ideal they generate in `K[x]` equals `I_0 = I intersect K[x]`,
  for a non-global ordering it can be a proper subset, and `I_0` is then computed through a primary decomposition of that ideal. The proof (pp. 84-85) uses the Taylor expansion of a polynomial about `(f_1, ..., f_n)`.
- [P] Remark 1.8.17 (p. 85): kernels and preimages are equivalent computations (the Singular command `preimage`); Example 1.8.18 (p. 85) checks the elimination `eliminate(H, ab)` against `preimage`. Section 1.8.11 (p. 86): algebraic dependence of polynomials is `Ker(phi) != 0`, and subalgebra membership
  uses an elimination ordering for `x_1, ..., x_n` on the monomials in `x_1, ..., x_n, y_0, ..., y_k` with the new variable `y_0` greater than `y_1, ..., y_k`.

## Radical membership, intersection, quotient and saturation (Section 1.8, pp. 77-83)

- [P] Lemma 1.8.8 (p. 77): for an ideal `I` and an element `f` of a ring `A`, `f` lies in the radical of `I` if and only if `1` lies in `<I, 1 - t f>` in `A[t]`; the solution (p. 78) eliminates `t` with an ordering that keeps `K[x]_> = K[x]_(>')` and looks for a standard basis element of leading monomial 1.
- [P] Lemma 1.8.10 (p. 79): `I_1 intersect I_2 = J intersect K[x]_>` for `J = <t f_1, ..., t f_k, (1 - t) h_1, ..., (1 - t) h_r>`, solved by elimination of `t`.
- [P] Section 1.8.8 (pp. 79-80): `I_1 : <h_1, ..., h_r>` is the intersection of the `I_1 : <h_i>`. Lemma 1.8.12 (p. 80): if `I intersect <h> = <g_1 h, ..., g_s h>` then `I : <h> = <g_1, ..., g_s>`. Solution 2 forms `h = h_1 + t_1 h_2 + ... + t_(r-1) h_r`, computes
  `I_1 : <h>` and eliminates `t_1, ..., t_(r-1)` to obtain `I_1 : I_2`.
- [P] Section 1.8.9 (p. 81): for ideals of `K[x]_>`, the chain `I_1 subset I_1 : I_2 subset I_1 : I_2^2 subset ...` stabilizes at some `s` (the ring is Noetherian), and `I_1 : I_2^infinity = union_i I_1 : I_2^i = I_1 : I_2^s` is the saturation of `I_1` with respect to `I_2`;
  the least such `s` is the saturation exponent, equal to 1 for a radical `I_1`. The algorithm sets `I^(0) = I_1`, `I^(j+1) = I^(j) : I_2` by the methods of Section 1.8.8, tests `I^(j+1) subset I^(j)` by membership (Section 1.8.1) and stops at the first `j = s` where this holds,
  returning `I^(s) = I_1 : I_2^infinity`; correctness rests on `I^(j) = I_1 : I_2^j`, a consequence of Lemma 1.8.14 (1). The book calls this usually much faster than computing `I_1 : I_2^j` directly, since the power `I_2^j` can become large.
- [P] Lemma 1.8.14 (p. 81): for ideals `I_1, I_2, I_3` of a ring `A`, (1) `(I_1 intersect I_2) : I_3 = (I_1 : I_3) intersect (I_2 : I_3)` and `(I_1 : I_2) : I_3 = I_1 : (I_2 I_3)`; (2) for a prime `I_1` with `I_2` not contained in it, `I_1 : I_2^j = I_1`; (3) for
  `I_1 = intersect J_i` with prime `J_i`, `I_1 : I_2^infinity = I_1 : I_2 = intersect over I_2 not in J_i of J_i`. Page 82 gives the geometric reading: for a radical `I_1`, `V(I_1 : I_2)` is the Zariski closure of `V(I_1) minus V(I_2)`, and `V(I) minus {a} = V(I : m_a^infinity)` for an ideal `I` of `K[x_1, ..., x_n]` and a point `a` of `V(I)` such that `V(I) minus {a}` is Zariski closed;
  in general a quotient or saturation can leave a component and only reduce its structure, as in `<x y^2, y^3> : <x, y> = <y^2>` (p. 83, Figure 1.4).
- [P] Example 1.8.15 (p. 83): in Singular `sat(I1, I2)` from `elim.lib` returns a list holding the saturation and the saturation exponent (for `I1 = <x^5 z^3, x y z, y z^4>` and `I2 = <z>` the saturation `<y, x^5>` with exponent 4), and the same result follows from repeating `quotient(I1, I2)` until `reduce(J, std(I1))` vanishes, which took four quotients.

## Flatness and standard bases (Section 7.5, pp. 404-411)

- [P] Theorem 7.5.1 (p. 404), under the section title "Flatness and Standard Bases": let `K` be a field, `>` a monomial ordering on `Mon(x)`, `F` a finite subset of `Mon(x)` and `I'` an ideal of `K[x]_>`. There is a weighted degree ordering `>_w` on `Mon(x, t)`, global in `t` and
  equal to `>` on `F`, such that, with `I = I' intersect K[x]` and `J` the ideal of `K[x, t]_(>_w)` generated by the weighted homogenization `I^h` (weights `w`, homogenizing variable `t`): (1) `B = K[x, t]_(>_w)/J` is a flat `K[t]`-algebra; if `I K[x]_>` is a proper ideal of `K[x]_>`, then for each maximal ideal `m` of `K[t]` some maximal ideal `M` of `B` over `m` has `dim B = dim B_M`, and in particular `B` is faithfully flat over `K[t]`; (2) the leading ideal `L(J)` is the extension of `L_>(I)`; (3) `L_>(J|_(t = lambda)) = L_>(I)` for every `lambda` in `K`; (4) `J|_(t=0) = L_>(I) K[x]_(>_w)` and `J|_(t=1) = I K[x]_(>_w)`, and for `lambda != 0`
  the fiber `B tensor K[t]/<t - lambda>` is isomorphic to `K[x]_(>_w)/I K[x]_(>_w)`. The page notes that for a mixed ordering `K[x]_(>_w)` differs from `K[x]_>` in general (units differ), and Corollary 7.5.2 (p. 404) gives the stronger form (4') `J|_(t=0) = L(I) K[x]_>`, `J|_(t=1) = I K[x]_>` for a global or local ordering.
- [P] Proposition 7.5.3 (p. 405): for generators `f_1, ..., f_r` of `I` whose leading monomials exceed their tails in the weighted degree (weight vector `w`, all `w_i != 0`) and `f_i^h` their weighted homogenizations, these are equivalent: `{f_i}` is a standard basis of `I`;
  `{f_i^h|_(t=lambda)}` is a standard basis of `J|_(t=lambda)` for all `lambda` in `K`; `{f_i^h}` is a standard basis of the homogenized ideal; `K[x, t]_>/(f_i^h)` is a flat `K[t]`-algebra (faithfully flat when `I != K[x]_>`).
  The proof (pp. 405-406) uses the `K^*`-action `x_i -> x_i/lambda^(w_i)` and the criterion of Exercise 7.3.19.
- [P] Proof of Theorem 7.5.1 (pp. 406-407): the proof takes an irredundant primary decomposition of `I`, standard bases of `I` and its components, an integer weight vector, and applies Proposition 7.5.3 to the components. Lemma 7.5.4 (p. 407): for a monomial ordering `>` and an ideal `I`
  there is a finite set `F` of monomials such that every monomial ordering `>_1` agreeing with `>` on `F` has `dim_K K[x]_>/I K[x]_> = dim_K K[x]_(>_1)/I K[x]_(>_1)` and the same Krull dimension. Corollary 7.5.5 (p. 408): `dim K[x]_>/I K[x]_> = dim K[x]/L(I)` for every
  monomial ordering; Corollary 7.5.6 (p. 408): the `K`-vector space dimensions agree as well, and when finite the monomials outside `L(I)` form a `K`-basis of `K[x]_>/I`.
- [P] SINGULAR Example 7.5.7 (p. 409): a flatness test for the homogenization of the ideal `<x^3 y + y z^2, x y^3 + x^2 z>` in `Q[x, y, z]`, comparing `I : <t>` with `I`, with the Tor criterion; the exercises 7.5.1 to 7.5.11 (pp. 410-411) extend Theorem 7.5.1 to modules and to Hilbert functions of the fibers (Exercise 7.5.2: for a global degree ordering and a homogeneous ideal the Hilbert function of the fiber is the same for all `lambda`).

## Mapping to this repository

- [I] Saturation step of the A_5 fiber-cone program ([run rulebook](../../runbooks/run-rulebook.md), ledger rows A5-416, A5-418 and A5-421 in `docs/evidence/a5-exceptional-fibers/ledger.tsv`): the defining ideal of the Rees algebra is
  obtained by saturating the ideal of the symmetric algebra by a generator `f` ([Vasconcelos 1994](vasconcelos-1994-arithmetic-blowup-algebras.md), Proposition 10.2.12 and the sentence after Proposition 10.2.3). The chain of statements is: saturation by stationary colon ideals (Section 1.8.9, p. 81), each colon ideal `I : <h>` from an intersection (Lemma 1.8.12, p. 80), that intersection by elimination of `t` (Lemma 1.8.10, p. 79), and the elimination from a standard basis for an elimination ordering (Lemma 1.8.3, p. 70).
  Section 1.8.9 (p. 81) justifies the computation of `I_1 : I_2^infinity` as a stationary chain of colon ideals,
  with the stopping test `I^(j+1) subset I^(j)` decided by reduction against a standard basis (Section 1.8.1, p. 67), and Lemma 1.8.14 (1) (p. 81) is the correctness statement; the saturation exponent `s` of the pages read is the number of
  colon steps. The elimination formulation `I : f^infinity = (I, 1 - t f) intersect K[x]` is not in the pages read; the pages give its radical-membership form in Lemma 1.8.8 (p. 77), the elimination lemma (Lemma 1.8.3, p. 70)
  that justifies solving such problems from a standard basis for an elimination ordering, and Lemma 1.8.12 (p. 80) which obtains a colon ideal by elimination of auxiliary variables.
- [I] Elimination step. The program's alternative route computes the defining ideal as the kernel of the map `T_i -> x_i t`. Lemma 1.8.16 (p. 84) is that statement for a ring map `phi` between quotients of polynomial rings, with the ordering conditions on the variables, and its solution is an elimination of the target
  variables from the graph ideal; Lemma 1.8.3 (p. 70) is the justification for reading the answer off a standard basis for an elimination ordering. For a global ordering `Ker(phi) = Ker(phi-bar)`; for a local or mixed ordering the lemma
  applies with the quotient `I_0`, which footnote 11 (p. 84) says may need a primary decomposition.
- [I] Colon ideal test. The membership test of Section 1.8.1 (reduction of each generator of one ideal modulo a standard basis of the other) decides `I_1 : I_2 = I_1` and `I^(j+1) subset I^(j)`; for the program's use ("is the colon ideal equal to the ideal, that is, is `f` regular modulo `I`") this is the test, and
  [Vasconcelos 1994](vasconcelos-1994-arithmetic-blowup-algebras.md) Proposition 10.2.3 states the regularity criterion in elimination form.
- [I] Theorem 7.5.1 and the standard basis lifting of [1005.5663](1005.5663.md). That note records the attribution of the global case to weighted homogenization (Theorem 7.5.1 of Greuel and Pfister). The theorem as printed on page 404 is a flatness statement: for an arbitrary
  monomial ordering and an ideal of a polynomial ring over a field `K`, a weighted degree ordering makes the weighted homogenization a flat family over `K[t]` with generic fiber `K[x]_(>_w)/I` and special fiber `K[x]_(>_w)/L(I)`. Proposition 7.5.3 (p. 405) is the equivalence that makes a standard basis of `I`
  a standard basis of the homogenization; Corollaries 7.5.5 and 7.5.6 (p. 408) carry dimension and `K`-dimension from `I` to `L(I)`, which equal the dimension statements used for fibers and leading ideals. The theorem states no comparison between two fields (such as `Q(i)` and `F_p`); the statement is over one field `K`.
- [I] Fields. Section 1.8 and Section 7.5 are stated over an arbitrary field `K`; Section 1.8.3 (p. 71) assumes `K` algebraically closed for its geometric reading, and no statement of the pages read restricts the characteristic. The commands in the book's examples are those of SINGULAR 3-0-3
  (second-edition preface) and the examples run over `Q`, so the procedure names (`sat` returning a list) are that version's; the repository runs Singular 4.4.1 (ledger row A5-421).
- [I] What the pages read do not give. (a) Neither Rees algebras nor fiber cones occur in the pages read. (b) No statement `I : f^infinity = (I, 1 - t f) intersect K[x]`, and no bound on the cost of a saturation (the book remarks only that the iterated quotient is usually faster than
  one quotient by a power). (c) The weighted truncation used in the repository's weight-slice computations (ledger row A5-421) is not a theorem of the pages read; Theorem 7.5.1 supplies the weighted homogenization and its flatness, and the repository's truncation argument is its own.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Only the pages listed under the reading scope were opened. The note asserts nothing about Sections 1.1 to 1.7, Sections 1.8.4 and 1.8.5 (solvability and solving of polynomial equations) and the rest of Section 1.8.3, Section 1.9 on non-commutative algebras, Chapters 2 to 6, the other sections of Chapter 7, the appendices or the SINGULAR
libraries beyond the commands named above. Proofs were read through and are not re-derived here, and no claim in this note rests on a computation in this repository.
