> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.TimelineEntry.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.TimelineEntry.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f950583040fbde15a0c4671b8890947dd9f2e170e6532b0c4259866d8340926b.

# TimelineEntry

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* TimelineEntry(*\**, *source*, *status*, *timestamp*)  
Bases: `BaseModel`

Timeline entry for a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.TimelineEntry.model_config "iqm.station_control.interface.models.jobs_new.TimelineEntry.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`source`](#iqm.station_control.interface.models.jobs_new.TimelineEntry.source "iqm.station_control.interface.models.jobs_new.TimelineEntry.source") | Source of the timeline entry. |
| [`status`](#iqm.station_control.interface.models.jobs_new.TimelineEntry.status "iqm.station_control.interface.models.jobs_new.TimelineEntry.status") | Name of the execution step that was reached. |
| [`timestamp`](#iqm.station_control.interface.models.jobs_new.TimelineEntry.timestamp "iqm.station_control.interface.models.jobs_new.TimelineEntry.timestamp") | Time at which `status` was reached. |

Methods

Parameters:  
- **source** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['iqm-server',* *'iqm-station-control'\]* *\|* *str*)

- **status** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

source*: Source*  
Source of the timeline entry.

status*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the execution step that was reached.

timestamp*: datetime*  
Time at which `status` was reached.

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.TimelineEntry](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-980d46159697dc0ce368a03c0f4c2f2644a7a53c.png)
