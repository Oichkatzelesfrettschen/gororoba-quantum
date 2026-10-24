> Full piece: [https://docs.qbraid.com/v2/account/organizations/creating-an-organization.md](https://docs.qbraid.com/v2/account/organizations/creating-an-organization.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ef0786b6c15e45154f524d263834d3c6f69bb681bf6ecf9b3c009877270070f3.

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

# Create an organization

> Request a team workspace and track or cancel your pending request.

1. Sign in to [qBraid Account](https://account.qbraid.com/).
2. Open [Request an Organization](https://account.qbraid.com/organizations/new).
3. Enter the organization name.
4. Enter a description of 10 to 500 characters.
5. Optionally enter a website and address. The website must be a valid HTTP or HTTPS URL.
6. Explain why you need the organization in 10 to 500 characters.
7. Select **Submit Request**.

After submission, the page shows **Request Submitted**. The page states that the team reviews requests within 2 to 3 business days and emails the decision.

## Review a pending request

Return to the request page to see the submitted details and **Pending Review** status. You can have one pending request at a time. Select **Cancel Request** if you need to withdraw it.

## Switch to the new organization

After approval, switch from your personal workspace to the organization before managing its resources.

1. Open the workspace switcher at the top-left of the dashboard sidebar.
2. Select the approved organization from the list. If you belong to more than five workspaces, use the search field to filter by part of its name.
3. Wait for the switching screen to finish.
4. Check that the switcher now shows the organization you selected.

<Frame caption="Open the switcher and select the workspace whose resources you want to use.">
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nw97eXuL9Uo8LlVXWaATyftYdIq5HzxghPbQJ"
    alt="Workspace switcher showing qBraid Default and an organization"
  />
</Frame>

<Frame caption="Workspace switching at 2× speed. The selected organization appears in the sidebar after the switching screen finishes.">
  <video
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50n9nZ2lN8VS286yKEb5TWqowfmRPC1Xl3O4xzh"
    controls
    muted
    playsInline
    preload="metadata"
    aria-label="Switching from qBraid Default to an organization at twice normal speed"
  />
</Frame>

[Watch the workspace-switching recording at 2× speed](https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50n9nZ2lN8VS286yKEb5TWqowfmRPC1Xl3O4xzh).

To return to your personal workspace, open the same switcher and select **qBraid Default**. You can switch to any organization in the list without signing out.

If an approved organization is missing, use [Refresh account data](https://docs.qbraid.com/v2/account/refresh), then reopen the switcher. Contact [Support](https://docs.qbraid.com/v2/account/support) if it still does not appear.

<Warning>
  Check the selected workspace before inviting members, transferring credits,
  or changing billing. These actions apply to that workspace.
</Warning>

Once you have selected the organization, [invite members](https://docs.qbraid.com/v2/account/organizations/members), review [Settings](https://docs.qbraid.com/v2/account/organizations/settings), or set up its [subscription](https://docs.qbraid.com/v2/account/organizations/subscriptions).

If you already have an invitation, follow [Join an organization](https://docs.qbraid.com/v2/account/organizations/invitations) instead of requesting another workspace.
