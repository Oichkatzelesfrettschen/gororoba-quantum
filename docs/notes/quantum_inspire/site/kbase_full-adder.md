> Full piece: [https://www.quantum-inspire.com/kbase/full-adder/](https://www.quantum-inspire.com/kbase/full-adder/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 f3fa233f7e3a78e8070c0adebc231bcc1f2ca7b9e58da3f5a2a388cd04fe14cc.

# Code example: Quantum full adder

## Backends

*This example is written for the [emulator backend](https://www.quantum-inspire.com/kbase/emulator-backends). [Spin-2](https://www.quantum-inspire.com/kbase/full-adder/kbase/spin-2-operational-specifics/) has only two qubits and does not support this example. The [Starmon-7](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics) backend can be used to execute this example.*

## What is the quantum full adder

Just like in classical electronics, where you can make [different types of binary adders like half adders, full adders, ripple carry adders etcetera](https://nl.wikipedia.org/wiki/Adder_(elektronica)), you can make adders in quantum circuits as well. In this example we will show how a quantum full adder is created and how this adder acts on [superposition states](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/).

The full adder adds to input bits A and B plus a Carry_input bit and produces the Sum and Carry_output bits as output. In classical control electronics the full adder has therefore three inputs and four outputs.

Since quantum circuits are reversible, they have an equal amount of input and output qubits, therefore we define a 4-qubit function, where the input qubits are A,B, CarryIn and (zero) and the output qubits are A,B, Sum and CarryOut, see the figure below.

![](https://www.datocms-assets.com/119587/1545062930-full-adder.png)

One possible implementation of a 2-bit full adder, using three CNOT gates and two Toffoli gates is the following, was originally proposed by Richard Feynman: Richard P. Feynman, Optics News 11, 11 (1985). The final CNOT between qubits A and B is only used to restore B after it was used as a temporary ancilla. The picture is courtesey from [Omnissiahs Hierophant](https://commons.wikimedia.org/wiki/File:Quantum_Full_Adder.png).

![](https://www.datocms-assets.com/119587/1746712884-quantum_full_adder.png)

For completeness we show the truth table for the full adder:

Inputs: q0 = A ; q1 = B ; q2= CarryIn

Outputs: q0 = A ; q1 = B ; q2= SumOut ; q3 = CarryOut

| .   | q3  | q2  | q1  | q0  | .   | q3  | q2  | q1  | q0  |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| .   | .   | Ci  | B   | A   | .   | Co  | S   | B   | A   |
| .   | .   | .   | .   | .   | .   | .   | .   | .   | .   |
| T1  | 0   | 0   | 0   | 0   | \-  | 0   | 0   | 0   | 0   |
| T2  | 0   | 1   | 0   | 0   | \-  | 0   | 1   | 0   | 0   |
| T3  | 0   | 0   | 1   | 0   | \-  | 0   | 1   | 1   | 0   |
| T4  | 0   | 1   | 1   | 0   | \-  | 1   | 0   | 1   | 0   |
| T5  | 0   | 0   | 0   | 1   | \-  | 0   | 1   | 0   | 1   |
| T6  | 0   | 1   | 0   | 1   | \-  | 1   | 0   | 0   | 1   |
| T7  | 0   | 0   | 1   | 1   | \-  | 1   | 0   | 1   | 1   |
| T8  | 0   | 1   | 1   | 1   | \-  | 1   | 1   | 1   | 1   |

## How does it work

The code below shows what happens when we use the quantum full adder to add three qubit states. You can copy and paste this code in your own editor and see what happens when you change the input states A, B and CarryIn to either $`\left\lvert 0 \right\rangle`$ or $`\left\lvert 1 \right\rangle`$ using the X-gate in the initialization function. In this example we set A = 1, B = 0 and CarryIn = 1, equal to T6 in the truth table.

## Examination of the code and results

When we execute the code, setting the number of shots to 1, we get the histogram as shown below the code, which is equal to the expected output (compare to T6 in the truth table). Note: [one shot is enough to determine the probability distribution](https://www.quantum-inspire.com/kbase/optimization-of-simulations/)

```cqasm
version 3.0

qubit[4] q
bit[4] b

/* 
  qubit definitions
  q[0] --> A 
  q[1] --> B
  q[2] --> CarryIn_SumOut
 q[3] --> CarryOut 
*/

// initialize inputs to some values
// initialize inputs A=1, B=0 and carry_in=1
X q[0, 2]
  
// perform addition
// decomposition of toffoli q[0], q[1], q[3]
H q[3]
CNOT q[1],q[3]
Tdag q[3]
CNOT q[0],q[3]
T q[3]
CNOT q[1],q[3]
Tdag q[3]
CNOT q[0],q[3]
T q[1,3]
CNOT q[0],q[1]
H q[3]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

CNOT    q[0],q[1]

// decomposition of toffoli q[1],q[2],q[3]
H q[3]
CNOT q[2],q[3]
Tdag q[3]
CNOT q[1],q[3]
T q[3]
CNOT q[2],q[3]
Tdag q[3]
CNOT q[1],q[3]
T q[2:3]
CNOT q[1],q[2]
H q[3]
T q[1]
Tdag q[2]
CNOT q[1],q[2]

CNOT    q[1],q[2]
CNOT    q[0],q[1]

b[0:3] = measure q[0:3]
```

1.000

1001

1.0

0.8

0.6

0.4

0.2

0.0

We can also use superposition states and entangled states, such as in the following code where we set A and B to a [Bell state](https://www.quantum-inspire.com/kbase/bell-states/) and CarryIn to a superposition state. This is similar to setting the input to states T1, T2, T7 and T8 at the same time.

Comparing again the truth table to the histogram of probability amplitudes, we indeed see that all 4 output states that we would expect are generated.

0.250

0000

0.250

0100

0.250

1011

0.250

1111

1.0

0.8

0.6

0.4

0.2

0.0

Note that there are multiple implementations possible for a quantum full adder. A nice implementation from Figgat (2018) requiring only seven two-qubit gates, of which some could be done in parallel, is the following:

```cqasm
version 3.0

qubit[4] q
bit[4] b

/* 
  qubit definitions
  q[0] --> A 
  q[1] --> B
  q[2] --> CarryIn_SumOut
 q[3] --> CarryOut 
*/

/* 
This example is from Figgat 2018 - Parallel Entangling Operations on a Universal Ion Trap Quantum Computer (2018)
*/

//un-comment next lines to initialize inputs to some values
//X q[0]
//X q[1]
//X q[2]

// perform addition
ctrl.X90 q[1],q[3]
ctrl.X   q[0],q[1]
ctrl.X90 q[2],q[3]
ctrl.X90 q[0],q[3]
ctrl.X   q[1],q[2]
ctrl.mX90 q[2],q[3]
ctrl.X   q[0],q[1]

b[0:3] = measure q[0:3]
```

## Want to know more?

In this example we showed how to create a simple quantum full adder. In the literature you can find other examples to add qubit states, subtract qubit states and execute more complex operations on qubit states.

[Previous](https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/) [Next](https://www.quantum-inspire.com/kbase/grover-algorithm/)
