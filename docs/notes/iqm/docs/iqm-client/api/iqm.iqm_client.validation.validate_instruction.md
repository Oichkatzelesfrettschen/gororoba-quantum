> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_instruction.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_instruction.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e2e44b64867a7584ed69cccd7ef0c46f6b80cc853cb4cba0f1842c6a8bb5c2fb.

# iqm.iqm_client.validation.validate_instruction

iqm.iqm_client.validation.validate_instruction(*architecture: DynamicQuantumArchitecture*, *instruction: [CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate an instruction against the dynamic quantum architecture.

Checks that the instruction uses a valid implementation, and targets a valid locus.

Parameters:  
- **architecture** (*DynamicQuantumArchitecture*) – Quantum architecture to check against.

- **instruction** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")) – Instruction to check.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if `instruction` already uses physical qubit names.

Raises:  
**CircuitValidationError** – validation failed

Return type:  
None
