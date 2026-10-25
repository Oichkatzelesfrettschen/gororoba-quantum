# R. B. Brown 1967: on generalized Cayley-Dickson algebras (Pacific J. Math. 20)

## Source copy and license

The [source PDF](http://msp.org/pjm/1967/20-3/pjm-v20-n3-p03-s.pdf) remains external to the published library.
Its optional personal reading copy is `docs/local_source_cache/brown-1967-generalized-cayley-dickson.pdf`.
The article's [landing page](https://msp.org/pjm/1967/20-3/p03.xhtml) prints "(c) Copyright 1967 Pacific Journal of
Mathematics" and names no open license; the PDF repeats the journal's notices on its title page and in the
volume listing. The inspected evidence supplies no rehosting grant, so the copy stays external.
[SOURCES.json](../../SOURCES.json) binds the source bytes, the landing-page hash and the reading scope.
Original PDF SHA-256: `03ffabb6b1f05282fe6c2d65ced324741108e07f717e1228a69432e3d7d4ee0d`.

[P] identifies a source statement. [I] identifies a repository deduction or
proposed use. Citation and retrieval fields record bibliographic facts. The page numbers below are the journal's
pages 415 to 422 as printed on the article pages.

This paper is by Robert B. Brown and is distinct from the 1972 dissertation of Harmon C. Brown on zero divisors
([brown-1972-dissertation.md](brown-1972-dissertation.md)).

## Citation and provenance

- Author: Robert Bruce Brown (University of California, Berkeley).
- Title: On generalized Cayley-Dickson algebras.
- Venue: Pacific Journal of Mathematics 20(3), 415-422 (1967), received 23 January 1966; DOI
  [10.2140/pjm.1967.20.415](https://doi.org/10.2140/pjm.1967.20.415) (Crossref record retrieved 25 October 2026).
- PDF: http://msp.org/pjm/1967/20-3/pjm-v20-n3-p03-s.pdf, 11 pages (the article plus the journal's front and back matter),
  1,008,368 bytes. The text layer is a scanned-page OCR: Greek letters and overbars are damaged.
- Reading scope: all 8 article pages. The formula of the order-3 automorphism `psi` (p. 417) and several displayed equations
  (Eqs. 1, 4 to 8 and 10, 11) are partly unreadable in the text layer; the statements below follow the surrounding prose and
  were checked by the computations in the next section, which reconstruct `psi`.

## Statements and hypotheses

- [P] Definitions (p. 415): for an algebra `A` with involution `a -> a*` and nonzero `gamma` in the ground field, `A{gamma}` is the set
  of pairs `a + b u` with `(a + b u)(c + d u) = (a c + gamma d* b) + (d a + b c*) u`, `u = (0, 1)`, so `u^2 = gamma`, and the involution
  extends by `a + b u -> a* - b u`. The generalized Cayley-Dickson algebra `A_t` of dimension `2^t` starts from the field with trivial
  involution and adjoins `u_1, ..., u_t` with `u_i^2 = gamma_i`; `n(x) = x x*`, and `A_t` is a composition algebra only for `t <= 3`.
- [P] Normal sets of generators (p. 416): `v_1, ..., v_t` with `v_i^2 = delta_i` such that multiplication in each `A_i = A_(i-1) + A_(i-1) v_i`
  follows Eq. 2; for `A_3` every normal set arises from `v_1` with `(v_1, 1) = 0`, `v_2` orthogonal to `1, v_1`, and `v_3` orthogonal to
  `1, v_1, v_2, v_1 v_2`; `A_3` has zero divisors exactly when some nonzero `a` has `n(a) = 0`.
- [P] Section 2, automorphisms (pp. 416-417): by Schafer, for `t >= 4` every derivation of `A_t` is `a + b u -> a D + (b D) u` with `D` a
  derivation of `A_(t-1)`. Over a ground field containing `beta = 1/sqrt(-3 gamma)`, for an automorphism `theta` of `A_(t-1)` the maps
  `theta'(a + b u) = a theta + (b theta) u`, `epsilon(a + b u) = a - b u` and an order-3 map `psi` satisfy
  `psi theta' = theta' psi`, `epsilon theta' = theta' epsilon`, `epsilon^2 = 1`, `psi^3 = 1`, `epsilon psi = psi^2 epsilon`, so
  `Aut(A_t)` contains `G = Aut(A_(t-1)) x S_3`; if `beta` is absent from the field, `psi` does not exist and the subgroup is
  `Aut(A_(t-1)) x Z_2`.
- [P] **Theorem 1 (p. 417):** for `t = 4, 5, 6` and characteristic not 2 or 3, `Aut(A_t) = G`. **Theorem 2 (p. 417):** for
  `t = 4, 5, 6`, `A_(t-1){gamma}` and `A'_(t-1){gamma'}` are isomorphic exactly when `A_(t-1)` and `A'_(t-1)` are and `gamma = lambda^2 gamma'`.
  The paper proves both in detail for `t = 4` and sketches `t = 5, 6`, and conjectures both for all `t >= 4`.
- [P] Lemma 1 (p. 417): for `t >= 4`, if `v` satisfies `(v, 1) = 0` and `x(xv) = x^2 v`, `(vx)x = v x^2` for all `x`, then `v` is a multiple
  of `u`. Lemma 2 (p. 418): the derivation algebra of `A_3` maps `A_3` into its pure part and its enveloping algebra is the
  full set of linear maps of that part. The proofs of Theorems 1 and 2 at `t = 4` follow (pp. 418-419), reducing them to quadratic
  equations in `a eta` and `b eta`.
- [P] Section 3, division algebras (pp. 420-422): Theorem 3 (p. 420): `A_4 = A_3{gamma}` is a division algebra iff `A_3` is,
  `gamma` is not the norm of an element of `A_3` and `-gamma` is not the norm of an element of the pure part; if `gamma = a a*`
  then `(a + u)(a* - u) = 0`, and if `-gamma = x x*` with `x` extended to a normal set `v_1 = x, v_2, v_3`, then
  `(v_1 v_2 - v_2 u)(v_1 v_3 + v_3 u) = 0`. Over finite fields, `p`-adic fields, the real field and the rational field no `A_t` with
  `t >= 4` is a division algebra; over `Q(sqrt(lambda))` for suitable positive `lambda`, `A_4` is, and for every `t` a division
  algebra exists over a field of iterated power series (pp. 421-422).

## Convention map and cd_core check

[I] Product. The printed rule `(a + b u)(c + d u) = (a c + gamma d* b) + (d a + b c*) u` with `gamma = -1` is `cd_core`'s doubling
`(a,b)(c,d) = (ac - conj(d) b, d a + b conj(c))`, and Brown's `u` is `e_(2^(t-1))` in the XOR index; no change of convention
is needed to compare with `cd_core`.

[I] Check results. A scratch script (ignored `docs/local/`, run with `-I`) tested the statements of this note on `cd_core` with the
floating-point and exact checks named:

| Paper statement | Result under `cd_core` |
| --- | --- |
| `epsilon` is an automorphism of `A_t` (p. 417) | exact: `epsilon(x y) = epsilon(x) epsilon(y)` on random vectors at `D = 16, 32, 64` (defect 0) |
| an order-3 `psi` with `epsilon psi = psi^2 epsilon` exists for `gamma = -1` (where `beta = 1/sqrt(3)` is real) | the reconstructed map fixing `e0` and `u` and rotating `(Im a, Im b)` of `a + b u` by 120 degrees is an automorphism with defect below `2.2e-14` on random vectors at `D = 16, 32, 64`, for either rotation sense; `psi^3 = 1` and `psi` then `epsilon` equals `epsilon` then `psi^2` to `5.6e-16` |
| Lemma 1 (p. 417) | the solution space of `(x, x, v) = (v, x, x) = 0` for all basis pairs is the whole algebra at `D = 8` and exactly `span{e0, e_(D/2)}` at `D = 16` and `D = 32` |
| Theorem 3 zero divisor (p. 420) | with `x = e1`, `v_2 = e2`, `v_3 = e4` and `u = e8`: `(e3 - e10)(e5 + e12) = 0` in `D = 16` |

[I] The map `psi` is the note author's reconstruction, derived from the printed relations and the structure of the commutant of
the derivations (it commutes with every extended automorphism `theta'` because it fixes real parts and rotates imaginary
parts uniformly); the printed formula of `psi` could not be read. The `D = 16` rotation agrees in structure with the exact
`psi` of the [sedenion automorphism evidence](../../evidence/sedenion-automorphisms/README.md), whose exact computation gives
`Aut(S) = G2 x S_3` and so confirms Theorem 1 at `t = 4`. The checks at `D = 32` and `D = 64` establish only that
`Aut(A_t)` contains `Aut(A_(t-1)) x S_3` for `t = 5, 6` (the lower bound of Theorem 1); the equality `Aut(A_t) = G` at `t = 5, 6`,
which the paper only sketches, is not tested.

## Repository bearing

[I] Automorphisms. Claim `sedenion-g2-bundle` (zero-product pair space of the sedenions with bundle `SU(2) -> G2 -> V_2(R^7)`):
Brown's statement `Aut(A_4) = Aut(A_3) x S_3`, with `Aut(A_3) = G2`, is the result that the repository's exact computation reproduces
at `t = 4`; the `S_3` factor is the group `{1, psi, psi^2, epsilon, epsilon psi, epsilon psi^2}`. Algebra automorphisms
of dimensions 32 and 64 (`t = 5, 6`): the reconstruction above supplies the `S_3` elements, and the lower-level group `Aut(A_(t-1))` is the diagonal factor; the full group order and the question of further
automorphisms are open in the repository, as in [the evidence README](../../evidence/sedenion-automorphisms/README.md#wilmots-two-statements). The loop
counterpart is [Kirshtein](1102.5151.md): the sign loop `Q_n` has only the `Z_2` factor `epsilon`, because `psi` is not a signed
permutation of the basis.

[I] Zero divisors. Brown's Theorem 3 prints a zero divisor pair for this algebra family
(`(v_1 v_2 - v_2 u)(v_1 v_3 + v_3 u) = 0`); under `cd_core` it is `(e3 - e10)(e5 + e12) = 0`, an element of the 84 sedenion
zero-divisor diagonals. The paper makes no statement about annihilator dimensions, Stiefel elements, associators or
box-kites, and none about dimensions beyond `t = 6`: claims `a5-stiefel-universal`, `a6-stiefel-witness`,
`dimension32-global-topology`, `cd-associator-census`: none. Moreno's Stiefel question (`math/0512517` Section 5): none.
Dimensions 64 and above: Theorems 1 and 2 cover `t = 4, 5, 6` (16, 32 and 64 dimensions) and are conjectured beyond.

## Boundaries

[I] The Brown equality `Aut(A_t) = G` for `t = 5, 6` is the paper's sketch, not re-derived; the field-theoretic classification
(Theorem 2) and the division-algebra constructions over other fields were not checked, since `cd_core` is over the rationals
and reals. The text layer is damaged; every displayed formula that is cited was cross-checked against prose and computation.
