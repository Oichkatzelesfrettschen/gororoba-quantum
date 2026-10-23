# Quandela input-port API audit

The public OpenAPI captures retain exact retrieved bytes. The generated
inventories traverse every JSON node, resolve each local reference, and retain
every operation's method, parameters, request body, responses, security and
description. The Cloud document contains 39 method/path entries, Toolbox 3
and Account 14. All three Toolbox entries duplicate entries in the Cloud document;
56 entries therefore describe 53 distinct origin/method/path combinations.

The [instrument observation catalogue](../catalogue-instrument-observations.json)
retains the 22 October refresh under its own path. The
[historical catalogue](../catalogue.json) preserves the 20 October source cited
by the platform specification and calibration notes. The refresh SHA-256 is
`7cdf0b57ec28b9ad7d17fe6cb480a204506ecbd04f17013cb9e496308ed29df5`.

The Account schema references the undefined `#/components/schemas/None`.
The inventory preserves that source defect in `unresolved_references`.
The strict `inventory()` interface rejects unresolved references. The audit
CLI retains them explicitly so the remaining source surface remains inspectable.

## Schema validation and MCP contract repair

The 22 October 2026 host audit used `openapi-spec-validator` 0.9.0,
`openapi-schema-validator` 0.9.0 and `jsonschema` 4.26.0. The validator
accepted Cloud (OpenAPI 3.0.3), rejected Toolbox because `info.title` is
missing, and rejected Account because the reference above has no target.
The captures retain the vendor bytes, including both defects:

| Capture | SHA-256 | Validator outcome |
|---|---|---|
| Cloud | `d444026d3d2735c4eee078410e001efe67863d670b55aaa0696e8f440540ab2f` | valid |
| Toolbox | `a1fe41a393a997f6bd764f05043e7a6478fa295806c5aab0b733944896d2d279` | missing title |
| Account | `eecb463e7e8c53dc2d39b1ce2f3c07a9684210b82757584d0e877f6b4baac65a` | unresolved reference |

Replay the optional host validator with the interpreter that carries those
packages; the standard inventory replay below needs neither optional validator:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" - <<'PY'
import json
from pathlib import Path
from openapi_spec_validator import validate
for name in ("cloud", "toolbox", "account"):
    path = Path("docs/evidence/quandela/input-port-api-audit") / f"{name}-openapi.json"
    try:
        validate(json.loads(path.read_bytes()))
        print(name, "valid")
    except Exception as error:
        print(name, type(error).__name__)
PY
```

`paru -Ss 'openapi|jsonschema|httpie'` identified installed `openapi-tui`,
`python-jsonschema`, `python-openapi-spec-validator` and
`python-openapi-schema-validator`. Those packages cover browsing and structural
validation. `openapi-diff` can compare future captures; `openapi-generator`
generates clients but cannot repair missing provider-side instrument mappings.
The audit required zero package installations. Automated endpoint fuzzing stays
outside the audit because documented GET routes include priced QRNG and session
mutation, and job/booking/token operations change remote state.

Eight MCP tools expose eight unique remote operations plus local simulation.
Five operations appear in the Cloud OpenAPI capture; its paths omit all three
platform reads below. The 56 documented entries therefore describe a bounded
schema inventory rather than the complete service API:

| Tool | Cloud operation |
|---|---|
| `qd_platforms` | GET `/api/platforms/public/explorer`, GET `/api/platforms/public` |
| `qd_platform` | GET `/api/platforms/{name}/processor` |
| `qd_availability` | GET `/api/jobs/availability` |
| `qd_usage` | GET `/api/tokens/usage/report` |
| `qd_job_status` | GET `/api/jobs/{id}/status` |
| `qd_job_result` | GET `/api/jobs/{id}/result` |
| `qd_cancel_job` | POST `/api/jobs/{id}/cancel` |
| `qd_simulate_local` | host Perceval; provider access excluded |

## Dashboard queue and accounting boundaries

The platform manual says platform cards display pending jobs
([source](../../../notes/quandela/guide/user-guide/02-understanding-platforms.md)).
The reviewed WebIDE bundle traces `PlatformStatusList` through
`getObjectPermission(USER, user.id, {count_jobs:true})` to
`GET /api/platform-permissions/users/{user_id}?count_jobs=true` and renders
`waiting_jobs`. The route requires a dashboard session and the signed-in user's
identity. Its user-scoped path alone establishes neither a global count nor a
user-filtered count; authenticated response semantics remain unverified.
The job token received HTTP 401 from `/api/platforms`,
`/api/platform-permissions/explorer-tokens`, `/api/jobs/page?status=waiting`
and `/api/platforms/lock-commands` during the read-only audit.

A fresh headless Firefox probe with Selenium and geckodriver opened
`https://cloud.quandela.com/webide/` on 22 October. After the application
rendered, the page displayed `Session Expired`, `Your Session Has Ended` and
`GO TO LOGIN`. The probe used an isolated temporary browser profile and read
the page; it supplied neither passwords nor copied browser credentials.
Authenticated dashboard telemetry remains unobserved. `qd_availability`
therefore preserves the token's six counters and adds `platform_queue` with
`count=null`, `status=requires-dashboard-session`, the dashboard link and an
offer to open it. The MCP response neither launches a browser nor treats an
unknown count as zero. The stdio regression verifies the link and boundary
beside unchanged token counters.

