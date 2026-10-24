> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/guidelines.md](https://docs.qbraid.com/v2/lab/user-guide/guidelines.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 b531e3d98db79816ba256a163c356117514f5829053e54e7ef2516544a65530c.

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

# Usage Guidelines

> Instructions to help you navigate, manage, and customize your lab environment effectively.

## Customizing Your Environment

Your `.bashrc` file contains a specific delimiter to delineate which sections of the file can be safely modified to persist between sessions. Here is the structure of the delimiter:

```bash
# ==================== DO NOT MODIFY CODE ABOVE THIS LINE ====================
# ANY CHANGES ABOVE THIS LINE WILL BE OVERWRITTEN DURING QBRAID SYSTEM STARTUP.
# You may add your custom configurations below this line.
```

Please ensure that **any customizations** you wish to retain are added **below** this delimiter line. Changes made above this line will not be saved when your session ends.

## Suppressing the Terminal Banner

If you prefer not to see the qBraid terminal banner during startup, you can suppress it by setting the `QBRAID_SHOW_BANNER` environment variable to `false`. This adjustment can be made by executing the following command in terminal:

```bash
echo "export QBRAID_SHOW_BANNER=false" >> "$HOME/.bashrc"
```

This command appends the setting to disable the banner to the end of your `.bashrc` file, ensuring it takes effect in all future terminal sessions.
