# A_5 kernel bundles on the nullity-eight strata

This evidence directory executes the
[nullity-eight kernel-bundle program](../../design/a5-kernel-bundles-nullity8-program.md). The first exact result
computes the connected compact `G_2 x U(1)` tangent ranks on the five complex nullity-eight orbits from the
[regularity record](../a5-strata-regularity/README.md): `W8`, E8-bar, the isotropic orbit `Iso`, and the two branches
`X_+` and `X_-`. Orbit invariants, complete moduli spaces, stabilizer representations, topology, transition data, and
bundle classes remain open.

Every calculation uses integer or rational arithmetic. [`compact-orbit-ranks-result.json`](compact-orbit-ranks-result.json)
is the output of [`compact_orbit_ranks.py`](compact_orbit_ranks.py) `--out`, and
[`w8-orbit-moduli-result.json`](w8-orbit-moduli-result.json) is the output of
[`w8_orbit_moduli.py`](w8_orbit_moduli.py) `--out`. Each producer carries a byte-exact `--check` and mutation-bearing
`--self-test`.

## Every nullity-eight orbit has generic compact rank fifteen

The connected compact symmetry acting on a unit section has fourteen compact `G_2` generators and the lifted base
phase, for dimension fifteen. The producer evaluates its tangent map at the recorded representative of each orbit
and at three exact moved points. The moves use rational exponentials of nilpotent `G_2(C)` derivations and rational
`SO(2,C)` boosts. Every moved point retains left nullity eight and the same closure-membership pattern as its
representative.

Two exact implementations compute every tangent rank. The first applies the committed 32 by 32 base matrices from
the constant kernel-symmetry solve. The second independently applies the compact octonion derivations to the two
complex seven-vector blocks and appends the direct complex phase tangent. The implementations agree on all twenty
points.

| Orbit | Unit-section dimension | Representative rank | Ranks after exact noncompact moves | Maximum observed rank | Generic local quotient dimension |
| --- | ---: | ---: | --- | ---: | ---: |
| `W8` | 23 | 12 | 15, 15, 15 | 15 | 8 |
| E8-bar | 21 | 12 | 12, 15, 15 | 15 | 6 |
| `Iso` | 21 | 15 | 15, 15, 15 | 15 | 6 |
| `X_+` | 19 | 12 | 12, 15, 15 | 15 | 4 |
| `X_-` | 19 | 12 | 12, 15, 15 | 15 | 4 |

The pointwise rows are **Observed** in the result record. The generic statement is **Inferred** from those exact
rows: rank fifteen is the largest possible rank of the fifteen-generator tangent matrix, and the nonvanishing of a
maximal minor persists on an open neighborhood. Therefore every orbit has generic compact tangent rank fifteen. The
local dimensions of the principal compact-orbit quotients are the unit-section dimensions minus fifteen, namely
eight on `W8`, six on E8-bar and `Iso`, and four on both `X` branches.

The representative data also expose a real compact-orbit refinement inside four complex orbits. The recorded points
of `W8`, E8-bar, `X_+`, and `X_-` have rank twelve even though each orbit contains rank-fifteen points. The recorded
`Iso` point already lies in the full-rank locus. The calculation does not yet identify every lower-rank compact
stratum.

The falsifier was a disagreement between the two exact rank implementations, a moved point that changed nullity or
open-orbit membership, failure to reach the full compact rank on any orbit, or a phase-deletion mutation that left
every downstream rank unchanged. None occurred. The mutation lowers at least one computed tangent rank.

## `W8` has a complete eight-dimensional invariant quotient

Write the original complex seven-vector blocks as

`u=a+i b,  v=c+i d`.

The open `W8` orbit satisfies

`u dot u=v dot v=q!=0,  u dot v=0`.

The unit condition is

`norm(a)^2+norm(b)^2+norm(c)^2+norm(d)^2=1`.

A common phase multiplies `q` by its square. Choose a phase that makes `q=r>0`; the two choices differ by the
residual phase `-1`, which sends `(a,b,c,d)` to `(-a,-b,-c,-d)`. In this phase slice the real Gram matrix has the
exact form

```text
G(r,A,E,F) =
[[A,   0,  E,  F],
 [0, A-r, -F,  E],
 [E,  -F,  C,  0],
 [F,   E,  0, C-r]],

C = 1/2+r-A.
```

Consequently the Gram part of the quotient is the four-dimensional spectrahedron

