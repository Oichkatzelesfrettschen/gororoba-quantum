> Full piece: [https://docs.openquantum.com/portal/monitoring-jobs/](https://docs.openquantum.com/portal/monitoring-jobs/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7ecebd4f160c224f7d03729148a04f94c48c6642d11257c756001635a6c11288.

# Monitoring Jobs

The [Jobs](https://www.openquantum.com/jobs) page shows every job in your organization regardless of how it was submitted. Jobs created through the Python SDK, Qiskit, PennyLane, Cirq, Qrisp, or the portal all appear here.

## Why This Matters

Quantum jobs often run from remote environments — cloud VMs, HPC clusters, or CI pipelines. The portal gives you a single place to monitor everything:

- Check job status from your laptop, phone, or any browser.
- No need to keep your script running to track progress.
- Review and download results days or weeks after a job completes.

## Job Status

Each job shows its current status:

| Status        | Description                                                |
|---------------|------------------------------------------------------------|
| **Created**   | Job submitted, awaiting credit deduction.                  |
| **Pending**   | Credits deducted, waiting for dispatch.                    |
| **Queued**    | Dispatched to the backend, waiting in the execution queue. |
| **Running**   | Circuit is executing on the QPU.                           |
| **Completed** | Results are ready to view and download.                    |
| **Failed**    | Execution failed. Credits are refunded.                    |
| **Canceled**  | Job was canceled. Credits are refunded.                    |

See [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) for the full breakdown.

## Viewing Results

On each job card you can:

- **Download** -- Download the raw result data as JSON when the job is **Completed** and results are available. Shape depends on the backend (for example measurement counts or other backend-specific JSON).
- **⋯ menu**
- **Download calibration data** -- Shown when the completing execution tagged a calibration snapshot (`calibration_data_url`). Opens a presigned JSON download.
- **Report an issue** -- Available for failed jobs.

Job details also include backend, status message, timestamps, and credit cost.

Note

Calibration is optional. If the backend did not attach calibration on completion, the download option does not appear. The same data is available in the Python SDK via `job.calibration_data_url` and `scheduler.download_job_calibration(job)`.

## Filtering and Search

Use the Jobs page to filter by status, backend, or date range. This is helpful when reviewing a batch of experiments or tracking down a specific run.
