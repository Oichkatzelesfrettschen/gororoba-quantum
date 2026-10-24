# Associator-phase census proof

[CdAssociatorCensus.v](../../../proofs/CdAssociatorCensus.v) proves the
census of [cd_phase_degree.md](../../notes/cd_phase_degree.md): the number
of unordered basis pairs whose associator phase has each ANF degree, for
every Cayley-Dickson dimension n = 2^k. It requires the
[associator-phase ANF proof](../cd-associator-anf/README.md) and the three
proofs below it, all unchanged.

`anf_degree k f` computes the degree of a truth table on x < 2^k as the
largest `weight` among the monomials with a nonzero `anf_coef`, the
coefficients that `anf_inversion` and `anf_unique` of the
[sign-row bundle](../cd-sign-row-anf/README.md) establish as the ANF.
`census k d` counts the pairs 0 < p < q < 2^k with
`anf_degree k (assoc k p q) = d`. The count therefore reads the degree off
the phase's own coefficients, and Theorem 2 (`assoc_degree_is`) enters only
through `degree_is_anf`, which shows that a function of exact degree d has
`anf_degree` d.

| Theorem | Statement |
| --- | --- |
| `degree_is_anf` | degree_is k f d implies anf_degree k f = d |
| `degree_is_unique` | a truth table has at most one exact degree |
| `assoc_anf_degree` | k >= 3, 0 < p < q < 2^k: anf_degree k (assoc k p q) = max(1, log2 q - 1) |
| `census_degree_one` | k >= 3: 21 pairs have degree 1 |
| `census_degree` | k >= 3, 2 <= d <= k - 2: 3 2^d (2^(d+1) - 1) pairs have degree d |
| `census_degree_none` | k >= 3: no pair has degree 0 or a degree above k - 2 |
| `census_new_level` | n >= 4: level n has 3 2^(n-2) (2^(n-1) - 1) pairs of degree n - 2 |
| `census_stable` | k >= 3, d <= k - 2: the degree-d count is the same at level k + 1 as at level k |
| `census_total` | k >= 3: twice the sum of the counts over d < k is (2^k - 1)(2^k - 2) |
| `census_dim256` | at k = 8 the counts of degree 1 to 6 are 21, 84, 360, 1488, 6048 and 24384 |

The phase of a pair p < q has degree max(1, log2 q - 1), so the inner sum
over p contributes q - 1 whenever the degree condition holds for q, and the
outer sum splits into bit-length shells 2^b <= q < 2^(b+1). `sum_shell`
restricts a sum over q < 2^k to one shell, `sum_prefix` to the shells below
b = c, and `shell_count` evaluates a shell's pairs with the Gauss sum
`sum_id`: shell b adds 3 2^(b-1) (2^b - 1) pairs. Degree 1 collects the
shells b <= 2, the 21 pairs inside the octonions (3 quaternion pairs and 18
new ones), and degree d >= 2 is the single shell b = d + 1. `census_total`
exchanges the sums over degrees and pairs (`sum_swap`), so every pair
counts at exactly one degree below k, and the total is C(2^k - 1, 2).

The theorems rest on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)), identical to the associator-phase ANF bundle's:
the Calculus of Inductive Constructions with a predicative Set and no
rewrite rules, with `eq`, `eq_true`, `eq_dep` and Btauto's `null` typed
under the default rule that inductive indices do not raise the universe
level. Beyond the kernel the proofs use the definitions and proved lemmas of
Corelib and Stdlib 9.2.0: natural-number and integer arithmetic through
`lia` and `nia`, `Nat.log2` with `Nat.log2_unique` and `Nat.log2_lt_pow2`,
and the bitwise operations the lower bundles use. Each of the ten
assumption queries in [assumptions.v](assumptions.v) prints `Closed under
the global context` ([assumptions.txt](assumptions.txt)): the proof terms
reach the kernel through those definitions alone, with every classical,
extensionality and choice principle absent. The tower sign sigma equals
the return value of cd_core.cd_sign for every k by the
[cd_sign Python-semantics bundle](../cd-sign-python-semantics/README.md); the remaining
trust is the one the associator-phase ANF bundle names.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-associator-census/replay_rocq.sh
sha256sum -c docs/evidence/cd-associator-census/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
five proof sources and [assumptions.v](assumptions.v) in temporary storage
with `-w @all`, fails on any warning or compiler output, runs `rocq check`,
and compares the outputs byte for byte with the receipts. The ci.yml job
rocq-replay runs it beside the other Rocq bundles, and `source_hashes.sha256`
binds the five proof sources and the receipts. The replay takes about 36 s
on the build host.
