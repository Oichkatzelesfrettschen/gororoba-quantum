# The two-dimension gap of the A_5 rank loci and the route to item 3

The local-dimension certificate
([evidence](../evidence/rank_locus_local_dimension/README.md),
`scripts/rank_locus_local_dimension.py`) closes every family of D_(5,k)
whose entries are both zero divisors and leaves each family with a
non-zero-divisor entry exactly 2 below its tangent bound:

| Family | Nullity | Family dimension | Tangent bound |
| --- | --- | --- | --- |
| {a, 0}, a not a zero divisor | 12 | 13 | 15 |
| a zero divisor, b in W(a) | 8 | 19 | 21 |
| a zero divisor, b not, off the locus | 4 | 25 | 27 |
| neither, C-orthogonal | 4 | 25 | 27 |

The open question is which side moves: either D_(5,k) carries two more
dimensions at these witnesses (the conjecture in the evidence README: the
extra directions leave H_5^perp through e_8 and e_24 and curve, since the
straight lines drop to nullity 0), or a second-order obstruction kills both
tangent directions and the local dimension equals the family dimension.
The question is classical and exact; it needs no QPU and no Tuna run.
Computation 7 settles the {a, 0} row: at its witnesses D_(5,12) has local
dimension 15, the tangent bound, with e_8 and e_24 tangent.

## The lead from the nullity-twelve cone

At x0 = e1 + e18 the nullity-12 locus has Bouligand cone A15 union B17
([note](nullity_twelve_local_geometry.md),
`gororoba_quantum/nullity_twelve_locus.py`). B17 is the
Biss-Christensen-Dugger-Isaksen D-locus bundle with its length ratio, the
certified 17-dimensional family. A15 is realized by actual curves (a
four-parameter rational slice and octonion derivation flows) and contains
the direction e8, so it leaves H_5^perp. A 15-dimensional nullity-12 piece
that exits through e8 has exactly the shape the conjecture predicts for the
{a, 0} family, whose tangent bound is also 15. The Schur machinery that
decided the cone at x0 (centered chart, `D(a) = -2 Q(h)`, the polarized
coefficient matrix G and its sum-of-squares reduction) runs unchanged at
any center whose kernel frame is exact.

## Design: three exact computations, cheapest first

The certificate's T(x) = {y : U^T L_y V = 0} is tangent to the cone S_k
and contains x, and the tangent bound is dim T(x) - 1 for the unit locus.
Every computation below therefore works in T_1(x) = T(x) intersected with x^perp, compares
against the unit family's tangent space T_F, a subspace of x^perp, and carries the norm
row <x, y> = 0 in its equations; the radial direction x is rank-preserving
and is never evidence of the gap.

1. **Locate the extra directions.** At each certified witness, complete
   T_F to T_1(x) and record the 2-dimensional complement in coordinates.
   Prediction: its projection onto span{e_8, e_24} has rank 2 at every
   non-zero-divisor witness. Falsifier: rank below 2 at any witness refutes
   the "leaves through e_8 and e_24" part of the conjecture while leaving
   the dimension question open.

   **Outcome.** The prediction holds at all 12 witnesses
   ([evidence](../evidence/rank_locus_gap_directions/README.md),
   `scripts/rank_locus_gap_directions.py`, gate `core-record-check-03` (`tests/test_cli_record_checks.py`) and gate `core-self-test-04` (`tests/test_cli_self_tests.py`)).
   - T_F is built from exact curve velocities inside each family:
     octonion-derivation flows, scalings, fiber lines and projection
     curves.
   - It is pinned from above by the kernel of each family's defining
     equations, and its dimension equals the family dimension.
   - The induced map T_1(x)/T_F -> span{e_8, e_24} has rank 2.
   - The result is sharper than predicted:
     T_1(x) = T_F (+) span{e_8, e_24}, an orthogonal sum.
   - So e_8 and e_24 are themselves the first-order exit directions, and no
     first-order direction touches e_0 or e_16.
   - T_1(x) intersected with H_5^perp equals T_F. So D_(5,k) intersected
     with H_5^perp has local dimension exactly the family dimension at
     every witness, and any excess must leave H_5^perp.
   - The question stays first order. Computation 2 now runs over
     T_1(x) = T_F (+) span{e_8, e_24}, with the e_8 and e_24 coefficients
     as the transverse variables.
