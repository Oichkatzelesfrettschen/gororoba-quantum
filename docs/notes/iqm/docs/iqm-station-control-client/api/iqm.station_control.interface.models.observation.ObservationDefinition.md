> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad412e544ee3e4c99c5a28b6f9b4df55c09111f756eb69e4fb285e275e9a48cd.

# ObservationDefinition

Module: [`iqm.station_control.interface.models.observation`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.html#module-iqm.station_control.interface.models.observation "iqm.station_control.interface.models.observation")

*class* ObservationDefinition(*\**, *dut_field*, *value*, *unit*, *uncertainty=None*, *invalid=False*, *dut_label*, *source*, *tags=\[\]*)  
Bases: [`ObservationBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html#iqm.station_control.interface.models.observation.ObservationBase "iqm.station_control.interface.models.observation.ObservationBase")

The content of the observation definition.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation.ObservationDefinition.model_config "iqm.station_control.interface.models.observation.ObservationDefinition.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`dut_label`](#iqm.station_control.interface.models.observation.ObservationDefinition.dut_label "iqm.station_control.interface.models.observation.ObservationDefinition.dut_label") | DUT label of the device the observation is about. |
| [`source`](#iqm.station_control.interface.models.observation.ObservationDefinition.source "iqm.station_control.interface.models.observation.ObservationDefinition.source") | How the observation was made, e.g. experiment analysis or manual specification. |
| [`tags`](#iqm.station_control.interface.models.observation.ObservationDefinition.tags "iqm.station_control.interface.models.observation.ObservationDefinition.tags") | Human-readable tags of the observation. |
| `dut_field` | Name of the property the observation is about. |
| `value` | Value of the observation. |
| `unit` | SI unit of the value. |
| `uncertainty` | Uncertainty of the observation value. |
| `invalid` | Flag indicating if the observation is invalid. |

Methods

Parameters:  
- **dut_field** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **value** (*Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*)

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **uncertainty** (*Annotated\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]* *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **source** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **tags** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT label of the device the observation is about.

source*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
How the observation was made, e.g. experiment analysis or manual specification. `source` always has the key `"type"` whose `str` value determines the other contents of the dict. The currently supported source types are: - analysis_source - configuration_source - measurement_source - sequence_analysis_source - specification_source

tags*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Human-readable tags of the observation.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation.ObservationDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-93449241b88292131a2a05d5d32c949f691be5dd.png)
