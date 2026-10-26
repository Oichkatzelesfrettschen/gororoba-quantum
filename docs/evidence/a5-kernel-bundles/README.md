# A_5 kernel bundles: exact transport, symmetry, stabilizers, and Pfaffian frames

This evidence directory executes the
[kernel-bundle program](../../design/a5-kernel-bundles-program.md). The current result corrects the complex transport
used to represent the real annihilator kernel, fixes the action of the canonical complex structure, computes the
constant kernel-pencil symmetry algebra and a visible twelve-component subgroup, and gives an exact finite family of
rational kernel frames covering all seven pieces of nullity at least twelve. It also identifies the connected compact
stabilizer and its irreducible kernel representation on both nullity-sixteen components, reduces those two bundles to
the sedenion `SU(2)` bundle, and determines their ordinary real, complex, and quaternionic classes. An exhaustive
component census, the non-homogeneous pieces' reduced transitions, the remaining non-homogeneous unit-section
topologies, and their characteristic classes remain open. The aligned nullity-twelve pieces now have an explicit
one-dimensional compact-orbit quotient, a computed unit-section topology, and exact stabilizer representations on
their principal and endpoint orbits. The open `V` orbit now has an explicit three-dimensional connected compact-orbit
quotient and its recorded representative is identified as another collinear endpoint.

Every computation uses rational or Gaussian-rational arithmetic. [`result.json`](result.json) is the output of
[`kernel_symmetry.py`](kernel_symmetry.py) `--out`. [`frames-result.json`](frames-result.json) is the output of
[`kernel_frames.py`](kernel_frames.py) `--out`. `stabilizer-result.json` is the output of
`stabilizer_representation.py --out`. `nullity-sixteen-bundle-result.json` is the output of
`nullity_sixteen_bundle.py --out`. `aligned-orbit-moduli-result.json` is the output of
`aligned_orbit_moduli.py --out`. `aligned-stabilizer-result.json` is the output of
`aligned_stabilizer_representation.py --out`. `v-orbit-moduli-result.json` is the output of
`v_orbit_moduli.py --out`. The focused contracts and mutation controls run without random input.

## Conventions

Write a doubly pure element of A_5 as `y = (p, q)` and put `z = p + i q` in C^15. For `x = (r, s)` in A_5, define

`phi(x) = r + i conjugate(s)` and `psi(x) = conjugate(phi(x))`.

The bordered complex matrix is

`A(z, t) = [[0, -t^T], [t, C_z]]`,

