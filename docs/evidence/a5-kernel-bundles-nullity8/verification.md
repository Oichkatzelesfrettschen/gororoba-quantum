# Independent verification of the nullity-eight kernel-bundle statements

[`verify_nullity8_independent.py`](verify_nullity8_independent.py) re-derives five statements of this record from
`gororoba_quantum/cd_core.py` and writes [`verification.json`](verification.json). Its algebra comes from the compact
helpers of the earlier [independent verifier](../a5-kernel-bundles/verify_kernel_bundles_independent.py): compact
`g_2` from `cd_sign(8, p, q)`, its blockwise lift to A_5, the phase and its domain lift, `L_y` from
`left_mult_matrix_exact(32, y)`, stabilizer solves, Casimir multiplicities and the representation-ring quotient.
Split-coordinate data come from
[`verify_regularity_independent.py`](../a5-strata-regularity/verify_regularity_independent.py) (`REPS`, closure
memberships, H-tangent vectors, nilpotent split derivations, G_2 and boost actions). `y_from_split` and `nullspace`
come from [`rederive_strata_equations.py`](../a5-rank-strata-equations/rederive_strata_equations.py). The script
imports nothing from this directory, and every check ran before the producer scripts here were read; only the definition of the four associative three-form values (the real frame (a, b, c, d) = (Re u, Im u, Re v, Im v) in original coordinates, phi(x, y, z) = <x cross y, z>) was taken from this directory's README prose beforehand. All arithmetic
is rational or Gaussian rational, and no random value enters.

Every test point is either a representative moved by Gaussian-rational split unipotents and complex or real boosts
(the `MOVES` sequences differ from the earlier verifier's), or a special point built explicitly and then classified
by its closure pattern, its H-orbit dimension and its `L_y` nullity. K is compact `G_2 x U(1)` phase. K_H is K times
the compact circle of `SO(2, C)`, whose generator `ROT: (u, v) -> (v, -u)` in original coordinates is checked to equal
i times the split boost generator. A primitive circle generator `Z` has integer base weights of gcd one and a positive
phase coefficient `t`. A native kernel weight `w` means `Z = w J` with `J = L_(e_16)`, and the converted weight is
`-(w + t)`, the convention of the earlier verifier.

## Verdicts

| # | Statement | Verdict | Decisive evidence (`verification.json`) |
| --- | --- | --- | --- |
| 1 | Compact tangent rank 12, 12, 15, 12, 12 at the representatives; 15 generically | confirmed | `statement_1`: the representatives give exactly 12, 12, 15, 12, 12. Each of the three moved points per orbit stays in its orbit with nullity 8 and has rank 15 |
| 2 | SU(2) on W8 acts on the rank-4 kernel as `2 V_1`; on E8-bar and X_+- as `2 V_0 + V_1`; an Iso circle on the coassociative locus acts as `C_0 + 2 C_(-3) + C_(-2)` | confirmed | `statement_2`: same decompositions at the representative and at 2-3 off-representative su(2) points per orbit, all outside the representative's K x R_+ orbit. Four Iso points with all three-form values zero have a one-dimensional stabilizer and converted weights {0, -3, -3, -2}; four Iso points with a nonzero value have stabilizer 0 |
| 3 | Limits lie in the boundary kernel; most incidences are path-dependent; X_+- -> B9 is canonical | confirmed (canonicity: no counterexample) | `statement_3`: 5 incidences with 5-7 valid curves each. E8-bar -> V gives 4 distinct limits from 5 curves, E8-bar -> V^a_+ gives 3 from 6, W8 -> B9 gives 3 from 5. X_+ -> B9 gives 1 limit from 7 curves and X_- -> B9 gives 1 from 5, including tangent-first curves whose normal component enters at order 2 |
| 4 | Complex stabilizers 4, 5, 5, 6, 6; cores `V_2(R^7) x S^1` (W8, X_+-), `V_2(R^7) x T^2` (E8-bar), `G_2` (Iso) | confirmed (dimensions computed; Mostow retraction is an argument) | `statement_4`: dim h_z is 4, 5, 5, 6, 6 and the reductive quotients are 4, 3, 2, 4, 4. Each core has dimension 16 minus the reductive quotient (12, 13, 14, 12, 12), and each orbit has an explicit point whose K_H stabilizer attains that dimension |
| 5 | Classes `2 xi` (W8), `C^2 + xi` (E8-bar, X_+-) with the order-two class, `C^4` (Iso) | confirmed (fibers and K-bookkeeping computed; bundle identifications are arguments) | `statement_5`: the fibers at the core points are `2 V_1` and `2 V_0 + V_1` with 7 -> 3 + 2t. The ring is Z/2, so the reduced classes are `0 x` (W8) and `x` (E8-bar, X_+-). The Iso circle meets G_2 trivially |

## What the computations show

**1. Compact tangent ranks.** The rank of `X -> X y` on the 15-dimensional compact algebra is computed at the five
representatives and at three moved points per orbit (`g1`, `g2`, `g3`, each mixing Gaussian unipotents with a complex
or real boost). The representatives give 12, 12, 15, 12, 12. Every moved point classifies into its orbit, has nullity
8, and has rank 15. Rank 15 is an open condition. It holds at one point of each connected complex orbit, so it is
generic on that orbit. A zero stabilizer makes the kernel representation `4 V_0`.

**2. Stabilizer strata.** At the W8, E8-bar, X_+ and X_- representatives the stabilizer is three-dimensional. Its
Killing form is negative definite, so it is su(2). The Killing Casimir gives:

- W8 kernel: `2 V_1`;
- E8-bar, X_+ and X_- kernels: `2 V_0 + V_1`;
- the 7 in every case: `3 V_0 + 2 V_1`, which is the SU(2) of `G_2/SU(2) = V_2(R^7)`;
- the 14 in every case: `3 V_0 + 4 V_1 + V_2`.

All four representatives keep u and v inside span(e1, e2, e3) in original coordinates, the 3-plane that the su(2)
fixes. The off-representative points therefore come from moving each representative by complex SO(3, C) rotations of
that 3-plane together with boosts. Both commute with the su(2). Every such point, and the X_+- core points below, has
the same su(2) and the same kernel decomposition, and lies outside the representative's K x R_+ orbit (its Hermitian
invariants differ).

