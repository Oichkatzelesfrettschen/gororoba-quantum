> Full piece: [https://docs.qbraid.com/v2/ai/integrations/ai-gateway.md](https://docs.qbraid.com/v2/ai/integrations/ai-gateway.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 cb7f1c7debc50ba096e2bb90c9216f6b431ae324b5c408b9f1537019275d668a.

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

# AI Gateway

> Call GPT and Claude models through the qBraid API with one API key.

The AI Gateway proxies language-model requests through the qBraid API using
OpenAI and Anthropic request formats. To use it with your existing SDK,
change the base URL and API key.

```text
https://api-v2.qbraid.com/api/v1/ai
```

Every request authenticates with your qBraid API key in the `X-API-Key`
header. Create a key at
[account.qbraid.com/account/api-keys](https://account.qbraid.com/account/api-keys).
The [API Keys guide](https://docs.qbraid.com/v2/account/api-keys) explains how to manage and
rotate keys.

## Endpoints

| Endpoint                         | Wire format             | Use with                             |
| -------------------------------- | ----------------------- | ------------------------------------ |
| `POST /chat/completions`         | OpenAI Chat Completions | `openai` SDKs, LangChain, most tools |
| `POST /responses`                | OpenAI Responses        | newer `openai` SDKs, Codex CLI       |
| `GET /models`                    | OpenAI                  | model discovery                      |
| `POST /v1/messages`              | Anthropic Messages      | `anthropic` SDKs, Claude Code        |
| `POST /v1/messages/count_tokens` | Anthropic               | token counting                       |
| `GET /quota`                     | qBraid                  | your remaining LLM quota             |

Anthropic routes include `/v1` because Anthropic SDKs append
`/v1/messages` to whatever base URL you give them. The gateway matches that
shape, so the same base URL works for both wire formats.

## Quickstart

The Anthropic SDK sends the `x-api-key` header on its own, so its `api_key`
argument takes your qBraid key directly. The OpenAI SDK only sends a bearer
header, so give it the key through `default_headers` instead.

<CodeGroup>

```bash curl
curl https://api-v2.qbraid.com/api/v1/ai/chat/completions \
  -H "X-API-Key: $QBRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.5",
    "messages": [{ "role": "user", "content": "Explain the GHZ state in two sentences." }]
  }'
```

```python Python (OpenAI SDK)
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api-v2.qbraid.com/api/v1/ai",
    api_key="unused",  # the gateway reads X-API-Key below
    default_headers={"X-API-Key": os.environ["QBRAID_API_KEY"]},
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Explain the GHZ state in two sentences."}],
)
print(response.choices[0].message.content)
```

```typescript TypeScript (OpenAI SDK)
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api-v2.qbraid.com/api/v1/ai",
  apiKey: "unused", // the gateway reads X-API-Key below
  defaultHeaders: { "X-API-Key": process.env.QBRAID_API_KEY },
});

const response = await client.chat.completions.create({
  model: "gpt-5.5",
  messages: [
    { role: "user", content: "Explain the GHZ state in two sentences." },
  ],
});
console.log(response.choices[0].message.content);
```

```python Python (Anthropic SDK)
import os

from anthropic import Anthropic

client = Anthropic(
    base_url="https://api-v2.qbraid.com/api/v1/ai",
    api_key=os.environ["QBRAID_API_KEY"],  # the SDK sends this as x-api-key
)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain the GHZ state in two sentences."}],
)
print(response.content[0].text)
```

</CodeGroup>

## Use with Claude Code

Claude Code uses the Anthropic request format, so it can use your qBraid
quota. Set the base URL and your key, then start it:

```bash
export ANTHROPIC_BASE_URL="https://api-v2.qbraid.com/api/v1/ai"
export ANTHROPIC_API_KEY="$QBRAID_API_KEY"
claude
```

`ANTHROPIC_API_KEY` reaches the gateway as the `x-api-key` header.

## Available models

Query `/models` for the current model catalog:

```bash
curl https://api-v2.qbraid.com/api/v1/ai/models \
  -H "X-API-Key: $QBRAID_API_KEY"
```

The response uses the OpenAI model-list format. Each entry includes its canonical `id` and qBraid metadata under `_qbraid`:

- `name`, `description`, and `provider` describe the model.
- `aliases` lists accepted alternative IDs.
- `capabilities` describes image input, structured outputs, and parallel tool-call control.
- `supportedEndpoints` lists the generation endpoints that accept the model.
- `pricing.inputCreditsPerMillionTokens` and `pricing.outputCreditsPerMillionTokens` give the token rates in qBraid credits.

Check `supportedEndpoints` before selecting a model for Chat Completions, Responses, or Anthropic Messages. Catalog discovery omits models without a callable generation endpoint. A missing pricing block does not mean a model is free.

By default, the catalog reflects the caller's model-access policy. `?includeLocked=1` also returns plan-locked models with `_qbraid.requiredTier` when restrictions apply. All current plan tiers allow the catalog, but still have different usage allowances.

See [Models and pricing](https://docs.qbraid.com/v2/account/models#model-rate-reference) for a dated rate reference that includes the GPT-6 family, GPT-6.1 Sol, Claude Opus 5.5, Claude Sonnet 5, and Claude Fable 5.1. Query the catalog for current IDs and rates before integrating a model.

Costs draw from your plan's AI allowance first. Spending beyond that allowance requires the effective **Auto-switch to Credits** policy and sufficient credits. The standard conversion is 100 credits = $1. See [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas).

## Check your quota

```bash
curl https://api-v2.qbraid.com/api/v1/ai/quota \
  -H "X-API-Key: $QBRAID_API_KEY"
```

The response contains your LLM subscription state and remaining quota. Streaming
responses also carry standard rate-limit headers.

<Tip>
  The gateway gives your code raw model access. If you want an AI client to act
  on the qBraid platform itself, with tools for devices, jobs, and credits,
  connect the [MCP Server](https://docs.qbraid.com/v2/ai/integrations/mcp-server).
</Tip>
