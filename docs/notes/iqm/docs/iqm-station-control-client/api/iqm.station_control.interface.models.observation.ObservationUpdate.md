> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationUpdate.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationUpdate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f6a490d7adcc94ed2bac32e104aedc97ae1e4f541cd99fe7f37ac012a21a4780.

# ObservationUpdate

Module: [`iqm.station_control.interface.models.observation`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.html#module-iqm.station_control.interface.models.observation "iqm.station_control.interface.models.observation")

*class* ObservationUpdate(*\**, *observation_id*, *invalid*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

The observation data to be updated in the database.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation.ObservationUpdate.model_config "iqm.station_control.interface.models.observation.ObservationUpdate.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_id`](#iqm.station_control.interface.models.observation.ObservationUpdate.observation_id "iqm.station_control.interface.models.observation.ObservationUpdate.observation_id") | Unique identifier of the observation. |
| [`invalid`](#iqm.station_control.interface.models.observation.ObservationUpdate.invalid "iqm.station_control.interface.models.observation.ObservationUpdate.invalid") | Flag indicating if the observation is invalid. |

Methods

Parameters:  
- **observation_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'forbid', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

observation_id*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Unique identifier of the observation.

invalid*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Flag indicating if the observation is invalid. Automated systems must not use invalid observations.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation.ObservationUpdate](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-4b956ff5be8581865e30994875e99e030e20c42b.png)
