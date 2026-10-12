# Ordinary doubling of the fixed-support incidence model

The [doubling module](../../gororoba_quantum/four_support_doubling.py)
extends the four-coordinate family through ordinary zero padding. A
structural induction establishes the rank, complete kernel, and normalized
partner-incidence model for every Cayley-Dickson stage `n>=5`. The exact
implementation expands frames and operators through dimension 256 and
provides allocation-free exponent descriptors for larger stages.

The first operand remains
`x_5=a e1+b e10+c e18+d e25`, with `x_(n+1)=(x_n,0)`.
Its normalized coefficient base remains the same `S3`, defined by
`N=a^2+b^2+c^2+d^2=1`. The partner ranges over the entire
`2^n`-dimensional algebra. Other first-operand coefficient directions
remain outside the classification.

The [base rank theorem](four_support_rank_loci.md) and
[base incidence homeomorphism](four_support_incidence_geometry.md) supply
the induction base. The [retained replay](../evidence/four_support_doubling/README.md)
checks exact polynomial identities at three doubling transitions and
rational API behavior at stages five through eight. The structural proof
below supplies the all-dimensional statement; larger finite samples alone
would supply a weaker result.

## Structural operator and kernel induction

The repository uses the doubling convention

```text
(a,b)(c,d)=(ac-conj(d)b, da+b conj(c)),
conj(a,b)=(conj(a),-b).
```

Conjugation is an involutive anti-automorphism at every stage. The real
base has the property. Assuming it in the lower algebra, distributivity
and the two-term multiplication rule give

```text
conj((a,b)(c,d))
  =(conj(c)conj(a)-conj(b)d, -da-b conj(c))
  =conj(c,d) conj(a,b).
```

Every displayed product preserves its indicated binary grouping. The
calculation therefore applies throughout the nonassociative tower.
Conjugation acts on real coordinates by the orthogonal involution
`C_n=diag(1,-1,...,-1)`.

For right multiplication `R_x(y)=yx`, the conjugation identity implies

```text
R_x=C_n L_conj(x) C_n.
```

Every zero-padded `x_n` in the fixed support is pure: its scalar
coordinate vanishes. Hence `conj(x_n)=-x_n` and

```text
R_x=-C_n L_x C_n.
```

The doubling convention also gives, directly,

```text
(x,0)(u,v)=(xu,vx),
L_(x,0)=diag(L_x,R_x).
```

Writing `K_n=ker L_(x_n)` therefore gives the complete kernel identity

```text
K_(n+1)=K_n direct_sum C_n K_n,
dim K_(n+1)=2 dim K_n.
```

The recurrence holds for every stage. The right-action conjugation minus
and the different left/right blocks are essential operator data, even when
some kernel subspaces agree after conjugation.

## Five factor blocks and complete recursive frames

Keep the base scalar factors

```text
Delta=a^2+b^2-c^2-d^2,
p=a-b-c-d, q=a-b+c+d,
r=a+b-c+d, s=a+b+c-d.
```

Put `h_n=4*2^(n-5)=2^(n-3)`. The base polynomial frame `G_5` has shape
`32x20`, grouped into five blocks of four columns, with positive diagonal
Gram matrix `D_5=G_5^T G_5`. The base certificate also supplies a residual
frame `H_5` satisfying

```text
L_(x_5) G_5=H_5 M_5,
M_5=diag(Delta I4,p I4,q I4,r I4,s I4).
```

The letter `H` denotes a residual frame; `R_x` continues to denote right
multiplication. For each stage, first form two copies and then regroup
columns into the same five factor blocks. For old block size `h`, the
column order is

```text
copy*(5*h)+factor*h+local,
factor=0,...,4; copy=0,1; local=0,...,h-1,
```

listed in that order. Let `P_n` be the corresponding permutation matrix.
Define

```text
G_(n+1)=diag(G_n,C_n G_n) P_n,
D_(n+1)=P_n^T diag(D_n,D_n) P_n,
H_(n+1)=diag(H_n,-C_n H_n) P_n.
```

Orthogonality of `C_n` proves
`G_(n+1)^T G_(n+1)=D_(n+1)`, with strictly positive diagonal for every
nonzero coefficient tuple. The operator identity proves

```text
L_(x_(n+1)) G_(n+1)=H_(n+1) M_(n+1),
M_(n+1)=diag(Delta I_(2h),p I_(2h),q I_(2h),r I_(2h),s I_(2h)).
```

The lower residual minus follows from `R_x C_n=-C_n L_x`.
Column regrouping depends only on the stage. It remains constant across
rank boundaries.

The base theorem states that precisely the zero-factor blocks span the
complete kernel. The kernel direct-sum identity carries completeness to
the next stage. Induction therefore proves completeness of every `G_n`
with the same five masks. If `k` of the five scalar factors vanish, then

```text
dim ker L_(x_n)=k h_n,  k in {0,1,2,3,4}.
```

The origin remains excluded from the normalized family. At the origin,
ordinary multiplication is the zero operator and its kernel is the whole
ambient algebra; the nonzero factor formula requires its stated domain.

The 96 normalized base strata and 704 closure incidences persist,
including 96 reflexive and 608 strict incidences. Each prior four-column
factor block expands to `h_n` columns. The literal coordinate-inclusion
maps along closures expand by the same rule. The base geometry changes
neither its sign labels nor its closure relation.

