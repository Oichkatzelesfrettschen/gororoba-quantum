> Full piece: [https://docs.openquantum.com/getting-started/resources/](https://docs.openquantum.com/getting-started/resources/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 66a06c839af762d46af6b82906398a0816fea096886aa7caf1a884289d92e963.

# Sample Circuits & Notebooks

Open Quantum provides ready-to-run quantum circuits and Jupyter notebooks to help you get started quickly.

## Sample QASM Circuits

The [Sample QASM](https://www.openquantum.com/sample-qasm) page on the portal has downloadable OpenQASM 2.0 circuits covering fundamental quantum algorithms:

| Circuit             | Algorithm              | Qubits |
|---------------------|------------------------|--------|
| `deutsch_n2.qasm`   | Deutsch's Algorithm    | 2      |
| `grover_n2.qasm`    | Grover's Search        | 2      |
| `cat_state_n4.qasm` | Cat State (GHZ)        | 4      |
| `simon_n6.qasm`     | Simon's Algorithm      | 6      |
| `qaoa_n3.qasm`      | QAOA                   | 3      |
| `bell_n4.qasm`      | Bell State Preparation | 4      |

These can be submitted directly through the [web portal](https://docs.openquantum.com/portal/submitting-jobs/) or via the SDK:

``` python
job = scheduler.submit_job(config, file_path="qft.qasm")
```

## Sample Notebooks

The [Sample Notebooks](https://www.openquantum.com/notebooks) page has Jupyter notebooks that open directly in Google Colab — no local setup required.

| Notebook | Description |
|----|----|
| **Run a Circuit in Python** | Execute a quantum circuit on real hardware using the Open Quantum Python SDK. Connect to IonQ, Rigetti, IQM, and AQT backends. |
| **Run a Simulation with Quantum Rings SDK** | Use the Quantum Rings SDK to run a quantum simulation without needing access to physical hardware. |

## Using Sample Circuits with the SDK

### Core SDK

``` python
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

scheduler = SchedulerClient(auth=auth)

config = JobSubmissionConfig(
    backend_class_id="ionq:forte-1",
    name="Grover Search",
    job_subcategory_id="opt:oth",  # Optimization
    shots=128,
)

job = scheduler.submit_job(config, file_path="grover_n2.qasm")
output = scheduler.download_job_output(job)
print(output)
if job.calibration_data_url:
    print(scheduler.download_job_calibration(job))
```

### Qiskit Plugin

``` python
from qiskit import QuantumCircuit
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService()
backend = service.return_backend("ionq:forte-1")

qc = QuantumCircuit.from_qasm_file("bell_n4.qasm")
job = backend.run(qc, shots=128)
result = job.result()
print(result.get_counts())
```

### PennyLane Plugin

``` python
import pennylane as qml

dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=128,
    backend="ionq:forte-1",
)

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    return qml.counts()

print(bell_state())
```

### Cirq Plugin

``` python
import cirq
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="ionq:forte-1")

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(*q, key="m"),
)

result = sampler.run(circuit, repetitions=128)
print(result.histogram(key="m"))
```

### Qrisp Plugin

``` python
from qrisp import QuantumVariable, h, cx
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(backend="ionq:forte-1", shots=128)

qv = QuantumVariable(2)
h(qv[0])
cx(qv[0], qv[1])

print(qv.get_measurement(backend=oq, shots=128))
```

## Related Pages

- [Submitting Jobs](https://docs.openquantum.com/portal/submitting-jobs/) -- Walk through submitting a job in the web UI.
- [Quick Start (SDK)](https://docs.openquantum.com/core-sdk/quickstart/) -- Submit your first job with Python.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Available quantum hardware.
