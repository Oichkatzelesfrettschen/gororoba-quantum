# quantum-al

quantum-al 0.2.0 (`python-quantum-al`) runs correlation-aware active
learning for materials discovery. It selects batches by expected
information gain (`expected_information_gain`, `greedy_batch_eig`,
`EnsembleCriterionSelector`, `GreedyBatchEIGSelector`) and tracks learning
curves. Its hard dependencies are numpy, scipy and scikit-learn. Qiskit and
Aer appear only in its optional quantum-kernel path, which uses
`StatevectorEstimator`, Aer `EstimatorV2`, `SparsePauliOp` and
`StatePreparation`; they are optdepends of the Arch package.

## Connections

- It sits at the edge of the Qiskit stack. Its core runs without Qiskit, and
  the quantum kernel is one interchangeable feature map.
- `fetch_data.py` queries api.materialsproject.org with `MP_API_KEY`, on an
  explicit call only. A key would live in the environment, never in a file
  of this repository.
