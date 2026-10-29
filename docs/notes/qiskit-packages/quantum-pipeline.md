# quantum-pipeline

quantum-pipeline 2.5.1 runs VQE on molecular Hamiltonians. Its stages are
PySCF drivers, qiskit-nature Jordan-Wigner mapping, an `EfficientSU2`
ansatz, and Aer or IBM Runtime `EstimatorV2` with qiskit-algorithms
gradients, followed by reports. It streams results to Kafka with an Avro
schema registry and pushes metrics to a Prometheus PushGateway, by default
at localhost:9092 and localhost:9091. It also runs `docker stats` when
docker is on PATH. All of that infrastructure is opt-in and local.

It caps qiskit-aer below 0.18, so the `quantum-pipeline-stack` Arch package
keeps it in a Python 3.13 environment under `/opt/quantum-pipeline-stack`.
The environment holds qiskit 2.6.1, qiskit-ibm-runtime 0.51.0, Aer 0.17.2,
qiskit-nature 0.8.0 and PySCF 2.14.0. The launchers are
`quantum-pipeline-python` and `quantum-pipeline`. The stack's check runs an
Aer `EstimatorV2` expectation of Z on |1> and asserts -1.

## Connections

- qiskit-nature is archived upstream, and `EfficientSU2` is deprecated
  since qiskit 2.1 and removed in 3.0. Both bound the package's life on the
  current core.
- Its `--ibm` flag submits through qiskit-ibm-runtime, and each submission
  waits for an approved case.
- It is the only chemistry stack on the host. qiskit-ecosystem.md marks
  qiskit-nature as out of scope for the repository's own work.
