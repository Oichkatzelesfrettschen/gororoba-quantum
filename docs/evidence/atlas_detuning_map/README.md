# Frame detunings fitted to the Fez ripple atlas, on the executed circuits

`result.json` is the output of `scripts/atlas_detuning_map.py --lanes all`,
run as the Kaggle kernel `gororoba-atlas-detuning-map` (CPU kernel, stack
proof passed, every file of the `gororoba-retained-runs` dataset matched its
manifest). It replaces the notebook `correlated-coherent`, whose
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
6e-15 rad. Leave-one-edge-out RMS error (rad) of four models against the
hardware-minus-replay offsets:

| Lane | Qubits | Executed CZ | Shot noise | Lane mean | Detuning | CZ phase | Both |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 112-115, 119 | 36-50 | 0.035 | 0.154 | 0.180 | 0.214 | 0.337 |
| 1 | 86-89, 97 | 33-53 | 0.020 | 0.238 | 0.120 | 0.180 | 0.154 |
| 2 | 24-26, 37, 45 | 36-50 | 0.019 | 0.212 | 0.093 | 0.136 | 0.247 |
| 3 | 130-132, 138, 151 | 35-51 | 0.026 | 0.173 | 0.114 | 0.165 | 0.079 |
| 4 | 50-52, 58, 71 | 36-46 | 0.021 | 0.136 | 0.103 | 0.091 | 0.264 |
| 5 | 126-128, 137, 147 | 33-50 | 0.027 | 0.130 | 0.113 | 0.130 | 0.324 |
| 6 | 103-106, 117 | 36-50 | 0.020 | 0.129 | 0.074 | 0.151 | 0.073 |

- A static frame detuning per qubit predicts held-out edges better than
  the lane mean on six of seven lanes, often halving the error (lane 2:
  0.212 to 0.093 rad). Lane 0, where no model beats the mean, is the
  exception.
- The fitted detunings are mostly 5 to 30 kHz, with qubits 105, 127 and 131
  at 30 to 60 kHz: the scale of the 40.9 kHz detuning difference behind the
  Kingston coherence-window rotation (`hw-idle-detuning-scale`), here on a
  different device and day. Lane 0's 117 kHz on qubit 113 comes from the lane
  the model does not explain.
- Residuals stay 3 to 5 times the shot noise, so detuning is the largest
  identified part of the offset, not all of it. The joint model, about 9
  parameters on 12 edges, overfits on most lanes.
- A first version of this fit recompiled each edge itself (57 to 94 CZ
  against the 33 to 53 the hardware ran); it was withdrawn before
  publication. Every response here comes from the executed circuits.

This is an exploratory reanalysis: the detunings are inferred from fringe
phases of one run. The conditional-Ramsey design
(`proposed-conditional-ramsey-hamiltonian`) measures detunings and ZZ on
named qubits directly and is the test that would confirm them.

Gate core-285 recomputes lane 4 on the CPU from the retained run and
requires every response to agree to 1e-9 and every fitted parameter to 1e-6.
