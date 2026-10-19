> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.QualityMetrics.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.QualityMetrics.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 11114e48596b22cebf766392c1efdf2f4bdfe68e91f04e576c2182c6df5ca624.

# QualityMetrics

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* QualityMetrics(*\**, *observation_set_type*, *describes_id=None*, *invalid=False*, *dut_label*, *observation_set_id*, *created_timestamp*, *end_timestamp*, *observations*, *calibration_set*)  
Bases: [`ObservationSetWithObservations`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservations.html#iqm.station_control.interface.models.observation_set.ObservationSetWithObservations "iqm.station_control.interface.models.observation_set.ObservationSetWithObservations")

The content of the quality metric set stored in the database, with a list of observations and calibration set.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.observation_set.QualityMetrics.model_config "iqm.station_control.interface.models.observation_set.QualityMetrics.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `calibration_set` |  |
| `dut_label` | String representation of the DUT the observation set is associated with. |
| `observation_set_id` | Unique identifier of the observation set. |
| `created_timestamp` | Time when the object was created in the database. |
| `end_timestamp` | Time when the observation set was finalized. |
| `observations` | Observations belonging to the observation set. |
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

- **observations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ObservationLite*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationLite.html#iqm.station_control.interface.models.observation.ObservationLite "iqm.station_control.interface.models.observation.ObservationLite")*\]*)

- **calibration_set** ([*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "iqm.station_control.interface.models.observation_set.ObservationSetData"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.QualityMetrics](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-f59a185bd6468c2776d6967451ff1ec84aac27b1.png)
