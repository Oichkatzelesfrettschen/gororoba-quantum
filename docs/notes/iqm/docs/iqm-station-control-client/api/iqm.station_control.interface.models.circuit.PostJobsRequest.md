> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5907b4b96a2ffdc2682530b63d2986ed20ca00af64c384e4a32a01c0cfdba322.

# PostJobsRequest

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* PostJobsRequest(*\**, *circuits*, *calibration_set_id=None*, *qubit_mapping=None*, *shots=1*, *max_circuit_duration_over_t2=None*, *heralding_mode=HeraldingMode.NONE*, *move_gate_validation=MoveGateValidationMode.STRICT*, *move_gate_frame_tracking=MoveGateFrameTrackingMode.FULL*, *active_reset_cycles=None*, *dd_mode=DDMode.DISABLED*, *dd_strategy=None*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Request to Station Control run a job that executes a batch of quantum circuits.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.circuit.PostJobsRequest.model_config "iqm.station_control.interface.models.circuit.PostJobsRequest.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `move_gate_frame_tracking_mode` |  |
| `move_validation_mode` |  |
| [`circuits`](#iqm.station_control.interface.models.circuit.PostJobsRequest.circuits "iqm.station_control.interface.models.circuit.PostJobsRequest.circuits") | Batch of quantum circuit(s) to execute. |
| [`calibration_set_id`](#iqm.station_control.interface.models.circuit.PostJobsRequest.calibration_set_id "iqm.station_control.interface.models.circuit.PostJobsRequest.calibration_set_id") | ID of the calibration set to use, or None to use the current default calibration set. |
| [`qubit_mapping`](#iqm.station_control.interface.models.circuit.PostJobsRequest.qubit_mapping "iqm.station_control.interface.models.circuit.PostJobsRequest.qubit_mapping") | Mapping from logical qubit names to physical qubit names, or None if `circuits` use physical qubit names. |
| [`shots`](#iqm.station_control.interface.models.circuit.PostJobsRequest.shots "iqm.station_control.interface.models.circuit.PostJobsRequest.shots") | How many times to execute each circuit in the batch, must be greater than zero. |
| [`max_circuit_duration_over_t2`](#iqm.station_control.interface.models.circuit.PostJobsRequest.max_circuit_duration_over_t2 "iqm.station_control.interface.models.circuit.PostJobsRequest.max_circuit_duration_over_t2") | Circuits are disqualified on the server if they are longer than this fraction of the T2 time of the worst qubit used. |
| [`heralding_mode`](#iqm.station_control.interface.models.circuit.PostJobsRequest.heralding_mode "iqm.station_control.interface.models.circuit.PostJobsRequest.heralding_mode") | Which heralding mode to use during the execution of circuits in this request. |
| [`move_gate_validation`](#iqm.station_control.interface.models.circuit.PostJobsRequest.move_gate_validation "iqm.station_control.interface.models.circuit.PostJobsRequest.move_gate_validation") | Which method of MOVE gate validation to use in circuit compilation. |
| [`move_gate_frame_tracking`](#iqm.station_control.interface.models.circuit.PostJobsRequest.move_gate_frame_tracking "iqm.station_control.interface.models.circuit.PostJobsRequest.move_gate_frame_tracking") | Which method of MOVE gate frame tracking to use for circuit compilation. |
| [`active_reset_cycles`](#iqm.station_control.interface.models.circuit.PostJobsRequest.active_reset_cycles "iqm.station_control.interface.models.circuit.PostJobsRequest.active_reset_cycles") | Number of active `reset` operations inserted at the beginning of each circuit for each active qubit. |
| [`dd_mode`](#iqm.station_control.interface.models.circuit.PostJobsRequest.dd_mode "iqm.station_control.interface.models.circuit.PostJobsRequest.dd_mode") | Whether dynamical decoupling is enabled or disabled during the execution. |
| [`dd_strategy`](#iqm.station_control.interface.models.circuit.PostJobsRequest.dd_strategy "iqm.station_control.interface.models.circuit.PostJobsRequest.dd_strategy") | Dynamical decoupling strategy to be used during the execution, if DD is enabled. |

Methods

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Circuit* *\|* *\_Circuit* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*)

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **max_circuit_duration_over_t2** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*)

- **heralding_mode** ([*HeraldingMode*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.HeraldingMode.html#iqm.station_control.interface.models.circuit.HeraldingMode "iqm.station_control.interface.models.circuit.HeraldingMode"))

- **move_gate_validation** ([*MoveGateValidationMode*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateValidationMode.html#iqm.station_control.interface.models.circuit.MoveGateValidationMode "iqm.station_control.interface.models.circuit.MoveGateValidationMode"))

- **move_gate_frame_tracking** ([*MoveGateFrameTrackingMode*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.html#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode"))

- **active_reset_cycles** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **dd_mode** ([*DDMode*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDMode.html#iqm.station_control.interface.models.circuit.DDMode "iqm.station_control.interface.models.circuit.DDMode"))

- **dd_strategy** ([*DDStrategy*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "iqm.station_control.interface.models.circuit.DDStrategy") *\|* *None*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

circuits*: CircuitBatch*  
Batch of quantum circuit(s) to execute.

calibration_set_id*: UUID \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
ID of the calibration set to use, or None to use the current default calibration set.

qubit_mapping*: QubitMapping \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Mapping from logical qubit names to physical qubit names, or None if `circuits` use physical qubit names.

shots*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
How many times to execute each circuit in the batch, must be greater than zero.

max_circuit_duration_over_t2*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Circuits are disqualified on the server if they are longer than this fraction of the T2 time of the worst qubit used. If set to 0.0, no circuits are disqualified. If set to None the server default value is used.

heralding_mode*: [HeraldingMode](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.HeraldingMode.html#iqm.station_control.interface.models.circuit.HeraldingMode "iqm.station_control.interface.models.circuit.HeraldingMode")*  
Which heralding mode to use during the execution of circuits in this request.

move_gate_validation*: [MoveGateValidationMode](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateValidationMode.html#iqm.station_control.interface.models.circuit.MoveGateValidationMode "iqm.station_control.interface.models.circuit.MoveGateValidationMode")*  
Which method of MOVE gate validation to use in circuit compilation.

move_gate_frame_tracking*: [MoveGateFrameTrackingMode](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.html#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode")*  
Which method of MOVE gate frame tracking to use for circuit compilation.

active_reset_cycles*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Number of active `reset` operations inserted at the beginning of each circuit for each active qubit. `None` means active reset is not used but instead reset is done by waiting (relaxation). Integer values smaller than 1 result in neither active nor reset by wait being used, in which case any reset operations must be explicitly added in the circuit.

dd_mode*: [DDMode](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDMode.html#iqm.station_control.interface.models.circuit.DDMode "iqm.station_control.interface.models.circuit.DDMode")*  
Whether dynamical decoupling is enabled or disabled during the execution.

dd_strategy*: [DDStrategy](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "iqm.station_control.interface.models.circuit.DDStrategy") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Dynamical decoupling strategy to be used during the execution, if DD is enabled. If None, use the server default strategy.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.PostJobsRequest](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-e899f69b9f70ac8aec880f0dab68c913bb545bb1.png)
