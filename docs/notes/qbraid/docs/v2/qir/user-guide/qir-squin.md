> Full piece: [https://docs.qbraid.com/v2/qir/user-guide/qir-squin.md](https://docs.qbraid.com/v2/qir/user-guide/qir-squin.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ed0c923630922be897bf407e8ca58931df5566422c1668de2d4926b04ef2fa55.

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

# Squin conversions

This module enables conversion from Quantum Intermediate Representation ([PyQIR](https://github.com/qir-alliance/pyqir)) to Squin kernels, allowing you to execute QIR circuits using the [Bloqade](https://github.com/QuEraComputing/bloqade) SDK's Squin execution engine. [Squin](https://bloqade.quera.com/dev/digital/dialects_and_kernels/squin/) provides a high-performance quantum circuit execution environment, and this conversion opens the door to running QIR circuits on Bloqade simulators and hardware backends.

## Installation

```shell
pip install 'qbraid-qir[squin]'
```

## Conversions

This section highlights the different ways in which the converter `load()` can be used with various formats and input types. Each conversion method is demonstrated with practical examples below.

### PyQIR String to Squin kernel

Convert PyQIR `IR string` to a Squin kernel:

<CodeGroup>

{/* prettier-ignore-start */}
```python Code
from qbraid_qir.squin import load

qir_str = """
; ModuleID = 'bell'
source_filename = "bell"

%Qubit = type opaque

define void @main() #0 {
entry:
  call void @__quantum__qis__h__body(%Qubit* null)
  call void @__quantum__qis__cnot__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*))
  ret void
}

declare void @__quantum__qis__h__body(%Qubit*)

declare void @__quantum__qis__cnot__body(%Qubit*, %Qubit*)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="2" "required_num_results"="2" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
"""

squin_kernel = load(qir_str, kernel_name="bell")
squin_kernel.print()

````
{/* prettier-ignore-end */}

```output Output
func.func @bell() -> !py.NoneType {
  ^0(%bell_self):
  │ %0 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %1 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %2 = func.invoke h(%0) : !py.NoneType maybe_pure=False
  │ %3 = func.invoke cx(%0, %1) : !py.NoneType maybe_pure=False
  │ %4 = func.const.none() : !py.NoneType
  │      func.return %4
} // func.func bell
```

</CodeGroup>

### PyQIR Module to Squin kernel

Convert a PyQIR `Module` object to a Squin kernel:

<CodeGroup>

{/* prettier-ignore-start */}
```python Code
from qbraid_qir.squin import load
from pyqir import BasicQisBuilder, SimpleModule

mod = SimpleModule("ghz", num_qubits=3, num_results=3)
qis = BasicQisBuilder(mod.builder)

qis.h(mod.qubits[0])
qis.cx(mod.qubits[0], mod.qubits[1])
qis.cx(mod.qubits[1], mod.qubits[2])

squin_kernel = load(mod._module)
squin_kernel.print()

````
{/* prettier-ignore-end */}

```output Output
func.func @main() -> !py.NoneType {
  ^0(%main_self):
  │ %0 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %1 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %2 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %3 = func.invoke h(%0) : !py.NoneType maybe_pure=False
  │ %4 = func.invoke cx(%0, %1) : !py.NoneType maybe_pure=False
  │ %5 = func.invoke cx(%1, %2) : !py.NoneType maybe_pure=False
  │ %6 = func.const.none() : !py.NoneType
  │      func.return %6
} // func.func main
```

</CodeGroup>

### Conversion from File

Load PyQIR IR from a `file` (`.ll` for LLVM IR text or `.bc` for LLVM bitcode):

```python Code
from qbraid_qir.squin import load

# Load from .ll file (LLVM IR text)
kernel = load("path/to/circuit.ll", kernel_name="my_circuit")

# Load from .bc file (LLVM bitcode)
kernel = load("path/to/circuit.bc", kernel_name="my_circuit")
```

### Integration with OpenQASM 3

Convert `OpenQASM3` programs to Squin kernels using `qbraid-qir`:

<CodeGroup>
```python Code
from qbraid_qir.qasm3 import qasm3_to_qir
from qbraid_qir.squin import load

program = """
OPENQASM 3;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
x q[0], q[1];
rx(pi/2) q[0];
"""

module = qasm3_to_qir(program, name="my_program")

squin_kernel = load(str(module))

squin_kernel.print()

````

```output Output
func.func @main() -> !py.NoneType {
  ^0(%main_self):
  │ %0 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %1 = func.invoke new() : !py.Qubit maybe_pure=False
  │ %2 = func.invoke h(%0) : !py.NoneType maybe_pure=False
  │ %3 = func.invoke x(%0) : !py.NoneType maybe_pure=False
  │ %4 = func.invoke x(%1) : !py.NoneType maybe_pure=False
  │ %5 = py.constant.constant 1.5707963267948966 : !py.float
  │ %6 = func.invoke rx(%5, %0) : !py.NoneType maybe_pure=False
  │ %7 = func.const.none() : !py.NoneType
  │      func.return %7
} // func.func main
````

</CodeGroup>

### Integration with CUDA-Q

Convert `CUDA-Q` kernels to Squin kernels

```python Code
import cudaq
from qbraid_qir.squin import load

@cudaq.kernel
def bell():
    q = cudaq.qvector(2)
    h(q[0])
    cx(q[0], q[1])

# Generate QIR from kernel
qir_str = cudaq.translate(bell, format="qir-base")

squin_kernel = load(qir_str, kernel_name="bell")
squin_kernel.print()
```

<Note>
  **CUDA-Q** is capable of exporting QIR using multiple profiles (such
  as`qir-base, qir-adaptive,` etc.). Currently, the qbraid-qir Squin integration
  supports only QIR generated with the **qir-base** profile. Ensure that when
  using **cudaq.translate**, you specify **format="qir-base"** for
  compatibility.
</Note>

### Using Qubit Register as Argument

Create a kernel that accepts a qubit register as an argument, enabling composition of kernel functions:

<CodeGroup>

{/* prettier-ignore-start */}
```python Code
from qbraid_qir.squin import load
from pyqir import BasicQisBuilder, SimpleModule

mod = SimpleModule("main", num_qubits=3, num_results=3)
qis = BasicQisBuilder(mod.builder)
qis.h(mod.qubits[0])
qis.cx(mod.qubits[0], mod.qubits[1])

squin_kernel = load(
module=mod._module,
kernel_name="bell",
register_as_argument=True,
register_argument_name="qreg"
)
squin_kernel.print()

````
{/* prettier-ignore-end */}

```output Output
func.func @bell(qreg : !py.IList[!py.Qubit, Literal(2,int)]) -> !py.NoneType {
  ^0(%bell_self, %qreg):
  │ %0 = py.constant.constant 0 : !py.int
  │ %1 = py.indexing.getitem(%qreg : !py.IList[!py.Qubit, Literal(2,int)], %0) : !py.Qubit
  │ %2 = py.constant.constant 1 : !py.int
  │ %3 = py.indexing.getitem(%qreg : !py.IList[!py.Qubit, Literal(2,int)], %2) : !py.Qubit
  │ %4 = func.invoke h(%1) : !py.NoneType maybe_pure=False
  │ %5 = func.invoke cx(%1, %3) : !py.NoneType maybe_pure=False
  │ %6 = func.const.none() : !py.NoneType
  │      func.return %6
} // func.func bell
```

</CodeGroup>

## Supported Gates

The following gates are currently supported for conversion from PyQIR to Squin kernels:

| QIR Gate                     | Squin Gate    | Description            |
| ---------------------------- | ------------- | ---------------------- |
| `__quantum__qis__h__body`    | `squin.h`     | Hadamard gate          |
| `__quantum__qis__x__body`    | `squin.x`     | Pauli-X gate           |
| `__quantum__qis__y__body`    | `squin.y`     | Pauli-Y gate           |
| `__quantum__qis__z__body`    | `squin.z`     | Pauli-Z gate           |
| `__quantum__qis__s__body`    | `squin.s`     | S gate (π/2 phase)     |
| `__quantum__qis__t__body`    | `squin.t`     | T gate (π/4 phase)     |
| `__quantum__qis__s__adj`     | `squin.s_adj` | S† gate (adjoint S)    |
| `__quantum__qis__t__adj`     | `squin.t_adj` | T† gate (adjoint T)    |
| `__quantum__qis__rx__body`   | `squin.rx`    | Rotation around X-axis |
| `__quantum__qis__ry__body`   | `squin.ry`    | Rotation around Y-axis |
| `__quantum__qis__rz__body`   | `squin.rz`    | Rotation around Z-axis |
| `__quantum__qis__cnot__body` | `squin.cx`    | Controlled-NOT gate    |
| `__quantum__qis__cz__body`   | `squin.cz`    | Controlled-Z gate      |

## Next Steps

Our current implementation provides comprehensive support for standard QIR gates and circuit conversion. We are actively working on expanding functionality in the following areas:

- **Measurement operations**: Support for measurement operations is planned for a future release.
- **Classical control flow**: Conditional gates and classical control flow are on our roadmap.
- **Custom gates**: We currently support all standard QIR gates listed in the [Supported Gates](#supported-gates) table, with plans to extend support for custom gate definitions.
