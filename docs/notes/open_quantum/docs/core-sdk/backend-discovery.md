> Full piece: [https://docs.openquantum.com/core-sdk/backend-discovery/](https://docs.openquantum.com/core-sdk/backend-discovery/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1663029c04d4783b6309d830935baa75d723cb9dd7a6132b818f2c1dc341787d.

# Backend Discovery

The Core SDK's `ManagementClient` provides methods to list available backends and hardware providers.

## Listing Backends

[](#__codelineno-0-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-0-2)`from`` ``openquantum_sdk.clients`` ``import`` ``ManagementClient`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-0-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-0-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-0-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-0-8)`    ``),`\
[](#__codelineno-0-9)`)`\
[](#__codelineno-0-10)\
[](#__codelineno-0-11)`management`` ``=`` ``ManagementClient``(``auth``=``auth``)`\
[](#__codelineno-0-12)\
[](#__codelineno-0-13)`result`` ``=`` ``management``.``list_backend_classes``(``limit``=``20``)`\
[](#__codelineno-0-14)`for`` ``backend`` ``in`` ``result``.``backend_classes``:`\
[](#__codelineno-0-15)`    ``print``(``f``"``{``backend``.``short_code``}``: ``{``backend``.``name``}`` (``{``backend``.``type``}``) - ``{``backend``.``status``}``"``)`\

Example output:

[](#__codelineno-1-1)`ionq:forte-1: IonQ Forte-1 (QPU) - Online`\
[](#__codelineno-1-2)`rigetti:cepheus-1-108q: Rigetti Cepheus-1 (QPU) - Online`\

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

[](#__codelineno-2-1)`result`` ``=`` ``management``.``list_backend_classes``(``provider_id``=``"ionq"``)`\
[](#__codelineno-2-2)`for`` ``backend`` ``in`` ``result``.``backend_classes``:`\
[](#__codelineno-2-3)`    ``print``(``f``"``{``backend``.``short_code``}``: ``{``backend``.``name``}``"``)`\

## Listing Providers

[](#__codelineno-3-1)`result`` ``=`` ``management``.``list_providers``()`\
[](#__codelineno-3-2)`for`` ``provider`` ``in`` ``result``.``providers``:`\
[](#__codelineno-3-3)`    ``print``(``f``"``{``provider``.``short_code``}``: ``{``provider``.``name``}`` - ``{``provider``.``description``}``"``)`\

Each `ProviderRead` object has:

| Property      | Type  | Description              |
|---------------|-------|--------------------------|
| `id`          | `str` | Unique identifier (UUID) |
| `name`        | `str` | Provider name            |
| `description` | `str` | Provider description     |
| `short_code`  | `str` | Provider short code      |

## Pagination

Backend and provider listings use cursor-based pagination:

[](#__codelineno-4-1)`result`` ``=`` ``management``.``list_backend_classes``(``limit``=``10``)`\
[](#__codelineno-4-2)`while`` ``result``.``pagination``.``next_cursor``:`\
[](#__codelineno-4-3)`    ``result`` ``=`` ``management``.``list_backend_classes``(`\
[](#__codelineno-4-4)`        ``limit``=``10``,`\
[](#__codelineno-4-5)`        ``cursor``=``result``.``pagination``.``next_cursor``,`\
[](#__codelineno-4-6)`    ``)`\
[](#__codelineno-4-7)`    ``for`` ``backend`` ``in`` ``result``.``backend_classes``:`\
[](#__codelineno-4-8)`        ``print``(``backend``.``short_code``)`\

## Input formats

Each backend may advertise which circuit language families it accepts (via platform `constraint_data.supported_formats`). The SDK default is OpenQASM (`"qasm"`). Other formats are valid only when the backend lists them. Pass matching `input_format` when preparing a job — see [Job Submission → Input formats](https://docs.openquantum.com/core-sdk/job-submission/#input-formats).

## Convenience methods on the client

The Qiskit, Cirq, and Qrisp plugins expose an `OpenQuantumClient` (as `service` or `client`) that wraps these discovery APIs with simple, filtered helpers:

[](#__codelineno-5-1)`# Online backends that are accepting jobs, as plain dicts`\
[](#__codelineno-5-2)`for`` ``bc`` ``in`` ``client``.``backends``(``online``=``True``):`\
[](#__codelineno-5-3)`    ``print``(``bc``[``"short_code"``],`` ``bc``[``"type"``],`` ``bc``[``"status"``])`\
[](#__codelineno-5-4)\
[](#__codelineno-5-5)`# Filter to simulators, or to a single vendor`\
[](#__codelineno-5-6)`sims`` ``=`` ``client``.``backends``(``device_type``=``"Simulator"``)`\
[](#__codelineno-5-7)`ionq`` ``=`` ``client``.``backends``(``vendor_id``=``"ionq"``)`\
[](#__codelineno-5-8)\
[](#__codelineno-5-9)`# Organizations the authenticated user belongs to`\
[](#__codelineno-5-10)`for`` ``org`` ``in`` ``client``.``organizations``():`\
[](#__codelineno-5-11)`    ``print``(``org``[``"id"``],`` ``org``[``"name"``])`\

`backends()` accepts `name`, `online`, `device_type` (`"QPU"` or `"Simulator"`), `vendor_id`, and `limit`, and returns a list of dicts (`id`, `name`, `type`, `short_code`, `status`, `accepting_jobs`, …). `organizations()` returns `{id, name}` dicts.

## Related Pages

- [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Use a backend short code to submit a job.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Backend concepts and properties.
