> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6fc7d70e0f5e707a0f16913bde5d42ce80ca12d7cbb809360a717e3c8be9efc7.

# ObservationSetBase

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* ObservationSetBase(*\**, *observation_set_type*, *describes_id=None*, *invalid=False*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Abstract base class of the observation set definition and data.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation_set.ObservationSetBase.model_config "iqm.station_control.interface.models.observation_set.ObservationSetBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_set_type`](#iqm.station_control.interface.models.observation_set.ObservationSetBase.observation_set_type "iqm.station_control.interface.models.observation_set.ObservationSetBase.observation_set_type") | Indicates the type (i.e. purpose) of the observation set. |
| [`describes_id`](#iqm.station_control.interface.models.observation_set.ObservationSetBase.describes_id "iqm.station_control.interface.models.observation_set.ObservationSetBase.describes_id") | Unique identifier of the observation set this observation set describes. |
| [`invalid`](#iqm.station_control.interface.models.observation_set.ObservationSetBase.invalid "iqm.station_control.interface.models.observation_set.ObservationSetBase.invalid") | Flag indicating if the set is invalid. |

Methods

Parameters:  
- **observation_set_type** ([*ObservationSetType*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "iqm.station_control.interface.models.observation_set.ObservationSetType"))

- **describes_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

observation_set_type*: [ObservationSetType](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "iqm.station_control.interface.models.observation_set.ObservationSetType")*  
Indicates the type (i.e. purpose) of the observation set.

describes_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Unique identifier of the observation set this observation set describes.

invalid*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Flag indicating if the set is invalid. Automated systems must not use invalid sets.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.ObservationSetBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-345bb8c7557809c1d05632987e95c4d3972541ee.png)
