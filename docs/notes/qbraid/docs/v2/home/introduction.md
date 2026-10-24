> Full piece: [https://docs.qbraid.com/v2/home/introduction.md](https://docs.qbraid.com/v2/home/introduction.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 322ff3ff3edeb35237c9e7c07e3ed3213fe453a968fe426bef0f7cce6387d3ad.

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

# qBraid Docs

> Guides and references for qBraid Account, quantum computing, Lab, and AI.

<CardGroup cols={3}>
    <Card
        title="ACCOUNT"
        icon="user"
        href="/v2/account/overview"
        iconType="duotone"
    >
    Manage credits, API keys, organizations, and more.
    </Card>
    <Card
        title="LAB"
        icon="flask"
        href="/v2/lab"
        iconType="duotone"
    >
    Web-based IDE optimized for quantum computing.
    </Card>
    <Card
        title="SDK"
        icon="python"
        href="/v2/sdk"
        iconType="duotone"
    >
    Platform-agnostic quantum runtime framework.
    </Card>
    <Card
        title="APIs"
        icon="code"
        href="/v2/api-reference"
        iconType="duotone"
    >
    Endpoints for submitting and managing quantum jobs.
    </Card>
    <Card
        title="CLI"
        icon="square-terminal"
        href="/v2/cli"
        iconType="duotone"
    >
    Command-line tool for interacting with the qBraid platform.
    </Card>
    <Card title="AI"
        icon="robot"
        href="/v2/ai"
        iconType="duotone"
    >
    AI-enabled quantum computing tools.
    </Card>
    <Card title="LEARN" icon="book-open" href="/v2/home/learning">
    Find courses in Account and open their chapters in qBook.
    </Card>
    <Card
        title="VS Code"
        icon="microsoft"
        href="/v2/vscode"
        iconType="duotone"
    >
    Quantum software extensions for code editors.
    </Card>
    <Card
        title="QIR"
        icon="cookie-bite"
        href="/v2/qir"
        iconType="duotone"
    >
    qBraid-SDK extension using an LLVM-based quantum compiler.
    </Card>
    <Card
        title="PyQASM"
        icon="bars-staggered"
        href="/v2/pyqasm"
        iconType="duotone"
    >
    Toolkit for OpenQASM program validation and compilation.
    </Card>
    <Card
        title="CORE"
        icon="server"
        href="/v2/core"
        iconType="duotone"
    >
    Low-level interface to qBraid cloud services.
    </Card>
    <Card
        title="ALGORITHMS"
        icon="network-wired"
        href="/v2/algorithms"
        iconType="duotone"
    >
    Library of quantum algorithm resources and tools.
    </Card>
    <Card
        title="PRICING"
        icon="file-invoice"
        href="/v2/home/pricing"
        iconType="duotone"
    >
    Compute resources and pricing for CPUs, GPUs, and QPUs.
    </Card>
</CardGroup>
