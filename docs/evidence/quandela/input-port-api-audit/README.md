# Quandela input-port API audit

The public OpenAPI captures retain exact retrieved bytes. The generated
inventories traverse every JSON node, resolve each local reference, and retain
every operation's method, parameters, request body, responses, security and
description. The Cloud document contains 39 method/path entries, Toolbox 3
and Account 14. All three Toolbox entries duplicate entries in the Cloud document;
56 entries therefore describe 53 distinct origin/method/path combinations.

The Account schema references the undefined `#/components/schemas/None`.
The inventory preserves that source defect in `unresolved_references`.
The strict `inventory()` interface rejects unresolved references. The audit
CLI retains them explicitly so the remaining source surface remains inspectable.

The portal route map records 59 literal `request$1` call sites in WebIDE
bundle `index-DrG4GsjV.js`, SHA-256
`2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e`.
The matching source identity also appears in the retained
[guide manifest](../../../notes/quandela/guide/MANIFEST.json).
The map is lexical evidence rather than proof of complete route coverage or
runtime reachability. Dynamic route templates retain their unresolved expressions.
The three literal strings `hardware_config`, `hardware_info` and
`circuit_input_ports` are absent from that bundle.

Live read-only probes on 22 October 2026 observed:

| Surface | Result | Boundary |
|---|---|---|
| Cloud `/health` | HTTP success, `message=ok` | HTTP service health, rather than optical instrument health |
| Token job availability | zero running, zero queued | token occupancy at that observation |
| Portal `/api/jobs/page?status=waiting` with the existing job token | HTTP 401 | the job token lacks access to this portal route |
| Portal `/api/platforms/lock-commands` with the existing job token | HTTP 401 | the job token lacks access to this portal route |
| Cloud WebIDE in the browser | redirected to account login | authenticated portal state remains unobserved |

The audit called neither QRNG endpoint, generated zero tokens and made zero
booking or platform-configuration requests. Job creation/cancellation belongs
to the separately retained acquisition receipts. The deprecated Account
`GET /api/logout` is classified as `session-mutation`, rather than admitted
to a read-only probe set merely because its HTTP method is GET.

Replay the retained contracts without network calls:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/quandela_api_inventory.py docs/evidence/quandela/input-port-api-audit
```

Add `--portal-map` to fetch and compare the public bundle. A fresh OpenAPI
capture uses `--capture` and a new destination; changing retained bytes raises
an error. The Cloud schema contains generated example identities, so equal
operation contracts can accompany differing raw document digests.

The [instrument-readiness design](../../../design/ascella-instrument-readiness-and-packed-tests.md)
binds the API findings to the static and native-mesh hardware diagnostics,
the client repairs and the remaining execution conditions.
