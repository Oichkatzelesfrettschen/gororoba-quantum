> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/interface.md](https://docs.qbraid.com/v2/sdk/user-guide/interface.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 4564f63b74b4a8679a93db6210f5a25fb2d980d9fccf9630f063b2cb6b5782b4.

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

# Interface

> Generate random circuits, unitary matrices, and test circuit equivalence.

<Info>
  API Reference:
  [qbraid.interface](https://qbraid.github.io/qBraid/api/qbraid.interface.html)
</Info>

## Generate random circuits

Generate a random quantum circuit object of any registered program type from
`qbraid.NATIVE_REGISTRY`. For example:

<CodeGroup>

```python Input
from qbraid import random_circuit

circuit = random_circuit("qiskit")  # Swap "cirq", "braket", "qasm3", etc.

print(circuit)
```

```text Sample Output
q_0: ─────────────■──────────────■─
                  │              │
q_1: ─────────────■──────────────X─
     ┌─────────────────────────┐ │
q_2: ┤ U(3.8035,5.0708,2.3633) ├─X─
     └─────────────────────────┘
```

</CodeGroup>

Optionally specify number of qubits, circuit depth, and whether to measure over all qubits.

<CodeGroup>

```python Input
circuit = random_circuit("cirq", num_qubits=2, depth=2, measure=True)

print(circuit)
```

```text Sample Output
q_0: ───×───Rz(1.34π)───────────M('c_0')───
        │
q_1: ───×───U3(0.0, 0.0, 0.0)───M('c_1')───
```

</CodeGroup>

## Generate random unitaries

Generate random unitary matrices of any specified dimension (`dim`):

<CodeGroup>

```python Input
from qbraid.interface import random_unitary_matrix

unitary = random_unitary_matrix(2)

print(unitary)
```

```text Sample Output
[[-0.46060623-0.33349006j -0.82238991+0.01735275j]
 [ 0.48450787-0.66473935j  0.01019327+0.56856822j]]
```

</CodeGroup>

## Check circuit unitary equivalence

Check whether two quantum circuits have equivalent unitary representations, regardless of their types.
All input circuits must be registered in `qbraid.programs.NATIVE_REGISTRY`. Below is an example demonstrating
the comparison between two circuits that each create a Bell state using different quantum programming libraries
(Cirq and Qiskit).

```python
import cirq
import qiskit

from qbraid.interface import circuits_allclose

def cirq_bell():
    circuit = cirq.Circuit()
    q0, q1 = cirq.LineQubit.range(2)
    circuit.append(cirq.H(q0))
    circuit.append(cirq.CNOT(q0, q1))
    return circuit

def qiskit_bell():
    circuit = qiskit.QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0,1)
    return circuit

# Returns True if the unitary matrices of the two circuits are equivalent
print(circuits_allclose(cirq_bell(), qiskit_bell())) # Output: True
```

This function also supports several optional keyword arguments that allow customization of the equivalence checking process:

- `index_contig`: If set to True, maps both circuits to use sequential qubit indexing prior to computing their unitaries. Defaults to False.
- `allow_rev_qubits`: If set to True, allows the function to consider circuits as equivalent even if their qubits are in reversed order. Defaults to False.
- `strict_gphase`: If set to False, ignores differences in global phase between the circuits. Defaults to True.
- `atol`: Sets the absolute tolerance level for the numerical comparison of unitaries, using np.allclose. Defaults to 1e-7.

Here are some examples of how these arguments could be used:

```python
# ignore global phase and use an increased error margin
circuits_allclose(circuit0, circuit1, strict_gphase=False, atol=1e-6)

# allow for non-sequential qubit indexing and reversed qubit order
circuits_allclose(circuit2, circuit3, index_contig=True, allow_rev_qubits=True)
```
