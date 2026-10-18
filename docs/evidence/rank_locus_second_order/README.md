# Second-order compatibility of the A_5 rank-locus gap directions

`result.json` is the output of `scripts/rank_locus_second_order.py --out`.
It covers the 12 witnesses of the four families that the
[local-dimension certificate](../rank_locus_local_dimension/README.md)
leaves 2 below their tangent bound, plus one control. All arithmetic is
exact over Q. The question is the second computation of the
[gap note](../../notes/rank_locus_two_dimension_gap.md). The
[first-order record](../rank_locus_gap_directions/README.md) proves that at
every witness

    T_1(x) = T_F (+) span{e_8, e_24}   (orthogonal direct sum).

This record asks which velocities v = tau + s e_8 + t e_24, with tau in T_F,
pass the second-order test for staying in D_(5,k). Every variable (tau, s, t)
is kept.

## Definitions

- **Schur complement.**
  - V spans ker L_x and U spans ker L_x^T.
  - Complements V_c and U_c give the invertible pivot P = U_c^T L_x V_c and
    the generalized inverse G = V_c P^-1 U_c^T.
  - U^T L_x = 0 and L_x V = 0, so rank L_(x+h) = rank A + rank S(h), where
    A = P + U_c^T L_h V_c and

        S(h) = U^T L_h V - U^T L_h G L_h V + U^T L_h G L_h G L_h V - ...

  - While A stays invertible, L_(x+h) has nullity k exactly when S(h) = 0.
- **Order conditions.** On a curve h = eps v + eps^2 w + eps^3 u, with
  Delta(y) = U^T L_y V:

  | Order | Condition |
  | --- | --- |
  | 1 | Delta(v) = 0, so v lies in T(x) |
  | 2 | Delta(w) = U^T L_v G L_v V |
  | 3 | Delta(u) = U^T L_v G L_w V + U^T L_w G L_v V - U^T L_v G L_v G L_v V |

- **Obstruction.** N spans the cokernel of Delta : R^32 -> R^(k x k). The
  order-2 equation has a solution w exactly when

      Q(v) = N^T vec(U^T L_v G L_v V) = 0.

  - The residual keeps all k^2 entries, and w ranges over all of R^32.
  - The target is independent of the complements on T(x): U^T L_v = M L_x and
    L_v V = L_x M' give U^T L_v G L_v V = M L_x M'.
- **Structure.** Every witness has x_0 = x_16 = 0, so L_x is skew, U = V
  exactly, and every order-2 target is skew. The script checks all three.
- **Unit sphere.** Adding c x to w leaves Delta(w) unchanged, so the norm
  condition 2 <x, w> + |v|^2 = 0 constrains nothing.
- **Tangent cone.** A Bouligand tangent vector v is a limit of
  (y_n - x)/t_n with y_n in the locus.
  - Write y_n - x = t_n v + r_n with r_n = o(t_n).
  - Projecting S(y_n) = 0 onto N removes Delta(r_n), and the remainder
    divided by t_n^2 tends to -Q(v).
  - So Q(v) = 0, and every tangent-cone vector passes the order-2 test.
- **Order 3.** When Q vanishes on T(x), its polarization vanishes on
  T(x) x T(x).
  - The order-3 condition then does not depend on the choice of w. It reads
    K3(v) = 0 for the cubic
    K3(v) = N^T vec(B(v, R(v)) - U^T L_v G L_v G L_v V).
  - R(v) is a fixed linear right inverse of Delta applied to the order-2
    target, and B(v, w) = U^T L_v G L_w V + U^T L_w G L_v V.

## Sign convention

The signs of the order-2 and order-3 equations are checked on an exact curve
of the cone whose order-2 target and triple term U^T L_v G L_v G L_v V are
nonzero, so a flipped target or a flipped triple term against B(v, w) fails:

- **zd-nonzd families.** The curve is the automorphism curve exp(eps D) x for
  the first of the 14 octonion derivations, extended diagonally to A_5. It
  has w = D^2 x / 2 and order-3 coefficient D^3 x / 6, and
  L_(g x) = g L_x g^-1 keeps the nullity.
- **nonzd-axis and nonzd-nonzd-locus.** Every derivation gives a zero target
  there. The curve is the rotation of the upper half p of x = (p, q) toward
  |p| e_8:

      Y(u) = (1 - m u^2) p + 2 m u e_8 + (1 + m u^2) q,   m = |p|^2,

  a polynomial curve x + u v + u^2 w.
  - Its nullity is proved from the exact ranks at 2 (33 - k) + 1 integer
    nodes: every (33 - k)-minor of L_Y(u) has degree at most 2 (33 - k), so
    rank at most 32 - k at every node makes each such minor vanish
    identically.
  - Rank 32 - k at u = 0 keeps the nullity exactly k near u = 0.

At every witness:
- The curve's w satisfies Delta(w) = +U^T L_v G L_v V, and the target is
  nonzero.
- Its order-3 coefficient u (zero on the rotation curve) satisfies
  Delta(u) = B(v, w) - U^T L_v G L_v G L_v V under both complements.
- The triple term is nonzero for the coordinate complements that the
  cubic uses.

B(v, w) and the triple term depend on the complements separately: under the
image complements the triple term of the rotation curve vanishes. Only their
difference is intrinsic.

