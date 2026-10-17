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
3. **Relate A15 to the {a, 0} family.** Closure is decided exactly or not
   at all. A positive answer is an explicit curve or parameterization of
   nullity-12 points, certified exactly along its parameter, whose limit is
   an {a, 0} witness with a not a zero divisor. A negative answer is a
   semialgebraic elimination showing that the A15-type piece and the {a, 0}
   family meet in no common component near such a witness. Exact rational
   points of the A15 slice serve only to choose the curve or the
   elimination; neither finding nor missing sampled points decides the
   attachment.

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
| 3. Components of D_(5,4), D_(5,8), D_(5,12) | D_(5,12) first: its known pieces are B17, A15, the {a, 0} family and Proposition 8.2's (i_4, e_p) points; the gap computation above fixes the dimension of the {a, 0} piece | the gap computation | a covering argument for every real coefficient vector, exact boundary admission; numerical charts alone do not admit |
| 4. Regularity and links | smoothness of each D_(5,12) piece from independent local equations; the normal link at x0, where A15 and B17 meet in dimension 13 | item 3 for D_(5,12) | rank loci and smooth strata kept distinct |
| 5. Kernel bundles | transition data of ker L_x over each smooth piece of D_(5,12) | item 4 | invariants computed; a classification needs its own sufficiency argument |
| 6. Attachments | how partner spheres specialize across every admitted closure incidence of D_(5,12) | items 3 and 5 | attaching maps, not a frontier matrix |
| 7. Global model | a finite model of Z_5 with a proved map, homology, cup products | items 3-6 for every nullity | chain maps and selected homotopy invariants; homology agreement alone does not admit |
| 8. Uniform structure in n | a recurrence across the doubling ladder | item 7 at n = 5 and the restricted family's sparse chain construction | a theorem, distinct from an algorithm that accepts n |

Items 3 to 8 are research obligations with no near-term hardware question;
the D_(5,12) column above is the smallest step that moves item 3.
