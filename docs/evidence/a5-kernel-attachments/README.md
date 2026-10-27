# A_5 partner-sphere attachments

This record studies the attaching data of the partner-sphere bundles across the nullity-changing closure incidences
of the A_5 zero-divisor strata. The [program](../../design/a5-kernel-attachments-program.md) defines the ordered
deliverables and the claim boundary. Every result below names its falsifier and retained evidence.

## The first-order effective forms are complex-linear at the tested boundary points

The exact [incidence census](incidence-census-result.json) derives 33 nullity-changing incidences from the committed
closure order rather than copying a frontier table: 15 passages from nullity 8 to 12, 8 passages from nullity 12 to
16, and 10 passages from nullity 8 to 16. The producer tests the canonical representative and two exact moved points
of each of the seven boundary orbits. One moved point uses a rational unipotent `G_2(C)` automorphism whose 60
candidate nilpotent derivations span the 14-dimensional derivation algebra; the other uses the rational boost with
`c=5/4` and `s=3/4`. All 21 points retain the expected closure-membership pattern and real left nullity.

Write the bordered skew matrix as

`A(z, conjugate(z)) = A^(1,0)(z) + A^(0,1)(conjugate(z))`.

The antiholomorphic part occupies only the scalar border. At every tested point, an exact principal-Pfaffian frame
`F` of the boundary kernel has zero scalar-coordinate row. The producer also multiplies the matrices directly and
obtains

`F^T A^(0,1)(conjugate(d)) F = 0`

identically in all 15 ambient directions. The retained point rows record both exact restricted matrices. Therefore
all 33 incidence rows have a complex-linear first-order effective form at their three tested boundary points, and no
verdict reverses under either non-compact move. This exact first-order certificate does not establish that a closed
Gauss-graph fiber is complex-algebraic: higher-order effective forms, the real curve-selection image, and variation
over the rest of each boundary orbit remain open.

