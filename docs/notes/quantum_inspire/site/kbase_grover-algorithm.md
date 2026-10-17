> Full piece: [https://www.quantum-inspire.com/kbase/grover-algorithm/](https://www.quantum-inspire.com/kbase/grover-algorithm/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 9f816d7316be73ced874b25abec6b326a75383d7b4f2f5d18c2653fe0e7fc9c0.

# Code example: Grover's algorithm

## Backends

*This example is written for the [emulator backend](https://www.quantum-inspire.com/kbase/emulator-backends). [Spin-2](https://www.quantum-inspire.com/kbase/grover-algorithm/kbase/spin-2-operational-specifics/) has only two qubits and does not support this example. The [starmon-7](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics) backend can be used to execute this example, however, since it does not support the Toffoli gate, the code needs to be rewritten into two-qubit and single-qubit operations.*

## What does it do?

In mathematical terms, Grover's algorithm [L. K. Grover, Phys. Rev. Lett. **79**, 325-328 (1997)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.79.325) solves the problem of an unstructured search. It is a quantum algorithm for finding the input value $`x_0`$ of an Oracle function $`f(x)`$ with $`f(x_0)=1`$ and $`f(x) = 0`$ for all other values of $`x`$. The strength of the algorithm is that when the Oracle function has $`N`$ possible input values, the algorithm only requires $`\mathcal{O}(\sqrt{N})`$ evaluations of the Oracle, while the best classical algorithm needs $`\mathcal{O}(N)`$ evaluations.

## What is the use?

An example of such a problem is finding a specific card in a shuffled deck of N cards. Classically this can only be done by searching the deck of cards one by one, in which case you will need $`N`$ steps (i.e. $`N`$ evaluations of the Oracle representing the inspection of cards). Grover's algorithm requires only $`\mathcal{O}(\sqrt{N})`$ evaluations of the Oracle. The caveat however is that the probability of finding the right answer is not 100%, as will become clearer from the steps in the algorithm. Other examples where Grover's algorithm or similar methods are used are for instance minimization problems.

![](https://www.datocms-assets.com/119587/1534853524-deck-of-cards.jpg)

## How does it work?

First, we have to define input states. Without loss of generality we will assume that the input states are integers between 0 and $`2^n`$ where $`n`$ is an integer. The $`2^n`$ integer states will be encoded by the states $`\vert 0 \rangle`$ and $`\vert 1 \rangle`$ of $`n`$ qubits.

Secondly, we have to define an Oracle function for our example, i.e. a function that returns 'zero' for all possible input states, except one input state. We require an Oracle function $`f(x)`$ that can be encoded in an operator (series of quantum gates) $`O`$ and that acts as

``` math
O \vert x\rangle = (-1)^{f(x)} \vert x\rangle .
```

This means that the Oracle negates the probability amplitude of the input state $`\vert x\rangle`$ if and only if $`f(x)=1`$.

## Examination of the code

Let's look at a concrete example. Let's say our Oracle is a function that returns a 1 (true) only for an input value of the decimal number 6 and 0 (false) for all other possible inputs between 0 and 7. The decimal number 6 is equal to the value 110 in binary representation. We can now try and see how many Oracle calls are needed to find the input value for which the function returns True.

The algorithm (see code below) consists of the following steps:

1.  Initialization of the qubits in the $`|0\rangle`$ state and creation of a uniform superposition of all basis inputs
2.  Execution of the Oracle
3.  Application of Grover's diffusion operator (inversion about the mean)
4.  Repetitions of step 2 and 3
5.  Final measurement

In this example 2 repetitions will achieve a high probability of success as will be shown below.

The Oracle operator can be defined in our case by the following circuit. It is not difficult to see that this circuit negates the amplitude probability of the input if and only if the input is 110.

```cqasm
version 3.0

qubit[3] q
bit[3] b

// Grover's algorithm for searching the decimal number 6 in a database of size 2^3

H q[2, 1, 0]

/* Oracle, first run */
X q[0]
H q[2]

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

H q[2]
X q[0]
```

The Oracle function is followed by Grover's diffusion operator (also called amplitude purification) which calculates the mean probability amplitude $`\mu`$ of all states and inverts the probability amplitudes around this mean. This actually amplifies the probability amplitude of the target state. Repeated steps of calling the Oracle and the diffusion operator amplifies the probability amplitude further. Combining all elements, we arrive at the following algorithm, where the sub circuit called Grover, consists of the Oracle followed by the diffusion operator and is called twice:

```cqasm
version 3.0

qubit[3] q
bit[3] b

// Grover's algorithm for searching the decimal number 6 in a database of size 2^3

H q[2, 1, 0]

/* Oracle, first run */
X q[0]
H q[2]

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

H q[2]
X q[0]

/* Diffusion operator */
H q[0, 1, 2]
X q[0, 1, 2]
H q[2]

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

H q[2]
X q[1, 0, 2]
H q[0, 1, 2]

/* Oracle, second run */
X q[0]
H q[2]

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

H q[2]
X q[0]

/* Diffusion operator */
H q[0, 1, 2]
X q[0, 1, 2]
H q[2]

// decomposition of toffoli q[0], q[1], q[2]
H q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[2]
CNOT q[1],q[2]
Tdag q[2]
CNOT q[0],q[2]
T q[1:2]
CNOT q[0],q[1]
H q[2]
T q[0]
Tdag q[1]
CNOT q[0],q[1]

H q[2]
X q[1, 0, 2]
H q[0, 1, 2]

b[0, 1, 2] = measure q[0, 1, 2]
```

## Examination of the results

Various resources on the web provide a detailed explanation of Grover's algorithm. To understand just a bit of what is happening let's look at the code, but first start with only one iteration. You can try this yourself by creating a new project, copying the code above to the editor and by changing the number of iterations to 1 in line 8.

When we execute this code, with one iteration only, on the QX single Node emulator (1024 shots) we get the following result (or something quite similar, due to the inherent probabilistic behavior of the code). You may have to scroll to the right to get a clear view on the full histogram. Remember that the input value we were looking for has value 110 (binary representation of the decimal number 6).

The histogram shows that even after 1 iteration there is a reasonable amount of success of finding this value, in this case around 77%, to find the correct entry.

0.032

000

0.025

001

0.037

010

0.025

011

0.034

100

0.028

101

0.775

110

0.042

111

1.0

0.8

0.6

0.4

0.2

0.0

If we now run the code again with two iterations we get the following result. We see that the probability of success has already increased to 95%! For a database of size $`N=2^n`$ the optimal number of rotations is $`r=\pi \sqrt{N}/4`$. In our case $`N=2^3=8`$, so the optimal number is $`2.22`$, rounded to $`2`$.

0.004

000

0.014

001

0.007

010

0.007

011

0.007

100

0.005

101

0.949

110

0.008

111

1.0

0.8

0.6

0.4

0.2

0.0

For three iterations, the success probability will decrease again. You can try this yourself by modifying the number of iterations to 3.

Note that the number of iterations in Grover's algorithm is critical. If you make too many iterations the probability of success decreases again.

## Want to know more?

To learn more about oracles and Grover's algorithm check out [Grover's algorithm on QuTube](https://www.qutube.nl/quantum-algorithms/grovers-algorithm-124).

You can also visit [Grover's algorithm on Wikipedia](https://en.wikipedia.org/wiki/Grover%27s_algorithm) and [this in-depth lecture by David Deutsch](http://www.quiprocone.org/Protected/Lecture_6.htm). Or check out this [quantiki page](https://www.quantiki.org/wiki/grovers-search-algorithm) or [this site](http://davidbkemp.github.io/animated-qubits/grover.html).

[Previous](https://www.quantum-inspire.com/kbase/full-adder/) [Next](https://www.quantum-inspire.com/kbase/repetition-code/)
