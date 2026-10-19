> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2fa1f0873c83019a2a539dee729d09f36aeef6d78e3cf9468fb20849eb20785e.

# ObservationLite

Module: [`iqm.station_control.interface.models.observation`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.html#module-iqm.station_control.interface.models.observation "iqm.station_control.interface.models.observation")

*class* ObservationLite(*\**, *dut_field*, *value*, *unit*, *uncertainty=None*, *invalid=False*, *observation_id*, *created_timestamp*, *modified_timestamp*)  
Bases: [`ObservationBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html#iqm.station_control.interface.models.observation.ObservationBase "iqm.station_control.interface.models.observation.ObservationBase")

The lightweight version of the observation data.

This model can be used when not all observation data is needed, to speed up retrieval.

Deprecated:  
Direct instantiation is deprecated since 2026-08-31, use [`ObservationData`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData") instead. Subclasses of `ObservationLite`, such as [`ObservationData`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData"), are unaffected.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation.ObservationLite.model_config "iqm.station_control.interface.models.observation.ObservationLite.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_id`](#iqm.station_control.interface.models.observation.ObservationLite.observation_id "iqm.station_control.interface.models.observation.ObservationLite.observation_id") | Unique identifier of the observation. |
| [`created_timestamp`](#iqm.station_control.interface.models.observation.ObservationLite.created_timestamp "iqm.station_control.interface.models.observation.ObservationLite.created_timestamp") | Time when the object was created in the database. |
| [`modified_timestamp`](#iqm.station_control.interface.models.observation.ObservationLite.modified_timestamp "iqm.station_control.interface.models.observation.ObservationLite.modified_timestamp") | Time when the object was last modified in the database. |
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

- **observation_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **modified_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

observation_id*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Unique identifier of the observation.

created_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was created in the database.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

modified_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was last modified in the database.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation.ObservationLite](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a92f49f5afb5ebc562fa35d6d9c0d880812d3880.png)
