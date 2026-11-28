# IBM Heron r2 machine capabilities: ibm_fez, ibm_kingston, ibm_marrakesh

This note collects what each of the three Heron r2 backends of the account reaches today, what a job can program on it,
what each retained run measured on it, and what no record states. It extends [ibm_heron_platform.md](../ibm_heron_platform.md)
(documentation pages and the 2026-10-14 Target snapshot), [hardware-controls.md](hardware-controls.md) (every control the
repository reaches), [qpu-submission.md](qpu-submission.md) (quota, approval and calibration binding) and
[heron-r2-readout-resonator.md](heron-r2-readout-resonator.md) (public readout evidence); it repeats a fact only where the
fact has no other home. The procedure that uses it is the `program-ibm-heron` skill of gororoba-infrastructure
(`agent-config/skills/program-ibm-heron/`) with one thin skill per machine.

Evidence classes. **read** is a value of the read of 2026-11-28T05:50Z, retained in
[targets-v2.json](../../evidence/heron_platform/targets-v2.json) by `scripts/heron_target_snapshot.py`
(qiskit 2.6.2, qiskit-ibm-runtime 0.51.0; calibration reads, Target, usage and queue length
only; no job was submitted, cancelled or created). **doc** is a statement of IBM's documentation as
[ibm_heron_platform.md](../ibm_heron_platform.md) cites it. **run** is a value measured on a retained job, named by its record
under `results/live/`. **inf** is an inference with its discriminating check. A calibration is a property of the moment:
every **read** value below moves with the next calibration cycle (monitoring about hourly, recalibration under two hours a
day), so a case reads the Target again in the process that submits (`AGENTS.md`, "QPU time and calibration").

## 1. What the three backends share

All three report processor type Heron revision 2, 156 qubits, dt 4 ns, basis gates cz, id, rz, sx, x and xslow, and
`open_pulse` false (**read**; IBM removed pulse-level control on 3 February 2025). The coupling graph is the same
heavy-hex lattice on each: 176 couplers, 352 directed CZ rows, degree histogram 8 qubits of degree 1, 100 of degree 2 and 48
of degree 3 (**read**; `coupling.degree_histogram`). The configuration reports `max_shots` 100,000 per PUB and
`max_experiments` 300 (the backend attribute `max_circuits` reads None), a repetition delay range of 0 to 2 ms with default
250 us, `dynamic_reprate_enabled` and `multi_meas_enabled` true, `measure_esp_enabled` false, and `supported_features`
dynamic_circuits, parameters, qasm3 and qobj (**read**). The configuration field `conditional` reads false while the Target
holds `if_else` and `store` is a supported instruction: dynamic circuits run through the Target's `if_else`, and the
legacy flag does not describe them (**inf**; the retained dynamic runs under section 6 settled on ibm_kingston and ibm_fez).

| Duration (ns) | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---|---|---|
| `sx` = `x` | 24.00 | 32.00 | 36.00 |
| `cz` | 68.0 to 88.0 (median 68.0) | 68.0 to 108 (median 68.0) | 68.0 to 96.0 (median 68.0) |
| `measure` | 1660 | 2180 | 2684 |
| `measure_2` | 1340 | 1380 | 1884 |

