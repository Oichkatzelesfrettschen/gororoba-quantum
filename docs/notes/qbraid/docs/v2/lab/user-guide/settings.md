> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/settings.md](https://docs.qbraid.com/v2/lab/user-guide/settings.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e8f07dff0f6c0cd3f729c3a3dd5dfc05fbc149591297d98bc6d7c7334541c1cb.

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

# Settings

> Monitor usage, configure session behavior, and manage notifications from the qBraid Lab Settings extension.

The Settings extension provides an overview of your usage and preferences directly within qBraid Lab. To open it, click the **Settings** icon in the bottom-left sidebar.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/lab/_static/settings.png" alt="Lab settings with usage and session controls" width="100%" />
</div>

The preferences on this page are stored in the `[lab-settings]` section of `~/.qbraid/qbraidrc`.

## Usage & Compute

The top section displays your current resource consumption:

- **Compute Hours**: Shows your cumulative compute hours used against your monthly quota, with a progress bar.
- **Storage**: Displays your current disk usage in GB against your plan's storage quota. See [Disk Usage](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#disk-usage) for quota details by plan.

A daily usage chart shows your compute activity over a selectable time window (7, 14, 30, 90, or 365 days). Below the chart, summary stats show **Total Hours**, **CPU Sessions**, and **GPU Sessions** for the selected period.

## Session management

Three settings control how your Lab session is managed. Each has a minute input and a toggle to enable or disable it.

### Session check-ins

Prompts you at a recurring interval (e.g. every 60 minutes) to confirm you want to keep the session running. If you don't respond, the session will shut down. This prevents idle sessions from consuming compute hours unnecessarily.

- **Default**: 60 minutes, enabled
- **Range**: 10–480 minutes

### Auto shutdown

Automatically shuts down your session after the specified total runtime, regardless of activity. Turn off to disable this cutoff. If you set a limit below the current session runtime, Lab asks you to confirm because the change can stop the session immediately.

- **Default**: 120 minutes, enabled
- **Range**: 30–1440 minutes

### Idle timeout

After user and compute inactivity reaches the timeout, Lab shows an **Are you still there?** prompt with a five-minute countdown. Respond to continue the session. Turn off to disable this idle timeout.

- **Default**: 15 minutes, enabled
- **Range**: 10–120 minutes

## Notifications

### Slack notifications

Enable this to receive session alerts via a connected Slack workspace. This is disabled by default.
