# A_5 kernel bundles on the nullity-eight strata

This evidence directory executes the
[nullity-eight kernel-bundle program](../../design/a5-kernel-bundles-nullity8-program.md). The first exact result
computes the connected compact `G_2 x U(1)` tangent ranks on the five complex nullity-eight orbits from the
[regularity record](../a5-strata-regularity/README.md): `W8`, E8-bar, the isotropic orbit `Iso`, and the two branches
`X_+` and `X_-`. The record also gives complete compact-orbit invariants and moduli spaces for all five orbits.
Unit-section topology, transition data, and bundle classes remain open.

Every calculation uses integer or rational arithmetic. [`compact-orbit-ranks-result.json`](compact-orbit-ranks-result.json)
is the output of [`compact_orbit_ranks.py`](compact_orbit_ranks.py) `--out`, and
[`w8-orbit-moduli-result.json`](w8-orbit-moduli-result.json) is the output of
[`w8_orbit_moduli.py`](w8_orbit_moduli.py) `--out`, and
[`remaining-orbit-moduli-result.json`](remaining-orbit-moduli-result.json) is the output of
[`remaining_orbit_moduli.py`](remaining_orbit_moduli.py) `--out`. Each producer carries a byte-exact `--check` and
mutation-bearing `--self-test`.

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

## The remaining four moduli are complete invariant-image quotients

The same ordered real four-frame

`(a,b,c,d)=(Re(u),Im(u),Re(v),Im(v))`

describes E8-bar, `Iso`, `X_+`, and `X_-`. Before the common-phase quotient, its real Gram matrix, four associative
three-form values, and coassociative four-form value form a complete compact `G_2` invariant. E8-bar also requires
the middle complex coordinate `mu`, which compact `G_2` fixes. The rank-stratified Gram-Schmidt normal-form argument
given for `W8` applies to every ordered real four-frame, so restricting the invariant map to any one of these four
orbits preserves completeness.

The common phase acts on the frame by

```text
(a,b,c,d) -> (cos(t)a-sin(t)b, sin(t)a+cos(t)b,
              cos(t)c-sin(t)d, sin(t)c+cos(t)d).
```

If `T(t)=diag(R(t),R(t))`, the Gram matrix transforms as `G -> T(t) G T(t)^T`, the associative values transform by
the third exterior power of `T(t)`, and the coassociative value stays fixed because `det(T(t))=1`. The middle pair
`(Re(mu),Im(mu))` transforms by `R(t)`. The producer checks this action exactly at a quarter turn on every fixture.

The resulting moduli spaces are therefore the following explicit invariant-image quotients:

- E8-bar: the complete invariant image in the unique phase gauge `mu>0` real. The open orbit has `mu!=0`, because
  its representative has nonzero `mu` and the `H` action only rescales that coordinate by a nonzero scalar.
- `Iso`: the complete invariant image of its unit section modulo the displayed circle action.
- `X_+` and `X_-`: the corresponding complete invariant images modulo the same circle action.

These descriptions retain the orbit equations as the defining restrictions on the invariant images; they do not
replace those images by an unproved ball or manifold model. Their principal dimensions follow from exact tangent
ranks:

| Orbit | Unit-section tangent dimension | Raw `G_2` invariant rank | Raw level-set dimension | Phase-quotient dimension |
| --- | ---: | ---: | ---: | ---: |
| E8-bar | 21 | 7 | 14 | 6 |
| `Iso` | 21 | 7 | 14 | 6 |
| `X_+` | 19 | 5 | 14 | 4 |
| `X_-` | 19 | 5 | 14 | 4 |

The table is **Observed** at every fixture with compact tangent rank fifteen. The fixtures also cover real-frame
ranks three and four on E8-bar and both `X` branches, and rank four on `Iso`. The equality between the
fourteen-dimensional invariant level-set kernel and the compact `G_2` tangent supplies the local completeness check;
the normal-form argument supplies global separation.

