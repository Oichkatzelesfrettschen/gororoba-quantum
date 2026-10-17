> Full piece: [https://docs.openquantum.com/mcp/tools/](https://docs.openquantum.com/mcp/tools/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 76ffa725adfcd2f52f953cb7ea78baeaf2062c8c49525ef41e82ce8ea3e5bed4.

# Tools & spend policy

This page describes the MCP tools exposed by **`openquantum-mcp`** and the credit safeguards the server enforces.

## Tool reference

### Account & discovery

| Tool | Description |
|----|----|
| `list_organizations` | Organizations for the authenticated account |
| `get_credits` | Spark and Full balances. Uses `organization_id`, else `OPENQUANTUM_ORGANIZATION_ID`, else the first org |
| `list_backends` | Backend classes with optional filters (`online_only`, `device_type`, `name_contains`, `max_qubits`) |
| `get_backend` | Details for one backend (short code or UUID); large constraint docs are summarized |
| `list_job_categories` | Categories and subcategories for `job_subcategory_id` |

### Job lifecycle

| Tool | Description |
|----|----|
| `prepare_job` | Upload OpenQASM (`qasm` string or `file_path`), prepare a quote; **does not** create the job or spend credits |
| `submit_job` | Create a job from a `preparation_id` **or** one-shot (backend + circuit). **Does not** wait for completion |
| `get_job` | Single status fetch |
| `list_jobs` | Recent jobs for an organization |
| `wait_for_job` | Poll until terminal status or timeout (default from `OPENQUANTUM_MCP_WAIT_TIMEOUT_SECONDS`, 600s). On timeout, returns current status so the agent can re-poll |
| `get_job_results` | Download and summarize output (bitstring counts when present; compact fallback otherwise) |
| `get_job_calibration` | Download calibration **only when requested** (not part of default results) |
| `cancel_job` | Cancel when platform rules allow (typically Pending only) |

### Circuit input

- Prefer **OpenQASM** text via `qasm`, or a local `file_path` readable by the MCP process.
- Default `job_subcategory_id` is **`oth:oth`** if omitted.
- Default shots: **128** (override per call or with `OPENQUANTUM_MCP_DEFAULT_SHOTS`).
- Jobs are tagged `submitted_with=mcp` for platform analytics.

Local file paths

`file_path` is read by the MCP process and **uploaded to the platform**. Anything the process user can read can leave the machine if an agent is tricked into passing that path as a “circuit.” Prefer inlining QASM via `qasm` when possible, and run the server with least privilege. Invalid QASM is rejected later by the scheduler — **after** the bytes have already been uploaded.

### Execution plan & queue priority

Both `prepare_job` and `submit_job` accept:

| Parameter | Default | Accepted values |
|----|----|----|
| `execution_plan` | `auto` | `auto`, `public`, `private`, or a raw execution-plan UUID |
| `queue_priority` | `auto` | `auto`, `standard`, `priority`, `instant`, or a raw queue-priority UUID |

- **`auto` plan:** the server prefers **Public** so Spark credits can apply when available, then lowest cost among remaining options.
- **Force Spark-eligible jobs:** pass `execution_plan="public"`. Private plan spend uses Full credits and requires `confirm_spend=true`.
- **Queue priority** changes price via the quote’s per-priority increase; `auto` picks the cheapest valid priority for the selected plan.

### Prepare response: quote & spend preview

`prepare_job` returns (among other fields):

| Field | Meaning |
|----|----|
| `estimated_credits` | Cost for the **selected** plan + priority |
| `execution_plan_name` / `queue_priority_name` | Human-readable selection |
| `quote_summary` | All quote plans with base price and each queue priority’s `price_increase` / `total`, plus which pair is `selected` |
| `spend_preview` | Whether submit would auto-approve, need `confirm_spend`, and the policy message |

Agents that need to choose Instant vs Standard (or compare Public vs Private) should read `quote_summary` before calling `submit_job`.

### Recommended agent flow

1.  `get_credits` / `list_backends`
2.  `prepare_job` → review `estimated_credits`, `quote_summary`, and `spend_preview`
3.  `submit_job` with `confirm_spend=true` when required
4.  `wait_for_job` (repeat if still queued)
5.  `get_job_results`
6.  `get_job_calibration` only if needed

## Spend policy

Open Quantum has two credit types: **Spark** (promotional / free tier, Public plan) and **Full** (purchased). See [Credits](https://docs.openquantum.com/concepts/credits/).

The MCP server applies:

| Rule | Behavior |
|----|----|
| **Hard cap** | Estimated cost **\> 10 credits** is rejected (override with `OPENQUANTUM_MCP_MAX_CREDITS`) |
| **Free jobs** | Cost **0** proceeds without confirmation |
| **Spark auto-spend** | Public plan and Spark balance ≥ cost (and ≤ cap) → allowed **without** `confirm_spend` |
| **Full credits** | Private plan, or Public when Spark is insufficient → requires **`confirm_spend=true`** |

On auto plan selection the server prefers **Public** so Spark can apply when available.

Warning

Agents can submit jobs quickly. Keep the credit cap low for shared machines, and require explicit confirmation before Full credit spend. Never put SDK secrets in prompts or committed config without a secrets manager.

## Multi-organization accounts

If `organization_id` is omitted, the server uses `OPENQUANTUM_ORGANIZATION_ID` when that variable is set. Otherwise it uses the **first** organization returned by the API and reports which org was selected. Pass `organization_id` explicitly when you belong to more than one org and need a specific one.

## Platform limits (reminder)

- Maximum active jobs per organization (see [job lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/))
- Maximum QASM payload size
- Cancel only in allowed statuses (typically Pending)

Tool errors surface these constraints when the API rejects a call.

## Results & calibration

- **`get_job_results`** returns a compact summary suitable for chat context. Bitstring count maps are summarized as top-N outcomes.
- Set `include_raw=true` only when you need a truncated raw payload.
- Calibration is **opt-in** via `get_job_calibration` when the completed job has a calibration URL.
