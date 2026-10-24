> Full piece: [https://docs.qbraid.com/v2/api-reference/rest/list-job-groups.md](https://docs.qbraid.com/v2/api-reference/rest/list-job-groups.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 bb1713466ce18659227f0e0b3f0d0c6fb6f2949078394df7334006f25dacba3f.

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

# List Job Groups


## OpenAPI

````yaml get /jobs/group
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
  /jobs/group:
    get:
      tags:
        - Jobs
      operationId: listJobGroups
      summary: List job groups
      description: List the caller's job groups, newest first. Expired OPEN groups are lazily auto-closed during listing.
      parameters:
        - name: status
          in: query
          required: false
          schema:
            $ref: "#/components/schemas/JobGroupStatus"
        - name: page
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
      responses:
        "200":
          description: Success.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ListJobGroupsResponse"
components:
  schemas:
    JobGroupStatus:
      type: string
      enum:
        - OPEN
        - CLOSED
        - COMPLETED
        - FAILED
        - CANCELLED
    JobGroup:
      type: object
      required:
        - _id
        - groupJobQrn
        - status
        - organizationUserId
        - jobCount
        - completedCount
        - failedCount
        - cancelledCount
      properties:
        _id:
          type: string
        groupJobQrn:
          type: string
          example: group:a1b2-664f0c1e2a3b4c5d6e7f8090
        name:
          type: string
        status:
          $ref: "#/components/schemas/JobGroupStatus"
        organizationUserId:
          type: string
        jobCount:
          type: integer
          minimum: 0
        completedCount:
          type: integer
          minimum: 0
        failedCount:
          type: integer
          minimum: 0
        cancelledCount:
          type: integer
          minimum: 0
        totalEstimatedCost:
          type: number
          minimum: 0
        totalCost:
          type: number
          minimum: 0
        maxTTL:
          type: integer
          minimum: 1
          maximum: 86400
        timeStamps:
          type: object
          required:
            - createdAt
          properties:
            createdAt:
              type: string
              format: date-time
            endedAt:
              type: string
              format: date-time
            executionDuration:
              type: number
              minimum: 0
        tags:
          type: object
          additionalProperties:
            oneOf:
              - type: string
              - type: number
              - type: boolean
        metadata:
          type: object
          additionalProperties: true
    ListJobGroupsResponse:
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
            $ref: "#/components/schemas/JobGroup"
      title: ListJobGroupsResponse
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY
      description: Authenticate requests using an API key linked to your qBraid account. Obtain your key by registering or logging in at [account.qbraid.com](https://account.qbraid.com).
````
