# Dimension-32 skew-Schur charts and curved rank changes

A local rank model must retain points where the kernel dimension changes.
The [skew-Schur implementation](../../gororoba_quantum/skew_schur_charts.py)
reduces a dimension-32 left-multiplication operator to the kernel size of a
chosen zero-divisor center. The API accepts exact rational points in every
one of the 30 doubly-pure coefficient directions. The written identities
below hold for arbitrary real coefficients on the stated pivot domain.
The [retained replay](../evidence/dimension32_skew_schur/README.md) separates
those identities from finite rational regression evidence.

The construction extends the [local research probe](../evidence/local_schur/README.md)
and complements [constant-rank charts](../../gororoba_quantum/rank_charts.py).
A constant-rank chart requires its Schur complement to vanish. The
skew-Schur chart retains a nonzero reduced matrix and certifies its rank.
The resulting map describes a local incidence space across ranks; a
constant-dimensional vector bundle appears only after restriction to a
suitable constant-rank base.

## Published foundations and claim boundary

[Biss, Christensen, Dugger and Isaksen, Lemma 2.3](0905.2987.md) gives
`L_x^T=L_conj(x)` for the Euclidean inner product in the repository's
Cayley-Dickson convention. A pure element therefore has a skew-symmetric
left-multiplication matrix. [Biss, Dugger and Isaksen](math-0511691.md),
Lemma 9.5, Theorem 9.8, Proposition 9.10, and Theorem 13.2 give double
purity, divisibility of annihilator dimension by four, and the sharp
dimension bound. In dimension 32, a nonzero zero divisor has nullity
4, 8, 12, or 16. These published
results supply the algebraic hypotheses; block elimination supplies the
Schur identities.

