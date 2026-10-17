> Full piece: [https://docs.openquantum.com/qrisp-plugin/supported-operations/](https://docs.openquantum.com/qrisp-plugin/supported-operations/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8ff5f4b8570d79b9272260cbdf93bdd8fb8368bf613ad0b62544f5c03bab2712.

# Supported Operations

The Qrisp plugin executes programs by compiling them to a Qiskit circuit (`QuantumCircuit.to_qiskit()`), converting that to OpenQASM, and submitting it to the platform. Operation support therefore follows Qrisp's own compilation and the target backend's capabilities.

## Gates

Qrisp lowers its high-level constructs (`QuantumVariable`, `QuantumFloat`, arithmetic, control flow) to standard gates during compilation. The resulting circuit is converted through Qiskit, so any gate Qrisp emits that maps to a standard QASM gate is supported. Gates outside a backend's native set are decomposed by Qrisp/Qiskit before submission.

The target backend's capabilities are the source of truth. The plugin validates each circuit against them and raises early if a construct is not permitted:

- gate set (native + decomposable),
- qubit connectivity (coupling map),
- shot and qubit-count limits,
- structural features such as reset, mid-circuit measurement, and barriers.

Discover a backend's capabilities with the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/) or the [Qiskit plugin](https://docs.openquantum.com/qiskit-plugin/backends-targets/).

## Single Quantum Register

Qrisp emits one quantum register per qubit, but the platform precompiler allows at most one. The plugin automatically flattens the compiled circuit onto a single quantum register (and a single classical register) before submission, so no action is required on your part.

## Measurements

The platform is shot-based: every execution returns measurement counts.

- `QuantumVariable.get_measurement(backend=oq, shots=N)` returns Qrisp's decoded result (a dictionary of outcomes to probabilities).
- `QuantumCircuit.run(backend=oq, shots=N)` returns the counts for the raw circuit.

Analytic (shot-free) execution is not supported.

## Bit Ordering

The platform returns bitstrings in Qiskit's little-endian convention. Qrisp reconciles bit order during measurement decoding, so the default (`reverse_bits=False`) returns correct results — a `QuantumFloat` set to 6 measures as 6, not the bit-reversed 3. You should not normally need to change this. If a particular backend ever returns counts in the opposite order for your program, construct the backend with `reverse_bits=True`:

``` python
oq = OpenQuantumBackend(backend="...", shots=1024, reverse_bits=True)
```

When trying a new backend, confirm ordering with an asymmetric value (set a `QuantumFloat` to a non-palindromic number such as 6) rather than a symmetric state, which cannot reveal the ordering.

## Serialization Format

Circuits are serialized as OpenQASM 3 by default. Pass `export_format="qasm2"` to emit OpenQASM 2 instead:

``` python
oq = OpenQuantumBackend(backend="...", shots=1024, export_format="qasm2")
```
