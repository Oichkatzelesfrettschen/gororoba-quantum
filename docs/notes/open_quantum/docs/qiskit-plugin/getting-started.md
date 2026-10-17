> Full piece: [https://docs.openquantum.com/qiskit-plugin/getting-started/](https://docs.openquantum.com/qiskit-plugin/getting-started/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 15223985350e8abc0ebc3f35105ed3f2ba89309a5061d0afedfb63b354f34988.

# Qiskit Plugin Getting Started

## Install

``` bash
pip install "openquantum-sdk[qiskit]"
```

This installs the Qiskit plugin along with `openquantum-sdk` (Core SDK) and `qiskit>=2.0.0`.

## Create a Service

### With Credentials

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)
```

### With a Saved Account

If you have previously saved credentials (see [Authentication](https://docs.openquantum.com/core-sdk/authentication/)):

``` python
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService.from_saved_account(name="default")
```

### With a JWT Token

``` python
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService(token="your_jwt_token")
```

### Auto-Load

If you have a saved account named `"default"`, the service loads it automatically:

``` python
service = OpenQuantumService()
```

When that account is missing or cannot be loaded, the same constructor falls back to environment credentials: `OPENQUANTUM_TOKEN`, an SDK-key file at `OPENQUANTUM_SDK_KEY`, or `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET`. An explicit `token` or `creds` argument still wins, and a saved account still wins over the environment.

Tip

Set `OPENQUANTUM_NO_AUTOLOAD=1` to skip the saved account and use only the environment credentials.

### Service URLs from the environment

`OpenQuantumService()` does not read the playbook URL variables. Use `from_env()` when you want `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. That call does not autoload a saved account, and it raises `AuthenticationError` when no credential resolves:

``` python
service = OpenQuantumService.from_env()
```

## Run a Simple Circuit

``` python
from qiskit.circuit import QuantumCircuit

# Get a backend
backend = service.return_backend("rigetti:cepheus-1-108q")

# Build a Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Run on Open Quantum
job = backend.run(qc, shots=128)
result = job.result()
counts = result.get_counts()
print(counts)
```

Expected output:

``` python
{'00': 512, '11': 512}
```

Note

Counts use bitstring keys, zero-padded to the circuit's classical register width and ordered most-significant-bit first (matching Qiskit's convention).

## Get Results

The `backend.run()` method returns an immediate result job. Call `.result()` to access the Qiskit `Result` object:

``` python
job = backend.run(qc, shots=128)
result = job.result()

# Get counts
counts = result.get_counts()

# Get memory (individual shot results)
memory = result.get_memory()
```

## Clean Up

Close the service when done to release HTTP connections:

``` python
service.close()
```

Or use the context manager:

``` python
with OpenQuantumService(creds=creds) as service:
    backend = service.return_backend("rigetti:cepheus-1-108q")
    job = backend.run(qc, shots=128)
    result = job.result()
```

## Next Steps

- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities and filtering.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- Use SamplerV2 and EstimatorV2.
- [Examples](https://docs.openquantum.com/qiskit-plugin/examples/) -- More Qiskit workflows.
