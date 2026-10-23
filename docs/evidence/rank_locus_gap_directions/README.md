# First-order directions of the A_5 rank-locus gap

`result.json` is the output of `scripts/rank_locus_gap_directions.py --out`.
It covers the 12 witnesses of the four families that the
[local-dimension certificate](../rank_locus_local_dimension/README.md)
leaves 2 below their tangent bound, every frame of `witnesses()` in
`scripts/rank_locus_local_dimension.py`. All arithmetic is exact over Q. The
question is the first computation of the
[gap note](../../notes/rank_locus_two_dimension_gap.md): where the two
dimensions of the gap point.

## Definitions

- **First-order space.** V spans ker L_x and U spans ker L_x^T. Then
  T(x) = {y : U^T L_y V = 0} and T_1(x) = T(x) intersected with x^perp. The
  norm row <x, y> = 0 removes the radial direction x, which preserves rank
  and is never evidence. dim T_1(x) is the certificate's tangent bound.
- **Family tangent space T_F.** x = {a, b} = (a + b, e_8 (b - a)), and (a, b)
  is read back from x. The script builds P, the span of velocities of exact
  curves inside the cone family through (a, b):
  - automorphism flows exp(s D) for the 14 octonion derivations D, applied
    diagonally;
  - scalings;
  - lines inside a linear fiber or an open condition;
  - for the C-orthogonal nonzd-nonzd family, rational projection curves.

  T_F is the bracket image of P intersected with x^perp. T_F lies in
  H_5^perp, where H_5 = span{e_0, e_8, e_16, e_24}.
- **Quotient map.** pi(y) = (y_8, y_24) vanishes on T_F, which the script
  checks on every basis vector. So pi induces a well-defined linear map
  T_1(x)/T_F -> span{e_8, e_24}, whose rank does not depend on any basis
  choice. The script computes that rank as rank pi(C) on the canonical
  complement C = T_1(x) intersected with T_F^perp. It also records
  rank pi(T_1(x)), which must agree. When the rank is 2, the record gives
  the unique basis c_8, c_24 of C with pi(c_8) = (1, 0) and
  pi(c_24) = (0, 1), together with their e_0 and e_16 coordinates.

## How T_F is proved

Each family's tangent space is squeezed between two exact subspaces of
equal dimension:
- **Below.** Every generator of P is the velocity of a curve that stays in
  the family:
  - A diagonal derivation is checked on all 256 basis pairs of A_4 and all
    1024 of A_5. It is also checked to be skew-symmetric and to vanish on
    e_0 and e_8. So exp(s D) is an orthogonal automorphism that fixes e_8
    and maps Z, Ann(a) and W(a) to their images.
  - Openness keeps a curve outside Z wherever its entry starts outside Z.
- **Above.** Each family has defining equations that vanish on it, so its
  tangent space lies in the kernel J of their Jacobian:
  - nonzd-axis: b = 0.
  - zd-nonzd-generic: Moreno's q1 = |a'|^2 - |a''|^2 and q2 = <a', a''> for
    the zero-divisor cone Z.
  - zd-nonzd-locus: q1, q2, <a, b> and <b, e_8 a>, plus
    E = (L_a^2 + |a|^2)(L_a^2 + 2|a|^2) b. E is 2|a|^4 times the
    Ann(a)-component of b, since -L_a^2 / |a|^2 has eigenvalues 0, 1 and 2
    on a zero divisor.
  - nonzd-nonzd-locus: <a, b> and <b, e_8 a>. The Jacobian has rank 2, so
    by the implicit function theorem the family is a 26-dimensional cone
    manifold with tangent space J. No cited structure enters.

The run requires P to lie in J with rank P = dim J. At a zero-divisor
entry a, the a-component T_Z(a) = span{D a} + R a has dimension 12, and it
equals both the Moreno kernel and the A_4 tangent bound
{alpha : U_a^T L_alpha V_a = 0}.

