> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobResult.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26f404b211472d3ed6f1c57c1cf8e82e3b8c44e508733d5803e6233c06176cdb.

# JobResult

Module: [`iqm.station_control.interface.models.jobs`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html#module-iqm.station_control.interface.models.jobs "iqm.station_control.interface.models.jobs")

*class* JobResult(*\**, *job_id*, *parallel_sweep_progress*, *interrupted*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Progress information for the JobExecutorStatus.EXECUTION_STARTED stage of a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs.JobResult.model_config "iqm.station_control.interface.models.jobs.JobResult.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`job_id`](#iqm.station_control.interface.models.jobs.JobResult.job_id "iqm.station_control.interface.models.jobs.JobResult.job_id") | ID of the job. |
| [`parallel_sweep_progress`](#iqm.station_control.interface.models.jobs.JobResult.parallel_sweep_progress "iqm.station_control.interface.models.jobs.JobResult.parallel_sweep_progress") | Progress of the sweeps if we are in the JobExecutorStatus.EXECUTION_STARTED stage, otherwise empty. |
| [`interrupted`](#iqm.station_control.interface.models.jobs.JobResult.interrupted "iqm.station_control.interface.models.jobs.JobResult.interrupted") | True iff the job was canceled. |

Methods

Parameters:  
- **job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **parallel_sweep_progress** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **interrupted** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

job_id*: UUID*  
ID of the job.

parallel_sweep_progress*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[\_Progress\]*  
Progress of the sweeps if we are in the JobExecutorStatus.EXECUTION_STARTED stage, otherwise empty.

interrupted*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
True iff the job was canceled.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs.JobResult](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-e33f1bcb29b322bf4c1e561f7b7e6547aaba00dc.png)
