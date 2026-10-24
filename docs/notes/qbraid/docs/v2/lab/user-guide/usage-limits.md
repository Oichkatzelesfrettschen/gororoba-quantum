> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/usage-limits.md](https://docs.qbraid.com/v2/lab/user-guide/usage-limits.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 f9843f2da3812b416bf8eec1abc537999835ca8712f1ae1a504f050fa7a486b0.

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

# Usage limits

> Check compute hours, storage quotas, and AI allowances in qBraid Lab.

Your subscription plan sets your compute, storage, and AI allowances. Check your remaining usage and renewal dates in the selected workspace's account dashboard.

## Compute hours

Your plan includes compute hours for subscription CPU instances. On-demand instances use credits instead of this allowance.

<Tip>
  Compute hours equal the allocated vCPUs multiplied by the hours used. For example, running a 2-vCPU instance
  for 3 hours uses 6 CPU hours, and running an 8-vCPU instance for 2 hours uses
  16 CPU hours.
</Tip>

See [subscription plans](https://docs.qbraid.com/v2/home/pricing#subscription-plans) for current compute-hour allowances.

Open **Account > Usage** to inspect your compute-hour balance and renewal date. The page also shows session counts, daily usage, and total compute hours used. Use **Compute Settings** to manage credit spending.

If your allowance is exhausted and credit spending cannot cover the session, launching a subscription CPU instance fails with
`Launch failed: Compute hours exhausted and insufficient credits`. See
[Troubleshooting](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting#launch-failed-compute-hours-exhausted) for how to
resolve it.

### Auto-switch to credits

To use wallet credits after your compute allowance runs out, enable automatic credit spending:

1. Open **Account > Usage > Compute Settings**.
2. Enable **Auto-switch to Credits**.

When compute hours run out, eligible sessions spend wallet credits.

With auto-switch enabled, sessions can continue while you have enough credits. Check the launch screen for the current rate, as described in [Pricing](https://docs.qbraid.com/v2/home/pricing#subscription-instances).

## Disk usage

Your subscription tier sets the storage quota for subscription Lab. See [subscription plans](https://docs.qbraid.com/v2/home/pricing#subscription-plans) for the plan allowances and **Account > Usage** for your effective quota.

Disk usage includes files, notebooks, environments, and data stored in subscription Lab. Check your usage in Account before adding large files or environments.

To do so, click **Dashboard** in the left sidebar and scroll to the **Usage Overview** section at the bottom of the page. For more details, go to **Account** > **Usage** in the left sidebar.

Inside Lab, open [Settings](https://docs.qbraid.com/v2/lab/user-guide/settings) to check your storage usage and quota.

### Exceeding disk usage quotas

Once the disk is full, notebook cells start failing with errors such as
`[Errno 28] No space left on device` or `database or disk is full`. See
[No space left on device](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting#no-space-left-on-device) for how to
recognize and resolve this.

If Lab reports that you are over quota, reduce storage usage before resuming work. Follow the warning shown in your session. The quota and available disk capacity both limit how much data you can store.

### Disk usage management

Installed Lab environments often use the most disk space. Uninstall environments you no longer need to free up storage.

To analyze your disk usage in detail, open the Terminal and run the `gdu` command:

```bash
gdu [flags] [directory_to_scan]
```

For more information on `gdu`, refer to the [official documentation](https://github.com/dundee/gdu).

Once you've identified large or unwanted files and directories, you can delete them using the `rm` command in the Terminal:

```bash
rm -rf [directory_to_delete]
```

Alternatively, you can remove files and directories from the [File Browser](https://docs.qbraid.com/v2/lab/user-guide/files) by right-clicking and selecting **Delete**.

## On-demand instance billing

On-demand GPU and CPU instances charge credits separately from subscription compute hours.

- Running instances charge compute and storage. Check the launch screen for the current rate. See [pricing](https://docs.qbraid.com/v2/home/pricing#gpu-instances) for details.
- Stopped instances charge for retained disk capacity at the applicable storage rate.
- Terminated instances incur no further charges. Termination permanently deletes the instance and its disk.

The default balance tiers allow up to five concurrent on-demand instances. Your account configuration can impose different limits. See [On-Demand Instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances#billing) for the thresholds and lifecycle details.

## AI chat usage

Your plan includes an AI spending allowance. Usage depends on the selected model's token rates, not a fixed number of prompts. See [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas) for allowances, renewal dates, and credit-spending rules.

AI has a separate **Auto-switch to Credits** setting:

1. Open **Account > Usage > AI Chat Usage**.
2. Enable **Auto-switch to Credits** if your workspace policy permits it.

Further AI usage can spend wallet credits when the allowance is exhausted, provided you have sufficient credits. An organization policy or outstanding balance can prevent further requests.

## Monitoring usage

Open **Account > Usage** from your [account dashboard](https://account.qbraid.com/) to inspect compute hours, storage, and AI usage. Select **Refresh** to retrieve current data.
