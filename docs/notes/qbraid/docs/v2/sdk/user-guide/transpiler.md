> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/transpiler.md](https://docs.qbraid.com/v2/sdk/user-guide/transpiler.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ebdd7bb437711fd5dc414b93d742c569cbac027b5e6ec785d7dc2faa527daf6b.

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

# Transpiler

> Graph-based approach to quantum program type conversions.

The qBraid-SDK transpiler allows converting quantum programs from one type to another, for any two program types for which
a "conversion path" exists. Registered program types are interconnected via a directed graph, where each program type is
represented as a node and supported conversions as edges. The breadth, depth, and connectivity of this `ConversionGraph`
can be customized by the user.

<Info>
  API Reference:
  [qbraid.transpiler](https://qbraid.github.io/qBraid/api/qbraid.transpiler.html)
</Info>

## Conversion Graph

To view what conversions are available, you can plot the `ConversionGraph`:

```python
from qbraid import ConversionGraph

graph = ConversionGraph()

len(graph.nodes()) # 10
len(graph.edges()) # 25

graph.plot(legend=True)
```

<img align="middle" width="511px" src="/v2/sdk/_static/conversion_graph.png" />

Gray arrows denote conversions implemented and managed by qBraid. Red arrows represent conversions implemented
by external packages or extensions. These are automatically incorporated into the conversion graph upon
installing the specified 'extra'.

You can use the native conversions supported by qBraid, or define your own custom nodes and/or edges. For example:

```python
from unittest.mock import Mock

from qbraid import register_program_type, Conversion

# replace with any program type
register_program_type(Mock, alias="mock")

# replace with your custom conversion function
example_qasm3_to_mock_func = lambda x: x

conversion = Conversion("qasm3", "mock", example_qasm3_to_mock_func)

graph.add_conversion(conversion)

# using a seed is helpful to ensure reproducibility
graph.plot(seed=20, k=3, legend=True)
```

<img
  align="middle"
  width="511px"
  src="/v2/sdk/_static/new_conversion_graph.png"
/>

Blue arrows indicate conversions added by the user during their current session.

Check if a conversion is supported between two given program types, and if so, what "conversion path(s)" would be used:

```python
graph.has_path("qiskit", "braket")  # True

for p in graph.all_paths("qiskit", "braket"): print(p)
# qiskit -> braket
# qiskit -> qasm3 -> braket
# qiskit -> qasm2 -> qasm3 -> braket
# qiskit -> qasm2 -> pytket -> braket
# qiskit -> qasm2 -> cirq -> braket

graph.shortest_path("qiskit", "braket")  # qiskit -> braket
```

Scope the conversions available to the transpiler by specifying your own `conversions` list:

```python
from qbraid import ConversionGraph, Conversion
from qbraid.transpiler.conversions.qiskit import qiskit_to_braket

conv = Conversion("qiskit", "braket", qiskit_to_braket)
graph = ConversionGraph(conversions=[conv])

graph.all_paths("qiskit", "braket")
# ["qiskit -> qasm3 -> braket"]
```

## Conversion Scheme

The `ConversionScheme` data class details information about conversion configurations, such as numbers of nodes and edges, as well as max depth.

```python
from qbraid import ConversionGraph, ConversionScheme

scheme = ConversionScheme(max_path_attempts=3, max_path_depth=None)

custom_graph = ConversionGraph(...)
scheme.update_scheme(conversion_graph=custom_graph)

scheme.to_dict()
```

## Transpile

Using the `qbraid.transpile` function, simply pass in the name of the target package from one of `qbraid.QPROGRAM_ALIASES`. For example, use input `"cirq"` to return a `cirq.Circuit`:

```python
from qiskit import QuantumCircuit

def bell():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0,1)
    return circuit

qiskit_circuit = bell()
```

<CodeGroup>

```python Input
from qbraid import transpile

cirq_circuit = transpile(qiskit_circuit, "cirq")

print(cirq_circuit)
```

```text Output
q_0: ───H───@───
            │
q_1: ───────X───
```

</CodeGroup>

This time, using the same origin circuit, we'll input `"pyquil"` to return a `pyquil.quil.Program`:

<CodeGroup>

```python Input
pyquil_program = transpile(qiskit_circuit, "pyquil")

print(pyquil_program)
```

```text Output
H 0
CNOT 0 1
```

</CodeGroup>

<Info>
  See also:
  <a
    href="https://github.com/qBraid/qbraid-lab-demo/blob/main/qBraid-SDK/qbraid_sdk_transpiler.ipynb"
    target="_blank"
  >
    - Transpiler Demo Notebook: General Usage
  </a>
</Info>
