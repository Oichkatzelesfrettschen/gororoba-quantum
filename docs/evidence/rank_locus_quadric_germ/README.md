# Is the nullity-12 rank locus at the {a, 0} witnesses a quadric cone?

Yes. At the three nonzd-axis witnesses e_r + e_(24+r) (r = 1, 2, 3) and the
seven Proposition 8.2 points e_8 + e_(16+j), the germ of the closed rank cone
R_12 = {y : rank L_y <= 20} of A_5 is the cone V below. D_(5,12), the
unit-sphere section of R_12, therefore has local dimension 15 there, one less
than the tangent bound 16 of the cone.

`result.json` is written by `scripts/rank_locus_quadric_germ.py --out` and
recomputed by `--check`, which compares the complete record apart from the
library versions that wrote it. That replay is
gate core-677 and takes about 25 seconds. `--self-test` is gate core-678; in
normal and `-O` modes it rejects:
- a flipped sign of the sedenion table;
- a transport map without the conjugation of s;
- a minor combination in the place of Q, whose Hilbert value in degree 2 is
  99;
- three point controls (off V, singular on V, and x0);
- nine corrupted record fields, among them a missing key and an extra null
  field.

## The cone V

Write y = (p, q) with p, q in Im A_4, so y_0 = y_16 = 0, and set
z = p + i q = (u, mu, v) in C^7 + C + C^7, so z_k = y_k + i y_(16+k).
- i is a scalar unit.
- u = (z_1..z_7), mu = z_8 and v = (z_9..z_15).
- Every dot product is complex bilinear.

V is cut out by

    u ^ v = 0,    Q(z) = u.u + mu^2 + v.v = 0,

which is 21 complex minors and one complex quadric, or 44 real quadrics in y.

## Degree of V

Let R = C[z_1..z_15], let I be the ideal of the 21 minors and J = I + (Q).
V is a reduced, irreducible cone of complex dimension 8 and degree 14, with
Hilbert series

    H_(R/J)(t) = (1 + 7t + 6t^2) / (1 - t)^8.

1. I is the ideal of 2 x 2 minors of the 2 x 7 matrix with rows u and v.
   C[u, v]/I is the coordinate ring of the cone over the Segre embedding of
   P^1 x P^6, a Cohen-Macaulay domain of dimension 8 with series
   (1 + 6t)/(1 - t)^8. Adjoining mu gives R/I, a Cohen-Macaulay domain of
   dimension 9 with series (1 + 6t)/(1 - t)^9.
2. I is generated in degree 2, so its degree-2 part is the 21-dimensional
   span of the minors. The recorded value h(2) = 98 = 120 - 22 puts Q outside
   that span, so Q is not in I.
3. R/I is a domain, so Q is a nonzerodivisor on it. Multiplying by 1 - t^2
   gives the series above, and its numerator at t = 1 gives degree 14.
4. R/J is a hypersurface quotient of a Cohen-Macaulay ring. So it is
   Cohen-Macaulay, and J has no embedded primes.
5. V is irreducible. Every rank-one pair is (u, v) = (a w, b w), so V is the
   image of {G = 0} under (a, b, w, mu) -> (a w, mu, b w), where
   G = (a^2 + b^2) w.w + mu^2.
   - mu^2 + g is reducible only when -g is a square.
   - g = (a + i b)(a - i b) w.w has three distinct irreducible factors, each
     to the first power, so it is not a square.
   - So G is irreducible, and so is its image V.
6. J is prime. At the ten scope points the real Jacobian of the 46 equations
   has rank 16, so the complex Jacobian of the 22 generators of J has rank
   7 = 15 - 8. R/J is regular there, hence reduced at the generic point of
   V. With no embedded primes, J is prime.

The record's `hilbert` field holds h(0..5) = 1, 15, 98, 420, 1386, 3822.
Degree 2 is the step that item 2 uses; degrees 3 to 5 are consistency checks.