The falsifier was an incorrectly sized unit-section tangent, motion of an invariant along compact `G_2`, a generic
level-set kernel larger than the compact `G_2` tangent, failure of the phase direction to remove one quotient
dimension, disagreement with the explicit quarter-turn action, failure of the rank-stratified normal form, or
survival of a tangent or four-form mutation. The exact checks satisfy each measured condition. The planted
one-block phase leaves the orbit tangent, and deletion of the four-form correction breaks the form identity.

## Exact samples expose two `SU(2)` fiber representations

[`stabilizer-fiber-samples-result.json`](stabilizer-fiber-samples-result.json) solves the connected compact point
stabilizer on the representative and three exact noncompact moves in each nullity-eight orbit. For each point, the
producer independently recomputes the compact tangent rank, constructs a `J`-adapted basis of the complex rank-four
kernel, restricts the stabilizer's domain action to that basis, and verifies kernel preservation and every represented
Lie bracket.

Thirteen fixtures have full compact tangent rank fifteen. Their connected stabilizer is trivial, as the open-rank
condition also proves generically, and the fiber is `4 V_0` for the trivial group. Seven lower-rank fixtures have
compact tangent rank twelve, zero-dimensional stabilizer center, three-dimensional derived algebra, and a
negative-definite Killing form. Their connected stabilizer is `SU(2)`: each fiber contains an odd-highest-weight
doublet, so the represented group does not factor through `SO(3)`.

The inverse-Killing Casimir separates two fiber types:

| Orbit and sampled compact stratum | Connected stabilizer | Complex rank-four fiber |
| --- | --- | --- |
| `W8`, recorded representative | `SU(2)` | `2 V_1` |
| E8-bar, representative and first unipotent move | `SU(2)` | `2 V_0 + V_1` |
| `X_+`, representative and first unipotent move | `SU(2)` | `2 V_0 + V_1` |
| `X_-`, representative and first unipotent move | `SU(2)` | `2 V_0 + V_1` |
| every sampled rank-fifteen point | trivial | `4 V_0` |

For `2 V_1`, the Casimir spectrum is `3/8` with multiplicity four. For `2 V_0+V_1`, the spectrum is zero with
multiplicity two and `3/8` with multiplicity two. The different representations refute a single universal fiber
type for all `SU(2)` stabilizer loci. The result is **Observed** on the twenty exact fixtures. The open-rank argument
proves the trivial connected stabilizer on a generic neighborhood in every orbit. The samples do not yet prove that
the zero and `su(2)` algebras exhaust all compact stabilizer strata, nor do they locate every jump locus in the
complete invariant quotients.

The falsifier was a stabilizer dimension different from fifteen minus the independent tangent rank, a stabilizer
direction moving the point or escaping the kernel, failure to commute with `J`, a represented-bracket mismatch, or a
mutation that survived. Those checks pass. The proposed constancy across all `SU(2)` samples fails in the measured
way above and therefore becomes a required orbit-specific stratum distinction. The moving-direction and perturbed
fiber-action mutations fail the point-fixing and bracket checks, respectively.

## Frame rank, associativity, and phase fixed points give all connected stabilizer strata

The complete invariant coordinates turn stabilizer classification into two finite conditions. First, a connected
phase projection must fix the complete `G_2` invariant tuple. Second, after the phase projection is removed, the
stabilizer is the pointwise compact `G_2` stabilizer of the real frame.

The phase projection vanishes on `W8`, E8-bar, `X_+`, and `X_-`. On `W8`, the nonzero common complex-bilinear square
rotates with phase weight two. E8-bar has nonzero `mu`, which rotates with phase weight one. Each open `X` branch lies
outside `Iso`, so at least one complex-bilinear pairing is nonzero and again has phase weight two. Any of these
nonzero scalars forces the infinitesimal phase coefficient to vanish.

The standard compact `G_2` frame isotropy gives the remaining classification. The pointwise stabilizer is `SU(2)`
for a real two-frame and for an associative real three-frame. It is trivial for a nonassociative real three-frame or
for a frame of rank at least four. For a rank-three frame, associativity is expressed entirely in the recorded
invariants: for any independent triple of frame vectors,

