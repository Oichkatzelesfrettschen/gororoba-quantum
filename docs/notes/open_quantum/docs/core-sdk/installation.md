> Full piece: [https://docs.openquantum.com/core-sdk/installation/](https://docs.openquantum.com/core-sdk/installation/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f7dd5272638c3c2ca37e8c77d9fc1708272eb6d0ba3c0c4a32171c37bdd21c5d.

# Installation

## Prerequisites

- **Python**: Core SDK 3.8+; Qiskit plugin 3.9+; PennyLane plugin 3.10+; Cirq plugin 3.10+; Qrisp plugin 3.11–3.13 (Qrisp itself does not yet support 3.14); the [MCP server](https://docs.openquantum.com/mcp/installation/) 3.10+

## Install from PyPI

Open Quantum provides a core SDK with optional framework plugins. Install the one that matches your workflow:

[](#__codelineno-0-1)`pip`` ``install`` ``openquantum-sdk``                      ``# Core SDK only`\
[](#__codelineno-0-2)`pip`` ``install`` ``"openquantum-sdk[qiskit]"``            ``# Core SDK + Qiskit plugin`\
[](#__codelineno-0-3)`pip`` ``install`` ``"openquantum-sdk[pennylane]"``         ``# Core SDK + PennyLane plugin`\
[](#__codelineno-0-4)`pip`` ``install`` ``"openquantum-sdk[qiskit,pennylane]"``  ``# Core SDK + Qiskit and PennyLane`\
[](#__codelineno-0-5)`pip`` ``install`` ``"openquantum-sdk[cirq]"``              ``# Core SDK + Cirq plugin`\
[](#__codelineno-0-6)`pip`` ``install`` ``"openquantum-sdk[qrisp]"``             ``# Core SDK + Qrisp plugin`\
[](#__codelineno-0-7)`pip`` ``install`` ``openquantum-mcp``                      ``# MCP server for AI agents (pulls in openquantum-sdk)`\

Note

Every plugin automatically installs `openquantum-sdk` as a dependency, so you do not need to install the Core SDK separately. The MCP package also depends on it.

Package name vs import name

Each plugin extra installs under a different import name: `openquantum-sdk[qiskit]` imports as `openquantum_sdk_qiskit`, `openquantum-sdk[pennylane]` as `pennylane_openquantum`, `openquantum-sdk[cirq]` as `cirq_openquantum`, and `openquantum-sdk[qrisp]` as `qrisp_openquantum`.

Cirq and Qrisp are in beta

The Cirq and Qrisp plugins are currently in **beta**. They work end to end, but their APIs and defaults may still change. Feedback is welcome in the [Quantum Rings community](https://www.quantumrings.com/community).

Current package versions

Core, Qiskit, and PennyLane are **1.0.0**. Cirq and Qrisp are **0.5.0**. The MCP server is **0.2.0**. Plugins and the MCP server require `openquantum-sdk>=1.0.0`. Qrisp also requires `openquantum-sdk-qiskit>=1.0.0`. These numbers live in each package's `pyproject.toml` and `__version__`. There is no separate changelog. The verify commands below print the version you have installed.

## Verify Installation

### Core SDK

[](#__codelineno-1-1)`python`` ``-c`` ``"import openquantum_sdk; print(openquantum_sdk.__version__)"`\

### Qiskit Plugin

[](#__codelineno-2-1)`python`` ``-c`` ``"import openquantum_sdk_qiskit; print(openquantum_sdk_qiskit.__version__)"`\

### PennyLane Plugin

[](#__codelineno-3-1)`python`` ``-c`` ``"import pennylane_openquantum; print(pennylane_openquantum.__version__)"`\

You can verify that the plugin is installed and PennyLane recognizes it:

[](#__codelineno-4-1)`python`` ``-``c`` ``"from pennylane_openquantum import OpenQuantumDevice; print('Plugin OK')"`\

### Cirq Plugin

[](#__codelineno-5-1)`python`` ``-c`` ``"import cirq_openquantum; print(cirq_openquantum.__version__)"`\

### Qrisp Plugin

[](#__codelineno-6-1)`python`` ``-c`` ``"import qrisp_openquantum; print(qrisp_openquantum.__version__)"`\

Note

The PennyLane device requires authentication credentials at creation time. To create a device instance, you must first configure credentials via arguments or environment variables. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for setup instructions.

## Next Steps

- [Quick Start](https://docs.openquantum.com/core-sdk/quickstart/) -- Submit your first quantum job.
- [Authentication](https://docs.openquantum.com/core-sdk/authentication/) -- Set up your SDK key credentials.
- [AI Agents & MCP](https://docs.openquantum.com/mcp/overview/) -- Run jobs from Claude, Cursor, and other MCP clients.
