# Principal skew charts with a small covering family

Fifteen explicit principal pivots cover every nonzero doubly-pure
coefficient vector in dimension 32. Each pivot has four coordinates and a
strictly positive determinant whenever its coefficient pair is nonzero.
The [implementation](../../gororoba_quantum/principal_skew_atlas.py) uses
that cover, exact principal elimination, and kernel-restricted overlap
maps. The [replay](../evidence/principal_skew_atlas/README.md) separates
finite rational checks from the all-real proofs below.

The existing [rank charts](../../gororoba_quantum/rank_charts.py) already
cover each fixed-rank locus through general row and column minors and
supply kernel transitions, cocycles, and Gram metrics. The
[centered skew charts](dimension32_skew_schur_charts.md) retain nonzero
residuals near a verified center. The added construction supplies a small,
explicit cover without choosing centers and supplies exact transition
identities across changing ranks. A chart cover provides a global
incidence presentation; computed topology requires additional work.

## Literature and attribution

[Biss, Dugger and Isaksen](math-0511691.md), Section 2 and Definition 2.10,
fix the Cayley-Dickson convention and orthonormal basis. Their Proposition
5.3 identifies the distinguished complex structure `C_n=span(1,i_n)`;
Lemma 9.5 places zero divisors in `C_n^perp`. Their Theorem 9.8 and
Proposition 9.10 give the fourfold nullity constraint and the nonzero
annihilator bound. Theorem 13.2 establishes sharpness. The adjoint identity
appears in their Lemma 3.4 and in
[Biss, Christensen, Dugger and Isaksen, Lemma 2.3](0905.2987.md).

