> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-jobs-statuses.md](https://docs.qbraid.com/v2/api-reference/rest/get-jobs-statuses.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 cdec7038a7e1ce5733f7c4cf91c3f21305d61d9c9726f4df5ece9bfd7c339718.

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

# Get Job Status Counts


## OpenAPI

````yaml get /jobs/statuses
openapi: 3.1.0
info:
  title: qBraid Runtime API
  description: Public REST API for qBraid's quantum platform. Submit and manage quantum jobs, organize them into batch groups, and browse available devices and their calibration data. Authenticate every request with an API key (`X-API-KEY`).
  version: "2"
servers:
  - url: https://api-v2.qbraid.com/api/v1
    description: Live Server
security:
  - ApiKeyAuth: []
paths:
  /jobs/statuses:
    get:
      tags:
        - Jobs
      operationId: getJobsStatuses
      summary: Get job counts by status
      description: A map of every job status to the number of the caller's jobs in that status.
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/JobsStatusesResponse"
components:
  schemas:
    JobsStatusesResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          type: object
          additionalProperties:
            type: integer
          example:
            INITIALIZING: 0
            QUEUED: 2
            VALIDATING: 0
            RUNNING: 1
            CANCELLING: 0
            CANCELLED: 0
            COMPLETED: 12
            FAILED: 1
            UNKNOWN: 0
            HOLD: 0
      title: JobsStatusesResponse
      description: Map of every job status to a job count.
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
