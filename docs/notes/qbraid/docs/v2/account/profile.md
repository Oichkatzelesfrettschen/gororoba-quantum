> Full piece: [https://docs.qbraid.com/v2/account/profile.md](https://docs.qbraid.com/v2/account/profile.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 cbbb09058c7ddf95ef6096749cf3276e16dfd0f97af855342c8ea42cadeef2ea.

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

# Profile

> Edit your profile, manage passkeys and notification preferences, and request account deletion.

Open [Account > Profile](https://account.qbraid.com/account/profile) to manage your personal account.

## Edit your profile

Select **Edit profile** to change your first name, last name, or username, then select **Save changes**. Use **Change profile photo** to choose an image for your avatar.

Your email address is read-only. Contact [Support](https://docs.qbraid.com/v2/account/support) if you need help changing it.

## Manage passkeys

The **Passkeys** card lets you sign in with your fingerprint, face, or a security key.

1. Select **Add passkey**.
2. Follow your browser or device's registration prompt.
3. Check that the new passkey appears in the list.

To remove a passkey, select its remove control and confirm **Remove**. That passkey can no longer sign you in.

If the browser does not support passkeys, use a supported browser on a device with a screen lock. The card displays a separate message when passkeys are unavailable for your account.

<Frame>
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nQVfO8de4nyjX09uLKfUqpP6JtibwDAks5Mzl"
    alt="Passkeys card showing the Add passkey control and an empty passkey list"
  />
</Frame>

Select Add passkey to start your browser or device registration prompt.

## Switch or leave organizations

The **Organizations** section lists your memberships and roles. Select another organization to switch the active workspace. Use the search field when it appears to find an organization by name.

To leave, select **Leave organization** for that membership and confirm. You lose access to its resources. Stop active Lab sessions before leaving. Your assigned seat is revoked, and any remaining organization wallet credits are queued for return to the organization. You cannot leave qBraid Default. Owners must [transfer ownership](https://docs.qbraid.com/v2/account/organizations/members#transfer-ownership) before leaving.

To accept an email invitation or join with a code, see [Join an organization](https://docs.qbraid.com/v2/account/organizations/invitations).

## Connect Open Quantum

Use the **Integrations** section to link an Open Quantum account. See the [Open Quantum setup guide](https://docs.qbraid.com/v2/account/integrations/openquantum).

## Set notification and cookie preferences

**Notification Preferences** provides separate email and in-app controls for each category, plus an overall enable control. Changes save when you toggle them. If email delivery is suspended, the card directs you to support.

Use **Cookie Preferences** to review your optional cookie choices.

## Request account deletion

1. Switch to **qBraid Default**.
2. Open **Profile** and find **Delete Account**.
3. Optionally enter a reason, up to 500 characters.
4. Confirm that you understand the action cannot be undone.
5. Submit the deletion request.

The request enters **Pending Review**. The page states that the team reviews requests within 2 to 3 business days. While the request is pending, select **Cancel Request** to withdraw it. If a request is rejected, review the displayed admin notes and use **Re-submit Request** if you want to apply again.

<Warning>
  Account deletion is permanent after processing. Approval cancels active
  subscriptions and signs you out. Save the data you need before requesting
  deletion.
</Warning>

<Frame>
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nG2g9hY3xMFJ6CBoTawtgyinzcOl7pqY15PL8"
    alt="Delete Account form with an optional reason, confirmation checkbox, and deletion request button"
  />
</Frame>

Review the deletion notice before submitting a request.

## Refresh account changes

If membership, role, or balance changes have not appeared, select **Refresh account data** beside settings in the sidebar profile row. See [Refresh account data](https://docs.qbraid.com/v2/account/refresh) for instructions and workspace recovery.
