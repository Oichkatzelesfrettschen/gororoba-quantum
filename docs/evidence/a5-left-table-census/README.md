# A_n left tables: commutant, associator census and Euclidean-cone points

The items of pool row MATH-71 and the reduction of pool row MATH-73, each computed exactly by
[`scripts/a5_left_table_census.py`](../../../scripts/a5_left_table_census.py). Ledger rows A5-633 to A5-636.

## Statements, each checked by `--check`

1. **Commutant.** For n = 3 to 10 (dimension 8 to 1024), the only matrices that commute with every left table L_a of
   the Cayley-Dickson algebra A_n are the scalars. The commutant has dimension 2 for n = 1 and 4 for n = 2: the
   right multiplications of C and H. Each entry links X[p, q] to X[a ^ p, a ^ q] with the sign
   s(a, a ^ q) s(a, a ^ p), so each difference d = p ^ q spans one orbit of the entries. An orbit adds one dimension
   exactly when its signs are consistent. From n = 3 on, only d = 0 is consistent. The rank of the linear system
   X L_a - L_a X = 0 modulo 32003 gives the same dimensions for n = 1 to 4.
2. **Envelope.** For n = 3 to 10, the left tables generate the full matrix algebra M_(2^n)(Q). The span of the L_a is
   closed under transposition (L_0 = I and L_a^T = -L_a for a != 0), so its associative envelope is semisimple: a nilpotent ideal holding x
   would hold the nilpotent positive semidefinite x x^T, which is 0. Commutant Q then makes Q^(2^n) one irreducible
   module whose endomorphisms are Q, and Wedderburn's theorem gives End_Q(Q^(2^n)). Zhou and Zhou 2026 (Zenodo
   10.5281/zenodo.23966060; abstract and introduction read on the page) prove Env_L(A_n) = M_(2^n)(F_p) for odd p and
   every n >= 3, with the doubling (a, b)(c, d) = (ac - d* b, da + b c*) of cd_core. The words in the L_a are integer
   matrices, and the rank of their span over Q is at least its rank over F_p, so their theorem gives the Q statement
   for every n >= 3. This record reaches it by another route (the commutant by sign cocycle, then semisimplicity) and
   checks n = 3 to 10 independently of their proof, a preprint without peer review. The earlier record's dimension 256
   at A_5 refers to the seven slice tables, not to all 32.
