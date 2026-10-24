> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-jobs-summary.md](https://docs.qbraid.com/v2/api-reference/rest/get-jobs-summary.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 5d8a88183e6ca40c119cc49d60b5e12295f3ab88675791d7a9344f62ca71cf07.

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

# Get Job Summary


## OpenAPI

````yaml get /jobs/summary
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
  /jobs/summary:
    get:
      tags:
        - Jobs
      operationId: getJobsSummary
      summary: Get job summary stats
      description: Aggregated statistics across the caller's jobs (counts, per-status/type breakdowns, cost/shots totals and averages).
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/JobsSummaryResponse"
components:
  schemas:
    JobsSummaryResponse:
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
          required:
            - totalJobs
            - statusCounts
            - avgExecutionTime
            - totalCost
            - avgCost
            - totalShots
            - avgShots
            - experimentTypeCounts
          properties:
            totalJobs:
              type: integer
            statusCounts:
              type: object
              additionalProperties:
                type: integer
              description: Count per job status (every status present, 0 when none).
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
            avgExecutionTime:
              type: number
              description: Average execution duration (ms) over completed jobs.
            totalCost:
              type: number
            avgCost:
              type: number
            totalShots:
              type: number
            avgShots:
              type: number
            experimentTypeCounts:
              type: object
              additionalProperties:
                type: integer
              example:
                gate_model: 14
                analog: 1
      title: JobsSummaryResponse
      description: Aggregated statistics across the caller's jobs.
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
