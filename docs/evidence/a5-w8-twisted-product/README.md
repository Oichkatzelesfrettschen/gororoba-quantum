# The A_5 piece W8 as a twisted product of two sedenion zero-divisor ideals

The 32-coordinate W8 closure ideal of A_5 equals J(z) + J(z') over F_32009, where J = (y_0, y_8, U - V, W) is the
sedenion zero-divisor ideal of the [W8 restriction record](../a5-w8-a4-restriction/README.md), z_k = x_k + i x_(16+k)
and z'_k = x_k - i x_(16+k). The variety of W8 is therefore the product V(J) x V(J) in the coordinates (z, z'), of
dimension 12 + 12 = 24 and degree 4 x 4 = 16, and its first Hilbert numerator is N_J(t)^2. The nullity of left
multiplication does not follow the product: n_32 = n_16(z) + n_16(z') holds on every random point of four sampled
classes and fails on 480 of the 512 mixed basis pairs e_i + s e_(16+j), where the nullity of L_x is a function of the
real nullity of e_i + s e_j. Ledger rows A5-223 (twisted product), A5-224 (sum rule) and A5-225 (joint nullity law).

`a5_w8_twisted_product.py` builds every input from the strata record's code, runs Singular and writes `result.json`;
`driver_*.sing` and `ideal_*.sing` are the Singular inputs, `log_*.txt` the Singular outputs with the
`/usr/bin/time -v` accounting.

## Conventions

The product is the cd_core doubling, e_p e_q = cd_sign(dim, p, q) e_(p XOR q), and L_x is
`cd_core.left_mult_matrix_exact(32, x)`; every nullity is `dim - rank L_x`. Over F_p with i^2 = -1 the forms z_k, z'_k
(k = 0..15) are 32 independent linear forms, so (z, z') is a linear change of coordinates. In F_32009 the script uses
i = 10754 = 3^((p-1)/4) mod p; 32003 = 3 mod 4 holds no i. The u, mu, v, U, V, W
notation is that of the W8 restriction record: u = z_1..z_7, mu = z_8, v = z_9..z_15, U = u.u, V = v.v, W = u.v.

## Method

**Twisted product.** `a5_w8_a4_restriction.w8_ideal_32` builds the W8 ideal in x_0..x_31 from the strata record's own
`GP` arithmetic: the real and imaginary parts of mu, U - V and W, with x_0 and x_16 (8 generators), and its
`w8_crosscheck` compares the original-coordinate generators with the record's `piece_ideals` W8 at 40 integer points
(120 comparisons agree up to a unit; the result records the pass). `ideal_J.sing` is that ideal restricted to
x_16..x_31 = 0 and equals the neighbor record's `ideal_J.sing` byte for byte. Singular maps y_k to x_k + i x_(16+k) and
to x_k - i x_(16+k) in `driver_32009.sing`, adds the two images of J, and decides both containments by reduction modulo
a standard basis (`option(redSB)`, global degree-reverse-lexicographic order). The identity also follows by hand:
for f with rational coefficients, Re f(z) = (f(z) + f(z'))/2 and Im f(z) = (f(z) - f(z'))/(2 i), so the real and
imaginary parts of the generators of W8 and the generators of J(z) + J(z') generate the same ideal whenever 2 and i are
units, and the numerator N_J^2 follows because z and z' are independent variables. At p = 32003 `driver_32003.sing`
computes the Hilbert data of the same integer generators with no i. The real slice x_16..x_31 = 0 sets z = z'
and `driver_32009.sing` compares W8 + (x_16..x_31) with J + (x_16..x_31).

**Controls.** `driver_controls.sing` repeats the containment test with a flipped sign of i in one coordinate (y_3 of
the second change of variables), with every sign flipped (z and z' swap), with W8 built from U + V in place of U - V
(`w8_sign`) and with W8 built without x_0 = x_16 = 0 (`w8_no_pure`). `--self-test` runs the same controls in a
temporary directory and adds the linear-algebra controls (below).

**Nullity spectrum.** For the 512 pairs (i, j, s) the script computes n_32(x) for x = e_i + s e_(16+j), n_16(z) and
n_16(z') for z = x_low + i x_high and z' = x_low - i x_high, and the real nullity n_16(e_i + s e_j), by Gauss-Jordan
rank over F_32009 of `left_matrix`, which is cd_core.cd_sign placed as L_x[k XOR c, c] += x_k cd_sign(dim, k, c). The
ranks of the real matrices over Q, from `left_mult_matrix_exact` and python-flint, agree with the ranks modulo p on all
512 pairs. Membership of x in W8 and of z, z' in V(J) is evaluated from the generators.

**Random points.** `numpy.random.default_rng([48732, 12744])` takes values 0 and 1 of
[the ANU draw of 2026-11-08T170257Z](../anu_qrng/draw-2026-11-08T170257Z.json) (`W8_SAMPLE_SEEDS`, ledger rows in
`docs/evidence/qrng_seeds/allocations.json`; the script re-reads the draw and raises on a mismatch). A point of V(J) is
u uniform in F_p^7 with nonzero norm, v in the perpendicular plane with v.v = u.u (a square root of the discriminant
by table) so that U = V and W = 0. Four classes: W8 (z, z' independent points of V(J)), diag (z' = z, the real
slice), offW8 (z on V(J), z' uniform) and generic (z, z' uniform); x_low = (z + z')/2 and x_high = (z - z')/(2 i).
The first ten draws of the stream (6 W8, 2 diag, 2 offW8) reproduce the orchestrator's recorded sample; a second
stream from the same seed then draws 200 points per class in the order W8, diag, offW8, generic, every input before any
rank, and the ranks run through `parallel.ordered_map`.

## Results

**Twisted product** (p = 32009, Singular 4.4.1).

| Quantity | Result |
|---|---|
| W8 in J(z) + J(z') and J(z) + J(z') in W8 | both 1; the reduced standard bases are identical |
| dimension, degree | 24, 16 |
| first Hilbert numerator over (1 - t)^32 | 1, -4, 2, 12, -17, -8, 28, -8, -17, 12, 2, -4, 1 = N_J^2 (N_J = 1, -2, -1, 4, -1, -2, 1) |
| second Hilbert series | 1, 4, 6, 4, 1 (the same for J(z) + J(z')) |
| p = 32003, Hilbert series only | dimension 24, degree 16, the same numerator |
| real slice x_16..x_31 = 0 | W8 + slice = J + slice (identical reduced bases), dimension 12, degree 4; J(z) + slice and J(z') + slice equal J + slice |

The real slice is the diagonal z = z' and gives J, as the W8 restriction record finds (ledger row A5-222).

| Control | W8 in T | T in W8 | Reading |
|---|---:|---:|---|
| unmutated | 1 | 1 | equality |
| one sign of i flipped (y_3, second map) | 0 | 0 | equality breaks |
| every sign flipped (z and z' swap) | 1 | 1 | equality persists: swapping the factors is a symmetry |
| W8 built from U + V | 0 | 0 | equality breaks |
| W8 built without x_0 = x_16 = 0 | 1 | 0 | W8 is a proper subideal |

**Nullity spectrum** (512 mixed basis pairs). Cells (n_32, n_16(z), n_16(z')):

| Cell | Pairs | n_32 = n_16(z) + n_16(z') |
|---|---:|---|
| (0, 0, 0) | 32 | holds |
| (0, 8, 8) | 60 | fails (0 against 16) |
| (4, 4, 4) | 168 | fails (4 against 8) |
| (12, 8, 8) | 252 | fails (12 against 16) |

The sum rule holds on 32 pairs and fails on 480. Joint law with the real nullity n_16(e_i + s e_j), by pair class
(each class lists (n_32, n_16(z), n_16(z'), real nullity): count):

| Pair class | Pairs | Joint law |
|---|---:|---|
| i, j >= 1, i != j | 420 | (4, 4, 4, 4): 168; (12, 8, 8, 0): 252 |
| i = 0, j >= 1 | 30 | (0, 8, 8, 0): 30 |
| j = 0, i >= 1 | 30 | (0, 8, 8, 0): 30 |
| i = j >= 1 | 30 | (0, 0, 0, 0): 15 (s = +1); (0, 0, 0, 16): 15 (s = -1, the zero vector) |
| i = j = 0 | 2 | (0, 0, 0, 0): 1; (0, 0, 0, 16): 1 |

- n_16(z) = n_16(z') on all 512 pairs.
- On the 420 pairs with i, j >= 1 and i != j, n_32 = 12 - 2 n_16(e_i + s e_j) and n_16(z) = n_16(z') = 8 - n_16(e_i + s e_j).
  The real nullity takes the value 4 on 168 pairs (the real zero-divisors) and 0 on 252.
- The 92 remaining pairs, i = 0 or j = 0 or i = j, have n_32 = 0 and fall outside the rule: the real nullity is 0 for
  e_0 + s e_j and e_i + e_i, and 16 for e_i - e_i = 0. The mixed rule needs the exception set {i = 0} union {j = 0}
  union {i = j}; the briefed exception (j = 0 or j = i) omits the 30 pairs with i = 0, j >= 1, where z = e_0 + i s e_j
  is a zero-divisor of nullity 8 and n_32 = 0 against 12 - 2 x 0 = 12.
- With W8 membership: the 168 pairs of the cell (12, 8, 8) with x on W8 have z, z' in V(J), where n_16 jumps from the
  generic 4 to 8 and n_32 from the generic 8 to 12; the other 84 pairs of that cell lie off W8. The 168 pairs of
  the cell (4, 4, 4) lie off W8 (z is not in V(J)).

**Random points** (200 per class, one stream per seed).

| Class | Points | (n_32, n_16(z), n_16(z')) | Sum rule holds / fails | x on W8 |
|---|---:|---|---|---:|
| W8 | 200 | (8, 4, 4) x 200 | 200 / 0 | 200 |
| diag | 200 | (8, 4, 4) x 200 | 200 / 0 | 200 |
| offW8 | 200 | (4, 4, 0) x 200 | 200 / 0 | 0 |
| generic | 200 | (0, 0, 0) x 200 | 200 / 0 | 0 |

The ten-point sample reproduces the recorded rows ((8, 4, 4) on the six W8 and two diag points, (4, 4, 0) on the two
offW8 points; the sum rule holds on all ten). The sum rule holds on every random point of every class and fails only at
the special points of the basis-pair table, where z and z' lie on loci of higher nullity than the generic point of
their class. Random points sample the generic nullity of each class, so they carry no information on the pairs where
the rule fails.

## Cost

One `--out` run takes 1.7 s wall and 58 MiB peak resident set for the driving process (`/usr/bin/time -v`); the three
Singular runs take at most 0.06 s wall and 15 MiB peak resident set each (the logs hold the figures of the retained
run), under an 8 GiB cgroup cap. Versions
are in `result.json` (`versions`): Python, numpy 2.5.4, python-flint 0.9.0, Singular 4.4.1.

## Commands

```sh
export PYTHON="${PYTHON:-python3}" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" -B -W error docs/evidence/a5-w8-twisted-product/a5_w8_twisted_product.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-w8-twisted-product/a5_w8_twisted_product.py \
    --out docs/evidence/a5-w8-twisted-product
```

`--self-test` checks `left_matrix` against cd_core at dimensions 16 and 32, `rank_mod` on known ranks, the square-root
table against a brute-force search, a sampled W8 point against every W8 generator, a moved point that leaves V(J) with
a lower nullity, the mixed pair e_0 + e_17 in the cell (0, 8, 8), and the Singular mutation controls.

## Falsifiers

- A change of the strata record's W8 generators (`w8_crosscheck` fails) or of `cd_core.cd_sign` retires the identity
  and the tables; the controls fail first.
- A point of V(J(z) + J(z')) outside V(W8), or the reverse, overturns the twisted product; the linear argument holds
  whenever 2 and i are units, so a counterexample would show an error in the generator construction.
- Characteristic 0 is not run: the identity over Q(i) follows from the argument and the Hilbert series at p = 32009
  and 32003, and no Singular computation over Q(i) exists in this record.
- The sum rule is refuted on the basis pairs. A random-point class on which it fails would show that the classes
  sampled here miss a locus; the points of the basis-pair table are such loci.
- The mixed law n_32 = 12 - 2 n_16(e_i + s e_j) is verified on the 420 basis pairs only. A mixed point off the basis
  pairs, for instance e_i + t e_(16+j) with t outside +-1 or a sum of three basis vectors, that violates the law, or a
  random point on a locus other than the four classes, decides the law off the basis pairs; no such point has been run.
- Statements about the nullity of L_x at the special points rest on ranks modulo 32009 with the exact ranks over Q
  agreeing for the real matrices; the ranks of L_z and L_z' over F_32009 have no Q counterpart.