`phi(x_i,x_j,x_k)^2 = det(G_{ijk})`.

The orbit equations give the frame-rank minima. `W8` has rank at least two. E8-bar and both `X` branches have rank at
least three, because at rank at most two their cross-product equation forces a lower orbit. The open `Iso` orbit has
rank four, because a positive real three-plane cannot contain two independent complex-isotropic vectors after
complexification.

`Iso` is the exceptional phase case. Its isotropic equations make the Gram matrix circle-fixed, and the
coassociative four-form is always fixed. The third exterior power of the common phase rotation fixes the four
associative three-form values exactly when all four vanish. At such a point the real frame has rank four and hence
trivial pointwise stabilizer. Completeness of the invariant tuple then gives a unique compensating `G_2` element for
each phase; uniqueness makes these elements a circle homomorphism. Thus the connected stabilizer is the graph of
`U(1)`. Away from this coassociative locus, the connected stabilizer is trivial.

The full connected-stratum list is:

| Orbit | Invariant locus | Connected stabilizer | Complex rank-four fiber |
| --- | --- | --- | --- |
| `W8` | real-frame rank two or associative rank three | `SU(2)` | `2 V_1` |
| `W8` | nonassociative rank three or rank four | trivial | `4 V_0` |
| E8-bar | associative rank three | `SU(2)` | `2 V_0 + V_1` |
| E8-bar | rank four | trivial | `4 V_0` |
| `Iso` | all four associative three-form values zero | `U(1)` | `C_0 + 2 C_(-3) + C_(-2)` |
| `Iso` | associative three-form vector nonzero | trivial | `4 V_0` |
| `X_+`, `X_-` | associative rank three | `SU(2)` | `2 V_0 + V_1` |
| `X_+`, `X_-` | rank four | trivial | `4 V_0` |

[`stabilizer-strata-result.json`](stabilizer-strata-result.json) checks this criterion against all twenty prior
fixtures and adds exact canonical points for the missing loci. The associative rank-three `W8` frame
`(e_1,(3/5)e_3,(4/5)e_2,0)` remains in the open orbit and has the same `2 V_1` fiber as the rank-two point. A
deterministic enumeration finds seven coordinate coassociative four-planes. One signed complex null two-plane on
each plane lies in open `Iso`, has compact tangent rank fourteen, and gives the same phase-normalized circle weights
`0,-3,-3,-2`; the opposite sign lies on `B9`. These rows establish that the `Iso` circle locus is nonempty and that
the weights agree across all seven coordinate realizations.

The falsifier was a frame below the claimed rank minimum, a phase projection away from the circle-fixed invariant
locus, an unclassified open-`Iso` circle fixed point, disagreement between the rank/associativity criterion and an
exact compact rank, or survival of a three-form or phase-projection mutation. The twenty sampled rows and eight new
canonical rows satisfy the classification. Ignoring the three-form vector misclassifies sampled `Iso` points, and
deleting the measured phase projection misclassifies every coassociative `Iso` point.

## Thirteen boundary incidences have path-dependent kernel limits

[`boundary-specializations-result.json`](boundary-specializations-result.json) covers all fifteen incidences from a
nullity-eight orbit to a nullity-twelve orbit in its committed closure table. The 33 exact paths include at least two
approaches to one verified point of every boundary orbit. After substitution into the closure generators, a path of
degree `e` gives polynomials of degree at most `e` times the largest generator degree. Vanishing at one more rational
parameter than that bound proves containment of the whole curve. Each boundary point has left nullity twelve, and
the samples at parameters one, two, and three have left nullity eight and the expected open-orbit pattern.

Write the bordered skew matrix along a path as

`A(t) = A_0 + t A_1 + t^2 A_2`.

The nullity-twelve boundary kernel `K_0` has complex dimension six. When the restriction of `A_1` to `K_0` has rank
two, its four-dimensional kernel is the limiting nullity-eight kernel. When the first restriction vanishes, the
producer instead takes the kernel of the second-order effective skew form

`D_2 + C_1^T B_0^-1 C_1`,

