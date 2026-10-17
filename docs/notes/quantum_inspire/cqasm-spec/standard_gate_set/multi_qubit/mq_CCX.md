> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CCX.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CCX.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 98192252ad7e5cc44f27caa46dcf2f693f62a0b333a9c95ab75f58e6c636ce9a;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Toffoli gate

| Identifier | Operator | Example statement          |
|------------|----------|----------------------------|
| CCX        | $`CCX`$ | **`CCX q[0], q[1], q[2]`** |

## Description

The Toffoli gate, also known as the controlled-[CNOT](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html) or CCX, gate is a three-qubit gate. It performs an [X gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html) on the third qubit, conditional on both the first and second qubits being in state $`|1\rangle`$. The first two qubits are referred to as the control qubits and the third qubit as the target qubit.

In the standard computational basis for three qubits $`\{|000\rangle, |001\rangle, |010\rangle, |011\rangle, |100\rangle, |101\rangle, |110\rangle, |111\rangle\}`$, the CCX gate:

- leaves both control qubits unchanged;
- performs an X gate on the target qubit when both control qubits are in state $`|1\rangle`$;
- leaves the target qubit unchanged otherwise.

Note

The notion of control qubits and a target qubit (for any controlled operation) only holds for the standard computational basis. Generally, in another basis, all states could be affected.

### Aliases

Also known as *controlled-controlled-X* or *CCNOT*.

### Properties

- [Involutory](https://en.wikipedia.org/wiki/Involutory_matrix) operation (its own inverse);
- [Controlled](https://en.wikipedia.org/wiki/Quantum_logic_gate#Controlled_gates) gate;
- Universal for reversible classical computation.

## Representation

```math
\begin{align}
CCX &= CCNOT = \left(\begin{matrix}
1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
CCX\,|000\rangle &= |000\rangle \\
\\
CCX\,|001\rangle &= |001\rangle \\
\\
CCX\,|010\rangle &= |010\rangle \\
\\
CCX\,|011\rangle &= |111\rangle \\
\\
CCX\,|100\rangle &= |100\rangle \\
\\
CCX\,|101\rangle &= |101\rangle \\
\\
CCX\,|110\rangle &= |110\rangle \\
\\
CCX\,|111\rangle &= |011\rangle
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For this three-qubit controlled gate, the matrix is represented such that $`q_0`$ and $`q_1`$ are the *control* qubits and $`q_2`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle`$.
