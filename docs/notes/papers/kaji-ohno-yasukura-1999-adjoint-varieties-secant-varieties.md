# Kaji, Ohno and Yasukura 1999: Adjoint varieties and their secant varieties (Indag. Math. 10)

## Source copy and license

The [source PDF](https://www.sciencedirect.com/science/article/pii/S0019357799800044/pdfft) remains external to the published library. It is a copy of the version of record (a scan of the journal pages) acquired from the publisher's site and held as a private reading copy. PDF page 1 is the first journal page ("Indag. Math., N.S., 10 (1), 45-57, March 29, 1999"); the pages carry no download stamp, no cover sheet and no publisher imprint.
No PDF page prints a copyright line, a license or a rights notice. The PDF holds no redistribution grant, so the registry records it as external-only under `NOASSERTION`. The reading copy is the ignored `docs/local_source_cache/kaji-ohno-yasukura-1999-adjoint-varieties-secant-varieties.pdf`. Attribution to Hajime Kaji, Masahiro Ohno and Osami Yasukura applies to every statement below.

Tag convention: [P] marks a statement of the paper; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index plus 44 (PDF page 1 is printed page 45 and PDF page 13 is printed page 57).

## Citation and provenance

- Authors: Hajime Kaji and Masahiro Ohno (Department of Mathematics, School of Science and Engineering, Waseda University, Japan) and Osami Yasukura (Department of Mathematics, Faculty of Education, Fukui University, Japan), as printed on p. 45; "Dedicated to Professor Hiroshi Asano on his 60th birthday"; "Communicated by Prof. A.J.H.M. van de Ven at the meeting of February 23, 1998".
  Journal: Indagationes Mathematicae, New Series, 10(1), 45-57 (March 29, 1999). The PDF prints no received date and no DOI; its metadata title field reads `PII: S0019-3577(99)80004-4`, an identifier that is not printed on any page.
- DOI [10.1016/S0019-3577(99)80004-4](https://doi.org/10.1016/S0019-3577(99)80004-4), not printed in the PDF. The Crossref record (title, authors, journal, volume 10, issue 1, pages 45-57, 1999) is a registered retrieval receipt; it lists the Elsevier text-mining and open-archive user licenses, which are Elsevier's own terms and no Creative Commons or public-domain grant.
- Retained PDF: 13 pages, 760297 bytes, SHA-256 `a0c5075f68418c70b7fbbf2a6e9592fed3a63e6c88bd5922423da7cad0cbf087`.
- Reading scope: PDF pages 1 to 13 in full (printed pages 45 to 57: the abstract and introduction, Sections 1 to 6 and the references), each page opened as an image, no text extraction. The scan is a bitmap of moderate resolution; the places where a printed glyph cannot be read with certainty are named in the Boundaries section.
- Status: published paper (version of record).

## Setting, definitions and the main results (abstract and introduction, pp. 45-46)

- [P] Abstract and introduction (pp. 45-46): `G` is a connected complex simple algebraic group with Lie algebra `g`, acting on the complex projective space `P_*(g)` of one-dimensional subspaces through the adjoint representation. The adjoint variety `X` is the unique closed orbit of this action; it is a smooth projective variety in `P_*(g)`, contained in no hyperplane, and independent of the choice of `G`.
  The secant variety `Sec X` of a complex projective variety `X` is the closure of the union of the projective lines through at least two points of `X`, and the secant deficiency is `delta = 2 dim X + 1 - dim Sec X`; the paper recalls Zak's bound `delta <= (1/2) dim X` for non-degenerate smooth `X` with `Sec X` not the ambient space, with equality for the Severi varieties.
- [P] Results announced on p. 46: a systematic form of the quadratic equations of all adjoint varieties through Dynkin's canonical form (Theorem 3.1); `dim Sec X = 2 dim X` for every adjoint variety, that is `delta = 1`, proved twice (Theorem 5.1); the description of `Sec X` as the closure of an orbit (Proposition 5.3); `Sec X` differs from the ambient space when the rank of `g` is at least 2 (Proposition 5.4), so the adjoint varieties of rank at least 2 give homogeneous projective varieties with degenerate secants (Example 5.5);
  and, for a general point `u` of `Sec X`, the contact locus `C_u` of `Sec X` with its embedded tangent space at `u` is a 2-dimensional linear subspace of `P_*(g)` (Theorem 6.1). The introduction adds that Zak's list of homogeneous varieties with degenerate secants omits adjoint varieties of rank at least 2 because a dimensional condition is assumed there, and that in the remaining rank-1 case, type `A_1`, the adjoint variety is a conic in `P^2` (Proposition 4.1).

## Graded decomposition and adjoint varieties (Sections 1 and 2, pp. 47-49)

- [P] Section 1 and Proposition 1.1 (p. 47): for a complex simple Lie algebra `g` with Killing form `B`, Cartan subalgebra `h`, root set `R`, a system of simple roots, the highest root `lambda` and a Chevalley basis `{H_alpha, X_alpha}`, the eigenspaces `g_j` of `ad H_lambda` give a decomposition `g = g_(-2) + g_(-1) + g_0 + g_1 + g_2`. Here `g_2 = C X_lambda` and `g_(-2) = C X_(-lambda)`; `g_1` and `g_(-1)` are spanned by the root vectors `X_alpha` and `X_(-alpha)` for `alpha` in `R_lambda`, the set of positive roots `alpha` with `lambda - alpha` a root;
  `g_0` is `h` plus the root vectors of both signs for the positive roots outside `R_lambda` and `lambda`; `[g_i, g_j]` lies in `g_(i+j)` with `g_j = 0` for `|j| > 2`; and `g_(+-1)` is nonzero if and only if `rk g >= 2` (the graded decomposition of complex contact type, a name the page uses when `rk g >= 2`).
- [P] Section 2 and Lemma 2.1 (pp. 47-48): for an irreducible finite-dimensional representation `V` of `G`, a nonzero `v` in `V` and `x = pi(v)`, the orbit `X = pi(G v) = G x` in `P_*(V)` is smooth and quasi-projective, closed when `v` is a highest weight vector. Lemma 2.1: the embedded tangent space `T_x X` is `P_*(g v)` when `v` lies in `g v` and `P_*(g v + C v)` when `v` does not.
  For the adjoint representation the orbit `X = pi(G X_lambda) = G x_lambda` of the highest root vector is the adjoint variety, determined by `g` alone (pp. 48-49).
- [P] Proposition 2.2 (p. 49): for an adjoint variety `X` in `P_*(g)`, with `x_lambda = pi(X_lambda)` and `h_lambda = pi(H_lambda)`, `T_(x_lambda) X = P_*(C H_lambda + g_1 + g_2)`, the span of `h_lambda`, `P_*(g_1)` and `x_lambda`; in particular `dim X = dim g_1 + 1 = #R_lambda + 1`.

## Equations of adjoint varieties (Section 3, pp. 49-51)

- [P] Setup (p. 49): Dynkin's canonical form is `D(Y, Z) = (B(T_lambda, T_lambda)/2) B(Y, Z)` with `B(T_lambda, H) = lambda(H)` for `H` in `h`, so `D(H_lambda, H_lambda) = 2` and `D(H_lambda, H) = lambda(H)`. For a constant `epsilon` in `C` and `Y_1, Y_2` in `g`, `Y_1 v_epsilon Y_2` is the linear endomorphism of `g` given by the symmetrized double bracket plus `D(Y_1, Z) Y_2 + D(Y_2, Z) Y_1 - epsilon D(Y_1, Y_2) Z`,
  and `(Y v_epsilon Y) Z = (ad Y)^2 Z + 2 D(Y, Z) Y - epsilon D(Y, Y) Z`.
- [P] Theorem 3.1 (p. 50): for an adjoint variety `X` in `P_*(g)` and `epsilon` different from 2, `X = pi(W)` with `W = {Y in g, Y nonzero : Y v_epsilon Y = 0}`; the statement is a description of `X` as a zero set of quadratic equations. Lemma 3.2 (p. 50): for `epsilon` different from 2 and `Y` nonzero, `Y v_epsilon Y = 0` if and only if `(ad Y)^2 Z + 2 D(Y, Z) Y = 0` for all `Z` in `g`.
  The proof (pp. 50-51) shows `X_lambda` in `W` by the graded decomposition and shows that any two nonzero elements of `W` project into one orbit of the adjoint group, first when `D(Y_1, Y_2)` is nonzero and then in general by an argument with an orthogonal complement and the irreducibility of the adjoint action.

## The case of type A_1 (Section 4, pp. 51-53)

- [P] Proposition 4.1 (p. 51): for `g = sl_2(C)` with `P_*(g) = P^2` and the conic `Q = {(xi : eta : zeta) : xi zeta + eta^2 = 0}`, the adjoint action has the two orbits `G x_+ = Q` and `G h = P^2` minus `Q`; so `Q` is the adjoint variety and `Sec Q = P^2`. The paper gives a second proof of the orbit of `h` through tangent lines to `Q` (p. 52) and states that the relation among `x_+`, `x_-` and `h` extends to general adjoint varieties (Remark 4.2, p. 52).
  The explicit quadratic equations of Theorem 3.1 for `sl_2(C)` are computed on pp. 52-53 and reduce to `xi zeta + eta^2 = 0`.

## Secant varieties (Section 5, pp. 53-55)

- [P] Lemma 5.2 (p. 53): the orbit of `(x_lambda, x_(-lambda))` in `X x X` is a dense open subset of `X x X`. Theorem 5.1 (p. 53): for an adjoint variety `X` in `P_*(g)`, `dim Sec X = 2 dim X`. Proof 1 (p. 53) applies Terracini's lemma at a general point `z` in the span of general points `x, y` of `X`, uses Lemma 5.2 to take `(x, y) = (x_lambda, x_(-lambda))`,
  and computes `<T_(x_lambda) X, T_(x_(-lambda)) X> = P_*(g_(-2) + g_(-1) + C H_lambda + g_1 + g_2)` by Proposition 2.2, of dimension `2(dim g_1 + 1) = 2 dim X`.
- [P] Proposition 5.3 (p. 54): for an adjoint variety `X` in `P_*(g)`, the orbit `G h_lambda` is a dense open subset of `Sec X`, so `Sec X` is the closure of `G h_lambda`; the proof reduces to the `A_1` subalgebra `s_lambda = C X_lambda + C H_lambda + C X_(-lambda)` and Proposition 4.1. Proof 2 of Theorem 5.1 (p. 54) computes the tangent space of the orbit `G h_lambda` at `h_lambda` as `P_*(g_(-2) + g_(-1) + C H_lambda + g_1 + g_2)`.
  Proposition 5.4 (p. 54): `codim(Sec X, P_*(g)) = dim g_0 - 1` for an adjoint variety `X` in `P_*(g)`; in particular `Sec X` is not `P_*(g)` when `rk g >= 2`.
- [P] Example 5.5 (p. 55): the table of adjoint varieties lists, for type `A_l` (`l >= 1`) with highest root `omega_1 + omega_l`, the variety printed as `P(T_(P^l)) = P^l x P^l intersect (1)` (the legend reads the last symbol as cutting by a general hyperplane) with `dim g = (l + 1)^2 - 1`; for `B_l` (`l >= 2`), `C_l` (`l >= 3`), `D_l` (`l >= 4`) the Fano variety of lines in a quadric (`B_l`, `D_l`) and the Veronese embedding `v_2(P^(2l-1))` (`C_l`); and one line for each of `E_6`, `E_7`, `E_8`, `F_4` and `G_2` with `dim g` equal to 78, 133, 248, 52 and 14.
  The text beneath the table identifies the `A_l` entry with the flag manifold of pairs `(P, H)`, `P` a point and `H` a hyperplane through `P`, of a projective space printed as `P_*(g)`. [I] The dimension `2l - 1` that Proposition 2.2 gives for type `A_l` fixes that space as `P^l`, the projective space of the defining representation.

## Contact loci (Section 6, pp. 55-56)

- [P] Section 6 (p. 55): for a smooth projective variety `X` in `P` and a general point `u` of `Sec X`, `C_u` is the closure of the set of points `v` of the smooth locus of `Sec X` with `T_v Sec X = T_u Sec X`, the contact locus of `Sec X` with the embedded tangent space at `u`. Theorem 6.1 (p. 56): for an adjoint variety `X` in `P_*(g)`, `dim C_u = 2` for a general point `u` of `Sec X`.
  Proposition 6.2 (p. 56): `C_(h_lambda) = P_*(s_lambda)`, the projective plane of the `A_1` subalgebra `s_lambda`; the proof uses Terracini's lemma, the identification of `T_(h_lambda) Sec X` with `P_*([g, L_lambda])` for `L_lambda = C X_lambda + C X_(-lambda)`, and the inclusion `g . s_lambda` in `s_lambda` for an element `g` of the group with `g . h_lambda` a general point of the contact locus.

## Mapping to this repository

- [I] Citing context. No ledger row, note or evidence file cites this paper. The lead that the degree-20 component of the W8 fiber cone is the adjoint variety of `SL_4` (the incidence variety of points and hyperplanes of `P^3` in `P(sl_4) = P^14`) was stated as a conjecture in issue 863 of this repository
  and refuted there in its equivariant form; this note rests on the paper and records what it supplies for that comparison.
- [I] What the paper supplies for a comparison with the adjoint variety of `SL_4` (type `A_3`, `g = sl_4`, `dim g = 15`). `R_lambda` has four positive roots (`alpha_1`, `alpha_3`, `alpha_1 + alpha_2`, `alpha_2 + alpha_3`), so `dim g_1 = 4` and Proposition 2.2 gives `dim X = 5` in `P_*(g) = P^14`; the table of Example 5.5 gives `dim g = 15` for `l = 3`. `g_0` is the Cartan subalgebra of dimension 3 plus the root vectors of both signs for the one remaining positive root `alpha_2`, so `dim g_0 = 5`;
  Theorem 5.1 gives `dim Sec X = 10` and Proposition 5.4 gives codimension `dim g_0 - 1 = 4` in `P^14`. Theorem 6.1 gives a contact locus of dimension 2 at a general point of `Sec X`, and Proposition 6.2 identifies it with the projective plane `P_*(s_lambda)` at `h_lambda`. Theorem 3.1 describes `X` as the zero set of quadrics `Y v_epsilon Y = 0` for `epsilon` different from 2. These are [I] computations from the printed statements for the case `sl_4` (the paper states the general formulas, not the case).
- [I] What the paper does not supply. (a) No degree, Hilbert function or Hilbert series of an adjoint variety, no number of independent quadrics, and no statement that the quadrics of Theorem 3.1 generate the ideal of `X` or that they define `X` as a reduced scheme; the theorem is a set-theoretic description. (b) Nothing on degenerations, cones over hyperplane sections, contractions along a symmetric pair or other varieties related to `X`. (c) Every statement is over the complex numbers; the program computes over `Q(i)` and modulo the primes 32009 and 32029,
  and the paper makes no statement over a field of positive characteristic or over a field that is not algebraically closed. (d) The comparison of a computed variety with `X` needs explicit coordinates in which `X` is the orbit of the highest root vector; the paper supplies the abstract description and the tangent and secant spaces, not a coordinate chart of `P^14`.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] All thirteen PDF pages were opened. The proofs of Theorem 3.1, Theorem 5.1, Proposition 5.3 and Proposition 6.2 were read through and are not re-derived here. Several glyphs of the scan are not read with certainty and are not relied on: the ambient projective space in the sentence on p. 55 that describes the `A_l` variety as pairs (point, hyperplane) (printed as `P_*(g)`, read as the projective space of the defining representation),
the exponents of the table entries of the exceptional types in Example 5.5 (only `dim g` is recorded for them), and the form of the `A_l` entry of the table (a hyperplane section of a product of two projective spaces, read as the incidence variety). The note asserts nothing about the cited works (Zak, Lazarsfeld and Van de Ven, Fujita and Roberts, Fujita, Ohno, Kaji, Lichtenstein, Freudenthal, Dynkin, Yamaguti, Asano, Wolf, Boothby and others)
beyond the paper's own citations of them. No claim in this note rests on a computation in this repository.
