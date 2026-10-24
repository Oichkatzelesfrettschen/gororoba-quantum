> Full piece: [https://docs.qbraid.com/v2/qir/user-guide/qasm3-qir.md](https://docs.qbraid.com/v2/qir/user-guide/qasm3-qir.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 21f29c3124c863f0706268ea344db14225f3af047f22e3c8dc03ecae3d7ce83b.

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

# OpenQASM 3 conversions

<CodeGroup>
```python Code
from qbraid_qir.qasm3 import qasm3_to_qir

program = """
OPENQASM 3;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""

module = qasm3_to_qir(program, name="bell")

ir = str(module)

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
declare void @__quantum__qis__mz__body(%Qubit*, %Result*) #1

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="2" "required_num_results"="2" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}
!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
````

</CodeGroup>

Execute the QIR program using the qir-runner command line tool:

```bash
$ qir-runner -f bell.bc
```

## Currently Supported Constructs

The `qbraid_qir.qasm3.qasm3_to_qir()` converter supports the following OpenQASM 3 constructs:

### 1. [Register Declarations](https://openqasm.com/language/types.html#quantum-types)

OpenQASM declarations of all forms `qreg`, `qubit`, `bit`, and `creg` are supported.

```qasm
OPENQASM 3;

// qubit declaration
qubit q1;
qubit[2] q2;
qreg q3[3];
qubit[1] q4;

// bit declaration
bit c1;
bit[2] c2;
creg c3[3];
bit[1] c4;
```

### 2. [Quantum Measurements](https://openqasm.com/language/insts.html#measurement)

OpenQASM measurements are supported which involve single qubit measurement and full register measurements.
Range based measurements are not supported currently.

```qasm
OPENQASM 3;

qubit[2] q1;
qubit[5] q2;
qubit q3;

bit[2] c1;
bit c2;

// supported
c1 = measure q1;
measure q1 -> c1;
c2[0] = measure q3[0];

//ERROR: not supported
c1[0:2] = measure q1[0:2];
```

### 3. [Quantum Reset](https://openqasm.com/language/insts.html#initialization)

Resets are supported on declared quantum registers in all forms.

```qasm
OPENQASM 3;

include "stdgates.inc";

// qubit declarations
qubit q1;
qubit[2] q2;
qreg q3[3];

// reset operations
reset q1;
reset q2[1];
reset q3[2];
reset q3[:2];
```

### 4. Quantum Gates

- `pyqir._native` gates are supported along with support for `U3` and U2 gates. The `U[x]` gates are defined in terms of existing `rx` and `rz` gates according to the decomposition present on the [Qiskit UGate documentation](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.UGate) and [PhaseGate documentation](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.PhaseGate).
- Full set of the openqasm3 ["stdgates.inc" gates](https://openqasm.com/language/standard_library.html) are supported. These gates are decomposed with the help of the `pyqir._native` gate set and subsequently converted to QIR.

### 5. [Quantum Barriers](https://openqasm.com/language/delays.html#barrier-instruction)

Barriers are supported only if they are placed on ALL the qubits in the circuit. For example:

```qasm
qubit q[2];

U(0.1, 0.2, 0.3) q[0];

// Barrier on all qubits
barrier q;

// ERROR: Barrier on a subset of qubits
barrier q[0];
```

### 6. [Custom Quantum Gates](https://openqasm.com/language/gates.html#defining-gates)

Gates defined by users are supported as long as they are defined in terms of `pyqir._native` gate set. Identifier mapping in gate parameter expressions is not supported at the moment. Example:

```qasm
OPENQASM 3.0;
include "stdgates.inc";

// Supported
gate custom2(g) s {
  h s;
  rz(g) s;
}

// Supported
gate custom(a,b,c) p, q {
  custom2(a) q;
  h p;
  cx p,q;
  rx(a) q;
  ry(0.5/0.1) q;
}

qubit[2] q;
custom(2 + 3 - 1/5, 0.1, 0.3) q[0], q[1];
```

### 7. [Simple Branching Statements](https://openqasm.com/language/classical.html#if-else-statements)

Since QIR supports branching on a measurement result, **single bit branching** statements are supported at the moment. General boolean expressions and support for branching on full registers will be added in future. For example:

```qasm
OPENQASM 3;
include "stdgates.inc";
qubit[4] q;
bit[4] c;
h q;
measure q -> c;

// supported
if (c[0]) {
    x q[0];
    cx q[0], q[1];
}

if (c[1] == 1) {
    cx q[1], q[2];
}

if (!c[2]) {
    h q[2];
}

// ERROR: not supported
if (c == 8) {
    x q[0];
}
// ERROR: not supported
int[4] element;
if (element > 5) {
    y q[1];
}
```

### 8. [Expressions](https://openqasm.com/language/classical.html#low-level-classical-instructions)

- General expression evaluation involving literals and constants is supported.
- Expressions involving constants and variables are fully supported.
- Expressions with arrays are also supported (in global scopes).

<CodeGroup>
```qasm expression with literals
OPENQASM 3;
qubit q;

// supported
rx(1.57) q;
rz(3-2*3) q;
rz(3-2*3\*(8/2)) q;
rx(-1.57) q;
rx(4%2) q;

````

```qasm expression with scalar variables
OPENQASM 3;

// scalar value assignment and declaration
int[32] a = 5;
float[32] b;
b = 3.14;

// constant value assignment and declaration
const int[32] c_int = 5;
const float[32] c_float = 3.141592;

// arbitary expressions
int[32] x = a + 5*c_int;
````

```qasm expression with arrays
OPENQASM 3;

// static initialization
array[int[32], 3, 2] arr_int = { {1, 2}, {3, 4}, {5, 6} };
array[float[32], 3, 2] arr_float32 = { {1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0} };

// assignment of individual elements
int a = 2;
arr_int[1][1] = a; // arr_int = { {1, 2}, {3, 2}, {5, 6} }

// array elements in expressions
float[32] b = arr_float32[1][1] * 3.1415; // b = 4.0*3.1415 = 12.566

qubit q;
rx(b) q; // rx(12.566) is applied on qubit q
```

</CodeGroup>

### 9. [Variables and Types](https://openqasm.com/language/types.html)

- Scalar types `int`, `uint`, `float`, `bool` and `bit` with arbitrary sizes are supported.
- `array` type is supported for `int`, `uint`, `float`, `bool` and `bit`.
- `complex` and `angle` types are not supported yet.

<CodeGroup>
```qasm scalar variables
OPENQASM 3;
// declarations
int a;
uint b;
int[2] c = 1;
uint[13] d = 2;
float[32] my_pi = 3.14;

// assignments and expressions
a = 5 \* c;
b = 6 - d;

````

```qasm array variables
OPENQASM 3;
// declarations
array[int[32], 3, 2] arr_int = { {1, 2}, {3, 4}, {5, 6} };
array[float[32], 3, 2] arr_float32;

// element assignment
float[32] c = 4.5;
arr_float32[1][1] = c; // arr_float32 = { {None, None}, {None, 4.5}, {None, None} }
arr_int[1][1] = 5; // arr_int = { {1, 2}, {3, 5}, {5, 6} }

// expressions
float[32] d = arr_float32[1][1] * 3.1415; // d = 4.5*3.1415 = 14.13775
````

</CodeGroup>

### 10. [Loops](https://openqasm.com/language/classical.html#for-loops)

Both `for` and `while` loops are supported at the moment. For example:

<CodeGroup>
```qasm simple for loop
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
int[32] i;
for int[32] i in [0:2] {
h q[i];
}

````

```qasm complex for loop
OPENQASM 3.0;
include "stdgates.inc";

qubit[4] q;
bit[4] c;

int j = 0;

h q;
for int i in [0:2]{
    cx q[i], q[i+1];
    h q[j];
    j += 1;
}
h q[j];
measure q -> c;
````

```qasm simple while loop
OPENQASM 3.0;
include "stdgates.inc";

qubit[4] q;
int i = 0;
while (i < 3) {
    h q[i];
    cx q[i], q[i+1];
    i += 1;
}
```

```qasm combined loops
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
int i = 0;
while (i < 2) {
    for int j in {0, 1} {
        h q[j];
    }
    i += 1;
}
```

</CodeGroup>

### 11. [**Aliasing**](https://openqasm.com/language/types.html#aliasing)

- Aliasing quantum registers is supported and can be used to refer to the same quantum register with different names.
- Aliases are currently supported in global scope of the qasm3 program, with support for function scopes coming soon.

<CodeGroup>
```qasm simple aliasing
OPENQASM 3.0;
include "stdgates.inc";

qubit[5] q;

let myqreg0 = q;
let myqreg1 = q[1];
let myqreg2 = q[1:];
let myqreg3 = q[:4];
let myqreg4 = q[1:4];
let myqreg5 = q[1:2:4];
let myqreg6 = q[{0, 1}];

x myqreg0[0];
h myqreg1;
cx myqreg2[0], myqreg2[1];
cx myqreg3[2], myqreg3[3];
ccx myqreg4;
swap myqreg5[0], myqreg5[1];
cz myqreg6;

````

```qasm aliasing in scope
OPENQASM 3;
include "stdgates.inc";
qubit[4] q;
bit[4] c;

h q;
measure q -> c;
if (c[0]) {
    let alias = q[0:2];
    x alias[0];
    cx alias[0], alias[1];
}

if (c[1] == 1) {
    cx q[1], q[2];
}

if (!c[2]) {
    h q[2];
}
````

</CodeGroup>
### 12. [Subroutines](https://openqasm.com/language/subroutines.html)

We support QASM3 subroutines in the QIR converter

<AccordionGroup>

<Accordion title = "Definitions">
Subroutines are supported in QASM3 and can be defined using the `def` keyword and are only allowed in the global scope.

    <CodeGroup>
        ```qasm simple definition
        OPENQASM 3;
        include "stdgates.inc";
        def my_function(qubit q) { // void function
            h q;
            return;
        }
        ```

        ```qasm definition with return type
        OPENQASM 3;
        include "stdgates.inc";
        def my_function(qubit q) -> int[32] {
            h q;
            return 1;
        }
        ```
    </CodeGroup>

</Accordion>

<Accordion title = "Calling subroutines">
Subroutines can be called from within the main program or from other subroutines.

    <CodeGroup>
        ```qasm simple call
        OPENQASM 3.0;
        include "stdgates.inc";

        def my_function(qubit a, float[32] b) {
            rx(b) a;
            float[64] c = 2*b;
            rx(c) a;
            return;
        }
        qubit q;
        bit c;
        float[32] r = 3.14;
        my_function(q, r);
        ```

        ```qasm call in expression
        OPENQASM 3;
        include "stdgates.inc";

        def my_function(qubit q) -> bool{
            h q;
            return true;
        }
        qubit q;
        bool b = my_function(q);
        ```

        ```qasm call from another subroutine
        OPENQASM 3;
        include "stdgates.inc";

        def my_function(qubit q) {
            h q;
            return;
        }

        def my_function_2(qubit[2] q) {
            my_function(q[1]);
            return;
        }
        qubit[2] q;
        my_function_2(q);

        ```

    </CodeGroup>

</Accordion>

<Accordion title = "Arguments and Return Types">
- Quantum arguments of type `qubit` are supported in subroutines.
- Classical arguments are supported for any scalar type and can return values of any scalar type.
- All argument validations mentioned in the OpenQASM3 specification are supported.

    <CodeGroup>
        ```qasm mixed arguments
        OPENQASM 3;
        include "stdgates.inc";

        def my_function(qubit q, int[32] a, float[32] b) {
            rz(a) q;
            rx(b) q;
            return;
        }
        qubit q;
        int[32] n = 5;
        float[32] b = 3.14;
        my_function(q, n, b);

        ```

        ```qasm simple return type
        OPENQASM 3;
        include "stdgates.inc";

        def my_function(qubit q) -> bool {
            h q;
            return true;
        }
        qubit q;
        bool b = my_function(q);
        ```

        ```qasm testing return values
        OPENQASM 3;
        include "stdgates.inc";

        def my_function(qubit q) -> float[32] {
            h q;
            return 3.14;
        }
        def my_function_2(qubit q, float[32] r) {
            rx(r) q;
            return;
        }
        qubit[2] q;
        float[32] r1 = my_function(q[0]);
        my_function_2(q[0], r1);

        array[float[32], 1, 1] r2 = {{3.14}};
        my_function_2(q[1], r2[0,0]);
        ```

    </CodeGroup>

</Accordion>

<Accordion title="Future Work ">
  - Add `mutable` and `readonly` arrays as classical arguments in a subroutines
  - Support looping statements inside a subroutine - Support switch statements
  inside a subroutine - Support for aliasing in a subroutine
</Accordion>

</AccordionGroup>

### 13. [Switch](https://openqasm.com/language/classical.html#the-switch-statement)

Switch statements in QASM3 are supported in the QIR converter. These are defined according to the OpenQASM3 spec
and support all the features mentioned in the specification.

<CodeGroup>
    ```qasm simple switch
    OPENQASM 3.0;
    include "stdgates.inc";
    
    const int i = 4;
    const int j = 4;
    qubit q;

    switch(i) {
        case 6, j {
            x q;
        }
        default {
            z q;
        }
    }
    ```

    ```qasm nested switch
    OPENQASM 3.0;
    include "stdgates.inc";

    const int i = 1;
    qubit q;

    switch(i) {
        case 1,3,5,7 {
            int j = 4; // definition inside scope
            switch(j) {
                case 1,3,5,7 {
                    x q;
                }
                case 2,4,6,8 {
                    y q; // this will be executed
                }
                default {
                    z q;
                }
            }
        }
        case 2,4,6,8 {
            y q;
        }
        default {
            z q;
        }
    }
    ```

</CodeGroup>
