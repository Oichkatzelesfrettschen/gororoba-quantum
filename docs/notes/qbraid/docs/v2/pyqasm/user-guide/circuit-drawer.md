> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/circuit-drawer.md](https://docs.qbraid.com/v2/pyqasm/user-guide/circuit-drawer.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 da98396555914263a2344f4231b3b846962380a024332cebe7223ebbf6072732.

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

# Circuit Drawer

To use the circuit drawer tool, install the `visualization` extra:

```shell
pip install 'pyqasm[visualization]'
```

Draw a quantum circuit directly from any OpenQASM string:

```python
from pyqasm import draw

qasm = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

h q[0];
z q[1];
rz(pi/1.1) q[0];
cx q[0], q[1];
swap q[0], q[1];
ccx q[0], q[1], q[2];
b = measure q;
"""

draw(qasm, output='mpl')
```

<div style={{ display: "flex", justifyContent: "left", alignItems: "left" }}>
  <img src="/v2/pyqasm/_static/pyqasm_circuit.png" width="150%" />
</div>

<Note>Currently, only the `mpl` (matplotlib) output format is supported.</Note>

## Input Formats

All draw methods accepts either a `str` (QASM source) or a [pyqasm.QasmModule](https://sdk.qbraid.com/pyqasm/stubs/pyqasm.QasmModule.html#pyqasm.QasmModule) object. The following are equivalent:

```python
from pyqasm import loads, draw
from pyqasm.printer import mpl_draw

module = loads(qasm_str)

draw(module, output='mpl')
draw(qasm_str, output='mpl')

mpl_draw(module)
mpl_draw(qasm_str)
```

## Exclude Idle Wires

Use the `idle_wires=False` option to exclude idle qubits (i.e. wires with no circuit elements) in the output circuit diagram:

```python
from pyqasm import draw

qasm = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[2] b;

h q[0];
h q[1];
cx q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
"""

draw(qasm, idle_wires=False, output='mpl')
```

<div style={{ display: "flex", justifyContent: "left", alignItems: "left" }}>
  <img src="/v2/pyqasm/_static/pyqasm_idle_wires_false.png" width="150%" />
</div>

## Save Diagram

Save the circuit diagram to a file by specifying `output='mpl'` and a `filename`:

```python
draw(qasm, output='mpl', filename='/path/to/circuit.png')
```
