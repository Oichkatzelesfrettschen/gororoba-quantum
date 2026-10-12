# Cellular homology of the four-coordinate zero-product incidence

The fixed-support kernel frame converts a continuous zero-product family into
an explicit finite CW space whose attachments admit exact integer computation.
Let `A_n` denote the real Cayley-Dickson algebra of dimension `2^n`, using the
repository multiplication convention. For `n>=5`, define

```text
X_n = {(x,y): x=a e1+b e10+c e18+d e25 in A_n,
                 ||x||=||y||=1, x*y=0}.
h = 4*2^(n-5).
```

The first operand has the displayed fixed support and arbitrary real
coefficients. The second operand ranges over every coordinate of `A_n`.
The [rank theorem](four_support_rank_loci.md),
[global incidence homeomorphism](four_support_incidence_geometry.md), and
[ordinary-doubling theorem](four_support_doubling.md) identify `X_n` with the
five-block incidence constructed below. Those three geometric dependencies
are essential: a correct abstract chain complex alone cannot identify a
space's topology.

The construction yields 1,200 cells at every stage, with degrees depending on
`h`. Its integral homology has the following complete list of nonzero groups:

| Degree | Integral homology |
| --- | --- |
| `0` | `Z` |
| `2` | `Z^23` |
| `h+1` | `Z^40` |
| `2h` | `Z^8` |
| `3h` | `Z^16` |
| `4h-1` | `Z^8` |

Every group is torsion-free. Integral cohomology has the same graded groups;
the degree-zero generator is the unit and every product of positive-degree
classes is zero. The proof below establishes the CW model, integral groups,
and ring. A wedge decomposition, higher homotopy operations, and the
unrestricted dimension-32 or all-dimensional pair spaces remain separate
research questions. The result carries no publication-priority claim.

## Base characteristic maps

Use the linear coordinates

```text
(p,q,r,s) = (a-b-c-d, a-b+c+d, a+b-c+d, a+b+c-d).
Q = pq+rs.
```

The coordinate transform takes the unit coefficient sphere to the radius-two
sphere. The positive-nullity base is the closed subset
`B={p*q*r*s*Q=0}` of that sphere. The remaining 24 smooth strata have empty
unit-partner fibers and therefore contribute no points to `X_n`.

The [geometry enumeration](../../gororoba_quantum/four_support_geometry.py)
provides 72 positive-nullity strata: eight vertices, 24 edges, 32 triangles,
and eight squares. The following characteristic maps establish their
regular CW structure; the stratum count alone supplies no such conclusion.

A coordinate vertex, edge, or triangle uses signed barycentric coordinates
on its active coordinate rays, in increasing coordinate order `p<q<r<s`.
For a nonnegative barycentric vector with sum one, restore the coordinate
signs and call the vector `v`. The map `v -> 2v/||v||` is well-defined and
injective: every ray in the signed closed orthant has exactly one vector
with absolute-coordinate sum one. The image is the entire closed cell and
its boundary is the union of the corresponding smaller coordinate cells.

A full-support cone cell has opposing signs for `pq` and `rs`. Its closed
square uses `0<=u,v<=1` and magnitudes

```text
(|p|,|q|,|r|,|s|)
    = (u*v, (1-u)*(1-v), u*(1-v), (1-u)*v).
```

Restore its fixed coordinate signs, then apply the same radial map. The
magnitude matrix `[[|p|,|r|],[|s|,|q|]]` has determinant zero and entry sum
one. Conversely, a nonnegative matrix of rank one and entry sum one equals
the outer product of its row and column marginals. Its marginals recover
`u=|p|+|r|` and `v=|p|+|s|`, including every boundary point. The parameter map
is consequently injective and covers the complete closed cone cell.

Each domain is a closed disk; a continuous bijection from that compact
domain to its Hausdorff image is a homeomorphism. Every boundary image is a
union of lower cells. The finite closed cover establishes the weak topology
and hence a regular finite CW structure on `B`. The argument requires
neither Whitney conditions nor closed-disk models for the omitted invertible
three-strata.

Orient coordinate edges and triangles by their ordered coordinate vertices.
The simplex boundary deletes vertex `j` with coefficient `(-1)^j`.
Orient each square by `du wedge dv`. Its boundary follows
`q -> r -> p -> s -> q`. Convert each directed boundary edge to the
increasing-coordinate orientation to obtain its sign. The executable
certificate checks every incidence against `closure_contains`, verifies
kernel-coordinate containment, and checks the resulting base differential
squares to zero.

## Compatible fiber cells and orientations

The available blocks over a stratum are the cone block when `Q=0` and the
coordinate blocks whose respective coordinates vanish. Each block has real
dimension `h`. Along a base boundary, the available block set only grows;
the global frame identifies the attachment with literal zero insertion in
these block coordinates.

