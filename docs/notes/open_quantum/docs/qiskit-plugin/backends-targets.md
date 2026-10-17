> Full piece: [https://docs.openquantum.com/qiskit-plugin/backends-targets/](https://docs.openquantum.com/qiskit-plugin/backends-targets/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3280f13a81f74d8e7ea12ec2b0a66e6dac730b216183581ca882ae91b44aec71.

# Backends & Targets

The Qiskit plugin provides backend discovery through `OpenQuantumService` and Qiskit `Target` objects that describe each backend's native gate set, topology, and qubit count.

## Listing Backends

Use `service.backends()` to list available backends with optional filters:

``` python
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService()

# All backends
all_backends = service.backends()

# Filter by availability
online = service.backends(online=True)

# Filter by type
qpus = service.backends(device_type="QPU")

# Filter by name or short code
ionq = service.backends(name="ionq")

# Filter by provider ID
rigetti = service.backends(vendor_id="rigetti-provider-uuid")
```

Each backend is returned as a dictionary:

``` python
{
    "id": "uuid",
    "name": "IonQ Forte-1",
    "description": "IonQ Forte-1 trapped-ion QPU",
    "type": "QPU",
    "provider_id": "uuid",
    "short_code": "ionq:forte-1",
    "queue_depth": 3,
    "accepting_jobs": True,
    "status": "Online",
}
```

## Getting a Backend Instance

Use `service.return_backend()` to get a Qiskit `BackendV2` instance:

``` python
# Simple usage: returns a clean BackendV2 for the target.
# job_subcategory_id lives at job creation time (see .run() or create_* below).
backend = service.return_backend("ionq:forte-1")

# Pass config for per-backend defaults (e.g. for repeated .run() calls without
# repeating options). job_subcategory_id can be supplied here as a default
# or overridden at the actual run/create time.
backend = service.return_backend(
    "ionq:forte-1",
    config={
        "job_subcategory_id": "phys:oth",  # default for this backend's .run() calls
        "organization_id": "...",
    },
)
```

### Config Dictionary

The optional `config` parameter on `return_backend()` lets you supply defaults for job submission metadata that will be used by direct `backend.run(...)` calls (they can still be overridden per-call). The more common place for `job_subcategory_id` is when creating jobs/primitives.

| Key | Required | Description |
|----|----|----|
| `backend_class_id` | No (defaults to the `name` arg to `return_backend`) | Backend identifier (UUID or short code) |
| `job_subcategory_id` | No (can be supplied here as a default for `.run()`; otherwise defaults to `"oth:oth"` at run time) | Job subcategory (UUID or short code). Best supplied at job creation. |
| `organization_id` | No | Organization UUID (auto-discovered if omitted) |
| `name` | No | Job name prefix |
| `configuration_data` | No | Provider-specific configuration |
| `execution_plan` | No | `"auto"` (default), `"public"`, `"private"`, an `ExecutionPlanType` value, or a plan UUID. `"auto"` picks the cheapest plan. |
| `queue_priority` | No | `"auto"` (default), `"standard"`, `"priority"`, `"instant"`, a `QueuePriorityType` value, or a priority UUID. `"auto"` picks the cheapest priority. |
| `verbose` | No | `False`. Print submission progress and the credit cost. Same default on every plugin. Also a `return_backend(..., verbose=)` argument and a per-`run()` override. |
| `job_timeout_seconds` | No | `86400` (one day). Maximum wait for the job to finish. Also a `return_backend(..., job_timeout_seconds=)` argument and a per-`run()` override. |

### Export Format

The `export_format` parameter controls how circuits are serialized for submission:

``` python
# OpenQASM 3 (default)
backend = service.return_backend("ionq:forte-1", export_format="qasm3")

# OpenQASM 2
backend = service.return_backend("ionq:forte-1", export_format="qasm2")
```

Other code that already has a Qiskit circuit can call the public helper. Import it from the package, not from the private `_qasm` module:

``` python
from openquantum_sdk_qiskit import export_circuit_to_qasm

payload = export_circuit_to_qasm(circuit, "qasm3")
```

`fmt` is `"qasm2"` or `"qasm3"`. Pass `backend=` when you want capability checks before export. The Qrisp plugin uses this helper.

## `list_backends` and `get_backend`

`openquantum_sdk.qiskit` also exposes two module-level helpers:

``` python
from openquantum_sdk.qiskit import get_backend, list_backends

rows = list_backends(name="ionq", online=True)
backend = get_backend("ionq:forte-1")
```

`get_backend` reads `OPENQUANTUM_ORGANIZATION_ID` when `organization_id` is omitted. `job_subcategory_id` defaults to `"oth:oth"`. The old environment names `OQ_ORG_ID` and `OQ_SUBCATEGORY_ID` are not read. The backend it returns keeps its service session open, so later `run()` calls can reuse it. `list_backends` still closes a service it created, because it returns plain dictionaries. Pass `service=` to use a client you already opened.

## Getting a Target

Use `service.return_target()` to get a Qiskit `Target` without creating a full backend:

``` python
target = service.return_target("ionq:forte-1")
print(f"Qubits: {target.num_qubits}")
print(f"Operations: {target.operation_names}")
```

Targets are useful for transpilation without submission.

## Backend Capabilities

The plugin does not ship hardcoded device data. When you call `service.return_backend("<short_code>")`, it fetches that backend's capability definition (native gate set, qubit count, connectivity, and configuration schema) from the platform and builds a Qiskit `Target` from it. This means the plugin always reflects the platform's current backends.

`return_backend` accepts:

| Argument | Description |
|----|----|
| `name` | Backend `id`, `short_code`, or `name` (e.g. `"rigetti:cepheus-1-108q"`). |
| `config` | Optional submission metadata (`organization_id`, `name`, `execution_plan`, `queue_priority`, `configuration_data`, `verbose`, `job_timeout_seconds`). |
| `export_format` | `"qasm2"` or `"qasm3"` (default). |
| `verbose` | Print submission progress and the credit cost. Default `False`. |
| `job_timeout_seconds` | Max seconds to wait for a job. Default `86400`. |

``` python
backend = service.return_backend("rigetti:cepheus-1-108q")
# A Qiskit BackendV2 whose Target is compiled from the platform's
# capability definition; use it directly with transpile() and run().
```

If the named backend's capabilities cannot be found on the platform, `return_backend` raises `ValueError`.

## Related Pages

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Install and first circuit.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- Primitives for sampling and estimation.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Platform-level backend concepts.
