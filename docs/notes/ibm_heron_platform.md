# IBM Heron r2 platform: measured Targets and current documentation

Tag convention: [P] marks documentation statements; [M] marks values read
from the live Targets; [I] marks repository interpretation.

## Measured Targets

[M] `scripts/heron_target_snapshot.py --out` read the three backends the
account reaches at 2026-10-14T21:00:38Z with qiskit 2.5.2 and
qiskit-ibm-runtime 0.50.0, plainly and with `use_fractional_gates=True`, and
retained per-qubit durations and errors in
[targets.json](../evidence/heron_platform/targets.json). Gates core-254 and
core-255 recompute the facts block from those values. The table gives
medians over 156 qubits (352 pairs for two-qubit gates); durations in ns.

| | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---:|---:|---:|
| calibration stamp (PDT) | 06:30:22 | 13:06:33 | 13:21:55 |
| `measure` duration / error | 1660 / 0.0114 | 2180 / 0.0096 | 2684 / 0.0159 |
| `measure_2` duration / error | 1340 / 0.0154 | 1380 / 0.0107 | 1884 / 0.0206 |
| `measure_reset` = `reset` duration | 1684 | 2212 | 2720 |
| `measure_reset_2` = `reset_2` duration | 1364 | 1412 | 1920 |
| `x` = `sx` duration | 24 | 32 | 36 |
| `xslow` duration | 1000 | 1000 | 1000 |
| `x` = `sx` = `xslow` reported error | 0.00030 | 0.00026 | 0.00040 |
| `cz` duration / error | 68 / 0.00268 | 68 / 0.00215 | 68 / 0.00287 |
| `rzz` duration / error | 68 / 0.00292 | 68 / 0.00205 | 68 / 0.00425 |
| pairs where `rzz` error equals `cz` | 6 of 352 | 8 of 352 | 10 of 352 |

[M] All three: processor type Heron revision 2, dt 4 ns, timing constraints
granularity 1, min_length 2, pulse_alignment 1, acquire_alignment 1,
default repetition delay 250 us, `rep_delay_range` [0, 2 ms], basis gates
cz, id, rz, sx, x, xslow, and supported instructions that include
`measure_2`, `measure_reset`, `measure_reset_2`, `reset_2` and `store`.
`rx` reports the `sx` error on every qubit. The preset transpiler at
optimization levels 1 to 3 emitted no `xslow` for a 5-qubit circuit of X,
SX, RX and CX gates. ibm_fez reported maintenance with 55 pending jobs
shortly before the read; its Target stayed readable.

[I] The `rzz` errors contradict the fractional-gates guide's statement that
the reported value is a copy of the non-fractional counterpart: the copy
holds for `rx`, not for `rzz` on these backends at this read. On ibm_fez and
ibm_marrakesh the median `rzz` error exceeds `cz`, so a fractional
decomposition is not a free improvement.

## Documentation pages and retrieval

Retrieved 2026-10-14T20:59:31Z with a Mozilla user agent. The SHA-256
identifies the HTML bytes served at retrieval; each [P] statement in the
table was confirmed present in those bytes. The documentation changes
without versioned URLs, so a later reading checks the live page.

| Page | URL | SHA-256 of retrieved HTML | Cited for |
|---|---|---|---|
| estimate-job-run-time | https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time | `a4f0a60ea234c9695d28a5f2fa80b4d158a94493d401d6736be0958439133492` | [P] "approximately 2s per sub-job"; a primitive job "may be divided into multiple sub-jobs"; `scheduler_timing` circuit time "is NOT the time used for billing"; session capacity is reserved "regardless of whether workloads are actively running"; a system error reports zero usage. |
| repetition-rate-execution | https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution | `c147427164b353b232a6253d09b7e6b3ac8d3b063be127dcf1865e67e527ded0` | [P] column-wise iteration over circuits and shots; "no guarantee on the order the circuits from PUBs are executed"; no guarantee that a job's circuits "run as a single batch"; `rep_delay_range` differs by QPU; a lower `rep_delay` raises state-preparation error. |
| calibration-jobs | https://quantum.cloud.ibm.com/docs/en/guides/calibration-jobs | `a57dfe7809b3acbb02f3aa2c71fcc193f550dce47da94900d68fa4433a1b984d` | [P] monitoring "approximately once an hour"; Heron calibration time "typically under two hours per day"; two jobs submitted together "might run under different calibration sets"; CZ and RZZ on Heron, ECR on Eagle. |
| fractional-gates | https://quantum.cloud.ibm.com/docs/en/guides/fractional-gates | `17b8966a79595c437d26ea39aec4e1ba1a0784616f4714106e4ac0d61c0e7d2c` | [P] `rzz` for 0 < theta <= pi/2, `rx` for any theta; out-of-range bound parameters fail the job; no Pauli twirling, PEC or PEA, TREX supported; reported error "is just a copy of the non-fractional gate's counterpart". |
| stretch | https://quantum.cloud.ibm.com/docs/en/guides/stretch | `543b6ebd3a9b47037e319bd026f5ed2103de3f37bd7528b303c69c841eb1f4a4` | [P] remainder "added to the first delay that uses the stretch"; resolved values through `stretch_values` and `scheduler_timing`. |
| qiskit-runtime-circuit-timing | https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-circuit-timing | `6654d2891601951373e41188d45eca47df84319963438a16497f30c1cb3da0d0` | [P] the experimental `scheduler_timing` flag; returned timing differs from billed QPU time. |
| processor-types | https://quantum.cloud.ibm.com/docs/en/guides/processor-types | `435ce1a65dbe4aade934a541107c6cab3da1c7caae7d9380e8075149cae25119` | [P] Heron r1 (133 qubits), r2 (156, heavy-hex, TLS mitigation), r3; Nighthawk r1 (120 qubits, grid) and r2. |
| execute-dynamic-circuits | https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits | `7e18b23fd8f570534820991de0877398de6f41f2ff87fcbc027ccb0a9b7fecda` | [P] `MidCircuitMeasure` (`measure_2`) recommended where supported; "Nested conditionals are not allowed"; operands "32 or fewer bits"; about 300 broadcasts of 60 bits or 2400 of 1 bit per job; `store` from runtime 0.47. |
| qiskit-ibm-runtime release notes | https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/release-notes | `e2da0245c08c60f3e514a3a7b78b1c7fede8241da232194071ae2e9f29007f77` | [P] 0.48: differing `pub.shots` across PUBs deprecated; 0.49: `MidCircuitReset`; 0.50: client-side `executor_sampler.Sampler`, top-level `max_execution_time`, `XSlowGate`, samplomatic 0.21.0 and ibm-quantum-schemas 0.12.20260921 floors. |

