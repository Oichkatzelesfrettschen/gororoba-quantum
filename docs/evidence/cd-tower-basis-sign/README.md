# Tower basis-sign proof

[CdTowerBasisSign.v](../../../proofs/CdTowerBasisSign.v) proves, for every
Cayley-Dickson dimension n = 2^k, the standard-basis multiplication table of
the integer pair tower that
[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v)
defines and the [conference bundle](../cd-imaginary-sum-conference/README.md)
replays. It requires that file unchanged and adds no definition to it. Basis
units multiply as e_a e_b = sigma_k(a, b) e_(a XOR b), with sigma_k the while
loop of `cd_core.cd_sign` unrolled one doubling per level, so the arc matrix
W_n of right multiplication by the imaginary sum s carries sigma_k(a, b) at
row a XOR b, column a for every b != 0 and 0 on its diagonal. With
`isum_conference` of the conference bundle, W_n is a skew conference matrix
in the standard basis in every dimension. The cochain recursion of Albuquerque
and Majid, Corollary 4.3 (the
[convention replay](../albuquerque-majid-convention/README.md)), gives
(-1)^f(a, b) = sigma_k(b, a) in every dimension, the transposed convention.

| Theorem | Statement, for every k and a, b, c < 2^k |
| --- | --- |
| `cd_sign_loop_sigma` | the cd_sign loop with accumulated sign t returns t sigma_k(p, q) |
| `basis_mul` | e_a e_b = sigma_k(a, b) e_(a XOR b) |
| `basis_mul_coord` | (e_a y)_c = sigma_k(a, a XOR c) y_(a XOR c) and (y e_b)_c = sigma_k(c XOR b, b) y_(c XOR b) |
| `arc_entry` | (e_a s)_(a XOR b) = sigma_k(a, b) for b != 0 |
| `arc_diagonal` | (e_a s)_a = 0 |
| `am_complex` | the Corollary 4.3 exponent at k = 1 is f(x, y) = xy |
| `am_sign` | (-1)^f_k(a, b) = sigma_k(b, a) |

The induction runs on the doubling halves: index bit k - 1 selects the half,
and the index facts reduce to `Nat.lxor` identities that `btauto` closes bit
by bit. Conjugation fixes e_0 and negates every other unit, and sigma_k(0, q)
= sigma_k(p, 0) = 1. The Corollary 4.3 exponent starts from the trivial group,
so level 1 reproduces the paper's f(x, y) = xy, and its diagonal
f(x, x) = [x != 0] carries the e_x e_x = -1 case of the induction.

Every theorem rests on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)): the Calculus of Inductive Constructions with a
predicative Set and no rewrite rules, with the equality types `eq`, `eq_true`
and `eq_dep` and Btauto's `null` typed under the default rule that inductive
indices do not raise the universe level. Beyond that kernel, the proofs use
only definitions and proved lemmas of Corelib and Stdlib 9.2.0: the integers
and their ring structure (ZArith, through `ring` and `lia`), the natural-number
bitwise operations `Nat.lxor`, `Nat.testbit` and `Nat.log2` with their
Stdlib lemmas, and Btauto's Boolean normalization. Each of the seven
assumption queries prints `Closed under the global context`, meaning the
proof term reaches the kernel through those definitions alone, with every
classical, extensionality or choice principle absent. The integer
coefficients are what make that possible, since the real-number Stdlib
carries axioms. The remaining trust is in the transcriptions: `sigma` and
`cd_sign_loop` against the Python loop of cd_core.cd_sign, which the bridge
below checks through n = 64, the tower doubling against the algebra, and
`am_exponent` against the printed Corollary 4.3.

## Bridge to cd_sign

`sigma` and `cd_sign_loop` are Rocq transcriptions of the Python loop, and
`cd_sign_loop_sigma` proves them equal. The conference bundle's
[tower_bridge.py](../cd-imaginary-sum-conference/tower_bridge.py) links the
transcription to the Python source: it mirrors `sigma` branch for branch and
requires sigma_k(a, b) = cd_sign(2^k, a, b) on all 5,460 pairs at n = 2 to 64,
with a negative control that negates each of the four branches in turn and
requires a disagreement at every n >= 4. The bridge is exact finite
computation; the Rocq side holds for every k.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-tower-basis-sign/replay_rocq.sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/cd-imaginary-sum-conference/tower_bridge.py
sha256sum -c docs/evidence/cd-tower-basis-sign/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles both
proof sources and [assumptions.v](assumptions.v) in temporary storage with
`-w @all`, fails on any warning or compiler output, runs `rocq check`, and
compares the outputs byte for byte with [assumptions.txt](assumptions.txt)
and [kernel.txt](kernel.txt). The ci.yml job rocq-replay runs it beside the
conference bundle. `source_hashes.sha256` binds both proof sources and the
receipts, so the gate fails on an edit to either source without new receipts.
The replay takes about 26 s on the build host.
