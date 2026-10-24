> Full piece: [https://docs.qbraid.com/v2/account/wallet/buy-credits.md](https://docs.qbraid.com/v2/account/wallet/buy-credits.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0fb1642e071448b77211465784662d8897cc3c469806dec3a8797c00562c7fce.

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

# Buy credits

> Top up your credit balance with a preset or custom amount, and apply a promo code at checkout.

You can buy credits without a subscription. The standard rate is $1 = 100 credits for supported qBraid-billed resources. Provider-funded jobs, such as Open Quantum, use the linked provider account's credits.

<Warning>
  Buying credits is only available in your **qBraid Default** workspace (the
  default). In an organization workspace, the Buy credits controls are hidden
  and you see a [Request
  credits](https://docs.qbraid.com/v2/account/organizations/credit-requests) button instead.
  Organization administrators buy credits for the team from [Organizations >
  Credits](https://docs.qbraid.com/v2/account/organizations/credits#buy-credits-for-the-org).
</Warning>

## What each part does

- **Preset amounts.** Five cards: $5, $10, $20, $50, and $100, each with its credit count.
- **Custom.** A dollar amount you type. The credit count updates as you type.
- **Add promo code.** Opens the promo code field. Stripe applies the code at checkout.
- **Buy button.** Reads **Buy N credits · $X**. The purchase button. It shows the credit count and price for your selection and opens Stripe Checkout.

<Frame>
  <img
    src="/v2/account/_static/wallet-buy-credits.webp"
    alt="Prepaid credits card showing Buy credits with the $10 preset selected, the promo code field open, and the Buy 1,000 credits button"
  />
</Frame>

## How to buy

<Steps>
  <Step title="Switch to qBraid Default">
    Open the workspace switcher in the top-left of the dashboard and select
    **qBraid Default**.
  </Step>
  <Step title="Open Wallet">
    Click **Account > Wallet** in the sidebar, or open
    [account.qbraid.com/account/wallet](https://account.qbraid.com/account/wallet)
    directly.
  </Step>
  <Step title="Find Buy credits">
    The section sits inside **Prepaid credits**, below the balance and usage
    stats.
  </Step>
  <Step title="Pick an amount">
    Click a preset card, or type a dollar amount in **Custom**. The button label
    updates with the credit count and total.
  </Step>
  <Step title="Add a promo code (optional)">
    Select **Add promo code** and type the code.
  </Step>
  <Step title="Select Buy">
    Click **Buy N credits · $X**. The wallet opens Stripe Checkout.
  </Step>
</Steps>

<Check>
  After payment, return to the wallet and wait for checkout confirmation.
  Refresh the wallet if the balance has not updated.
</Check>

<Tip>
  The current exchange rate appears under **Available balance**. The standard
  rate is $1 = 100 credits. The custom amount field enforces the allowed
  purchase range.
</Tip>

## Add a promo code on the wallet

<Steps>
  <Step title="Switch to qBraid Default">
    Open the workspace switcher and select **qBraid Default**.
  </Step>
  <Step title="Open Wallet">Click **Account > Wallet** in the sidebar.</Step>
  <Step title="Pick an amount">
    In **Buy credits**, select a preset or enter a custom amount.
  </Step>
  <Step title="Type the code">
    Select **Add promo code** and enter the code in the field.
  </Step>
  <Step title="Select Buy">
    Click **Buy N credits · $X**. Stripe applies the discount at checkout. An
    invalid code shows an error in the field instead of opening checkout.
  </Step>
</Steps>

## Apply a promo code on Stripe Checkout

<Steps>
  <Step title="Start a purchase">
    Follow the steps above without entering a promo code on the wallet.
  </Step>
  <Step title="On Stripe Checkout, click Add promotion code">
    A small text field appears.
  </Step>
  <Step title="Paste the code and click Apply">
    The discount appears on the order summary.
  </Step>
  <Step title="Complete the order">Click **Complete Order**.</Step>
</Steps>

Review the final amount in Stripe before completing checkout.

## If you can't see the Buy button

In an organization workspace, your wallet shows **Request credits** instead of the purchase controls. Organization administrators buy for the team from **Billing**. See [Credit Requests](https://docs.qbraid.com/v2/account/organizations/credit-requests).

## Outstanding balance

An **Outstanding Balance** banner shows unpaid compute charges separately from the wallet balance. Credit purchases and transfers can settle that debt. After checkout, check both the debt and the available wallet balance.
