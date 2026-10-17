> Full piece: [https://docs.openquantum.com/concepts/job-lifecycle/](https://docs.openquantum.com/concepts/job-lifecycle/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d8f236d51d24b559fa2cf88fafcfaf2161196e31395170c317b26039f318aff5.

# Job Lifecycle

Every job on Open Quantum goes through a series of states from creation to completion.

## Job States

| Status | Description | Terminal? |
|----|----|----|
| **Created** | Job submitted, awaiting credit deduction. | No |
| **Pending** | Credits deducted, awaiting execution dispatch. | No |
| **Queued** | Dispatched to a backend, waiting in the execution queue. | No |
| **Running** | Circuit is being executed on the backend. | No |
| **Completed** | Execution finished, results available. | Yes |
| **Failed** | Job failed at any stage. Credits refunded. | Yes |
| **Canceled** | User canceled the job. Credits refunded. | Yes |

### Preparation Phase

Before a job can be submitted, the circuit must be uploaded and prepared.

### Execution Phase

Once a job enters the Pending state:

- The platform dispatches the circuit to the requested backend.
- The circuit is executed on the QPU.
- Results are validated and made available for download.

### Completion

When execution succeeds, results are available for download via a presigned URL (`output_data_url`). The URL is valid for a limited time and regenerated on each job fetch.

If the backend tagged a calibration snapshot on the completing execution, the job also exposes `calibration_data_url` (same presigned-URL pattern). Not all backends provide calibration.

### Retry Behavior

If execution fails (hardware error, timeout, etc.):

- The job is retried up to **3 times**.
- After 3 failed attempts, the job transitions to **Failed** and credits are refunded.

## Cancellation

Jobs can only be canceled from the **Pending** state:

Core SDKPortal

``` python
scheduler.cancel_job("job-uuid")
```

Cancel jobs from the [Open Quantum Portal](https://www.openquantum.com) under **Jobs**.

Warning

Jobs in Queued or Running status cannot be canceled. Once execution has been dispatched, you must wait for it to complete or fail.

## Constraints

- Maximum **10 active Public jobs** and **100 active Private jobs** per organization (Created, Pending, Queued, or Running). The two limits are counted separately.
- Maximum QASM file size is 10 MB.

## SDK Behavior

Every SDK surface handles the job lifecycle automatically. The Core SDK's `submit_job()`, the Qiskit plugin's `backend.run()`, the PennyLane plugin's `execute()`, the Cirq sampler's `run()`, and the Qrisp backend's `get_measurement()` all manage upload, preparation, submission, polling, and result retrieval internally.

## Related Pages

- [Monitoring Jobs](https://docs.openquantum.com/portal/monitoring-jobs/) -- Track job status and download results from the portal.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- How pricing and refunds work.
- [Troubleshooting](https://docs.openquantum.com/pennylane-plugin/troubleshooting/) -- Common job errors.
