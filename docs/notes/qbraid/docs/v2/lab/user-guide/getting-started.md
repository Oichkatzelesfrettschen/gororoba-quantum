> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/getting-started.md](https://docs.qbraid.com/v2/lab/user-guide/getting-started.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 dd5cc61167e4f6f7b46427973f067b7ea24ef427e1250326d63c9674e625a8a5.

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

# Getting Started

> This section will walk you through the basics of using the Lab interface and managing your server instance.

## Launch Lab

### Starting an Instance

From your [account page](https://account.qbraid.com/), select a compute profile and click **Launch** to start your quantum environment.

qBraid Lab offers two types of instances:

- **Subscription instances** (CPU): Included with your plan, billed against your monthly compute hours. Available in Small (2 vCPU), Medium (4 vCPU), and Large (8 vCPU) configurations. Your files are automatically synced from cloud storage on each launch.
- **On-demand instances** (GPU + high-spec CPU): Pay-as-you-go with [qBraid credits](https://docs.qbraid.com/v2/home/pricing#credits), billed per minute. Includes 20+ GPU configurations and high-spec CPU instances. See [On-Demand Instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances) for the full lifecycle guide.

[Paid subscription tiers](https://www.qbraid.com/pricing) provide additional benefits including higher disk storage limits and compute hours.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/lab/launch-lab-part-1.gif"
    alt="launch_lab_new_account"
    width="150%"
  ></img>
</div>

Depending on its size, pulling an image may take up to 2 minutes for the first time. The next time you launch Lab, it will load much more quickly.

<Note>
  If launching fails with `Compute hours exhausted and insufficient credits`,
  you've used your monthly compute hour allocation. See
  [Troubleshooting](https://docs.qbraid.com/v2/lab/user-guide/troubleshooting#launch-failed-compute-hours-exhausted)
  for how to upgrade your plan or switch the session over to credits.
</Note>

### Stopping Lab

To stop your running Lab instance:

1. Navigate to your [account dashboard](https://account.qbraid.com/)
2. Click **Stop Running Server** to stop the running instance

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/lab/stop-lab.gif"
    alt="stop_lab_new_account"
    width="150%"
  ></img>
</div>

Stopping your server will not delete your data, but will stop it from running and consuming compute hours.

<Note>
  On-demand instances (GPUs, high-spec CPUs) have an additional **Terminate**
  action that permanently deletes the instance and its disk. See [On-Demand
  Instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances#stop-vs-terminate) for
  details on the stop vs terminate distinction.
</Note>

## Lab interface

Once your image is pulled, you will be taken to the qBraid Lab interface. Here are a few helpful resources to get started:

- **Interactive tour**: Click **Start Tour** (pop-up at first launch, or **Help** drop-down) to begin a guided tour of all of the Lab extensions and their key features.
- **Help drop-down**: The top-bar menu **Help** drop-down contains links to qBraid user guides, demos, and other reference materials.
