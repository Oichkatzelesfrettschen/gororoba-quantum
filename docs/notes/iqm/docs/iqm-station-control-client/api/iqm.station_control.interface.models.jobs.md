> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 67b0e3521386c1130bee0f3ac5b62e08085779f80357096a4e758d11d589b566.

# jobs

Full path: iqm.station_control.interface.models.jobs

Job-related models.

Module Attributes

|  |  |
|----|----|
| [`ProgressCallback`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.ProgressCallback.html#iqm.station_control.interface.models.jobs.ProgressCallback "iqm.station_control.interface.models.jobs.ProgressCallback") | Callback function for reporting progress on a list of tasks. |
| [`Statuses`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.Statuses.html#iqm.station_control.interface.models.jobs.Statuses "iqm.station_control.interface.models.jobs.Statuses") | Progress of the parallel sweeps of a job. |

Classes

|  |  |
|----|----|
| [`JobData`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobData.html#iqm.station_control.interface.models.jobs.JobData "iqm.station_control.interface.models.jobs.JobData") | Status, artifacts and metadata of a job. |
| [`JobError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobError.html#iqm.station_control.interface.models.jobs.JobError "iqm.station_control.interface.models.jobs.JobError") | Error message for a job. |
| [`JobExecutorStatus`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus") | Different statuses a job can be in. |
| [`JobResult`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobResult.html#iqm.station_control.interface.models.jobs.JobResult "iqm.station_control.interface.models.jobs.JobResult") | Progress information for the JobExecutorStatus.EXECUTION_STARTED stage of a job. |
| [`TimelineEntry`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.TimelineEntry.html#iqm.station_control.interface.models.jobs.TimelineEntry "iqm.station_control.interface.models.jobs.TimelineEntry") | Status and timestamp pair for a job timeline. |

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-18b1584d021ea9652172d85e0d35e4916d6306b9.png)
