> Full piece: [https://docs.qbraid.com/v2/account/organizations/invitations.md](https://docs.qbraid.com/v2/account/organizations/invitations.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 65bcb654250a27c8de5031ba90216d19bfac312637c0059bff5318477161a103.

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

# Join an organization

> Accept an email invitation or redeem an organization invite code.

## Accept an email invitation

Open the invitation link to review the organization and invitee details. If you are signed out, sign up or sign in with the invited email address.

Select **Accept invitation** to join, or **Decline** to reject the invitation. Opening the link alone does not accept it.

If the page says **Wrong account**, select **Sign in with different account**. For a cancelled or invalid invitation, ask the inviter to send a new one.

You can also open [Invitations](https://account.qbraid.com/invitations) while signed in to accept or decline pending invitations sent to your email.

## Join with a code

Use **Have an invite code?** on [Invitations](https://account.qbraid.com/invitations), open the shared join link, or scan its QR image. The preview asks you to confirm **Join [organization name]** after sign-in.

Follow [Join with a code](https://docs.qbraid.com/v2/account/organizations/invite-codes#join-with-a-code) for the complete steps and [existing-membership behavior](https://docs.qbraid.com/v2/account/organizations/invite-codes#existing-memberships). Codes grant the Member role on Free, which can differ from a role offered through an email invitation.
