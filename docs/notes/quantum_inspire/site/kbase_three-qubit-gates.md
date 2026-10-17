> Full piece: [https://www.quantum-inspire.com/kbase/three-qubit-gates/](https://www.quantum-inspire.com/kbase/three-qubit-gates/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 430edd01405551312fe9ece82228fdb906076a28f2d2d5972d84f417b33492b4.

# Three-qubit gates

Some standard three-qubit gates, such as the Toffoli gate, the Fredkin gate and the Margolus gate, are often used in Quantum Computing. In the current version of cQASM, three-qubit gates such as Toffoli, Fredkin and Margolus are not part of of the language (yet). In order to use these gates, you need to use a version of the gates which is already decomposed into standard two-qubit gates. For your convenience we provide some standard decompsitions below for these gates, which you can simply copy and paste in your code. With [OpenSquirrel](https://www.quantum-inspire.com/kbase/opensquirrel/), you can use the circuit builder to plug in these decompositions.

Depending on the connectivity of the backend, other, more efficient decompositions might be available.

## Toffoli gate

The Toffoli gate, also known as the Controlled-Controlled NOT gate, is a three-qubit operation defined by:

$`\ Toffoli= \begin{pmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \end{pmatrix}`$

For more information see [Toffoli gate](https://en.wikipedia.org/wiki/Toffoli_gate) on Wikipedia.

It can be decomposed as follows:

```cqasm
version 3.0

qubit[3] q

/*
The Toffoli gate can be decomposed using 6 CNOT gates
*/

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
```

## Fredkin gate

The Fredkin gate, also known as the Controlled-SWAP gate, is a three-qubit operation defined by:

$`\ Toffoli= \begin{pmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \end{pmatrix}`$

For more information see [Fredkin gate](https://en.wikipedia.org/wiki/Fredkin_gate) on Wikipedia.

A standard decomposition that uses adjacent 9 CNOT gates is:

```cqasm
version 3.0

qubit[3] q

/*
The Fredkin gate can be decomposed using 9 adjacent CNOT gates
*/

CNOT q[2],q[1]
mY90 q[2]
T q[0,1,2]
CNOT q[0],q[1]
CNOT q[1],q[2]
Tdag q[1]
T q[2]
CNOT q[0],q[1]
CNOT q[1],q[2]
CNOT q[0],q[1]
Tdag q[2]
CNOT q[1],q[2]
X90 q[1]
Tdag q[2]
CNOT q[0],q[1]
CNOT q[1],q[2]
S q[2]
X90 q[1]
mX90 q[2]
```

## Margolus gate

The Margolus gate, which is sometimes referred to as the '*simplified*' Toffoli gate, is equivalent to the Toffoli gate up to a single change of sign in the diagonal. Note that in quantum algorithms you cannot simply replace a Toffoli by a Margolus gate, because the phase change of one of the status is relevant form most algorithms.

$`\ Margolus= \begin{pmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & -1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \end{pmatrix}`$

The decomposition requires only 3 CNOTs:

```cqasm
version 3.0

qubit[3] q

/*
The Margolus gate can be decomposed using 3 CNOT gates
*/

Ry(pi/4) q[2]
CNOT q[1],q[2]
Ry(pi/4) q[2]
CNOT q[0],q[2]
Ry(-pi/4) q[2]
CNOT q[1],q[2]
Ry(-pi/4) q[2]
```
