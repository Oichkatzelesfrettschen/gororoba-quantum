> Full piece: [https://docs.openquantum.com/core-sdk/backend-discovery/](https://docs.openquantum.com/core-sdk/backend-discovery/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1663029c04d4783b6309d830935baa75d723cb9dd7a6132b818f2c1dc341787d.

# Backend Discovery

The Core SDK's `ManagementClient` provides methods to list available backends and hardware providers.

## Listing Backends

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

result = management.list_backend_classes(limit=20)
for backend in result.backend_classes:
    print(f"{backend.short_code}: {backend.name} ({backend.type}) - {backend.status}")
```

Example output:

```
ionq:forte-1: IonQ Forte-1 (QPU) - Online
rigetti:cepheus-1-108q: Rigetti Cepheus-1 (QPU) - Online
```

## Backend Properties

Each `BackendClassRead` object has the following fields:

| Property         | Type   | Description                                        |
|------------------|--------|----------------------------------------------------|
| `id`             | `str`  | Unique identifier (UUID)                           |
| `name`           | `str`  | Display name                                       |
| `description`    | `str`  | Backend description                                |
| `type`           | `str`  | `"QPU"`                                            |
| `provider_id`    | `str`  | Provider UUID                                      |
| `short_code`     | `str`  | Human-readable identifier (e.g., `"ionq:forte-1"`) |
| `queue_depth`    | `int`  | Number of jobs currently in the queue              |
| `accepting_jobs` | `bool` | Whether the backend is accepting new jobs          |
| `status`         | `str`  | `"Online"` or `"Offline"`                          |

## Filtering by Provider

Pass a `provider_id` to filter backends by hardware provider:

``` python
result = management.list_backend_classes(provider_id="ionq")
for backend in result.backend_classes:
    print(f"{backend.short_code}: {backend.name}")
```

## Listing Providers

``` python
result = management.list_providers()
for provider in result.providers:
    print(f"{provider.short_code}: {provider.name} - {provider.description}")
```

Each `ProviderRead` object has:

| Property      | Type  | Description              |
|---------------|-------|--------------------------|
| `id`          | `str` | Unique identifier (UUID) |
| `name`        | `str` | Provider name            |
| `description` | `str` | Provider description     |
| `short_code`  | `str` | Provider short code      |

## Pagination

Backend and provider listings use cursor-based pagination:

``` python
result = management.list_backend_classes(limit=10)
while result.pagination.next_cursor:
    result = management.list_backend_classes(
        limit=10,
        cursor=result.pagination.next_cursor,
    )
    for backend in result.backend_classes:
        print(backend.short_code)
```

## Input formats

Each backend may advertise which circuit language families it accepts (via platform `constraint_data.supported_formats`). The SDK default is OpenQASM (`"qasm"`). Other formats are valid only when the backend lists them. Pass matching `input_format` when preparing a job — see [Job Submission → Input formats](https://docs.openquantum.com/core-sdk/job-submission/#input-formats).

## Convenience methods on the client

The Qiskit, Cirq, and Qrisp plugins expose an `OpenQuantumClient` (as `service` or `client`) that wraps these discovery APIs with simple, filtered helpers:

``` python
# Online backends that are accepting jobs, as plain dicts
for bc in client.backends(online=True):
    print(bc["short_code"], bc["type"], bc["status"])

# Filter to simulators, or to a single vendor
sims = client.backends(device_type="Simulator")
ionq = client.backends(vendor_id="ionq")

# Organizations the authenticated user belongs to
for org in client.organizations():
    print(org["id"], org["name"])
```

`backends()` accepts `name`, `online`, `device_type` (`"QPU"` or `"Simulator"`), `vendor_id`, and `limit`, and returns a list of dicts (`id`, `name`, `type`, `short_code`, `status`, `accepting_jobs`, …). `organizations()` returns `{id, name}` dicts.

## Related Pages

- [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Use a backend short code to submit a job.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Backend concepts and properties.
