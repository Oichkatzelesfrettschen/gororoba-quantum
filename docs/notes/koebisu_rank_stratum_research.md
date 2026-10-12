# Koebisu's dimension-32 rank question: geometry, reduction, and experiment design

Koebisu's [Discussion question 4](https://arxiv.org/html/2608.08232v1#S10)
asks how the zero-divisor variety `D14=0` decomposes according to
`dim ker L_x`. The repository answers the algebraic membership part for all
real coefficients and constructs one complete attachment family. The global
geometry of the remaining rank loci and the complete normalized pair space
remain open research obligations. A finite hardware sample measures the
implementation of selected operators; an exact geometric classification
requires mathematical certificates.

This note connects the primary literature to the
[rank-stratum construction](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md)
and identifies a smaller local calculation that can advance the geometric
question. The calculations below are deductions from the cited statements
and elementary linear algebra. They carry no priority claim.

## Source-to-method map

| Primary source and locator | Established input | Consequence for the work |
| --- | --- | --- |
| Biss, Christensen, Dugger, Isaksen, [Eigentheory, 0905.2987v1](https://arxiv.org/html/0905.2987v1), Lemma 2.3 and Propositions 3.9, 3.13, 3.20 | The adjoint is `L_conj(x)`; Gram eigenvalues are nonnegative, include `N=||x||^2`, and have fourfold multiplicity | Trace coefficients give exact rank predicates; pure elements admit a skew-symmetric local reduction |
| Koebisu, [2608.08232v1](https://arxiv.org/html/2608.08232v1), Definitions 3.1/3.3, Proposition 4.3, Theorems 5.3/9.1, Discussion Q4 | Newton recursion constructs `D14=E7` and `det L_x=N^2 E7^2`; the construction extends to dimension `2^n` | Retain the full coefficient sequence for rank membership and retain kernel data for geometry |
| Biss, Dugger, Isaksen, [Large annihilators, math/0511691v1](https://arxiv.org/html/math/0511691v1), Corollary 9.3, Lemma 9.5, Theorem 10.1, Corollary 14.7 | Zero divisors are doubly pure; ordinary embedding doubles the kernel; the maximal dimension-32 element locus is two copies of `V2(R7)` | Reduce the ambient coefficient domain, establish a genuine restricted induction, and use the known maximal stratum as a geometric control |
| Biss, Christensen, Dugger, Isaksen, [Large annihilators II, math/0702075v2](https://arxiv.org/html/math/0702075v2), Theorems 7.5/8.12 | A constrained D-locus is an `S5`-bundle; fixed-deficit families satisfy a stability theorem | Supply exact subfamilies and parameter-dependent hypotheses, rather than an unrestricted all-rank recurrence |
| Reggiani, [2411.18881v1](https://arxiv.org/html/2411.18881v1#S2.SS2), Section 2.2 | The normalized sedenion pair space is `G2`, with `SU(2) -> G2 -> V2(R7)` | Supply the dimension-16 bundle benchmark; the `SU(2)` fiber does not extend unchanged to larger kernels |
| Hatcher, [Algebraic Topology, Chapter 0](https://pi.math.cornell.edu/~hatcher/AT/ATch0.pdf), Propositions 0.17/0.18 | Appropriate contractible subspaces and homotopic attaching maps preserve homotopy type | Justify the restricted mapping-cylinder reduction after the geometric incidence model is established |
| Coste, [Introduction to Semialgebraic Geometry](coste-semialgebraic-geometry.md), Theorems 3.12, 4.1, 4.4 | Compatible finite triangulation of compact semialgebraic sets, Hardt triviality for continuous semialgebraic maps, and local conic structure | Supply existence theorems for global models and links while leaving their actual computation and gluing as explicit obligations |
| Córcoles et al., [2102.01682v1](https://arxiv.org/abs/2102.01682v1), PRL 127, 100501, [DOI](https://doi.org/10.1103/PhysRevLett.127.100501) | Dynamic phase estimation trades qubit use against measurement, feedback, and device noise | Require matched device controls when comparing folded and coherent implementations |

The [rank source ledger](cayley_dickson_rank_topology_sources.md) records
the mathematical hypotheses and known transcription caveats. The
[annihilator source ledger](cayley_dickson_annihilator_sources.md) separates
element bases from partner bundles. The
[block-encoding note](1806.01838.md) separates input normalization from LCU
normalization. These distinctions remain necessary when combining papers.

The direct inspection for this note covers Koebisu's Sections 3--5, 7, 9,
and 10. The retrieved HTML has SHA-256
`e7cb0aace6a034943a1ee99ece0796d3f05fc777ac1ecf4803b4e722bcc507c9`,
matching the earlier ledger. Discussion Q4 states the rank-stratum question
explicitly. Remark 4.2 overstates the obstruction to continuous eigenvalue
labeling: ordered eigenvalues of a real symmetric matrix admit continuous
labeling. The symmetric trace construction remains valid independently of
that remark. The other mathematical source locators inherit the primary
inspection scopes recorded in their linked notes.

## Rank predicates solve membership, while kernels carry gluing

Put `B=L_x^T L_x`, `N=||x||^2`, and `m=7` in dimension 32. Remove one
fourfold spectral block equal to `N`. The remaining seven block values
`beta_i` are nonnegative. Newton's identities give

```text
q_j = tr(B^j)/4 - N^j,
E_0 = 1,
j E_j = sum_(i=1)^j (-1)^(i-1) E_(j-i) q_i,
chi_B(z) = [(z-N) sum_(j=0)^7 (-1)^j E_j z^(7-j)]^4.
```

For `x != 0`, nullity `4k` is equivalent to
`E_(7-k)>0` and `E_(8-k)=0`. Positivity makes the implication exact: an
elementary symmetric sum of nonnegative entries vanishes precisely when
every product in that sum vanishes. The implemented predicates therefore
cover nullities 4, 8, 12, and 16 for arbitrary real coefficients. The
executable evaluator accepts rational coordinates; the all-real statement is
a theorem about the defining polynomials, rather than an equality oracle for
arbitrary real encodings.

The single determinant factor `E7` loses all distinctions between those
four nullities. Even the entire eigenvalue list loses eigenspace orientation
and transition functions. For example, a constant rank-one projection over
a circle and the projection onto the line at angle `theta/2` have identical
eigenvalues `{0,1}` at every point. Their kernel line bundles are respectively
trivial and Möbius. Their unit kernel bundles have respectively two connected
circles and one connected circle. This linear-algebra example does not claim
that both families arise from Cayley-Dickson multiplication. The example
identifies the information that spectral coefficients omit, so a geometric
classification must recover the actual kernel map.

Every `E_j` is nonnegative on real coefficient space. Consequently,
`grad E_j=0` at its real zeros. A zero gradient of `E7` therefore supplies
neither a dimension estimate nor a singularity classification for its real
zero set. The fixed-minor Schur equations in
[rank_charts.py](../../gororoba_quantum/rank_charts.py) retain the local
matrix information that the scalar polynomial conceals.

## Exact local collapse to the exceptional kernel

An exact Schur reduction converts the local geometric problem near an
exceptional point into a smaller matrix problem. The reduction preserves
rank and explicitly lifts every kernel vector. It does not require a
quantum measurement.

Let `x_*` be a nonzero doubly-pure dimension-32 element with kernel dimension
`k_*`. Every nonzero zero divisor belongs to the 30-dimensional real space
`C_5^perp`, so restrict nearby coefficients to that space. The adjoint
identity gives `L_x^T=-L_x`. Choose columns `V` spanning `ker L_(x_*)`
and columns `U` spanning its orthogonal complement, and set `T=[U,V]`.
Rational `x_*` admits rational choices. The columns need not be normalized.
The matrix congruence has the form

```text
T^T L_x T = [ A(x)     B(x) ]
            [-B(x)^T  D(x) ],
S(x) = D(x) + B(x)^T A(x)^(-1) B(x).
```

The matrix `A(x_*)` is invertible because a real skew-symmetric operator
maps its kernel complement isomorphically onto itself. Hence `det A != 0`
defines an open neighborhood of `x_*`. Block elimination proves

```text
rank L_x = (32-k_*) + rank S(x),
dim ker L_x = dim ker S(x),
ker L_x = { T[-A^(-1) B w; w] : S(x) w=0 }.
```

The exact residual identity is

```text
T^T L_x T[-A^(-1) B; I] = [0; S(x)].
```

The Schur matrix remains skew-symmetric. Its entries are rational functions
whose denominator divides `det A`; clearing that denominator preserves the
equations only on the stated open pivot domain. The construction uses an
8-, 12-, or 16-dimensional effective matrix near the corresponding
exceptional points. Near a nullity-four point, the fourfold-multiplicity
constraint leaves only nullities zero and four on this chart, and the local
zero-divisor locus is exactly `S=0`.

Near a maximal point, the possible Schur ranks are 0, 4, 8, 12, and 16.
These are pullbacks through the constrained map `x -> S(x)`. Treating `S`
as an arbitrary skew-symmetric matrix introduces inadmissible directions and
incorrect codimension counts. Pfaffian or minor equations can represent
these reduced rank conditions, but geometric use still requires the real
radical and dependence analysis of the pulled-back equations.

At the center, `B(x_*)=D(x_*)=0`, so the linearized equation simplifies:

```text
dS_(x_*)[h] = V^T L_h V.
```

Every differentiable curve through `x_*` that retains nullity `k_*` has a
tangent in the kernel of this linear map. Normalization adds
`<x_*,h>=0`. The map can supply a sharp tangent bound when the rank locus
is already known to be smooth, or an upper bound requiring higher-order
analysis elsewhere. The quadratic term `B^T A^(-1) B` records obstructions
that a first-order calculation can miss.

The resulting near-term implementation has four explicit acceptance checks:

1. Construct `U,V,A,B,D` from an existing exact rank certificate and verify
   the pivot determinant and full basis rank.
2. Verify the residual, skew-symmetry, rank, and kernel-lift identities with
   exact arithmetic, including a deliberately damaged sign or lift.
3. Compute the linear deformation map on all 30 doubly-pure coordinate
   directions and remove the radial direction for the unit base.
4. Resolve higher-order equations and overlaps before admitting a smooth
   stratum, a normal link, or an attachment map.

The repository already implements general pivot Schur charts. The
[retained finite research probe](../evidence/local_schur/README.md) implements
the skew reduction and derivative calculation on the stated fixtures. A
production chart API and a covering atlas of reduced germs remain proposed
extensions. The finite probe checks the six rational
perturbations `x_*(j)+e_i/3`, with `j=0,1,2` and `i=2,17`, where `x_*(j)`
is the unnormalized certified path endpoint. Every pivot remains invertible;
every reduced/full rank and lifted-residual identity agrees; all six
perturbations have zero nullity. The probe also computes the following
linearized bounds:

| Path endpoint | Kernel dimension | Rank of `h -> V^T L_h V` on `C_5^perp` | Unit-base linearized dimension | Rank in the path tangent direction |
| --- | ---: | ---: | ---: | ---: |
| 0 | 8 | 6 | 23 | 4 |
| 1 | 12 | 8 | 21 | 8 |
| 2 | 16 | 18 | 11 | 12 |

The last row agrees with the published maximal-stratum dimension
`dim V2(R7)=11`. The first two rows describe linearized constraints at two
specific points; they establish neither the dimensions of whole lower-rank
loci nor their smoothness. The probe supports a candidate atlas
implementation; its finite fixture domain remains distinct from the
all-real local identity proved above.

A complementary global compression comes from the source structures in
[Zhilina's doubly alternative paper](2608.26893.md), Lemmas 6.9--6.10.
For doubly-pure inputs, left multiplication is complex-antilinear and
skew-Hermitian in the stated complex structure. In orthonormal complex
coordinates, write `L_x(z)=K_x conjugate(z)` with `K_x^T=-K_x` and
`K_x` of size `16 x 16`. Conjugation is an invertible real map, so
`rank_R L_x=2 rank_C K_x`. Even complex rank of a skew-symmetric matrix
recovers the real fourfold rank restriction. Complex Pfaffian-minor equations
can then be split into real and imaginary parts to encode rank loci.
The source suggests a full-domain algebraic compression, whereas the Schur
reduction supplies smaller matrices near a chosen exceptional point.
The repository needs an explicit complex coordinate map, exact sign and
adjoint checks, and equivalence certificates before treating this route as
an implemented replacement for the `32 x 32` real matrix.

## Attachments require limiting kernel directions

The existing polynomial path has generic kernel `W` of dimension four and
exceptional kernels of dimensions 8, 12, and 16. Its exact construction
proves the restricted incidence space has homotopy type

```text
S7 wedge S11 wedge S15 wedge S4 wedge S4.
```

The Schur reduction gives a way to investigate additional approach
directions. A point near `x_*` has kernel equal to the lifted kernel of
`S(x)`. For a path `x(s) -> x_*`, retain the limiting subspace
`lim ker S(x(s))` when that limit exists. The lift tends to `V`, since
`B(x_*)=0`. Different approach directions may produce different subspaces
inside the same exceptional kernel. One shared four-plane along one path
therefore does not identify the full local attachment.

An attachment certificate needs an exact domain of approach directions,
the reduced kernel on that domain, its transition maps, and the limiting
inclusion into the exceptional kernel. A finite collection of paths can
refute a proposed universal limiting plane. A proof that the collection
covers every approach direction is a separate requirement. Once those
links and gluing maps cover the complete base, a compatible finite
topological model can support integral boundary matrices, torsion,
cohomology products, and specified homotopy invariants.

Ordinary zero padding supplies a genuine all-dimensional theorem for the
existing restricted family:

```text
Ann((a,0)) = Ann(a) x Ann(a),    a perpendicular to C_n.
```

After `n-5` embeddings, `g=4*2^(n-5)` and the restricted homotopy type is
`S^(2g-1) wedge S^(3g-1) wedge S^(4g-1) wedge S^g wedge S^g`.
The published induction proves that family for every `n>=5`. A universal
classification requires a covering recurrence for arbitrary operands and
all approach directions, beyond those ordinary embeddings.

The global construction has a rigorous semialgebraic foundation. Coste's
Theorem 3.12 applies to the compact algebraic incidence set `Z_5`, together
with the four semialgebraic subsets lying over its positive-nullity bases.
It guarantees a finite simplicial model compatible with those subsets.
Theorem 4.1 applies to the continuous semialgebraic projection `(x,y)->x`
and guarantees finite fiberwise product pieces. Theorem 4.4 identifies
sufficiently small local neighborhoods with cones on their links.
The [source note](coste-semialgebraic-geometry.md) records the exact
hypotheses and reading scope.

Existence of those models leaves three computational obligations: construct
the partition and its complete coverage certificate; identify the linear
kernel transition data within the pieces; and determine the links and
gluing across their frontiers. Hardt triviality does not make the original
rank loci smooth, and a topological fiber trivialization does not determine
a linear bundle isomorphism. A tractable implementation can use the local
Schur matrices to reduce the equations first, then certify overlap and
boundary compatibility. A finite triangulation of the whole incidence set
provides an independent route to global homology once its homeomorphism to
the defined algebraic set is established.

## Dimensional folding needs an explicit preserved object

The exact block reduction above preserves rank and lifts the kernel;
the affine-XOR decomposition in
[rank_attachments.py](../../gororoba_quantum/rank_attachments.py) preserves
the complete multiplication matrix up to input/output permutations. The
latter decomposition produces eight `4 x 4` blocks for the selected support
plane. Arbitrary real coefficients need not preserve those eight blocks.

A coefficient projection, a combinatorial count, a unitary register reuse,
and a deformation retraction preserve different objects. A transfer from
`open_gororoba` requires the precise map and its hypotheses. In particular,
for a candidate algebra collapse `P`, test `P(xy)=P(x)P(y)` before calling
`P` multiplicative. Even multiplicativity only sends zero products to zero
products; a normalized pair can collapse to zero, and a bundle or homotopy
equivalence needs additional nonvanishing, lifting, and inverse-homotopy
arguments. The [sister-repository proof audit](open_gororoba_folding_proofs.md)
records the actual Rocq theorem statements separately from surrounding
research labels.

## Four probes identify four quadratic values, not a general Gram matrix

For a real `4 x 4` sector operator `M`, define `G=M^T M`. An ideal LCU
success probability for a real unit probe `v` is

```text
p(v) = v^T G v / alpha^2.
```

A real symmetric `4 x 4` matrix has ten independent entries. Four probes
give at most four independent linear functionals of those entries, leaving
a linear nullspace of dimension at least six. Around a positive-definite
matrix, sufficiently small perturbations in that nullspace remain positive
definite and give exactly the same four probabilities. A restricted
parametric model may need fewer probes, but its identifiability must be
proved and recorded. Combining probes at different path parameters requires
an additional shared model because the Gram matrix changes with the
parameter.

One informationally complete real design uses the four coordinate probes
and the six pair probes `(e_i+e_j)/sqrt(2)`. They recover

```text
G_ii = alpha^2 p(e_i),
G_ij = alpha^2 p((e_i+e_j)/sqrt(2)) - (G_ii+G_jj)/2.
```

A general complex Hermitian model has sixteen real parameters and also
needs imaginary-quadrature probes. The real design establishes completeness
only under the real-symmetric hypothesis. Measurement noise and state
preparation errors still require a separate model; a finite positive
estimate of a small eigenvalue does not settle exact mathematical nullity.

Normalization also changes the experimental cost. Reconstructing the
squared norm `q=alpha^2 p` multiplies a probability half-width by `alpha^2`.
When `alpha` rises from 2 to 4, the same probability half-width produces
four times the squared-norm uncertainty. A fixed worst-case Hoeffding bound
for that squared norm scales its shot count as `alpha^4`, giving a factor
of sixteen. The actual binomial variance is
`alpha^4 p(1-p)/shots`; the realized cost also depends on `p` and runtime
overhead. Comparing probability precision alone conceals this physical
observable cost.

## Prioritize a model decision before an atlas

The immediate scientific decision is whether a specific optimizer change
improves a specified hardware observable at equal or lower charge. The
existing raw QPU records first constrain competing models. Terminal readout,
feedback timing, scheduling, and crosstalk are separate candidate mechanisms;
one successful fit does not establish its physical cause.

1. Define candidate models and a held-out contrast before using the new
   results. State which ideal or noisy distributions differ and which
   alternatives remain observationally equivalent.
2. Select the smallest set of existing or proposed rows that separates
   those models. For two fixed Bernoulli models, expected log-likelihood
   information per shot is a Kullback-Leibler divergence; compare that
   information against calibrated per-shot cost and overhead. Unknown
   nuisance parameters require a composite-model analysis.
3. Choose one optimizer decision, such as matched terminal qubit placement,
   latency-aware scheduling, or a native compilation choice. Match layout,
   measurement route, and control conditions where the causal comparison
   requires them. A changed terminal writer confounds a feedback-only claim.
4. Preregister a practically meaningful improvement or equivalence margin,
   an uncertainty method, the familywise error allocation, and a seconds
   ceiling. A detectable effect above zero differs from a useful accuracy
   gain; a narrow interval differs from an equivalence decision.
5. Validate the chosen intervention on an independent contrast. Expand the
   atlas only when additional rows test a new model distinction, a new
   mechanism, or a deliberately sampled stability claim.

The existing proposed rank-sector probes can test known dark/bright laws
and hardware deviations. Their scientific value becomes concrete when the
result selects or rejects an optimizer action. They do not compute the
unknown topology in Discussion Q4. Exact rank geometry directs useful
operator selection; hardware measurements characterize the noisy execution
of those operators. Those two evidence streams meet at a specified
observable, rather than through a claim that shot data prove global
topology.

## Replay and completion conditions

Run the implemented exact mechanisms from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error rank_polynomials.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error rank_charts.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error rank_attachments.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error rank_path_topology.py --stage 5
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error rank_path_topology.py --stage 6
)
```

The [retained local Schur probe](../evidence/local_schur/probe.py) uses
`path_matrix(j).columnspace()` for `U` and
`path_matrix(j).nullspace()` for `V`; it evaluates the displayed identities
at `j=0,1,2` and perturbation indices `2,17` with coefficient `1/3`.
Flattening the strict upper triangle of `V^T L_(e_i) V` for all
`i` except `0,16` reproduces the table's deformation ranks with exact
elimination. The unit-base bound is `30-rank-1`; the last subtraction
removes the radial direction, which already lies in the deformation kernel.
The [result](../evidence/local_schur/result.json) records source digests,
rank/lift identities, and negative controls. Replay the retained result with
`--check` under both normal execution and `-O`, as the bundle README specifies.

Completion of Q4's geometric program requires certified coverage of the
continuous rank loci, their smooth subdivisions, kernel bundles, closure
links, and attaching maps. Completion of the pair-space program then
requires a proved global model and invariants computed from that model.
The determinant identity, local reduction, finite probes, and restricted
induction each advance a named part of the program with a distinct
acceptance boundary.
