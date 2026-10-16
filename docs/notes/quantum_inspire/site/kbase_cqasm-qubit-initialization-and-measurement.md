> Full piece: [https://www.quantum-inspire.com/kbase/cqasm-qubit-initialization-and-measurement/](https://www.quantum-inspire.com/kbase/cqasm-qubit-initialization-and-measurement/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 adb9f414826587a10b6039e3958651c74ddc3bb0e880e2ef4e8d3b84dee1a3e6.

# cQASM: Qubit initialization and measurement

## Qubit initialization

By default, qubits will be initialized in the ground state in the z-basis at the start of the algorithm. Initialization in this state can be done specifically using the `prep_z` instruction. Initialization can also be done [along other bases](https://www.quantum-inspire.com/kbase/qubit-basis-states/). cQASM defines three prepare statements:

- [`prep_z`](https://www.quantum-inspire.com/kbase/prep-z/)
- [`prep_y`](https://www.quantum-inspire.com/kbase/prep-y/)
- [`prep_x`](https://www.quantum-inspire.com/kbase/prep-x/)

Depending on the hardware backend, preparation in a basis other than the z-basis may actually expand to an initialization in the z-basis followed by a rotation to obtain one of the basis states in the desired base.

## Qubit measurement

Each qubit in the qubit register has a corresponding classical bit in a classical register, known as the [binary register](https://www.quantum-inspire.com/kbase/binary-register/). The mapping is simple: the qubit with index 0 has a corresponding classical bit with index 0. Qubit 1 corresponds to bit 1. In general, the qubit at index n corresponds to the classical bit with index n.

The result of a measurement on a single qubit is 0 or 1. The measurement instructions store the result of measuring a qubit in the corresponding classical bit register.

As an example, let’s look at this simple cQASM program:

```cqasm
version 3.0

qubit[2] q
bit[2] b

init q[0]

X q[0]

b[0] = measure q[0]
```

The measurement taken at line 5 will measure the qubit at index 0 in the z-basis, and store the result (a classical 0 or 1) in the classical register at index 0.

The most used measurement is in the z-basis, which can be expressed in cQASM as `measure_z` or just `measure`. The full list of measurement instructions is:

- [`measure`](https://www.quantum-inspire.com/kbase/measure/) - an alias for `measure_z`
- [`measure_z`](https://www.quantum-inspire.com/kbase/measure-z/) - measure in the z-basis
- [`measure_y`](https://www.quantum-inspire.com/kbase/measure-y/) - measure in the y-basis
- [`measure_x`](https://www.quantum-inspire.com/kbase/measure-x/) - measure in the x-basis
- [`measure_all`](https://www.quantum-inspire.com/kbase/measure-all/) - measure all qubits in the z-basis

Note that only one binary register is used. When a qubit is measured multiple times during an algorithm, the corresponding bit in the binary register will be overwritten by the new measurement result, even when a measurement is done in a basis different than the basis used for an earlier measurement. Measurement results of qubit q\[n\] will always be stored in binary register b\[n\].
