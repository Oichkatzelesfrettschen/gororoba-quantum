# Exact rank strata and restricted Cayley-Dickson attachment topology

The normalized pair space has several distinct evidence surfaces. Exact rank
predicates describe every real coefficient vector. Kernel charts describe a
bundle over a fixed rank. A path with certified exceptional ranks supplies a
restricted attachment model. A classification of the complete pair space also
needs the topology of every base stratum and all attachments between them.
These constructions retain those distinctions.

Write `A_n` for the real Cayley-Dickson algebra of dimension `d=2^n`, with
`(a,b)(c,d)=(ac-conj(d)*b, d*a+b*conj(c))`. Define

```text
Z_n = {(x,y) in A_n x A_n : ||x||=||y||=1, x*y=0},
D_(n,k) = {x in A_n : ||x||=1, dim ker L_x=k}.
```

The projection `(x,y) -> x` has fiber `S^(k-1)` over `D_(n,k)`. For `n=5`,
the nonempty positive-nullity loci have `k=4,8,12,16`. The published
all-dimensional bound and occurrence theorem establish the possible values;
the formulas below describe membership for arbitrary real coefficients.

The maximal element base already has a published classification. Corollary
14.7 of Biss-Dugger-Isaksen gives `D_(5,16)` as two disjoint copies of
`V_2(R^7)`. More generally, Theorem 15.7 identifies `D_(n,M_n)` with
`2^(n-4)` copies of `V_2(R^7)`, where `M_n=2^n-4*n+4` and `n>=4`.
These statements concern unit elements. The normalized partner fiber over
`D_(5,16)` is `S15`, and over `D_(n,M_n)` it is `S^(M_n-1)`; base and
fiber homeomorphism types alone do not determine the total sphere bundle or
its attachments to lower-nullity loci. The remaining dimension-32 base
geometry therefore focuses on `D_(5,4)`, `D_(5,8)`, and `D_(5,12)`, while
retaining the known maximal base.

The global incidence equations use the signed basis product
`e_i*e_j=sign(d,i,j)*e_(i XOR j)`. For each `ell=0,...,d-1`, define

```text
F_ell(x,y) = sum_(i=0)^(d-1) sign(d,i,i XOR ell)*x_i*y_(i XOR ell).
```

The `d` equations `F_ell=0`, together with `sum x_i^2=1` and
`sum y_i^2=1`, define exactly `Z_n`. They make `Z_n` a compact real algebraic
set described by `d+2` quadratic equations. An exact global presentation does
not by itself determine a triangulation, smooth stratification, or homotopy
type. The general proofs below are written mathematical arguments; executable
certificates check their specified finite algebraic identities.

Published annihilator results permit a smaller equivalent ambient description.
Corollary 9.3 and Lemma 9.5 of Biss-Dugger-Isaksen imply
`x_0=x_(d/2)=y_0=y_(d/2)=0` for every unit zero-product pair. The complex
inner product is the projection of `x*conj(y)` onto `C_n`; since `y` is
imaginary, the zero product implies complex orthogonality. For `n>=4`,
`Z_n` is therefore a closed subset of the complex Stiefel manifold
`V_2(C^(d/2-1))`. In dimension 32, eliminating the four zero coordinates
leaves 60 real variables; imposing the two unit norms and complex
orthogonality gives a smooth ambient manifold of real dimension 56.
That ambient dimension is an upper bound, rather than the dimension of `Z_5`.

The scalar and distinguished-coordinate product equations already express the
two real components of complex orthogonality, up to sign. Replacing those two
equations by complex orthogonality is valid; dropping them is insufficient.
For example, the unit doubly-pure pair `x=y=e1` satisfies the remaining product
coordinates but has scalar product `-1`. These coordinate reductions concern
the incidence presentation. The trace/Newton theorem below retains the full
`d x d` multiplication matrix; truncating its domain changes the spectral
hypotheses.

## Existing mechanisms and their roles

| Module | Mathematical or executable role |
| --- | --- |
| [cd_core.py](cd_core.py) | Shared doubling convention, signed basis products, and multiplication matrices |
| [claim_boundaries.py](claim_boundaries.py) | Finite counterexamples and circuit checks for the original three scientific claims |
| [sedenion_bundle.py](sedenion_bundle.py) | Explicit sedenion charts, transitions, principal action, and numerical admission |
| [annihilator_strata.py](annihilator_strata.py) | Signed sparse census and exact maximal-annihilator witnesses |
| [rank_polynomials.py](rank_polynomials.py) | Exact incidence equations, trace/Newton evaluation, and rank-locus predicates |
| [rank_charts.py](rank_charts.py) | Rational fixed-minor kernel frames and their overlap identities |
| [rank_attachments.py](rank_attachments.py) | Polynomial path, exceptional ranks, and common-kernel certificates |
| [integral_homology.py](integral_homology.py) | Verified integer Smith transformations and torsion-preserving chain homology |
| [rank_path_topology.py](rank_path_topology.py) | Restricted incidence quotient, endpoint nullhomotopies, sphere-wedge invariants, and embedding induction |

