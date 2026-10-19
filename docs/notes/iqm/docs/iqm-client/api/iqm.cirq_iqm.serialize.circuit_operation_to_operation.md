> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.circuit_operation_to_operation.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.circuit_operation_to_operation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 91a783662890a50ba92fdfca7280a1423c6791a4f406f541f1e2cbf85fc9b171.

# iqm.cirq_iqm.serialize.circuit_operation_to_operation

iqm.cirq_iqm.serialize.circuit_operation_to_operation(*circuit_operation: [CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*) → Operation  
Convert an IQM circuit operation to a Cirq Operation.

Parameters:  
**circuit_operation** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")) – the IQM circuit_operation

Returns:  
the converted operation

Return type:  
Operation

Raises:  
**OperationNotSupportedError When the circuit contains an unsupported operation.** –
