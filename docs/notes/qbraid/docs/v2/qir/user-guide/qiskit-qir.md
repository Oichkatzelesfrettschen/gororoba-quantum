> Full piece: [https://docs.qbraid.com/v2/qir/user-guide/qiskit-qir.md](https://docs.qbraid.com/v2/qir/user-guide/qiskit-qir.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 2d87547aa3bfd32a6f4fad47271ef56ae8a71e109df8a3d05cfa011c5a55d3dc.

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

# Qiskit conversions

## Installation

Install the `qiskit` extra:

```shell
pip install 'qbraid-qir[qiskit]'
```

Requires Qiskit >= 2.0.

## Example Usage

Convert a Qiskit `QuantumCircuit` to QIR:

<CodeGroup>
```python Code
from qiskit import QuantumCircuit
from qbraid_qir import dumps
from qbraid_qir.qiskit import qiskit_to_qir

# create a test circuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# convert to QIR

module = qiskit_to_qir(qc, name="bell")

# saves to .ll and .bc files in working directory

dumps(module)

print(module)

````

```output Output
; ModuleID = 'bell'
source_filename = "bell"

%Qubit = type opaque
%Result = type opaque

define void @main() #0 {
entry:
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cnot__body(%Qubit* inttoptr (i64 0 to %Qubit*), %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mz__body(%Qubit* inttoptr (i64 0 to %Qubit*), %Result* inttoptr (i64 0 to %Result*))
  call void @__quantum__qis__mz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 1 to %Result*))
  ret void
}

declare void @__quantum__qis__h__body(%Qubit*)
declare void @__quantum__qis__cnot__body(%Qubit*, %Qubit*)
declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) #1

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="2" "required_num_results"="2" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}
!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
````

</CodeGroup>

## Transpilation

If your circuit contains gates not directly supported by QIR, you can set `transpile=True` to automatically decompose them into the supported basis gate set before conversion:

```python
module = qiskit_to_qir(qc, name="my-circuit", transpile=True)
```

## Supported Operations

| Category         | Gates                                                     |
| ---------------- | --------------------------------------------------------- |
| **Single-qubit** | `h`, `x`, `y`, `z`, `s`, `sdg`, `t`, `tdg`, `id`, `reset` |
| **Rotations**    | `rx`, `ry`, `rz`                                          |
| **Two-qubit**    | `cx`, `cz`, `swap`                                        |
| **Three-qubit**  | `ccx`                                                     |
| **Measurement**  | `measure`                                                 |
| **Other**        | `barrier`, `delay`                                        |