The real presentation has a different degree.
- Treat the coordinates y as complex variables and set
  w_k = y_k - i y_(16+k) beside z_k = y_k + i y_(16+k), an invertible linear
  change.
- Each generator f has integer coefficients, so Re f = (f(z) + f(w))/2 and
  Im f = (f(z) - f(w))/(2i).
- The 44 real quadrics therefore generate J(z) + J(w), which cuts V x V.
- Its coordinate ring is R/J tensored with itself, with series
  (1 + 7t + 6t^2)^2 / (1 - t)^16, dimension 16 and degree 196.
- The linear forms y_0 and y_16 change neither number.

## Why V lies in R_12

All of these identities hold over Z[z, t], with z and t independent, and the
record checks every entry.

1. Let C_z be the imaginary part of (L_z - R_z)/2 on Im (A_4)_C, where z is a
   complex sedenion. Then C_z is skew and C_z z = 0.
2. The matrix E(z) = C_z^2 - z z^T + Q(z) I lies in the span of the minors:
   E = sum over i < j of M_ij (u_i v_j - u_j v_i). The M_ij are constant
   integer matrices with 168 nonzero entries, each +2 or -2 (`remainder`).
3. Transport. Identify (r, s) in A_4 + A_4 with xi = r + i conj(s), where
   conj is Cayley-Dickson conjugation.
   - Under this identification, L_y sends xi to A(z, t) applied to the
     coefficientwise complex conjugate of xi.
   - Here t = p - i q and A = [[0, -t^T], [t, C_z]].
   - The record checks this on all 30 imaginary basis elements y with the
     doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) of `cd_core`.
   - It follows that rank_R L_y = 2 rank_C A.
4. Sylvester bound. On V the identity gives C_z^2 = z z^T, which has rank at
   most 1.
   - Sylvester's inequality then gives 2 rank C_z - 15 <= 1, so
     rank C_z <= 8.
   - The border row and column add at most 2, so rank A <= 10.
   - So rank L_y <= 20, and nullity L_y >= 12, at every y in V.

The cubic matrix B = a C_z + z h^T - h z^T, with a = z^T t and h = C_z t,
satisfies two identities: t^T B = 0 and C_z B = (E - Q I)(a I - t z^T). So
on V each column b of B gives two real kernel vectors of L_y,
(0, Re b; 0, Im b) and (0, -Im b; 0, Re b). These are cubic polynomials in
(p, q). At every scope point they span ker L_x (`cubic_kernel_rank` 12).

## Local dimension and germ

Each recorded point has a unit u_r. Near such a point, V is
- the graph v = lambda u over the coordinates (w = u, lambda, mu) in C^9,
- cut by F = mu^2 + (1 + lambda^2) w.w = 0.

The `chart` field records dF at each point:

| Points | lambda, mu | dF |
| --- | --- | --- |
| e_r + e_(24+r) | i, 0 | 2i dlambda |
| e_8 + e_(16+j) | 0, 1 | 2 dmu + 2i dw_j |

dF is nonzero at both kinds of point. So V is a complex 8-manifold near each
point, which is a real 16-manifold, and the real Jacobian of the 46 equations
(the 44 quadrics plus y_0 and y_16) has rank 16 there.

The rational chart below parameterizes the same germ by C^8, with q = w.w:

    lambda = i (q - tau^2) / (q + tau^2),    mu = 2 i q tau / (q + tau^2),
    tau = mu / (lambda + i).

- It solves F = 0 identically.
- It is regular at both kinds of point: at (q, tau) = (1, 0) for the
  witnesses and at (-1, -i) for the Proposition 8.2 points.

Let N_r and N_l be exact right and left kernel bases of L_x.
- The map y -> N_l^T L_y N_r is the differential at x of the Schur complement
  of a 20 x 20 pivot block. Its exact rank is 16, so the tangent bound T(x)
  has dimension 16.
- The 16 Schur entries with independent differentials therefore cut out a
  smooth 16-manifold M, as in
  [rank_locus_padic_lift](../rank_locus_padic_lift/README.md), and R_12 lies
  in M near x.