dim T_F then equals the family dimension that `witnesses()` assigns. Every
basis vector of T_F satisfies U^T L_y V = 0 and <x, y> = 0, checked in
integer arithmetic.

Exactness:
- Kernels come from FLINT's fmpq_mat reduced row echelon form.
- Every kernel vector is checked in Python integers.
- Each dimension is pinned between rank modulo 2^61 - 1 and the count of
  independent verified kernel vectors.

## Result

| Family | Witnesses | Nullity | dim T_1 | dim T_F | dim (T_1 cap H_5^perp) | Rank of T_1/T_F -> span{e_8, e_24} |
| --- | --- | --- | --- | --- | --- | --- |
| {a, 0}, a not a zero divisor | 1, 8, 15 | 12 | 15 | 13 | 13 | 2 |
| a zero divisor, b in W(a) | 4, 11, 18 | 8 | 21 | 19 | 19 | 2 |
| a zero divisor, b not, off the locus | 5, 12, 19 | 4 | 27 | 25 | 25 | 2 |
| neither, C-orthogonal | 6, 13, 20 | 4 | 27 | 25 | 25 | 2 |

The prediction holds at all 12 witnesses: the rank is 2 everywhere, so the
falsifier did not fire. The result is sharper than the prediction. At every
witness c_8 = e_8 and c_24 = e_24, with zero e_0 and e_16 coordinates, so

    T_1(x) = T_F (+) span{e_8, e_24}   (orthogonal direct sum).

Three consequences follow:
- e_8 and e_24 are themselves first-order admissible.
- The exit plane is span{e_8, e_24} itself, not a graph over it.
- No first-order direction has an e_0 or e_16 component.

## What it establishes

- **Inside H_5^perp.** T_1(x) intersected with H_5^perp equals T_F at every
  witness, so the tangent cone of D_(5,k) intersected with H_5^perp lies in
  T_F. With the family as the lower bound, D_(5,k) intersected with
  H_5^perp has local dimension exactly the family dimension at each
  witness.
- **Where any excess must go.** Any local dimension of D_(5,k) above the
  family's comes from points off H_5^perp. Its tangent directions then have
  a nonzero (y_8, y_24) component, and modulo T_F they lie in
  span{e_8, e_24}.
- **First order only.** This is a tangent-cone containment. It does not
  show that D_(5,k) leaves H_5^perp at these witnesses, and it does not
  decide the local dimension. The local-dimension README notes that at {e_1, 0}
  the straight lines along e_8 and e_24 drop to nullity 0, so at that
  witness a curve with these velocities bends at second order. The other
  witnesses' straight lines are not checked.
  - Computation 2 of the gap note decides this. It is the Schur system over
    all of T_1(x), with the family variables kept and the two transverse
    coordinates being exactly the e_8 and e_24 coefficients.
- **Cited inputs.** The family manifold statements and Moreno's description
  of Z enter only through the upper and lower squeeze above. The eigenvalue
  structure of L_a^2 is checked at each witness and cited for nearby zero
  divisors.

The registry claim `a5-nonzero-divisor-two-dimension-gap` stays open.

## Replay

`"$PYTHON" scripts/rank_locus_gap_directions.py --check docs/evidence/rank_locus_gap_directions/result.json`
recomputes every witness, runs the row verifier on each, and requires the
retained file to equal, byte for byte, the text `--out` writes.

`--self-test` requires the verifier to reject 32 damaged rows (8 per
family). The damage covers:
- a corrupted nullity or kernel frame;
- a T_F vector moved off H_5^perp, moved out of T_1, or replaced by a
  complement vector;
- a corrupted complement vector;
- a wrong dim T_1;
- an altered projection rank.

Gate core-551 runs `--check` and gate `core-self-test-04` (`tests/test_cli_self_tests.py`)
runs `--self-test`, each in normal and `-O` mode. Each mode runs in about 5 s serially, and `parallel.py`
spreads the witnesses over the available CPUs.
