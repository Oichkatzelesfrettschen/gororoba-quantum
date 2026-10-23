# Does the Schur-complement germ at a rank-locus witness carry the whole tangent bound?

`result.json` is written by `scripts/rank_locus_padic_lift.py --out` and
recomputed by `--check` (gate core-666, about a minute with pyadic and 15
seconds without it), which compares the complete record. `--self-test` (gate
core-667) rejects corrupted orders, digits, flags, charts and controls in
normal and `-O` modes, and reads order 5 from a toy germ whose obstruction
starts there.

## The germ and its excess equations

At a witness x of nullity k with r = 32 - k, a pivot block A = L_x[R, C] is
invertible, and near x the closed rank cone R_k = {y : rank L_y <= r} is the
zero set of the k x k Schur complement
S(y) = L_y[R', C'] - L_y[R', C] A(y)^-1 L_y[R, C'].
Its differential at x has rank c = 32 - dim T(x), where T(x) is the tangent
bound of [rank_locus_local_dimension](../rank_locus_local_dimension/README.md).

- The record names c entries of S with independent differentials
  (`independent_entries`) and c coordinates on which their Jacobian minor is
  invertible (`dependent_coordinates`).
- Those c entries cut out a smooth germ M of dimension dim T(x), the graph of
  an analytic map phi over the remaining free coordinates, and R_k lies inside
  M near x.
- The other k^2 - c entries H (`excess_entries`) restrict to M as a power
  series P(u) = H(phi(u)) with rational coefficients.
- P is identically zero exactly when R_k contains M near x, which is exactly
  when D_(5,k) reaches its tangent bound dim T(x) - 1 at x. If P is not zero,
  {P = 0} is a proper analytic subset of M, and the unit local dimension is at
  most dim T(x) - 2.

The second- and third-order tests of
[rank_locus_second_order](../rank_locus_second_order/README.md) are the order-2
and order-3 parts of P. This record evaluates P exactly to far higher order
along seeded directions.

## Two exact routes

- **p-adic (pyadic 0.3.0).**
  - The free coordinates take the values x_f + p^s w in Z_p.
  - Modified Newton steps with the Jacobian inverse at x lift the dependent
    coordinates until the independent entries vanish to O(p^12).
  - The pivot block, the Jacobian minor and every coordinate of x are units or
    integers modulo p, so Hensel's lemma puts a true point of M(Z_p) within
    p^-12 of the lift.
  - H there is known exactly to O(p^12). Its valuation is s m, and its leading
    digits are P_m(w) mod p, where m is the order of P along w.
- **Series (python-flint `nmod_mat`).**
  - The same lift runs over F_p[[t]] / t^64 with y_f = x_f + t w, solved order
    by order.
  - The first nonzero coefficient of H(t) is P_m(w) mod p.

The routes share only the exact chart. The record requires the p-adic
valuation and leading digits at scale 1 to equal the series order and
coefficients, and at scale 2 to double the valuation and keep the digits.

- The primes are 2147483647 and 2147483629, the first two of `pyadic.primes`.
- Each witness gets two seeded directions per prime in the series route.
- The p-adic route lifts the first direction of the first prime.
- Every weight vector is in the record.

`--check` without pyadic recomputes the series route and holds the retained
p-adic rows to it.

## Result

| Witnesses | Role | k | dim T(x) | Independent / excess entries | Series, 4 directions | p-adic, scale 1 |
| --- | --- | --- | --- | --- | --- | --- |
| zd-axis (3) | smooth control | 16 | 12 | 20 / 236 | zero to O(t^64) | zero to O(p^12) |
| zd-zd-locus (3) | smooth control | 12 | 18 | 14 / 130 | zero to O(t^64) | zero to O(p^12) |
| zd-zd-generic (3) | smooth control | 8 | 24 | 8 / 56 | zero to O(t^64) | zero to O(p^12) |
| nonzd-axis (3) | gap | 12 | 16 | 16 / 128 | zero to O(t^64) | zero to O(p^12) |
| zd-nonzd-locus (3) | gap | 8 | 22 | 10 / 54 | zero to O(t^64) | zero to O(p^12) |
| zd-nonzd-generic (3), nonzd-nonzd-locus (3) | gap | 4 | 28 | 4 / 12 | zero to O(t^64) | zero to O(p^12) |
| Proposition 8.2 (7) | upper bound only | 12 | 16 | 16 / 128 | zero to O(t^64) | zero to O(p^12) |
| Moreno unequal norm (1) | upper bound only | 4 | 28 | 4 / 12 | zero to O(t^64) | zero to O(p^12) |
| x0 = e1 + e18 (1) | obstructed control | 12 | 22 | 10 / 134 | order 2, 32 entries | valuation 2; 4 at scale 2 |

**The controls.**
- At the zero-divisor families, the certified local dimension equals the
  tangent bound, so M is the germ there and H vanishes in both routes.
- At x0 the Bouligand cone is A15 union B17
  ([nullity_twelve_local_geometry](../../notes/nullity_twelve_local_geometry.md)),
  of dimension 17 at unit norm against the tangent bound 21.
  - H is nonzero there at order 2 in every direction.
  - At scale 2 the same 32 entries carry the same leading digits at valuation
    4, so the valuation measures the homogeneous order.
- A failed control stops the run.

**Reading.**
- At all 12 gap witnesses, P vanishes through order 63 along four seeded
  directions per witness and to O(p^12) at a lifted p-adic point.
- Any nonzero excess value would have been an exact refutation of
  `a5-nonzero-divisor-two-dimension-gap` at that witness, and none occurred.
- Vanishing admits nothing, because no finite order of vanishing makes a power
  series zero. It does bound how P could fail:
  - P would have to have order at least 64 along every drawn direction;
  - or a leading form P_m with m below 64 would have to vanish at a uniformly
    drawn w modulo p, which happens with probability at most m / p by the
    Schwartz-Zippel lemma, about 3e-8 per direction;
  - or P_m would have to vanish identically modulo p for both primes.
- An exact proof would need one of the following, and neither is available:
  - Vanishing beyond deg(M closure) times deg(H). By the Bezout bound that is
    on the order of 29^4 x 29 at nullity 4.
  - A certificate that H lies in the local ideal of the independent entries.
- The Proposition 8.2 and Moreno points carry no family dimension, and their
  rows show the same vanishing.
- `recurrence_lengths` records the Berlekamp-Massey length of each dependent
  coordinate's coefficients t^1 to t^63 along the line.
  - A constant coordinate reads 0, and a linear one reads 1.
  - Every other coordinate reads 32, the maximum for 63 terms, at every
    witness, the smooth controls included.
  - So no coordinate is a rational function of t of degree below 32, and the
    chart offers no low-degree rational parameterization of M.
