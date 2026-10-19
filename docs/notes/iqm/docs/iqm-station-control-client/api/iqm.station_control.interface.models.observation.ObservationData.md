> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3c886a5a6ce7426daf3cff93fa5d541c3e0adb5ec276eb17cf94d1e1e2f23997.

# ObservationData

Module: [`iqm.station_control.interface.models.observation`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.html#module-iqm.station_control.interface.models.observation "iqm.station_control.interface.models.observation")

*class* ObservationData(*\**, *dut_field*, *value*, *unit*, *uncertainty=None*, *invalid=False*, *dut_label*, *source*, *tags=\[\]*, *observation_id*, *created_timestamp*, *modified_timestamp*, *observation_set_ids=\[\]*)  
Bases: [`ObservationLite`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html#iqm.station_control.interface.models.observation.ObservationLite "iqm.station_control.interface.models.observation.ObservationLite"), [`ObservationDefinition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "iqm.station_control.interface.models.observation.ObservationDefinition")

The content of the observation stored in the database.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation.ObservationData.model_config "iqm.station_control.interface.models.observation.ObservationData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_set_ids`](#iqm.station_control.interface.models.observation.ObservationData.observation_set_ids "iqm.station_control.interface.models.observation.ObservationData.observation_set_ids") | List of observation set UUIDs this observation belongs to. |
| `observation_id` | Unique identifier of the observation. |
| `created_timestamp` | Time when the object was created in the database. |
| `modified_timestamp` | Time when the object was last modified in the database. |
| `dut_label` | DUT label of the device the observation is about. |
| `source` | How the observation was made, e.g. experiment analysis or manual specification. |
| `tags` | Human-readable tags of the observation. |
| `dut_field` | Name of the property the observation is about. |
| `value` | Value of the observation. |
| `unit` | SI unit of the value. |
| `uncertainty` | Uncertainty of the observation value. |
| `invalid` | Flag indicating if the observation is invalid. |

Methods

|  |  |
|----|----|
| [`from_observation_lite`](#iqm.station_control.interface.models.observation.ObservationData.from_observation_lite "iqm.station_control.interface.models.observation.ObservationData.from_observation_lite") | Create an observation data from an observation lite, using placeholder values for the missing fields. |

Parameters:  
- **dut_field** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **value** (*Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*)

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **uncertainty** (*Annotated\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]* *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **source** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **tags** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **observation_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **modified_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **observation_set_ids** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

observation_set_ids*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")\]*  
List of observation set UUIDs this observation belongs to.

*classmethod* from_observation_lite(*observation*, *dut_label=None*)  
Create an observation data from an observation lite, using placeholder values for the missing fields.

Parameters:  
- **observation** ([*ObservationLite*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html#iqm.station_control.interface.models.observation.ObservationLite "iqm.station_control.interface.models.observation.ObservationLite")) – Lightweight observation to convert.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – DUT label of the device the observation is about. A placeholder is used if not given.

Returns:  
Observation data corresponding to `observation`, with placeholder `dut_label`, `source` and `tags` if not otherwise derivable from `observation`.

Return type:  
[*ObservationData*](#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation.ObservationData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-dc736da1acb53e0bd66662ae26655ee5fda44753.png)
