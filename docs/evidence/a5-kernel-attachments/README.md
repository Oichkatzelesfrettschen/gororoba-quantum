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

## Holomorphic Schur blow-ups reproduce all eight resolved first-order images

The exact [`holomorphic_gauss_fibers.py`](holomorphic_gauss_fibers.py) replay constructs the holomorphic `C_z`
matrix on the path-supported transverse slice of each first-order-resolved incidence. At every boundary point,
`C_z` has rank eight and the bordered matrix has rank ten. An exact principal eight-dimensional block `B(t)` has a
nonzero Pfaffian at the origin. In the fixed complement-plus-kernel basis, the replay forms the cleared seven-by-seven
Schur numerator

`Pf(B) D + C^T adj_Pf(B) C`.

Its 21 upper-triangle entries have common origin order one, total degree at most five, and at most 83 terms in either
Gaussian-rational component. Direct polynomial multiplication verifies `B adj_Pf(B)=Pf(B) I`, skew-symmetry, and
agreement between the exceptional restriction and the committed bordered first-order form.

The ordinary blow-up chart with exceptional coordinate `t_j` substitutes `t_j=e` and every other slice coordinate
as `e u_k`, removes the common factor `e`, and sets `e=0`. The producer implements the resulting exceptional
coordinates by taking the degree-one homogeneous Schur terms and setting `t_j=1`. Singular checks every affine
exceptional chart first modulo 32003 and then over `Q(i)`. Every nonempty chart is basepoint-free, every rank-four
Pfaffian vanishes on the exceptional divisor, and the two characteristics give the same image invariants:

| Incidence | Holomorphic exceptional fiber: projective dimension, degree, components |
| --- | --- |
| E8-bar to `B9` | 1, 2, 1 |
| E8-bar to `V` | 2, 2, 2 |
| `Iso` to `B9` | 1, 1, 1 |
| `W8` to `B9` | 2, 1, 1 |
| `X_+` to `B9` | 0, 1, 1 |
| `X_+` to `V^a_+` | 2, 2, 2 |
| `X_-` to `B9` | 0, 1, 1 |
| `X_-` to `V^a_-` | 2, 2, 2 |

These dimension, degree, and component triples equal the committed first-order image triples. All 17 retained arc
directions give a nonzero exceptional point. Because the exceptional coordinates have no projective basepoint on
these eight tangent cones, the holomorphic kernel map extends after the single ordinary blow-up, and its exceptional
fiber is the projectivization of the displayed image. The replay does not cover the seven incidences with a
first-order base locus, variation along a boundary orbit, or the global bordered-kernel Gauss fiber beyond the
holomorphic-kernel identification established on the retained sample set.

The falsifier was a wrong boundary rank or zero pivot Pfaffian; a failed Pfaffian-adjugate, skewness, or bordered-form
comparison; a surviving rank-four Pfaffian; a nonempty exceptional chart retaining a basepoint; a modular or rational
dimension, degree, or component count differing from the committed image; a retained arc with zero exceptional
coordinates; or a derivative-input mutation that leaves the map resolved. Deleting the `t2` coefficient from the
`W8`-to-`B9` holomorphic slice input creates a one-dimensional affine degeneracy locus and a basepoint in chart two
in both characteristics. The successful capped run took 0.82 seconds wall time and 66,868 KiB peak resident memory.
Two prior capped attempts stopped before retention: the first exposed an unpicklable task-aggregation factory at
0.61 seconds and 40,052 KiB, and the second exposed a python-flint integer at JSON serialization at 0.83 seconds and
66,688 KiB. Evidence: [`holomorphic-gauss-fibers-result.json`](holomorphic-gauss-fibers-result.json) and the
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

## Nakayama-reduced Rees fibers of six higher-order incidences

