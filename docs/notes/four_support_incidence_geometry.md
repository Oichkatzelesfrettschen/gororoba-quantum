# Smooth strata and partner incidence on the four-coordinate support

The [geometry module](../../gororoba_quantum/four_support_geometry.py)
constructs a finite smooth decomposition and an explicit global incidence
model for the coefficient support `{1,10,18,25}`. The normalized base has
96 connected smooth strata and 704 closure incidences, including 96
reflexive incidences and 608 strict boundary incidences. A global
20-column frame identifies the complete restricted unit-partner incidence
with five coordinate blocks subject to scalar factor equations.

The construction uses the
[all-real rank and kernel certificate](four_support_rank_loci.md).
Every statement concerns `x=a e1+b e10+c e18+d e25`; the base sphere is
`N=a^2+b^2+c^2+d^2=1`. Positive scaling extends the kernel descriptions
to nonzero coefficients. Antipodal inputs remain distinct points.
The [source-bound replay](../evidence/four_support_geometry/README.md)
checks the finite combinatorics and polynomial identities. The analytic
arguments below establish smoothness, connectedness, closure sufficiency,
and the global homeomorphism beyond the finite rational checks.

## Feasible sign labels and smooth connected pieces

Use the invertible linear coordinates from the rank certificate:

```text
p=a-b-c-d,  q=a-b+c+d,
r=a+b-c+d,  s=a+b+c-d,
Q=pq+rs=2 Delta,  Delta=a^2+b^2-c^2-d^2.
```

The transform satisfies `T T^T=4I`, so the unit base corresponds to
`p^2+q^2+r^2+s^2=4`. For a nonzero coordinate sign vector
`sigma in {-1,0,+1}^4` and cone sign `epsilon in {-1,0,+1}`, define

```text
S(sigma,epsilon) = {ell on the radius-two sphere:
    sign(ell_i)=sigma_i, sign(Q)=epsilon}.
```

Set `A=sigma_p sigma_q` and `B=sigma_r sigma_s`. Feasibility follows
directly from the signs of the two products:

- If `A=0`, then `epsilon=B`.
- If `A != 0` and either `B=0` or `A=B`, then `epsilon=A`.
- If `A=-B != 0`, all three cone signs occur.

The last case requires full coordinate support. The generator enumerates
these rules and constructs an exact rational ray witness for each label.
Radial normalization supplies a point on the sphere while preserving the
label. The origin belongs to a different rank case and lies outside the
normalized geometry.

Fix a sign vector with `m` active coordinates. On the corresponding open
orthant face write `u_i=|ell_i|>0` and

```text
y_i=log(u_i)-(1/m) sum_j log(u_j),   sum_i y_i=0.
ell_i=2 sigma_i exp(y_i)/sqrt(sum_j exp(2y_j)).
```

The displayed inverse uses active coordinates only. These maps give a
smooth diffeomorphism between the orthant face and `R^(m-1)`.
If `A=-B != 0`, then

```text
sign(Q)=A*sign(y_p+y_q-y_r-y_s).
```

The zero-cone piece becomes a linear hyperplane, and either nonzero-cone
piece becomes an open half-space. Each is diffeomorphic to a Euclidean
space. Every other feasible label occupies the entire orthant face.
Each feasible stratum is therefore connected and smooth, with dimension
`m-1`, except for full support on the cone, whose dimension is two.
The strata are semialgebraic by their original polynomial definitions;
the logarithmic proof establishes their smooth open-cell descriptions.

The following table counts connected components of each individual rank
locus on the support sphere:

| Kernel dimension | Stratum dimension | Components | Shape |
| --- | --- | --- | --- |
| 0 | 3 | 24 | `R^3` |
| 4 | 2 | 40 | `R^2` |
| 8 | 1 | 8 | `R` |
| 12 | 1 | 16 | `R` |
| 16 | 0 | 8 | point |

The 40 nullity-four components comprise 32 coordinate-face pieces and
8 full-support cone pieces. The closure criterion below proves that every
proper boundary raises nullity. Consequently each connected piece is
closed relative to its rank locus. The finite partition then also makes
each piece relatively open, proving the stated component counts.

## Exact closures and explicit approach rays

A feasible target `S(tau,eta)` lies in the closure of a feasible source
`S(sigma,epsilon)` exactly when

```text
tau_i is either 0 or sigma_i for every coordinate,
eta is either 0 or epsilon.
```

In particular, a source with `epsilon=0` only reaches cone targets.
Continuity of coordinates and `Q` proves necessity. The following
constructions prove sufficiency for every point of an allowed target,
rather than only for its rational witness.

