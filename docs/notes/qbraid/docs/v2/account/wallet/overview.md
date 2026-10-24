> Full piece: [https://docs.qbraid.com/v2/account/wallet/overview.md](https://docs.qbraid.com/v2/account/wallet/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e06c57363bdfe0d942e9f995186c867309453cbebe4f5304fdda055bb7531529.

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

# Overview

> What you see when you open your wallet: subscription, prepaid credits, transactions, and invoices.

Use your wallet to manage credits, your subscription, and payment history.

Open it from the sidebar under **Account > Wallet**, or visit [account.qbraid.com/account/wallet](https://account.qbraid.com/account/wallet).

<Note>
  The wallet changes with the selected workspace. In **qBraid Default** you see
  your personal subscription, **Buy credits**, and an **Invoices & receipts**
  tab. In an **organization** workspace you see a **Your seat** card, a
  **Request credits** button, and transactions only. See [workspace
  selection](https://docs.qbraid.com/v2/account/overview#choose-a-workspace) for details.
</Note>

<Frame>
  <img
    src="/v2/account/_static/wallet-paid-plan.webp"
    alt="Wallet in qBraid Default showing an active Standard Monthly subscription card, a Compare plans row, and the Prepaid credits card"
  />
</Frame>

## What each part does

- **Payment link.** The **Manage payment & invoices** button. Opens the Stripe customer portal for payment methods and invoices. Personal workspace only.
- **Subscription.** Shows your personal plan. In an organization this section becomes **Your seat**.
- **Prepaid credits.** Shows the balance, recent use, and the **Buy credits** controls. Called **Your credits** in an organization.
- **Transactions.** Lists credit activity for the selected workspace. Adds the **Invoices & receipts** tab in qBraid Default.

## Subscription

In **qBraid Default**, the subscription card shows your tier, billing interval, and status. A paid plan shows the renewal date and charge. If a discount applies, the card strikes through the list price and shows the percent off next to the next charge. **Change plan** and **Cancel subscription** open in-app dialogs. A scheduled change or pending cancellation appears as a row inside the card.

On the **Free** plan, **Upgrade your plan** follows the card with the Standard and Pro cards. Standard has a **Most popular** badge. Use the **Monthly** and **Annual** toggle to switch prices. On a paid plan the cards collapse into a **Compare plans** row. Links to `/account/wallet#available-plans` open it automatically.

See [Personal subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions) for buy, change, and cancel steps.

## Team member view

In an **organization** workspace, the wallet shows your seat instead of a personal subscription. Owners and admins assign seats in **Organizations > Billing**.

### With a seat

A member with a seat sees the seat tier, an **Active** badge, and the seat text. The **Your credits** card sits below it.

<Frame>
  <img
    src="/v2/account/_static/wallet-team-seat.webp"
    alt="Wallet in an organization workspace for a member with a Standard seat, showing Your seat as Standard with an Active badge, a Plan managed by your organization badge, and the Your credits card with a 1,000 credit balance"
  />
</Frame>

On a phone, the cards stack in one column.

<Frame>
  <img
    src="/v2/account/_static/wallet-team-seat-mobile.webp"
    alt="Wallet on a phone for a member with a Standard seat, showing the seat card above the Your credits card"
  />
</Frame>

- **Your seat.** Names the tier of the seat you hold, such as **Standard**.
- **Active badge.** Shows the seat status.
- **Seat text.** Reads **Your seat includes _tier_ features**. Says what the seat gives you. Credits for compute and QPU jobs come from your balance below.
- **Managed badge.** Reads **Plan managed by your organization**. Replaces the personal plan actions. You cannot buy, change, or cancel a plan here.
- **Your credits.** Shows your balance in this organization. Admins add credits from the organization pool when they approve your request.
- **Pending request.** Reads **Request for _N_ credits is pending**. Appears after you send a request. It shows the send date and your reason. **View request** opens it.

Assigning a seat moves credits from the organization wallet to your balance. The admin sees the amount before they confirm.

<Frame>
  <img
    src="/v2/account/_static/wallet-assign-seat.webp"
    alt="Assign Seat dialog showing a Standard seat, 3 of 3 available seats, 1,000 credits to transfer, the current organization balance, and the new organization balance"
  />
</Frame>

### Without a seat

A member without a seat sees **Free** and **No seat assigned in** _organization_. The **Need more credits?** panel holds **Request credits**.

<Frame>
  <img
    src="/v2/account/_static/wallet-team-no-seat.webp"
    alt="Wallet in an organization workspace for a member without a seat, showing Your seat as Free with No seat assigned, the Your credits card, and a Request credits button"
  />
</Frame>

Select **Request credits** to ask the organization admins for credits. A pending request replaces the **Need more credits?** panel. See [Credit requests](https://docs.qbraid.com/v2/account/organizations/credit-requests).

## Prepaid credits

The credits card shows your **Available balance** first, with its dollar value at the current rate. A seven-day usage chart appears next to the balance. With no recent use, the card shows **No recent activity** instead.

- **Burn rate.** Credits used in the last 30 days, shown per day.
- **Runway.** How long the balance lasts at that rate: **≈ N days left**, **No usage yet**, or **> 1 year**. Red under 14 days.
- **Added · 30 days.** Credits added in the last 30 days.
- **All time.** Expands to the lifetime totals added, deducted, and the net change.

<Frame>
  <img
    src="/v2/account/_static/wallet-prepaid-credits.webp"
    alt="Prepaid credits card with the balance, burn rate, runway, added credits, and the Buy credits presets"
  />
</Frame>

The wallet computes these figures from the most recent transactions it loads, so they can leave out older activity. The transactions list below shows the underlying rows.

In qBraid Default, **Buy credits** offers preset and custom amounts. See [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits). In an organization, **Request credits** asks org admins for credits. A pending request shows **Request for N credits is pending** with a **View request** button. See [Credit requests](https://docs.qbraid.com/v2/account/organizations/credit-requests).

## Transactions

The **Transactions** section lists credit activity for the selected workspace. In qBraid Default it opens on **Credit transactions** next to the **Invoices & receipts** tab. On narrow screens the tabs shorten to **Transactions** and **Invoices**, and rows display as cards.

<Frame>
  <img
    src="/v2/account/_static/wallet-mobile-transactions.webp"
    alt="Wallet on a phone showing transactions as stacked cards under the search and filter controls"
  />
</Frame>

Select a row to open its receipt or details. See [Payment history](https://docs.qbraid.com/v2/account/wallet/payment-history).

## Outstanding balance

An **Outstanding Balance** banner shows unpaid compute charges separately from the wallet balance. A later credit purchase or transfer settles this debt automatically. Check the debt and the available balance before retrying a blocked launch.

## Where to next

- Add funds: [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits).
- Pick a plan: [Personal subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions).
- Ask your organization for credits: [Credit requests](https://docs.qbraid.com/v2/account/organizations/credit-requests).
- Audit your charges: [Payment history](https://docs.qbraid.com/v2/account/wallet/payment-history).
- Find invoices: [Payment history](https://docs.qbraid.com/v2/account/wallet/payment-history#invoices).
