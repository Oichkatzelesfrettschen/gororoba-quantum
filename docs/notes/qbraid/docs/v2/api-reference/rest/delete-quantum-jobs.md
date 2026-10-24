> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/delete-quantum-jobs.md](https://docs.qbraid.com/v2/api-reference/rest/delete-quantum-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 49e4924ba95428c8f9f8d6a9143318ba4de63036e014399ccbb147a0b85bd474.

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

# Delete Multiple Jobs

<ResponseExample>

```json 200
{
  "success": true,
  "data": {
    "successfulIds": ["qbraid:job:abc123xyz", "qbraid:job:def456uvw"],
    "failedIds": {
      "qbraid:job:invalid123": "Job not found"
    }
  }
}
```

</ResponseExample>


## OpenAPI

````yaml delete /jobs
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
    delete:
      tags:
        - Jobs
      operationId: deleteMultipleJobs
      summary: Soft-delete multiple jobs
      description: Soft-delete several jobs by QRN. Non-terminal jobs keep running and are still billed (see `stillRunning`).
      parameters:
        - name: qrns
          in: query
          required: true
          schema:
            type: string
            description: JSON array of job QRNs to delete
            title: Job QRNs
          description: JSON array of job QRNs to delete (e.g., ["qbraid:job:abc123", "qbraid:job:xyz789"])
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/DeleteMultipleJobsResponse"
        "400":
          description: Validation error.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    DeleteMultipleJobsResponse:
      title: DeleteMultipleJobsResponse
      description: Response for bulk soft-delete.
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
            - successfulIds
            - failedIds
            - stillRunning
          properties:
            successfulIds:
              type: array
              items:
                type: string
              description: QRNs successfully soft-deleted.
            failedIds:
              type: object
              additionalProperties:
                type: string
              description: Map of QRN -> failure reason.
            stillRunning:
              type: array
              items:
                type: string
              description: QRNs that were deleted while not yet terminal (still running, still billed).
    ErrorResponse:
      type: object
      required:
        - success
        - message
        - error
      description: Standard error envelope returned for 4xx/5xx responses.
      properties:
        success:
          type: boolean
          example: false
        message:
          type: string
          description: Human-readable error message.
        error:
          type: object
          required:
            - message
            - code
          properties:
            message:
              type: string
            code:
              description: Machine-readable error code (string) or HTTP status (integer).
              oneOf:
                - type: string
                - type: integer
          additionalProperties: true
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
