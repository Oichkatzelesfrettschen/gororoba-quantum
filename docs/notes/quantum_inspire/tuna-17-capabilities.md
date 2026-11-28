# Tuna-17 capabilities: a programmability reference

This note collects what a Tuna-17 job can be programmed to do, each capability with its limit, its cost and the retained run
that exercised it, beside the live read of 2026-11-28 and the measured anomalies. It extends [tuna-17.md](tuna-17.md) (result
registers, readout drift, operating rules), [platform-facts.md](platform-facts.md) (per-backend constraints by source),
[tuna-17-run-design.md](tuna-17-run-design.md) (batch cost and packing) and [usage.md](usage.md) (queue and pause rules), and
repeats a fact only where it has no other home. The procedure that uses it is the `program-quantum-inspire-tuna17` skill of
gororoba-infrastructure (`agent-config/skills/program-quantum-inspire-tuna17/`).

Evidence classes. **read** is a value of the free reads of 2026-11-28T05:24Z through the `quantum-inspire` MCP tools
(`qi_hardware_status`, `qi_backend`, `qi_backends`, `qi_jobs`, `qi_performance_dashboard`, `qi_performance_query`);
no job was created, compiled or submitted. **doc** is a statement of the platform's captured pages
([platform-facts.md](platform-facts.md)). **run** is a value measured on retained runs under
`results/quantum_inspire/`. **inf** is an inference with its discriminating check.

## 1. The device today (read)

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
readout and T1 circuits of the retained runs (section 3).

Native durations (**doc**, [platform-facts.md](platform-facts.md)): 20 ns single-qubit gates, 60 ns CZ, 800 ns measurement,
500 or 200 us initialization, angles in multiples of pi/36, one `wait` cycle 20 ns. The dashboard's dated notice states a
300 ns readout duration from 23 May 2026 (**doc**, same observation record); the two figures differ and no record decides
which the device runs (**inf**; the answer needs the provider).

## 2. Cost, queue and pause rules

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

## 3. Measured figures from the retained series

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

## 4. What we can program

| Primitive | Size limit | Cost (s) | Retained run | Known failure mode |
|---|---|---|---|---|
| Single-qubit rotations (X90, Y90, Rx, Ry, Rz, S, T) | 17 qubits; angle multiples of pi/36 | 20 ns per gate | every series | an unquantized angle is rounded by the stack (**doc**) |
| CZ on the 24 couplers | depth set by the 0.955 to 0.9688 retention per CZ: about 20 to 22 CZ for a block of 0.5 visibility (**inf**, 0.9688 to the 21st power) | 60 ns per CZ | coset blocks (20 to 22 CZ), box-kite ladder (depth 1 to 9), kernel cancellation (45 CZ) | the full map at 116 to 144 CZ and the 45-CZ kernel carry no resolved signal |
| Mid-circuit measurement and bit register | `bit[34]` on `qubit[17]` returns all 34 bits | per job | series P and Q ring-down | QX returns the measurement register only, so the QX twin lacks the mid-circuit bits |
| `reset` | measure then flip; no active-reset option | 800 ns measurement | ring-down | none recorded |
| `wait(n)` and `barrier` | n cycles of 20 ns | n x 20 ns | T1 ladder (6 waits), ring-down arms | the stack schedules as late as possible, so a barrier fixes an order |
| Readout pair (all 17 prepared in 0 and in 1) | one circuit each, up to 131,072 shots | about 12 s at 16,384 shots | every series | context-dependent assignment error (q13 reads e10 0.090 beside 17 excited and 0.044 beside idle neighbors) |
| Parallel witnesses on disjoint pairs | up to 15 packed witnesses in 7 batches | 7 batches plus pauses | box-kite follow series 2026-10-17 | batch-to-batch scatter about 0.03 at depth 9 |
| Raw per-shot lists | one bit string per shot | none | every series | a 50 Hz line rides the shot order (section 5) |
| Batch of 3 circuits (legacy) or 5 (wave-v1) | queue 1 or 3 batches | 30 s or 60 s pause per wave | all series | an early submit is refused before any remote write |
| Repetition delay, initialization time, active reset, calibration read | not offered | | none | the job accepts `number_of_shots` and `raw_data_enabled` only |

## 5. Measured anomalies

1. **Readout faults between runs.** q9 read P(1|0) 0.026 to 0.027 and then 0.271 to 0.288 from the first recalibration batch
   onward; q0 and q6 read P(1|1) 0.847 and 0.670 and then 0.393 and 0.144; the box-kite batch of the same afternoon read them
   0.973, 0.957 and 0.018, so the fault cleared ([tuna-17.md](tuna-17.md), **run**). A series that corrects each batch carries
   its own readout pair.
2. **A 50 Hz line in the shot order.** The line appears in 72 of 159 jobs before 2026-10-18 and none of 113 QX jobs, and in 21
   of 165 later jobs; it reaches an amplitude of 0.43 in P(1) on q7 and appears in Ramsey, CZ-ladder, walk, additivity and Walsh
   circuits and in none of the 51 readout circuits ([tuna_17_shot_record_line.json](../../../results/quantum_inspire/tuna_17_shot_record_line.json),
   **run**). The mechanism is a chip-wide modulation at the mains frequency (**inf**; no retained probe separates flux
   pickup from another 50 Hz path).
3. **Null selector offset.** The null block b0 reads a constant 0.014 that drifts between jobs plus 0.025 cos(theta) over the
   line's phase theta ([tuna17-null-rotation-scan-line-phase.md](tuna17-null-rotation-scan-line-phase.md), **run**); the phase
   scan of 2026-11-21 ends `none_adequate`.
4. **Non-exponential T1.** A single exponential fails on 15 of 17 qubits and the interleaved pooled tail test reads
   `not_confirmed` with no admissible fit on 16 qubits ([tuna17-interleaved-characterization-2026-11-20.md](tuna17-interleaved-characterization-2026-11-20.md), **run**).
5. **Drive-and-readout context.** 29 of 98 crosstalk contrasts exceed |z| 3.49 on 15 qubits, the largest at the 256-pulse X90
   ladder of q15 (z 44.1) (same note, **run**).
6. **Dashboard and API disagree.** The compute API reads `executing` and the Status dashboard `Idle` for Tuna-17 in the same
   minute (**read**); the admission gate reads the compute API's status and the account's own queue ([tuna17-interleaved-submit-gate.md](tuna17-interleaved-submit-gate.md)).
7. **A service-side job failure.** The account's job list of 2026-11-24 holds a failed job whose message reads "Quantum backend
   error: Inter-kernel communication: execution failed ... OSError [Errno 28] No space left on device"; the sibling jobs of
   its batch completed in 12 and 10 s (**read**, `qi_jobs`). The failing side is the platform's.
8. **Calibration datasource outage.** The calibration panels have timed out since at least 2026-10-27
   ([observations](../../evidence/tuna-projector-geometry/README.md)) and still time out on 2026-11-28 (**read**).

## 6. Facts this note could not source

- Any provider calibration figure for 2026-11-28 (T1, T2, gate or readout error): the datasource is unreachable and the API
  has no route.
- The readout duration the device runs (800 ns or 300 ns) and the initialization time in force.
- Whether the shot order is execution time: the line's period grows with circuit length, which argues for wall-clock time, and
  no retained probe separates the source ([tuna-17.md](tuna-17.md#shot-order-a-50-hz-line)).
