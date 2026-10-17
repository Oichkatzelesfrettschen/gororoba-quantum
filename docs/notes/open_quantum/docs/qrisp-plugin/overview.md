> Full piece: [https://docs.openquantum.com/qrisp-plugin/overview/](https://docs.openquantum.com/qrisp-plugin/overview/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2cf384c7cc0d26a6cee5bc6bd55c3afce0187d5970ae353ea99774ed825797b6.

# Qrisp Plugin Overview

Beta

The Qrisp plugin is in **beta**. It works end to end, but the API and defaults may still change. We'd love your feedback: join the [Quantum Rings community](https://www.quantumrings.com/community).

The `openquantum-sdk[qrisp]` plugin connects [Qrisp](https://www.qrisp.eu/index.html) to the Open Quantum platform, letting you run high-level Qrisp programs on real QPU hardware. It builds on the [Core SDK](https://docs.openquantum.com/core-sdk/overview/) (`openquantum-sdk`) for authentication and job submission, and on the [Qiskit plugin](https://docs.openquantum.com/qiskit-plugin/overview/) for circuit conversion.

Qrisp is an open-source, high-level quantum programming language — an Eclipse Foundation project developed with Fraunhofer FOKUS. Learn more at the [Qrisp website](https://www.qrisp.eu/index.html) and the [Qrisp GitHub repository](https://github.com/eclipse-qrisp/Qrisp).

## Installation

[](#__codelineno-0-1)`pip`` ``install`` ``"openquantum-sdk[qrisp]"`\

This pulls in `qrisp`, `openquantum-sdk`, and `openquantum-sdk-qiskit`. There is no entry-point registration step: you import `OpenQuantumBackend` and pass it to Qrisp at call time.

## What the Plugin Does

Qrisp already depends on Qiskit and can convert any program to a Qiskit circuit (`QuantumCircuit.to_qiskit()`). The Open Quantum backend uses that bridge, so it reuses the Qiskit plugin's serializer and capability validation rather than reimplementing them. When you call `get_measurement` (or `qc.run`) with an `OpenQuantumBackend`, the plugin:

1.  **Compiles** your Qrisp program to a Qiskit circuit.
2.  **Flattens** it onto a single quantum register (the platform precompiler requires one).
3.  **Validates** it against the target backend's capabilities (gate set, coupling map, shot and qubit limits).
4.  **Converts** it to OpenQASM and submits it through the Core SDK scheduler.
5.  **Returns results** in Qrisp's native decoded form, so the rest of your program is unchanged.

## Quick Example

[](#__codelineno-1-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-1-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-1-5)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-1-6)`    ``shots``=``1024``,`\
[](#__codelineno-1-7)`    ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-1-8)`    ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-1-9)`)`\
[](#__codelineno-1-10)\
[](#__codelineno-1-11)`qv`` ``=`` ``QuantumVariable``(``2``)`\
[](#__codelineno-1-12)`h``(``qv``[``0``])`\
[](#__codelineno-1-13)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-1-14)\
[](#__codelineno-1-15)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``1024``))`\
[](#__codelineno-1-16)`# {'00': 0.51, '11': 0.49}`\

Tip

Set `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` as environment variables to avoid passing credentials in code. See the [Authentication](https://docs.openquantum.com/core-sdk/authentication/) guide.

### Key Components

| Component | Description |
|----|----|
| **OpenQuantumBackend** | Qrisp `Backend` subclass. Implements `run_async()` to execute programs on Open Quantum. |
| **OpenQuantumJob** | Qrisp `Job` wrapper holding the completed counts. |
| **Qiskit serializer** | `export_circuit_to_qasm`, imported from the public `openquantum_sdk_qiskit` package, converts circuits to OpenQASM. |
| **Core session** | Shared `OpenQuantumClient` auth, token caching, and job submission. |

## Supported Backends

The plugin works with any backend on the Open Quantum platform, identified by its `short_code` (e.g. `"ionq:forte-1"`, `"rigetti:cepheus-1-108q"`). Discover backends with the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/), the [Qiskit plugin](https://docs.openquantum.com/qiskit-plugin/backends-targets/), or the [Open Quantum Portal](https://www.openquantum.com).

## Shot-Based Execution Only

Open Quantum is a shot-based platform. Every execution requires a finite number of shots, set via the backend's `shots` option or the `shots=` argument to `get_measurement` / `run`.

## Next Steps

- [Getting Started](https://docs.openquantum.com/qrisp-plugin/getting-started/) — install, authenticate, and run.
- [Supported Operations](https://docs.openquantum.com/qrisp-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/qrisp-plugin/examples/) — Bell states, QuantumFloat arithmetic, and backend selection.
- [Troubleshooting](https://docs.openquantum.com/qrisp-plugin/troubleshooting/) — auth, backend config, and common errors.
