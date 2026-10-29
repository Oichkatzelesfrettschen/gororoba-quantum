# Unsent SDK issue draft: backend metadata route and deployed API

**Target:** [Quantum Inspire SDK issues](https://github.com/QuTech-Delft/quantuminspire/issues)

**Status:** Draft; do not post without explicit messaging authorization.

**Title:** Clarify generated backend-metadata client methods when the deployed API omits the route

## Observed behavior

On 2026-10-28 UTC, the Quantum Inspire API's served OpenAPI document at
`https://api.quantum-inspire.com/openapi.json` listed 53 paths and no `/metadata` route.
An authenticated read-only GET of `/metadata/backend/7`, with `latest=true`, `page=1`
and `size=1`, returned HTTP 404 and `Not Found`. Backend 7 was the Tuna-17 backend
instance in the observed account. The local environment reported
`qi-compute-api-client` 0.64.0 and `quantuminspire` 4.2.0; the generated client included
backend-metadata methods. The observed client version does not identify the provider's
deployed server version. A 404 describes this route at the observed time and does not
establish whether the provider retains calibration or acquisition information internally.

The [sanitized served-API observation](../../evidence/tuna-projector-geometry/destination-served-api-observation.json)
and [runtime observation](../../evidence/tuna-projector-geometry/destination-one-runtime.json)
retain retrieval times and hashes. The API may have changed since the observations.

## Reproduction boundary

1. Inspect the currently served OpenAPI path inventory and the installed client version.
2. If the account can access the chosen backend, use the supported authenticated client to
   request its metadata with the parameters above. Keep credentials and account identifiers
   out of the report and logs.
3. Compare the generated client's advertised operation and its documentation with the
   deployed path inventory and response. Do not submit or upload a circuit for this check.

## Expected clarification

Please identify the supported API or export route for backend metadata, and whether the
generated method describes a different service deployment or API revision. If the route
is deliberately unavailable, please clarify the generated-client compatibility contract
and documentation. Separately, can any supported export bind a calibration configuration to
an individual completed job? A backend-wide latest snapshot alone would not establish the
configuration that served a past acquisition.

The separate [private support draft](../../notes/quantum_inspire/destination-response-upstream-request.md)
names six completed jobs and requests acquisition-event association, pre-packing labels,
IQ/discriminator settings and served schedules. That private request is the appropriate
place for job-specific traces. This public draft contains no raw shots or account-specific
identifiers; backend 7 is the public backend-instance identifier recorded above. The
[QX simulator draft](../../notes/quantum_inspire/upstream-readout-report.md#unsent-qx-contract-report)
concerns result representation and should remain a separate issue.
