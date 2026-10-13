# Real kernel-graph closures and unit-partner evaluation

The real closure of the rank-24 kernel graph on the affine cone slice
`e1+e18+A e3+B e8+C e27` is a smooth cylinder `R x S1`. Its vertex fiber
is exactly a circle of rank-eight planes in the twelve-dimensional endpoint
kernel. A global rational frame and a trace-coordinate inverse establish
both coverage and uniqueness over all real coefficients on that slice.
The [implementation](../../gororoba_quantum/real_frontier_graphs.py) decides
membership at exact real algebraic points and records the induced integral
map from resolved unit partners to the attachment image.

The result computes the real graph closure used by the
[projective-frontier construction](projective_kernel_frontiers.md) for this
entire named slice. Other dimension-32 rank loci, ambient neighborhoods,
normalized-base boundary points outside the slice, and unrestricted global
invariants remain separate obligations.

## Prior work and proof inputs

The [cone rank and attachment proof](annihilator_kernel_limits.md) supplies
all real rank loci, the orthogonal endpoint decomposition, and the complete
attachment image. The new calculation gives global graph equations,
an inverse for its projector coordinates, and integral evaluation maps.
The earlier cone proof retains ownership of its original identities and
geometric incidence model; its bytes remain unchanged.

[Basu-Roy, Theorem 1 and Definitions 1-3](1803.00505.md), and
[Coste, Theorem 3.13](coste-semialgebraic-geometry.md), require actual real
closure membership before curve selection applies. Here the global frame
and its inverse prove that membership directly; fixed-direction real rays
realize every vertex plane. Polynomial paths with rational coefficients
still supply a smaller executable class than all real rays.

[Hatcher, Chapter 0, Proposition 0.18](hatcher-algebraic-topology.md)
justifies replacing attaching maps by homotopic maps with the indicated
CW/cofibration hypotheses. The retained Chapter 0 PDF, printed pages 15-16,
is re-read for those hypotheses. Its SHA-256 is
`3c390bac0b166d5e084bc723c8593dcc7fc6b9bef54dbcae0784a3d348c3c73e`.
The Basu-Roy and Coste bytes retain their registered identities and existing
external-only rights status. The repository claims a reproducible reduction
and certificate, rather than priority for graph resolution, homotopy
pushouts, or their characteristic algebraic-topology constructions.

## An inverse for the complete circle of planes

Let `P_F` be an orthogonal projector onto a fixed real c-plane, and let
`U,V` be orthonormal p-column frames satisfying

```text
U^T U=V^T V=I_p, U^T V=0, P_F U=P_F V=0.
```

For `a^2+b^2=1`, define

```text
P(a,b)=P_F+[(1+a)UU^T+(1-a)VV^T+b(UV^T+VU^T)]/2.
```

The external 2-by-2 scalar block has trace one and determinant zero.
Its eigenvalues are zero and one. Thus `P(a,b)` is an orthogonal projector
of rank `c+p`. It depends only on the line selected by the two rotating
summands. The following linear functions recover its circle coordinates:

```text
a=[tr(U^T P U)-tr(V^T P V)]/p,
b=2 tr(U^T P V)/p.
```

The identities prove injectivity. A candidate plane belongs to this circle
exactly when the recovered pair satisfies `a^2+b^2=1` and the entire
reconstructed matrix equals the candidate. The criterion includes every
entry of the projector and supplies a quantifier-free real equation set.
Its sufficiency follows from reconstruction; its necessity follows from
the displayed trace identities. The graph-plane image is homeomorphic to
`S1`, with an affine trace inverse, and is a smooth embedded circle.

For the dimension-32 cone, `c=p=4`, `U=W0/2`, `V=W_infinity/2`.
The equation `L_x0 P=0`, symmetry, idempotence and trace eight permit extra
subplanes. An explicit counterexample keeps the fixed four-plane, two
columns of U and two different columns of V. Its recovered coordinates
are `(0,0)`, so it fails the circle equation despite lying in the endpoint
kernel with the correct rank. This excludes that plane from all cone
approaches, including changing-angle approaches.

## A global frame with a positive real denominator

