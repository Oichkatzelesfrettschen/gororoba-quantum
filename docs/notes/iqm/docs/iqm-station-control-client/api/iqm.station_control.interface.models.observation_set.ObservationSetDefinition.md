> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dd88964ddf68e7b16f8f407807986958ca75b6fe7bf48299a482fab7f0960522.

# ObservationSetDefinition

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* ObservationSetDefinition(*\**, *observation_set_type*, *describes_id=None*, *invalid=False*, *observation_ids*)  
Bases: [`ObservationSetBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetBase.html#iqm.station_control.interface.models.observation_set.ObservationSetBase "iqm.station_control.interface.models.observation_set.ObservationSetBase")

The content of the observation set object when creating it.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation_set.ObservationSetDefinition.model_config "iqm.station_control.interface.models.observation_set.ObservationSetDefinition.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_ids`](#iqm.station_control.interface.models.observation_set.ObservationSetDefinition.observation_ids "iqm.station_control.interface.models.observation_set.ObservationSetDefinition.observation_ids") | Database IDs of the observations belonging to the observation set. |
| `observation_set_type` | Indicates the type (i.e. purpose) of the observation set. |
| `describes_id` | Unique identifier of the observation set this observation set describes. |
| `invalid` | Flag indicating if the set is invalid. |

Methods

Parameters:  
- **observation_set_type** ([*ObservationSetType*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "iqm.station_control.interface.models.observation_set.ObservationSetType"))

- **describes_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **observation_ids** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

observation_ids*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Database IDs of the observations belonging to the observation set.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'forbid', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.ObservationSetDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-3241e9c00b28c0bff554064c9348ad23079d2c27.png)
