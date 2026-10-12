# Limiting annihilators along polynomial paths

An endpoint kernel contains vectors that a nearby rank locus never reaches.
The rational orthogonal projector separates those vectors from the actual
limiting partner fiber. The [implementation](../../gororoba_quantum/kernel_limits.py)
retains rank witnesses, a removable projector limit, a complete persistent
frame, an exact punctured-neighborhood radius, and coordinates for its
inclusion into the endpoint kernel. The [replay](../evidence/kernel_limits/README.md)
binds the calculation to its source bytes and checks damaged certificates.

## Generic rank and the persistent subspace

Let `M(t)` be an `m x n` polynomial matrix with real coefficients. Its
rank over `R(t)` is `r`, and `k=n-r`. A nonzero `r x r` minor and an
independent `n x k` rational kernel frame `K(t)` prove both rank bounds.
Outside the finite zero set of the minor and the frame denominators,
`M(t)` has rank `r` and `K(t)` spans its complete real kernel. For `k=0`,
retain the empty frame and the zero projector.

For `k>0`, the Gram matrix is positive definite at every admitted real
parameter, so its rational determinant is a nonzero function. Define

```text
P(t)=K(t) (K(t)^T K(t))^(-1) K(t)^T.
P(t)^T=P(t), P(t)^2=P(t), M(t)P(t)=0, tr P(t)=k.
```

Each entry belongs to `R(t)`. For real parameters in the admitted domain,
`P(t)` is the Euclidean orthogonal projection, so its operator norm is at
most one. A rational entry with a genuine pole at a real endpoint would
be unbounded in every sufficiently small punctured interval. Boundedness
therefore makes every real-endpoint pole removable. Cancellation and
substitution give a unique two-sided limit `P0` at any real endpoint `t0`.
The identities extend by continuity:

```text
P0^T=P0, P0^2=P0, tr P0=k, M(t0)P0=0.
```

A symmetric idempotent has eigenvalues zero and one; its trace is its
rank. Hence `range(P0)` has dimension `k` and lies in `ker M(t0)`, whose
dimension may be larger. The conclusion covers every real coefficient
polynomial matrix of every finite size. The executable API certifies
`Q[t]` matrices at rational endpoints with exact arithmetic. Its exact
input domain differs from the unrestricted written real-coefficient
statement.

## Complete local chart and an explicit radius

Choose `k` independent columns `F0` of `P0`, and set

```text
F(t)=P(t)F0, G(t)=F(t)^T F(t).
```

The endpoint Gram determinant is positive. The certificate includes the
numerator of `det G(t)` among its exceptional factors, along with the
rank-minor numerator and all frame/projector denominators. Let the
square-free exceptional polynomial be `E(t)`. After translating the
endpoint and stripping its zero factor, write

```text
E(t0+s)=s^j (q0+q1 s+...+qd s^d), q0!=0.
R=sum_(i>=1) |qi|.
epsilon=min(1,|q0|/(2R)) if R>0; epsilon=1 otherwise.
```

For `0<|s|<=epsilon`, the remainder has absolute value at most `|q0|/2`.
Thus `E(t0+s)!=0`. The radius certifies the generic rank, rational
projector, and independent persistent frame throughout both punctured
sides. At the endpoint, `F(t0)=F0` stays independent. Positive
`G(t)` supplies a weighted sphere chart, with exact linear inverse
`G(t)^(-1) F(t)^T` on its image.

Let `E0` be a complete endpoint kernel frame. Its free-coordinate rows
are an identity matrix. Reading those rows from `F0` gives the attachment
matrix `A`, and the verifier checks

```text
E0 A=F0,
A^T (E0^T E0) A=F0^T F0.
```

The second identity follows from the first; it records the metric that
turns coordinate inclusion into the actual unit-partner map. An
arbitrary endpoint vector outside `range(P0)` fails the extension API's
membership test.

## Actual incidence closure and attachment

