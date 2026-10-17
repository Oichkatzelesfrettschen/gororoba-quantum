> Full piece: [https://docs.openquantum.com/qiskit-plugin/examples/](https://docs.openquantum.com/qiskit-plugin/examples/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 404c46112a374eaa57ecbc8e4c3fcacf5f03e091aa58e9bcf762d79a5bfffbd5.

# Qiskit Plugin Examples

Common Qiskit workflows using the `openquantum-sdk[qiskit]` plugin.

Note

All examples assume you have valid credentials configured. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for setup options.

## Bell State with Sampler

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService
from qiskit.circuit import QuantumCircuit

service = OpenQuantumService(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

backend = service.return_backend("rigetti:cepheus-1-108q")

sampler = service.create_sampler(
    backend=backend,
    job_subcategory_id="phys:oth",  # Physics
)

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

job = sampler.run([qc], shots=128)
result = job.result()
counts = result[0].data.meas.get_counts()
print(f"Bell state counts: {counts}")

service.close()
```

## Expectation Value with Estimator

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

service = OpenQuantumService(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

backend = service.return_backend("rigetti:cepheus-1-108q")

estimator = service.create_estimator(
    backend=backend,
    job_subcategory_id="phys:oth",  # Physics
)

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

observable = SparsePauliOp("ZZ")

job = estimator.run([(qc, observable)])
result = job.result()
print(f"<ZZ> = {result[0].data.evs}")

service.close()
```

## Multi-Circuit Batch with Sampler

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService
from qiskit.circuit import QuantumCircuit

service = OpenQuantumService(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

backend = service.return_backend("rigetti:cepheus-1-108q")

sampler = service.create_sampler(
    backend=backend,
    job_subcategory_id="oth:oth",
)

# Circuit 1: Bell state
qc1 = QuantumCircuit(2, 2)
qc1.h(0)
qc1.cx(0, 1)
qc1.measure([0, 1], [0, 1])

# Circuit 2: GHZ state
qc2 = QuantumCircuit(3, 3)
qc2.h(0)
qc2.cx(0, 1)
qc2.cx(1, 2)
qc2.measure([0, 1, 2], [0, 1, 2])

# Submit both circuits
job = sampler.run([qc1, qc2], shots=128)
result = job.result()

print(f"Bell state: {result[0].data.meas.get_counts()}")
print(f"GHZ state:  {result[1].data.meas.get_counts()}")

service.close()
```

## Backend Selection and Filtering

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

# List all online QPU backends
qpu_backends = service.backends(online=True, device_type="QPU")
for b in qpu_backends:
    print(f"{b['short_code']}: {b['name']} (queue: {b['queue_depth']})")

# Search by name
ionq = service.backends(name="ionq")
for b in ionq:
    print(f"{b['short_code']}: {b['name']}")

service.close()
```

## Using a Saved Account

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService

# Save credentials once
OpenQuantumService.save_account(
    name="default",
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

# Load from saved account in future sessions
service = OpenQuantumService.from_saved_account()

# Or let it auto-load
service = OpenQuantumService()

backends = service.backends()
print(f"Found {len(backends)} backends")

service.close()
```

## Related Pages

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Installation and first circuit.
- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- SamplerV2 and EstimatorV2 reference.
