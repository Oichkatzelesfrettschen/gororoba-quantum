# Independent verification of the stiefel-pfaffian-higher claims

This note records an adversarial check of [README.md](README.md) and
[`scripts/stiefel_pfaffian_higher.py`](../../../scripts/stiefel_pfaffian_higher.py). The verifier code is a separate
script that builds every matrix from `cd_core.cd_multiply_exact` alone: the full basis product table of dimensions
64, 128 and 256 is read off `cd_multiply_exact(e_p, e_q)`, L_y is assembled column by column from that table, and
C_z is the e_a coefficient of z e_b in A_(n-1) from the same table. It shares no code with the producer except the
`disjoint_stiefel` constructor, used only to obtain the witness vectors, whose Stiefel conditions and ranks it then
checks itself. Modular computations use p = 4611686018427386981 (p = 1 mod 4, distinct from the producer's
2^61 - 1, which has no square root of -1), with i mapped to a fixed square root of -1 mod p. The verifier script is
not retained in the tree; its outputs are quoted below.

The producer gates were also run: `--check` exits 0 against `result.json`, and `--self-test` exits 0 in normal
and `-O` modes. `measure()` `_require`s every mathematical outcome the README calls a gate decision (C_z identities,
point rank, transport at n = 6, 7, small cofactors, f^2 cross-checks, determinant identity, slice divisibility and
valuation, the three recorded lines, witness ranks, pair and avoidance tables). `explore.json` has no gate: the
A_8 transport, the 4495 triple and 31465 quadruple slices, the isotropic-line multiplicities and the line searches
are reproduced only by running `--explore`. A fresh `--explore` replay of the current script, written outside the tree, matches every
scientific field of the retained `explore.json` (versions and timing excluded); this is a reproduction, not an
independent check, and it shows the retained file is current.

## Verdicts