The [primary-source ledger](../literature/notes/cayley_dickson_rank_topology_sources.md)
records the published hypotheses, the local derivations, and the checked source
versions. Source theorems, general algebraic proofs, exact finite checks, and
numerical simulations carry separate conclusions. A quantum measurement tests
a circuit observable; it supplies neither a universal rank proof nor a
classification of a continuous pair space.

## Exact polynomial predicates for every real coefficient vector

Let `N=||x||^2` and `B=L_x^T*L_x`. The adjoint identity
`L_x^T=L_conj(x)` makes `B` positive semidefinite. For nonzero `x`, the
published eigentheory gives fourfold multiplicity for every eigenvalue and
includes `N` among the eigenvalues. For `n>=2`, set `m=2^(n-2)-1`. Count the
spectrum as fourfold blocks and remove one block equal to `N`. The remaining
`m` block values are nonnegative real numbers `beta_1,...,beta_m`.

Define polynomials by exact traces and Newton recursion:

```text
q_i(x) = trace(B^i)/4 - N^i,
E_0(x) = 1,
E_j(x) = (1/j) * sum_(i=1)^j (-1)^(i-1) E_(j-i)(x) q_i(x).
```

Each `E_j` is homogeneous of degree `2*j`. Newton's identities identify
`E_j` with the elementary symmetric function of degree `j` in the `beta`
values. Consequently, `E_j>=0` for every real coefficient vector. If exactly
`s<m` of those values are positive, then `E_s>0` and `E_(s+1)=0`. Conversely,
those two conditions imply exactly `s` positive values: each elementary
symmetric sum contains nonnegative terms, and any `s+1` positive entries would
make `E_(s+1)>0`. The removed `N` block is positive. Therefore, for `1<=k<=m`,

```text
nullity(L_x) = 4*k
    if and only if E_(m-k)(x)>0 and E_(m-k+1)(x)=0.
```

Invertibility is equivalent to `E_m>0`; `E_0=1` handles the endpoint of the
coefficient sequence. The zero input requires separate admission because its
removed block is also zero. Unit normalization excludes that input from `Z_n`.

For dimension 32, `m=7`, so the complete positive-nullity predicates are:

| Nullity | Unit rank-locus predicate | Degrees of positive and zero coefficients |
| --- | --- | --- |
| 4 | `N=1`, `E_6>0`, `E_7=0` | 12, 14 |
| 8 | `N=1`, `E_5>0`, `E_6=0` | 10, 12 |
| 12 | `N=1`, `E_4>0`, `E_5=0` | 8, 10 |
| 16 | `N=1`, `E_3>0`, `E_4=0` | 6, 8 |

The dimension bound excludes larger positive nullities for nonzero inputs.
For example, the exact unit vector `(e1+e10+e18-e25)/2` has
`(E_0,...,E_7)=(1,7,14,8,0,0,0,0)`. The predicate `E_3>0,E_4=0`
identifies its nullity 16. Its Gram characteristic polynomial is
`z^16*(z-1)^8*(z-2)^4*(z-4)^4`; the executable audit compares that invariant
presentation with an independent exact characteristic polynomial.

These equations exhaust the real coefficient domain; they do not enumerate its
connected components. The trace recursion represents the defining polynomials
without expanding their potentially enormous monomial lists. Exact rational
arithmetic preserves the divisions by four and by `j`; integrality of every
polynomial coefficient is a separate question.

The symbolic formulas define sets over all real coefficients. The executable
point evaluator, `evaluate_rank_polynomials`, accepts integer and `Fraction`
coordinates and returns exact rational coefficients; `rank_locus` checks a
requested nullity against that evaluation. Binary floating-point coordinates
fall outside that input contract. The all-real theorem does not supply a
uniform exact equality oracle for arbitrary encodings of real numbers.
For a nonzero rational vector `a`, its unit representative `x=a/sqrt(N(a))`
may have irrational coordinates. Homogeneity still gives the exact identity
`E_j(x)=E_j(a)/N(a)^j`; the positive normalization leaves the rank predicate
unchanged and requires no floating-point coordinate conversion.
`incidence_presentation` generates the symbolic equations defining the complete
normalized incidence set; its output remains a presentation rather than a
classification.

