> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-simulator-usage.md](https://docs.qbraid.com/v2/api-reference/rest/get-simulator-usage.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d0500920d2e6921d2051536b1e59c44c60dd8dcc3245394a394fd1d62d162d46.

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

# Get Simulator Usage


## OpenAPI

````yaml get /usage/simulator
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
  /usage/simulator:
    get:
      tags:
        - Account
      operationId: getSimulatorUsage
      summary: Get simulator daily usage and quota
      description: Return the daily per-simulator job quota and current usage for the tier of the caller. Usage resets at 00:00 UTC. The organization is taken from the API key, which is bound to a single organization.
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/SimulatorUsageResponse"
        "401":
          description: Authentication / org context required.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "404":
          description: Organization user not found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
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
    SimulatorUsageItem:
      type: object
      required:
        - deviceQrn
        - deviceName
        - usage
        - quota
        - remaining
        - unlimited
        - percentageUsed
        - resetsAt
        - creditFallover
        - autoSwitchToCredits
      properties:
        deviceQrn:
          type: string
        deviceName:
          type: string
        usage:
          type: integer
        quota:
          type: integer
          nullable: true
          description: Daily cap; null = unlimited.
        remaining:
          type: integer
          nullable: true
        unlimited:
          type: boolean
        percentageUsed:
          type: integer
          description: 0-100; 0 when unlimited.
        resetsAt:
          type: string
          format: date-time
          description: Next 00:00 UTC reset.
        creditFallover:
          type: boolean
          description: True for a simulator whose daily quota is a free allowance that can fall over to credits (the GPU simulators). Once the allowance is used, further jobs run charged from credits at the device's per-minute price when `autoSwitchToCredits` is true, and are refused when it is false.
        autoSwitchToCredits:
          type: boolean
          description: The caller's usage-based billing setting for simulators; the same on every entry. Only affects entries with `creditFallover`.
    SimulatorUsageResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          type: array
          items:
            $ref: "#/components/schemas/SimulatorUsageItem"
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
