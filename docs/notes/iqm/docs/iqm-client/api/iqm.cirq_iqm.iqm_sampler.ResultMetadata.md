> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.ResultMetadata.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.ResultMetadata.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e39313d897e479c2fd82ba691101829dadcbc9c189b65ffa365edab130ca054a.

# ResultMetadata

Module: [`iqm.cirq_iqm.iqm_sampler`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.html#module-iqm.cirq_iqm.iqm_sampler "iqm.cirq_iqm.iqm_sampler")

*class* iqm.cirq_iqm.iqm_sampler.ResultMetadata(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*, *request: PostJobsRequest*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Metadata for an IQM execution result.

Parameters:  
- **job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

- **request** (*PostJobsRequest*)

job_id  
ID of the computational job.

Type:  
[uuid.UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")

calibration_set_id  
Calibration set used for this [`IQMResult`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html#iqm.cirq_iqm.iqm_sampler.IQMResult "iqm.cirq_iqm.iqm_sampler.IQMResult").

Type:  
[uuid.UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| None

request  
Request made to run the job.

Type:  
iqm.station_control.interface.models.circuit.PostJobsRequest

Attributes

|  |  |
|----|----|
| [`job_id`](#iqm.cirq_iqm.iqm_sampler.ResultMetadata.job_id "iqm.cirq_iqm.iqm_sampler.ResultMetadata.job_id") |  |
| [`calibration_set_id`](#iqm.cirq_iqm.iqm_sampler.ResultMetadata.calibration_set_id "iqm.cirq_iqm.iqm_sampler.ResultMetadata.calibration_set_id") |  |
| [`request`](#iqm.cirq_iqm.iqm_sampler.ResultMetadata.request "iqm.cirq_iqm.iqm_sampler.ResultMetadata.request") |  |

Methods

Inheritance

![Inheritance diagram of iqm.cirq_iqm.iqm_sampler.ResultMetadata](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-2020feb35b0cf738b473187ae5254c1baf456ef6.png)
