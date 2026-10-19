> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a93b1bd6e738768d5b1e733f179df3a635af275808c6b5e80039071d3bc78a2.

# iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter

iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter(*qc: QuantumCircuit*, *dqa: DynamicQuantumArchitecture*, *circuit_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'Qrisp_converted'*) → [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")  
Converts a Qrisp QuantumCircuit to an IQM `Circuit`.

The circuit should already be transpiled to native gates (CZ, PRX) and have a valid qubit layout. For a one-step transpile-and-convert workflow, use `transpile_to_iqm()` followed by this function.

Parameters:  
- **qc** (*QuantumCircuit*) – The Qrisp circuit to convert. Must already be transpiled to IQM-native gates (CZ, PRX).

- **dqa** (*DynamicQuantumArchitecture*) – Determines the physical qubit names and available gate loci. `dqa` maps Qrisp’s `qubits[i]` to the i-th physical qubit name (`QB1`, `QB2`, …) in the IQM device.

- **circuit_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name assigned to the output IQM circuit.

Returns:  
`qc` converted to IQM circuit format.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the circuit has more qubits than the DQA.

- [**Exception**](https://docs.python.org/3.11/library/exceptions.html#Exception "(in Python v3.11)") – If an unknown gate type is encountered (circuit was not properly transpiled).

Return type:  
[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")

Examples

``` python
from qrisp import QuantumCircuit
from iqm.qrisp_iqm import transpile_to_iqm, qrisp_to_iqm_converter

# 1. Create and transpile a Qrisp circuit
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 2)
qc.measure(range(3))

coupling_map = [(0, 1), (1, 2), (2, 3)]
transpiled = transpile_to_iqm(qc, coupling_map)

# 2. Obtain the IQM device DQA
from iqm.iqm_client import IQMClient
client = IQMClient.from_url(
    iqm_server_url="https://resonance.iqm.tech/",
    quantum_computer="garnet",
    token="YOUR_API_TOKEN",
)

dqa = client.get_dynamic_quantum_architecture()

# 3. Convert the transpiled circuit to IQM format
iqm_circuit = qrisp_to_iqm_converter(transpiled, dqa)
print(iqm_circuit)

# Yields:

# Circuit(
#   name='Qrisp_converted',
#   instructions=(
#     CircuitOperation(name='prx', locus=('QB1',),
#       args={'angle': 1.5707963267948966, 'phase': 6.283185307179586}, implementation=None),
#     CircuitOperation(name='prx', locus=('QB2',),
#       args={'angle': 1.5707963267948966, 'phase': 6.283185307179586}, implementation=None),
#     CircuitOperation(name='cz', locus=('QB1', 'QB2'), args={}, implementation=None),
#     CircuitOperation(name='measure', locus=('QB1',), args={'key': 'cb_0'}, implementation=None),
#     CircuitOperation(name='measure', locus=('QB3',), args={'key': 'cb_0'}, implementation=None),
#     CircuitOperation(name='prx', locus=('QB2',),
#       args={'angle': 1.5707963267948966, 'phase': 3.141592653589793}, implementation=None),
#     CircuitOperation(name='measure', locus=('QB2',), args={'key': 'cb_0'}, implementation=None)),
#   metadata=None,
# )
```

The printed IQM circuit shows each gate as a `CircuitOperation` with its name, locus (target qubits), and arguments.
