> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/gpus.md](https://docs.qbraid.com/v2/lab/user-guide/gpus.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 fdba290ab57da95206a884e4feeae1505f014f251c6c649837e549fe413dc510.

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

# GPUs

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/gpu_nvidia_banner.png"
    width="150%"
    className="block dark:hidden"
  />
  <img
    src="/v2/lab/_static/gpu_nvidia_banner_dark.png"
    width="150%"
    className="hidden dark:block"
  />
</div>

qBraid Lab GPU instances support accelerated circuit simulation and quantum machine learning, including GPU-based quantum gradients.

## Available GPU configurations

qBraid offers NVIDIA GPU instances with Blackwell, Hopper, Ampere, and Ada Lovelace architectures:

- NVIDIA B200 (Blackwell) is available in 1x, 2x, 4x, and 8x configurations.
- NVIDIA H200 and H100 (Hopper) are available in configurations up to 8x for large workloads.
- NVIDIA GH200 (Grace Hopper) combines CPU and GPU hardware in a superchip.
- NVIDIA A100 (Ampere) is available in configurations up to 8x.
- NVIDIA L4, L40S, RTX 4090, RTX 5090, and RTX 6000 Ada provide lower-cost options for development and inference.

Billing is in credits/minute with rates shown in your account launcher. See [GPU pricing](https://docs.qbraid.com/v2/home/pricing#gpu-instances) for how to check current rates.

## Launch a GPU instance

From your [account dashboard](https://account.qbraid.com/dashboard), switch to the **On-Demand** tab. Each GPU profile shows its per-minute credit rate and a real-time availability indicator. Click **Launch** next to an available profile to start the instance.

<img src="/v2/lab/_static/gpu-instances.png" alt="GPU instance profiles in the on-demand launcher" />

<Note>
  GPU instances may take a few minutes to provision as resources are allocated
  on-demand.
</Note>

Once the instance is running, you can open it in JupyterLab, VS Code, or connect via the built-in terminal, all from the browser. See [Accessing Your Instance](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances#accessing-your-instance) for details.

## Managing GPU instances

GPU instances follow the on-demand lifecycle. Stop and resume are available only when the provider can preserve the instance disk:

- **Stop** pauses compute billing and preserves your disk and files for resumption.
- **Terminate** permanently deletes the instance and its data, ending all billing.

See [On-Demand Instances](https://docs.qbraid.com/v2/lab/user-guide/on-demand-instances) for the complete lifecycle guide, including file persistence, billing details, and concurrent instance limits.

## GPU utilities

Inspect your GPU hardware with the
[NVIDIA System Management Interface](https://developer.nvidia.com/nvidia-system-management-interface) (`nvidia-smi`) and
[NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) (`nvcc`) command line utilities.

<Note>
  Visit your [account page](https://account.qbraid.com/dashboard) to see the
  full list of GPU options including real-time availability.
</Note>
