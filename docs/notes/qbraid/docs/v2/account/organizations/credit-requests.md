> Full piece: [https://docs.qbraid.com/v2/account/organizations/credit-requests.md](https://docs.qbraid.com/v2/account/organizations/credit-requests.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 2cdf3131277f1e350f54cbde6b73d3f1a2de11bd8b4a84489706ab6eb58aa79e.

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

# Credit requests

> Request organization credits, cancel a pending request, and approve or reject requests as an administrator.

Use **Wallet** in an organization workspace to request credits from the organization pool. Organization Owners and Admins review requests in **Billing > Credit Requests**. Managers and Members cannot approve or reject requests.

Approved credits go to your member wallet within the selected organization. Use that organization workspace when you spend them. They do not add to your personal qBraid Default balance.

<Note>
  Credit requests are available in organization workspaces. In **qBraid Default**,
  use [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits) to fund your personal wallet.
</Note>

## Submit a request

Use these steps as a member.

<Steps>
  <Step title="Select your organization">
    Open the workspace switcher in the top-left of the dashboard. Select the
    organization that will fund your work.
  </Step>
  <Step title="Open Wallet">
    Select **Account > Wallet** in the sidebar. Under **Need more credits?**, select **Request credits**.
  </Step>
  <Step title="Enter the amount and reason">
    The **Request Credits from Organization** dialog opens. Enter a whole number of credits
    from 1 to 10,000 in **Amount**.

    **Reason** is optional. Leave it blank, or enter 10 to 500 characters
    that explain what you need the credits for. For example, name the project and
    the work you plan to run.

    <Frame>
      <img
        src="/v2/account/_static/wallet-request-credits.webp"
        alt="Request Credits from Organization dialog with 100 entered as the amount and a short reason, and the Submit Request button enabled"
      />
    </Frame>
  </Step>
  <Step title="Submit the request">
    Select **Submit Request**. Select **Cancel** instead if you do not want to
    send it. The dialog tells you that the request goes to organization owners and admins for approval.
  </Step>
  <Step title="Check the pending state">
    The **Need more credits?** panel changes to **Request for _N_ credits is pending**. It shows the send date and your reason. **Request credits** turns off until an admin processes the request.

    <Frame>
      <img
        src="/v2/account/_static/wallet-request-pending.webp"
        alt="Your credits card showing Request for 100 credits is pending with View request and a turned-off Request credits button"
      />
    </Frame>
  </Step>
</Steps>

You can have one pending request at a time in each organization. Submitting a request does not transfer credits.

## Track the request

1. Select the same organization in the workspace switcher.
2. Open **Account > Wallet**.
3. Select **View request**.
4. Review **Amount**, **Reason**, **Status**, and **Requested** in the **Pending Credit Request** dialog.
5. Select **Close** to leave the request pending.

<Frame caption="The request stays pending until an administrator processes it or you cancel it.">
  <img
    src="/v2/account/_static/wallet-view-request.webp"
    alt="Pending Credit Request dialog showing 100 credits, the reason, Pending status, the request time, and Close and Cancel Request buttons"
  />
</Frame>

This dialog shows your pending request. It does not show completed requests or an administrator's rejection reason. After an administrator approves or rejects it, check your Wallet balance in the organization, or ask an administrator about the decision.

## Cancel or change a pending request

You can cancel your own pending request. To change its amount or reason, cancel it and submit a new request.

1. Open **Wallet > View request** in the same organization.
2. Select **Cancel Request**.
3. Review the amount in **Cancel Credit Request?**.
4. Select **Cancel Request** again to confirm, or **Keep Request** to leave it pending.
5. After cancellation, use **Request credits** to submit a replacement if needed.

You cannot cancel a request after an administrator approves or rejects it. If an administrator acts on the request while the dialog is open, refresh the account data before you do anything else.

## Review requests as an administrator

1. Select the organization in the workspace switcher.
2. Open [Billing](https://account.qbraid.com/organizations/billing).
3. Select **Credit Requests**.
4. Find the member in **Pending Requests**.
5. Read the amount and reason. Then select **Approve** or **Reject**.

<Frame caption="The pending count appears on Credit Requests. Review the member, amount, and reason before you act.">
  <img
    src="/v2/account/_static/wallet-admin-requests.webp"
    alt="Billing page in an organization with the Credit Requests tab open, listing pending requests with member, amount, reason, date, and Approve and Reject buttons"
  />
</Frame>

Each pending row shows the member's name and email, requested amount, reason, request date, and **Approve** and **Reject** actions. The table can shorten long reasons. Open **Approve** to read the full reason before you decide, then select **Cancel** if you do not want to approve it.

### Approve a credit request

<Steps>
  <Step title="Open the approval dialog">
    Select **Approve** on the member's request.
  </Step>
  <Step title="Review the recipient and balance">
    In **Approve Credit Request**, verify the member, reason, **Amount to transfer**,
    **Current org balance**, and **New org balance**.

    Approval transfers the full requested amount. This dialog does not let you
    change the amount or add an approval note.
  </Step>
  <Step title="Confirm approval">
    Select **Approve Request** and wait for the success message.
    Select **Cancel** instead to leave the request pending.
  </Step>
  <Step title="Check the result">
    The request moves to **Request History** with status **accepted**.
    Check the organization balance and [Transactions](https://docs.qbraid.com/v2/account/organizations/transactions).
    The member sees the new balance in **Wallet** when they select
    the same organization.
  </Step>
</Steps>

If the pool cannot cover the request, the dialog shows **Insufficient organization balance. Buy more credits first.** and disables approval. [Buy credits for the organization](https://docs.qbraid.com/v2/account/organizations/credits#buy-credits-for-the-org), then reopen the request after the balance updates.

If a different amount is appropriate, ask the member to cancel and submit a revised request. You can also reject the request with an explanation and make a [direct transfer](https://docs.qbraid.com/v2/account/organizations/credits#transfer-credits-to-members). Resolve the original request first so it does not remain available for another approval.

### Reject a credit request

1. In **Pending Requests**, select **Reject** on the member's row.
2. In **Reject Credit Request**, enter a **Rejection Reason** of 10 to 500 characters.
3. Explain the decision and any next step, such as requesting a different amount.
4. Select **Reject Request** and wait for confirmation. To leave the request pending, select **Cancel** instead.

The request moves to **Request History** with status **rejected**. Rejection does not transfer credits. The member can submit another request after the rejection. Share the decision with the member if they need the explanation, because Wallet does not display completed request details.

## Check request history

The **Request History** table shows the member, amount, status, and original request date. **accepted** means an administrator approved the request. **rejected** means an administrator declined it. The date is the request date, not the decision date.

The tab shows up to 20 of the newest requests across pending requests and history, with only the latest request retained for each member. A replacement request can therefore remove an earlier decision from this view. Canceled requests do not appear in history.

Use [Transactions](https://docs.qbraid.com/v2/account/organizations/transactions) to check credit movements and [Audit logs](https://docs.qbraid.com/v2/account/organizations/audit-logs) to investigate recorded administrator actions. Request History is not a complete record of all past requests or proof that a queued transfer has finished.

## Resolve a request problem

- If you already have a pending request, open **View request**. Cancel it before submitting a replacement.
- If the request fails to send, check the amount and the reason. The amount must be a whole number from 1 to 10,000. A reason, if you add one, must be 10 to 500 characters.
- If a request is no longer pending, another action may have processed or canceled it. [Refresh account data](https://docs.qbraid.com/v2/account/refresh), then check the request list.
- If approval fails or the balance has not updated, check the current request status and Transactions before retrying or making a separate transfer.
- If **Credit Requests** is unavailable, verify the selected organization and your Owner or Admin role.

For an urgent request, contact an organization administrator. Administrators can [transfer credits directly](https://docs.qbraid.com/v2/account/organizations/credits#transfer-credits-to-members) without requiring a request.
