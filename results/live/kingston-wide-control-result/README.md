# Recovered Kingston wide-control job

Job `db6qe7klf4us73c5pdc0` completed on `ibm_kingston` with two PUBs of 512 shots and a settled 2 s QPU charge.

Completed hardware acquisition recovered retrospectively. Original approval, local pre-submission archive, calibration, and preregistration are unavailable.
Analysis remains retrospective and descriptive.

## Actual submitted resources and ideal laws

The replay reads `submitted-circuits.qpy`, validates its recorded digest and decoded item order, and derives connected components from gate and classical dependencies.

| PUB | Gate-active qubits | Measured qubits | Measurement-only spectators | Idle unmeasured qubits | Active components |
| --- | ---: | ---: | ---: | ---: | ---: |
| `exp1_ramsey_156q` | 2 | 156 | 154 | 0 | 1 |
| `exp2_shor_carpet_150q` | 87 | 29 | 0 | 69 | 29 |

The 156-bit Ramsey register contains 154 zero-state measurement-only spectators and the outputs from physical qubits 79 and 93. Qubit 93 is measured before reset and again into c[93]; the final register overwrites the earlier value. A conditional RZ immediately after reset changes only the reset state's global phase, so that conditional cannot alter the final output law.

Ramsey's ideal active output law is `{'00': '1/4', '01': '1/4', '10': '1/4', '11': '1/4'}` in c[93]c[79] order. The measured ideal-support violation count is 0/512. All spectator bits are zero in 27/512 hardware shots. Ramsey admits all four active outputs, so its zero support-violation count carries no agreement evidence; total variation measures the active distribution residual.

The carpet's name includes 150q, while the decoded submitted gates occupy 87 physical qubits in 29 disconnected three-qubit components. Each component writes two classical bits. The remaining 69 qubits carry neither gates nor measurements in the decoded QPY; the backend scheduler's initialization/finalization pulses remain a separate execution surface. Two replica outputs measure one recycled control qubit before and after reset/feed-forward; active work qubits remain unmeasured.

The exact replay keeps Gaussian-integer amplitudes and integer powers of two, branches on measurement/reset without sampling, executes each classical condition, and sums exact rational output probabilities. Qiskit Statevector gate evolution cross-checks every component within 1e-12. The largest state has eight amplitudes; the replay never builds a 156-qubit state.

## Measured carpet outputs

Labels list the later bit on the left and the earlier bit on the right. An ideal-support violation is an observed output whose exact ideal probability is zero; total variation additionally measures deviations among supported outcomes.

