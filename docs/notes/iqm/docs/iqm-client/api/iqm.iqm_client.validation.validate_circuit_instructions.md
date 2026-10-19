> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_circuit_instructions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_circuit_instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c13dee69f0f690d175c84b773c69c3e95f196ea77d726b15f62791fc964a58eb.

# iqm.iqm_client.validation.validate_circuit_instructions

iqm.iqm_client.validation.validate_circuit_instructions(*architecture: DynamicQuantumArchitecture*, *circuits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") \| \_Circuit \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*, *validate_moves: MoveGateValidationMode = MoveGateValidationMode.STRICT*, *\**, *must_close_sandwiches: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate the given circuits against the given quantum architecture.

Parameters:  
- **architecture** (*DynamicQuantumArchitecture*) – Quantum architecture to check against.

- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") *\|* *\_Circuit* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Circuits to be checked.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if all `circuits` already use physical qubit names. Note that the `qubit_mapping` is used for all `circuits`.

- **validate_moves** (*MoveGateValidationMode*) – Determines how MOVE gate validation works.

- **must_close_sandwiches** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, MOVE sandwiches cannot be left open when the circuit ends.

Raises:  
**CircuitValidationError** – validation failed

Return type:  
None