[`nakayama_rees_fibers.py`](nakayama_rees_fibers.py) computes the fiber over the boundary point `p` of the closed
holomorphic Gauss graph for `X+->VB`, `X-->VB`, `Iso->VB`, `W8->VB`, `E8bar->Va+` and `E8bar->Va-`, writing
[`nakayama-rees-fibers-result.json`](nakayama-rees-fibers-result.json). The fiber is the special fiber
`Proj (+)_d I^d / m I^d` of the blow-up of the ideal `I` of the 21 Schur coordinates in the germ ring `k[t]/J`; each
graded piece is annihilated by `m`, so the polynomial ring in a global ordering computes it exactly. The producer
picks Schur coordinates whose classes form a basis of `I / (m I + J)`, so by Nakayama they generate `I` at `p`;
removes the slice variables that `J` solves linearly (`elimpart`); eliminates `a` from `J + (y_i - a g_i)`; sets
`t = 0`; saturates by the target variables; and decomposes with `minAssGTZ`. The constant terms of `lift(J + m I +
(g), f)` give the `21 x s` matrix that embeds the reduced fiber in `P^20`; its rank equals `s` on every row. Each
committed target comes from the full first and second arc coefficients in the fixed boundary `C_z` frame, because
substituting those coefficients into the coordinate-slice variables changes the second-order Schur correction of
an arc that leaves the slice.

| Incidence | Minimal generators `s` | Fiber over `p` in the reduced coordinates | Committed arcs in the fiber |
| --- | --- | --- | --- |
| `X+->VB`, `X-->VB` | 3 | all of `P^2` | 2 of 2 each |
| `Iso->VB` | 4 | all of `P^3` | 2 of 2 |
| `W8->VB` | 5 | all of `P^4` | 2 of 2 |
| `E8bar->Va+`, `E8bar->Va-` | 6 | two disjoint planes, `{y1=y2=y6=0}` and `{y3=y4=y5=0}` | 2 of 2 each, both in the second plane |

The modulo-32003 and `Q(i)` calculations agree on every row. On the four `VB` rows `s` equals the germ dimension
and the fiber is the whole projective space of the span, which accounts for the second-order dependence of the
`W8`-to-`VB` limit plane in `schur-degeneracy-witnesses-result.json`. The two `E8bar` planes match the two smooth
sheets of the source germ; no committed arc witnesses the first plane. A standard basis point outside each embedding
column span fails the containment test, and deleting one generator of the `W8`-to-`VB` Rees ideal changes the fiber
and breaks both committed arc containments. A changed generator count, embedding rank, fiber component, arc
containment or characteristic comparison falsifies the record.

`E8bar->VB` stays open. Its minimal generator count is 10 against a germ of dimension 4 whose tangent cone is
non-reduced (`t8^2` lies in it, `t8` does not), so its fiber is a proper subvariety of `P^9`. Modulo 32003 the
reduced Rees elimination exhausts 4 GiB; `slimgb` reaches a 15-minute timeout at 346 MB; plain `std` under 16 GiB
reaches a 30-minute timeout at 14 GB; and the degree-by-degree fiber cone takes 107 s for degree 2 and exhausts
8 GiB in degree 3. The withdrawn iterated-blow-up draft took `sat(...)[1]`, which in Singular 4.4 keeps one
generator of the saturation, so its earlier E8-bar residual-base measurement carries no information.

## Nullity-16 basepoints, germs, and Schur-coordinate counts

[`nullity16_basepoints.py`](nullity16_basepoints.py) selects the canonical `N+` or `N-` census endpoint reached by a
committed path for each of the 18 incidences into nullity 16 and writes
[`nullity16-basepoints-result.json`](nullity16-basepoints-result.json). At each endpoint the producer constructs the
nine-dimensional coordinate slice complementary to the boundary orbit, intersects the reduced source-closure
components through the origin, and computes the germ through the global-ordering deformation to the normal cone.
The boundary matrix `C_z` has rank six and a nine-dimensional kernel. For a nullity-12 source the producer uses the
36 upper-triangle entries of the rank-two Schur form; for a nullity-8 source it uses the 126 principal four-Pfaffians
of the rank-four form. The Nakayama count is the dimension of the coordinate ideal modulo the source-germ maximal
ideal.

All 18 reduced germs reproduce the committed `(dimension, multiplicity, embedding dimension, components)` tuple.
Ten Nakayama calculations complete, while the other eight reach the 300-second limit after their germ calculation
has completed:

