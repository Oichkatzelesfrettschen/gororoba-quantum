> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/update-simulator-usage-settings.md](https://docs.qbraid.com/v2/api-reference/rest/update-simulator-usage-settings.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 7ab61d692484c3d76c2126a77bd465c5d119bdb8e3e941600f76e939605aa609.

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

# Update Simulator Usage Settings


## OpenAPI

````yaml patch /usage/simulator/settings
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
  /usage/simulator/settings:
    patch:
      tags:
        - Account
      operationId: updateSimulatorUsageSettings
      summary: Update simulator usage settings
      description: Turn usage-based billing for simulators on or off for the caller. With `autoSwitchToCredits` true, once a GPU simulator's free daily allowance is used, further jobs on it run and are charged from credits at the device's per-minute price. With it false (the default), those jobs are refused until the allowance resets at 00:00 UTC. The organization is taken from the API key, which is bound to a single organization.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/SimulatorUsageSettings"
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/SimulatorUsageSettingsResponse"
        "400":
          description: Invalid request body.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
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
    SimulatorUsageSettings:
      type: object
      required:
        - autoSwitchToCredits
      properties:
        autoSwitchToCredits:
          type: boolean
          description: Run jobs past a GPU simulator's free daily allowance, charged from credits (true), or refuse them (false).
    SimulatorUsageSettingsResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          $ref: "#/components/schemas/SimulatorUsageSettings"
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
