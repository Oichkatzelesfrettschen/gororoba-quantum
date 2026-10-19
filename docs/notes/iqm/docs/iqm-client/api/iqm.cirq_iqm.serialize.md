> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b81db37c39e3ef35e4906d836c962a0fe741ccf99c3cac9e08230f23e094d1a7.

# serialize

Full path: iqm.cirq_iqm.serialize

Helper functions for serializing and deserializing quantum circuits between Cirq and IQM circuit formats.

Functions

|  |  |
|----|----|
| [`circuit_operation_to_operation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.circuit_operation_to_operation.html#iqm.cirq_iqm.serialize.circuit_operation_to_operation "iqm.cirq_iqm.serialize.circuit_operation_to_operation")(circuit_operation) | Convert an IQM circuit operation to a Cirq Operation. |
| [`deserialize_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.deserialize_circuit.html#iqm.cirq_iqm.serialize.deserialize_circuit "iqm.cirq_iqm.serialize.deserialize_circuit")(circuit) | Deserializes a quantum circuit from the IQM data transfer format to a Cirq Circuit. |
| [`operation_to_circuit_operation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.operation_to_circuit_operation.html#iqm.cirq_iqm.serialize.operation_to_circuit_operation "iqm.cirq_iqm.serialize.operation_to_circuit_operation")(operation) | Map a Cirq Operation to the IQM data transfer format. |
| [`serialize_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.serialize_circuit.html#iqm.cirq_iqm.serialize.serialize_circuit "iqm.cirq_iqm.serialize.serialize_circuit")(circuit) | Serializes a quantum circuit into the IQM data transfer format. |

Exceptions

|  |  |
|----|----|
| [`OperationNotSupportedError`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.serialize.OperationNotSupportedError.html#iqm.cirq_iqm.serialize.OperationNotSupportedError "iqm.cirq_iqm.serialize.OperationNotSupportedError") | Raised when a given operation is not supported by the IQM Server. |
