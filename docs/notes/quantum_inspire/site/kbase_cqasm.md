> Full piece: [https://www.quantum-inspire.com/kbase/cqasm/](https://www.quantum-inspire.com/kbase/cqasm/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 c60f10f56668466dca6f44b35e60ea9aa9ac864c8986ac57f90daf8663ff70c9.

# cQASM: A Quantum Programming Language

QASM originated as a language for formally defining a quantum circuit to render images for visualization purposes. As quantum computation evolved, the language was adopted as a way to specify quantum circuits as input to a quantum computer.

A QASM program declares the classical bits and qubits, describes the operations (gates) on those qubits and the measurements needed to obtain the classical result by inspecting the qubits. Many variants of QASM have seen the light since its inception as a mark-up language for generating images. Quantum Inspire uses cQASM 3.0. Whenever this site mentions QASM or cQASM, it is referring to cQASM 3.0 unless explicitly stated otherwise.

cQASM is used to describe relatively simple circuits, which is fine for the current generation of quantum computers. In the future, a higher level of abstraction will be required to deal with the billions of qubits needed to make up a practical quantum computer.

cQASM 3.0 is extensively [described here](https://qutech-delft.github.io/cQASM-spec/) on github pages

## Basic Example

Let's start with an example where we create a [Bell state](https://www.quantum-inspire.com/kbase/bell-states/) to get a feel for the language:

```cqasm
version 3.0

// a basic cQASM example 

/*This is an example 
        creating one of the Bell states */

qubit[2] q
bit[2] b

init q[0:1]

H q[0]
CNOT q[0], q[1]

b[0,1] = measure q[0,1]
```

The file starts with the specification of the cQASM version on line 1. This line is always present.

Line 3 is a single-line comment. Single-line comments start with a (`//`), and everything after it until the end of current line is ignored by the cQASM parser. Use comments to document your code, so that someone else can understand what you were trying to do (note: someone else could also be your future self).

Line 5 and 6 show a multi-line comment starting with (`/*`) and ending in (`*/`)

Line 8 defines the size of the qubit register. In this simple example, two qubits are defined. Each qubit in the register is identified by its index. The first qubit has index 0 and the second qubit has index 1. When displaying qubits or bits, the (qu)bit with index 0 is the right-most one.

Line 9 defines the size of the bit register.

Line 11 contains the first quantum instruction, to prepare both qubits in their ground state. The [Single-Gate Multiple-Qubits (SGMQ) syntax](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/) is used to address both qubits at once. Alternatively, we could have written line 11 as two lines.

Line 13 and 14 describe the quantum gates that form the circuit. First, a Hadamard gate is applied to the qubit with index 0, followed by a CNOT where the qubit with index 0 is the control qubit and the qubit with index 1 is the target qubit.

Finally, at line 16 the state of all qubits is measured along the Z-axis to obtain the final result.

Note that cQASM 3.0 is case-sensitive, whereas cQASM 1.0 was case-insensitive.

## Features deprecated from cQASM 1.0

### Static loops and sub circuits

The previous version of cQASM (cQASM 1.0) supported sub circuits to create static loops. This feature has been deprecated in cQASM. Static loops can be defined much more easily and with enhanced features using for instance the circuit builder functionality from [OpenSquirrel](https://qutech-delft.github.io/OpenSquirrel/index.html) or using the Quantum Inspire plugins for Qiskit and Pennylane SDK's.

### Curly bracket notation

cQASM 1.0 included the use of Curly brackets around instructions, denoting that these gates should be executed in parallel, if possible. Executing instructions in parallel or sequentially is a form of scheduling, which is not part of the cQASM language, but is handled by the backends (just as other scheduling choices, like whether to exeute an instruction as soon as possible or as late as possible). We have therefore removed this feature from the language. Some form of scheduling is still possible by using the wait and barrier instructions, which act as a non-commuting instruction on the qubits.
