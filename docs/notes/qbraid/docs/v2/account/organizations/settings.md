> Full piece: [https://docs.qbraid.com/v2/account/organizations/settings.md](https://docs.qbraid.com/v2/account/organizations/settings.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 54de64755cf77bb4a6238dd6a406276201cc62c9e9519e3288c030d61df6324b.

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

> Set your org's name and logo, control what happens when new members join, and find owner-only actions.

Owners and Admins can use **General** and **Member Settings** on the [Settings page](https://account.qbraid.com/organizations/settings) to update organization details and member settings. Only the Owner sees **Danger Zone**.

## General

Organization details appear in invitations, the workspace switcher, and the dashboard.

| Field             | Required | Notes                                                |
| ----------------- | -------- | ---------------------------------------------------- |
| Organization Name | Yes      | What people see everywhere your org shows up.        |
| Description       | No       | A short summary of what your group does.             |
| Website           | Yes      | Must be a valid URL.                                 |
| Address           | No       | Used for invoices and contracts.                     |
| Logo (Light)      | No       | For light-themed UIs. PNG, JPG, or WEBP. Max 200 KB. |
| Logo (Dark)       | No       | For dark-themed UIs. Same formats and size limit.    |

### Update general settings

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher in the top-left of the dashboard and select your
    organization.
  </Step>
  <Step title="Open Settings">Click **Settings** in the sidebar.</Step>
  <Step title="Edit the General section">
    Update any field. Required fields are marked.
  </Step>
  <Step title="Save">
    Click **Save** at the bottom of the section. An "Unsaved changes" reminder
    appears next to the button until you save. Select **Cancel** to discard
    changes to this section.
  </Step>
</Steps>

<Tip>
  Upload both a light and a dark logo if you have versions for each theme.
  qBraid picks the right one automatically based on the viewer's theme.
</Tip>

## Member settings

Email invitations use the role selected by the inviter. Invite codes always join people as Members on Free, regardless of the default-role and automatic-seat settings below. Change a member's role or assign a paid seat afterward when needed.

Automatic seat assignment runs when a member accepts an email invitation or an administrator activates a membership. It requires an available seat. Seat-assignment credits apply to future seat assignments, including manual assignments to existing members.

| Setting                  | What it does                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Auto-assign Default Role | Stores the default-role preference. It does not override an email invitation or invite code.                                         |
| Default Role             | Choose Member, Manager, or Admin. Use the invitation form or **Members > Edit Role** to set a member's actual role.                  |
| Auto-assign Seats        | When **Enabled**, attempts to assign an available seat on email acceptance or membership activation. Invite-code joins are excluded. |
| Seat Assignment Credits  | Credits to transfer from the org wallet whenever a seat gets assigned (manual or automatic). Max 100,000.                            |

<Frame>
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nKYgzpa2IhwkxcPtRs2nLmr4z1DGVlQTayYve"
    alt="Member Settings showing default role, automatic role and seat assignment controls, seat assignment credits, and Save"
  />
</Frame>

Member settings control automatic seat assignment and the credits allocated with a seat.

### Update member settings

<Steps>
  <Step title="Switch to your organization">
    Open the workspace switcher and select your organization.
  </Step>
  <Step title="Open Settings">Click **Settings** in the sidebar.</Step>
  <Step title="Scroll to Member Settings">Below the General section.</Step>
  <Step title="Edit the fields">
    Change auto-assign behavior, default role, or seat credits.
  </Step>
  <Step title="Save">Click **Save**.</Step>
</Steps>

<Note>
  A membership can become active even if automatic seat assignment fails. Check
  **Billing > Seat Management** after acceptance or activation. If no seat was
  assigned, check available seats and the credits needed for its allocation,
  then [assign a seat manually](https://docs.qbraid.com/v2/account/organizations/seats#assign-a-seat).
</Note>

## Ownership and deletion

The owner-only **Danger Zone** displays disabled **Transfer** and **Delete** controls marked **Coming soon**. Organization deletion is not available there.

Ownership transfer is available from **Members > Edit Role** for another active member. Follow [Transfer ownership](https://docs.qbraid.com/v2/account/organizations/members#transfer-ownership) to use the working flow.
