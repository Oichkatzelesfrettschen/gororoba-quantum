> Full piece: [https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 277a4a6a5f87eb0444f220c9b7405872c33b019ee0be8dc712ee234c41e3a3d5.

# Spin-2+: Operational specifics

## Introduction

Not all quantum devices can realize all quantum gates. In practice this is not an issue since any quantum gate can be constructed from a series of universal quantum gates provided the device can execute them. The downside is that the combination of gates takes longer to perform and hence introduces a higher error rate.

For example, on spin-qubit devices the CNOT gate is not directly available. We can however realize this gate by a combination of single qubit rotations and a CZ gate. In this section the restrictions of Spin-2 are specified.

## Topology and allowed gate set

Each of the quantum processors has a specific topology the way the qubits are connected) and a specific allowed gate set (supported qubit operations).

Spin-2+ has two data qubits which are connected to one ancilla qubit user for readout. Currently, you are only allowed to perform operations on the two data qubits. You can execute arbitrary single-and two-qubit gates according to the [latest cQASM specifications](https://qutech-delft.github.io/cQASM-spec/latest/) which will be decomposed by the OpenSquirrel compiler to a subset (**`X90`**, **`CZ`**) of the native gate operations for this backend, which are **`X90`**, **`mX90`**, **`Y90`**, **`mY90`**, **`Rz`**, and **`CZ`**.

Specifically:

- Multiple line comments in `/* … */` are supported.
- Single line comments in `// …`, `/* …*/` are supported.
- A program **must** start with version 3.0.
- The version must be followed by a single declaration of the format `qubit[1-4] <varname>` or `qubit <varname>`, where the latter implies `qubit[1] <varname>`.
- `<varname>` must be used to denote a qubit
- The single-gate-multiple-qubit (SGMQ) notation is fully supported for single qubit gates
- Libqasm 1.x language structures are not supported.
- No `reset` instructions are allowed.
- The Spins-2+ backend will init all supported qubits before circuit execution and measure all in the z-basis at the end of the circuit and only return the subset as defined in the qubit register.
  - Bit register declaration statements, e.g., bit\[[number-of-bits:INT](number-of-bits:INT)\] [bit-register-name:ID](bit-register-name:ID) or bit [bit-name:ID](bit-name:ID), are accepted and subsequently ignored.
  - Measure instruction statements assign outcomes to bit variables, e.g. [bit-name:BIT](bit-name:BIT) = measure [qubit-argument:QUBIT](qubit-argument:QUBIT). These statements are accepted and subsequently ignored.

## Compile strategy

As defined above, the Spin-2+ backend supports a small set of native gate operations, namely **`X90`**, **`mX90`**, **`Y90`**, **`mY90`**, **`Rz`**, and **`CZ`**. When executing quamtum circuits on this backend, either via the WEB GUI or via the SDK, quantum circuits are compiled to a combination of **`X90`**, **`Rz`**, and **`CZ`** gates.

- single-qubit rotation around the z-axis with `Rz(angle)`, executed as a virtual operation (control signal phase update) and require zero time.

The compiler decomposes all other allowed operations into this native gate set using the following methods:

1.  Two-qubit operations `CNOT`, `SWAP`, `CR` and `CRk` are decomposed to `CZ` operations in combination with single-qubit operations
2.  Sequences of single-qubit operations on one qubit are decomposed using the method described in [McKay - Efficient Z-Gates for Quantum Computing](https://arxiv.org/abs/1612.00858) resulting in a sequence of maximum five single-qubit operations, namely three **`Rz(..)`** operations with different angles of rotation and two **`Rx(pi/2)`** (or equivalently **`X90`**) operations.
3.  Consecutive operations which result in identity are removed from the algorithm

Note that a large number of single-qubit Clifford operations will be efficiently converted into a sequence of just one **`X90`** gate, combined with zero, one or two **`Rz(..)`** gates.

## Initialization, execution and readout

The qubits are initialized in the ground state at the start of each shot. The single-qubit **`X90`** operations are executed by sending a microwave pulse of the required duration, amplitude and phase to the qubits. The **`Rz()`** operation is executed by a phase-update (virtual Z-gate) of the the microwave signals. The two-qubit **`CZ`** operation is executed by a calibrated exchange interaction between the qubits which results in a controlled 180 degree phase change of the \|11\> state of the qubits. Single-qubit operations on two different qubits are executed in sequence, not in parallel. At the end of the algorithm both qubits are **always** measured.
