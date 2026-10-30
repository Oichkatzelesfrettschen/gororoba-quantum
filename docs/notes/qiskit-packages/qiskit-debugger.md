# qiskit-debugger

qiskit-debugger 0.1.2 is a 158-line circuit debugger from 2023. It provides
`QuantumDebugCircuit`, a `QuantumCircuit` subclass with breakpoints, and
`QCDebugger`, which steps through a circuit and shows its intermediate
measurement histograms. It imports `qiskit.Aer` and `qiskit.execute`, both
removed in Qiskit 1.0, and pins `qiskit==0.43.2`.

The `qiskit-debugger-stack` Arch package keeps it in a Python 3.11
environment under `/opt/qiskit-debugger-stack` (launcher
`qiskit-debugger-python`), with qiskit 0.43.2, qiskit-terra 0.24.1 and
qiskit-aer 0.12.1. The qiskit 0.43.2 metapackage ships only an sdist with a
bare `setup.py`, so it alone builds from source. Every other distribution
installs from hash-locked wheels. The stack's check runs a legacy
`execute(circuit, Aer.get_backend("qasm_simulator"))` and asserts the
debugger's classes.

## Connections

- None to the Qiskit 2.x stack. A circuit crosses over only as OpenQASM 2,
  which both versions read.
- The stack retires when upstream supports Qiskit 2.x or the package is
  dropped (README Open item 3).
