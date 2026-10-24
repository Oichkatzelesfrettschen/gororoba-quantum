> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/migration.md](https://docs.qbraid.com/v2/api-reference/rest/migration.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9602a2c80574df2ca3fe97fe6cd85e3dc3bbde855866ba4cc3c12b9dca826b05.

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

# Migrating from V1

This guide covers breaking changes when migrating from the qBraid V1 API to V2.

## What's changed

### Authentication and response structure

#### Base URL

| Version | Base URL                           |
| ------- | ---------------------------------- |
| V1      | `https://api.qbraid.com/api`       |
| V2      | `https://api-v2.qbraid.com/api/v1` |

#### Authentication header

| Version | Header      |
| ------- | ----------- |
| V1      | `api-key`   |
| V2      | `X-API-KEY` |

#### Response envelope

The device and job REST responses use a standard envelope:

```json
{
  "success": boolean,
  "data": { ... }
}
```

V1 returned raw payloads without this wrapper.

### Devices

V2 device objects include `paradigm`, `modality`, and `pricingModel` fields. Device identifiers use qBraid Resource Names (QRNs).

#### Routes

| Operation    | V1 Route               | V2 Route                    |
| ------------ | ---------------------- | --------------------------- |
| List devices | `GET /quantum-devices` | `GET /devices`              |
| Get device   | —                      | `GET /devices/{device_qrn}` |

#### Identifier

| Version | Field              | Example                    |
| ------- | ------------------ | -------------------------- |
| V1      | `qbraidDeviceId`   | `qbraid_qir_simulator`     |
| V2      | `qrn` (QRN format) | `qbraid:qbraid:sim:qir-sv` |

#### Response fields

V2 adds:

| Field           | Description                                   |
| --------------- | --------------------------------------------- |
| `qrn`           | QRN identifier                                |
| `paradigm`      | `gate_model`, `analog`, `annealing`, `other`  |
| `modality`      | Device modality (e.g., `sparse_simulator`)    |
| `pricingModel`  | `fixed` or `dynamic`                          |
| `pricing`       | Object with `perTask`, `perShot`, `perMinute` |
| `directAccess`  | Boolean for direct device access              |
| `runInputTypes` | Array of supported input formats              |

V2 renames:

- `type` → `deviceType` (values: `SIMULATOR`, `QPU`)

### Jobs

V2 job responses use QRNs as identifiers. Job submissions specify the program format instead of using the `openQasm` or `bitcode` fields.

#### Routes

| Operation            | V1 Route                       | V2 Route                      |
| -------------------- | ------------------------------ | ----------------------------- |
| Create job           | `POST /quantum-jobs`           | `POST /jobs`                  |
| Get job              | `GET /quantum-jobs`            | `GET /jobs/{job_qrn}`         |
| Get result           | `GET /quantum-jobs/result/:id` | `GET /jobs/{job_qrn}/result`  |
| Get program          | —                              | `GET /jobs/{job_qrn}/program` |
| Cancel job           | `PUT /quantum-jobs/cancel/:id` | `POST /jobs/{job_qrn}/cancel` |
| Delete job           | —                              | `DELETE /jobs/{job_qrn}`      |
| Delete multiple jobs | `DELETE /quantum-jobs/:ids`    | `DELETE /jobs?qrns=[...]`     |

#### Request body

**V1:**

```json
{
  "qbraidDeviceId": "qbraid_qir_simulator",
  "openQasm": "OPENQASM 3; ...",
  "shots": 1000,
  "tags": {}
}
```

**V2:**

```json
{
  "deviceQrn": "qbraid:qbraid:sim:qir-sv",
  "program": {
    "format": "qasm3",
    "data": "OPENQASM 3; ..."
  },
  "shots": 1000,
  "tags": {}
}
```

Key differences:

- `qbraidDeviceId` → `deviceQrn` (QRN format)
- `openQasm`/`bitcode` → `program.data` with explicit `program.format`
- `circuitNumQubits` removed (inferred from program)

#### Response fields

V2 adds these fields to job responses:

| Field            | Description                                             |
| ---------------- | ------------------------------------------------------- |
| `jobQrn`         | QRN identifier (replaces V1's `_id`)                    |
| `batchJobQrn`    | Batch job reference                                     |
| `experimentType` | `gate_model`, `analog`, `annealing`, `other`            |
| `estimatedCost`  | Pre-execution cost estimate                             |
| `timeStamps`     | Object with `createdAt`, `endedAt`, `executionDuration` |
| `metadata`       | Extensible metadata object                              |

## What's the same

- API key authentication model (header-based)
- Core job lifecycle: create → poll status → get result
- `shots`, `tags`, `status` fields
- Job statuses: `INITIALIZING`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`
- Device statuses: `ONLINE`, `OFFLINE`, `UNAVAILABLE`

## Deprecated endpoints

The following V1 endpoints are **not available** in V2:

| Endpoint           | Notes                           |
| ------------------ | ------------------------------- |
| `POST /chat`       | Deprecated chat completions   |
| `GET /chat/models` | Deprecated chat model listing |

## Quick migration checklist

1. Update base URL to `https://api-v2.qbraid.com/api/v1`
2. Change auth header from `api-key` to `X-API-KEY`
3. Replace `qbraidDeviceId` with `deviceQrn` using QRN format
4. Wrap program in `{ "format": "...", "data": "..." }` object
5. Update route paths (`/quantum-jobs` → `/jobs`, `/quantum-devices` → `/devices`)
6. Handle new response envelope (`response.data` instead of raw payload)
7. Replace legacy chat integrations with the [AI Gateway](https://docs.qbraid.com/v2/ai/integrations/ai-gateway). Its OpenAI-compatible and Anthropic-compatible responses use their own formats.
