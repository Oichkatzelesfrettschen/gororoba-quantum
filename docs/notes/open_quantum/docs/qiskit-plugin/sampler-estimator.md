> Full piece: [https://docs.openquantum.com/qiskit-plugin/sampler-estimator/](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1438e8ce041a9086f88979fdaca5dbfec138d4dd561b354f6a9277d4d8624c5b.

# Sampler & Estimator

The Qiskit plugin provides `OQSampler` (SamplerV2) and `OQEstimator` (EstimatorV2) primitives that submit circuits to Open Quantum for execution.

## OQSampler (SamplerV2)

`OQSampler` implements Qiskit's `BaseSamplerV2` interface. It submits circuits to Open Quantum and returns measurement results as `BitArray` objects.

### Creating a Sampler

Use `service.create_sampler()`:

``` python
from openquantum_sdk.auth import ClientCredentials
from openquantum_sdk_qiskit import OpenQuantumService

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
    verbose=False,                  # default; True prints progress and credit cost
    job_timeout_seconds=86400,      # default, one day
)
```

`verbose` and `job_timeout_seconds` are the same on every Open Quantum plugin. Both default as above. Omit them to inherit the values already set on the backend from `return_backend`. `create_estimator` accepts the same two arguments. `backend.run(..., verbose=, job_timeout_seconds=)` overrides them for one submission.

### Running the Sampler

``` python
from qiskit.circuit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

job = sampler.run([qc], shots=128)
result = job.result()

# Access the first pub result
pub_result = result[0]
bit_array = pub_result.data.meas
counts = bit_array.get_counts()
print(counts)
```

Expected output:

``` python
{'00': 507, '11': 517}
```

### Shots Configuration

Specify shots per run:

``` python
job = sampler.run([qc], shots=4096)
```

If `shots` is not specified, it defaults to 100.

### Parameter Binding

The sampler supports parameterized circuits with automatic binding:

``` python
from qiskit.circuit import QuantumCircuit, Parameter

theta = Parameter("theta")

qc = QuantumCircuit(1, 1)
qc.rx(theta, 0)
qc.measure(0, 0)

# Single parameter value
job = sampler.run([(qc, [0.5])], shots=128)

# Multiple parameter values
import numpy as np
values = np.linspace(0, np.pi, 5)
job = sampler.run([(qc, values.reshape(-1, 1))], shots=128)
```

### Export Format

Control the QASM export format:

``` python
# Use OpenQASM 2 instead of the default OpenQASM 3
job = sampler.run([qc], shots=128, export_format="qasm2")
```

## OQEstimator (EstimatorV2)

`OQEstimator` implements Qiskit's `BaseEstimatorV2` interface. It computes expectation values of observables by delegating to Qiskit's `BackendEstimatorV2` with an Open Quantum backend.

### Creating an Estimator

``` python
estimator = service.create_estimator(
    backend=backend,
    job_subcategory_id="phys:oth",  # Physics
)
```

### Running the Estimator

``` python
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

observable = SparsePauliOp("ZZ")

job = estimator.run([(qc, observable)], precision=0.01)
result = job.result()

print(f"Expectation value: {result[0].data.evs}")
```

### Precision

The `precision` parameter controls the target precision for the expectation value estimate:

``` python
# Higher precision (more shots internally)
job = estimator.run([(qc, observable)], precision=0.001)

# Lower precision (fewer shots, faster)
job = estimator.run([(qc, observable)], precision=0.1)
```

### Multiple Observables

``` python
obs_zz = SparsePauliOp("ZZ")
obs_xx = SparsePauliOp("XX")

job = estimator.run([
    (qc, obs_zz),
    (qc, obs_xx),
])
result = job.result()

print(f"<ZZ> = {result[0].data.evs}")
print(f"<XX> = {result[1].data.evs}")
```

## Direct Construction

You can also construct the primitives directly without `service.create_sampler()` or `service.create_estimator()`:

``` python
from openquantum_sdk_qiskit import OQSampler, OQEstimator

sampler = OQSampler(
    backend=backend,
    scheduler=service.scheduler,
    config={
        "backend_class_id": "rigetti:cepheus-1-108q",
        "job_subcategory_id": "phys:oth",  # Physics
    },
    export_format="qasm3",
)

estimator = OQEstimator(
    backend=backend,
    scheduler=service.scheduler,
    config={
        "backend_class_id": "rigetti:cepheus-1-108q",
        "job_subcategory_id": "phys:oth",  # Physics
    },
    export_format="qasm3",
)
```

## Related Pages

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Install and first circuit.
- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities.
- [Examples](https://docs.openquantum.com/qiskit-plugin/examples/) -- Complete Qiskit workflows.
