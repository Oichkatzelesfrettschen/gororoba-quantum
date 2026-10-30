# eigenkit

eigenkit 1.1.0 (`python-eigenkit`, Apache-2.0) is a quantum machine-learning
library. It provides hybrid quantum neural classifiers and regressors
(`HQNC`, `HQNR` and recurrent variants), kernel `QSVC` and `QSVR`, quantum
reservoir models, time-series models, datasets and a benchmark harness, with
pluggable execution backends. It requires only numpy>=2.4, pydantic and
scipy. Qiskit, Aer and qiskit-ibm-runtime are optional backends, declared
as optdepends of the Arch package. The Qiskit backend uses `QuantumCircuit`,
`Parameter`, `transpile`, `UnitaryGate`, `AerSimulator`, and the runtime
`SamplerV2` and `EstimatorV2`.

## Connections

- Executes on [qiskit-aer](qiskit-aer.md) locally. The IBM Runtime backend
  submits jobs, and each submission waits for an approved case.
- Registered datasets download with `urlretrieve` on an explicit call only.
- Its estimator path overlaps qiskit-machine-learning's, which the host
  does not install ([qiskit-ecosystem.md](../qiskit-ecosystem.md)).
