> Full piece: [https://docs.qbraid.com/v2/ai/user-guide/agent-mode.md](https://docs.qbraid.com/v2/ai/user-guide/agent-mode.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 a87f2ca4c75ab478b5e73e2631390292a33de348893dc97ee939123aff6476f7.

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

# Agent mode

> Attach a coding agent to a running compute instance or launch an instance from Account.

[Agent mode](https://account.qbraid.com/agent) runs a `codeq` terminal session inside a qBraid compute instance. The agent works with that instance's files, packages, and terminal.

## Start an agent session

1. Open **Agent** in qBraid Account.
2. Under **Your instances**, select **Attach** for a running instance or **Resume** for a stopped on-demand instance.
3. To create an instance, choose a profile under **Launch a new instance** and review the launch confirmation.
4. Wait for the instance and terminal to connect, then enter your task in the agent terminal.

Both subscription and on-demand instances can host the agent. The header identifies the attached instance and shows its per-minute credit rate when available.

A useful first task is:

```text
Create a Python script for a two-qubit Bell circuit.
Run it on an available free simulator and explain the measurement counts.
```

The agent uses the files and permissions available inside the instance. Review any approval prompts in the agent terminal and specify a spending limit before requesting paid hardware jobs.

## Reconnect or stop

If the terminal connection fails, select **Retry**. If the session ends while the instance is still running, select **Reconnect**.

Use **Stop instance** to stop the attached compute instance. The confirmation explains that this also ends the agent session. Closing the Agent page does not stop the instance.

Stopping an on-demand instance preserves its disk. Terminating it deletes its files. See [on-demand instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances) before removing an instance.

## Costs

Agent sessions use compute resources as well as AI tokens. Subscription instances draw on the applicable compute allocation, and on-demand instances use credits at their displayed rate. Model usage follows [AI quotas and credit spending](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas).

For platform questions that do not need a terminal, use [AI Chat](https://docs.qbraid.com/v2/ai/user-guide/ai-chat). For your own coding client, connect through the [AI Gateway](https://docs.qbraid.com/v2/ai/integrations/ai-gateway) and [MCP server](https://docs.qbraid.com/v2/ai/integrations/mcp-server).
