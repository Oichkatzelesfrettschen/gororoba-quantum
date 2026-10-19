> Full piece: [https://docs.iqm.tech/4.7/iqm-client/index.html](https://docs.iqm.tech/4.7/iqm-client/index.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a6d8afbd3b1579def74f785460a98d41be6864d94dc26d306bfb5f2f42385e29.

# IQM client

Release:  
36.0.0

Date:  
2026-10-06

Client-side library for connecting to an [IQM](https://iqm.tech/) quantum computer. Provides both circuit-level and pulse-level access.

Includes adapters for the [Qiskit](https://qiskit.org/), [Cirq](https://quantumai.google/cirq) and [Qrisp](https://www.qrisp.eu/) quantum computing frameworks, each with its own optional dependencies. See user guides for [Qiskit](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#user-guide-qiskit), [Cirq](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#user-guide-cirq) and [Qrisp](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#user-guide-qrisp) for introductions on how to install and use the framework adapters. Each adapter exposes a dedicated Python import package with classes and functions for circuit construction, transpilation, execution, and result retrieval.

## Contents

- [iqm-client](https://docs.iqm.tech/4.7/iqm-client/readme.html)
  - [Migration from legacy packages](https://docs.iqm.tech/4.7/iqm-client/readme.html#migration-from-legacy-packages)
  - [Installation](https://docs.iqm.tech/4.7/iqm-client/readme.html#installation)
- [Qrisp on IQM user guide](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html)
  - [Installation](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#installation)
  - [Authentication](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#authentication)
  - [Hello, world!](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#hello-world)
  - [Transpilation](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#transpilation)
  - [Submitting circuits for execution](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#submitting-circuits-for-execution)
  - [IQM Pulse integration](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#iqm-pulse-integration)
  - [Quantum error correction](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#quantum-error-correction)
  - [Next steps](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/index.html#next-steps)
- [Qiskit on IQM user guide](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html)
  - [Installation](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#installation)
  - [Authentication](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#authentication)
  - [Hello, world!](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#hello-world)
  - [Running quantum circuits on an IQM quantum computer](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#running-quantum-circuits-on-an-iqm-quantum-computer)
  - [Transpilation](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#transpilation)
  - [Batch execution of circuits](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#batch-execution-of-circuits)
  - [Multiplexed measurements](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#multiplexed-measurements)
  - [Simulation](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html#simulation)
- [Cirq on IQM user guide](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html)
  - [Installation](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#installation)
  - [IQM’s quantum devices](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#iqm-s-quantum-devices)
  - [Constructing circuits](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#constructing-circuits)
  - [Decomposition](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#decomposition)
  - [Routing](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#routing)
  - [Optimization](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#optimization)
  - [Classical control](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#classical-control)
  - [Resetting qubits](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#resetting-qubits)
  - [Running on a real quantum computer](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#running-on-a-real-quantum-computer)
  - [More examples](https://docs.iqm.tech/4.7/iqm-client/user_guide_cirq.html#more-examples)
- [Integration guide](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html)
  - [Authentication](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#authentication)
  - [Code example](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#code-example)
  - [Job payload](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#job-payload)
  - [Job metadata and errors](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#job-metadata-and-errors)
  - [Circuit transpilation](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#circuit-transpilation)
  - [Note on qubit mapping](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#note-on-qubit-mapping)
  - [Note on circuit duration check](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#note-on-circuit-duration-check)
  - [Note on environment variables](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#note-on-environment-variables)
  - [Integration testing](https://docs.iqm.tech/4.7/iqm-client/integration_guide.html#integration-testing)
- [API reference](https://docs.iqm.tech/4.7/iqm-client/API.html)
  - [iqm_client](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.html)
  - [iqm_server_client](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.html)
  - [cirq_iqm](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.html)
  - [qiskit_iqm](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.html)
  - [qrisp_iqm](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.html)

- [Common errors](https://docs.iqm.tech/4.7/iqm-client/common_errors.html)
- [References](https://docs.iqm.tech/4.7/iqm-client/references.html)
- [Changelog](https://docs.iqm.tech/4.7/iqm-client/changelog.html)
- [License](https://docs.iqm.tech/4.7/iqm-client/license.html)

## Indices and tables

- [Index](https://docs.iqm.tech/4.7/iqm-client/genindex.html)

- [Module Index](https://docs.iqm.tech/4.7/iqm-client/py-modindex.html)

- [Search Page](https://docs.iqm.tech/4.7/iqm-client/search.html)
