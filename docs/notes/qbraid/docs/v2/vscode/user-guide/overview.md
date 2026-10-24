> Full piece: [https://docs.qbraid.com/v2/vscode/user-guide/overview.md](https://docs.qbraid.com/v2/vscode/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 a255d53a3ad938cb03c4232f48e96fc0849a1b328d9a3761f54a0ea08fb8094d.

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

# Overview

> Get an overview of the qBraid VS Code extension pack and our custom VS Code deployment.

# qBraid and VS Code

<img
  src="/v2/vscode/_static/qbraid-vscode-logo.png"
  alt="qBraid VS Code Logo"
  width="100%"
  className="block dark:hidden"
/>
<img
  src="/v2/vscode/_static/qbraid-vscode-logo-dark.png"
  alt="qBraid VS Code Logo"
  width="100%"
  className="hidden dark:block"
/>
The qBraid VS Code Extension Pack brings together a curated set of extensions
designed to streamline quantum software development, device access, and
environment management—all within the familiar Visual Studio Code interface.
This pack is available for both local installations and as part of qBraid’s
custom, cloud-hosted VS Code deployment.

## Extension Packs

The extension pack includes:

- [**Quantum Console:**](https://docs.qbraid.com/v2/vscode/user-guide/quantum-console) Manage quantum jobs, devices, and providers like qBraid, and IBM directly from VS Code.
- [**Environment Manager:**](https://docs.qbraid.com/v2/vscode/user-guide/environment-manager) Easily switch between and manage Python environments, essential for quantum software development.

## VS Code Deployment

qBraid offers a custom deployment of Visual Studio Code, which provides:

- **Pre-installed Quantum Extensions:** All core qBraid extensions and dependencies are ready to use—no setup required.
- **Cloud-based Development:** Access your development environment from anywhere, with persistent storage and scalable compute resources.
- **Integrated Authentication:** Secure access to qBraid and IBM Quantum services, with easy API key management.
- **Consistent Experience:** Enjoy the same interface and features whether working locally or in the cloud.

Navigate to account [Lab Instances](https://account.qbraid.com/dashboard/lab-instances), choose **VS Code** as your IDE, select a compute profile, and launch.

## Local & Cloud Flexibility

The qBraid extension pack can be installed in your local VS Code or used directly within the custom cloud deployment. This ensures a consistent, powerful quantum development experience—no matter where you work.

Explore the following pages for detailed guides on each of our extensions and deployment features, including screenshots and step-by-step usage instructions.
