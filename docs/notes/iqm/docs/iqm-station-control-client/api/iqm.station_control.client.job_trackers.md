> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 62a7eb733283bdaef1241765f6209ab1a4cb8c313cce4114f7a9ffa3efa86190.

# job_trackers

Full path: iqm.station_control.client.job_trackers

Concrete implementations of job trackers for different job types.

This module contains specialized [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker") subclasses that extend the base tracking logic with type-specific result processing.

Each tracker is responsible for:

1.  **Lifecycle Monitoring**: Inheriting the polling and status synchronization logic from the base interface.

2.  **Result Interpretation**: Implementing the `result()` method to fetch specific artifacts (e.g., N-dimensional arrays for sweeps or bitstrings for circuits).

Classes

|  |  |
|----|----|
| [`CircuitJobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.CircuitJobTracker.html#iqm.station_control.client.job_trackers.CircuitJobTracker "iqm.station_control.client.job_trackers.CircuitJobTracker") | Tracker for circuit jobs. |
| [`RunJobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html#iqm.station_control.client.job_trackers.RunJobTracker "iqm.station_control.client.job_trackers.RunJobTracker") | Tracker for experiment run jobs. |

Inheritance

![Inheritance diagram of iqm.station_control.client.job_trackers](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-fa7044ff3304be734b4f5bae109f1ce2e40b45be.png)
