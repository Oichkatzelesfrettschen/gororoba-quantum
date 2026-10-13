# Schur acceleration certificates and necessary tangent conditions

Second-order Schur equations distinguish a curved rank-preserving path from
a straight path with the same velocity. The
[implementation](../../gororoba_quantum/schur_acceleration.py) certifies
exact rational acceleration systems in the dimension-32 centered charts.
The [independent replay](../evidence/schur_acceleration/README.md) checks
complete affine solution spaces, separating covectors, symbolic paths, and
quadratic coefficients. The proofs below apply to real coefficients;
the executable certificate domain uses exact integers and rational numbers.

## Sources and attribution

[Biss, Christensen, Dugger and Isaksen, Lemma 2.3](0905.2987.md)
identifies the real adjoint of left multiplication with multiplication by
the conjugate. Pure coefficients therefore give real skew-symmetric
matrices. [Biss, Dugger and Isaksen](math-0511691.md), Lemma 9.5,
Theorem 9.8, and Proposition 9.10 supply double purity, fourfold nullity,
and the nonzero annihilator bound. Those results give the dimension-32
nontrivial nullities 4, 8, 12, and 16.

The existing [centered Schur construction](dimension32_skew_schur_charts.md)
supplies the chart used here. The
[principal atlas](principal_skew_atlas.md) supplies a finite cover and
kernel gluing maps. Schur elimination, differentiation, solvability by
left-kernel covectors, rank-nullity, and quadratic polarization are standard
linear algebra and calculus. The note proves the particular consequences
and retains their exact implementation checks; it claims no publication
priority for those mechanisms.

