> Full piece: [https://www.quantum-inspire.com/kbase/qubit-register/](https://www.quantum-inspire.com/kbase/qubit-register/)
> Retrieved 2026-10-16T22:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 eae8d9951be0364b5eab495ee55bcf7c927a0a7d85813d8dea79f45474a79dd7.

# Qubit register

## Virtual qubit register

The qubits in a quantum computer are conceptually grouped together in the qubit register. Each qubit has an index within this register, starting at index 0 and counting up by 1. So, a system with 5 qubits, for example, has a qubit register that has a width of 5 and indexed by 0, 1, 2, 3 and 4.

Each qubit can be addressed in qubit operations by using the qubit index.

When writing an algorithm in Quantum Inspire you can use one or more qubit registers. These are referred to a *virtual* qubit registers. They are not (yet) linked to the physical qubits on a chip. As an example take the following [qubit register declarations](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html):

In this example, 5 individual virtual qubit registers are defined, which can all be used in the quantum algorithm. When this algorithm is executed on an actual quantum backend, the Quantum Inspire platform will map these virtual qubits onto physical qubits, simply using the order of declaration. So the mapping that will be done is:

`north[0] --> q[0] north[1] --> q[1] left --> q[2] center --> q[3] right --> q[4] south[0] --> q[5] south[1] --> q[6]`

## Qubit register memory usage in an emulator

The full quantum state is stored in memory and described in terms of the probability amplitude for each state. As an example, a two-qubit system is described by 4 complex parameters:

$`\lvert \Psi \rangle = \alpha_{0} \lvert 00 \rangle + \alpha_{1} \lvert 01 \rangle + \alpha_{2} \lvert 10 \rangle +  \alpha_{3} \lvert 11 \rangle`$

and a three-qubit system is described by 8 complex parameters:

$`\lvert \Psi \rangle = \alpha_{0} \lvert 000 \rangle + \alpha_{1} \lvert 001 \rangle + \alpha_{2} \lvert 010 \rangle + \cdots + \alpha_{7} \lvert 111 \rangle`$

where $`\alpha_i`$ are the probability amplitudes associated with the computational basis states, see also [qubit basis states](https://www.quantum-inspire.com/kbase/qubit-basis-states/).

Because each complex parameter is specified by two 64-bit precision floating-point values, a quantum system with 3 qubits requires 128 bytes of memory. A system with 10 qubits requires 16 kBytes. A system with 37 qubits requires more than 2 TBytes.

[Previous](https://www.quantum-inspire.com/kbase/managing-your-account/) [Next](https://www.quantum-inspire.com/kbase/binary-register/)
