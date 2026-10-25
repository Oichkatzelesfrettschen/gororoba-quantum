> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 4f0b261c7a24dab9fdfd38e6c405c6c190e02eecdc9be33e1440b0169f5b6c11.

# ExecutionStatus

Note

This class used to be called `JobStatus`. However, it was renamed for consistency reasons. While the old name will still work, it should not be used.

An [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) object contains a lot of metadata on top of the computation results a user wants to get. These can be retrieved from the `ExecutionStatus` object every execution contains.

``` default
>>> s = my_execution.status  # s is an ExecutionStatus instance
>>> if s.completed:
...    print(f"My job lasted {s.duration} seconds.")
My job lasted 37 seconds.
```

*class* perceval.runtime.execution_status.ExecutionStatus  
Stores metadata related to an execution

*property* canceled*: bool*  
Returns:  
whether the execution is in “CANCELED” or “CANCEL_REQUESTED” status

*property* completed*: bool*  
Returns:  
whether the execution has completed, i.e. not waiting or running anymore (corresponding statuses are “SUCCESS”, “ERROR” and “CANCELED”)

*property* creation_timestamp*: float*  
Returns:  
the timestamp the execution was created

*property* duration*: float*  
Returns:  
the duration of the execution (in seconds)

*property* failed*: bool*  
Returns:  
whether the execution has failed to complete (corresponding statuses are “CANCELED” and “ERROR”)

*property* maybe_completed*: bool*  
Returns:  
whether the execution has or might have completed (corresponding statuses are “SUCCESS”, “ERROR”, “CANCELED” and “UNKNOWN”)

*property* message*: str \| None*  
Returns:  
The execution message, if any.

*property* progress*: float*  
Returns:  
the current execution progress (between 0 and 1, 1 meaning 100%)

*property* running*: bool*  
Returns:  
whether the execution is running (corresponding statuses are “RUNNING” and “CANCEL_REQUESTED”)

start_run()  
Informs that the execution is starting. Sets the execution start time as the current time and the running status to “RUNNING”

*property* start_timestamp*: float*  
Returns:  
the timestamp the execution was started

*property* status*: [RunningStatus](#perceval.runtime.execution_status.RunningStatus "perceval.runtime.execution_status.RunningStatus")*  
Returns:  
the execution running status

*property* stop_message*: str \| None*  
Returns:  
the execution stop message, if any. In case of a successful execution, this will be None.

stop_run(*cause=RunningStatus.SUCCESS*, *mesg=None*)  
Informs that the execution has just stopped. Sets the execution stop time as the current time.

Parameters:  
- **cause** ([`RunningStatus`](#perceval.runtime.execution_status.RunningStatus "perceval.runtime.execution_status.RunningStatus")) – running status causing the end of the execution

- **mesg** (`Optional`\[`str`\]) – optional additional message related to the end of the execution

*property* success*: bool*  
Returns:  
whether the execution is in “SUCCESS” status

*property* unknown*: bool*  
Returns:  
whether the execution status is unknown

update_progress(*progress*, *phase=None*)  
Updates the execution progress.

Parameters:  
- **progress** (`float`) – the current progress (between 0 and 1, 1 meaning 100%)

- **phase** (`Optional`\[`str`\]) – message related to the current progress

update_times(*creation_datetime*, *start_time*, *duration*)  
Set the important times from external information

Parameters:  
- **creation_datetime** (`float`) – the timestamp the execution was created

- **start_time** (`float`) – the timestamp the execution was started

- **duration** (`float`) – the duration of the execution (in seconds)

*property* waiting*: bool*  
Returns:  
whether the execution is in “WAITING” status

&nbsp;

*enum* perceval.runtime.execution_status.RunningStatus(*value*)  
An enumeration.

Valid values are as follows:

NONE *= \<RunningStatus.NONE: -1\>*  

SUCCESS *= \<RunningStatus.SUCCESS: 0\>*  
The job has completed successfully. The full results are to be expected.

WAITING *= \<RunningStatus.WAITING: 1\>*  
The job is recorded on the Cloud but waits for a computing platform to be available in order to start.

RUNNING *= \<RunningStatus.RUNNING: 2\>*  
The job is being run on a given computing platform.

SUSPENDED *= \<RunningStatus.SUSPENDED: 3\>*  
The job was halted by the remote system and may be resumed later on.

CANCEL_REQUESTED *= \<RunningStatus.CANCEL_REQUESTED: 4\>*  
Transitional status leading to CANCELED. The Cloud sent a cancel order to the platform running the job.

CANCELED *= \<RunningStatus.CANCELED: 5\>*  
The job was canceled either by the user or the system. Partial results might be available.

ERROR *= \<RunningStatus.ERROR: 6\>*  
The job has failed and partial results might be available.

UNKNOWN *= \<RunningStatus.UNKNOWN: 7\>*  
An unknown status code was encountered.

The `Enum` and its members also have the following methods:

*static* from_server_response(*res*)  
Converts a job status name from the server to an enum value.

Note

the server name for SUCCESS is “completed”.

Parameters:  
**res** (`str`) – the job status name

Return type:  
[`RunningStatus`](#perceval.runtime.execution_status.RunningStatus "perceval.runtime.execution_status.RunningStatus")

Returns:  
the corresponding enum value or UNKNOWN if the status name is unknown.

*static* to_server_response(*status*)  
Converts a job status enum value to an acceptable name for the server.

Note

SUCCESS is converted to “completed”.

Parameters:  
**status** ([`RunningStatus`](#perceval.runtime.execution_status.RunningStatus "perceval.runtime.execution_status.RunningStatus")) – the job status enum value

Return type:  
`str`

Returns:  
the status name

*static* merge_with_index(*left*, *right*, *index_left*, *index_right*)  
Return type:  
`tuple`\[[`RunningStatus`](#perceval.runtime.execution_status.RunningStatus "perceval.runtime.execution_status.RunningStatus"), `int`\]

Returns:  
The predominant RunningStatus between left and right, as well as its associated index. As a special case, SUCCESS + WAITING = RUNNING, and the returned index is the one of the WAITING status
