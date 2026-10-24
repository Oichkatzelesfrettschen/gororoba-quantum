> Full piece: [https://docs.qbraid.com/v2/home/faq.md](https://docs.qbraid.com/v2/home/faq.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 12ad7dc3160c848caa64bb0a865a6c211830b008ff0b1e5fdcac482543a70133.

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

# FAQ

> Frequently asked questions about the V2 platform.

<AccordionGroup>
<Accordion title="Where did my credits go?">
Only credits purchased with a credit card or transferred to you within an organization were migrated from the legacy platform. Promotional credits (e.g., those redeemed via access codes) did not carry over and have expired.

If your credits lived in an organization (purchased or transferred there), check that you're viewing that organization. "qBraid Default" in the upper left means you're in your default workspace. Click the organization name to open the dropdown, switch to the correct organization, and the balance will update.

</Accordion>

<Accordion title="Where did my quantum jobs go?">
  Quantum jobs data was not migrated from the legacy platform. To get your old
  jobs data, go to **Jobs** on your [account page](https://account.qbraid.com/)
  and click **Download Old Jobs Data**. You can work with that data using the
  qBraid-SDK. See [Legacy Jobs Retrieval](https://docs.qbraid.com/v2/home/legacy-jobs) for details.
</Accordion>

<Accordion title="Where did my files go?">
  Lab uses a [file sync](https://docs.qbraid.com/v2/lab/user-guide/file-sync) mechanism, so your files
  can take a few minutes to appear after you launch. Once you're in Lab, check
  the file sync indicator in the bottom toolbar to see progress. You can keep
  working while files populate in the background; after a few minutes, your
  files should be fully restored.
</Accordion>

<Accordion title="What are CPU hours?">
  CPU hours measure usage as (number of vCPUs) × (hours used). For example, a
  2-vCPU instance for 3 hours uses 6 CPU hours; an 8-vCPU instance for 2 hours
  uses 16 CPU hours. See [Usage Limits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits) for
  more.
</Accordion>

<Accordion title="Why does launching Lab fail with 'Compute hours exhausted and insufficient credits'?">
  You've used all the compute hours included with your plan for this month, and
  you don't have credits set up to cover the session instead. Either [upgrade
  your subscription](https://docs.qbraid.com/v2/account/wallet/subscriptions#subscribe-or-upgrade) for a larger
  monthly allocation, or [buy
  credits](https://docs.qbraid.com/v2/account/wallet/buy-credits#how-to-buy) and turn on [auto-switch
  to credits](https://docs.qbraid.com/v2/lab/user-guide/usage-limits#auto-switch-to-credits). Both
  steps are needed, since credits only cover CPU sessions when auto-switch is
  on. See the full walkthrough in
  [Troubleshooting](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting#launch-failed-compute-hours-exhausted).
</Accordion>

<Accordion title="What is auto-switch to credits?">
  Your qBraid account has usage limits for AI chat and CPU hours. If you reach a
  limit, you can "switch to credits" and keep using that service. Usage is then
  billed in qBraid credits instead of counting against the quota. Those charges
  appear on your account under **Transactions**. The GPU simulators have a
  similar setting, **Usage-based billing for GPU simulators**, for jobs past
  their free daily allowance. See [Simulator
  usage](https://docs.qbraid.com/v2/account/usage#turn-on-usage-based-billing-for-gpu-simulators).
</Accordion>

<Accordion title="Why don't my environments show up in Lab? It says 'Workspace Empty'.">
  After you launch Lab, [files can take a few minutes to sync](https://docs.qbraid.com/v2/lab/user-guide/file-sync). When sync finishes, refresh the Environment Manager in the sidebar and your environments should appear.

If sync has completed and you've refreshed Environment Manager but it still says "Workspace Empty," you don't have any environments installed yet. Click **Add** in the Environment Manager, then [install an environment](https://docs.qbraid.com/v2/lab/user-guide/environments#install-environment) to get started.

</Accordion>

<Accordion title="What does 'No Capacity' mean next to a GPU instance?">
  It means all GPU instances of that type are currently in use due to high
  demand. Try again later or choose another instance type.
</Accordion>

<Accordion title="What is 'qBraid Default' in the upper left of my account page?">
  On qBraid, you can belong to multiple organizations (e.g., courses, teams, or your own qBraid Default workspace). Credits and context are per-organization. The name in the upper left shows which organization you're in, and switching it changes which credits and resources you see.

**qBraid Default** is your own workspace: your own credits and work, separate from any course or other org you've joined. Credits here are yours (purchased or held in your name), and you have full control with no shared management.

</Accordion>

<Accordion title="Why do I need to generate API keys to launch lab?">
  API keys authenticate you with qBraid services. When you launch Lab, we check
  for credentials in `~/.qbraid/qbraidrc`. If none are found, we prompt you to
  create an API key and save it there so Lab, extensions, and the qBraid-SDK
  work without extra setup. For more on creating and managing keys, see [API
  Keys](https://docs.qbraid.com/v2/account/api-keys).
</Accordion>

<Accordion title="I ran out of CPU hours and can't access my files. What do I do?">
  When you exhaust your CPU hours, "Launch Lab" is blocked. Your files remain
  available without launching Lab. Go to **Dashboard** on your [account
  page](https://account.qbraid.com/), scroll to **Usage Overview** at the
  bottom, and click **Download Files**. See [Download your
  files](https://docs.qbraid.com/v2/account/usage#download-your-files). To start launching again,
  either upgrade your plan or set up credits, as described in
  [Troubleshooting](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting#launch-failed-compute-hours-exhausted).
</Accordion>

<Accordion title="Can I submit quantum jobs to IBM devices through qBraid?">
  No. To run jobs on IBM devices you must use your own IBM credentials. qBraid
  does support direct access to other QPUs, including Rigetti, IQM, AQT,
  IonQ, Pasqal, QuEra, and more. See the [full list of
  devices](https://account.qbraid.com/devices) on your account page.
</Accordion>

</AccordionGroup>
