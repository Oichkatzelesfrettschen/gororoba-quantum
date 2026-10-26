# A_5 kernel bundles: exact transport, symmetry, and Pfaffian frames

This evidence directory executes the
[kernel-bundle program](../../design/a5-kernel-bundles-program.md). The current result corrects the complex transport
used to represent the real annihilator kernel, fixes the action of the canonical complex structure, computes the
constant kernel-pencil symmetry algebra and a visible twelve-component subgroup, and gives an exact finite family of
rational kernel frames covering `N_+` and `N_-`. An exhaustive component census, frames on the five nullity-twelve
pieces, a transition atlas, the remaining unit-section topology, and characteristic classes remain open.

Every computation uses rational or Gaussian-rational arithmetic. [`result.json`](result.json) is the output of
[`kernel_symmetry.py`](kernel_symmetry.py) `--out`. [`frames-result.json`](frames-result.json) is the output of
[`kernel_frames.py`](kernel_frames.py) `--out`. The focused contracts and mutation controls run without random input.

## Conventions

Write a doubly pure element of A_5 as `y = (p, q)` and put `z = p + i q` in C^15. For `x = (r, s)` in A_5, define

`phi(x) = r + i conjugate(s)` and `psi(x) = conjugate(phi(x))`.

The bordered complex matrix is

`A(z, t) = [[0, -t^T], [t, C_z]]`,

where `C_z` is the imaginary block of left multiplication by `z` in the complexified sedenions. The representative
names `B9`, `V`, `VB`, `Vap`, `Vam`, `Np`, and `Nm` are the open-orbit representatives B9, V, V intersect B9,
V^a_+, V^a_-, N_+, and N_- from the
[regularity record](../a5-strata-regularity/README.md#conventions).

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
for `N_+` and `N_-`; it makes no transition, characteristic-class, or nullity-twelve-piece claim.

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
dimensions, and twelve distinct visible components. The Pfaffian charts establish closed-form frames on `N_+` and
`N_-`. The computation has not proved that the visible components exhaust the group and has not classified
point-dependent kernel transports, a second anticommuting complex structure, frames on the nullity-twelve pieces, or
a bundle invariant. The compact symmetry orbits are strictly smaller than the complex rank-stratum orbits in general,
so the rank-stratum orbit labels do not make those kernel bundles homogeneous under the constant symmetry group.

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
```
