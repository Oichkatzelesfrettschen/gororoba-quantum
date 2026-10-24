> Full piece: [https://docs.qbraid.com/v2/account/chat.md](https://docs.qbraid.com/v2/account/chat.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 774f3dc8c1800de9fb0485fbdc2cad74b1e22e5ce67a2d714f38f19da1994995.

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

# Chat and Agent

> Use AI chat for quantum computing questions or attach Agent to a compute instance.

## Start a chat

1. Open [Chat](https://account.qbraid.com/chat) in the intended workspace.
2. Choose an available model in the message composer.
3. Enter your question and send the message.
4. Review any tool approval request before you approve or deny the action.

Model availability depends on your account's access. If the model list fails to load, retry it before sending. See [AI models](https://docs.qbraid.com/v2/account/models) for model selection and [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas) for allowances and charges.

When image attachments are available, use the attachment control to include images with your question. If an attachment fails validation, remove it or choose a supported image before retrying.

## Return to a conversation

Use the conversation history to reopen a saved chat. A conversation link reopens that thread in the same workspace when you have access. Start a new chat when you need a separate conversation.

The conversation controls let you export or delete the current conversation. The usage panel shows token and model usage for the thread. [Account Usage](https://docs.qbraid.com/v2/account/usage) shows your monthly allowance and the separate AI **Auto-switch to Credits** setting.

If a message fails to send, check the draft and its attachments before retrying. An error while loading history does not mean that your saved conversation has been deleted.

## Use Agent on a compute instance

Open [Agent](https://account.qbraid.com/agent) to run a codeq session inside a compute instance. Attach to an available running instance, resume a stopped one, or launch an available profile.

Agent opens a terminal session on the selected instance. Launch and running costs follow the instance's compute profile. Use the instance controls to stop compute when you are finished.

If the terminal session ends, use **Reconnect**. See [Dashboard and instances](https://docs.qbraid.com/v2/account/dashboard) for the difference between stopping and terminating compute.
