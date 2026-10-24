> Full piece: [https://docs.qbraid.com/v2/account/models.md](https://docs.qbraid.com/v2/account/models.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 bb3b9fb05ed8e3a352a0d6937aaf8de6d46d598267c765ba316a2c5f6a005dba.

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

# Models and pricing

> Find available AI models, compare token rates, and understand plan allowances and credits.

qBraid Account's AI model picker lists OpenAI and Claude models with their current input and output rates. Your subscription allowance pays for AI usage first. If **Auto-switch to Credits** is enabled, additional usage can draw from your workspace's credit balance.

## Choose a model

1. Open AI chat in your selected workspace.
2. Select the model name beside the message composer.
3. Search by model name or ID.
4. Compare the input and output rates, then select a model.

The picker groups models under **OpenAI** and **Claude**. Capability labels include **Coding**, **Vision**, and **Economy** where applicable. A **Vision** label indicates image-input support. **Economy** identifies a model with a lower output-token rate.

Rates appear as **credits per 1M tokens**, with input first and output second. For example, `200 / 1k` means 200 credits per million input tokens and 1,000 credits per million output tokens. These are rates, not a charge for each message.

All current subscription tiers can use the models in the catalog. If an access policy changes, unavailable models appear under **Requires an upgrade**. The catalog can change as models are added or removed. If loading fails, select **Models unavailable. Retry**.

<Frame>
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nA1sFxePFLTOKHSVhQoix0NRqJsd4ynPDlm6B"
    alt="AI model picker showing search, Vision and Economy labels, and input and output credit rates"
  />
</Frame>

The picker shows input and output credits per million tokens beside each model.

## Model rate reference

The following rates were checked against qBraid's released API rate card and the live Account model picker on October 5, 2026. Prices are in **qBraid credits per million tokens**. The picker and [AI Gateway model catalog](https://docs.qbraid.com/v2/ai/integrations/ai-gateway#available-models) provide the current rates and availability.

| Model ID            | Input | Output |
| ------------------- | ----: | -----: |
| `gpt-6-astra`       |  1000 |   5000 |
| `gpt-6-sol`         |   200 |   1000 |
| `gpt-6-luna`        |    10 |     50 |
| `gpt-6.1-sol`       |   200 |   1000 |
| `gpt-5.6-sol`       |   500 |   3000 |
| `gpt-5.6-luna`      |   100 |    600 |
| `gpt-5.6-terra`     |   250 |   1500 |
| `gpt-5.5`           |   500 |   3000 |
| `gpt-5.4`           |   250 |   1500 |
| `gpt-5.4-mini`      |    75 |    450 |
| `gpt-5.4-nano`      |    20 |    125 |
| `gpt-5.3-codex`     |   175 |   1400 |
| `claude-sonnet-4-6` |   300 |   1500 |
| `claude-haiku-4-5`  |   100 |    500 |
| `claude-opus-4-8`   |   500 |   2500 |
| `claude-opus-5`     |   500 |   2500 |
| `claude-opus-5-5`   |   400 |   2000 |
| `claude-sonnet-5`   |   200 |   1000 |
| `claude-fable-5-1`  |  1000 |   5000 |

At the standard conversion, 100 credits equals $1 USD. Cached-input rates can change a request's charge. Use token estimates to plan usage, then check the recorded charge. Review **Account > Usage** and wallet transactions for recorded usage.

## Plans, allowances, and credits

| Resource                  | How to check the price or limit                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| Personal subscription     | [Personal plans](https://docs.qbraid.com/v2/account/wallet/subscriptions) and the wallet's plan cards           |
| Organization subscription | [Team subscriptions](https://docs.qbraid.com/v2/account/organizations/subscriptions), priced per purchased seat |
| AI usage                  | Model picker rates and [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas)                 |
| Quantum jobs              | The selected device's pricing and job estimate                                           |
| On-demand compute         | The selected profile's effective rate before launch                                      |
| Credit purchases          | The wallet's exchange rate and checkout total                                            |

Plan allowances are separate from your wallet balance. CPU hours are not AI tokens, simulator job counts are not currency, and a seat allocation does not create additional purchased credits. Check the selected workspace before comparing balances or usage.

See [On-demand pricing](https://docs.qbraid.com/v2/home/pricing) for resource billing units and [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits) to fund usage beyond your plan allowances.
