> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/kernels.md](https://docs.qbraid.com/v2/lab/user-guide/kernels.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 01131eaabf60f8ebb0a5e4261ae2ddab57fa14097fb0879d2ca7b890e5624498.

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

# Kernels

## Add and remove kernels

The IPython kernel is the Python execution backend for Jupyter.

Under **Environments**, choose an environment, and expand its panel. Click **Add kernel** to create an ipykernel for the environment.
This is a necessary step before running code in a Jupyter Notebook using a given environment.

Once "active", click **Remove kernel** to remove the environment's ipykernel from the launcher.

<Frame>
  <video
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/lab/add-remove-kernel.mp4"
    autoPlay
    muted
    loop
    playsInline
    width="100%"
  />
</Frame>
