> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-cost-estimate.md](https://docs.qbraid.com/v2/api-reference/rest/get-quantum-jobs-cost-estimate.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 30df81870ffa15387791a5ff47baf32159de8910037f1c830a221bb4fdc82dad.

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

# Estimate Job Cost

<ResponseExample>

```json 200 Priced device
{
  "success": true,
  "data": {
    "pricingAvailable": true,
    "estimatedCost": 2380,
    "deviceQrn": "aws:aqt:qpu:ibex-q1",
    "shots": 1000
  }
}
```

```json 200 Pricing unavailable
{
  "success": true,
  "data": {
    "pricingAvailable": false,
    "reason": "dynamic_pricing_unavailable",
    "deviceQrn": "ibm:ibm:qpu:fez",
    "pricingModel": "dynamic"
  }
}
```

</ResponseExample>


## OpenAPI

````yaml get /jobs/cost-estimate
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
  /jobs/cost-estimate:
    get:
      tags:
        - jobs
      summary: Estimate Job Cost
      description: |-
        Estimate the cost, in qBraid credits, of running a job on a device before submitting it.

        The quote is a guide, not a cap. When you submit a job, its estimated cost is held from your credit balance; when the job finishes, you are charged its actual cost and the difference is refunded or debited. A job that runs longer than quoted is billed for what it used. A QPU is quoted from that device's execution history. A simulator is quoted from a fixed conservative duration, so its quote does not change with the shot count.

        A device whose pricing cannot be quoted is a state, not an error: the response has `pricingAvailable: false` and a `reason`.

        **Args:**
        - **deviceQrn** (string): Device QRN (qBraid Resource Name)
        - **shots** (integer, optional): Shot count to quote for. Defaults to 1000.

        **Returns:**
        - A quote with `estimatedCost` when `pricingAvailable` is true, or a `reason` when it is false

        **Raises:**
        - **400**: `deviceQrn` is missing or `shots` is outside 1 to 100000
        - **403**: You do not have device execution permission for this device
        - **404**: Device is not found
        - **410**: Device is retired
      operationId: getJobCostEstimate
      parameters:
        - name: deviceQrn
          in: query
          required: true
          schema:
            type: string
            description: Device QRN (qBraid Resource Name)
            title: Device Qrn
          description: Device to quote
          example: aws:aqt:qpu:ibex-q1
        - name: shots
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100000
            default: 1000
            description: Shot count to quote for
            title: Shots
          description: Shot count to quote for. Defaults to 1000.
      responses:
        "200":
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/CostEstimateResponse"
        "400":
          description: Bad Request
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
                  message:
                    type: string
                    example: "Query validation failed: shots: shots must be at least 1"
        "403":
          description: Forbidden
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
                  message:
                    type: string
                    example: "Missing device execution permission for: aws:aqt:qpu:ibex-q1"
        "404":
          description: Device Not Found
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
                  message:
                    type: string
                    example: "Device not found: does:not:exist:nope"
        "410":
          description: Device Retired
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
                  message:
                    type: string
                    example: "Device is retired and no longer available: aws:aws:sim:tn1"
components:
  schemas:
    CostEstimateResponse:
      properties:
        success:
          type: boolean
          title: Success
        data:
          oneOf:
            - $ref: "#/components/schemas/CostEstimateAvailable"
            - $ref: "#/components/schemas/CostEstimateUnavailable"
          title: Data
      type: object
      required:
        - success
        - data
      title: CostEstimateResponse
      description: Response schema for a job cost estimate
    CostEstimateAvailable:
      properties:
        pricingAvailable:
          type: boolean
          enum:
            - true
          title: Pricing Available
          description: Always true for this shape
        estimatedCost:
          type: number
          minimum: 0
          title: Estimated Cost
          description: Estimated cost in qBraid credits
        deviceQrn:
          type: string
          title: Device Qrn
          description: Device the quote is for
        shots:
          type: integer
          title: Shots
          description: Shot count the quote assumes. Only present when `shots` was passed in the request.
      type: object
      required:
        - pricingAvailable
        - estimatedCost
        - deviceQrn
      title: CostEstimateAvailable
      description: A quote for a device with usable pricing
    CostEstimateUnavailable:
      properties:
        pricingAvailable:
          type: boolean
          enum:
            - false
          title: Pricing Available
          description: Always false for this shape
        reason:
          type: string
          enum:
            - no_pricing_configured
            - dynamic_pricing_unavailable
          title: Reason
          description: "Why no cost could be quoted. `no_pricing_configured`: the device has no price data. `dynamic_pricing_unavailable`: the price depends on the submitted program and cannot be quoted up front."
        deviceQrn:
          type: string
          title: Device Qrn
          description: Device the quote is for
        pricingModel:
          type: string
          enum:
            - fixed
            - dynamic
          nullable: true
          title: Pricing Model
          description: The device's pricing model, or null if none is configured
      type: object
      required:
        - pricingAvailable
        - reason
        - deviceQrn
        - pricingModel
      title: CostEstimateUnavailable
      description: The device's pricing cannot be quoted
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