where `B_0` is an invertible principal block of `A_0`, `C_1` is the first-order coupling to that block, and `D_2` is
the restriction of `A_2` to `K_0`. Every effective form has rank two. Every resulting four-plane lies in `K_0`,
admits the required formal first-order lift, and has an exact two-dimensional complement in `K_0`.

Exact approaches to the same boundary point give different limiting four-planes in these thirteen incidences:

- E8-bar to `B9`, `V`, `VB`, `V^a_+`, and `V^a_-`;
- `Iso` to `B9` and `VB`;
- `W8` to `B9` and `VB`;
- `X_+` to `VB` and `V^a_+`;
- `X_-` to `VB` and `V^a_-`.

Each unequal pair is an **Observed** counterexample to a path-independent inclusion. The two remaining incidences,
`X_+` to `B9` and `X_-` to `B9`, have equal limits on the two exact approaches. **Inferred:** the inclusion is
canonical because the committed reduced transverse germ is a smooth one-dimensional normal line, rescaling its
nonzero normal parameter leaves the restricted-matrix kernel unchanged, changes along the orbit arise from group
curves tending to the identity, and the full three-dimensional constant-lift stabilizer of the boundary point
preserves the limiting plane. Thus a nullity-eight kernel is not canonically a subspace of the adjacent
nullity-twelve kernel in general; only these two incidences carry the canonical inclusion established here.

The two middle-coordinate sheets approaching each aligned E8-bar boundary `V^a_+` and `V^a_-` have the same
four-plane for the tested normal direction. A boundary-stabilizer unipotent move produces a four-plane whose
intersection with that sheet limit has dimension three, so each full incidence remains path-dependent. Equality of
the two tested sheet limits therefore supplies local attaching data but does not establish equality of the bundles
over the two sheets.

For each path, the producer also solves the connected compact stabilizer fixing every coefficient of the path and
decomposes the limiting plane, its quotient, and the full boundary kernel. Fourteen paths preserve `SU(2)` and give

`(2 V_0 + V_1) + V_1 = 2 V_0 + 2 V_1`.

The other nineteen paths have trivial preserved connected stabilizer and give

`4 V_0 + 2 V_0 = 6 V_0`.

All represented brackets agree, every limiting plane is invariant under its path stabilizer, and every direct sum
matches the independently decomposed boundary representation.

The falsifier was a missing declared incidence, an unproved degeneration, a boundary or nearby nullity other than
twelve or eight, a limiting or quotient dimension other than four or two, a plane escaping the boundary kernel, a
claimed canonical plane changed by another approach, a preserved stabilizer moving the plane, a representation sum
different from the boundary representation, or a surviving mutation. Adding a middle-coordinate term to the
`W8`-to-`B9` path breaks closure containment. Deleting the second-order Schur correction on the
E8-bar-to-`V^a_+` path changes the effective rank from two to six. Both mutations fail downstream checks.

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
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/remaining_orbit_moduli.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/remaining_orbit_moduli.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/remaining_orbit_moduli.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/remaining-orbit-moduli-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/stabilizer_fiber_samples.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/stabilizer_fiber_samples.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/stabilizer_fiber_samples.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/stabilizer-fiber-samples-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/stabilizer_strata.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/stabilizer_strata.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/stabilizer_strata.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/stabilizer-strata-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/boundary_specializations.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/boundary_specializations.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/boundary_specializations.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/boundary-specializations-result.json
```

The measured `--check` wall times were 7.84 seconds for the compact-rank producer and 3.18 seconds for the `W8`
moduli producer, and 1.94 seconds for the remaining-orbit producer on the 2026-10-26 build host with four workers.
The sampled stabilizer and representation producer checked in 9.19 seconds. Each check builds the sorted,
two-space-indented JSON plus its final newline in memory, compares the UTF-8 bytes with the retained record, writes
no repository file, and exits nonzero on a difference. The exhaustive stabilizer-stratum producer checked in 8.23
seconds. The boundary-specialization producer checked in 9.91 seconds.
