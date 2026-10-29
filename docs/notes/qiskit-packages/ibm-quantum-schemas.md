# ibm-quantum-schemas

ibm-quantum-schemas 0.13.20261016 (`python-ibm-quantum-schemas`) holds the
pydantic models of the payloads that the IBM Quantum Platform accepts and
returns. qiskit-ibm-runtime 0.51.0 serializes primitive requests through
them, and they encode circuits as QPY or OpenQASM 3.
It depends on qiskit, pydantic, samplomatic (boxed templates appear in the
payloads), qiskit-qasm3-import (OpenQASM 3 parsing), numpy and pybase64.

The release replaces 0.12.20260921, the floor of runtime 0.50. The replay
runtime of [ci/requirements-replay.txt](../../../ci/requirements-replay.txt)
keeps 0.12.20260921, so retained Qiskit 2.5 evidence replays against the
schema it was written with.

## Connections

- qiskit-ibm-runtime: a hard dependency, so a runtime upgrade can move it.
- [qiskit-serverless and qiskit-ibm-catalog](qiskit-functions.md) reach the
  same platform through a separate REST API, which uses none of these models.
- It contacts no network service and constructs no service object.