| # | Claim | Verdict | Decisive independent computation | Wording the registry may use |
| --- | --- | --- | --- | --- |
| 1 | Transport phi(y x) = A(z, conj z) conj(phi(x)) in every dimension, rank_R L_y = 2 rank_C A | proved | The written derivation was re-derived line by line (doubling formula, conj(ab) = conj(b) conj(a), w' q + q w' = -2<w', q> for pure w', q); every sign agrees. Own matrix identity on every basis y and every basis x: 0 failures of 62 (A_6), 0 of 126 (A_7), 0 of 254 (A_8). Both sides are real-bilinear in (y, x), so the basis check is the identity. | "For doubly pure y in A_n, phi(y x) = A(z, conj z) conj(phi(x)), so rank_R L_y = 2 rank_C A(z, conj z); written proof for all n, integer basis check at n = 6, 7, 8 (n = 8 independent of the producer)." |
| 2 | P_j = f_n z_j, deg f_n = 2^(n-2) - 2, det L_y = N^4 \|f_n\|^4; f_4 = Q, f_5 = Q G | proved | The cofactor argument is complete: M P = 0 holds for every odd-order skew M, rank h - 2 at one point puts P in the line of z on a Zariski-open set, coprimality of z_j and z_k gives z_j \| P_j. Own check of det L_y = N^4 f(z)^2 f(conj z)^2 mod p at 6 random points of A_6, 3 of A_7, 2 of A_8 and the zero divisor e_1 + i e_2 at each n (all agree; both sides vanish at the pair). Generic rank of C_z is h - 2 at random F_p Stiefel points (30, 62, 126). f^2 = Q^2 (n = 4) and (Q G)^2 (n = 5) at random F_p points; f = Q^(2^(n-3) - 1) on S = {1, 2, 3} for n = 4..8 at random F_p points. The exact Z[z] identities f_4 = Q, f_5 = Q G are the producer's and the A_5 record's. | "On doubly pure y in A_n, det L_y = N^4 \|f_n(z)\|^4 with f_n in Z[z] homogeneous of degree 2^(n-2) - 2 defined by P_j = f_n z_j; f_4 = Q, f_5 = Q G." |
| 3 | f_6, f_7, f_8 irreducible over Q; Q does not divide f_n | proved | The producer's mod-p line argument is valid as implemented: factors of a homogeneous f are homogeneous, Gauss's lemma moves a Q-factorization to Z, `poly.degree() == 2d` enforces f(b) != 0 mod p, so both factor degrees survive restriction and reduction, and f(a + s b)^2 = c g^2 with g irreducible of degree d forces f(a + s b) = lambda g. No genericity of the line is needed. Independent and prime-free: on an own integer line z = a + s b (seeded integers in [-9, 9]), exact integer determinants of C_z without row 1, divided by z_1^2, interpolated over Q at 2d + 1 nodes and confirmed at two more, give f(a + s b)^2 in Z[s] of degree 2d with factorization over Z equal to g^2, g irreducible of degree d = 14, 30, 62, content 1. This proves irreducibility over Q at n = 6, 7, 8 on the first line tried. Q does not divide f_n: own exact ranks 64, 128, 256 of Stiefel witnesses (rows 5 and 6). | "f_n is irreducible over Q for n = 6, 7, 8 and is not divisible by Q; absolute irreducibility is open." |
| 4 | Stiefel zero-divisor set {Q = 0, f_6 = 0} is pure of complex dimension 29, real codimension 2 in the Stiefel cone, unit set dimension 57 (121, 249 at A_7, A_8) | proved | The concern that a complex dimension does not give a real dimension does not apply here: z = p + i q maps the doubly pure real space R^(2h-2) bijectively onto all of C^(h-1), so the zero-divisor Stiefel set is the full set of complex points of V(Q, f_n), not the real points of a variety. Krull's principal ideal theorem on the irreducible cone V(Q) (rank h - 1 quadric) with f_n not vanishing on it (row 3) makes V(Q, f_n) pure of complex dimension h - 3, and the complex points of a pure d-dimensional complex variety have real local dimension 2d everywhere. Real cone of dimension 2h - 6 = 58, 122, 250 minus the radial direction gives 57, 121, 249. Independent lower bound needing no Krull step but the BCDI theorem: the Stiefel cone in {z_s = 0} has real dimension 2(h - 2) - 2 = 2h - 6, and own F_p points there all have rank C_z = h - 4. The A_6 value 57 sharpens the registry's "at most 58" in `a6-stiefel-generic-invertibility`. | "The zero-divisor Stiefel elements of A_n, n = 6, 7, 8, form a real-algebraic cone of pure real dimension 2^n - 6 (codimension 2 in the Stiefel cone); on unit pairs, dimension 57, 121, 249." |
| 5a | At least two components of {Q = f_6 = 0}; the BCDI section {Q = z_16 = 0} is one | proved-with-gap | Gap: the component {Q = z_16 = 0} rests on the imported BCDI Theorem 1.5 (f_6 vanishes on that quadric). Own support: 20 random F_p points of {Q = 0, z_16 = 0} all give rank C_z = 28 (f = 0), against 30 at random Stiefel points with z_16 != 0; likewise 60 vs 62 at A_7 and 124 vs 126 at A_8. The off-hyperplane point is proved by own exact ranks: all 60 pairs e_i + i e_j with 16 in {i, j} have nullity exactly 28, z_16 != 0. | "Given BCDI Theorem 1.5, {Q = f_6 = 0} contains the component {Q = z_16 = 0} and at least one other component, through e_16 + i e_1." |
| 5b | Least support 5 at A_6: every Stiefel element with at most 4 nonzero coordinates is a zero divisor; e_12 + e_15 + e_16 + e_23 + 2 e_34 is invertible | proved-with-gap: the invertible witness is proved; the at-most-4 half rests on the exact slices of `explore.json`, which no gate covers (Monte Carlo corroborated) | Own: y_0 = y_32 = 0, \|p\|^2 = \|q\|^2 = 4, <p, q> = 0, exact integer rank 64, det L_y != 0 mod p. The at-most-4 half rests on the exact slice computations of `explore.json` (Q_S \| f_S for all 4495 triples and 31465 quadruples); the logic is sound (restriction to coordinates is a ring map, so divisibility passes to sub-supports, and a support-4 y has a support-4 z). Own Monte Carlo: two random F_p points of {Q_S = 0} per triple and per quadruple, all 4495 + 31465 subsets give rank C_z <= 28; controls: the six- and seven-coordinate slices give 30 and the slice without z_16 gives 28. Admit only after `--explore` (or a gate covering it) is replayed. | "The five-term element e_12 + e_15 + e_16 + e_23 + 2 e_34 is an invertible Stiefel element of A_6. Every Stiefel element of A_6 supported on at most four coordinates is a zero divisor (exact slice computation, ungated exploration)." |
| 6 | A_7, A_8: a disjoint-support Stiefel element has exact rank 128 and 256 | proved | Own: Stiefel conditions exact (doubly pure, defect (0, 0)), 62 and 126 nonzero coordinates, exact fmpz rank 128 and 256 from the own L_y (cross-checked against `cd_multiply_exact` on a random x), and det != 0 mod p. The avoiding-z_s variants have nullity 4 at n = 6, 7, 8. | "Moreno's question has a negative answer at A_7 and A_8: an explicit integer Stiefel element is invertible in each." |
| 7a | On the 6- and 7-coordinate slices f is in (Q, z_16^2) and not in (Q, z_16^3) | f_6 not in (Q, z_16^3): proved (lifts from the slice). f_6 in (Q, z_16^2): proved-with-gap, slices only | The producer's normal form uses lex order with a leading variable other than z_16 and Q monic in it, so the remainder is unique and membership in (Q, z_16^k) is "every remainder term divisible by z_16^k"; the logic holds. Restriction maps (Q, z_16^3) into (Q_S, z_16^3), so non-membership on a slice lifts to the full f_6; membership in (Q, z_16^2) does not lift. Own: on random F_p points of {Q_S = 0} for S = {2, 5, 14, 16, 20, 22}, f^2 equals the square of -256 (z_5 z_14^2 z_16 z_20 z_22)^2 (z_2^2 + z_5^2) at 10 of 10 points. | "f_6 does not lie in (Q, z_16^3); on two coordinate slices it lies in (Q, z_16^2). Global membership f_6 in (Q, z_16^2) is open." |
| 7b | Multiplicity of the z_s root of f on isotropic lines is exactly 2 at n = 6, 7 | f_n not in (Q, z_s^3) at n = 6, 7: proved. f_n in (Q, z_s^2): not proved (consistent evidence only) | Own isotropic lines (own construction and prime), three per n: f has full degree 14 and 30 on each line and the z_s root has multiplicity exactly 2 every time. If f_n = Q a + z_s^3 b over Z (division by the monic Q keeps a, b integral), every isotropic F_p line would show multiplicity at least 3, so one line with multiplicity 2 refutes it. Multiplicity at least 2 on three lines does not prove membership in (Q, z_s^2). | "f_n does not lie in (Q, z_s^3) for n = 6, 7 (isotropic line over F_p); f_n in (Q, z_s^2) is supported by slices and lines, not proved." |

