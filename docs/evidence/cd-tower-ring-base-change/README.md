# Basis reduction, base change and the order-three map on the commutative-ring tower

Three Rocq files extend the functor `RingTower` of
[cd-tower-ring](../cd-tower-ring/README.md), the Cayley-Dickson pair tower over
a signature that holds the commutative-ring laws alone:

- [CdTowerRingBasis.v](../../../proofs/CdTowerRingBasis.v) reduces an identity
  between linear or bilinear maps to its values on basis vectors;
- [CdTowerRingBaseChange.v](../../../proofs/CdTowerRingBaseChange.v) carries a
  ring homomorphism through every level and transports an identity checked on
  the basis vectors of a source ring to all elements over the target ring;
- [CdTowerOrderThreeMap.v](../../../proofs/CdTowerOrderThreeMap.v) uses both to
  prove that the order-three map psi of the sedenions (Gresnigt, arXiv
  2609.10569, Eq. 61) preserves products over every commutative ring with a
  square root of 3 and an inverse of 2.

The purpose is a route for certificates: a finite computation over the
integers, or over a ring of integers such as Z[sqrt 3], decided by
`vm_compute`, becomes a theorem about all elements over every commutative
ring that receives a homomorphism from it. A symbolic `ring` proof of the
256 basis identities of level 4 took 31 s for one pair on the pinned
toolchain, so the direct route was abandoned.

## Theorems of `RingTowerBasis`, for every level k and every commutative ring

| Theorem | Statement |
| --- | --- |
| `coord_basis` | coordinate j of the basis vector e_i is 1 for i = j and 0 otherwise, for i, j below 2^k |
| `decompose` | x is the sum over i below 2^k of coord_i(x) e_i |
| `linear_ext` | two linear maps that agree on the basis vectors agree everywhere |
| `bilinear_ext` | two bilinear maps that agree on the pairs of basis vectors agree everywhere |
| `mul_bilinear` | the product of level k is bilinear |
| `multiplicative_by_basis` | a linear map f with f(e_i e_j) = f(e_i) f(e_j) for all basis pairs satisfies f(x y) = f(x) f(y) |
| `derivation_by_basis` | a linear map f with the Leibniz rule on basis pairs is a derivation |
| `re_add`, `re_scale`, `re_one`, `re_conj` | the real part is linear, re(1) = 1 and re(conj x) = re(x) |

"Linear" is additive and compatible with `scale`; "basis" is the coordinate
basis of the nested pairs, first half first.

## Theorems of `BaseChange`, for a ring homomorphism h from A to B

`tmap k` applies h to every coordinate of an element of level k.

| Theorem | Statement |
| --- | --- |
| `tmap_zero`, `tmap_one`, `tmap_add`, `tmap_scale`, `tmap_conj`, `tmap_mul` | tmap preserves 0, 1, sums, scalars (through h), conjugates and products |
| `tmap_re`, `tmap_coord`, `tmap_basis` | tmap commutes with the real part and the coordinates and sends e_i to e_i |
| `target_map_tmap` | for a table `images` of 2^k elements over A, the linear map over B with those images (`target_map`) is the transport of the one over A (`source_map`) |
| `derivation_transport` | if `source_map images` satisfies the Leibniz rule on the basis pairs over A, `target_map images` is a derivation over B |
| `scaled_multiplicative_transport` | if `source_map images` satisfies f(e_i) f(e_j) = c f(e_i e_j) on the basis pairs over A, then `target_map images` satisfies f(x) f(y) = h(c) f(x y) for all x, y over B |

`IntegerRing` and `IntegerHom` give the source ring Z and the homomorphism
from Z to any commutative ring (`gen_phiZ` with `gen_phiZ_morph` of Stdlib),
so a table of integer images checked over Z holds over every commutative
ring.

## The order-three map

For octonions A and B write A = re(A) + A' and B = re(B) + B'. With
r3 r3 = 3,

    psi2(A, B) = (3 re(A) - A + r3 B', 3 re(B) - B - r3 A')

is twice the map psi of Eq. 61 in the pair coordinates of level 4.

