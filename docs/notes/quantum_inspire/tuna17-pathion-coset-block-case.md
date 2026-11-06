# Written case: A_5 coset-block kernel map on Tuna-17

Status: the owner has approved executing this case; each submission quotes that approval (`--approval`). Nothing is
submitted yet. The QX dry run and each Tuna-17 batch follow the procedure in
[usage.md](usage.md#run-on-tuna-17), through the series gate of `scripts/qi_pathion_coset_block_series.py`. The case series is retained under
`results/quantum_inspire/cases/pathion_coset_block_tuna_17/` (hardware) and `results/quantum_inspire/cases/pathion_coset_block_qx/`
(emulator twin), built by `scripts/qi_pathion_coset_block_cases.py` from
`gororoba_quantum/pathion_coset_block.py`. The platform and program context is in
[the pathion kernel map record](../../evidence/pathion-kernel-map/README.md).

## What it measures

The pair-resolved kernel map of two-term operands e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5
(`gororoba_quantum/pathion_kernel_map.py`) restricts exactly to a coset block: for a subspace V of (Z/2)^5 that
contains m = i XOR j, the SELECT of the linear combination of unitaries maps the coset k0 + V onto the coset
(k0 XOR i) + V, so the uniform input with the orientation oracle splits into independent blocks. A block of
dimension 3 reads 4 XOR pairs and 16 of the 64 SELECT signs on three data qubits and the selector. Each block circuit is H on
the data, a diagonal (orientation oracle times the s = 0 SELECT sign), H on the selector, a diagonal on four qubits
(the ratio of the two SELECT sign tables), a CNOT from the selector onto data bit 0 and H on the selector. The two
orientations differ by a phase pi on data qubit 0, so they are one parametrized circuit with one routing. The
observable is the per-bin contrast c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) over the 8 output bins: +1 on both
bins of an aligned pair and (+1, -1) on a misaligned pair, so the bin signs are a readout of the compiled sign network
and not only of its count N_b of aligned pairs.

Blocks (plain names first, template keys in code font):

| Block | Operand | V = span | Coset k0 | Aligned pairs N_b | Ideal selector contrast | Ideal c(y), bins 0 to 7 |
|---|---|---|---|---|---|---|
| operand e1 + e18, nullity 12 (`ba`) | (1, 18, +1) | 19, 2, 12 | 1 | 2 | 0.5 | -1, +1, -1, +1, +1, +1, +1, +1 |
| operand e1 + e26, nullity 4 (`bb`) | (1, 26, +1) | 27, 2, 9 | 0 | 2 | 0.5 | -1, +1, +1, +1, +1, +1, -1, +1 |
| null operand e1 + e17, nullity 0 (`b0`) | (1, 17, +1) | 16, 1, 2 | 0 | 0 | 0 | -1, +1, -1, +1, -1, +1, -1, +1 |
| `ba` with every SELECT sign table replaced by its unsigned XOR permutation, the cocycle-free control (`xor_ba`) | (1, 18, +1) | 19, 2, 12 | 1 | not defined | -1 | -1 in all 8 bins |

(Ideal values are those of the circuits of record to the grid rounding, at most 0.004 away: `cases.json` carries them
to 6 digits.) `ba` and `bb` have one selector contrast, 0.5, and differ in bins 2 and 6, so the selector contrast alone
cannot separate their cocycles and the bin pattern does. Check of the restriction
(`tests/gororoba_quantum/test_pathion_coset_block.py`, Statevector, 37 cases): for every block and arm, the block law equals
|V| / 32 times the six-qubit law of `pathion_kernel_map.kernel_map_circuit` on the output coset to 2e-16 (also for the
cocycle-free law); the c(y) of the block equals the module's c(k) at the algebra index k = (k0 XOR i) XOR (sum of the
bin's bits times the basis) exactly; the four cosets of each V cover all 32 outputs once, their N_b sum to
`pathion_kernel_map.nullity` (2 + 2 + 4 + 4 = 12 for V = span(19, 2, 12); 2 + 2 + 0 + 0 = 4 for span(27, 2, 9); 0 for
span(16, 1, 2)), and the concatenated c(y) equals the full c(k).

## Why a simulation cannot answer it

