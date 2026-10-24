> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/advanced-features.md](https://docs.qbraid.com/v2/pyqasm/user-guide/advanced-features.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 12f1ba9523309b5bde88efb89358712b994b26efaaf2cf84971cac62b7302d33.

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

# Advanced Features

## Branch Optimization

We optimize the conditional branching statements using the following techniques:

1. **Branch Elimination**: We evaluate the outcome of the branch condition, if it is known at compile time
   and does not contain measurement results of qubits. We remove the branch statement
   and if it evaluates to a true value, attach the corresponding block of code to the main program.

<CodeGroup>
```python Elimination
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
bit[1] c;
int[32] a = 0;
if(a > 0){
h q[0];
}
if(a < 0){
x q[0];
}
if(a == 0){
y q[0];
measure q -> c;
}
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
bit[1] c;
y q[0];
c[0] = measure q[0];
````

</CodeGroup>

2. **Branch Unfolding**: If the branch condition contains measurement results of qubits, we unfold the classical
   registers into individual bits and insert equivalent conditional statements for each bit. This method
   is particularly useful for systems which do not support multi-bit classical registers in conditional
   statements.

<CodeGroup>
```python Unfolding
import pyqasm

qasm_code = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
bit[4] c;
if(c == 3){
h q[0];
}
if(c >= 3){
h q[0];
} else {
x q[0];
}
if(c <= 3){
h q[0];
} else {
x q[0];
}
if(c < 4){
h q[0];
} else {
x q[0];
}
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
bit[4] c;
if (c[0] == false) {
  if (c[1] == false) {
    if (c[2] == true) {
      if (c[3] == true) {
        h q[0];
      }
    }
  }
}
if (c[2] == true) {
  if (c[3] == true) {
    h q[0];
  } else {
    x q[0];
  }
} else {
  x q[0];
}
if (c[0] == false) {
  if (c[1] == false) {
    h q[0];
  } else {
    x q[0];
  }
} else {
  x q[0];
}
if (c[0] == false) {
  if (c[1] == false) {
    h q[0];
  } else {
    x q[0];
  }
} else {
  x q[0];
}
````

</CodeGroup>

## Switch Case Optimization

The openqasm reference enforces the switch targets to be of type int and the cases to be unique integer
literals or constant integer expressions. This implies that the switch case statements can be optimized
at compile time as long as the target variable is not dependent on a measurement result.

Once the target variable is evaluated at compile time, the `switch` statement is removed and the
corresponding `switch` case code block is attached to the main program.

<CodeGroup>
```python Switch Case
import pyqasm

qasm_code = """
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
                j = 5; // assignment inside scope
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

"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
y q[0];
````

</CodeGroup>

## Subroutine Inlining

Subroutine inlining is the process of replacing a subroutine call with the actual code of the subroutine.
Since quantum devices do not support subroutines, it is essential to inline the subroutine code against
the call to the subroutine. Here, the formal parameters of the subroutine are replaced with the actual
parameters used in the subroutine call. Moreover, the subroutine code is inserted at the location of the
subroutine call with careful consideration of the scope of the variables used in the subroutine.

<CodeGroup>
```python Inlining
import pyqasm

qasm_code = """OPENQASM 3.0;
include "stdgates.inc";

    gate my_gate(a) q2 {
        rx(a) q2;
    }

    def my_function(qubit a, float[32] b) {
        float[64] c = 2*b;
        my_gate(b) a;
        my_gate(c) a;
        return;
    }
    qubit q;
    float[32] r = 3.14;
    my_function(q, r);

"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
rx(3.14) q[0];
rx(6.28) q[0];
````

</CodeGroup>

## Loop Unrolling

Loop unrolling is the process of unfolding a loop with a list of equivalent instructions.
This is particularly important for quantum programs as quantum computers do not support direct execution
of loops. We provide support for unrolling `while` and `for` loops -

1. **`while` Loop**
   - We evaluate the loop conditions at _compile time_ and visit the loop body
     till the condition becomes false.

<CodeGroup>
```python Unroll while
import pyqasm

qasm_code = """
OPENQASM 3.0;
qubit[4] q;
int i = 0;
while (i < 3) {
h q[i];
cx q[i], q[i+1];
i += 1;
}

"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
qubit[4] q;
h q[0];
cx q[0], q[1];
h q[1];
cx q[1], q[2];
h q[2];
cx q[2], q[3];
````

</CodeGroup>
    - To ensure that the unrolling process does not go into an infinite
    loop, we have introduced a `max_loop_iters` parameter. It has a default value of `1e9` and allows
    the user to control the max number of loop iterations -
<CodeGroup>
```python Max Loop Iterations
import pyqasm

qasm_code = """
OPENQASM 3.0;
qubit[100] q;
int i = 0;
while (i < 50) {
h q[i];
cx q[i], q[i+1];
i += 1;
}

"""
module = pyqasm.loads(qasm_code)

# set max loop iterations to 10

module.unroll(max_loop_iters=10)

print(pyqasm.dumps(module))

````

```qasm Output
ERROR:pyqasm: Error at line 5, column 0 in QASM file

 >>>>>> while (i < 50) {
    h q[i];
    cx q[i], q[i + 1];
    i += 1;
}

...

LoopLimitExceededError: Loop exceeded max allowed iterations
````

</CodeGroup>
    - This unrolling process is not applicable in a case when the `while` condition is _dependent on a
    quantum measurement result_. Since the truth value of the condition can only be known at runtime,
    an exception is raised while unrolling such loops -

<CodeGroup>
```python Unroll while
import pyqasm

qasm_code = """
OPENQASM 3.0;
qubit q;
bit c;
c = measure q;
while (c) {
h q;
c = measure q;
}

"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
ERROR:pyqasm: Error at line 6, column 4 in QASM file

 >>>>>> while (c) {
    h q;
    c = measure q;
}

....

ValidationError: Cannot unroll while-loop with condition depending on quantum measurement
result.
````

</CodeGroup>
    Unrolling `while` loops which contain quantum measurements is, in fact, an active area of development.
    Some researchers have proposed to identify such loops and convert them into a [native `while` 
    loop instructions which can be executed during runtime](https://github.com/qBraid/pyqasm/pull/199#issuecomment-2922055327). However, this approach has not been 
    fully implemented yet.

2.  **`for` Loop**
    - The process is similar to the `while` loop unrolling process, but the loop counter is
      chosen from the range provided by the user. The loop body is executed as many times as
      the range value -

<CodeGroup>
```python Unroll for
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[4] q;
bit[4] c;

h q;
for int i in [0:2]{
cx q[i], q[i+1];
}
c = measure q;
"""
module = pyqasm.loads(qasm_code)
module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
bit[4] c;
h q[0];
h q[1];
h q[2];
h q[3];
cx q[0], q[1];
cx q[1], q[2];
cx q[2], q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];

````

</CodeGroup>

## Qubit Register Consolidation

This feature enables the transformation of multiple named qubit registers into a single unified register named `__PYQASM_QUBITS__`. This simplifies register management and prepares the circuit for hardware-specific or simulator-specific backends that expect a flat register structure.

**Usage**

```python
qc = pyqasm.loads(qasm_file)
qc.unroll(consolidate_qubits = True)
```

**Key Features:**

- If `device_qubits` is provided while loading the QASM file, enforces a qubit limit and validates register size.

  ```python
  pyqasm.loads(qasm_file, device_qubits = 10)
  ```

- If not provided, the unified register size equals the total number of qubits across all original registers.
- Updates all qubit references in the code to align with the new unified register.

**Examples:**

<Tabs>
  <Tab title="Consolidation">
<CodeGroup>

```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
qubit[2] q1;
qubit[3] q2;
cx q1[0], q2[2];
"""
module = pyqasm.loads(qasm_code)
module.unroll(consolidate_qubits=True)

print(pyqasm.dumps(module))
```

```qasm output
OPENQASM 3.0;
qubit[5] __PYQASM_QUBITS__;
cx __PYQASM_QUBITS__[0], __PYQASM_QUBITS__[4];
```

</CodeGroup>
</Tab>
<Tab title="Consolidation with device_qubits">
<CodeGroup>
```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
qubit[2] q1;
qubit[2] q2;
cx q1[1], q2[0];
"""
module = pyqasm.loads(qasm_code, device_qubits = 5)
module.unroll(consolidate_qubits=True)

print(pyqasm.dumps(module))

````

```qasm output
OPENQASM 3.0;
qubit[5] __PYQASM_QUBITS__;
cx __PYQASM_QUBITS__[1], __PYQASM_QUBITS__[2];

````

</CodeGroup>
</Tab>
</Tabs>

## Circuit Timing Operations

In OpenQASM 3, circuit execution is not only determined by gate order but also by explicit timing primitives that define time and duration of operations. PyQASM now supports the following timing operations:

**Operations:**

- **duration** - A typed literal or variable representing an explicit length of time, expressed in units such as `ns`, `us`, `ms`, or hardware clock cycles (`dt`).
- **stretch** - A symbolic non-negative duration that is resolved at compile time into a concrete value chosen to satisfy timing constraints.
- **delay** - An identity operation applied to one or more qubits for a given duration, used to pin timing and prevent unintended commutation.
- **box** - A timing context that groups statements together with an enforced total duration, ensuring well-defined scheduling boundaries.
- **angle** - A fixed-width representation of phase values, useful for encoding rotations and phase shifts in hardware-specific bitstring formats.
- **extern** - User or backend defined functions that can be declared in QASM and validated in PyQASM for tasks such as cycle alignment or calibration.
- **complex** - Support for complex literals and standard functions (`abs`, `real`, `imag`, `sin`, `cos`, etc.) to describe calibrated amplitudes, phases, or control laws.

**Example:**

<CodeGroup>

```python QASM-Code
import pyqasm
qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

// Duration examples
duration t1 = 100ns;
const duration t2 = 50us;
const duration t3 = 200dt;

// Stretch examples
const stretch s1 = 75ns;
const stretch s2 = t2 + t3;

// Delay examples
qubit[2] q;
delay[t1] q[0];
delay[s1] q[1];
delay[25ns] q[0], q[1];

// Box examples
box[150ns] {
    delay[50ns] q[0];
    h q[1];
    delay[50ns] q[0];
    cx q[0], q[1];
    delay[50ns] q[1];
}

box[t1] {
    delay[25ns] q[0];
    x q[1];
    delay[25ns] q[0];
    y q[1];
    delay[50ns] q[0], q[1];
}

// Angle examples
angle[8] ang1 = pi/2;
angle[4] ang2 = "1010";
const angle[8] ang3 = 3*pi/4;

// Extern examples
extern calibrate(angle, duration) -> complex;
extern measure_fidelity(int, complex) -> float[64];

complex[float[64]] result;
float[64] fidelity;

result = calibrate(ang1, t1);
fidelity = measure_fidelity(2, 1.0 + 2.0im);

// Complex examples
complex c1 = 1.0 + 2.0im;
complex c2 = -3.5 - 1.5im;
complex[float[64]] c3 = 2.5 + 3.7im;

complex c4 = c1 + c2;
complex c5 = c1 * c2;
float mag = abs(c1);
complex c6 = sqrt(c1);
"""
module = pyqasm.loads(qasm_code)
module.validate()

print(pyqasm.dumps(module))
```

```qasm output
OPENQASM 3.0;
include "stdgates.inc";
duration t1 = 100.0ns;
const duration t2 = 50.0us;
const duration t3 = 200.0dt;
const stretch s1 = 75.0ns;
const stretch s2 = t2 + t3;
qubit[2] q;
delay[100.0ns] q[0];
delay[75.0ns] q[1];
delay[25.0ns] q[0], q[1];
box[150.0ns] {
  delay[50.0ns] q[0];
  h q[1];
  delay[50.0ns] q[0];
  cx q[0], q[1];
  delay[50.0ns] q[1];
}
box[100.0ns] {
  delay[25.0ns] q[0];
  x q[1];
  delay[25.0ns] q[0];
  y q[1];
  delay[50.0ns] q[0], q[1];
}
angle[8] ang1 = pi / 2;
angle[4] ang2 = "1010";
const angle[8] ang3 = 3 * pi / 4;
extern calibrate(angle, duration) -> complex;
extern measure_fidelity(int, complex) -> float[64];
complex[float[64]] result;
float[64] fidelity;
result = calibrate(1.5707963267948966, 100.0ns);
fidelity = measure_fidelity(2, 1.0 + 2.0im);
complex c1 = 1.0 + 2.0im;
complex c2 = -3.5 - 1.5im;
complex[float[64]] c3 = 2.5 + 3.7im;
complex c4 = -2.5 + 0.5im;
complex c5 = -0.5 - 8.5im;
float mag = 2.23606797749979;
complex c6 = 1.272019649514069 + 0.7861513777574233im;
```

</CodeGroup>
