> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs.md](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 12d33a48d66b5f1668e2e913186e2b12a208bed1abf0990117d3852a440656b7.

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

# Get Job

<ResponseExample>

```json 200
{
  "success": true,
  "data": {
    "name": "My quantum job",
    "shots": 1000,
    "deviceQrn": "qbraid:qbraid:sim:qir-sv",
    "tags": {},
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
}
```

</ResponseExample>


## OpenAPI

````yaml get /jobs/{job_qrn}
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
  /jobs/{job_qrn}:
    get:
      tags:
        - Jobs
      operationId: getJob
      summary: Get a job
      description: Retrieve a single job by its QRN.
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
                $ref: "#/components/schemas/GetJobResponse"
        "404":
          description: Job not found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    GetJobResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          $ref: "#/components/schemas/RuntimeJob"
      type: object
      required:
        - success
        - data
      title: GetJobResponse
      description: Response schema for retrieving a single job
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