| Incidence family | Reduced germ | Nakayama count or blocked stage |
| --- | --- | --- |
| `B9->N+`, `B9->N-` | `(3,1,3,1)` | 3 |
| `V->N+`, `V->N-` | `(2,2,3,1)` | 3 |
| `VB->N+`, `VB->N-` | `(1,1,1,1)` | 1 |
| `Va+->N+`, `Va-->N-` | `(1,1,1,1)` | 1 |
| `E8bar->N+`, `E8bar->N-` | `(5,3,8,1)` | blocked at `nakayama_count` |
| `Iso->N+`, `Iso->N-` | `(5,2,6,1)` | 17 |
| `W8->N+`, `W8->N-` | `(6,2,7,1)` | blocked at `nakayama_count` |
| `X+->N+`, `X-->N-` | `(4,2,7,1)` | blocked at `nakayama_count` |
| `X+->N-`, `X-->N+` | `(4,1,4,1)` | blocked at `nakayama_count` |

The retained generation pooled four workers and measured these row costs. Each peak is the largest completed
Singular timing-wrapper measurement for the row. A timeout kills the Nakayama wrapper with its process group, so the
starred peaks measure the completed germ stage only; the timed-out Nakayama process's peak resident memory remains
unmeasured.

| Incidence | Row wall time (s) | Measured Singular peak RSS (KiB) | Outcome |
| --- | ---: | ---: | --- |
| `B9->N+` | 0.546 | 20,368 | completed |
| `B9->N-` | 0.616 | 20,372 | completed |
| `V->N+` | 0.745 | 22,932 | completed |
| `V->N-` | 0.804 | 22,648 | completed |
| `VB->N+` | 0.786 | 20,044 | completed |
| `VB->N-` | 0.757 | 19,860 | completed |
| `Va+->N+` | 0.623 | 20,324 | completed |
| `Va-->N-` | 0.708 | 20,140 | completed |
| `E8bar->N+` | 312.797 | 35,416* | blocked at `nakayama_count` |
| `E8bar->N-` | 321.191 | 34,760* | blocked at `nakayama_count` |
| `Iso->N+` | 20.146 | 159,428 | completed |
| `Iso->N-` | 10.382 | 160,008 | completed |
| `W8->N+` | 301.466 | 19,392* | blocked at `nakayama_count` |
| `W8->N-` | 300.675 | 19,800* | blocked at `nakayama_count` |
| `X+->N+` | 301.544 | 21,068* | blocked at `nakayama_count` |
| `X+->N-` | 300.696 | 21,176* | blocked at `nakayama_count` |
| `X-->N+` | 300.646 | 21,160* | blocked at `nakayama_count` |
| `X-->N-` | 300.909 | 20,732* | blocked at `nakayama_count` |

The full capped generation took 10:36.31 and reached 160,008 KiB peak resident memory. Every Singular call had a
4 GiB address-space cap and a 300-second timeout; the producer imposed no wall-clock gate. Deleting the first exact
generator of the `Va+` source closure changes the `Va+->N+` germ from `(1,1,1,1)` to `(2,1,2,1)`, so the mutation
control is detected. The record has `pass=false` because eight counts remain blocked, while all ten completed rows
pass. The record certifies basepoints, slices, reduced germs, and the ten completed local generator counts. It
computes neither a nullity-16 Gauss fiber nor an attaching map. A changed germ or completed count, a blocked row that
fails to name its stage, or a surviving source-ideal mutation falsifies the retained outcome.

## The nullity-16 Rees-fiber attempt stops after survivor reduction

[`nullity16_rees_fibers.py`](nullity16_rees_fibers.py) applies the prescribed one-pass normal-form reduction to the
126 four-Pfaffian coordinates of the eight rows that timed out above, then asks for the Nakayama-reduced Rees fiber
modulo 32003 and over `Q(i)`. The retained
[`nullity16-rees-fibers-result.json`](nullity16-rees-fibers-result.json) certifies these exact survivor-selection
results before the next modular stage reaches its resource boundary:

