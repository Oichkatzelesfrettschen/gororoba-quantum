# Pathion kernel map: the A_5 sign network on hardware

Left multiplication by a two-term operand e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5 pairs the 32
basis states into 16 XOR pairs {k, k XOR m}, m = i XOR j, and its nullity N is the number of pairs on which the
signed permutation K = L_i^T (t L_j) carries equal signs (`gororoba_quantum/pathion_kernel_map.py`; N = 0, 4, 8, 12
for two-term operands, among the A_5 annihilator dimensions 0, 4, 8, 12, 16 of Biss, Dugger and Isaksen,
math/0511691, Theorem 1.2; Skiouris, Aphanics at the Pathion Level, Proposition 2.2, gives 12 and 4 for the pairs
with i < 16 < j). The pairs' outputs are disjoint, so the operator splits over the cosets of
any subgroup V of (Z/2)^5 that contains m, and N is the sum of the coset blocks' nullities.

## What a hardware run can test

A QPU cannot re-prove an exact F_p or integer rank faster than elimination: rank testing over F_q needs Omega(n)
quantum matrix-vector queries (Childs, Hung and Li, arXiv:2102.11349), and distinguishing full rank from nullity one
needs Omega(n) quantum queries even for linear functions (van Apeldoorn and Gribling, arXiv:1810.12030); both bound
query access to an unknown matrix, and the kernel map compiles a known one, so they frame the claim rather than limit
the circuit. A run tests the device's realization of the exactly known sign network. Two design rules follow:

- A test whose input lies on two basis states touches only the four cocycle signs of one pair, whatever the
  dimension; a 32-dimensional claim needs one compiled operator acting on many pairs and a readout that resolves them.
- A diagonal sign applied immediately before a computational-basis measurement is unobservable, and IBM implements a
  diagonal Z as an exact virtual frame change; arms that differ only by such a sign test nothing.

## Package agreement

`scripts/pathion_kernel_map_packages.py` (build host `$PYTHON`) compares hypercomplex, hyprat and hypercomplex-engine
with cd_core on all 1024 basis pairs under the identity map, then recomputes each operand's nullity (python-flint
fmpz_mat rank) and aligned-pair count through each package: `packages.json`, every package 1024/1024 and every operand
equal to `pathion_kernel_map.nullity`.

## Program across platforms

| Platform | Object | Runs | Record |
|---|---|---|---|
| IBM Heron r2 | the full map: one compiled A_5 SELECT on all 16 pairs, six operands of nullity 0 to 12, twins, mutations, six replicas | ran 2026-11-06 on ibm_fez (backup account), job `dbn1tv8qtr0c73ac82eg`, 24 PUBs at 16,384 shots, five replicas; the coset-block map ran the same day on ibm_fez (job `dbn3a55t7fqc73ais42g`) and ibm_marrakesh (job `dbn38t0ou4as73b3q1n0`) | `results/live/2026-11-06T183538.809814Z/collect.json`, `results/live/2026-11-06T201037.234804Z/collect.json`, `results/live/2026-11-06T200832.558771Z/collect.json`, [findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md) |
| Quantum Inspire Tuna-17 | two-term coset blocks: 4 XOR pairs (16 SELECT signs) on 3 data qubits and the selector, 20 to 22 CZ; the full map routes to 116 to 144 CZ and does not resolve at the measured 0.955 retention per CZ | ran 2026-11-06 and 2026-11-07: the first series (QX control of 8 batches, then Tuna-17 batches 00 to 03, stopped by its drift rule) and the coin-arm series (QX control, then Tuna-17 batches 00 to 03, 10 jobs at 65536 shots and 16384 for the last, on qubits 2, 4, 8, 11, 12); every job completed | [tuna17-pathion-coset-block-case.md](../../notes/quantum_inspire/tuna17-pathion-coset-block-case.md) (run directories and job ids), `results/quantum_inspire/pathion_coset_*_analysis.json`, [findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md#cross-platform-runs-tuna-17-and-ascella-2026-11-07) (coin-series decisions, null offset, `ba` misses) |
| Quandela Ascella | four-term operands, whose 4 x 4 coset blocks include classes absent below dimension 32 | ran 2026-11-06 and 2026-11-07: the four-term block case (`sim:ascella` job `bfa9a0ef-1557-4f20-8f7a-7681bf6d8e56`, `qpu:ascella` job `f3a11b5f-b045-42be-9205-de7da91cbfec`) and the two-block pair case (`sim:ascella` job `64b1ba77-7f79-4f2f-a1c1-37740eeecf2a`, `qpu:ascella` job `db6355f7-87d5-4e7a-91f5-b898c33c839a`); all four completed | `results/quandela/runs/*-ascella_pathion_four_term_blocks-*`, `results/quandela/runs/*-ascella_pathion_coset_block_pairs-*`, [findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md#cross-platform-runs-tuna-17-and-ascella-2026-11-07) (four-term blocks conform; two-block job not admitted) |

Every measured reading of these runs sits in one long table, [evidence_table.csv](evidence_table.csv), one row per
reading with its ideal, standard error, calibration and the claim-ledger rows that cite the run;
[evidence_pivots.md](evidence_pivots.md) holds the four pivots computed from it (per backend and observable, the same
block across platforms, simulator against QPU, and each ledger row against its readings).
`scripts/pathion_evidence_table_build.py` writes both files (`--check` reports drift) through the reader
`gororoba_quantum/pathion_evidence_table.py`.

The evidence table holds block-level readings only. The Ascella mesh-persistence runs record the instrument (the fixed
error of each served mesh and the simulator's mesh identity), so `scripts/pathion_evidence_table_build.py` skips them by
name through `pathion_evidence_table.is_ascella_instrument_record` and raises on any unknown record; their readings live
in the [findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md) section "Ascella mesh persistence".

The mechanism probes behind the cross-platform findings (Ascella mirror failure, Tuna-17 null offset, Tuna-17 `ba`
misses) live in [conjectures/](conjectures/README.md) with their logs and a runner.

Every two-term pair block on these operands is one of the 16 sign matrices Belenos already measured in all 32
configurations (2026-10-30); a photonic two-term kernel map would repeat retained data, which is why the photonic
candidate moves to four-term blocks.