where `C_z` is the imaginary block of left multiplication by `z` in the complexified sedenions. The representative
names `B9`, `V`, `VB`, `Vap`, `Vam`, `Np`, and `Nm` are the open-orbit representatives B9, V, V intersect B9,
V^a_+, V^a_-, N_+, and N_- from the
[regularity record](../a5-strata-regularity/README.md#conventions).

## The connected compact stabilizer on `N_+` and `N_-` is `U(2)`

Let `K_c` denote the connected compact symmetry acting effectively on a unit section: the fourteen compact `G_2`
directions and the lifted base phase. The two directions that act trivially on the base and the radial scaling belong
to the full constant-triple group but do not change this unit-section orbit calculation. At either exact representative
`p` of `N_+` or `N_-`, the tangent map

`Lie(K_c) -> T_p N_+-`, `X -> X p`,

has rank 11 and a four-dimensional kernel. Every computed kernel direction fixes `p`; its domain lift preserves
`ker_R L_p` and commutes there with `J=L_(e_16)`. Exact brackets give a one-dimensional center and a
three-dimensional derived algebra. In the derived basis selected by the computation, the Killing matrix is
`-32 I_3`, so the compact derived algebra is `su(2)`, not the split real form. Thus

`Lie((K_c)_p) = su(2) + u(1)`.

The repository source record identifies the `G_2` action on `V_2(R^7)` with point stabilizer `SU(2)`
([source note](../../notes/papers/2411.18881.md)). The exact lattice check identifies the extra central circle. In the
ordered basis of fourteen derivations followed by the base phase, its primitive generator has nonzero coefficients

`compact_g2_7 + compact_g2_13 + 2 base_phase_lift`.

The `G_2` part `X` has characteristic polynomial

`lambda^8 (lambda^2+1)^8 (lambda^2+4)^4`

on both the base and the domain, and satisfies `X(X^2+1)(X^2+4)=0`. Therefore its half-turn is the exact rational
matrix

`exp(pi X)=I+(8/3)X^2+(2/3)X^4`.

The replay checks that this matrix is a nonidentity involution, fixes `p`, and centralizes the derived `SU(2)`. The
phase coefficient two contributes `exp(2 pi J)=I` at the same parameter value. The half-turn is consequently the
nontrivial center of the source-established `SU(2)`, and the connected compact stabilizer is

`(K_c)_p = (SU(2) x U(1))/diagonal Z_2 = U(2)`.

## The rank-eight complex fiber splits into five `U(2)` irreducibles

Use the complex structure `J` on `ker_R L_p`, so the fiber has complex dimension eight. The program constructs a
`J`-adapted exact kernel basis and expresses all four stabilizer generators as Gaussian-rational 8 by 8 matrices.
Their matrix commutators equal the represented stabilizer brackets exactly.

Normalize the central generator `Z` by the primitive circle above and write `V_(n,m)` for the irreducible module on
which the `SU(2)` factor has highest weight `n` and `Z` acts by `i m`. The inverse-Killing Casimir has characteristic
polynomial

`lambda^2 (8 lambda-3)^6 / 262144`.

The eigenvalues `0` and `3/8=n(n+2)/8` give two `SU(2)` singlets and three standard doublets. Joint central weights
give the full decomposition, identically on `N_+` and `N_-`:

`(ker_R L_p,J) = V_(0,-4) + 2 V_(1,-3) + V_(0,-2) + V_(1,-1)`.

The parity `m=n mod 2` in every summand is the diagonal-`Z_2` descent condition. If `S` denotes the standard
two-dimensional representation of `U(2)`, the same decomposition is

`det^(-2) + 2(S tensor det^(-2)) + det^(-1) + (S tensor det^(-1))`.

The repeated `V_(1,-3)` term is not inferred from dimensions alone. The exact commutant has dimension seven and
supplies two commuting rank-two projectors inside its four-dimensional isotypic block. Together with the three
central spectral projectors, the five projectors have ranks `1,2,2,1,2`; they are idempotent, invariant, pairwise
annihilating, and sum to the identity. This proves the displayed irreducible direct sum.

The falsifier was a stabilizer direction moving `p`, failing to preserve the kernel or commute with `J`, a bracket or
Killing-form mismatch, a different decomposition on the two components, an isotypic block without exact invariant
projectors, a failed diagonal half-turn, or a planted moving direction that survived. None occurred. The mutation
replaces one stabilizer basis vector with a compact direction that moves `p`, and both component checks reject it.
The result determines the connected compact homogeneous representation. The disconnected stabilizer inside the
still-unclassified full component group remains open. The next section uses the connected representation to compute
the ordinary bundle's characteristic and K-theory classes.

## The complex bundle has a nonzero order-two K-class

The connected compact orbit can be written as

`(G_2 x U(1))/U(2) = G_2/SU(2) = V_2(R^7)`.

The determinant sequence `SU(2) -> U(2) -> U(1)` makes the inclusion of `G_2` a reduction of the homogeneous
principal `U(2)` bundle to the source-established principal bundle
`SU(2) -> G_2 -> V_2(R^7)`. Consequently, the central weights in `V_(n,m)` retain equivariant information but do not
change the ordinary vector bundle. If `xi=G_2 x_(SU(2)) C^2` denotes the standard complex doublet, the fiber
decomposition above gives, on each of `N_+` and `N_-`,

`E_C = C^2 + 3 xi`.

The seven sedenion complement charts supply the transition representation

`diag(I_2,Q,Q,Q)`, `Q in SU(2)`.

The exact replay checks the real and complex quaternion representations on all sixteen products of quaternion basis
elements, a rational unit-quaternion inverse and cocycle, unitarity, determinant one, and two preserved
anticommuting right-quaternion structures. The structure group therefore reduces to the diagonal `SU(2)=Sp(1)` in
`Sp(4)` and `SU(8)`. The source-backed sedenion atlas supplies the seven base charts; the replay derives the displayed
fiber representation from the committed stabilizer decomposition instead of constructing another kernel atlas.

The sphere fibration `S^5 -> V_2(R^7)=S(TS^6) -> S^6` gives a four-cell complex in degrees 0, 5, 6, and 11. The
degree-six cellular boundary is the Euler number `chi(S^6)=2`; every other cellular boundary is zero by degree. The
resulting groups are

```text
H_0=Z, H_5=Z/2, H_11=Z,
H^0=Z, H^6=Z/2, H^11=Z.
```

The base is simply connected, and every positive-degree cup product vanishes by degree. This cellular calculation
also gives `K^0=Z+(Z/2)` and `K^1=Z` through the complex K-theory Atiyah-Hirzebruch spectral sequence; degree and
torsion leave every differential zero.

The homogeneous calculation identifies which class `xi` occupies. Put `t=[V_1]` in
`R(SU(2))=Z[t]`. The point stabilizer fixes the three imaginary directions of its quaternion subalgebra and acts on
the four-dimensional complement as the real quaternionic standard module. The complexified restrictions of the two
fundamental `G_2` representations are therefore

```text
7  -> 3 V_0 + 2 V_1 = 3+2t,
14 -> 3 V_0 + 4 V_1 + V_2 = t^2+4t+2.
```

For `x=t-2`, the two augmentation relations are `2x` and `x^2+8x`. The Hodgkin Tor spectral sequence applies because
`G_2` is simply connected and `SU(2)` is connected. Its Koszul complex has

```text
Tor_0 = Z[x]/(2x,x^2) = Z + (Z/2)x,
Tor_1 = Z,
Tor_2 = 0.
```

For completeness, every first syzygy is a polynomial multiple of `(-(x+8),2)`, while the second Koszul boundary is
`x (-(x+8),2)`; hence `Tor_1=Z[x]/(x)=Z`. The spectral sequence has only columns zero and one, so it collapses without
an extension ambiguity. The associated-bundle map sends `x` to `[xi]-2`, proving

`reduced K^0(V_2(R^7)) = (Z/2){[xi]-2}`.

This order-two class is invisible to ordinary Chern classes. A line summand is trivial because `H^2=0`. The rank-two
bundle `xi` has `c_1=c_2=0` because `H^2=H^4=0`, and `c_j=0` for `j>2` by rank. The Whitney formula then gives
`c(E_C)=1`, in particular `c_3 mod 2=w_6=0`. The stable and actual conclusions are nevertheless:

| Connected-stabilizer summand | Ordinary bundle per copy | `c_3 mod 2` | Reduced K-class per copy | Complex class |
| --- | --- | ---: | --- | --- |
| `V_(0,-4)` | `C` | 0 | 0 | trivial |
| `2 V_(1,-3)` | two copies of `xi` | 0 | `x` each | stably and actually nontrivial per copy |
| `V_(0,-2)` | `C` | 0 | 0 | trivial |
| `V_(1,-1)` | `xi` | 0 | `x` | stably and actually nontrivial |
| Total `E_C` | `C^2+3xi` | 0 | `3x=x` | stably and actually nontrivial |

The real and quaternionic answers differ. At `(a,b)` the four vectors `(1,a,b,ab)` globally frame the quaternion
subalgebra `H`, so the octonion splitting `O=H+H^perp` gives

`xi_R + R^4 = R^8` and `E_R + R^12 = R^28`.

The real rank of `E_R` is 16, greater than the base dimension 11, so stable-range cancellation makes `E_R` actually
trivial. This argument does not decide whether the individual real four-plane `xi_R` is actually trivial. Pairing
the two trivial complex lines gives a trivial quaternionic line, so `E_H=H+3xi_H`; forgetting quaternionic structure
recovers the nonzero complex class `x`, which proves that the quaternionic bundle is stably and actually nontrivial.
All Stiefel-Whitney and Pontryagin classes of the total real bundle vanish, and its Euler class lies in the zero group
`H^16`.

The falsifier was a restricted fiber other than two trivial lines plus three standard doublets, a transition outside
the diagonal `SU(2)`, a failed inverse or cocycle, a cellular boundary other than two, a K-theory quotient in which
`x` vanished, a nonzero `c_3`, or a failure of the real stable complement. None occurred. Three mutations remove one
doublet, replace the Euler boundary by one, or replace `3+2t` by the rank-preserving false branching `5+t`; the replay
rejects all three. The result classifies the ordinary bundles under the connected homogeneous action. It makes no
claim about an equivariant extension to the still-unclassified disconnected stabilizer.

## The aligned nullity-twelve pieces have a one-dimensional compact-orbit quotient

The two aligned pieces `V^a_+` and `V^a_-` have split coordinates `(w,0,+-w)`. Under
`z_k=i^popcount(k) z'_k`, put `u_j=z_j` for `1<=j<=7`. The upper coordinates then obey

`z_(8+j)=+- i u_j`,

and the split quadratic form becomes the ordinary complex bilinear form `u dot u`. Thus the two pieces have the
original-coordinate parameterizations

`z=(u,0,+- i u)`, with `u dot u != 0`.

The unit condition is `u^* dot u=1/2`. Write `u=a+i b` with `a,b` real and define

`rho=abs(u dot u)/(u^* dot u)`.

The compact connected symmetry `G_2 x U(1)` preserves `rho`: `G_2` preserves the real Gram matrix of `(a,b)`, while
the phase rotates that ordered pair and multiplies `u dot u` by a unit complex number. Conversely, a phase makes
`u dot u` nonnegative real. The resulting real Gram matrix is diagonal, with eigenvalues

`(u^* dot u)(1+rho)/2` and `(u^* dot u)(1-rho)/2`.

For `0<=rho<1`, the normalized real and imaginary parts form an ordered orthonormal two-frame. The
source-established transitivity `G_2/SU(2)=V_2(R^7)` therefore identifies any two points with the same `rho`. At
`rho=1`, one Gram eigenvalue vanishes and the point is phase-equivalent to a real vector. The endpoint locus is
connected and seven-dimensional; the exact compact orbit below is closed and has the same dimension, so it fills the
endpoint. Consequently each aligned unit section has compact-orbit space

`0<rho<=1`.

The exact compact tangent and bracket calculation gives three orbit types, identically for both signs:

| Locus | Compact orbit dimension | Connected stabilizer algebra | Left nullity |
| --- | ---: | --- | ---: |
| `0<rho<1` | 12 | `su(2)` | 12 |
| `rho=1` | 7 | `su(3)` | 12 |
| closure boundary `rho=0` | 11 | `su(2)+u(1)` | 16 |

The stabilizer identifications use exact centers, derived algebras, and Killing forms. The principal stabilizer has
dimension three, zero center, and negative-definite Killing form. The collinear endpoint stabilizer has dimension
eight, zero center, equals its derived algebra, and has negative-definite Killing form. The null boundary reproduces
the committed four-dimensional `su(2)+u(1)` stabilizer. In particular, the earlier rank-seven computation at the
repository representative of each `V^a` piece measured the `rho=1` endpoint orbit. It did not measure the principal
orbit: the generic compact orbit has codimension one in the thirteen-dimensional unit section, rather than
codimension six. The source-established stabilizer of an ordered two-frame identifies the principal connected group
as `SU(2)`; the exact endpoint calculation identifies its Lie algebra but does not yet certify the endpoint group's
global finite quotient. This stabilizer jump is a finer real stratification inside each complex `H`-orbit.

The same parameterization settles the unit-section topology. After a constant radial rescaling, each sign's unit
section is diffeomorphic to `S^13 minus V_2(R^7)`.

The quadratic argument map

`u -> (u dot u)/abs(u dot u)`

is a fibration over `S^1`; a local square root of the argument gives its local trivializations. Its fiber over `1`
consists of `a perpendicular to b` with `norm(a)>norm(b)` and fixed total norm. It is the open tangent disk bundle of
`S^6`, hence retracts to `S^6`. A circuit around the base changes the chosen square-root phase by `pi`, so the
monodromy is `u -> -u`; on the zero section it is the antipodal map of degree `-1`. The mapping-torus sequence gives

```text
pi_1 = Z,
H^0 = Z, H^1 = Z, H^7 = Z/2,
H^j = 0 otherwise.
```

Alexander duality supplies an independent check: the link has `H_11=Z` and `H_5=Z/2`, which become reduced
cohomology in degrees one and seven of its complement. Every positive-degree cup product vanishes by degree.

The falsifier was an aligned point outside `0<rho<=1`, incomplete Gram data, a tangent rank other than 12, 7, or 11
at the three displayed loci, a different compact stabilizer algebra, a sign-dependent result, a different link
complement topology, or survival of a phase-deletion or trivial-monodromy mutation. None occurred. The exact replay
uses rational cone representatives; positive rescaling to the unit section preserves `rho`, stabilizers, and
nullity. This result identifies the moduli and topology. The following section decomposes the kernel on its compact
orbits; reduced transitions and characteristic classes over the full unit section remain open.

## The aligned fiber representation is constant on the principal interval

Fix the canonical representative `u=e_1+i t e_2`, with `0<t<1`. The connected compact stabilizer is the same
`SU(2)` subgroup of `G_2` for every `t`: it fixes the ordered frame `(e_1,e_2)` pointwise, while a nonzero infinitesimal
phase cannot fix a Gram matrix with unequal eigenvalues. Restricting the compact domain lifts to the complex
rank-six kernel and computing the inverse-Killing Casimir gives

`(ker_R L_y,J) = 2 V_0 + 2 V_1`,

where `V_0` is the trivial complex line and `V_1` is the standard complex doublet of `SU(2)`. The Casimir has
eigenvalue zero with multiplicity two and `3/8` with multiplicity four. Its two spectral projectors have ranks two
and four. The fixed `SU(2)` acts on a smooth constant-rank kernel over the connected interval `0<t<1`, so the integer
isotypic multiplicities are locally constant and hence constant on the entire principal interval. Exact calculations
at `t=1/3,1/2,2/3`, on both signs, check the implementation rather than replace that continuity argument.

At the collinear endpoint `t=0`, the stabilizer algebra jumps to `su(3)`. Its inverse-Killing Casimir is `4/9` on all
six complex dimensions. The exact commutant has dimension two and contains complementary invariant projectors of
rank three. A unique invariant symmetric form has rank six and vanishes on each projected summand, pairing the two
summands nondegenerately. Thus the endpoint representation is

`3 + conjugate(3)`.

The fundamental plus dual representation is faithful on the order-three center of the simply connected group. The
represented connected stabilizer is therefore `SU(3)`, rather than `PSU(3)` or another quotient with the same Lie
algebra. This representation is the complexification of the real tangent isotropy representation on the `S^6`
factor of the collinear locus.

At the closure boundary `t=1`, the same exact calculation recovers the committed nullity-sixteen restriction

`2 V_0 + 3 V_1`.

The passage from a principal aligned orbit to `N_+` or `N_-` consequently adds one standard `SU(2)` doublet to the
kernel. Both aligned signs have identical endpoint, principal, and boundary representations. This comparison is a
statement about the connected stabilizers. It does not determine the action of disconnected stabilizer elements,
the gluing around the quadratic-argument circle, or the characteristic classes of the full aligned unit section.

The falsifier was a stabilizer direction moving the point, escaping the kernel, or failing to commute with `J`; a
different representation at another principal value or on the other sign; an endpoint without complementary
dual rank-three summands; a boundary restriction different from the committed `N_+-` result; or survival of the
moving-generator or perturbed-fiber-action mutations. None occurred. The exact certificates and input digests are
in `aligned-stabilizer-result.json`.

## The open `V` orbit has a three-dimensional compact-orbit quotient

The split-coordinate parameterization of the open `V` orbit is

`(u',mu',v')=(alpha w,m,beta w)`,

where `eta(w)!=0`, `m!=0`, and `(alpha^2-beta^2)eta(w)=m^2`. After the repository's diagonal coordinate change, put
`a_j=i^popcount(j) w_j`. The original-coordinate blocks are

`(u,mu,v)=(alpha a,i m,i beta a)`.

On the chart `u!=0`, write `v=lambda u`, so `lambda=i beta/alpha`. The quadric equation becomes

`mu^2=-(1+lambda^2)(u dot u)`.

The open-orbit conditions `u dot u!=0` and `mu!=0` exclude `lambda=+i,-i`. The chart `u=0` supplies
`lambda=infinity`. Thus the first connected compact-orbit invariant is

`lambda in CP^1 minus {+i,-i}`.

The second invariant is the normalized real Gram discriminant

`rho=abs(u dot u)/(u^* dot u) in (0,1]`,

computed from either nonzero vector block. Both invariants are fixed by `G_2 x U(1)`: the simultaneous real `G_2`
action preserves the collinearity ratio and Gram matrix, while the global phase preserves the ratio and multiplies
the bilinear square by a unit scalar. The replay differentiates both invariants along all fifteen compact generators
at every fixture and obtains zero exactly.

These invariants are complete. For finite `lambda`, the unit condition and the quadric give

`u^* dot u = 1/(1+abs(lambda)^2+rho abs(1+lambda^2))`.

The reciprocal chart gives the same formula at infinity. For two points with equal `(lambda,rho)`, a global phase
first matches their nonzero `mu` coordinates. The quadric then makes their common-line bilinear squares agree, while
the unit formula makes their Hermitian norms agree. Their real-imaginary Gram matrices are therefore identical.
Transitivity of `G_2` on ordered orthonormal two-frames maps the common vectors when `rho<1`; transitivity on the unit
six-sphere does the same at `rho=1`. Hence the connected compact-orbit space is

`(CP^1 minus {+i,-i}) x (0,1]`,

a three-real-dimensional space homotopy equivalent to `C^*`, with fundamental group `Z` and integral cohomology `Z`
in degrees zero and one. These are invariants of the orbit space, not the topology of the full `V` unit section.

Exact tangent and bracket calculations at three projective ratios, including the infinity chart, and three Gram
types give:

| Locus | Compact orbit dimension | Connected stabilizer | Left nullity |
| --- | ---: | --- | ---: |
| `0<rho<1` | 12 | `SU(2)` | 12 |
| `rho=1` | 7 | `SU(3)` | 12 |

The type is independent of `lambda`. The repository representative has `lambda=(5/3)i` and `rho=1`, so its
seven-dimensional orbit is a collinear endpoint rather than a generic orbit. The classification uses the connected
compact group `G_2 x U(1)`; the visible finite kernel symmetries may identify points of the displayed quotient and
remain outside this claim.

The falsifier was a point outside the stated parameter space, incomplete Gram data, nonstationary invariants, a
generic tangent rank or stabilizer different from `12` and `su(2)`, an endpoint result different from `7` and
`su(3)`, dependence on `lambda`, or survival of the phase-deletion or missing-`i` mutations. None occurred. The exact
rows and input digests are in `v-orbit-moduli-result.json`.

## Principal-Pfaffian frames cover `N_+` and `N_-`

Let `sigma` be `+1` or `-1`. The original and split coordinates obey

`z_k = i^(popcount(k)) z'_k`.

On `N_sigma`, the split coordinates satisfy `mu'=0`, `v'=sigma u'`, and `eta(u')=0`. Put

`w_j=z_j=i^(popcount(j))u'_j`, for `1 <= j <= 7`.

Since `popcount(8+j)=1+popcount(j)`, every point of the cone has the exact original-coordinate form

`z=(w,0,sigma i w)`, with `w dot w=0` and `w!=0`.

Conversely, every such `w` gives a point of `N_sigma`. Writing `w=a+i b` with real `a,b` turns `w dot w=0` into

`a dot a=b dot b` and `a dot b=0`.

The squared norm of `z` is `2(a dot a+b dot b)`. The unit section therefore has
`a dot a=b dot b=1/4`; the pair `(2a,2b)` is an ordered orthonormal two-frame in `R^7`. This recovers the
`V_2(R^7)` description directly from the repository's coordinate change.

Let `A_sigma(a,b)=A(z,conjugate(z))`, indexed by the scalar coordinate `0` and the fifteen imaginary coordinates.
The matrix is skew and has rank eight everywhere on `N_sigma`: the nullity-sixteen theorem gives complex kernel
dimension eight under the proved bordered transport. For an eight-element index set `I`, let `J` be its complement
and write, in `I,J` order,

```text
A_sigma = [[B_I, C_I],[-C_I^T,D_I]].
```

Define the chart

`U_I={z in N_sigma: pf(B_I)!=0}`.

On `U_I`, `B_I` is invertible. The rank of the full matrix already equals the rank of `B_I`, so its Schur complement
vanishes:

`D_I+C_I^T B_I^(-1) C_I=0`.

Consequently the columns of

`F_I=[-B_I^(-1) C_I; I_8]`

in `I,J` order satisfy `A_sigma F_I=0`. Their free rows form `I_8`, so they are independent and constitute the entire
complex kernel. The polynomially cleared frame is

`Fhat_I=[-adj(B_I) C_I; det(B_I) I_8]`.

The rational frame's exact degeneracy locus is `pf(B_I)=0`, equivalently
`det(B_I)=pf(B_I)^2=0`. The inequation remains part of the chart: the cleared columns alone carry no claim on that
locus.

The 12,870 choices of `I` cover both cones. A skew matrix of rank eight has a nonzero order-eight principal minor:
choose a nonzero entry to obtain an invertible principal two-block, eliminate that pair by congruence, and repeat on
the residual skew matrix. Four iterations select eight original coordinate indices, and the Schur determinant
identity makes their principal block invertible. Thus some `pf(B_I)` is nonzero at every point of either cone. The
argument supplies coverage of the parameterized real family; the finite fixture sweep is an implementation check,
not the coverage proof.

To recover a frame of the requested real annihilator, write a complex bordered vector as
`xi=(xi_0,...,xi_15)`. The inverse of `psi=conjugate o phi` is

```text
r_j=Re(xi_j),
s_0=-Im(xi_0),
s_j=Im(xi_j) for 1 <= j <= 15.
```

If `f_1,...,f_8` are the columns of `F_I`, then

`psi^-1(f_1), psi^-1(i f_1), ..., psi^-1(f_8), psi^-1(i f_8)`

are sixteen real independent columns in `ker_R L_y`. The transport identity proves annihilation for every point of
every chart. The exact replay also constructs `L_y` from `cd_core` and checks these sixteen columns directly on all
21 coordinate isotropic two-planes `w=e_j+i e_k`, `j<k`, for each sign. At `w=e_1+i e_2`, both signs admit the pivot
`I={0,1,2,3,4,5,8,9}`, with Pfaffian `4` and determinant `16`. A mutation that flips one top-border coefficient makes
the corresponding complex frame fail annihilation.

The falsifier was a parameter outside the stated cone, a point with every order-eight principal Pfaffian zero, a
nonzero-Pfaffian chart whose frame lost rank or escaped either `ker A_sigma` or `ker_R L_y`, a different denominator
locus, or a surviving border mutation. None occurred. This result completes the closed-form-frame deliverable only
for `N_+` and `N_-`; the next section supplies the nullity-twelve pieces.

## Order-ten Pfaffian frames cover every nullity-twelve piece

The same rank-only construction removes the apparent dependence of the frame problem on the unresolved K-orbit
moduli. In split coordinates the five pieces have these parameterizations and open conditions:

| Piece | Parameterization |
| --- | --- |
| B9 | `(u',0,v')`, where `u',v'` are independent, isotropic, and `u' cross v'=0` |
| V | `(alpha w,mu',beta w)`, where `eta(w)!=0`, `mu'!=0`, and `(alpha^2-beta^2)eta(w)=mu'^2` |
| VB | `(alpha n,0,beta n)`, where `n!=0` is null and `alpha^2!=beta^2` |
| `V^a_+` | `(w,0,w)`, where `eta(w)!=0` |
| `V^a_-` | `(w,0,-w)`, where `eta(w)!=0` |

At every point of every row, `A(z,conjugate(z))` has rank ten and complex kernel dimension six. For a ten-element
coordinate set `I` and its six-element complement `J`, write

```text
A = [[B_I,C_I],[-C_I^T,D_I]]
```

in `I,J` order. On `pf(B_I)!=0`, the Schur complement vanishes and

`F_I=[-B_I^(-1)C_I;I_6]`

is a six-column complex frame. Its polynomial clearing is

`Fhat_I=[-adj(B_I)C_I;det(B_I)I_6]`.

The rational frame degenerates exactly on `pf(B_I)=0`; as before,
`det(B_I)=pf(B_I)^2`. The 8,008 ten-element subsets cover each piece because the principal-rank argument applied to a
rank-ten skew matrix produces a nonzero principal order-ten Pfaffian. Realification through `psi^-1` turns the six
complex columns and their `i` multiples into twelve independent columns of `ker_R L_y`. The proof is pointwise in the
ambient `(z,conjugate(z))` coordinates, so it applies over every K-orbit modulus without choosing a quotient coordinate
or assuming that a stabilizer type stays constant.

The replay verifies the relevant closure equations at the five exact representatives from the regularity record,
constructs each bordered matrix independently from `cd_core` signs, derives a principal pivot, checks `A F_I=0`, and
checks all twelve realified columns against `L_y`. The representative certificates are:

| Piece | Pivot indices | Pfaffian | Determinant |
| --- | --- | ---: | ---: |
| B9 | `{0,1,2,3,4,5,7,9,10,12}` | `-104` | `10816` |
| V | `{0,1,2,3,4,5,6,7,8,9}` | `-1350 i` | `-1822500` |
| VB | `{0,1,2,3,4,5,8,9,12,13}` | `-2 i` | `-4` |
| `V^a_+` | `{0,1,2,3,4,5,6,7,8,9}` | `-2 i` | `-4` |
| `V^a_-` | `{0,1,2,3,4,5,6,7,8,9}` | `-2 i` | `-4` |

The falsifier was a nullity-twelve point with every order-ten principal Pfaffian zero, a nonzero-Pfaffian chart whose
frame lost rank or escaped the complex or real kernel, a denominator locus other than the stated Pfaffian zero set, or
a surviving border mutation. None occurred; the mutation fails at one of the five representatives. Together with the
order-eight result, the order-ten construction completes deliverable 2 for all seven high-nullity pieces. The common
atlas does not identify the K-moduli spaces, their stabilizers, or a smaller structure group; those questions remain
live inputs to topology, transitions, and invariants.

## The transport uses the conjugated input

The Pfaffian record proves the real-linear identity

`phi(y x) = A(z, conjugate(z)) conjugate(phi(x))`.

Consequently,

`ker_R L_y = psi^-1(ker_C A(z, conjugate(z)))`

and equivalently

`phi(ker_R L_y) = conjugate(ker_C A(z, conjugate(z)))`.

The formula without the outer input conjugation is false. Exact right-kernel bases of `L_y` refute
`A(z, conjugate(z)) phi(x) = 0` at every one of the seven representatives of nullity at least 12. The real kernel
dimensions are 12 on B9, V, VB, V^a_+, and V^a_-, and 16 on N_+ and N_-; the bordered-matrix complex kernel
dimensions are respectively 6 and 8. Inclusion under `psi` plus equality of these real dimensions proves equality of
the kernels at each representative.

The falsifier was a representative whose exact `L_y` kernel either escaped `ker A` under `psi`, or whose real
nullity differed from twice the complex nullity. No such representative occurred. The control removes the input
conjugation; all seven representatives then fail. The exact rows are in
[`result.json`](result.json), and [`test_kernel_symmetry.py`](test_kernel_symmetry.py) fixes the expected nullities.

## The canonical complex structure is explicit

Let `J = L_(e_16)`. Direct Cayley-Dickson multiplication gives

`J(r, s) = (-conjugate(s), conjugate(r))`,

so `phi(J x) = i phi(x)` and `psi(J x) = -i psi(x)`. The anticommutation `J L_y = -L_y J` therefore makes `J` preserve
every real kernel, while the identification with `ker A` through `psi` carries `J` to multiplication by `-i`. The
identification through `phi` is complex-linear but lands in the coefficientwise conjugate of `ker A`. This conjugate
bundle distinction affects the sign convention for odd Chern classes and must remain explicit in the transition and
invariant deliverables.

The falsifier was any exact kernel vector for which `J x` left the kernel, `phi(J x)` differed from `i phi(x)`, or
`psi(J x)` differed from `-i psi(x)`. The seven representatives supply 92 exact real kernel basis vectors; none
falsified the identities. The control reverses `J` and the phase check fails.

## The constant symmetry algebra is `g_2` plus four central directions

Let `U` be the 30-dimensional doubly pure subspace. A constant infinitesimal symmetry is a triple `(G, H, H')` that
satisfies

`L_(G y) + L_y H = H' L_y`

for every `y` in `U`, with one `H'` independent of `y`. For each basis vector `e_p` of `U`, put
`M_p = H' L_(e_p) - L_(e_p) H`. The matrix `M_p` equals left multiplication by an element of `U` exactly when its
first column has zero entries in rows 0 and 16 and every other column is the signed Cayley-Dickson translate of that
first column. Eliminating `G` this way gives 994 equations for each of the 30 basis vectors: an exact sparse system
with 29,820 rows, 2,048 unknown entries of `(H, H')`, and 115,440 nonzero integer coefficients.

The rational nullspace has dimension 18. Recovering `G e_p = M_p e_0` from every nullspace vector and checking all
30 x 32 x 32 coefficients proves that every recovered triple satisfies the original tensor equation. The computed
space equals the span of these explicit triples:

- Fourteen octonion derivations `(D|_U, D, D)`, where `D` acts in each of the four octonion blocks of A_5.
- Base scaling `(I_U, 0, I)`.
- Domain scaling `(0, I, I)`.
- The vertical complex rotation `(0, J, -J)` for `J = L_(e_16)`.
- The base-phase lift `(J|_U, R, J + R)` for `R = R_(e_16)`.

Exact commutators have rank 14, and the simultaneous commutant inside the 18-dimensional algebra has dimension 4.
Thus the Lie algebra is `g_2` plus a four-dimensional center. The represented identity component is locally
`G_2 x R_+^2 x U(1)^2`; the full finite component group and any global quotient remain to be determined. Projection to
the base has dimension 16. Its kernel has dimension 2 and is spanned by domain scaling and the vertical `J` rotation.
Projection to the domain action `H` has dimension 17.

The split-coordinate boost does not lift. Appending its real 30-dimensional base matrix raises the exact base-span
rank from 16 to 17. The boost therefore lies outside the projection of every constant triple, rather than merely
outside the explicit expected subgroup.

The compact base directions are the fourteen `G_2` directions and the base `J` phase. Their exact tangent ranks on
the real unit sections are:

| Orbit | Unit-section orbit | Cone orbit |
| --- | ---: | ---: |
| B9 | 14 | 15 |
| V | 7 | 8 |
| VB | 11 | 12 |
| V^a_+ | 7 | 8 |
| V^a_- | 7 | 8 |
| N_+ | 11 | 12 |
| N_- | 11 | 12 |

The falsifier was a missing expected direction, an additional nullspace direction, a recovered triple that failed one
multiplication-tensor coefficient, a lifting boost, or a bracket rank different from 14 with center dimension
different from 4. None occurred. The mutation flips one multiplication-table sign; the fourteen `G_2` triples then
fail, so the control rejects the claimed decomposition.

## A visible `S_3 x Z_2` occupies twelve components

Write A_5 as the doubling of the sedenions A_4. The
[exact sedenion automorphism certificate](../sedenion-automorphisms/README.md#the-automorphism-group) proves that
`epsilon` and `psi` generate the lower `S_3`: `epsilon` has order 2, `psi` has order 3, and
`epsilon psi = psi^2 epsilon`. Extend each lower map diagonally to both A_4 halves of A_5. The
[Brown doubling record](../../notes/papers/brown-1967-generalized-cayley-dickson.md#statements-and-hypotheses) supplies
the outer reflection `(a, b) -> (a, -b)`. Each map preserves the doubly pure base, and every algebra automorphism `T`
supplies the finite kernel-pencil triple

`(T|_U, T, T)`,

because `L_(T y) T = T L_y`.

Exact arithmetic over `Q(sqrt(3))`, represented by pairs of rational numbers, checks all 256 sedenion basis products
for each of the six lower elements and all 1,024 A_5 basis products for each of the twelve products of a lower element
with the outer reflection. Every product identity holds. The two factors commute, and the exact `S_3` and order-2
relations hold.

The six lower elements represent six distinct components of the constant kernel symmetry group. Both lower generators
centralize all 18 infinitesimal triples. A lower element in the identity component would therefore lie in its center.
The domain matrices of the connected center lie in

`span{I, J, R, J R}`,

where `J = L_(e_16)` and `R = R_(e_16)`. This algebra has rank 4. Adding the lower identity keeps rank 4, while adding
any of the other five lower matrices raises the rank to 5. All six lower actions have determinant `+1` on the
30-dimensional base. The outer reflection has determinant `-1` there, so its products occupy six further components.
The visible subgroup of the component group is consequently `S_3 x Z_2`, of order 12.

The falsifier was a failed basis product, relation, commutator, center-separation rank, or determinant. None occurred.
The control changes one radical coefficient of `psi`; 244 sedenion basis products and 1,952 A_5 basis products then
fail. This computation does not prove that `S_3 x Z_2` is the entire component group: Brown's automorphism theorem
classifies algebra automorphisms in dimension 32, while the kernel-pencil group also permits triples that are not
algebra automorphisms. An exhaustive normalizer census remains open.

## Scope

The exact solve establishes the identity-component Lie algebra of constant linear kernel-pencil symmetries, its orbit
dimensions, and twelve distinct visible components. The order-eight and order-ten Pfaffian charts establish
closed-form frames on all seven pieces of nullity at least twelve. On each `N_+` and `N_-` unit section it also
identifies the connected compact point stabilizer as `U(2)` and decomposes the complex rank-eight fiber into five
irreducible summands. The `SU(2)` reduction then classifies the ordinary real, complex, and quaternionic bundles on
both `N_+` and `N_-`, including the order-two complex K-class that their zero Chern classes do not detect. The
computation also decomposes the connected stabilizer representations on the principal and endpoint orbits of both
aligned nullity-twelve pieces and identifies the extra doublet acquired at their nullity-sixteen boundaries. It has
also classified the three-dimensional connected compact-orbit quotient of the open `V` orbit. It has not proved that
the visible components exhaust the group and has not classified an equivariant extension under the disconnected
`N_+-` stabilizers, the actual real type of the individual four-plane `xi_R`, the `B9` and `VB` compact-orbit moduli,
the full unit-section topology of `V`, or any non-homogeneous piece's reduced transition functions and bundle
invariants. The compact
symmetry orbits are strictly smaller than the complex rank-stratum orbits outside `N_+-`, so the rank-stratum orbit
labels do not make those kernel bundles homogeneous under the constant symmetry group.

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_kernel_symmetry.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_symmetry.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/kernel_symmetry.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_symmetry.py \
    --out docs/evidence/a5-kernel-bundles/result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_kernel_frames.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_frames.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/kernel_frames.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_frames.py \
    --out docs/evidence/a5-kernel-bundles/frames-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_stabilizer_representation.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/stabilizer_representation.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/stabilizer_representation.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/stabilizer_representation.py \
    --out docs/evidence/a5-kernel-bundles/stabilizer-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_nullity_sixteen_bundle.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/nullity_sixteen_bundle.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/nullity_sixteen_bundle.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/nullity_sixteen_bundle.py \
    --out docs/evidence/a5-kernel-bundles/nullity-sixteen-bundle-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_aligned_orbit_moduli.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/aligned_orbit_moduli.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/aligned_orbit_moduli.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/aligned_orbit_moduli.py \
    --out docs/evidence/a5-kernel-bundles/aligned-orbit-moduli-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_aligned_stabilizer_representation.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/aligned_stabilizer_representation.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/aligned_stabilizer_representation.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/aligned_stabilizer_representation.py \
    --out docs/evidence/a5-kernel-bundles/aligned-stabilizer-result.json
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_v_orbit_moduli.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/v_orbit_moduli.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/v_orbit_moduli.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/v_orbit_moduli.py \
    --out docs/evidence/a5-kernel-bundles/v-orbit-moduli-result.json
```
