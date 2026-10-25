# Stiefel elements of A_6, A_7 and A_8: Pfaffian transport, the cofactor polynomial f_n and the zero-divisor locus

`result.json` is the output of
[`scripts/stiefel_pfaffian_higher.py`](../../../scripts/stiefel_pfaffian_higher.py) `--out`, and
`explore.json` is the output of its `--explore` mode. The record extends the
[A_5 Pfaffian proof](../a5-stiefel-pfaffian-germs/README.md) to A_n for n = 6, 7, 8. It establishes four
statements and leaves a fifth open:

1. the transport rank_R L_y = 2 rank_C A(z, conj z) holds in every dimension 2^n;
2. the maximal Pfaffians of C_z factor as P_j = f_n z_j with a polynomial f_n of degree 2^(n-2) - 2, and
   det L_y = N^4 |f_n(z)|^4 on doubly pure y, for n = 6, 7, 8;
3. f_n is not divisible by Q for n = 6, 7, 8, so the A_5 mechanism (the Pfaffian vanishes on the Stiefel set) is
   absent from A_6 upward. A_6 contains a Stiefel zero divisor set that is a proper hypersurface section of the
   Stiefel quadric;
4. Moreno's question has a negative answer at A_7 and A_8 as well, and the zero-divisor Stiefel set has real
   codimension exactly 2 in the Stiefel cone at n = 6, 7, 8;
5. the exact shape of f_n modulo Q (open).

Every decision of the gate rests on an exact computation over Z, Z[z], an exact integer rank or determinant, or a
polynomial factorization over Z. The modular inputs (the f^2 cross-checks of item 6 and the irreducibility of f_n
on a line in item 7, which settles n = 7 and 8) are stated as such. No random draw enters: every point is an explicit integer vector or an arithmetic sequence. Gate
`--check` recomputes `result.json`, and `--self-test` runs the mutation controls in normal and `-O` modes.

## Conventions

The product is the cd_core doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), e_p e_q = cd_sign(dim, p, q)
e_(p XOR q). A_n has dimension 2^n; write h = 2^(n-1). An element y = (p, q) with p, q in A_(n-1) is doubly pure
when y_0 = y_h = 0. Put z = p + i q in C^(h-1), z_k = y_k + i y_(h+k), with i a scalar unit and every product of
vectors complex bilinear. Every z in C^(h-1) arises from exactly one real doubly pure y, so doubly pure elements
and points of C^(h-1) coincide as real manifolds.

