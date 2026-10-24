> Full piece: [https://docs.qbraid.com/v2/account/overview.md](https://docs.qbraid.com/v2/account/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 2c20569aed3a9f1dffbbd40151e51c5ac47c90a9b7944433e0389be8184fe9ca.

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

# Account overview

> Launch compute, build circuits, use AI chat, and manage your qBraid workspace.

Sign in at [account.qbraid.com](https://account.qbraid.com/). Use Account to launch Lab, run quantum jobs, build circuits, chat with AI models, and manage your workspace.

For account creation, email codes, Google sign-in, and passkeys, see [Sign in](https://docs.qbraid.com/v2/account/sign-in).

## Video walkthroughs

These short recordings play at 2× speed. Each guide includes written steps and a video player.

- [Refresh account data](https://docs.qbraid.com/v2/account/refresh#refresh-your-account).
- [Switch workspaces](https://docs.qbraid.com/v2/account/organizations/creating-an-organization#switch-to-the-new-organization).
- [Build a circuit in Composer](https://docs.qbraid.com/v2/account/composer#watch-the-composer-flow).

## Choose a workspace

Use the workspace switcher to select **qBraid Default** or an organization you belong to. Check the selected workspace before you launch compute, create an API key, or change billing.

qBraid Default is your individual workspace. Organizations have their own members, credits, subscriptions, and permissions. Your profile is personal, while resource and billing pages use the selected workspace.

## Compute and quantum tools

<CardGroup cols={2}>
  <Card
    title="Dashboard and instances"
    icon="desktop"
    href="/v2/account/dashboard"
  >
    Launch Lab, manage compute instances, and download your files.
  </Card>
  <Card
    title="Circuit Composer"
    icon="diagram-project"
    href="/v2/account/composer"
  >
    Build a circuit, edit QASM, and submit it to a quantum device.
  </Card>
  <Card
    title="Devices and quantum jobs"
    icon="microchip"
    href="/v2/account/quantum-jobs"
  >
    Compare devices and inspect job status, results, and errors.
  </Card>
  <Card title="Chat and Agent" icon="comments" href="/v2/account/chat">
    Ask quantum computing questions or open an agent terminal on your compute
    instance.
  </Card>
  <Card title="Explore and Learn" icon="compass" href="/v2/account/explore-catalog">
    Find projects, courses, events, and challenges, or submit your own project.
  </Card>
  <Card title="Support" icon="life-ring" href="/v2/account/support">
    Submit a request, read replies, and follow its status.
  </Card>
</CardGroup>

## Account and team settings

<CardGroup cols={2}>
  <Card title="Profile" icon="user" href="/v2/account/profile">
    Edit your profile, register passkeys, and manage notification preferences.
  </Card>
  <Card title="API keys" icon="key" href="/v2/account/api-keys">
    Create, rotate, and revoke keys for the selected workspace.
  </Card>
  <Card title="Wallet" icon="wallet" href="/v2/account/wallet/overview">
    Manage your credits, subscription, and payment history.
  </Card>
  <Card title="Usage" icon="chart-line" href="/v2/account/usage">
    Inspect compute, storage, AI, and simulator usage.
  </Card>
  <Card
    title="Organizations"
    icon="users"
    href="/v2/account/organizations/overview"
  >
    Manage membership, invitations, team billing, and settings.
  </Card>
</CardGroup>

## Refresh account changes

If membership, role, or balance changes have not appeared, select **Refresh account data** beside settings in the sidebar profile row. See [Refresh account data](https://docs.qbraid.com/v2/account/refresh) for instructions and workspace recovery.
