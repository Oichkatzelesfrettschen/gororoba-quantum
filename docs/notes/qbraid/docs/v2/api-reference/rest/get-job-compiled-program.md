> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-job-compiled-program.md](https://docs.qbraid.com/v2/api-reference/rest/get-job-compiled-program.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 3f926a4bcfa0137aba6dc871d6428acf64e2c4cd873a98cae43a3ca095eb6eda.

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

# Get Compiled Program


## OpenAPI

````yaml get /jobs/{job_qrn}/compiled-program
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
  /jobs/{job_qrn}/compiled-program:
    get:
      tags:
        - Jobs
      operationId: getJobCompiledProgram
      summary: Get compiled program
      description: Retrieve the vendor-compiled program for a job (stored `{format, data}` artifact). 404 when none is available.
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
                $ref: "#/components/schemas/CompiledProgramResponse"
        "404":
          description: Job not found, or no compiled program available.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
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
    CompiledProgramResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          $ref: "#/components/schemas/Program"
      title: CompiledProgramResponse
      description: The vendor-compiled program (`{format, data}`) stored for the job.
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
