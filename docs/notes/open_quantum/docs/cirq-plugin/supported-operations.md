> Full piece: [https://docs.openquantum.com/cirq-plugin/supported-operations/](https://docs.openquantum.com/cirq-plugin/supported-operations/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b389b5d7b1b5b19a37799190d6d73f52d8e269427a50322ec5cc3f05c23c3869.

# Supported Operations

The Cirq plugin executes circuits by exporting them to OpenQASM with Cirq's native exporter (`cirq.Circuit.to_qasm()`) and submitting the result to the platform. Operation support therefore follows Cirq's own QASM export and the target backend's capabilities.

## Gates

Any gate Cirq can export to its QASM gate set is supported. Cirq lowers common operations (`H`, `X`, `Y`, `Z`, `S`, `T`, `CNOT`, `CZ`, `SWAP`, single-qubit rotations `rx`/`ry`/`rz`, and more) to standard `qelib1` gates. Gates outside a backend's native set are transpiled by the platform precompiler before execution.

If Cirq cannot express an operation in QASM, `to_qasm()` raises before anything is submitted. Decompose such gates with Cirq (for example `cirq.decompose(op)`) before sampling.

## Single Quantum Register

The platform precompiler allows at most one qubit register. Cirq maps all qubits onto a single `qreg q[N]` in `cirq.QubitOrder.DEFAULT` order, so this constraint is satisfied automatically — no flattening step is needed.

## Measurements

The platform is shot-based: every execution returns measurement counts. Your circuit must contain at least one `cirq.measure(...)`; the QASM exporter does **not** add measurements for you.

[](#__codelineno-0-1)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-0-2)`circuit`` ``=`` ``cirq``.``Circuit``([``cirq``.``H``(``q``[``0``]),`` ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`` ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``)])`\
[](#__codelineno-0-3)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``1024``)`\

Results come back as a standard `cirq.Result`:

- `result.histogram(key="m")` — a `Counter` of big-endian integer outcomes.
- `result.measurements["m"]` — a `(repetitions, num_qubits)` `uint8` array.
- `result.repetitions` — the shot count.

A circuit may measure into several keys (e.g. `cirq.measure(q0, key="a")` and `cirq.measure(q1, key="b")`); the plugin slices the platform bitstring back into per-key arrays from the classical registers in the submitted QASM.

Because the sampler implements `run_sweep`, `run`, `sample`, and `run_batch` also work, and a `cirq.Sweepable` of parameter resolvers submits one circuit per resolver.

Analytic (shot-free) execution and state-vector simulation are not supported — use a local `cirq.Simulator` for those.

## Bit Ordering

The platform returns counts little-endian (the first classical bit is the rightmost character, Qiskit-style), while Cirq is big-endian (the first measured qubit is the most-significant bit). The sampler reverses each bitstring by default (`reverse_bits=True`) so the mapping is correct. This was confirmed live against an asymmetric `|10>` state.

Set `reverse_bits=False` only for a backend that returns counts big-endian:

[](#__codelineno-1-1)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"..."``,`` ``reverse_bits``=``False``)`\

When trying a new backend for the first time, verify ordering with an asymmetric state (apply `X` to one qubit and confirm which bit flips).

## Serialization Format

Circuits are serialized as OpenQASM 3.0 by default, matching the other Open Quantum plugins. Pass `export_format="qasm2"` to emit OpenQASM 2.0 instead:

[](#__codelineno-2-1)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"..."``,`` ``export_format``=``"qasm2"``)`\
