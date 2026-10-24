> Full piece: [https://docs.qbraid.com/v2/ai/user-guide/overview.md](https://docs.qbraid.com/v2/ai/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 6efac4d9f91c9fae0a68e48c588c9c38549b8b301dd485e2b71bda92d7832f41.

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

# qBraid AI

> Use AI Chat, run an agent in a compute instance, or connect your own AI client.

qBraid AI connects language models to quantum devices, jobs, and platform tools. Choose the interface that fits your task:

<CardGroup cols={2}>
  <Card title="AI Chat" icon="comments" href="/v2/ai/user-guide/ai-chat">
    Ask questions, inspect devices and jobs, and continue saved conversations in Account.
  </Card>
  <Card title="Agent mode" icon="robot" href="/v2/ai/user-guide/agent-mode">
    Run a coding agent in a subscription or on-demand compute instance.
  </Card>
  <Card title="AI Gateway" icon="route" href="/v2/ai/integrations/ai-gateway">
    Call available models from OpenAI-compatible or Anthropic-compatible clients with your qBraid API key.
  </Card>
  <Card title="MCP server" icon="plug" href="/v2/ai/integrations/mcp-server">
    Connect an external AI client to qBraid tools using OAuth.
  </Card>
</CardGroup>

## Start a conversation

Open [AI Chat](https://account.qbraid.com/chat), select a model, and ask a question. For example:

```text
List the available quantum simulators and compare their prices.
```

Tool calls can retrieve current platform information. Check the returned device status, cost estimate, and job result before acting on an answer.

## Models and usage

The model selector shows the models available to your account. See [AI Gateway](https://docs.qbraid.com/v2/ai/integrations/ai-gateway#available-models) for model discovery and pricing, and [usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas) for included AI usage and credit spending.

Running an agent also uses the compute instance you attach to. Its compute charges are separate from model usage. See [compute pricing](https://docs.qbraid.com/v2/home/pricing#cpus-and-gpus).
