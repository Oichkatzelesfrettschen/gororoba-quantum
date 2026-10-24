> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/examples.md](https://docs.qbraid.com/v2/pyqasm/user-guide/examples.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 af14a7e977b7d14ec4ceb900811657e24cddd5defa490ea362a55c5ceca45bb7.

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

# Usage Examples

## Compilation

### Inlining and Unrolling

This example demonstrates the capabilities of the PyQASM tool by unrolling a complex OpenQASM program into a simplified form.

In PyQASM, “unrolling” refers to the process of simplifying a quantum program by expanding custom gate definitions and flattening
complex language constructs like subroutines, loops, and conditional statements into basic operations. This technique, also known
as **program flattening** or **inlining**, transforms nested and recursive structures into a linear sequence of operations consisting solely
of qubit and classical bit declarations, gate operations, and measurement operations. By converting the program into this simplified
format, it becomes easier to perform subsequent transpilation or compilation steps before executing the program on a quantum device.

```qasm example.qasm
OPENQASM 3.0;
include "stdgates.inc";

// Define custom gates
gate hgate q {
    h q;
}
gate xgate q {
    x q;
}
gate cxgate q1, q2 {
    cx q1, q2;
}

// Define a subroutine for creating a Bell state
def create_bell_state(qubit[2] q) {
    hgate q[0];
    cxgate q[0], q[1];
    return;
}

// Define a subroutine for a generic quantum operation
def generic_operation(qubit[N] q) {
    for int i in [0:N-1] {
        hgate q[i];
        xgate q[i];
        y q[i];
        rx(pi) q[i];
    }
    return;
}

// Main program
const int[32] N = 4;
qubit[N] q;
bit[N] c;

// Create a Bell state using the alias
create_bell_state(q[0:2]);

measure q[0:1] -> c[0:1];

// Perform a generic operation on all qubits
generic_operation(q);

// Classical control flow
if (c[0]) {
    hgate q[0];
} else {
    xgate q[0];
}

// Define an array of angles for parameterized gates
array[float[64], N] angles = {pi/2, pi/4, pi/8, pi/16};

// Apply parameterized rotations
for int i in [0:N-1] {
    rx(angles[i]) q[i];
}

// Measure the qubits
c = measure q;
```

<CodeGroup>

```python example.py
import pyqasm

module = pyqasm.load("example.qasm")

module.validate()
module.unroll()

print(pyqasm.dumps(module))
```

```qasm output
OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
bit[4] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
h q[0];
x q[0];
y q[0];
rx(3.141592653589793) q[0];
h q[1];
x q[1];
y q[1];
rx(3.141592653589793) q[1];
h q[2];
x q[2];
y q[2];
rx(3.141592653589793) q[2];
h q[3];
x q[3];
y q[3];
rx(3.141592653589793) q[3];
if (c[0] == true) {
  h q[0];
} else {
  x q[0];
}
rx(1.5707963267948966) q[0];
rx(0.7853981633974483) q[1];
rx(0.39269908169872414) q[2];
rx(0.19634954084936207) q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
```

</CodeGroup>

For complete details about the supported operations, see [PyQASM Supported Operations](https://github.com/qBraid/pyqasm/blob/main/src/README.md#supported-operations).

## Analysis

### `num_qubits`, `num_clbits`, and `depth`

This example demonstrates how to use the `num_qubits`, `num_clbits`, and `depth` methods.

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Get the number of qubits and classical bits

num_qubits = module.num_qubits
num_clbits = module.num_clbits

# Calculate the depth of the circuit

depth = module.depth()

print(f"Number of qubits: {num_qubits}")
print(f"Number of classical bits: {num_clbits}")
print(f"Depth of the circuit: {depth}")

````

```bash Output
Number of qubits: 3
Number of classical bits: 3
Depth of the circuit: 3
````

</CodeGroup>

## Transformations

### `has_measurements` and `remove_measurements`

This example demonstrates how to check for measurements and remove them.

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Check if the module has measurements

print(f"Has measurements: {module.has_measurements()}")

# Remove measurements

module.remove_measurements()
print("\nModule without measurements: ")
print(pyqasm.dumps(module))

# Check if the module has measurements

print(f"Has measurements: {module.has_measurements()}")

````

```bash Output
Has measurements: True

Module without measurements:
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];

Has measurements: False
````

</CodeGroup>

Very similar to the previous example, we also have `has_barriers` and `remove_barriers` methods
to check for barriers and remove them, respectively.

### `populate_idle_qubits`

This example demonstrates how to populate idle qubits with identity gates -

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
h q[0];
cx q[0], q[1];
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Populate idle qubits with identity gates

module.populate_idle_qubits()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
h q[0];
cx q[0], q[1];
id q[2];
id q[3];
id q[4];
````

</CodeGroup>

### `remove_idle_qubits`

This example demonstrates how to remove idle qubits from the module and shows the qubit count before and after.

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
h q[0];
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Print the number of qubits before removing idle qubits

print(f"Number of qubits before: {module.num_qubits}")

# Remove idle qubits

module.remove_idle_qubits()

# Print the number of qubits after removing idle qubits

print(f"Number of qubits after: {module.num_qubits}")

print(pyqasm.dumps(module))

````

```qasm Output
Number of qubits before: 5
Number of qubits after: 1
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
````

</CodeGroup>

### `reverse_qubit_order`

This example demonstrates how to reverse the order of qubits in the module with a more involved program.

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
h q[0];
cx q[0], q[1];
cx q[1], q[2];
cx q[2], q[3];
cx q[3], q[4];
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Reverse the order of qubits

module.reverse_qubit_order()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
h q[4];
cx q[4], q[3];
cx q[3], q[2];
cx q[2], q[1];
cx q[1], q[0];
````

</CodeGroup>

### `rebase`

Unroll and convert an QASM program to a specified basis gate set.
The target basis set can be chosen from the options present in the `pyqasm.elements.BasisSet` class. Currently we
support conversion to the following basis sets:

1. `BasisSet.CLIFFORD_T` : `{"h", "t", "s", "cx", "tdg", "sdg"}`
2. `BasisSet.ROTATIONAL_CX` : `{"rx", "ry", "rz", "cx"}`

For example -

<CodeGroup>
```python example.py
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
// Operations
h q;
x q;
cz q[0], q[1];
c = measure q;
"""
module = pyqasm.loads(qasm_code)

module.rebase(pyqasm.elements.BasisSet.ROTATIONAL_CX)

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
ry(1.5707963267948966) q[0];
rx(3.141592653589793) q[0];
ry(1.5707963267948966) q[1];
rx(3.141592653589793) q[1];
rx(3.141592653589793) q[0];
rx(3.141592653589793) q[1];
ry(1.5707963267948966) q[1];
rx(3.141592653589793) q[1];
cx q[0], q[1];
ry(1.5707963267948966) q[1];
rx(3.141592653589793) q[1];
c[0] = measure q[0];
c[1] = measure q[1];
````

</CodeGroup>

The `rebase` functionality is useful for converting a program to a basis set that is supported by a specific
quantum device. This conversion can be extended to new custom basis sets by adding the required gate decompositions
to the `pyqasm.maps.decomposition_rules` module.

Currently we have complete conversion support for the `BasisSet.ROTATIONAL_CX` basis set,
whereas only non-parameterized gate conversion is available for `BasisSet.CLIFFORD_T`.

Refer to the [PyQASM API Documentation](https://qbraid.github.io/pyqasm/api/pyqasm.html)
for more details on the available methods and their usage.
