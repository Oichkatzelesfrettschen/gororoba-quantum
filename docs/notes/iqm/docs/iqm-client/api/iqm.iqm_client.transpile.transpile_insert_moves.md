> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 af329b47e737ffb02e499b92a8c849a8c12fcec491edca974119b9b8f99ccadc.

# iqm.iqm_client.transpile.transpile_insert_moves

iqm.iqm_client.transpile.transpile_insert_moves(*circuit: [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*, *arch: DynamicQuantumArchitecture*, *\**, *existing_moves: [ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") = ExistingMoveHandlingOptions.KEEP*, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*, *restore_states: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")  
Convert a simplified architecture circuit into an equivalent Star architecture circuit.

Adds resonators and MOVE gates, if needed. In the typical use case `circuit` has been transpiled to a simplified architecture where the resonators have been abstracted away, and this function converts it into the corresponding Star architecture circuit.

It can also handle the case where `circuit` already contains MOVE gates and resonators, which are treated according to `existing_moves`, followed by the conversion of the two-qubit gates that are not supported by the Star architecture.

The function does nothing if `arch` does not support MOVE gates.

Parameters:  
- **circuit** ([*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")) – The circuit to convert.

- **arch** (*DynamicQuantumArchitecture*) – Real Star architecture of the target device.

- **existing_moves** ([*ExistingMoveHandlingOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions")) – Specifies how to deal with existing MOVE instructions in `circuit`, if any.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if `circuit` already uses physical qubit names.

- **restore_states** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, all qubit states held in resonators are returned to their qubits at the end of the circuit (i.e. all MOVE sandwiches are closed), even when there is no computational reason to do so.

Returns:  
Equivalent Star architecture circuit with MOVEs and resonators added.

Return type:  
[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")
