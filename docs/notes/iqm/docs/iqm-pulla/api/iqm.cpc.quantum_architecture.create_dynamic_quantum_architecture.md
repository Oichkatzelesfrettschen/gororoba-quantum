> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.quantum_architecture.create_dynamic_quantum_architecture.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.quantum_architecture.create_dynamic_quantum_architecture.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d7e1f4a9651029b61b30405c468879776d9c4d32d6c4d09d5e4c5a1de91043e2.

# iqm.cpc.quantum_architecture.create_dynamic_quantum_architecture

iqm.cpc.quantum_architecture.create_dynamic_quantum_architecture(*calibration_set_id*, *observations*, *chip_topology*)  
Create a dynamic quantum architecture (DQA) for the given calibration set.

Has deprecated support for old-style calibration sets without default implementation observations.

Parameters:  
- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the calibration set used to create the DQA.

- **observations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]\]*) – Contents of the calibration set used to create the DQA.

- **chip_topology** ([*ChipTopology*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)")) – Topology of the QPU the calibration set is for.

Returns:  
Dynamic quantum architecture containing information about calibrated operations.

Return type:  
[*DynamicQuantumArchitecture*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.html#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture "(in iqm-station-control-client v14.0.0)")
