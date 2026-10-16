> Full piece: [https://www.quantum-inspire.com/kbase/compilation/](https://www.quantum-inspire.com/kbase/compilation/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 64acdd5a7dd4afe1566a864da8edc2ce04dc57965d7fe4389535436c56f12eec.

# Compilation

## Compilers

A cQASM program (or any piece of computer code for that matter) needs to be compiled in order to be executed by the underlying hardware (or emulator), which is knows as the `target` for execution. Compilation requires knowledge of the hardware that is used for the execution, such as information about the topology of the chip (the connections between the qubits), the native gate set (the gate operations that can be directly executed by the hardware), information about the gate durations and various constraints, such as timing constraints, constraints on the parallel execution of operation etc.

Various compilers for quantum computers exist, that all operate at different levels of the stack. Some are low level compilers, used for the generation of micro-instructions of the control hardware or for the definition of microwave pulse envelopes. And some are more high level compilers, used for instance to convert a program written in a higher level of abstraction or templates to lower levels of abstraction, such as [LibKet](https://www.quantum-inspire.com/kbase/libket), or to decompose multi-qubit operations into single- and two-qubit operations.

In Quantum Inspire we use [LibQASM](https://qutech-delft.github.io/libqasm/latest/) to parse cQASM programs and produce an Abstract Syntax Tree (AST) representation of the program. LibQASM is also used by the [QX simulator](https://qutech-delft.github.io/qx-simulator/latest/index.html) and the [OpenSquirrel Compiler](https://qutech-delft.github.io/OpenSquirrel/).

In Quantum Inspire we use OpenSquirrel as the default compiler in the platform. Below we provide more general information about compiling a circuit. [On this page](https://www.quantum-inspire.com/kbase/opensquirrel/) you can find more specifics how we configure and use OpenSquirrel in the Quantum Inspire platform.

## Compilation passes

Generally, the compilation process consists of the following steps/passes:

- mapping;
- routing;
- decomposition;
- optimization;
- scheduling;
- code generation.

How to compile for a given target is known as the compilation strategy. More on compilation strategies can be found in the OpenQL manual.

## Mapping

Mapping is the act of changing the qubit indices in the circuit such that the connectivity constraints of the target device are met. For complex circuits, it is not always possible to find a solution that matches with all constraints (or it may be too time-consuming to compute, as this is an NP problem).

## Routing

In case mapping does not yield a satisfiable solution, a compiler could for instance insert SWAP gates to route non-nearest-neighbor qubits toward each other. Other solutions, depending on the hardware capabilities, could be to physically move qubits to another location where interactions are possible. Examples of moving qubits are the use of shuttlers in spin qubit systems, or the use of optical tweezers to relocate an atom to another position in neutral atom based quantum computers. Often, but not always, mapping and routing passes are combined into a single pass.

## Decomposition

Decomposition is the act of converting gates that cannot be executed using a single instruction in the target gateset into a list of gates that have the same behavior. For example, a SWAP gate may be decomposed into three CNOT gates.

## Optimization

Optimization tries to reduce the algorithm to a more compact form. This is particularly relevant after decomposition, as the decomposition rules may lead to sequences of gates that trivially cancel each other out. Other optimizations could be to commute operations (change the order if possible), to create operations which are easier to execute, remove irrelavant operations (such as Rz rotations after initialization of a qubit in the z-basis or just before a measurment of a qubist in the z-basis) or remove rotations which are so small, that they cannot be executed by a backend.

## Scheduling

Scheduling is the act of assigning cycle numbers to each gate in a kernel. This can of course be done trivially by assigning monotonously increasing cycle numbers to each gate in the order in which they were written by the user, but this is highly inefficient; instead, heuristics and commutation rules are used to try to find a more optimal solution that makes efficient use of the parallelism provided by the control architecture.

## Code generation

Finally, code generation takes the completed program and converts it to the assembly or machine-code format that the architecture-specific tools expect at their input.

## Compilation strategy

A strategy consists of a list of passes, along with pass-specific configuration options for each pass. Often, a more optimal compile strategy will have iterations between these passes, as a optimization pass for instance, could lead to a circuit that can be more optimally mapped then the initial mapping.

[Previous](https://www.quantum-inspire.com/kbase/software-development-kit/) [Next](https://www.quantum-inspire.com/kbase/opensquirrel/)