At 20:44 UTC, the token reported zero running and one queued job, and job
`4058ce4e-7892-4da4-9e86-7f78f5fa9777` reported `waiting` with zero shots.
Recursive platform responses exposed neither a queue count nor queue position.
Explorer and processor reads reported Belenos `calibration`; the public list
reported `available`. The platform identifiers matched in memory. Those
observations establish a same-platform status disagreement, with cache or
synchronization causality unresolved. The runner's refusal to submit while
either token counter is occupied is a local conservative admission rule,
rather than a measurement of Ascella's scheduler occupancy.

The usage report totals 56 recorded jobs: Ascella 5, Belenos simulator 17 and
Belenos QPU 34. The QPU total includes the waiting job. The two completed
diagnostic jobs `c8d90a80-4330-4e7a-875e-938c561ca71c` and
`ef06045d-de41-47dc-ad42-e8fc8e318448` each added 164 execution seconds and
1.08 free credits consumed. Their totals progress from 53 to 54 to 55 jobs,
and QPU consumption from 30.30742 to 31.38742 to 32.46742 credits.
The waiting job increased the count to 56 while execution seconds and debit
stayed at 2921 and 32.46742. The second completed diagnostic, rather than an
unidentified additional acquisition, explains the second 1.08-credit debit.
These token-scoped cumulative counters establish neither account balance nor
platform queue depth. The documented shot rate likewise leaves job, slot,
notebook and QRNG pricing dependent on the account offer.

## Transport and source replay

The MCP 1.29 startup repair completes the SDK Settings forward references
instead of suppressing warnings. The server enables low-level JSON Schema
validation before FastMCP compatibility coercion and rejects undeclared tool
arguments. Local simulation rejects Boolean/fractional photon occupations and
nonfinite or oversized matrix entries before native arithmetic. The HTTP
adapter bounds responses to 64 MiB and classifies oversized or unusable JSON
acknowledgments as unanswered; a mutation can have happened despite an unusable
acknowledgment, so callers must reconcile before retrying.
Mutation HTTP 408 and 5xx responses likewise preserve an unknown outcome rather
than certify a refusal. A synthetic submission regression verifies that the
checkpoint stays `post_outcome_unknown` and a repeat invocation sends zero
additional POSTs. Explicit 401/403/404/422/429 rejections retain their status.

`tests/scripts/test_quandela_mcp_contract.py` exercises warning-free startup,
numeric rejection, bounded HTTP reads, unknown mutation outcomes and the real
SDK client/server stdio boundary. Synthetic transport tests disable provider
access and establish software contracts rather than optical instrument recovery.
`tests/scripts/test_quandela_mcp_transport.py` exercises every tool through a
real SDK stdio client with a synthetic HTTP fixture and a fail-closed network
guard. The fixture verifies public/authenticated route selection, account-id
redaction, bulk inclusion, nested truncation, raw results, cancellation
annotations and type/path rejection. Native descriptor-one output reaches
stderr while JSON-RPC remains parseable. Two HTTP reads synchronize through
worker-thread events, proving the event loop can serve a concurrent request.

The portal route map records 59 literal `request$1` call sites in WebIDE
bundle `index-DrG4GsjV.js`, SHA-256
`2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e`.
The matching source identity also appears in the retained
[guide manifest](../../../notes/quandela/guide/MANIFEST.json).
The map is lexical evidence rather than proof of complete route coverage or
runtime reachability. Dynamic route templates retain their unresolved expressions.
The offline inventory replay pins the route-map bytes to SHA-256
`29842b690e3fd8a48fa3d36286c5f7ec7258ba9639a62f9f5b6410a9f91c7262`.
That integrity check preserves the reviewed lexical evidence; recomputing the
call sites from the public bundle remains the separate `--portal-map` probe.
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
capture uses `--capture` and a new or empty destination; the destination check
precedes network access. The capture writes `capture-sha256.json`, which binds
that successor's three raw schemas and portal route map. An offline replay
uses the successor's own ledger, so a new WebIDE deployment can enter a new
capture without replacing the historical portal digest. The ledger records
retrieved identity; an unreviewed successor remains a new evidence object.

The historical capture in this directory always uses the four reviewed
code-pinned SHA-256 values, including each raw OpenAPI document's digest in
the table above. A local successor ledger cannot replace those historical
pins. A historical copy without a successor ledger also uses those pins.
The replay checks each raw source before comparing its derived inventory;
editing a source and its inventory together therefore rejects the historical
replay. Changing successor source bytes without matching its retained ledger
also raises an error. The Cloud schema contains generated example identities,
so equal operation contracts can accompany differing raw document digests.

The [instrument-readiness design](../../../design/ascella-instrument-readiness-and-packed-tests.md)
binds the API findings to the static and native-mesh hardware diagnostics,
the client repairs and the remaining execution conditions.
