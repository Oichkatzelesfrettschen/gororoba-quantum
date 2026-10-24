> Full piece: [https://docs.qbraid.com/v2/account/organizations/credits.md](https://docs.qbraid.com/v2/account/organizations/credits.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0bd2a724e64b759d45111baee6ab24db7ba2a77221801a14df3f52194c65f572.

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

# Credits

> Buy credits for the organization, transfer them to members, and approve credit requests.

Administrators buy credits for the organization wallet, then transfer them to members to fund their work.

Open the [Billing page](https://account.qbraid.com/organizations/billing) to see the organization balance, buy credits, or transfer them to members.

## Buy credits for the org

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher in the top-left of the dashboard and select your
    organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Click Buy Credits">In the top-right of the Billing page.</Step>
  <Step title="Enter an amount">
    Type the dollar amount you want to spend. The credit count updates as you
    type.
  </Step>
  <Step title="Purchase">
    Click **Purchase** and finish checkout on Stripe.
  </Step>
</Steps>

<Check>The purchase adds credits to the organization wallet.</Check>

## Transfer credits to members

1. Switch to the organization and open **Billing**.
2. Select **Transfer** on the Balance card.
3. Use **Selected** to choose one or more active members, or **All Members** for every active member.
4. Enter the **Amount per member** and an optional reason.
5. Review the recipient count and total, then confirm the transfer.

Search the recipient list to find members. Review the selection before you use the option to add all matching members.

The organization wallet must cover the total amount. For example, 100 credits each for three members requires 300 credits. Credits go to each member's wallet within this organization. They do not become a personal qBraid Default balance.

## Approve a credit request

Owners and Admins review member requests in **Billing > Credit Requests**. Approval queues the full requested amount for transfer to the member's organization wallet. The organization pool must cover that amount.

Follow [Approve a credit request](https://docs.qbraid.com/v2/account/organizations/credit-requests#approve-a-credit-request) to review the recipient, reason, balances, and completed transfer.

## Reject a credit request

Rejection requires a reason of 10 to 500 characters and does not transfer credits. Follow [Reject a credit request](https://docs.qbraid.com/v2/account/organizations/credit-requests#reject-a-credit-request) to record the decision.

Members can [submit, track, or cancel a request](https://docs.qbraid.com/v2/account/organizations/credit-requests) from their organization Wallet.

<Tip>
  Set **Seat Assignment Credits** in [Settings > Member
  Settings](https://docs.qbraid.com/v2/account/organizations/settings#member-settings) to transfer
  credits when a seat is assigned. Joining with an invite code does not assign
  a seat or trigger this allocation.
</Tip>

## Credit sources and allocations

Direct purchases add credits to the organization wallet. A transfer or configured seat-assignment allocation moves credits out of that pool and into a member's organization wallet. Seat assignment does not create new credits.

When a member leaves voluntarily, their remaining organization-wallet credits are queued for return to the organization. Review [Transactions](https://docs.qbraid.com/v2/account/organizations/transactions) to audit purchases, allocations, and returns.
