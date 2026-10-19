> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.CircuitJobTracker.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.CircuitJobTracker.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e3c1caabc1f64b9f6640e1bb565b78076016d58cfebe72d648bd81bcf948e728.

# CircuitJobTracker

Module: [`iqm.station_control.client.job_trackers`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.html#module-iqm.station_control.client.job_trackers "iqm.station_control.client.job_trackers")

*class* CircuitJobTracker(*\**, *job_data*, *\_executor*, *\_context=\<factory\>*, *\_payload=None*)  
Bases: [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker")\[[`PostJobsRequest`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest")\]

Tracker for circuit jobs.

Attributes

|            |                                         |
|------------|-----------------------------------------|
| `job_data` | The underlying job status and metadata. |

Methods

|  |  |
|----|----|
| [`result`](#iqm.station_control.client.job_trackers.CircuitJobTracker.result "iqm.station_control.client.job_trackers.CircuitJobTracker.result") | Fetch the job results as raw bitstrings. |
| [`result_counts`](#iqm.station_control.client.job_trackers.CircuitJobTracker.result_counts "iqm.station_control.client.job_trackers.CircuitJobTracker.result_counts") | Fetch the job results as aggrated bitstring counts. |

Parameters:  
- **job_data** ([*JobData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData"))

- **\_executor** ([*ExecutorInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface"))

- **\_context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **\_payload** (*T_JobDefinition* *\|* *None*)

result()  
Fetch the job results as raw bitstrings.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\] \| *None*

result_counts()  
Fetch the job results as aggrated bitstring counts.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitMeasurementCounts*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts")\] \| *None*

Inheritance

![Inheritance diagram of iqm.station_control.client.job_trackers.CircuitJobTracker](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-74d5b935748eb4a67b9b7241aa094097e2da6e25.png)