## Uniform normalized incidence and exact weighted inverse

Set `F_n=G_n D_n^(-1/2)` using the positive diagonal square roots.
Every `F_n` is continuous on the entire coefficient sphere and satisfies
`F_n^T F_n=I_(5h_n)`.

Let `z=(z_cone,z_p,z_q,z_r,z_s)` with each block in `R^(h_n)`. Define

```text
Y_n={(x,z) in S3 x S^(5h_n-1):
       Delta(x) z_cone=0,
       p(x) z_p=q(x) z_q=r(x) z_r=s(x) z_s=0}.
```

Let `Z_n` be the actual normalized pair incidence with the fixed
coefficient input, partner `y in S^(2^n-1)`, and `x_n y=0`.
The maps

```text
Phi_n(x,z)=(x,F_n(x)z),
Psi_n(x,y)=(x,F_n(x)^T y)
```

are continuous inverses. The factor equations and orthonormality prove
the forward kernel and norm conditions. Inductive kernel completeness
proves `F_n F_n^T y=y` on actual kernels and supplies the inverse identity.
Both formulas are continuous in the ambient product topologies, so the
homeomorphism includes all rank boundaries.

A base point with `k>0` zero factors has unit-partner fiber
`S^(k h_n-1)`. A point with `k=0` has an empty unit-partner fiber.
The weighted model uses

```text
M_n w=0,  w^T D_n w=1,
y=G_n w,  w=D_n^(-1) G_n^T y.
```

The weighted maps use exact rational operations at rational inputs.
Positive normalization relates them to the standard sphere model.

The largest nullity in this restricted family is `4h_n=2^(n-1)`.
The restriction matters at higher stages: dimension 64 has restricted
maximum 32, whereas the published ambient maximum is 44. The growing
partner dimension does not enlarge the four-dimensional coefficient base
into the full algebra.

## Executable API and resource boundary

`DoublingModel(stage)` validates every integer stage at least five and
stores exponent metadata. `record()` retains the exponents for the
ambient and factor-block dimensions; it never constructs `2^stage`.
The regression includes stage `10^9` to check that contract.

Expanded APIs accept stages five through eight, corresponding to ambient
dimensions 32 through 256. The guard precedes exponent shifts, matrix
construction, and recursive allocation. The expansion limit bounds local
work and differs from the theorem's unlimited stage domain.

- `expanded_frame(stage, coefficients)` reuses the base rational frame
  and constructs the exact regrouped frame, positive Gram diagonal, and
  repeated factors.
- `apply_left(stage, coefficients, partner)` applies the left/right
  recurrence through a dimension-32 basis-action kernel. It accepts the
  zero multiplier because multiplication at zero remains defined.
- `lift_kernel_coordinates()` validates all repeated factor equations
  and returns the exact partner vector.
- `kernel_coordinates()` verifies actual kernel membership and computes
  the weighted inverse, then checks its forward reconstruction.
- `kernel_inclusion()` expands the literal factor-slot inclusion along
  a validated base closure incidence.
- `doubling_column_order(source_stage)` exposes the canonical regrouping
  for a transition whose target stays inside the expansion boundary.

Coefficient and vector arguments accept integers and `Fraction` values.
Boolean and approximate entries fall outside that exact interface.
Normalized-incidence frames require nonzero coefficient tuples. The
linear lift/inverse APIs also admit the zero partner; unit incidence adds
the weighted norm equation.

Runtime construction reuses the public base-frame evaluator. Symbolic
replay reuses the existing internal polynomial builder to preserve one
base algebra implementation. The replay pins its source bytes alongside
the public modules and proof notes.

## Verification and remaining proof surfaces

The exact regression derives independent left and right matrices from
`cd_sign` at each tested dimension. It checks the conjugation sign,
ordinary embedding, complete frame Gram recurrence, action-factor
identity, and canonical column regrouping for `32->64->128->256`.
Twenty-four rational cases cover all six nonzero base locus types across
four stages. They verify nullity scaling, inverse round trips, weighted
metrics, and structured operator application against independent basis
multiplication. A closure inclusion check accompanies each stage.

Negative controls reject a repeated-left operator, a missing conjugation
minus, a permutation across different factor blocks, invalid stages,
origin frame construction, oversized expansion, malformed rational
inputs, vectors outside the kernel, and reversed closure maps.
Normal and optimized Python retain the same explicit checks. Serial and
spawned-pool execution produce identical retained JSON.

The [annihilator source ledger](cayley_dickson_annihilator_sources.md)
records the published ordinary embedding theorem in Biss-Dugger-Isaksen,
*Large annihilators in Cayley-Dickson algebras*, Theorem 10.1. The
[existing embedded path](../../gororoba_quantum/rank_path_topology.py)
already uses its ordinary-doubling specialization. The input family has
both scalar and distinguished-unit coefficients zero at every stage.
The present derivation applies the same structural mechanism to the
complete four-coordinate incidence frame. Publication priority remains
unestablished.

The written induction proves a restricted all-dimensional theorem;
exact symbolic replay supplies implementation certificates through the
expansion limit. Rocq formalization is a separate proof surface. The
remaining coefficient directions, Whitney conditions, finite
triangulations, homology, torsion, cup products, and unrestricted pair-space
classification remain outside this construction.
