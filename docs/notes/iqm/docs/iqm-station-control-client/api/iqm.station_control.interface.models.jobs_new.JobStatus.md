> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobStatus.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 156781ae22938305eb47c663b2a06911dbbd1bd98fe984ff333dd1f79760be58.

# JobStatus

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobStatus(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Job statuses in IQMServer.

Attributes

|  |  |
|----|----|
| [`WAITING`](#iqm.station_control.interface.models.jobs_new.JobStatus.WAITING "iqm.station_control.interface.models.jobs_new.JobStatus.WAITING") | Job is in a queue, waiting to be executed. |
| [`PROCESSING`](#iqm.station_control.interface.models.jobs_new.JobStatus.PROCESSING "iqm.station_control.interface.models.jobs_new.JobStatus.PROCESSING") | Job is being executed. |
| [`COMPLETED`](#iqm.station_control.interface.models.jobs_new.JobStatus.COMPLETED "iqm.station_control.interface.models.jobs_new.JobStatus.COMPLETED") | Job has completed successfully. |
| [`FAILED`](#iqm.station_control.interface.models.jobs_new.JobStatus.FAILED "iqm.station_control.interface.models.jobs_new.JobStatus.FAILED") | Job has failed. |
| [`CANCELLED`](#iqm.station_control.interface.models.jobs_new.JobStatus.CANCELLED "iqm.station_control.interface.models.jobs_new.JobStatus.CANCELLED") | Job has been cancelled by the user or the admin. |

Methods

|  |  |
|----|----|
| [`terminal_statuses`](#iqm.station_control.interface.models.jobs_new.JobStatus.terminal_statuses "iqm.station_control.interface.models.jobs_new.JobStatus.terminal_statuses") | Statuses from which the execution no longer continues. |

WAITING *= 'waiting'*  
Job is in a queue, waiting to be executed.

PROCESSING *= 'processing'*  
Job is being executed.

COMPLETED *= 'completed'*  
Job has completed successfully.

FAILED *= 'failed'*  
Job has failed.

CANCELLED *= 'cancelled'*  
Job has been cancelled by the user or the admin.

*classmethod* terminal_statuses()  
Statuses from which the execution no longer continues.

Once a job reaches a terminal status, its status will no longer change.

Return type:  
[*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[*JobStatus*](#iqm.station_control.interface.models.jobs_new.JobStatus "iqm.station_control.interface.models.jobs_new.JobStatus")\]

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-cde2e41c21b2f8a16e502d3ba49365ad6afad94e.png)
