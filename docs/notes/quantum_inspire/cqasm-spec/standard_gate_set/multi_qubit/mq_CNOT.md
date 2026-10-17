> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 a92df14768e086c2c49d84976c0be6995dd8d715387aa0e94da351391c444d9b;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Controlled-NOT gate

| Identifier | Operator | Example statement     |
|------------|----------|-----------------------|
| CNOT       | $`CNOT`$ | **`CNOT q[0], q[1]`** |

## Description

The controlled-NOT, or CNOT, gate is a two-qubit gate. It performs an X gate on the second qubit, conditional on the state of the first qubit. The first qubit is usually referred to as the control qubit and the second qubit as the target qubit.

In the standard computational basis for two qubits $`\{|00\rangle ,|01\rangle \,|10\rangle ,|11\rangle \}`$ , the CNOT gate:

- leaves the control qubit unchanged,
- performs an X gate on the target qubit, when the control qubit is in state $`|1\rangle`$,
- leaves the target qubit unchanged, when the control qubit is in state $`|0\rangle`$.

Note

The notion of a control qubit and a target qubit (for any controlled operation) only holds for the standard computational basis. Generally, in another basis, all states could be affected.

### Aliases

Also known as *controlled-X*, *CX*, or *controlled bit-flip* gate.

### Properties

- [Clifford](https://en.wikipedia.org/wiki/Clifford_gates) gate;
- [Involutory](https://en.wikipedia.org/wiki/Involutory_matrix) operation (its own inverse);
- [Controlled](https://en.wikipedia.org/wiki/Quantum_logic_gate#Controlled_gates) gate;
- Perfect Entangler (maximally entangles specific product states);
- Maximum Entangling Power over all uniformly random product states;
- Ising gate.

## Representation

```math
\begin{align}
CNOT &= \left(\begin{matrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 0 & 1 \\
0 & 0 & 1 & 0 
\end{matrix}\right)
\end{align}
```

which is equal to:

```math
CNOT = CX = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes X.
```

## Operation examples

### Standard basis

```math
\begin{align}
CNOT\,|00\rangle &= |00\rangle \\
\\
CNOT\,|01\rangle &= |11\rangle \\
\\
CNOT\,|10\rangle &= |10\rangle \\
\\
CNOT\,|11\rangle &= |01\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.
