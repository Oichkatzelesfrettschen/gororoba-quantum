# Written case: A_5 coset-block kernel map on Tuna-17, coin-arm series

Status: run on 2026-11-07 under the owner's approval of 2026-11-06, quoted in each submission receipt (`--approval`): the QX
control (`results/quantum_inspire/runs/2026-11-07T000930Z-pathion_coset_coin_qx-batch-00`, batch job 922371, jobs 1686078 to 1686081,
2048 shots) and Tuna-17 batches 00 to 03 (`results/quantum_inspire/runs/2026-11-07T001031Z-pathion_coset_coin_tuna_17-batch-0{0..3}`,
batch jobs 922372, 922375, 922378 and 922382, jobs 1686082 to 1686084, 1686091 to 1686093, 1686100 to 1686102 and 1686114, 65536 shots
and 16384 for batch 03), every job completed. The analyses are `results/quantum_inspire/pathion_coset_coin_qx_analysis.json` and
`results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json`; their interpretation lands in a later change. The series is `pathion_coset_coin_tuna_17` (hardware) with the twin `pathion_coset_coin_qx` (emulator),
retained under `results/quantum_inspire/cases/`, built by `scripts/qi_pathion_coset_coin_cases.py` from
`gororoba_quantum/pathion_coset_block.py` and gated by `scripts/qi_pathion_coset_coin_series.py`. It succeeds the
first series (`pathion_coset_block_tuna_17`, 8 batches of 3 jobs, generator `scripts/qi_pathion_coset_block_cases.py`), which
stopped after batch 03 and stays retained, with its case files, as a drift record
(`results/quantum_inspire/runs/*-pathion_coset_block_tuna_17-batch-0{0..3}`,
`results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json`). The procedure of a Tuna-17 run is
[usage.md](usage.md#run-on-tuna-17); the platform and program context is
[the pathion kernel map record](../../evidence/pathion-kernel-map/README.md).

## Rule change of 2026-11-06 (before any data of this series)

The first series ended on its drift stop: the readout-1 circuit of batch 03 read q11 e10 = 0.107 against 0.276 in batch 01 (change
-0.170 against the 0.02 limit; q11 e01 read 0.069 throughout, against 0.022 in the retained 2026-10-23 circuits). The owner decided
on 2026-11-06 to run a fresh full series on the current calibration and to treat drift as a recorded covariate, never a stop.
The rules below replace the first series' rule 7 (a bracket change above 0.02 stops the series before the next submission and counts as a
failed rule) and its pooled-assignment correction:

- Each primary template (`ba`, `bb`, `b0`) is corrected with the assignment of its own batch, read from the readout pair that
  shares that batch, so a recalibration between batches is a stratum.
- The analysis reports every register qubit's assignment per batch, the change between successive brackets (flag above
  0.02, informational), and the cross-platform statistic of each primary recomputed under every bracket of the series
  (`drift_covariate`). `all_decisions_met` no longer contains a drift term.