On Iso, the isotropic pairs inside the complexified coassociative 4-plane span(e4, e5, e6, e7) fall into two rulings:

- **beta** ruling, span(e4 + i e5, e6 - i e7): four pairs, all in Iso. Each has a one-dimensional stabilizer with
  phase coefficient t = 1, native kernel weights {-1, 1, 2, 2}, and converted weights {0, -3, -3, -2}, as claimed.
- **alpha** ruling, span(e4 + i e5, e6 + i e7): both pairs classify as B9, not Iso.

The Iso representative and three moved Iso points carry nonzero three-form values and have stabilizer 0.

**3. Boundary specializations.** Each approach is a polynomial curve `z(t)` in split coordinates, built in the
closure of the open orbit and then moved by one fixed non-compact element (`CURVE_MOVE`). That move makes all curves
of an incidence end at the same non-special boundary point. Each curve passes three checks:

- every closure generator of the open orbit vanishes at 4·deg + 1 sample values of t, hence identically;
- the curve classifies into the open orbit at t = 1/2 and t = 1/3, hence for all but finitely many t;
- its endpoint classifies into the boundary orbit.

The limit is the span of the leading terms `x_0` of the Jordan chains `sum_j L_(y_j) x_(i-j) = 0`, for i up to
the order at which that span first drops to 8 real dimensions. All limits are J-invariant and lie in the
12-dimensional boundary kernel, which holds automatically because `L_(y_0) x_0 = 0`. Results:

- **E8-bar -> V.** The curves `(e1, mu0, lambda e1) + t (alpha n, 0, beta n)` use a null n in the +1 or -1
  eigenspace of `e1 x .`; these eigenspaces are the two sheets. Curves on opposite sheets give limits that differ by
  4 real dimensions. On one sheet, different n give limits that differ by 2 real dimensions. Moving u or v along the
  same n gives the same limit.