- V lies in R_12, which lies in M, and V and M are both 16-manifolds through x.
  So V is open in M, and

      (V, x) = (R_12, x) = (M, x).

- Rank is lower semicontinuous, and the nonzero 20 x 20 minor on
  `pivot_rows` x `pivot_columns` gives rank L_x = 20. So exact nullity is 12
  on V near x.
- D_(5,12) near x is therefore V on the unit sphere, of dimension 15. The
  excess Schur-complement entries vanish on M there, which settles the order
  question of `a5-schur-germ-unobstructed` at these points.

At the witnesses, e_8 and e_24 (the real and imaginary parts of mu) are
tangent to V, which matches the gap statement's extra directions. At the
Proposition 8.2 points dF has a dmu term, so e_8 and e_24 are not tangent.

| Points | Nullity | dim T(x) | Jacobian rank of V | Cubic kernel rank |
| --- | --- | --- | --- | --- |
| e_1 + e_25, e_2 + e_26, e_3 + e_27 | 12 | 16 | 16 | 12 |
| e_8 + e_(16+j), j = 1..7 | 12 | 16 | 16 | 12 |
| x0 = e_1 + e_18 (control) | 12 | 22 | 16 | 12 |
| e_1 - e_10 + e_18 + e_25 (singular, dF = 0) | 16 | 12 | 14 | 8 |

At the singular control the kernels have dimension 16, so its T(x) is the
tangent bound of the rank-16 locus {rank L_y <= 16}. Every 21 x 21 minor
vanishes to order 5 at a rank-16 point, so R_12 has no first-order constraint
there.

## x0 and the A15 family

x0 = e_1 + e_18 is a smooth point of V, but its tangent bound is 22. There
R_12 contains B17 as well, so V is only one piece of R_12 at x0
([nullity_twelve_local_geometry](../../notes/nullity_twelve_local_geometry.md)).

The record shows that the A15 family of `gororoba_quantum/nullity_twelve_curves.py`
lies in V:
- The four-parameter slice X(beta, delta, k, f) satisfies all 22 equations
  as rational functions.
- The 14 octonion derivations act as one real skew 7 x 7 block on u and on v
  and fix mu, so their flows preserve u ^ v = 0 and Q.
- The 11 orbit directions and the slice differential reconstruct the A15
  frame.
- The fixed-norm tangent of V at x0 has dimension 15 and contains that
  frame.

The A15 family, a 15-dimensional germ inside the fixed-norm section of V,
is therefore that section's germ at x0.

A path joins x0 to the witness e_1 + e_25 at exact nullity 12. With
s = sin(alpha) and c = cos(alpha), 0 <= alpha <= pi/2:

    y(alpha) = e_1 - sc e_10 + c e_18 + sc e_24 + s e_25.

- y(alpha) lies in V modulo s^2 + c^2 = 1, so nullity >= 12 along it.
- Its principal minors keep the rank at 20 or above:
  - det L_y[0..19] = 16 c^8 (1 + s^2 c^2)^2 (1 - s^2 c^2)^4, positive for
    c > 0;
  - det L_y[0..17, 24, 25] = 16 s^4 (1 + 2 c^2)^2 (1 + s^2 c^2)^2 (1 - s^2 c^2)^4,
    positive for s > 0.
- For c > 0, y(alpha) = ((1 + c)/2) X(0, 2sc/(1 + c), s, 0).
- At the endpoint, the crossing k = s reaches 1, where the slice chart has its
  denominator.

## Scope

- V lies in the closed locus R_12, not in the exact nullity-12 stratum.
  e_1 - e_10 + e_18 + e_25 lies on V with dF = 0 and nullity 16.
- The germ statements hold at the ten recorded points.
- The record leaves the nullity-8 and nullity-4 families of
  `a5-nonzero-divisor-two-dimension-gap` open, decomposes no rank locus and
  counts no components of R_12.
- The identities are checked exactly in Python over Z[z, t]. They are not
  formalized in Rocq.
