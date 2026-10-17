# Quantum Inspire MCP server

`scripts/qi_mcp_server.py` is a stdio MCP server (mcp 2.3.0 `MCPServer`)
over the compute job manager REST API, run by the Quantum Inspire
interpreter so it reads the tokens `qi login` stored. It reuses
`scripts/qi_platform.py`'s `Client`, which renews the access token before
its 3600 s lifetime ends, so a long-lived server keeps working.

## Tools

| Tool | Effect | Annotation | Permission |
|---|---|---|---|
| `qi_backends()` | every backend type with qubits, status, shot and time limits, batch and queue limits, messages, queue | read-only | allow |
| `qi_backend(backend_type_id)` | one backend type in full: gate set, topology, compiler passes, limits, queue | read-only | allow |
| `qi_hardware_status()` | every backend instance with status, message, last heartbeat | read-only | allow |
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