| Incidence family | Independent survivors | Coefficient monomials |
| --- | ---: | ---: |
| `E8bar->N+`, `E8bar->N-` | 103 of 126 | 3,741 |
| `W8->N+`, `W8->N-` | 124 of 126 | 2,589 |
| `X+->N+`, `X-->N-` | 69 of 126 | 727 |
| `X+->N-`, `X-->N+` | 69 of 126 | 731 |

All eight survivor-reduced rows then reach the 300-second limit at `modular_nakayama_and_embedding`. The other ten
rows stop immediately at that modular stage because Singular reports `2nd module does not lie in the first` for
`lift(LiftBasis,FullF)`. The producer uses the committed minimal local Nakayama generators as `F` and constructs
`LiftBasis = J + mF + G`. Those generators span `I/(mI+J)`, but they need not generate every original Schur
coordinate as a module over the global polynomial ring. The requested lift of all 36 or 126 coordinates is therefore
undefined. The zero rows printed after the failed lift carry no mathematical information and enter no claim.

Three capped generation attempts exercised the same algebraic formulation. Attempts one and two stopped during
aggregation after their mutation targets blocked; they took 11:00.74 at 264,204 KiB peak RSS and 11:03.41 at
264,424 KiB peak RSS. Attempt three retained the blocked mutation outcome and took 11:02.23 at 264,312 KiB peak
RSS. Every Singular call had a 4 GiB address-space cap and a 300-second timeout, the Python controller had the
standing 16 GiB cap, and the producer imposed no wall-clock gate.

The retained record has `pass=false`: all 18 incidences are blocked and zero Rees fibers complete. The record
certifies only the eight exact survivor ranks above and the stage-specific cost outcome. It certifies no full Schur
embedding, standard-basis-point control, characteristic comparison, Rees fiber, generator-deletion mutation, real
fiber, or attaching map. A successful modular count, a valid full embedding of the original coordinates, or a
detected generator-deletion mutation falsifies this blocked outcome.

The optimized self-test replays the same blocked invariants successfully. The byte-exact check does not pass: the
`blocked_diagnostic` field retains `/usr/bin/time` measurements from the failed Singular lift, so a fresh run changes
the JSON bytes even when every survivor rank and blocked stage agrees. The retained record digest is
`ee1b8663a034439aa1b09616a6299f39b3358d09f04449ab48ff82108a716f63`; the replay digest was
`81d51f41f84778acde79552507fb1e0a47ed665a90220f2cd535cf74fea7056a`. Fixing that serialization and regenerating
the result would exceed the sub-step's three-attempt cap. The replay failure therefore remains part of the blocker.

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
prlimit --as=17179869184 -- "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-attachments/holomorphic_gauss_fibers.py --self-test
prlimit --as=17179869184 -- "$PYTHON" -B -W error -O \
    docs/evidence/a5-kernel-attachments/holomorphic_gauss_fibers.py --self-test
prlimit --as=17179869184 -- "$PYTHON" docs/evidence/a5-kernel-attachments/holomorphic_gauss_fibers.py \
    --check docs/evidence/a5-kernel-attachments/holomorphic-gauss-fibers-result.json
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
prlimit --as=17179869184 -- "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-attachments/nullity16_basepoints.py --self-test
prlimit --as=17179869184 -- "$PYTHON" -B -W error -O \
    docs/evidence/a5-kernel-attachments/nullity16_basepoints.py --self-test
prlimit --as=17179869184 -- "$PYTHON" docs/evidence/a5-kernel-attachments/nullity16_basepoints.py \
    --check docs/evidence/a5-kernel-attachments/nullity16-basepoints-result.json
prlimit --as=17179869184 -- "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py --self-test
prlimit --as=17179869184 -- "$PYTHON" -B -W error -O \
    docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py --self-test
prlimit --as=17179869184 -- "$PYTHON" docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py \
    --check docs/evidence/a5-kernel-attachments/nullity16-rees-fibers-result.json
```

The `--check` command constructs the sorted, two-space-indented JSON plus its final newline in memory and compares
the UTF-8 bytes with the retained record. The command writes no record. The result contains integers, rationals,
exact symbolic expressions, and booleans; it contains no floating-point observations.