If the source's product signs fail to oppose, replace each source-active
zero target magnitude by a positive parameter. The resulting sign pattern
has the required cone sign by the feasibility rules. If the source has
opposing product signs and the target has nonzero `Q`, the same construction
preserves the sign for a sufficiently small parameter.

The executable `approach_ray()` chooses a valid parameter for every
positive rational input `t`. Put `h=t/(1+t)`. For an opposing-product
source and a target with nonzero `Q_0`, use

```text
h = [t/(1+t)] * |Q_0|/[2*(sum_i |ell_i|+2+|Q_0|)].
```

After filling missing coordinates with magnitude `h`, the change in `Q`
is bounded by `h*sum_i |ell_i|+2h^2`. Since `h<1` and
`h<|Q_0|/[2*(sum_i |ell_i|+2)]`, the change is smaller than `|Q_0|/2`.
The cone sign therefore remains fixed for every `t>0`, and the added
coordinates tend to zero as `t` tends to zero.

The remaining case has a full-support source with opposing product signs
and a target on `Q=0`. Arrange the nonnegative target magnitudes as

```text
M = [[|p|,|r|],[|s|,|q|]].
```

The matrix is nonzero, nonnegative, and has determinant zero. Choose any
positive entry `M_ij`. The factorization

```text
u=M[:,j],  v=M[i,:]/M_ij,  M=u*v
```

has nonnegative factors. The replay verifies the determinant identity
that justifies this factorization on each of the four pivot domains.
For `t>0`, the positive matrix

```text
M_t=(u+t*(1,1)^T)*(v+t*(1,1))
```

has determinant zero and converges to `M`. It approaches a cone source.
Adding `t E_11` gives determinant `t*(M_t)_22>0`; adding `t E_12`
gives determinant `-t*(M_t)_21<0`. Choose the determinant sign
`A*epsilon`, restore the source coordinate signs, and normalize radially.
The resulting point stays in the requested source and approaches the
specified target.

The finite replay checks all 704 allowed pairs, their coordinate
inclusions, and three rational approach parameters per pair. The proof
above supplies the all-real closure statement. The relation is reflexive,
antisymmetric, and transitive. Every proper boundary has smaller dimension
and greater nullity, so the decomposition satisfies the frontier condition.
The construction establishes a finite smooth semialgebraic stratification
in the frontier-condition sense. Whitney conditions require additional
proofs.

A coordinate-face nullity-four closure is a spherical triangle. A cone
nullity-four closure has a square model under positive `L1` normalization:

```text
M(u,v)=[[uv,u(1-v)],[(1-u)v,(1-u)(1-v)]],  0<=u,v<=1.
```

Its entries sum to one and its determinant is zero. The first row and
column sums recover `u,v`. Every nonnegative rank-one matrix with entry
sum one has this form, so radial normalization gives a closed-disk model
on the support sphere. Its four edges have nullity 12 and its four vertices
have nullity 16. These bounded descriptions avoid assuming a regular
closed-three-cell model for every invertible stratum.

## A global frame for the restricted incidence

The rank certificate supplies four cone columns `v0,...,v3` and constant
four-planes associated with the linear factors `p,q,r,s`. Lift all 20
columns to the original 32 partner coordinates in the fixed order

```text
G(x)=[V(x),W_p,W_q,W_r,W_s].
```

The four cone columns retain their polynomial scaling. The 16 constant
columns use the normalization `K/2` or `DK/2` from the rank certificate.
Put `A_0=a^2+b^2`, `B_0=c^2+d^2`. The replay verifies

```text
D(x)=G(x)^T G(x)
    =diag(N^2+4A_0 B_0,N,N,N^2+4A_0 B_0,1,...,1),
L_x G(x)=R(x) diag(Delta I4,p I4,q I4,r I4,s I4),
R(x)^T R(x)=diag(N,1,1,N,1,...,1).
```

Both Gram diagonals are strictly positive at every nonzero real `x`.
Hence the 20 columns of `G` and of `R` are independent throughout the
nonzero coefficient domain. The factor identity proves that the kernel
within the image of `G` consists exactly of the blocks whose scalar
factors vanish. The all-real rank formula counts precisely those columns,
so their span equals the entire kernel of `L_x`.

Use positive square roots to define `F(x)=G(x)D(x)^(-1/2)`. The frame is
continuous on the whole support sphere and satisfies `F^T F=I20`.
Let `z=(z_cone,z_p,z_q,z_r,z_s)` with each block in `R^4`. Define