Consider the parameterized incidence
`I={(t,y):M(t)y=0, ||y||=1}` on the certified punctured interval. If
`(t_i,y_i)->(t0,y0)`, then `P(t_i)y_i=y_i`, and continuity gives
`P0 y0=y0`. Conversely, for any unit `y0` in `range(P0)`, the curve

```text
y(t)=P(t)y0 / ||P(t)y0||
```

is defined near `t0`, belongs to the unit kernel, and converges to `y0`.
Its denominator tends to one. Therefore the closure fiber is exactly
`S(range(P0))`, on each side separately. The larger sphere
`S(ker M(t0))` belongs to the endpoint incidence; its extra vectors are
separate from the approaching fiber.

The persistent frame supplies a concrete local model: two punctured
interval products with `S^(k-1)` attach to the endpoint `S^(l-1)` through
the inclusion represented by `A`, where `l=dim ker M(t0)`. A continuous
sphere chart is `z -> F(t)z/||F(t)z||`; its inverse normalizes
`G(t)^(-1)F(t)^T y`. This description uses the parameterized pullback.
A base-path image requires its own local injectivity statement. For the
same-derivative witnesses below, the nonzero derivative supplies local
injectivity after restricting the interval.

For a Cayley-Dickson coefficient path `x(t)`, the operator is `L_x(t)`.
Radial normalization of a nonzero multiplier preserves its kernel and
all projector data. Normalizing the multiplier requires `x(t0)!=0` and
a neighborhood in which its norm stays positive. The retained examples
satisfy that condition. A zero endpoint remains a valid operator limit,
but falls outside normalized base incidence.

## Same derivative and different limiting fibers

At `x0=e1+e18`, the complete endpoint annihilator has dimension twelve.
The exact four-support paths in the replay share derivative `e10-e25`
and generic nullity four. Their limiting kernels are pairwise orthogonal
four-planes whose direct sum is the endpoint kernel. The four-support
rank and frame theorem already implies those inclusions; the projector
calculation reconstructs them independently from complete multiplication
matrices.

The replay also retains paths outside that support:

```text
x_A(u)=x0+u(e3+e27), x_B(u)=x0+u(e4+e11),
x_C(u)=x0+u(e8+e27), x_D(u)=x0+u(e11+e24).
```

Their generic nullity is eight. Nonzero rank-sized minors and complete
kernel frames certify the recorded domains. Every pair of limiting
planes intersects in a four-plane. The projector trace for the first
pair is `tr(P_A P_B)=9/2`, which also records nontrivial relative angles.
The individual certificate's exceptional polynomial controls every
claimed real parameter, including failures of a chosen pivot that need
not indicate a rank change.

For a common nonzero derivative, replace `u` by `t^2` and apply a
rational quaternion automorphism on every quaternion block. Write

```text
c=(1-t^2)/(1+t^2), s=2t/(1+t^2),
B(t)=[[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]],
T(t)=diag(B(t),...,B(t)).
```

All sixteen quaternion basis products, orthogonality, unit preservation,
and commutation with conjugation hold exactly. Componentwise doubling
preserves multiplicativity because the Cayley-Dickson product uses only
multiplication, addition, and conjugation. Induction makes `T(t)` an
orthogonal automorphism at every stage. In dimension 32,
`T'(0)x0=2(e2-e17)`. Multiplication of `T(t)x_i(t^2)` by `1+t^2` clears
the denominator, preserves the kernel, and leaves the derivative unchanged.
All four polynomial numerators have center `x0` and that same nonzero
derivative. Their kernel projectors transform by `T P_i T^T`, so their
limiting planes retain the pairwise distinctions. A common base tangent
therefore fails to determine the actual partner attachment.

## Complete real rank loci on an affine three-coefficient slice

The new slice leaves the earlier four-coordinate support:

```text
x(A,B,C)=e1+e18+A e3+B e8+C e27,
Delta=A^2+B^2-C^2, N=2+A^2+B^2+C^2>0.
```

