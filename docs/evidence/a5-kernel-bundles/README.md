# A_5 kernel bundles: exact transport and symmetry evidence

This evidence directory executes the
[kernel-bundle program](../../design/a5-kernel-bundles-program.md). The current result corrects the complex transport
used to represent the real annihilator kernel, fixes the action of the canonical complex structure, and computes the
constant kernel-pencil symmetry algebra and a visible twelve-component subgroup. An exhaustive component census,
closed-form frames, transition atlas, unit-section topology, and characteristic classes remain open.

Every computation uses rational or Gaussian-rational arithmetic. [`result.json`](result.json) is the output of
[`kernel_symmetry.py`](kernel_symmetry.py) `--out`. The focused contracts and both mutation controls run without random
input.

## Conventions

Write a doubly pure element of A_5 as `y = (p, q)` and put `z = p + i q` in C^15. For `x = (r, s)` in A_5, define

`phi(x) = r + i conjugate(s)` and `psi(x) = conjugate(phi(x))`.

The bordered complex matrix is

`A(z, t) = [[0, -t^T], [t, C_z]]`,

where `C_z` is the imaginary block of left multiplication by `z` in the complexified sedenions. The representative
names `B9`, `V`, `VB`, `Vap`, `Vam`, `Np`, and `Nm` are the open-orbit representatives B9, V, V intersect B9,
V^a_+, V^a_-, N_+, and N_- from the
[regularity record](../a5-strata-regularity/README.md#conventions).

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
dimensions, and twelve distinct visible components. The computation has not proved that those components exhaust the
group and has not classified point-dependent kernel transports, a second anticommuting complex structure, a
closed-form frame, or a bundle invariant. The compact symmetry orbits are strictly smaller than the complex
rank-stratum orbits in general, so the rank-stratum orbit labels do not make the kernel bundles homogeneous under the
constant symmetry group.

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
```