- **E8-bar -> V^a_+.** The same sheet structure appears: 3 distinct limits among 6 curves.
- **W8 -> B9.** 3 distinct limits among 5 curves.
- **X_+ -> B9 and X_- -> B9.** All curves give one limit: 7 curves for X_+, 5 for X_-, including a complex-phase
  rotation of the normal direction, an added tangent direction, a quadratic curve, and three tangent-first curves.
  A tangent-first curve has a first-order term tangent to B9, so its normal component enters at t^2 and its Jordan
  chain needs order 2. That limit is invariant under
  the boundary point's compact U(1) stabilizer, as canonicity requires. None of the path-dependent limits is invariant
  under its endpoint's compact stabilizer.

**4. Stabilizer dimensions and cores.** The complex stabilizer h_z is solved as a real subalgebra of the realified
`g_2(C) + so(2, C) + C` acting on split C^15. It is solved at the representative and at a moved point of each orbit,
and the dimensions agree:

| Orbit | dim h_z | dim rad | dim unipotent radical | reductive quotient | core dim |
| --- | ---: | ---: | ---: | ---: | ---: |
| W8 | 4 | 1 | 0 | 4 | 12 |
| E8-bar | 5 | 2 | 2 | 3 | 13 |
| Iso | 5 | 5 | 3 | 2 | 14 |
| X_+ | 6 | 3 | 2 | 4 | 12 |
| X_- | 6 | 3 | 2 | 4 | 12 |

The radical is the Killing-orthogonal complement of the derived algebra. The unipotent radical is the radical of the
faithful trace form restricted to the radical. The trace form is positive definite on the rational cocharacters of a
torus and vanishes on nilpotent elements, so its radical is exactly the nilpotent part. The script checks that this
part is nilpotent (`X^30 = 0`), that it is an ideal, and that the radical modulo it is abelian. Core dimensions are
16 minus the reductive quotient. They equal dim V_2(R^7) + 1, + 2, and dim G_2, with dim V_2(R^7) = 11 computed as
the G_2 orbit dimension of an orthonormal pair. The explicit core points are:

- **W8 and E8-bar:** the representatives. Their K_H stabilizers are su(2) + u(1) and su(2).
- **Iso:** the beta coassociative point, with a two-dimensional K_H stabilizer whose projection to the (phase,
  rotation) torus has rank 2.
- **X_+-:** the representatives are not core points, since their K_H stabilizer is su(2), dimension 3, and their K_H
  orbit is 13-dimensional. The points `(m + e3, 0, -i m + i e3)` and `(m + e3, 0, i m - i e3)` with `m = e1 - i e2`
  are core points: K_H stabilizer su(2) + u(1), dimension 4, external projection rank 1, and K orbit = K_H orbit,
  dimension 12.

**Inferred** (Mostow): the unit section of `H/H_z` deformation-retracts onto `K_H/(K_H)_z` at a point where
`(K_H)_z` is a maximal compact subgroup of H_z. With the measured stabilizers this gives:

- W8, X_+-: `(G_2 x U(1))/SU(2) = V_2(R^7) x S^1`;
- E8-bar: `(G_2 x T^2)/SU(2) = V_2(R^7) x T^2`;
- Iso: `(G_2 x T^2)/T'` with T' projecting onto T^2, which equals G_2 when T' meets G_2 trivially.

That triviality holds because the circle's G_2 weights {0, 1, 2} are divisible by t = 1.

**5. Classes.** On W8, X_+ and X_- the K orbit of the core point equals the core, so the kernel bundle is the
homogeneous bundle `K x_SU(2) F`. F is `2 V_1` on W8 and `2 V_0 + V_1` on X_+-, so the bundle is the pullback of
`2 xi` or `C^2 + xi` from V_2(R^7). The script measures the restrictions 7 -> 3 + 2t and 14 -> t^2 + 4t + 2. The
earlier verifier's ring quotient then gives reduced K^0(V_2(R^7)) = Z/2 generated by x = [xi] - 2, so `2 xi` has class
2x = 0 and `C^2 + xi` has class x != 0. Projection onto V_2(R^7) has a section, so pullback to the core is injective
and the class stays nonzero.

On E8-bar, K is not transitive on the 13-dimensional core. The rotated representative (rotation (3/5, 4/5)) lies
outside the K orbit, since its Hermitian invariants differ. It has the same K-stabilizer subalgebra and the same fiber
`2 V_0 + V_1`. **Inferred:** the core is K-equivariantly `S^1 x K/SU(2)`. K-equivariant bundles on it correspond to
SU(2)-equivariant bundles on the circle with trivial action. With fiber `2 V_0 + V_1`, the automorphism group
`GL(2, C) x GL(1, C)` is connected, so the bundle is the pullback of `C^2 + xi`.

