> Full piece: [https://docs.openquantum.com/core-sdk/overview/](https://docs.openquantum.com/core-sdk/overview/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 290892138723a1a751907af2e2a1712826ab1f4fb882a10fd0eff94985bd8145.

# Python SDK Overview

The Open Quantum Python SDK provides programmatic access to the platform. It consists of a core package and four optional framework plugins:

| Package | Install | Use case |
|----|----|----|
| **Core SDK** | `pip install openquantum-sdk` | Submit QASM files directly, manage jobs and backends |
| **Qiskit Plugin** | `pip install "openquantum-sdk[qiskit]"` | Use Open Quantum backends with Qiskit's `BackendV2`, `SamplerV2`, `EstimatorV2` |
| **PennyLane Plugin** | `pip install "openquantum-sdk[pennylane]"` | Use Open Quantum as a PennyLane device |
| **Cirq Plugin** | `pip install "openquantum-sdk[cirq]"` | Run Cirq circuits via an Open Quantum `cirq.Sampler` |
| **Qrisp Plugin** | `pip install "openquantum-sdk[qrisp]"` | Run Qrisp programs on Open Quantum backends |

The plugins include the Core SDK automatically. See the [Qiskit Plugin](https://docs.openquantum.com/qiskit-plugin/overview/), [PennyLane Plugin](https://docs.openquantum.com/pennylane-plugin/overview/), [Cirq Plugin](https://docs.openquantum.com/cirq-plugin/overview/), and [Qrisp Plugin](https://docs.openquantum.com/qrisp-plugin/overview/) sections for framework-specific documentation.

New to the SDK? Start with [Installation](https://docs.openquantum.com/core-sdk/installation/), then [Authentication](https://docs.openquantum.com/core-sdk/authentication/), then the [Quick Start](https://docs.openquantum.com/core-sdk/quickstart/).

------------------------------------------------------------------------

## Core SDK

The `openquantum-sdk` package provides direct Python access to the Open Quantum platform. It includes two main clients and a high-level job submission interface.

## What the Core SDK Provides

| Component | Description |
|----|----|
| **SchedulerClient** | Submit jobs, poll status, download results / calibration, cancel jobs |
| **ManagementClient** | List backends, list providers, discover organizations |
| **JobSubmissionConfig** | High-level configuration for one-call job submission |
| **ClientCredentialsAuth** | OAuth2 authentication with automatic token refresh |

## Basic Flow

The typical workflow with the Core SDK is:

1.  Set up authentication
2.  Create a client
3.  Submit a job
4.  Download results

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

# 1. Set up auth
auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

# 2. Create client
scheduler = SchedulerClient(auth=auth)

# 3. Submit a job
config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="My Quantum Job",
    job_subcategory_id="oth:oth",
    shots=128,
)
job = scheduler.submit_job(config, file_path="circuit.qasm")

# 4. Download results (and calibration if tagged)
output = scheduler.download_job_output(job)
print(output)
if job.calibration_data_url:
    cal = scheduler.download_job_calibration(job)
    print(cal)

scheduler.close()
```

## SchedulerClient

`SchedulerClient` handles the full job lifecycle.

``` python
from openquantum_sdk.clients import SchedulerClient

scheduler = SchedulerClient(auth=auth)
```

Key methods:

| Method | Description |
|----|----|
| `submit_job(config, file_path=..., file_content=...)` | High-level: upload, prepare, submit, and wait for completion |
| `upload_job_input(file_path=..., file_content=...)` | Upload circuit input (QASM or other supported formats), returns an upload ID |
| `prepare_job(preparation)` | Start job preparation (validation + pricing); set `input_format` on the payload |
| `get_preparation_result(preparation_id)` | Poll preparation status and get the pricing quote |
| `create_job(job)` | Submit a prepared job for execution |
| `get_job(job_id)` | Check job status (`output_data_url`, `calibration_data_url`, …) |
| `cancel_job(job_id)` | Cancel a pending job |
| `list_jobs(organization_id=...)` | List jobs for an organization |
| `get_job_categories(limit=..., cursor=...)` | List job categories |
| `get_job_subcategories(category_id, limit=..., cursor=...)` | List subcategories for a category |
| `download_job_output(job)` | Download and parse job results as JSON |
| `download_job_calibration(job)` | Download and parse calibration JSON when `calibration_data_url` is set |
| `close()` | Close the underlying HTTP session |

## ManagementClient

`ManagementClient` handles backend discovery and platform administration.

``` python
from openquantum_sdk.clients import ManagementClient

management = ManagementClient(auth=auth)
```

Key methods:

| Method | Description |
|----|----|
| `list_backend_classes(limit=..., cursor=..., provider_id=...)` | List available backends |
| `list_providers(limit=..., cursor=...)` | List hardware providers |
| `list_user_organizations(limit=..., cursor=...)` | List organizations the user belongs to |
| `close()` | Close the underlying HTTP session |

Note

`SchedulerClient` automatically creates a `ManagementClient` internally for organization auto-discovery. You only need to create one explicitly if you want to browse backends or providers directly.

## Next Steps

- [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Detailed guide to `JobSubmissionConfig` and `submit_job()`.
- [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Listing and filtering backends.
- [Examples](https://docs.openquantum.com/core-sdk/examples/) -- Common workflows with the Core SDK.
- [Qiskit Plugin](https://docs.openquantum.com/qiskit-plugin/overview/) -- Use Open Quantum with Qiskit circuits.
- [PennyLane Plugin](https://docs.openquantum.com/pennylane-plugin/overview/) -- Use Open Quantum as a PennyLane device.
- [Cirq Plugin](https://docs.openquantum.com/cirq-plugin/overview/) -- Run Cirq circuits on Open Quantum.
- [Qrisp Plugin](https://docs.openquantum.com/qrisp-plugin/overview/) -- Run Qrisp programs on Open Quantum.
- [API Reference](https://docs.openquantum.com/api-reference/) -- Auto-generated API docs.
