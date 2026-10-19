> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qir_utils.generate_qiskit_qir_qubit_mapping.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qir_utils.generate_qiskit_qir_qubit_mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c67e37cda0f5f0ded80b3c0c7ed4cab09b25598ac7e94930624a7486ee93237.

# iqm.qiskit_iqm.qir_utils.generate_qiskit_qir_qubit_mapping

iqm.qiskit_iqm.qir_utils.generate_qiskit_qir_qubit_mapping(*qiskit_circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *qiskit_backend: [BackendV2](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.BackendV2 "(in Qiskit v2.5)")*) → WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\]  
Generate qubit mapping for QIR.

`qiskit-qir` has a bug, which causes qubit pointers to not be generated correctly according to the final_layout. So we replicate this logic here and generate a new mapping. Then we assign `qiskit-qir` index to the qiskit logic qubit idx.

Parameters:  
- **qiskit_circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The Qiskit circuit to generate the mapping for.

- **qiskit_backend** ([*BackendV2*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.BackendV2 "(in Qiskit v2.5)")) – The Qiskit backend object to be used for qubit name generation.

Returns:  
A dictionary mapping Qiskit qubit indices to QIR qubit pointers.

Return type:  
[*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], *BeforeValidator*(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping, json_schema_input_type=PydanticUndefined), *PlainSerializer*(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping, return_type=PydanticUndefined, when_used=always), *WithJsonSchema*(json_schema={‘anyOf’: \[{‘type’: ‘array’, ‘items’: {‘type’: ‘object’, ‘required’: \[‘logical_name’, ‘physical_name’\], ‘properties’: {‘logical_name’: {‘type’: ‘string’}, ‘physical_name’: {‘type’: ‘string’}}, ‘additionalProperties’: False}}, {‘type’: ‘null’}\]}, mode=None)\]
