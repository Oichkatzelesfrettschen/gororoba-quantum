> Full piece: [https://docs.openquantum.com/qiskit-plugin/overview/](https://docs.openquantum.com/qiskit-plugin/overview/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 890b7d2cdad29f61a6325cf8c5a1d37fe9a565531320f37d57a41d26ac4294ff.

# Qiskit Plugin Overview

The `openquantum-sdk[qiskit]` package integrates Open Quantum with [Qiskit](https://www.ibm.com/quantum/qiskit), providing a Qiskit `BackendV2`, `SamplerV2`, and `EstimatorV2` that submit circuits to Open Quantum backends.

## Package Features

| Component | Description |
|----|----|
| **OpenQuantumService** | Entry point for authentication, backend discovery, and primitive creation |
| **OpenQuantumBackend** | Qiskit `BackendV2` that submits circuits to Open Quantum |
| **OQSampler** | Qiskit `SamplerV2` for sampling measurement outcomes |
| **OQEstimator** | Qiskit `EstimatorV2` for computing expectation values |

## Supported Backends

The Qiskit plugin builds a Qiskit transpiler `Target` for any backend on the platform. It does not ship a hardcoded device list: `service.return_backend("<short_code>")` fetches that backend's capability definition (native gate set, qubit count, and connectivity) from Open Quantum at runtime, so the plugin always reflects the platform's current backends.

Browse what is available with `service.backends()` or on the [Open Quantum Portal](https://www.openquantum.com), and see [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/). Qiskit's transpiler uses the fetched target to compile circuits to each backend's native gate set and topology.

## Next Steps

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Install and run your first Qiskit circuit.
- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities and target building.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- SamplerV2 and EstimatorV2 usage.
- [Examples](https://docs.openquantum.com/qiskit-plugin/examples/) -- Common Qiskit workflows.
