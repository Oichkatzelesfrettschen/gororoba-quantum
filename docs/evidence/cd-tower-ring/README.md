# The pair tower over a commutative ring and the scope of the kernel swap

[CdTowerRing.v](../../../proofs/CdTowerRing.v) states the Cayley-Dickson pair
tower as a Rocq functor over a signature that holds the commutative-ring laws
alone, `CommutativeRing`, with the doubling
(a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) of
[CdTowerDomain.v](../../../proofs/CdTowerDomain.v) and
`gororoba_quantum/cd_core.py`. The ordered-domain functor of
[cd-tower-domain](../cd-tower-domain/README.md) proves Corollary 9.3 of Biss,
Dugger and Isaksen (math/0511691), a z = 0 exactly when z a = 0, from the
order of its coefficients; Q(i), the complex numbers and the prime fields have
no such order. This bundle proves what holds over every commutative ring and
shows that the swap itself holds only when 2 = 0 once the ring contains a
square root of -1.

## Theorems of `RingTower`, for every level k and every commutative ring

| Theorem | Statement |
| --- | --- |
| `conj_mul`, `conj_conj`, `conj_add`, `conj_scale` | conjugation is an additive involution that commutes with scalars and reverses products |
| `kernel_conj` | a z = 0 exactly when conj(z) conj(a) = 0, so conjugation maps ker L_a onto ker R_(conj a) bijectively |
| `re_zero_pure` | re(a) = 0 implies conj(a) = -a (`pure`) |
| `pure_kernel_conj`, `pure_kernel_conj_right` | for pure a, a z = 0 exactly when conj(z) a = 0, and w a = 0 exactly when a conj(w) = 0: ker R_a = conj(ker L_a) |
| `two_zero_commutative` | when 2 = 0, x y = y x |
| `reflect_mul` | at level k + 1 the map (a, b) -> (a, -b) satisfies reflect(x y) = reflect(x) reflect(y) |
| `reflect_add`, `reflect_scale`, `reflect_one`, `reflect_conj`, `reflect_involutive` | the reflection is linear, fixes 1, commutes with conjugation and is its own inverse |
| `reflect_kernel` | x z = 0 exactly when reflect(x) reflect(z) = 0, so the reflection maps ker L_x onto ker L_(reflect x) bijectively |
| `lift_mul`, `lift_conj`, `lift_scale`, `lift_zero_inv` | x -> (x, 0), iterated, embeds level j in level k + j as a subalgebra closed under conjugation |

`kernel_conj` is the anti-automorphism law read on a vanishing product. The
map conj is linear and bijective, so ker L_a and ker R_(conj a) are isomorphic
modules; over a field their dimensions agree, and for pure a the left and
right nullities of a agree. `reflect_mul` unfolds one doubling step and uses
the scalar laws of the product; it needs no induction on the level.

## Theorems of `RingTowerI`, over a commutative ring with i i = -1

At level 2 write a nested pair ((x0, x1), (x2, x3)) as
x0 + x1 e_1 + x2 e_2 + x3 e_3. `nilpotent2` is a = e_1 + i e_2 and `witness2`
is w = -1 - i e_3.

| Theorem | Statement |
| --- | --- |
| `nilpotent2_pure`, `nilpotent2_square` | a is pure and a a = 0 |
| `witness2_product` | a e_1 = w |
| `nilpotent_witness`, `witness_nilpotent` | at level k + 2, a w = 0 and w a = -2 a for the lifted pair |
| `kernel_swap_witness` | when 2 differs from 0: a is pure, a w = 0 and w a differs from 0 |
| `pure_kernel_swap_two_zero` | the swap a z = 0 -> z a = 0 for pure a at level k + 2 implies 2 = 0 |
| `kernel_swap_iff_two_zero` | the swap holds at level k + 2 exactly when 2 = 0 |

