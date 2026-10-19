> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a7995a56df3dd30f956558ad5058cb3796b0734ca26243f326177c21f230a4f4.

# JobData

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobData(*\**, *id*, *type*, *status*, *execution=None*, *compilation=None*, *messages=\[\]*, *errors=\[\]*, *queue_position=None*, *timeline=\[\]*, *artifacts=\[\]*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Status, lightweight artifacts and metadata of a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.JobData.model_config "iqm.station_control.interface.models.jobs_new.JobData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`id`](#iqm.station_control.interface.models.jobs_new.JobData.id "iqm.station_control.interface.models.jobs_new.JobData.id") | Unique ID of the job. |
| [`type`](#iqm.station_control.interface.models.jobs_new.JobData.type "iqm.station_control.interface.models.jobs_new.JobData.type") | What kind of job it is. |
| [`status`](#iqm.station_control.interface.models.jobs_new.JobData.status "iqm.station_control.interface.models.jobs_new.JobData.status") | Current job status. |
| [`execution`](#iqm.station_control.interface.models.jobs_new.JobData.execution "iqm.station_control.interface.models.jobs_new.JobData.execution") | Execution information for the job. |
| [`compilation`](#iqm.station_control.interface.models.jobs_new.JobData.compilation "iqm.station_control.interface.models.jobs_new.JobData.compilation") | Compilation information for the job. |
| [`messages`](#iqm.station_control.interface.models.jobs_new.JobData.messages "iqm.station_control.interface.models.jobs_new.JobData.messages") | Informational messages for the job. |
| [`errors`](#iqm.station_control.interface.models.jobs_new.JobData.errors "iqm.station_control.interface.models.jobs_new.JobData.errors") | Errors for a failed job. |
| [`queue_position`](#iqm.station_control.interface.models.jobs_new.JobData.queue_position "iqm.station_control.interface.models.jobs_new.JobData.queue_position") | Iff the status is JobStatus.WAITING, the number of jobs ahead of this job in the queue. |
| [`timeline`](#iqm.station_control.interface.models.jobs_new.JobData.timeline "iqm.station_control.interface.models.jobs_new.JobData.timeline") | Server-side statuses reached by the job so far. |
| [`artifacts`](#iqm.station_control.interface.models.jobs_new.JobData.artifacts "iqm.station_control.interface.models.jobs_new.JobData.artifacts") | Generated artifacts that represent the output of the job. |

Methods

Parameters:  
- **id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **type** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['run',* *'circuit'\]*)

- **status** ([*JobStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus"))

- **execution** ([*JobExecution*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobExecution.html#iqm.station_control.interface.models.jobs_new.JobExecution "iqm.station_control.interface.models.jobs_new.JobExecution") *\|* *None*)

- **compilation** ([*JobCompilation*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobCompilation.html#iqm.station_control.interface.models.jobs_new.JobCompilation "iqm.station_control.interface.models.jobs_new.JobCompilation") *\|* *None*)

- **messages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*JobMessage*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobMessage.html#iqm.station_control.interface.models.jobs_new.JobMessage "iqm.station_control.interface.models.jobs_new.JobMessage")*\]*)

- **errors** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMServerError*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError")*\]*)

- **queue_position** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **timeline** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TimelineEntry*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.TimelineEntry.html#iqm.station_control.interface.models.jobs_new.TimelineEntry "iqm.station_control.interface.models.jobs_new.TimelineEntry")*\]*)

- **artifacts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*JobArtifactInfo*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobArtifactInfo.html#iqm.station_control.interface.models.jobs_new.JobArtifactInfo "iqm.station_control.interface.models.jobs_new.JobArtifactInfo")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

id*: UUID*  
Unique ID of the job.

type*: JobType*  
What kind of job it is.

status*: [JobStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus")*  
Current job status.

execution*: [JobExecution](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobExecution.html#iqm.station_control.interface.models.jobs_new.JobExecution "iqm.station_control.interface.models.jobs_new.JobExecution") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Execution information for the job.

compilation*: [JobCompilation](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobCompilation.html#iqm.station_control.interface.models.jobs_new.JobCompilation "iqm.station_control.interface.models.jobs_new.JobCompilation") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Compilation information for the job.

messages*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[JobMessage](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobMessage.html#iqm.station_control.interface.models.jobs_new.JobMessage "iqm.station_control.interface.models.jobs_new.JobMessage")\]*  
Informational messages for the job.

errors*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMServerError](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError")\]*  
Errors for a failed job.

queue_position*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Iff the status is JobStatus.WAITING, the number of jobs ahead of this job in the queue. Otherwise None.

timeline*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[TimelineEntry](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.TimelineEntry.html#iqm.station_control.interface.models.jobs_new.TimelineEntry "iqm.station_control.interface.models.jobs_new.TimelineEntry")\]*  
Server-side statuses reached by the job so far. May include statuses from several services.

artifacts*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[JobArtifactInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobArtifactInfo.html#iqm.station_control.interface.models.jobs_new.JobArtifactInfo "iqm.station_control.interface.models.jobs_new.JobArtifactInfo")\]*  
Generated artifacts that represent the output of the job.

Lists the currently available artifacts. More may be added as long as the job is not in a terminal status.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-12e9e38959946a7ba8dc975e56cc80e855724b88.png)
