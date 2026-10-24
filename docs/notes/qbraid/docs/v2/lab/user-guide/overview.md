> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/overview.md](https://docs.qbraid.com/v2/lab/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ca1b2db679e4d4023272d326cc70b83087b4e3d1088c214b245bf94c86c69e7b.

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

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/lab_banner.png"
    alt="qBraid-Lab"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/lab/_static/lab_banner_dark.png"
    alt="qBraid-Lab"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _A web-based IDE optimized for quantum computing._
</div>

[qBraid Lab](https://lab.qbraid.com/) is a web-based IDE providing curated software tools for researchers and developers in quantum computing.

- Hosts **30+** configurable virtual environments spanning quantum machine learning, quantum chemistry, quantum error correction, and more.
- Integrates with **GitHub**, **Slack**, and AI coding assistants like **Claude Code** and **Codex**.
- **Collaborative tools** enable sharing custom environments.
- Provides direct access to a robust suite of computing resources, encompassing scalable **CPUs**, **GPUs**, and **QPUs**.

## Operating System

qBraid offers several specialized Lab instances tailored to various applications and use cases. However, the
standard and most widely used qBraid Lab instance is built on [Ubuntu 22.04.4 LTS (Jammy Jellyfish)](https://releases.ubuntu.com/22.04/)
and utilizes an [x86_64](https://en.wikipedia.org/wiki/X86-64) architecture.

To discuss projects with specific system requirements, please [contact us](https://www.qbraid.com/contact).