The [cone implementation](../../gororoba_quantum/circle_kernel_attachments.py)
partitions all 32 input and output coordinates into four eight-dimensional
XOR blocks. The subgroup is `{0,2,9,11,17,19,24,26}`, with representatives
`0,1,4,5`. The two internal block determinants are `-Delta^2 N^2`;
the two external determinants are `Delta^4`. Thus every off-cone point
has rank 32.

Every nonzero real cone point belongs to one of the two charts

```text
(A,B,C)=(u(1-v^2),2uv,u(1+v^2)),
(A,B,C)=(u(w^2-1),2uw,u(1+w^2)), u!=0.
```

Indeed, `C!=0` on the punctured cone. If `C+A!=0`, take
`u=(C+A)/2`, `v=B/(C+A)`; otherwise `C-A!=0` gives the second chart.
The cone equation verifies the inverse formulas. The second chart
includes the missing first-chart pole. These formulas supply arbitrary
real coverage rather than a finite rational sample.

For each block `M`, consider `det(z I-M^T M)`. Both charts give zero
coefficients of `z^0` and `z^1`, and the coefficient of `z^2` is

```text
internal: 256 [1+u^2(1+v^2)^2]^6,
external: 4096 u^8(1+v^2)^8,
```

with `w` in place of `v` in the second chart. Gram eigenvalues are
nonnegative. The elementary symmetric coefficient for seven eigenvalues
vanishes, while that for six is strictly positive. Hence each block has
rank exactly six at every punctured cone point. At the vertex, the
internal ranks are six and the external ranks are four. Consequently

```text
rank L_x=32 when Delta!=0,
rank L_x=24 when Delta=0 and (A,B,C)!=0,
rank L_x=20 when (A,B,C)=0.
```

The punctured cone has two smooth components, `C>0` and `C<0`, each
parametrized by a circle and a positive amplitude. Their closures meet
at the vertex. The coefficient multiplier always stays nonzero because
its `e1` and `e18` coefficients equal one. Radial normalization embeds
this affine slice into the constant-norm sphere: its inverse recovers
`A,B,C` from the corresponding coefficient ratios to `x1>0`.

## Complete kernel bundles and their transition maps

The local positions `(0,1,3,4,5,7)` select a six-dimensional pivot in
each internal block. Its determinant in both circle charts is
`-4[1+u^2(1+v^2)^2]^2`, which never vanishes on the real domain.
The complementary positions `(2,6)` supply a complete two-column kernel
frame by elimination. Its free rows form `I2`. The internal frames
therefore have identity transition maps between the charts: the same
free-coordinate normalization identifies the unique kernel vector.
The internal bundle has a global rational frame of width four, denoted
`K`. At amplitude `tau=C=0`, this frame has the angle-independent limit
`K_C`, spanning a fixed four-plane `C4`.

The external frames combine into `W(v)=W0+v W_infinity`, with exact
identities

```text
W0^T W0=W_infinity^T W_infinity=4 I4,
W0^T W_infinity=0, K_C^T W0=K_C^T W_infinity=0.
```

Each external two-column block has Gram `4(1+v^2) I2` and satisfies the
full polynomial kernel identity. These four external columns are
complete because both external blocks have rank six. In the second
chart, `W_second(w)=w W0+W_infinity`; on `v=1/w`, the raw-coordinate
transition is `xi_second=xi_first/w`. Normalizing the frames gives
transition `sign(w) I4`. This describes four copies of the tautological
line over `RP1`.

Four copies admit a global trivialization. Let `J` represent quaternion
left multiplication by `i` on `R4`, so `J^T=-J` and `J^2=-I`. Set
`a=A/C`, `b=B/C`; on the punctured cone, `a^2+b^2=1`. The frame

```text
E(a,b)=[W0((1+a)I+bJ)+W_infinity(bI+(1-a)J)]/4
```

has Gram `I4` and spans the external kernel. For a proof, write
`a=cos(2theta)`, `b=sin(2theta)`. Then

```text
E=(W0 cos(theta)+W_infinity sin(theta))
   (cos(theta)I+sin(theta)J)/2.
```

