> Full piece: [https://docs.qbraid.com/v2/api-reference/user-guide/overview.md](https://docs.qbraid.com/v2/api-reference/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 4c2532fb49f43e7497fc217f28d898b3e6562f2d612de700b15667dcaadab30f.

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

# Overview

> Learn to work with qBraid APIs

The qBraid REST API provides authenticated endpoints for devices, jobs, credits, and usage. The reference pages document JSON request and response formats. The separate [AI Gateway](https://docs.qbraid.com/v2/ai/integrations/ai-gateway) also supports streaming responses.

<Warning>
  This API is designed for server-to-server use. Browser (cross-origin) requests
  are restricted to an allowlist of qBraid origins, so calling the API directly
  from a web page on your own domain is blocked by CORS. Call it from your
  backend instead, where your API key also stays out of client-side code.
</Warning>

## OpenAPI specification

The machine-readable definition of the documented REST endpoints is available as an
[OpenAPI 3.1 document](https://docs.qbraid.com/openapi-v2.json). Download it to generate client
libraries, import the API into tools like Postman or Insomnia, or hand it to an
AI agent as a compact description of the documented endpoints, parameters, and responses. Platform features outside this specification have separate guides, including the AI Gateway.

## Quantum job flow

The diagram shows how an application converts a quantum program to an intermediate representation (IR), submits it through the qBraid API, and receives results from a quantum backend.

<img
  src="/v2/api-reference/_static/qbraid-runtime-api.png"
  alt="qBraid Runtime API Server"
  className="block dark:hidden"
/>
<img
  src="/v2/api-reference/_static/qbraid-runtime-api_dark.png"
  alt="qBraid Runtime API Server"
  className="hidden dark:block"
/>

For a client-side view of how the qBraid-SDK integrates with the qBraid API see the [Runtime overview](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components#runtime-overview) in the SDK docs.

## Rate limiting

The shared rate limiter uses request-method and path counters, scoped to an IP address, user, organization, or user within an organization. The default window starts with the first request and expires after 15 minutes. Individual routes and organization configurations can override these defaults.

| Tier                 | Window | Max requests |
| -------------------- | ------ | ------------ |
| Unauthenticated (IP) | 15 min | 100          |
| Authenticated user or organization | 15 min | 1,000 |

Exceeding the applicable limit returns HTTP 429 (Too Many Requests). Read the response rate-limit headers and wait before retrying. Authentication does not bypass endpoint-specific limits.

<Tip>
  Higher rate limits for your [organization](https://docs.qbraid.com/v2/account/organizations/overview)
  are available upon request.
</Tip>

## Using the SDK and CLI

<Tip>
  The qBraid SDK and CLI wrap most of these endpoints. They handle authentication, the `{ success, data }` response envelope,
  pagination, and retries. Use the REST API when you need
  something the client doesn't cover.
</Tip>

Install with `pip install -U qbraid qbraid-cli`, then run `qbraid configure` once
with an [API key](https://account.qbraid.com/account/api-keys).

| To do this                               | CLI                      | Python SDK                                          |
| ---------------------------------------- | ------------------------ | --------------------------------------------------- |
| Submit & track jobs (incl. batch groups) | `qbraid jobs`            | `QbraidProvider`, `device.run()`, `GroupJobSession` |
| Browse devices & calibrations            | `qbraid devices`         | `provider.get_devices()`, `provider.get_device()`   |
| Check credits & account                  | `qbraid account credits` | `QbraidSessionV1`                                   |

For any endpoint without a dedicated wrapper, `QbraidSessionV1` (from
`qbraid_core`) is an authenticated session. Call methods such as `.get()` and `.post()`
against the API. The session sets the `X-API-Key` header.