3. **Associator census.** The number of ordered triples (a, b, c) of imaginary basis units with
   [e_a, e_b, e_c] != 0 equals (D - 2)(D - 4)(D + 6)/2 for D = 4 to 1024: 0, 168, 1848, 15960, 130200, 1046808,
   8385048, 67101720, 536856600. The associator of basis units is
   (s(a, b) s(a ^ b, c) - s(b, c) s(a, b ^ c)) e_(a ^ b ^ c).

   **Proof for every D (A5-649).** Theorem 1 of [cd_associator_defect_census.md](../../notes/topics/cd_associator_defect_census.md)
   (2026-10-22) proves the formula for every D: its associator-lifting Lemma 3, summed over the eight top-bit choices,
   leaves the rank-at-most-1 triples alone. A5-634 called the proof open because the searches of 2026-11-26 looked
   outside the repository. A second derivation runs through Albuquerque and Majid, whose Corollary 4.3 and
   Proposition 4.5 are the published forms of that note's sign lifting (Lemma 2) and associator lifting (Lemma 3).
   Write G = Z_2^n with D = 2^n, and phi(a, b, c) = s(a, b) s(a ^ b, c) s(b, c) s(a, b ^ c), which is -1 exactly when
   the associator is nonzero.
   - *The cochain.* s(p, q) = F(q, p), where F = (-1)^f is the cochain of the standard Cayley-Dickson process of
     Albuquerque and Majid (arXiv math/9802116, Corollary 4.3, page 18). Peeling the top bit, the four branches of
     `cd_core.cd_sign` are the four cases of their recursion with the arguments exchanged, given F(y, y) = -1 for y != 0
     (their Proposition 4.2, page 17). So A_n is the opposite of their algebra k_F G, its phi(a, b, c) is theirs at
     (c, b, a), and the count is the same for both (A5-648).
   - *The doubling.* Their Proposition 4.5 (page 20) writes the cocycle of the doubled group through phi and
     R(x, y) = F(x, y)/F(y, x) on G, for x, y, z in G and the new generator v: phi(x, y, z); R(y, z) phi at (vx, y, z);
     R(y, z) R(xy, z) phi at (x, vy, z); R(x, y) phi at (x, y, vz); R(xy, z) phi at (vx, vy, z); R(y, z) R(x, y) phi at
     (vx, y, vz); R(x, yz) phi at (x, vy, vz); R(xy, z) R(x, y) phi at (vx, vy, vz). Distinct imaginary units
     anticommute, so R(x, y) = -1 exactly when x and y are nonzero and distinct.
   - *Degenerate triples.* phi = 1 outside Gamma = {(x, y, z): x, y nonzero, x != y, z not in {0, x, y, x ^ y}}. A triple
     of the doubled group outside its Gamma projects to a triple of G outside Gamma, where phi = 1 by induction, so its
     cocycle is the R product of its case. That product depends only on which sums of x, y, z vanish, and every such
     pattern occurs in Z_2^3, so the tables at D = 8 and D = 16 (phi = 1 off Gamma at both, hence every R product
     of the doubling equal to 1; `tests/scripts/test_cd_sign_quasialgebra.py`) settle every n; D = 2 and 4 are
     associative.
   - *The count.* On Gamma every R factor is -1: the cases (x, y, z), (x, vy, z), (vx, y, vz) and (vx, vy, vz) keep phi
     and the other four negate it, giving 4N + 4(|Gamma| - N) = 4(D - 1)(D - 2)(D - 4). Off Gamma phi = 1 and the case
     (x, y, z) adds none. Each one-factor case adds 4(D - 1)(D - 2): for R(y, z), the pairs y, z nonzero and distinct
     with x in {0, y, z, y ^ z}, and likewise for R(x, y), R(xy, z) and R(x, yz). Each two-factor case counts the
     triples where exactly one factor is -1, also 4(D - 1)(D - 2): fixing the shared element w (z, y or xy), each factor
     is -1 for D - 2 values of its other argument. So N(2D) = 4(D - 1)(D - 2)(D - 4) + 28(D - 1)(D - 2)
     = 4(D - 1)(D - 2)(D + 3) = (2D - 2)(2D - 4)(2D + 6)/2, and N(4) = 0 gives the formula for every D >= 4.
4. **Euclidean cone over number fields.** L_y has nullity 12 at 10 points y = x + t e_26 with r^2 + t^2 = 0:
   - over Q(sqrt(-d)) for d = 1, 2, 3, 5, 6, 7, 11, with t = s sqrt(-d) and sum x_a^2 = d s^2;
   - the four Q(i) points add to the three of the [associator envelope](../a5-null-slice-associator-envelope/README.md).

   Each nullity is half the nullity of the rational 64 x 64 form [[A, -d s J], [s J, A]]. Two points with
   sum x_a^2 != d have nullity 0.
5. **Euclidean cone over Q_p.** At 10 points of Z_p with t^2 = -r^2 (p = 5, 11, 13, 17, 29, 37, 41 twice, 43, 61), the
   reduction mod p has nullity 12. Hensel's lemma lifts the root t, since p is odd and -r^2 is a nonzero square mod p.
   A nonzero 20 x 20 minor of the reduction is a unit of Z_p, so the nullity over Q_p is at most 12. The bound
   nullity >= 12 holds in characteristic 0 (A5-623), so the nullity is exactly 12. The primes 5, 11, 13, 17 and 29 lie
   below the bound 32 of A5-623 and still give 12 at these points.

