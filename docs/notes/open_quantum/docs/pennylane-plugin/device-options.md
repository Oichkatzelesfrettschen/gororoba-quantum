> Full piece: [https://docs.openquantum.com/pennylane-plugin/device-options/](https://docs.openquantum.com/pennylane-plugin/device-options/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7b7fc69adc06a0033fa9ea690e3221c449d57403041e7a9d27250903fc2e8032.

# Device Options

This page documents all parameters available when creating an `openquantum.device`.

## Basic Usage

``` python
import pennylane as qml

dev = qml.device(
    "openquantum.device",
    wires=4,
    shots=128,
    backend="ionq:forte-1",
)
```

## Required Parameters

| Parameter | Type | Description |
|----|----|----|
| `wires` | `int` | Number of qubits in the circuit. |
| `shots` | `int` | Number of measurement shots per circuit execution. Must be a positive integer. |
| `backend` | `str` | Backend short code identifying the target QPU (e.g., `"ionq:forte-1"`). |

Warning

`shots=None` (analytic mode) is not supported. Always specify a positive integer.

## Authentication Parameters

Authentication is resolved by `OpenQuantumClient.from_env()`. Constructor arguments take precedence over environment variables. The order is:

1.  A pre-built `client=` (`OpenQuantumClient`).
2.  `token=` or `OPENQUANTUM_TOKEN`.
3.  `client_id` + `client_secret`, or `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET`, or an SDK-key file at `OPENQUANTUM_SDK_KEY`.

If none of those resolve, constructing the device raises `AuthenticationError`. The parameter used to be `scheduler=` (a raw `SchedulerClient`). Pass `client=` instead.

| Parameter | Type | Default | Description |
|----|----|----|----|
| `client` | `OpenQuantumClient` | `None` | Pre-built client. When set, credential and URL arguments are ignored. |
| `token` | `str` | `None` | Bearer token. Falls back to `OPENQUANTUM_TOKEN`. |
| `client_id` | `str` | `None` | SDK key Client ID. Falls back to `OPENQUANTUM_CLIENT_ID`. |
| `client_secret` | `str` | `None` | SDK key Client Secret. Falls back to `OPENQUANTUM_CLIENT_SECRET`. |
| `scheduler_url` | `str` | production scheduler URL | Scheduler API base. Falls back to `OPENQUANTUM_SCHEDULER_URL`. |
| `management_url` | `str` | production management URL | Management API base. Falls back to `OPENQUANTUM_MANAGEMENT_URL`. |
| `keycloak_base` | `str` | production identity URL | Keycloak base. Falls back to `OPENQUANTUM_KEYCLOAK_BASE`. |
| `realm` | `str` | `"platform"` | Keycloak realm. Falls back to `OPENQUANTUM_KEYCLOAK_REALM`. |

## Cost Control and Cancellation

Before executing circuits, the device:

1.  **Checks backend status** — with `verbose=True`, shows whether the target QPU is online and its queue depth. If it is offline, lists alternatives and (unless `auto_confirm=True`) asks before continuing.
2.  **Shows credit cost** — prepares the first circuit to get a real quote. The cost is printed when `verbose=True`, and also whenever the confirmation prompt is shown.
3.  **Prompts for confirmation** (terminal only) — asks `Proceed? [y/N]`. In Jupyter notebooks, execution proceeds immediately.
4.  **Live status updates** — with `verbose=True`, shows a spinner with job status. While the job is pending, you can interrupt (Ctrl+C or Jupyter stop button) to cancel it on the platform. Once queued, it can no longer be cancelled. The wait stops after `job_timeout_seconds`.

| Parameter | Type | Default | Description |
|----|----|----|----|
| `auto_confirm` | `bool` | `False` | If `True`, skip the confirmation prompt (terminal) and backend-unavailable warnings. |
| `verbose` | `bool` | `False` | Print submission progress and the credit cost. Same default on every Open Quantum plugin. |

``` python
# Default: prints the cost and prompts in the terminal. No status spinner.
dev = qml.device("openquantum.device", wires=2, shots=128, backend="ionq:forte-1")
# Output:
#   [Open Quantum] Batch: 1 circuit(s) × 2 credit(s) each = 2 credit(s) total
#   [Open Quantum] Proceed? [y/N]

# Skip prompts and stay quiet (recommended for iterative algorithms)
dev = qml.device("openquantum.device", wires=2, shots=128, backend="ionq:forte-1",
                  auto_confirm=True)
# No progress lines. dev.total_credits_used still updates.

# Skip the prompt but print progress and the credit cost
dev = qml.device("openquantum.device", wires=2, shots=128, backend="ionq:forte-1",
                  auto_confirm=True, verbose=True)
```

You can check cumulative credits spent at any time:

``` python
print(dev.total_credits_used)  # e.g., 160
```

Cancelling in Jupyter

In Jupyter notebooks, the confirmation prompt is skipped (since `input()` can hang). Instead, you can cancel a pending job by pressing the stop button (⬜) or using Kernel \> Interrupt. The device will attempt to cancel the job on the platform. Once the job moves to "Queued", it can no longer be cancelled.

## Optional Parameters

| Parameter | Type | Default | Description |
|----|----|----|----|
| `organization_id` | `str` | `None` | Organization UUID. Falls back to `OPENQUANTUM_ORGANIZATION_ID`. If that is also unset, the SDK uses the first organization on the account and warns when there are several. |
| `execution_plan` | `str` | `"auto"` | `"auto"`, `"public"`, `"private"`, an `ExecutionPlanType` value, or a plan UUID. `"auto"` selects the cheapest available plan. |
| `queue_priority` | `str` | `"auto"` | `"auto"`, `"standard"`, `"priority"`, `"instant"`, a `QueuePriorityType` value, or a priority UUID. `"auto"` selects the cheapest priority. |
| `job_subcategory_id` | `str` | `"oth:oth"` | Job subcategory short code. The full list of allowed ids can be retrieved using the `SchedulerClient`. |
| `configuration_data` | `dict` | `None` | Backend-specific job configuration merged into every submission (e.g. `{"engine": "amber_quantum_rings"}` for Quantum Rings simulators). `shots` is always set automatically. |
| `job_timeout_seconds` | `int` | `86400` | Maximum time in seconds to wait for a job to complete. |

### Listing Categories

``` python
from openquantum_sdk.clients import SchedulerClient
scheduler = SchedulerClient(auth=auth)

categories = scheduler.get_job_categories()
for cat in categories.categories:
    print(f"{cat.id}: {cat.name} ({cat.short_code})")

    subcategories = scheduler.get_job_subcategories(category_id=cat.id)
    for sub in subcategories.categories:
        print(f"  {sub.id}: {sub.name} ({sub.short_code})")
```

## Environment Variable Reference

| Environment Variable | Corresponding Parameter | Description |
|----|----|----|
| `OPENQUANTUM_TOKEN` | `token` | Bearer token |
| `OPENQUANTUM_CLIENT_ID` | `client_id` | SDK key Client ID |
| `OPENQUANTUM_CLIENT_SECRET` | `client_secret` | SDK key Client Secret |
| `OPENQUANTUM_SDK_KEY` | — | Path to a JSON file with `client_id` and `client_secret` |
| `OPENQUANTUM_ORGANIZATION_ID` | `organization_id` | Organization UUID |
| `OPENQUANTUM_SCHEDULER_URL` | `scheduler_url` | Scheduler API base |
| `OPENQUANTUM_MANAGEMENT_URL` | `management_url` | Management API base |
| `OPENQUANTUM_KEYCLOAK_BASE` | `keycloak_base` | Keycloak base |
| `OPENQUANTUM_KEYCLOAK_REALM` | `realm` | Keycloak realm |

## Configuration Examples

### Minimal (credentials from environment)

``` python
dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=128,
    backend="ionq:forte-1",
)
```

### Explicit credentials

``` python
dev = qml.device(
    "openquantum.device",
    wires=4,
    shots=2048,
    backend="ionq:forte-1",
    client_id="s_abc123def456",
    client_secret="your_secret_here",
    organization_id="550e8400-e29b-41d4-a716-446655440000",
)
```

### Auto-confirm for iterative algorithms

``` python
dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=4096,
    backend="ionq:forte-1",
    auto_confirm=True,  # skip prompt on every VQE step
)
```

## Related Pages

- [Authentication](https://docs.openquantum.com/core-sdk/authentication/) -- How to set up credentials.
- [Supported Operations](https://docs.openquantum.com/pennylane-plugin/supported-operations/) -- Available gates and measurements.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- How execution plans and priorities affect pricing.