The falsifier was a closure-derived incidence missing from the census; a point leaving its declared boundary orbit or
source closure; a wrong nullity; a nonzero scalar-coordinate frame row; a nonzero restricted antiholomorphic form; a
moved point reversing the verdict; or a surviving input mutation. The producer adds `a_1(E_12-E_21)` to the
antiholomorphic derivative input. The restriction at the canonical `B9` point becomes nonzero, the complex-linearity
verdict changes, and the mutation fails the baseline check. Evidence: [`incidence_census.py`](incidence_census.py),
[`incidence-census-result.json`](incidence-census-result.json), and the
[item-1 ledger row](ledger.md#ledger-rows).

## Nine exact basepoints support all retained nullity-8 degenerations

The retained nullity-8 paths do not all end at the canonical representatives used by the regularity record. Directly
identifying those kernels would assume a lift of a non-compact rank-stratum symmetry that the kernel-symmetry record
rules out. The [basepoint certificate](path-supported-basepoints-result.json) instead groups the 33 retained paths by
their literal boundary coefficients and selects a path-supported point for each of the 15 incidences. Nine distinct
exact points suffice.

At every selected point, [`path_supported_basepoints.py`](path_supported_basepoints.py) recomputes the closure pattern,
real left nullity, orbit dimension, and a coordinate slice complementary to the exact orbit tangent space. A bounded
Singular deformation to the normal cone then reproduces the germ dimension, multiplicity, embedding dimension, and
component count recorded at the canonical representative. Every retained path direction projects into that
point-specific tangent cone. This establishes an exact input surface for the subsequent Gauss-map computations; it
does not transport a kernel between points and does not yet determine any full limit set.

The falsifier was a missing path-supported point, a wrong orbit pattern or nullity, a non-complementary slice, a local
invariant differing from the orbit-constant regularity result, an admitted direction outside the recomputed tangent
cone, or a surviving mutation. Adding the split middle-coordinate direction to the retained `W8`-to-`B9` path makes
the curve leave the `W8` closure and its tangent cone, so the mutation fails. Evidence:
[`path_supported_basepoints.py`](path_supported_basepoints.py),
[`path-supported-basepoints-result.json`](path-supported-basepoints-result.json), and the
[ledger](ledger.md#ledger-rows).

## Eight first-order maps resolve after one blow-up

At each path-supported point, [`first_order_normal_cones.py`](first_order_normal_cones.py) restricts the linear
bordered-matrix derivative to the exact six-dimensional boundary kernel. A bounded Singular calculation eliminates
the transverse tangent cone through independent coordinates of that skew form. Every rank-four Pfaffian reduces to
zero, so each nonzero image form has rank two and its kernel is a four-plane. The retained path limits agree with
those kernel planes whenever their first-order form is nonzero.

The [retained result](first-order-normal-cones-result.json) gives the following complex-projective first-order images.
“None” in the degeneracy column means that only the affine cone vertex maps to zero. An empty image means that the
first-order map vanishes on the whole tangent cone; its displayed affine scheme can still be nonreduced at the origin.

| Incidence | First-order image: dimension, degree, components | Projective degeneracy dimension | First-order outcome |
| --- | --- | ---: | --- |
| E8-bar to `B9` | 1, 2, 1 | none | one blow-up resolves |
| E8-bar to `V` | 2, 2, 2 | none | one blow-up resolves |
| E8-bar to `VB` | empty; degree-4 origin, 1 component | 3 | identically zero; higher order required |
| E8-bar to `V^a_+` | 2, 2, 2 | 0 | higher order required at one projective direction |
| E8-bar to `V^a_-` | 2, 2, 2 | 0 | higher order required at one projective direction |
| `Iso` to `B9` | 1, 1, 1 | none | one blow-up resolves |
| `Iso` to `VB` | 1, 1, 1 | 1 | higher order required |
| `W8` to `B9` | 2, 1, 1 | none | one blow-up resolves |
| `W8` to `VB` | 1, 1, 1 | 2 | higher order required |
| `X_+` to `B9` | 0, 1, 1 | none | one blow-up resolves to the known canonical plane |
| `X_+` to `VB` | empty; reduced origin | 2 | identically zero; higher order required |
| `X_+` to `V^a_+` | 2, 2, 2 | none | one blow-up resolves |
| `X_-` to `B9` | 0, 1, 1 | none | one blow-up resolves to the known canonical plane |
| `X_-` to `VB` | empty; reduced origin | 2 | identically zero; higher order required |
| `X_-` to `V^a_-` | 2, 2, 2 | none | one blow-up resolves |

Thus eight first-order maps have no projective base direction, while seven need a higher-order exceptional analysis.
The `VB` passages from E8-bar and both `X` branches are stronger than isolated degeneracies: their full tangent cones
map to zero at first order. This table is an exact complex-algebraic upper bound on the first-order limits. It does not
prove that real exact arcs fill each image, and it omits every additional plane produced over a degeneracy direction;
the table therefore remains short of the two-sided semialgebraic certificate required for deliverable 1.

The falsifier was a basepoint or germ mismatch, a surviving rank-four Pfaffian, a retained path outside the tangent
cone, a first-order plane differing from its retained exact limit, an incorrectly empty degeneracy locus, or a
surviving geometric-input mutation. All baseline checks pass. The middle-coordinate mutation of the
`W8`-to-`B9` path leaves the closure and tangent cone and fails. Evidence:
[`first_order_normal_cones.py`](first_order_normal_cones.py),
[`first-order-normal-cones-result.json`](first-order-normal-cones-result.json), and the
[ledger](ledger.md#ledger-rows).

## Investigated questions

### Does the antiholomorphic first-order part survive on a boundary kernel?

The question matters because a surviving antiholomorphic restriction would make the first-order Gauss map only
real-linear and would rule out a complex-algebraic description at that order. The cheapest decisive probe splits the
bordered-matrix derivative and restricts its antiholomorphic part to exact kernel frames at canonical and moved
points. The restriction vanishes at all 21 points, for the scalar-row mechanism above. A nonzero restriction at any
exact point falsifies the result. Evidence: [`incidence-census-result.json`](incidence-census-result.json).

### Can canonical-representative local data be applied to every retained degeneration?

The question matters because the non-compact stratum symmetry does not lift to kernels, and several retained paths
end at exact points different from the canonical regularity representatives. The cheapest decisive probe groups paths
by their literal boundary coefficients and recomputes the transverse germ at the selected points. Nine exact points
support all 33 paths and reproduce every tested orbit and germ invariant. The result licenses point-specific local
analysis, not kernel transport. A mismatched local invariant or a path outside the recomputed tangent cone falsifies
the result. Evidence: [`path-supported-basepoints-result.json`](path-supported-basepoints-result.json).

### Does one blow-up resolve every nullity-8 to nullity-12 kernel Gauss map?

The question matters because a projective direction on which the first-order form vanishes carries additional
higher-order limits. The cheapest decisive probe eliminates each tangent cone through the exact first-order form and
measures the zero fiber. Eight incidences have no projective zero direction, while seven do. Three of those seven have
an identically zero first-order map. Therefore one blow-up does not resolve the whole family. A nonempty degeneracy
locus in any of the eight resolved rows, or an empty locus in a row classified exceptional, falsifies the result.
Evidence: [`first-order-normal-cones-result.json`](first-order-normal-cones-result.json).

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/incidence_census.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/incidence_census.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/incidence_census.py \
    --check docs/evidence/a5-kernel-attachments/incidence-census-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/path_supported_basepoints.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/path_supported_basepoints.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/path_supported_basepoints.py \
    --check docs/evidence/a5-kernel-attachments/path-supported-basepoints-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/first_order_normal_cones.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/first_order_normal_cones.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/first_order_normal_cones.py \
    --check docs/evidence/a5-kernel-attachments/first-order-normal-cones-result.json
```

The `--check` command constructs the sorted, two-space-indented JSON plus its final newline in memory and compares
the UTF-8 bytes with the retained record. The command writes no record. The result contains integers, rationals,
exact symbolic expressions, and booleans; it contains no floating-point observations.
