# Chan and Dokovic 2006: conjugacy classes of subalgebras of the real sedenions

## Source copy and license

The [source PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/E3602D99D8C6C96F78EADAD2EDC1BC27/S0008439500006020a.pdf/div-class-title-conjugacy-classes-of-subalgebras-of-the-real-sedenions-div.pdf)
remains external to the published library. Its optional personal reading copy is
`docs/local_source_cache/chan-dokovic-2006-sedenion-subalgebras.pdf`. The article's
[landing page](https://www.cambridge.org/core/journals/canadian-mathematical-bulletin/article/conjugacy-classes-of-subalgebras-of-the-real-sedenions/E3602D99D8C6C96F78EADAD2EDC1BC27)
shows "Copyright (c) Canadian Mathematical Society 2006" and no open-license statement; the PDF footer reads "Published online
by Cambridge University Press". The inspected evidence supplies no rehosting grant, so the copy stays external.
[SOURCES.json](../../SOURCES.json) binds the source bytes, the landing-page hash and the reading scope.
Original PDF SHA-256: `c4379e7222df2bc86f14602fdfd09327317aa9fd874a6b30562c868a0dc95838`.

[P] identifies a source statement. [I] identifies a repository deduction or
proposed use. Citation and retrieval fields record bibliographic facts. Page numbers are the journal's printed pages
492 to 507.

## Citation and provenance

- Authors: Kai-Cheong Chan and Dragomir Z. Dokovic (Department of Pure Mathematics, University of Waterloo).
- Title: Conjugacy classes of subalgebras of the real sedenions.
- Venue: Canadian Mathematical Bulletin 49(4), 492-507 (2006), received 10 September 2004, revised 12 November 2004; DOI
  [10.4153/CMB-2006-048-6](https://doi.org/10.4153/CMB-2006-048-6) (Crossref record retrieved 25 October 2026). The paper
  cites Chan's 2004 Waterloo master's thesis for the quaternion subalgebras.
- PDF: 16 pages, 221,728 bytes; the first page of the PDF is the article itself, not a paywall stub.
- Reading scope: all 16 pages, including every proof except the Maple minors of Theorem 8.1 (p. 505), which were not recomputed.

## Statements and hypotheses

- [P] Setting (pp. 492-494): the real Cayley-Dickson algebra `A_n` with `x y = (x_1 y_1 - conj(y_2) x_2, y_2 x_1 + x_2 conj(y_1))`
  (Eq. 1.1); sedenion notation `i = e1, j = e2, k = e3, l = e4, e = e8`, `i j = k`, `i l = e5`, `j l = e6`, `k l = e7`, `i e = e9`,
  `j e = e10`, `(kl)e = e15`. With `zeta = (-1 + sqrt(3) e)/2`, `mu(x) = zeta x conj(zeta)` is an automorphism of order 3,
  `mu(alpha + beta e + x + y e) = alpha + beta e - (x + sqrt(3) y)/2 + ((sqrt(3) x - y)/2) e` for `x, y` pure octonions, and
  `tau(x + y e) = x - y e` has order 2; `mu` and `tau` generate `Sigma_3`. Each automorphism `sigma` of `O` extends to
  `x + y e -> sigma(x) + sigma(y) e`, and Brown's theorem (1967) gives `G = Aut(A_4) = G2 x Sigma_3`; Eakin and Sathaye proved
  Brown's conjecture for all `n >= 4`.
- [P] Main results (p. 494, abstract): proper subalgebras of `A_4` have dimension 1, 2, 3, 4, 6 or 8 (none of dimension 5, 7 or
  above 8); the proper non-division subalgebras have dimensions 3, 6 and 8, with exactly one conjugacy class in each; there
  are infinitely many conjugacy classes in dimensions 2 and 4, and exactly three classes of 8-dimensional division subalgebras
  (two of them octonion algebras, the classes of `O` and `O_(i,j,e)`).
- [P] Section 2 (pp. 495-496), Proposition 2.1: for pure `x, y`, `x` is orthogonal to `y` iff `x y = -y x`; `L_a` and `R_a` are skew-symmetric for
  pure `a`; every zero divisor is doubly pure; a sedenion `x = (x_1, x_2)` is a zero divisor iff it is doubly pure with
  `|x_1| = |x_2|` and `x_1` orthogonal to `x_2`. Proposition 2.2 (citing Khalil and Yiu): `G2` acts freely and transitively on the
  pairs `(x, y)` of unit sedenions with `x y = 0`. Examples of subalgebras: `S_3 = <1, i + le, j + (kl)e>` with `(i + le)(j + (kl)e) = 0`;
  `H`, `H_(i,e) = <1, i, e, ie>`, `S_4 = <1, i + je, l + (kl)e, il - (jl)e>` with `ab = 2c`, `bc = 2a`, `ca = 2b`; `S_6 = S_3 + S_3 e`;
  `O = H + H l`, `O_(i,j,e) = H + H e`, `R_8 = S_4 + S_4 e`, `S_8 = H + H(le)`.
- [P] Section 3 (pp. 496-499): Proposition 3.1: the subspaces of doubly pure alternative elements are `V' a` (`V'` a subspace of the pure octonions and
  `a` a unit in `C_e = <1, e>`) or `x C_e`. A ZD-subspace is a subspace of zero divisors; Proposition 3.2: it is `V'(phi) = {x + phi(x) e}` for a
  special isometry `phi` (`x` orthogonal to `phi(x)`); Proposition 3.3: the maximal dimension of a ZD-subspace is 6, attained by
  `{x + (ix) e : x in <j, k, l, il, jl, kl>}`, because there is no skew-symmetric operator on a 7-dimensional space.
  Proposition 3.4: `ker(L_z) = {(x, a(bx)) : x in O cap H_(a,b)^perp}` for a zero divisor `z = (a, b)` with `|a| = |b| = 1`;
  products of zero divisors `(a, b)(c, d) = 0` with unit entries satisfy `ab + cd = 0`; and `xy = yz = zx = 0` forces one of `x, y, z` to
  vanish. Corollaries 3.5 and 3.6: every 4-dimensional subalgebra is a division algebra and `S_6` lies in no 8-dimensional
  subalgebra. **Proposition 3.7:** for `a = r i + (s i + t j) e` with `r^2 + s^2 + t^2 = 1` and `rt != 0`, `L_a^2` has eigenvalues
  `-1` (eigenspace `O_(i,j,e)`) and `-1 +- 2rt`, whose eigenspaces `{x l -+ ((xk)l)e : x in H}` are ZD-subspaces.
- [P] Sections 4 to 6 (pp. 499-504): Lemma 4.1 and Propositions 4.2 to 4.4 exclude proper subalgebras of dimension above 8, 7 and 5; Theorem 5.1
  (pp. 501-502): with `Q(x) = |x_1|^2 - |x_2|^2 + 2(x_1 | x_2) e` in `C_e`, `Q` maps the unit sphere `S^13` of doubly pure sedenions onto the unit disk, an
  element is alternative iff `|Q(x)| = 1` and a zero divisor iff `Q(x) = 0`, and two points lie in one `G2`-orbit iff they have the same `Q`
  (so `S^13 / G2` is the disk); Proposition 5.2 gives a cross section, Corollary 5.3 the orbit space `S^13 / G` as a sector, and Propositions 6.1
  and 6.2 representatives of the conjugacy classes of 2-dimensional subalgebras and the condition `Q(u)^3` real for `a` and `-a` to be conjugate.
- [P] Sections 7 to 9 (pp. 504-507): Theorem 7.1: a 4-dimensional subalgebra is conjugate to `S_4` or to a quaternion subalgebra of
  `O_(i,j,e)`; Theorem 8.1: the non-division subalgebras are conjugate to `S_3`, `S_6` or `S_8`, and the subalgebras containing `S_3`
  are `S_3, S_6, S_8` and two conjugates of `S_8` generated by `S_3` and `k zeta` or `k zeta^2`; Proposition 9.1 and Theorem 9.3: the
  8-dimensional alternative division subalgebras are `O, mu(O), mu^2(O)`, and the three conjugacy classes of 8-dimensional
  division subalgebras are those of `O`, `O_(i,j,e)` and `R_8`.

## Convention map and cd_core check

[I] Product. Eq. 1.1 is `cd_core`'s doubling `(a,b)(c,d) = (ac - conj(d) b, d a + b conj(c))`, and the paper's basis `e_0, ..., e_15` is the
XOR-indexed basis with `e = e8`; the notation line of p. 493 reproduces exactly (`il = e5`, `jl = e6`, `kl = e7`, `ie = e9`, `(kl)e = e15`).

[I] Check results: no mismatch. A scratch script (ignored `docs/local/`, run with `-I`) tested the statements with exact rational arithmetic
where possible and double precision for the irrational `sqrt(3)`:

| Paper statement | Result under `cd_core` |
| --- | --- |
| `S_3`, `S_4`, `S_6`, `S_8`, `R_8`, `O_(i,j,e)`, `O` are closed subalgebras of dimensions 3, 4, 6, 8, 8, 8, 8 | each spans the stated dimension and is closed under multiplication |
| `(i + le)(j + (kl)e) = 0` and the `S_4` relations | `(e1 + e12)(e2 + e15) = 0`; `ab = 2c`, `bc = 2a`, `ca = 2b` for `a = e1 + e10`, `b = e4 + e15`, `c = e5 - e14` |
| `mu` and `tau` are automorphisms, `mu` of order 3, with the printed formula | automorphism defects `5.3e-15` (`mu`) and 0 (`tau`), `mu^3 = 1` to `6.7e-16`, and the formula of p. 493 holds; `mu` equals the 120-degree rotation of `(Im a, Im b)` used in [Brown](brown-1967-generalized-cayley-dickson.md) with the sense `psi(+)` |
| Theorem 5.1(b): alternative iff `\|Q\| = 1`, zero divisor iff `Q = 0` | agree on 30 of 30 random doubly pure unit vectors for both criteria, and on the constructed cases `x_1` parallel `x_2` and `e1 + e10` |
| a 6-dimensional ZD-subspace (Proposition 3.3) | `{x + (ix) e}` over `<j, k, l, il, jl, kl>` has dimension 6 and all 10 random elements have singular `L_z` |
| Proposition 3.7 for `(r, s, t) = (2/3, 1/3, 2/3)` | the spectrum of `L_a^2` is `-1` (8 times), `-1 + 2rt` (4 times) and `-1 - 2rt` (4 times) with `rt = 4/9`; `L_a^2 + 1` kills `O_(i,j,e)`; the printed eigenvectors `x l -+ ((xk)l)e` satisfy the eigen-equations |

[I] Not tested: the nonexistence statements (no proper subalgebras of dimension 5, 7 or above 8), Proposition 3.4(iii), the
classification theorems 7.1, 8.1 and 9.3 (their Maple computations and conjugacy arguments), and Proposition 5.2's cross
section. The checks cover the explicit subalgebras, the automorphism formulas and the quantitative criteria.

## Repository bearing

[I] Zero divisors, annihilators and automorphisms of the sedenions. Proposition 2.1(v) is the zero-divisor criterion `s = 0`, `A = B`,
`gamma = 0` of the repository's claim `sedenion-determinant-membership` (a nonzero `v` with `det L_v = 0`: doubly pure, equal
half norms, orthogonal halves). The kernel statement of Proposition 3.4(i) gives annihilator dimension 4 for every sedenion
zero divisor (consistent with the nullity-4 rows of the [sparse census](../topics/cayley_dickson_sparse_census.md) restricted to
dimension 16), and Theorem 5.1's `Q` is a complete `G2` invariant of doubly pure unit sedenions. Claim `sedenion-g2-bundle` (`SU(2) -> G2 -> V_2(R^7)`): Proposition 2.2 (`G2`
acting freely and transitively on unit zero-divisor pairs) is the transitivity behind the bundle structure, and `G = G2 x Sigma_3`
is the sedenion automorphism group that the repository's exact computation reproduces
([evidence](../../evidence/sedenion-automorphisms/README.md)). The paper gives the explicit formula of `mu`, the order-3 element
that [Brown](brown-1967-generalized-cayley-dickson.md) leaves unreadable in print.

[I] Box-kites and subalgebras. The 3-, 6- and 8-dimensional non-division subalgebras `S_3`, `S_6`, `S_8` and the division algebra
`R_8` give an algebra-level view of the sedenion zero-divisor structure; a map from `S_3` (which contains the zero-product pair
`(e1 + e12)(e2 + e15)`) to the 7 box-kites of [de Marrais](math-0011260.md) is not given. For dimension 32, the subloop count
of [Cawagas et al.](0907.2047.md) (the 31 sedenion-type subalgebras) is the coordinate analog; no statement of this paper
covers dimension 32. Claims `a5-stiefel-universal`, `a6-stiefel-witness` and `dimension32-global-topology`: none, because the paper
treats the sedenions only. Moreno's Stiefel question (`math/0512517` Section 5): none. Dimensions 64 and above: none.

## Boundaries

[I] Only dimension 16 is covered. The classification results rest on case analyses and Maple minors that were not rerun, and
the quaternion-subalgebra classification (deferred to Chan's thesis) is not part of the paper. The numerical checks
establish the explicit objects named in the table, not the exhaustive statements.
