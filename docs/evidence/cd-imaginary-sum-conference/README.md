# Imaginary-sum conference proof

[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v)
proves, for every Cayley-Dickson dimension n = 2^k, the skew and Gram
identities of right multiplication by the imaginary sum s = e_1 + ... + e_(n-1)
on the recursive pair tower over the integers. In the standard basis that map
is the arc matrix W_n of the
[star-lattice tower](../../notes/topics/cd-star-lattice-tower.md#the-boundary-as-a-paley-matrix),
and the identities are W_n^T = -W_n and W_n^T W_n = (n - 1) I in every
dimension. In the standard basis e_a, a < 2^k, the tower multiplies basis
units as e_a e_b = sigma_k(a, b) e_(a XOR b), with sigma_k the loop of
cd_core.cd_sign unrolled one doubling per level, so W_n carries sigma_k(a, b)
at row a XOR b, column a for every b != 0 and 0 on its diagonal. The cochain
recursion of Albuquerque and Majid, Corollary 4.3 (the
[convention replay](../albuquerque-majid-convention/README.md)), gives
(-1)^f(a, b) = sigma_k(b, a) in every dimension, the transposed convention.

| Theorem | Statement, for every k |
| --- | --- |
| `isum_laws` | s (s x) = (x s) s = -(n - 1) x and s (x s) = (s x) s |
| `isum_skew` | <s x, y> = -<x, s y> and <x s, y> = -<x, y s> |
| `isum_conference` | <x s, y s> = (2^k - 1) <x, y> |
| `isum_skew_hadamard` | <x + x s, y + y s> = 2^k <x, y> |
| `cd_sign_loop_sigma` | the cd_sign loop with accumulated sign t returns t sigma_k(p, q) |
| `basis_mul` | e_a e_b = sigma_k(a, b) e_(a XOR b) for a, b < 2^k |
| `basis_mul_coord` | (e_a y)_c = sigma_k(a, a XOR c) y_(a XOR c) and (y e_b)_c = sigma_k(c XOR b, b) y_(c XOR b) |
| `arc_entry` | (e_a s)_(a XOR b) = sigma_k(a, b) for b != 0 |
| `arc_diagonal` | (e_a s)_a = 0 |
| `am_complex` | the Corollary 4.3 exponent at k = 1 is f(x, y) = xy |
| `am_sign` | (-1)^f_k(a, b) = sigma_k(b, a) for a, b < 2^k |

The tower is the recursive pair construction over the integers with the
doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), the inner product
the coordinate dot product. The induction runs on the block forms of left
and right multiplication by s' = (s, 1 + s) that the tower note derives; the
commutation law closes through conj x = 2 re(x) 1 - x and s s = -(n - 1) 1, so
flexibility of the algebra is proved for s rather than assumed. Integer
coefficients keep every theorem free of axioms: all eleven assumption queries
print `Closed under the global context`, and the kernel check lists no axioms,
type-in-type, unsafe fixpoints or assumed positivity.

The definitions transcribe open_gororoba `proofs/theories/RecursiveCDTower.v`
(the same doubling over the reals). That file is absent at the commit
`ci/open_gororoba.pin` names, and moving the pin would change
`BooleanCochainFiltration.v` under the hash-bound folding_proofs bundle, so
the proof stands alone on Stdlib's ZArith.

## Bridge to cd_sign

`sigma` and `cd_sign_loop` are Rocq transcriptions of the Python loop, and
`cd_sign_loop_sigma` proves them equal. [tower_bridge.py](tower_bridge.py)
links the transcription to the Python source: it mirrors `sigma` branch for
branch and requires sigma_k(a, b) = cd_sign(2^k, a, b) on all 5,460 pairs at
n = 2 to 64, with a negative control that negates each of the four branches in
turn and requires a disagreement at every n >= 4. It also transcribes the
tower's multiplication onto coordinate lists and checks
e_a e_b = cd_sign(n, a, b) e_(a XOR b) on the same pairs and that the tower's
(s, 1 + s) recursion yields e_1 + ... + e_(n-1). The bridge is exact finite
computation; the Rocq side holds for every k.

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
and [kernel.txt](kernel.txt). The ci.yml job rocq-replay runs it on the
nightly schedule and on manual dispatch, which always replay; a pull request's
premerge replay runs by hand and is recorded against the reviewed PR head. `source_hashes.sha256` binds
the source and receipts, so an edit to the proof without new receipts fails
the hash gate. The compile takes about 6 s on the build host.
