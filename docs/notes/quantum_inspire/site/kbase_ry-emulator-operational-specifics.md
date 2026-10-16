> Full piece: [https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 8526412dfaf5bebe6039a37446d5880e4826a1d4e64edc4fcc8abae0420c827f.

# Ry emulator: Operational specifics

## Introduction

Ry Emulator is a neutral atom quantum computing emulator that currently operates with 9 qubits. This number will be expanded soon, and also in the near future an actual neutral atom hardware platform will be added as a backend. The gate operations will be expanded in the future as well, but currently they comprise of single qubit $`X, Z, T, S, Rx, Rz`$ gates and multi-qubit Rydberg gates. These Rydberg gates are implemented via an assembly code block that contains two specific directives: INIT and RYD. These are explained in detail on page Code example: Getting started with the neutral atom platform. Part of this backend is that one can learn how to program a neutral atom platform with hardware specific properties, such as the geometrical placement of the qubits for particular qubit array configurations that may be specific for certain algorithms.

## Topology

Neutral atom computing allows users to place atoms on a specific lattice position and have connections between nearby atoms. Our Rydberg backend provides a regular rectangular lattice in which users can place the atoms where each atom represents a qubit. The Rydberg blockade mechanism enables entanglement of neighboring atoms. A user can place at most 9 atoms to a rectangular lattice for a circuit.

## Measurement

The Rydberg backend doesn’t allow mid circuit measurements. In fact, the user doesn’t provide any measurement statement, each circuit has an implied measurement on all qubits at the end. The backend will return the measurement results for all qubits at the end of the run.

## Operations

We allow a number of single qubit operations and some Rydberg platform specific directives.

- Single qubit operations:
  - X, Z, T, S, Rx, Rz
- Rydberg specific directives:
  - INIT: Initializes an atom to a specific position
  - RYD: Global Rydberg operation

The INIT operation can only be used at the start of the circuit. If the user tries to use it after any operation is performed, an error message will be displayed. The Rydberg specific operations are discussed in more detailed in: [Code example: Getting started with the neutral atom platform](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform)

[Previous](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/) [Next](https://www.quantum-inspire.com/kbase/emulator-backends/)
