> Full piece: [https://docs.openquantum.com/cirq-plugin/getting-started/](https://docs.openquantum.com/cirq-plugin/getting-started/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3570a14b4ba2c8bc87f73f4b45662efac0eac585cd1bc31ac6bbd4e2f36bc694.

# Cirq Plugin Getting Started

## Install

``` bash
pip install "openquantum-sdk[cirq]"
```

This installs the Cirq sampler along with `cirq-core` and `openquantum-sdk` (Core SDK).

## Create a Sampler

The `OpenQuantumSampler` builds an `OpenQuantumClient` with `from_env()`. Authentication is resolved in this order: a pre-built `client`, then a `token`, then `client_id` + `client_secret` (or an SDK-key file at `OPENQUANTUM_SDK_KEY`). Each explicit value falls back to the matching environment variable. Omitted service URLs also read `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. If nothing resolves, construction raises `AuthenticationError`.

### With Environment Variables (recommended)

``` bash
export OPENQUANTUM_CLIENT_ID="s_your_client_id"
export OPENQUANTUM_CLIENT_SECRET="your_client_secret"
```

``` python
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="rigetti:cepheus-1-108q")
```

### With Explicit Credentials

``` python
sampler = OpenQuantumSampler(
    backend="rigetti:cepheus-1-108q",
    client_id="s_your_client_id",
    client_secret="your_client_secret",
)
```

### With a Pre-built Client

Reuse an existing `OpenQuantumClient` (for saved accounts, custom URLs, or keyring-backed credentials):

``` python
from openquantum_sdk import OpenQuantumClient
from cirq_openquantum import OpenQuantumSampler

client = OpenQuantumClient.from_saved_account(name="default")
sampler = OpenQuantumSampler(backend="rigetti:cepheus-1-108q", client=client)
```

## Run a Circuit

Build a circuit with a measurement and call `run`:

``` python
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(*q, key="m"),
])

result = sampler.run(circuit, repetitions=1024)
print(result.histogram(key="m"))
# Counter({0: ~512, 3: ~512})   # 00 and 11
```

`result` is a standard `cirq.Result`, so `result.measurements["m"]`, `result.histogram(key="m")`, and `cirq.plot_state_histogram(result)` all work.

## Backend-Specific Configuration

Some backends require extra parameters. Simulators in the Quantum Rings family, for example, require an `engine`. Pass these through `configuration_data`:

``` python
sampler = OpenQuantumSampler(
    backend="qr:gpu-gb10",
    configuration_data={"engine": "amber_quantum_rings"},
)
```

Note

Only send the fields a backend actually needs. Conditional schema fields (for example a `threshold` that only applies when `performance="CUSTOM"`) should be set explicitly and only when they apply.

## Cost and Scheduling Controls

``` python
sampler = OpenQuantumSampler(
    backend="ionq:forte-1",
    job_subcategory_id="ml:qcl",   # classify your workload
    execution_plan="private",       # "auto" | "public" | "private"
    queue_priority="priority",      # "auto" | "standard" | "priority" | "instant"
    organization_id="your-org-uuid",
    job_timeout_seconds=3600,       # max wait (default 86400 / 1 day)
)
```

## Next Steps

- [Supported Operations](https://docs.openquantum.com/cirq-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/cirq-plugin/examples/) — more Cirq workflows.
- [Troubleshooting](https://docs.openquantum.com/cirq-plugin/troubleshooting/) — auth, backend config, and common errors.