2. **Second-order compatibility with the family variables kept.** Run the
   centered Schur construction of `nullity_twelve_locus.py` at the
   nullity-12 witnesses {a, 0} (then the nullity-8 and nullity-4
   witnesses): `Dmap`, its nullspace K over all of T(x), the obstruction
   space C and the quadratic system `C^T upper_triangle(Q(K z)) = 0`, with
   K spanning the kernel inside T_1(x). The system is quadratic, so a mixed vector `t + z` with `t` tangent to the
   family and `z` transverse can satisfy it through cross terms while every
   pure transverse vector fails; restricting to a complement decides
   nothing. The computation keeps every variable and decides whether the
   real zero set V lies inside the family's tangent space T_F, by the route
   that settled x0: reduce the generators, find the sum-of-squares identities
   that split V into linear pieces, and compare each piece with T_F.
   - V inside T_F: every second-order compatible velocity, hence the
     tangent cone, lies in T_F, so the local dimension equals the family
     dimension and the conjecture is refuted at that nullity. The
     certificate is the generator reduction plus the identities that place
     every real solution in T_F.
   - A real solution with nonzero component outside T_F: the solution
     names a candidate direction and raises nothing by itself. Curves
     through x with transverse velocities form a union of one-dimensional
     germs, whose velocity span bounds no local dimension from below. The
     local dimension rises to m only through a certified m-dimensional
     piece of D_(5,k) through x: an explicit parameterization (a rational
     slice as for A15, or an exact flow family) whose nullity holds exactly
     on an open set of parameters and whose differential has rank m at x,
     or a proof that the tangent cone contains a semialgebraic subset of
     dimension m.

   **Outcome.** The test is vacuous at all 12 witnesses
   ([evidence](../evidence/rank_locus_second_order/README.md),
   `scripts/rank_locus_second_order.py`, gates core-553 and core-554).
   - The projected quadratic map Q(v) = N^T vec(U^T L_v G L_v V) has an
     identically zero coefficient matrix on T_1(x) in the variables
     (tau, s, t). So its zero set is T_1(x), and every first-order
     velocity, e_8 and e_24 alone included, is formally second-order
     compatible: Outcome B in its degenerate form.
   - Q vanishes on T(x), so the order-3 condition does not depend on the
     choice of acceleration. Its cubic is also identically zero on T_1(x):
     every first-order velocity is formally compatible through order 3.
   - At the nonzd-axis and nonzd-nonzd-locus witnesses, rotating one half of
     x = (p, q) toward that half's e_8 is an exact polynomial curve of
     D_(5,k), with velocity e_8 or e_24. Its nullity is proved from ranks at
     interpolation nodes. So both directions lie in the tangent cone there.
   - At the zd-nonzd witnesses both rotations leave the locus, and no
     transverse curve is known.
   - The construction reproduces the eight canonical quadrics at e1 + e18.
     At every witness, an exact curve with a nonzero order-2 target and a
     nonzero triple term fixes the signs of the order-2 and order-3
     equations.
   - Neither the conjecture (B with curves) nor its alternative (A)
     predicted a vacuous test. Second- and third-order compatibility decide
     nothing here. The question moves to a certified m-dimensional piece
     through x, or to higher order.
   - The A branch above overstates its consequence. A tangent cone inside
     T_F bounds no local dimension of a real algebraic set: the surface
     y^2 + z^2 = x^4 has local dimension 2 at 0 and tangent cone the x-axis.
     An upper bound below dim T_1(x) needs equations that cut out D_(5,k)
     near x, not its tangent cone.
