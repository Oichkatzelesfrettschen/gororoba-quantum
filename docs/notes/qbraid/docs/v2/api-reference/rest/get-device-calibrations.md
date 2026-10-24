> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-device-calibrations.md](https://docs.qbraid.com/v2/api-reference/rest/get-device-calibrations.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 6c50ef7036b03e063e0930193a73b6ab6d5e33c718216076a13e311ac92c5677.

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

# Get Device Calibrations


## OpenAPI

````yaml get /devices/{device_qrn}/calibrations
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
  /devices/{device_qrn}/calibrations:
    get:
      tags:
        - Devices
      operationId: getDeviceCalibrations
      summary: Get device calibration data
      description: "Retrieve the latest calibration snapshot for a device: qubit-level (T1, T2, frequency, readout/gate errors) and edge-level (two-qubit gate errors, gate lengths)."
      parameters:
        - name: device_qrn
          in: path
          required: true
          description: The device qrn (qBraid Resource Name).
          schema:
            type: string
            minLength: 1
            example: aws:tn1:qpu:device-name
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/GetDeviceCalibrationsResponse"
        "400":
          description: Invalid or missing QRN.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "404":
          description: Calibration data not found for this device.
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
    EdgeEntry:
      type: object
      required:
        - source
        - target
        - value
      properties:
        source:
          type: integer
        target:
          type: integer
        value:
          type: number
    QubitCalibration:
      type: object
      description: Qubit-level properties; presence depends on the provider.
      properties:
        t1:
          type: number
        t2:
          type: number
        frequency:
          type: number
        readoutError:
          type: number
        gateError:
          type: object
          additionalProperties:
            type: number
          description: Per-single-qubit-gate error, keyed by gate name.
    DeviceCalibration:
      type: object
      required:
        - deviceQRNs
        - provider
        - lastCalibrated
        - fetchedAt
        - qubits
        - edges
      properties:
        _id:
          type: string
        deviceQRNs:
          type: array
          items:
            type: string
        provider:
          type: string
        lastCalibrated:
          type: string
          format: date-time
        fetchedAt:
          type: string
          format: date-time
        qubits:
          type: object
          additionalProperties:
            $ref: "#/components/schemas/QubitCalibration"
          description: Qubit-level properties keyed by qubit index (string).
        edges:
          type: object
          description: Edge-level properties keyed by metric name, then by source-qubit key, to a list of edge entries.
          additionalProperties:
            type: object
            additionalProperties:
              type: array
              items:
                $ref: "#/components/schemas/EdgeEntry"
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
    GetDeviceCalibrationsResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          example: true
        data:
          $ref: "#/components/schemas/DeviceCalibration"
      title: GetDeviceCalibrationsResponse
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
