> Full piece: [https://docs.openquantum.com/core-sdk/examples/](https://docs.openquantum.com/core-sdk/examples/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec3a8f5d8077dbc9349fc34933b416c86a0281679fb2d6d989a2fe8562684a8f.

# Core SDK Examples

Common workflows using the `openquantum-sdk` package.

Note

All examples assume you have valid SDK key credentials. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for setup.

## Submit a QASM File from Disk

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

scheduler = SchedulerClient(auth=auth)

config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="File Upload Job",
    job_subcategory_id="oth:oth",
    shots=128,
)

job = scheduler.submit_job(config, file_path="my_circuit.qasm")
output = scheduler.download_job_output(job)
print(output)

scheduler.close()
```

## Submit a QASM String

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

scheduler = SchedulerClient(auth=auth)

qasm = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="String QASM Job",
    job_subcategory_id="oth:oth",
    shots=128,
)

job = scheduler.submit_job(config, file_content=qasm.encode("utf-8"))
output = scheduler.download_job_output(job)
print(output)

scheduler.close()
```

## List and Filter Backends

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import ManagementClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

management = ManagementClient(auth=auth)

# List all backends
result = management.list_backend_classes()
for bc in result.backend_classes:
    status = "accepting jobs" if bc.accepting_jobs else "not accepting"
    print(f"{bc.short_code} ({bc.type}, {bc.status}, {status})")

# Filter by provider
ionq_backends = management.list_backend_classes(provider_id="ionq")
for bc in ionq_backends.backend_classes:
    print(f"IonQ: {bc.short_code} - {bc.name}")

management.close()
```

## Check Job Status

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

scheduler = SchedulerClient(auth=auth)

job = scheduler.get_job("your-job-uuid")
print(f"Job: {job.id}")
print(f"Status: {job.status}")
print(f"Submitted: {job.submitted_at}")

if job.status == "Completed" and job.output_data_url:
    output = scheduler.download_job_output(job)
    print(f"Results: {output}")

if job.calibration_data_url:
    cal = scheduler.download_job_calibration(job)
    print(f"Calibration keys: {list(cal) if isinstance(cal, dict) else type(cal)}")

scheduler.close()
```

## List Organization Jobs

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)

scheduler = SchedulerClient(auth=auth)

# List recent jobs (organization is auto-discovered)
result = scheduler.list_jobs()
for job in result.jobs:
    print(f"{job.name}: {job.status} ({job.submitted_at})")

# Filter by status
completed = scheduler.list_jobs(status="Completed")
for job in completed.jobs:
    print(f"Completed: {job.name} - {job.credits_used} credits")

scheduler.close()
```

## Use the CLI

The Core SDK includes a command-line interface:

``` bash
python -m openquantum_sdk \
    --input circuit.qasm \
    --backend rigetti:cepheus-1-108q \
    --subcategory oth:oth \
    --shots 128 \
    --client-id "s_your_client_id" \
    --client-secret "your_client_secret" \
    --auto-approve
```

Or with an SDK key file:

``` bash
python -m openquantum_sdk \
    --input circuit.qasm \
    --backend rigetti:cepheus-1-108q \
    --subcategory oth:oth \
    --shots 128 \
    --sdk-key credentials.json
```

The SDK key file is a JSON file with `client_id` and `client_secret` fields:

``` json
{
    "client_id": "s_your_client_id",
    "client_secret": "your_client_secret"
}
```

## Related Pages

- [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Detailed `JobSubmissionConfig` reference.
- [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Backend listing and filtering.
- [Authentication](https://docs.openquantum.com/core-sdk/authentication/) -- All authentication options.