The same proof gives

```text
det(L_x) = N^2 * E_m^2,
chi_B(z) = [(z-N) * sum_(j=0)^m (-1)^j E_j z^(m-j)]^4.
```

The determinant sign follows by writing `x=r*1+u` with imaginary `u`.
The matrix `L_u` is real skew-symmetric, so
`det(r*I+L_u)=product_j(r^2+sigma_j^2)>=0`. The Gram determinant therefore
fixes `det(L_x)` with the displayed nonnegative sign. The
characteristic-polynomial expression is an invariant presentation in terms of
traces, rather than a geometric classification of the attainable spectra.

## Kernel charts, transitions, and smoothness

Fix rank `r=d-k`. Select row indices `I` and column indices `J` of size `r`
whose pivot matrix `P=L_x[I,J]` is invertible. Let `K` be the complementary
column indices, and reorder the matrix into blocks

```text
L_x = [P Q; R S].
```

On the fixed-rank locus, `S-R*P^(-1)*Q=0`. A rational kernel frame `F` has
rows `J` equal to `-P^(-1)*Q` and rows `K` equal to the identity. Its columns
are independent and span the whole kernel. The conditions

```text
det(P) != 0,
det(P)*S - R*adj(P)*Q = 0
```

give polynomial equations and an open pivot condition. Every rank-`r` matrix
has such a pivot, so the family indexed by all admissible row/column subsets
covers the rank locus. A finite witness collection tests selected charts; the
linear-algebra argument supplies coverage over all real points.

For charts `alpha,beta`, let `R_beta` select the free-coordinate rows of
chart `beta`. The coordinate change from `alpha` to `beta` is
`T_(beta,alpha)=R_beta*F_alpha`. On an overlap,

```text
F_alpha = F_beta*T_(beta,alpha),
T_(gamma,alpha) = T_(gamma,beta)*T_(beta,alpha).
```

The API `chart_transition(source,target)` returns `T_(source,target)`, which
maps target coordinates into source coordinates. `ConstantRankChart.certify`
checks an exact rational point; `symbolic_domain` records the determinant and
adjugate polynomial contract over the real coefficient domain.

With `G_alpha=F_alpha^T*F_alpha`, unit partners have coordinates satisfying
`t^T*G_alpha*t=1`. The transition preserves that metric:
`T_(beta,alpha)^T*G_beta*T_(beta,alpha)=G_alpha`. The ellipsoid form retains
exact rational coefficients; a Euclidean orthonormal frame may introduce
algebraic square roots. Raw-frame transitions lie in `GL(k,R)` and preserve
the chart-dependent Gram metrics; they need not be Euclidean-orthogonal.
Higher-dimensional charts require their actual transition group; the sedenion principal `SU(2)` action does not automatically
extend to every kernel bundle.

The compact coefficient predicates cannot establish smoothness by a
regular-value test. A differentiable globally nonnegative polynomial satisfies
`grad(E_j)=0` at every real zero, because each zero is a minimum. Vanishing
Jacobian rows therefore reflect the chosen equation and do not prove that the
underlying rank locus is singular. Pivot-Schur equations also require analysis
of dependent equations, the real radical, or transversality. The map from
coefficient vectors to multiplication matrices is highly constrained; the
codimension of an unrestricted matrix rank stratum cannot be transferred to
its pullback without proof.

## Closure constraints and an exact attachment path

Nullity is upper semicontinuous: a limit of rank-`r` matrices has rank at most
`r`. Thus

```text
closure(D_(n,k)) is contained in union_(j>=k) D_(n,j).
```

The norm-one condition is closed, so the limit remains in the normalized base.
This inclusion supplies a necessary closure constraint. Equality, incidence
with every component, and the local links of the closure require additional
proofs. An exact path proves the specific attachment it reaches.

In dimension 32, consider the polynomial vector

```text
a(t) = e1 + (t-1)^2*e10 + t*(3-t)/2*e18 - t*(t-1)/2*e25,
x(t) = a(t)/||a(t)||.
```

The coefficient of `e1` is one, so `a(t)` is nonzero for every real `t`.
Moreover, `(x_18-x_25)/x_1=t`, which makes the normalized path injective.
Its exceptional kernel dimensions are

```text
t=0:  8,    t=1: 12,    t=2: 16,
all other real t: 4.
```

The support is an affine XOR plane. Permuting rows and columns divides the
left-action matrix into eight `4x4` blocks. Four blocks have determinants,
up to sign,

