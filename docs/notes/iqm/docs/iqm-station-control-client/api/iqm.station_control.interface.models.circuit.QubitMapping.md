> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.QubitMapping.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.QubitMapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 86ef712a88417db0f11b145c2bed38a8e8b79480d4475ae0dd3abfc219ae42b1.

# QubitMapping

QubitMapping  
Mapping from logical qubit names to physical qubit names.

alias of `Annotated`\[[`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], `BeforeValidator`(func=`_parse_legacy_qubit_mapping`, json_schema_input_type=PydanticUndefined), `PlainSerializer`(func=`_serialize_as_legacy_qubit_mapping`, return_type=PydanticUndefined, when_used=always), `WithJsonSchema`(json_schema={‘anyOf’: \[{‘items’: {‘additionalProperties’: False, ‘properties’: {‘logical_name’: {‘type’: ‘string’}, ‘physical_name’: {‘type’: ‘string’}}, ‘required’: \[‘logical_name’, ‘physical_name’\], ‘type’: ‘object’}, ‘type’: ‘array’}, {‘type’: ‘null’}\]}, mode=[`None`](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)"))\]
