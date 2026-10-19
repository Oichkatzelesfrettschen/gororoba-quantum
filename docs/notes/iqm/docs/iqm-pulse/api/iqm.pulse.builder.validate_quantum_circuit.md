> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.validate_quantum_circuit.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.validate_quantum_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 04b52bfb34cacf47b540c71b705edc58cdb00b08442be2a9b717e9b89293ea52.

# iqm.pulse.builder.validate_quantum_circuit

iqm.pulse.builder.validate_quantum_circuit(*operations*, *op_table*, *\**, *require_measurements=False*)  
Validate a sequence of circuit operations constituting a quantum circuit.

Parameters:  
- **operations** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – quantum circuit to be validated

- **op_table** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – table containing allowed/calibrated quantum operations

- **require_measurements** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff True the circuit must include at least one measurement operation

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `operations` do not constitute a valid quantum circuit

Return type:  
*None*
