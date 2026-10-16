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
| `qi_submit(cqasm, backend_type_id, shots, approval, raw_data=True)` | one circuit as one batch job; executes on the backend; refuses an empty approval, an offline backend and an out-of-range shot count | mutating | ask |

A failed call raises `ToolError` with the service's message, so the client
sees `isError: true` and the reason (an unknown instruction returns the
libqasm analyzer error). A research run still goes through
`qi_platform.py submit`, which binds circuits to cases.json digests and
retains the records; `qi_submit` serves exploration.

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
ask for `mcp__quantum-inspire__qi_compile` and `mcp__quantum-inspire__qi_submit`.
The shell launcher loads `CLAUDE_MCP_SERVERS` (default
`kaggle,quantum-inspire`); `CLAUDE_MCP_SERVERS=` starts with none.

Quantum Inspire authentication belongs to the SDK: `codex mcp login` and
Claude's MCP OAuth do not replace `qi login`.

## Smoke test

A Python MCP client over stdio negotiates protocol 2025-11-25, lists the ten
tools with their annotations, runs `qi_run_local` on X q[0] (64 shots read
`01`), returns isError with the analyzer message for an unknown instruction,
and reads `qi_backends`, `qi_usage`, `qi_jobs` and `qi_job`.

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
