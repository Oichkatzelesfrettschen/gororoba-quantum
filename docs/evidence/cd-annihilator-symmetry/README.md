# Annihilator-symmetry proof

[CdAnnihilatorSymmetry.v](../../../proofs/CdAnnihilatorSymmetry.v) proves,
for every Cayley-Dickson dimension n = 2^k, that left and right annihilators
coincide on the integer pair tower that
[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v)
defines: a z = 0 exactly when z a = 0, for every pair of elements with
integer coordinates. It requires that file unchanged and adds no definition
to it. The statement is Corollary 9.3 of Biss, Dugger and Isaksen
([math-0511691.md](../../notes/math-0511691.md)), and the proof is the one
written in
[cd-one-sided-inverses.md](../../notes/topics/cd-one-sided-inverses.md):
the norm law x conj(x) = conj(x) x = <x, x> 1 (Lemma 2), the trace-form
adjoint identities <x y, z> = <y, conj(x) z> = <x, z conj(y)> (Lemma 3, the
paper's Lemma 3.4), and the purity of annihilators (Lemma 4, the paper's
Lemmas 9.4 and 9.5). The direct-finiteness corollary a b = 1 implies
b a = 1 follows, with the right inverses of a described by
<a, a> b = conj(a) + w, a w = 0, the integer-cleared form of the note's
affine family conj(a)/<a, a> + ker L_a.

| Theorem | Statement, for every k and all x, y, z, a, b of the level-k tower |
| --- | --- |
| `dot_self_zero` | <x, x> = 0 implies x = 0 |
| `norm_mul` | x conj(x) = <x, x> 1 and conj(x) x = <x, x> 1 |
| `adjoint` | <x y, z> = <y, conj(x) z> and <x y, z> = <x, z conj(y)> |
| `dot_mul_self_r` | <a z, z> = <z, z> re(a) |
| `dot_mul_self_l` | <a z, a> = <a, a> re(z) |
| `purity_left` | a z = 0 with a != 0 and z != 0 implies re(a) = 0 and re(z) = 0 |
| `purity_right` | z a = 0 with a != 0 and z != 0 implies re(a) = 0 and re(z) = 0 |
| `kernel_swap` | a z = 0 implies z a = 0 |
| `kernel_equality` | a z = 0 exactly when z a = 0 |
| `right_inverse_affine` | a b = 1 implies a (<a, a> b - conj(a)) = 0 |
| `direct_finiteness` | a b = 1 implies b a = 1 |

The norm and adjoint laws run by induction on the doubling. Each step
expands the pair product, moves the scalars and conjugations out through the
`alg` and `dotlin` rewrite databases of the conference proof, and matches the
four terms of each side through the level-j identities in the order the note
lists them; the coordinate extensionality lemma `ext` then closes each vector
identity with `ring`. The purity lemma is the two products above: a z = 0
makes <z, z> re(a) and <a, a> re(z) vanish, and <x, x> is a sum of squares,
so each real part is zero once its factor's partner is nonzero. The theorem
decides the zero cases of a and z through <x, x> = 0, and for pure a and z
reads z a = (-z)(-a) = conj(z) conj(a) = conj(a z) = 0 coordinate by
coordinate. The corollary applies the theorem to <a, a> b - conj(a), which
a annihilates, and cancels the nonzero integer <a, a>.

No step uses associativity, alternativity or multiplicativity of the norm,
which fail from k = 4 on, and no step divides: every cancellation is of a
nonzero integer factor <x, x>. The integer coefficients bound the statement.
Scaling by a common denominator carries it to every element with rational
coordinates, since a z = 0 and a b = 1 are homogeneous in each factor. The
real-coefficient theorem of the note rests on its written argument; the
script follows that argument step for step and would prove it over any
ordered field once the tower is restated over one.

Every theorem rests on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)): the Calculus of Inductive Constructions with a
predicative Set and no rewrite rules, with the equality types `eq`,
`eq_true` and `eq_dep` and Btauto's `null` typed under the default rule that
inductive indices do not raise the universe level. Beyond that kernel, the
proofs use only definitions and proved lemmas of Corelib and Stdlib 9.2.0:
the integers and their ring structure (ZArith, through `ring`, `lia` and
`nia`) and the conference proof's own lemmas. Each of the eleven assumption
queries prints `Closed under the global context`
([assumptions.txt](assumptions.txt)), so no classical, extensionality or
choice principle enters any proof term.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-annihilator-symmetry/replay_rocq.sh
sha256sum -c docs/evidence/cd-annihilator-symmetry/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
conference proof, this proof and [assumptions.v](assumptions.v) in temporary
storage with `-w @all`, fails on any warning or compiler output, runs
`rocq check`, and compares the outputs byte for byte with
[assumptions.txt](assumptions.txt) and [kernel.txt](kernel.txt). The ci.yml
job rocq-replay runs it beside the other tower bundles, and
`scripts/rocq_kaggle_replay.py --only cd-annihilator-symmetry` selects it.
`source_hashes.sha256` binds both proof sources and the receipts, so the
ledger test fails on an edit to either source without new receipts. The
replay takes about 23 s on the build host.
