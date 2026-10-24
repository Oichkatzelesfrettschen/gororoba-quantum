> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/post-quantum-jobs.md](https://docs.qbraid.com/v2/api-reference/rest/post-quantum-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 96b10210268f3a68333d7d0e583912e959faaaa7f9bd6aada90a7da8dd99d3c7.

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

# Create Job

<ResponseExample>
```json 201
{
  "success": true,
  "data": {
    "jobQrn": "aws:aws:sim:dm1-a1b2-qjob-1234567890abcdef",
    "status": "INITIALIZING"
  }
}
```
</ResponseExample>


## OpenAPI

````yaml post /jobs
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
    post:
      tags:
        - Jobs
      operationId: createJob
      summary: Submit a job
      description: Submit a quantum job (or a batch of circuits) to a device. `data` is the created job.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/JobRequest"
      responses:
        "201":
          description: Job created.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/CreateJobResponse"
        "400":
          description: Validation error.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "403":
          description: No execution access to the device.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    CreateJobResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          $ref: "#/components/schemas/RuntimeJob"
      title: CreateJobResponse
      description: Response for job creation. `data` is the newly created job.
    JobRequest:
      properties:
        name:
          anyOf:
            - type: string
            - type: "null"
          title: Name
          description: Job name
        shots:
          type: integer
          minimum: 0
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
        program:
          description: A single program, or an array of programs for a batch submission (1-2000).
          oneOf:
            - $ref: "#/components/schemas/Program"
            - type: array
              minItems: 1
              maxItems: 2000
              items:
                $ref: "#/components/schemas/Program"
        groupJobQrn:
          anyOf:
            - type: string
            - type: "null"
          description: QRN of a job group to attach this job to.
      type: object
      required:
        - shots
        - deviceQrn
        - program
      title: JobRequest
      description: Schema for job submission request body
    Program:
      properties:
        format:
          type: string
          enum:
            - qasm2
            - qasm3
            - qir.bc
            - qir.ll
            - analog
            - pulser.sequence
            - quil
            - ionq.circuit.v0
            - problem
          title: Format
          description: Program format
        data:
          title: Data
          description: Program data
      type: object
      required:
        - format
        - data
      title: Program
      description: Schema for quantum program
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
