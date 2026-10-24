> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/get-credit-pricing.md](https://docs.qbraid.com/v2/api-reference/rest/get-credit-pricing.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 10b302e69897dbc45a9aeae25f18b4f21641f31a7929faa985c09f5da6402caf.

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

# Get Credit Pricing


## OpenAPI

````yaml get /billing/credits/pricing
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
  /billing/credits/pricing:
    get:
      tags:
        - Account
      operationId: getCreditPricing
      summary: Get credit-pack pricing
      description: Return the credit conversion rate, minimum purchase amount, currency, and example credit packs. Public — no authentication required.
      security: []
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/CreditPricingResponse"
components:
  schemas:
    CreditPricingResponse:
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
            - creditRate
            - minPurchaseUSD
            - currency
            - examples
          properties:
            creditRate:
              type: integer
              description: Credits per 1 USD.
              example: 100
            minPurchaseUSD:
              type: integer
              example: 5
            currency:
              type: string
              example: USD
            examples:
              type: array
              items:
                type: object
                required:
                  - usd
                  - credits
                properties:
                  usd:
                    type: integer
                  credits:
                    type: integer
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
