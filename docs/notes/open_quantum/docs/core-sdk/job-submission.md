> Full piece: [https://docs.openquantum.com/core-sdk/job-submission/](https://docs.openquantum.com/core-sdk/job-submission/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 332b5d5ca8286415cc85b0d0584ac99b429de11c495988e6bb83d98b7b2c7d69.

# Job Submission

The Core SDK provides a high-level `submit_job()` method that handles the entire job lifecycle in a single call: upload, prepare, submit, and wait for completion.

## JobSubmissionConfig

`JobSubmissionConfig` defines all parameters for a job submission:

[](#__codelineno-0-1)`from`` ``openquantum_sdk.clients`` ``import`` ``JobSubmissionConfig`\
[](#__codelineno-0-2)\
[](#__codelineno-0-3)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-0-4)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-0-5)`    ``name``=``"My Quantum Job"``,`\
[](#__codelineno-0-6)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-0-7)`    ``shots``=``128``,`\
[](#__codelineno-0-8)`)`\

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

[](#__codelineno-1-1)`# OpenQASM (default) — omit input_format or set "qasm"`\
[](#__codelineno-1-2)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-1-3)`    ``backend_class_id``=``"ionq:forte-1"``,`\
[](#__codelineno-1-4)`    ``name``=``"Bell State"``,`\
[](#__codelineno-1-5)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-1-6)`    ``shots``=``128``,`\
[](#__codelineno-1-7)`    ``input_format``=``"qasm"``,`\
[](#__codelineno-1-8)`)`\
[](#__codelineno-1-9)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"circuit.qasm"``)`\

Low-level `JobPreparationCreate` accepts the same `input_format` field:

[](#__codelineno-2-1)`prep`` ``=`` ``JobPreparationCreate``(`\
[](#__codelineno-2-2)`    ``organization_id``=``org_id``,`\
[](#__codelineno-2-3)`    ``backend_class_id``=``"ionq:forte-1"``,`\
[](#__codelineno-2-4)`    ``name``=``"Manual Job"``,`\
[](#__codelineno-2-5)`    ``upload_endpoint_id``=``upload_id``,`\
[](#__codelineno-2-6)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-2-7)`    ``shots``=``128``,`\
[](#__codelineno-2-8)`    ``input_format``=``"qasm"``,`\
[](#__codelineno-2-9)`)`\

Note

If you declare an `input_format` the backend does not list in `supported_formats`, job preparation fails with a validation error.

## Bringing circuits from other frameworks

Open Quantum accepts **OpenQASM**, so you can run circuits written in almost any framework by exporting them to QASM and submitting the text. Your circuit must include measurements — the backend returns counts over the measured bits.

| Framework | Export to OpenQASM |
|----|----|
| Qiskit | `from qiskit import qasm2; qasm2.dumps(circuit)` (or `qasm3.dumps`) |
| Cirq | `cirq.qasm(circuit)` |
| Qrisp | `circuit.to_qiskit()`, then flatten + `qasm2.dumps` (see below) |

[](#__codelineno-3-1)`import`` ``cirq`\
[](#__codelineno-3-2)\
[](#__codelineno-3-3)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-3-4)`circuit`` ``=`` ``cirq``.``Circuit``(`\
[](#__codelineno-3-5)`    ``cirq``.``H``(``q``[``0``]),`` ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`` ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``)`\
[](#__codelineno-3-6)`)`\
[](#__codelineno-3-7)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_content``=``cirq``.``qasm``(``circuit``)``.``encode``(``"utf-8"``))`\

One quantum register per program

The platform accepts **a single quantum register and a single classical register** per program. Qiskit and Cirq already export this way. Some exporters (notably Qrisp's native `QuantumCircuit.qasm()`) emit **one register per qubit**, which is rejected during job preparation with `At most one qubit register allowed`. Flatten to a single register first.

The most portable way to flatten is to rebuild the circuit on a fresh single-register Qiskit `QuantumCircuit` of the right size, then export that:

[](#__codelineno-4-1)`from`` ``qiskit`` ``import`` ``QuantumCircuit``,`` ``qasm2`\
[](#__codelineno-4-2)\
[](#__codelineno-4-3)`` # `source` is any Qiskit circuit, including one produced by another ``\
[](#__codelineno-4-4)`# framework's Qiskit bridge (e.g. a Qrisp circuit's .to_qiskit()).`\
[](#__codelineno-4-5)`flat`` ``=`` ``QuantumCircuit``(``source``.``num_qubits``,`` ``source``.``num_clbits``)`\
[](#__codelineno-4-6)`flat``.``compose``(``source``,`` ``inplace``=``True``)``  ``# single 'q' / 'c' registers, mapped by index`\
[](#__codelineno-4-7)`qasm`` ``=`` ``qasm2``.``dumps``(``flat``)`\

For Qrisp, go through its Qiskit bridge and then flatten:

[](#__codelineno-5-1)`import`` ``qrisp`\
[](#__codelineno-5-2)`from`` ``qiskit`` ``import`` ``QuantumCircuit``,`` ``qasm2`\
[](#__codelineno-5-3)\
[](#__codelineno-5-4)`qc`` ``=`` ``qrisp``.``QuantumCircuit``(``3``,`` ``3``)`\
[](#__codelineno-5-5)`qc``.``h``(``0``)`\
[](#__codelineno-5-6)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-5-7)`qc``.``cx``(``0``,`` ``2``)`\
[](#__codelineno-5-8)`qc``.``measure``([``0``,`` ``1``,`` ``2``],`` ``[``0``,`` ``1``,`` ``2``])`\
[](#__codelineno-5-9)\
[](#__codelineno-5-10)`qk`` ``=`` ``qc``.``to_qiskit``()`\
[](#__codelineno-5-11)`flat`` ``=`` ``QuantumCircuit``(``qk``.``num_qubits``,`` ``qk``.``num_clbits``)`\
[](#__codelineno-5-12)`flat``.``compose``(``qk``,`` ``inplace``=``True``)`\
[](#__codelineno-5-13)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_content``=``qasm2``.``dumps``(``flat``)``.``encode``(``"utf-8"``))`\

### Execution Plan and Queue Priority

When set to `"auto"` (the default), the SDK selects the cheapest available execution plan and the lowest-cost queue priority. You can also pass an enum, a friendly name (`"public"`, `"private"`, `"standard"`, `"priority"`, `"instant"`), or the plan/priority UUID:

[](#__codelineno-6-1)`from`` ``openquantum_sdk.enums`` ``import`` ``ExecutionPlanType``,`` ``QueuePriorityType`\
[](#__codelineno-6-2)\
[](#__codelineno-6-3)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-6-4)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-6-5)`    ``name``=``"Priority Job"``,`\
[](#__codelineno-6-6)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-6-7)`    ``shots``=``128``,`\
[](#__codelineno-6-8)`    ``execution_plan``=``ExecutionPlanType``.``PUBLIC``,`\
[](#__codelineno-6-9)`    ``queue_priority``=``QueuePriorityType``.``PRIORITY``,`\
[](#__codelineno-6-10)`)`\

## Submitting a Job

Use `submit_job()` with either a file path or raw bytes:

### From a File

[](#__codelineno-7-1)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"circuit.qasm"``)`\

### From a String

[](#__codelineno-8-1)`qasm`` ``=`` ``"""`\
[](#__codelineno-8-2)`OPENQASM 2.0;`\
[](#__codelineno-8-3)`include "qelib1.inc";`\
[](#__codelineno-8-4)`qreg q[2];`\
[](#__codelineno-8-5)`creg c[2];`\
[](#__codelineno-8-6)`h q[0];`\
[](#__codelineno-8-7)`cx q[0],q[1];`\
[](#__codelineno-8-8)`measure q[0] -> c[0];`\
[](#__codelineno-8-9)`measure q[1] -> c[1];`\
[](#__codelineno-8-10)`"""`\
[](#__codelineno-8-11)\
[](#__codelineno-8-12)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_content``=``qasm``.``encode``(``"utf-8"``))`\

Warning

`file_content` must be `bytes`, not `str`. Encode your string with `.encode("utf-8")`.

## Downloading Results

After a job completes, download the output:

[](#__codelineno-9-1)`output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-9-2)`print``(``output``)`\

The `download_job_output()` method fetches the result from the presigned URL in the job's `output_data_url` field and parses it as JSON.

Note

`download_job_output()` takes a `JobRead` object (returned by `submit_job()` / `get_job()`), not a job ID string.

Result shape depends on the backend (for example a bitstring **counts** map, or another backend-specific JSON document).

## Calibration data

Some backends tag a **calibration snapshot** on the completing execution. When present, the job includes a presigned `calibration_data_url` (same pattern as `output_data_url`).

[](#__codelineno-10-1)`job`` ``=`` ``scheduler``.``get_job``(``job``.``id``)``  ``# refresh URLs if needed`\
[](#__codelineno-10-2)\
[](#__codelineno-10-3)`if`` ``job``.``calibration_data_url``:`\
[](#__codelineno-10-4)`    ``cal`` ``=`` ``scheduler``.``download_job_calibration``(``job``)`\
[](#__codelineno-10-5)`    ``print``(``cal``)`\
[](#__codelineno-10-6)`else``:`\
[](#__codelineno-10-7)`    ``print``(``"No calibration tagged on this job"``)`\

| Field / method | Description |
|----|----|
| `job.calibration_data_url` | Presigned download URL, or `None` if no calibration was tagged |
| `scheduler.download_job_calibration(job)` | GET + parse JSON for that URL |

Calibration is **optional**. Backends that report calibration to the platform set it when the execution completes successfully.

Portal

On [Jobs](https://www.openquantum.com/jobs), open the **⋯** menu on a job that has calibration data and choose **Download calibration data**.

## Error Handling

The SDK raises specific exceptions for API errors:

[](#__codelineno-11-1)`from`` ``openquantum_sdk.models`` ``import`` ``APIError`\
[](#__codelineno-11-2)\
[](#__codelineno-11-3)`try``:`\
[](#__codelineno-11-4)`    ``job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"circuit.qasm"``)`\
[](#__codelineno-11-5)`except`` ``APIError`` ``as`` ``e``:`\
[](#__codelineno-11-6)`    ``print``(``f``"Status: ``{``e``.``error_response``.``status_code``}``"``)`\
[](#__codelineno-11-7)`    ``print``(``f``"Message: ``{``e``.``error_response``.``message``}``"``)`\
[](#__codelineno-11-8)`    ``print``(``f``"Request ID: ``{``e``.``error_response``.``error_code``}``"``)`\
[](#__codelineno-11-9)`except`` ``TimeoutError`` ``as`` ``e``:`\
[](#__codelineno-11-10)`    ``print``(``f``"Job timed out: ``{``e``}``"``)`\
[](#__codelineno-11-11)`except`` ``RuntimeError`` ``as`` ``e``:`\
[](#__codelineno-11-12)`    ``print``(``f``"Submission error: ``{``e``}``"``)`\

Common error scenarios:

| HTTP Status | Meaning |
|----|----|
| 401 | Invalid or expired credentials |
| 402 | Insufficient credits |
| 409 | Active job limit reached (max 10 Public or 100 Private jobs per organization) |

## Verbose Mode

Enable verbose output to see progress during submission:

[](#__codelineno-12-1)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-12-2)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-12-3)`    ``name``=``"Verbose Job"``,`\
[](#__codelineno-12-4)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-12-5)`    ``shots``=``128``,`\
[](#__codelineno-12-6)`    ``verbose``=``True``,`\
[](#__codelineno-12-7)`)`\
[](#__codelineno-12-8)\
[](#__codelineno-12-9)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"circuit.qasm"``)`\

Output:

[](#__codelineno-13-1)`Step 1/5: Uploading job input...`\
[](#__codelineno-13-2)`Step 2/5: Preparing job and fetching quote...`\
[](#__codelineno-13-3)`  > Preparation status: Completed`\
[](#__codelineno-13-4)`  > Preparation complete.`\
[](#__codelineno-13-5)`Step 3/5: Processing quote...`\
[](#__codelineno-13-6)`  > Auto-selected plan: Public Plan (2 credits)`\
[](#__codelineno-13-7)`  > Auto-selected priority: Standard Queue (+0)`\
[](#__codelineno-13-8)`Step 3/5: Quote approved automatically (auto_approve_quote=True)`\
[](#__codelineno-13-9)`Step 4/5: Submitting job (Public Plan + Standard Queue)...`\
[](#__codelineno-13-10)`Step 5/5: Job 'abc123...' created. Waiting for completion (timeout: 86400s)...`\
[](#__codelineno-13-11)`  > Job status: Completed`\
[](#__codelineno-13-12)`  > Job finished with status: Completed`\

## Job Categories

Every job requires a `job_subcategory_id` (e.g., `"oth:oth"`). The high-level `submit_job()` accepts short codes and resolves them automatically, but for low-level submission you may need to discover the valid category and subcategory UUIDs.

### Listing Categories

[](#__codelineno-14-1)`categories`` ``=`` ``scheduler``.``get_job_categories``()`\
[](#__codelineno-14-2)`for`` ``cat`` ``in`` ``categories``.``categories``:`\
[](#__codelineno-14-3)`    ``print``(``f``"``{``cat``.``id``}``: ``{``cat``.``name``}`` (``{``cat``.``short_code``}``)"``)`\

### Listing Subcategories

[](#__codelineno-15-1)`subcategories`` ``=`` ``scheduler``.``get_job_subcategories``(``category_id``=``"<category-uuid>"``)`\
[](#__codelineno-15-2)`for`` ``sub`` ``in`` ``subcategories``.``categories``:`\
[](#__codelineno-15-3)`    ``print``(``f``"``{``sub``.``id``}``: ``{``sub``.``name``}`` (``{``sub``.``short_code``}``)"``)`\

Both methods support pagination with `limit` and `cursor` parameters.

## Polling Utility

The SDK provides a generic `poll_for_status` utility for polling any status endpoint. It is used internally by `submit_job()` to wait for job preparation and completion, but you can also use it directly for low-level workflows.

[](#__codelineno-16-1)`from`` ``openquantum_sdk`` ``import`` ``poll_for_status`\
[](#__codelineno-16-2)\
[](#__codelineno-16-3)`result`` ``=`` ``poll_for_status``(`\
[](#__codelineno-16-4)`    ``get_status_fn``=``my_status_checker``,`\
[](#__codelineno-16-5)`    ``resource_id``=``"resource-uuid"``,`\
[](#__codelineno-16-6)`    ``interval``=``5``,``       ``# seconds between polls (default: 5)`\
[](#__codelineno-16-7)`    ``timeout``=``300``,``       ``# max seconds before TimeoutError (default: 300)`\
[](#__codelineno-16-8)`)`\

| Parameter | Type | Default | Description |
|----|----|----|----|
| `get_status_fn` | `Callable[[str], tuple[bool, Any]]` | -- | Takes a resource ID, returns `(is_done, result)` |
| `resource_id` | `str` | -- | ID passed to `get_status_fn` on each call |
| `interval` | `float` | `5` | Seconds between polling attempts |
| `timeout` | `float` | `300` | Maximum seconds before polling stops |
| `raise_on_timeout` | `bool` | `True` | Raise `TimeoutError`, or return the last result when `False` |

Example with job status polling:

[](#__codelineno-17-1)`def`` ``check_job``(``job_id``):`\
[](#__codelineno-17-2)`    ``job`` ``=`` ``scheduler``.``get_job``(``job_id``)`\
[](#__codelineno-17-3)`    ``return`` ``job``.``status`` ``in`` ``(``"Completed"``,`` ``"Failed"``,`` ``"Canceled"``),`` ``job`\
[](#__codelineno-17-4)\
[](#__codelineno-17-5)`job`` ``=`` ``poll_for_status``(``check_job``,`` ``"your-job-uuid"``,`` ``interval``=``10``,`` ``timeout``=``600``)`\
[](#__codelineno-17-6)`print``(``f``"Final status: ``{``job``.``status``}``"``)`\

For a job or a preparation, prefer the client helpers. They use `poll_for_status` and share one definition of terminal statuses and plan selection:

[](#__codelineno-18-1)`from`` ``openquantum_sdk.models`` ``import`` ``JobCreate`\
[](#__codelineno-18-2)\
[](#__codelineno-18-3)`result`` ``=`` ``scheduler``.``wait_for_preparation``(``prep_resp``.``id``,`` ``timeout``=``300``,`` ``interval``=``2``)`\
[](#__codelineno-18-4)`selection`` ``=`` ``scheduler``.``choose_plan_and_priority``(`\
[](#__codelineno-18-5)`    ``result``,`\
[](#__codelineno-18-6)`    ``execution_plan``=``"auto"``,``   ``# "public" / "private" / UUID also work`\
[](#__codelineno-18-7)`    ``queue_priority``=``"auto"``,``   ``# "standard" / "priority" / "instant" / UUID`\
[](#__codelineno-18-8)`)`\
[](#__codelineno-18-9)`job`` ``=`` ``scheduler``.``create_job``(``JobCreate``(`\
[](#__codelineno-18-10)`    ``job_preparation_id``=``prep_resp``.``id``,`\
[](#__codelineno-18-11)`    ``execution_plan_id``=``selection``.``execution_plan_id``,`\
[](#__codelineno-18-12)`    ``queue_priority_id``=``selection``.``queue_priority_id``,`\
[](#__codelineno-18-13)`))`\
[](#__codelineno-18-14)`job`` ``=`` ``scheduler``.``wait_for_job``(``job``.``id``,`` ``timeout``=``86_400``,`` ``interval``=``5``)`\

`choose_plan_and_priority(..., prefer_public=True)` ranks Public plans first when the plan is `"auto"`. `submit_job()` leaves this off and keeps the cheapest plan. `wait_for_job(..., raise_on_timeout=False, raise_on_failure=False)` returns the latest job instead of raising, which is what a caller does when it needs to re-poll later.

## Low-Level Submission

For finer control, you can use the individual methods instead of `submit_job()`:

[](#__codelineno-19-1)`from`` ``openquantum_sdk.models`` ``import`` ``JobPreparationCreate``,`` ``JobCreate`\
[](#__codelineno-19-2)\
[](#__codelineno-19-3)`# Step 1: Upload`\
[](#__codelineno-19-4)`upload_id`` ``=`` ``scheduler``.``upload_job_input``(``file_path``=``"circuit.qasm"``)`\
[](#__codelineno-19-5)\
[](#__codelineno-19-6)`# Step 2: Prepare (input_format defaults to "qasm"; set only if the backend needs another format)`\
[](#__codelineno-19-7)`prep`` ``=`` ``JobPreparationCreate``(`\
[](#__codelineno-19-8)`    ``organization_id``=``"your-org-uuid"``,`\
[](#__codelineno-19-9)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-19-10)`    ``name``=``"Manual Job"``,`\
[](#__codelineno-19-11)`    ``upload_endpoint_id``=``upload_id``,`\
[](#__codelineno-19-12)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-19-13)`    ``shots``=``128``,`\
[](#__codelineno-19-14)`    ``input_format``=``"qasm"``,`\
[](#__codelineno-19-15)`)`\
[](#__codelineno-19-16)`prep_resp`` ``=`` ``scheduler``.``prepare_job``(``prep``)`\
[](#__codelineno-19-17)\
[](#__codelineno-19-18)`# Step 3: Wait for the quote, then pick a plan (cheapest by default)`\
[](#__codelineno-19-19)`result`` ``=`` ``scheduler``.``wait_for_preparation``(``prep_resp``.``id``)`\
[](#__codelineno-19-20)`selection`` ``=`` ``scheduler``.``choose_plan_and_priority``(``result``,`` ``execution_plan``=``"auto"``,`` ``queue_priority``=``"auto"``)`\
[](#__codelineno-19-21)\
[](#__codelineno-19-22)`# Step 4: Submit`\
[](#__codelineno-19-23)`job_create`` ``=`` ``JobCreate``(`\
[](#__codelineno-19-24)`    ``job_preparation_id``=``prep_resp``.``id``,`\
[](#__codelineno-19-25)`    ``execution_plan_id``=``selection``.``execution_plan_id``,`\
[](#__codelineno-19-26)`    ``queue_priority_id``=``selection``.``queue_priority_id``,`\
[](#__codelineno-19-27)`)`\
[](#__codelineno-19-28)`job`` ``=`` ``scheduler``.``create_job``(``job_create``)`\
[](#__codelineno-19-29)\
[](#__codelineno-19-30)`# Step 5: Wait for a terminal status`\
[](#__codelineno-19-31)`job`` ``=`` ``scheduler``.``wait_for_job``(``job``.``id``)`\

## Related Pages

- [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Find available backends before submitting.
- [Examples](https://docs.openquantum.com/core-sdk/examples/) -- Complete workflows.
- [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) -- Detailed job state machine.