- The platform-failure stop stays: a failed job, a short shot list or a refused submission stops the series and raises
  the pause ladder ([usage.md](usage.md#pause-escalation)).
- The pattern rule reads the bins where the signs of the two ideal c(y) differ (2 and 6), as the first series' note stated.
  The first series' code compared the 6-digit-rounded ideals for inequality and so treated all 8 bins as differing, which
  asked each block to read its own sign at 3 standard errors on every bin; this series computes the stated rule.

Why a stratum is required and a pooled correction is not: on the retained `ba`, `bb` and `b0` arm pairs of the first
series, correcting with the q11 e10 of batch 01 against that of batch 03 moves the corrected ratio c(y) / V by up to 5.7
(`ba`), 6.6 (`bb`) and 1.0 (`b0`) Tuna standard errors. The shift on `ba` and `bb` exceeds the 3-standard-error rule, so a bracket
shared across batches would decide the cross-platform rule by which bracket it used.

## What it measures

The pair-resolved kernel map of two-term operands e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5
(`gororoba_quantum/pathion_kernel_map.py`) restricts exactly to a coset block: for a subspace V of (Z/2)^5 that
contains m = i XOR j, the SELECT of the linear combination of unitaries maps the coset k0 + V onto the coset
(k0 XOR i) + V, so the uniform input with the orientation oracle splits into independent blocks. A block of
dimension 3 reads 4 XOR pairs and 16 of the 64 SELECT signs on three data qubits and the selector. The block circuit is H on
the data, a diagonal (orientation oracle times the s = 0 SELECT sign), the orientation phase pi on data qubit 0 for the plus arm,
H on the selector, a diagonal on four qubits (the ratio of the two SELECT sign tables), a CNOT from the selector onto
data bit 0 and H on the selector. The observable is the per-bin contrast c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y)
over the 8 output bins: +1 on both bins of an aligned pair and (+1, -1) on a misaligned pair, so the bin signs read the compiled sign
network and not only its count N_b of aligned pairs.

| Block | Operand | V = span | Coset k0 | Aligned pairs N_b | Ideal selector contrast | Ideal c(y), bins 0 to 7 |
|---|---|---|---|---|---|---|
| operand e1 + e18, nullity 12 (`ba`) | (1, 18, +1) | 19, 2, 12 | 1 | 2 | 0.5 | -1, +1, -1, +1, +1, +1, +1, +1 |
| operand e1 + e26, nullity 4 (`bb`) | (1, 26, +1) | 27, 2, 9 | 0 | 2 | 0.5 | -1, +1, +1, +1, +1, +1, -1, +1 |
| null operand e1 + e17, nullity 0 (`b0`) | (1, 17, +1) | 16, 1, 2 | 0 | 0 | 0 | -1, +1, -1, +1, -1, +1, -1, +1 |
| `ba` with every SELECT sign table replaced by its unsigned XOR permutation, the cocycle-free control (`xor_ba`) | (1, 18, +1) | 19, 2, 12 | 1 | not defined | -1 | -1 in all 8 bins |

(Ideal values are those of the circuits of record to the grid rounding, at most 3.6e-4 away; `cases.json` carries them to 6
digits.) `ba` and `bb` have one selector contrast, 0.5, and differ in bins 2 and 6, so only the bin pattern separates their cocycles.
`tests/gororoba_quantum/test_pathion_coset_block.py` checks the restriction (Statevector, every block and arm: the block law equals
|V| / 32 times the six-qubit law of `pathion_kernel_map.kernel_map_circuit` to 2e-16, also for the cocycle-free law; c(y) equals the
module's c(k) at the algebra index of the bin; the four cosets of each V cover all 32 outputs once with N_b summing to the nullity).

## Why a simulation cannot answer it

The ideal laws are exact and checked three ways (Statevector of the logical block, Statevector of the rounded routed circuit,
local qxelarator on the emitted cQASM). The question is the device's: whether Tuna-17 keeps the sign pattern of a degree-3 sign
network at 21 to 23 routed CZ. The retained Tuna-17 points bracket that depth without covering it (contrast 0.954, 0.857, 0.710 at 1,
5 and 9 CZ in the box-kite ladder, a fit of 0.9654 per CZ; 0.955 to 0.956 per CZ at 45 to 91 CZ in the kernel-cancellation and
zero-divisor series; [tuna-17.md](tuna-17.md), [experiments.md](experiments.md)) and the platform publishes no Tuna calibration to
build a noise model on ([tuna-17.md](tuna-17.md#readout-calibration-drift)). The full six-qubit map routes to 116 to 144 CZ, where
the same retention predicts a per-output contrast of 0.1 to 1.3 percent against a per-bin standard error of 3.1 percent at 16384
shots, so the block is the largest piece of the map the device can resolve.

## Design: the most mathematics per job

The first series spent 24 jobs: 16 arm jobs (4 templates, 2 arms, 2 replicates) and 8 readout jobs. This series spends 10 jobs in 4
batches and keeps every decision of the first series (list below). Each option was evaluated against the platform's job model and
the measured Tuna-17 numbers:

| Option | Verdict | Evidence |
|---|---|---|
| Several blocks in one circuit on disjoint regions | not chosen; an owner decision | Under the preregistered admission rules (zero-divisor readout faults q0, q5, q6, q7, q9; q15; q13; every inner coupler at most 10 kHz) no two admitted regions are disjoint: `--select-region` counts 0 disjoint pairs of admitted 4-qubit regions and 0 of 5-qubit regions. Dropping the coupler limit and the q13 exclusion admits 8 disjoint pairs of 4-qubit regions (best (1, 2, 4, 8) with (11, 12, 14, 16), 20 CZ each for `ba` without the coin) and, with q15 also admitted, 4 pairs of 5-qubit coin regions (best (1, 2, 4, 8, 12) with (10, 11, 13, 14, 16), 21 and 26 CZ for `ba`). These counts come from an exploratory scan (eight candidate seeds of the first series' draw for the 4-qubit pairs, six of this series' draw for the 5-qubit pairs) that no retained routing reproduces. That placement uses the (1,4) coupler at -19.3 kHz and the (11,14) coupler at -31.4 kHz, puts q13 beside q11, and runs two CZ-heavy regions at once, which no retained Tuna-17 record measures; it would halve the data jobs but confound this series' decisions with parallel operation, so the series keeps one region. |
| Both orientation arms in one job through a second circuit | not available | The API job takes one circuit: OpenAPI `JobIn` holds one `file_id` plus `number_of_shots` and `raw_data_enabled` ([api/openapi.json](api/openapi.json)). |
| Both arms in one circuit through `reset` reuse | refused | Two sequential blocks double the depth; `reset` is a measurement and flip whose phase handling qxelarator gets wrong ([qx-runs.md](qx-runs.md), item 5), so no local check can certify the circuit, and mid-circuit bits have no QX counterpart. |
| Both arms in one circuit through a coin qubit | chosen | A fifth qubit in \|+> controls the orientation phase: the state is (\|0> minus arm + \|1> plus arm) / sqrt(2), and a Z-basis read of the coin labels each shot. The circuit gains one CZ and no new platform capability. Statevector arithmetic confirms both arms equal the phase arms to 1e-12 for every block, and each arm's data marginal is uniform to 1e-12 (`test_pathion_coset_block.py`). |
| Readout bracket inside the data job | refused | A readout circuit prepares known states and the data circuit cannot. A spare qubit calibrates only itself. The drift record above shows the assignment of a register qubit (q11) moving by 0.17 between batches, which the bracket of the same batch corrects. |
| Readout pair per primary batch, none for `xor_ba` | chosen | Each of `ba`, `bb`, `b0` is corrected with the e01 and e10 its own batch measured. `xor_ba` decides on the sign of its selector contrast (ideal -1 against +0.5), which needs no correction. |
| One replicate against two | one coin job per template | The first series' second replicate balanced the arm order; interleaved arms need none. One job at 65536 shots holds an expected 32768 shots per arm, equal to the first series' two replicates pooled, so every preregistered standard error carries over. |
| More shots per job against more jobs | 65536 shots per primary job, 16384 for `xor_ba` | The platform cap is 131072 shots and 300 s per job (`BackendType`); 65536 shots take 38 s on the timing fit (2.62 s plus 0.534 ms per shot, [tuna-17-run-design.md](tuna-17-run-design.md)) and at most 64 s at the slowest retained per-shot time. |

Coin properties used by the analysis, each stated and checked: a coin misread (readout error, relaxation of |1> after its CZ) moves a
fraction of each arm into the other pile. Because each arm's data marginal is uniform, this scales every c(y) by one common factor
(for a coin reading 1 for a true 0 with probability 0.05 and 0 for a true 1 with probability 0.08, 0.92 / 0.97 - 0.08 / 1.03 = 0.871;
`test_a_coin_misread_scales_every_contrast_by_one_factor`), which leaves c / V, N_hat, every sign decision and the null unchanged and
biases only V and the depth reading low. The assignment correction acts on all five bits (a 32 x 32 matrix applied to the 32
counts before the split by coin) and removes the readout part of that factor; the relaxation part is unidentified, so the depth reading is a lower
bound. Both arms now sample the same phases of the 50 Hz line of [tuna-17.md](tuna-17.md#shot-order-a-50-hz-line), which separate jobs did not.
The null block `b0` reads any arm-dependent offset the coin adds.

Job count, decision by decision: 24 jobs fall to 10 (a factor 2.4), and batches from 8 to 4. The 16 arm jobs became 4 coin jobs: every
raw-count rule (resolution, pattern, null, cocycle-free) reads the coin piles of one job, with one calibration shared by both arms. The first
series' 8 readout circuits were one per batch with alternating kinds, so no batch identified its own assignment; this series' 6 are a full
pair in each primary batch and none for `xor_ba`, because resolution, pattern, null and cocycle-free read raw counts, depth is reported and
`xor_ba` supplies no depth comparison, while the cross-platform rule reads `ba`, `bb` and `b0`, each of which keeps its own pair. Batch 03 holds
two free slots; a readout pair there would add an end-of-series bracket, and a flipped-SELECT-sign arm would add a mutation, at two more jobs
each, which the fewest-jobs rule leaves to the owner. Device time is the cost of that trade: 3 data jobs and 6 readout jobs at 65536
shots plus the `xor_ba` job at 16384 shots is 9 x 37.6 s + 11.4 s = 350 s on the timing fit and 600 s at the slowest retained per-shot time
(the first series: 273 s and 370 s). The platform fixes one shot count per batch, so a readout circuit runs at its batch's shot count.

## Routing, seeds and qubits

- Admitted region: the connected 5-qubit regions off `qi_zero_divisor_cases.excluded_qubits()` (q0, q5, q6, q7, q9), off q15
  (P(0|1) 0.270, [tuna17-bipartite-designs.md](tuna17-bipartite-designs.md)) and off q13 (its |1> misassignment doubles
  beside an excited q11, [tuna-17.md](tuna-17.md#readout-context); the exclusion is fixed before the seed search), whose
  inner couplers all have a retained residual coupling |J| of at most 10 kHz
  (`results/quantum_inspire/coupler_zz_tuna_17_analysis.json`). One region remains: (2, 4, 8, 11, 12), the star on q8 with q2 attached to q4,
  couplers (2,4), (4,8), (8,11) and (8,12) at 4.1, -5.0, 6.6 and -0.7 kHz. The coin sits on q2.
- Seeds: every routing candidate takes its transpiler seed from the ANU QRNG draw
  `docs/evidence/anu_qrng/draw-2026-11-06T225841Z.json` (64 uint16 values, drawn 2026-11-06T22:58:41Z). Template slice t holds draw indices 16 t
  to 16 t + 15 (`ba` 0 to 15, `bb` 16 to 31, `b0` 32 to 47, `xor_ba` 48 to 63). The fewest-CZ candidate wins; among equal counts the
  candidate that puts q11 (the register qubit with the least stable readout, whose misassignment mixes bins when it carries data) on the selector or the coin
  comes first, then the lowest index: `ba` index 0, seed 60989; `bb` index 16, seed 3527; `b0` index 32, seed 22836; `xor_ba` index 48,
  seed 63671. The manifest names the draw, so the case owns it (`ci/seed_provenance.py --check`).
- Compilation: Qiskit transpile at optimization level 2 onto the region (basis cz, rz, sx, x), one compile per template, every rotation rounded to the nearest
  multiple of pi/36 (Tuna applies the same grid). The ideal of record is the Statevector of the rounded routed circuit read through its final layout over
  32 outcomes (index y + 8 s + 16 c); it departs from the unrounded block law by at most 3.6e-4 in any probability.
- Routed CZ per circuit (the coin's CZ included) and the physical qubits of data bits 0, 1, 2, the selector and the coin:

| Template | Routed CZ | d0 | d1 | d2 | selector | coin |
|---|---|---|---|---|---|---|
| `ba` | 21 | 11 | 12 | 4 | 8 | 2 |
| `bb` | 23 | 12 | 11 | 4 | 8 | 2 |
| `b0` | 21 | 12 | 4 | 11 | 8 | 2 |
| `xor_ba` | 5 | 8 | 12 | 4 | 11 | 2 |

- Toolchain: libqasm 1.2.1 analyzes and OpenSquirrel 0.9.1 compiles all 14 new circuits (10 hardware, 4 emulator) with no error, using the functions of
  `qi_toolchain_check.py` on exactly those files; 8 report a changed gate-sequence text because OpenSquirrel prints rotations to 8 significant digits.
- Local emulation: `qx_local_series.py` ran the 4 hardware data circuits and the 4 emulator circuits at 65536 shots on qxelarator; the
  total variation distance to the ideal law of record is 0.0068 to 0.0074 (hardware series) and 0.0050 to 0.0073 (emulator series) against the 0.025 bound of
  `--qx-conformance` (the sampling floor at 32 outcomes and 65536 shots is about 0.009).

## Backend, shots, batches and seconds

- Backend: Tuna-17 (backend type 7, `tuna_17`); QX emulator (backend type 1) for the dry run at 2048 shots, its maximum.
- Series (4 batches, 10 jobs, one batch queued at a time):

| Batch | Jobs | Shots per job |
|---|---|---|
| 00 | `readout-0`, `ba`, `readout-1` | 65536 |
| 01 | `readout-0`, `bb`, `readout-1` | 65536 |
| 02 | `readout-0`, `b0`, `readout-1` | 65536 |
| 03 | `xor_ba` | 16384 |

  A readout circuit excites the five register qubits (readout-1) or none (readout-0) and measures all 17, which is the context of the data circuits.
  The platform runs the jobs of a batch in an order of its own; the analysis reports the executed order from the provider start times. The QX series
  holds the four data circuits in one batch at 2048 shots.
- Pacing and queue rules applied, each with its source:
  - At most 3 jobs queued per hardware backend, abuse removes the account (FAQ, [site/faq.md:84](site/faq.md); the live page, read 2026-11-06, carries the same
    sentence). The runner applies the strictest reading: at most 3 circuits per batch and no batch queued while another job of the account on a hardware type is
    unfinished ([usage.md](usage.md#queue-rules-the-faq-governs)). Four batches go in one after another.
  - A large shot count may lengthen a job's queue time (FAQ, [site/faq.md:90](site/faq.md)), and the number of shots per request and the execution time are limited
    per backend (terms, [site/terms-and-conditions.md:39](site/terms-and-conditions.md)): 65536 shots stay below the platform's 131072 cap
    (`max_number_of_shots`) and a job's 38 to 64 s stays below the 300 s limit (`job_execution_time_limit`). `xor_ba`, which decides on a sign at z above 30, runs at 16384 shots.
  - Precautions against unnecessary loss of processor hours, for example syntax checking (terms item 9, [site/terms-and-conditions.md:61](site/terms-and-conditions.md)):
    the toolchain check and the local qxelarator runs above, then the remote QX dry run, precede the first Tuna-17 batch, and `--submit-next` refuses a Tuna-17 batch
    without a passing QX control.
  - Tuning: backends tune automatically for a few seconds to 30 minutes and a job scheduled during tuning waits (FAQ, [site/faq.md:89](site/faq.md)); the series needs
    no idle time for it.
  - No provider page sets an interval between submissions, so the pause is a repository rule: 30 s between hardware batches, raised to 60, 90 and 120 s after a
    platform failure ([usage.md](usage.md#pause-escalation)). Three pauses add 90 s (360 s at the 120 s step).
  - Terms of use: non-commercial research use (the conditions of 6 Feb 2025, [site/terms-and-conditions.md](site/terms-and-conditions.md)), and every uploaded circuit and datum is open to QuTech
    for its own and third-party use (item 14), so nothing confidential is submitted.
- Own execution time: 350 s on the timing fit, up to 600 s at the slowest retained per-shot time (above), so the series needs about 8 to 20 minutes of its own
  time with the pauses. The global Tuna-17 queue held 48 jobs at 18:37:39Z on 2026-11-06 with a mean wait of 5426 s; the statistic describes other users' long jobs
  and is no forecast for this account's batches (the first series' four batches started within seconds of their submissions).
- QX dry run: the four circuits as one remote QX batch at 2048 shots (QX jobs take 0.006 to 10.4 s each; credits 0, the ledger recorded no charge for any of its 450 jobs on
  2026-11-06T18:37Z). Its noiseless laws must read within 2 times the sampling floor of the ideal laws of record (`qx_control.pass`).

## Live state to read before batch 00

Re-read `qi_hardware_status` and `qi_backend` for type 7 (account scope) and proceed only while Tuna-17 is online and the account has no batch queued. The reads of the
first series (2026-11-06T18:34Z) showed Tuna-17 executing, 0 account jobs queued and the QX emulator idle; they hold no authority for this series.

## Predicted result

Model (hypothesis-level): the 32-outcome law contracts toward uniform by rho to the power of the routed CZ, then each of the five bits is misassigned with the assignment
of the first series' own readout circuits (the current calibration: mean e01 from its two readout-0 circuits and e10 from its two readout-1 circuits): q2 (0.017, 0.019), q4
(0.013, 0.049), q8 (0.032, 0.023), q11 (0.069, 0.191), q12 (0.006, 0.023). The q11 e10 is bimodal (0.276 and 0.107 in the two circuits), so the forecast brackets rather than
predicts it. rho spans 0.955 (the 45 to 91 CZ series) to 0.9654 (the 1 to 9 CZ ladder fit). Values per template are in `prediction.json`; z is |c(y)| over its standard error per bin.

| Template | Routed CZ | Retention rho^CZ | Predicted selector contrast | Predicted visibility V (raw) | z per bin | selector se |
|---|---|---|---|---|---|---|
| `ba` | 21 | 0.380 to 0.477 | 0.173 to 0.217 | 0.295 to 0.370 | 19.9 to 44.6 | 0.0038 |
| `bb` | 23 | 0.347 to 0.445 | 0.158 to 0.203 | 0.265 to 0.341 | 17.6 to 42.3 | 0.0038 |
| `b0` | 21 | 0.380 to 0.477 | 0 | 0.335 to 0.421 | 29.3 to 45.8 | 0.0039 |
| `xor_ba` | 5 | 0.794 to 0.839 | -0.566 to -0.598 | 0.566 to 0.598 | 30.5 to 35.2 | 0.0064 |

Measured at the current calibration (the first series' `ba`, `bb`, `b0` and `xor_ba` arm pairs, one replicate at 16384 shots per arm, no coin): raw V 0.385, 0.325, 0.483 and
0.831 (the first series' `xor_ba` has 4 CZ and q8 on its selector; the new one has 5 CZ and q11 on its selector, which the forecast carries), selector contrasts 0.185 +- 0.005 (`ba`), 0.194 +- 0.005 (`bb`), 0.017 +- 0.006
(`b0`) and -0.832 +- 0.003 (`xor_ba`), and per-bin standard errors 0.011 to 0.019, which the doubled per-arm sample of this series divides by 1.41. The per-bin z margin over the
3-standard-error rule is at least 5.9 on every primary bin of the model.

Null power: with a selector standard error of 0.0039 the rule flags an offset above 0.012. The retained signed response of -0.0167 +- 0.0039 (45 CZ, kernel cancellation)
would read at z = 4.3 (power 0.90), and the first series' `b0` selector contrast of +0.0167 +- 0.0055 (z = 3.0 on one replicate, coin-free) would also read at z = 4.3 if it is a device offset. The null
is therefore expected to fail if that offset persists. The analysis reports the difference between the coin series' `b0` contrast and that coin-free value (`decisions.null.stopped_series_reference`):
a reading near +0.017 locates the offset in the device, and a reading near zero locates it in the first series' job-to-job difference.

## Cross-platform comparison with the IBM map

The IBM coset-map case (`results/live/2026-11-06T194735.738910Z/CASE.md`) ran the same block circuits on ibm_fez and ibm_marrakesh: group `pathion_coset_map`, one 4-qubit circuit pair
per coset of `pathion_coset_block.default_basis(operand)`, 17 replicas on ibm_fez (job `dbn3a55t7fqc73ais42g`, record `results/live/2026-11-06T201037.234804Z/collect.json`) and 11 on
ibm_marrakesh (job `dbn38t0ou4as73b3q1n0`, record `results/live/2026-11-06T200832.558771Z/collect.json`), 16384 shots per replica. `prediction.json` carries their sha256 digests, and the analysis
refuses a changed file. A Tuna block uses another basis and coset than the IBM blocks, so the two sides compare by algebra output label: bin y of a Tuna block maps to the algebra
index k(y) = (k0 XOR i) XOR (the XOR of the basis vectors named by the bits of y) (`pathion_coset_block.output_labels`; `labels` in every `cases.json`).

| Block | k(y), Tuna bins 0 to 7 | IBM cosets holding these labels |
|---|---|---|
| `ba`, operand e1 + e18 | 0, 19, 2, 17, 12, 31, 14, 29 | k0 and k12 of V = span(19, 1, 2) |
| `bb`, operand e1 + e26 | 1, 26, 3, 24, 8, 19, 10, 17 | k0 and k8 of V = span(27, 1, 2) |
| `b0`, operand e1 + e17 | 1, 17, 0, 16, 3, 19, 2, 18 | k0 of V = span(16, 1, 2) |

The measured IBM values (visibility, nullity estimate and ratio per coset) are in `prediction.json` under `ibm_measured`; the per-label ratios c_I / V_I lie within 0.051 of the ideal
sign on ibm_fez and within 0.067 on ibm_marrakesh. The statistic is D(y) = c_T(y) / V_T - c_I(k(y)) / V_I with the standard error sqrt(se_T^2 + se_I^2); the Tuna error is the delta-method
propagation of the 32 multinomial counts of the coin job through the assignment correction, c, V and the ratio (`coin_statistics`), and the IBM error is the standard deviation of the per-replica
ratios (the Tuna block is one placement, so it meets one placement's draw of the IBM distribution). The prediction is D = 0, because both devices carry the same compiled sign network
and contract a bin alike. Two Tuna ratios are computed, the raw one and the readout-corrected one; the decision uses the corrected ratio with the assignment of the template's own batch,
and the raw D is reported beside it. Predicted corrected D(y) under the contraction model at rho 0.955 to 0.9654 (`cross_platform` in `prediction.json`): every block reads 8 of 8 bins within 3 combined
standard errors against each device, with combined standard errors 0.030 to 0.074 and a largest |z| of 0.59 to 1.18. The chance that a device obeying the model reads fewer than 7 of 8 bins on at least one of
the six block-and-device pairs is 1.3e-4 at rho 0.955 and 4.8e-5 at rho 0.9654 (`refutation_probability_any_pair`, exact enumeration over independent bins with the Tuna delta-method error as the only
random term). The rule tests a common contraction across the 8 bins of a block and the sign pattern; it is blind to a contraction common to the whole block, which V_T absorbs, and its power against a
single misrouted bin is a deviation of about 0.1 to 0.2 in the ratio against the 2.0 that a flipped sign produces.

## Preregistered decisions

All use the coin piles of a template's job (the coin read as the arm) and Z_RESOLVE = 3.0 standard errors; the readout-corrected statistic enters only the cross-platform and depth readings.
A bin whose sampled selector outcomes are deterministic in both arms has standard error 0 and counts as resolved when its contrast carries the ideal sign exactly
(`signed_z` in `gororoba_quantum/pathion_coset_analysis.py`) and each arm holds at least `DETERMINISTIC_MIN_COUNT` (5) shots in the bin, the least count at which a chance run of one outcome in both arms (probability at most 4^-n) falls below the
3-sigma one-sided tail; a deterministic bin with fewer shots decides nothing. The report lists deterministic bins under `deterministic_bins` with a null z.

1. Resolution: `ba` and `bb` each read the ideal sign at 3 standard errors on at least 6 of their 8 bins. Failure refutes "Tuna-17 realizes the compiled A_5 block map at 21 to 23 CZ"
   (predicted z 17.6 to 44.6).
2. Pattern: `ba` and `bb` read opposite signs at 3 standard errors in both bins (2 and 6) where their ideal c(y) carry opposite signs (`pattern_bins` selects them by the sign of the ideal contrasts); their selector contrasts agree to
   1e-4 by construction (0.5), so only the pattern separates the two cocycles.
3. Null: the `b0` selector contrast lies within 3 standard errors (0.012) of zero. The reported reference is the first series' coin-free +0.0167 +- 0.0055.
4. Cocycle-free control: the `xor_ba` selector contrast is negative at 3 standard errors and the `ba` contrast positive at 3 standard errors, each with a strict sign, so a zero contrast with zero standard error does not pass (predicted -0.57 to -0.60 against +0.17 to +0.22).
5. Depth, reported and not decided: the contraction per CZ implied by each primary's readout-corrected visibility, against 0.955 to 0.9654, with the routed CZ and the coin read fraction beside it.
   The correction removes the readout part of the coin factor; the relaxation part is unidentified from these data, so the reading is a lower bound.
6. Cross-platform: the readout-corrected D(y) of the previous section, at least 7 of 8 bins within 3 combined standard errors of zero for each of `ba`, `bb` and `b0`, against each of ibm_fez and ibm_marrakesh
   separately (both devices must hold).
7. Drift, a covariate: recorded per batch as in the rule change above; it stops nothing and enters no decision, and the analysis reports whether decision 6 holds under every bracket of the series
   (`drift_covariate.cross_platform_under_each_bracket`, `stable`).

Each decision has a refusal in the generator's `--self-test`: a cocycle-free circuit in the `ba` slot, a `b0` selector offset and a device at retention 0.02 fail the corresponding rule, an honest device at retention
0.5 passes every one (including the comparison with the measured IBM runs), and a 0.17 assignment move on a register qubit between brackets is recorded, flagged and corrected without a stop.
`tests/scripts/test_qi_pathion_coset_coin.py` scores synthetic series built from the ideal laws (a contracted device, a coin misread, a `bb` slot carrying the `ba` laws, a drifting bracket, a partial series, a short shot
list and the QX control) and exercises every refusal of `--submit-next`.

Mutation and null arms not in the series, with the reason: a single flipped SELECT sign (the IBM case carries it at six qubits; its block form moves the selector contrast by 0.25 and one bin pattern), the oracle of
another operand and the quarter-turn twin each cost another job for a question the cocycle-free control and the `ba` and `bb` pattern already answer at the first level.

## Command sequence after approval

1. `"$PYTHON" scripts/qi_pathion_coset_coin_cases.py --check results/quantum_inspire/cases`
2. QX dry run, one batch (the series gate copies the batch into
   `results/quantum_inspire/runs/<UTC stamp>-pathion_coset_coin_qx-batch-00/`, applies the shot checks and submits it through `qi_platform.submit`; QX needs no pause):
   `RUN=$("$QI_PYTHON" scripts/qi_pathion_coset_coin_series.py --submit-next results/quantum_inspire/cases/pathion_coset_coin_qx --approval "QUOTE")`
   then `"$QI_PYTHON" scripts/qi_platform.py collect "$RUN" --poll 15 --timeout 3600`. Analyze with
   `"$PYTHON" scripts/qi_pathion_coset_coin_cases.py --analyze results/quantum_inspire/runs/*-pathion_coset_coin_qx-batch-* --out results/quantum_inspire/pathion_coset_coin_qx_analysis.json`;
   its `qx_control.pass` gates the hardware series.
3. Tuna-17 batches 00 to 03, the same two commands with the hardware series and the control analysis, four times:
   `RUN=$("$QI_PYTHON" scripts/qi_pathion_coset_coin_series.py --submit-next results/quantum_inspire/cases/pathion_coset_coin_tuna_17 --control results/quantum_inspire/pathion_coset_coin_qx_analysis.json --approval "QUOTE")`
   then `"$QI_PYTHON" scripts/qi_platform.py collect "$RUN" --poll 15 --timeout 3600`. Before it sends, `--submit-next` requires every earlier batch collected with completed jobs, full shot lists
   and case bytes equal to the series, waits out the account's hardware pause (30 s, raised one step through `QI_HARDWARE_PAUSE_SECONDS` after a platform failure, which stops the series) and writes
   `series-gate.json` (with the drift record of the collected brackets) into the run directory. `--sanity RUN_DIR...` prints the drift record and exits 0 whatever it holds.
4. `"$PYTHON" scripts/qi_pathion_coset_coin_cases.py --analyze results/quantum_inspire/runs/*-pathion_coset_coin_tuna_17-batch-* --out results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json`
   scores the decisions, per-template c(y), visibility, N_hat and selector contrast, the comparison with both IBM devices and the drift covariate; a partial series reports its batches and drift record only.

## Not run and open

- Run: the first series' QX control (`results/quantum_inspire/runs/2026-11-06T221242Z-pathion_coset_block_qx-batch-0{0..7}`, batch jobs 922207 to 922220, 2048 shots) and its
  Tuna-17 batches 00 to 03 (`results/quantum_inspire/runs/2026-11-06T221626Z-pathion_coset_block_tuna_17-batch-0{0..3}`, batch jobs 922223, 922226, 922229 and 922232, 16384 shots), after
  which the drift stop ended the series; the coin series above. The IBM comparison uses the measured ibm_fez and ibm_marrakesh records and needs no further job.
- Open before a merge: a gate entry in `ci/gates.json` for `--check` and `--self-test` of the generator and for
  `tests/gororoba_quantum/test_pathion_coset_block.py` and `tests/scripts/test_qi_pathion_coset_coin.py`; the QX local replay record. The generator pins four of the first series'
  readout files and the `b0` arm files by sha256 (`STOPPED_FILES`) and refuses `--write` and `--check` when one is missing or changed.
- Residual risk: the coin is a new circuit element whose arm-dependent effects only the null decision reads (the first series' coin-free `b0` reading of +0.017 is the reference). q2 couples to q4 at +4.1 kHz, so a
  coin in |1> shifts q4's phase relative to |0> by about 0.03 rad per microsecond of idle; the null block and the cross-platform ratio would show it.
- Residual risk: the assignment correction takes each bracket as the state of its batch's data job; the bracket's two circuits and the data job run minutes apart inside one batch, and q11's e10 moved by 0.17 between
  two batches of the first series, so a move inside a batch reaches the corrected ratio unseen, and the covariate reports only moves between batches.
- Residual risk: q8 is the star center and no retained single-qubit record covers q8 beside q2, q4, q11 and q12 at once; the readout assignment above is from the first series' calibration and the series measures its own; the
  model's per-CZ contraction treats every error as depolarizing; the 0.02 flag threshold of the drift covariate is informational.

## Amendments after data (2026-11-07)

The rules above are the preregistration the owner approved on 2026-11-06 and stay as written. These amendments came
after the coin series ran, from the local review of PR #774; none changes a retained verdict (the coin Tuna-17 null
reads `fails` and its cross-platform rule `fails` with or without them; the retained standard errors sit within the floor).

- The null (rule 3) and each cross-platform bin also require a standard error no worse than twice its design value.
  Precision floor (`PRECISION_FACTOR` = 2 in `gororoba_quantum/pathion_coset_analysis.py`, shared by both analyzers). A null "holds" and a cross-platform bin "within" accept a departure up to 3 standard errors, so a run
  with a larger standard error accepts a wider departure; failure to reject zero is not agreement. Each of the two verdicts therefore also requires the measured standard error to stay within twice its design
  value, the larger of the two RHO_BAND ends of this case's `prediction.json` (`templates.b0.rho_*.selector_se`; `cross_platform.templates.<template>.<device>.rho_*.readout_corrected.se`, which carries the
  IBM replica spread), scaled by the root of the forecast's shots over the run's shots. At the hardware forecast's shots the factor bounds the 3-standard-error acceptance half-width at six design standard errors: 0.023 on the `b0` selector
  (an aligned pair gives 0.5 times the visibility, about 0.16 or more here) and at most 0.44 on a ratio bin (the largest design combined error is 0.074; a wrong label differs by about 1), so the verdict still excludes the effects the rule exists to exclude,
  and a run that reaches the forecast's precision is never refused. The QX twin runs 2048 shots and scales the design by 2.8 (16384-shot circuits) or 5.7 (65536-shot circuits), which widens its bound by the same factor; it is a control of the
  analysis path. A verdict whose precision fails reads `uninformative` (`decisions.null.outcome`; `outcome` of each cross-platform cell, device and total, with `precise` and `bins_within_unfloored` in each cell)
  and leaves `all_decisions_met` false. The resolution, pattern and cocycle-free rules reject zero and need no floor. The analysis reads each batch through `qi_records` (receipt, job and batch identities, raw shots
  against the recorded histogram), rejects a duplicate batch, and writes null for a statistic that is undefined (zero visibility, no readout circuit); `--out` refuses a non-finite number.
- The analysis tests add a run with three times the design standard error, which reads `uninformative`.
- Wording for any interpretation: a null or cross-platform bin that passes means no disagreement detected at 3
  standard errors, not agreement; the floor bounds the acceptance half-width but sets no equivalence margin.
- The QX control analyses that the series gate checked before each Tuna-17 submission keep their bytes, since the
  `series-gate.json` receipts bind them (`results/quantum_inspire/pathion_coset_block_qx_analysis.json`,
  `pathion_coset_coin_qx_analysis.json`). Their successors under the amended analyzer,
  `results/quantum_inspire/pathion_coset_block_qx_analysis.v2.json` and `pathion_coset_coin_qx_analysis.v2.json`, keep
  `qx_control.pass` true, so each gate decision holds under the corrected rules.
- Derived analyses of this series come from the pinned CI interpreter (ci-py3.14.7); against the build host's
  /usr/bin/python every verdict, flag and text field agrees and floats differ by at most 1e-12.

## Successor: the selector offset of the null block

The coin series' null block b0 read a raw selector contrast of +0.0164 +- 0.0039. The successor case
[pathion_one_cz_null_tuna_17](../../../results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/CASE.md) replays b0 byte
for byte, adds the three 6-CZ blocks k4, k8 and k12 (selector q8 and coin q2 held) and a joint readout characterization of
the coin q2, the selector q8 and q12, with preregistered decision rules for the coherent over-rotation of ledger row A5-186
against a coin-conditioned or q12-correlated selector readout. Its generator is `scripts/qi_pathion_one_cz_null_cases.py`
and its QX twin `pathion_one_cz_null_qx`; the owner approved both on 2026-11-07, both series are retained under
`results/quantum_inspire/runs/`, and the Tuna-17 series read `unresolved_batch` under the preregistered rule
(`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json`).