`B_W={G(r,A,E,F) positive semidefinite: r>0}`.

The trace-one condition is already built into the displayed value of `C`. Positive definiteness gives the
real-frame-rank-four interior; matrix ranks three and two give its boundary strata. The exact producer reconstructs
this matrix from every fixture rather than accepting the formula as a pass flag.

Gram data alone does not classify a real four-frame under compact `G_2`. Let

`tau_ijk=phi(x_i,x_j,x_k)` and `psi_1234=psi(x_1,x_2,x_3,x_4)`

for `(x_1,x_2,x_3,x_4)=(a,b,c,d)`, where `phi(x,y,z)=<x cross y,z>` is the octonion associative three-form. The
coassociative four-form is computed from

`psi(a,b,c,d)=<a cross b,c cross d>-<a,c><b,d>+<a,d><b,c>`.

Put `lambda=(tau_234,-tau_134,tau_124,-tau_123)`. The producer verifies the exact identity

`lambda^T G lambda + psi_1234^2 = det(G)`.

After Gram–Schmidt on a rank-four frame, the four `tau` values and `psi` therefore form a point of `S^4`. The
residual common sign reverses the four `tau` coordinates and fixes `psi`, so the fiber over the rank-four interior is

`S^4 / ((tau,psi)~(-tau,psi))`,

equivalently the suspension of `RP^3`. Over a rank-three Gram matrix, one normalized three-form value lies in
`[-1,1]` and the residual sign identifies its endpoints symmetrically; over rank two, Gram data is complete.

**Inferred completeness.** Equal Gram matrices give the same lexicographic Gram–Schmidt transformation. For rank at
most two, compact `G_2` transitivity on ordered orthonormal two-frames maps one frame to the other. For rank three,
map the first two orthonormal vectors, put `h=x_1 cross x_2`, and decompose the third as
`alpha h+w`. The value `alpha=phi(x_1,x_2,x_3)` is fixed by the invariants; the `SU(2)` stabilizer of the ordered
two-frame acts transitively on the unit sphere in the four-dimensional quaternionic complement, so it maps `w`.
For rank four with `abs(alpha)<1`, that normalization fixes the residual `SU(2)` element, and the remaining four form
coordinates determine the fourth orthonormal vector. At `abs(alpha)=1`, the first three vectors form an associative
three-frame and its `SU(2)` stabilizer is transitive on the complementary three-sphere. This proves that the displayed
data separates every compact `G_2` orbit. Quotienting by the explicit common phase proves that the stratified space
above is the `G_2 x U(1)` moduli space.

The exact differential supplies an independent local check. The five `W8` unit constraints have rank five, leaving
a 23-dimensional tangent space. On every moved point with compact tangent rank fifteen, the raw Gram-and-form
invariant differential has rank nine. Its level-set tangent kernel therefore has dimension fourteen, exactly the
compact `G_2` tangent rank; the phase supplies the ninth invariant direction before the final circle quotient.

The falsifier was a failure of the form identity or Gram reconstruction, a compact tangent that changed the raw
invariants, a generic raw invariant differential whose kernel exceeded the `G_2` tangent, two equal invariant tuples
with distinct rank-stratified normal forms, or survival of the four-form or one-block-phase mutation. None occurred.
The exact fixtures cover real frame ranks two, three, and four. The mutations respectively break the form identity
and the `W8` constraint derivative.

## No nullity-eight orbit is compact homogeneous

**Inferred.** A connected compact orbit has dimension at most fifteen. Each nullity-eight unit section has dimension
at least nineteen, and the exact probe reaches the upper bound fifteen. Consequently none of the five nullity-eight
orbits is transitive under the connected compact symmetry. This answers one standing program question but does not
classify the quotient spaces.

The falsifier was a unit section of dimension at most fifteen or an exact compact tangent rank above fifteen. The
committed unit-section dimensions are 23, 21, 21, 19, and 19, and every computed rank is at most fifteen.

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/compact-orbit-ranks-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/w8_orbit_moduli.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/w8_orbit_moduli.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/w8_orbit_moduli.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/w8-orbit-moduli-result.json
```

The measured `--check` wall times were 7.84 seconds for the compact-rank producer and 3.18 seconds for the `W8`
moduli producer on the 2026-10-26 build host with four workers. Each check builds the sorted, two-space-indented JSON
plus its final newline in memory, compares the UTF-8 bytes with the retained record, writes no repository file, and
exits nonzero on a difference.
