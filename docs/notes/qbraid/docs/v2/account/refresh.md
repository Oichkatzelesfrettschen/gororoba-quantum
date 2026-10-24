> Full piece: [https://docs.qbraid.com/v2/account/refresh.md](https://docs.qbraid.com/v2/account/refresh.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 eff944a39f3e15439ac8a2bef80d4c435bf30a4fa8147a0117e58b0d77a84a95.

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

# Refresh account data

> Update your organizations, roles, credits, and account access without signing out.

Use **Refresh account data** when an organization, role, credit balance, or subscription change has not appeared in Account. You can refresh your account without signing out or leaving the page.

## Refresh your account

1. Open the sidebar. If it is collapsed, select **Toggle Sidebar**.
2. Find your profile row near the bottom, above **Log out**.
3. Select the circular-arrow button beside **Account settings**. Its label is **Refresh account data**.
4. Wait for **Refreshing account…** to change to **Account refreshed**.
5. Check the workspace switcher and the page affected by the change.

The icon spins while the refresh runs. The control is temporarily unavailable during a refresh or an organization switch.

<Frame caption="Select the circular-arrow button beside Account settings to refresh your account.">
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nLh0015VeqSNuhfJndBxKE61UVciHAgWY4srZ"
    alt="Refresh account data button circled beside Account settings in the sidebar profile row"
    width="256"
  />
</Frame>

<Frame caption="Account refresh at 2× speed. Wait for Account refreshed before checking the updated data.">
  <video
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nOQpiONERqbTUIK1z5VaNLSmw6khtlWYseFvd"
    controls
    muted
    playsInline
    preload="metadata"
    aria-label="Refreshing account data and seeing the Account refreshed message at twice normal speed"
  />
</Frame>

[Open the refresh recording](https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nOQpiONERqbTUIK1z5VaNLSmw6khtlWYseFvd).

## What refresh updates

Refresh reloads your account information, including organization memberships, roles, and credits, and updates the related organization and billing data. Use it after an administrator changes your access or after a credit or subscription change is missing from the UI.

It does not accept a pending invitation or grant a role, seat, or credits. Complete the [email invitation](https://docs.qbraid.com/v2/account/organizations/invitations) or [invite-code flow](https://docs.qbraid.com/v2/account/organizations/invite-codes#join-with-a-code) to join first. A successful code join refreshes your membership and opens the organization's dashboard automatically.

Account refresh is separate from refreshing a job list, device catalog, or compute environment. Use the relevant page's controls to check those resources.

## Select the right workspace

Use the workspace switcher to choose **qBraid Default** or your organization. Account shows **Switching to [organization name]…** while the change completes, then loads that workspace's data. If the name is not available, the message is **Switching organization…**.

An account refresh keeps your current workspace if you still belong to it. If your membership has been removed, Account switches to your default workspace and displays **You were removed from your organization. Switched to your default workspace.**

If an organization is still missing after refreshing, check that you signed in with the account that joined it. Ask the organization administrator to check your membership. Refresh cannot restore removed or suspended access.

## Troubleshoot refresh

| Message or behavior                                                     | What to do                                                                                                                                                                                                                       |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Couldn't refresh — please try again.**                                | You remain signed in on the current page. Try the refresh again. If it keeps failing, contact [Support](https://docs.qbraid.com/v2/account/support).                                                                                                    |
| **Your session expired. Redirecting to sign in…**                       | Sign in again to continue.                                                                                                                                                                                                       |
| The refresh control is unavailable                                      | Wait for the current refresh or organization switch to finish.                                                                                                                                                                   |
| The workspace is correct but your access or balance is still unexpected | Ask the organization administrator to check your role, seat, or credit allocation. See [Members](https://docs.qbraid.com/v2/account/organizations/members), [Seats](https://docs.qbraid.com/v2/account/organizations/seats), and [Credits](https://docs.qbraid.com/v2/account/organizations/credits). |