Both factors change sign under `theta -> theta+pi`, so their product
descends to the full circle. Polynomial Gram and kernel identities
verify the formula without selecting a half-angle. The coefficient
ratios in the displayed formula are globally defined because `C!=0`.
Thus `H=[K,E]` is a global complete rank-eight frame on each punctured
cone component. Its Gram metric is positive definite, and
`(H^T H)^(-1)H^T` supplies its exact inverse on the kernel. The bundle
is trivial even though its endpoint attachment depends on the angle.

## Complete cone-approach attachment image

The limiting projector in the first chart is

```text
P(v)=P_C + W(v)W(v)^T/[4(1+v^2)],
```

where `P_C` is the orthogonal projector onto `C4`. The reciprocal chart
provides the value at infinity. It verifies the same operator there;
positive denominators cover every real parameter. Distinct projective
parameters have limiting-plane intersection exactly `C4`: equality
`W0 alpha+W_infinity v alpha=W0 beta+W_infinity w beta` forces
`alpha=beta` and `(v-w)alpha=0` by orthogonality. The infinity case follows
from the same direct-sum coordinates. Their projector traces are

```text
tr(P(v)P(w))=4+4(1+vw)^2/[(1+v^2)(1+w^2)].
```

The complete endpoint kernel decomposes as the orthogonal sum
`C4 + W0 R4 + W_infinity R4`, of dimension twelve. In orthonormal
coordinates `(c,alpha,beta)` on this sum, the union of limiting unit
partners is exactly

```text
M={||c||^2+||alpha||^2+||beta||^2=1,
   alpha_i beta_j-alpha_j beta_i=0 for every i<j}.
```

The six minors state that the two vectors are proportional. Every
nonzero proportional pair selects a line in `R2`, hence a projective
circle direction; pure `C4` vectors belong to every limiting plane.
This proves both set inclusions.

Completeness also covers cone approaches with changing angle. On either
compact circle chart, the internal projector is continuous jointly in
amplitude and angle at amplitude zero, since its fixed pivot stays
invertible there. Compactness supplies uniform endpoint convergence.
Every sequence of cone directions has a convergent subsequence in the
projective circle. Its converging unit partners land in the corresponding
limiting plane. Conversely, the projector extension constructs a kernel
curve for every vector in every limiting plane. Thus `M` is the complete
attachment image for all approaches inside the named cone slice.

Let `X` be the unit rank-one locus of `(alpha,beta)` in `R4+R4`.
Factorization gives
`X=(S1 x S3)/((z,q)~(-z,-q))`. Regard `S1` as complex unit quaternions.
The map

```text
[z,q] -> (z^2,zq)
```

is well-defined, continuous and bijective onto `S1 x S3`. Either choice
of square root supplies the inverse class; the two choices identify
under the diagonal involution. Compactness and the Hausdorff target
make this a homeomorphism. Orthogonal norm decomposition then gives

```text
M is homeomorphic to S3 * (S1 x S3).
```

Join coordinates supply the forward map and inverse, with the usual
endpoint identifications when either summand has zero length. This
statement identifies the space itself, rather than only its Betti table.

The product of the standard sphere cell structures has cells in degrees
`0,1,3,4` and zero integral differentials. Joining with `S3` gives four
unreduced suspensions. For the connected product, reduced homology
shifts by four: Mayer-Vietoris for the two contractible suspension cones
proves each shift. Therefore `H0,H5,H7,H8` are `Z` and every other
positive integral group vanishes. The groups are torsion-free.
The attachment image has dimension eight; the smallest possible
positive-degree cup product has degree ten, so every such product
vanishes. The executable chain descriptor derives those degrees from
the product cells and the suspension shift. A Rocq proof of the
geometric identification remains deferred.

## Actual global pair incidence of the slice

The attachment image differs from the parameterized unit-kernel sphere
bundle `S1 x S7`. Its evaluation map collapses the circle over pure `C4`
unit vectors. The exact frame retains that collapse:

```text
f(angle,z)=H(0,angle)z/||H(0,angle)z||, z in S7.
```

