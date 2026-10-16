> Full piece: [https://www.quantum-inspire.com/kbase/opensquirrel/](https://www.quantum-inspire.com/kbase/opensquirrel/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 02041f90698b564570255dab0ef478bcd7724c995ec1dd8119f3da0ea292902d.

# OpenSquirrel compiler

In the Quantum Inspire platform we use [LibQASM](https://qutech-delft.github.io/libqasm/latest/) for parsing of cQASM programs and [OpenSquirrel](https://qutech-delft.github.io/OpenSquirrel/) as compiler.

A full tutorial on OpenSquirrel, explaining the different passes that are available and explaining the programmatic API is available on [github pages](https://qutech-delft.github.io/OpenSquirrel/). OpenSquirrel if fully compatible with cQASM.

## Compile stages (compilation strategy)

The Quantum Inspire platform internally uses so-called **compile stages**. Each compile **stage** can contain zero, or more compile **passes** from OpenSquirrel. The names of the compile stages are:

- (internal) Verification
- Decomposition
- Mapping
- Optimization
- Routing
- (Scheduling)
- Exporting
- (internal) Validation (backend)

The verification and validation stage cannot be skipped, also not when using the QI tool (see below). The scheduling stage is currently not used but is added for future features.

Each backend defines a default compilation strategy for the QI platform, by defining the passes for each stage and the order of the stages. The default QI platform compile strategy for each backend can be found in the [Spin specifics page](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/) and [Starmon specifics page](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/).

## Using the WEB GUI

When you use the WEB GUI, quantum programs that you `RUN` will go through **all compile stages**. The result of each compile stage is used internally as input for the next compile stage. These files are not visible to you.

When you do want to inspect the result of each compile stage, you should select `Compile` from the menu instead. This will generate a set of files with filenames appended by `_compiled_stage` for each stage in the pre-defined compile strategy, but it will not execute the quantum program.

Note that you can select a compile target that is different from your final execution target. This allows you to for instance compile a quantum program for a hardware backend, but run the compiled program on an emulator backend.

As an example take the following quantum program. Notice that line 6 uses [SGMQ notation](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/) to generate three CNOT's.

```cqasm
version 3.0

qubit[2] q

H q[0]
CNOT q[1,0,1],q[0,1,0]
```

When this is compiled using Spin-2+ as a backend and taking into account the [compile strategy for Spin-2+](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/) you may expect that the three CNOT gates are compiled to three CZ gates sandhwiched between H gates on the target qubits. This measn that the first H gate on `q[0]` will be cancelled. From the McKay decomposition for single-qubit gates, you expect each H gate to be decomposed in Rz and X90 gates, as can be seen from the compiled circuit:

```cqasm
version 3.0

qubit[2] q

Rz(3.1415927) q[0]
CZ q[1], q[0]
Rz(-1.5707963) q[0]
X90 q[0]
Rz(1.5707963) q[0]
Rz(1.5707963) q[1]
X90 q[1]
Rz(-1.5707963) q[1]
CZ q[0], q[1]
Rz(-1.5707963) q[1]
X90 q[1]
Rz(1.5707963) q[1]
Rz(1.5707963) q[0]
X90 q[0]
Rz(-1.5707963) q[0]
CZ q[1], q[0]
Rz(-1.5707963) q[0]
X90 q[0]
Rz(1.5707963) q[0]
```

## Using the QI Tool

When you use the QI tool, directly or through the QIskit or Pennylane plugin, you have more freedom for your compile strategy and you can bypass one or more of the ore-defined compile stages (except for the verification and validation stages which check the integrity of your quantum programs.

## Using OpenQL and LibKet together with Quantum Inspire

In the current version of Quantum Inspire, LibKet and OpenQl are not integrated with Quantum Inspire. However, both allow compilation of algorithms written in cQASM and compilation to Quantum Inspire targets. Qiskit also provides standard compilation passes which can be used together with the Quantum Inspire plugin for Qiskit. The interested user is referred to these programs to get the most out of Quantum Inspire.

## Stacking multiple compilers

When you use mutliple compilers consecutively, always check your results, because the integrity of your quantum program may not always be preserved.

[Previous](https://www.quantum-inspire.com/kbase/compilation/) [Next](https://www.quantum-inspire.com/kbase/low-level-api/)