6. **Commutation-set lemma of the two so(m,1) families.** For the slices of A5-618 (time 7 * 2^(n-3) with space
   [1, 2^(n-2)) without 2^(n-3), for n = 4 to 12; time 2^(n-1) + 2^(n-2) + 8 with space 1 to 7, for n = 6 to 12),
   L_a and L_tau commute on e_k exactly for k in T or T ^ a ^ tau, for every space index a. Here
   T = {u, v, tau ^ u, tau ^ v}, with (u, v) = (2^(n-3), 2^(n-2)) in the first family and (8, 2^(n-2)) in the second.

   **The lemma gives disjoint stars for every n (proved).** Both terms of K_a = -(L_a L_tau + L_tau L_a)/2 send e_k
   to plus or minus e_(k ^ a ^ tau). So K_a is a symmetric signed partial XOR permutation whose support is the set
   C_a where L_a and L_tau commute on e_k.

   If C_a = T u (T ^ a ^ tau), then the leaves T ^ a ^ tau of a and b meet only when a ^ b lies in
   T + T = {0, u ^ v, tau, tau ^ u ^ v}, and a leaf meets T only when a ^ tau lies in T + T:
   - First family: T + T = {0, 3h, 7h, 4h} with h = 2^(n-3), while a ^ b < 2h and a < 2h.
   - Second family: T + T = {0, 8 + 2^(n-2), tau, 2^(n-1)}, while a and b lie in 1 to 7.

   Neither event can occur, so the stars are disjoint. The sufficient direction of A5-617 then gives the so(m,1)
   relations. The families of A5-618 therefore hold at every n where the lemma holds.

   **The lemma for every n** is proved in the [family proof](../a5-null-slice-family-proof/README.md) (MATH-73). That
   proof peels the top bit of the cd_sign recursion: for k below the top bit the commutation sign at level n is minus
   the sign at level n - 1 with time tau' = tau - 2^(n-1), except on {0, a, tau', tau' ^ a} (Lemma R).

## Predictions

Before the run, a reviewer had computed (not recorded) the commutant for n = 3 to 7 and the triple formula for D = 8
to 64 (review record of the associator envelope, row 10). The predictions were that both extend to 1024 and that
every cone point has nullity 12. All held.

## Controls

`--self-test` runs five paired controls:

| Control | Baseline | Mutant |
|---|---|---|
| orbit cocycle | equals the direct system at D = 8 | dropping the factor s(a, a) does not |
| associator predicate | 1848 at D = 16 | the wrong index in s(a, b ^ c) does not |
| field form | Q(sqrt(-2)) point gives 12 | the Q(i) form at the same x does not |
| local root | t mod 17 gives 12 | t + 1 does not |
| common support | the lemma holds at n = 5 | moving u by one fails |

## Open

- A proof of statement 1 for every n (statements 3 and 6 are proved; see above and the family proof). The lower-half orbits (d < 2^n) of A_(n+1) contain the constraint graph
  of A_n, so their inconsistency is inherited; the orbits with d >= 2^n need their own argument; Zhou and Zhou's theorem covers
  statement 1 for every n if it holds. Targeted searches on 2026-11-26 for the triple formula, arXiv
  `all:"Cayley-Dickson" AND all:associator AND all:basis`, `all:"Cayley-Dickson" AND all:triples AND all:associative`
  and `all:sedenion AND all:associator AND all:count`, and zbMATH documents `Cayley-Dickson associator basis`, found
  Wilmot 2025 (arXiv 2505.11747), which classifies the associativity of basis triples in a graded notation; they
  missed the repository's own proof (statement 3). Its abstract
  states no count, and its text was not read.
- Equality on the Euclidean cone at every point over every field of characteristic 0 (the bound is proved; equality
  is checked at points).

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_left_table_census.py --check docs/evidence/a5-left-table-census/result.json
"$PYTHON" -B -W error scripts/a5_left_table_census.py --self-test
```

Gates `core-a5-left-table-census` and `core-a5-left-table-census-self-test` run both.
