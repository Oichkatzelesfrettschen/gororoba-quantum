> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/delete-quantum-job.md](https://docs.qbraid.com/v2/api-reference/rest/delete-quantum-job.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 01e0cf038067a5630adc9e578b86dbc1d079a7ea3b92a3c15bb66bf8440bb545.

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

# Delete Job

<ResponseExample>

```json 200
{
  "success": true,
  "data": {
    "message": "Job deleted successfully"
  }
}
```

</ResponseExample>


## OpenAPI

````yaml delete /jobs/{job_qrn}
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
    delete:
      tags:
        - Jobs
      operationId: deleteJob
      summary: Soft-delete a job
      description: Soft-delete a job. A non-terminal job keeps running and is still billed (see `stillRunning`); it is not cancelled.
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
                $ref: "#/components/schemas/DeleteJobResponse"
        "404":
          description: Job not found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    DeleteJobResponse:
      title: DeleteJobResponse
      description: Response for soft-deleting a single job. `stillRunning` is true when the job had not reached a terminal status — it is NOT cancelled, keeps running, and is still billed; a client may offer a follow-up cancel.
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
            - message
            - jobQrn
            - stillRunning
          properties:
            message:
              type: string
              example: Job deleted successfully
            jobQrn:
              type: string
            deletedAt:
              type: string
              format: date-time
            stillRunning:
              type: boolean
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
