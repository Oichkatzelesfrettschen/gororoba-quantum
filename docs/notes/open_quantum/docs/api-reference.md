> Full piece: [https://docs.openquantum.com/api-reference/](https://docs.openquantum.com/api-reference/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2253b66c0188fab3ca3e4afa0a8196103c19f59cbb92c8e25fefbccff5471918.

# API Reference

Complete reference documentation for all Open Quantum SDK classes, methods, and data models.

## Core SDK

### SchedulerClient

## `SchedulerClient` [¶](#openquantum_sdk.clients.SchedulerClient "Permanent link")

Bases: `BaseClient`

Client for the OpenQuantum Scheduler API.

Handles the full job lifecycle: uploading circuit files, preparing quotes, submitting jobs, polling for completion, and downloading results.

The high-level `submit_job()` method wraps the entire flow in a single call. Lower-level methods (`upload_job_input`, `prepare_job`, `wait_for_preparation`, `choose_plan_and_priority`, `create_job`, `wait_for_job`) are available when the caller needs to stop between the quote and the spend.

Example

> > > from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig auth = ClientCredentialsAuth( ... creds=ClientCredentials(client_id="s\_...", client_secret="...") ... ) scheduler = SchedulerClient(auth=auth) config = JobSubmissionConfig( ... backend_class_id="ionq:aria-1", ... name="My Job", ... job_subcategory_id="phys:oth", ... shots=1024, ... ) job = scheduler.submit_job(config, file_path="circuit.qasm")

### `submit_job` [¶](#openquantum_sdk.clients.SchedulerClient.submit_job "Permanent link")

Submit a job end-to-end: upload, prepare, approve, create, and poll.

This is the recommended way to run a circuit. It handles the full lifecycle automatically:

1.  Upload the circuit file.
2.  Prepare the job and fetch a pricing quote.
3.  Select (or auto-select) the execution plan and queue priority.
4.  Approve the quote and create the job.
5.  Poll until the job completes (or times out).

Provide exactly one of `file_content` or `file_path`.

Returns:

[TABLE]

Raises:

[TABLE]

Example

> > > config = JobSubmissionConfig( ... backend_class_id="ionq:aria-1", ... name="Bell State", ... job_subcategory_id="phys:oth", ... shots=1024, ... ) job = scheduler.submit_job(config, file_path="bell.qasm") output = scheduler.download_job_output(job)

### `upload_job_input` [¶](#openquantum_sdk.clients.SchedulerClient.upload_job_input "Permanent link")

Upload a circuit file and return the upload ID.

Provide exactly one of `file_content` or `file_path`.

Returns:

[TABLE]

Raises:

[TABLE]

### `prepare_job` [¶](#openquantum_sdk.clients.SchedulerClient.prepare_job "Permanent link")

Submit a job preparation request.

Preparation validates the circuit, calculates pricing, and returns a preparation ID that can be polled via `get_preparation_result()`.

Returns:

[TABLE]

### `get_preparation_result` [¶](#openquantum_sdk.clients.SchedulerClient.get_preparation_result "Permanent link")

Get the status and pricing quote for a job preparation.

Poll this method until the returned `status` is `"Completed"` or `"Failed"`. On completion, the `quote` field contains the available execution plans and queue priorities with pricing.

Returns:

[TABLE]

### `create_job` [¶](#openquantum_sdk.clients.SchedulerClient.create_job "Permanent link")

Create and submit a job from a completed preparation.

This deducts credits and places the job in the execution queue. Organization is taken from the preparation; `organization_id` on `JobCreate` is optional.

Returns:

[TABLE]

### `get_job` [¶](#openquantum_sdk.clients.SchedulerClient.get_job "Permanent link")

Get the current status of a job.

Returns:

[TABLE]

### `cancel_job` [¶](#openquantum_sdk.clients.SchedulerClient.cancel_job "Permanent link")

Cancel a queued or running job.

### `list_jobs` [¶](#openquantum_sdk.clients.SchedulerClient.list_jobs "Permanent link")

List jobs for an organization.

Returns:

[TABLE]

### `download_job_output` [¶](#openquantum_sdk.clients.SchedulerClient.download_job_output "Permanent link")

Download and parse the output of a completed job.

Returns:

[TABLE]

Raises:

[TABLE]

### `download_job_calibration` [¶](#openquantum_sdk.clients.SchedulerClient.download_job_calibration "Permanent link")

Download and parse the calibration snapshot tagged on a job.

Calibration is optional: only present if reported.

Returns:

[TABLE]

Raises:

[TABLE]

### `wait_for_preparation` [¶](#openquantum_sdk.clients.SchedulerClient.wait_for_preparation "Permanent link")

Poll a preparation until it completes or fails.

A `Failed` preparation raises `RuntimeError`. A timeout raises `TimeoutError`. Not-found responses (the preparation row is not visible yet) are retried until the timeout.

### `wait_for_job` [¶](#openquantum_sdk.clients.SchedulerClient.wait_for_job "Permanent link")

Poll a job until it reaches a terminal status or times out.

Terminal statuses are `Completed`, `Failed`, and `Canceled` (see :data:`TERMINAL_JOB_STATUSES`).

Returns:

[TABLE]

### `choose_plan_and_priority` [¶](#openquantum_sdk.clients.SchedulerClient.choose_plan_and_priority "Permanent link")

Choose a plan and priority from a completed preparation.

See :func:`select_plan_and_priority` for the selection rules. `prefer_public=True` ranks Public plans first when the plan is `"auto"` (the MCP spend policy). The default keeps cheapest-wins.

### Plan selection

## `openquantum_sdk``.``clients``.``select_plan_and_priority``(``quote``,`` ``execution_plan``=``'auto'``,`` ``queue_priority``=``'auto'``,`` ``*``,`` ``prefer_public``=``False``)` [¶](#openquantum_sdk.clients.select_plan_and_priority "Permanent link")

Pick an execution plan and queue priority from a preparation quote.

`"auto"` minimizes total cost (base price + priority increase), then base price. Friendly names (`"public"`, `"private"`, `"standard"`, `"priority"`, `"instant"`), `ExecutionPlanType` / `QueuePriorityType` members, and raw UUIDs select that option exactly.

`prefer_public` only affects `execution_plan="auto"`: Public plans are ranked ahead of Private ones, then the cheapest pair inside that group wins. The MCP server sets this so Spark credits can apply. The default (`False`) keeps the historical cheapest-plan behavior used by `submit_job`.

Raises:

[TABLE]

### OpenQuantumClient

Framework-agnostic session used by PennyLane, Cirq, Qrisp, and the MCP server. `from_env()` resolves environment credentials and the playbook URL variables and does not autoload a saved account.

## `openquantum_sdk.session.OpenQuantumClient` [¶](#openquantum_sdk.session.OpenQuantumClient "Permanent link")

Authenticated session holding a management + scheduler client pair.

Authentication is resolved in this order:

1.  An explicit `token` or `creds` argument.
2.  A saved account on disk (autoloaded when neither is given and `auto_load` is true). Set `OPENQUANTUM_NO_AUTOLOAD=1` or `auto_load=False` to disable. `OPENQUANTUM_ACCOUNT_NAME` selects the account (default `"default"`).

Environment-variable credential resolution (`OPENQUANTUM_TOKEN` etc.) is intentionally *not* performed in `__init__`. Callers that want env credentials and service URLs without a saved-account autoload should use :meth:`from_env`. This keeps autoload and explicit-env behavior separable.

Use as a context manager to close HTTP sessions on exit.

### `from_env``(``*``,`` ``token``=``None``,`` ``creds``=``None``,`` ``client_id``=``None``,`` ``client_secret``=``None``,`` ``sdk_key_path``=``None``,`` ``keycloak_base``=``None``,`` ``realm``=``None``,`` ``scheduler_url``=``None``,`` ``management_url``=``None``,`` ``require``=``True``,`` ``**``kwargs``)`  `classmethod`  [¶](#openquantum_sdk.session.OpenQuantumClient.from_env "Permanent link")

Build a client from arguments and environment variables.

Does **not** autoload a saved account. Credential resolution uses :func:`openquantum_sdk.credentials.resolve_env_credentials`. Service URLs fall back to `OPENQUANTUM_SCHEDULER_URL` / `OPENQUANTUM_MANAGEMENT_URL` / `OPENQUANTUM_KEYCLOAK_BASE` / `OPENQUANTUM_KEYCLOAK_REALM`, then the production defaults.

When `require` is true (the default) and no credential resolves, raises :class:`~openquantum_sdk.exceptions.AuthenticationError`. Pass an already-resolved `creds` or `token` to skip env lookup.

### `organizations``()` [¶](#openquantum_sdk.session.OpenQuantumClient.organizations "Permanent link")

List organizations the authenticated user belongs to.

### `backends``(``*``,`` ``name``=``None``,`` ``online``=``None``,`` ``device_type``=``None``,`` ``vendor_id``=``None``,`` ``min_num_qubits``=``None``,`` ``limit``=``50``)` [¶](#openquantum_sdk.session.OpenQuantumClient.backends "Permanent link")

List available backend classes with optional client-side filtering.

Returns a list of dicts with `id`, `name`, `description`, `type`, `provider_id`, `short_code`, `queue_depth`, `accepting_jobs`, and `status`.

### `login``(``*``,`` ``token``=``None``,`` ``creds``=``None``,`` ``save``=``False``,`` ``name``=``'default'``,`` ``filename``=``None``,`` ``**``kwargs``)`  `classmethod`  [¶](#openquantum_sdk.session.OpenQuantumClient.login "Permanent link")

Authenticate and return a client, optionally saving the credentials.

### `close``()` [¶](#openquantum_sdk.session.OpenQuantumClient.close "Permanent link")

Close the underlying HTTP sessions.

### ManagementClient

## `ManagementClient` [¶](#openquantum_sdk.clients.ManagementClient "Permanent link")

Bases: `BaseClient`

Client for the OpenQuantum Management API.

Provides backend discovery, provider listing, and organization lookup. The management API is read-only and does not require an organization context.

Example

> > > from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth auth = ClientCredentialsAuth( ... creds=ClientCredentials(client_id="s\_...", client_secret="...") ... ) mgmt = ManagementClient(auth=auth) backends = mgmt.list_backend_classes()

### `list_backend_classes` [¶](#openquantum_sdk.clients.ManagementClient.list_backend_classes "Permanent link")

List available backend classes (QPUs and simulators).

Returns:

[TABLE]

### `list_providers` [¶](#openquantum_sdk.clients.ManagementClient.list_providers "Permanent link")

List quantum hardware providers on the platform.

Returns:

[TABLE]

### `list_user_organizations` [¶](#openquantum_sdk.clients.ManagementClient.list_user_organizations "Permanent link")

List organizations the authenticated user belongs to.

Returns:

[TABLE]

### JobSubmissionConfig

## `openquantum_sdk.clients.JobSubmissionConfig`  `dataclass`  [¶](#openquantum_sdk.clients.JobSubmissionConfig "Permanent link")

Configuration for submitting a job via `SchedulerClient.submit_job()`.

This dataclass bundles every option needed to upload a circuit, prepare a quote, and submit the job in a single call.

Parameters:

[TABLE]

Example

> > > config = JobSubmissionConfig( ... backend_class_id="ionq:aria-1", ... name="Bell State", ... job_subcategory_id="phys:oth", ... shots=1024, ... ) job = scheduler.submit_job(config, file_path="circuit.qasm")

### Authentication

## `openquantum_sdk.auth.ClientCredentialsAuth` [¶](#openquantum_sdk.auth.ClientCredentialsAuth "Permanent link")

Keycloak client-credentials OAuth2 helper with thread-safe token caching.

Manages the full token lifecycle: initial fetch, automatic refresh when the token is within `leeway_seconds` of expiry, and forced refresh on 401 retries. All token operations are thread-safe.

The token endpoint is constructed as: `{keycloak_base}/realms/{realm}/protocol/openid-connect/token`

### `token_endpoint`  `property`  [¶](#openquantum_sdk.auth.ClientCredentialsAuth.token_endpoint "Permanent link")

The full Keycloak token endpoint URL for this realm.

### `__init__``(``creds``,`` ``keycloak_base``=``'https://id.openquantum.com'``,`` ``realm``=``'platform'``,`` ``scope``=``None``,`` ``leeway_seconds``=``30``,`` ``session``=``None``)` [¶](#openquantum_sdk.auth.ClientCredentialsAuth.__init__ "Permanent link")

Initialize the auth helper.

Parameters:

[TABLE]

### `apply_auth_header``(``headers``)` [¶](#openquantum_sdk.auth.ClientCredentialsAuth.apply_auth_header "Permanent link")

Add a Bearer authorization header using the current access token.

Does not mutate the input dict; returns a new dict with the `Authorization` header added.

Parameters:

[TABLE]

Returns:

[TABLE]

### `get_access_token``(``force``=``False``)` [¶](#openquantum_sdk.auth.ClientCredentialsAuth.get_access_token "Permanent link")

Return a valid access token, refreshing if needed.

Uses double-checked locking to ensure only one thread fetches a new token at a time.

Parameters:

[TABLE]

Returns:

[TABLE]

Raises:

[TABLE]

## `openquantum_sdk.auth.ClientCredentials`  `dataclass`  [¶](#openquantum_sdk.auth.ClientCredentials "Permanent link")

SDK key credentials for machine-to-machine authentication.

Attributes:

[TABLE]

### Models

## `openquantum_sdk.models.APIError` [¶](#openquantum_sdk.models.APIError "Permanent link")

Bases: [`OpenQuantumError`](#openquantum_sdk.exceptions.OpenQuantumError "OpenQuantumError (openquantum_sdk.exceptions.OpenQuantumError)")

Exception raised when the Open Quantum API returns an error response.

Wraps an `ErrorResponse` and produces a human-readable message that includes the status code, error messages, and request ID.

Attributes:

[TABLE]

### Exceptions

The shared exception hierarchy raised across the SDK and all framework plugins. Catch `OpenQuantumError` to handle any Open Quantum failure uniformly.

## `openquantum_sdk.exceptions` [¶](#openquantum_sdk.exceptions "Permanent link")

Exception hierarchy for the Open Quantum SDK and its framework plugins.

Everything the SDK or a plugin raises derives from :class:`OpenQuantumError`, so `except OpenQuantumError` catches any Open Quantum failure regardless of which framework surface produced it. Below the root are a small set of *semantic* errors, caught by the kind of failure rather than by framework:

- :class:`AuthenticationError` -- missing or invalid credentials.
- :class:`CircuitValidationError` -- the circuit cannot be serialized or is not accepted by the target backend (unsupported gate, missing measurement, bad structure).
- :class:`JobError` -- a submitted job failed, was cancelled, or returned a result the client could not interpret.

`APIError` (raised for HTTP-level API responses) is reparented onto this root in :mod:`openquantum_sdk.models`, so it too is an `OpenQuantumError`.

Simple argument validation (an empty backend, a bad `export_format`) stays a plain :class:`ValueError`, matching normal Python convention.

### `AuthenticationError` [¶](#openquantum_sdk.exceptions.AuthenticationError "Permanent link")

Bases: [`OpenQuantumError`](#openquantum_sdk.exceptions.OpenQuantumError "OpenQuantumError (openquantum_sdk.exceptions.OpenQuantumError)")

Raised when credentials are missing or cannot authenticate the client.

### `CircuitValidationError` [¶](#openquantum_sdk.exceptions.CircuitValidationError "Permanent link")

Bases: [`OpenQuantumError`](#openquantum_sdk.exceptions.OpenQuantumError "OpenQuantumError (openquantum_sdk.exceptions.OpenQuantumError)")

Raised when a circuit cannot be serialized or is rejected by the backend.

### `JobError` [¶](#openquantum_sdk.exceptions.JobError "Permanent link")

Bases: [`OpenQuantumError`](#openquantum_sdk.exceptions.OpenQuantumError "OpenQuantumError (openquantum_sdk.exceptions.OpenQuantumError)")

Raised when a job fails, is cancelled, or returns an unreadable result.

### `OpenQuantumError` [¶](#openquantum_sdk.exceptions.OpenQuantumError "Permanent link")

Bases: `Exception`

Base class for every error raised by the Open Quantum SDK and plugins.

## Qiskit Plugin

### QASM export

Public helper. Import `export_circuit_to_qasm` from `openquantum_sdk_qiskit`, not from the private `_qasm` module.

## `openquantum_sdk_qiskit``.``export_circuit_to_qasm``(``circuit``,`` ``fmt``,`` ``*``,`` ``backend``=``None``)` [¶](#openquantum_sdk_qiskit.export_circuit_to_qasm "Permanent link")

Export a circuit to QASM, optionally validating against a backend first.

If `backend` is provided and has a `validate_circuit` method, it will be called before export. This provides early, capability-aware rejection (custom gates, shot limits when combined with higher-level callers, etc.).

### OpenQuantumService

## `openquantum_sdk_qiskit.oq_service.OpenQuantumService` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService "Permanent link")

Bases: [`OpenQuantumClient`](#openquantum_sdk.session.OpenQuantumClient "openquantum_sdk.session.OpenQuantumClient")

Entry point for the OpenQuantum Qiskit plugin.

Inherits authentication, saved-account management, and backend/organization discovery from [`OpenQuantumClient`](#openquantum_sdk.session.OpenQuantumClient "openquantum_sdk.session.OpenQuantumClient"), and adds the Qiskit-specific factories: building a Qiskit `Target` or `BackendV2` for a device, and creating Sampler / Estimator primitives that submit jobs to the OpenQuantum platform.

The service can be instantiated directly with a `token` or `creds`, loaded from a saved account on disk, or created via the convenience :meth:`login` classmethod. When neither `token` nor `creds` is supplied the constructor attempts to auto-load the saved account named by `OPENQUANTUM_ACCOUNT_NAME` (default `"default"`). If that account is missing or cannot be loaded, it falls back to :func:`openquantum_sdk.credentials.resolve_env_credentials` (`OPENQUANTUM_TOKEN`, an SDK key file, or `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET`). Set `OPENQUANTUM_NO_AUTOLOAD=1` or `auto_load=False` to skip the saved account and use only those environment credentials.

Use as a context manager to close HTTP sessions on exit.

Example

``` python
from openquantum_sdk_qiskit import OpenQuantumService

service = OpenQuantumService(token="oq_tok_...")
backends = service.backends(online=True)
backend = service.return_backend("rigetti:ankaa-3")
sampler = service.create_sampler(backend=backend, job_subcategory_id="oth:oth")
service.close()
```

Attributes:

[TABLE]

### `__init__``(``*``,`` ``token``=``None``,`` ``creds``=``None``,`` ``keycloak_base``=``DEFAULT_KEYCLOAK_BASE``,`` ``realm``=``DEFAULT_REALM``,`` ``scheduler_url``=``DEFAULT_SCHEDULER_URL``,`` ``management_url``=``DEFAULT_MANAGEMENT_URL``,`` ``auto_load``=``True``,`` ``account_name``=``None``,`` ``accounts_file``=``None``)` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService.__init__ "Permanent link")

### `return_backend``(``name``,`` ``*``,`` ``config``=``None``,`` ``export_format``=``'qasm3'``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``)` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService.return_backend "Permanent link")

Create an `OpenQuantumBackend` (Qiskit `BackendV2`) for `name`.

The returned backend works with Qiskit's transpiler and can submit circuits via its :meth:`~OpenQuantumBackend.run` method.

Parameters:

[TABLE]

Raises:

[TABLE]

### `return_target``(``name``)` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService.return_target "Permanent link")

Build a Qiskit `Target` for the named backend.

The `Target` describes the backend's native gate set, qubit count, and coupling map, and is used by the Qiskit transpiler.

Parameters:

[TABLE]

Raises:

[TABLE]

### `create_sampler``(``*``,`` ``backend``,`` ``organization_id``=``None``,`` ``job_subcategory_id``=``'oth:oth'``,`` ``name``=``None``,`` ``configuration_data``=``None``,`` ``execution_plan``=``'auto'``,`` ``queue_priority``=``'auto'``,`` ``export_format``=``'qasm3'``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``)` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService.create_sampler "Permanent link")

Create an :class:`OQSampler` (Qiskit `SamplerV2`) backed by OpenQuantum.

Parameters:

[TABLE]

Raises:

[TABLE]

### `create_estimator``(``*``,`` ``backend``,`` ``organization_id``=``None``,`` ``job_subcategory_id``=``'oth:oth'``,`` ``name``=``None``,`` ``configuration_data``=``None``,`` ``execution_plan``=``'auto'``,`` ``queue_priority``=``'auto'``,`` ``export_format``=``'qasm3'``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``)` [¶](#openquantum_sdk_qiskit.oq_service.OpenQuantumService.create_estimator "Permanent link")

Create an :class:`OQEstimator` (Qiskit `EstimatorV2`) backed by OpenQuantum.

Arguments mirror :meth:`create_sampler`.

Raises:

[TABLE]

### OpenQuantumBackend

## `openquantum_sdk_qiskit.oq_backend.OpenQuantumBackend` [¶](#openquantum_sdk_qiskit.oq_backend.OpenQuantumBackend "Permanent link")

Bases: `BackendV2`

Qiskit `BackendV2` implementation for the OpenQuantum platform.

Wraps the OpenQuantum scheduler so that circuits can be submitted and results retrieved through the standard Qiskit backend interface. The backend's `Target` (native gate set, coupling map, qubit count) is derived from a capabilities dictionary that is either supplied explicitly or resolved from built-in data.

This backend is typically obtained via :meth:`OpenQuantumService.return_backend` rather than constructed directly.

Example

``` python
backend = service.return_backend("rigetti:ankaa-3")
```

### `__init__``(``name``,`` ``*``,`` ``capabilities``=``None``,`` ``scheduler``=``None``,`` ``config``=``None``,`` ``export_format``=``'qasm3'``,`` ``configuration_schema``=``None``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``,`` ``**``kwargs``)` [¶](#openquantum_sdk_qiskit.oq_backend.OpenQuantumBackend.__init__ "Permanent link")

Initialise the backend.

Parameters:

[TABLE]

Raises:

[TABLE]

### `run``(``circuits``,`` ``/``,`` ``*``,`` ``job_subcategory_id``=``None``,`` ``backend_class_id``=``None``,`` ``organization_id``=``None``,`` ``name``=``None``,`` ``configuration_data``=``None``,`` ``execution_plan``=``None``,`` ``queue_priority``=``None``,`` ``**``run_options``)` [¶](#openquantum_sdk_qiskit.oq_backend.OpenQuantumBackend.run "Permanent link")

Submit one or more circuits to the OpenQuantum platform.

Each circuit is serialised to QASM, submitted to the scheduler, and the results are downloaded synchronously. The method returns immediately with a job-like wrapper around the collected `Result`.

Job submission metadata (job_subcategory_id, etc.) can be supplied here at the point of job creation, or as defaults via the config passed to the backend constructor.

Parameters:

[TABLE]

Returns:

[TABLE]

Raises:

[TABLE]

### OQSampler (SamplerV2)

## `openquantum_sdk_qiskit.oq_sampler.OQSampler` [¶](#openquantum_sdk_qiskit.oq_sampler.OQSampler "Permanent link")

Bases: `BaseSamplerV2`

Qiskit `SamplerV2` implementation backed by the OpenQuantum platform.

Submits sampling PUBs (Primitive Unified Blocs) to the OpenQuantum scheduler and returns results using Qiskit's primitives containers (`DataBin`, `BitArray`, `SamplerPubResult`, `PrimitiveResult`).

Typically obtained via :meth:`OpenQuantumService.create_sampler` rather than constructed directly.

Example

``` python
sampler = service.create_sampler(
    backend=backend,
    job_subcategory_id="oth:oth",
)
pub = (circuit, shots)
job = sampler.run([pub])
result = job.result()
```

### `__init__``(``*``,`` ``backend``,`` ``options``=``None``,`` ``scheduler``=``None``,`` ``config``=``None``,`` ``export_format``=``'qasm3'``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``)` [¶](#openquantum_sdk_qiskit.oq_sampler.OQSampler.__init__ "Permanent link")

Initialise the sampler.

Parameters:

[TABLE]

Raises:

[TABLE]

### `run``(``pubs``,`` ``*``,`` ``shots``=``None``,`` ``export_format``=``None``)` [¶](#openquantum_sdk_qiskit.oq_sampler.OQSampler.run "Permanent link")

Submit sampling PUBs to the OpenQuantum platform.

Each PUB's circuit is serialised, parameter-bound, and submitted to the scheduler. Results are collected and returned as Qiskit `SamplerPubResult` objects containing `BitArray` measurement data.

Parameters:

[TABLE]

Returns:

[TABLE]

Raises:

[TABLE]

### OQEstimator (EstimatorV2)

## `openquantum_sdk_qiskit.oq_estimator.OQEstimator` [¶](#openquantum_sdk_qiskit.oq_estimator.OQEstimator "Permanent link")

Bases: `BaseEstimatorV2`

Qiskit `EstimatorV2` implementation backed by the OpenQuantum platform.

Computes expectation values of observables by delegating to Qiskit's `BackendEstimatorV2` with an :class:`OpenQuantumBackend` that submits circuits to the OpenQuantum scheduler.

Typically obtained via :meth:`OpenQuantumService.create_estimator` rather than constructed directly.

Example

``` python
estimator = service.create_estimator(
    backend=backend,
    job_subcategory_id="oth:oth",
)
pub = (circuit, observable)
job = estimator.run([pub])
result = job.result()
```

### `__init__``(``*``,`` ``backend``,`` ``options``=``None``,`` ``scheduler``=``None``,`` ``config``=``None``,`` ``export_format``=``'qasm3'``,`` ``verbose``=``None``,`` ``job_timeout_seconds``=``None``)` [¶](#openquantum_sdk_qiskit.oq_estimator.OQEstimator.__init__ "Permanent link")

Initialise the estimator.

Internally creates a shallow copy of the supplied `backend` and injects the `scheduler` and `config` into it, then wraps it with Qiskit's `BackendEstimatorV2` to handle observable decomposition and expectation-value computation.

The backend proxy's `run` method is patched to fully transpile measurement-basis circuits into the device native gate set before submission (see module-level note on `BackendEstimatorV2`).

Parameters:

[TABLE]

### `run``(``pubs``,`` ``*``,`` ``precision``=``None``)` [¶](#openquantum_sdk_qiskit.oq_estimator.OQEstimator.run "Permanent link")

Estimate expectation values for one or more PUBs.

Delegates to the internal `BackendEstimatorV2` which decomposes observables, executes the required circuits on the OpenQuantum backend, and combines shot results into expectation-value estimates.

Parameters:

[TABLE]

Returns:

[TABLE]

## PennyLane Plugin

### Device

## `pennylane_openquantum.device.OpenQuantumDevice` [¶](#pennylane_openquantum.device.OpenQuantumDevice "Permanent link")

Bases: `Device`

PennyLane device for the OpenQuantum quantum computing platform.

Authenticates via one of three methods (checked in order): 1. A pre-built `OpenQuantumClient` passed as `client`. 2. A bearer `token` (e.g. from `OPENQUANTUM_TOKEN`). 3. `client_id` + `client_secret` for the OAuth2 client-credentials flow (env vars `OPENQUANTUM_CLIENT_ID` / `OPENQUANTUM_CLIENT_SECRET`).

Parameters:

[TABLE]

### `__init__``(``wires``,`` ``shots``=``None``,`` ``backend``=``''``,`` ``*``,`` ``auto_confirm``=``False``,`` ``client``=``None``,`` ``token``=``None``,`` ``client_id``=``None``,`` ``client_secret``=``None``,`` ``organization_id``=``None``,`` ``scheduler_url``=``None``,`` ``management_url``=``None``,`` ``keycloak_base``=``None``,`` ``realm``=``None``,`` ``job_subcategory_id``=``'oth:oth'``,`` ``execution_plan``=``'auto'``,`` ``queue_priority``=``'auto'``,`` ``configuration_data``=``None``,`` ``verbose``=``False``,`` ``job_timeout_seconds``=``86400``)` [¶](#pennylane_openquantum.device.OpenQuantumDevice.__init__ "Permanent link")

### `execute``(``circuits``,`` ``execution_config``=``ExecutionConfig``())` [¶](#pennylane_openquantum.device.OpenQuantumDevice.execute "Permanent link")

Execute one or more circuits on the OpenQuantum platform.

Before submitting: - Checks the target backend status and queue depth. - If the backend is offline or not accepting jobs, shows online alternatives and prompts for confirmation. - Prints a live updating status line during job execution.

Parameters:

[TABLE]

Returns:

[TABLE]

Raises:

[TABLE]

### `preprocess``(``execution_config``=``ExecutionConfig``())` [¶](#pennylane_openquantum.device.OpenQuantumDevice.preprocess "Permanent link")

Build the preprocessing transform program.

### QASM Serializer

## `pennylane_openquantum.qasm_serializer` [¶](#pennylane_openquantum.qasm_serializer "Permanent link")

PennyLane tape to OpenQASM 2.0 serialization.

This module converts PennyLane quantum tapes into OpenQASM 2.0 program strings. It uses `OPERATION_MAP` to translate PennyLane gate names (e.g. `"PauliX"`, `"CNOT"`) to their OpenQASM 2.0 gate identifiers (e.g. `"x"`, `"cx"`).

When backend capabilities are provided, gates that the backend supports are emitted directly without inline definitions. Otherwise, gates not known by the backend parser are emitted as inline `gate` definitions in terms of u1/u2/u3/cx/ccx.

### `OPERATION_MAP`` ``=`` ``{``'PauliX'``:`` ``'x'``,`` ``'PauliY'``:`` ``'y'``,`` ``'PauliZ'``:`` ``'z'``,`` ``'Hadamard'``:`` ``'h'``,`` ``'CNOT'``:`` ``'cx'``,`` ``'CZ'``:`` ``'cz'``,`` ``'SWAP'``:`` ``'swap'``,`` ``'RX'``:`` ``'rx'``,`` ``'RY'``:`` ``'ry'``,`` ``'RZ'``:`` ``'rz'``,`` ``'PhaseShift'``:`` ``'p'``,`` ``'S'``:`` ``'s'``,`` ``'T'``:`` ``'t'``,`` ``'SX'``:`` ``'sx'``,`` ``'Toffoli'``:`` ``'ccx'``,`` ``'CSWAP'``:`` ``'cswap'``,`` ``'CRX'``:`` ``'crx'``,`` ``'CRY'``:`` ``'cry'``,`` ``'CRZ'``:`` ``'crz'``,`` ``'Identity'``:`` ``'id'``}`  `module-attribute`  [¶](#pennylane_openquantum.qasm_serializer.OPERATION_MAP "Permanent link")

### `circuit_to_qasm``(``tape``,`` ``num_wires``,`` ``capabilities``=``None``)` [¶](#pennylane_openquantum.qasm_serializer.circuit_to_qasm "Permanent link")

Convert a PennyLane tape to an OpenQASM 2.0 string.

Parameters:

[TABLE]

Returns:

[TABLE]

Raises:

[TABLE]

### Exceptions

## `pennylane_openquantum.exceptions` [¶](#pennylane_openquantum.exceptions "Permanent link")

Custom exception classes for the Open Quantum PennyLane plugin.

### `OpenQuantumCircuitError` [¶](#pennylane_openquantum.exceptions.OpenQuantumCircuitError "Permanent link")

Bases: [`OpenQuantumDeviceError`](#pennylane_openquantum.exceptions.OpenQuantumDeviceError "OpenQuantumDeviceError (pennylane_openquantum.exceptions.OpenQuantumDeviceError)")

Raised when circuit serialization or validation fails.

Common causes include unsupported gate operations or invalid circuit structure that cannot be converted to OpenQASM 2.0.

### `OpenQuantumDeviceError` [¶](#pennylane_openquantum.exceptions.OpenQuantumDeviceError "Permanent link")

Bases: [`OpenQuantumError`](#openquantum_sdk.exceptions.OpenQuantumError "OpenQuantumError (openquantum_sdk.exceptions.OpenQuantumError)")

Base exception for Open Quantum PennyLane device errors.

Raised for device-level issues such as invalid device configuration. Missing credentials raise :class:`openquantum_sdk.exceptions.AuthenticationError` instead, matching the other plugins. Subclasses :class:`openquantum_sdk.exceptions.OpenQuantumError`, so callers can catch any Open Quantum failure uniformly.

## Cirq Plugin

### OpenQuantumSampler

## `cirq_openquantum.sampler.OpenQuantumSampler` [¶](#cirq_openquantum.sampler.OpenQuantumSampler "Permanent link")

Bases: `Sampler`

Cirq sampler that executes circuits on the Open Quantum platform.

Use it anywhere a `cirq.Sampler` is accepted::

```
sampler = OpenQuantumSampler(
    backend="qr:gpu-gb10",
    configuration_data={"engine": "amber_quantum_rings"},
)
result = sampler.run(circuit, repetitions=1024)
print(result.histogram(key="m"))
```

Authentication mirrors the other Open Quantum plugins and is resolved in this order:

1.  A pre-built :class:`openquantum_sdk.OpenQuantumClient` passed as `client` (full control over auth, URLs, saved accounts).
2.  A bearer `token` (falls back to `OPENQUANTUM_TOKEN`).
3.  `client_id` + `client_secret` for the OAuth2 client-credentials flow (fall back to `OPENQUANTUM_CLIENT_ID` / `OPENQUANTUM_CLIENT_SECRET`).

Parameters:

[TABLE]

### `backend`  `property`  [¶](#cirq_openquantum.sampler.OpenQuantumSampler.backend "Permanent link")

Alias for :attr:`backend_class_id` (matches the other plugins).

### `backend_class_id`  `property`  [¶](#cirq_openquantum.sampler.OpenQuantumSampler.backend_class_id "Permanent link")

The Open Quantum backend class ID or short_code this sampler targets.

### `run_sweep``(``program``,`` ``params``,`` ``repetitions``=``1``)` [¶](#cirq_openquantum.sampler.OpenQuantumSampler.run_sweep "Permanent link")

Submit a circuit once per parameter resolver and collect results.

Implementing `run_sweep` gives `run`, `sample`, `run_async`, and `run_batch` for free (Cirq's `Sampler` routes them all here).

Parameters:

[TABLE]

Returns:

[TABLE]

### Result Helpers

## `cirq_openquantum``.``result``.``result_from_counts``(``counts``,`` ``circuit``,`` ``params``=``None``,`` ``*``,`` ``reverse_bits``=``False``,`` ``qasm``=``None``)` [¶](#cirq_openquantum.result.result_from_counts "Permanent link")

Reconstruct a `cirq.ResultDict` from a platform counts histogram.

Parameters:

[TABLE]

Returns:

[TABLE]

## Qrisp Plugin

### OpenQuantumBackend

## `qrisp_openquantum.backend.OpenQuantumBackend` [¶](#qrisp_openquantum.backend.OpenQuantumBackend "Permanent link")

Bases: `Backend`

Qrisp backend that executes circuits on the Open Quantum platform.

Pass an instance to any Qrisp execution call, e.g. `qv.get_measurement(backend=oq, shots=1024)` or `qc.run(backend=oq, shots=1024)`.

Authentication mirrors the other Open Quantum plugins and is resolved in this order:

1.  A pre-built :class:`openquantum_sdk_qiskit.OpenQuantumService` passed as `service` (full control over auth, URLs, saved accounts).
2.  A bearer `token` (falls back to `OPENQUANTUM_TOKEN`).
3.  `client_id` + `client_secret` for the OAuth2 client-credentials flow (fall back to `OPENQUANTUM_CLIENT_ID` / `OPENQUANTUM_CLIENT_SECRET`).

Parameters:

[TABLE]

### `backend`  `property`  [¶](#qrisp_openquantum.backend.OpenQuantumBackend.backend "Permanent link")

Alias for :attr:`backend_class_id` (matches the other plugins).

### `backend_class_id`  `property`  [¶](#qrisp_openquantum.backend.OpenQuantumBackend.backend_class_id "Permanent link")

The Open Quantum backend class ID or short_code targeted by this backend.

### `run_async``(``circuits``,`` ``shots``=``None``)` [¶](#qrisp_openquantum.backend.OpenQuantumBackend.run_async "Permanent link")

Submit one or more Qrisp circuits and return a completed job.

Each circuit is converted to a Qiskit circuit, validated against the backend's capabilities, serialised to QASM, and submitted to the platform synchronously.

Parameters:

[TABLE]

Returns:

[TABLE]

### OpenQuantumJob

## `qrisp_openquantum.job.OpenQuantumJob` [¶](#qrisp_openquantum.job.OpenQuantumJob "Permanent link")

Bases: `Job`

A completed Open Quantum job wrapping one counts dict per circuit.

Parameters:

[TABLE]

### `cancel``()` [¶](#qrisp_openquantum.job.OpenQuantumJob.cancel "Permanent link")

Jobs are already terminal when returned, so there is nothing to cancel.

### `result``(``timeout``=``None``)` [¶](#qrisp_openquantum.job.OpenQuantumJob.result "Permanent link")

Return the measurement results (job is already terminal).

### `status``()` [¶](#qrisp_openquantum.job.OpenQuantumJob.status "Permanent link")

Return the cached (terminal) status.
