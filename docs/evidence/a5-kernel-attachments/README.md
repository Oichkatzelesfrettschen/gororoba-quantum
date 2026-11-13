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

`E8bar->VB` stays open here as a Rees elimination; the exceptional-fiber track carries its Hilbert ladder: the fiber cone equals k[y]/K2 through degree 5 at p = 32009 and p = 32029 by the linear-algebra truncated rank ([exceptional-fiber evidence](../a5-exceptional-fibers/README.md)), and the open item there is whether the degree-3 component of V(K2) lies in the fiber. Its minimal generator count is 10 against a germ of dimension 4 whose tangent cone is
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

## The nullity-16 Rees fibers: eight complete, ten block at the modular fiber

[`nullity16_rees_fibers.py`](nullity16_rees_fibers.py) applies the one-pass normal-form reduction to the 126
four-Pfaffian coordinates of the eight rows that timed out above, then computes the Nakayama-reduced Rees special
fiber over `Q(i)` and modulo the split prime 32009 under both square roots of -1 (10754 and 21255). The retained
[`nullity16-rees-fibers-result.json`](nullity16-rees-fibers-result.json) certifies these survivor selections:

| Incidence family | Independent survivors | Coefficient monomials |
| --- | ---: | ---: |
| `E8bar->N+`, `E8bar->N-` | 103 of 126 | 3,741 |
| `W8->N+`, `W8->N-` | 124 of 126 | 2,589 |
| `X+->N+`, `X-->N-` | 69 of 126 | 727 |
| `X+->N-`, `X-->N+` | 69 of 126 | 731 |

Eight incidences complete, with the rational fiber and both modular fibers agreeing in component count, degree and
projective dimension:

| Incidence | Embedding rank | Special fiber |
| --- | ---: | --- |
| `B9->N+`, `B9->N-` | 3 | the plane `P^2` |
| `V->N+`, `V->N-` | 3 | the conic `y2^2 - y1*y3` in `P^2` |
| `VB->N+`, `VB->N-`, `Va+->N+`, `Va-->N-` | 1 | one point |

The generator-deletion mutation on `B9->N+` drops the first Nakayama generator (original coordinate 23) and changes
the fiber from degree 2 to degree 1, so the check detects a missing generator. The ten incidences from the nullity-8
sources `E8bar`, `Iso`, `W8`, `X+` and `X-` complete the Nakayama count and embedding and then reach the 300-second
timeout at `modular_rees_fiber`; the self-test admits exactly that stage for them. Every Singular call runs in a cgroup scope with a 16 GiB `MemoryMax`, no swap and a 300-second timeout, and the row
analyses run one at a time; the record's `execution_contract` binds these limits.

The record has `pass=false` because ten rows block. It certifies the survivor ranks, the eight fibers above, their
characteristic agreement and the detected mutation. It certifies no fiber for the ten blocked rows, no real fiber
and no attaching map. A completed modular fiber for a blocked row, a characteristic disagreement, a standard basis
point inside an embedding span, or a surviving mutation falsifies it.

## On the retained slice germ the real limit set at fourteen incidences is the whole holomorphic fiber

For every nonzero doubly pure `z`, the kernel of the bordered matrix is the Hermitian complement of `z` in
`ker C_z`: the partner-purity identities (`C_z` skew, `C_z z = 0`, hence `a z^T conjugate(z) = 0` and `a = 0`) leave
the equations `C_z u = 0` and `conjugate(z)^T u = 0`, and `conjugate(z)^T z > 0` gives
`ker C_z = C z (+) ker A(z, conjugate(z))`. The identity holds at every point, where the
[holomorphic-kernel record](holomorphic-kernel-lemma-result.json) verified it at 110 samples.

Three consequences follow at a boundary point `z_0` with `K_0 = ker C_(z_0) meet z_0^perp`.

1. **Inferred:** the map `P -> P meet z^perp` on planes through `z` is continuous in `(z, P)`, and every limit of
   `ker C_z` along `z -> z_0` contains `z_0`. The limits of the bordered kernel are therefore the planes
   `P meet z_0^perp` for `P` a limit of the holomorphic kernel, and `P -> P meet z_0^perp` identifies the 5-planes of
   `ker C_(z_0)` through `z_0` with `Gr(4, K_0)`.
2. **Inferred:** the five source closures are complex-algebraic subvarieties cut out by holomorphic polynomials in
   `z` alone (`strata_regularity.py`, the generators of `W8`, `Ehat`, `Iso`, `Xp` and `Xm`), each named source is
   the dense locally closed orbit in its closure, and the doubly pure real locus is all of `C^15`. The graph of
   `z -> ker C_z` over the source germ is therefore a complex constructible set, whose Zariski closure equals its
   closure in the classical topology (Mumford, The Red Book of Varieties and Schemes, section I.10, Theorem 1; the
   book is not held in the documents repositories and has no row in `docs/SOURCES.json`, so the locator is cited
   from the standard literature and its text was not inspected), so
   every point of the computed fiber lies in the Euclidean closure of the graph. The graph is also a real
   semialgebraic set, and the curve selection lemma
   ([Basu and Roy, Theorem 1](../../notes/1803.00505.md)) gives a continuous semialgebraic path that starts at the
   fiber point and lies in the graph for positive parameter. Its `z` component is an arc of real A_5 points in the
   source, and the kernel along it converges to the fiber point. Every point of the holomorphic fiber is a real
   limit on the slice germ.
3. **Inferred:** a limit along any arc in the same slice germ lies in the closed graph fiber, so on that germ the
   fiber excludes every other plane.

[`real_limit_sets.py`](real_limit_sets.py) verifies the identities symbolically, checks the splitting exactly at
`z = e_1 + i e_2` (kernel dimension 7, Hermitian complement 6), and collects the fourteen computed fibers in
[`real-limit-sets-result.json`](real-limit-sets-result.json). On all 29 retained arcs of these incidences the
holomorphic limit equals the retained bordered limit plus the boundary line. The record's `pass` covers these
computed checks; the three consequences are deductions from them and the two cited theorems. On the retained
transverse slice germ at each selected basepoint, the real limit set in `Gr(4, K_0)` is:

| Incidence | Real limit set on the slice germ: projective dimension, degree, components |
| --- | --- |
| E8-bar to `B9` | 1, 2, 1 |
| E8-bar to `V` | 2, 2, 2 |
| E8-bar to `V^a_+`, E8-bar to `V^a_-` | 2, 2, 2 (two disjoint planes) |
| `Iso` to `B9` | 1, 1, 1 |
| `Iso` to `VB` | 3, 1, 1 (a `P^3`) |
| `W8` to `B9` | 2, 1, 1 |
| `W8` to `VB` | 4, 1, 1 (a `P^4`) |
| `X_+` to `B9`, `X_-` to `B9` | 0, 1, 1 (the canonical plane) |
| `X_+` to `VB`, `X_-` to `VB` | 2, 1, 1 (a `P^2`) |
| `X_+` to `V^a_+`, `X_-` to `V^a_-` | 2, 2, 2 |

