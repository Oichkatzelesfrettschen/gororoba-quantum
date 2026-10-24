> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-result.md](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-result.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 325baa4cf18421c937179a78f85217ee9dc6619da2bddb5e896585e0f9cac2f3.

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

# Get Job Result

<ResponseExample>

```json 200
{
  "success": true,
  "data": {
    "status": "COMPLETED",
    "cost": 0.501875,
    "timeStamps": {
      "createdAt": "2025-01-15T10:30:00Z",
      "endedAt": "2025-01-15T10:30:05Z",
      "executionDuration": 5000
    },
    "resultData": {
      "measurementCounts": { "00": 504, "11": 496 }
    }
  }
}
```

</ResponseExample>


## OpenAPI

````yaml get /jobs/{job_qrn}/result
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
  /jobs/{job_qrn}/result:
    get:
      tags:
        - Jobs
      operationId: getJobResult
      summary: Get job result
      description: Retrieve the result(s) of a completed job (a single result, or an array for batch jobs).
      parameters:
        - name: job_qrn
          in: path
          required: true
          description: The job qrn (qBraid Resource Name).
          schema:
            type: string
            minLength: 1
            example: aws:aws:sim:dm1-a1b2-qjob-1234567890abcdef
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/GetJobResultResponse"
        "404":
          description: Job or result not found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    GetJobResultResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          $ref: "#/components/schemas/Result"
      type: object
      required:
        - success
        - data
      title: GetJobResultResponse
      description: Response schema for retrieving job results
    JobStatus:
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
      title: JobStatus
      description: |-
        Enum for the status of processes (i.e. quantum jobs / tasks) resulting
        from any `qbraid.runtime.QuantumDevice.run` method.

        Displayed status text values may differ from those listed below to provide
        additional visibility into tracebacks, particularly for failed jobs.
    Result:
      properties:
        status:
          $ref: "#/components/schemas/JobStatus"
        cost:
          anyOf:
            - type: integer
            - type: number
            - type: string
          type: number
          title: Credits
          description: A monetary amount where 1 Credit = $0.01 USD.
          examples:
            - 10
            - 0.05
            - 1.5
        timeStamps:
          $ref: "#/components/schemas/TimeStamps"
        resultData:
          additionalProperties: true
          type: object
          title: Resultdata
      type: object
      required:
        - status
        - cost
        - timeStamps
        - resultData
      title: Result
      description: Schema for job result
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
