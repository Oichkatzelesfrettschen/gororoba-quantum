> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8124b85a75051105eb8f91c1acebddf7cfb400c29e5f37bf7d664278415e80ad.

# station_control_executor

Full path: iqm.station_control.client.station_control_executor

Implementation of the ExecutorInterface for communication with a Station Control.

This module provides the [`StationControlExecutor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.StationControlExecutor.html#iqm.station_control.client.station_control_executor.StationControlExecutor "iqm.station_control.client.station_control_executor.StationControlExecutor"), which enables quantum job execution and hardware metadata retrieval by interfacing with the Station Control’s REST API.

Functions

|  |  |
|----|----|
| [`cast_dataclass`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.cast_dataclass.html#iqm.station_control.client.station_control_executor.cast_dataclass "iqm.station_control.client.station_control_executor.cast_dataclass")(source_instance, ...) | Copies shared fields from source_instance to a new target_class instance. |

Classes

|  |  |
|----|----|
| [`StationControlExecutor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.StationControlExecutor.html#iqm.station_control.client.station_control_executor.StationControlExecutor "iqm.station_control.client.station_control_executor.StationControlExecutor") | Concrete executor that communicates with a remote Station Control to manage hardware execution and results. |

Inheritance

![Inheritance diagram of iqm.station_control.client.station_control_executor](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-368c97ca3dee256904d2f9b93894aaa865e11cb4.png)