The control runs the construction at e1 + e18 on the tangent coordinates of
`gororoba_quantum/nullity_twelve_locus.py`:
- It finds rank 8, and its row space equals that module's eight canonical
  quadrics.
- Unequal multiples of the frame vectors scale Delta's rows unevenly, and
  they leave the row space unchanged.

## Result

| Family | Witnesses | Nullity | dim T_1 | Cokernel dim | Monomials | Independent quadratic equations | Cubic rank | Outcome | Certificate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {a, 0}, a not a zero divisor | 1, 8, 15 | 12 | 15 | 128 | 120 | 0 | 0 | B | Q = 0 on T_1; (e_8, w) and (e_24, w) verified; rotation curves |
| a zero divisor, b in W(a) | 4, 11, 18 | 8 | 21 | 54 | 231 | 0 | 0 | B | Q = 0 on T_1; (e_8, w) and (e_24, w) verified |
| a zero divisor, b not, off the locus | 5, 12, 19 | 4 | 27 | 12 | 378 | 0 | 0 | B | Q = 0 on T_1; (e_8, w) and (e_24, w) verified |
| neither, C-orthogonal | 6, 13, 20 | 4 | 27 | 12 | 378 | 0 | 0 | B | Q = 0 on T_1; (e_8, w) and (e_24, w) verified; rotation curves |

The coefficient matrix of Q in the coordinates (tau, s, t) is identically
zero at all 12 witnesses, so the real zero set is Z = T_1. The three frames
of each family agree.

- **Order 2 is vacuous.** Every first-order velocity, including e_8 and e_24
  alone, is formally second-order compatible. The record carries the exact
  pairs (v, w) for v = e_8 and v = e_24.
- **Order 3 is vacuous.** The cubic K3 is identically zero on T_1 at every
  witness.
- **Transverse curves.** The rotation of the upper half toward e_8 and of the
  lower half toward e_24 both keep the nullity at the six nonzd-axis and
  nonzd-nonzd-locus witnesses. So e_8 and e_24 are velocities of actual
  curves of D_(5,k) there, and both lie in the tangent cone.
- **No curve at the zd families.** At the six zd-nonzd witnesses both
  rotations exhibit a nonzero (33 - k)-minor. The rotated point therefore
  has nullity below k for all but finitely many u, and no transverse curve
  was found there.

The note's conjecture predicted Outcome B with curves, and its alternative
predicted Outcome A. The deviation is the finding: the second-order test is
vacuous at every witness, so it can neither confirm nor refute the two extra
dimensions.

## What it establishes

- **Proved.**
  - At every witness, Q vanishes on T_1, and so does K3. Every
    v in T_1 is formally compatible through order 3.
  - The Bouligand tangent cone of D_(5,k) lies in T_1, which is the
    first-order bound.
  - At the nonzd-axis and nonzd-nonzd-locus witnesses, e_8 and e_24 are
    velocities of exact curves in D_(5,k).
- **Formal only.** Compatibility at orders 2 and 3 constructs no curve, and
  says nothing about orders 4 and beyond.
- **Not established.**
  - The local dimension at any witness. Curves with transverse velocities
    form a union of one-dimensional germs, and their velocity span bounds no
    local dimension from below.
  - The dimension rises only through a certified m-dimensional piece through
    x: an explicit parameterization whose nullity holds exactly on an open
    set of parameters and whose differential has rank m at x.
  - Whether the tangent cone is a linear space.
- **Upper bound.** No upper bound below dim T_1 follows either. A tangent
  cone inside a subspace bounds no local dimension of a real algebraic set:
  the surface y^2 + z^2 = x^4 has local dimension 2 at 0, and its tangent
  cone is the x-axis.

The registry claim `a5-nonzero-divisor-two-dimension-gap` stays open.

## Replay

`"$PYTHON" scripts/rank_locus_second_order.py --check docs/evidence/rank_locus_second_order/result.json`
recomputes every witness and the control. It then runs the row verifier,
which repeats the computation through different routes:
- G is rebuilt from the image columns of L_x instead of coordinate
  complements.
- Q is rebuilt from its values Q(b_i) and Q(b_i + b_j) instead of
  polarization.
- Both frames, the cokernel pin and T_F are checked against the family
  builder.
- The order-2 solutions, both sign-check identities and the rotation-curve
  node ranks are rechecked.
- The cubic is recomputed.

The retained file must equal, byte for byte, the text `--out` writes.

`--self-test` takes the first witness of each family and requires the
verifier to reject 48 damaged rows, 12 per family:
- a nonzero coefficient entry, or a wrong coefficient rank;
- a corrupted order-2 acceleration, or a solution with s = t = 0;
- the outcome label A;
- a corrupted kernel frame, a corrupted T_F vector, or a wrong cokernel
  dimension;
- a sign-flipped exact-curve acceleration, or a corrupted order-3 curve
  coefficient;
- a nonzero cubic coefficient;
- a flipped transverse-curve verdict.

Outcome B carries no sum-of-squares weights, so the label, solution and
sign-check mutations stand in for the certificate-weight mutations.

The gates are core-553 (`--check`) and core-554 (`--self-test`), each in normal
and `-O` mode, on the full tier. Serial cost is dominated by the order-3 cubic
at the zd-nonzd-locus witnesses, and `parallel.py` spreads the witnesses over
the available CPUs.
