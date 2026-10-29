# qiskit-noise-learning

qiskit-noise-learning 0.1.0 (`python-qiskit-noise-learning`, IBM, Apache-2.0)
builds randomized noise-characterization experiments and fits their data.
It covers sequences of layers twirled into Pauli channels, fidelity
estimation over paths of instruction sequences, and the Pauli-Lindblad
model fits that probabilistic error cancellation and amplification consume.
Its subpackages are `experiment_builder`, `circuit_generator`, `sequences`,
`gate_sets`, `models`, `protocols`, `analysis` and `data`. `data` stores
results as xarray datasets. It requires qiskit>=2.5, samplomatic>=0.21,
rustworkx, scipy and xarray.

## Connections

- samplomatic supplies the boxed, twirled templates that the experiments
  instantiate.
- The fitted Pauli-Lindblad rates are the noise model that
  [qiskit-addon-slc](qiskit-addon-slc.md) bounds lightcones against, and
  that pauli-prop propagates as `PauliLindbladError` channels.
- The experiments run on any primitive. On Aer they need no approval. On an
  IBM backend each submission waits for an approved written case
  ([AGENTS.md](../../../AGENTS.md), QPU time).
- It is complementary to qiskit-mitigation and mthree. Those correct
  readout and expectation values from a run; noise learning measures the
  gate-layer channel that PEC and PEA invert.
