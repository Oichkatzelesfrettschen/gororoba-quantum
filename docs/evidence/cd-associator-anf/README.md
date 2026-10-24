# Associator-phase ANF proof

[CdAssociatorAnf.v](../../../proofs/CdAssociatorAnf.v) proves Theorem 2 of
[cd_phase_degree.md](../../notes/cd_phase_degree.md), the exact algebraic
degree of the associator phases, for every Cayley-Dickson dimension
n = 2^k. It requires the sign-row ANF proof
([sign-row ANF bundle](../cd-sign-row-anf/README.md)), the tower basis-sign
proof and the conference proof below them, all unchanged.

For basis units e_p, e_q the operator W = L_(e_p e_q)^dagger L_(e_p) L_(e_q)
of `predict.associator_phase` is diagonal with entry (-1)^g(x) on e_x, where

    g_(p,q)(x) = phi(q, x) + phi(p, q XOR x) + phi(p XOR q, x) + phi(p, q),

phi(a, b) = [sigma_k(a, b) = -1]. The proof defines `assoc k p q x` from the
Albuquerque-Majid Corollary 4.3 cochain, phi(a, b) = `am_exponent k b a`, and
`assoc_sigma` checks that reading against the four tower signs in the
factor order of `predict.associator_phase`. The ANF definitions
`anf_coef`, `weight` and `degree_is` are those of the sign-row bundle, where
`anf_inversion` and `anf_unique` establish `anf_coef` as the ANF.

| Theorem | Statement, for every k and p, q, x < 2^k |
| --- | --- |
| `assoc_sigma` | (-1)^g(x) = sigma_k(p, q) sigma_k(p XOR q, x) sigma_k(q, x) sigma_k(p, q XOR x) |
| `assoc_basis` | e_p (e_q e_x) = (-1)^g(x) (e_p e_q) e_x in the integer tower |
| `assoc_degenerate` | g vanishes when p = 0, q = 0 or p = q (Lemma C) |
| `assoc_quaternion` | every phase of the quaternions (k = 2) vanishes |
| `two_point` | k >= 1, u != v: [y = u] + [y = v] has degree exactly k - 1 (Lemma B) |
| `assoc_degree_is` | k >= 3, p, q distinct and nonzero: g has degree exactly max(1, bitlen(max(p, q)) - 2) (Theorem 2) |

The induction splits x = (y, xi) at the highest index bit n of level n + 1
and reads p = (p', alpha), q = (q', beta) the same way:

- every phase satisfies g(y, 1) = g(y, 0) + c with
  c = [p' != 0] + [q' != 0] + [p' XOR q' != 0] (Lemma D1). The four
  `assoc_high_*` lemmas derive it from the paired sign rows `row_pair_low`
  and `row_pair_high` of the sign-row bundle and `alt_triple`, which cancels
  the point indicators of the three commutator exponents in pairs;
- for a pair inside the low half, g(y, 0) is the phase one level down
  (`assoc_low`) and c = 1, so the degree passes up unchanged (`lift`), with
  `lift_zero` covering the quaternion step g = xi;
- for a pair reaching the top half, g(y, 0) is the phase of (p', q') plus
  two distinct point indicators and a constant (`assoc_lh_low`,
  `assoc_hl_low`, `assoc_hh_low` with `alt_delta`). The indicators have
  degree n - 1 by `two_point`; the lower phase has degree at most n - 2,
  zero for a degenerate or quaternion pair and the induction hypothesis
  otherwise, so `upper_degree` fixes the degree at n - 1 = bitlen - 2.

The theorems rest on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)), identical to the sign-row and tower basis-sign
bundles': the Calculus of Inductive Constructions with a predicative Set and
no rewrite rules, with `eq`, `eq_true`, `eq_dep` and Btauto's `null` typed
under the default rule that inductive indices do not raise the universe
level. Beyond the kernel the proofs use the definitions and proved lemmas of
Corelib and Stdlib 9.2.0: natural-number and integer arithmetic through `lia`
and `ring`, the bitwise operations `Nat.lxor`, `Nat.ldiff`, `Nat.ones`,
`Nat.testbit` and `Nat.log2` with their Stdlib lemmas, and Btauto's Boolean
normalization. Each of the six assumption queries in
[assumptions.v](assumptions.v) prints `Closed under the global context`
([assumptions.txt](assumptions.txt)): the proof terms reach the kernel
through those definitions alone, with every classical, extensionality and
choice principle absent. The remaining trust is the transcription of the
cd_sign loop and of Corollary 4.3 that the tower bundle names.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-associator-anf/replay_rocq.sh
sha256sum -c docs/evidence/cd-associator-anf/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
four proof sources and [assumptions.v](assumptions.v) in temporary storage
with `-w @all`, fails on any warning or compiler output, runs `rocq check`,
and compares the outputs byte for byte with the receipts. The ci.yml job
rocq-replay runs it beside the other Rocq bundles, and `source_hashes.sha256`
binds the four proof sources and the receipts. The replay takes about 47 s
on the build host.
