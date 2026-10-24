> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-device.md](https://docs.qbraid.com/v2/api-reference/rest/get-device.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ba4628b77bad9e013e5e7ecb3c268bf1fda043149acc9e86c9d10af7572404d9.

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

# Get Device

<ResponseExample>

```json 200
{
  "success": true,
  "data": {
    "runInputTypes": ["pyqir", "qasm3"],
    "numberQubits": 64,
    "noiseModels": [],
    "statusMsg": null,
    "nextAvailable": null,
    "avgQueueTime": null,
    "qrn": "qbraid:qbraid:sim:qir-sv",
    "modality": null,
    "name": "QIR Simulator",
    "paradigm": "gate_model",
    "pricing": {
      "perTask": 0,
      "perShot": 0,
      "perMinute": 0
    },
    "status": "ONLINE",
    "vendor": "qbraid",
    "description": "Sparse state vector simulator using QIR compiler. Free of cost.",
    "deviceType": "SIMULATOR",
    "queueDepth": 0,
    "directAccess": true,
    "pricingModel": "fixed"
  }
}
```

</ResponseExample>


## OpenAPI

````yaml get /devices/{device_qrn}
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
  /devices/{device_qrn}:
    get:
      tags:
        - Devices
      operationId: getDevice
      summary: Get a device
      description: Retrieve a single device by its QRN.
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
                $ref: "#/components/schemas/GetDeviceResponse"
        "404":
          description: Device not found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
components:
  schemas:
    DevicePricing:
      properties:
        perTask:
          type: number
          title: Credits
          description: A monetary amount where 1 Credit = $0.01 USD.
          examples:
            - 10
            - 0.05
            - 1.5
        perShot:
          type: number
          title: Credits
          description: A monetary amount where 1 Credit = $0.01 USD.
          examples:
            - 10
            - 0.05
            - 1.5
        perMinute:
          type: number
          title: Credits
          description: A monetary amount where 1 Credit = $0.01 USD.
          examples:
            - 10
            - 0.05
            - 1.5
      type: object
      required:
        - perTask
        - perShot
        - perMinute
      title: DevicePricing
      description: Represents pricing information for a quantum device.
    DeviceStatus:
      type: string
      enum:
        - ONLINE
        - UNAVAILABLE
        - OFFLINE
        - RETIRED
      title: DeviceStatus
      description: |-
        Enumeration for representing various operational statuses of devices.

        Attributes:
            ONLINE (str): Device is online and accepting jobs.
            UNAVAILABLE (str): Device is online but not accepting jobs.
            OFFLINE (str): Device is offline.
            RETIRED (str): Device has been retired and is no longer operational.
    GetDeviceResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          $ref: "#/components/schemas/RuntimeDevice"
      type: object
      required:
        - success
        - data
      title: GetDeviceResponse
      description: Response schema for retrieving a single device
    ExperimentType:
      type: string
      enum:
        - gate_model
        - analog
        - annealing
        - other
      title: ExperimentType
      description: |-
        Enumeration for quantum experiment types.

        Attributes:
            GATE_MODEL (str): Gate-based quantum computing (e.g., OpenQASM).
            ANALOG (str): Analog quantum computing
            ANNEALING (str): Quantum annealing for optimization problems.
            OTHER (str): Placeholder for other or unspecified quantum computing models.
    RuntimeDevice:
      properties:
        name:
          type: string
          title: Name
        qrn:
          type: string
          title: Qrn
        vendor:
          type: string
          enum:
            - aws
            - azure
            - ibm
            - ionq
            - qbraid
          title: Vendor
        deviceType:
          type: string
          enum:
            - SIMULATOR
            - QPU
          title: Devicetype
        runInputTypes:
          items:
            type: string
          type: array
          title: Runinputtypes
        status:
          $ref: "#/components/schemas/DeviceStatus"
        statusMsg:
          anyOf:
            - type: string
            - type: "null"
          title: Statusmsg
        nextAvailable:
          anyOf:
            - type: string
              format: date-time
            - type: "null"
          title: Nextavailable
        queueDepth:
          anyOf:
            - type: integer
            - type: "null"
          title: Queuedepth
        avgQueueTime:
          anyOf:
            - type: integer
            - type: "null"
          title: Avgqueuetime
        numberQubits:
          anyOf:
            - type: integer
            - type: "null"
          title: Numberqubits
        paradigm:
          $ref: "#/components/schemas/ExperimentType"
        modality:
          anyOf:
            - type: string
            - type: "null"
          title: Modality
        noiseModels:
          anyOf:
            - items:
                type: string
              type: array
            - type: "null"
          title: Noisemodels
        pricingModel:
          anyOf:
            - type: string
              enum:
                - fixed
                - dynamic
            - type: "null"
          title: Pricingmodel
        pricing:
          anyOf:
            - $ref: "#/components/schemas/DevicePricing"
            - type: "null"
        directAccess:
          type: boolean
          title: Directaccess
          default: true
      type: object
      required:
        - name
        - qrn
        - vendor
        - deviceType
        - runInputTypes
        - status
        - paradigm
      title: RuntimeDevice
      description: Schema for device response
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
