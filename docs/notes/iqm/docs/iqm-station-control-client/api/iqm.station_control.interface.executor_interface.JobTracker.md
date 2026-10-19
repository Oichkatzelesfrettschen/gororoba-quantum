> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 65989ca51258183ef62cf96ea5d9e0aa642a85e3f776c48dbe244a7197556577.

# JobTracker

Module: [`iqm.station_control.interface.executor_interface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.html#module-iqm.station_control.interface.executor_interface "iqm.station_control.interface.executor_interface")

*class* JobTracker(*\**, *job_data*, *\_executor*, *\_context=\<factory\>*, *\_payload=None*)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)"), [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`T_JobDefinition`\]

Orchestrates the lifecycle of a job, bridging raw data with execution logic.

A JobTracker wraps a static [`JobData`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData") snapshot and uses an [`ExecutorInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface") to perform live actions like status synchronization, waiting for completion, or cancellation.

Attributes

|  |  |
|----|----|
| [`errors`](#iqm.station_control.interface.executor_interface.JobTracker.errors "iqm.station_control.interface.executor_interface.JobTracker.errors") | All errors formatted as a string. |
| [`job_id`](#iqm.station_control.interface.executor_interface.JobTracker.job_id "iqm.station_control.interface.executor_interface.JobTracker.job_id") | Unique ID of the job. |
| [`status`](#iqm.station_control.interface.executor_interface.JobTracker.status "iqm.station_control.interface.executor_interface.JobTracker.status") | Last queried status of the job. |
| [`job_data`](#iqm.station_control.interface.executor_interface.JobTracker.job_data "iqm.station_control.interface.executor_interface.JobTracker.job_data") | The underlying job status and metadata. |

Methods

|  |  |
|----|----|
| [`cancel`](#iqm.station_control.interface.executor_interface.JobTracker.cancel "iqm.station_control.interface.executor_interface.JobTracker.cancel") | Cancel the job. |
| [`find_timeline_entry`](#iqm.station_control.interface.executor_interface.JobTracker.find_timeline_entry "iqm.station_control.interface.executor_interface.JobTracker.find_timeline_entry") | Search the job's execution timeline for an entry matching the specified criteria. |
| [`payload`](#iqm.station_control.interface.executor_interface.JobTracker.payload "iqm.station_control.interface.executor_interface.JobTracker.payload") | Retrieve the original definition/payload used to submit this job. |
| [`update`](#iqm.station_control.interface.executor_interface.JobTracker.update "iqm.station_control.interface.executor_interface.JobTracker.update") | Update the job data by querying the execution backend. |
| [`wait_for_completion`](#iqm.station_control.interface.executor_interface.JobTracker.wait_for_completion "iqm.station_control.interface.executor_interface.JobTracker.wait_for_completion") | Poll the backend updating the job status, until the job reaches a terminal state, or until we hit a timeout. |

Parameters:  
- **job_data** ([*JobData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData"))

- **\_executor** ([*ExecutorInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface"))

- **\_context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **\_payload** (*T_JobDefinition* *\|* *None*)

job_data*: [JobData](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData")*  
The underlying job status and metadata.

*property* job_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique ID of the job.

*property* status*: [JobStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus")*  
Last queried status of the job.

Note that this is not necessarily the same as the current status of the job, unless the status is terminal. To get the current status, use [`update()`](#iqm.station_control.interface.executor_interface.JobTracker.update "iqm.station_control.interface.executor_interface.JobTracker.update").

update()  
Update the job data by querying the execution backend.

Modifies [`job_data`](#iqm.station_control.interface.executor_interface.JobTracker.job_data "iqm.station_control.interface.executor_interface.JobTracker.job_data"). If the job is already in a terminal state (COMPLETED, FAILED, or CANCELLED), no query is performed to save bandwidth.

Returns:  
Current status of the job.

Return type:  
[*JobStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus")

cancel()  
Cancel the job.

Return type:  
*None*

payload()  
Retrieve the original definition/payload used to submit this job.

If the payload was provided at initialization (e.g., during submission), it is returned immediately. Otherwise, it is fetched from the executor.

Return type:  
*T_JobDefinition*

wait_for_completion(*\**, *timeout_secs=10800.0*, *polling_interval=1.0*, *progress_callback=None*)  
Poll the backend updating the job status, until the job reaches a terminal state, or until we hit a timeout.

The terminal states are “completed”, “failed”, and “cancelled”.

Will stop the polling (but does not cancel the job) upon receiving a KeyboardInterrupt (Ctrl-C). If you want to cancel the job, call [`cancel()`](#iqm.station_control.interface.executor_interface.JobTracker.cancel "iqm.station_control.interface.executor_interface.JobTracker.cancel").

Modifies `self`.

Parameters:  
- **timeout_secs** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Maximum time to wait in seconds. If nonzero, the method will return the current status after this period even if it is non-terminal.

- **polling_interval** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Time to wait in seconds between successive status synchronization requests.

- **progress_callback** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)") *\|* *None*) – Optional callback function triggered on every status update loop. Receives progress data packets (e.g., queue positions or execution metrics) to update UI progress bars. Defaults to None.

Returns:  
Last seen job status.

Raises:  
[**KeyboardInterrupt**](https://docs.python.org/3.11/library/exceptions.html#KeyboardInterrupt "(in Python v3.11)") – Received Ctrl-C while waiting for the job to finish.

Return type:  
[*JobStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus")

find_timeline_entry(*status*, *source=None*)  
Search the job’s execution timeline for an entry matching the specified criteria.

The timeline is an ordered log of state transitions and events. This method performs a linear search from the beginning of the timeline and returns the first entry that matches the provided status and, optionally, the source.

Parameters:  
- **status** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The status string to search for (e.g., “pending”, “running”).

- **source** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['iqm-server',* *'iqm-station-control'\]* *\|* *str* *\|* *None*) – The component or service that generated the timeline entry. If provided, only entries from this source are considered. If None (default), entries from any source matching the status will be returned.

Returns:  
The first matching `TimelineEntry` found, or `None` if no entry in the timeline satisfies the criteria.

Return type:  
[*TimelineEntry*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.TimelineEntry.html#iqm.station_control.interface.models.jobs_new.TimelineEntry "iqm.station_control.interface.models.jobs_new.TimelineEntry") \| *None*

*property* errors*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
All errors formatted as a string.

Inheritance

![Inheritance diagram of iqm.station_control.interface.executor_interface.JobTracker](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-7d876b5cc38bb00be596ba76a103d2cb931280f2.png)
