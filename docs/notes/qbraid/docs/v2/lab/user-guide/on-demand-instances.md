> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances.md](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 3e0b12fa8bd83ce84ab807ceb6cbc4cb38d187e4ed9dfac59b70f323684d08e6.

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

# On-Demand Instances

> Launch, manage, and understand the lifecycle of on-demand GPU and CPU instances on qBraid Lab.

On-demand instances provide GPUs and CPU configurations billed in credits. Choose an available profile and review its price before launching.

## Launching an instance

From your [dashboard](https://account.qbraid.com/dashboard), switch to the **On-Demand** tab to see available GPU and CPU profiles. Each profile shows its pricing in credits per minute and a capacity tag indicating current availability: **High**, **Medium**, or **Low**. Profiles tagged **No Capacity** cannot be launched until resources free up. A profile without a tag has no current capacity data.

Click **Launch** next to any available profile to start an instance.

<Frame>
  <img
    src="https://5iv4rqgitg.ufs.sh/f/75CeDcn3E50nz0uGWCPfD1sKE47iVhQXIZqWS6tfwP9yn8J2"
    alt="On-demand CPU and GPU profiles with credit rates, capacity labels, and the minimum-credit launch notice"
  />
</Frame>

The On-Demand tab shows each profile's rate and whether the current balance permits launch.

<Note>
  The default balance tiers allow up to 5 concurrent on-demand instances. Your
  account configuration can impose different limits. See
  [pricing](https://docs.qbraid.com/v2/home/pricing#gpu-instances) for how to check current rates.
</Note>

## Accessing your instance

Once an instance is running, it appears under your **My Instances** tab.

<img
  src="/v2/lab/_static/my-instances.png"
  alt="Running and stopped instances in My Instances"
/>

The instance row has two actions:

- Select the **Arrow icon** to open the instance in JupyterLab.
- Select the **Pencil (Edit) icon** to open the instance details and choose a browser connection:

  - **JupyterLab** opens notebooks for interactive computing.
  - **VS Code** provides an IDE with extensions and debugging.
  - **Terminal** provides shell access to the instance.

<img
  src="/v2/lab/_static/launch-options.png"
  alt="JupyterLab, VS Code, and terminal connection options"
/>

You can also connect to running instances remotely via SSH using the [qBraid CLI](https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute).

## Instance lifecycle

On-demand instances have three states you control: **Running**, **Stopped**, and **Terminated**.

```
Launch → Running → Stop → Stopped → Resume → Running
                      │                  │
                      └── Terminate ◄────┘
```

### Running

Your instance is active and accessible. Compute is billed at the credits-per-minute rate shown on the instance tile. Storage is billed separately based on retained disk capacity and the applicable per-GB-hour rate.

### Stopped

Stopping releases compute and preserves your instance's disk, including files and installed packages. Storage charges continue while the instance is stopped. The rate is per GB-hour and depends on the retained disk capacity.

You can resume a stopped instance at any time. When you do, your files will be exactly as you left them.

### Terminated

The instance and its disk are **permanently deleted**. All files on the instance are lost and cannot be recovered. Billing stops completely.

## Stop vs terminate

|                  | Stop                            | Terminate                       |
| :--------------- | :------------------------------ | :------------------------------ |
| **Compute**      | Released (no compute charges)   | Deleted                         |
| **Disk / Files** | Preserved                       | Permanently deleted             |
| **Billing**      | Storage billed per GB-hour of retained disk | No further charges              |
| **Resumable**    | Yes; resume anytime            | No; launch a new instance |

Stop the instance when you want to return to the same environment later. Your files, packages, and configuration stay intact.

Terminate the instance when you are done and do not need its data. Terminating frees the storage slot and stops all billing.

<Note>
  Some instance types only support termination. Stop and resume are unavailable.
  For these instances, the Stop button will not appear; only Terminate is shown.
</Note>

<img
  src="/v2/lab/_static/terminate-instance.png"
  alt="Instance termination confirmation"
/>

<Warning>
  Terminating an instance permanently deletes all files on it. Download or
  export any important work before terminating. When the provider supports it,
  **stop** the instance to keep its disk for resumption.
</Warning>

## File persistence

On-demand instances handle files differently from subscription instances:

- On-demand instances do not sync files from cloud storage at launch. Each instance has its own disk.
- Use the **Files** tab to download files from cloud storage into an instance. Changes do not sync back to cloud storage.
- Stopping preserves the disk. Your files remain available when you resume.
- Terminating permanently deletes the disk and all its files.

<Tip>
  If you're working on important files in an on-demand instance, download them
  to your local machine or push them to a Git repository before terminating.
</Tip>

## Billing

On-demand instances are billed per minute in [qBraid credits](https://docs.qbraid.com/v2/home/pricing#credits) (100 credits = $1 USD).

| State      | What you are charged                   |
| ---------- | -------------------------------------- |
| Running    | The displayed compute and storage rate |
| Stopped    | Storage for the retained disk          |
| Terminated | No further instance charges            |

Compute rates vary by instance type. See [pricing](https://docs.qbraid.com/v2/home/pricing#gpu-instances) for how to check current rates. Storage charges depend on retained disk capacity and the applicable rate. Check the instance details instead of assuming a fixed storage price.

The default credit-balance tiers determine how many instances you can provision or resume:

| Credit Balance        | Concurrent Instances |
| :-------------------- | :------------------- |
| 100+ credits ($1+)    | 1                    |
| 1,000+ credits ($10+) | 2                    |
| 2,500+ credits ($25+) | 5                    |

An administrator can configure different thresholds or a lower cap. Stopped instances do not use running slots, but still count toward the total instance limit. A balance drop does not immediately remove an already-running instance; continued operation depends on payment renewal.

## Manage instances from the CLI

The current CLI provides the same lifecycle through `qbraid compute instances`:

```bash
qbraid compute instances list
qbraid compute instances availability
qbraid compute instances show INSTANCE_ID
```

Run `qbraid compute instances --help` to find launch, resume, stop, terminate, and SSH commands for your installed version.
