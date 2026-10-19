> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetUpdate.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetUpdate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f962748af9bfd80311339b7e32500b2fa2b55c23ff321050fbe8adb0b4e4c275.

# ObservationSetUpdate

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* ObservationSetUpdate(*\**, *observation_set_id*, *observation_ids=None*, *invalid*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

The observation set data to be updated in the database.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation_set.ObservationSetUpdate.model_config "iqm.station_control.interface.models.observation_set.ObservationSetUpdate.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_set_id`](#iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_set_id "iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_set_id") | Unique identifier of the observation set. |
| [`observation_ids`](#iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_ids "iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_ids") | Database IDs of the observations belonging to the observation set. |
| [`invalid`](#iqm.station_control.interface.models.observation_set.ObservationSetUpdate.invalid "iqm.station_control.interface.models.observation_set.ObservationSetUpdate.invalid") | Flag indicating if the set is invalid. |

Methods

Parameters:  
- **observation_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **observation_ids** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'forbid', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

observation_set_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the observation set.

observation_ids*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Database IDs of the observations belonging to the observation set.

This will only add new observations to the observation set, deleting existing ones is not possible. Setting this to `None` or omitting it will leave existing [`observation_ids`](#iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_ids "iqm.station_control.interface.models.observation_set.ObservationSetUpdate.observation_ids") as is with no changes.

invalid*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Flag indicating if the set is invalid. Automated systems must not use invalid sets.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.ObservationSetUpdate](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-0c222074019d376b5665d6a06254613b22667532.png)
