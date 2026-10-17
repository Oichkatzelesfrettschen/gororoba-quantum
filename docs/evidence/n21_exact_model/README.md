# Exact branch-resolved law of the encoded N=21 feedback pair

`validation.json` pools three Kaggle CPU kernels that sampled the two
dynamic circuits of `results/live/2026-10-17T003834.987727Z/isa.qpy`
(n21_encoded_feedback and n21_encoded_no_feedback, seven active qubits on
ibm_kingston) under the ibm_kingston calibration snapshot
`docs/evidence/calibration/history/ibm_kingston/20261016T1213360700.json`,
with Aer statevector trajectories, seeds 1000, 2000 and 3000 (circuit k takes
seed + k), 196,608 shots per circuit per kernel: 589,824 shots per circuit.

`scripts/n21_exact_model_validation.py --check validation.json` (gate
core-485) recomputes the exact law of each circuit with
`gororoba_quantum/dynamic_density.py` from the same snapshot and ISA, samples
nothing, and requires every one of the eight outcome probabilities to lie
within the simultaneous Hoeffding radius at total tail 1e-3,
sqrt(ln(16000) / (2 x 589,824)) = 0.00286.

| Circuit | exact law | pooled frequency | max gap |
| --- | --- | --- | --- |
| n21_encoded_feedback | 0.28338, 0.25129, 0.21857, 0.24676 | 0.28276, 0.25084, 0.21879, 0.24760 | 0.00084 |
| n21_encoded_no_feedback | 0.28333, 0.23586, 0.21866, 0.26216 | 0.28475, 0.23560, 0.21912, 0.26053 | 0.00163 |

The exact signed-contrast difference under this snapshot is 0.0308; the
pooled sample reads 0.0282. The kernels ran Kaggle's image Python with numpy
2.1.3, qiskit 2.5.2 and qiskit-aer 0.17.2 on four CPUs; the collected runs
are `results/kaggle/2026-10-17T090404Z-gororoba-n21-exact-model-s1000`,
`...T090412Z-...-s2000` and `...T090416Z-...-s3000`. The law is the Aer
noise model's; a hardware discrepancy is outside what this comparison tests.