```text
(t-2)*(t-1)*(t^2-t+2)*||a(t)||^2/2.
```

The other four blocks have identically zero determinant and a `3x3` minor,
up to sign,

```text
t*(t-2)^2*(t-1)*(t^2-t+2)/2.
```

The factor `t^2-t+2=(t-1/2)^2+7/4` is strictly positive. Together with exact
endpoint ranks, those polynomial identities certify the rank for every real
parameter, rather than only a sampled parameter grid.

A constant orthonormal basis of the common four-dimensional kernel `W` is

```text
(-e4+e15+e23+e28)/2,
(-e5-e14-e22+e29)/2,
(-e6+e13+e21+e30)/2,
(-e7-e12-e20+e31)/2.
```

Coefficientwise multiplication proves `L_a(t)*W=0`; the generic rank proof
makes `W` the entire kernel away from the three exceptional points.

## A complete topological model for the restricted path

Let `X_5` be the full normalized partner incidence over `x([0,2])`, as a
subspace of `Z_5`. Write `K_i=ker L_a(i)` for `i=0,1,2`. The exact kernel
identities give a homeomorphism from the following compact quotient to `X_5`:

```text
S(K_0) joined to S(K_1) by S(W) x [0,1],
S(K_1) joined to S(K_2) by S(W) x [1,2],
with each cylinder end attached by the literal inclusion S(W) -> S(K_i).
```

The map sends a cylinder point `(y,t)` to `(x(t),y)` and an exceptional sphere
point `y` to `(x(i),y)`. Injectivity of `x(t)` and the complete kernel statement
make the quotient map bijective. Compactness of the domain and the Hausdorff
property of the incidence subspace make the bijection a homeomorphism.

Each endpoint inclusion is nullhomotopic. Choose a unit vector `u_i` in
`K_i` perpendicular to `W`; the homotopy
`((1-s)*y+s*u_i)/sqrt((1-s)^2+s^2)`, for `0<=s<=1`, contracts the included
`S(W)` to `u_i` inside `S(K_i)`. Orthogonality gives unit norm, and
`(1-s)^2+s^2=2*(s-1/2)^2+1/2` certifies a positive denominator.
Replacing the four attaching maps by these constant maps preserves homotopy
type. Collapsing the connecting tree leaves

```text
X_5 homotopy equivalent to S7 wedge S11 wedge S15 wedge S4 wedge S4.
```

The mapping-cylinder argument uses the homotopy extension property, as in
Hatcher, Propositions 0.17 and 0.18. It yields a homotopy equivalence; the
sphere wedge is not asserted to be homeomorphic to the incidence subspace.
The integral homology is `H_0=Z`, `H_4=Z^2`, and `H_7=H_11=H_15=Z`, with
all other groups zero. The space is simply connected, its Euler characteristic
is zero, and products of positive-degree cohomology classes vanish. The
homotopy groups of a wedge also contain interactions such as Whitehead
products; listing the summand spheres does not turn all homotopy groups into
a direct sum of sphere groups.

## A uniform restricted construction in every higher dimension

For `n>=5`, embed the same path by zero padding: `a_(n+1)(t)=(a_n(t),0)`.
The path is perpendicular to `C_n=span(1,i_n)` at every level. The published
ordinary-embedding formula gives the full kernel identity

```text
Ann(a_(n+1)(t)) = Ann(a_n(t)) x Ann(a_n(t)).
```

After `n-5` embeddings, put `g=4*2^(n-5)`. The generic common kernel has
dimension `g`; the exceptional kernels have dimensions `2g,3g,4g`. The same
quotient construction and explicit nullhomotopies prove

```text
X_n homotopy equivalent to
S^(2g-1) wedge S^(3g-1) wedge S^(4g-1) wedge S^g wedge S^g.
```

This is an all-dimensional theorem for a specified restricted family. Its
proof uses the exact dimension-32 path identities and induction, rather than
extrapolating finite machine checks. The formula does not identify `X_n` with
all of `Z_n`. The remaining pair space includes bases outside the embedded
path, smaller-nullity strata, and additional attachment directions.

## Replay and retained certificates

