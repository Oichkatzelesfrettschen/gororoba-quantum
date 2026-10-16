> Full piece: [https://www.quantum-inspire.com/kbase/what-is-a-quantum-algorithm/](https://www.quantum-inspire.com/kbase/what-is-a-quantum-algorithm/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 fe8f0a73356c0debba2e5e01cfc2c9383c2620cf48ffd6771c2cb43e0ea49196.

# What is a quantum algorithm?

## Quantum Algorithms

An algorithm is a step-by-step procedure to perform a calculation, or a sequence of instructions to solve a problem, where each step can be performed on a computer. Therefore, an algorithm is a quantum algorithm when it can be performed on a quantum computer. In principle it is possible to run all classical algorithms on a quantum computer. However, the term quantum algorithm is applied to algorithms of which at least one of the steps is distinctly ‘quantum’, using [superposition or entanglement](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/).

[Play![](https://www.quantum-inspire.com/icons/play.svg)](https://youtu.be/V0ssQZBS8-U)

[QTM1x_2018_22-Quantum_Algorithm-video](https://youtu.be/V0ssQZBS8-U)

## Quantum circuits

Quantum algorithms are most commonly described by a quantum circuit, of which a simple example is shown in the figure below. A quantum circuit is a model for quantum computation, where the steps to solve the problem are quantum gates performed on one or more qubits. A quantum gate is an operation applied to a qubit that changes the quantum state of the qubit. Quantum gates can be divided into single-qubit gates and two-qubit gates, depending on the number of qubits on which they are applied at the same time. Three-qubit gates and other multi-qubit gates can also be defined. A quantum circuit is concluded with a measurement on one or more qubits.

```cqasm
version 3.0

// define a quantum register named q with 2 qubits and a bit register named b with 2 bits

qubit[2] q
bit[2] b

H q[0]
CNOT q[0],q[1]
b[0,1] = measure q[0,1]
```

## Reversibility of quantum circuits

A difference with a classical algorithm is that a quantum algorithm is always reversible. This means that if measurements are not a part of the circuit, a reverse traversal of the quantum circuit will undo the operations brought about by a forward traversal of that circuit.

## The power of quantum algorithms

Problems that are fundamentally unsolvable by classical algorithms (so called undecidable problems) cannot be solved by quantum algorithms either. The added value of quantum algorithms is that they can solve some problems significantly faster than classical algorithms. The best-known examples are Shor’s algorithm and [Grover’s algorithm](https://www.quantum-inspire.com/kbase/grover-algorithm/). Shor’s algorithm is a quantum algorithm for integer factorization. Simply put, when given an integer N, it will find its prime factors. It can solve this problem exponentially faster than the best-known classical algorithm can. Grover’s algorithm can search an unstructured database or unordered list quadratically faster than the best classical algorithm with this purpose.

[Previous](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/) [Next](https://www.quantum-inspire.com/kbase/hello-quantum-world/)
