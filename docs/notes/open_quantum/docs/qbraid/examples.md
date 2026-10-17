> Full piece: [https://docs.openquantum.com/qbraid/examples/](https://docs.openquantum.com/qbraid/examples/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3327312948dadff542c83b058e0369d5281fd01a9d7ab6a97899f9c57e7f6487.

# Examples

Common quantum circuits utilizing a range of qBraid-compatible frameworks, ready to run in qBraid Lab or your preferred local code editor.

Note

In [qBraid Lab](https://www.qbraid.com/lab), the qBraid SDK is preinstalled and your API key is detected automatically, so you can drop the `api_key` argument: `provider = QbraidProvider()`.

## Bell State (Qiskit)

Target an Open Quantum backend from the qBraid runtime, build a Bell state with Qiskit, run it, and print the measurement counts.

``` python
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

# Your qBraid API key (auto-detected inside qBraid Lab)
provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")

# Target an Open Quantum backend
device = provider.get_device("openquantum:iqm:qpu:garnet")

# Build a Bell state with standard Qiskit
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1]) 

# Run on real quantum hardware
job = device.run(circuit, shots=1024)
result = job.result()
print(result.data.get_counts())
# e.g. {'00': 503, '11': 521}
```

Note

When submitting jobs through the `QbraidProvider`, you can specify optional parameters using the `runtime_options` argument: `runtime_options={"parameter": "value"}`. The `runtime_options` dictionary is passed directly to the backend, so you can use any parameters supported by the Open Quantum SDK.

## Bell State (Cirq)

The same Bell state, built in Cirq.

``` python
from qbraid.runtime import QbraidProvider
import cirq

provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")
device = provider.get_device("openquantum:iqm:qpu:garnet")

# Build a Bell state with Cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key="result"),
)

job = device.run(
    circuit, 
    shots=1024,
    runtime_options={ # Optional parameters
        "organization_id": "None", # Organization UUID
        "execution_plan": "public", # Execution plan ('public', 'private', 'auto') 
        "queue_priority": "standard", # Queue priority ('standard', 'priority', 'auto') 
        "job_subcategory_id": "oth:oth", # Job subcategory short code (list possible ids with the Open Quantum SDK 'SchedulerClient')
        "job_timeout_seconds": "86400" # Maximum time to wait for a job to complete
        }
    )
result = job.result()
print(result.data.get_counts())
```

## GHZ State (Qiskit)

3-qubit GHZ State using Qiskit.

``` python
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")
device = provider.get_device("openquantum:iqm:qpu:garnet")

# 3-qubit GHZ state
circuit = QuantumCircuit(3, 3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(1, 2)
circuit.measure([0, 1, 2], [0, 1, 2])

job = device.run(circuit, shots=1024)
result = job.result()
print(result.data.get_counts())
# e.g. {'000': 490, '111': 502, '010': 16, '101': 16}
```

## Parameterized Rotation with Expectation Value (PennyLane)

Use qBraid's PennyLane plugin to sweep an `RX` rotation angle and measure the expectation value of `PauliZ`.

``` python
import numpy as np
import pennylane as qml
from pennylane.tape import QuantumTape

from qbraid import QbraidProvider

provider = QbraidProvider(api_key="YOUR_QBRAID_API_KEY")
device = provider.get_device("openquantum:iqm:qpu:garnet")

def rotation_circuit(angle, shots=10):
    with QuantumTape() as tape:
        qml.RX(angle, wires=0)
        qml.sample(wires=0)

    job = device.run(tape, shots=shots)
    result = job.result()
    counts = result.data.get_counts()

    # Compute <Z> manually from measured bitstrings: +1 for '0', -1 for '1'
    total = sum(counts.values())
    expval = sum((1 if bit == "0" else -1) * n for bit, n in counts.items()) / total
    return expval

# Sweep over angles from 0 to 2*pi
angles = np.linspace(0, 2 * np.pi, 8)
for angle in angles:
    result = rotation_circuit(angle)
    print(f"RX({angle:.2f}):  = {result:.4f}")

# e.g.
# RX(0.00):  = 1.0000
# RX(0.90):  = 0.6235
# RX(1.80):  = -0.2272
# RX(2.69):  = -0.9010
# RX(3.59):  = -0.9010
# RX(4.49):  = -0.2272
# RX(5.39):  = 0.6235
# RX(6.28):  = 1.0000
```

Tip

Simply change the device id to run the same circuit on different hardware, for example `provider.get_device("openquantum:ionq:qpu:forte-1")`. See [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) for the full list.

## Next Steps

- [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) -- all Open Quantum device ids.
- [Installation & Authentication](https://docs.openquantum.com/qbraid/installation/) -- account linking and credentials.
