# Tuna-17: capabilities, result registers, readout drift and operating rules

Tuna-17 (backend type 7, `tuna_17`) is the Quantum Inspire device the
repository runs its hardware cases on. This note collects what the retained
runs establish about its capabilities and limits (what a job can be programmed to do,
its cost and queue), its result format, its readout calibration, and the
procedures that kept a shared account's batches intact. Each statement names
the run, record or gate that carries its evidence; a statement marked
"inferred" has no retained probe behind it. The note extends [platform-facts.md](platform-facts.md)
(per-backend constraints by source), [tuna-17-run-design.md](tuna-17-run-design.md) (batch cost and packing) and
[usage.md](usage.md) (queue and pause rules), and repeats a fact only where it has no other home. The procedure that
uses it is the `program-quantum-inspire-tuna17` skill of gororoba-infrastructure
(`agent-config/skills/program-quantum-inspire-tuna17/`).

Evidence classes. **read** is a value of the free reads of 2026-11-28T05:24Z through the `quantum-inspire` MCP tools
(`qi_hardware_status`, `qi_backend`, `qi_backends`, `qi_jobs`, `qi_performance_dashboard`, `qi_performance_query`);
no job was created, compiled or submitted. **doc** is a statement of the platform's captured pages
([platform-facts.md](platform-facts.md)). **run** is a value measured on retained runs under
`results/quantum_inspire/`. **inf** (or "inferred") is an inference with its discriminating check.

## The device today (read 2026-11-28)