Put `(A,B,C)=(s*a,s*b,s)` with `a^2+b^2=1`. Every nonvertex cone point
has `s=C!=0`, and its unique direction is `(a,b)=(A/C,B/C)`.
The two internal six-dimensional pivots of the earlier proof now give a
single global four-column frame `F(s,a,b)`. Reducing the exact elimination
formulas modulo the circle equation gives denominator `D=1+s^2` in every
entry. The replay retains the polynomial matrix `D*F`.

The internal Gram matrix consists of two 2-by-2 blocks, with the second
block obtained by reversing the diagonal entries and the off-diagonal sign:

```text
G_first=[[2*(a^2*s^2+s^2+1)/(s^2+1), 2*a*s],
         [2*a*s, 2*(s^2+1)]],
det(F^T F)=16*(1+s^2)^2.
```

The frame uses identity free rows. Its real Gram matrix is positive
definite, and both its entry denominators and its Gram determinant stay
positive at every real amplitude and direction. The rational matrix

```text
P_internal=F(F^T F)^(-1)F^T
```

therefore extends over the whole cylinder. At `s=0`, F is the fixed
endpoint frame and `P_internal=P_F`, independently of direction.
The external global orthonormal frame E from the earlier cone proof has
projector `P(a,b)-P_F`. The combined frame `H=[F,E]` has rank eight,
satisfies the full multiplication-matrix kernel equation modulo
`a^2+b^2-1`, and gives

```text
P_graph(s,a,b)=P_internal(s,a,b)+P(a,b)-P_F.
```

The replay checks kernel action, symmetry, idempotence, trace eight,
internal/external orthogonality, positive denominator factors, and the
trace inverse as polynomial identities. The new exact-real point interface
uses real algebraic numbers, including radicals. The symbolic identities
and positive denominators prove their statements for arbitrary real
coefficients, including transcendental amplitudes and circle coordinates.
Finite point controls verify implementation behavior separately.

## Exact real graph closure

Let `G` be the graph of the complete eight-dimensional kernel over the
punctured cone. The global map

```text
Psi(s,a,b)=((s*a,s*b,s),P_graph(s,a,b)), a^2+b^2=1
```

parametrizes G for `s!=0`, because the previous rank classification proves
that each such kernel has dimension eight. At every real amplitude, the
base coordinate gives `s=C`, and the external-block trace formulas recover
a,b from `P_graph`. The polynomial identities verify that inverse.
Hence Psi is a smooth embedding, with a smooth inverse on its image.

The real closure of G is exactly the image of Psi on all `R x S1`.
For the forward inclusion, a convergent graph sequence has convergent
amplitudes, and the circle has a convergent subsequence of its directions.
Continuity of the positive-denominator formulas identifies its limit with
Psi. For the reverse inclusion, every vertex point is the limit of
`Psi(s,a,b)` as nonzero s tends to zero with fixed a,b. Each nonvertex point
already lies in G. This proves both inclusions for all real approaches.
Each component `s>0` or `s<0` has a half-cylinder closure; their intersection
is precisely the vertex circle.

The graph admits the quantifier-free description

```text
a^2+b^2=1, A=C*a, B=C*b,
P=P_graph(C,a,b),
a=[tr(U^T P U)-tr(V^T P V)]/4,
b=tr(U^T P V)/2.
```

Clearing the certified positive denominators preserves this real domain.
The point API checks those equations with exact algebraic arithmetic.
Radial normalization embeds the named affine coefficient slice by the
positive e1 coefficient and its ratio inverse. The statement covers that
image; its additional boundary as amplitudes diverge requires its own
rank and graph analysis.

## Resolved sphere space, evaluation and its fibers

The global frame H trivializes the graph's tautological kernel bundle.
The map `z -> H z/||H z||` on the unit coordinate sphere has inverse obtained
by applying the weighted frame inverse and normalizing. Thus its resolved
unit-partner space is `R x S1 x S7`. It retracts to the vertex space
`E0=S1 x S7`, while the kernel graph retracts to `S1`.

At the vertex, normalize the fixed frame and keep the orthonormal E.
Evaluation maps E0 onto the previously certified attachment image M.
Every partner with a nonzero rotating component has exactly one direction:
its two external coordinate vectors determine the rank-one line. A unit
partner in the fixed four-plane has every circle direction as its preimage.
Consequently M is the pushout

```text
A=S1 x S3 --j--> E0=S1 x S7,
       |p                 |
       v                  v
       S3 ------------->  M,
```

