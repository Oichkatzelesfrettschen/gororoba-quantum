> Full piece: [https://docs.qbraid.com/v2/home/pricing.md](https://docs.qbraid.com/v2/home/pricing.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c348e72c21fc2972796412cd13ee4fe2c13c06b7c1664c5014b55b92ad712e0c.

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

# On-demand pricing

> Understand credits, resource billing units, AI token rates, and subscription allowances.

## Credits

The standard exchange rate is **100 qBraid credits = $1 USD**. A job priced at $3.80 uses 380 credits. [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits) from your wallet, then check the selected workspace's balance before you run paid resources.

Credit purchases, personal plans, and team plans are separate purchases. A plan provides resource allowances. Credits pay for eligible usage outside those allowances or for resources billed on demand. Review the rate and total shown in the application before checkout or launch.

## Subscription plans

| Plan     | Monthly | Annual | CPU hours per month | Storage | AI allowance per quota period |
| -------- | ------: | -----: | ------------------: | ------: | ----------------------------: |
| Free     |      $0 |     $0 |                 100 |   15 GB |                            $5 |
| Standard |     $20 |   $192 |                 400 |   50 GB |                           $15 |
| Pro      |    $100 |   $960 |               2,000 |  150 GB |                           $50 |

Annual subscriptions are billed yearly, equivalent to $16 per month for Standard and $80 per month for Pro. Team plans use the same per-seat prices with a minimum of two seats. Enterprise plans use custom terms.

See [Personal subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions) or [Team subscriptions](https://docs.qbraid.com/v2/account/organizations/subscriptions) for benefits and management instructions. Use **Account > Usage** to check your effective allowance and renewal date.

## Quantum computers

Open [Devices](https://account.qbraid.com/devices) and inspect the selected QPU's pricing. Device availability and rates can change. A QPU can use a per-task fee, per-shot fee, execution-time fee, or a combination.

A shot is one execution of a quantum program. A task submits a program with a chosen shot count. For a device with task and shot pricing, estimate credits as:

```text
per-task credits + number of shots × per-shot credits
```

For time-based devices, the execution-time charge depends on the device's billing rules. Review the job's estimate and final charge. Do not apply one provider's minimum duration or rounding rules to another provider.

If you connect your own provider account, review that provider's billing terms as well. See [Open Quantum](https://docs.qbraid.com/v2/account/integrations/openquantum) for its account and credit setup.

## Quantum circuit simulators

Use the [device catalog](https://account.qbraid.com/devices) for current simulator availability and rates. Some simulators have no qBraid usage charge, while others charge for execution. A simulator's price and daily job quota are separate constraints.

For qBraid-managed daily simulator quotas, Free allows 100 jobs per simulator per UTC day and Standard allows 500. Pro has no daily job-count limit for these managed simulators. This does not make a paid simulator free or remove provider-specific limits. The GPU simulators are the exception, described below.

### GPU simulators

The [GPU simulators](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators), `qbraid:qbraid:sim:gpu-sv` and `qbraid:qbraid:sim:gpu-tn`, each have a smaller daily allowance of circuits, and jobs inside it are free. A single job is one circuit, and a batch counts one per circuit:

| Plan       | Free circuits per GPU simulator per UTC day |
| ---------- | ------------------------------------------: |
| Free       |                                          25 |
| Standard   |                                         125 |
| Pro        |                                   Unlimited |
| Enterprise |                                   Unlimited |

Once you have used the day's allowance, further jobs on that simulator are refused until 00:00 UTC unless you turn on **Usage-based billing for GPU simulators** in [Account > Usage](https://docs.qbraid.com/v2/account/usage#simulator-usage). With it on, each further job is charged from your credits at the simulator's per-minute price, 5 credits ($0.05) per minute of execution, with a minimum of 3 seconds (0.25 credits) per single-circuit job. A 14.3-second job costs about 1.19 credits. A job that fails is not charged, and a batch where some circuits fail is charged for its full execution time. The setting is off unless you turn it on.

## CPUs and GPUs

qBraid offers subscription compute that consumes CPU hours and on-demand compute that consumes credits. See [Usage limits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits) for CPU-hour accounting and credit overflow settings.

### Subscription instances

CPU hours count allocated vCPUs multiplied by elapsed hours. A two-vCPU instance running for three hours consumes six CPU hours. When an instance uses your remaining plan allowance, that usage does not deduct on-demand credits.

If you enable **Auto-switch to Credits**, eligible usage beyond the compute allowance can spend wallet credits. Check the instance's credit rate before you enable this setting. AI's auto-switch policy is a separate setting.

### On-demand instances

Inspect the current compute profile for its CPU or GPU configuration and effective rate before you launch. Profile catalogs and prices can change, so the launch screen is the reference for available configurations.

The personal plan cards advertise on-demand compute discounts of 10% for Standard and 18% for Pro. The billed compute rate uses the configured tier discount, so compare the effective rate shown for your selected workspace. Storage charges are separate and do not use the compute discount.

See [On-demand instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances) for lifecycle and billing details, or [GPUs](https://docs.qbraid.com/v2/lab/user-guide/gpus) for GPU access.

#### GPU instances

Select a GPU profile by GPU model, count, memory, and availability in the compute catalog. Check the displayed rate and any separate storage cost.

#### CPU instances

Select a CPU profile by vCPU count and memory. For CLI workflows, use the current profile's identifier with [qBraid compute](https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute).

## AI models

The model picker displays separate input and output rates in **credits per million tokens**. [Models and pricing](https://docs.qbraid.com/v2/account/models) includes the current documented model-rate reference and instructions for querying the live catalog.

AI usage draws from your plan's allowance first. Usage beyond the allowance can spend credits when your effective auto-switch policy permits it. See [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas).

## Review charges

Use [Wallet payment history](https://docs.qbraid.com/v2/account/wallet/payment-history) for your workspace's credit activity and personal Stripe invoices. Organization administrators use [Billing transactions](https://docs.qbraid.com/v2/account/organizations/transactions) and the separate **Invoices** tab for organization purchases.
