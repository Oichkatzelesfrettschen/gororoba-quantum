> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e94ec63ab084fc067a4fccabcfcdff14a025c932783ca35d791d8c84876d41d8.

# IQMJob

Module: [`iqm.qrisp_iqm.backends.iqm_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.html#module-iqm.qrisp_iqm.backends.iqm_job "iqm.qrisp_iqm.backends.iqm_job")

*class* iqm.qrisp_iqm.backends.iqm_job.IQMJob(*job: T_JobTracker*, *\**, *backend: [iqm.qrisp_iqm.backends.backend.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend")*)  
Bases: `Job`, [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`T_JobTracker`\]

ABC for wrapping IQM job trackers, shared by circuit-level and pulse-level jobs.

Implements routines that do not differ between the two submission paths: status polling, cancellation, and the high-level result-retrieval flow.

Parameters:  
- **job** (*T_JobTracker*) – The IQM job tracker for an existing job. Used when retrieving a previously submitted job via `retrieve_job()`.

- **backend** (*qrisp_IQMBackend*) – The backend instance that created this job.

Notes

Jobs are normally created by `run_async()` and should not be instantiated directly by the user.

Attributes

|  |  |
|----|----|
| [`backend`](#iqm.qrisp_iqm.backends.iqm_job.IQMJob.backend "iqm.qrisp_iqm.backends.iqm_job.IQMJob.backend") | The `IQMBackend` that created this job. |

Methods

|  |  |
|----|----|
| [`cancel`](#iqm.qrisp_iqm.backends.iqm_job.IQMJob.cancel "iqm.qrisp_iqm.backends.iqm_job.IQMJob.cancel") | Attempt to cancel the job on the IQM server. |
| [`result`](#iqm.qrisp_iqm.backends.iqm_job.IQMJob.result "iqm.qrisp_iqm.backends.iqm_job.IQMJob.result") | Block until the job completes and return its measurement results. |
| [`status`](#iqm.qrisp_iqm.backends.iqm_job.IQMJob.status "iqm.qrisp_iqm.backends.iqm_job.IQMJob.status") | Query and return the current job status. |

*property* backend*: [iqm.qrisp_iqm.backends.backend.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend")*  
The `IQMBackend` that created this job.

result(*timeout: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → JobResult  
Block until the job completes and return its measurement results.

Waits for the IQM job to reach a terminal state on the server, and then parses and returns the measurement counts, or raises an appropriate error.

Parameters:  
**timeout** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Maximum number of seconds to wait for the job to finish. `None` means use the default client timeout.

Returns:  
The measurement results.

Raises:  
- [**TimeoutError**](https://docs.python.org/3.11/library/exceptions.html#TimeoutError "(in Python v3.11)") – If `timeout` is specified and the job does not finish in time.

- **JobFailureError** – If the job terminated with an error.

- **JobCancelledError** – If the job was cancelled.

Return type:  
*JobResult*

cancel() → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Attempt to cancel the job on the IQM server.

Returns:  
`True` iff cancellation was successful.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

status() → JobStatus  
Query and return the current job status.

This is a live query that fetches the latest status from the IQM server, which involves a network call.

Returns:  
The current status of the job.

Return type:  
*JobStatus*

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.backends.iqm_job.IQMJob](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-00b10fb575dadb40d59819ca0c34074e2d0e8779.png)
