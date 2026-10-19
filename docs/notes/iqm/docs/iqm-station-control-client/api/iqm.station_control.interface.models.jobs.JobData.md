> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cde25ab3e44e5394ab5bdfae6ea64d3b08b09b23fad6409e0142b04e46a4c5c6.

# JobData

Module: [`iqm.station_control.interface.models.jobs`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html#module-iqm.station_control.interface.models.jobs "iqm.station_control.interface.models.jobs")

*class* JobData(*\**, *job_id*, *job_status*, *job_result*, *job_error*, *position*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Status, artifacts and metadata of a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs.JobData.model_config "iqm.station_control.interface.models.jobs.JobData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`job_id`](#iqm.station_control.interface.models.jobs.JobData.job_id "iqm.station_control.interface.models.jobs.JobData.job_id") | Unique ID of the job. |
| [`job_status`](#iqm.station_control.interface.models.jobs.JobData.job_status "iqm.station_control.interface.models.jobs.JobData.job_status") | Current job status. |
| [`job_result`](#iqm.station_control.interface.models.jobs.JobData.job_result "iqm.station_control.interface.models.jobs.JobData.job_result") | Progress information for the JobExecutorStatus.EXECUTION_STARTED stage of a job. |
| [`job_error`](#iqm.station_control.interface.models.jobs.JobData.job_error "iqm.station_control.interface.models.jobs.JobData.job_error") | Error message(s) for a failed job, otherwise None. |
| [`position`](#iqm.station_control.interface.models.jobs.JobData.position "iqm.station_control.interface.models.jobs.JobData.position") | Number of jobs ahead of this job in its current queue. |

Methods

Parameters:  
- **job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **job_status** ([*JobExecutorStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus"))

- **job_result** ([*JobResult*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobResult.html#iqm.station_control.interface.models.jobs.JobResult "iqm.station_control.interface.models.jobs.JobResult"))

- **job_error** ([*JobError*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobError.html#iqm.station_control.interface.models.jobs.JobError "iqm.station_control.interface.models.jobs.JobError") *\|* *None*)

- **position** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

job_id*: UUID*  
Unique ID of the job.

job_status*: [JobExecutorStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus")*  
Current job status.

job_result*: [JobResult](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobResult.html#iqm.station_control.interface.models.jobs.JobResult "iqm.station_control.interface.models.jobs.JobResult")*  
Progress information for the JobExecutorStatus.EXECUTION_STARTED stage of a job.

job_error*: [JobError](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobError.html#iqm.station_control.interface.models.jobs.JobError "iqm.station_control.interface.models.jobs.JobError") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Error message(s) for a failed job, otherwise None.

position*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Number of jobs ahead of this job in its current queue. None means the job has reached a terminal status.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs.JobData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-d8795740949c632b0ce6d1527635299a800b02d8.png)
