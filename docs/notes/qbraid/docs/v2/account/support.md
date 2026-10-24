> Full piece: [https://docs.qbraid.com/v2/account/support.md](https://docs.qbraid.com/v2/account/support.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 67943325f5b8e56f7f2994bffc67221f2165e6813b1675b6bdae01dc6c621cf7.

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

# Support

> Submit support requests, track their status, and reply to the qBraid team.

1. Open [Support](https://account.qbraid.com/support).
2. Select **New Request**.
3. Describe the problem, including the affected feature and steps to reproduce it.
4. Submit the request.
5. Open the request in the list to read the response and comments.

Use the status filters to find an existing request. When a request accepts replies, type into **Write a reply** and select **Send reply**. You can also press **Ctrl+Enter** to send. Closed requests show that the conversation is closed.

Use the request reference when following up. Do not include API keys, payment details, or other credentials in your request.

The Composer **Feedback** button also opens the support form. Send feedback through Support. The standalone Feedback page does not yet have a submission form.