[Zhilina, Section 6, Lemmas 6.6-6.10](2608.26893.md) gives a related
complex skew representation. An explicit intertwiner to that representation
remains a separate obligation. The local necessary conditions below address
part of [Koebisu's Discussion question 4](2608.08232.md); they supply
neither a classification of its rank strata nor their complete topology.

## Centered chart and all-real derivatives

Fix a nonzero doubly-pure real center `x0` with nullity `k`. Write `L_x`
for left multiplication by `x`. Let the columns of `V` form a basis of
`ker L_x0`, and let `U` be a complementary frame chosen so that `[U,V]`
is invertible and `A0=U^T L_x0 U` is invertible. The certified centered
chart provides those properties. Set

```text
A(x)=U^T L_x U,   B(x)=U^T L_x V,   D(x)=V^T L_x V,
S(x)=D(x)+B(x)^T A(x)^(-1) B(x).
```

Every block before inversion is linear in `x`; `B(x0)=D(x0)=0`.
The skew block convention is `[[A,B],[-B^T,D]]`, which fixes the plus
sign in `S`. On the open domain `det A(x)!=0`, block elimination gives
`rank L_x=(32-k)+rank S(x)`. Consequently `S(x)=0` describes exactly
the same-nullity `k` locus in that domain. Nullity at least `k` gives
the same locus there, because the pivot already has rank `32-k`.

For a twice differentiable path through the center, write

```text
x(t)=x0+t h+(t^2/2) a+o(t^2),
Q(h)=B(h)^T A0^(-1) B(h).
```

Continuity and differentiability of the matrix inverse near `A0` give
`A(x(t))^(-1)=A0^(-1)+O(t)`. Since
`B(x(t))=t B(h)+(t^2/2) B(a)+o(t^2)`, multiplication gives

```text
S(x(t))=t D(h)+(t^2/2) D(a)+t^2 Q(h)+o(t^2),
S'(0)=D(h),
S''(0)=D(a)+2 Q(h).
```

Terms involving a derivative of the inverse or `B(a)` enter only at
order three or higher. A constant-norm path also satisfies

```text
<x0,h>=0,              <x0,a>=-||h||^2.
```

Thus a constant-norm same-nullity path necessarily obeys
`D(h)=0`, the first norm equation, `D(a)=-2Q(h)`, and the second norm
equation. The equations hold on the sphere of radius `||x0||`; rational
normalization of the center to radius one is unnecessary.

## Complete acceleration space and radial solvability

Use the 30 doubly-pure coordinates, excluding indices 0 and 16. Let
`Dmap` have one row per strictly upper-triangular entry of `D`, and let
`c` contain the center's 30 coordinates. Skew symmetry makes the upper
triangle a complete set of equations. Define

```text
M = [ Dmap ],         rhs(h) = [ upper_triangle(-2Q(h)) ],
    [ c^T  ]                  [         -||h||^2        ]
```

The direction is first-order admissible precisely when `M h=0`, using
its 30-coordinate column. A compatible acceleration solves `M a=rhs`.
For a particular solution `p` and a full column basis `K` of `ker M`,
the complete set of accelerations is `p+K z`, for arbitrary real `z`.
Independence and completeness follow from `M K=0`, column rank of `K`
equal to `30-rank M`, and a nonzero rank-sized minor of `M`. These
finite exact identities certify the entire affine real solution space.

If a column `ell` satisfies `ell^T M=0` and `ell^T rhs!=0`, then
`M a=rhs` has no solution. Conversely, the annihilator of `ker M^T`
is `im M`, so an inconsistent system admits such a separating covector.
Exact rational matrices admit rational particular solutions, kernel bases,
and separating covectors whenever the corresponding real objects exist.

The norm equation adds no solvability obstruction. Linearity and
`D(x0)=0` give `Dmap c=0`, while `c^T c=||x0||^2>0`. For any solution
`a0` of the Schur equation, the correction

```text
a=a0+alpha c,
alpha=(-||h||^2-c^T a0)/(c^T c)
```

preserves that equation and enforces the norm equation. The norm row is
independent of the rows of `Dmap`: any dependence, evaluated on `c`,
would imply `c^T c=0`. Hence `rank M=rank Dmap+1`. Evaluating any
left-kernel relation on `c` also proves that every separator's coefficient
on the norm row is zero.

The certificate retains the system, right-hand side, direct first-order
residual, and one of three explicit states: first-order inadmissibility,
second-order obstruction, or second-order compatibility. An affine
certificate retains a Schur particular solution, radial correction,
corrected particular solution, complete homogeneous kernel, and rank
minor. An obstruction certificate retains a separating covector and its
nonzero pairing. The verifier reconstructs the equations from the chart
and direction before checking the retained witnesses.

## Curvature fixture and normalization boundary

At `x0=e1+e10`, the nullity is eight and `h=e3` satisfies both first-order
conditions. The exact rational path

```text
x_c(t)=((4-t^2)/(4+t^2)) e1+(4t/(4+t^2)) e3+e10
```

has norm squared two, velocity `e3`, and acceleration `-e1`. Symbolic
Schur reduction gives `S(x_c(t))=0` in the centered pivot neighborhood.
Its acceleration satisfies `D(-e1)+2Q(e3)=0` and `<x0,-e1>=-1`.

The straight path `x_s(t)=e1+t e3+e10` has the same initial velocity
but has `S''(0)=2Q(e3)` of rank eight and `det S(x_s(t))=t^16`.
Radial normalization of that path is
`sqrt(2/(2+t^2)) x_s(t)`. Its acceleration is `-x0/2`, which satisfies
the norm equation while leaving the Schur obstruction unchanged because
`D(x0)=0`. Norm correction therefore leaves genuine transverse curvature
requirements intact. The compatible acceleration space has dimension 23.

## Exact incompatible direction

At `x0=e1+e18`, the nullity is twelve and `h=e11` satisfies both
first-order conditions. The derivative map has rank eight and the
constant-norm linearized kernel has dimension 21. In the retained
centered basis, two zero-based residual rows give

```text
D(a)_(0,1)=2(a1-a18),       (-2Q(e11))_(0,1)= 2,
D(a)_(4,5)=2(a1-a18),       (-2Q(e11))_(4,5)=-2.
```

Their difference forces incompatible values of `a1-a18`. The covector
with coefficient `-1` at row `(0,1)`, `+1` at row `(4,5)`, and zero
elsewhere satisfies `ell^T M=0` and `ell^T rhs=-4`. In particular,
`ell Q(e11)=2`. A complete second-order compatible jet with that
velocity does not exist.

## Necessary tangent outer bound without acceleration regularity

Let `X` be the same-nullity `k` locus intersected with the center's
constant-norm sphere and fixed pivot domain. A Bouligand tangent
direction at `x0` is a limit `h_j->h` with positive `t_j->0` and
`x0+t_j h_j` in `X`. The exact centered identity gives

```text
0=t_j D(h_j)+t_j^2 B(h_j)^T A(x0+t_j h_j)^(-1) B(h_j).
```

The inverse remains bounded and converges to `A0^(-1)`, because the
center pivot is invertible. Division by `t_j` gives `D(h)=0`. The
constant-norm identity gives `<x0,h>=0` in the limit. For any linear
functional `lambda` that annihilates every `D(v)`, projection kills
the first term exactly. Division by `t_j^2` and continuity then give
`lambda Q(h)=0`.

Consequently the real quadratic conditions `lambda Q(h)=0`, together
with both first-order conditions, contain the Bouligand tangent cone of
`X`. The `e11` witness excludes that direction even as a limiting
tangent and as the velocity of a same-nullity `C1` curve. The conclusion
concerns the named nullity locus; the union of all zero-divisor ranks
has different local equations. The proof establishes a necessary outer
bound, not equality with the tangent cone.

## Coefficient-complete quadratic checks and remaining geometry

Choose a full basis `K` of `ker M` and a full basis of `ker Dmap^T`.
Every projected expression `lambda Q(K z)` is a homogeneous quadratic
polynomial in real coordinates `z`. Values on every basis vector and
every pair sum determine all coefficients:

```text
diagonal coefficient i = q(e_i),
cross coefficient ij = q(e_i+e_j)-q(e_i)-q(e_j).
```

The replay constructs the full projected coefficient matrix. At `e1+e10`,
all coefficients vanish on the 23-dimensional linearized sphere kernel;
276 basis and pair-sum evaluations suffice. At `e1+e10+e18-e25`, they
vanish on its 11-dimensional kernel; 66 evaluations suffice. These
coefficient identities prove second-order solvability for every real
first-order direction at those centers. They go beyond sampled directions
while supplying no general curve-existence theorem.

A compatible second-order jet satisfies the equations only through order
two. Higher-order obstructions, real radicals, sufficient curve criteria,
smooth subdivisions, changing-kernel attachments, and global topological
invariants remain separate obligations. The explicit rational curvature
path proves curve existence for its own direction. The local calculations
require exact CPU algebra; QPU measurements supply neither polynomial
identity proofs nor the missing geometric classification.
