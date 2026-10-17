> Full piece: [https://docs.openquantum.com/mcp/overview/](https://docs.openquantum.com/mcp/overview/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ae739a06276d99d69c73dd3d50442ec93b6e35c92c30475cf2cba1739d40f9d8.

# AI Agents & MCP

Run Open Quantum jobs from AI coding agents using the [Model Context Protocol](https://modelcontextprotocol.io) (MCP).

The **`openquantum-mcp`** package is a local stdio MCP server on top of the [Core SDK](https://docs.openquantum.com/core-sdk/overview/). Compatible clients (Claude, Cursor, VS Code, Grok, and others) can discover backends, submit circuits, wait for completion, and summarize results using **your** SDK key — without hand-writing boilerplate for each iteration.

## What you get

- **Discover** organizations, backends, and credit balances
- **Prepare** a job and inspect the credit quote before spend
- **Submit** OpenQASM circuits to real QPUs and simulators
- **Wait / poll** for status (queues can be long; the agent re-polls)
- **Summarize** measurement counts and fetch calibration on demand

There is a **single** MCP server for all clients. Client apps differ only in how you register the process and environment variables.

## How it works

[](#__codelineno-0-1)`AI client (Claude, Cursor, …)`\
[](#__codelineno-0-2)`        │  MCP (stdio)`\
[](#__codelineno-0-3)`        ▼`\
[](#__codelineno-0-4)` openquantum-mcp  (local process on your machine)`\
[](#__codelineno-0-5)`        │`\
[](#__codelineno-0-6)`        ▼`\
[](#__codelineno-0-7)` openquantum-sdk  →  Open Quantum APIs`\

Credentials stay on your machine in the MCP process environment.

## Prerequisites

- Python **3.10+**
- An [Open Quantum account](https://www.openquantum.com) and [SDK key](https://docs.openquantum.com/portal/sdk-keys/)
- An MCP-capable agent or IDE

## Next steps

- [Installation](https://docs.openquantum.com/mcp/installation/) — install from PyPI and verify
- [Client setup](https://docs.openquantum.com/mcp/client-setup/) — wire Claude, Cursor, and other hosts
- [Tools & spend policy](https://docs.openquantum.com/mcp/tools/) — tool reference and credit safeguards

## Related

- [SDK keys](https://docs.openquantum.com/portal/sdk-keys/)
- [Credits & pricing](https://docs.openquantum.com/concepts/credits/)
- [Job lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/)
- [Core SDK authentication](https://docs.openquantum.com/core-sdk/authentication/)