The ideal laws are exact and checked three ways (Statevector of the logical block, Statevector of the rounded routed
circuit, local qxelarator on the emitted cQASM). The question is the device's: whether Tuna-17 keeps the sign pattern of
a degree-3 sign network at 20 to 22 routed CZ. The retained Tuna-17 points bracket that depth without covering it
(contrast 0.954, 0.857, 0.710 at 1, 5 and 9 CZ in the box-kite ladder, a fit of 0.9654 per CZ; 0.955 to 0.956 per CZ at
45 to 91 CZ in the kernel-cancellation and zero-divisor series; [tuna-17.md](tuna-17.md), [experiments.md](experiments.md)),
and the platform publishes no Tuna calibration to build a noise model on
([tuna-17.md](tuna-17.md#readout-calibration-drift)). The full six-qubit map routes to 116 to 144 CZ on the admitted qubits, where the same
retention predicts a per-output contrast of 0.1 to 1.3 percent against a per-bin standard error of 3.1 percent at 16384
shots, so the block is the largest piece of the map the device can resolve.

## Routing, seeds and qubits

- Admitted region: the connected 4-qubit regions off `qi_zero_divisor_cases.excluded_qubits()` (q0, q5, q6, q7, q9),
  off q15 (P(0|1) 0.270, [tuna17-bipartite-designs.md](tuna17-bipartite-designs.md)), whose inner couplers all have a retained
  residual coupling |J| of at most 10 kHz (`results/quantum_inspire/coupler_zz_tuna_17_analysis.json`, which excludes (1,4) at
  -19.3 kHz, (11,14) at -31.4 kHz and (12,14) at 10.4 kHz). Six regions remain. The region with the fewest routed CZ summed over `ba`, `bb`
  and `b0` is (4, 8, 11, 12), the star on q8 with couplers (4,8), (8,11) and (8,12) at -5.0, 6.6 and -0.7 kHz; the next
  regions cost 28, 30 and 28 CZ (sum 86 against 62).
- Seeds: every routing candidate takes its transpiler seed from the ANU QRNG draw
  `docs/evidence/anu_qrng/draw-2026-11-06T184327Z.json` (64 uint16 values, drawn 2026-11-06T18:43:27Z). Template slice t holds draw
  indices 16 t to 16 t + 15 (`ba` 0 to 15, `bb` 16 to 31, `b0` 32 to 47, `xor_ba` 48 to 63); every region of the search
  reuses the template's slice. The fewest-CZ candidate on the chosen region wins (ties: the lowest index): `ba` index 0,
  seed 31581; `bb` index 16, seed 53647; `b0` index 32, seed 3704; `xor_ba` index 48, seed 22884. The case manifest
  names the draw, so it owns the whole draw (`ci/seed_provenance.py --check` passes).
- Compilation: Qiskit transpile at optimization level 2 onto the region (basis cz, rz, sx, x), one compile per
  template with `ORIENTATION` unbound; both arms bind it by name, every rotation rounds to the nearest multiple of pi/36
  (Tuna applies the same grid), and the build refuses a pair of arms whose non-rotation operations or rotation sites
  differ. The ideal of record is the Statevector of the rounded routed circuit read through its final layout; it departs from the
  unrounded block law by at most 3.6e-4 in any probability.
- Routed CZ per circuit on the admitted qubits (the same for the plus and minus arm):

| Template | Routed CZ | Rz after rounding | Data qubits 0, 1, 2 and selector on physical qubits |
|---|---|---|---|
| `ba` | 20 | on grid | 4, 12, 11 and 8 |
| `bb` | 22 | on grid | 4, 12, 11 and 8 |
| `b0` | 20 | on grid | 12, 4, 11 and 8 |
| `xor_ba` | 4 | on grid | 12, 4, 11 and 8 |

  The cocycle-free control routes to 4 CZ against 20 for `ba`, so its visibility exceeds `ba`'s. Its decision uses
  the sign of the selector contrast (ideal -1 against +0.5), which separates the two at any visibility above 0.04,
  and it makes no depth comparison.
- Toolchain: `qi_toolchain_check.py` under the Quantum Inspire environment (libqasm 1.2.1, OpenSquirrel 0.9.1) analyzes
  and compiles all 48 new circuits with no error; 32 of them report a changed gate-sequence text because OpenSquirrel prints
  rotations to 8 significant digits (for example 1.48352986419518 to 1.4835299), 13 of the 3109 Tuna circuits retained before this case report the same kind of change.
- Local emulation: `qx_local_series.py` ran all 24 hardware-series circuits on qxelarator at 16384 shots; the total
  variation distance to the ideal law of record of the 16 arms ranges 0.0029 to 0.0132 against the 0.025 bound that
  `--qx-conformance` enforces (the sampling floor at 16 outcomes and 16384 shots is about 0.0125).

## Backend, shots, batches and seconds

- Backend: Tuna-17 (backend type 7, `tuna_17`) at 16384 shots per circuit, the shot count of the retained series; QX
  emulator (backend type 1) for the dry run at 2048 shots, its maximum.
- Series: 8 batches of 3 circuits (an arm pair and one readout circuit), 24 jobs, one batch queued at a time, each pair
  inside one batch so its minus and plus arm share a calibration:

| Batch | Template | Replicate | Arm order | Readout |
|---|---|---|---|---|
| 00 | `ba` | 0 | plus, minus | readout-0 |
| 01 | `bb` | 0 | plus, minus | readout-1 |
| 02 | `b0` | 0 | plus, minus | readout-0 |
| 03 | `xor_ba` | 0 | plus, minus | readout-1 |
| 04 | `ba` | 1 | minus, plus | readout-1 |
| 05 | `bb` | 1 | minus, plus | readout-0 |
| 06 | `b0` | 1 | minus, plus | readout-1 |
| 07 | `xor_ba` | 1 | minus, plus | readout-0 |

  Each template sees both readout references and each reference kind alternates along the series. The platform runs the jobs of a batch in
  an order of its own; the analysis reads the executed order from the provider start times and reports it.
- Limits applied ([usage.md](usage.md#queue-rules-the-faq-governs)): at most 3 circuits per hardware batch, no batch queued while another
  account job on a hardware type is unfinished, the FAQ's 3 queued jobs, a pause of 30 s between batches (60, 90 and 120 s after a platform failure),
  300 s per job, bracket drift stop at 0.02 between successive readout references of one kind (`qi_pathion_coset_block_series.py`
  `--submit-next` refuses the next batch after a flagged drift, and `--sanity` reports it after a collect).
- Own execution time: 2.62 s per job plus 0.534 ms per shot gives 11.4 s per job and 273 s for 24 jobs (up to 15.4 s
  per job, 370 s, at the slowest retained per-job time); 7 pauses add 210 s (840 s at the 120 s step), so the series
  needs 8 to 20 minutes of its own time.
- Queue and calibration: the global Tuna-17 queue held 48 jobs at 18:37:39Z with a mean wait of 5426 s and a maximum of 56324 s (the
  statistics describe other users' long jobs and are not a forecast for this account's batches), so with eight sequential
  batches the wall time ranges from about 10 minutes at an idle queue to more than 12 hours at the global mean wait. The series can
  span several calibration cycles, which is why every batch carries its own readout reference and no contrast crosses a
  batch boundary.
- QX dry run: the same 24 circuits through the `pathion_coset_block_qx` series at 2048 shots on the remote
  emulator, 8 batches, retained QX jobs take 0.006 to 10.4 s each, so at most a few minutes of execution; credits 0 (the ledger
  recorded no charge for any of its 450 jobs). It runs before the first Tuna-17 batch and its noiseless laws must read within
  shot error of the ideal laws of record.
- Credits: none charged by the ledger (account usage read 2026-11-06T18:37Z: 450 jobs, change 0).

## Live state read for this case

| Read (UTC) | Source | Value |
|---|---|---|
| 2026-11-06T18:34:10Z | `qi_hardware_status` | Tuna-17 executing (heartbeat 18:34:02Z); QX emulator and Ry emulator idle; Tuna-5, Tuna-9, Spin-2+, Starmon-7 offline; the Quantum Inspire login refreshed the same day and the authenticated reads succeeded |
| 2026-11-06T18:34:11Z | `qi_backend(7)`, account scope | 0 jobs of this account queued |
| 2026-11-06T18:37:39Z | `qi_backend(7)`, global scope | 48 jobs in the queue; minimum, mean and maximum wait 17 s, 5426 s, 56324 s |
| 2026-11-06T18:37:33Z | `qi_usage` | 450 jobs, 5477.6 s of reported execution, 8,511,376 shots, ledger change 0, 0 unretained; the newest Tuna-17 job of this account finished 2026-10-30T04:11:45Z |

The platform publishes no Tuna calibration time; calibration and benchmarking run between jobs and hold queued jobs at no
cost. Re-read `qi_hardware_status` and `qi_backend` before batch 00, and proceed only while Tuna-17 is online and the account has no batch queued.

## Predicted result

Model (hypothesis-level): the 16-outcome law contracts toward uniform by rho to the power of the routed CZ, then each of the four bits is
misassigned with the retained single-qubit assignment. rho spans 0.955 (the 45 to 91 CZ series) to 0.9654 (the 1 to 9 CZ ladder
fit). Assignment of the region qubits (e01 = P(1 | prepared 0), e10 = P(0 | prepared 1)) from the six readout circuits of the kernel-cancellation series
(`results/quantum_inspire/runs/2026-10-23T*-kernel_cancellation_tuna_17-batch-*`): q4 (0.012, 0.048), q8 (0.030, 0.022), q11
(0.022, 0.052), q12 (0.007, 0.024). The values per template are in `prediction.json` beside the cases. The z column is the
smallest and largest |c(y)| over its standard error for two replicates pooled at 16384 shots per arm.

| Template | Routed CZ | Retention rho^CZ | Predicted selector contrast | Predicted visibility (mean of c(y) times ideal sign) | z per bin |
|---|---|---|---|---|---|
| `ba` | 20 | 0.398 to 0.494 | 0.189 to 0.234 | 0.353 to 0.438 | 29.8 to 46.8 |
| `bb` | 22 | 0.363 to 0.461 | 0.172 to 0.218 | 0.317 to 0.402 | 25.8 to 43.3 |
| `b0` | 20 | 0.398 to 0.494 | 0 | 0.364 to 0.453 | 33.9 to 48.1 |
| `xor_ba` | 4 | 0.832 to 0.869 | -0.788 to -0.823 | 0.788 to 0.823 | 111 to 137 |

Predicted c(y) of `ba` at rho 0.955 and 0.9654: (-0.306, 0.368, -0.306, 0.368, 0.361, 0.377, 0.361, 0.377) and (-0.380, 0.457, -0.380,
0.457, 0.448, 0.468, 0.448, 0.468); of `bb`: (-0.264, 0.335, 0.307, 0.344, 0.314, 0.344, -0.292, 0.335) and (-0.335, 0.425, 0.389, 0.436,
0.399, 0.436, -0.370, 0.425). The asymmetry between a bin and its partner comes from the larger e10 than e01. The standard error is 0.010 per bin
and 0.0039 for the selector contrast with two replicates pooled. The earlier design estimate used a flat readout factor of 0.81 and predicted
z of 19 to 26; the retained per-qubit assignment lifts it to 26 to 48. Resolution holds down to a raw visibility of about 0.03.

## Cross-platform comparison with the IBM map

The IBM coset-map case (`results/live/2026-11-06T194735.738910Z/CASE.md`) ran the same block circuits on ibm_fez and
ibm_marrakesh: group `pathion_coset_map`, one 4-qubit circuit pair per coset of `pathion_coset_block.default_basis(operand)`
(m followed by the two lowest extending vectors), 17 replicas on ibm_fez (job `dbn3a55t7fqc73ais42g`, record
`results/live/2026-11-06T201037.234804Z/collect.json`) and 11 on ibm_marrakesh (job `dbn38t0ou4as73b3q1n0`, record
`results/live/2026-11-06T200832.558771Z/collect.json`), 16384 shots per replica. `prediction.json` carries their
sha256 digests, and the analysis refuses a changed file. A Tuna block uses another basis and coset than the IBM blocks, so the two
sides compare by algebra output label: bin y of a Tuna block maps to the algebra index k(y) = (k0 XOR i) XOR (the XOR of the
basis vectors named by the bits of y) (`pathion_coset_block.output_labels`; `labels` in every `cases.json`), and the four IBM
cosets of an operand cover all 32 labels once.

| Block | k(y), Tuna bins 0 to 7 | IBM cosets holding these labels |
|---|---|---|
| `ba`, operand e1 + e18 | 0, 19, 2, 17, 12, 31, 14, 29 | k0 and k12 of V = span(19, 1, 2) |
| `bb`, operand e1 + e26 | 1, 26, 3, 24, 8, 19, 10, 17 | k0 and k8 of V = span(27, 1, 2) |
| `b0`, operand e1 + e17 | 1, 17, 0, 16, 3, 19, 2, 18 | k0 of V = span(16, 1, 2) |

Measured IBM values (`prediction.json`, `ibm_measured`; per replica c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y), V the mean of c times the ideal
sign over the block's 8 bins, ratio c / V; the mean over replicas, with `ratio_se` the standard error of that mean and `ratio_spread` the standard deviation over replicas):

| Operand | Coset | V ibm_fez | V ibm_marrakesh | N_hat ibm_fez | N_hat ibm_marrakesh | Ideal N_b |
|---|---|---|---|---|---|---|
| e1 + e18 | k0 | 0.747 +- 0.021 | 0.740 +- 0.026 | 0.018 +- 0.011 | 0.017 +- 0.015 | 0 |
| e1 + e18 | k4, k8, k12 | 0.826 to 0.831 | 0.838 to 0.841 | 4 (set by the signs, all aligned) | 4 | 4 |
| e1 + e26 | k0, k8 | 0.778, 0.748 | 0.761, 0.743 | 2.068, 2.056 | 2.087, 2.097 | 2 |
| e1 + e26 | k4, k12 | 0.801, 0.793 | 0.794, 0.795 | 0.061, 0.062 | 0.047, 0.049 | 0 |
| e1 + e17 | k0 | 0.759 +- 0.021 | 0.748 +- 0.025 | 0.026 +- 0.012 | 0.029 +- 0.024 | 0 |
| e1 + e17 | k4, k8, k12 | 0.877 to 0.878 | 0.895 to 0.900 | 0.004 to 0.011 | 0.051 to 0.054 | 0 |

The per-label ratios c_I / V_I lie within 0.051 of the ideal sign over the labels the three blocks cover on ibm_fez (largest: -0.949 on label 1 of
e1 + e17; e1 + e18 reads -0.969, 0.983, -1.027, 1.039 on its four k0 labels) and within 0.067 on ibm_marrakesh (largest: 1.067 on label 19 of
e1 + e26). The standard error of the mean is 0.003 to 0.009 on ibm_fez and the spread over replicas 0.024 to 0.035 (0.025 to 0.066 on ibm_marrakesh).

The statistic is D(y) = c_T(y) / V_T - c_I(k(y)) / V_I with the standard error sqrt(se_T^2 + se_I^2); the Tuna error is the delta-method
propagation of the multinomial counts of both arms through c, V and the ratio (`contrast_statistics`), and the IBM error is the
standard deviation of the per-replica ratios, not the error of their mean (the combined replica interval): the Tuna block is one placement, so
the IBM ratio it meets is one placement's draw, and the spread brackets the IBM readout asymmetry that offsets its mean ratio from the ideal sign by up to
0.067. The error of the mean would put the same offsets at 2.2 to 2.4 standard errors on single bins (`z_of_mean` in `prediction.json`). The prediction is D = 0, because both
devices carry the same compiled sign network and contract a bin alike. Two Tuna ratios are computed: the raw one, and the readout-corrected one, whose assignment matrix comes from the series' own
readout-0 and readout-1 circuits (`register_assignment`). The decision uses the corrected ratio. A device that contracts the 16-outcome
law toward uniform and then misassigns each bit reads a raw ratio that departs from the ideal sign by its assignment asymmetry (the larger
e10 than e01 of q4, q11 and q12), and the correction removes exactly that: under the model the corrected ratio is +-1 on every bin. The raw
ratio sits at the edge of the rule under the model alone: `ba` against ibm_fez reads 7 and 6 of 8 bins inside 3 combined standard errors at rho 0.955 and 0.9654
(largest |z| 4.2 and 4.7, on bin 2, where the modeled c / V is -0.87), and `bb` against ibm_marrakesh reads 8 and 7. The raw D is reported beside the corrected one.

Predicted corrected D(y) under the contraction model at rho 0.955 to 0.9654 (`cross_platform` in `prediction.json`; the model
ratio is +-1, so D = sign - c_I / V_I):

| Block | Device | Predicted D(y), bins 0 to 7 | Combined se | Largest abs z |
|---|---|---|---|---|
| `ba` | ibm_fez | -0.031, 0.017, 0.027, -0.039, 0.010, 0.005, 0.006, -0.001 | 0.025 to 0.045 | 1.0 to 1.2 |
| `ba` | ibm_marrakesh | -0.029, -0.002, 0.023, -0.032, 0.004, 0.006, 0.027, 0.009 | 0.029 to 0.071 | 0.7 to 0.8 |
| `bb` | ibm_fez | -0.044, -0.015, 0.002, -0.014, 0.014, -0.029, -0.040, -0.010 | 0.032 to 0.055 | 0.8 to 0.9 |
| `bb` | ibm_marrakesh | -0.041, -0.014, -0.003, -0.015, -0.020, -0.065, -0.044, 0.009 | 0.037 to 0.059 | 1.2 to 1.3 |
| `b0` | ibm_fez | -0.051, 0.027, -0.010, -0.008, 0.014, -0.019, 0.021, -0.027 | 0.030 to 0.044 | 1.2 to 1.3 |
| `b0` | ibm_marrakesh | -0.037, 0.039, 0.010, -0.027, -0.011, -0.012, 0.010, -0.029 | 0.040 to 0.057 | 0.7 to 0.8 |

Every block reads 8 of 8 bins inside 3 combined standard errors under the model. The chance that a device obeying the model reads fewer than 7 of 8
bins on at least one of the six block-and-device pairs is 5e-5 at rho 0.955 and 1e-5 at rho 0.9654 (`refutation_probability_any_pair`, exact enumeration over
independent bins with the Tuna delta-method error as the only random term; `refutation_probability` per pair). The model-branch IBM numbers of the earlier draft (visibilities 0.50 to 0.58 from a noise model of
the full six-qubit map) are replaced by these measured values. The rule tests a common contraction across the 8 bins of a block and the sign
pattern; it is blind to a contraction common to the whole block, which `V_T` absorbs, and its power against a single misrouted bin is a deviation of about
0.1 to 0.2 in the ratio (3 combined standard errors of 0.03 to 0.07), against the 2.0 that a flipped sign produces.

## Preregistered decisions

All use raw counts pooled over a template's two replicates and Z_RESOLVE = 3.0 standard errors; the readout-corrected visibility enters only
the depth reading.

1. Resolution: `ba` and `bb` each read the ideal sign at 3 standard errors on at least 6 of their 8 bins. Failure refutes
   "Tuna-17 realizes the compiled A_5 block map at 20 to 22 CZ" (predicted z 26 to 47, so the margin is a factor of 9).
2. Pattern: `ba` and `bb` read opposite signs at 3 standard errors in both of the bins (2 and 6) where their ideal c(y) differ; their selector
   contrasts agree to 1e-4 by construction (0.5), so only the pattern separates the two cocycles.
3. Null: the `b0` selector contrast lies within 3 standard errors (0.012) of zero. A selector offset that adds to one arm shows here; the earlier
   retained control carried a signed response of -0.0167 +- 0.0039 at 45 CZ, which this rule would flag if it recurred.
4. Cocycle-free control: the `xor_ba` selector contrast is negative at 3 standard errors and the `ba` contrast positive at 3 standard errors
   (predicted -0.79 to -0.82 against +0.19 to +0.23).
5. Depth, reported and not decided: the contraction per CZ implied by each template's readout-corrected visibility, against 0.955 to 0.9654,
   with the routed CZ beside it. It places the 20 to 22 CZ point between the 9 CZ ladder and the 45 CZ series; `xor_ba` (4 CZ) supplies no depth
   comparison.
6. Cross-platform: the readout-corrected D(y) of the previous section, at least 7 of 8 bins within 3 combined standard errors of zero for each of
   `ba`, `bb` and `b0`, against each of ibm_fez and ibm_marrakesh separately (both devices must hold).
7. Readout drift, a stop and a rule: each readout circuit is compared with the previous circuit of its kind (e01 from readout-0, e10 from readout-1) on
   the four register qubits; a change above 0.02 stops the series before the next batch is submitted and counts as a failed rule in the analysis.

Each decision has a refusal in the generator's `--self-test`: a cocycle-free circuit in the `ba` slot, a `b0` selector offset, a device
at retention 0.02 and a readout bracket moving 0.05 each fail the corresponding rule, and an honest device at retention 0.5 passes every one of them
(including the comparison with the measured IBM runs). `tests/scripts/test_qi_pathion_coset_block_series.py` scores synthetic series built from the
ideal laws (a contracted device, a drifting bracket, a `bb` slot carrying the `ba` laws, a partial series, a short shot list and the QX control) and
exercises every refusal of `--submit-next`.

Mutation and null arms not in the series, with the reason: a single flipped SELECT sign (the IBM case carries it at six qubits; its block
form moves the selector contrast by 0.25 and one bin pattern), the oracle of another operand, and the quarter-turn twin each cost
two more batches for a question the cocycle-free control and the `ba` and `bb` pattern already answer at the first level.

## Command sequence after approval

1. `"$PYTHON" scripts/qi_pathion_coset_block_cases.py --check results/quantum_inspire/cases`
2. QX dry run, one batch at a time (the series gate copies the next batch into
   `results/quantum_inspire/runs/<UTC stamp>-pathion_coset_block_qx-batch-NN/`, applies the order and shot checks and submits it through
   `qi_platform.submit`; QX needs no pause):
   `RUN=$("$QI_PYTHON" scripts/qi_pathion_coset_block_series.py --submit-next results/quantum_inspire/cases/pathion_coset_block_qx --approval "QUOTE")`
   then `"$QI_PYTHON" scripts/qi_platform.py collect "$RUN" --poll 15 --timeout 3600`, eight times. Analyze with
   `"$PYTHON" scripts/qi_pathion_coset_block_cases.py --analyze results/quantum_inspire/runs/*-pathion_coset_block_qx-batch-* --out results/quantum_inspire/pathion_coset_block_qx_analysis.json`;
   its `qx_control.pass` (every arm within 2 times its sampling floor of the ideal law of record) gates the hardware series.
3. Tuna-17 batches 00 to 07, the same two commands with the hardware series and the control analysis:
   `RUN=$("$QI_PYTHON" scripts/qi_pathion_coset_block_series.py --submit-next results/quantum_inspire/cases/pathion_coset_block_tuna_17 --control results/quantum_inspire/pathion_coset_block_qx_analysis.json --approval "QUOTE")`
   then `collect`. Before it sends, `--submit-next` requires every earlier batch collected with completed jobs, full shot lists and case bytes equal to the
   series, refuses when the readout-bracket drift exceeds 0.02 (`--sanity RUN_DIR...` prints the same report), waits out the account's hardware pause
   (30 s, raised one step of the ladder through `QI_HARDWARE_PAUSE_SECONDS` after a platform failure, which stops the series) and writes `series-gate.json` into the
   run directory. The drift of the last batch is read by the analysis or by `--sanity`, because no later submission follows it.
4. `"$PYTHON" scripts/qi_pathion_coset_block_cases.py --analyze results/quantum_inspire/runs/*-pathion_coset_block_tuna_17-batch-* --out results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json`
   scores the decisions, per-template c(y), visibility, N_hat and selector contrast, the comparison with both IBM devices and the drift rule; a series
   stopped before batch 07 reports its batches and drift only.

## Not run and open

- Not run: every provider job, including the QX dry run. The IBM comparison uses the measured ibm_fez and ibm_marrakesh records and needs no further job.
- Open before a merge: the retained record of `qi_toolchain_check.py` (gate core-368) names exactly the current case files, so it needs the regeneration
  `"$QI_PYTHON" scripts/qi_toolchain_check.py` for the 48 new circuits; a gate entry for `--check` and `--self-test` of the generator and for
  `tests/gororoba_quantum/test_pathion_coset_block.py` and `tests/scripts/test_qi_pathion_coset_block_series.py` in `ci/gates.json`; the QX local replay record; the registration of the run in
  `docs/state/research_state.json` after the acquisition. `--submit-next` compares no live backend topology or gate-set digest, because the cases carry none;
  `qi_platform.submit` checks the backend's identifier, status, capacity and queue.
- Residual risk: the readout-corrected ratio uses an assignment pooled over the whole series, and the drift stop admits a change of up to 0.02 between successive references of
  one kind; a shift of about 0.01 in an assignment rate moves the corrected ratio by roughly the standard error of one bin (0.03 to 0.04), so a drift near the stop
  limit can shift the cross-platform statistic by one standard error without a rule firing.
- Residual risk: q8 is the star center and no retained single-qubit record covers q8 beside q4, q11 and q12 at once; the readout assignment above is from 2026-10-23
  and the series measures its own; the control circuit is not depth-matched, and the model's per-CZ contraction toward uniform treats every error as depolarizing.
