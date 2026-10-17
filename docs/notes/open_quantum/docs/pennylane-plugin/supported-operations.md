> Full piece: [https://docs.openquantum.com/pennylane-plugin/supported-operations/](https://docs.openquantum.com/pennylane-plugin/supported-operations/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4917143176ea494754a172b4be978e865b39acf6136fb3bf36967970afab5cbc.

# Supported Operations

This page lists all PennyLane operations, observables, and measurements supported by the `openquantum.device`.

## Gate Operations

The plugin supports the following PennyLane gate operations, each mapped to its OpenQASM 2.0 equivalent:

### Single-Qubit Gates

| PennyLane Operation | QASM Gate | Parameters | Description           |
|---------------------|-----------|------------|-----------------------|
| `qml.PauliX`        | `x`       | 0          | Pauli-X (NOT) gate    |
| `qml.PauliY`        | `y`       | 0          | Pauli-Y gate          |
| `qml.PauliZ`        | `z`       | 0          | Pauli-Z gate          |
| `qml.Hadamard`      | `h`       | 0          | Hadamard gate         |
| `qml.S`             | `s`       | 0          | S (phase) gate        |
| `qml.T`             | `t`       | 0          | T gate                |
| `qml.SX`            | `sx`      | 0          | Square root of X gate |
| `qml.Identity`      | `id`      | 0          | Identity gate         |

### Parameterized Single-Qubit Gates

| PennyLane Operation | QASM Gate | Parameters | Description            |
|---------------------|-----------|------------|------------------------|
| `qml.RX`            | `rx`      | 1 (angle)  | Rotation around X axis |
| `qml.RY`            | `ry`      | 1 (angle)  | Rotation around Y axis |
| `qml.RZ`            | `rz`      | 1 (angle)  | Rotation around Z axis |
| `qml.PhaseShift`    | `p`       | 1 (angle)  | Phase shift gate       |

### Two-Qubit Gates

| PennyLane Operation | QASM Gate | Parameters | Description         |
|---------------------|-----------|------------|---------------------|
| `qml.CNOT`          | `cx`      | 0          | Controlled-NOT gate |
| `qml.CZ`            | `cz`      | 0          | Controlled-Z gate   |
| `qml.SWAP`          | `swap`    | 0          | SWAP gate           |

### Parameterized Two-Qubit Gates

| PennyLane Operation | QASM Gate | Parameters | Description                  |
|---------------------|-----------|------------|------------------------------|
| `qml.CRX`           | `crx`     | 1 (angle)  | Controlled rotation around X |
| `qml.CRY`           | `cry`     | 1 (angle)  | Controlled rotation around Y |
| `qml.CRZ`           | `crz`     | 1 (angle)  | Controlled rotation around Z |

### Three-Qubit Gates

| PennyLane Operation | QASM Gate | Parameters | Description                    |
|---------------------|-----------|------------|--------------------------------|
| `qml.Toffoli`       | `ccx`     | 0          | Toffoli (CCNOT) gate           |
| `qml.CSWAP`         | `cswap`   | 0          | Fredkin (controlled-SWAP) gate |

### Differentiable Gates

The following gates support differentiation via the parameter-shift rule, enabling gradient-based optimization on hardware:

`RX`, `RY`, `RZ`, `PhaseShift`, `CRX`, `CRY`, `CRZ`

### Decomposition Behavior

If you use a PennyLane operation that is not in the supported set (e.g., `qml.Rot`, `qml.U3`), PennyLane will automatically decompose it into supported gates before sending it to the device. This decomposition is transparent -- you do not need to handle it manually.

## Observables

The following observables are supported for expectation value and variance measurements:

| Observable | Description |
|----|----|
| `qml.PauliX` | Pauli-X observable |
| `qml.PauliY` | Pauli-Y observable |
| `qml.PauliZ` | Pauli-Z observable |
| `qml.Identity` | Identity observable |
| `qml.Hadamard` | Hadamard observable |
| `qml.Hermitian` | Arbitrary Hermitian matrix observable |
| `qml.prod()` | Tensor product of observables (e.g., `qml.PauliZ(0) @ qml.PauliZ(1)`) |
| `qml.sum()` | Sum of observables |
| `qml.s_prod()` | Scalar product of an observable |
| `qml.Hamiltonian` | Linear combination of observables (Hamiltonian) |
| `qml.LinearCombination` | Linear combination of observables |

## Measurements

All measurements require finite shots (`shots > 0`).

| Measurement | PennyLane Function | Description |
|----|----|----|
| **Counts** | `qml.counts()` | Raw bitstring counts dictionary |
| **Sample** | `qml.sample()` | Individual measurement samples |
| **Expectation** | `qml.expval(obs)` | Expectation value of an observable |
| **Variance** | `qml.var(obs)` | Variance of an observable |
| **Probability** | `qml.probs(wires=...)` | Marginal probabilities for specified wires |

### Measurement Examples

``` python
import pennylane as qml

dev = qml.device("openquantum.device", wires=2, shots=128, backend="rigetti:cepheus-1-108q")

@qml.qnode(dev)
def circuit_counts():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.counts()
# Returns: {'00': 512, '11': 512}

@qml.qnode(dev)
def circuit_expval():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))
# Returns: 0.0 (approximately)

@qml.qnode(dev)
def circuit_probs():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])
# Returns: [0.5, 0.0, 0.0, 0.5] (approximately)

@qml.qnode(dev)
def circuit_multi():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0)), qml.probs(wires=[0, 1])
# Returns: (0.0, [0.5, 0.0, 0.0, 0.5]) (approximately)
```

## Unsupported Features

The following features are **not supported** by the Open Quantum device:

| Feature | Reason |
|----|----|
| Analytic mode (`shots=None`) | Open Quantum is a shot-based execution platform |
| State vector access (`qml.state()`) | Hardware backends do not expose full state vectors |
| Mid-circuit measurements | Not supported by the current QASM serialization pipeline |
| Dynamic qubit management | Fixed qubit allocation at device creation |
| `qjit` compilation | Not compatible with remote execution backends |

## Related Pages

- [Device Options](https://docs.openquantum.com/pennylane-plugin/device-options/) -- Configuration parameters.
- [Basic Circuits](https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/) -- Code examples using these operations.
- [VQE Example](https://docs.openquantum.com/pennylane-plugin/examples/vqe/) -- Using differentiable gates for variational algorithms.
