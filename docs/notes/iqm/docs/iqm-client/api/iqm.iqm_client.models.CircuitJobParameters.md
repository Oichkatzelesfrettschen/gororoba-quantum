> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitJobParameters.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitJobParameters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf760cf2a9485cf92df040caf427c5b41caefb28e97d91f72cf58026669c2427.

# CircuitJobParameters

Module: [`iqm.iqm_client.models`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.html#module-iqm.iqm_client.models "iqm.iqm_client.models")

*class* iqm.iqm_client.models.CircuitJobParameters(*max_circuit_duration_over_t2: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *heralding_mode: HeraldingMode = HeraldingMode.NONE*, *move_gate_validation: MoveGateValidationMode = MoveGateValidationMode.STRICT*, *move_gate_frame_tracking: MoveGateFrameTrackingMode = MoveGateFrameTrackingMode.FULL*, *active_reset_cycles: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *dd_mode: DDMode = DDMode.DISABLED*, *dd_strategy: DDStrategy \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*)  
Bases: [`CircuitCompilationOptions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions")

Parameters for a circuit execution job (see `CircuitJobDefinition` for definitions).

Attributes

|  |  |
|----|----|
| [`calibration_set_id`](#iqm.iqm_client.models.CircuitJobParameters.calibration_set_id "iqm.iqm_client.models.CircuitJobParameters.calibration_set_id") | ID of the calibration set to use, or None to use the current default calibration set. |
| [`qubit_mapping`](#iqm.iqm_client.models.CircuitJobParameters.qubit_mapping "iqm.iqm_client.models.CircuitJobParameters.qubit_mapping") | Mapping of logical qubit names to physical qubit names, or None if `circuits` use physical qubit names. |
| [`shots`](#iqm.iqm_client.models.CircuitJobParameters.shots "iqm.iqm_client.models.CircuitJobParameters.shots") | How many times to execute each circuit in the batch, must be greater than zero. |

Methods

Parameters:  
- **max_circuit_duration_over_t2** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*)

- **heralding_mode** (*HeraldingMode*)

- **move_gate_validation** (*MoveGateValidationMode*)

- **move_gate_frame_tracking** (*MoveGateFrameTrackingMode*)

- **active_reset_cycles** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **dd_mode** (*DDMode*)

- **dd_strategy** (*DDStrategy* *\|* *None*)

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*)

shots*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
How many times to execute each circuit in the batch, must be greater than zero.

calibration_set_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
ID of the calibration set to use, or None to use the current default calibration set.

qubit_mapping*: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None* *= None*  
Mapping of logical qubit names to physical qubit names, or None if `circuits` use physical qubit names.

Inheritance

![Inheritance diagram of iqm.iqm_client.models.CircuitJobParameters](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-f71f150a952dbdfa5a1f32272b0f1c1030a158b1.png)
