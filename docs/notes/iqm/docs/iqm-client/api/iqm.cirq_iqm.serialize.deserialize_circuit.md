> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.deserialize_circuit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.deserialize_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d7e29d9f0953c1dc0865aea7c31e7a538173e80f357eaca07dcbae3b5ed28260.

# iqm.cirq_iqm.serialize.deserialize_circuit

iqm.cirq_iqm.serialize.deserialize_circuit(*circuit: [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*) → Circuit  
Deserializes a quantum circuit from the IQM data transfer format to a Cirq Circuit.

Parameters:  
**circuit** ([*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")) – data transfer object representing the circuit

Returns:  
quantum circuit

Return type:  
*Circuit*