### Repetition delay floor and timeout codes

Retrieved 2026-10-18T20:32:46Z with a Mozilla user agent, under the same
rule as the table above.

| Page | URL | SHA-256 of retrieved HTML | Cited for |
|---|---|---|---|
| latest-updates | https://quantum.cloud.ibm.com/docs/en/guides/latest-updates | `b98468c783bcc61c59245d316ac070ad855da48fc744eacdcdfb2088f5de5605` | [P] February 2026: "we have expanded the allowable repetition delay time range from 20-500 µs to 20-2000 µs on our Heron and Eagle QPUs. The Nighthawk QPU delay time range continues to be 1000-4000 µs"; September 2026, ibm_phoenix (Nighthawk r2): "the default repetition delay is 1 µs (previously 250 µs)". |
| errors | https://quantum.cloud.ibm.com/docs/en/errors | `3f0075c500834ef96d5ad5f2b5f9b3ffb5fcb01bfb1e1ab209f3500a87b460c7` | [P] 1304 "Job {} exceeded the max_execution_time of {} seconds."; 1305 "Job {} ran longer than {}." with "Contact support."; 1602 "Supplied rep_delay is not in the supported backend range."; 8030 "Repetition delay ({0}) not supported."; 8038 "A timing error occurred during execution of the input circuits."; 8045 "A buffer overflow occurred during result collection." |
| max-execution-time | https://quantum.cloud.ibm.com/docs/en/guides/max-execution-time | `ada3410adb19db940e839f310097badb58cc429051f734d9549567b1348ee8be` | [P] the limit is the smaller of `max_execution_time` and three hours, "based on QPU usage (quantum usage only), not wall clock time". |
| execution options | https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/options-models-execution-options | `9cd0bb5050f990bf317dcda42579868b6eb7f94642af4b7fa908061c5360277e` | [P] `rep_delay` "must be from the range supplied by `backend.rep_delay_range`"; no minimum or note about 0. |

[I] The changelog's Heron floor of 20 us contradicts the [0, 2 ms]
`rep_delay_range` that the configuration of all three backends reports and
that the service's own range check (1602) applies: a 0 us job is accepted
and then fails at execution
([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md)).
A design below 50 us therefore takes the changelog's 20 us as the floor,
and the configuration's range only as the upper bound.

## Mapping to this repository

- [I] The Heron execution facts section of AGENTS.md states the rules these
  measurements and pages support; core-254 and core-255 hold the measured
  ones to the retained snapshot.
- [I] live_run.py already sets `max_execution_time` at the Sampler's top
  level, records the timing constraints in the calibration identity, and
  replays collected PUBs under the calibration at their execution start.
- [I] Backend identity is recorded data. qiskit-ibm-runtime 0.50.0 reports
  `backend_version` (X.Y.Z) on the backend configuration, the properties and
  the status, and `processor_type` (`family`, `revision`, optional
  `segment`) on the configuration only; `IBMBackend.refresh()` replaces the
  configuration and leaves the `BackendV2.backend_version` read at
  construction. `live_run.backend_identity` therefore reads both from
  `backend.configuration()`, and every backend summary (`backends`,
  `system_inventory`) and group record carries them; `--collect` adds each
  job's `backend_identity` with the properties' `backend_version` at every
  execution start. Neither field enters the approved-record comparison or
  the pre-submission reuse check, so a version change alone refuses nothing.
  `heron_target_snapshot.py --out` and `calibration_snapshot.py --export`
  write the same fields. The retained targets.json and calibration
  snapshots carry neither, and each checker accepts a snapshot without them.
- [I] The repetition-rate guide's ordering statements are why a shot-array
  lag statistic is not an inter-shot memory measurement
  (results/live/KINGSTON_ALGEBRA_CASES.md).