`xslow` lasts 1,000 ns on every qubit, reports the error of `x` and `sx`, and the preset transpiler never emits it
([ibm_heron_platform.md](../ibm_heron_platform.md#measured-targets), **doc** and 2026-10-14 read).
`measure_2` is shorter than `measure` on every backend (reported error higher on all three at the 2026-10-14 read; the median reads 0.0128 against 0.0101 on ibm_fez but 0.0095 against 0.0098 on ibm_kingston and 0.0154 against 0.0181 on ibm_marrakesh at the 2026-11-28 read, so the ordering is a property of the calibration and not of the platform); `reset` lasts as long as
`measure_reset`. The three backends differ in gate and readout durations (the table above), so one logical circuit has a
different schedule length on each; a layout comparison across backends compares schedules, not gate counts.

### Fractional gates

With `use_fractional_gates=True` the Target of each backend adds `rx` and `rzz` (**read**). Medians over 352 directed pairs:

| Fractional gate | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---|---|---|
| `rzz` duration median, maximum (ns) | 68, 116 | 68, 108 | 68, 140 |
| `rzz` error median (`cz` median) | 0.00286 (0.00245) | 0.00187 (0.00190) | 0.00326 (0.00277) |
| pairs where `rzz` error equals `cz` error | 2 of 352 | 8 of 352 | 2 of 352 |
| `rx` error median (`sx` median) | 0.000310 (0.000310) | 0.000249 (0.000249) | 0.000366 (0.000366) |

The documented range is `rzz(theta)` for 0 < theta <= pi/2 and `rx` for any theta, and a bound value outside it fails the job
(**doc**). A grep of the retained `record.json` files of `results/live/` finds no record that names fractional gates, so no
retained run exercised them (**read** of the tree, 2026-11-28); the claim that `rzz` is a free improvement over two `cz`
stays untested on hardware.

## 2. Quota and billing today

The primary account's `usage()` reads 67 s consumed of 600 s, 533 s remaining, over the
period 2026-10-31 to 2026-11-28 (**read**; instance e3de05b6901e, the 12-hex digest of its CRN). A
second saved account holds its own 600 s that quotas never pool with (`AGENTS.md`). The service holds the same 46 jobs the
2026-11-08 inventory lists for the primary account, so no primary-account job ran after 2026-11-07 (**read**,
`service.jobs(limit=None)` on 2026-11-28; the backup account was not read). Billing is QPU lock time: about 2 s per
sub-job plus (repetition delay + circuit) per execution ([qpu_run_economy.md](../qpu_run_economy.md); **doc** and **run**).
Settled charges of the retained jobs are in the next section and in [qpu-job-inventory.json](../../../results/live/qpu-job-inventory.json).

## 3. Fresh read per machine

| Item | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---|---|---|
| backend_version | 1.3.37 | 1.0.0 | 1.0.21 |
| calibration stamp (PST) | 2026-11-27 21:42:07 | 2026-11-27 21:31:16 | 2026-11-27 21:21:13 |
| qubits / dead qubits / healthy | 156 / 1 / 155 | 156 / 2 / 154 | 156 / 5 / 151 |
| dead qubits (sx error 1.0 or no T1 or T2; see below) | 72 | 121, 146 | 82, 94, 113, 119, 130 |
| couplers / dead / usable | 176 / 1 / 173 | 176 / 4 / 169 | 176 / 1 / 166 |
| dead couplers (cz error 1.0; see below) | 32-33 | 112-113, 130-131, 145-146, 146-147 | 113-119 |
| usable graph components (qubits) | 155 | 153, 1 | 147, 4 |
| qubits with readout error at least 0.1 | 6: 5, 53, 72, 83, 93, 148 | 4: 87, 113, 121, 146 | 14: 3, 31, 48, 51, 60, 68, 73, 81, 82, 83, 94, 113, 119, 130 |
| couplers with cz error at least 0.05 | 7: 27-28, 32-33, 63-64, 71-72, 72-73, 102-103, 148-149 | 9: 84-85, 85-86, 86-87, 111-112, 112-113, 120-121, 130-131, 145-146, 146-147 | 9: 40-41, 81-82, 82-83, 108-109, 109-110, 109-118, 113-119, 119-133, 130-131 |
| couplers above 3 x median cz error | 23 (threshold 0.00735) | 29 (threshold 0.00570) | 20 (threshold 0.00830) |
| queue (pending jobs) | 0 | 0 | 0 |

| Quantity, min / p10 / median / p90 / max | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---|---|---|
| T1 (us) | 7.71 / 72.2 / 130 / 203 / 318 | 22.9 / 135 / 258 / 362 / 490 | 6.67 / 83.0 / 157 / 266 / 367 |
| T2 (us) | 5.58 / 28.3 / 88.2 / 167 / 268 | 11.2 / 40.7 / 143 / 340 / 579 | 5.75 / 21.0 / 80.7 / 204 / 357 |
| readout error (`measure`) | 0.00244 / 0.00464 / 0.0101 / 0.0591 / 0.468 | 0.00269 / 0.00452 / 0.00977 / 0.0314 / 0.499 | 0.00146 / 0.00537 / 0.0181 / 0.0933 / 0.499 |
| `sx` error | 0.000116 / 0.000197 / 0.000310 / 0.000602 / 1.00 | 0.000105 / 0.000157 / 0.000249 / 0.000480 / 1.00 | 0.000132 / 0.000210 / 0.000366 / 0.000845 / 1.00 |
| `cz` error | 0.00133 / 0.00175 / 0.00245 / 0.0127 / 1.00 | 0.000827 / 0.00122 / 0.00190 / 0.00819 / 1.00 | 0.00108 / 0.00155 / 0.00277 / 0.0111 / 1.00 |

Dead rule. IBM's own flag is `BackendProperties.is_qubit_operational` and `is_gate_operational`, which `faulty_qubits()`
and `faulty_gates()` collect; each answers True where a row carries no `operational` property. The read counts rows that
carry it: 0 of 156 qubit rows and 0 of the gate rows on every backend (**read**, `operational_property_rows`), so the vendor
lists read empty because the flag is absent, not because every part works. The repository therefore counts a qubit dead when
the vendor flags it, its `sx` error equals 1.0 (the value the Target reports for a part calibration could not fit) or the
calibration reports no T1 or T2, and a coupler dead when the vendor flags a `cz` on it or its `cz` error equals 1.0 (our
rule; the 1.0 test and the T1 and T2 test are ours, not IBM's). The measured gap supports a sentinel test over a threshold:
the largest `sx` error below 1.0 is 0.0255, 0.0206 and 0.00404 and the largest `cz` error below 1.0 is 0.194, 0.189 and 0.142
on the three backends, so no value lies between 0.194 and 1.0, and `scripts/heron_target_snapshot.py --check` fails on a
snapshot whose largest error below 1.0 reaches 0.5.

Reading of the tables (**read**, with **inf** where marked):

- ibm_fez has one dead qubit (72, sx error 1.0, readout 0.47) and one dead coupler (32-33), and the other 155 qubits form one
  connected component. Its `cz` median error is 0.00245, between the other two backends'.
  It has the fastest `sx`, `measure` and `measure_2`, and the shortest T1 median of the three.
- ibm_kingston has the lowest median `cz` error (0.00190), the lowest median readout error and
  the longest T1 and T2 medians. Two dead qubits (121, 146) and four dead couplers leave qubit 120 as an island of one (its coupler to the
  dead qubit 121 is unusable), so the usable graph is 153 qubits plus that island. Kingston reports no T1 for 146.
- ibm_marrakesh has the highest median `cz` error, the highest median readout error and the slowest readout. Five qubits
  are dead or incomplete (82, 94, 113, 119, 130), fourteen have readout error of 0.1 or more, and the usable graph splits into
  147 qubits and an island of four (95, 99, 114, 115). A layout on marrakesh excludes those qubits by construction (`--exclude-qubits`).
- A coupler with `cz` duration above 68 ns is slower than the median by up to 40 ns (fez 10 rows, kingston 8, marrakesh 30 of
  352). **inf**: a longer pulse accompanies a coupler that needed a recalibrated pulse; no record separates the cause.
- The reported `readout error` and T1 describe the calibration run and not the shots of a job. Qubits 0 and 1 of ibm_kingston
  read a readout error of 0.0088 and 0.0066 in the calibration of 2026-10-15 while the job measured P(1|0) of 0.388 and 0.274
  ([ZERO_DIVISOR_AND_CORNER_FINDINGS.md](../../../results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md), **run**), and qubit 0
  of the same backend read e10 = 0.786 in a job against a calibrated 0.006
  ([PRIMORIAL_COHERENCE_FINDINGS.md](../../../results/live/PRIMORIAL_COHERENCE_FINDINGS.md), **run**). A case reads
  readout in the job (a readout pair beside the payload) and never rests on the reported value alone.

## 4. Dynamic circuits and timing

The Target holds `measure_2`, `measure_reset`, `measure_reset_2`, `reset_2` and `if_else` on all three backends (**read**).
The guide's limits (**doc**): one level of `if`, no nesting, no measurement or reset inside a conditional, operands of at most
32 bits, about 300 broadcasts of 60 bits or 2,400 of 1 bit per job. A job holds either static or dynamic circuits per result
group: the live_run.py planner refused a group that mixed them three times on 2026-10-13
([PATCH_WINDOW_FINDINGS.md](../../../results/live/PATCH_WINDOW_FINDINGS.md), **run**). The scheduler tables of 11 retained jobs give the feed-forward path in cycles
([feedforward-latency.json](../../evidence/heron_platform/feedforward-latency.json), **run**, backend_version unrecorded):
ibm_fez, 16 broadcasts over 5 jobs, 406 cycles per broadcast and 112 cycles from the end of the target measurement to the receive
step; ibm_kingston, 23 broadcasts over 6 jobs, 526 to 630 cycles and 102 to 206 cycles; the receive step takes 7 cycles on both. The latency-recovery run fixed L = 215 dt (0.86 us) on ibm_kingston
([LATENCY_RECOVERY_FINDINGS.md](../../../results/live/LATENCY_RECOVERY_FINDINGS.md), **run**).

## 5. Repetition delay

The configuration range is 0 to 2 ms and the default 250 us, and the changelog's floor is 20 us (**doc**). A delay of 0 us
passes the service range check and then stalls: two jobs on ibm_kingston stayed running 129 s and 207 s and ended in error
1305 ([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md), **run**). A 20 us delay ran
the measurement-sequence envelope (88 PUBs, 720,896 shots, 38 s charged) and the idle-penalty probe (44 PUBs, 16 s charged) on
ibm_kingston (**run**). A lower delay raises state-preparation error (**doc**), so a design takes the delay as a controlled
variable.

## 6. Retained runs by machine

Counts from the two inventories of 2026-11-08 ([primary](../../../results/live/qpu-job-inventory.json), [backup](../../../results/live/qpu-job-inventory.f59f9992321c.json)):

| Backend | Completed jobs | Settled seconds | Error and cancelled jobs | Dates |
|---|---:|---:|---|---|
| ibm_fez | 23 (14 primary, 9 backup) | 359 | none | 2026-10-13 to 2026-11-07 |
| ibm_kingston | 49 (26, 23) | 779 | 6 error (14 s and 4 s), 4 cancelled (0 s) | 2026-10-11 to 2026-11-07 |
| ibm_marrakesh | 2 (2, 0) | 42 | none | 2026-10-21 to 2026-11-06 |

Measured facts by backend (each row names its record):

| Backend | Run (job or record) | Seconds | Measured fact | Class |
|---|---|---:|---|---|
| ibm_fez | pathion full map (`dbn1tv8qtr0c73ac82eg`, [2026-11-06T183538.809814Z](../../../results/live/2026-11-06T183538.809814Z/collect.json)) | 18 | at 136 to 173 routed CZ the block visibility reads 0.09 to 0.24 against a calibrated model's 0.49 to 0.58; 0.50 to 0.59 at 48 to 50 CZ; a compounded excess of 0.990 per CZ fits the 48 CZ visibility; the visibility fell to about zero for m in {25, 27} on two placements | run ([PATHION_KERNEL_MAP_FINDINGS.md](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)) |
| ibm_fez | pathion coset-block map (`dbn3a55t7fqc73ais42g`, [2026-11-06T201037.234804Z](../../../results/live/2026-11-06T201037.234804Z/collect.json)) | 18 | blocks of 1 to 20 CZ read 0.76 to 0.87 visibility; 32 of 32 signs on all eight operands; readout-corrected N_hat within 0.15 of the integer; no m-dependent collapse, so the full map's loss came from depth | run (same findings file) |
| ibm_fez | parallel coset blocks, 17 placements (`dbnai2oqtr0c73acl9gg`, [2026-11-07T042521.359670Z](../../../results/live/2026-11-07T042521.359670Z/collect.json)) | 57 | 32 of 32 signs; nullity bands pass; null selector contrast fails on block k8; placement spread fails (slope and R squared); within-arm repeats pass | run |
| ibm_fez | ripple ([2026-10-13T025444.603480Z](../../../results/live/2026-10-13T025444.603480Z/collect.json)), rank sector ([2026-10-13T032011.664435Z](../../../results/live/2026-10-13T032011.664435Z/collect.json)) | 66, 31 | the box-kite contrast signs and rank-sector contrast signs hold; 35 of 37 packed-against-isolated controls pass the 0.10 margin | run ([CAMPAIGN_FINDINGS.md](../../../results/live/CAMPAIGN_FINDINGS.md)) |
| ibm_fez | patch window (three jobs, [2026-10-13T201757.782152Z](../../../results/live/2026-10-13T201757.782152Z/collect.json)); orbit and window arms (2026-10-13) | 25; 4 and 11 | the window context changes the orbit distributions with no resolved product-state Ramsey phase | run ([PATCH_WINDOW_FINDINGS.md](../../../results/live/PATCH_WINDOW_FINDINGS.md), [N21_ORBIT_RCA.md](../../../results/live/N21_ORBIT_RCA.md)) |
| ibm_fez | ground Ramsey sweep of qubit 143 ([2026-10-20T031212.175942Z](../../../results/live/2026-10-20T031212.175942Z/collect.json)); segmented coprime-swap sweep of the same qubit, 2026-10-21 | | the ground sweep shows two coherent lines of qubit 143 with weights 0.644 and 0.356; the beat is a candidate TLS or charge-parity mixture, and the segmented sweep of 2026-10-21 was built to separate them | run ([N21_Q143_COPRIME_SWAP_CASE.md](../../../results/live/N21_Q143_COPRIME_SWAP_CASE.md); the 2026-10-21 result is not restated here) |
| ibm_fez | wide coset blocks on 17 placements, group `pathion_wide_coset_d32` (`dbnk9noou4as73b4nn90`, backup account, [2026-11-07T153325.440007Z](../../../results/live/2026-11-07T153325.440007Z/collect.json)) | 9 | 12 PUBs at 18,816 shots; sign resolution 64 of 64 and 128 of 128; copy agreement fails for n64 (-0.994, z -11.42) and o64 (-0.172, z -5.61) and holds for m64 | run ([pathion_wide_coset_analysis.json](../../../results/live/pathion_wide_coset_analysis.json)) |
| ibm_kingston | folded QPE pilot and ladder (`db5qmqclf4us73c4e1ug`; 2026-10-12) | 9; 40 | hybrid Shor and folded QPE mod 15 ran as dynamic PUBs; the folded delay comparison is inconclusive and the correction adoption failed | run ([CAMPAIGN_FINDINGS.md](../../../results/live/CAMPAIGN_FINDINGS.md)) |
| ibm_kingston | corner baseline (`db87o48r1c5c738lu8jg`, [2026-10-15T070847.644554Z](../../../results/live/2026-10-15T070847.644554Z/collect.json)) | 4 | qubits 0 and 1 misassign the ground state 39 and 27 percent against a reported readout error below 1 percent; the zero-divisor fringe floor reads 2.2 times the model | run ([ZERO_DIVISOR_AND_CORNER_FINDINGS.md](../../../results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md)) |
| ibm_kingston | n21 feedback (`dba8r7k24mrc738527d0`, 2026-10-18; five jobs) | 48 | feedback changes no measured outcome: contrast difference +0.0027 [-0.0129, +0.0184], model +0.0344; four control jobs ended in error 1305 and billed 2 to 5 s | run ([N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md](../../../results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md)) |
| ibm_kingston | primorial coherence stage 1 (`dbfdotnpc3tc739n8nm0`, 2026-10-26) | 23 | qubit 0 voids the case (e10 0.786 against reported 0.006); stage 2 not sent | run ([PRIMORIAL_COHERENCE_FINDINGS.md](../../../results/live/PRIMORIAL_COHERENCE_FINDINGS.md)) |
| ibm_kingston | idle-penalty probe (`dbfrg3fpc3tc739o4kag`, 2026-10-26) | 16 | 44 PUBs on 31 coupled pairs at 4096 shots and 20 us delay | run ([IDLE_PENALTY_PROBE_FINDINGS.md](../../../results/live/IDLE_PENALTY_PROBE_FINDINGS.md)) |
| ibm_kingston | latency recovery (`dbf5kdom94ac738ssug0`, 2026-10-25) | 40 | 34 dynamic PUBs at 16,384 shots; L = 215 dt | run ([LATENCY_RECOVERY_FINDINGS.md](../../../results/live/LATENCY_RECOVERY_FINDINGS.md)) |
| ibm_kingston | measurement-sequence envelope (`dbg08t9j4t8s73abaghg`, 2026-10-27) | 38 | every one of 32 qubits fails the reset screen (median residual difference 0.0123); no device verdict | run ([MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md](../../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)) |
| ibm_kingston | rep_delay 0 controls (2026-10-18) | 2 to 5 | jobs ran 129 s and 207 s with no shot loop, error 1305 | run ([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md)) |
| ibm_kingston | wide coset blocks on 16 placements, group `pathion_wide_coset` (`dbnk9ndt7fqc73ajpfl0`, primary account, [2026-11-07T153325.886771Z](../../../results/live/2026-11-07T153325.886771Z/collect.json)) | 11 | 12 PUBs at 21,888 shots; sign resolution 64 of 64 and 128 of 128; target minus mutation reads 30.03 (D=64) and 62.09 (D=128); copy agreement holds on n64, o64 and m64 | run ([pathion_wide_coset_analysis.json](../../../results/live/pathion_wide_coset_analysis.json)) |
| ibm_kingston | parallel coset blocks, 16 placements (`dbnahh5t7fqc73aj7bdg`, [2026-11-07T042346.084449Z](../../../results/live/2026-11-07T042346.084449Z/collect.json)) | 32 | 32 of 32 signs; null N_hat, odd part and within-arm repeats fail; parallel crosstalk passes (90 percent interval inside 0.015) | run ([PATHION_KERNEL_MAP_FINDINGS.md](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)) |
| ibm_marrakesh | pathion coset-block map (`dbn38t0ou4as73b3q1n0`, [2026-11-06T200832.558771Z](../../../results/live/2026-11-06T200832.558771Z/collect.json)) | 24 | 11 replicas; 32 of 32 signs; block visibility 0.76 to 0.87; the two devices agree on every operand within their intervals; null operand reads +0.19 [0.03, 0.35] | run (same findings file) |
| ibm_marrakesh | qubit 47 baseline of the coprime-swap case (`dbc40u8c77vs7385ee0g`, 2026-10-21) | 18 | baseline Ramsey run before the fez qubit-143 question | run ([N21_Q143_COPRIME_SWAP_CASE.md](../../../results/live/N21_Q143_COPRIME_SWAP_CASE.md)) |

The A5-242 orientation-bit case ([pathion-kernel-map-orientation-bit.md](../../design/pathion-kernel-map-orientation-bit.md)) has
dry-run records and a compile case ([orientation-bit evidence](../../evidence/pathion-kernel-map/orientation-bit/case_compile.json))
and no submitted job; the ledger row waits on a written case. The device-agreement rules of the wide coset analysis read
`-0.302 against 0.523` (n64) to `-0.179 against 0.943` (m128) and are not restated here.

## 7. What we can program

Cost is the service's charge for a job of that shape; a new shape takes the planner's estimate and the settled charge of its first job as the measurement
([qpu_run_economy.md](../qpu_run_economy.md); the per-shot residual is in
[PATHION_KERNEL_MAP_FINDINGS.md](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md), parallel coset blocks). The size limit is the Target's or the guide's.
Every row rests on a retained run or on **doc** (marked); a row without a retained run is unexercised.

### 7.1 ibm_fez

| Primitive | Size limit | Cost (s) | Retained run | Known failure mode |
|---|---|---|---|---|
| static Sampler circuits (cz, sx, rz, x) | 155 healthy qubits, 300 circuits, 100,000 shots per PUB | 66 for 146 PUBs | ripple 2026-10-13 | calibration moves between plan and execution; the approved-record comparison refuses a changed plan |
| packed placements of one circuit | 17 placements of 4 qubits in one fused PUB (68 qubits per shot) | 57 at 16,384 shots, 112 PUBs | parallel coset 2026-11-07 | placement spread fails (slope and R squared); crosstalk passes within 0.015 |
| deep routed circuit (100+ CZ) | visibility 0.09 to 0.24 at 136 to 173 CZ | 18 | full map 2026-11-06 | m-dependent collapse on two placements; decompose to 1 to 20 CZ blocks |
| coset-block decomposition | blocks of 1 to 20 CZ | 18 | coset-block map 2026-11-06 | nullity-8 and nullity-12 operands carry blocks fixed by their signs (the estimator forces 4) |
| dynamic circuit on feed-forward | one `if` level, 32-bit operands | 4 and 11 | orbit and window arms 2026-10-13 | window context changes the orbit distribution; mixed static and dynamic groups are refused |
| wide coset blocks (D=64, 128) | 17 placements of four-qubit blocks, 12 PUBs at 18,816 shots | 9 | wide coset 2026-11-07 | copy agreement fails on n64 and o64 |
| long-lived Ramsey (qubit 143) | single qubit sweeps | see record | ground Ramsey 2026-10-20 and segmented sweep 2026-10-21 | two lines of weights 0.644 and 0.356 on qubit 143 |
| fractional gates | rzz in (0, pi/2], rx any angle (**doc**) | | none | out-of-range bound value fails the job; no twirling, PEC or PEA (**doc**) |

### 7.2 ibm_kingston

| Primitive | Size limit | Cost (s) | Retained run | Known failure mode |
|---|---|---|---|---|
| dynamic Sampler (measure_2, if_else, reset) | one `if` level; 88 PUBs of 8,192 shots in one job | 38 | measurement-sequence envelope 2026-10-27 | every qubit fails the reset screen; no verdict |
| folded QPE and hybrid Shor | six dynamic PUBs at 4,096 shots | 9 | pilot 2026-10-11 | the folded delay comparison is inconclusive |
| feed-forward with latency recovery | six physical qubits, 34 dynamic PUBs at 16,384 shots, 20 us or 50 us delay | 40 | latency recovery 2026-10-25 | the case's L = 215 dt holds only under the executed calibration |
| packed placements | 16 placements of 4 qubits | 32 at 8,192 shots | parallel coset 2026-11-07 | null N_hat and odd part fail |
| wide coset blocks (D=64, 128) | 16 placements of four-qubit blocks, 12 PUBs at 21,888 shots | 11 | wide coset 2026-11-07 | none of the copy-agreement rules fails |
| coherence probes on a path | 98 circuits at 800 shots on three qubits | 23 | primorial coherence 2026-10-26 | a wire with readout assignment factor below 0.8 voids the case (qubit 0) |
| readout and Ramsey baseline | 6 qubits, 1,024 shots | 4 | corner baseline 2026-10-15 | qubits 0 and 1 carry a readout fault the calibration omits |
| idle-penalty pairs | 31 coupled pairs, 44 PUBs | 16 | idle-penalty probe 2026-10-26 | exposure gate before any readout verdict |
| repetition delay 0 | none | n/a | two controls 2026-10-18 | accepted by the service, never runs a shot loop, error 1305 |

### 7.3 ibm_marrakesh

| Primitive | Size limit | Cost (s) | Retained run | Known failure mode |
|---|---|---|---|---|
| coset-block map | 11 replicas of blocks of 1 to 20 CZ | 24 | coset-block map 2026-11-06 | the null operand reads +0.19 and the 1-CZ blocks +0.05 after correction (open) |
| single-qubit Ramsey baseline | qubit 47 | 18 | 2026-10-21 | none recorded |
| any layout | 151 healthy qubits in components of 147 and 4 | | | the 14 qubits with readout error of 0.1 or more and the dead couplers need exclusion |

Marrakesh has two retained jobs and no dynamic-circuit run, so every dynamic-circuit primitive there is unexercised (**inf**
from the Target's `if_else`, which `ibm_kingston` runs).

## 8. Facts this note could not source

- Backend version history: the configuration reports a version string only
  ([heron-r2-readout-resonator.md](heron-r2-readout-resonator.md#1g-backend_version-history-not-public)).
  Kingston reads backend_version 1.0.0 today; no record says when it was assigned.
- Queue wait: `pending_jobs` is the count of the service status; no wait time per backend is read (see
  [qpu-submission.md](qpu-submission.md#queue-depth-and-wait)).
- A retained run that exercises `xslow`, `stretch`, `rzz` or a second saved-account job on marrakesh: none found.
- The cause of a coupler's longer `cz` pulse, and the cause of the weak qubits' T1: no record states either.

## 9. Regeneration

```sh
GOROROBA_IBM_ACCOUNT= "$PYTHON" scripts/heron_target_snapshot.py --out docs/evidence/heron_platform/targets-v2.json
"$PYTHON" scripts/heron_target_snapshot.py --check docs/evidence/heron_platform/targets.json docs/evidence/heron_platform/targets-v2.json
```

`--check` (gate core-254) recomputes the platform facts of each file, and for `targets-v2.json` also the summary, the coupling
and the health block from the retained per-qubit values. The 2026-10-14 snapshot
[targets.json](../../evidence/heron_platform/targets.json) keeps its bytes because retained records cite its sha256 (the
`algebra-device-conjectures-*` manifests, the pathion orientation-bit case, `gororoba-retained-runs.json` and others), so a
refresh lands in the versioned successor `targets-v2.json`, which adds the calibration distributions, the health block and the
queue and usage context.
