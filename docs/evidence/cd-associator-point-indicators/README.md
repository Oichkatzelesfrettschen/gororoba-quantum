# Point-indicator associator pairs

[CdAssociatorPointIndicators.v](../../../proofs/CdAssociatorPointIndicators.v)
formalizes the displayed identity of Proposition 5 in
[cd_phase_degree.md](../../notes/cd_phase_degree.md) for every doubling level
n >= 3, and proves the family's exact ANF degree. The dimension is 2^n.
The proof imports the existing conference, tower basis-sign, sign-row ANF
and associator ANF proofs without changing them.

For natural m < 2^(n-2), set

    i = 2^(n-1) + m,
    j = i + 2^(n-2),
    z = x mod 2^(n-2),   x < 2^n.

With addition in F_2, delta_m(z) = [z = m] and N(z) = [z != 0], the
associator phase is

    g_ij(x) = x_(n-1) + delta_m(z)   when m != 0,
    g_ij(x) = N(z)                   when m = 0.

Bit n - 2 is absent in both cases; the top bit is also absent when m = 0.
Both phases have degree exactly n - 2, including degree 1 at n = 3.

| Theorem | Statement, with the bounds above |
| --- | --- |
| `point_indicator_pairs` | The complete two-case identity for `assoc n i j x` |
| `point_indicator_nonzero` | The point indicator plus the top bit when m != 0 |
| `point_indicator_zero` | N(z) for i = 2^(n-1), j = 2^(n-1) + 2^(n-2) |
| `point_indicator_degree` | `degree_is n (assoc n i j) (n - 2)` |

The argument applies the already proved associator recursion twice. At the
first doubling, the pair (m, m + 2^k) has phase
N(m) + [z = 0] + [z = m] on either input half. At the second, the two point
indicators in the upper-pair correction cancel the dependence on bit k.
The remaining top-bit coefficient is N(m). Taking k = n - 2 gives the
displayed formula. The degree corollary applies the existing all-level
`assoc_degree_is` theorem to these distinct nonzero indices.

## Scope and assumptions

The proof uses `assoc` from the
[associator-phase ANF bundle](../cd-associator-anf/README.md), whose
`assoc_sigma` and `assoc_basis` identify the phase with the four tower signs
and the basis associator. It uses that bundle's ANF definitions and
`degree_is`, rather than a new surrogate for either phase or degree. The
separate [cd_sign Python-semantics bundle](../cd-sign-python-semantics/README.md)
records the connection to the Python implementation and its trust boundary.

The identity and exact degree are the scope of this formalization. The
positive-polarity monomial counts and circuit interpretation in the note
remain written consequences; this file does not formalize a gate language,
gate costs or the later finite sparsity classification. In particular, it
does not turn those finite classifications into all-level theorems.

Each of the four queries in [assumptions.v](assumptions.v) prints
`Closed under the global context` ([assumptions.txt](assumptions.txt)). The
independent [kernel check](kernel.txt) reports no axioms, type-in-type,
unsafe fixpoints or assumed positivity. Its context is the Calculus of
Inductive Constructions with predicative Set and no rewrite rules; the
listed equality and Boolean inductives use the default rule that indices
do not raise their universe level. Arithmetic and Boolean proof steps use
the definitions and proved lemmas of Corelib and Stdlib 9.2.0.

The formalization was developed with AI assistance. The retained
assumption and kernel-check receipts record its verification.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-associator-point-indicators/replay_rocq.sh
sha256sum -c docs/evidence/cd-associator-point-indicators/source_hashes.sha256
```

`replay_rocq.sh` requires the banner in [toolchain.txt](toolchain.txt): Rocq
9.3.0 on OCaml 5.5.1, with Stdlib 9.2.0 from the pinned CI switch. It
compiles the five proof sources and the assumption queries in temporary
storage with `-w @all`, rejects warnings and unexpected compiler output,
runs `rocq check`, and compares both receipts byte for byte. The
`source_hashes.sha256` ledger binds the five proof sources, queries,
receipts, toolchain banner and replay script. The CI Rocq replay runs this
bundle alongside the other proof bundles.
