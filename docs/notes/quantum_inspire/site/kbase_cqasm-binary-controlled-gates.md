> Full piece: [https://www.quantum-inspire.com/kbase/cqasm-binary-controlled-gates/](https://www.quantum-inspire.com/kbase/cqasm-binary-controlled-gates/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 49bf842b105c27221c2aa6d43965d8748c0014327feea6ccdb4e32624137a7ec.

# cQASM: Binary controlled gates

## Binary controlled gates

All single qubit gates can be controlled by the result of an earlier measurement or measurements. These are called *binary controlled gates*. Binary controlled gates can only be used in the QX emulator, not on our current actual quantum processors due to coherence time limitations. In the simplest form, the single qubit gate is executed only when the measurement result was 1. As an example, consider this simple cQASM program:

```cqasm
version 1.0

qubits 2

prep_z q[0:1]
H q[0]
measure_z q[0]

c-X b[0], q[1]
measure q[1]
```

Line 5 prepares the qubits, followed by the creation of a superposition on qubit 0.

This qubit is measured in line 7, which will result in a 0 or 1 (each with 50% probability) being stored in the classical register at index 0.

Line 9 shows the binary-controlled X gate. Only when the measurement of the qubit at index 0, `q[0]` on line 7 yielded 1 (and thus the bit at index 0, `b[0]` is 1) will the X gate be executed. If `b[0]` is 0, the X gate will not be applied. In the circuit visualization a small '0' is attached to the left of the binary controlled X gate.

Any single qubit gate can be prepended with `c-` to execute that gate only when the classical argument is 1. Furthermore, it is possible to specify more than one classical bit using [SGMQ syntax](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/). The gate is executed if and only if all specified classical bits are 1:

```cqasm
version 1.0

qubits 3

prep_z q[0:2]
X q[1]
measure_z q[0]
measure_z q[1]
c-Y b[0,1], q[2]
```

In this example, the binary-controlled Y gate on line 9 will not apply (no Y rotation is carried out on `q[2]`) because `b[0]` will be 0.

## Classical logic not

Sometimes it is desirable to apply the conditional gate when a bit is 0 instead of 1. A bit in the measurement register can be flipped with the `not` instruction:

```cqasm
version 1.0

qubits 2

prep_z q[0,1]
H q[0]
measure_z q[0]
not b[0]
c-X b[0], q[1]
```

## Non-deterministic algorithm

Note that in the first example above we added a `measure` instruction at the end of the algorithm for both qubits. This is because the measurement on `q[0]`, followed by the controlled-X gate on `q[1]` renders the algorithm non-deterministic (the final state of the system depends on the outcome of the first measurement. For non-deterministic algorithms me must always include a `measure` instruction at the end in order to get meaningful results, see [optimization of simulations](https://www.quantum-inspire.com/kbase/optimization-of-simulations/).

Side note: It is not the binary-controlled gate that actually makes the algorithm non-deterministic. It is the measurement on the first qubit. Without the measurement on the first qubit the algorithm would be deterministic, because the input for the controlled X-gate would always be zero.