The full unit-partner incidence over the affine slice has two mapping
cylinders of `f`, one for each sign of `tau=C`, with their common target
the complete vertex sphere `S11`. Away from the vertex, the map is

```text
(tau,angle,z) -> (x(tau,angle), H(tau,angle)z/||H(tau,angle)z||).
```

The global frame and its weighted inverse make this map bijective on
each punctured component. At the vertex it has exactly the stated
identifications. On every bounded amplitude band, the parameter domain
and the vertex sphere are compact; the continuous bijection from their
adjunction quotient to the actual Hausdorff incidence is a homeomorphism.
Local amplitude bounds give the same conclusion for the entire,
possibly unbounded affine slice. Radial normalization of the first
operand preserves this model through its coefficient-ratio inverse.

The homotopy `tau -> (1-s)tau`, holding `angle,z` fixed in the cylinders,
is a strong deformation retraction onto `S11`; every vertex partner
stays fixed. The endpoint frame limit is uniform over the compact circle
and unit-coordinate sphere, which proves continuity where the cylinders
meet their target, including the collapsed-circle subset. Consequently
this restricted total incidence has the homotopy type of `S11`, integral
homology `Z` in degrees zero and eleven, zero torsion, and zero
positive-degree cup products. The attachment image's degrees five,
seven and eight describe a different space and do not transfer to the
total incidence.

## All-stage transport and remaining classification

For a pure multiplier `x` in `A_n`, conjugation `C_n` gives
`R_x=-C_n L_x C_n`. Ordinary doubling satisfies

```text
L_(x,0)=diag(L_x,R_x),
P_(x,0)=diag(P_x,C_n P_x C_n).
```

The second formula is the unique orthogonal kernel projector of the first
operator. It holds along every admitted pure coefficient path, so taking
limits commutes with ordinary doubling. Both generic and endpoint kernel
dimensions double, and the attachment matrix doubles with the corresponding
conjugated frames. Induction supplies this transport at every higher
stage. The published ordinary embedding theorem has its own doubly-pure
hypotheses; see [Biss-Dugger-Isaksen, Theorem 10.1](math-0511691.md).
The operator derivation here uses the explicit pure-coordinate hypothesis.

For the cone family at stage `n>=5`, put `p=4*2^(n-5)=2^(n-3)`.
The shared endpoint plane has dimension `p`, the two orthogonal rotating
summands each have dimension `p`, and every limiting plane has dimension
`2p`. The generic and endpoint nullities are `2p` and `3p`. Conjugated
ordinary copies preserve the frame Gram identities and the circle
attachment. Since `p` is even, a block complex structure `J` supplies
both the global external trivialization and the quotient homeomorphism
used above. Thus the same proof gives

```text
attachment image M_n is homeomorphic to S^(p-1)*(S1 x S^(p-1)),
positive integral homology is Z in degrees p+1, 2p-1, 2p,
torsion is zero and positive-degree cup products vanish,
restricted total incidence has homotopy type S^(3p-1).
```

The cup-degree bound is `2p+2>dim M_n=2p`. The two mapping-cylinder
construction and uniform endpoint argument remain valid after doubling.
These statements follow by structural induction, with expanded exact
implementation checks through dimension 256. Successive finite checks
validate the implementation and differ from the unbounded written proof.

The all-size projector theorem and all-stage transport classify attachments
along each specified path. They leave the complete real rank loci, their
smooth subdivisions, all frontier directions, full local links, global
pair-space invariants, and unrestricted all-dimensional classification
open. [Coste's curve-selection and triangulation results](coste-semialgebraic-geometry.md)
allow additional semialgebraic paths and finite models; they supply no
proof that rational polynomial paths exhaust every frontier.

The proof-obligation manifest retains exact inputs and lemma dependencies
for a later Rocq port. The human defers new formalization until the
execution owner completes approved campaign raw collection and
preregistered adjudication, or supplies a new instruction. Physical
results control that workflow order. The deterministic algebraic proof
stands independently of QPU frequencies. Publication priority remains
unassessed.
