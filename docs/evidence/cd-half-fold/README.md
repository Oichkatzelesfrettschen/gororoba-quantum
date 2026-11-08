# Half-operand fold of the Cayley-Dickson kernel

[CdHalfFold.v](../../../proofs/CdHalfFold.v) proves that, in the pair tower
at level k + 1 with the doubling (a, b)(c, d) = (ac - conj(d) b,
da + b conj(c)), left multiplication by an operand that lives in one half has
a kernel that is the product of two copies of the kernel one level down, so
its nullity is twice that of the level below. This is the low-pair and
high-pair doubling of |S+| in
[singular_sector_dynamics.md](../../notes/singular_sector_dynamics.md), whose
checker `scripts/singular_sector_dynamics.py` verifies it through D = 512.

| Theorem | Statement, for every k and all a, b, c, d of the level-k tower |
| --- | --- |
| `first_half` | (a, 0)(c, d) = 0 exactly when a c = 0 and a d = 0 |
| `second_half` | (0, b)(c, d) = 0 exactly when b c = 0 and b d = 0 |

The proofs are generic over the ordered coefficient domain of
[CdTowerDomain.v](../../../proofs/CdTowerDomain.v): the functor `HalfFold`
proves both folds on `CdTower D`, and `ZHalf` and `RHalf` instantiate it at
the integers and the Stdlib reals. `RealHalfFold` restates both theorems in
the vocabulary of [CdTowerReal.v](../../../proofs/CdTowerReal.v) through the
operation identities of `CdTowerDomainR.RBridge`. The only new reasoning is
the componentwise product of a half operand, (a, 0)(c, d) = (ac, da) and
(0, b)(c, d) = (-conj(d) b, b conj(c)) (`mul_low`, `mul_high`). The first fold
turns d a = 0 into a d = 0 by `kernel_equality` (Corollary 9.3 of
[math-0511691.md](../../notes/math-0511691.md)); the second removes the two
conjugations by `lemma_9_2` (Lemma 9.2) and then applies `kernel_equality`.
No step uses associativity, alternativity or multiplicativity of the norm.

`RealHalfFoldDimension` turns the two folds into the dimension statement. A
subspace W has dimension n (`has_dim`) when n vectors of W are linearly
independent (`independent`) and span W (`spans`); `product_dimension` shows
that a basis of m vectors of W1 and one of n vectors of W2 give a basis of
m + n vectors of the product subspace {(c, d) : c in W1, d in W2} at the next
level, with the vectors (v, 0) and (0, v') as the basis. With `ker_left`, the
kernel of left multiplication, the folds give:

| Theorem | Statement, for every k, a, b and n |
| --- | --- |
| `half_fold_dimension_low` | ker L_a has a basis of n vectors at level k, so ker L_(a, 0) has a basis of n + n vectors at level k + 1 |
| `half_fold_dimension_high` | the same for ker L_(0, b) |
| `half_fold_rank` | n <= 2^k gives 2^(k + 1) - 2n = 2 (2^k - n), the rank as the dimension minus the nullity |

The existence of a basis of every subspace of R^(2^k) and the invariance of
the basis size are the standard finite-dimensional facts that enter through
the hypothesis of the first two theorems, and the rank is defined as the
dimension minus the nullity; none of these is re-proved here.

The cross-operand fold stays an open target. With h = 2^k, k >= 3,
0 < i < h, 0 <= j < h and t = +1 or -1, n_2h(e_i + t e_(h+j)) = 0 when j = 0
or j = i, and otherwise n_2h(e_i + t e_(h+j)) = h - 4 - 2 n_h(e_i + t e_j).
The case i = 0, the scalar-plus-high operand, is no instance of the rule; its
value n_32 = 0 at h = 16 is recorded in
[a5-w8-twisted-product](../a5-w8-twisted-product/README.md). The header of
`CdHalfFold.v` records the statement with the paper derivation in
`singular_sector_dynamics.md` and its checker.

## Assumptions

[assumptions.txt](assumptions.txt) holds ten `Print Assumptions` queries:
`RealHalfFold.first_half`, `RealHalfFold.second_half`, `RHalf.first_half` and
`RHalf.second_half` each list exactly
`ClassicalDedekindReals.sig_forall_dec` and
`FunctionalExtensionality.functional_extensionality_dep`, the two axioms of
Stdlib's construction of the reals; `ZHalf.first_half` and
`ZHalf.second_half` read "Closed under the global context". `RealHalfFoldDimension.product_dimension`,
`half_fold_dimension_low` and `half_fold_dimension_high` list the same two
axioms, and `half_fold_rank` reads "Closed under the global context". The
imported-library kernel context in [kernel.txt](kernel.txt) is byte-identical
to that of the other real tower bundles. No proof introduces an axiom or an
`Admitted`.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-half-fold/replay_rocq.sh
sha256sum -c docs/evidence/cd-half-fold/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
real tower, the functor, the real bridge, this proof and
[assumptions.v](assumptions.v) in temporary storage with `-w @all`, fails on
any warning or compiler output, runs `rocq check`, and compares the outputs
byte for byte with the two receipts. The integer tower file stays out of the
compile because the integer and real tower files each create rewrite
databases of the same names. `scripts/rocq_kaggle_replay.py --only
cd-half-fold` selects the replay and `source_hashes.sha256` binds the
sources and receipts. The replay takes about one minute.
