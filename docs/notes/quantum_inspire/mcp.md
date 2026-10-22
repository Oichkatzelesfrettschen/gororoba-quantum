# Quantum Inspire MCP server

`scripts/qi_mcp_server.py` is a stdio MCP server (mcp 2.3.0 `MCPServer`)
over the compute job manager REST API, run by the Quantum Inspire
interpreter so it reads the tokens `qi login` stored. It reuses
`scripts/qi_platform.py`'s `Client`, which renews the access token before
its 3600 s lifetime ends, so a long-lived server keeps working.

## Tools

| Tool | Effect | Annotation | Permission |
|---|---|---|---|
| `qi_backends(user_only=True)` | every backend type with qubits, status, limits and explicitly scoped queue | read-only | allow |
| `qi_backend(backend_type_id, user_only=True)` | one backend type, matching physical instances, compiler configuration, limits and explicitly scoped queue | read-only | allow |
| `qi_hardware_status()` | every backend instance with status, message, heartbeat and retrieval interval | read-only | allow |
| `qi_usage()` | the transaction ledger aggregated by domain and backend type, beside each job's shots and execution seconds | read-only | allow |
| `qi_jobs(latest=20)` | most recent jobs, newest first | read-only | allow |
| `qi_job(job_id)` | one job, its result metadata and, unless completed, its logs | read-only | allow |
| `qi_results(job_id, include_raw=False)` | outcome counts, and every shot on request | read-only | allow |
| `qi_run_local(cqasm, shots=1024)` | local qxelarator emulation, at most 24 qubits and 100000 shots | read-only, closed world | allow |
| `qi_compile(cqasm, backend_type_id, stage="decomposition")` | remote compilation; creates project, algorithm, commit and file; executes nothing | mutating | ask |
| `qi_submit_case(case_dir, backend_type_id, approval)` | one batch from retained `cases.json` and checked cQASM files; enables raw shots and uses the durable submission guard | mutating | ask |
| `qi_submit(cqasm, backend_type_id, shots, approval, raw_data=True)` | legacy signature; refuses execution and names `qi_submit_case` as its replacement | refuses execution | no execution |

A failed call raises `ToolError` with the service's message, so the client
sees `isError: true` and the reason (an unknown instruction returns the
libqasm analyzer error). Every execution uses `qi_platform.py submit`,
directly or through `qi_submit_case`, which binds circuits to cases.json
digests and retains the records. The legacy raw-string tool no longer
provides an unrecorded exploration path.

To migrate a raw-string call, write its cQASM to a retained case directory
and add `cases.json` with `backend`, `backend_type_id`, `shots` and the
ordered `circuits` list of `file` and `sha256` entries. Pass that directory
and the approval to `qi_submit_case`; the manifest supplies the shot count.
The tool checks the current user's queue capacity before creating resources
and returns a `qi-submission-v2` receipt with `state: enqueued`, the manifest's
`cases_sha256`, and each uploaded job's circuit `sha256`.
An uncertain enqueue response leaves `submission-state.json`, which blocks
a retry. Use `qi_platform.py reconcile CASE_DIR` for read-only receipt
recovery, then `qi_platform.py collect CASE_DIR` to retain the raw shots.
The recovery and retention rules are in [usage.md](usage.md).

## Status and queue interpretation

The status tools issue fresh API GET requests on every call; the cached object is the authenticated
HTTP client, rather than a cached catalogue. `request_started_utc` and `retrieved_utc` bound each
observation. The backend-type, queue and physical-instance reads are sequential observations,
not an atomic snapshot. A transition between those reads can produce different statuses.

`enabled` is the provider's enable flag; the API does not define it as account entitlement.
The backend type's `status` records operational state;
`backend_instances` retains the physical instances' separate statuses and `last_heartbeat` values.
A recent heartbeat establishes that an instance reports to the service; an `offline` instance with
a recent heartbeat remains offline. Each physical-instance row returned by `qi_hardware_status`
also carries the API retrieval interval separately from its heartbeat.

