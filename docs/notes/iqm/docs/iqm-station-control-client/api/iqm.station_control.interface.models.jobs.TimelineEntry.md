> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.TimelineEntry.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.TimelineEntry.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 326729753fdc5d8eb5e4c73c6f68d34f974822dbebf3f573be78921fffbc2a95.

# TimelineEntry

Module: [`iqm.station_control.interface.models.jobs`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html#module-iqm.station_control.interface.models.jobs "iqm.station_control.interface.models.jobs")

*class* TimelineEntry(*\**, *status*, *timestamp*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Status and timestamp pair for a job timeline.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs.TimelineEntry.model_config "iqm.station_control.interface.models.jobs.TimelineEntry.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`status`](#iqm.station_control.interface.models.jobs.TimelineEntry.status "iqm.station_control.interface.models.jobs.TimelineEntry.status") | Job status that was reached. |
| [`timestamp`](#iqm.station_control.interface.models.jobs.TimelineEntry.timestamp "iqm.station_control.interface.models.jobs.TimelineEntry.timestamp") | Time at which `status` was reached. |

Methods

Parameters:  
- **status** ([*JobExecutorStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus"))

- **timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

status*: [JobExecutorStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus")*  
Job status that was reached.

timestamp*: datetime*  
Time at which `status` was reached.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs.TimelineEntry](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-c7b16153130a3ef32013068750088c77b9cbd583.png)
