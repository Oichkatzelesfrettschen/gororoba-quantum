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
   `scripts/rank_locus_gap_directions.py`, gate core-551 and the behavioral suite (`tests/test_cli_self_tests.py`)).
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
   and a
   perturbation cloud at scale 1e-2 spans 16 directions
   ([evidence](../evidence/rank_locus_nullity12_refinement/README.md),
   `scripts/rank_locus_nullity12_refinement.py`, gate core-662). A refined
   point is close to a rank-20 matrix, not provably close to a point of
   D_(5,12), because the rank-20 cone meets the left multiplications far
   from transversally. The probe therefore decides nothing: the local
   dimension stays undecided between the family's and the tangent bound,
   and admission still needs an exact piece or local equations.

Every computation is a loop over independent witnesses or sample points
and runs through `parallel.py`. Each joins `ci/gates.json` with `--check`
regenerating its retained result and `--self-test` rejecting a corrupted
nullity, frame or coefficient, in normal and `-O` modes. The registry
carries the question as the open claim `a5-nonzero-divisor-two-dimension-gap`
and promotes it only through a retained certificate.

## Route to the global classification (roadmap items 3-8)

The global obligations are listed in
[RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates)
and registered as the open claim `dimension32-global-topology`. They
depend on each other in order, and each has a first deliverable that
admits on its own:

| Item | First deliverable | Rests on | Admission |
| --- | --- | --- | --- |
| 3. Components of D_(5,4), D_(5,8), D_(5,12) | D_(5,12) first: its known pieces are B17, A15, the {a, 0} family and Proposition 8.2's (i_4, e_p) points; the extended-precision probe (computation 4) places the {a, 0} family inside a 15-dimensional piece numerically, so the certified piece through an {a, 0} witness is the deliverable | the gap computation | a covering argument for every real coefficient vector, exact boundary admission; numerical charts alone do not admit |
| 4. Regularity and links | smoothness of each D_(5,12) piece from independent local equations; the normal link at x0, where A15 and B17 meet in dimension 13 | item 3 for D_(5,12) | rank loci and smooth strata kept distinct |
| 5. Kernel bundles | transition data of ker L_x over each smooth piece of D_(5,12) | item 4 | invariants computed; a classification needs its own sufficiency argument |
| 6. Attachments | how partner spheres specialize across every admitted closure incidence of D_(5,12) | items 3 and 5 | attaching maps, not a frontier matrix |
| 7. Global model | a finite model of Z_5 with a proved map, homology, cup products | items 3-6 for every nullity | chain maps and selected homotopy invariants; homology agreement alone does not admit |
| 8. Uniform structure in n | a recurrence across the doubling ladder | item 7 at n = 5 and the restricted family's sparse chain construction | a theorem, distinct from an algorithm that accepts n |

Items 3 to 8 are research obligations with no near-term hardware question;
the D_(5,12) column above is the smallest step that moves item 3.