3. **Relate A15 to the {a, 0} family.** The second-order test leaves the
   {a, 0} dimension open, so this computation, or a certified piece of
   dimension 14 or 15 through an {a, 0} witness, now carries the
   nullity-12 question. Closure is decided exactly or not
   at all. A positive answer is an explicit curve or parameterization of
   nullity-12 points, certified exactly along its parameter, whose limit is
   an {a, 0} witness with a not a zero divisor. A negative answer is a
   semialgebraic elimination showing that the A15-type piece and the {a, 0}
   family meet in no common component near such a witness. Exact rational
   points of the A15 slice serve only to choose the curve or the
   elimination; neither finding nor missing sampled points decides the
   attachment.

   **Outcome.** The half-rotation composite is no such piece
   ([evidence](../evidence/rank_locus_rotation_composite/README.md),
   `scripts/rank_locus_rotation_composite.py`, gates core-585 and core-586).
   - The candidate composes both exact turns over the {a, 0} family. With
     a ranging over C_4^perp, its differential at {e_i, 0} has rank 16 on
     the cone, so it would have carried a 15-dimensional germ; the record
     retains that rank and the composite on the stereographic slice.
   - Rank 32 at the rational point sigma = 2, tau = 3 of x0 exhibits a
     nonzero 21-minor, so the composite leaves D_(5,12) on an open dense
     set. Each turn alone keeps rank 20 there.
   - One turn keeps nullity 12 from the retained family points whose
     octonion halves are parallel, the stratum of the witnesses, and drops
     to nullity 4 from the retained generic points, hence off a proper
     closed subset of the family. Neither turn extends over the family.
   - The tangent bound is also 15 at three further family points, two
     with non-parallel halves, so the gap is not confined to the witness
     stratum at the points evaluated.
   - Related triples of A_5 (SageMath) form an 18-dimensional algebra whose
     orbit tangent space at two slice points is 13-dimensional and inside
     the family span; two of its generators move e_8 or e_24 across the
     halves.
   - The nullity-12 question stays open. The next step is equations that
     cut out D_(5,12) near {e_i, 0} (the centered Schur complement of
     computation 2 with its higher-order terms), or a curve family that is
     not a product of half turns.
4. **Extended-precision probe of the {a, 0} witnesses.** Near-rank-20
   points reached from seeded starts near each witness keep their distance
   from the family when refined at 110 digits to sigma_21/sigma_1 < 1e-40,
   and a perturbation cloud at scale 1e-2 spans 16 directions
   ([evidence](../evidence/rank_locus_nullity12_refinement/README.md),
   `scripts/rank_locus_nullity12_refinement.py`, gate core-662). A refined
   point is close to a rank-20 matrix, not provably close to a point of
   D_(5,12), because the rank-20 cone meets the left multiplications far
   from transversally. The probe therefore decides nothing: the local
   dimension stays undecided between the family's and the tangent bound,
   and admission still needs an exact piece or local equations.
5. **Exact linearity test of the tangent bound.** At all 29 witnesses,
   L_y has rank above 32 - k at seeded rational points y of T(x), computed
   over the rationals with FLINT
   ([evidence](../evidence/rank_locus_tangent_linearity/README.md),
   `scripts/rank_locus_tangent_linearity.py`, gates core-663 and core-664): rank 32 at
   every nullity-4, -8 and -12 witness and 20 at the nullity-16 ones. T(x)
   is therefore never inside the closed rank cone
   R_k = {y : rank L_y <= 32 - k}, and the cone over a piece of D_(5,k) of
   the tangent-bound dimension, if one exists, is curved. The nullity-16
   witnesses, whose local dimension equals the tangent bound on the curved
   zero-divisor cone, fail the test as well, so it excludes only a linear
   piece.
