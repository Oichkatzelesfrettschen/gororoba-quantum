> Full piece: [https://docs.qbraid.com/v2/account/organizations/members.md](https://docs.qbraid.com/v2/account/organizations/members.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 de45b4a565bbad6ccfa55276df31254600e74fd621266542a7c5077cd3815dfc.

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

# Members and invitations

> Invite members, manage roles and access, create invite codes, and transfer ownership.

Select your organization and open [Members](https://account.qbraid.com/organizations/members). Access and available actions depend on your role. Search by name or email, then filter by role or status, including active, pending, suspended, and inactive.

## Roles

| Role    | Purpose                                                                  |
| ------- | ------------------------------------------------------------------------ |
| Owner   | Controls the organization and can transfer ownership.                    |
| Admin   | Manages members, resources, settings, and billing.                       |
| Manager | Invites and manages members within the permissions granted to that role. |
| Member  | Uses the organization's resources.                                       |

Invitation roles are limited by your own role. Owner is not an invitation role. The organization has one owner, and ownership changes through the transfer flow below.

## Invite a person

1. Select **Invite Member**.
2. Enter the person's email address.
3. Select an available role.
4. Optionally enter credits to allocate and a welcome message.
5. Send the invitation.

<Frame>
  <img src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nhymrGGYzQV0XrqfCJBvN1OSoxHFbk2IpcTiG" alt="Member invitation form with email, Admin, Manager, and Member roles, optional credit allocation, and welcome message" />
</Frame>

The member remains pending until they accept. They can sign up if they do not already have a qBraid account. See [Join an organization](https://docs.qbraid.com/v2/account/organizations/invitations) for the recipient's steps.

Invitation credit allocations are processed when the invitation is created, so they can leave the organization pool before acceptance. Cancelling or declining an invitation queues a return of allocated credits. Check [Transactions](https://docs.qbraid.com/v2/account/organizations/transactions) for the transfer and return.

## Invite several people

Select **Bulk Invite**. Add entries manually with **Add to Queue**, or upload a CSV. Download the form's CSV template to use the supported role identifiers.

```csv
email,role,credits
alice@example.com,organization_member,500
bob@example.com,organization_admin,0
carol@example.com,organization_member,1000
```

The role identifiers for ordinary organizations are `organization_admin`, `organization_manager`, and `organization_member`. Available roles still depend on your permissions. Provider organizations use their own provider roles.

Review the queue after importing. Invalid email rows can be omitted, and an unavailable role can fall back to your default role. Do not assume that every CSV row was imported unchanged.

Send at most 100 invitations per request. The total credit allocation cannot exceed the organization wallet balance. Review the per-row result after selecting **Send Invitations**.

## Manage members

Open the actions menu on a member's row. Available actions depend on the member's status and your permissions.

- **Resend Invite** sends another email for a pending invitation.
- **Cancel Invite** opens the confirmation dialog. Select **Cancel Invitation** to withdraw the pending invitation.
- **Suspend Member** suspends a member's access.
- **Activate Member** reactivates a suspended member.
- **Remove Member** removes the membership after confirmation.
- **Edit Role** changes an assignable role.

Review the confirmation before removing or suspending a member. If a removed member needs access again, send a new invitation.

## Create an invite code

Use **Members > Invite Codes** for a shareable code, join link, or QR image. Owners, Admins, and Managers can create and disable codes. Recipients join as Members on Free.

Follow [Invite codes](https://docs.qbraid.com/v2/account/organizations/invite-codes) for creation, sharing, redemption, expiration, usage limits, and existing-membership behavior.

## Transfer ownership

Only the current owner can transfer ownership to another active member.

1. Find the recipient on **Members**.
2. Open **Edit Role**.
3. Select **Transfer ownership**.
4. Review the confirmation naming the new owner.
5. Confirm **Make [name] the owner**.

You become an admin after the transfer. Only the new owner can transfer ownership back. Pending invitees cannot receive ownership.
