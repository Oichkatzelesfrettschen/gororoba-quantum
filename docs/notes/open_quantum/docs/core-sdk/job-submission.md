> Full piece: [https://docs.openquantum.com/core-sdk/job-submission/](https://docs.openquantum.com/core-sdk/job-submission/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 332b5d5ca8286415cc85b0d0584ac99b429de11c495988e6bb83d98b7b2c7d69.

# Job Submission

The Core SDK provides a high-level `submit_job()` method that handles the entire job lifecycle in a single call: upload, prepare, submit, and wait for completion.

## JobSubmissionConfig

`JobSubmissionConfig` defines all parameters for a job submission:

``` python
from openquantum_sdk.clients import JobSubmissionConfig

config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="My Quantum Job",
    job_subcategory_id="oth:oth",
    shots=128,
)
```

### Required Fields

| Field | Type | Description |
|----|----|----|
| `backend_class_id` | `str` | Target backend (UUID or short code, e.g., `"rigetti:cepheus-1-108q"`) |
| `name` | `str` | Display name for the job |
| `job_subcategory_id` | `str` | Job subcategory (UUID or short code, e.g., `"oth:oth"`) |
| `shots` | `int` | Number of measurement shots |

### Optional Fields

| Field | Type | Default | Description |
|----|----|----|----|
| `organization_id` | `str` | `None` | Organization UUID. Auto-discovered if not provided. |
| `configuration_data` | `dict` | `None` | Backend-specific configuration data. |
| `execution_plan` | `str` | `"auto"` | `"auto"`, a friendly name (`"public"` or `"private"`), an `ExecutionPlanType` value, or a plan UUID. Names are case-insensitive. `"auto"` picks the cheapest plan. |
| `queue_priority` | `str` | `"auto"` | `"auto"`, a friendly name (`"standard"`, `"priority"`, or `"instant"`), a `QueuePriorityType` value, or a priority UUID. Names are case-insensitive. `"auto"` picks the cheapest priority. |
| `auto_approve_quote` | `bool` | `True` | Automatically approve the pricing quote. |
| `verbose` | `bool` | `False` | Print progress messages during submission. |
| `job_timeout_seconds` | `int` | `86400` | Maximum time to wait for job completion (1 day). |
| `submitted_with` | `str` | `"sdk"` | Client surface for analytics (`"sdk"`, `"cli"`, etc.). |
| `input_format` | `str` | `"qasm"` | Circuit language family (default OpenQASM). Other values may be accepted when listed in the backend's `supported_formats`. |

## Input formats

Backends advertise accepted input language **families** via `constraint_data.supported_formats` (defaults to `["qasm"]` when omitted).

| `input_format` | What you upload | Notes |
|----|----|----|
| `"qasm"` (default) | OpenQASM 2 or 3 text | Version is detected from the file header (`OPENQASM 2.0` / `OPENQASM 3.0`). |
| `"qblox_sequence"` | Qblox sequence JSON (`program` + waveforms) | Only if listed in `supported_formats`. |
| `"qblox_schedule"` | Official qblox-scheduler Schedule JSON | Only if listed in `supported_formats`. |
| Other values | Backend-specific input | Only valid if the backend lists them in `supported_formats`. |

``` python
# OpenQASM (default) — omit input_format or set "qasm"
config = JobSubmissionConfig(
    backend_class_id="ionq:forte-1",
    name="Bell State",
    job_subcategory_id="oth:oth",
    shots=128,
    input_format="qasm",
)
job = scheduler.submit_job(config, file_path="circuit.qasm")
```

Low-level `JobPreparationCreate` accepts the same `input_format` field:

``` python
prep = JobPreparationCreate(
    organization_id=org_id,
    backend_class_id="ionq:forte-1",
    name="Manual Job",
    upload_endpoint_id=upload_id,
    job_subcategory_id="oth:oth",
    shots=128,
    input_format="qasm",
)
```

Note

If you declare an `input_format` the backend does not list in `supported_formats`, job preparation fails with a validation error.

## Bringing circuits from other frameworks

Open Quantum accepts **OpenQASM**, so you can run circuits written in almost any framework by exporting them to QASM and submitting the text. Your circuit must include measurements — the backend returns counts over the measured bits.

| Framework | Export to OpenQASM |
|----|----|
| Qiskit | `from qiskit import qasm2; qasm2.dumps(circuit)` (or `qasm3.dumps`) |
| Cirq | `cirq.qasm(circuit)` |
| Qrisp | `circuit.to_qiskit()`, then flatten + `qasm2.dumps` (see below) |

``` python
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q[0]), cirq.CNOT(q[0], q[1]), cirq.measure(*q, key="m")
)
job = scheduler.submit_job(config, file_content=cirq.qasm(circuit).encode("utf-8"))
```

One quantum register per program

The platform accepts **a single quantum register and a single classical register** per program. Qiskit and Cirq already export this way. Some exporters (notably Qrisp's native `QuantumCircuit.qasm()`) emit **one register per qubit**, which is rejected during job preparation with `At most one qubit register allowed`. Flatten to a single register first.

The most portable way to flatten is to rebuild the circuit on a fresh single-register Qiskit `QuantumCircuit` of the right size, then export that:

``` python
from qiskit import QuantumCircuit, qasm2

# `source` is any Qiskit circuit, including one produced by another
# framework's Qiskit bridge (e.g. a Qrisp circuit's .to_qiskit()).
flat = QuantumCircuit(source.num_qubits, source.num_clbits)
flat.compose(source, inplace=True)  # single 'q' / 'c' registers, mapped by index
qasm = qasm2.dumps(flat)
```

For Qrisp, go through its Qiskit bridge and then flatten:

``` python
import qrisp
from qiskit import QuantumCircuit, qasm2

qc = qrisp.QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure([0, 1, 2], [0, 1, 2])

qk = qc.to_qiskit()
flat = QuantumCircuit(qk.num_qubits, qk.num_clbits)
flat.compose(qk, inplace=True)
job = scheduler.submit_job(config, file_content=qasm2.dumps(flat).encode("utf-8"))
```

### Execution Plan and Queue Priority

When set to `"auto"` (the default), the SDK selects the cheapest available execution plan and the lowest-cost queue priority. You can also pass an enum, a friendly name (`"public"`, `"private"`, `"standard"`, `"priority"`, `"instant"`), or the plan/priority UUID:

``` python
from openquantum_sdk.enums import ExecutionPlanType, QueuePriorityType

config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="Priority Job",
    job_subcategory_id="oth:oth",
    shots=128,
    execution_plan=ExecutionPlanType.PUBLIC,
    queue_priority=QueuePriorityType.PRIORITY,
)
```

## Submitting a Job

Use `submit_job()` with either a file path or raw bytes:

### From a File

``` python
job = scheduler.submit_job(config, file_path="circuit.qasm")
```

### From a String

``` python
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

job = scheduler.submit_job(config, file_content=qasm.encode("utf-8"))
```

Warning

`file_content` must be `bytes`, not `str`. Encode your string with `.encode("utf-8")`.

## Downloading Results

After a job completes, download the output:

``` python
output = scheduler.download_job_output(job)
print(output)
```

The `download_job_output()` method fetches the result from the presigned URL in the job's `output_data_url` field and parses it as JSON.

Note

`download_job_output()` takes a `JobRead` object (returned by `submit_job()` / `get_job()`), not a job ID string.

Result shape depends on the backend (for example a bitstring **counts** map, or another backend-specific JSON document).

## Calibration data

Some backends tag a **calibration snapshot** on the completing execution. When present, the job includes a presigned `calibration_data_url` (same pattern as `output_data_url`).

``` python
job = scheduler.get_job(job.id)  # refresh URLs if needed

if job.calibration_data_url:
    cal = scheduler.download_job_calibration(job)
    print(cal)
else:
    print("No calibration tagged on this job")
```

| Field / method | Description |
|----|----|
| `job.calibration_data_url` | Presigned download URL, or `None` if no calibration was tagged |
| `scheduler.download_job_calibration(job)` | GET + parse JSON for that URL |

Calibration is **optional**. Backends that report calibration to the platform set it when the execution completes successfully.

Portal

On [Jobs](https://www.openquantum.com/jobs), open the **⋯** menu on a job that has calibration data and choose **Download calibration data**.

## Error Handling

The SDK raises specific exceptions for API errors:

``` python
from openquantum_sdk.models import APIError

try:
    job = scheduler.submit_job(config, file_path="circuit.qasm")
except APIError as e:
    print(f"Status: {e.error_response.status_code}")
    print(f"Message: {e.error_response.message}")
    print(f"Request ID: {e.error_response.error_code}")
except TimeoutError as e:
    print(f"Job timed out: {e}")
except RuntimeError as e:
    print(f"Submission error: {e}")
```

Common error scenarios:

| HTTP Status | Meaning |
|----|----|
| 401 | Invalid or expired credentials |
| 402 | Insufficient credits |
| 409 | Active job limit reached (max 10 Public or 100 Private jobs per organization) |

## Verbose Mode

Enable verbose output to see progress during submission:

``` python
config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="Verbose Job",
    job_subcategory_id="oth:oth",
    shots=128,
    verbose=True,
)

job = scheduler.submit_job(config, file_path="circuit.qasm")
```

Output:

```
Step 1/5: Uploading job input...
Step 2/5: Preparing job and fetching quote...
  > Preparation status: Completed
  > Preparation complete.
Step 3/5: Processing quote...
  > Auto-selected plan: Public Plan (2 credits)
  > Auto-selected priority: Standard Queue (+0)
Step 3/5: Quote approved automatically (auto_approve_quote=True)
Step 4/5: Submitting job (Public Plan + Standard Queue)...
Step 5/5: Job 'abc123...' created. Waiting for completion (timeout: 86400s)...
  > Job status: Completed
  > Job finished with status: Completed
```

## Job Categories

Every job requires a `job_subcategory_id` (e.g., `"oth:oth"`). The high-level `submit_job()` accepts short codes and resolves them automatically, but for low-level submission you may need to discover the valid category and subcategory UUIDs.

### Listing Categories

``` python
categories = scheduler.get_job_categories()
for cat in categories.categories:
    print(f"{cat.id}: {cat.name} ({cat.short_code})")
```

### Listing Subcategories

``` python
subcategories = scheduler.get_job_subcategories(category_id="<category-uuid>")
for sub in subcategories.categories:
    print(f"{sub.id}: {sub.name} ({sub.short_code})")
```

Both methods support pagination with `limit` and `cursor` parameters.

## Polling Utility

The SDK provides a generic `poll_for_status` utility for polling any status endpoint. It is used internally by `submit_job()` to wait for job preparation and completion, but you can also use it directly for low-level workflows.

``` python
from openquantum_sdk import poll_for_status

result = poll_for_status(
    get_status_fn=my_status_checker,
    resource_id="resource-uuid",
    interval=5,       # seconds between polls (default: 5)
    timeout=300,       # max seconds before TimeoutError (default: 300)
)
```

| Parameter | Type | Default | Description |
|----|----|----|----|
| `get_status_fn` | `Callable[[str], tuple[bool, Any]]` | -- | Takes a resource ID, returns `(is_done, result)` |
| `resource_id` | `str` | -- | ID passed to `get_status_fn` on each call |
| `interval` | `float` | `5` | Seconds between polling attempts |
| `timeout` | `float` | `300` | Maximum seconds before polling stops |
| `raise_on_timeout` | `bool` | `True` | Raise `TimeoutError`, or return the last result when `False` |

Example with job status polling:

``` python
def check_job(job_id):
    job = scheduler.get_job(job_id)
    return job.status in ("Completed", "Failed", "Canceled"), job

job = poll_for_status(check_job, "your-job-uuid", interval=10, timeout=600)
print(f"Final status: {job.status}")
```

For a job or a preparation, prefer the client helpers. They use `poll_for_status` and share one definition of terminal statuses and plan selection:

``` python
from openquantum_sdk.models import JobCreate

result = scheduler.wait_for_preparation(prep_resp.id, timeout=300, interval=2)
selection = scheduler.choose_plan_and_priority(
    result,
    execution_plan="auto",   # "public" / "private" / UUID also work
    queue_priority="auto",   # "standard" / "priority" / "instant" / UUID
)
job = scheduler.create_job(JobCreate(
    job_preparation_id=prep_resp.id,
    execution_plan_id=selection.execution_plan_id,
    queue_priority_id=selection.queue_priority_id,
))
job = scheduler.wait_for_job(job.id, timeout=86_400, interval=5)
```

`choose_plan_and_priority(..., prefer_public=True)` ranks Public plans first when the plan is `"auto"`. `submit_job()` leaves this off and keeps the cheapest plan. `wait_for_job(..., raise_on_timeout=False, raise_on_failure=False)` returns the latest job instead of raising, which is what a caller does when it needs to re-poll later.

## Low-Level Submission

For finer control, you can use the individual methods instead of `submit_job()`:

``` python
from openquantum_sdk.models import JobPreparationCreate, JobCreate

# Step 1: Upload
upload_id = scheduler.upload_job_input(file_path="circuit.qasm")

# Step 2: Prepare (input_format defaults to "qasm"; set only if the backend needs another format)
prep = JobPreparationCreate(
    organization_id="your-org-uuid",
    backend_class_id="rigetti:cepheus-1-108q",
    name="Manual Job",
    upload_endpoint_id=upload_id,
    job_subcategory_id="oth:oth",
    shots=128,
    input_format="qasm",
)
prep_resp = scheduler.prepare_job(prep)

# Step 3: Wait for the quote, then pick a plan (cheapest by default)
result = scheduler.wait_for_preparation(prep_resp.id)
selection = scheduler.choose_plan_and_priority(result, execution_plan="auto", queue_priority="auto")

# Step 4: Submit
job_create = JobCreate(
    job_preparation_id=prep_resp.id,
    execution_plan_id=selection.execution_plan_id,
    queue_priority_id=selection.queue_priority_id,
)
job = scheduler.create_job(job_create)

# Step 5: Wait for a terminal status
job = scheduler.wait_for_job(job.id)
```

## Related Pages

- [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Find available backends before submitting.
- [Examples](https://docs.openquantum.com/core-sdk/examples/) -- Complete workflows.
- [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) -- Detailed job state machine.
