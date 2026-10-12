# Cayley-Dickson annihilator topology: sources and implementation scope

The source review separates three objects: the unit zero-divisor element space,
the unit zero-product pair space, and finite basis-supported samples. A kernel
certificate determines one fiber. A bundle also needs a base, local charts, and
transition functions. A classification of kernel dimensions supplies neither a
cell decomposition nor all homotopy groups of the full pair space.

## Primary sources checked

The following versioned primary papers use the same doubling convention as
`cd_core.py`: `(a,b)(c,d)=(ac-conj(d)*b, d*a+b*conj(c))`.

| Source | Checked statements | Reuse |
| --- | --- | --- |
| [Reggiani, 2411.18881v1](https://arxiv.org/html/2411.18881v1#S2.SS2), Section 2.2 | Proposition 2.1 identifies sedenion zero divisors; Theorem 2.2 identifies normalized pair space with `G2`; the following text identifies `SU(2) -> G2 -> V2(R7)` | Base, fiber, group action, and normalization convention |
| [Biss, Dugger, Isaksen, math/0511691v1](https://arxiv.org/html/math/0511691v1), Definition 2.1, Theorem 7.1, Corollary 11.2, Section 12 | Explicit multiplication convention; Cayley frames parametrize octonion automorphisms; `Ann(a,b)={(c,-(ab)c/||ab||):c perpendicular H<a,b>}` for equal-norm orthogonal imaginary octonions | Explicit sedenion partner map and full annihilator, rather than inference from a few kernels |
| Same paper, Theorem 9.8, Proposition 9.10, Theorem 13.2 | Nonzero-element nullity is a multiple of four bounded by `M_n=2^n-4n+4`; every permitted multiple occurs | Separate published all-dimensional classification from computed finite witnesses |
| Same paper, Theorems 10.1 and 10.2 | Ordinary embedding doubles annihilator dimension; the special lift `(a,+/-i_n*a)` has nullity `2^n-4+dim Ann(a)` and an explicit direct-sum kernel | Exact recursive maximum-annihilator construction |
| Same paper, Corollary 14.7 and Theorem 15.7 | The unit maximal-annihilator element stratum is `2^(n-4)` disjoint copies of `V2(R7)` for `n>=4` | Known topology of a named stratum |
| [Biss, Christensen, Dugger, Isaksen, math/0702075v2](https://arxiv.org/html/math/0702075v2), Definition 1.4, Theorems 5.10, 6.7, and 6.12 | The orthogonal splitting `{a,b}` has annihilator dimension `dim Ann(a)+dim Ann(b)`, with an additional four dimensions precisely on the D-locus | A wider family beyond the maximum-annihilator constructor |
| Same sequel, Theorem 7.5 | A specified unit-factor D-locus in `A5` is the unit sphere bundle of `xi + R^2`, with `xi` the sedenion annihilator four-plane bundle | A published `S5`-bundle over `V2(R7)`, with its stated domain |
| Same sequel, Definition 1.6 and Theorem 8.12 | The near-maximum unit-element family `T_n^c` stabilizes exactly when `n>=c/4+4`, under the stated range of `c` | A stability result for a threshold family, distinct from the full pair space |

The two annihilator-paper HTML responses were inspected on 2026-10-11. Their
SHA-256 values below identify the fetched HTML rendering, rather than a PDF or
source archive. ArXiv version identifiers identify the mathematical source.

```text
math/0511691v1 HTML  1a29ef4ec9e7eb574093ce82cf2a49904814dc5a8268f810f61f6a6a52aea8d8
math/0702075v2 HTML  539dddc29b0d12c99eb284041b9667f1ba11388e4234cd912e99de154380eaaf
```

Two transcription boundaries matter. The introductory Theorem 1.2 in the first
paper omits the nonzero hypothesis that Proposition 9.10 states explicitly;
zero has the whole algebra as annihilator. Proposition 15.6 prints `i_n` in its
statement while its proof and Theorem 10.2 use the distinguished unit of the
lower algebra. The implementation uses `i_n=e_(2^(n-1))` in `A_n` and lifts from
`A_n` to `A_(n+1)`, which keeps dimensions explicit. The existence proof after
Theorem 13.2 points to Theorem 10.1 for the special lift; the required dimension
formula is Theorem 10.2. These locator slips do not alter the checked formula.

## Constructive formulas

For unit orthogonal `a,b` in the imaginary octonions, set `q=a*b` and
`H=span(1,a,b,q)`. The normalized element and partner maps are

```text
x(a,b) = (a,b)/sqrt(2),
y(a,b,c) = (c,-q*c)/sqrt(2),  c in H^perp, ||c||=1.
```

Corollary 11.2 supplies the entire kernel, so the four-dimensional domain
`H^perp` accounts for every partner. The corresponding Cayley matrix has columns
`[1,a,b,q,c,a*c,b*c,q*c]`. Theorem 7.1 identifies that matrix with an octonion
automorphism. The executable local checks compare all 64 basis products against
the multiplication table; the paper supplies the general theorem.

A seven-chart construction makes the gluing explicit. Set
`P=I-[1,a,b,q][1,a,b,q]^T`. On the open set `U_r` where `P*e_r` is nonzero,
for `r=1,...,7`, define

```text
c_r = P*e_r / ||P*e_r||,
F_r = [c_r, a*c_r, b*c_r, q*c_r].
```

The rank-four projection guarantees that these open sets cover the base. Each
`F_r` is an orthonormal frame of `H^perp`. On an overlap, write
`h_rs=F_r^T*c_s` in quaternion coordinates `[1,a,b,q]`. Then

```text
F_s = F_r * L_H(h_rs),
h_rt = h_rs * h_st,
```

where `h_rs` has unit norm and `L_H` denotes quaternion left multiplication.
The identity `u*(v*c)=(v*u)*c` for `u,v in H` fixes the multiplication order.
These transition matrices lie in the left quaternion copy of `SU(2)` in
`SO(4)`. Right multiplication of the local fiber coordinate by a unit quaternion
commutes with the transitions, yielding the principal action. A point outside
`U_r` requires another chart; choosing one frame with SVD or pivoting across the
whole base would conceal chart changes.

For exact bases, `trace(P)=4` guarantees a projected coordinate norm at least
`sqrt(4/7)`. Numerical admission also requires projected norm at least
`eps^(1/4)`, followed by section-complement, frame-complement, frame-Gram,
frame-projector, lifted-Gram, and lifted-annihilation residuals at most
`4096*eps`. The section residual uses the Euclidean norm; matrix residuals use
the spectral norm. The implementation checks approximate bases against these
residuals after normalizing the section. The exact cover theorem supplies the
mathematical coverage statement; numerical admission remains a separate check.

For the higher-dimensional construction, let `a` be nonzero and perpendicular
to `C_n=span(1,i_n)` in `A_n`. Theorem 10.2 gives

```text
Ann(a, s*i_n*a)
  = {(u, s*i_n*u) : u in Ann(a)}
    direct-sum {(v, -s*i_n*v) : v perpendicular span(1,a,i_n,i_n*a)},
s in {+1,-1}.
```

Each summand map becomes isometric after division by `sqrt(2)`. In particular,
`k_(n+1)=k_n+2^n-4`. Starting from a sedenion maximal element gives maxima
`4,16,44,104,228` in dimensions `16,32,64,128,256`. Unit-input normalization
uses the same `sqrt(2)` factor for each lift. Exact integer representatives
retain an explicit norm separately; scaling leaves their kernels unchanged.

The recursively constructed maximal **element** stratum has the published
`2^(n-4)` components. Over each such base point, the normalized partner set is
`S^(M_n-1)`. That sphere dimension grows with `n`; it is not the sedenion `S3`
fiber reused unchanged. The complete zero-product pair space also lies over
all smaller-nullity element strata. Gluing those strata and computing the full
space's homology require further constructions. The source review establishes
the named results above; it is not an exhaustive claim about all later research.

The sequel's notation is
`{a,b}=((a+b),i_n*(b-a))/sqrt(2)` for `a,b in C_n^perp`. Its D-locus requires
complex orthogonality of `a,b`, real orthogonality of `a` to `Ann(b)`, and real
orthogonality of `b` to `Ann(a)`. Both factors must be nonzero for the
sum-versus-sum-plus-four theorem. Theorem 7.5 fixes both factors to unit length;
its `S5`-bundle describes that constrained D-locus, rather than every
12-dimensional-annihilator element of `A5`. The stability theorem uses
`T_n^c={unit a : dim Ann(a)>=M_n-c}`; its threshold set includes several ranks
when `c>0`.

## Existing repository work reviewed

The canonical `open_gororoba` source snapshot is commit
`abbf13cada78d9b106fc610a36f6eea54567ecfc`. All eight listed file blobs were compared
with the corresponding Git objects at that commit and matched during the source
review. Source inspection establishes
the definitions and claimed theorem surfaces below; a fresh Rust test or Rocq
kernel run requires its own retained result.

| Source path in open_gororoba | Existing mechanism | Scope retained |
| --- | --- | --- |
| `crates/algebra_analysis/src/exact_annihilator.rs` | Rational multiplication matrices; nonzero rank-sized pivot minor plus independent full kernel; mutation checks; fixed-minor Schur-complement charts | Exact rational membership and rank, all 84 sedenion assessor diagonals, and an `A5` rank-24 scalar orbit already exist |
| Same source, `OperatorScaling` | `alpha=sum(abs(a_i))`, input norm squared, and normalized-input block scale squared | Unit normalization and sufficient LCU scale remain separate; the source returns matrices and scales, rather than a quantum circuit |
| Same source, `ConstantRankChart` | Requires both an invertible pivot and zero Schur complement | A chart on a fixed-rank algebraic locus; source explicitly leaves smoothness to a separate regularity argument |
| `crates/algebra_analysis/src/annihilator.rs` | SVD nullspace, rectangular-matrix handling, finite-input validation | Numerical proximity to singularity, with exact rank delegated to the rational module |
| `proofs/theories/MorenoKerLaNonAlternative.v` | Four disjoint-support annihilators and linear independence for `e3+e10` | A concrete lower bound of four; the file explicitly supplies no upper bound |
| `proofs/theories/MorenoSedenionInstance.v` | Concrete sedenion skew-symmetry instance | Its header identifies a remaining functor-internal kernel-equality assumption |
| `proofs/theories/C1542_MorVlambdaMod4.v` | Canonical alternative octonion eigenspaces of dimensions zero and four | The header explicitly excludes a proof of the arbitrary-dimensional mod-four theorem |
| `proofs/verified/C005_ZDAnnihilatorGeometry.v` and `C014_AnnihilatorDim4.v` | Concrete zero-product and nonzero-partner theorems | Their theorem bodies do not establish a general dimension-four classification despite the dimension-oriented titles |
| `docs/external_sources/REGGIANI_MANIFOLD_CLAIMS.md` | Source mapping and distinction between algebra and geometry | Its `docs/SEDENION_ATLAS.md` link is absent in the inspected checkout; the new construction cites the primary paper directly |

```text
0769f94d0ceb9bf935324a5220c5905d2826e6b88be19ef7e0c45d6b4d96ead2  exact_annihilator.rs
252bee923fc2f23c6962db30a4a15bb16592cb682b59b6d2202b126def31f82b  annihilator.rs
53979972099cadaae5f6b48d6a4d58fa8cdd407bb47ce8e031bd50580c430e4b  MorenoKerLaNonAlternative.v
36831adb9196953c14a0b42f5762d45b053ccc90a89176f3eb2b8b30087377cb  MorenoSedenionInstance.v
c64f9d4769e90a5533edfde8c4b53a623b275806b484dc4e8f2842175ed2fac5  C1542_MorVlambdaMod4.v
65fdecad8d18980a0e42aab7d02a0941053362cf8893162289d8f2d3e9fc6da3  C005_ZDAnnihilatorGeometry.v
effa10b99714c11f809a30821e131ecfa3d4f587eab8dc719da66a521443aea0  C014_AnnihilatorDim4.v
3deacd4d09f7d8dce1fdf1e1fc02f26774ec472adcd9b05ff2805e4029b3dc6f  REGGIANI_MANIFOLD_CLAIMS.md
```

The added Python work reuses the existing sign convention, rank-certificate
requirements, normalization discipline, and published annihilator formulas.
Its additions are an explicit sedenion chart/transition API, a bounded signed
basis-pair census across several dimensions, and recursive canonical witnesses
for the maximal strata. Neither the signed corpus nor the canonical witnesses
exhausts arbitrary real vectors. The source ledger prevents exact finite ranks,
published global results, and unfinished full-space topology from acquiring the
same verification label.