The four-coordinate pivot below follows directly from the published
multiplication convention and quaternion multiplication table. Principal
elimination and kernel transitions use standard linear algebra; the note
supplies their short proofs. The small selected cover and its retained
certificates form a repository construction. The source review establishes
neither publication priority nor an unrestricted topology classification.
[Koebisu's Discussion question 4](2608.08232.md) still asks for the geometry
of the rank strata. [Zhilina's Section 6](2608.26893.md) offers a related
complex skew representation; the present construction keeps real
coordinates and requires no unimplemented complex intertwiner.

## All-stage four-coordinate pivot

Let the algebra have dimension `d=2^n`, with `n>=2`, and put `h=d/2`.
The nonzero doubly-pure coefficient domain is

```text
D_n={x in R^d : x_0=x_h=0, x!=0}.
```

For `1<=i<h`, choose the ordered principal index set

```text
I_i=(0,h,i,h+i),  a=x_i,  b=x_(h+i),  q_i=a^2+b^2.
```

Use the convention
`(u,v)(w,z)=(uw-conj(z)v,zu+v conj(w))`. The basis elements `e_i`,
`e_h`, and `e_(h+i)` square to `-1` and satisfy

```text
e_i e_h=e_(h+i),  e_h e_(h+i)=e_i,  e_(h+i) e_i=e_h.
```

Reversing two distinct imaginary basis factors changes the sign. These
identities follow from the doubling formula with `e_h=(0,1)` and
`e_(h+i)=(0,e_i)`. The four-dimensional span has the quaternion
multiplication table. The argument verifies that particular coordinate
subalgebra; it assumes no general two-generator associativity theorem for
higher Cayley-Dickson algebras.

A matrix entry of `L_x` at row `p`, column `q` depends only on
`x_(p xor q)`. The four selected indices are closed under XOR, so every
other coefficient drops out of the selected principal block. In the
ordered basis above, the block is

```text
A_i(x) = [[ 0,  0, -a, -b],
          [ 0,  0,  b, -a],
          [ a, -b,  0,  0],
          [ b,  a,  0,  0]].
```

Multiplication gives `A_i^2=-q_i I_4` and
`det A_i=q_i^2`. Hence the domain `U_i={x in D_n:q_i>0}` admits
`A_i^(-1)=-A_i/q_i`. Every nonzero doubly-pure coefficient belongs to at
least one pair, so

```text
D_n = union_(i=1,...,h-1) U_i.
```

The proof holds for arbitrary real coefficients and every stage `n>=2`.
Dimension 32 has `h-1=15` domains. The rational implementation expands
only its documented dimension range. Finite expanded checks remain
regression evidence for the all-stage argument.

## Initial pivot conditioning

On the doubly-pure domain, `sum_i q_i=||x||^2`. A deterministic selector
chooses the largest `q_i`, breaking ties by the lowest index. The selected
pivot satisfies

```text
q_i >= ||x||^2/(h-1),
det A_i >= ||x||^4/(h-1)^2,
||A_i^(-1)||_2 <= sqrt(h-1)/||x||.
```

The inverse norm follows from `A_i^T A_i=q_i I_4`. In dimension 32 at
unit norm, the determinant is at least `1/225` and the inverse norm is at
most `sqrt(15)`. These are initial-pivot bounds. Later principal
refinements require their own conditioning analysis. Exact rational
arithmetic retains the sign and rank decisions independently of numerical
conditioning.

## Principal reduction on each domain

For any ordered even-sized principal pivot `I`, let `U` select its basis
vectors and let `V` select the remaining indices in increasing order.
Then `T=[U,V]` is a permutation matrix. For a nonzero doubly-pure input,
`L=L_x` is skew-symmetric. Define

```text
A=U^T L U,  B=U^T L V,  D=V^T L V,  delta=det A,
S=D+B^T A^(-1) B,
H=V-U A^(-1) B,
J=V^T,
G=H^T H.
```

The chart requires `delta!=0`. Block elimination gives

```text
P=[[I,-A^(-1)B],[0,I]],
P^T T^T L T P=diag(A,S),
S^T=-S,
L H=V S,
J H=I,
rank L=|I|+rank S,
ker L=H(ker S).
```

The independent free-coordinate rows of `H` make `G` positive definite.
Consequently `(x,w)->(x,H(x)w)` and `(x,y)->(x,Jy)` give inverse
continuous maps between `S(x)w=0, w^T G(x)w=1` and
`L_x y=0, y^T y=1` on the pivot domain. The construction allows the
kernel dimension to change. At an invertible point the unit-partner fiber
is empty, and the full kernel frame has shape `d x 0`.

Clearing denominators gives
`Sbar=delta D+B^T adj(A)B` and `Hbar=delta V-U adj(A)B`.
Their polynomial identities are `L Hbar=V Sbar` and `J Hbar=delta I`.
The inequation `delta!=0` remains part of every chart. A singular even
skew pivot has corank at least two, hence `adj(A)=0`; vanishing cleared
numerators at that boundary supply no rational chart.

## Constructive maximal principal refinement

Every nonzero skew matrix has a nonzero off-diagonal entry. Choose the
first such pair in the residual coordinate order. Its two-by-two block
has determinant equal to the square of that entry and is invertible.
Eliminating the block leaves another skew matrix and decreases rank by
two. Repetition stops exactly when the residual becomes zero.

Each selected residual pair adds the corresponding original coordinate
indices to the existing principal set. If `A` is the existing pivot and
`R` is the selected residual two-by-two principal block, the determinant
identity is

```text
det L_(I union selected pair, I union selected pair)=det(A) det(R).
```

Thus every refinement stays principal and invertible. Induction proves
that the final principal block has order `rank L`; the zero residual
certifies maximality. The proof also establishes the standard fact that
every skew matrix has a nonsingular principal minor of every even order
up to its rank. The algorithm avoids enumerating all principal subsets.
The rational certificate retains the selected pairs, pivot determinants,
and stopping residual for independent replay.

For a final pivot of order `r`, the rank-`r` locus in that domain is
exactly `S=0`. The matrix `H` then supplies a complete kernel frame of
width `d-r`. Those frames give a vector bundle over the fixed-rank locus
with its subspace topology. Smoothness of that base remains a separate
condition. The implementation links maximal principal certificates to
the existing constant-rank chart API and compares both frames.

## Overlap maps across changing ranks

Use subscripts `a`, `b`, and `c` for principal charts at the same point.
Define the ambient coordinate transport from chart `a` to chart `b` by

```text
M_ba=J_b H_a,
C_ba=U_b A_b^(-1) U_b^T V_a.
```

Different pivot sizes give rectangular `M_ba`. Even a square ambient map
requires restriction to the residual kernel before claiming invertibility.
The elementary identity

```text
I-H_b J_b=U_b A_b^(-1) U_b^T L
```

follows by applying both sides to the coordinate decomposition
`y=U_b u+V_b w`. Combining it with `L H_a=V_a S_a` proves the exact
residual-factor identities

```text
H_b M_ba-H_a=-C_ba S_a,
S_b M_ba=H_b^T V_a S_a,
M_ab M_ba-I=-J_a C_ba S_a,
M_cb M_ba-M_ca=-J_c C_ba S_a.
```

Therefore `M_ba` maps `ker S_a` to `ker S_b`, reconstructs the same full
partner, has inverse `M_ab` on that kernel, and satisfies the cocycle
identity there. These statements hold throughout each real overlap,
including points where the rank changes.

For `u,v` in `ker S_a`, reconstruction also gives

```text
u^T M_ba^T G_b M_ba v = u^T G_a v.
```

The equality preserves the transported sphere metric. The ambient matrix
identity can fail outside the kernel. With a certified reduced kernel
frame `K_a`, exact point verification checks
`K_a^T (M_ba^T G_b M_ba-G_a) K_a=0`. Reduced kernel frames in both
charts convert the restricted map into an ordinary `GL(k,R)` matrix at
constant nullity `k`. An invertible base point has `k=0`; its coordinate
isomorphism is the unique map on the zero vector space.

The orientation convention here maps source coordinates to target
coordinates. The existing `rank_charts.chart_transition(source,target)`
returns the opposite orientation: target coordinates to source
coordinates. An API comparison must reverse its arguments or invert the
matrix explicitly.

## Global incidence presentation and remaining topology

Apply the fifteen domains to the dimension-32 unit base. Glue the local
sets `S_i(x)w=0, w^T G_i(x)w=1` through the restricted maps `M_ji`.
The covering theorem and overlap identities make the resulting quotient
homeomorphic to the full normalized pair incidence. The homeomorphism is
`(x,w)->(x,H_i(x)w)`; its inverse is continuous locally through `J_i`.
The same construction works at every stage with its finite covering
family. The conclusion is a global semialgebraic presentation by equations
and gluing maps.

The cover does not compute a compatible triangulation, CW attachments,
connected components of lower-nullity loci, normal links, or characteristic
classes. The domains and their intersections need not be contractible after
restriction to rank loci, so their nerve alone does not determine homotopy
type. [Coste's Theorems 3.12, 4.1, and 4.4](coste-semialgebraic-geometry.md)
supply triangulation, Hardt triviality, and local conic existence theorems;
their concrete partitions and certificates remain work.

The next geometric obligations are the real reduced equations, independent
relations and real radicals, smooth subdivisions, closure incidences, and
approach-dependent limiting kernels. Integral boundary maps, torsion, cup
products, and chosen homotopy invariants follow a certified computable
attachment model. A uniform chart construction at every stage supplies
neither an all-dimensional classification nor a Rocq kernel proof. QPU
measurements cannot replace those algebraic and topological obligations.