Give each `S^(h-1)` block the CW structure consisting of a north-pole point
and one open `(h-1)`-cell. An explicit characteristic map on the closed unit
ball in `R^(h-1)` is

```text
t = ||w||^2,  D = t+(1-t)^2,
phi(w) = (2*(1-t)*w/D, (t-(1-t)^2)/D).
```

Here `D=(t-1/2)^2+3/4>0`. The squared numerator norm equals `D^2`.
The boundary `t=1` maps to the north pole. Stereographic coordinates on the
open ball equal `w/(1-t)`; the radial function `r/(1-r^2)` increases from
zero to infinity. Thus the open ball maps homeomorphically onto the sphere
minus its north pole. These identities hold in every required dimension.

For an available nonempty block set `A`, the join of its block spheres is
the unit sphere in their direct sum. The homeomorphism is

```text
(lambda_i,u_i) -> z_i=sqrt(lambda_i)*u_i,
lambda_i>=0, sum lambda_i=1.
```

A zero weight forgets its factor coordinate. The join quotient is compact;
the displayed continuous bijection to the Hausdorff unit sphere is a
homeomorphism. A fiber cell selects a nonempty participating subset `J` of
`A`, selects the point or the top cell in each participating factor, and
requires positive weights. Its characteristic domain is the product of the
closed weight simplex with the selected closed factor disks, hence a closed
ball. Its interior is an open ball and its boundary enters smaller cells.
Factor-boundary collapses make the fiber CW structure nonregular.

Use increasing global block order `(cone,p,q,r,s)`. For `k` participating
blocks with ordinary cell dimensions `d_0,...,d_(k-1)` in `{0,h-1}`, begin
with the weight simplex orientation followed by the oriented factor disks.
Multiply the resulting orientation by `(-1)^alpha`, where

```text
alpha = sum_i (k-1-i)*d_i.
```

Deleting a point factor at participating position `j` changes `alpha` by
`sum_(i<j) d_i`. Combining the simplex facet sign with that orientation
change gives

```text
(-1)^(j + sum_(i<j) d_i)
    = (-1)^(sum_(i<j)(d_i+1)).
```

The certificate checks the orientation identity for every abstract point
facet of the five-block state set. A top disk's boundary drops dimension by
`h-1>=3`, so its cellular differential contributes zero. Removing the only
point factor is an augmented boundary and is omitted from ordinary chains.
The finite states absent, point, and top therefore have shifted degrees
`0,1,h`; the fiber cell dimension is the shifted-degree sum minus one.

## Product CW structure and signed chain matrices

For each base cell, take its product with every fiber cell supported on its
available blocks. The product characteristic map uses the base map and the
global block sphere coordinates. Every boundary base point permits all
blocks of the source cell, so the closed product map remains in the
incidence. The interior maps homeomorphically onto its open product cell.
Both base and fiber boundaries land in strictly lower-dimensional cells.

The finite disjoint union of compact characteristic domains surjects onto
the Hausdorff incidence subspace and is therefore a quotient map. The maps
establish the weak topology and the finite CW structure. The positive
global frame and its continuous inverse transfer that structure to `X_n`.
Kernel variation and attachments enter through actual coordinate inclusions,
rather than through a rank count or a closure poset.

For a base cell `e` of dimension `b` and fiber state `f`, use the base-first
product orientation. The cellular differential is

```text
d(e,f) = sum_face incidence(e,face)*(face,f)
         + (-1)^b*(e,d_join(f)).
```

In a join boundary, deleting a point uses the preceding shifted-degree sum
for its sign; the final empty assignment is omitted. Since `h` is even,
all signs agree with those at `h=4`. Base inclusion coefficients are `+1`
because the global fiber characteristic map and orientation remain identical.

[The implementation](../../gororoba_quantum/four_support_homology.py)
derives the matrices from `enumerate_strata()`, the simplex/square formulas,
and the fiber state product. The retained evidence contains every cell,
every signed nonzero matrix entry, and every cancellation. At `h=4`, the
chain ranks by degree are

```text
degree  0   1   2  3   4   5  6  7   8  9  11  12  15
rank   32 112 128 56 160 248 80 48 152 96  32  48   8.
```

The matrices satisfy `d*d=0` over the integers. The total cell count is
1,200, derived as eight vertex fibers of 80 cells, eight edge fibers of
eight cells, sixteen edge fibers of 26 cells, and forty face fibers of two
cells. The fiber over `k` available blocks has `3^k-1` cells.

## Integral cancellation certificate

For a unit pivot `u=+1` or `-1`, write the relevant differential in blocks:

