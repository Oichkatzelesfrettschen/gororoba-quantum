> Full piece: [https://docs.openquantum.com/qbraid/backends-targets/](https://docs.openquantum.com/qbraid/backends-targets/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2fc5d77a2bc0a97d4894ebef1a5484a332af1bd28a0c2d0ee6bebff307a1d36f.

# Backends & Targets

Open Quantum exposes its QPUs to qBraid as devices. This page covers how to discover and target them.

## Backend IDs

qBraid device ids are hierarchical, colon-separated strings of the form `provider:vendor:type:device`. Open Quantum devices use the `openquantum` provider. For example, to target IQM Garnet:

[](#__codelineno-0-1)`openquantum:iqm:qpu:garnet`\

The following Open Quantum backends are available through qBraid:

| QPU | Technology | Qubits | qBraid device id |
|----|----|----|----|
| IonQ Forte 1 | Trapped ion | 36 | `openquantum:ionq:qpu:forte-1` |
| IonQ Forte Enterprise 1 | Trapped ion | 36 | `openquantum:ionq:qpu:forte-enterprise` |
| Rigetti Cepheus-1-108Q | Superconducting | 108 | `openquantum:rigetti:qpu:cepheus-1-108q` |
| IQM Emerald | Superconducting | 54 | `openquantum:iqm:qpu:emerald` |
| IQM Garnet | Superconducting | 20 | `openquantum:iqm:qpu:garnet` |
| AQT IBEX Q1 | Trapped ion | 12 | `openquantum:aqt:qpu:ibex-q1` |

## Listing Devices

### From the qBraid SDK

Use `QbraidProvider` to enumerate the devices available to your linked account:

[](#__codelineno-1-1)`from`` ``qbraid.runtime`` ``import`` ``QbraidProvider`\
[](#__codelineno-1-2)\
[](#__codelineno-1-3)`provider`` ``=`` ``QbraidProvider``(``api_key``=``"YOUR_QBRAID_API_KEY"``)`\
[](#__codelineno-1-4)\
[](#__codelineno-1-5)`# All devices visible to your account`\
[](#__codelineno-1-6)`for`` ``device`` ``in`` ``provider``.``get_devices``():`\
[](#__codelineno-1-7)`    ``print``(``device``.``id``)`\
[](#__codelineno-1-8)\
[](#__codelineno-1-9)`# Fetch a specific Open Quantum backend`\
[](#__codelineno-1-10)`device`` ``=`` ``provider``.``get_device``(``"openquantum:iqm:qpu:garnet"``)`\

### From the qBraid Website

Open Quantum backends appear under **Devices** in the qBraid dashboard once your accounts are linked. You can also browse status and metadata.

## Supported Operations

You can write circuits in any framework qBraid supports (Qiskit, Cirq, Braket, OpenQASM, and more). qBraid transpiles your program and Open Quantum applies backend-specific transformations before execution, so standard gate sets work without manual decomposition.

Native gate sets, qubit connectivity, and features such as mid-circuit measurement vary by QPU. Transpilation maps your circuit onto the target, but operations a device cannot support will be rejected.

Note

Every run requires a finite `shots` value. Analytic/statevector mode is not available on hardware.

## Next Steps

- [Examples](https://docs.openquantum.com/qbraid/examples/) -- complete, runnable examples.