Queue reads default to `user_only=true`, matching `qi_platform.submit`'s account-scoped admission
check. `queue_user_only` records the scope in every response. Pass `user_only=false` explicitly
to inspect the global queue; another user's waiting batch does not consume this account's queue
capacity. An empty account queue alone establishes neither online hardware nor an elapsed hardware
pause. Submission repeats its own account queue and account-wide hardware-pause checks under the
submit lock.

Long-lived stdio processes retain their imported implementation until the MCP host reconnects them.
After deploying a server change, reconnect the Quantum Inspire server in each owning session and
verify that the discovered `qi_backend` input schema includes `user_only` with default `true`.
Leave another session's server process under that session's ownership. Compare status values only
with timestamped direct API reads; a historical tool response is an observation, not a live monitor.

## Registration

```sh
QI_PY=$HOME/.local/share/quantuminspire/venv/bin/python
SRV=$HOME/Projects/IBMQuantum/scripts/qi_mcp_server.py
claude mcp add --transport stdio --scope user quantum-inspire -- "$QI_PY" -I "$SRV"
codex mcp add quantum_inspire -- "$QI_PY" -I "$SRV"
```

User scope makes the server available in every project
(`~/.claude.json` top level; `~/.codex/config.toml` `[mcp_servers.quantum_inspire]`).
The path names the primary checkout, so the server connects once the
branch carrying it is merged there. `-I` isolates the interpreter from the
working directory; the script adds its own directory to `sys.path` for
`qi_platform`.

Claude Code permission rules in `~/.claude/settings.json`: allow
`mcp__quantum-inspire__qi_{backends,backend,hardware_status,usage,jobs,job,results,run_local}`,
ask for `mcp__quantum-inspire__qi_compile` and `mcp__quantum-inspire__qi_submit_case`.
The shell launcher loads `CLAUDE_MCP_SERVERS` (default
`kaggle,quantum-inspire`); `CLAUDE_MCP_SERVERS=` starts with none.

Quantum Inspire authentication belongs to the SDK: `codex mcp login` and
Claude's MCP OAuth do not replace `qi login`.

## Smoke test

The original Python MCP smoke test over stdio negotiated protocol 2025-11-25,
listed ten tools with their annotations, ran `qi_run_local` on X q[0] (64 shots read
`01`), returned isError with the analyzer message for an unknown instruction,
and read `qi_backends`, `qi_usage`, `qi_jobs` and `qi_job`.

The case-directory migration adds the eleventh tool. The mock-only contract
`scripts/check_qi_platform_retention.py` imports the server with SDK stubs,
checks the legacy refusal and guarded submission, and verifies that a repeat
submission becomes `ToolError` without terminating stdio or printing to it.
These checks require neither the MCP SDK nor credentials. They do not rerun
the original SDK transport smoke test.

The status/queue repair also ran a fresh mcp 2.3.0 stdio session against direct API reads.
At 2026-10-22T16:50:19Z through 16:50:23Z, direct reads before and after the MCP call and
the MCP backend-type response all reported Tuna-17 `offline`. The physical instance also
reported `offline`, with heartbeat 16:50:15.229017Z. The account queue contained zero batches.
The session discovered all eleven tools and a boolean `user_only` input with default `true`.
The observation establishes transport/schema conformance at that time, rather than a persistent
availability claim. The SDK-free regressions also exercise changed statuses between calls,
different backend-type and physical-instance statuses, account/global queue differences and
UTC retrieval intervals.

## Community bridge, for comparison

quantum-vibecoding-mcp 0.1.0 (`qvc-qi`, five tools; source at
JDerekLomas/quantuminspire commit 08396a5, `mcp-servers/src/quantum_vibecoding_mcp/qi.py`)
imports `quantuminspire.util.api.remote_backend` and `local_backend`, which
quantuminspire 4.1.0 no longer ships, and `mcp.server.fastmcp`, which mcp 2.x
renamed to `mcp.server.mcpserver`; it needs an older stack in a separate
environment (an outside compatibility check ran it under quantuminspire 3.5.3
and mcp 1.30.0, not rerun here), returns errors as `{"error": ...}` inside a
successful result, and offers no compile, usage or logs tool. This repository does not
install it.
