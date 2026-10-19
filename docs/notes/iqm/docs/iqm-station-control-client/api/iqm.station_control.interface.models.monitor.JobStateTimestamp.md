> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.JobStateTimestamp.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.JobStateTimestamp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 edeae2fab56fa9d65b1d9901548fd535d1150270dafa1bf7897935b09fe26489.

# JobStateTimestamp

Module: [`iqm.station_control.interface.models.monitor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.html#module-iqm.station_control.interface.models.monitor "iqm.station_control.interface.models.monitor")

*class* JobStateTimestamp(*\**, *job_id*, *status*, *timestamp*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Represents a single timestamped state for a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.monitor.JobStateTimestamp.model_config "iqm.station_control.interface.models.monitor.JobStateTimestamp.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `job_id` |  |
| `status` |  |
| `timestamp` |  |

Methods

Parameters:  
- **job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **status** ([*JobExecutorStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus"))

- **timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.monitor.JobStateTimestamp](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-1a2fbb1cac0b1b75b5e600cf3806d66594bbd6f3.png)
