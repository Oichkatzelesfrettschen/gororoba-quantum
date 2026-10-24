> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/programs.md](https://docs.qbraid.com/v2/sdk/user-guide/programs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 4e4f9af38df06c5cc95682c0e9714a682e3928d8f1dd6f1f35089e34bfb95812.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# Programs

> Extract and manage metadata from supported quantum program types, with the flexibility to introduce new types.

In this module, you will learn how to use the qBraid-SDK to interface with quantum circuits across various frontends.
We will demonstrate how to load quantum programs, register new quantum program types, and highlight a few other circuit-level
convenience features.

<Info>
  API Reference:
  [qbraid.programs](https://qbraid.github.io/qBraid/api/qbraid.programs.html)
</Info>

## Quantum Program Registry

The `QPROGRAM_REGISTRY` contains dictionary mappings of shorthand identifiers for "registered" quantum program types.
By default (i.e. without any optional dependencies installed) this simply includes three variations of OpenQASM programs:

```python
>>> from qbraid import QPROGRAM_REGISTRY
>>> QPROGRAM_REGISTRY
{'openqasm3': openqasm3.ast.Program,
 'qasm2': str,
 'qasm3': str}
```

In this example, 'openqasm3' serves as a type alias for an `openqasm3.ast.Program` object, while 'qasm2' and 'qasm3' are aliases
for raw OpenQASM 2 and OpenQASM 3 strings, respectively.

For each of its 10 natively supported program type aliases, the qBraid-SDK will automatically detect whether the corresponding library is installed,
and add that program type along with its type alias to the `QPROGRAM_REGISTRY`. For example, after installing the following optional dependencies,

```bash
pip install cirq-core qiskit amazon-braket-sdk pennylane pyquil pytket pyqir
```

the `QPROGRAM_REGISTRY` is automatically updated:

```python
>>> from qbraid import QPROGRAM_REGISTRY
>>> QPROGRAM_REGISTRY
{'cirq': cirq.circuits.circuit.Circuit,
 'qiskit': qiskit.circuit.quantumcircuit.QuantumCircuit,
 'pennylane': pennylane.tape.tape.QuantumTape,
 'pyquil': pyquil.quil.Program,
 'pytket': pytket._tket.circuit.Circuit,
 'braket': braket.circuits.circuit.Circuit,
 'openqasm3': openqasm3.ast.Program,
 'pyqir': Module,
 'qasm2': str,
 'qasm3': str}
```

This arrangement simplifies the process of targeting and transpiling between various quantum programming frameworks,
which will be discussed in detail in the transpiler, interface, and runtime tutorials.

### Register New Program Types

You can register new quantum program types using either custom or default type aliases, and overwrite
existing type aliases when necessary. For example:

```python
import cirq
import stim

from qbraid import register_program_type

# register new program type with default module alias
register_program_type(stim.Circuit)

# register native program type with custom alias
register_program_type(cirq.Circuit, alias="myalias")

# overwrite existing type alias with new program type
register_program_type(dict, alias="qasm2", overwrite=True)
```

## Load Program

Any quantum program of a natively supported type can be encapsulated within a `qbraid.programs.QbraidProgram`
object. This encapsulation provides a unified framework for circuit manipulation—such as removing idle qubits
and reversing qubit order—and for extracting valuable metadata, including the number of qubits, circuit depth,
and the unitary representation.

As an example, we'll start with a simple qiskit circuit that creates the bell state,
load the quantum circuit object into the qBraid representation, verify the
circuit depth number of qubits, calculate the circuit's unitary representation,
and draw the circuit.

<CodeGroup>

```python Input
from qbraid import load_program
from qbraid.visualization import circuit_drawer

qprogram = load_program(qiskit_circuit)

assert qprogram.num_qubits == 2
assert qprogram.depth == 2
assert qprogram.unitary().shape ==  (4, 4)

circuit_drawer(qprogram.program)
```

```text Output
     ┌───┐
q_0: ┤ H ├──■──
     └───┘┌─┴─┐
q_1: ─────┤ X ├
          └───┘
```

</CodeGroup>

Now, let's try reversing the qubit order, and drawing the circuit again:

<CodeGroup>

```python Input
qprogram.reverse_qubit_order()

circuit_drawer(qprogram.program)
```

```text Ouput
          ┌───┐
q_0: ─────┤ X ├
     ┌───┐└─┬─┘
q_1: ┤ H ├──■──
     └───┘
```

</CodeGroup>

Any quantum program type listed in the `qbraid.NATIVE_REGISTRY` can be loaded and utilized in this manner.
Each `QbraidProgram` object has `num_qubits` and `depth` attributes and `unitary()` method, regardless of the input circuit type.
For example, we could load an Amazon Braket circuit, and repeat similar steps:

<CodeGroup>

```python Input
from qbraid import load_program
from qbraid.visualization import circuit_drawer

qprogram = load_program(braket_circuit)

assert qprogram.unitary().shape == ((1 << qprogram.num_qubits),) * 2

circuit_drawer(qprogram.program)
```

```text Output
T  : │  0  │  1  │  2  │
      ┌───┐
q0 : ─┤ H ├───●─────────
      └───┘   │
            ┌─┴─┐
q2 : ───────┤ X ├───●───
            └───┘   │
                  ┌─┴─┐
q4 : ─────────────┤ X ├─
                  └───┘
T  : │  0  │  1  │  2  │
```

</CodeGroup>

Some wrapped program types support additional methods that can help resolve compatibility issues, such as differences in
qubit indexing rules across frontends. For instance, the `remove_idle_qubits()` method allows you to remap qubit indices
without having to reconstruct the circuit:

<CodeGroup>

```python Input
qprogram.remove_idle_qubits()

circuit_drawer(qprogram.program)
```

```text Output
T  : │  0  │  1  │  2  │
      ┌───┐
q0 : ─┤ H ├───●─────────
      └───┘   │
            ┌─┴─┐
q1 : ───────┤ X ├───●───
            └───┘   │
                  ┌─┴─┐
q2 : ─────────────┤ X ├─
                  └───┘
T  : │  0  │  1  │  2  │
```

</CodeGroup>

Using the `remove_idle_qubits` method, we mapped the qubit indices of the
Amazon Braket circuit from `[0, 2, 4]` to the contiguous `[0, 1, 2]` convention.
