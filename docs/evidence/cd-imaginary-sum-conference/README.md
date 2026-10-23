# Imaginary-sum conference proof

[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v)
proves, for every Cayley-Dickson dimension n = 2^k, the skew and Gram
identities of right multiplication by the imaginary sum s = e_1 + ... + e_(n-1)
on the recursive pair tower over the integers. In the standard basis that map
is the arc matrix W_n of the
[star-lattice tower](../../notes/topics/cd-star-lattice-tower.md#the-boundary-as-a-paley-matrix),
and the identities are W_n^T = -W_n and W_n^T W_n = (n - 1) I in every
dimension. The remaining conference conditions, a zero diagonal and entries
+-1 off it, follow from the basis products e_a e_b = +-e_(a XOR b), which the
bridge below checks against cd_sign through n = 64; the Rocq theorem for them
is the open step of the
[basis-sign plan](../../state/plans/cd-tower-basis-sign-theorem.json).

| Theorem | Statement, for every k |
| --- | --- |
| `isum_laws` | s (s x) = (x s) s = -(n - 1) x and s (x s) = (s x) s |
| `isum_skew` | <s x, y> = -<x, s y> and <x s, y> = -<x, y s> |
| `isum_conference` | <x s, y s> = (2^k - 1) <x, y> |
| `isum_skew_hadamard` | <x + x s, y + y s> = 2^k <x, y> |

The tower is the recursive pair construction over the integers with the
doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), the inner product
the coordinate dot product. The induction runs on the block forms of left
and right multiplication by s' = (s, 1 + s) that the tower note derives; the
commutation law closes through conj x = 2 re(x) 1 - x and s s = -(n - 1) 1, so
flexibility of the algebra is proved for s rather than assumed. Integer
coefficients keep every theorem free of axioms: all four assumption queries
print `Closed under the global context`, and the kernel check lists no axioms,
type-in-type, unsafe fixpoints or assumed positivity.

The definitions transcribe open_gororoba `proofs/theories/RecursiveCDTower.v`
(the same doubling over the reals). That file is absent at the commit
`ci/open_gororoba.pin` names, and moving the pin would change
`BooleanCochainFiltration.v` under the hash-bound folding_proofs bundle, so
the proof stands alone on Stdlib's ZArith.

## Bridge to cd_sign

The Rocq theorems hold for the tower. [tower_bridge.py](tower_bridge.py)
transcribes the tower's multiplication onto coordinate lists and checks
e_a e_b = cd_sign(n, a, b) e_(a XOR b) for every pair at n = 2 to 64, and that
the tower's (s, 1 + s) recursion yields e_1 + ... + e_(n-1). That step is
exact finite computation, not a Rocq theorem.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-imaginary-sum-conference/replay_rocq.sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/cd-imaginary-sum-conference/tower_bridge.py
sha256sum -c docs/evidence/cd-imaginary-sum-conference/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
source and [assumptions.v](assumptions.v) in temporary storage with
`-w @all`, fails on any warning or compiler output, runs `rocq check`, and
compares the outputs byte for byte with [assumptions.txt](assumptions.txt)
and [kernel.txt](kernel.txt). The ci.yml job rocq-replay runs it on a pull
request that touches `proofs/` or this bundle. `source_hashes.sha256` binds
the source and receipts, so an edit to the proof without new receipts fails
the hash gate. The compile takes about 3 s on the build host.
