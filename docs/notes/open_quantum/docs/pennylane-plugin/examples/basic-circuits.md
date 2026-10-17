> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/](https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9f9e5751d3c84008150c99a59818c1de3b63b4db12e45404968a48a529e61de2.

# Basic Circuits

This page demonstrates common circuit patterns using the Open Quantum PennyLane plugin.

Note

All examples assume you have set the `OPENQUANTUM_CLIENT_ID`, `OPENQUANTUM_CLIENT_SECRET`, and `OPENQUANTUM_ORGANIZATION_ID` environment variables. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for details.

## Bell State with Counts

Create a maximally entangled two-qubit state and measure bitstring counts:

``` python
import pennylane as qml

dev = qml.device("openquantum.device", wires=2, shots=128, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.counts()

result = bell_state()
print(result)
```

Expected output:

``` python
{'00': 507, '11': 517}
```

The Bell state \\\|\Phi^+\rangle = \frac{1}{\sqrt{2}}(\|00\rangle + \|11\rangle)\\ produces only the bitstrings `00` and `11`, each with approximately 50% probability.

## GHZ State with Probabilities

Create a 3-qubit GHZ state and measure the probability distribution:

``` python
import pennylane as qml

dev = qml.device("openquantum.device", wires=3, shots=4096, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def ghz_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    return qml.probs(wires=[0, 1, 2])

probs = ghz_state()
print(probs)
```

Expected output:

``` python
[0.502, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.498]
```

The GHZ state \\\frac{1}{\sqrt{2}}(\|000\rangle + \|111\rangle)\\ has non-zero probabilities only at indices 0 (`000`) and 7 (`111`).

## Parameterized Rotation Circuit with Expectation Value

Use parameterized gates and measure an observable's expectation value:

``` python
import pennylane as qml
import numpy as np

dev = qml.device("openquantum.device", wires=1, shots=4096, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def rotation_circuit(angle):
    qml.RX(angle, wires=0)
    return qml.expval(qml.PauliZ(0))

# Sweep over angles from 0 to 2*pi
angles = np.linspace(0, 2 * np.pi, 8)
for angle in angles:
    result = rotation_circuit(angle)
    print(f"RX({angle:.2f}): <Z> = {result:.4f}")
```

Expected output:

```
RX(0.00): <Z> = 1.0000
RX(0.90): <Z> = 0.6235
RX(1.80): <Z> = -0.2272
RX(2.69): <Z> = -0.9010
RX(3.59): <Z> = -0.9010
RX(4.49): <Z> = -0.2272
RX(5.39): <Z> = 0.6235
RX(6.28): <Z> = 1.0000
```

The expectation value of \\\langle Z \rangle\\ after an \\R_X(\theta)\\ rotation follows \\\cos(\theta)\\.

Tip

Using more shots (e.g., 4096 instead of 1024) reduces statistical noise in expectation value estimates.

## Multiple Measurements in One Circuit

Return multiple measurement types from a single circuit execution:

``` python
import pennylane as qml

dev = qml.device("openquantum.device", wires=2, shots=2048, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def multi_measurement():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return (
        qml.expval(qml.PauliZ(0)),
        qml.expval(qml.PauliZ(1)),
        qml.probs(wires=[0, 1]),
    )

z0, z1, probs = multi_measurement()
print(f"<Z0> = {z0:.4f}")
print(f"<Z1> = {z1:.4f}")
print(f"P(00, 01, 10, 11) = {probs}")
```

Expected output:

```
<Z0> = 0.0039
<Z1> = -0.0059
P(00, 01, 10, 11) = [0.499 0.001 0.003 0.497]
```

Note

All measurement results in a single QNode call are computed from the same set of shots. PennyLane handles the post-processing to extract each measurement from the raw counts.

## Tensor Product Observables

Measure correlations between qubits using tensor product observables:

``` python
import pennylane as qml

dev = qml.device("openquantum.device", wires=2, shots=4096, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def correlation():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

result = correlation()
print(f"<Z0 Z1> = {result:.4f}")
```

Expected output:

```
<Z0 Z1> = 1.0000
```

For a Bell state, the \\Z \otimes Z\\ correlation is exactly 1 because qubits 0 and 1 are always measured in the same state.

## Next Steps

- [VQE Example](https://docs.openquantum.com/pennylane-plugin/examples/vqe/) -- Variational quantum eigensolver on Open Quantum.
- [QML Workflow](https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/) -- Quantum machine learning classification.
- [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) -- Choosing the right backend.