| Replica | Physical qubits | Classical bits (LSB first) | Exact ideal law | Counts 00, 01, 10, 11 | Support violations | TV |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 0 | [0, 1, 2] | [0, 1] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 52, 89, 113, 258 | 113/512 | 0.474609 |
| 1 | [20, 21, 22] | [2, 3] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 240, 97, 8, 167 | 8/512 | 0.091797 |
| 2 | [40, 41, 42] | [4, 5] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 238, 111, 19, 144 | 19/512 | 0.068359 |
| 3 | [60, 61, 76] | [6, 7] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 219, 102, 22, 169 | 22/512 | 0.123047 |
| 4 | [100, 101, 102] | [8, 9] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 252, 74, 9, 177 | 9/512 | 0.113281 |
| 5 | [120, 121, 122] | [10, 11] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 154, 133, 77, 148 | 77/512 | 0.199219 |
| 6 | [140, 141, 142] | [12, 13] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 221, 50, 27, 214 | 27/512 | 0.220703 |
| 7 | [4, 5, 6] | [14, 15] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 221, 91, 35, 165 | 35/512 | 0.140625 |
| 8 | [8, 9, 10] | [16, 17] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 246, 111, 15, 140 | 15/512 | 0.052734 |
| 9 | [13, 14, 15] | [18, 19] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 224, 176, 24, 88 | 24/512 | 0.140625 |
| 10 | [18, 30, 31] | [20, 21] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 220, 110, 25, 157 | 25/512 | 0.105469 |
| 11 | [24, 25, 37] | [22, 23] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 243, 96, 11, 162 | 11/512 | 0.087891 |
| 12 | [33, 34, 39] | [24, 25] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 209, 81, 27, 195 | 27/512 | 0.183594 |
| 13 | [38, 49, 50] | [26, 27] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 247, 116, 15, 134 | 15/512 | 0.041016 |
| 14 | [46, 47, 57] | [28, 29] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 205, 74, 31, 202 | 31/512 | 0.205078 |
| 15 | [55, 59, 75] | [30, 31] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 244, 89, 8, 171 | 8/512 | 0.099609 |
| 16 | [58, 71, 72] | [32, 33] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 236, 132, 22, 122 | 22/512 | 0.050781 |
| 17 | [63, 64, 65] | [34, 35] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 135, 14, 117, 246 | 117/512 | 0.458984 |
| 18 | [78, 89, 90] | [36, 37] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 235, 120, 29, 128 | 29/512 | 0.056641 |
| 19 | [79, 92, 93] | [38, 39] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 252, 105, 13, 142 | 13/512 | 0.052734 |
| 20 | [82, 83, 96] | [40, 41] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 240, 127, 3, 142 | 3/512 | 0.033203 |
| 21 | [86, 87, 97] | [42, 43] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 264, 123, 5, 120 | 5/512 | 0.025391 |
| 22 | [98, 110, 111] | [44, 45] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 245, 119, 7, 141 | 7/512 | 0.039062 |
| 23 | [99, 114, 115] | [46, 47] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 254, 113, 7, 138 | 7/512 | 0.033203 |
| 24 | [104, 105, 106] | [48, 49] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 267, 120, 3, 122 | 3/512 | 0.027344 |
| 25 | [118, 129, 130] | [50, 51] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 270, 124, 2, 116 | 2/512 | 0.031250 |
| 26 | [126, 127, 137] | [52, 53] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 238, 116, 17, 141 | 17/512 | 0.058594 |
| 27 | [132, 133, 134] | [54, 55] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 241, 118, 2, 151 | 2/512 | 0.048828 |
| 28 | [138, 150, 151] | [56, 57] | 00:1/2, 01:1/4, 10:0, 11:1/4 | 257, 113, 2, 140 | 2/512 | 0.029297 |

At least one carpet component violates its ideal support in 403/512 shared shots; the mean is 1.357422 violating components per shot. `analysis.json` retains the joint violation histogram, all 406 replica pairs' joint counts/covariance/correlation, first/second-half statistics, and lag-one descriptions. Those quantities preserve the raw same-PUB shot order. PUB indices identify separate executions, so the analysis pairs replicas within the carpet PUB and treats the two PUBs separately.

Wilson 95% intervals are marginal binomial descriptions under independent identical shot sampling. They are neither simultaneous nor preregistered. Shot drift and shared-resource dependence remain unmodeled; pairwise statistics describe same-PUB shot vectors. PUB shot indices are not paired across PUBs.

Hardware errors combine initialization, gates, reset, feedback, and readout. The recovered archive cannot attribute the observed residuals to one mechanism, establish a calibration-matched noise prediction, or admit a matched benefit claim. Classical-register occupancy differs from coherent quantum-resource occupancy; spectator ones describe zero-state/readout residuals.

## Offline replay and byte retention

Run from the repository root with the pinned requirements:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/review_wide_control_job.py --check
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/review_wide_control_job.py --check
(cd results/live/kingston-wide-control-result && sha256sum -c SHA256SUMS)
```

Generation uses the same command without `--check`. Generation writes only `analysis.json`, `README.md`, and `SHA256SUMS`. Check mode compares all three derived files byte for byte and writes stdout. The replay validates every raw-index digest, metrics digest, PUB order/name, register width, shot count, bit alphabet, measurement-bit partition, and QPY digest. `SHA256SUMS` records immutable input files and generated outputs; `analysis.json` binds the replay source digest.

The self-test checks exact conditional feedback, reset, classical-bit overwrite, and entanglement laws. Nine copied-fixture mutations exercise raw/QPY/metric digest identity, PUB order, width, shot count, bit alphabet, shot ordering, and file completeness.

`retention.json` binds the original retrieval script by digest. That temporary script contains a local absolute path and remains outside the published bundle. The immutable decoded inputs and raw files provide the replay inputs. A later retrieval would create a separately identified acquisition snapshot rather than rewrite these bytes.
