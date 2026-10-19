> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b79ec2ac38219cdfaf3d3d584db1986f7b1ccae7eba6933fe48241ce48bbadbc.

# executor_interface

Full path: iqm.station_control.interface.executor_interface

Standardized interface for quantum job execution and lifecycle management.

This module provides two primary abstractions to manage the active lifecycle of quantum tasks:

1.  [`ExecutorInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface"): A stateless backend adapter that standardizes how jobs are submitted, queried, and cancelled.

2.  [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker"): A stateful handle for an in-flight job, encapsulating synchronization logic, progress tracking, and results retrieval.

Module Attributes

|  |  |
|----|----|
| [`DEFAULT_TIMEOUT_SECONDS`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.DEFAULT_TIMEOUT_SECONDS.html#iqm.station_control.interface.executor_interface.DEFAULT_TIMEOUT_SECONDS "iqm.station_control.interface.executor_interface.DEFAULT_TIMEOUT_SECONDS") | Default timeout (in seconds) when waiting for a job to reach a terminal state. |
| [`DEFAULT_POLLING_INTERVAL`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.DEFAULT_POLLING_INTERVAL.html#iqm.station_control.interface.executor_interface.DEFAULT_POLLING_INTERVAL "iqm.station_control.interface.executor_interface.DEFAULT_POLLING_INTERVAL") | Default interval (in seconds) between successive status synchronization requests. |

Classes

|  |  |
|----|----|
| [`ExecutorInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface") | Interface for managing quantum job execution and results retrieval. |
| [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker") | Orchestrates the lifecycle of a job, bridging raw data with execution logic. |

Inheritance

![Inheritance diagram of iqm.station_control.interface.executor_interface](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-794cee92ebd96dc035836c2efb512ae7acd6da7b.png)
