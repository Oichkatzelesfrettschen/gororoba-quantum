> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_qubit_mapping.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_qubit_mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 66c5debeeeacd30275d765c32e76ffeac811a967943b24d634a4b89314122123.

# iqm.iqm_client.validation.validate_qubit_mapping

iqm.iqm_client.validation.validate_qubit_mapping(*architecture: DynamicQuantumArchitecture*, *circuits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") \| \_Circuit \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate the given qubit mapping.

Parameters:  
- **architecture** (*DynamicQuantumArchitecture*) – Quantum architecture to check against.

- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") *\|* *\_Circuit* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Circuits to be checked.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if all `circuits` already use physical qubit names. Note that the `qubit_mapping` is used for all `circuits`.

Raises:  
**CircuitValidationError** – There was something wrong with `circuits`.

Return type:  
None