```text
A = [[u,r],[c,D]],
U = [[1,0],[-c/u,I]],  V = [[1,-r/u],[0,I]],
U*A*V = [[u,0],[0,D-c*r/u]].
```

Every entry of `U` and `V` is an integer and both determinants are one.
Change the preceding differential to `previous*U^-1` and the following
differential to `V^-1*following`. The chain identities force the matching
preceding column and following row to vanish. Deleting the isolated
`Z --u--> Z` pair removes a contractible direct summand and preserves
integral homology. The argument preserves torsion, unlike rational rank
reduction.

The generator chooses deterministic sparse unit pivots and records each
pivot and its complete pre-operation row and column vectors. An independent
replay applies elementary row and column shears, explicitly applies their
inverses to the adjacent differentials, checks the deleted vectors vanish,
and verifies `d*d=0` after every cancellation. The replay uses the shear
operations rather than the generator's Schur-complement update.

The 552 cancellations remove 1,104 generators. All remaining differential
entries vanish exactly, leaving 96 generators. The zero residual therefore
certifies the complete integral homology and the absence of torsion.
Retained negative controls reject altered signs, omitted product signs,
missing generators, changed grading, mutated pivot units or vectors,
truncated reductions, and a nonunit torsion residual. Independent Smith
computations check small join-sphere fixtures and detect `Z/2` torsion;
two sheared chain fixtures exercise both adjacent inverse updates and retain
their `Z/6` residuals.

## Uniform degree construction and cohomology ring

Every boundary preserves the complete subset `T` of top sphere factors.
The certificate verifies that each pivot and each shear also remains in
one such subset. Consequently the complex splits as an integral direct
sum over `T`. Replacing shifted top degree four by `h` changes each degree
in that summand by `(h-4)*|T|`, while every matrix and cancellation remains
identical. The ordinary-doubling theorem identifies the regraded complex
with `X_n` for `h=4*2^(n-5)`.

The exact residual generators have the following derived bigradings:

| `|T|` | Offset in `h*|T|+offset` | Multiplicity |
| --- | --- | --- |
| 0 | 0 | 1 |
| 0 | 2 | 23 |
| 1 | 1 | 40 |
| 2 | 0 | 8 |
| 3 | 0 | 16 |
| 4 | -1 | 8 |

The implementation stores this sparse bigrading and relabels its degrees;
it never expands an ambient `2^n` matrix to compute the all-stage groups.
Concrete degree expansion accepts integer stages from 5 through 4096 and
checks that bound before constructing any power of two. An allocation-free
`stage_homology_descriptor` records exponent, multiplier and offset expressions
at every stage, including a regression at stage `10^100`. A stage-128
regression exercises large exact degree labels. The uniform
conclusion follows from the preserved summands and doubling induction,
rather than from that finite regression.

Dualizing the integral chain homotopy equivalence produces a cochain
homotopy equivalence: each deleted unit pair remains contractible, and the
surviving free groups retain zero differential. Integral cohomology therefore
has the same supported degrees and ranks. The integral universal coefficient
theorem gives the same conclusion because every homology group is free. For even `h>=4`, the positive
support is `{2,h+1,2h,3h,4h-1}`. For every ordered candidate target and every
unordered pair of supported positive degrees, the certificate solves the
affine degree equality exactly. Every possible root lies outside even
integers at least four, or the equality is a nonzero constant. Thus every
positive-degree product has a zero target group. The degree-zero `Z` acts
as the unit. This establishes the ring without a cellular diagonal because
degree support forces the vanishing; chains alone do not settle arbitrary
cohomology products.

The Euler characteristic is `1+23-40+8+16-8=0`, consistent with the odd
sphere fibers. As an independent low-degree check, the coordinate part of
`B` is the two-skeleton of the four-dimensional cross-polytope boundary,
with `H_1=0` and `H_2=Z^15`. The eight cone squares increase the second
rank to 23. These checks support the explicit certificate and do not replace
its geometric identification or integer basis proof.

## Sources and reproduction

The [Coste source note](coste-semialgebraic-geometry.md) supplies compatible finite
triangulation, Hardt triviality, and local-cone context; its existence theorems
do not supply these explicit matrices. The
[Hatcher source note](hatcher-algebraic-topology.md) supplies the CW and
attachment framework. The construction above gives the actual characteristic
maps and degrees rather than assigning topology from a face poset.

The [retained replay](../evidence/four_support_homology/README.md) binds
source and proof-note hashes, verifies loaded module paths, recomputes every
chain and cancellation, and compares the complete JSON result. Normal and
optimized Python, serial execution, and four-worker execution produce
identical certificate bytes with the pinned dependencies. The replay uses
exact local CPU arithmetic and performs zero QPU submissions.
