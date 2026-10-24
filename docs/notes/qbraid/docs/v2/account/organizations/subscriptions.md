> Full piece: [https://docs.qbraid.com/v2/account/organizations/subscriptions.md](https://docs.qbraid.com/v2/account/organizations/subscriptions.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 55c13f8f6855f54aac55ce0476da894e5973a8a964f2871ffc76b18d7efaebc4.

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

# Team subscriptions

> Buy a team plan, change tier or interval, add capacity, and handle cancellations.

A team subscription gives your organization a Standard or Pro tier and seats you assign to members. Members with a seat get the tier's benefits. Members without one stay on Free-level access.

<Note>
  Team subscriptions are different from personal ones. They're priced per seat,
  managed inside qBraid (not Stripe), and let you give benefits to specific
  members. See [Personal vs Team
  comparison](https://docs.qbraid.com/v2/account/wallet/subscriptions#personal-vs-team).
</Note>

## Plans

| Plan     | Monthly per seat | Annual, per seat per month | Compute per seat      | Storage per seat |
| -------- | ---------------- | -------------------------- | --------------------- | ---------------- |
| Standard | \$20             | \$16                       | 400 CPU hrs / month   | 50 GB            |
| Pro      | \$100            | \$80                       | 2,000 CPU hrs / month | 150 GB           |

The annual column shows monthly equivalents. The yearly charge is $192 per Standard seat or $960 per Pro seat. Team subscriptions require at least two seats. Review the full checkout total before subscribing.

Standard includes full Qubes and Quantum Software Engineering course access and priority support. Pro includes higher AI usage limits and dedicated support. Each assigned Standard seat has a limit of 500 jobs per managed simulator per day, or 125 free circuits per day on each [GPU simulator](https://docs.qbraid.com/v2/home/pricing#gpu-simulators). Pro has no daily job-count limit for those simulators. Device usage charges can still apply.

For Enterprise, use **Contact Sales** to submit an organization request for custom terms.

## Create a team subscription

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher in the top-left of the dashboard and select your
    organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Click Create Subscription">
    In the top-right of the Billing page, click **Create Subscription**.
  </Step>
  <Step title="Pick a tier">Choose **Standard** or **Pro**.</Step>
  <Step title="Choose billing interval">
    Monthly or Annual. Annual billing saves 20% compared with twelve monthly
    payments.
  </Step>
  <Step title="Enter number of seats">Minimum is 2 seats.</Step>
  <Step title="Subscribe">
    Click **Proceed to Payment** and finish checkout on Stripe.
  </Step>
</Steps>

<Check>
  After checkout, wait for the Billing page to confirm the subscription.
</Check>

## Upgrade

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Stay on the Subscription tab">It's the default tab.</Step>
  <Step title="Open the manage dialog">
    Click **Manage Team Subscription** on the subscription card.
  </Step>
  <Step title="Pick the Plan Tier tab">
    It's the default tab in the dialog.
  </Step>
  <Step title="Upgrade">
    Click **Upgrade to Pro Now** (or Standard, if you're starting from Free).
  </Step>
  <Step title="Confirm">
    The confirmation dialog shows the prorated cost. Click **Confirm**.
  </Step>
</Steps>

<Check>
  The new tier takes effect immediately. Stripe prorates the difference for the
  current period.
</Check>

## Downgrade

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Open Manage Team Subscription">
    On the Subscription tab, click **Manage Team Subscription**.
  </Step>
  <Step title="Stay on the Plan Tier tab">It's the default tab.</Step>
  <Step title="Scroll to Downgrade to Standard">
    Review the benefits and effective date in the dialog.
  </Step>
  <Step title="Schedule the downgrade">
    Click **Schedule Downgrade** and confirm. You keep Pro features until the
    end of the current billing period.
  </Step>
</Steps>

<Note>
  You can't change tier while a cancellation is scheduled. Reactivate the
  subscription first.
</Note>

## Switch between monthly and annual

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Open Manage Team Subscription">
    On the Subscription tab, click **Manage Team Subscription**.
  </Step>
  <Step title="Open the Billing Interval tab">
    Click the **Billing Interval** tab inside the dialog.
  </Step>
  <Step title="Pick the new interval">Switch between Monthly and Annual.</Step>
</Steps>

Both interval changes update the subscription through Stripe with proration. Review the confirmation dialog and the resulting billing dates. An annual-to-monthly change is not a scheduled tier downgrade.

## Add more seats

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">Click **Billing** in the sidebar.</Step>
  <Step title="Stay on the Subscription tab">It's the default tab.</Step>
  <Step title="Click Add Seats">On the subscription card.</Step>
  <Step title="Enter the new total">
    Enter the desired total in **New Seat Count**. It must exceed the current
    total. For example, enter 6 to add 4 seats to a subscription with 2 seats.
  </Step>
  <Step title="Confirm">
    Stripe charges a prorated amount for the rest of the period.
  </Step>
</Steps>

<Check>
  The new seats are available to assign immediately. See
  [Seats](https://docs.qbraid.com/v2/account/organizations/seats) for how to assign them.
</Check>

## Cancel

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Billing">
    Click **Billing** in the sidebar.
  </Step>
  <Step title="Open Manage Team Subscription">
    On the Subscription tab, click **Manage Team Subscription**.
  </Step>
  <Step title="Expand Cancel Subscription">
    Scroll to the bottom of the dialog and click into the **Cancel Subscription** section.
  </Step>
  <Step title="Read what you'll lose">
    All assigned seats are revoked at the end of the current period. Members keep any credits already in their wallets.
  </Step>
  <Step title="Tick the confirmation box">
    *"I understand this will revoke all `<n>` assigned seats at end of period and cannot be undone."*
  </Step>
  <Step title="Cancel">
    Click **Cancel Team Subscription**.
  </Step>
</Steps>

The subscription enters the **canceling** state, and a banner shows the end date. Resubscribe before that date to cancel the scheduled cancellation.

<Danger>
  Once the period ends, every assigned seat is revoked and members return to
  Free-tier access. Members keep their wallet credits.
</Danger>

## Invoices and scheduled changes

Open **Billing > Invoices** for organization invoice dates, billing periods, totals, statuses, receipt links, and PDFs.

A scheduled tier downgrade prevents a billing-interval change until you cancel the scheduled downgrade. A scheduled cancellation also prevents plan changes until you reactivate. Review the effective date and proration shown in the confirmation dialog before you apply a change.

Use [Audit logs](https://docs.qbraid.com/v2/account/organizations/audit-logs) to review recorded subscription and seat changes, including who performed them and their results.
