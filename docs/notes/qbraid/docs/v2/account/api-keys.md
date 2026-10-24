> Full piece: [https://docs.qbraid.com/v2/account/api-keys.md](https://docs.qbraid.com/v2/account/api-keys.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ee0c998fee1d745f3376bbbc7fcfe700cd8fa45d23095d2cbc13846ad123fe51.

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

# API keys

> Create, inspect, rotate, and revoke API keys for the selected workspace.

Use API keys with [qBraid Runtime](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components), the [REST API](https://docs.qbraid.com/v2/api-reference/user-guide/overview), and the [CLI](https://docs.qbraid.com/v2/cli/api-reference/qbraid).

## Create a key

1. Select the intended workspace.
2. Open [Account > API Keys](https://account.qbraid.com/account/api-keys).
3. Select **Create API Key**.
4. Enter a name and, optionally, a description.
5. Choose 30, 60, or 90 days, **Never expire**, or a custom number of days.
6. Create the key and copy its secret value into your password manager or secrets store.

<Warning>
  The secret value appears only after creation or regeneration. If you lose it,
  regenerate the key or create a replacement.
</Warning>

The creation form does not provide a scope selector. Use the key details to inspect the permissions associated with a key.

## Inspect a key

Select a key in the table to open its detail dialog. The table shows status, creation date, last use, and expiration. Details can include the last IP address, rate limit, permissions, constraints, and revocation information.

Keys belong to the selected workspace. Switch workspaces if the key you expect is not in the list.

## Rotate a key

Select the key's **Regenerate** control and confirm the dialog. Copy the new secret when it appears.

<Warning>
  Regeneration invalidates the previous secret. Update the applications that use
  it immediately. For a planned migration, create a separate replacement key,
  update and verify your applications, then revoke the old key.
</Warning>

## Revoke a key

Select the key's **Revoke** control and confirm. Revocation prevents further use of that key. Check that your applications have a working replacement before revoking a key they still need.

Keep secret values out of source control, screenshots, and support requests. Review last-used information when investigating unexpected access. Report vulnerabilities through the [qBraid security advisory form](https://github.com/qBraid/community/security/advisories).
