> Full piece: [https://docs.qbraid.com/v2/qir/user-guide/profiles.md](https://docs.qbraid.com/v2/qir/user-guide/profiles.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 19bfb4639c671f6d4607a483e8dac6c35d8849a61abf38fc8aeab794f904990b.

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

# QIR Profiles

QIR (Quantum Intermediate Representation) profiles in `qbraid-qir` define the rules, restrictions,
and capabilities that govern how OpenQASM 3 programs are converted to QIR. When converting a QASM
program to QIR using `qbraid-qir`, you must specify a profile—either **Base** or **Adaptive**—which
determines the allowed quantum operations, branching, measurement handling, and output recording.
This ensures that the generated QIR is compliant with the requirements of the target quantum backend
or workflow.

## Available Profiles

### Base Profile

- **Name:** `Base`
- **Capabilities:**
  - Conditional execution (`if` statements) is supported.
  - Only sequential output recording is supported.
- **Restrictions:**
  - No forward branching (no `goto` or loops).
  - Qubit reuse after measurement is **not** allowed.
  - Measurement tracking is **not** enabled.
  - No grouped output recording.
  - No qubit reuse after measurement.
  - Barriers must cover **all** qubits (no subset barriers).
  - Only a fixed set of gates is supported.

### Adaptive Profile

- **Name:** `AdaptiveExecution`
- **Capabilities:**
  - Conditional execution and forward branching are supported.
  - Qubit reuse after measurement is **allowed**.
  - Measurement tracking is enabled.
  - Grouped output recording is supported (register structure is preserved).
  - Barriers must cover **all** qubits.
  - Supports a broader set of gates and more flexible control flow.
- **Restrictions:**
  - Subset barriers are **not** allowed (barriers must cover all qubits).
  - Only constant parameters for parameterized gates.

## How to Use

When converting QASM to QIR, specify the profile using the `profile` argument:

<CodeGroup>

```python converting qasm to qir
from qbraid_qir.qasm3 import qasm3_to_qir

qasm3_code = """
OPENQASM 3;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
if (c[0]) {
    x q[1];
}
c[1] = measure q[1];
"""

# Convert using the Base profile
qir_base = qasm3_to_qir(qasm3_code, profile="base")
print(qir_base)

# Convert using the Adaptive profile
qir_adaptive = qasm3_to_qir(qasm3_code, profile="adaptive")
print(qir_adaptive)
```

```llvm base profile output
; ModuleID = 'program-b27e5a7a-4b58-11f0-824a-cae339f58535'
source_filename = "program-b27e5a7a-4b58-11f0-824a-cae339f58535"

%Qubit = type opaque
%Result = type opaque

define void @program-b27e5a7a-4b58-11f0-824a-cae339f58535() #0 {
entry:
  call void @__quantum__rt__initialize(i8* null)
  call void @__quantum__qis__h__body(%Qubit* null)
  call void @__quantum__qis__mz__body(%Qubit* null, %Result* null)
  %0 = call i1 @__quantum__qis__read_result__body(%Result* null)
  br i1 %0, label %then, label %else

then:                                             ; preds = %entry
  call void @__quantum__qis__x__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  br label %continue

else:                                             ; preds = %entry
  br label %continue

continue:                                         ; preds = %else, %then
  call void @__quantum__qis__mz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 1 to %Result*))
  call void @__quantum__rt__result_record_output(%Result* null, i8* null)
  call void @__quantum__rt__result_record_output(%Result* inttoptr (i64 1 to %Result*), i8* null)
  ret void
}

declare void @__quantum__rt__initialize(i8*)

declare void @__quantum__qis__h__body(%Qubit*)

declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) #1

declare i1 @__quantum__qis__read_result__body(%Result*)

declare void @__quantum__qis__x__body(%Qubit*)

declare void @__quantum__rt__result_record_output(%Result*, i8*)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="base" "required_num_qubits"="2" "required_num_results"="2" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
```

```llvm adaptive profile output
; ModuleID = 'program-b27f2086-4b58-11f0-824a-cae339f58535'
source_filename = "program-b27f2086-4b58-11f0-824a-cae339f58535"

%Qubit = type opaque
%Result = type opaque

define void @program-b27f2086-4b58-11f0-824a-cae339f58535() #0 {
entry:
  call void @__quantum__rt__initialize(i8* null)
  call void @__quantum__qis__h__body(%Qubit* null)
  call void @__quantum__qis__mz__body(%Qubit* null, %Result* null)
  %0 = call i1 @__quantum__qis__read_result__body(%Result* null)
  br i1 %0, label %then, label %else

then:                                             ; preds = %entry
  call void @__quantum__qis__x__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  br label %continue

else:                                             ; preds = %entry
  br label %continue

continue:                                         ; preds = %else, %then
  call void @__quantum__qis__mz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 1 to %Result*))
  call void @__quantum__rt__array_record_output(i64 2, i8* null)
  call void @__quantum__rt__result_record_output(%Result* inttoptr (i64 1 to %Result*), i8* null)
  call void @__quantum__rt__result_record_output(%Result* null, i8* null)
  ret void
}

declare void @__quantum__rt__initialize(i8*)

declare void @__quantum__qis__h__body(%Qubit*)

declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) #1

declare i1 @__quantum__qis__read_result__body(%Result*)

declare void @__quantum__qis__x__body(%Qubit*)

declare void @__quantum__rt__array_record_output(i64, i8*)

declare void @__quantum__rt__result_record_output(%Result*, i8*)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive" "required_num_qubits"="2" "required_num_results"="2" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
```

</CodeGroup>

The `qir_base` and `qir_adaptive` variables will contain the generated QIR code for the specified profile.

## Example QASM Programs

<Tabs>
<Tab title = 'Base Profile'>

```qasm
OPENQASM 3;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
x q[1];      // Allowed
reset q[0];  // Not allowed in Base profile (qubit reuse forbidden)
```

The last line will cause an error in the Base profile because qubit reuse after measurement is not
permitted

</Tab>

<Tab title = 'Adaptive Profile'>

```qasm
OPENQASM 3;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
reset q[0];  // Allowed in Adaptive profile
x q[0];     // Allowed in Adaptive profile
```

This program is valid in the Adaptive profile, which allows qubit reuse after measurement and reset.

</Tab>

<Tab title = 'Conditional Branching'>

```qasm
OPENQASM 3;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
if (c[0]) {
    x q[1];
}
```

Both profiles support conditional execution, but only the `Adaptive` profile supports more advanced
branching and measurement-based control flow.

</Tab>
</Tabs>

## Conclusion

When converting QASM to QIR with `qbraid-qir`, always choose the profile that **matches your target
backend's requirements** The `Base` profile is strict and suitable for simple, hardware-oriented
workflows, while the `Adaptive` profile enables more advanced quantum programming features such as
qubit reuse, grouped output, and flexible control flow.