- N = z . conj z = |p|^2 + |q|^2 and Q = z . z = |p|^2 - |q|^2 + 2i <p, q>. The Stiefel set (Moreno's elements)
  is {Q = 0}, an irreducible quadric cone of complex dimension h - 2 and real dimension 2h - 4.
- C_z is the (h-1) x (h-1) Im-block of left multiplication by z on Im (A_(n-1))_C; entry (a, b) is
  cd_sign(h, a XOR b, b) z_(a XOR b) for a != b. A(z, t) = [[0, -t^T], [t, C_z]] is h x h.
- s = h/2 is the index of the doubling unit of A_(n-1): s = 16, 32, 64 for n = 6, 7, 8. z_s = 0 is the
  hyperplane H^perp of [Biss, Christensen, Dugger and Isaksen](../../notes/math-0702075.md), and by their
  Theorem 1.5 every Stiefel element of H^perp is a zero divisor.
- A pair e_i + i e_j is y = e_i + e_(h+j), z = e_i + i e_j for i != j. A disjoint-support element is the integer
  Stiefel element `disjoint_stiefel` of the script: values on half of the pure coordinates and the same values,
  alternately signed and permuted by k -> r k mod m, on the other half; with `avoid` = k it leaves the coordinate
  z_k empty.

## Finite computations

Each item is an exact check in the record and states what it establishes.

1. **Left matrix** (`left_matrix_cross_checks`). L_y built from `cd_sign` equals `cd_core.cd_multiply_exact` on
   deterministic integer vectors at dimensions 64, 128 and 256.
2. **Transport** (`transport`). Phi L_y = M Phi on all 62 imaginary basis elements y of A_6 and all 126 of A_7,
   where Phi (r, s) = (r, conj s) and M is the real form of xi -> A(z, conj z) conj(xi). `--explore` repeats it for
   the 254 elements of A_8. Both sides are real-linear in y, so the identity holds on all doubly pure y. The
   self-test shows that dropping conj(s) breaks it.
3. **Cofactor identities** (`cross_matrix`, `cross_matrix_rank`, `degree_identity_*`):
   - C_z is skew and C_z z = 0 over Z[z] for n = 6, 7, 8, coefficient by coefficient;
   - at one Gaussian integer point rank_C C_z = h - 2, exact over the real form (30, 62, 126);
   - det L_y |z_j|^4 = N^4 det_R(C_z without row and column j), with det_R the determinant of the real form
     [[Re, -Im], [Im, Re]], at five points of A_6 (including two zero divisors, where both sides vanish) and at
     one Stiefel point of each of A_7 and A_8. The self-test shows that N^2 in place of N^4 fails.
4. **Small cofactor polynomials** (`small_cofactors`). Over Z[z], f_4 = Q at h = 8, f_5 = Q G at h = 16 with G =
   Q^2 - 4 (U V - W^2), and Q and G are irreducible (15 and 141 terms).
5. **Slices** (`three_coordinate_slices`, `six_coordinate_slice`, `seven_coordinate_slice`,
   `slice_without_z16`). A slice restricts f to the coordinates S, exactly over Z[z_S]; P_j / z_j is an exact
   quotient there. Results:
   - on S = {1, 2, 3}, f = Q^(2^(n-3) - 1) for n = 4, 5, 6, 7, 8 (exponents 1, 3, 7, 15, 31);
   - on S = {2, 5, 14, 16, 20, 22} of A_6, f has 792 terms, is irreducible over Q, and f = Q a + r with
     r = 256 z_5^2 z_14^4 z_16^2 z_20^2 z_22^2 (z_14^2 + z_16^2 + z_20^2 + z_22^2). Modulo Q the sum of the four
     squares equals -(z_2^2 + z_5^2), so f = -256 (z_5 z_14^2 z_16 z_20 z_22)^2 (z_2^2 + z_5^2) on Q = 0;
   - on S = {3, 4, 13, 14, 16, 22, 26}, Q does not divide f; the normal form of f modulo Q has x_16-exponent at
     least 2 in every term and exactly 2 in some term. `--explore` records the same for
     S = {3, 4, 10, 16, 21, 25, 27, 28};
   - on S = {2, 5, 14, 20, 22, 3}, which omits z_16, Q divides f.
6. **f^2 cross-checks** (`f_squared_crosschecks`). The modular route used in item 7, f^2 = det(C_z without j) /
   z_j^2 mod p, equals (Q G)^2 at two points of A_5 and the exact slice polynomial squared at a point of A_6.
7. **Irreducible lines** (`irreducible_lines`). On the arithmetic line z = a + s b of index t (t = 30 at n = 6, 52
   at n = 7, 112 at n = 8), p = 2^61 - 1, interpolating f^2 from 2d + 3 values of det(C_z without j) / z_j^2
   gives f(a + s b)^2 of degree 2d, d = 2^(n-2) - 2, and its factorization over F_p is g^2 with g irreducible of
   degree d. A factorization f = g h over Z into polynomials of positive degree would factor f(a + s b) mod p
   into two factors of positive degree, since the leading coefficient f(b) is nonzero mod p. So f_n is irreducible
   over Q for n = 6, 7, 8. At n = 6 the exact slice of item 5 proves the same without a prime.
8. **Stiefel witnesses** (`stiefel_witnesses`), all with exact integer rank of L_y:
   - the five-term element e_12 + e_15 + e_16 + e_23 + 2 e_34 of A_6 (z_12 = z_15 = z_16 = z_23 = 1, z_2 = 2i)
     has Q = 1 + 1 + 1 + 1 - 4 = 0 and rank 64;
   - the six-term element e_2 + e_5 + e_20 + e_46 + e_48 + e_54 of A_6 (z_2 = z_5 = z_20 = 1, z_14 = z_16 = z_22
     = i) has Q = 0 and rank 64;
   - the disjoint-support element has rank 64, 128 and 256 in A_6, A_7, A_8;
   - the five- and six-term index patterns in A_7 and A_8 have nullity 4 and 12 (their z_32 and z_64 vanish, so they
     lie on the BCDI hyperplane), and Moreno's Proposition 4.3 elements (e_1 + e_2, e_3 + e_4) and
     (e_1 + e_2, e_17 + e_18) of A_6 have nullity 28 (the last two are controls).
9. **Pairs** (`pair_nullities`). Exact nullity of every e_i + i e_j: 210, 930 and 3906 pairs in A_5, A_6, A_7.
   None has nullity 0. Every nullity is 4 mod 8, at most h - 4. The pairs with i = s or j = s have z_s != 0 and
   so lie outside H^perp; they all have nullity exactly h - 4 (28 pairs at A_5, 60 at A_6, 124 at A_7).
   `--explore` adds A_7 in full and A_8 (16002 pairs).
10. **Avoidance** (`avoid_nullities`). A disjoint-support Stiefel element that leaves the coordinate z_k empty has
    nullity 4 for k = s and nullity 0 for every other k, at A_6 (31 values of k) and A_7 (63 values); at A_8 for
    k in {1, 2, 64, 127}. `--explore` completes A_8 (127 values).

## Statement 1: the transport holds in every dimension

Let y = (p, q) be doubly pure in A_n and x = (r, s) in A_n, with p, q, r, s in A_(n-1), p and q pure. The doubling
product gives y x = (p r - conj(s) q, s p + q conj(r)). Put rho = conj(s), phi(x) = r + i rho and
w = r - i rho, the coefficientwise conjugate of phi(x). Since conj(s p) = -p rho and conj(q conj(r)) = -r q for pure
p and q, and rho + i r = i w,

phi(y x) = (p r - rho q) - i (p rho + r q) = p w - i w q.

For pure w' and pure q, w' q = -q w' - 2 <w', q> (the real part of w' q is -<w', q>, and conj(w' q) = q w'). The
real unit w_0 satisfies w_0 q = q w_0. With z = p + i q and t = p - i q = conj(z), the unit coordinate of
p w - i w q is -(t . w') and its pure part is t w_0 + C_z w'. That is A(z, conj z) w. So

phi(y x) = A(z, conj z) conj(phi(x)),

in every dimension 2^n. The argument uses only the doubling formula, conj(a b) = conj(b) conj(a) and the purity of p
and q. The record verifies it as an integer matrix identity on all basis elements of A_6 and A_7 (item 2), which
fixes every sign. Because phi is a real-linear bijection of R^(2h) onto C^h, rank_R L_y = 2 rank_C A(z, conj z).

## Statement 2: the cofactor polynomial f_n and the determinant identity

C_z is skew and C_z z = 0 (z z = -Q for pure z), so the vector P of signed maximal Pfaffians
P_j = (-1)^(j-1) Pf(C_z without row and column j) lies in ker C_z wherever rank_C C_z = h - 2. At the Gaussian
integer point of item 3 that rank is h - 2, so ker C_z is spanned by z there. Hence P_j z_k = P_k z_j holds on a
nonempty Zariski open subset of the irreducible space C^(h-1), so everywhere. The variables z_j and z_k are coprime,
so z_j divides P_j: P_j = f_n z_j with f_n in Z[z], homogeneous. A Pfaffian of order h - 2 with entries linear in z
has degree 2^(n-2) - 1, so deg f_n = 2^(n-2) - 2. Expanding Pf A(z, t) along its first row gives
Pf A(z, t) = -sum_j t_j P_j = -(z . t) f_n(z). Statement 1 and Pf^2 = det then give

det_R L_y = |det A|^2 = |Pf A|^4 = N^4 |f_n(z)|^4,

of degree 4 * 2 + 4 (2^(n-2) - 2) = 2^n in y. Item 3 checks the integer form of this identity at points of A_6, A_7
and A_8.

A doubly pure y != 0 has N > 0, so it is a zero divisor exactly when f_n(z) = 0. The doubly pure zero divisors are
the complex hypersurface {f_n = 0} of C^(h-1), of degree 2^(n-2) - 2.

| n | dimension | h - 1 | deg f_n | f_n | status |
| --- | --- | --- | --- | --- | --- |
| 4 | 16 | 7 | 2 | Q | exact (item 4) |
| 5 | 32 | 15 | 6 | Q G, G of degree 4 | exact (item 4), both factors irreducible |
| 6 | 64 | 31 | 14 | irreducible over Q | exact (items 5 and 7) |
| 7 | 128 | 63 | 30 | irreducible over Q | line over F_p (item 7) |
| 8 | 256 | 127 | 62 | irreducible over Q | line over F_p (item 7) |

## Statement 3: the A_5 mechanism fails from A_6 upward

At n = 5 f_5 = Q G is divisible by Q, so Pf A vanishes on the Stiefel set. At n = 6, 7, 8 it is not.

*A_6 proof.* The five-term element of item 8 satisfies Q = 0 and has rank 64, so det L_y != 0 and, by Statement 2,
f_6(z) != 0 at a point of {Q = 0}. Since Q generates a prime ideal (a quadratic form of rank 31), f_6 does not
vanish on {Q = 0}, so Q does not divide f_6. The exact slice of item 5 gives the same conclusion independently: the
normal form of f_6 modulo Q on S = {2, 5, 14, 16, 20, 22} is nonzero (four terms).

The same argument, with the disjoint-support element of rank 128 and 256, shows that Q does not divide f_7 or f_8.

**Dimension of the zero-divisor Stiefel set.** V(Q) is irreducible of complex dimension h - 2, and f_n does not
vanish on it. Every irreducible component of V(Q, f_n) is a proper closed subset, of dimension at most h - 3, and
has dimension at least h - 3 by Krull's principal ideal theorem. So the zero-divisor Stiefel cone has complex
dimension exactly h - 3, which is real dimension 2h - 6, real codimension 2 in the Stiefel cone (2h - 4). On
normalized pairs the zero-divisor set has dimension 2h - 7 = 57, 121, 249 for n = 6, 7, 8, against 2h - 5 = 59,
123, 251 for V_2(R^(h-1)). The claim a6-stiefel-generic-invertibility records the bound "at most 58" at A_6;
this gives 57 and exactness.

## Statement 4: Moreno's question at A_7 and A_8

The disjoint-support element is a Stiefel element with exact integer rank 128 in A_7 and 256 in A_8, so it is not
a zero divisor. By Statement 3 the zero-divisor Stiefel elements have real codimension 2 in the Stiefel cone at
each of n = 6, 7, 8. Among n = 5 to 8, A_5 is the only dimension where the Pfaffian vanishes on the whole Stiefel set.

**Minimal support at A_6.** A Stiefel element y with at most four nonzero basis coordinates has at most four nonzero
coordinates z_k = y_k + i y_(32+k). `explore.json` records that Q_S divides f_S for all 4495 triples and all 31465
quadruples S of coordinates (restriction to a subset keeps divisibility, so pairs and singles follow). Then f(z) = 0
on every Stiefel point supported on at most four coordinates, so every such element is a zero divisor. The
five-term element of item 8 is not, so five nonzero basis coordinates is the least support of a Stiefel element of A_6
that is not a zero divisor. The record gives no minimum at A_7 or A_8, whose five-term patterns found here lie on
the hyperplane z_(h/2) = 0.

## What the zero divisors on the Stiefel set look like

The decisive object is f_n modulo Q. The record gives the following, with different strengths.

- **Established, from the cited theorem.** BCDI Theorem 1.5 puts every Stiefel element of H^perp in the zero
  divisors, so f_n vanishes on the whole complex quadric {Q = 0, z_s = 0} (every point of C^(h-1) is a real
  element y). That quadric is irreducible of rank h - 2, so (Q, z_s) is prime and f_n lies in the ideal (Q, z_s).
  The slice computations agree: Q divides f on S without z_16, and fails to on S with it.
- **Established, off the hyperplane.** The pairs of item 9 with i = s or j = s have z_s != 0 and nullity h - 4: the
  Stiefel zero divisors include elements outside H^perp, so the BCDI slice is a proper subset of the zero-divisor
  Stiefel set.
- **Established on slices.** On the six- and seven-coordinate slices of A_6, f lies in (Q, z_16^2) and not in
  (Q, z_16^3). On the six-coordinate slice f equals -256 (z_5 z_14^2 z_16 z_20 z_22)^2 (z_2^2 + z_5^2) on Q = 0,
  a product of coordinate squares and one sum of two squares.
- **Observed modulo p, not exact.** On isotropic lines (a, b) of {Q = 0} over F_p, the root of z_s(a + s b) is a
  root of f of multiplicity 2 at n = 6 and n = 7 (`special_root_multiplicity` in `explore.json`). This is
  consistent with f = Q a + z_s^2 g for a polynomial g not divisible by z_s; it is not a proof.
- **Hyperplane specificity.** The avoidance table (item 10) shows that z_s = 0 is the only coordinate hyperplane
  z_k = 0 whose Stiefel elements are all zero divisors in the tested family: for every k != s a disjoint-support
  Stiefel element avoiding z_k is invertible.

Together: a Stiefel element of A_6 is a zero divisor exactly when f_6(z) = 0 on {Q = 0}. The set {Q = f_6 = 0}
has pure complex dimension 29. It contains the irreducible component {Q = z_16 = 0}, which has dimension 29 as well.
The pair e_16 + i e_1 is a zero divisor with z_16 != 0, so it lies on a second component. So {Q = f_6 = 0} has at
least two irreducible components over C, one of them the BCDI hyperplane section.

## Exploration

`explore.json` is not a gate. It holds:

- every one of the 4495 triples and 31465 quadruples S of coordinates of A_6 has Q_S dividing f_S (exact slices);
- all 1365 five-element subsets of {1, ..., 16} that contain 16 have Q_S dividing f_S;
- on the eight-coordinate slice {3, 4, 10, 16, 21, 25, 27, 28} (4695 terms), Q does not divide f, and the normal
  form of f modulo Q has 390 terms with x_16-exponent at least 2 and exactly 2 in some term;
- the transport identity on all 254 imaginary basis elements of A_8;
- all 3906 pairs of A_7 and 16002 pairs of A_8: no nullity 0; every nullity is 4 mod 8 and at most h - 4; the 124
  and 252 pairs through z_s have nullity 60 and 124, which is h - 4;
- the avoidance table of A_8 for all 127 coordinates: nullity 4 at k = 64 and 0 elsewhere;
- on three isotropic lines of {Q = 0} over F_p at each of n = 6 and n = 7, the root of z_s(a + s b) has
  multiplicity exactly 2 in f(a + s b);
- the first arithmetic line with f_n irreducible over F_p: t = 52 at n = 7 and t = 112 at n = 8, the values the
  gate verifies.

## Open questions

- The exact factorization of f_6 modulo Q and whether f = Q a + z_16^2 g holds with g irreducible mod Q. Not
  decided: only slices and mod-p lines support it.
- Absolute irreducibility of f_n for n = 6, 7, 8. The line argument proves irreducibility over Q only; over C the
  polynomial could split into Galois-conjugate factors.
- The components of {Q = f_n = 0} other than {Q = z_s = 0}, their number and their real structure.
- The least support of a non-zero-divisor Stiefel element at A_7 and A_8; the five- and six-term patterns of A_6
  lie on the hyperplane z_(h/2) = 0 there.
- Products of the Stiefel elements with alternative elements (for example (e_1 + e_2) times an octonion
  element), listed in the task, were not run.
- Rocq formalization: none of the statements is formalized.

## Literature

The A_5 README's [Literature](../a5-stiefel-pfaffian-germs/README.md#literature) section holds the search and the
relation to Biss, Christensen, Dugger and Isaksen (math/0702075) and Koebisu (2608.08232). No network access was
used here. This record's relation to those sources:

- BCDI Theorem 1.5 covers the hyperplane H^perp at every n, which the record uses as the input of the ideal
  inclusion above and cross-checks on slices and on the disjoint-support family.
- Koebisu's D_14 equals N |f_5|^2 on doubly pure elements (the A_5 record); the doubly pure form of det L_y at
  every n is N^4 |f_n|^4.

## Replay

```sh
"$PYTHON" -B -W error scripts/stiefel_pfaffian_higher.py --check docs/evidence/stiefel-pfaffian-higher/result.json
"$PYTHON" -B -W error scripts/stiefel_pfaffian_higher.py --self-test && "$PYTHON" -B -W error -O scripts/stiefel_pfaffian_higher.py --self-test
"$PYTHON" scripts/stiefel_pfaffian_higher.py --explore docs/evidence/stiefel-pfaffian-higher/explore.json
```

The check recomputes everything and compares the record, minus its `versions` field. It measured 5.5 s on 12 CPUs
and 9.9 s serially (`GOROROBA_WORKERS=1`) at a machine load of about 12, with python-flint 0.9.0, numpy 2.5.4 and
Python 3.14.7 (under a load of 40 to 50 it took 16 s and 30 s). The self-test measured 2.0 s in normal mode and in
`-O` mode. The exploration measured about 8 minutes at a load of 20 to 50.
