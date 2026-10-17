> Full piece: [https://docs.openquantum.com/concepts/backends/](https://docs.openquantum.com/concepts/backends/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 82f1ba8752189c2b52115d70e31e150294d81589734ee159a03be97f769cdb05.

# Backends

Open Quantum provides access to quantum processing units (QPUs) through a unified interface. Each backend is represented as a **backend class** with a unique short code.

## Backend Types

| Type | Description |
|----|----|
| **QPU** | Real quantum hardware. Circuits run on physical qubits with real noise characteristics. |

## Backend Properties

Each backend exposes the following properties:

| Property | Type | Description |
|----|----|----|
| `id` | UUID | Unique identifier. |
| `short_code` | string | Human-readable identifier (e.g., `ionq:forte-1`). Used as the `backend` parameter in all SDKs. |
| `name` | string | Display name. |
| `type` | `QPU` | Backend type. |
| `status` | `Online`, `Offline`, or `Maintenance` | Current operational state of the backend. |
| `accepting_jobs` | boolean | Whether the backend is accepting new job submissions. |
| `queue_depth` | integer | Number of jobs currently waiting in the queue. |

## Backend Status

| Status | Meaning |
|----|----|
| **Online** | The backend is operational and can execute jobs. |
| **Offline** | The backend is unavailable (hardware issues or other problems). |
| **Maintenance** | The backend is temporarily unavailable for scheduled maintenance. |

Note

A backend can be `Online` but have `accepting_jobs: false` if it is temporarily paused for job intake (e.g., during calibration). Check both fields before submitting jobs.

## Listing Backends

Core SDKQiskit PluginPennyLane Plugin

``` python
from openquantum_sdk.clients import ManagementClient

management = ManagementClient(auth=auth)
result = management.list_backend_classes()
for bc in result.backend_classes:
    print(f"{bc.short_code}: {bc.name} ({bc.type})")
```

``` python
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService()
backends = service.backends(online=True)
for b in backends:
    print(f"{b['short_code']}: {b['name']} ({b['type']})")
```

PennyLane devices are created by short code. Use the Core SDK's `ManagementClient` to discover available backends, then pass the short code to `qml.device`:

``` python
from openquantum_sdk.clients import ManagementClient
import pennylane as qml

# List available backends
management = ManagementClient(auth=auth)
result = management.list_backend_classes()
for bc in result.backend_classes:
    print(f"{bc.short_code}: {bc.name} ({bc.type})")

# Create a device targeting any available backend
dev = qml.device("openquantum.device", wires=2, shots=1024,
                  backend="ionq:forte-1")
```

## Related Pages

- [Core SDK Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Listing backends with the Core SDK.
- [Qiskit Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Qiskit backend capabilities.
- [PennyLane Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) -- Choosing backends in PennyLane.
- [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) -- How jobs are executed on backends.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- How backend choice affects pricing.