Run the checks from the repository root with the selected interpreter:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" rank_polynomials.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" rank_charts.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" rank_attachments.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" integral_homology.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" rank_path_topology.py --stage 5
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" rank_path_topology.py --stage 6
)
```

The commands write local audit JSON to stdout. The rank-polynomial default
corpus reaches dimension 32; `--max-dimension 64` extends that finite corpus.
Fixed dimension-32 normalization, directional-derivative, and incidence
regressions run with every corpus setting. `directional_derivatives` checks
the differentiated trace/Newton recurrence with exact rational inputs.
The topology `--stage` parameter uses the doubling index `n`, with algebra
dimension `2^n`. Its executable interval is `5<=n<=256`; the written induction
covers every integer `n>=5`. The sparse chain construction records only
nonzero degrees and avoids materializing an exponentially large array of
empty chain groups. Stage instantiation evaluates the restricted theorem's
formula; it is distinct from reconstructing every multiplication matrix at
that dimension.

Retained evidence:

- [Rank-polynomial and incidence audit](../results/hw_estimate/rank_polynomials.json).
- [Dimension-64 rank-polynomial audit](../results/hw_estimate/rank_polynomials_dimension64.json).
- [Kernel-chart audit](../results/hw_estimate/rank_charts.json).
- [Polynomial attachment audit](../results/hw_estimate/rank_attachments.json).
- [Integral chain-homology audit](../results/hw_estimate/integral_homology.json).
- [Dimension-32 restricted topology audit](../results/hw_estimate/rank_path_topology.json).
- [Dimension-64 embedded topology audit](../results/hw_estimate/rank_path_topology_embedded.json).
- [Source and execution verification manifest](../results/hw_estimate/rank_topology_verification.json).

The Smith-normal-form verifier checks unimodular changes of basis and expresses
the next boundary in the resulting integer kernel basis. Rational ranks alone
would lose torsion information. The geometric quotient and nullhomotopies
identify the particular chain complex with the restricted incidence space;
the generic homology routine certifies only the supplied chain complex.

## Global classification roadmap and admission gates

1. **Verify the rank and chart mechanisms.** Compare exact Newton predicates
   with independent matrix elimination on sparse, dense rational, zero, and
   invertible inputs. Check pivot residuals, frame rank, inverse transitions,
   cocycles, and Gram preservation. Mutations must fail the relevant gate.
2. **Certify restricted attachments.** Verify the complete block polynomial
   identities, exceptional ranks, constant common kernel, normalization, and
   endpoint inclusion certificates. Verify the quotient model and its cellular
   homology. Retain polynomial certificates rather than sampled plots alone.
3. **Describe the remaining base components in dimension 32.** Preserve the
   published two-component `V_2(R^7)` description of `D_(5,16)`. Starting from
   the exhaustive rank predicates, compute certified semialgebraic
   decompositions and connected components for `D_(5,4)`, `D_(5,8)`, and
   `D_(5,12)`. Record a covering argument for every real coefficient vector
   and exact admission for boundaries. A list of successful numerical charts
   does not meet this condition. First local slice:
   [rank_locus_local_dimension](../docs/evidence/rank_locus_local_dimension/README.md)
   certifies local dimensions 11, 17 and 23 at witnesses of the
   zero-divisor-only families of `D_(5,16)`, `D_(5,12)` and `D_(5,8)`. Every
   family with a non-zero-divisor coordinate sits two below its exact
   tangent bound, an open gap; witnesses outside `H_5^perp` carry upper
   bounds only.
4. **Resolve local regularity and links.** Prove which pieces are smooth using
   independent local equations. Construct a suitable stratification, dimensions,
   normal links, and componentwise closure incidences. Keep rank loci and smooth
   strata distinct when one rank locus needs several pieces.
5. **Determine the kernel bundles on those pieces.** Compute their actual
   transition data and equivalence classes. Characteristic classes and monodromy
   provide invariants; their sufficiency for classifying a given bundle requires
   a separate argument.
6. **Construct all attachments.** Determine how partner spheres specialize
   across every admitted closure incidence, including directions absent from
   the polynomial path. A frontier matrix alone omits the attaching maps.
7. **Certify a global model and invariants.** Produce a finite topological model
   with a proved map to `Z_5`, such as a compatible triangulation or a complete
   homotopy-colimit construction. Compute chain maps, boundary operators,
   homology, cup products, and explicitly selected homotopy invariants. Homology
   agreement alone does not establish a homotopy equivalence.
8. **Establish uniform structure beyond the restricted family.** Prove a
   recurrence or other structural theorem controlling every stratum and every
   attachment for arbitrary `n`. An algorithm that accepts `n`, and a compact
   system of defining equations, provide different deliverables from such a
   classification theorem. The published fixed-deficit stability theorem covers
   near-maximum element families; its hypotheses do not exhaust all nullities
   as `n` increases.

The complete `Z_5` classification and the unrestricted all-dimensional theorem
remain research obligations. The scalar equations, kernel atlas, and restricted
homotopy model supply exact starting points with explicit boundaries.