```text
Y = {(x,z) in S^3 x S^19:
       Delta(x) z_cone=0,
       p(x) z_p=q(x) z_q=r(x) z_r=s(x) z_s=0}.
```

Let `Z` denote the actual unit-pair incidence with `x` on the fixed
coefficient sphere, `y in S^31`, and `xy=0`. Then

```text
Phi:Y->Z,  Phi(x,z)=(x,F(x)z),
Psi:Z->Y,  Psi(x,y)=(x,F(x)^T y)
```

are inverse continuous maps. The factor equations and `F^T F=I20`
prove that `Phi` preserves the kernel condition and partner norm.
Kernel completeness gives `F F^T y=y` for every `(x,y)` in `Z`; the
identity is asserted on the kernel, rather than on all of `R^32`.
The identity also proves that `Psi` preserves unit norm and that both
compositions equal the identity. The formulas therefore give a
homeomorphism of the entire restricted normalized pair space.
Invertible inputs have empty unit-partner fibers because every block of
`z` is forced to zero while `z` must have norm one.

The executable rational API uses the equivalent weighted model

```text
Delta*w_cone=0,  ell_i*w_i=0,  w^T D(x) w=1,
y=G(x)w,  w=D(x)^(-1) G(x)^T y.
```

`incidence_frame()` evaluates `G,D` and the factors.
`lift_kernel_coordinates()` checks the factor equations and returns `Gw`.
`kernel_coordinates()` verifies actual kernel membership and returns the
weighted inverse. Both linear APIs also accept zero vectors; unit incidence
adds the displayed norm equation. Exact rational tests therefore establish
round trips and metric identities without approximating square roots.
The global real homeomorphism follows from the positive normalization above.

## Kernel specialization and compatibility

The frame columns available on a stratum are determined by its zero
factors. Along every closure incidence, source zero factors remain zero
at the target. All source frame columns extend continuously and become
literal columns of the target frame. In the global block order, the
specialization map inserts zero coordinates into newly available slots.
`coordinate_inclusion()` constructs and checks that map; its transpose
product equals the identity on source coordinates.

The normalized columns preserve the partner sphere metric under these
inclusions. Cone columns in sectors 0 and 3 depend quadratically on `x`,
whereas sectors 1 and 2 depend linearly on `x`. Evaluating the polynomial
frame at signed endpoints preserves these differences. A basis that
forgets the endpoint signs would change the explicit gluing maps.

The same global frame underlies all local trivializations and the global
incidence model. Consequently the construction carries both rank-locus
closure data and actual partner-coordinate gluing, beyond a list of fiber
dimensions.

## Evidence boundary and research attribution

The replay retains every stratum, exact witnesses, all closure targets,
component counts, constructive polynomial identities, frame identities,
and negative controls. Fifteen additional approach checks cover target
magnitudes and parameters from `10^-40` through `10^40`. An unscaled
perturbation fails an extreme target, testing the necessity of the
scale-dependent step bound. It rejects impossible sign labels, reversed
incidences, origin use, duplicate columns, changed frame signs, invalid
rational domains, and vectors outside the kernel. Independent rank-module
evaluations verify the frame span at every retained stratum witness.
Normal and optimized Python retain identical checks and deterministic
output. The result is an executable symbolic certificate with a written
analytic proof; a Rocq kernel certificate is a separate evidence surface.

The [rank source ledger](cayley_dickson_rank_topology_sources.md) and
[Koebisu research synthesis](koebisu_rank_stratum_research.md) distinguish
known annihilator and spectral results from the remaining global geometry.
This construction derives a bounded extension using elementary sign
geometry, logarithmic coordinates, nonnegative rank-one factorization,
and the repository's exact sector calculation. The derivation carries
no publication-priority claim.

The model determines the restricted incidence as an explicit compact
semialgebraic space. A finite triangulation, integral homology, torsion,
cohomology products, and a homotopy classification still require separate
construction and computation. The closure poset alone supplies insufficient
data for those claims. The other dimension-32 coefficient directions and
unrestricted higher-dimensional pair spaces remain outside the theorem.

Ordinary doubling supplies a structural next step for the same coefficient
family. For pure `x`, the convention gives
`L_(x,0)=diag(L_x,-C L_x C)`, so the kernel dimension doubles.
The [embedded path implementation](../../gororoba_quantum/rank_path_topology.py)
already uses that mechanism. Extending the five-block frame by the
corresponding block recurrence preserves the fixed coefficient support.
The all-stage proof and executable recurrence remain a separate follow-on.
The present geometry replay covers dimension 32.
