# qiskit-serverless and qiskit-ibm-catalog

qiskit-ibm-catalog 0.21.0 (`python-qiskit-ibm-catalog`) is the client for
IBM Qiskit Functions. `QiskitFunctionsCatalog` lists, loads and runs
functions hosted on the IBM Quantum Platform. qiskit-serverless 0.37.0
(`python-qiskit-serverless`) is the SDK beneath it: `ServerlessClient` and
`IBMServerlessClient`, `QiskitFunction` uploads, the `distribute_task`
decorators, and a local Ray mode.

Upstream caps qiskit-ibm-runtime below 0.51. It also pins
`cloudpickle==3.1.2`, `zipp==4.1.1`, `certifi==2026.7.22`, `ipython<9` and
OpenTelemetry `<1.46` to match its Ray node image. The system package
rewrites those lines in `requirements.txt` during `prepare()` to admit
runtime 0.51.0, ipython 9.17, and the distribution's zipp, certifi and
OpenTelemetry. That combination is untested upstream. Both modules import
on the host, and no catalog call has run (Open item 1 of the
[README](README.md)). The pinned cloudpickle matters only when a function
pickles code across to a remote Ray node; a version skew there can break
deserialization on the node.

## Connections

- qiskit-ibm-runtime provides the account and channel. Constructing
  `QiskitFunctionsCatalog` reads the saved account and contacts IBM; every
  function run is a provider job that waits for an approved case.
- qiskit-ibm-transpiler would also pull qiskit-serverless, at `~=0.30`,
  which requires runtime below 0.46. It stays uninstalled
  ([qiskit-ecosystem.md](../qiskit-ecosystem.md), finding 5).
- A Kaggle kernel never imports either package; it holds no IBM credential.