The first plane of E8-bar to `V^a_+` and to `V^a_-` is a real limit by consequence 2, and no arc of the two fiber
records reaches it; the [sheet record below](#each-e8-bar-sheet-at-va-carries-one-fiber-plane-and-an-exact-arc-reaches-the-first)
supplies an exact arc. Each fiber is computed on the retained
transverse slice at the selected path-supported basepoint. The record does not cover E8-bar to `VB`, whose fiber is
the open Rees elimination; the variation of a fiber along its boundary orbit; or the exclusion of limits along arcs
that leave the slice, which holds where the boundary orbit carries a local product structure that acts on `ker C_z`.
The [equivariance record below](#g_2-and-scaling-act-on-the-holomorphic-kernel-and-the-boost-does-not) gives the
that structure at the basepoints on `B9`, `V^a_+`, `V^a_-`, `N+` and `N-` by an exact rank check and the inverse
function theorem, so the exclusion holds there; on `V` and `VB` it stays open.

The falsifier is a failed identity; a failed Hermitian splitting at an exact point; a retained arc whose holomorphic
limit differs from its bordered limit plus the boundary line; a source stratum whose equations involve
`conjugate(z)`; or a fiber invariant on which the two characteristics disagree. Replacing the Hermitian pairing by
the bilinear pairing `z^T u` at the isotropic point `e_1 + i e_2` puts `z` in its own complement, and the splitting
fails. The `--out` run took 1.5 seconds wall time (one process) and 77,448 KiB peak resident memory. Evidence:
[`real_limit_sets.py`](real_limit_sets.py), [`real-limit-sets-result.json`](real-limit-sets-result.json), and the
[ledger](ledger.md#ledger-rows).

## The same identification gives eight real limit sets into nullity 16

The deduction of the previous section uses only the kernel identity, the holomorphic source closures and the two
cited theorems, so it applies at a nullity-16 boundary point `z_0`, where `ker C_(z_0)` has dimension 9 and
`K_0 = ker C_(z_0) meet z_0^perp` has dimension 8. The limits of the bordered kernel of a nullity-12 source are the
planes `P meet z_0^perp` for `P` a limit of the 7-plane `ker C_z`, in `Gr(6, K_0)`. The closures of `B9`, `V`, `VB`,
`V^a_+` and `V^a_-` are cut out by holomorphic polynomials in `z` (`strata_regularity.py`). **Inferred:** on the
retained slice germ at the census-supported `N+` or `N-` basepoint, the real limit set of each of the eight
incidences with a completed Rees fiber is that whole fiber:

| Incidence | Real limit set on the slice germ: projective dimension, degree, components |
| --- | --- |
| `B9` to `N+`, `B9` to `N-` | 2, 1, 1 (a `P^2`) |
| `V` to `N+`, `V` to `N-` | 1, 2, 1 (the conic `y2^2 - y1*y3`) |
| `VB` to `N+`, `VB` to `N-` | 0, 1, 1 (one point) |
| `V^a_+` to `N+`, `V^a_-` to `N-` | 0, 1, 1 (one point) |

The four one-point rows carry a canonical limiting six-plane on the slice germ. No retained arc ends at these
basepoints, so no arc comparison enters, and the ten incidences from the nullity-8 sources (`E8bar`, `Iso`, `W8`,
`X+`, `X-` into `N+` and `N-`) have no fiber in the nullity-16 Rees record; the
[next section](#the-ten-blocked-fibers-into-nullity-16-are-the-fiber-cones-of-the-exceptional-fiber-record)
imports their fibers from the exceptional-fiber record. The boundaries of the previous section hold
here as stated for the slice germ; the
[equivariance record below](#g_2-and-scaling-act-on-the-holomorphic-kernel-and-the-boost-does-not) removes the
last two at the `N+` and `N-` basepoints, where the limits along paths that leave the slice are limits along the
slice germ and the fiber of holomorphic kernel limits `P` is transported along the orbit by `G_2(C) x C^*`; the
bordered-kernel limits at `g z_0` are the planes `g P meet (g z_0)^perp`. A characteristic disagreement on one of
the eight fibers, a source closure with an equation in
`conjugate(z)`, or an exact real arc in a slice germ with a limit outside the listed fiber falsifies a row.
Evidence: the `nullity_16` block of [`real-limit-sets-result.json`](real-limit-sets-result.json),
[`nullity16-rees-fibers-result.json`](nullity16-rees-fibers-result.json), and the [ledger](ledger.md#ledger-rows).

## The ten blocked fibers into nullity 16 are the fiber cones of the exceptional-fiber record

The special fiber of the Rees algebra of the Nakayama generator ideal `(G)` on the germ `V(J)` is `Proj F`,
`F = sum_d (G)^d / m (G)^d`. That graded ring is the fiber cone `F(I)` which
[`../a5-exceptional-fibers`](../a5-exceptional-fibers/README.md) determines degree by degree, by rank computations
and arc families, from headers that [`fiber_inputs.py`](fiber_inputs.py) emits from the phase-one script of
`nullity16_rees_fibers.py`. The elimination that reaches the 300-second limit and the degree-by-degree record
therefore compute one object from one `J` and one `G`. [`nullity8_fiber_import.py`](nullity8_fiber_import.py)
regenerates the header of each of the ten blocked incidences and of `E8bar->VB` at the cells
`(32009, i = 10754)`, `(32009, i = 21255)` and `(32029, i = 9115)` and writes
[`nullity8-fiber-import-result.json`](nullity8-fiber-import-result.json). **Observed:** 31 of 31 regenerated
headers equal the retained file byte for byte; the selected Pfaffian coordinates are the same, in the same order, at
every cell and equal the chosen coordinates of the nullity-16 record; the generator count equals that record's Nakayama count and
embedding rank. The header regenerated at `i = 21255` differs from the retained header at `i = 10754` at all nine
incidences that have both, so the comparison detects the conjugate embedding. The generation takes 74 seconds and
124 MiB of resident memory on twelve cores, against the eliminations the exceptional-fiber ledger records as
exhausted (`A5-042`, `A5-048`, `A5-070`, `A5-071`, `A5-328`).

| Incidences | Generators | Fiber `V_+(K2)`: projective dimension, degree, reduced components | `F = k[y]/K2` decided | Characteristic 0 |
| --- | ---: | --- | --- | --- |
| `X+->N-`, `X-->N+` | 3 | 2, 1: the plane `P^2`, `K2 = 0` | every degree at 32009 and 32029 (`A5-001`) | decided: `Q(i)[y1, y2, y3]` (`A5-270`) |
| `X+->N+`, `X-->N-` | 15 | 3, 12: one threefold; the scheme has nilpotents `y1`, `y5`, `y6` | every degree (`A5-304`) | decided: 69 quadrics over `Q(i)` reducing to `K2` (`A5-305`) |
| `Iso->N+`, `Iso->N-` | 17 | 4, 23: one geometrically prime fourfold, Cohen-Macaulay | every degree (`A5-007`, `A5-067`) | open: dimension at least 5 and the 68 quadrics (`A5-293`, `A5-294`) |
| `W8->N+`, `W8->N-` | 24 | 5, 50: two fivefolds of degrees 20 and 30, Cohen-Macaulay | every degree (`A5-008`, `A5-066`) | open: dimension at least 6 (`A5-293`) |
| `E8bar->N+`, `E8bar->N-` | 21 | 4, 11: a fourfold of degree 11 and a threefold of degree 4 | degrees 1 to 7 (`A5-009`, `A5-335`, `A5-339`) | open: lower bounds on `h_d` for `d` at most 7 (`A5-346`) |
| `E8bar->VB` | 10 | 3, 7: threefolds of degrees 3 and 4, Cohen-Macaulay | every degree (`A5-005`) | open: the 21 quadrics at 32029 (`A5-315`) |

The record binds, for each row, the Hilbert and Cohen-Macaulay rows of `k2-hilbert.jsonl` and `k2-cm.jsonl` and the
status of each deciding ledger row; a status that changes in the ledger fails the record until it is regenerated.
The results on the `N+` header pass to the `N-` header by the sign automorphism `phi(a, b) = (a, -b)` (`A5-013`).
`X+->N+` has no retained `K2` at 32009.

**Inferred:** the limiting kernel planes form the fiber itself. The nullity-16 record expresses all 126 principal
four-Pfaffians of the rank-four Schur form, the Pluecker coordinates of the limiting plane, as a constant matrix
applied to the selected generators modulo `m (G)`, of rank equal to the generator count over `Q(i)` and modulo
32009. The map from `Proj F` to the Grassmannian is therefore the restriction of a linear embedding of
`P^(g - 1)` into `P^125`: it is injective on the whole fiber and its image is `V_+` of the defining ideal of `F`
in those linear coordinates. The sampled kernel-limit records of the exceptional-fiber track (`A5-272` to
`A5-275`, `A5-292`, `A5-296`) are instances.

### Real limit sets of the ten incidences

The deduction of the two previous sections applies with `ker C_z` of dimension 5 inside the 9-dimensional
`ker C_(z_0)`: the limits of the bordered kernel are the planes `P meet z_0^perp` in `Gr(4, K_0)`, `K_0` of
dimension 8, for `P` in the closed-graph fiber, and the
[equivariance record](#g_2-and-scaling-act-on-the-holomorphic-kernel-and-the-boost-does-not) makes the limits
along every sequence in the source stratum the limits along the slice germ at the `N+` and `N-` basepoints. The
closed-graph fiber is the set of complex points of `Proj` of the fiber cone over `Q(i)`. **Inferred:** for
`X+->N-` and `X-->N+` the real limit set is the complex plane `P^2`, and for `X+->N+` and `X-->N-` it is the set
of complex points of the degree-12 threefold cut out by the 69 quadrics of `A5-305`; both statements rest on the
closure theorem cited above, whose text is uninspected. For `Iso`, `W8` and `E8bar` the same deduction identifies
the real limit set with the complex points of the characteristic-0 fiber, and that fiber is determined modulo
32009 and 32029, and over `Q(i)` as far as the
[weight-slice record](#on-a-torus-weight-slice-the-quadrics-of-all-ten-fiber-cones-are-computed-over-qi) reaches:
the whole fiber cone of `Iso->N-` (`A5-422`), the quadrics, Hilbert numerator and minimal primes of the quadric
ideal for `W8` and `E8bar` (`A5-421`), and `h_1` to `h_7` of `E8bar` (`A5-423`). Open are `Iso->N+`, the
degree-20 component of `W8` over `Q(i)`, and both components of `E8bar` above degree 7 (`A5-418`).

Evidence: [`nullity8-fiber-import-result.json`](nullity8-fiber-import-result.json),
[`nullity16-rees-fibers-result.json`](nullity16-rees-fibers-result.json), the header receipts under
[`../a5-exceptional-fibers/working/build/inputs`](../a5-exceptional-fibers/working/build/inputs), and the
[ledger](ledger.md#ledger-rows). A regenerated header that differs from its retained file, a selection that differs
from the nullity-16 record, a changed Hilbert row or deciding status, a generator of the defining ideal of the
`E8bar` fiber cone in degree 8 or above, or a fiber cone over `Q(i)` whose reduction differs from `K2` falsifies
the corresponding statement.

## Each E8-bar sheet at Va carries one fiber plane, and an exact arc reaches the first

[`sheet_fiber_planes.py`](sheet_fiber_planes.py) decomposes the reduced slice germ of E8-bar at the `V^a_+` and
`V^a_-` basepoints into its two prime sheets (dimension 4 each; their intersection is the germ ideal) and computes
the special fiber of each sheet by the recipe of the Nakayama record, over `Q(i)` and modulo 32003. Each sheet gives
exactly one of the two fiber planes: the sheet `t6 = t7, t4 = -t5, t1 = t3, t2^2 + t8^2 + 2 t2 = 0` at `V^a_+`
(with `t1 = -t3` at `V^a_-`) gives `{y1 = y2 = y6 = 0}`, the plane no arc of the fiber records reached, and the
other sheet gives `{y3 = y4 = y5 = 0}`.

The line `t = (1, 0, 1, -2, 2, 3, 3, 0) u` at `V^a_+`, and `t = (1, 0, -1, -2, 2, 3, 3, 0) u` at `V^a_-`, lies on
the first sheet: the sheet, germ and closure generators vanish identically in `u`, `rank C_z` is 8 at `u = 0` and 10
at `u = 1, 2, 3`, and the 21 Schur coordinates vanish to order one with leading vector equal to the embedded point
`[0 : 0 : 2i : -10 : 2 : 0]` (respectively `[0 : 0 : -10i : 2 : -2 : 0]`) of the first plane. That line
lies in the closure of `X+` (respectively `X-`), a lower stratum of nullity 8 inside the E8-bar closure: rank 10
holds on E8-bar, `X+` and `X-` alike, and every generator of the `X+` closure vanishes on the line. The sheet's
conic `t2^2 + t8^2 + 2 t2 = 0` admits no other line through the origin, so the arc in the open orbit is curved:
`t2 = -2 u^2 / (1 + u^2)`, `t8 = -2 u / (1 + u^2)` with the same coefficients elsewhere. On it the E8-bar closure,
germ and sheet generators vanish identically, each of the nine closures strictly inside the E8-bar closure (`X+`,
`X-`, `B9`, `V`, `VB`, `V^a_+`, `V^a_-`, `N+`, `N-`) keeps a nonvanishing generator, `rank C_z` is 8 at `u = 0` and
10 at `u = 1, 2, 3`, and the leading vector is the same plane point. The first plane is therefore reached by an
exact arc in the open E8-bar source and by an exact arc in `X+` or `X-`. One arc witnesses one point of each plane;
the realization of the remaining points rests on the previous section. Adding 1 to the `t5` coefficient of the conic
arc leaves a sheet generator nonzero, and the check fails. A sheet whose fiber meets both planes, an arc generator
that does not vanish, a lower closure that contains the conic arc, or a leading vector outside the first plane
falsifies the record. The replay takes 1.6 seconds wall time and 4.2 CPU seconds with the default worker pool on
the 12-core build host. Evidence: [`sheet-fiber-planes-result.json`](sheet-fiber-planes-result.json) and the
[ledger](ledger.md#ledger-rows).

## G_2 and scaling act on the holomorphic kernel, and the boost does not

[`kernel_equivariance.py`](kernel_equivariance.py) tests which symmetries of the strata act on `ker C_z`. In original
coordinates the `G_2` automorphism `g` of the census, a product of three unipotent automorphisms with trace 12 and
so not itself unipotent, satisfies `g^T g = I` and
`C_(g z) = g^(-T) C_z g^(-1)` on the 15 basis directions, hence for every `z` by linearity, and
`ker C_(g z) = g ker C_z` at the twelve canonical points. The boost `b` (`c = 5/4`, `s = 3/4`) preserves each
nullity and fails the congruence for the four candidate matrices tested; `b ker C_z` differs from `ker C_(b z)` at
`B9`, `V`, `VB`, E8-bar, `X+` and `X-`, with the smallest witness at `VB` (two 7-planes meeting in dimension 6).

The linear system for an infinitesimal congruence, `C_(X e_k) + R^T C_k + C_k R = 0` in `(X, R)`, has a
15-dimensional solution space whose `X` projection holds the 14 `G_2` derivations and the scaling and excludes the
boost generator. **Inferred:** no rational one-parameter family of congruences through the identity exists for
the boost group, since its derivative would be a solution of that system; a congruence for a single boost element
outside the four candidates tested is not excluded. At each canonical point the tangent span of
`G_2` and the scaling has the dimension of the orbit, except at `V` (7 against 8), `VB` (6 against 7) and E8-bar
(10 against 11), where the boost generator supplies the missing direction.

The group `G_2(C) x C^*` acts on the kernel bundle. For each of the 14 `G_2` derivations `X` in original coordinates
the pair `(X, R) = (X, X)` solves the infinitesimal system exactly and `X` is skew, so
`F(t) = exp(tX)^T C_(exp(tX) z) exp(tX)` has derivative zero and `exp(tX)` satisfies the congruence with `rho = g`
for every `t`. **Inferred:** the exponentials generate the connected group `G_2(C)` and the congruence is closed
under products, so `ker C_(g z) = g ker C_z` for every `g` in `G_2(C)` and every `z`; the scaling has lift
`R = -I/2` and fixes each kernel. The solution space and its `X` projection both have dimension 15, so each lift
is unique. Replacing a lift by its negative leaves a nonzero residual for all 15 generators.

At the retained basepoint of each of the 33 incidences the record compares the tangent span of `g_2` and the scaling
with the boundary orbit and with the slice. At the 27 basepoints on `B9`, `V^a_+`, `V^a_-`, `N+` and `N-` the
tangent span has the orbit dimension and spans `C^15` together with the slice. **Inferred:** the map
`(xi, s) -> exp(xi) s`, from a complement of the stabilizer algebra times the slice, is then a local biholomorphism
at the basepoint `z_0` by the inverse function theorem, so every `z` near `z_0` is `g(z) s(z)` with `g(z)` tending
to the identity and `s(z)` in the slice. The source strata are invariant under the group, so `s(z)` stays in the
source slice germ and `ker C_z = g(z) ker C_(s(z))`. The limits of `ker C_z` along any sequence or continuous path
in the source tending to `z_0` are therefore limits along the slice germ (the fiber over `z_0` of the closed graph
equals that of its restriction to the slice), and the fiber of holomorphic kernel limits over `g z_0` is `g`
applied to the fiber over `z_0`. The bordered-kernel limits over `g z_0` are the planes `g P meet (g z_0)^perp` for `P` in the fiber over `z_0`: `g` is
complex orthogonal and need not be unitary, so it does not carry `P meet z_0^perp` to that plane. Hence
at those basepoints the closed-graph fibers of the two sections above are the limit sets over all approaches;
their identification with the limits along real arcs keeps the condition of those sections,
and they are transported along the whole boundary orbit by the group: `G_2(C) x C^*` is a direct factor of the
connected group `G_2(C) x SO(2, C) x C^*` whose orbit is the boundary orbit, so its tangent rank is constant along
that orbit, its orbits there are open, and a connected set holds only one of them. At the 6 basepoints on `V` and `VB` the tangent
span is one short of the orbit (7 against 8, 6 against 7) and reaches rank 14 with the slice; there the kernel can
vary along the boost direction, and the variation of the fiber is open.
Using the split-coordinate matrix in place of `g` leaves 1,458 nonzero residual entries. A nonzero residual for
`g`, a kernel that `g` fails to transport, or the boost generator inside the `X` projection falsifies the record.
The replay of commit `542a51836` takes 8.2 seconds wall time and 51 CPU seconds (Python 3.14.7, python-flint 0.9.0,
12 workers) on the 12-core build
host. Evidence:
[`kernel-equivariance-result.json`](kernel-equivariance-result.json) and the [ledger](ledger.md#ledger-rows).

## A composed limit through a nullity-12 stratum lies in a linear section of the nullity-16 fiber

Every row into `N+`, and every row into `N-`, uses one basepoint `z_0`, one slice and one frame of the
9-dimensional `ker C_(z_0)`, so the fibers of all sources at that basepoint live in one space. A nullity-12
stratum `M` has the rank-two Schur form `S` and the limiting 7-plane `Q = ker S_0`; a nullity-8 source has the
rank-four form `T`, the limiting 5-plane `P = ker T_0`, and the Pfaffian vector `pi` of `T`. A limit of 5-planes
taken first at points `w` of `M` and then along `w -> z_0` lies in the limit of `ker C_w`, so a composed limit
through `M` is a plane `P` inside some `Q`. With `S_0 = alpha ^ beta` the containment reads
`(iota_v S_0) ^ pi = 0` for every `v`, which is linear in the fiber coordinates `y` of the source for a fixed
point `m` of the fiber of `M`. [`composed_limit_sections.py`](composed_limit_sections.py) evaluates that linear
section of `V_+(K2)` from the two embedding matrices of the nullity-16 record and the retained quadrics, modulo
32009 and 32029, and writes [`composed-limit-sections-result.json`](composed-limit-sections-result.json): 41
chains, 136 sections, 2 seconds. Each K2 relation file is bound to the canonical header it is written
against: the K2 digest of `k2-hilbert.jsonl` is certified by a degree-2 receipt (or, for `E8bar->N+` at 32009, by
the sign-isomorphism witness from `E8bar->N-`) whose `input_sha256` is the digest of the regenerated header of
[`nullity8-fiber-import-result.json`](nullity8-fiber-import-result.json) and whose `generator_order_sha256` is the
digest of a `gens.txt` that lists the header's G ideal in the header's order (`k2_bindings` in the record, 11
source and prime pairs). **Observed:** the sections agree between the primes for the 19 source and stratum pairs
that both primes carry. The three pairs of `X+->N+` (through `B9`, `VB` and `V^a_+`) exist at 32029 only, since no K2
file of `X+->N+` is retained at 32009 (the sign map carries `X-->N-` there); the record marks those chains
`single_prime_excluded_from_agreement` and leaves them out of the agreement. Each value below holds at every prime
that carries the pair:

| Source | Through `VB` (one `Q`) | Through `V^a_+` or `V^a_-` (one `Q`) | Through `B9` at a point off the `VB` form | Through `V` at a point off the `VB` form |
| --- | --- | --- | --- | --- |
| `X` opposite sign (`P^2`) | the whole `P^2`, no condition | no such chain | a line | no such chain |
| `X` same sign (threefold of degree 12) | a plane | a plane with section degree 2 | two lines | no such chain |
| `Iso` (fourfold of degree 23) | a `P^3` with section degree 2 | no such chain | a plane and a `P^3` | no such chain |
| `W8` (fivefolds of degrees 20 and 30) | a `P^4` with section degree 2 | no such chain | a `P^3` and a `P^4` | no such chain |
| `E8bar` (fourfold of degree 11, threefold of degree 4) | threefolds of degrees 3 and 4 | a plane with section degree 2 | a plane and a quadric surface | a plane with section degree 2 |

The `E8bar` sections are sections of `V_+(K2)`, which is the special fiber only given `F(I) = k[y]/K2` in degrees
8 and above (`A5-009`, `survives`); a Hilbert function that agrees through degree 7 does not fix the fiber.

The section through `VB` has the reduced components of the fiber of the same source over `VB`, computed
independently at a `VB` basepoint: `P^2`, `P^3` and `P^4` (the Nakayama record) and the cubic and quartic
threefolds of `E8bar->VB` (`A5-005`). The section through `V^a_+` or `V^a_-` is one plane of degree 2 where the
fiber over that stratum is two disjoint planes. The third generator of `B9->N` and of `V->N` is the form of `VB`,
and at that point of either fiber the section is the section through `VB`. The containment equations vanish on
an exact plane inside a 7-plane and have 1,000 and 1,112 nonzero coefficients on a plane sharing one covector
and on a transverse plane.

**Inferred:** a composed limit through `M` lies in the section of some point `m`.

`hypothesis:` through `VB` the composed limit set is the whole reduced section. Computed: the section and the
fiber of the source over `VB` have equal dimension, degree and component count at the retained `VB` basepoint
(and, for `Iso`, `W8`, `X+` and `X-`, at the three sampled boosts below). Missing: a flat family of the fibers over
the points of `VB` near `z_0` whose special fiber specializes componentwise, so that the limit of the fibers is a
closed subscheme of the section with the same dimension and degree; constant nearby dimension and total degree do not
supply it. The inference is plausible for the irreducible linear `Iso`, `W8` and `X` sections. For `E8bar` the
degree-3 and degree-4 components need separate tracking, since equal total degree 7 admits a collision of components
or a multiplicity. The group action transports the fiber along six of the seven orbit directions of `VB`, and the
boost record below samples the seventh for `Iso`, `W8`, `X+` and `X-`. A flat relative Rees or Grassmannian family
over `VB`, or an exact one-parameter limit, decides it.

Through `V^a_+` and `V^a_-` the two planes of the fiber have one
limit plane. The record does not decide which planes of a section through `B9` or `V` are composed limits: there
the fiber of the source over the middle stratum is smaller than the section (one point for `X`, a line for
`Iso`, a plane for `W8` and a conic for `E8bar` over `B9`), and the missing datum is the limit of that fiber
along `w -> z_0`. A section through `VB` whose reduced components differ from the fiber over `VB`, or a section
that differs between the primes at a pair both primes carry, falsifies the observation.

## Along the boost the four whole-space fibers into VB keep their shape at three sampled basepoints

At a basepoint on `VB` the orbit of `G_2(C) x C^*` has dimension 6 in the 7-dimensional boundary orbit, and the
missing direction is the boost `u -> c u + s v`, `v -> s u + c v` with `c^2 - s^2 = 1`, which preserves every
stratum and has no lift to the kernel (the section above). [`boost_fiber_variation.py`](boost_fiber_variation.py)
moves the retained `VB` basepoint of `Iso->VB`, `W8->VB`, `X+->VB` and `X-->VB` by the boosts
`(c, s) = (5/4, 3/4)`, `(5/3, 4/3)` and `(13/12, -5/12)`, keeps the retained slice columns, and recomputes the
Nakayama-reduced Rees special fiber over `Q(i)` and modulo 32003; the record is
[`boost-fiber-variation-result.json`](boost-fiber-variation-result.json). **Observed:** at all sixteen basepoints
(the retained one and three moved ones per incidence) the moved point lies on the `VB` orbit, the slice is
complementary to it (rank 15 with the orbit tangent space), the germ keeps its dimension, and the special fiber
is the whole projective space of the generators in both characteristics: `P^3` for `Iso`, `P^4` for `W8`, `P^2`
for `X+` and `X-`, with embedding rank equal to the generator count. The selected Pfaffian coordinates are the
same at every basepoint for `Iso`, `X+` and `X-`; for `W8` they are `8, 12, 16, 17, 18` at the retained basepoint
and `3, 8, 12, 17, 18` at each moved one, so the retained `W8` basepoint is special for the selection and not for
the fiber. A slice with one column removed has rank 14 and fails the check. The generation takes 45 seconds and
204 MiB.

The record samples the boost orbit. It compares no limiting plane between basepoints, so it does not decide
whether the family of fibers over the boost orbit is a product; it covers neither `E8bar->VB`, whose fiber at the
retained basepoint is the cubic and quartic threefold pair of the import table above and whose quadric scheme the
[next section](#along-the-boost-the-quadric-schemes-of-e8bar-vb-at-four-sampled-basepoints-are-projectively-equivalent)
samples, nor `E8bar->V`, where the
Nakayama route ran 31 minutes at the retained basepoint without output and was stopped. A sampled basepoint whose
fiber is a proper subvariety, or whose slice is not complementary, falsifies the observation.

## Along the boost the quadric schemes of E8bar->VB at four sampled basepoints are projectively equivalent

[`boost_e8_vb_quadrics.py`](boost_e8_vb_quadrics.py) samples the boost for `E8bar->VB`, which the section above
leaves out, through the relations of low degree of its fiber cone; the record is
[`boost-e8-vb-quadrics-result.json`](boost-e8-vb-quadrics-result.json). At the retained `VB` basepoint and at the
boosts `(5/4, 3/4)`, `(5/3, 4/3)` and `(13/12, -5/12)` of it the script keeps the retained slice columns, emits the
presolved slice ideal and the Nakayama generators by the phase-one script of the nullity-16 Rees record, and
computes the degree-2 relations `{q : q(G) in J + m I^2}` modulo 32029 with `i = 9115`.

**Observed (`A5-428`):** at all four basepoints the moved point lies on the `VB` orbit with a complementary slice
(rank 15), and the fiber cone has 10 generators and 21 quadrics whose ideal has dimension 4, multiplicity 7, first
Hilbert numerator `1, 0, -21, 70, -105, 84, -35, 6`, is saturated and radical, has two minimal primes of dimension
4 and degrees 3 and 4, and has a linear symmetry algebra of dimension 15. At the retained basepoint the echelon
form of the relations equals the retained `K2` of the exceptional-fiber record. The four computations read four
different inputs (the digest of the moved point, the Schur coordinates and the slice columns differs at each), and
their four echelon forms differ. At the boost `(5/4, 3/4)` the degree-3 relations number 140 of 220 products, so
`h_3 = 80`, the value of the quadric ring.

The four echelon bases have one support and differ in three scalars `a`, `b`, `d` read from them. The linear spans
of the two components are cut out by `y7, y3, y4 + y6` and by `y10 + a y1, y9 + b y5, y8 + b y2, y6 - y4 + d y1`;
the substitution `y = M w` that takes those seven forms to `w1, w2, w3` and `w4 - (d/2) w7, w5, w6, w7`, and
`y1, y2, y5` to `w8, w9, w10`, is invertible, and after it the four quadric ideals have the same reduced echelon
basis. So `M_k M_0^{-1}` carries the quadric ideal at basepoint `k` onto the one at the retained basepoint: the four
quadric schemes are projectively equivalent over `F_32029`, by explicit matrices. The frame of the retained
basepoint, applied at each moved basepoint, gives a different ideal (the control of the comparison).

**Inferred, modulo 32029:** the fiber of `E8bar` over each sampled point lies in one quadric scheme up to a linear
change of the 10 generators, and at `(5/4, 3/4)` the fiber cone agrees with the quadric ring through degree 3.
`hypothesis:` the family of fibers of `E8bar` over the boost orbit is constant up to projective equivalence, in
characteristic 0 as well. The record compares the quadric schemes at four sampled points in one characteristic; it
compares no limiting plane and decides the fiber cone above degree 3 at no moved point. An invariant that differs
at a rational boost, a degree-3 count other than 140, or a sampled basepoint whose adapted frame fails to carry
its quadric ideal onto the common one falsifies the observation; a sampled boost whose quadric scheme is
inequivalent to the retained one, or a fiber that leaves its quadric scheme in a higher degree at one basepoint
and not at another, falsifies the hypothesis.

The replay takes 19 minutes 51 seconds of wall time, 1,083 CPU seconds and 0.33 GiB on two workers under an 8 GiB
memory scope (Python 3.14.9, python-flint 0.9.0, Singular 4.4.1) on the build host; each degree-2 basepoint takes
12 seconds and the degree-3 count 18 minutes. Evidence:
[`boost-e8-vb-quadrics-result.json`](boost-e8-vb-quadrics-result.json) and the [ledger](ledger.md#ledger-rows).

## On a torus weight slice the quadrics of all ten fiber cones are computed over Q(i)

At the `N+` or `N-` basepoint `z_0` the stabilizer in `g_2` + scaling + boost contains a two-dimensional torus
that acts on `ker C_(z_0)`. [`weight_slice_fiber_relations.py`](weight_slice_fiber_relations.py) takes the
nine-dimensional normal slice along joint eigenvectors of that torus and writes the Schur form in a frame of torus
eigenvectors. **Computed:** the 126 principal 4-Pfaffians are then homogeneous for the weight
`(1, 0, 3, 2, 2, 1, 4, 4, 3)` on the slice coordinates. The germ ideal `J` of a source closure is replaced by the
intersection of its minimal primes through the origin, and the Nakayama generators `G`, their products and the
relations `{q : q(G) in J + m I^2}` come from standard bases truncated above the largest weight present. **Inferred:**
the truncation changes no normal form of a product, because every ideal involved is graded by the weight and the
added monomials lie above the largest product weight; and membership in the polynomial ring equals membership in
the local ring, because the class of `q(G)` modulo `J + m P` is killed by the maximal ideal, so the local units
`det B`, `1 + i s_2` and `1 - s_2^2` act on it as nonzero constants. The component step changes the germ ideal of
the two `X` sources only (at `N-`: `E8bar`, `W8` and `Iso` are radical already). The table runs over `Q(i)` in 60 s; the ungraded standard
basis of `J + m P` took 1,507 s for `Iso` (`A5-294`) and did not finish for `W8` and `E8bar`.

| Source | Generators | Quadrics at `N+` and `N-` | Quadric ideal over `Q(i)` |
|---|---|---|---|
| `W8` | 24 | 144 | dimension 6, multiplicity 50, primes of degrees 20 and 30 |
| `E8bar` | 21 | 148 | dimension 5, multiplicity 11, primes of dimension 5 degree 11 and dimension 4 degree 4 |
| `Iso` | 17 | 68 | not computed here (`A5-422`) |
| same-sign `X` | 15 | 69 | `A5-305` |
| opposite-sign `X` | 3 | 0 | `A5-270` |

The counts equal the modular ones of the [import record](#the-ten-blocked-fibers-into-nullity-16-are-the-fiber-cones-of-the-exceptional-fiber-record).
For `W8` and `E8bar` the quadric ideal is saturated with the Hilbert numerator of the modular `K2`, and at `N-` the
`Q(i)` relation space reduced at `(32009, i = 10754)` equals that of the modular cell of the same run (ranks 144 and 148, joint ranks the
same). Two controls run in the record: a permuted weight vector leaves 59 Pfaffians inhomogeneous, and without the
component step `X+->N-` returns 12 generators in place of 3.

**Inferred (`A5-422`, conditional on `A5-293` and `A5-294`):** the fiber cone of `Iso->N-` over `Q(i)` is `Q(i)[y]/K` with `K` the ideal of the 68
quadrics. The reduction `K'` of the saturated lattice of `K` has the Hilbert function of `K` and contains the
modular `K2`, which is prime of dimension 5 (`A5-060`); `K` lies in the relation ideal `L`, whose quotient has
dimension at least 5 (`A5-293`), so `K' = K2`. The quotient of the lattice by its saturated part is
torsion-free over the prime above 32009, so each nonzero class is a power of that prime times a class that stays
nonzero modulo it, and the reduction is a domain; hence `K` is prime, `V(L)` is a closed subset of the irreducible
`V(K)` of the same dimension, and `L = K`. The counterexample of `A5-316` lacks exactly the primality and dimension inputs this uses.

**Inferred (`A5-423`):** for `E8bar->N+` and `E8bar->N-` the 148 quadrics bound `h_d` over `Q(i)` above by the
Hilbert function of their ideal, 21, 83, 225, 495, 952, 1666, 2718 for `d = 1..7`, and the arc-jet ranks of
`A5-346` bound it below by the same numbers. The quadrics live on the weight slice and the arcs on the header
slice; `h_d` is an invariant of the ideal germ, and the two slices are joined by the transverse-slice isomorphism of
the [equivariance section](#g_2-and-scaling-act-on-the-holomorphic-kernel-and-the-boost-does-not), under which the
Pfaffian ideal is invariant (`pf4(W) = det(B)^2 pf4(S)`).

Evidence: [`weight-slice-fiber-relations-result.json`](weight-slice-fiber-relations-result.json) and the
[ledger](ledger.md#ledger-rows). The relation lines are named by digest and regenerated by the producer; no map
from its generators to the header generators of the modular record is retained. A rerun with different counts,
numerator, minimal primes or reduction ranks, a weight-inhomogeneous Pfaffian, or a relation that fails the
untruncated membership falsifies the table; a prime at which the saturated lattice of `K` reduces off `K2`
falsifies the `Iso` statement.

## Over Q(i) the linear symmetries of the fiber-cone quadrics are sl2 over a solvable radical with a torus of rank 4 to 6

[`symmetry_algebra_qi.py`](symmetry_algebra_qi.py) regenerates the quadrics `K` of the
[weight-slice record](#on-a-torus-weight-slice-the-quadrics-of-all-ten-fiber-cones-are-computed-over-qi) for the
eight cells that have any (`W8`, `E8bar`, `Iso` and same-sign `X` at `N+` and `N-`), checks each digest against that
record, and computes over `Q(i)` the Lie algebra `g` of matrices in `gl_n` whose derivation
`y_i -> sum_j A_ij y_j` maps `K` into `K`; the record is
[`symmetry-algebra-qi-result.json`](symmetry-algebra-qi-result.json). The linear system is formed modulo 32009, a
spanning set of its rows is formed over `Q(i)`, and every basis matrix of the null space of those rows is applied to
every basis quadric and reduced exactly, so the null space equals `g` whatever the modular selection did. The
structure is computed by the definitions of the modular record of the
[quadric census](../a5-exceptional-fibers/quadric-census/README.md#structure-of-the-symmetry-algebras-over-f_p-a5-347-a5-348-a5-349),
in exact arithmetic over `Q(i)`.

**Observed (`A5-424`), the same numbers at `N+` and `N-`:**

| Source | Generators | dim g | derived series | radical r | nilpotent ideal u | g / r | Cartan subalgebra | center |
|---|---:|---:|---|---:|---:|---|---|---:|
| `W8` | 24 | 26 | 26, 22 | 23 | 19 | sl2 | 5, toral | 1 |
| `E8bar` | 21 | 34 | 34, 29, 26, 23 | 31 | 26 | sl2 | 6, toral | 1 |
| `Iso` | 17 | 17 | 17, 14, 13 | 14 | 11 | sl2 | 4, toral | 1 |
| same-sign `X` | 15 | 23 | 23, 19, 18 | 20 | 16 | sl2 | 5, toral | 1 |

On each cell `r = {x : kappa(x, [g, g]) = 0}` is an ideal whose derived series reaches 0, `[g, g] + r = g`, and
`g / r` has dimension 3 and holds `h, e, f` over `Q(i)` with `[h, e] = 2e`, `[h, f] = -2f` and `[e, f] = h`, so `r`
is the radical and the quotient is the split `sl2`. `u`, the part of `r` orthogonal to `g` under the trace form, is
an ideal whose lower central series reaches 0. The Fitting null component of one fixed element is abelian and each
of its basis matrices has a squarefree minimal polynomial. The center is the line of the Euler field, and the
diagonal matrix of the torus weights of the generators lies in `g`. The basis of `g` reduced at
`(32009, i = 10754)` has the same structure numbers under the modular script, the stabilizer of the reduced quadrics
has the dimension of `g`, and the same number of quadrics with hash-stream integer coefficients keeps the Euler
field alone modulo 32009, which bounds its stabilizer over `Q(i)` by 1. The numbers equal those of the modular
record (`A5-347`) for `X`, `Iso`, `E8bar -> N+-` and `W8 -> N-`, which that record computes in header coordinates
at 32009 and 32029.

**Inferred:** in characteristic 0 the stabilizer of `K` in `GL_n` is smooth, so `g` is its Lie algebra and a Cartan
subalgebra of `g` is the Lie algebra of a Cartan subgroup, the centralizer of a maximal torus. That Cartan
subalgebra consists of semisimple matrices on every cell, so the maximal tori of the group of linear symmetries of
`K` have rank 5, 6, 4 and 5, and the Levi factor of its identity component has Lie algebra `sl2`. The torus is a
subgroup of `GL_n`, and an element `g` of it that fixes every point of the cone has `g - 1` vanishing on the cone,
so the rows of `g - 1` lie in the linear part of the radical of `K`; for `Iso->N-`, where `K` is prime and is the
whole relation ideal (`A5-422`, conditional on `A5-293` and `A5-294`), that part is zero, `g = 1`, and the torus of rank 4 acts effectively on the
5-dimensional fiber cone (`A5-348`).

**Observed (`A5-426`), a Levi subalgebra and a split maximal torus, the same at `N+` and `N-`.** The triple of
`g / r` lifts to elements `h, e, f` of `g` that satisfy the `sl2` relations exactly (corrections solved along the
derived series of `r`). `h` has integer eigenvalues on the generators, symmetric about 0, and they split the
generators into irreducible `sl2` summands:

| Source | Generators | Weights of `h` (weight: multiplicity) | Summands of dimension 1, 2, 3, 4 |
|---|---:|---|---|
| `W8` | 24 | 0: 6, +-1: 6, +-2: 2, +-3: 1 | 4, 5, 2, 1 |
| `E8bar` | 21 | 0: 5, +-1: 6, +-2: 1, +-3: 1 | 4, 5, 1, 1 |
| `Iso` | 17 | 0: 3, +-1: 4, +-2: 2, +-3: 1 | 1, 3, 2, 1 |
| same-sign `X` | 15 | 0: 3, +-1: 4, +-2: 1, +-3: 1 | 2, 3, 1, 1 |

`h` commutes with the derivation `D` of the slice-torus weight `2 w_1 - w_2`. A Cartan subalgebra of `g` that
contains `h` and `D` (the Fitting null component of an element of their common centralizer, abelian with semisimple
basis matrices and of the dimension of the table above) has all its eigenvalues in `Q(i)`, and its joint eigenspaces
fill the generators: the maximal torus is split over `Q(i)`. Its weights on the generators, written on a basis of
the lattice they generate, are integer vectors of full rank 5, 6, 4 and 5; the Euler field, `h` and `D` are integer
cocharacters. The weights are pairwise distinct for `E8bar` (21), `Iso` (17) and same-sign `X` (15), and `W8` has
23 distinct weights on 24 generators (one of multiplicity 2). On torus eigen-coordinates the quadric space is the
direct sum of its weight spaces: the ranks on the monomials of each weight add up to 144, 148, 68 and 69. The
record lists every weight, and per weight the dimensions of the monomial space and of the quadrics in it: 6, 37
and 10 weights of `W8`, `E8bar` and same-sign `X` hold a single monomial that lies in the quadric space, and no
weight of `Iso` does.

**Inferred:** on `Iso` the torus has rank 4 and the cone dimension 5, so the action has complexity one (`A5-348`),
and the coordinates are torus eigenvectors of pairwise distinct weights. The weight list of the record is the input
of a description by polyhedral divisors, which no record computes.

`hypothesis:` the `sl2` is the image of the derived algebra of the `gl_2` part of the stabilizer of the base point
in `g_2` plus scaling; the [stabilizer record](#the-base-point-stabilizer-maps-onto-the-levi-factor-of-the-symmetry-algebra)
tests it. `dim g` exceeds `dim G_2 = 14` on every cell. The record does not cover `E8bar->VB`, whose
quadrics over `Q(i)` come from the 650-second run of `A5-315` and are not retained. A matrix of the retained basis
that fails to stabilize the regenerated quadrics, a structure number that differs from the tables, a reduction with
other numbers, a control of dimension above 1, a triple with a nonzero defect, a Cartan basis matrix with an
eigenvalue outside `Q(i)`, weights of rank below the Cartan dimension, or a quadric space that is not the sum of
its weight spaces falsifies the record. The replay takes 3 minutes 55 seconds of wall time, 419 CPU seconds and
0.63 GiB on two workers under a 12 GiB memory scope (Python 3.14.9, python-flint 0.9.0, Singular 4.4.1) on the build
host. Evidence: [`symmetry-algebra-qi-result.json`](symmetry-algebra-qi-result.json) and
the [ledger](ledger.md#ledger-rows).

## The base-point stabilizer maps onto the Levi factor of the symmetry algebra

[`stabilizer_action_qi.py`](stabilizer_action_qi.py) computes the action of the stabilizer `p` of the basepoint
`z_0` in `g_2(C)` plus the scaling on the generators of each fiber cone, and compares its image with the symmetry
algebra `g` of the [section above](#over-qi-the-linear-symmetries-of-the-fiber-cone-quadrics-are-sl2-over-a-solvable-radical-with-a-torus-of-rank-4-to-6);
the record is [`stabilizer-action-qi-result.json`](stabilizer-action-qi-result.json). `C(z)` is linear in `z`, so
along the field `z -> X z` the Schur form moves by the product rule, a generator `G_a = pf4(W)` moves to a polynomial
`dG_a` on the slice, and `rho(X)` is the matrix with `dG_a = sum_b rho(X)_ab G_b` modulo `J + m (all Pfaffians)`.
**Inferred:** the field leaves the slice, and the correction that returns it is a combination, with coefficients
in `m`, of the fields of `g_2` and the scaling, each of which maps the Pfaffian ideal into itself; those fields
span the tangent space of the boundary orbit at `z_0`, because the boost generator of the stabilizer torus fixes
`z_0` and so moves `z_0` as a derivation of `g_2` does. The class modulo `m I` is therefore the action on the slice
germ. The normal forms are taken modulo the weight truncation and the sixth power of the slice coordinate
of weight zero, a quotient that is Artinian and local; the generators stay independent there (rank equal to their
number on every cell), which makes each `rho(X)` unique.

**Observed (`A5-427`), the same at `N+` and `N-` and on `W8`, `E8bar`, `Iso` and same-sign `X`:**

- `p` has dimension 9: a part of grading weight 0 of dimension 4 (two torus elements and the root vectors of
  weights `(1, 2)` and `(-1, -2)` under the two torus characters), and a part of dimension 5 of grading weights
  -1, -1, -2, -3, -3.
- Every one of the nine basis elements has a matrix, and every matrix lies in `g` (it maps each basis quadric into
  the quadric space, exactly). The brackets of the images equal the images of the brackets on all 36 pairs.
- The image of the grading element `2 t_1 - t_2` is the diagonal matrix of the generator weights that the producer
  measures, with no multiple of the Euler field added.
- `rho` is injective (image of dimension 9). The image and the radical of `g` together span `g` (dimension 26, 34,
  17, 23). The weight-zero part maps to a subalgebra of dimension 4 whose image modulo the radical has dimension 3,
  and the part of nonzero weight maps into the radical.
- Control: the diagonal matrix 1, 2, ..., 15, a direction outside `g_2`, the scaling and the boost, has no matrix
  on any cell.
- A derivation of `g_2` that moves `z_0` has a matrix on every cell, and that matrix lies outside `g` on every cell.
- The boost generator of the stabilizer torus, which is outside `g_2` plus scaling and has no lift to the kernel,
  has a matrix in `g` on `W8`, `Iso` and same-sign `X`, where it adds one dimension to the image (10), and has no
  matrix on `E8bar`. No invariance argument covers the boost, so its matrices are statements about this truncated
  quotient (weight margin 4, sixth power of the weight-zero coordinate) and a larger quotient could lose them; the
  absence of a matrix on `E8bar` holds in every larger quotient.

**Inferred:** the Levi factor `sl2` of `g` is the image of the `sl2` in the weight-zero part `gl_2` of `p`, whose
compact form is the `SU(2)` of the stabilizer `(SU(2) x U(1)) / Z_2` of the base point in `G_2 x U(1)`
([kernel bundles](../a5-kernel-bundles/README.md)); the hypothesis of the section above holds on these eight cells.
The derived algebra of all of `p` has dimension 8 and maps injectively, so it is larger than the Levi factor. The rest of `g` (dimension 17, 25, 8 and 14 beyond the
image) is not explained by `g_2` plus scaling. `hypothesis:` the boost acts on the fiber cones of `W8`, `Iso` and
same-sign `X` because their closures are cut out by forms that the boost preserves as an ideal, and fails on
`E8bar`; no record tests the mechanism.

A stabilizer element without a matrix, an image outside `g`, a bracket that fails, a grading image that differs
from the weight derivation, an image that misses the Levi factor, or a diagonal control with a matrix falsifies the
record. Evidence: [`stabilizer-action-qi-result.json`](stabilizer-action-qi-result.json) and the
[ledger](ledger.md#ledger-rows). The replay takes 2 minutes 34 seconds of wall time and
0.47 GiB on two workers under a 12 GiB memory scope (Python 3.14.9, python-flint 0.9.0, sympy 1.14.0, Singular
4.4.1) on the build host.

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
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/boost_e8_vb_quadrics.py --check
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
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/nullity8_fiber_import.py \
    --check docs/evidence/a5-kernel-attachments/nullity8-fiber-import-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/boost_fiber_variation.py \
    --check docs/evidence/a5-kernel-attachments/boost-fiber-variation-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/composed_limit_sections.py \
    --check docs/evidence/a5-kernel-attachments/composed-limit-sections-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-attachments/weight_slice_fiber_relations.py \
    --check docs/evidence/a5-kernel-attachments/weight-slice-fiber-relations-result.json
```

The `--check` command constructs the sorted, two-space-indented JSON plus its final newline in memory and compares
the UTF-8 bytes with the retained record. The command writes no record. The result contains integers, rationals,
exact symbolic expressions, and booleans; it contains no floating-point observations.
