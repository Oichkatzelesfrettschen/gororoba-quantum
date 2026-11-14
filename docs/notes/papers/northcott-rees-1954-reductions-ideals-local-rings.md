# Northcott and Rees 1954: Reductions of ideals in local rings (Proc. Cambridge Philos. Soc. 50)

## Source copy and license

The [source PDF](https://doi.org/10.1017/S0305004100029194) remains external to the published library. It is a copy of the version of record (a scan of the journal pages, preceded by a one-page publisher cover sheet)
acquired from a third-party mirror and held as a private reading copy. PDF page 1 is a Cambridge Journals cover sheet ("Published online: 24 October 2008") that carries a download stamp dated 04 May 2013 and links headed "Terms of use"
and "Request Permissions"; no PDF page prints a copyright line. The PDF holds no redistribution grant, so the registry records it as external-only under `NOASSERTION` with the cover sheet as the rights locator. The reading copy is the ignored
`docs/local_source_cache/northcott-rees-1954-reductions-ideals-local-rings.pdf`. Attribution to D. G. Northcott and D. Rees applies to every statement below.

Tag convention: [P] marks a statement of the paper; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index plus 143 (PDF page 2 is printed page 145 and PDF page 15 is printed page 158); PDF page 1 is the cover sheet and has no printed number. Section numbers restart at 1 in each section of the paper, so a result is cited as "Theorem 1 of Section 4" with its printed page.

## Citation and provenance

- Authors: D. G. Northcott and D. Rees. The two addresses at the end of the paper (p. 158) read "The University, Sheffield" and "Downing College, Cambridge"; the paper does not tie an address to a name, and the left-to-right order of the addresses matches the order of the authors.
  Journal: Proceedings of the Cambridge Philosophical Society, Vol. 50, Part 2 (April 1954), pp. 145-158; "Received 2 September 1953" (p. 145). The cover sheet prints the DOI 10.1017/S0305004100029194 and "Volume 50 / Issue 02 / April 1954".
- DOI [10.1017/S0305004100029194](https://doi.org/10.1017/S0305004100029194), printed on the cover sheet. The Crossref record (title, authors, volume 50, issue 2, pages 145-158, April 1954) is a registered retrieval receipt; it names the journal by its later title, Mathematical Proceedings of the Cambridge Philosophical Society, and lists the Cambridge Core terms, which are the publisher's own terms and no Creative Commons or public-domain grant.
- Retained PDF: 15 pages, 1380722 bytes, SHA-256 `77fea37911f3611fb5604ed3f56426999a06e10ca632612a2668f65e3d67b596`.
- Reading scope: PDF pages 1 to 15 in full (the cover sheet and printed pages 145 to 158: the introduction, Sections 1 to 8 and the three references), each page opened as an image, no text extraction. The scan is a bitmap of moderate resolution; the two places where a printed
  formula cannot be read with certainty are named in the Boundaries section.
- Status: published paper (version of record).
- References of the paper (p. 158): Chevalley, Intersections of algebraic and algebroid varieties, Trans. Amer. Math. Soc. 57 (1945); Pruefer, Untersuchungen ueber die Teilbarkeitseigenschaften in Koerpern, J. reine angew. Math. 168 (1932); Samuel, La notion de multiplicite en algebre et en geometrie, thesis (Paris, 1951).

## Reductions and their multiplicities (Section 1, pp. 145-146)

- [P] Section 1 (p. 145): `R` is a commutative ring with a unit element in which every ideal is finitely generated, and "ideal" always means a proper ideal. Definition 1: for ideals `b` and `a` of `R`, `b` is a reduction of `a` if `b` lies in `a` and `b a^r = a^(r+1)` for at least one positive integer `r`;
  the introduction (p. 145) states the same condition as `b a^n = a^(n+1)` for all large `n`. The page adds that every ideal is a reduction of itself, and that `b a^r = a^(r+1)` implies `b a^n = a^(n+1)` for all `n >= r` and `b^m a^r = a^(r+m)` for all positive integers `m`.
- [P] Theorem 1 of Section 1 (p. 146): if `b` is a reduction of `a`, then `a` and `b` have the same minimal prime ideals, and `e(a, p) = e(b, p)` for every common minimal prime ideal `p`. Here `e(q)` is the integer `e` in the leading term `e n^d / d!` of the polynomial that the length function `P_q(n)` of the `n`-th symbolic power of a primary ideal `q` becomes
  for large `n` (`d` the rank of the prime of `q`, citing Samuel's thesis), and `e(a, p) = e(q)` for the `p`-primary component `q` of `a` at a minimal prime `p`. The proof (p. 146) sandwiches the symbolic powers of the two primary components through `a^m >= b^m >= b^m a^r = a^(r+m)`.
- [P] Definitions 2 and 3 and Lemma 1 of Section 1 (p. 146): a reduction `b` of `a` is minimal if no ideal strictly inside `b` is a reduction of `a`; an ideal with no reduction other than itself is basic; if `b` is a reduction of `a` and `c` is a reduction of `b`, then `c` is a reduction of `a`.
  A minimal reduction of an ideal is therefore basic (p. 146).

## Existence of minimal reductions (Section 2, pp. 146-148)

- [P] Standing hypothesis of Section 2 (pp. 146-147): the reductions considered belong to a fixed local ring `Q` with maximal ideal `m`, and "for simplicity" the residue field `k = Q/m` is assumed infinite, although the paper remarks that several results do not need it. The first use of the infinite residue field is
  recorded in a footnote on p. 150 (the proof of Lemma 2 of Section 4), so none of the results of Sections 1 to 3 and no Lemma 1 of Section 4 invokes it.
- [P] Theorem 1 of Section 2 (p. 147): if `b` is a reduction of `a`, there is at least one ideal `c` inside `b` that is a minimal reduction of `a`. Lemma 1 of Section 2 (p. 147): `a_1 <= a_2 + a_1 m` implies `a_1 <= a_2`. Lemma 2 of Section 2 (p. 147): an ideal `c` inside `a` is a reduction of `a` if and only if `c + am` is a reduction of `a`.
  Lemma 3 of Section 2 (pp. 147-148): if `c` is a minimal reduction of `a` and `b` is an ideal with `c <= b <= a`, then every minimal base of `c` extends to a minimal base of `b`.

## Analytic spread (Section 3, pp. 148-149)

- [P] Theorem 1 of Section 3 (p. 148): `phi(s, a) = dim_k (a^s / a^s m)`, the number of elements in a minimal base of `a^s`, equals a polynomial in `s` for all large `s`. The proof fixes a base `u_1, ..., u_t` of `a` (not necessarily minimal) and defines the null forms of `a`: for a form `phi(X_1, ..., X_t)` of degree `s` with coefficients in `Q`,
  not all in `m`, the residue form `phi-bar` in `k[X_1, ..., X_t]` is a null form of `a` when `phi(u) = 0 (mod a^s m)` (Definition 1, p. 148). The null form ideal `n` of `a` is the homogeneous ideal of `k[X_1, ..., X_t]` generated by the null forms (Definition 2, p. 148). The proof gives, for each `s`, an isomorphism of `k`-vector spaces between `a^s / a^s m`
  and the space of degree-`s` forms modulo the degree-`s` forms in `n`, so `phi(s, a)` is the ordinary Hilbert function of `n` (stated on p. 149).
- [P] Definition 3 (p. 149): the analytic spread `l(a)` is `d + 1`, with `d` the degree of the polynomial of Theorem 1; `phi(s, a) = 0` for all large `s` exactly when `a` is nilpotent, and for a nilpotent ideal `l(a)` is taken to be zero, while `l(a)` is strictly positive for every other ideal.
  Theorem 2 of Section 3 (p. 149): `l(a)` equals the dimension of the null form ideal `n` of `a`, as an immediate consequence of `phi(s, a)` being the Hilbert function of `n`.

## Minimal reductions and analytic independence (Section 4, pp. 149-152)

- [P] Definitions 1 and 2 of Section 4 (p. 149): elements `v_1, ..., v_r` of `a` are analytically independent in `a` when every form `phi` of degree `p` with coefficients in `Q` and `phi(v) = 0 (mod a^p m)` has all its coefficients in `m`; elements of `Q` are analytically independent when `phi(v) = 0` forces the coefficients into `m`.
  Elements are analytically independent if and only if they are analytically independent in the ideal they generate. Lemma 1 of Section 4 (p. 149): elements analytically independent in `a` form a minimal base of the ideal they generate, and every other minimal base of that ideal is again analytically independent in `a`.
- [P] Lemma 2 of Section 4 (p. 149, proof p. 150): if `c` is a minimal reduction of `a` and `v_1, ..., v_r` is a minimal base of `c`, the `v_i` are analytically independent in `a`; the proof uses the infinite residue field. Lemma 3 of Section 4 (p. 150): analytically independent elements `v_1, ..., v_r` of `a` satisfy `r <= l(a)`.
- [P] Theorem 1 of Section 4 (p. 150, proof pp. 150-151): let `b` be a reduction of `a` with minimal base `v_1, ..., v_r`; then `b` is a minimal reduction of `a` if and only if the `v_i` are analytically independent in `a`, and if `b` is a minimal reduction of `a`, then `r = l(a)`.
- [P] Theorem 2 of Section 4 and its corollary (p. 151): if `b` is a reduction of `a`, at least `l(a)` elements are needed to generate `b`, and if `b` can be generated by `l(a)` elements, it is a minimal reduction of `a`; hence `l(a)` is the smallest number of elements that generate a reduction of `a`.
  Theorem 3 of Section 4 (p. 151): `l(a)` is the maximum number of elements of `a` that are analytically independent in `a`.
- [P] Lemma 4 of Section 4 (p. 151), for an arbitrary ideal `a`: `rank a <= l(a) <= dim_k (a / am)`, where "rank" is the paper's term for the rank of an ideal, used on these pages without a definition. The proof takes a minimal reduction `c` with minimal base `v_1, ..., v_l`, notes that `c` and `a` have the same minimal primes (Theorem 1 of Section 1), and bounds `rank a = rank (v_1, ..., v_l)` by `l`.
- [P] Theorem 4 of Section 4 (p. 152): `a` is basic if and only if the elements of a minimal base of `a` are analytically independent, and if and only if `l(a) = dim_k (a / am)`; the page adds that a local ring is regular exactly when its maximal ideal is basic.
  Theorem 5 of Section 4 (p. 152): an ideal of rank `r` that can be generated by `r` elements is basic, so the elements of each of its minimal bases are analytically independent (the analytic independence of a system of parameters is the special case).

## Reductions and non-special elements (Section 5, pp. 152-154)

- [P] Lemma 1 of Section 5 (p. 152, proof pp. 152-153): for `a = (u_1, ..., u_r)` with a base that need not be minimal, null form ideal `n` in `k[X_1, ..., X_r]` and linear forms `lambda_i(X) = sum_j alpha_ij X_j` with `alpha_ij` in `Q` (`1 <= i <= t`),
  the elements `lambda_1(u), ..., lambda_t(u)` generate a reduction of `a` if and only if the ideal `(lambda-bar_1, ..., lambda-bar_t, n)` of `k[X]` is primary to `(X_1, ..., X_r)`, where the bar is the residue form over `k`.
- [P] Theorem 1 of Section 5 (p. 153, proof pp. 153-154): for `l = l(a)` there is a system of polynomials `D_1(Z_ij), ..., D_n(Z_ij)` in the `lr` indeterminates `Z_ij` (`1 <= i <= l`, `1 <= j <= r`) with coefficients in `Q` (a kind of resultant system of generators of `n` and the linear forms) such that, for elements `a_ij` of `Q`,
  the `l` elements `v_i = sum_j a_ij u_j` generate a minimal reduction of `a` if and only if at least one `D_nu(a_ij)` is a unit of `Q`. The remark on p. 154 states that, because `Q/m` is infinite, elements `a_ij` with `D(a_ij)` nonzero modulo `m` exist, and calls this the precise form of the statement that any `l` non-special elements of `a` generate a minimal reduction.

## Primary ideals of the maximal ideal (Section 6, p. 154)

- [P] Section 6 (p. 154): `d = dim Q`. Theorem 1 of Section 6 (printed with `a` for `q` in the hypothesis): if `q` is `m`-primary, then `l(q) = rank q = dim Q`. Corollary 1: for `m`-primary `q`, the maximum number of elements of `q` that are analytically independent in `q` is `dim Q`. Corollary 2: an `m`-primary ideal is basic if and only if a system of parameters generates it.
  Theorem 2 of Section 6: for `m`-primary `q` and `d` non-special elements `v_1, ..., v_d` of `q`, the `v_i` form a system of parameters and `e(q) = e(v_1, ..., v_d)`; the proof applies Theorem 1 of Section 5 (the `v_i` generate a minimal reduction of `q`) and Theorem 1 of Section 1 (that reduction is `m`-primary and has the multiplicity of `q`).

## Ideals containing a non-zero-divisor (Section 7, pp. 154-157)

- [P] Section 7 (pp. 154-155) extends the results to ideals that are not composed exclusively of zero-divisors, by methods tied to Pruefer's A-process, and notes that what the paper calls analytic dependence of an element had been called integral dependence. Lemma 1 of Section 7 (p. 155): if `b_1` is a reduction of `a_1` and `b_2` is a reduction of `a_2`, then `b_1 + b_2` is a reduction of `a_1 + a_2`.
  Theorem 1 of Section 7 (p. 155): for every ideal `a` there is a (necessarily unique) ideal `a-hat` such that `a` is a reduction of `a-hat` and every ideal that has `a` as a reduction lies in `a-hat`; the proof uses the maximal condition on ideals. Its corollary: if `b` is a reduction of `a`, then `b-hat = a-hat`.
- [P] Definitions of Section 7 (pp. 155-156): an element `v` is analytically dependent on elements `u_1, ..., u_r` if some form `phi` in `r + 1` variables satisfies `phi(u_1, ..., u_r, v) = 0` and its coefficient of `V^m`, `m` the degree of `phi`, is a unit; an element is analytically dependent on an ideal if it is analytically dependent on some base of the ideal (Lemma 2 and its corollary, pp. 155-156, show the choice of base is immaterial).
  The paper numbers both the dependence definition for an ideal and the definition of a relevant ideal "Definition 2" in Section 7; a relevant ideal is one not composed exclusively of zero-divisors (p. 156). Lemma 3 of Section 7 (p. 156): `b` is a reduction of `(b, alpha)` if and only if `alpha` is analytically dependent on `b`.
- [P] Theorem 2 of Section 7 (p. 156): for `b` contained in a relevant ideal `a`, `b` is a reduction of `a` if and only if `bc = ac` for some relevant ideal `c`. Theorem 3 of Section 7 (pp. 156-157): for a relevant ideal `a`, `a-hat` consists of all elements analytically dependent on `a`, and the ideals that have `a` as a reduction are exactly the ideals between `a` and `a-hat`.
  Theorem 4 of Section 7 (p. 157): if `b` is a reduction of the relevant ideal `a`, then `l(a) = l(b)`, and the reductions of `a` contained in `b` are the reductions of `b`; its corollary: a reduction `b` of a relevant ideal `a` is a minimal reduction if and only if `b` is basic.
  Theorem 5 of Section 7 (p. 157): elements `v_1, ..., v_r` of a relevant ideal `a` form a minimal base of a minimal reduction of `a` if and only if they are analytically independent and every element of `a` is analytically dependent on them.

## Analytic disjointness and the associative law (Section 8, pp. 157-158)

- [P] Lemma 1 of Section 8 (p. 157): `l(a + b) <= l(a) + l(b)` for any two ideals. Definition 1 of Section 8 (p. 157): `a` and `b` are analytically disjoint when `l(a + b) = l(a) + l(b)`.
- [P] Theorem 1 of Section 8 (p. 158): let `Q` be a local ring that admits a nucleus (the notion of Chevalley, not restated in the paper), and let `a` and `b` be analytically disjoint ideals whose sum is `m`-primary; then `e(a + b) = sum_i e[(a + p_i)/p_i] e[b, p_i]`, with `p_1, ..., p_s` the minimal prime ideals of `b`.
  The proof reduces to a system of parameters and applies the associative law for multiplicities of Chevalley (reference (1), Theorem 5, 25).

## Mapping to this repository

- [I] The A_5 fiber-cone program ([run rulebook](../../runbooks/run-rulebook.md), ledger row A5-004 and the "analytic spread" paragraph of `docs/evidence/a5-exceptional-fibers/structure/README.md`) cites this paper for one criterion: the fiber `F(I)` of the Rees algebra at the maximal ideal is a quotient of the polynomial ring `k[y_1, ..., y_s]` in the generators of `I`,
  its Krull dimension is the analytic spread `l(I)`, and `F(I) = k[y]` exactly when `l(I) = s`. Row A5-004 is the only row that names the paper. Rows A5-005, A5-011, A5-014, A5-021, A5-065, A5-245 and A5-293 use the analytic spread without citing it, and row A5-175 tests whether a 4-generated reduction `Q` with `Q I^r = I^(r+1)`
  bounds the spread, which is Definition 1 of Section 1 of this paper with `b = Q`.
- [I] What the paper supplies for the criterion. For a fixed base `u_1, ..., u_t` of `a`, Theorem 1 of Section 3 (proof, p. 148) identifies each graded piece `a^s / a^s m` with the degree-`s` piece of `k[X_1, ..., X_t] / n`, and Theorem 2 of Section 3 (p. 149) sets `l(a)` equal to the dimension of the null form ideal `n`.
  Reading `k[X]/n` as the fiber `F(a)` (the substitution `X_i -> u_i` is multiplicative, a step the paper states only as an isomorphism of vector spaces) gives `F(a)` as a quotient of a polynomial ring in `t` variables with `dim F(a) = l(a)`. A nonzero homogeneous ideal of the domain `k[X_1, ..., X_t]` lowers the Krull dimension below `t`,
  so `F(a) = k[X]` exactly when `n = 0`, that is when `l(a) = t`; the paper does not state this step, which uses no hypothesis on the residue field. Lemma 4 of Section 4 (p. 151) bounds `l(a)` by `dim_k (a / am)`, the number of minimal generators; its proof takes a minimal reduction, so it stands under the infinite residue field of Section 4, and the same upper bound follows without it from Theorem 2 of Section 3 applied to a minimal base.
- [I] What the paper does not supply. (a) The second clause of A5-004, that a count `s` above the dimension of the germ ring forces a proper fiber, needs `l(a) <= dim Q` for the ideal at hand. The paper states `l(q) = dim Q` for `m`-primary ideals only (Theorem 1 of Section 6, p. 154) and bounds `l(a)` above by `dim_k (a / am)` for an arbitrary ideal; the bound by `dim Q` for an arbitrary ideal is not on the pages read.
  On the Iso and W8 slices the zero locus of the generators near the origin is a linear 3-space, so the ideal is not `m`-primary there (`docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/README.md`, the paragraph "Structure that explains the ranks"). (b) The infinite residue field. The results on minimal reductions (Theorem 1 of Section 2 apart) and the equalities `l(a) =` the number of generators of a minimal reduction (Theorem 1 and Theorem 2 of Section 4), Lemma 4 of Section 4 as proved, and Theorems 1 and 2 of Section 6 rest on Lemma 2 of Section 4,
  which uses it (footnote, p. 150). The program computes modulo the primes 32009 and 32029, where the residue field at the origin is finite, and over `Q(i)`, where it is infinite; so the dimension statement of Theorem 2 of Section 3 applies in both cases and the generator-count statements (as in row A5-175) only over `Q(i)`.
  (c) The paper treats local rings; the passage from the local ring at the origin of a germ to the graded polynomial rings of the scripts is not in it. (d) It gives no Hilbert function of `F(a)` and no presentation of `n` for any family of ideals.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] All fifteen PDF pages were opened and every statement above was read against its printed page. The proofs of Sections 2 to 7 were read through and are not re-derived here. Two printed formulas are not reproduced because the scan does not let them be read with certainty: the length function in the definition of `e(q)` on p. 146
(the scan shows `length q^(n)`, and the definition is recorded in words), and the inequality chain in the proof of Theorem 1 of Section 6 on p. 154, where the printed order of the two lengths cannot be read. The notion of a nucleus (Section 8) is not defined in the paper and is not defined here. The note asserts nothing about the cited works (Chevalley, Pruefer, Samuel) beyond the paper's own citations of them.
No claim in this note rests on a computation in this repository.
