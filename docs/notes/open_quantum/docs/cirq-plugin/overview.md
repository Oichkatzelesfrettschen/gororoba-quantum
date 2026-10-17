> Full piece: [https://docs.openquantum.com/cirq-plugin/overview/](https://docs.openquantum.com/cirq-plugin/overview/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b84c0e7f72b29d11261c3f2d8b2c581299742ef0e59879338801615d4810f8c9.

# Cirq Plugin Overview

Beta

The Cirq plugin is in **beta**. It works end to end, but the API and defaults may still change. We'd love your feedback: join the [Quantum Rings community](https://www.quantumrings.com/community).

The `openquantum-sdk[cirq]` plugin connects [Cirq](https://quantumai.google/cirq) to the Open Quantum platform, letting you run Cirq circuits on real QPU hardware. It builds on the [Core SDK](https://docs.openquantum.com/core-sdk/overview/) (`openquantum-sdk`) for authentication and job submission.

Cirq is an open-source Python framework for writing, manipulating, and optimizing quantum circuits, created and maintained by Google Quantum AI. Learn more at the [Cirq website](https://quantumai.google/cirq) and the [Cirq GitHub repository](https://github.com/quantumlib/cirq).

## Installation

[](#__codelineno-0-1)`pip`` ``install`` ``"openquantum-sdk[cirq]"`\

This pulls in `cirq-core` and `openquantum-sdk`. There is no entry-point registration step: you import `OpenQuantumSampler` and use it anywhere a `cirq.Sampler` is accepted.

## What the Plugin Does

Cirq exports OpenQASM natively (`cirq.Circuit.to_qasm()`), so — unlike the Qrisp plugin — it does not route through the Qiskit plugin. `OpenQuantumSampler` is a thin [`cirq.Sampler`](https://quantumai.google/reference/python/cirq/Sampler). When you call `run` (or any sampler method), the plugin:

1.  **Resolves** parameters for each circuit in the sweep.
2.  **Serializes** the resolved circuit to OpenQASM. Cirq maps all qubits onto a single `qreg q[N]`, which is exactly what the platform precompiler requires.
3.  **Submits** it through the Core SDK scheduler.
4.  **Reconstructs** the platform's `{bitstring: count}` histogram into a native `cirq.Result`, so `result.histogram(...)`, `result.measurements`, and friends work as usual.

Because it implements `run_sweep`, the standard `cirq.Sampler` methods — `run`, `sample`, `run_sweep`, and `run_batch` — all work.

## Quick Example

[](#__codelineno-1-1)`import`` ``cirq`\
[](#__codelineno-1-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-1-5)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-1-6)`    ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-1-7)`    ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-1-8)`)`\
[](#__codelineno-1-9)\
[](#__codelineno-1-10)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-1-11)`circuit`` ``=`` ``cirq``.``Circuit``([`\
[](#__codelineno-1-12)`    ``cirq``.``H``(``q``[``0``]),`\
[](#__codelineno-1-13)`    ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`\
[](#__codelineno-1-14)`    ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``),`\
[](#__codelineno-1-15)`])`\
[](#__codelineno-1-16)\
[](#__codelineno-1-17)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``1024``)`\
[](#__codelineno-1-18)`print``(``result``.``histogram``(``key``=``"m"``))`\
[](#__codelineno-1-19)`# Counter({0: ~512, 3: ~512})   # 00 and 11`\

Tip

Set `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` as environment variables to avoid passing credentials in code. See the [Authentication](https://docs.openquantum.com/core-sdk/authentication/) guide.

### Key Components

| Component | Description |
|----|----|
| **OpenQuantumSampler** | `cirq.Sampler` subclass. Implements `run_sweep()` to execute circuits on Open Quantum. |
| **result_from_counts** | Rebuilds a `cirq.ResultDict` from a platform counts histogram. |
| **Core session** | Shared `OpenQuantumClient` auth, token caching, and job submission. |

## Supported Backends

The plugin works with any backend on the Open Quantum platform, identified by its `short_code` (e.g. `"ionq:forte-1"`, `"rigetti:cepheus-1-108q"`). Discover backends with the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/) or the [Open Quantum Portal](https://www.openquantum.com).

## Shot-Based Execution Only

Open Quantum is a shot-based platform. Every execution requires a finite number of shots, set via the `repetitions` argument to `run` / `sample` / `run_sweep`. Every circuit must contain at least one measurement; the QASM exporter does not add measurements for you.

## Next Steps

- [Getting Started](https://docs.openquantum.com/cirq-plugin/getting-started/) — install, authenticate, and run.
- [Supported Operations](https://docs.openquantum.com/cirq-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/cirq-plugin/examples/) — Bell states, parameter sweeps, and backend selection.
- [Troubleshooting](https://docs.openquantum.com/cirq-plugin/troubleshooting/) — auth, backend config, and common errors.
