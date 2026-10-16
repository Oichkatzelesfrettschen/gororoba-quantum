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
| `noise.json` | `scripts/n21_conjugation_noise.py --challenger ...`, one Kaggle CPU kernel per backend under `--ci-env`, combined with `--merge` | core-327 (full tier) |

Gate core-329 binds all three records to the retained Kaggle outputs under `results/kaggle/`: it re-merges the five shards and the three noise records, compares both merges byte for byte, and compares the challenger record with its kernel output.

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

## Noisy laws under the 2026-10-16 midday calibrations

`noise.json` samples the baseline and the encoded circuits (cosets 15265 and
15241) under the Fez, Kingston and Marrakesh snapshots retrieved at
12:12, 12:13 and 11:51 (-07:00), using the retained
`docs/evidence/calibration/history/` files.
- **Compile:** each circuit compiles at optimization level 3 on the snapshot
  Target over transpiler seeds 0 to 7, keeping the fewest routed CZ.
- **Sampling:** each circuit samples statevector trajectories of
  live_run's noise channels on its 7 active qubits, at 32,768 shots for each
  two-round arm and 16,384 for the ten-round circuit.
- **Signal:** the two-round signal is the signed-contrast difference between
  the feed-forward and no-feed-forward arms, ideal 1/4.

| Backend | Routed CZ, two-round | Contrast, baseline | Contrast, encoded | Shots per arm for power 0.8 (encoded) | QPU seconds, both arms in one job at 8,192 / 32,768 shots |
| --- | --- | --- | --- | --- | --- |
| ibm_kingston | 1,023 -> 713 | 0.0067 +- 0.0055 | 0.0417 +- 0.0055 | 4,454 | 7.7 / 23.8 |
| ibm_fez | 1,023 -> 713 | -0.0046 +- 0.0054 | 0.0198 +- 0.0055 | 20,048 | 7.6 / 23.4 |
| ibm_marrakesh | 1,023 -> 713 | -0.0018 +- 0.0055 | 0.0135 +- 0.0055 | 42,972 | 7.8 / 24.1 |

**Two-round diagnostic.**
- **Contrast.** The encoding moves its modeled contrast above sampling noise
  on all three backends, from zero within one standard error to 2.5 to 7.6
  standard errors.
- **Shot cost.** It cuts the shots a 0.8-power test needs on Kingston by a
  factor of 39 (174,337 per arm unencoded). The baseline contrast on Fez and
  Marrakesh is not positive, so no shot count detects it.
- **Fidelity.** The modeled contrast stays a sixth of the ideal at best,
  with both arms' total variation from their ideal laws at 0.10 to 0.23.

**Ten-round circuit.** Order recovery is 0.134 to 0.139 baseline and 0.129
to 0.134 encoded. That is at or below the fully depolarized 0.1445 and far
from the noiseless 0.334, so neither form carries order information on
these devices.

**Seconds.**
- **Formula:** shots x (Target duration of the true-branch gate-time view +
  20 us per feed-forward stage + the 250 us repetition delay), plus 2.3 s per
  job, using live_run's planning declarations.
- **What it omits:** the scheduler's alignment and reset residual, which the
  retained runs measured at 540 to 584 dt per feed-forward round trip.

These are design estimates. The shot counts use the normal approximation at
the modeled contrast and omit live_run's simultaneous simulation allowance.
Admission belongs to a submit-free live_run dry run of the encoded family,
and any execution needs an approved case.

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
"$PYTHON" scripts/n21_conjugation_noise.py --check docs/evidence/linear_conjugation/noise.json
```

The noise replay recompiles every circuit's chosen seed on its retained
snapshot, holding routed CZ, layout and classical stages exact and depth
and duration within 0.002. It re-derives every distribution, contrast,
recovery rate and seconds estimate from the retained counts, and samples
nothing.

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