6. **p-adic Hensel lift of the Schur-complement germ.** This computation
   turns the question into one about a single power series.
   - Near x, R_k is the zero set of the k x k Schur complement S(y) of a
     pivot block of L_y.
   - c = 32 - dim T(x) of its entries have independent differentials. They
     cut out a smooth germ M of dimension dim T(x) that contains R_k.
   - The gap conjecture at x is therefore equivalent to the following
     statement:

     **Smooth-germ conjecture.** The excess entries H vanish on M. In other
     words, the power series P(u) = H(phi(u)) along M is zero, and the
     cone over D_(5,k) near x is the smooth, curved germ M itself.

     Computation 2 is the order-2 and order-3 part of P, and computation 5
     is the statement that M is not linear.

   The piece the item-3 row of the roadmap asks for is M, which is
   computable. What needs certifying is only that H vanishes on it.

   **Why p-adics help.** A p-adically small displacement is an exact
   infinitesimal:
   - Set the free coordinates to x_f + p w.
   - Hensel's lemma then lifts the dependent ones to a true point of
     M(Z_p), known to O(p^N) with no rounding.
   - H there is exact to O(p^N). When P_m(w) is a p-adic unit, where m is
     the order of P along w, and m < N, its valuation is m and its leading
     digit is P_m(w) mod p. Otherwise the valuation runs higher, so a zero
     to O(p^N) bounds the valuation, and the order only through the
     Schwartz-Zippel argument below.

   The real refinement of computation 4 could not make that step, because
   closeness to a rank-20 matrix places no locus point nearby.

   **Outcome.** The lift finds no obstruction at all 12 witnesses
   ([evidence](../evidence/rank_locus_padic_lift/README.md),
   `scripts/rank_locus_padic_lift.py`, gates core-668 and core-669).
   - H vanishes to O(p^12) at the pyadic lift. It also vanishes through
     t^63 in an independent F_p[[t]] lift (FLINT `nmod_mat`) along four
     seeded directions per witness over two 31-bit primes.
   - The controls pin down the method:
     - The zero-divisor families, whose local dimension equals the tangent
       bound, read zero.
     - x0 = e1 + e18 reads order 2 in both routes, with equal digits, and
       valuation 4 at scale p^2. Its cone A15 union B17 has unit dimension
       17 against the tangent bound 21.
     - Seeded velocities at x0 inside A15 and inside A15 intersect B17,
       where the order-2 obstruction vanishes, read orders 3 and 4 in both
       routes with equal digits. Detection therefore holds at the order
       where an obstruction at a gap witness would first appear.
     - A toy germ reads order 5.
   - The result points one way, but it admits nothing. A nonzero P of
     order below 64 would escape a drawn direction with probability at most
     64 / (p - 1), about 3e-8, with weights drawn from F_p^*, unless its
     leading form vanished modulo both
     primes.
   - The exact routes differ in reach:
     - An explicit identity h H = sum a_i G_i with h(x) nonzero is a finite
       certificate. Bare membership adds nothing: M is smooth, so the local
       ideal of G is prime, and H lies in it exactly when the conjecture
       holds.
     - The Bezout route works one curve at a time.
       - A line in the free coordinates lifts to M intersected with a linear
         space, a curve of degree at most d^c, where d = 33 - k is the degree
         of the cleared Schur entries.
       - So vanishing beyond d^(c+1) proves H zero on that curve only.
       - That is 29^5, about 2.1e7, at nullity 4; 25^11, about 2.4e15, at
         nullity 8; and 21^17, about 3.0e22, at nullity 12.
       - Finitely many seeded curves never cover M, and a generic direction
         brings back the Schwartz-Zippel bound.
     - An explicit parameterization of M. Computation 7 supplies one at
       nullity 12.

     Berlekamp-Massey length of the dependent coordinates. Along a line in
     the chart, every lifted dependent coordinate that moves has
     Berlekamp-Massey length 32 over its 63 series terms, at every witness,
     the smooth controls included.
     - The lengths are computed over F_p from the coefficients of t^1 to
       t^63. 32 is ceil(63/2), the value a sequence with no short recurrence
       takes; a prefix of N terms can reach length N.
     - Over F_p, a rational function P/Q of t with Q(0) nonzero obeys, from
       t^1 on, a recurrence of length max(deg P, deg Q). Length 32 therefore
       excludes every such P/Q with max(deg P, deg Q) <= 31.
     - In characteristic zero the exclusion covers the P/Q whose
       coefficients are p-integral with Q(0) a p-adic unit, because those
       reduce modulo p without raising either degree.
     - That constrains the graph coordinates only. At nullity 12, solving
       the quadrics of computation 7 for them takes a square root, and the
       same germ has a rational parameterization in other coordinates.