| Theorem | Statement |
| --- | --- |
| `Root3Integers`, `Root3Hom` | Z[sqrt 3] as pairs of integers is a commutative ring with a square root of 3, and x + y sqrt 3 -> x + y r3 is a homomorphism to every ring with a square root r3 of 3 |
| `images_basis_check` | over Z[sqrt 3], psi2(e_i) psi2(e_j) = 2 psi2(e_i e_j) for the 256 basis pairs of level 4, by `vm_compute` |
| `psi2_mul` | psi2(x) psi2(y) = 2 psi2(x y) for all x, y of level 4 over every commutative ring with a square root of 3 |
| `psi2_conj` | psi2 commutes with conjugation at every level |
| `psi_add`, `psi_scale`, `psi_conj`, `psi_mul` | with 2 inv2 = 1, psi = inv2 psi2 is linear, commutes with conjugation and satisfies psi(x y) = psi(x) psi(y) at level 4 |
| `psi_diagonal_mul` | (a, b) -> (psi a, psi b) preserves the product of level 5 (dimension 32), by `RingTower.diag_mul` |

Instances: `Root3Map` applies `OrderThreeMap` to Z[sqrt 3] itself, and `Mod11`
applies `OrderThreeAutomorphism` to Zmod 11, where 5 5 = 3 and 2 6 = 1, so
both signatures have a model.

Mutation control (run by hand on the pinned toolchain, not part of the
replay): with one sign of `source_psi2` flipped, `images_basis_check` fails at
the basis pair (1, 8).

## Scope

The files prove that psi preserves sums, scalars, products and conjugates.
No Rocq statement here says that psi is a bijection, that its cube is the
identity, or that it generates with the reflection of `cd-tower-ring` the
group S_3 of [sedenion-automorphisms](../sedenion-automorphisms/README.md);
the cube is checked on the printed table by the test below (computed, not
proved). `derivation_transport` is stated and proved, and no derivation table
is passed through it yet: the 14 derivations of the sedenions are the next
input. `psi_diagonal_mul` gives a product-preserving map of level 5; whether
level 5 has further automorphisms is outside this bundle.

## Binding to Eq. 61 and to cd_core

[images.txt](images.txt) is the `vm_compute` output of [images.v](images.v):
the coordinates over Z[sqrt 3] of psi2(e_m) for the 16 basis elements of
level 4. `tests/gororoba_quantum/test_cd_tower_order_three_map.py` requires
that table to equal twice Eq. 61 written out on the basis
(psi(e_i) = -e_i/2 - (sqrt 3 / 2) e_(i+8) and
psi(e_(i+8)) = (sqrt 3 / 2) e_i - e_(i+8)/2 for i = 1..7, with e_0 and e_8
fixed, the matrix `psi()` of
`tests/gororoba_quantum/test_sedenion_automorphism_group.py`), recomputes the
256 identities psi2(e_i) psi2(e_j) = 2 psi2(e_i e_j) with `cd_core.cd_sign`
extended bilinearly to Z[sqrt 3], requires psi2 applied three times to equal
8 on every basis element, and requires the product check to fail on the
table with one sign flipped. The identity of the pair-tower product with
`cd_sign` at integer coefficients is the chain of proofs named in
[cd-tower-ring](../cd-tower-ring/README.md) ("Binding to cd_core"); the
passage to coordinates in Z[sqrt 3] is the bilinear extension, which no Rocq
statement covers.

## Assumptions

[assumptions.txt](assumptions.txt) holds 28 `Print Assumptions` queries on the
Z[sqrt 3] and Zmod 11 instances; every one reads "Closed under the global
context". [kernel.txt](kernel.txt) is the `rocq check` context of the three
libraries: it lists no axiom. No proof introduces an axiom or an `Admitted`.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-tower-ring-base-change/replay_rocq.sh
sha256sum -c docs/evidence/cd-tower-ring-base-change/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles
`CdTwistedProduct.v`, `CdTowerRing.v`, the three files of this bundle,
[assumptions.v](assumptions.v) and [images.v](images.v) in temporary storage
with `-w @all`, fails on any warning or compiler output, runs `rocq check`
over the three libraries, and compares the outputs byte for byte with the
three receipts. `scripts/rocq_kaggle_replay.py --only cd-tower-ring-base-change`
selects the replay and `source_hashes.sha256` binds the three sources and the
receipts. A replay takes about one minute; `CdTowerOrderThreeMap.v` is 22 s of
it.
