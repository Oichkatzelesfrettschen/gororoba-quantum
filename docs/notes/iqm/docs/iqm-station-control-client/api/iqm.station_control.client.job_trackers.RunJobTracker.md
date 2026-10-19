> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 25a5b243a32847a8d1102ee9219579aab057dfd1a1fa127db12cddf58f67e380.

# RunJobTracker

Module: [`iqm.station_control.client.job_trackers`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.html#module-iqm.station_control.client.job_trackers "iqm.station_control.client.job_trackers")

*class* RunJobTracker(*\**, *job_data*, *\_executor*, *\_context=\<factory\>*, *\_payload=None*)  
Bases: [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker")\[[`RunDefinition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "iqm.station_control.interface.models.run.RunDefinition")\]

Tracker for experiment run jobs.

Attributes

|            |                                         |
|------------|-----------------------------------------|
| `job_data` | The underlying job status and metadata. |

Methods

|  |  |
|----|----|
| [`result`](#iqm.station_control.client.job_trackers.RunJobTracker.result "iqm.station_control.client.job_trackers.RunJobTracker.result") | Fetch and process the job results. |
| [`result_exa`](#iqm.station_control.client.job_trackers.RunJobTracker.result_exa "iqm.station_control.client.job_trackers.RunJobTracker.result_exa") | Fetch and process the job results. |
| [`result_sweep`](#iqm.station_control.client.job_trackers.RunJobTracker.result_sweep "iqm.station_control.client.job_trackers.RunJobTracker.result_sweep") | Fetch the raw sweep results. |

Parameters:  
- **job_data** (*JobDataNew*)

- **\_executor** ([*ExecutorInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface"))

- **\_context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*)

- **\_payload** (*T_JobDefinition* *\|* *None*)

result()  
Fetch and process the job results.

Returns:  
Results for the job, or None if the results are not available.

Return type:  
CircuitExecutionResults \| *None*

result_exa(*\**, *compiler=None*)  
Fetch and process the job results.

Parameters:  
**compiler** (*Compiler* *\|* *None*) – Compiler for post-processing the job results. If None, just do default EXA post-processing.

Returns:  
Results for the job, or None if the results are not available.

Return type:  
RunResult \| *None*

result_sweep()  
Fetch the raw sweep results.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ndarray*\]\] \| *None*

Inheritance

![Inheritance diagram of iqm.station_control.client.job_trackers.RunJobTracker](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-108653a7cd6a7b11d0b22442bcf5cc7bf0a54c6a.png)