## What the record may claim

Established, with independent confirmation: statements 1, 2 and 3 of the README; Q does not divide f_n; the
dimension statement of item 4 at n = 6, 7, 8 (the README's derivation is a proof, not an upper bound); the A_6
five-term witness and the A_7, A_8 negative answers to Moreno's question; f_6 not in (Q, z_16^3).

Established with an imported theorem: the BCDI component {Q = z_16 = 0} and hence at least two components.

Established only by an ungated computation: the at-most-four-coordinate half of the minimal-support statement.
It needs a gate or a recorded `--explore` replay before the registry calls it established.

Open: f_n in (Q, z_s^2) globally, the factorization of f_n modulo Q, absolute irreducibility, the number and real
structure of the components.

## README corrections

- The "Observed modulo p, not exact" bullet under "What the zero divisors on the Stiefel set look like" (repeated
  in the Exploration list) can add that one isotropic line with multiplicity exactly 2 already proves f_n not in
  (Q, z_s^3) at n = 6 and 7; the README lists it only as consistent evidence.

## Replay data of the independent computations

- Exact line of row 3: for n = 6, 7, 8 and t = 0, `r = random.Random(1000 n + t)`; a and b are h - 1 values
  `r.randint(-9, 9)` each (a drawn first, then b), after which a[0] = `r.randint(1, 9)` and b[0] = `r.randint(1, 9)`
  replace the first entries (z_1 > 0 on every node); nodes s = 0 .. 2d + 2; the dropped row and column is j = 1.
  Every line succeeded at t = 0.
- The Monte Carlo draws of rows 2, 4, 5 and 7 (random F_p points, isotropic points and lines) use seeded
  pseudorandom values, not QRNG draws. They corroborate and decide nothing; the decisions of rows 1, 3 and 6 and
  the exact nullities rest on exact integer computations, and the non-membership of row 7b rests on an exact F_p
  computation at an explicit line.
