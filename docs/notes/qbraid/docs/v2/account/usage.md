> Full piece: [https://docs.qbraid.com/v2/account/usage.md](https://docs.qbraid.com/v2/account/usage.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 7f543d30068cacbfd7ead3bde75062a546b7f7079f1e8c7082272e76ceea9d60.

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

# Usage

> Review compute and AI allowances, inspect session charges, and control automatic credit spending.

## Open your personal usage

1. Open [qBraid Account](https://account.qbraid.com/).
2. Select **qBraid Default** in the workspace switcher to inspect your personal usage.
3. Open **Account > Usage** in the sidebar.
4. Select **Overview** for balances and allowances, or **Session History** to investigate individual compute sessions.

The same page shows your usage within an organization when that workspace is selected. It does not show every member's consumption. Administrators can use [Organization usage](https://docs.qbraid.com/v2/account/organizations/usage) for that view.

## Overview

<Frame caption="Personal Usage in the default workspace. This test account has no recorded compute usage.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nyKmm28CktzIdDcJjHfu4Ss1vTq92YARExbMg" alt="Account Usage in qBraid Default with Overview selected, allowance cards, and Compute Settings" />
</Frame>

Start with the cards near the top of **Overview**:

| Card | What to check |
| --- | --- |
| **Available Credits** | Your qBraid wallet balance in the selected workspace. |
| **Compute Hours** | Subscription compute allowance consumed, total quota, and renewal countdown. |
| **Storage** | Stored data in GB and the displayed storage quota. |
| **Credits Charged** | Recorded compute credit charges for the selected history range. |

The **Understanding Your Usage** card separates subscription compute from on-demand billing. Open the question-mark help controls beside individual metrics for their definitions.

### How compute hours and charges work

<Frame caption="The page explains the two billing types in Understanding Your Usage.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50n1CwFow5jQpcOFeGo6nwMJRrzu9S74dPxmHBk" alt="Understanding Your Usage card explaining subscription compute and on-demand billing" />
</Frame>

Subscription CPU Lab instances use your compute-hours allowance first. Compute hours are **vCPU-hours**, calculated as session duration multiplied by the number of vCPUs. One hour on a 2-vCPU instance consumes two compute hours.

**Compute Time**, session **Duration**, and **Total Compute Time** measure elapsed running time. They do not multiply duration by machine size. The Compute Hours quota also follows its renewal date, while historical totals follow the selected date range. These numbers can therefore differ without indicating a billing error.

On-demand instances use wallet credits instead of subscription compute hours. They charge for compute while running and can charge for retained storage while stopped. Terminating an on-demand instance stops its storage charges but deletes its disk. Download needed files first. See [On-demand instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances).

### Change the history range

<Frame caption="Use the range selector beside Daily Usage to change the historical totals.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nvFqje2NrFtAsIMBLpamlTiN9XkzhQqO38P0w" alt="Subscription and On-Demand session summaries above the Daily Usage chart and range selector" />
</Frame>

1. Scroll to **Daily Usage**.
2. Open its range selector.
3. Choose **7 days**, **14 days**, **30 days**, **90 days**, **1 year**, or **All time**.
4. Compare the chart, session breakdown, **Credits Charged**, and **Summary** for that range.

The default range is 30 days. It changes the historical totals, not the wallet balance or monthly allowance.

The chart shows **Subscription Hours**, **On-Demand Hours**, and **Credits Charged**. Read hours on the left axis and credits on the right. Hover over a point for its daily values.

The **Subscription Sessions** and **On-Demand Sessions** cards show session counts and running time. The on-demand card also separates **Compute Credits** from **Storage Credits**. **Summary** shows total running time, the subscription and on-demand session counts, and total credits charged.

A pending-settlement notice means recorded charges can still update. If on-demand usage is temporarily unavailable, the displayed totals may be incomplete. Refresh after the service recovers before treating them as final.

## Turn on automatic credits for compute

<Frame caption="The compute switch is on in this example. It is separate from the AI switch.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50naPQUn5Rr7oSEJ8tPxqzhVQ6NL4HkIgB3U9WX" alt="Compute Settings with Auto-switch to Credits enabled for subscription CPU usage" />
</Frame>

Enable this setting if you want subscription CPU sessions to use wallet credits after the compute-hours allowance runs out. Check **Available Credits** first. Enabling the setting does not purchase credits.

1. Open **Account > Usage > Overview** in the intended workspace.
2. Find **Compute Settings**.
3. Turn on **Auto-switch to Credits**.
4. Wait for **Auto-switch to credits enabled**.
5. Review your wallet balance and session charges as you continue using compute.

Changes save when you toggle the switch; there is no separate Save button. The switch is unavailable while the update runs. If **Failed to update settings** appears, the update failed and the switch returns to its previous setting. Retry and check the success message.

To turn automatic credit spending off, use the same switch and wait for **Auto-switch to credits disabled**. With fallback disabled, subscription CPU sessions are terminated when compute hours run out, and new subscription launches are blocked until the allowance renews or fallback is enabled. Save your work before exhausting the allowance.

This setting applies to subscription CPU fallback. On-demand instances already use credits, and AI has its own setting below. See [Lab usage limits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits) for allowances.

## Session history

<Frame caption="Session History lists subscription and on-demand sessions with duration, credit charges, status, and pagination.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nMADv5Vqw1Hg4qdUN9TOkaRKJzcr8XuvABI50" alt="Session History showing ten of twenty sessions, subscription and on-demand filters, credit charges, and Completed and Terminated statuses" />
</Frame>

Use this tab to identify a long-running session, compare subscription and on-demand work, or investigate a charge.

1. Open **Session History**.
2. Select **All**, **Subscription**, or **On-Demand** to filter by billing tier.
3. Use **All Status** to select a status, such as **Running**, **Stopped**, **Completed**, or **Error**.
4. Read the matching rows, then use **Previous** and **Next** for additional pages.
5. Select a row to open its billing details. Keyboard users can focus a row and press **Enter** or **Space**.

The table shows 10 sessions per page. Changing a filter returns to page one. These filters are separate from the Overview chart's date range.

| Column | Meaning |
| --- | --- |
| **Start** and **End** | Recorded session times. An unfinished row can show **Running…** instead of an end time. Check its Status too. |
| **Tier** | Subscription or On-Demand billing. |
| **Profile** | The compute profile or instance label, with supporting vCPU or instance information. |
| **Duration** | Elapsed running time, rather than vCPU-hours. |
| **Credits** | Recorded credit charges. A dash means no positive charge is shown. |
| **Status** | The recorded session state. |

An **Unpaid charges** indicator means usage could not be covered by the available credits. **Settlement pending** means billing is still processing. These indicators describe different conditions.

### Inspect a session's billing details


<Frame caption="An on-demand session with expanded billing events. Charged and Total show the session charge; the event rows do not add up to that total.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nXltUFf1Y0NrDQVkz4KvJ8dMFcgwyp93EAeOf" alt="Terminated on-demand session showing 0.17 credits charged, 3 minutes 38 seconds of runtime, and two expanded compute billing events" />
</Frame>

In this example:

- **On-Demand** identifies wallet-credit billing. **Terminated** is the recorded instance status.
- **Charged: 0.17 Cr** is the recorded charge for the session. The **Compute** line and bottom **Total** also show 0.17 credits.
- **Ran for: 3m 38s** is the elapsed runtime. The two event windows, **3m 9s** and **29s**, account for that runtime.
- **Events: 2** counts the recorded billing events. It does not mean two separate final wallet charges.
- **PREPAID · PER-MIN** describes the compute billing model. The expanded rows show recorded event times, types, windows, and credit values.

The event rows show **1.14** and **0.17** credits, but adding them does not give the final session charge. On-demand compute is charged in advance, with unused time refunded. Use **Charged**, the compute/storage line items, and **Total** to read the recorded charge. This screenshot alone does not show the full refund or settlement history needed to reconstruct each event's credit value.


The dialog identifies the session and shows **Charged** and **Ran for**. Subscription sessions also show **Compute**, the vCPU-time drawn from the allowance. On-demand sessions show **Events** and a compute/storage breakdown when available.

Read **Billing events** for the recorded usage windows. On-demand sessions provide **Show all [number] events** and **Hide events** controls. The detailed events are meter readings; they are not necessarily individual wallet charges. Use the **Charged** total and compute/storage line items to reconcile charges, rather than summing meter readings yourself.

If the dialog reports that it is showing only the latest events, the displayed timeline is incomplete even though the charge total covers the session. **No billing events yet.** is different from **Couldn't load billing events.** Use **Retry** for a loading error.

Select **Report Issue** to open a support request with the session identifier and billing details already supplied. Add what you expected and what looks wrong before submitting.

## Outstanding balances

An **Outstanding Balance** alert appears when there are unpaid compute charges. It can include subscription debt and on-demand debt together. The amount owed is different from the available wallet balance and from charges still awaiting settlement.

Add credits through the [Wallet](https://docs.qbraid.com/v2/account/wallet/buy-credits), then wait for settlement before retrying a blocked launch. The alert warns that sessions can be terminated or new sessions blocked while debt remains. If the balance still looks wrong after settlement, inspect the session's billing details and use **Report Issue**.

## AI chat usage

<Frame caption="The AI switch is off in this example; the compute setting does not change it.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50n2qCGRe1pwDJH6pQVRd7zcgMWnKXTGBAIP1j2" alt="AI Chat Usage showing quota, status, renewal, Can Send, and its separate Auto-switch to Credits control" />
</Frame>

Scroll to **AI Chat Usage** in **Overview**. It shows the monthly quota percentage, **Status**, **Renews**, and **Can Send**.

- **Using Quota** means usage is drawing from the included allowance.
- **Using Credits** means usage is drawing from wallet credits.
- **Quota Exhausted** means the included allowance has run out.
- **Can Send** reports whether requests can currently proceed.

### Turn on automatic credits for AI

1. Check that the intended workspace has enough wallet credits.
2. Find **AI Chat Usage**, below the simulator section.
3. Turn on that card's **Auto-switch to Credits** control.
4. Wait for **AI chat auto-switch to credits enabled**.

To stop automatic AI fallback, turn the same control off and wait for **AI chat auto-switch to credits disabled**. If **Failed to update AI chat settings** appears, retry the update. The compute switch does not change this setting.

Review [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas) and [AI models](https://docs.qbraid.com/v2/account/models) for model eligibility, token rates, and allowance limits. An enabled switch alone does not guarantee that every model is available or affordable.

## Simulator usage

<Frame caption="Check the selected simulator and its daily allowance before running jobs.">
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50n8Ty0BDigItG9vq5RLXdYNFeOKZTHSxVDmP7f" alt="Simulator Usage with simulator and range selectors, jobs used today, remaining jobs, and UTC reset time" />
</Frame>

The **Simulator Usage** card tracks your daily job allowance for each simulator.

1. Choose a device with the **Simulator** selector.
2. Check jobs used today, percentage used, and jobs remaining.
3. Use **Range** to choose 7, 14, 30, or 90 days of simulator history.

Daily limits reset at **00:00 UTC**. Plans without a daily cap show **Unlimited** instead of a metered allowance. The simulator date selector is separate from the compute chart's selector. Check the device's displayed limits before submitting more jobs.

For the [GPU simulators](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators), the daily allowance is a number of free circuits: a single job is one circuit, and a batch counts one per circuit. Their rows read, for example, **3 / 25 free circuits today** and **22 free circuits remaining**.

### Turn on usage-based billing for GPU simulators

The GPU simulators, `qbraid:qbraid:sim:gpu-sv` and `qbraid:qbraid:sim:gpu-tn`, each give you a free daily allowance: 25 circuits on Free and 125 on Standard. Once it is used, further jobs on that simulator are refused until the reset, unless you turn on usage-based billing. With it on, they run and are charged from your credits at the simulator's per-minute price. See [Pricing](https://docs.qbraid.com/v2/home/pricing#gpu-simulators) for the rate.

1. Check **Available Credits** in the intended workspace. Enabling the setting does not purchase credits.
2. Open **Account > Usage > Overview** and scroll to **Simulator Usage**.
3. At the bottom of the card, below **Jobs run over time**, turn on **Usage-based billing for GPU simulators**.
4. Wait for **Usage-based billing for GPU simulators enabled**.

The switch's description reads: "After your free daily circuits, further jobs on the GPU simulators run and are charged from your credits for each minute of execution, at the simulator's per-minute price. When off, jobs that need more circuits than you have left are refused."

Changes save when you toggle the switch; there is no separate Save button. The switch is unavailable while the update runs. If **Failed to update simulator billing settings** appears, the update failed and the switch returns to its previous setting. Retry and check the success message. To stop charging further jobs, turn the same switch off and wait for **Usage-based billing for GPU simulators disabled**.

The switch appears only when a GPU simulator has a limited daily allowance on your plan, so Pro and Enterprise members, whose allowance is unlimited, do not see it. It also appears on each GPU simulator's device page. The setting is yours in the selected workspace and is separate from the compute and AI switches.

If [Circuit Composer](https://docs.qbraid.com/v2/account/composer) refuses a GPU simulator job because the day's allowance is used, its error offers **Turn on usage-based billing**, which turns the setting on without leaving the composer, and a **Review on the Usage page** link. The job is not resubmitted for you: after **Usage-based billing for GPU simulators enabled. Run the job again to submit it.** appears, run the job again.

To read or change the setting through the REST API, use [Get Simulator Usage](https://docs.qbraid.com/v2/api-reference/rest/get-simulator-usage), whose GPU simulator entries carry `creditFallover: true` and your `autoSwitchToCredits` setting, and [Update Simulator Usage Settings](https://docs.qbraid.com/v2/api-reference/rest/update-simulator-usage-settings).

## Refresh or recover missing data

Use **Refresh** at the top of Usage to reload the overview, AI allowance, and simulator data. If **Error loading usage data** or **Couldn't load your sessions** appears, select the associated **Retry** button.

For **No sessions found**, select **All** and **All Status** before concluding that the workspace has no history. Check that you selected the workspace where you ran the sessions. A failed query is not an empty history.

## Download your files

You can download Lab files without starting a session from **Dashboard > Usage Overview > Download Files**. Follow [Download Lab files](https://docs.qbraid.com/v2/account/dashboard#download-lab-files). The exhausted-compute help control can also offer a file download when a new session is blocked.
