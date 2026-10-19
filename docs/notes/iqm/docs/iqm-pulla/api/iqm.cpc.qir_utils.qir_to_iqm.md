> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.qir_utils.qir_to_iqm.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.qir_utils.qir_to_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 294c1e8a4734862c4126d1ed653d30feeac2c38633987a5458519c706d020f66.

# iqm.cpc.qir_utils.qir_to_iqm

iqm.cpc.qir_utils.qir_to_iqm(*compiler*, *qir*, *qubit_mapping=None*)  
Convert a QIR module to an IQM quantum circuit.

Parameters:  
- **compiler** ([*Compiler*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "iqm.cpc.compiler.compiler.Compiler")) – Compiler to use.

- **qir** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")) – QIR source or bitcode to convert to a circuit.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Dictionary mapping QIR qubit indexes to physical qubit names, None will assume opaque pointers match physical names.

Returns:  
Quantum circuits extracted from the QIR module, compiler with updated `component_mapping`.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – The QIR program has more than one basic block.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\], [*Compiler*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "iqm.cpc.compiler.compiler.Compiler")\]
