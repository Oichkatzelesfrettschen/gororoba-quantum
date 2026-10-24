> Full piece: [https://docs.qbraid.com/v2/ai/user-guide/ai-chat.md](https://docs.qbraid.com/v2/ai/user-guide/ai-chat.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e885528a970ea443a830bbddcd68159b48b198b8b075bc5a00729f5bf3d9eab3.

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

# AI Chat

> Start and manage conversations, choose a model, and inspect tool results in qBraid Account.

[AI Chat](https://account.qbraid.com/chat) answers questions about quantum computing and uses qBraid tools to retrieve platform information.

## Start a chat

1. Sign in to [qBraid Account](https://account.qbraid.com/chat).
2. Choose a model in the message composer.
3. Type your question and press **Enter**. Use **Shift+Enter** for a new line.
4. Read the response and expand tool details when you need to inspect a result.

For example:

```text
Show my recent quantum jobs. Which completed, which failed,
and what information is available about the failures?
```

Model availability and prices come from the current catalog. If the model list fails to load, retry it before sending. See [models and pricing](https://docs.qbraid.com/v2/ai/integrations/ai-gateway#available-models).

## Continue and export conversations

Conversations are saved to your account. Open an existing conversation from the sidebar or start a new chat for a separate task. Switching organizations changes the conversation context.

Use **Export** in the composer to download the conversation as Markdown. Use **Delete** to remove the current conversation after confirming the dialog. Export anything you want to keep before deleting it.

## Add images

When **Attach images** is available, select an image or paste one into the composer. Supported file types are PNG, JPEG, WebP, and GIF. Review the thumbnails and remove any image you do not want to send.

Image attachment availability depends on the deployed chat configuration. The composer reports preparation or validation errors before the message is sent.

## Work with code

Use **Code Canvas** to inspect code from a conversation and send code back to chat with an instruction. To execute code in a compute instance, open [Agent mode](https://docs.qbraid.com/v2/ai/user-guide/agent-mode).

## Check usage and recover a failed request

The chat header shows usage information. Open the usage panel for the conversation's model and token breakdown. The context indicator shows how much of the selected model's context window the conversation uses.

If a request fails, follow the recovery action shown in chat. A quota or credit error links to spending controls. A model access error requires refreshing the model list or choosing an available model. See [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas).

For long tasks, include the framework, device requirements, and desired output in your prompt. Inspect tool results and generated code before using them in an experiment.
