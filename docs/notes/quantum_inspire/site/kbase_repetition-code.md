> Full piece: [https://www.quantum-inspire.com/kbase/repetition-code/](https://www.quantum-inspire.com/kbase/repetition-code/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 9a4dfaa51610a73f7463ce904dd20ec4d06e0c9d21120608d8ae08405971a37e.

# Code example: Repetition code

## Backends

*This example is written for the [emulator backend](https://www.quantum-inspire.com/kbase/emulator-backends).*

## What is quantum error correction?

Whenever you do calculations on your computer, there is a small chance that errors will be introduced, resulting for instance in one of the memory bits changing from 1 to 0. Various methods exist to deal with these errors and allow for robust classical computing, such as using parity bits or using repetition codes.

Quantum computing is also not perfect. Due to decoherence, leakage, control errors, material imperfections etc. quantum states will never be in perfect alignment with the intended state. Classical error correction does not work for quantum computing. One reason for this is the [no-cloning theorem](https://en.wikipedia.org/wiki/No-cloning_theorem) stating that quantum states cannot be perfectly cloned. However, there exist various methods to perform error correction on quantum states, such as repetition codes and stabilizer codes.

In this example we will give a simple example of quantum error correction, where we encode one logical qubit using three physical qubits. Note that the proposed encoding is not sufficient to correct *all* single qubit errors: this specific example only allows for correction of so-called single bit-flip errors.

In this example we make use of [binary controlled gates](https://www.quantum-inspire.com/kbase/cqasm-binary-controlled-gates/) which can be simulated with our [QX emulator](https://www.quantum-inspire.com/kbase/emulator-backends/) backend.

## How does it work

Repetition is one of the easiest ways to prevent and correct errors. Instead of using a physical qubit $`\vert\psi\rangle = \alpha \vert 0\rangle + \beta\vert 1\rangle`$, we encode a logical qubit using three physical qubits as $`\vert\psi\rangle = \alpha \vert 000\rangle + \beta\vert 111\rangle`$. Using two extra ancilla bits, single bit-flip errors can now be detected and corrected.

## Examination of the code and results

The first stage of our repetition code is to encode a single qubit into our logical qubit. Using two CNOT-operations, encoding to a logical qubit is done from an arbitrary state $`q[0] = \vert\psi\rangle`$, where $`q[1] = q[2] = \vert 0\rangle`$. The circuit diagram for this encoding step is:

### Error detection

Error-detection is done using the two ancilla qubits. Two `CNOT` operations are coupled with the first ancilla qubit, which is subsequently measured, giving the parity of the first two qubits. If we measure 1, we know that in either the first or the second qubit an error occurred. Similarly, two `CNOT` operations are coupled with the second ancilla qubit and the first and third qubit. Measuring the second ancilla qubit gives the parity between the first and third qubit. If we measure 1, we now know that in either the first or third qubit an error occurred.

### Error correction

Combining measurement results from the ancilla qubits, we can determine in which qubit, if any, an error occurred. The combined result of the two parity measurements is called the error-syndrome. Let $`b_i`$ be the measurement result of ancilla qubit $`i=1,2`$. If a single bit-flip occurred in one of the qubits, then at least one of $`b_i`$ is non-zero and the error occurred in qubit $`2\cdot(1-b_1) + (1-b_2)`$. Suppose for example a measurement of the ancillas gives 1 for the first and 0 for the second ancilla qubit, then we know that an error occurred in qubit $`q[1]`$. The error can be corrected by applying a binary controlled X-gate on the qubit.

Above, we assumed that only a single error occurred. In case two errors occurred, we are still able to run the error correcting circuit, however, the wrong bit will be corrected. If all bits are flipped, we are not able to detect an error, and in fact, we wrongfully assume no error occurred. With an error-probability smaller than 0.5, it is more likely that at most a single error occurred, than that two or more errors occurred.

In the figure below, we show the entire quantum bit-flip correction circuit, where we manually apply an error on qubit 1.

```cqasm
version 3.0

qubit[5] q
bit[5] b

/* Encoding */
CNOT q[0], q[1]
CNOT q[0], q[2]
    
/* Introduce error */
X q[1]

/* Error detection */
CNOT q[0], q[3]
CNOT q[1], q[3]
CNOT q[0], q[4]
CNOT q[2], q[4]
b[3, 4] = measure q[3, 4]

/* Error correction */
/* Not yet supported in cQASM v3
Both b[3]=b[4]=0
do nothing

b[3]=b[4]=1
c-x b[3,4], q[0]

b[3]=1,b[4]=0
not b[4]
c-x b[3,4], q[1]
not b[4]

b[3]=0,b[4]=1
not b[3]
c-x b[3,4], q[2]
b[3]
*/

/* Measurement */
b[0:2] = measure q[0:2]
```

When not applying error correction, measurement of the first three qubits will give $`010`$, while applying error correction will result in $`000`$, with the ancilla qubits being $`q[3]=1`$ and $`q[4]=0`$.

When the code above is executed on the Quantum Inspire platform, the resulting histogram will look like this, showing that the bit-flip has indeed been corrected:

1.000

01000

1.0

0.8

0.6

0.4

0.2

0.0

### Probabilistic error introduction

Instead of manually introducing errors, we can also use ancilla qubits to introduce errors with some probability.

By rotating three ancilla qubits around the $`x`$-axis with angle \theta, we obtain for each ancilla the state $`\cos(\theta /2) \lvert 0 \rangle - i \sin(\theta /2) \lvert 1 \rangle`$. By measuring and introducing a bit-flip if the measurement result is $`1`$, we see that we introduce an error on each of the three qubits $`q[0],q[1],q[2]`$ with probability $`\sin(\theta /2) ^{2}`$. Errors are now introduced using binary controlled rotations.

Let's run the repetition code using a single qubit error probability of 5% (an angle of 0.45 for the Rx-gate corresponds to an error probability of 5%). The circuit implementation looks like this:

```cqasm
version 3.0

qubit[8] q
bit[8] b

/* Encoding */
CNOT q[0], q[1]
CNOT q[0], q[2]
    
/* Introduce error */
Rx(0.45) q[5:7]
b[5:7] = measure q[5:7]
/* Not yet supported in cQASM v3
c-x b[5], q[0]
c-x b[6], q[1]
c-x b[7], q[2]
*/

/* Error detection */
CNOT q[0], q[3]
CNOT q[1], q[3]
CNOT q[0], q[4]
CNOT q[2], q[4]
b[3, 4] = measure q[3, 4]
// prep_z q[3,4]

/* Error correction */
/* Not yet supported in cQASM v3
Both b[3]=b[4]=0
do nothing

b[3]=b[4]=1
c-x b[3,4], q[0]

b[3]=1,b[4]=0
not b[4]
c-x b[3,4], q[1]
not b[4]

b[3]=0,b[4]=1
not b[3]
c-x b[3,4], q[2]
not b[3]
*/

/* Measurement */
b[0:2] = measure q[0:2]
```

Because this code contains measurement-based operations, this simulation [cannot be optimized](https://www.quantum-inspire.com/kbase/optimization-of-simulations/). The runtime of the simulation therefore scales with the number of shots. Below we show the simulation results for 128 shots.

When we examine the output of the circuit, we have to keep in mind that the 3 least significant bit values denote the state of the digital register of the data qubits at the end of the code, the next two bits show the state of the digital register of the two ancilla qubits and the 3 most significant bits that of our *error-control qubits*.

We see that in 87% of the cases, no error was introduced at all (an no correction was needed). In ~11% of the cases (2.3% + 2.3% + 6.3%) a single qubit error was introduced (and corrected), but in 1.6% (0.8% + 0.8%) of the cases two-single errors were introduced (and not corrected).

0.875

00000000

0.023

00111000

0.023

01001000

0.008

01110111

0.063

10010000

0.008

11011111

1.0

0.8

0.6

0.4

0.2

0.0

We could also try and see what happens when we increase the error probability to 30%, by setting the rotation angle on the three error introducing qubits to 1.16. In this case more situations will occur with two or three simultaneous errors which cannot be corrected by the repetition code, as shown in the histogram below. In this case no error was introduced in 33.6% of the shots. A single error was introduced in 43.7% of the shots (and corrected) and two or three simultaneous errors were introduced in the remainder of the shots (and not corrected).

0.336

00000000

0.156

00111000

0.156

01001000

0.063

01110111

0.125

10010000

0.102

10101111

0.055

11011111

0.008

11100111

1.0

0.8

0.6

0.4

0.2

0.0

## Want to know more?

Note that this is a simple circuit where only a single error is manually introduced and henceforward corrected. In practice, systems will be more complex and errors can occur at any point in the circuit, including in the error correction part. Furthermore, in reality the errors that occur are more complex than just bit-flip errors. For more information on quantum error correction and repetition codes, we refer to <https://en.wikipedia.org/wiki/Quantum_error_correction> and specialized literature on this topic.

[Previous](https://www.quantum-inspire.com/kbase/grover-algorithm/) [Next](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-transmons/)