7. **Quadric germ at nullity 12.** At the three nonzd-axis witnesses and the
   seven Proposition 8.2 points, the germ of R_12 is a quadric cone
   ([evidence](../evidence/rank_locus_quadric_germ/README.md),
   `scripts/rank_locus_quadric_germ.py`, gates core-677 and core-678).
   - Set z = p + i q = (u, mu, v) for y = (p, q) with pure halves.
   - The cone is V = {u ^ v = 0, u.u + mu^2 + v.v = 0} over C^7 + C + C^7.
     It is reduced and irreducible of complex dimension 8 and degree 14,
     with Hilbert series (1 + 7t + 6t^2)/(1 - t)^8. Its 44 real quadrics
     cut V x V over C, of degree 196.
   - Why V lies in R_12:
     - The sedenion cross-product matrix satisfies
       C_z^2 - z z^T + Q I = sum M_ij (u_i v_j - u_j v_i), with 168
       coefficients of plus or minus 2.
     - rank_R L_y = 2 rank_C [[0, -t^T], [t, C_z]] with t = p - i q.
     - On V, C_z^2 = z z^T, and Sylvester's inequality then gives
       nullity >= 12.
   - The chart v = lambda u has a nonzero differential of
     F = mu^2 + (1 + lambda^2) w.w at all ten points. So V is a real
     16-manifold there.
   - The exact tangent bound is also 16. So the Schur germ M of
     computation 6 equals V, D_(5,12) has local dimension 15, and H vanishes
     on M at those points.
   - The record also places the A15 family of x0 inside V, and joins x0 to
     e1 + e25 by an exact path of constant nullity 12.
   - V passes through none of the nullity-8 and nullity-4 witnesses, where
     u ^ v is nonzero. Those families stay open.

Every computation is a loop over independent witnesses or sample points
and runs through `parallel.py`. Each joins `ci/gates.json` with `--check`
regenerating its retained result; computations 1, 2, 3, 5, 6 and 7 also run
`--self-test`, which rejects a corrupted nullity, frame, coefficient or
rank in normal and `-O` modes. The registry
carries the question as the open claim `a5-nonzero-divisor-two-dimension-gap`
and promotes it only through a retained certificate. Claim
`a5-nullity12-quadric-germ` admits the {a, 0} row at its witnesses, and the
nullity-8 and nullity-4 rows stay open.

## Route to the global classification (roadmap items 3-8)

The global obligations are listed in
[RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates)
and registered as the open claim `dimension32-global-topology`. They
depend on each other in order, and each has a first deliverable that
admits on its own:

| Item | First deliverable | Rests on | Admission |
| --- | --- | --- | --- |
| 3. Components of D_(5,4), D_(5,8), D_(5,12) | D_(5,12) first: its known pieces are B17, A15, the {a, 0} family and Proposition 8.2's (i_4, e_p) points; the extended-precision probe (computation 4) decides nothing, computation 5 excludes a linear piece, and computation 6 finds the Schur-complement germ M unobstructed through order 63, and computation 7 identifies M at the nonzd-axis witnesses and the Proposition 8.2 points as the quadric cone V, which also carries the A15 family at x0, so the remaining deliverable is how V meets B17 and the other pieces | the gap computation | a covering argument for every real coefficient vector, exact boundary admission; numerical charts alone do not admit |
| 4. Regularity and links | smoothness of each D_(5,12) piece from independent local equations; the normal link at x0, where A15 and B17 meet in dimension 13 | item 3 for D_(5,12) | rank loci and smooth strata kept distinct |
| 5. Kernel bundles | transition data of ker L_x over each smooth piece of D_(5,12) | item 4 | invariants computed; a classification needs its own sufficiency argument |
| 6. Attachments | how partner spheres specialize across every admitted closure incidence of D_(5,12) | items 3 and 5 | attaching maps, not a frontier matrix |
| 7. Global model | a finite model of Z_5 with a proved map, homology, cup products | items 3-6 for every nullity | chain maps and selected homotopy invariants; homology agreement alone does not admit |
| 8. Uniform structure in n | a recurrence across the doubling ladder | item 7 at n = 5 and the restricted family's sparse chain construction | a theorem, distinct from an algorithm that accepts n |

Items 3 to 8 are research obligations with no near-term hardware question;
the D_(5,12) column above is the smallest step that moves item 3.
