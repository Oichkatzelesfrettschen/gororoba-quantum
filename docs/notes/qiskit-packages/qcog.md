# qcog

qcog 0.1.0 (`python-qcog`, console script `qcog`) simulates, explains and
visualizes small circuits. Its `Engine` runs `QuantumCircuit`s on Aer,
optionally with a `NoiseSpec` depolarizing channel, and reports states,
POVM and projective-measurement outcomes, sequential results and Bloch
views. Its Qiskit surface is `QuantumCircuit`, `transpile`, `UnitaryGate`,
`StatePreparation`, `quantum_info` (`Operator`, `Statevector`,
`DensityMatrix`, `partial_trace`, `schmidt_decomposition`) and Aer noise
models. An optional backend runs on qiskit-ionq.

## Connections

- Executes on [qiskit-aer](qiskit-aer.md). The optional qiskit-ionq backend
  lives in the `ionq-stack` environment and does not reach the system
  interpreter.
- It is a teaching and inspection tool. A repository simulation of an
  algebra circuit still runs through live_run.py's noise model from the live
  calibration.
