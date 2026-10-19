> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 357c1e1a77037cdd446c520f004db12f25006d91071f52b7adbb114e6d5f4071.

# ObservationSetWithObservationData

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* ObservationSetWithObservationData(*\**, *observation_set_type*, *describes_id=None*, *invalid=False*, *dut_label*, *observation_set_id*, *created_timestamp*, *end_timestamp*, *observations*)  
Bases: [`ObservationSetBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetBase.html#iqm.station_control.interface.models.observation_set.ObservationSetBase "iqm.station_control.interface.models.observation_set.ObservationSetBase")

The content of the observation set stored in the database, with a list of full observation data.

Unlike [`ObservationSetWithObservations`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservations.html#iqm.station_control.interface.models.observation_set.ObservationSetWithObservations "iqm.station_control.interface.models.observation_set.ObservationSetWithObservations"), which carries the lightweight [`ObservationLite`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html#iqm.station_control.interface.models.observation.ObservationLite "iqm.station_control.interface.models.observation.ObservationLite") shape used internally, this is the shape exposed by [`StorageInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "iqm.station_control.interface.storage_interface.StorageInterface") to its callers.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.model_config "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`observation_ids`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observation_ids "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observation_ids") | Database IDs of the observations belonging to the observation set. |
| [`dut_label`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.dut_label "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.dut_label") | String representation of the DUT the observation set is associated with. |
| [`observation_set_id`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observation_set_id "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observation_set_id") | Unique identifier of the observation set. |
| [`created_timestamp`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.created_timestamp "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.created_timestamp") | Time when the object was created in the database. |
| [`end_timestamp`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.end_timestamp "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.end_timestamp") | Time when the observation set was finalized. |
| [`observations`](#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observations "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.observations") | Observations belonging to the observation set. |
| `observation_set_type` | Indicates the type (i.e. purpose) of the observation set. |
| `describes_id` | Unique identifier of the observation set this observation set describes. |
| `invalid` | Flag indicating if the set is invalid. |

Methods

Parameters:  
- **observation_set_type** ([*ObservationSetType*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "iqm.station_control.interface.models.observation_set.ObservationSetType"))

- **describes_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **observation_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **end_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") *\|* *None*)

- **observations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
String representation of the DUT the observation set is associated with. Can only be None for generic sets.

observation_set_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the observation set.

created_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was created in the database.

end_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Time when the observation set was finalized. If `None`, the set is not finalized yet.

observations*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ObservationData](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")\]*  
Observations belonging to the observation set.

*property* observation_ids*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Database IDs of the observations belonging to the observation set.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-5e33b8bb88160a475b23a0d02b7e8e165a61ac86.png)