[Koebisu's Discussion question 4](2608.08232.md) asks for the geometry of
the dimension-32 rank strata. The determinant factorization describes a
zero set but leaves kernel geometry and attachments open. The
[research synthesis](koebisu_rank_stratum_research.md) maps that question to
reduced equations, smooth subdivisions, overlaps, and normal links.
[Zhilina's Section 6](2608.26893.md) supplies related skew-linear structure
and a second route through complex skew-symmetric matrices. The present
implementation uses the real skew matrix and a fixed center complement.

The implementation contributes a reproducible reduction, exact input
admission, retained certificates, and an explicit nonlinear regression
fixture. Publication priority requires further literature and expert review.
The results classify neither all real rank loci nor the global pair space.

## Center and exact input domain

Write `C_5=span(e_0,e_16)` and use the coordinate domain

```text
D = { x in R^32 : x_0=x_16=0, x != 0 }.
```

The constructor takes a verified left-multiplication rank certificate for
a center `x_*` in `D` with nullity `k` in `{4,8,12,16}`. The rational API
accepts integers and `Fraction` values. The origin, booleans, floating-point
values, incorrect dimensions, right-side certificates, and damaged center
certificates fail admission through explicit exceptions. The constructor's
center restriction leaves invertible points admissible when their pivot
remains invertible.

Let `L_*=L_(x_*)`. Choose the deterministic independent columns of `L_*`
as the columns of `U` and derive the canonical free-coordinate kernel
basis `V` from the verified matrix. A certificate supplied in a different
column order still selects the same canonical chart basis. Put `r=32-k` and `T=[U,V]`. Skew symmetry gives

```text
im L_* = (ker L_*)^perp,
U^T V = 0,
T is invertible.
```

The restriction of `L_*` to its kernel complement is invertible: its
kernel on that complement is zero, and skew symmetry preserves the
complement. Therefore `A_*=U^T L_* U` is invertible. The columns of `U`
and `V` require linear independence rather than Euclidean normalization.
All choices remain fixed as the input point varies.

## All-real congruence and rank identity

For `x` in `D`, define

```text
A=U^T L_x U,  B=U^T L_x V,  D_0=V^T L_x V,
delta=det A,
S=D_0+B^T A^(-1) B,
H=V-U A^(-1) B,
J=[0,I_k] T^(-1).
```

The chart domain is the open set `delta != 0`. Its center belongs to that
set, so the chart describes a neighborhood of the center within `D`.
The letter `D_0` denotes the lower diagonal block and differs from the
coefficient domain `D`.

Set `P=[[I_r,-A^(-1)B],[0,I_k]]`. Direct multiplication gives

```text
T^T L_x T = [[A,B],[-B^T,D_0]],
P^T T^T L_x T P = diag(A,S),
S^T=-S,
rank L_x = r + rank S,
T^T L_x H = [0;S],
J H = I_k.
```

For the lower left block in the congruence, use
`(A^(-1))^T=-A^(-1)`. The upper right block becomes
`A*(-A^(-1)B)+B=0`; the lower right block becomes
`D_0+B^T A^(-1)B`. Both `T` and `P` are invertible, so congruence preserves
rank. The residual identity and invertibility of `T^T` give

```text
ker L_x = { H w : w in ker S }.
```

Conversely, write a full kernel vector as `y=T[u;w]`. The upper block
says `A u+B w=0`, hence `u=-A^(-1)B w`, so `y=H w` and `w=J y`.
The proof covers every real point in the pivot domain, including points
where the reduced kernel is zero. The numerical API evaluates exact
rational instances of the same identities.

A reduced rank certificate combines a nonzero rank-sized minor of `S`
with an independent complete kernel basis. The minor gives a lower bound
and the kernel gives a matching upper bound. The production evaluator
then obtains full rank from `r+rank S`; the replay compares selected
results with the independent full-matrix certificate implementation.

## Metric and unit-partner incidence transport

The identity `J H=I_k` makes `H` injective. Its Gram matrix
`G=H^T H` is therefore positive definite. The maps

```text
(x,w) -> (x,H(x)w),
(x,y) -> (x,J y)
```

give inverse continuous maps between

```text
{ (x,w) : delta(x)!=0, S(x)w=0, w^T G(x)w=1 }
```

and the unit-partner incidence space

```text
{ (x,y) : delta(x)!=0, L_x y=0, y^T y=1 }.
```

Rational dependence of `H` on `x` makes the forward map continuous on the
pivot domain; `J` is a fixed linear map. The formulas remain continuous
across changes of kernel dimension. Restricting `x` to a unit sphere gives
the corresponding local normalized pair space. Invertible points have an
empty unit-partner fiber.

A Euclidean unit sphere in the ambient reduced coordinates is generally
incorrect: the retained metric `G` carries the physical Euclidean norm of
the full partner. The replay checks the norm identity on reduced kernel
vectors and checks the inverse on their full lifts. Such rational tests
avoid requiring a square root in the exact input API; division by the
positive norm supplies the unit-vector statement over the reals.

## Polynomial denominator contract

The adjugate identity `A adj(A)=delta I_r` yields unexpanded polynomial
matrices

```text
Sbar = delta D_0+B^T adj(A) B,
Hbar = T[-adj(A)B;delta I_k].
```

The polynomial identities are

```text
T^T L_x Hbar=[0;Sbar],
J Hbar=delta I_k.
```

On `delta != 0`, the equalities `Sbar=delta S` and `Hbar=delta H`
recover the rational chart. The equations at `delta=0` require separate
analysis; clearing a denominator alone admits spurious boundary points.
For a unit partner expressed as `y=Hbar w/delta`, the metric equation is
`w^T Hbar^T Hbar w=delta^2`, together with `Sbar w=0` and `delta != 0`.
The symbolic-domain API retains these expressions and their inequation
rather than expanding large multivariate determinants.

The rational evaluator also retains the cleared expressions at singular
pivots. The pivot size `r` is even, and every real skew-symmetric matrix
has even rank. A singular `A` therefore has corank at least two, so every
`(r-1)`-minor vanishes and `adj(A)=0`. Consequently both cleared
numerators vanish at a singular pivot. The inequation `delta != 0` remains
essential: those vanishing numerators alone carry no kernel-chart claim.

## Linearized bounds and the same-tangent fixture

At the center, `B=D_0=0`. Differentiation therefore gives

```text
dS_(x_*)[h]=V^T L_h V.
```

The derivative API retains the map on all 30 doubly-pure coordinate
basis vectors and the constraint `<x_*,h>=0` for a fixed-norm base.
The radial direction lies in the derivative kernel. If the derivative
has rank `q`, the unit-base linearized kernel has dimension `29-q`.
Every differentiable fixed-norm curve of constant nullity `k` through
the center has its tangent in the unit-base linearized kernel. The derivative kernel alone does not classify
nearby ranks, establish smoothness, or identify an attachment.

The retained centers give the following exact derivative measurements.
Each row describes its stated point, rather than every point of that
nullity. The fixed-norm column records a linearized bound.

| Center | Nullity | Derivative rank | Fixed-norm linearized dimension |
| --- | ---: | ---: | ---: |
| `e_1+e_10/4+5e_18/8+e_25/8` | 4 | 2 | 27 |
| `e_1+e_10` | 8 | 6 | 23 |
| `e_1+e_18` | 12 | 8 | 21 |
| `e_1+e_10+e_18-e_25` | 16 | 18 | 11 |

The retained symbolic fixture takes

```text
x_*=e_1+e_10,  h=e_3,
x_s(t)=e_1+t e_3+e_10,
x_c(t)=((4-t^2)/(4+t^2)) e_1+(4t/(4+t^2)) e_3+e_10.
```

Both paths have center `x_*` and derivative `h` at zero. The direction
`h` lies outside the four-coordinate support used in the earlier
restricted classification. The center has nullity eight and satisfies
`V^T L_h V=0`. With the deterministic chart basis, the replay proves

```text
det A(x_s(t))=2^32 (t^2+2)^8,
S(x_s(t)) has entries in {0,t^2,-t^2},
det S(x_s(t))=t^16,
rank S''(x_s(0))=8,
det A(x_c(t))=2^56/(t^2+4)^8,
S(x_c(t))=0,
||x_c(t)||^2=2.
```

Every real parameter lies in both pivot domains because the displayed
quadratic denominators and factors are positive. Thus `x_s(t)` has
nullity zero for every nonzero real `t`, while `x_c(t)` has nullity eight
for every real `t`. Normalizing by `sqrt(2+t^2)` and `sqrt(2)` respectively
produces unit-base paths with the same center and first derivative and
with different nearby ranks. The first-order equations cannot distinguish
those paths; the quadratic Schur term supplies the missing information.
The example supplies an exact higher-order test, rather than a proof that
the rank locus is singular.

The fixture also has `H(x_s(t))=H(x_c(t))` and
`G(x_s(t))=G(x_c(t))=((t^2+4)/2) I_8`. The replay verifies both identities.
The identical elimination lift and metric transport the same reduced
coordinate space, while the two residual matrices impose different kernel
membership. The columns of `H` give a complete kernel frame only where
`S=0`; in general, the kernel comes from restricting `H` to `ker S`.
Consequently a lift and its metric alone omit essential incidence data
across a rank change. The retained reduced equation `S(x)w=0` decides which
lifted vectors belong to the annihilator. The deduction concerns these
explicit paths and supplies an implementation test, not a priority claim.

## Remaining geometric obligations

The API certifies each admitted pivot domain. A globally covering atlas
requires a proven center-selection scheme and overlap coverage. On an
overlap, the coordinate transport from chart `a` to chart `b` is
`J_b H_a` restricted to `ker S_a`. If center kernel dimensions differ,
the ambient matrix is rectangular. Only its pointwise kernel restriction
is an isomorphism, so an unrestricted `GL(k)` transition claim is incorrect.

A classification still requires the actual pulled-back rank equations,
real radicals, smooth subdivisions, closure relations, normal links and
approach-dependent kernel limits. Global homology and cohomology require a
certified global attachment model. Rocq formalization requires a separate
kernel-checked development. Exact CPU certificates strengthen that program;
QPU samples measure compiled operators and cannot replace those proofs.
