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

## Every partner of a nonzero doubly pure element is doubly pure

The zero scalar row seen in the 21 incidence-census frames is structural. Write the repository bordered matrix as

`A(z, conjugate(z)) = [[0, -conjugate(z)^T], [conjugate(z), C_z]]`.

The exact [`partner_purity.py`](partner_purity.py) replay reconstructs `C_z` directly from the repository
Cayley-Dickson signs and matches the interior block of the bordered-matrix implementation. It verifies symbolically
that `C_z` is skew and `C_z z=0`; hence `z^T C_z=0`. If the complex kernel vector `(a,u)` represents a partner, its
lower kernel equation is

`a conjugate(z) + C_z u = 0`.

Multiplication by `z^T` gives `a z^T conjugate(z)=0`. On the real A_5 locus, the second factor is the sum of the 30
squares of the real and imaginary coordinates of `z`, so the factor is positive for a nonzero left element.
**Inferred:** `a=0`, and inversion of the split-complex coordinate map gives zero `e_0` and `e_16` coordinates for
every partner. The antiholomorphic derivative occupies only the scalar border, so its restriction to every such
kernel vanishes. The item-1 complex-linearity conclusion therefore holds at every nonzero doubly pure boundary point,
while higher-order and real curve-selection questions remain open.

The falsifier was a mismatch with the repository bordered block, a failure of skew-symmetry or either annihilator
identity, a Hermitian pairing unequal to the Euclidean sum of squares, a partner-coordinate term surviving the
projection, or a surviving input mutation. Flipping the Cayley-Dickson signs for the `e_1 e_2` skew pair preserves
skew-symmetry but changes `C_z z` and leaves `-2 u_1 z_2 z_3 + 2 u_2 z_1 z_3` in the projected equation. Evidence:
[`partner-purity-result.json`](partner-purity-result.json) and the [ledger](ledger.md#ledger-rows).

## The bordered kernel is a Hermitian hyperplane in the holomorphic kernel at every retained sample

For the holomorphic, skew, linear block `C_z`, the proposed replacement for the bordered kernel is

`ker C_z = C z (+) ker A(z, conjugate(z))`,

where the bordered kernel is identified with the Hermitian complement of `z` in `ker C_z`. The exact
[`holomorphic_kernel_lemma.py`](holomorphic_kernel_lemma.py) replay checks this description at all nine
path-supported nullity-twelve basepoints and at parameters 1, 2, and 3 on all 33 retained nullity-eight arcs. It also
checks the coordinate-isotropic-plane representative of each nullity-sixteen orbit so that every claimed rank occurs
in the retained result.

Gaussian-rational row reduction and an independent python-flint rational rank of the realified matrices agree at all
110 samples. The nullity-eight arc samples have `rank C_z=10` and `dim ker C_z=5`; the nullity-twelve basepoints have
rank 8 and kernel dimension 7; the two nullity-sixteen fixtures have rank 6 and kernel dimension 9. At every sample,
`C_z z=0`, the Hermitian pairing with `z` has rank one on `ker C_z`, and its complement has complex dimensions 4, 6,
or 8 respectively. Direct exact span comparison identifies that complement with the kernel of the bordered matrix
and identifies `ker C_z` with its orthogonal direct sum with `C z`.

The falsifier was a wrong `C_z` rank, nonzero `C_z z`, a mismatch between the bordered kernel and the Hermitian
complement, a failed direct-sum comparison, disagreement between Gaussian-rational and FLINT ranks, or a pairing
mutation that preserves the bordered kernel. At each sample the producer replaces `z` in the pairing by the first
recorded vector of `ker C_z` independent of `z`; all 110 mutated complements differ from the bordered kernel. The
capped producer took 1.55 seconds wall time and 39,100 KiB peak resident memory. This finite verification supports the
holomorphic reformulation on the retained exact sample set; it neither proves the lemma at every stratum point nor
computes a holomorphic Gauss fiber. Evidence:
[`holomorphic-kernel-lemma-result.json`](holomorphic-kernel-lemma-result.json) and the
[ledger](ledger.md#ledger-rows).

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
cone, or a surviving mutation. Deleting the first independent tangent-cone generator for `W8` to `B9` changes the
recomputed linear tangent dimension from three to four, so the mutation fails. Evidence:
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
surviving restricted-form mutation. All baseline checks pass. Replacing the rank-two `W8`-to-`B9` restricted form by
zero changes the projected effective rank to zero, removes the retained first-order four-plane comparison, and fails.
Evidence:
[`first_order_normal_cones.py`](first_order_normal_cones.py),
[`first-order-normal-cones-result.json`](first-order-normal-cones-result.json), and the
[ledger](ledger.md#ledger-rows).

## Second jets can change the limiting plane on a fixed first-order direction

The seven exceptional first-order rows need the Schur-corrected form

`F^T A(e) F + C_1^T B_0^-1 C_1`

for an arc with first coefficient `d` and second coefficient `e`. The exact
[`schur_degeneracy_witnesses.py`](schur_degeneracy_witnesses.py) replay supplies two degree-at-most-two arcs at the
path-supported point of every exceptional incidence. All 14 arcs remain in the declared source closure, enter its
nullity-8 orbit away from the boundary, and have projectively nonzero normal projections on the coordinate-slice
tangent cone. Every projected first-order form vanishes. Every Schur-corrected form is skew of rank two and yields a
four-plane inside the six-dimensional boundary kernel. Every approach already retained by the nullity-8 record
reproduces its retained plane.

Five paired limits agree. The two E8-bar-to-`VB` directions give distinct four-planes with two-dimensional
intersection. The sharper result occurs for `W8` to `VB`: two exact quadratic arcs have the same projective first
coefficient and different second coefficients, but their four-planes intersect in dimension three. Thus the
projective first-order degeneracy direction does not determine the limit plane. The control pair for `Iso` to `VB`
also fixes its first coefficient and varies its second coefficient, but both arcs give the same plane. Higher-jet
dependence is incidence-specific.

The exact-arc family is a lower bound on each Gauss fiber. The replay does not classify every formal arc above the
coordinate-slice degeneracy locus and does not supply the required two-sided real curve-selection certificate. The
falsifier was an exact arc leaving its declared source or nullity, a projected direction outside the tangent cone or
with nonzero first-order rank, a non-skew or wrong-rank Schur form, a retained-plane mismatch, a pairwise equality
inconsistent with exact union rank, an overstated completeness claim, or a surviving Schur-block mutation. Deleting
`C_1^T B_0^-1 C_1` from the E8-bar-to-`V^a_+` witness changes the effective rank from two to six and fails. Evidence:
[`schur-degeneracy-witnesses-result.json`](schur-degeneracy-witnesses-result.json) and the
[ledger](ledger.md#ledger-rows).

## The reduced positive-sign X-to-VB modular elimination exceeds the five-minute gate

The reduced construction parameterizes the smooth transverse germ by three holomorphic conic parameters and three
formal-conjugate parameters. It forms the fifteen augmented-Pfaffian numerators as Gaussian pairs of python-flint
`fmpz_mpoly` values, removes the common pivot-Pfaffian factor because its value at the origin is the local unit
`-60 I`, and presents the Rees graph with fifteen Plucker coordinates and one auxiliary. The resulting elimination
has 22 variables. The coordinates have total degree at most 26 and at most 560 terms in either Gaussian component.

The exact pre-elimination controls pass: the conic chart has Jacobian rank three and a verified rational inverse; the
boundary matrix has rank ten; an admitted real sample has bordered rank twelve and rank-two augmented-Pfaffian form;
all fifteen polynomial Plucker relations vanish; and the retained null-fiber arc has order two and reproduces its
recorded Schur vector. Zeroing the first nonzero augmented-Pfaffian generator breaks the arc comparison.

Singular modulo 32003 reached the 300-second gate and was terminated after 300.879 seconds without producing a
fiber, so the producer skipped characteristic zero. The outer `/usr/bin/time -v` measurement reports 5:01.59 wall
time and 43,240 KiB peak resident memory for the Python controller. The killed inner timing wrapper emitted no
Singular peak-resident-memory report, so the elimination process's peak remains unmeasured. This cost record proves
neither a complex-algebraic exceptional fiber nor the real semialgebraic Gauss fiber. Completion within five minutes
and 16 GiB, or any claimed fiber from this record, falsifies the recorded outcome. The holomorphic-kernel
formulation supersedes this real elimination, so its cost record is not retained; the
[ledger](ledger.md#ledger-rows) row 2g carries the measurement.

## Investigated questions

### Does the antiholomorphic first-order part survive on a boundary kernel?

The question matters because a surviving antiholomorphic restriction would make the first-order Gauss map only
real-linear and would rule out a complex-algebraic description at that order. The cheapest decisive probe splits the
bordered-matrix derivative and restricts its antiholomorphic part to exact kernel frames at canonical and moved
points. The restriction vanishes at all 21 points, for the scalar-row mechanism above. A nonzero restriction at any
exact point falsifies the result. Evidence: [`incidence-census-result.json`](incidence-census-result.json).

### Is the zero scalar row sampled or structural?

The question matters because a sampled vanishing result gives no control between tested representatives. The cheapest
decisive probe is the symbolic projection of the bordered-kernel equation above. **Inferred:** every partner of every
nonzero doubly pure element has zero scalar coordinate, so the antiholomorphic restriction vanishes on the whole
nonzero locus. A valid partner with nonzero `e_0` or `e_16` coordinate, or a failed identity in the retained proof
record, falsifies the result. Evidence: [`partner-purity-result.json`](partner-purity-result.json).

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

### Which exceptional passages are invisible on their whole first-order tangent cone?

The question matters because an isolated base direction needs a local correction, whereas an identically zero map
needs a full second-order model. The cheapest decisive probe compares the first-order image dimension with the
tangent-cone and zero-fiber dimensions. E8-bar, `X_+`, and `X_-` into `VB` have empty projective first-order images;
their zero fibers equal their whole tangent cones. A nonzero effective form on any of those three cones falsifies the
result. Evidence: [`first-order-normal-cones-result.json`](first-order-normal-cones-result.json).

### Do the two E8-bar sheets collapse to one first-order image component?

The question matters because a collapse would identify the sheetwise attaching data before higher-order corrections.
The cheapest probe compares the minimal components of each two-sheet germ with the eliminated image. Along `V`,
`V^a_+`, and `V^a_-`, both the germ and the first-order image have two minimal components. **Inferred:** the sheets
therefore have distinct first-order image closures: the Zariski-continuous image of an irreducible sheet has
irreducible closure, so two image components cannot come from one collapsed common closure. The statement does not
exclude higher-order intersections or equality after adding exceptional limits. A radical replay yielding one image
component, or a sheet mapping wholly into the other sheet’s image, falsifies the result. Evidence:
[`first-order-normal-cones-result.json`](first-order-normal-cones-result.json) and the
[regularity record](../a5-strata-regularity/README.md#theorem-6-transverse-germs).

### Does a first-order degeneracy direction determine its higher-order plane?

The question matters because a positive answer would make one normal blow-up sufficient after a pointwise correction.
The cheapest decisive probe fixes the first coefficient and varies exact second coefficients. The `W8`-to-`VB`
witnesses give different four-planes with three-dimensional intersection, so the answer is negative in general. The
`Iso`-to-`VB` control pair gives the same plane, so second-jet dependence is not automatic. Equality of the two `W8`
planes, or failure of either exact arc, falsifies the result. Evidence:
[`schur-degeneracy-witnesses-result.json`](schur-degeneracy-witnesses-result.json).

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/incidence_census.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/incidence_census.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/incidence_census.py \
    --check docs/evidence/a5-kernel-attachments/incidence-census-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/partner_purity.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/partner_purity.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/partner_purity.py \
    --check docs/evidence/a5-kernel-attachments/partner-purity-result.json
prlimit --as=17179869184 -- "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-attachments/holomorphic_kernel_lemma.py --self-test
prlimit --as=17179869184 -- "$PYTHON" -B -W error -O \
    docs/evidence/a5-kernel-attachments/holomorphic_kernel_lemma.py --self-test
prlimit --as=17179869184 -- "$PYTHON" docs/evidence/a5-kernel-attachments/holomorphic_kernel_lemma.py \
    --check docs/evidence/a5-kernel-attachments/holomorphic-kernel-lemma-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/path_supported_basepoints.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/path_supported_basepoints.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/path_supported_basepoints.py \
    --check docs/evidence/a5-kernel-attachments/path-supported-basepoints-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/first_order_normal_cones.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/first_order_normal_cones.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/first_order_normal_cones.py \
    --check docs/evidence/a5-kernel-attachments/first-order-normal-cones-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/schur_degeneracy_witnesses.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-attachments/schur_degeneracy_witnesses.py --self-test
"$PYTHON" docs/evidence/a5-kernel-attachments/schur_degeneracy_witnesses.py \
    --check docs/evidence/a5-kernel-attachments/schur-degeneracy-witnesses-result.json
```

The `--check` command constructs the sorted, two-space-indented JSON plus its final newline in memory and compares
the UTF-8 bytes with the retained record. The command writes no record. The result contains integers, rationals,
exact symbolic expressions, and booleans; it contains no floating-point observations.