| Item | Value |
|---|---|
| Backend type | id 7, identifier `tuna_17`, on-premise, TU Delft, `is_hardware` true, `enabled` true, protocol version 2 |
| Status | `executing` on the compute API with heartbeat 05:23:59Z; the public Status dashboard panel 1 read Tuna-17 at value 0 (Idle) in the same minute |
| Queue | account scope: 0 jobs; global scope: 6 jobs, waits of 14 s minimum, 55 s average and 117 s maximum (other workers' jobs, which the repository never cancels); Tuna-5 and Tuna-9 read offline |
| Qubits and couplers | 17 transmons in a ninja-star layout, 24 flux-tunable couplers (48 directed pairs); degree 4 on qubits 4, 5, 8, 11, 12, degree 3 on 2, 7, 9, 14, degree 2 on the other eight |
| Coupler list | 0-1, 0-2, 1-4, 2-4, 2-5, 3-5, 3-6, 4-7, 4-8, 5-8, 5-9, 6-9, 7-10, 7-11, 8-11, 8-12, 9-12, 10-13, 11-13, 11-14, 12-14, 12-15, 14-16, 15-16 |
| Gate set | I, Rx, X, X90, mX90, Ry, Y, Y90, mY90, Rz, Z, S, T, Sdag, Tdag, H, CZ, init, measure, reset, barrier, wait |
| Compiler passes | decomposition only: SWAP2CZDecomposer then CZDecomposer; mapping, routing and optimization are empty |
| Shots | default 8,192, maximum 131,072 per job |
| Time and batching | `job_execution_time_limit` 300 s; 5 jobs per batch job; 5 batch jobs per queue |
| Raw data | `supports_raw_data` true: one bit string per shot |
| Calibration figures | none: every calibration panel of the Tuna-17 dashboard (T1, T2R, T2E, initialization, readout, QNDness, single-qubit gate, Bell-state error) failed its query on 2026-11-28 with a connection timeout from the dashboard to its calibration datasource; the dashboard definition is version 38, updated 2026-11-27T20:31:22Z, and carries the notice of 2026-10-22 that the latest performance data are withheld |

The compute API's OpenAPI definition lists no calibration route
([calibration-datasource-upstream-question.md](calibration-datasource-upstream-question.md); source observations in
[tuna-projector-geometry](../../evidence/tuna-projector-geometry/README.md)). The only calibration record is therefore the
readout and T1 circuits of the retained runs ([measured figures](#measured-figures-from-the-retained-series)).

Native durations (**doc**, [platform-facts.md](platform-facts.md)): 20 ns single-qubit gates, 60 ns CZ, 800 ns measurement,
500 or 200 us initialization, angles in multiples of pi/36, one `wait` cycle 20 ns. The dashboard's dated notice states a
300 ns readout duration from 23 May 2026 (**doc**, same observation record); the two figures differ and no record decides
which the device runs (**inf**; the answer needs the provider).


## Result registers

- Tuna-17 returns the full classical bit register. A `bit[34]` circuit on
  `qubit[17]` comes back as 34-character strings that carry every mid-circuit
  outcome (the series P and Q runs under `results/quantum_inspire/runs/`;
  claim `qi-tuna17-register-and-readout-state`). The readout ring-down
  analysis uses those bits for its postselection check.
- QX returns its measurement register, not the bit register (C21 in
  [qx-runs.md](qx-runs.md)), so a case that reads mid-circuit bits on
  Tuna-17 has no QX counterpart for them.
- The Ry emulator rejects any bit declaration and fails `measure` at compile
  ([ry-emulator.md](ry-emulator.md), gate core-385 over the three probe runs).
- QX and Tuna put qubit 0 at the rightmost character; the Ry emulator puts it
  at the leftmost (README.md, Binding rules, execution facts).

## Readout calibration drift

The platform publishes no calibration data, so the readout-0 and readout-1
circuits of the retained runs are the only calibration record. The device
context (`results/quantum_inspire/readout_ringdown_tuna_17_device_context.json`,
gate core-387) lists them per qubit in timestamp order; a change is located
only to the interval between two retained runs.

- q9 idle P(1|0) measured 0.026 to 0.027 in the coupler-map and series P
  batch-00 runs, 0.271 in the first series P recalibration batch, and 0.276 to
  0.288 in every later run through the three zero-divisor batches. The gates
  applied on the qubit in those circuits, so the shift is a readout or
  state-preparation change of the qubit.
- q0 and q6 prepared in |1> read P(1|1) of 0.847 and 0.670 after a 2 us wait
  in series P batch-00 and 0.393 and 0.144 in the recalibration run that
  follows the platform calibration. With no wait the zero-divisor batches
  read 0.565 and 0.163, so for q6 the loss does not grow with the wait: the
  readout of |1> collapsed. The implied-T1 formula of the device context
  assumes an unchanged assignment between runs and gives 14.2 us for q0 and
  5.5 us for q6 from the earlier pair only.
- q15 prepared in |1> read P(1|1) of 0.730 after a 2 us wait in series Q
  batch-00 and 0.914 after the same wait in the Q-recal-053951 run. With no
  wait it reads 0.975 to 0.979, so the 2 us wait cost 0.06 to 0.25 depending
  on the run. A single T1 cannot produce both (inferred: readout variability
  between runs).
- The platform's "calibrating" and "benchmarking" states hold queued jobs
  (observed through the hardware status read; the states are not retained, so
  no record carries their durations). The platform schedules them itself,
  and a job that meets one waits ([site/faq.md](site/faq.md), "automated
  tuning program"); the account-wide pause in `qi_platform.py submit` paces
  the account and is not needed for them.

- The fault cleared by the afternoon. The box-kite pre-T0 batch (jobs
  finished 15:38Z, after the platform benchmarking the operator observed at
  15:34Z) reads Q0 P(1|1) 0.973, Q6 0.957 and Q9 P(1|0) 0.018, against the
  morning's 0.39, 0.14 and 0.27 to 0.29; every qubit of the box-kite layout
  reads P(1|1) 0.912 to 0.975 and P(1|0) at most 0.045. Its double-X
  discriminator was not read, because its precondition requires the fault
  (claim `qi-tuna17-boxkite-pre-t0-readout-recovered`).

Consequence for the ring-down analysis: the preregistered rule inverts the
series' batch-00 readout assignment for every batch. Where the device drifts
after batch-00, a target's Ramsey visibility leaves [0, 1] (q6 at 1.08 in
series P, q15 at 1.28 to 1.46 in series Q) and its tail class rests on a
stale correction. A time-nearest calibration is a sensitivity analysis
outside the rule.

## Readout ring-down results

- Series P, targets Q0, Q4, Q5, Q6, Q10, Q11, Q12, Q16: verdict "not
  detected" (3 of 7 usable targets classify as tails); claim
  `qi-tuna17-readout-ringdown-P`, gate core-386.
- Series Q, targets Q1, Q2, Q3, Q7, Q8, Q9, Q13, Q14, Q15: verdict "not
  detected" (3 of 7 usable targets, Q9, Q14 and Q15, classify as tails,
  Q15 under the all-shot estimator only; Q7 and Q8 fail the 0.3 visibility
  floor); claim `qi-tuna17-readout-ringdown-Q`,
  gate core-430. Series Q uses one readout batch (Q-batch-00); the
  Q-recal-053951 run is a repeated calibration outside the analysis, because
  duplicate readout files raise.
- Neither series fits the tail model on its classified targets in general:
  the rule compares H2 with H1 and tests neither fit, so a tail class marks
  arm-to-arm structure beyond shot noise. Series Q fits H2 on Q9 alone
  (chi2 6.95 on 3 degrees of freedom).

## Sanity checks and exemptions

`qi_readout_ringdown_cases.py --sanity RUN_DIR` guards each series with a
readout-error ceiling (`--sanity-readout-error`, 0.35 for series Q) and
exempts named qubits (`--sanity-exempt`). An exemption covers every check on
the qubit: the series Q batch-01 mid-circuit P1 check kept failing on an
exempted qubit until the exemption reached that check.

## Runner and account rules

- A run directory that holds `submission.json` and no `results.json` is
  submitted and uncollected; `qi_platform.py collect` finishes it and no
  resubmit is ever needed. A runner refuses an existing run directory so a
  resumed series cannot write a batch's files into another run's folder.
- Process control reads the run directories, never a harness task-output
  file, whose lines are flushed late: a handover keyed to those lines can stop
  a runner moments after a submit.
- Token renewal, the paths that spend a login outside the repository's
  lock and the recovery by `qi login --force` are in
  [setup.md](setup.md#login-failures).
- Sessions that share the account alternate hardware batches at Ramsey-pair
  boundaries, paced by the account-wide pause (`HARDWARE_PAUSE_SECONDS`,
  [usage.md](usage.md#pause-escalation)). Series P and Q calibrate
  readout once per series, in batch-00 and in separate recalibration runs;
  batches Q-05 to Q-08 hold Ramsey arms only, so readout drift after the
  last calibration enters their correction unseen, as the stale Q15
  correction above shows. A series that must correct each batch for its
  own readout state carries a readout-0/readout-1 pair in every batch.
- The pause guard refuses an early submit before any remote write and prints
  the seconds left; the guard counts Ry jobs too, since Ry reports
  `is_hardware: true` ([ry-emulator.md](ry-emulator.md)). A series runner
  therefore retries a refused submit every 30 s, at most 10 times, and
  stops the series when the tenth attempt is refused; a retry never
  duplicates a batch, because the refusal precedes the submission-state
  checkpoint.

### Cost, queue and pause

- A Tuna-17 job takes about 2.6 s fixed plus 0.53 ms per shot, so 16,384 shots execute in 9.9 to 12.6 s and a full
  131,072-shot job in about 72 s (**run**, fit of [tuna-17-run-design.md](tuna-17-run-design.md); a shot lasts 400.7 to
  404.6 us at the 50 Hz line, the rest of the 0.53 ms is overhead).
- Every retained job shows `charged: 0` (**run**, [usage.json](../../evidence/quantum_inspire/usage.json)); the scarce
  resources are circuits per batch and batches per hour.
- The runner policy `legacy` queues one batch of at most 3 circuits and pauses 30 s (escalation ladder 30, 60, 90, 120 s)
  between waves; `wave-v1` queues 3 batches of at most 5 circuits and pauses 60 s ([usage.md](usage.md#queue-rules-the-faq-governs)).
  The pause clock is account-wide, the Ry emulator included.
- Every job on a provider waits for the owner's approval of a written case (`AGENTS.md`, "Hardware services"), and a
  Quantum Inspire hardware batch keeps its pause and queue limits.
- The Quantum Inspire credential stays outside every checkout, and the private gororoba-infrastructure repository records
  where it lives and which host submits. Only that host submits; every other checkout analyzes retained runs.
- A batch submitted while the device reads `calibrating` waits: batch 00 of the 2026-11-16 characterization sat 8 h 20 min
  from submission to execution ([tuna17-characterization-2026-11-16.md](tuna17-characterization-2026-11-16.md), **run**).
  Since 2026-11-21 the interleaved series admits a batch at status `idle` or `executing` with the account's own queue empty
  and refuses `calibrating` and offline ([tuna17-interleaved-submit-gate.md](tuna17-interleaved-submit-gate.md)).

## Box-kite T0 depth ladder

Three batches of the reduced two-label LCU of edge (1,10)(4,15) of kite 3
at CZ depths 1, 5 and 9 on the pairs (1,4), (10,13) and (12,14), 16384
shots per circuit, each corrected with its own batch's readout pair
(`results/quantum_inspire/box_kite_tuna_17_pre_t0_analysis.json`, gate
core-425; claim `qi-tuna17-boxkite-t0-depth-ladder`): C(1) = 0.954, C(5) =
0.857 and C(9) = 0.710 (standard errors 0.003), r = 0.9654 per CZ with 99%
interval [0.9638, 0.9671], inside the decision band [0.87, 0.97] as
preregistered and above the prediction [0.87, 0.96]. Every
batch passed its sanity checks, and the QX twins of the three witness
circuits read every replica exactly. C(1) lies above its preregistered
[0.72, 0.82] because that prediction carried the selector's readout factor
(about 0.87) while C(n) is readout-corrected; 0.82 / 0.874 = 0.94.

## Shot order: a 50 Hz line

The retained raw lists are in time order, and that order carries a line at
the 50 Hz grid frequency (`scripts/qi_shot_record_line.py`,
`results/quantum_inspire/tuna_17_shot_record_line.json`, gate core-426 and
gate `core-self-test-09` (`tests/test_cli_self_tests.py`); claim `qi-tuna17-shot-record-50hz-line`).

- A band scan at 0.019 to 0.021 cycles per shot finds it in 72 of 159
  Tuna-17 jobs and in none of 113 QX jobs before 2026-10-18, and in 21 of 165 later Tuna-17 jobs. On Tuna-17 it is absent from
  all 51 readout circuits, at up to 131072 shots, and all 8 depth-1 LCU
  circuits.
  It is present in Ramsey, CZ-ladder, walk, additivity and Walsh-exemplar
  circuits.
- Its amplitude in P(1) reaches 0.43 on q7 (ring-down Ramsey) and 0.39 on q5
  (coupler-ZZ Ramsey).
- In the follow series the three bright-edge selectors oscillate at 0.19 to
  0.26 at CZ depth 9 and 0.09 to 0.13 at depth 5, and stay below 0.0175 at
  depth 1. Within one job they share one phase on all three pairs.
- The ring-down arms differ only in a wait of tau cycles. Their peak
  frequency rises with tau at 50.4 +- 4.0 Hz, so the source runs in
  wall-clock time, not on the shot index.
- At 50 Hz one shot takes 402.9 to 404.6 us in the ring-down circuits and
  400.7 us in the follow series; the period grows with circuit length, which
  is the slope above. The fitted execution cost of 0.53 ms per shot therefore
  includes about 0.13 ms of per-shot time outside the repetition period.

The inferred mechanism is a chip-wide modulation of qubit frequency or flux
pulses at the mains frequency. No retained probe separates flux pickup from
any other 50 Hz path.

Consequences:
- A job's mean averages its outcome over the line's phase. Any contrast that
  depends on accumulated phase is lowered by an amount set by the modulation
  depth, and that depth can differ between batches.
- The shot index plus a per-job phase gives every shot its line phase. A
  demodulated analysis therefore recovers phase-resolved contrast from data
  a job already returns.
- Block stationarity (16 block means per bit; the smallest per-bit tail
  times the bits scanned) falls below 0.01 in 61 to 75 percent of the
  morning ring-down jobs and in 11 to 33 percent of the box-kite jobs. Within-job
  stationarity depends on the device's state, so each series checks it.

## Readout context

q13's |1> misassignment depends on what the rest of the chip is prepared in.
In the ladder series, readout-1 (all 17 excited) gives e10 = 0.090 and 0.086
and readout-iso-x (q1, q13, q14 alone) gives 0.044 and 0.040, about 45
standard errors apart; q1 and q14 read alike in both contexts (claim
`qi-tuna17-boxkite-ladder-readout-context`). The two circuits differ in the
neighbors' state at measurement and in the X pulses on the neighbors, so
state-dependent readout and drive crosstalk on q13's preparation stay
unseparated. A witness whose data qubit sits beside idle neighbors is
corrected with the isolated rate: on (10,13) the depth-1 coherence reads
-0.997 that way and -1.104 with readout-1. q10's e01 rises by about 0.012
beside an excited q13.

## Run design

[tuna-17-run-design.md](tuna-17-run-design.md) holds the platform
configuration that prices a Tuna-17 batch (decompose-only compilation, the
fitted 2.6 s per job plus 0.53 ms per shot, no published calibration) and the
box-kite follow series built on it: seven batches whose readout pairs bracket
fifteen packed witnesses, sized from T0's r, the readout drift across the T0
batches and the coupler-ZZ map (`docs/evidence/box_kite_follow_design/design.json`,
gate `core-record-check-05` (`tests/test_cli_record_checks.py`) and gate `core-self-test-09` (`tests/test_cli_self_tests.py`)). The series ran on 2026-10-17 from 23:08Z to
23:29Z with every preregistered decision as the census predicts: all six
classification rows, twist equality at |z| at most 2.44 in all four
crossovers, every depth-1 X coherence sign and both walk signs. Its results
section records the depth-9 batch-to-batch scatter of about 0.03, the drift
against T0 seven and a half hours earlier (-0.209 on (12,14) at depth 9) and
the context-dependent q13 readout error (claims
`qi-tuna17-boxkite-follow-crossover` and
`qi-tuna17-boxkite-follow-ladder-drift`).

## Kernel cancellation probe

The kernel cancellation series of 2026-10-23
([qi_cancellation_cases.py](../../../scripts/qi_cancellation_cases.py), claim
`qi-tuna17-kernel-cancellation`) ran a 45-CZ circuit on q4, q8, q11, q12 and
q14 with every rotation on the pi/36 grid, six batches of three circuits at
16384 shots, each batch submitted to collected in about four minutes. The
control q8 read e01 0.030 and e10 0.022. The bright vector, whose ideal odd
part is zero, carried a signed response of -0.0167 +- 0.0039, as large as
the kernel's -0.0222 at phi = pi/36, so a Tuna-17 case preregisters its
decision on the difference from a matched control
([principles](../topics/algebra-hardware-probe-principles.md)); this
series preregistered the kernel against zero, so its matched difference is a
post hoc reading. The kernel's
odd part implies a visibility of 0.134 through its batch pair's readout,
against Garnet's 0.36 at 37 CZ. A three-circuit batch holds one readout
reference, so a pair reads e01 in one batch and e10 in the other and neither
batch's own assignment factor is identified; the spread of the three e01 and
three e10 readings (factor spread 0.0024) enters every corrected error and
moves no decision. Each circuit of a batch runs as its own job
in an order the platform chooses: one listed +, -, -, + contrast ran +, -,
+, -, so an analysis reads the executed order from the jobs' start times.

## Measured figures from the retained series

| Quantity | Value | Run | Class |
|---|---|---|---|
| Readout P(1\|0), P(1\|1) over 17 qubits | 0.006 to 0.055 (mean 0.027), 0.911 to 0.985 (mean 0.959) | characterization 2026-11-16 | run |
| T1 over 17 qubits | 13.2 to 32.2 us, median 22.9 us; a single exponential fails on 15 of 17 qubits | characterization 2026-11-16 | run |
| CZ retention per gate | 0.9654 [0.9638, 0.9671]; C(1) 0.954, C(5) 0.857, C(9) 0.710 | box-kite ladder (core-425) | run |
| CZ contraction in the coin series | 0.9688, 0.9643, 0.9680 per routed CZ | coset coin series 2026-11-07 | run |
| Deep circuit | the A_5 full map routes to 116 to 144 CZ and does not resolve at 0.955 per CZ | [PATHION_KERNEL_MAP_FINDINGS.md](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md) | run |
| 45-CZ kernel cancellation | the ideal-zero bright vector reads -0.0167 +- 0.0039, as large as the kernel's -0.0222 | 2026-10-23 series | run |
| Jobs per hour | six batches of three circuits at 16,384 shots, about four minutes from submission to collection | kernel cancellation | run |
| Execution total of the interleaved series | 90 jobs, 688,128 shots, 643.2 s, 0 credits | interleaved characterization 2026-11-20 | run |

Retained series, each with its analysis record: coset blocks and coin arm
([pathion_coset_block_tuna_17_analysis.json](../../../results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json),
[pathion_coset_coin_tuna_17_analysis.json](../../../results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json)), the
one-CZ null ([analysis](../../../results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json), reads
`unresolved_batch`), the rotation scan 2026-11-15
([analysis](../../../results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json), `unresolved_none`), the phase
scan 2026-11-21 ([analysis](../../../results/quantum_inspire/pathion_null_phase_scan_tuna_17_analysis.json),
`none_adequate`), the box-kite follow and ladder series
([follow](../../../results/quantum_inspire/box_kite_tuna_17_follow_analysis.json),
[ladder](../../../results/quantum_inspire/box_kite_tuna_17_ladder_analysis.json)), the readout ring-down series P and Q (verdict
not detected), the characterization pair
([2026-11-16](../../../results/quantum_inspire/characterization_tuna_17_analysis.json),
[2026-11-20](../../../results/quantum_inspire/characterization_interleaved_tuna_17_analysis.json)), the kernel cancellation
([analysis](../../../results/quantum_inspire/kernel_cancellation_tuna_17_analysis.json)), the zero-divisor and Walsh series
([Walsh](../../../results/quantum_inspire/walsh_exemplar_tuna_17_analysis.json),
[visibility floor](../../../results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json)) and the exploratory
residual passes ([REPORT.md](../../evidence/hardware-residuals/tuna-quandela/REPORT.md)).

Cross-platform result of the coin series: the Tuna-17 block reads the A_5 sign network and not its XOR permutation, because the
selector contrast of the cocycle-free control flips from +0.2350 +- 0.0038 to -0.7181 +- 0.0054; the null block b0 reads
0.0164 +- 0.0039 (z 4.19) and the readout-corrected agreement with ibm_fez and ibm_marrakesh holds on 7 of 8 bins for b0 and bb
and on 5 and 6 of 8 for ba ([PATHION_KERNEL_MAP_FINDINGS.md](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md), **run**).

## What a job can be programmed to do

| Primitive | Size limit | Cost (s) | Retained run | Known failure mode |
|---|---|---|---|---|
| Single-qubit rotations (X90, Y90, Rx, Ry, Rz, S, T) | 17 qubits; angle multiples of pi/36 | 20 ns per gate | every series | an unquantized angle is rounded by the stack (**doc**) |
| CZ on the 24 couplers | depth set by the 0.955 to 0.9688 retention per CZ: about 20 to 22 CZ for a block of 0.5 visibility (**inf**, 0.9688 to the 21st power) | 60 ns per CZ | coset blocks (20 to 22 CZ), box-kite ladder (depth 1 to 9), kernel cancellation (45 CZ) | the full map at 116 to 144 CZ and the 45-CZ kernel carry no resolved signal |
| Mid-circuit measurement and bit register | `bit[34]` on `qubit[17]` returns all 34 bits | per job | series P and Q ring-down | QX returns the measurement register only, so the QX twin lacks the mid-circuit bits |
| `reset` | measure then flip; no active-reset option | 800 ns measurement | ring-down | none recorded |
| `wait(n)` and `barrier` | n cycles of 20 ns | n x 20 ns | T1 ladder (6 waits), ring-down arms | the stack schedules as late as possible, so a barrier fixes an order |
| Readout pair (all 17 prepared in 0 and in 1) | one circuit each, up to 131,072 shots | about 12 s at 16,384 shots | every series | context-dependent assignment error (q13 reads e10 0.090 beside 17 excited and 0.044 beside idle neighbors) |
| Parallel witnesses on disjoint pairs | up to 15 packed witnesses in 7 batches | 7 batches plus pauses | box-kite follow series 2026-10-17 | batch-to-batch scatter about 0.03 at depth 9 |
| Raw per-shot lists | one bit string per shot | none | every series | a 50 Hz line rides the shot order ([shot order](#shot-order-a-50-hz-line)) |
| Batch of 3 circuits (legacy) or 5 (wave-v1) | queue 1 or 3 batches | 30 s or 60 s pause per wave | all series | an early submit is refused before any remote write |
| Repetition delay, initialization time, active reset, calibration read | not offered | | none | the job accepts `number_of_shots` and `raw_data_enabled` only |

## Further measured anomalies

The readout faults between runs and the 50 Hz line are in the sections above and below; the later jobs add one count: the line appears in 21 of 165 jobs after 2026-10-18 ([tuna_17_shot_record_line.json](../../../results/quantum_inspire/tuna_17_shot_record_line.json), **run**).

1. **Null selector offset.** The null block b0 reads a constant 0.014 that drifts between jobs plus 0.025 cos(theta) over the
   line's phase theta ([tuna17-null-rotation-scan-line-phase.md](tuna17-null-rotation-scan-line-phase.md), **run**); the phase
   scan of 2026-11-21 ends `none_adequate`.
2. **Non-exponential T1.** A single exponential fails on 15 of 17 qubits and the interleaved pooled tail test reads
   `not_confirmed` with no admissible fit on 16 qubits ([tuna17-interleaved-characterization-2026-11-20.md](tuna17-interleaved-characterization-2026-11-20.md), **run**).
3. **Drive-and-readout context.** 29 of 98 crosstalk contrasts exceed |z| 3.49 on 15 qubits, the largest at the 256-pulse X90
   ladder of q15 (z 44.1) (same note, **run**).
4. **Dashboard and API disagree.** The compute API reads `executing` and the Status dashboard `Idle` for Tuna-17 in the same
   minute (**read**); the admission gate reads the compute API's status and the account's own queue ([tuna17-interleaved-submit-gate.md](tuna17-interleaved-submit-gate.md)).
5. **A service-side job failure.** The account's job list of 2026-11-24 holds a failed job whose message reads "Quantum backend
   error: Inter-kernel communication: execution failed ... OSError [Errno 28] No space left on device"; the sibling jobs of
   its batch completed in 12 and 10 s (**read**, `qi_jobs`). The failing side is the platform's.
6. **Calibration datasource outage.** The calibration panels have timed out since at least 2026-10-27
   ([observations](../../evidence/tuna-projector-geometry/README.md)) and still time out on 2026-11-28 (**read**).


## Facts this note could not source

- Any provider calibration figure for 2026-11-28 (T1, T2, gate or readout error): the datasource is unreachable and the API
  has no route.
- The readout duration the device runs (800 ns or 300 ns) and the initialization time in force.
- Whether the shot order is execution time: the line's period grows with circuit length, which argues for wall-clock time, and
  no retained probe separates the source ([shot order](#shot-order-a-50-hz-line)).
