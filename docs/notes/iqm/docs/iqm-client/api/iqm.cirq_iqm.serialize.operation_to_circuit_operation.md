> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.operation_to_circuit_operation.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.operation_to_circuit_operation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 217a32919f08864ae57168bc3e5bc9096779cda04c2c32e5dcb2c97668df9912.

# iqm.cirq_iqm.serialize.operation_to_circuit_operation

iqm.cirq_iqm.serialize.operation_to_circuit_operation(*operation: Operation*) → [CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")  
Map a Cirq Operation to the IQM data transfer format.

Assumes the circuit has been transpiled so that it only contains operations natively supported by the given IQM quantum architecture.

Parameters:  
**operation** (*Operation*) – a Cirq Operation

Returns:  
the converted operation

Return type:  
CircuitOperation

Raises:  
**OperationNotSupportedError When the circuit contains an unsupported operation.** –
