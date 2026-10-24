> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/troubleshooting.md](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 51f9332e8aef9049014ee71e7f006720d4b53487e2a1d3ff724c840445a5d3eb.

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

# Troubleshooting

[![https://img.shields.io/badge/issue_tracking-github-blue?logo=github](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/qBraid/community/issues)

Check the [qBraid Status Page](https://status.qbraid.com/) to see if there are any ongoing incidents or maintenance windows affecting services.

If your error is not listed or the suggested fix does not work, [submit a support request](https://account.qbraid.com/support), [email us](mailto:contact@qbraid.com), or [open a bug report](https://github.com/qBraid/community/issues/new?assignees=&labels=bug).

Also see our [FAQs](https://docs.qbraid.com/v2/home/faq).

## Launch failed: Compute hours exhausted

When you click **Launch** on a subscription (CPU) profile and get:

```text
Launch failed: Compute hours exhausted and insufficient credits.
Required: $0.00/hour, available: $0.00.
```

you have used all of the [compute hours](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#compute-hours) included with
your plan for the current month, and you do not have credits set up to cover the session instead. The
amounts shown in the message vary with the profile you tried to launch. Nothing is wrong with your
account, and none of your files or environments are affected.

Compute hours reset at the start of each month. Until then you can still download your files, and you
can restore the ability to launch by upgrading your plan or by switching sessions over to credits.

### Get your files without launching

To download your files without launching Lab, open the
**Usage Overview** section of your account dashboard. See
[Download your files](https://docs.qbraid.com/v2/account/usage#download-your-files).

### Upgrade your subscription

A higher tier comes with a larger monthly compute hour allocation (Free 100, Standard 400, Pro 2000).
See [Personal Subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions#subscribe-or-upgrade) to change your plan, or
[Organization Subscriptions](https://docs.qbraid.com/v2/account/organizations/subscriptions) if your seat is managed by an
organization.

### Buy credits and enable auto-switch

Credits cover CPU sessions once your compute hours run out, but only when auto-switch is turned on.
Both steps are required. Adding credits alone does not resolve the error.

1. [Buy credits](https://docs.qbraid.com/v2/account/wallet/buy-credits#how-to-buy) from **Account > Wallet**. If you are in
   an organization without purchase permissions,
   [request credits from an admin](https://docs.qbraid.com/v2/account/organizations/credit-requests) instead.
2. Enable [Auto-switch to credits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#auto-switch-to-credits) under
   **Account > Usage > Compute Settings**.

Sessions then bill against your credit balance at the rate shown on the launch screen. See [Pricing](https://docs.qbraid.com/v2/home/pricing#subscription-instances) for how to check current rates. You can confirm your remaining compute hours and credit
balance at any time on the [Usage page](https://docs.qbraid.com/v2/account/usage).

<Tip>
  [On-demand instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances) (GPUs and
  high-spec CPUs) always bill credits directly and never draw on compute hours,
  so they remain available even when your monthly allocation is exhausted.
</Tip>

## Launch failed: JupyterHub is temporarily unavailable

When you click **Launch** and get an error like:

```text
Launch failed: JupyterHub API error
(user: user-email@example.com, cluster: labX, operation: get_user_info):
Server error - JupyterHub is temporarily unavailable
```

this is a temporary problem on qBraid's side, not something wrong with your account. It is unrelated
to your quota, credits, subscription, or anything you did. Your files, environments, and balances
are all unaffected, and no compute hours are consumed by the failed launch. The user, cluster, and
operation named in the message are diagnostic details, not settings you need to change.

The service often recovers on its own. Wait a few minutes before trying again:

1. Check the [qBraid Status Page](https://status.qbraid.com/) for an ongoing incident.
2. Wait a few minutes, then click **Launch** again.
3. If it still fails, [submit a support request](https://account.qbraid.com/support) from your
   account page. Include the full error message. The user, cluster, and operation it names help us
   identify the problem.
4. Once we confirm the service is restored, launch again as normal.

<Note>
  Repeatedly clicking **Launch** will not speed up recovery. Give it a few
  minutes between attempts.
</Note>

## Lab server errors

If you get one of the following errors from inside Lab,

- `Service unavailable or unreachable`
- `File Save Error`

For these types of errors, refreshing the page won't work and you will need to restart your qBraid Lab server.

You can stop your running server from your [account dashboard](https://account.qbraid.com/), and then launch a new instance.

## ModuleNotFoundError

While running a notebook, if you get a `ModuleNotFoundError` after an import statement:

1. Check to make sure you are using the correct notebook kernel for your environment, see [Switch notebook kernel](https://docs.qbraid.com/v2/lab/user-guide/notebooks/#switch-notebook-kernel).
2. If you are using the correct kernel, the package you are trying to import may not be installed in that environment. See [Install new package](https://docs.qbraid.com/v2/lab/user-guide/environments#install-new-package).

## No space left on device

If running a notebook cell produces errors like:

```text
The history saving thread hit an unexpected error
(OperationalError('database or disk is full')).
History will not be written to the database.

mkdir -p failed for path /home/jovyan/.cache/matplotlib:
[Errno 28] No space left on device

Fontconfig error: No writable cache directories
```

you have run out of [disk space](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#disk-usage). The exact wording
varies depending on which library tried to write to disk first, but the giveaways are
`database or disk is full`, `[Errno 28] No space left on device`, and complaints about cache
directories that cannot be written. The error indicates that there is no space left to save data.

Check your current usage against your quota from the **Storage** card in the
[Settings](https://docs.qbraid.com/v2/lab/user-guide/settings) extension, opened with the **Settings** icon
in the bottom-left of Lab, or from the **Storage** card on the
[Usage page](https://docs.qbraid.com/v2/account/usage#overview) under **Account > Usage**. Then either free up space or
raise your quota:

- **Free up space.** Installed environments are usually the biggest consumers, so uninstalling ones
  you no longer use frees the most space. You can also delete files from the
  [file browser](https://docs.qbraid.com/v2/lab/user-guide/files) or track down large directories from the terminal. See
  [Disk Usage Management](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#disk-usage-management).
- **Upgrade your subscription.** Storage scales with your plan: 15 GB on Free, 50 GB on Standard,
  150 GB on Pro. See [Personal Subscriptions](https://docs.qbraid.com/v2/account/wallet/subscriptions#subscribe-or-upgrade).

After clearing space, restart the kernel (**Kernel > Restart Kernel**) so the affected libraries can
recreate their caches.

<Warning>
  If you stay over your disk quota, your Lab session will eventually be
  terminated, and you will need to reduce your usage before you can resume. See
  [Exceeding Disk Usage
  Quotas](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#exceeding-disk-usage-quotas).
</Warning>
