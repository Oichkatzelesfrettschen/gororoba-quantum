> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-quantum-devices.md](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-devices.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 dbf64e1c6bd1d6401fc76c5ca5b843328c48510c333ed120237ced2c775252ea.

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

# Get All Devices

<ResponseExample>

```json 200
{
  "success": true,
  "data": [
    {
      "name": "QIR sparse simulator",
      "qrn": "qbraid:qbraid:sim:qir-sv",
      "vendor": "qbraid",
      "deviceType": "SIMULATOR",
      "runInputTypes": ["qasm2", "qasm3", "qir.bc", "qir.ll"],
      "status": "ONLINE",
      "statusMsg": null,
      "nextAvailable": null,
      "queueDepth": 0,
      "avgQueueTime": null,
      "numberQubits": 64,
      "paradigm": "gate_model",
      "modality": "sparse_simulator",
      "noiseModels": null,
      "pricingModel": "fixed",
      "pricing": {
        "perTask": 0.5,
        "perShot": 0,
        "perMinute": 7.5
      },
      "directAccess": true
    }
  ]
}
```

</ResponseExample>


## OpenAPI

````yaml get /devices
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
  /devices:
    get:
      tags:
        - Devices
      operationId: listDevices
      summary: List devices
      description: List quantum devices (simulators and QPUs) visible to the caller, with filtering, search, sorting, and pagination.
      parameters:
        - name: qrn
          in: query
          required: false
          schema:
            type: string
            description: Device QRN (qBraid Resource Name)
            title: Qrn
          description: Filter devices by QRN
        - name: vendor
          in: query
          required: false
          schema:
            type: string
            enum:
              - aws
              - azure
              - ibm
              - ionq
              - qbraid
            description: Filter devices by vendor
            title: Vendor
          description: Filter devices by vendor
        - name: providerId
          in: query
          required: false
          schema:
            type: string
            description: Provider ID to filter by
            title: Provider Id
          description: Filter devices by provider ID
        - name: deviceType
          in: query
          required: false
          schema:
            type: string
            enum:
              - QPU
              - SIMULATOR
            description: Filter by hardware type
            title: Device Type
          description: Filter devices by hardware type
        - name: status
          in: query
          required: false
          schema:
            $ref: "#/components/schemas/DeviceStatus"
          description: Filter devices by operational status
        - name: retired
          in: query
          required: false
          schema:
            type: boolean
            description: Include or exclude retired devices
            title: Retired
          description: Include (`true`) or exclude (`false`) retired devices
        - name: private
          in: query
          required: false
          schema:
            type: boolean
            description: Filter by device visibility
            title: Private
          description: Filter by visibility — `true` for private, `false` for public
        - name: verified
          in: query
          required: false
          schema:
            type: boolean
            description: Filter by device verification status
            title: Verified
          description: Filter by device verification status
        - name: directAccess
          in: query
          required: false
          schema:
            type: boolean
            description: Filter by direct access availability
            title: Direct Access
          description: Filter devices by direct access availability
        - name: search
          in: query
          required: false
          schema:
            type: string
            minLength: 1
            maxLength: 255
            description: Search keyword
            title: Search
          description: Search devices by name, description, or about (1–255 characters)
        - name: sortBy
          in: query
          required: false
          schema:
            type: string
            enum:
              - name
              - vendor
              - deviceType
              - status
              - numberQubits
              - createdAt
              - updatedAt
            description: Field to sort by
            title: Sort By
          description: Field to sort devices by
        - name: sortOrder
          in: query
          required: false
          schema:
            type: string
            enum:
              - asc
              - desc
            default: asc
            description: Sort order direction
            title: Sort Order
          description: "Sort order direction (default: `asc`)"
        - name: page
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
            description: Page number (1-indexed)
            title: Page
          description: "Page number (1-indexed, default: 1)"
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
            description: Number of items per page
            title: Limit
          description: "Number of items per page (1–100, default: 20)"
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ListDevicesResponse"
        "400":
          description: Invalid query parameters.
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
    ListDevicesResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          type: array
          items:
            $ref: "#/components/schemas/RuntimeDevice"
          description: Array of devices matching the query filters
      type: object
      required:
        - success
        - data
      title: ListDevicesResponse
      description: Response schema for listing devices
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
