# The pair tower as a functor over an ordered domain

[CdTowerDomain.v](../../../proofs/CdTowerDomain.v) states the Cayley-Dickson
pair tower once, as a Rocq functor over an abstract coefficient signature, and
proves on it every theorem that
[CdAnnihilatorSymmetry.v](../../../proofs/CdAnnihilatorSymmetry.v) proves on
the integer tower and
[CdAnnihilatorSymmetryReal.v](../../../proofs/CdAnnihilatorSymmetryReal.v) on
the real tower. The signature `OrderedDomain` names the facts those proofs
use of their coefficients and nothing else: a commutative ring (its
`ring_theory`, so the ring tactic closes every coordinate identity), a
relation `le` with `0 <= a a`, nonnegative terms adding to a nonnegative sum
and a vanishing sum of nonnegative terms vanishing termwise, `a b = 0` forcing
a factor to vanish, and `1 <> 0`. `ZDomain` and `RDomain` prove it from
Stdlib (`Zth`, `Z.square_nonneg`, `Zmult_integral`; `RTheory`,
`Rmult_le_pos`, `Rplus_le_le_0_compat`, `Rplus_eq_0_l`, `Rmult_integral`),
and `ZTower` and `RTower` are the two instances. `OrderedField` adds an
inverse of every nonzero element; `CdTowerField` proves the affine inverse
family on it and `RField` instantiates it at R.
[CdTowerDomainZ.v](../../../proofs/CdTowerDomainZ.v) and
[CdTowerDomainR.v](../../../proofs/CdTowerDomainR.v) are the bridges: each
identifies the instance's operations with the ones of
[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v) and
[CdTowerReal.v](../../../proofs/CdTowerReal.v) by induction on the level and
restates the functor's theorems in those files' own vocabulary. The plan
record is `docs/state/plans/cd-tower-ordered-domain-rocq.json`.

| Theorem of `CdTower` | Statement, for every level k | Source theorem |
| --- | --- | --- |
| `norm_mul`, `adjoint` | x conj(x) = <x, x> 1 and the adjoints of L_x and R_y (Lemmas 3.6 and 3.4 of math/0511691) | both files |
| `re_commutator`, `re_associator` | re(x y) = re(y x), re((x y) z) = re(x (y z)) (Lemmas 2.6, 2.8) | real file |
| `flex_sum_zero`, `flexible` | x (y z) - (x y) z + z (y x) - (z y) x = 0 and (x y) x = x (y x) (Corollary 2.9) | real file |
| `conj_mul_left`, `conj_mul_right`, `lemma_9_2` | x (conj(x) y) = conj(x) (x y), its mirror, and the equivalence of x y = 0, conj(x) y = 0, x conj(y) = 0 (Lemma 9.2) | real file |
| `kernel_equality` | a z = 0 exactly when z a = 0 (Corollary 9.3) | both files |
| `purity_left`, `purity_right` | a z = 0 with a, z nonzero implies re(a) = re(z) = 0 (Lemma 9.4) | both files |
| `lemma_9_5`, `annihilator_orthogonal` | at level k + 1 a zero divisor and the annihilator of a nonzero element are orthogonal to 1 and to the adjoined unit (0, 1) (Lemma 9.5) | real file |
| `right_inverse_affine`, `direct_finiteness` | a (<a, a> b - conj(a)) = 0 and a b = 1 implies b a = 1 | integer file (the integer-cleared family) |
| `CdTowerField.right_inverse_form` | a b = 1 implies b = conj(a)/<a, a> + w with a w = 0, over an ordered field | real file (the affine family) |

The bridge theorems `ZBridge.kernel_equality`, `ZBridge.direct_finiteness`,
`ZBridge.flexible`, `ZBridge.lemma_9_5` and `ZBridge.purity_left` are the
integer file's statements word for word, with Lemma 9.5 and flexibility new
on the integer tower; `RBridge` restates the same five on the real tower and
`RFieldBridge.right_inverse_form` restates the real file's affine family.

The proofs are those of the two files with the coefficient-specific steps
replaced by the signature: `lra` and `nia` become the order axioms
(`dot_self_nonneg`, `dot_self_zero`), the cancellation of a nonzero scalar
reads the norm of r x as r r <x, x> and applies `mul_integral`
(`scale_zero_factor`), 2 and -1 are the named constants `two` and `neg_one`,
nonzero because 1 = 1 1 is nonnegative and 1 <> 0, and the coordinate tactic
`vec` unfolds them before `ring`. `lia` remains only on the nat indices of
`ext`. No proof decides equality on the coefficient domain, so neither
`Z.eq_dec` nor `Req_dec` enters. No step uses associativity, alternativity
or multiplicativity of the norm, which fail from level 4 on.

Every theorem rests on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)) for the two bridge libraries together: the
Calculus of Inductive Constructions with a predicative Set and no rewrite
rules; the imported-library context names the four real-construction and
classical axioms of Stdlib's reals, as the real bundles do. The nine queries
of [assumptions_z.txt](assumptions_z.txt), on `ZTower` and `ZBridge`, each
read "Closed under the global context": the integer statements hold without
an axiom. The ten queries of [assumptions_r.txt](assumptions_r.txt), on
`RTower`, `RBridge` and `RFieldBridge`, each list exactly
`ClassicalDedekindReals.sig_forall_dec` and
`FunctionalExtensionality.functional_extensionality_dep`, the two axioms of
Stdlib's construction of the reals. The queries live in two files because the
integer and real tower files each create rewrite databases named `coord`,
`alg` and `dotlin`, and requiring both in one file warns; the functor's own
databases carry the prefix `domain_`.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-tower-domain/replay_rocq.sh
sha256sum -c docs/evidence/cd-tower-domain/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
integer and real tower files, the functor, both bridges and both assumption
files in temporary storage with `-w @all`, fails on any warning or compiler
output, runs `rocq check` over both bridge libraries, and compares the
outputs byte for byte with the three receipts. The ci.yml job rocq-replay
runs it beside the other tower bundles, `scripts/rocq_kaggle_replay.py
--only cd-tower-domain` selects it, and gate sources-415 lints the script.
`source_hashes.sha256` binds the three proof sources and the receipts, so the
ledger test fails on an edit to a source without new receipts. The replay
takes about 80 s on the build host, most of it the two tower files it
recompiles.
