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
| `am_quaternion` | Proposition 4.4(ii): f_2(x, y) = x1 y1 + (x1 + x2) y2 |
| `am_octonion` | Proposition 4.4(iii) with the cubic term x1 x2 y3 |
| `am_octonion_printed_differs` | the printed cubic term x2 x2 y3 differs from f_3 at x = 2, y = 4 |
| `am_altercommutative` | Definition 3.2 and Proposition 4.2: f_k(a, b) + f_k(b, a) = [a != 0, b != 0, a != b] |
| `sigma_diagonal` | sigma_k(a, a) = -1 for a != 0 |
| `sigma_anticommute` | sigma_k(a, b) = -sigma_k(b, a) for distinct nonzero a, b |
| `am_left_involution` | f_k(x, a) + f_k(a XOR x, a) = [a != 0] |
| `sigma_left_involution` | sigma_k(a, x) sigma_k(a, a XOR x) = -1 for a != 0: e_a (e_a e_x) = -e_x |
| `sigma_right_involution` | sigma_k(a, b) sigma_k(a XOR b, b) = -1 for b != 0: (e_x e_b) e_b = -e_x |
| `right_mul_entry` | (e_a v)_(a XOR b) = sigma_k(a, b) v_b: R_v carries v_b on XOR diagonal b |
| `isum_scaled_isometry` | <alpha x + beta x s, alpha y + beta y s> = (alpha^2 + (n - 1) beta^2) <x, y> |
| `convention_discriminator` | ((e_0 + e_1) s)_3 = 2 and (s (e_0 + e_1))_3 = 0 for n >= 4 |

The induction runs on the doubling halves: index bit k - 1 selects the half,
and the index facts reduce to `Nat.lxor` identities that `btauto` closes bit
by bit. Conjugation fixes e_0 and negates every other unit, and sigma_k(0, q)
= sigma_k(p, 0) = 1. The Corollary 4.3 exponent starts from the trivial group,
so level 1 reproduces the paper's f(x, y) = xy, and its diagonal
f(x, x) = [x != 0] carries the e_x e_x = -1 case of the induction.

The Proposition 4.4 theorems read paper index i on index bit i - 1, the
highest index bit being the last doubling. Proposition 4.4(iii) as printed
carries the cubic term x2 x2 y3; Corollary 4.3 produces x1 x2 y3, and the
two differ on the 8 cells with x1 = 0, x2 = 1, y3 = 1 (the misprint
[math-9802116.md](../../notes/math-9802116.md) records). Proposition 4.4(iv)
stays out: no reading the note tried reproduces it. `am_left_involution` is
Lemma A of [cd_phase_degree.md](../../notes/cd_phase_degree.md) in the
paper's argument order, proved for every k, and the right involution follows
from it with altercommutativity. The right involution pairs a with a XOR b,
so the Walsh coefficients of the sign row sigma_k(., b) vanish at every z
with b . z even; [cd_phase_degree.py](../../../scripts/cd_phase_degree.py)
checks that consequence numerically.

`isum_scaled_isometry` with alpha = beta = 1 is the skew Hadamard identity, so
U_n = (I + W_n)/sqrt(n) is orthogonal with every entry +-1/sqrt(n), and every
computational-basis input gives the uniform output distribution. Right and
left multiplication by s share that Gram matrix, so basis-input counts cannot
tell the intended operator from one built on the untransposed convention.
`convention_discriminator` gives the separating input: on
(|0> + |1>)/sqrt(2), the output-3 probability is 2/n for (I + R_s)/sqrt(n)
and 0 for (I + L_s)/sqrt(n). A circuit replay of the transform carries that
input as its convention control.

Every theorem rests on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)): the Calculus of Inductive Constructions with a
predicative Set and no rewrite rules, with the equality types `eq`, `eq_true`
and `eq_dep` and Btauto's `null` typed under the default rule that inductive
indices do not raise the universe level. Beyond that kernel, the proofs use
only definitions and proved lemmas of Corelib and Stdlib 9.2.0: the integers
and their ring structure (ZArith, through `ring` and `lia`), the natural-number
bitwise operations `Nat.lxor`, `Nat.testbit` and `Nat.log2` with their
Stdlib lemmas, and Btauto's Boolean normalization. Each of the nineteen
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
computation; the Rocq side holds for every k. The
[cd_sign Python-semantics bundle](../cd-sign-python-semantics/README.md)
proves the same agreement for every k, by running the syntax tree of
cd_core.cd_sign under a Rocq semantics of the Python subset it uses, and
the bridge stays as an independent cross-check.

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
The replay takes about 31 s on the build host.
