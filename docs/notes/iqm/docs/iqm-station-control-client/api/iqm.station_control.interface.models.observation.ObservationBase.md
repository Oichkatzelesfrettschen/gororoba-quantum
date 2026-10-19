> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c58dc06da87892bdfba9473f58e9033503cd43a7dd244a75aa67c089afcc2567.

# ObservationBase

Module: [`iqm.station_control.interface.models.observation`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.html#module-iqm.station_control.interface.models.observation "iqm.station_control.interface.models.observation")

*class* ObservationBase(*\**, *dut_field*, *value*, *unit*, *uncertainty=None*, *invalid=False*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Abstract base class of the observation models.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation.ObservationBase.model_config "iqm.station_control.interface.models.observation.ObservationBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`dut_field`](#iqm.station_control.interface.models.observation.ObservationBase.dut_field "iqm.station_control.interface.models.observation.ObservationBase.dut_field") | Name of the property the observation is about. |
| [`value`](#iqm.station_control.interface.models.observation.ObservationBase.value "iqm.station_control.interface.models.observation.ObservationBase.value") | Value of the observation. |
| [`unit`](#iqm.station_control.interface.models.observation.ObservationBase.unit "iqm.station_control.interface.models.observation.ObservationBase.unit") | SI unit of the value. |
| [`uncertainty`](#iqm.station_control.interface.models.observation.ObservationBase.uncertainty "iqm.station_control.interface.models.observation.ObservationBase.uncertainty") | Uncertainty of the observation value. |
| [`invalid`](#iqm.station_control.interface.models.observation.ObservationBase.invalid "iqm.station_control.interface.models.observation.ObservationBase.invalid") | Flag indicating if the observation is invalid. |

Methods

Parameters:  
- **dut_field** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **value** (*Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*)

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **uncertainty** (*Annotated\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]* *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

dut_field*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the property the observation is about.

value*: WithJsonSchema(json_schema={}, mode=None)\]*  
Value of the observation.

unit*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
SI unit of the value. Empty string means the value is dimensionless.

uncertainty*: WithJsonSchema(json_schema={}, mode=None)\] \| None*  
Uncertainty of the observation value. `None` means unknown.

invalid*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Flag indicating if the observation is invalid. Automated systems must not use invalid observations.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation.ObservationBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-9543ca1b460f87a6afe95491f5f708a02098eb9a.png)
