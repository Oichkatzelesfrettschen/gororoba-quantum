# Frame detunings fitted to the Fez ripple atlas, on the executed circuits

`result.json` (schema v6) is the output of `scripts/atlas_detuning_map.py
--lanes all` at its committed revision, run as the Kaggle CPU kernel
`gororoba-atlas-detuning-map` (run directory
results/kaggle/2026-10-16T114149Z-gororoba-atlas-detuning-map; the stack
proof passed and every file of the `gororoba-retained-runs` dataset matched
its manifest). It replaces the notebook `correlated-coherent`, whose
over-rotation test could not change a Z-basis population
(`docs/evidence/simulation-notebook-audit/README.md`).

The Fez atlas ran 84 box-kite edges as 8-point phase sweeps on 7 lanes of 5
physical qubits (`results/ripple/measured-ripple.json`). Fitted fringe
phases sit about +0.13 rad from the ideal (spread 0.22 rad) on hardware and
within 0.06 rad in the calibrated execution replay, whose noise model has no
coherent term. Each phase point is simulated as its executed replica,
rebuilt from the run's `isa.qpy`, with every pulse at the start time IBM's
`scheduler_timing` reported for that PUB; with no error term every edge's
simulated fringe phase equals the recorded ideal fringe phase to within
6e-15 rad.

The models are least-squares fits to fringe-phase slopes taken at 1 kHz
detuning and 0.01 rad CZ phase, so each physical model is scored twice: by
the linear prediction of those slopes, and by resimulating every held-out
edge at its leave-one-out fitted detunings and CZ phases. Only the second
tests the static-error model itself. The shot-noise floor propagates each
point's binomial variance through the fringe fit to its phase.
Leave-one-edge-out RMS error (rad), linear / resimulated, against the
hardware-minus-replay offsets:

| Lane | Qubits | Executed CZ | Shot noise | Lane mean | Detuning | CZ phase | Both |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 112, 113, 114, 115, 119 | 36-50 | 0.041 | 0.154 | 0.180 / 0.186 | 0.214 / 0.214 | 0.337 / 0.314 |
| 1 | 86, 87, 88, 89, 97 | 33-53 | 0.030 | 0.238 | 0.120 / 0.120 | 0.180 / 0.180 | 0.154 / 0.116 |
| 2 | 24, 25, 26, 37, 45 | 36-50 | 0.027 | 0.212 | 0.093 / 0.093 | 0.136 / 0.133 | 0.247 / 0.240 |
| 3 | 130, 131, 132, 138, 151 | 35-51 | 0.034 | 0.173 | 0.114 / 0.117 | 0.165 / 0.164 | 0.079 / 0.081 |
| 4 | 50, 51, 52, 58, 71 | 36-46 | 0.029 | 0.136 | 0.103 / 0.104 | 0.091 / 0.091 | 0.264 / 0.304 |
| 5 | 126, 127, 128, 137, 147 | 33-50 | 0.035 | 0.130 | 0.113 / 0.108 | 0.130 / 0.131 | 0.324 / 0.339 |
| 6 | 103, 104, 105, 106, 117 | 36-50 | 0.029 | 0.129 | 0.074 / 0.086 | 0.151 / 0.151 | 0.073 / 0.077 |

The shot-noise column propagates each point's binomial variance, for the
hardware counts and for the execution replay (which live_run sampled at the
run's own shots), through the fringe fit to the phase. A held-out residual
also carries the noise of the prediction fitted to the other 11 edges, so
each model has its own leave-one-out noise floor, both variances propagated
linearly through the fit; it applies to the linear scores (rad):

| Lane | Lane mean | Detuning | CZ phase | Both |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.043 | 0.056 | 0.052 | 0.113 |
| 1 | 0.031 | 0.040 | 0.037 | 0.097 |
| 2 | 0.028 | 0.036 | 0.033 | 0.064 |
| 3 | 0.035 | 0.046 | 0.042 | 0.084 |
| 4 | 0.030 | 0.044 | 0.039 | 0.076 |
| 5 | 0.036 | 0.050 | 0.045 | 0.093 |
| 6 | 0.030 | 0.042 | 0.037 | 0.069 |

- Resimulated at its fitted values, a static frame detuning per qubit
  predicts held-out edges better than the lane mean on six of seven lanes,
  often halving the error (lane 2: 0.212 to 0.093 rad). Lane 0, where no
  model beats the mean, is the exception. The single-term models are close
  to linear over the fitted range: resimulation moves their held-out error
  by at most 0.012 rad.
- The fitted detunings are mostly 5 to 30 kHz, with qubits 105, 127 and 131
  at 30 to 60 kHz: the scale of the 40.9 kHz detuning difference behind the
  Kingston coherence-window rotation (`hw-idle-detuning-scale`), here on a
  different device and day. Lane 0's 117 kHz on qubit 113 comes from the lane
  the model does not explain.
- Against its own leave-one-out floor, the detuning model's linear
  held-out error is 1.8 to 3.0 times the noise on lanes 1 to 6, so a static
  detuning is the largest identified part of the offset, not all of it. The
  joint model (about 9 parameters on 12 edges) comes within 0.9 to 1.6
  times its floor on lanes 1, 3 and 6, where detuning plus CZ phase
  accounts for the offsets to about the noise, and overfits on lanes 2, 4
  and 5 (3.5 to 3.8 times).
- A first version of this fit recompiled each edge itself (57 to 94 CZ
  against the 33 to 53 the hardware ran); it was withdrawn before
  publication. Every response here comes from the executed circuits.

This is an exploratory reanalysis: the detunings are inferred from fringe
phases of one run. The conditional-Ramsey design
(`proposed-conditional-ramsey-hamiltonian`) measures detunings and ZZ on
named qubits directly and is the test that would confirm them.

Gate core-293 requires `result.json` to equal the kernel's retained output
byte for byte. Gate core-285 requires the retained file to hold lanes 0 to 6 once each,
recomputes lane 4 on the CPU from the retained run, and requires every
response to agree to 1e-9 and every fitted parameter and score, linear and
resimulated, to 1e-6.
