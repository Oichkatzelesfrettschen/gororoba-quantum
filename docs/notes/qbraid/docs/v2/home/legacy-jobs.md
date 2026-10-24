> Full piece: [https://docs.qbraid.com/v2/home/legacy-jobs.md](https://docs.qbraid.com/v2/home/legacy-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 8b87c98d082bab0fddab59e322d6710212affa46cedee814f8541a64e5c9403f.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# Legacy Jobs Retrieval

Following the migration to qBraid's V2 platform, quantum jobs from the legacy platform are no longer directly accessible through the new API. However, you can download and work with your legacy jobs data using the instructions below.

<Warning>
**Schema Changes**

Legacy jobs will **not** match the schema of the new runtime jobs in API V2. If you're working with both legacy and new jobs, be aware that their data structures and field names will differ.

For more details, see the [API Reference for V2 Jobs](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs).

</Warning>

## Downloading legacy jobs data

1. Log in to your qBraid account at [account.qbraid.com](https://account.qbraid.com/)
2. Navigate to the **Jobs** page
3. Look for the **Download Old Jobs** option
4. Click to export all your legacy quantum jobs as a JSON file
5. Save the JSON file to your local machine

## Displaying legacy jobs with qBraid-SDK

Once you've downloaded your legacy jobs JSON file, you can view the jobs data using the qBraid-SDK.

### Prerequisites

Ensure you have qBraid-SDK version `0.10.2` installed:

```bash
pip install 'qbraid==0.10.2'
```

### Loading the data

<Tabs>
<Tab title="Retrieving jobs">
```python
from qbraid.runtime import QbraidProvider

# Path to the legacy jobs JSON file

legacy_jobs_path = 'legacy_jobs.json'

# Initialize the provider with the legacy jobs path

provider = QbraidProvider(legacy_jobs_path=legacy_jobs_path)

# Display the first 5 jobs

print(provider.display_jobs(max_results=5))

````
</Tab>
<Tab title="Output">
```python
Displaying 5/5 jobs matching query:

Job ID    | Submitted                 | Status
--------- | ------------------------- | ---------------
<job_id_1> | 2025-12-31 T17:52:46.850Z | COMPLETED
<job_id_2> | 2025-11-06 T13:29:16.031Z | FAILED
<job_id_3> | 2025-10-31 T17:52:44.674Z | CANCELLED
<job_id_4> | 2025-10-31 T17:52:42.551Z | COMPLETED
<job_id_5> | 2025-10-28 T09:32:11.508Z | COMPLETED
````

</Tab>
</Tabs>

### Functionality and limitations

Once the `QbraidProvider` is initialized with the legacy jobs JSON path, you can only use the `display_jobs()` method to display the jobs.

Methods that interface with the API, such as `get_device()`, will **not** work when using legacy jobs. This is because device information is not available through the old API endpoints.

<Note>
  For full functionality including device access and job submission, upgrade to
  qBraid-SDK version **0.11.0 or greater** and use the new V2 API endpoints. See
  the [V2 SDK documentation](https://docs.qbraid.com/v2/sdk/user-guide/overview) for details.
</Note>

## Retrieving job details with qbraid-core

For more detailed information about individual jobs, you can use the **qbraid-core** library, which provides direct access to job metadata and results.

### Prerequisites

Install qbraid-core version`0.1.50`:

```bash
pip install 'qbraid-core==0.1.50'
```

### Using QuantumClient

The `QuantumClient` accepts the same legacy jobs JSON path parameter and provides methods for retrieving detailed job information:

```python
from qbraid_core.services.quantum import QuantumClient

# Initialize the client with the legacy jobs JSON path
legacy_jobs_path = 'legacy_jobs.json'
client = QuantumClient(legacy_jobs_path=legacy_jobs_path)

# List all jobs
jobs_list = client.search_jobs()

# display the first 5 jobs
print(jobs_list[:5])

# Get detailed information for a specific job
job_id = jobs_list[0]['qbraidJobId']
job_details = client.get_job(job_id)
print(job_details)
```

### Available methods

- **`search_jobs()`** - Returns a list of all legacy jobs
- **`get_job(job_id)`** - Retrieves detailed metadata for a specific job
- **`get_job_result(job_id)`** - Fetches the results and measurements for a completed job

## Need help?

If you encounter any issues retrieving or working with your legacy jobs data, contact [contact@qbraid.com](mailto:contact@qbraid.com).

## Related

- [Migration Guide](https://docs.qbraid.com/v2/home/migration) - Learn about the platform migration
- [V2 Documentation](https://docs.qbraid.com/v2/home/introduction) - Get started with the new platform
- [qBraid-SDK Documentation](https://docs.qbraid.com/v2/sdk) - Full SDK reference
