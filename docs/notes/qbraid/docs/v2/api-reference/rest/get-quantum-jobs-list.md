> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-list.md](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-list.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 2d80a1d81e79f70c0bef15973547658e0cf931dde5b42adae14a9c6fa5c826af.

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

# Get All Jobs

<ResponseExample>

```json 200
{
  "success": true,
  "data": [
    {
      "name": "Bell state job",
      "shots": 1000,
      "deviceQrn": "qbraid:qbraid:sim:qir-sv",
      "tags": { "experiment": "bell-state" },
      "runtimeOptions": {},
      "jobQrn": "qbraid:job:abc123xyz",
      "batchJobQrn": null,
      "vendor": "qbraid",
      "provider": "qbraid",
      "status": "COMPLETED",
      "statusMsg": null,
      "experimentType": "gate_model",
      "queuePosition": null,
      "timeStamps": {
        "createdAt": "2025-01-15T10:30:00Z",
        "endedAt": "2025-01-15T10:30:05Z",
        "executionDuration": 5000
      },
      "cost": 0.501875,
      "estimatedCost": 0.5,
      "metadata": {}
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  },
  "meta": {
    "timestamp": "2025-01-15T10:30:06.000Z"
  }
}
```

</ResponseExample>


## OpenAPI

````yaml get /jobs
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
  /jobs:
    get:
      tags:
        - Jobs
      operationId: listJobs
      summary: List jobs
      description: List the caller's jobs with filtering, sorting, and pagination. Soft-deleted jobs are excluded.
      parameters:
        - name: vendor
          in: query
          required: false
          schema:
            type: string
            enum:
              - aws
              - azure
              - ibm
              - ionq
              - qbraid
              - all
            description: Filter jobs by vendor
            title: Vendor
          description: Filter jobs by vendor
        - name: provider
          in: query
          required: false
          schema:
            type: string
            description: Filter jobs by provider name
            title: Provider
          description: Filter jobs by provider name
        - name: statusGroup
          in: query
          required: false
          schema:
            type: string
            enum:
              - all
              - pending
              - returned
            description: Filter by status group
            title: Status Group
          description: Filter by status group — `pending` (active/in-progress), `returned` (completed/failed/cancelled), or `all`
        - name: status
          in: query
          required: false
          schema:
            type: string
            enum:
              - INITIALIZING
              - QUEUED
              - VALIDATING
              - RUNNING
              - CANCELLING
              - CANCELLED
              - COMPLETED
              - FAILED
              - UNKNOWN
              - HOLD
            description: Filter by individual job status
            title: Status
          description: Filter by individual job status. Takes priority over `statusGroup` when both are provided
        - name: search
          in: query
          required: false
          schema:
            type: string
            minLength: 1
            maxLength: 255
            description: Search keyword
            title: Search
          description: Search jobs by keyword (1–255 characters)
        - name: tags
          in: query
          required: false
          schema:
            type: string
            description: JSON object of tag key-value pairs to filter by
            title: Tags
            example: '{"experiment":"bell-state"}'
          description: Filter by tags as a JSON object (e.g., `{"experiment":"bell-state"}`)
        - name: page
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
            description: Page number (1-indexed)
            title: Page
          description: "Page number (1-indexed, default: 1)"
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
            description: Number of items per page
            title: Limit
          description: "Number of items per page (1–100, default: 50)"
      responses:
        "200":
          description: Paginated jobs.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ListJobsResponse"
components:
  schemas:
    ListJobsResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          type: array
          items:
            $ref: "#/components/schemas/RuntimeJob"
          description: Array of jobs matching the query filters
        pagination:
          type: object
          properties:
            page:
              type: integer
              description: Current page number
            limit:
              type: integer
              description: Number of items per page
            total:
              type: integer
              description: Total number of jobs
            totalPages:
              type: integer
              description: Total number of pages
            hasNext:
              type: boolean
              description: Whether a next page exists
            hasPrev:
              type: boolean
              description: Whether a previous page exists
          required:
            - page
            - limit
            - total
            - totalPages
            - hasNext
            - hasPrev
        meta:
          type: object
          properties:
            timestamp:
              type: string
              format: date-time
              description: Response timestamp
          required:
            - timestamp
      type: object
      required:
        - success
        - data
        - pagination
        - meta
      title: ListJobsResponse
      description: Paginated response for listing user jobs
    RuntimeJob:
      properties:
        name:
          anyOf:
            - type: string
            - type: "null"
          title: Name
          description: Job name
        shots:
          type: integer
          exclusiveMinimum: 0
          title: Shots
          description: Number of shots to execute
        deviceQrn:
          type: string
          title: Deviceqrn
          description: qBraid device resource name
        tags:
          additionalProperties:
            anyOf:
              - type: string
              - type: integer
              - type: boolean
          type: object
          title: Tags
          description: Job tags
        runtimeOptions:
          additionalProperties: true
          type: object
          title: Runtimeoptions
          description: Runtime options
        jobQrn:
          type: string
          title: Jobqrn
          description: qBraid job resource name
        batchJobQrn:
          anyOf:
            - type: string
            - type: "null"
          title: Batchjobqrn
          description: Batch job resource name
        vendor:
          type: string
          enum:
            - aws
            - azure
            - ibm
            - ionq
            - qbraid
          title: Vendor
          description: Vendor name
        provider:
          type: string
          enum:
            - aqt
            - aws
            - azure
            - equal1
            - ibm
            - iqm
            - ionq
            - nec
            - oqc
            - pasqal
            - quantinuum
            - quera
            - rigetti
            - qbraid
          title: Provider
          description: Provider name
        status:
          type: string
          description: Job status
        statusMsg:
          anyOf:
            - type: string
            - type: "null"
          title: Statusmsg
          description: Job status message
        experimentType:
          type: string
          description: Experiment type
        queuePosition:
          anyOf:
            - type: integer
              minimum: 0
            - type: "null"
          title: Queueposition
          description: Job queue position
        timeStamps:
          anyOf:
            - $ref: "#/components/schemas/TimeStamps"
            - type: "null"
          description: Job time stamps
        cost:
          anyOf:
            - type: number
            - type: "null"
          title: Cost
          description: Job cost in credits
        estimatedCost:
          anyOf:
            - type: number
            - type: "null"
          title: Estimatedcost
          description: Job estimated cost in credits
          ge: 0
        metadata:
          additionalProperties: true
          type: object
          title: Metadata
          description: Job metadata
      type: object
      required:
        - shots
        - deviceQrn
        - jobQrn
        - vendor
        - provider
        - status
        - experimentType
        - estimatedCost
      title: RuntimeJob
      description: Schema for runtime job model
    TimeStamps:
      properties:
        createdAt:
          type: string
          format: date-time
          title: Createdat
        endedAt:
          anyOf:
            - type: string
              format: date-time
            - type: "null"
          title: Endedat
        executionDuration:
          anyOf:
            - type: integer
              minimum: 0
            - type: "null"
          title: Executionduration
          description: Execution time in milliseconds
      type: object
      required:
        - createdAt
      title: TimeStamps
      description: Model for capturing time-related information in an experiment.
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
