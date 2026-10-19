> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 04ef3fe210b8120011079342db1b3772c42cc16b4795d0788e2b6c0751d7e958.

# JobExecutorStatus

Module: [`iqm.station_control.interface.models.jobs`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html#module-iqm.station_control.interface.models.jobs "iqm.station_control.interface.models.jobs")

*class* JobExecutorStatus(*value*)  
Bases: [`Enum`](https://docs.python.org/3.11/library/enum.html#enum.Enum "(in Python v3.11)")

Different statuses a job can be in.

The ordering of these statuses is important, and execution logic relies on it. Thus, if a new status is added, ensure that it is slotted in at the appropriate place. See the `__lt__()` implementation for further details.

Attributes

|  |  |
|----|----|
| [`RECEIVED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.RECEIVED "iqm.station_control.interface.models.jobs.JobExecutorStatus.RECEIVED") | The job has been received by the server. |
| [`VALIDATION_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.VALIDATION_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.VALIDATION_STARTED") | The job is being validated. |
| [`VALIDATION_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.VALIDATION_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.VALIDATION_ENDED") | The job passed validation. |
| [`FETCH_CALIBRATION_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.FETCH_CALIBRATION_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.FETCH_CALIBRATION_STARTED") | Calibration data for the job is being fetched. |
| [`FETCH_CALIBRATION_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.FETCH_CALIBRATION_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.FETCH_CALIBRATION_ENDED") | Calibration data for the job has been fetched. |
| [`COMPILATION_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.COMPILATION_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.COMPILATION_STARTED") | The job is being compiled. |
| [`COMPILATION_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.COMPILATION_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.COMPILATION_ENDED") | The job has been successfully compiled. |
| [`SAVE_SWEEP_METADATA_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.SAVE_SWEEP_METADATA_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.SAVE_SWEEP_METADATA_STARTED") | Metadata about the sweep is being stored to database. |
| [`SAVE_SWEEP_METADATA_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.SAVE_SWEEP_METADATA_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.SAVE_SWEEP_METADATA_ENDED") | Metadata about the sweep has been stored to database. |
| [`PENDING_EXECUTION`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.PENDING_EXECUTION "iqm.station_control.interface.models.jobs.JobExecutorStatus.PENDING_EXECUTION") | The job is ready for execution and is waiting for its turn in the queue. |
| [`EXECUTION_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.EXECUTION_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.EXECUTION_STARTED") | The job has started executing on the instruments. |
| [`EXECUTION_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.EXECUTION_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.EXECUTION_ENDED") | The job has finished execution on the instruments. |
| [`POST_PROCESSING_PENDING`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_PENDING "iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_PENDING") | The job has finished execution and is awaiting further processing. |
| [`POST_PROCESSING_STARTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_STARTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_STARTED") | Execution artifacts are being constructed and persisted. |
| [`POST_PROCESSING_ENDED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_ENDED "iqm.station_control.interface.models.jobs.JobExecutorStatus.POST_PROCESSING_ENDED") | Execution artifacts have been constructed and persisted. |
| [`READY`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.READY "iqm.station_control.interface.models.jobs.JobExecutorStatus.READY") | The job has completed. |
| [`FAILED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.FAILED "iqm.station_control.interface.models.jobs.JobExecutorStatus.FAILED") | The job has failed. |
| [`ABORTED`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.ABORTED "iqm.station_control.interface.models.jobs.JobExecutorStatus.ABORTED") | The job has been aborted. |

Methods

|  |  |
|----|----|
| [`terminal_statuses`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.terminal_statuses "iqm.station_control.interface.models.jobs.JobExecutorStatus.terminal_statuses") | Statuses from which the execution can't continue. |
| [`in_progress_statuses`](#iqm.station_control.interface.models.jobs.JobExecutorStatus.in_progress_statuses "iqm.station_control.interface.models.jobs.JobExecutorStatus.in_progress_statuses") | Statuses representing jobs that should be cleaned up on restart. |

RECEIVED *= 'received'*  
The job has been received by the server.

VALIDATION_STARTED *= 'validation_started'*  
The job is being validated.

VALIDATION_ENDED *= 'validation_ended'*  
The job passed validation.

FETCH_CALIBRATION_STARTED *= 'fetch_calibration_started'*  
Calibration data for the job is being fetched.

FETCH_CALIBRATION_ENDED *= 'fetch_calibration_ended'*  
Calibration data for the job has been fetched.

COMPILATION_STARTED *= 'compilation_started'*  
The job is being compiled.

COMPILATION_ENDED *= 'compilation_ended'*  
The job has been successfully compiled.

SAVE_SWEEP_METADATA_STARTED *= 'save_sweep_metadata_started'*  
Metadata about the sweep is being stored to database.

SAVE_SWEEP_METADATA_ENDED *= 'save_sweep_metadata_ended'*  
Metadata about the sweep has been stored to database.

PENDING_EXECUTION *= 'pending_execution'*  
The job is ready for execution and is waiting for its turn in the queue.

EXECUTION_STARTED *= 'execution_started'*  
The job has started executing on the instruments.

EXECUTION_ENDED *= 'execution_ended'*  
The job has finished execution on the instruments.

POST_PROCESSING_PENDING *= 'post_processing_pending'*  
The job has finished execution and is awaiting further processing.

POST_PROCESSING_STARTED *= 'post_processing_started'*  
Execution artifacts are being constructed and persisted.

POST_PROCESSING_ENDED *= 'post_processing_ended'*  
Execution artifacts have been constructed and persisted.

READY *= 'ready'*  
The job has completed.

FAILED *= 'failed'*  
The job has failed. Error message(s) may be available.

ABORTED *= 'aborted'*  
The job has been aborted.

*classmethod* terminal_statuses()  
Statuses from which the execution can’t continue.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*JobExecutorStatus*](#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus")\]

*classmethod* in_progress_statuses()  
Statuses representing jobs that should be cleaned up on restart.

Returns all non-terminal statuses.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*JobExecutorStatus*](#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus")\]

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs.JobExecutorStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-3b0f69b5bfd5bac9173cb3505967a2a0a52d8d93.png)