where j is the equatorial inclusion and p projects to the fixed sphere.
The product equator is a closed CW subspace after compatible sphere cell
structures are chosen, or has a tubular neighborhood giving a cofibration.
The ordinary pushout therefore agrees in homotopy type with the double
mapping cylinder. The sphere equator is nullhomotopic inside S7: rotate
its vectors toward any fixed external unit vector. Holding the circle
coordinate fixed gives a homotopy from j to the map preserving only the
circle. Hatcher's homotopic-attachment result applies to the mapping
cylinder construction with the indicated CW pair, preserving E0 up to the
resulting evaluation homotopy.

## Integral chains and the induced maps

The calculation generalizes to fixed dimension c>=2 and positive even
rotating dimension p. A block complex structure trivializes the p rotating
columns around the circle. Put `q=c+p-1`. The source has product cells
`e0,e_circle,e_sphere,e_product` in degrees `0,1,q,q+1`. The fixed sphere
has `b0,b_sphere` in degrees `0,c-1`. The intersection product has cells
in degrees `0,1,c-1,c`; its suspension in the double mapping cylinder has
`a0,a_circle,a_sphere,a_product` in degrees `1,2,c,c+1`.
After the stated nullhomotopy, the only nonzero boundaries are

```text
d(a0)=e0-b0, d(a_circle)=e_circle, d(a_sphere)=-b_sphere.
```

The contraction retains `e0,e_sphere,e_product,a_product`. Its projection
sends b0 to e0 and the cancelled cells to zero. Its degree-one homotopy
sends `b0 -> -a0`, `e_circle -> a_circle`, and
`b_sphere -> -a_sphere`. The replay verifies, over integers,

```text
pi*i=identity, d*h+h*d=identity-i*pi,
d*i=0, pi*d=0.
```

The existing Smith verifier independently computes the original complex's
integral homology and torsion. The source-to-cone inclusion followed by pi
records the actual induced evaluation map. In positive degrees it kills
the source circle class, maps the q-sphere and top product classes with
coefficient one to their retained target generators, and misses the new
class in degree c+1. If generator degrees coincide, their labels retain
both generators; the p=2 control checks that case explicitly.

For dimension 32, the graph closure has H0=H1=Z. E0 has integral homology
Z in degrees `0,1,7,8`. The target has Z in degrees `0,5,7,8`.
Evaluation induces isomorphisms in degrees seven and eight, kills degree
one, and has zero image in degree five. Torsion vanishes in both spaces.
The source integral cohomology has generators u,v,w in degrees 1,7,8,
with `u*v=w`, `v*u=-w`, and both squares zero. The product sphere cells'
standard diagonal and the product orientation give those coefficients.
The target's degree-seven and degree-eight generators pull back to v and
w; its degree-five generator pulls back to zero.

The target is `S^(c-1)*(S1 x S^(p-1))`, hence a c-fold suspension. Its
positive-degree cup products vanish integrally: the two contractible cone
halves let each positive-degree class lift to relative cohomology for
either half, and their relative product lands in cohomology relative to
the whole space. That group is zero. The target can therefore pull back
its top generator to the source product u*v without having a degree-one
class of its own. Equal Betti ranks in degrees seven and eight omit that
map and ring information.

## All-stage transport and remaining obligations

For a pure multiplier, ordinary doubling transports its full real kernel
projector as `diag(P,C_n P C_n)`. This fixed orthogonal transport commutes
with the global graph extension and its inverse. It doubles the fixed and
rotating widths. Induction transports the named cone graph and evaluation
construction to every stage n>=5, with `c=p=2^(n-3)`. The vertex graph
fiber remains S1, the resolved sphere fiber becomes `S^(2p-1)`, and the
same labelled integral contraction computes the evaluation map. The
implementation checks pencil transport through dimension 256; the
unbounded statement follows from the operator identity and induction.

The complete ambient dimension-32 graph closures and their overlap data
still require coverage proofs. Smooth ambient strata, all normal links,
normalized-base boundaries, a global finite pair-space model, and unrestricted
all-dimensional classification remain open. The proof-obligation manifest
retains the written arguments and exact inputs for Rocq translation. The
roadmap records the available raw-results milestone; the new statements
require their own compiler and kernel receipts before formal admission.
