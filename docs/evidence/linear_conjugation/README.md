# Linear work-register encoding of N=21 order finding

The N=21 order-finding circuit conjugates every controlled multiplier by one
uncontrolled B in GL(5,2). That replaces round k's multiplier f_k by
`g_k = B^-1 f_k B` and prepares the work register in `B^-1 |1>`. The phase
register's law is unchanged. Encoding with the admitted B lowers routed CZ
by 27.5 percent for the ten-round circuit and by 33.2 percent for the
two-round n21-feedback diagnostic. The construction and its admission
argument are in
[MODULAR_SYNTHESIS.md](../../../gororoba_quantum/MODULAR_SYNTHESIS.md#linear-work-register-encoding).

## Records

| Record | Produced by | Replay gate |
| --- | --- | --- |
| `search.json` | `scripts/linear_conjugation_search.py`, five Kaggle CPU shards merged with `--merge` | core-325 |
| `results/hw_estimate/n21_linear_conjugation_challenger.json` | `gororoba_quantum/linear_conjugation_challenger.py --search search.json`, one Kaggle CPU kernel under CI's interpreter and pins (`kaggle_run.py push --ci-env`) | core-326 |

**`search.json` contents.**
- Per coset: s(4) and s(2) for every one of the 83,328 cosets, in
  lexicographic order of their sorted column sets. Coset 0 is B = I.
- Summary: the ten-round winners, the s(4) winners, and the histograms.
- Run provenance: each shard's machine and seconds.
- Assumption checks: a separate seeded sample of 1,000 cosets
  (`results/kaggle/2026-10-16T192706Z-gororoba-linear-conjugation-sample`)
  checked the two assumptions the shards rely on, both on all 1,000 cosets:
  - `s(B^-1 f_16 B) = s(B^-1 f_4 B)`;
  - `cost(B P) = cost(B)` for a seeded permutation matrix P. Left
    multiplication `P B` changed the cost on 935 of the 1,000 cosets, which
    confirms that the right side is the invariant one.

**Challenger record contents.**
- **Compiles:** both problems with every admitted coset's per-seed compile
  record.
- **Checks:** the exhaustive conjugation check, the controlled-network
  operator check, and the seeded Aer phase-count comparison.
- **Verdicts:** the admission clauses for every candidate.

## Results

| | Ten-round, a = 2 | Two-round n21-feedback, a = 4 |
| --- | --- | --- |
| Multipliers | 4, 16 (x4), 4, 2 | 16, 4 |
| Surrogate at B = I | 2,556 | 504 |
| Surrogate minimum, coset | 1,896, coset 281 | 372, coset 281 |
| Admitted cosets (of the eight compiled) | 8 | 8 |
| Best admitted coset (columns) | 15241 (2, 4, 5, 8, 25) | 15265 (2, 4, 5, 10, 17) |
| Median routed CZ, baseline -> encoded | 5,422 -> 3,933 | 1,107 -> 739 |
| Median depth | 13,662 -> 9,847 | 2,688 -> 1,839 (feed-forward arm) |
| Median duration (dt) | 131,793 -> 96,196.5 | 25,734 -> 17,607 |

The admitted circuit with the fewest median routed CZ is not the surrogate
optimum. The surrogate weighs each cube's control count. The router also
pays for where those controls sit on the heavy-hex coupling map, which the
surrogate does not see.

## Replay across hosts

Routed CZ, qubit counts, layouts and classical stages replay exactly on
every host measured. Depth and duration follow floating-point single-qubit
synthesis and shift with the BLAS build:
- between Kaggle's pip numpy wheels and the build host's AOCL numpy they
  differ by at most one layer and 18 dt of 131,793, a relative 0.00037;
- the replay accepts such differences up to 0.002;
- it re-derives the best coset's admission verdict from the recompiled runs.

The challenger record was produced under CI's interpreter and pins (Python
3.14.7, numpy 2.5.4, qiskit 2.5.2, qiskit-ibm-runtime 0.50.0), the
environment of the CI gate that replays it.

## Replay

```sh
"$PYTHON" scripts/linear_conjugation_search.py --check docs/evidence/linear_conjugation/search.json
"$PYTHON" gororoba_quantum/linear_conjugation_challenger.py --check results/hw_estimate/n21_linear_conjugation_challenger.json
```

The first replay recomputes these cosets:
- the baseline;
- every ten-round and s(4) winner;
- the first 40 cosets (`--limit`).

It requires every summary field to equal the one derived from the retained
costs.

The second replay recompiles the baseline and the best admitted coset of
each problem over all eight seeds.

## Scope

- **Family.** The search is exhaustive over the linear family under the
  target-flip surrogate.
- **What the counts cover.** The routed numbers come from one captured fake
  backend.
- **What they do not cover.** They predict no fidelity. A hardware use needs
  a fresh dry run and an approved case.
- **Split conjugators.** One B for rounds 1 to 9 and another for round 10
  would add one uncontrolled CNOT network at that boundary. The minimum s(2)
  over all cosets is 180, against 222 at the joint optimum, so a split can
  gain at most 42 surrogate units minus that network's CNOT count. That
  variant has not been searched.
