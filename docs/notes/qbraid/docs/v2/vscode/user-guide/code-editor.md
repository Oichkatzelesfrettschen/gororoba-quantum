> Full piece: [https://docs.qbraid.com/v2/vscode/user-guide/code-editor.md](https://docs.qbraid.com/v2/vscode/user-guide/code-editor.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c7380489c89974866013b704b9e00b2f9a83048ade35779bbc9bfe8c5e791232.

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

# qBraid VS Code

> Directly connect to an online VS Code environment with pre-installed quantum extensions.

## Overview

qBraid VS Code is a cloud-hosted deployment of Visual Studio Code, designed for quantum computing and available to all qBraid users. It offers a browser-based coding environment with direct access to quantum resources, pre-configured environments, and seamless integration with qBraid Lab. Users can develop, run, and manage quantum and classical code from anywhere, without the need for local setup or installation.

## How to Launch

<img
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/launch-vscode.gif"
  alt="vscode-launch"
  width="100%"
></img>

1. **Login to qBraid:**  
   Go to [qbraid.com](https://qbraid.com) and sign in with your account.

2. **Choose VS Code Instance:**  
   Navigate to the Dashboard section and select the VS Code option from your available compute environments. You will have an option to choose instances with varying resource allocations based on your needs.

3. **Launch:**  
   Click the "Launch New Instance" button to start your cloud VS Code session. The editor will open in your browser, ready to use with all quantum tools pre-installed.

## Features

<img
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/vscode-general.gif"
  alt="vscode-features"
  width="100%"
></img>

- **Quantum Console:**  
  Manage quantum jobs, devices, and providers (including IBM and qBraid) directly from the VS Code interface.

- **Environment Manager:**  
  Create, activate, and manage Python environments for quantum development, both locally and in the cloud.

- **Pre-configured Quantum Lab:**  
  Access Jupyter notebooks, quantum SDKs, and all necessary dependencies without manual setup.

- **Seamless Integration:**  
  Move between code, notebooks, and quantum resources with a unified experience, leveraging qBraid’s authentication and resource management.

qBraid VS Code streamlines quantum development, making it easy to start coding, experimenting, and running jobs on real quantum hardware — all
within the same environment.