On Iso, the core equals the K orbit `K/U(1)`, which is G_2 because the circle meets G_2 trivially. The bundle is a sum
of four line bundles, and `H^2(G_2) = 0` makes each one trivial, giving `C^4`.

`2 xi` is stably trivial. Rank 4 over the 12-dimensional core lies outside the stable range, so whether `2 xi` is
actually trivial stays undecided.

## Methods that differ from the producer scripts

- **Test points.** The su(2) points off the representatives come from SO(3, C) rotations of the fixed associative
  3-plane composed with boosts, not from invariant-coordinate criteria. The X_+- compact cores come from circle weight
  vectors.
- **X_+- cores.** `unit_section_topology.py` uses the X_+- representatives as compact fixtures. There it observes a
  three-dimensional K_H stabilizer and infers the S^1 factor from the complex stabilizer's torus projection. This
  verifier exhibits explicit Mostow-adapted X_+- points with the four-dimensional K_H stabilizer and checks the fiber
  there.
- **Kernel limits.** `boundary_specializations.py` uses a second-order Schur complement on a boundary-kernel frame.
  This verifier takes the leading-term space of truncated Jordan chains to whatever order is needed, and certifies
  closure membership identically in t by sample counts against generator degree.
- **Unipotent radical.** `unit_section_topology.py` takes the Killing-form kernel of h_z when all its elements are
  nilpotent. This verifier takes the trace-form radical inside the Killing complement of the derived algebra and
  checks nilpotency, the ideal property and that the quotient is abelian.
- **Arithmetic.** Linear algebra runs on python-flint `fmpq_mat` throughout; the producers use sympy.

## Not checked

- **Exhaustiveness of the stabilizer strata.** Only the listed types were tested, and only at the listed points.
  "The circle locus equals the coassociative locus inside Iso" holds on four coassociative and four non-coassociative
  points but is not proved.
- **Component groups.** Disconnected stabilizer components were not examined. The bundle identifications assume
  connected point stabilizers in K.
- **Canonicity of X_+- -> B9.** Only falsified-against: 12 approaches gave one limit (3 of them tangent-first, chain
  order 2), plus a U(1)-invariance necessary condition. No proof that every approach gives the same limit.
- **Untested incidences.** W8 -> Iso, W8 -> VB, W8 -> N_+-; E8-bar -> X_+-, B9, VB, V^a_-, N_+-; Iso -> B9, VB,
  N_+-; X_+- -> VB, V^a_+-, N_+-. The tests covered E8-bar -> V, E8-bar -> V^a_+, W8 -> B9, X_+ -> B9 and
  X_- -> B9.
- **Homotopy steps.** The Mostow retraction and the equivariant-bundle classification over the E8-bar rotation
  circle are arguments, not machine checks. So are the triviality of line bundles over G_2 and the full K-groups of
  the cores beyond pullback injectivity.
- **Actual triviality of `2 xi` on W8.** Undecided: its reduced class is zero, but its rank is outside the stable
  range.

## Replay

```sh
export PYTHON="${PYTHON:-python3}"
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-bundles-nullity8/verify_nullity8_independent.py \
    --out docs/evidence/a5-kernel-bundles-nullity8/verification.json
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-bundles-nullity8/verify_nullity8_independent.py --self-test
```

The full run took 22.6 s and the self-test 3.4 s with four workers (Python 3.14.8, python-flint 0.9.0). Each of
the seven self-test mutations changes a downstream value:

| Mutation | Effect |
| --- | --- |
| Unmoved points | W8 generic rank 12 |
| Flipped J | Iso weights {-2, 0, 1, 1} |
| False 7 branching 5 + t | the ring loses Z/2 |
| One normal direction for every curve | E8-bar -> V has one limit |
| A non-coassociative isotropic pair | Iso stabilizer 0 |
| Whole radical taken as unipotent | W8 reductive dimension 3 |
| Leibniz term dropped | derivation dimension 1 |
