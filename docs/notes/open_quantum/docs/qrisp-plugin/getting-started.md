> Full piece: [https://docs.openquantum.com/qrisp-plugin/getting-started/](https://docs.openquantum.com/qrisp-plugin/getting-started/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9c2a62620a249c80bd7cc5ead8a00644c78000d80d9899c9fe3859b096f029f5.

# Qrisp Plugin Getting Started

## Install

``` bash
pip install "openquantum-sdk[qrisp]"
```

This installs the Qrisp backend along with `qrisp`, `openquantum-sdk` (Core SDK), and `openquantum-sdk-qiskit`.

## Create a Backend

The `OpenQuantumBackend` builds an `OpenQuantumService` with `from_env()`. Authentication is resolved in this order: a pre-built `service`, then a `token`, then `client_id` + `client_secret` (or an SDK-key file at `OPENQUANTUM_SDK_KEY`). Each explicit value falls back to the matching environment variable. Omitted service URLs also read `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. If nothing resolves, construction raises `AuthenticationError`.

### With Environment Variables (recommended)

``` bash
export OPENQUANTUM_CLIENT_ID="s_your_client_id"
export OPENQUANTUM_CLIENT_SECRET="your_client_secret"
```

``` python
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(backend="rigetti:cepheus-1-108q", shots=1024)
```

### With Explicit Credentials

``` python
oq = OpenQuantumBackend(
    backend="rigetti:cepheus-1-108q",
    shots=1024,
    client_id="s_your_client_id",
    client_secret="your_client_secret",
)
```

### With a Pre-built Service

Reuse an existing `OpenQuantumService` (for saved accounts, custom URLs, or keyring-backed credentials):

``` python
from openquantum_sdk_qiskit import OpenQuantumService
from qrisp_openquantum import OpenQuantumBackend

service = OpenQuantumService.from_saved_account(name="default")
oq = OpenQuantumBackend(backend="rigetti:cepheus-1-108q", shots=1024, service=service)
```

## Run a Program

Pass the backend to `get_measurement` on a `QuantumVariable`:

``` python
from qrisp import QuantumVariable, h, cx

qv = QuantumVariable(2)
h(qv[0])
cx(qv[0], qv[1])

print(qv.get_measurement(backend=oq, shots=1024))
# {'00': 0.51, '11': 0.49}
```

Note

`get_measurement` returns Qrisp's decoded outcomes as **probabilities**, not shot counts. This is Qrisp's own normalization and applies to every backend. To get integer counts, run a low-level `QuantumCircuit` with `QuantumCircuit.run(backend=oq, shots=...)`, shown next.

Or run a raw `QuantumCircuit` directly, which returns integer counts:

``` python
from qrisp import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1])

counts = qc.run(backend=oq, shots=1024)
# e.g. {'00': 518, '11': 506}
```

## Backend-Specific Configuration

Some backends require extra parameters. Simulators in the Quantum Rings family, for example, require an `engine`. Pass these through `configuration_data`:

``` python
oq = OpenQuantumBackend(
    backend="qr:gpu-gb10",
    shots=1024,
    configuration_data={"engine": "amber_quantum_rings"},
)
```

Note

Only send the fields a backend actually needs. Conditional schema fields (for example a `threshold` that only applies when `performance="CUSTOM"`) should be set explicitly and only when they apply.

## Cost and Scheduling Controls

``` python
oq = OpenQuantumBackend(
    backend="ionq:forte-1",
    shots=1024,
    job_subcategory_id="ml:qcl",   # classify your workload
    execution_plan="private",       # "auto" | "public" | "private"
    queue_priority="priority",      # "auto" | "standard" | "priority" | "instant"
    organization_id="your-org-uuid",
    job_timeout_seconds=3600,       # max wait (default 86400 / 1 day)
)
```

## Next Steps

- [Supported Operations](https://docs.openquantum.com/qrisp-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/qrisp-plugin/examples/) — more Qrisp workflows.
- [Troubleshooting](https://docs.openquantum.com/qrisp-plugin/troubleshooting/) — auth, backend config, and common errors.
