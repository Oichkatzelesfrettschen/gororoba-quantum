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

Eight MCP tools expose eight unique Cloud operations plus local simulation:

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

The MCP 1.29 startup repair completes the SDK Settings forward references
instead of suppressing warnings. The server enables low-level JSON Schema
validation before FastMCP compatibility coercion and rejects undeclared tool
arguments. Local simulation rejects Boolean/fractional photon occupations and
nonfinite or oversized matrix entries before native arithmetic. The HTTP
adapter bounds responses to 64 MiB and classifies oversized or unusable JSON
acknowledgments as unanswered; a mutation can have happened despite an unusable
acknowledgment, so callers must reconcile before retrying.

`tests/scripts/test_quandela_mcp_contract.py` exercises warning-free startup,
numeric rejection, bounded HTTP reads, unknown mutation outcomes and the real
SDK client/server stdio boundary. Synthetic transport tests disable provider
access and establish software contracts rather than optical instrument recovery.

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
capture uses `--capture` and a new destination; changing retained bytes raises
an error. The Cloud schema contains generated example identities, so equal
operation contracts can accompany differing raw document digests.

The [instrument-readiness design](../../../design/ascella-instrument-readiness-and-packed-tests.md)
binds the API findings to the static and native-mesh hardware diagnostics,
the client repairs and the remaining execution conditions.
