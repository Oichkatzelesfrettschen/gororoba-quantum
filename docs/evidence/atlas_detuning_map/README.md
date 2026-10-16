# Coherent-error fit to the Fez ripple atlas fringe phases

`result.json` is the output of `scripts/atlas_detuning_map.py --lanes all`,
run as the Kaggle kernel `gororoba-atlas-detuning-map` (CPU kernel, stack
proof passed; run directory under results/kaggle/). It replaces the
notebook `correlated-coherent`, whose over-rotation test could not change a
Z-basis population (`docs/evidence/simulation-notebook-audit/README.md`).

The Fez atlas ran 84 box-kite edges as 8-point phase sweeps on 7 lanes of 5
physical qubits (`results/ripple/measured-ripple.json`). Fitted fringe
phases sit on average +0.13 rad from the ideal (spread 0.22 rad) on
hardware, and within 0.06 rad in the calibrated execution replay, whose
noise model has no coherent term. For each lane the script computes the
fringe-phase response of every edge to a 1 kHz frame detuning per qubit and
to a CPhase error per coupler, from the compiled, ALAP-scheduled circuit on
the lane's 5-qubit sub-target, and compares four models by
leave-one-edge-out RMS error (rad) against the shot-noise floor:

| Lane | Qubits | Shot noise | Lane mean | Detuning | CZ phase | Both |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 112-115, 119 | 0.035 | 0.154 | 0.191 | 0.223 | 0.080 |
| 1 | 86-89, 97 | 0.020 | 0.238 | 0.232 | 0.220 | 0.474 |
| 2 | 24-26, 37, 45 | 0.019 | 0.212 | 0.237 | 0.177 | 0.413 |
| 3 | 130-132, 138, 151 | 0.026 | 0.173 | 0.138 | 0.175 | 0.158 |
| 4 | 50-52, 58, 71 | 0.021 | 0.136 | 0.083 | 0.063 | 0.154 |
| 5 | 126-128, 137, 147 | 0.027 | 0.130 | 0.126 | 0.122 | 0.100 |
| 6 | 103-106, 117 | 0.020 | 0.129 | 0.147 | 0.137 | 0.229 |

- The offsets are real: every lane's spread is 3 to 10 times its shot noise.
- No single coherent family explains them across lanes. Detuning or CZ
  phase beats the lane mean on lanes 3 and 4 (lane 4's CZ-phase model halves
  the error), and the joint model, about 9 parameters on 12 edges, overfits
  on lanes 1, 2 and 6.
- The fit uses the 2026-10-14 Fez Target for durations two days after the
  run; durations are fixed by the calibrated pulse shapes, but the
  detunings, if real, are of that run's day only.

This is an exploratory reanalysis. The test that would decide it is the
conditional-Ramsey design (`proposed-conditional-ramsey-hamiltonian`), which
measures detunings and ZZ directly on named qubits.

Gate core-285 recomputes lane 4 on the CPU and requires every response to
agree to 1e-9 and every fitted parameter to 1e-6.
