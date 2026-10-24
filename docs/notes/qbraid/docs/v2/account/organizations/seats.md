> Full piece: [https://docs.qbraid.com/v2/account/organizations/seats.md](https://docs.qbraid.com/v2/account/organizations/seats.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e3dd5de06f8123f66f8f8c7b3a9ec6ca181b468fc9cfdd20c6c93475c3257a0a.

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

# Seats

> Assign your subscription's seats to specific members and revoke them when people move on.

An assigned seat gives a member your team subscription's benefits. Unassigned seats remain available for other members.

The Seat Management table is on the **Subscription** tab of the [Billing page](https://account.qbraid.com/organizations/billing).

## Assign a seat

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher in the top-left of the dashboard and select your
    organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Stay on the Subscription tab">It's the default tab.</Step>
  <Step title="Scroll to Seat Management">
    The table sits below the subscription card.
  </Step>
  <Step title="Open the assign dialog">
    Find an active member and click **Assign Seat** on their row.
  </Step>
  <Step title="Review the assignment">
    Check the tier, available seats, credits to transfer, and resulting
    organization balance.
  </Step>
  <Step title="Confirm">Click **Assign Seat**.</Step>
</Steps>

<Check>
  The member gets tier benefits right away. If you've turned on
  credits-on-assign in [Settings](https://docs.qbraid.com/v2/account/organizations/settings), they also
  receive a credit transfer at the same time.
</Check>

<Tip>
  Turn on **Auto-assign Seats** in
  [Settings](https://docs.qbraid.com/v2/account/organizations/settings) and new members get a seat
  automatically when they accept an email invitation, if assignment succeeds.
  Invite-code joins do not assign seats. Check Seat Management after acceptance.
</Tip>

## Revoke a seat

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Stay on the Subscription tab">It's the default tab.</Step>
  <Step title="Scroll to Seat Management">
    The table sits below the subscription card.
  </Step>
  <Step title="Click Revoke">On the member's row.</Step>
  <Step title="Confirm">Confirm in the dialog.</Step>
</Steps>

The seat becomes available for another member. The member loses tier benefits but keeps any credits already in their wallet.

## How seats and members interact

| Action                                                       | Effect on seat                                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Member accepts email invitation (with Auto-assign Seats on)  | Attempts to assign an available seat. Check capacity and credits if none is assigned. |
| Member accepts email invitation (with Auto-assign Seats off) | They join without a seat. Assign one manually if needed.                              |
| Admin removes a member                                       | Revoke the member's seat before removal if you need to free capacity.                 |
| Admin suspends a member                                      | An assigned seat can remain assigned. Use **Revoke** to return it to the pool.        |
| Subscription is canceled (period ends)                       | All assigned seats are revoked at the same time.                                      |
| Admin adds seats to the subscription                         | New seats become available to assign.                                                 |

Invite-code recipients join as Members on Free even when **Auto-assign Seats** is enabled. Assign their seats manually. Activating a membership also attempts automatic assignment when enabled.

## Need more seats?

Adding seats is a billing action, not a member action. See [Subscriptions > Add more seats](https://docs.qbraid.com/v2/account/organizations/subscriptions#add-more-seats).

## Find a member and check eligibility

Use **Search members** in Seat Management to find a member by name or email. The table shows membership status and seat status separately. Only active members can receive a seat. An inactive or suspended member can still have an assigned seat, so revoke it explicitly when you need to free capacity.

A member with a personal paid tier and no organization seat displays that tier instead of an assignment action. A paid tier alone does not mean the organization assigned a seat.

The organization owner's seat cannot be revoked from Seat Management. If assignment includes a credit transfer, the organization must have enough credits to fund it.
