> Full piece: [https://docs.qbraid.com/v2/ai/user-guide/usage-quotas.md](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 739d779eaa2ff730eecf2d0923f973877997e9d03892f877df25ef0abe6af1e4.

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

# AI usage quotas

> Check your AI allowance, token costs, and policy for spending credits.

AI usage consumes your plan's allowance before it uses wallet credits. Usage and credit balances belong to the selected workspace.

## Plan allowances

| Plan     | AI allowance per quota period    | Default Auto-switch to Credits |
| -------- | -------------------------------- | ------------------------------ |
| Free     | $5, equivalent to 500 credits    | Off                            |
| Standard | $15, equivalent to 1,500 credits | On                             |
| Pro      | $50, equivalent to 5,000 credits | On                             |

These are AI spending allowances, not deposits into your wallet. Check **Account > Usage > AI Chat Usage** for the actual renewal date and any account-specific allocation. All current tiers can use the model catalog. A more expensive model consumes the same allowance faster.

## Token costs

Each model has separate rates for input and output tokens. [Models and pricing](https://docs.qbraid.com/v2/account/models) lists the rate units and explains how to inspect the model picker. Longer prompts, longer answers, and tool results that add conversation context can increase usage.

For an uncached request, estimate the cost in credits as:

```text
(input tokens × input rate + output tokens × output rate) / 1,000,000
```

Use rates in credits per million tokens. Cached-token billing can change the final cost. qBraid supports fractional credits, so a small request does not automatically round up to a whole credit.

## When the allowance runs out

- With allowance remaining, usage draws from the allowance.
- With **Auto-switch to Credits** enabled, usage beyond the allowance can draw from the wallet. A request that crosses the boundary can use both.
- With auto-switch disabled, exhausted allowance blocks further requests. Enable credit spending if permitted, upgrade, or wait for renewal.
- With auto-switch enabled but no available credits, add credits or wait for renewal.

A remainder of $0.01 or less counts as exhausted when the application decides whether you can send another request. In an organization, the organization's effective policy can override a member's personal auto-switch setting.

The final token cost is known after generation. A request can exceed the allowance that remained when it started. The displayed ability to send is not a guarantee that the remaining allowance will cover the entire response. An outstanding AI balance can also block later requests until it can be settled.

## Track usage

1. Select your workspace.
2. Open [Account > Usage](https://account.qbraid.com/account/usage).
3. Inspect **AI Chat Usage** for consumption, the renewal date, and whether you can send requests.
4. Review **Auto-switch to Credits** before you continue beyond your allowance.

For individual charges, use [Wallet payment history](https://docs.qbraid.com/v2/account/wallet/payment-history). Organization administrators can inspect [organization transactions](https://docs.qbraid.com/v2/account/organizations/transactions).

## Reduce costs

Select a model with a lower token rate when it meets your needs. Keep prompts and requested output focused. Use agent tools when the task needs them, since tool results add context that the model must process.

To increase your allowance, compare [personal subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions) or [team subscriptions](https://docs.qbraid.com/v2/account/organizations/subscriptions). For compute and storage limits, see [Usage limits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits).