The element a has norm 1 + i i = 0, which an ordered domain excludes through
`dot_self_zero` of `CdTowerDomain.v`. The instances `GaussianTower` (the
Gaussian integers Z[i] as pairs of integers, a subring of Q(i)) and
`Mod5Tower` (Zmod 5 with i = 2, the `Zmod5` module of
[CdTwistedProduct.v](../../../proofs/CdTwistedProduct.v)) satisfy the
signature with 2 different from 0, and `gaussian_kernel_swap_fails` and
`mod5_kernel_swap_fails` state the failure at every level k + 2, level 5
(dimension 32) included. Over Q(i) or modulo an odd prime p = 1 (mod 4) the
general law for pure a is therefore ker R_a = conj(ker L_a), and
ker R_a = ker L_a is a property of particular operands.

## The ordered-domain tower is the same tower

[CdTowerRingDomain.v](../../../proofs/CdTowerRingDomain.v) applies `RingTower`
to `ZDomain` and `RDomain` and proves each operation equal to the operation of
`ZTower` and `RTower` by reflexivity (`cd_eq`, `zero_eq`, `one_eq`, `add_eq`,
`scale_eq`, `conjugate_eq`, `mul_eq`, `re_eq`), so the refuted swap and
Corollary 9.3 concern one product and differ in their coefficients alone.
`ZRingBridge` and `RRingBridge` restate `reflect_mul`, `reflect_involutive`,
`reflect_kernel` and `pure_kernel_conj` in the vocabulary of `ZTower` and
`RTower`.

## Binding to cd_core

`tests/gororoba_quantum/test_cd_tower_ring_witness.py` reads `nilpotent2` and
`witness2` from the proof source, places them at coordinates 0 to 3 and checks
a e_1 = w, a a = 0, a w = 0 and w a = -2 a with `cd_core.cd_sign` extended
bilinearly to Gaussian-integer coordinates in dimensions 4, 8, 16 and 32. Its
controls: with i replaced by 1 the product a (a e_1) differs from 0, and the
real sedenion pair (e_3 + e_10)(e_6 - e_15) vanishes in both orders.

## Scope

No statement here concerns a dimension count over a general ring, the
nullity values of the A_5 strata, or an ideal. The exchange of the orbits
X+ and X-, and N+ and N-, by the reflection is the computed record of
[a5-exceptional-fibers/structure](../a5-exceptional-fibers/structure/README.md);
`reflect_mul` proves the automorphism that record checks on basis pairs at
levels 3, 4 and 5.

## Assumptions

[assumptions.txt](assumptions.txt) holds 34 `Print Assumptions` queries. The
24 on `GaussianTower` and `Mod5Tower` and the five on `ZRingBridge` read
"Closed under the global context". Of the five on `RRingBridge`, `mul_eq` and
`conjugate_eq` list `ClassicalDedekindReals.sig_forall_dec`, and
`reflect_mul`, `reflect_kernel` and `pure_kernel_conj` list it with
`FunctionalExtensionality.functional_extensionality_dep`: the two axioms of
Stdlib's construction of the reals. [kernel.txt](kernel.txt) is the
`rocq check` context of the two libraries together; `CdTowerRingDomain`
imports the real library through `CdTowerDomain`, so the context names the
four real-construction and classical axioms that the real bundles name, and
the per-theorem lists above are the dependencies of each statement. No proof
introduces an axiom or an `Admitted`.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-tower-ring/replay_rocq.sh
sha256sum -c docs/evidence/cd-tower-ring/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles
`CdTwistedProduct.v`, `CdTowerRing.v`, `CdTowerDomain.v`,
`CdTowerRingDomain.v` and [assumptions.v](assumptions.v) in temporary storage
with `-w @all`, fails on any warning or compiler output, runs `rocq check`
over the two libraries, and compares the outputs byte for byte with the two
receipts. `scripts/rocq_kaggle_replay.py --only cd-tower-ring` selects the
replay and `source_hashes.sha256` binds the two sources and the receipts. One
replay measured 74 s; `rocq check` over the imported real library accounts
for most of it.
