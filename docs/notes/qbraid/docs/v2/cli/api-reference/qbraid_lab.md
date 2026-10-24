> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_lab.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_lab.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d9a0f3cb4bae299211fd02ecbc74be7a1059a72b5642a8885864758a555ab1eb.

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

# qbraid lab

> Launch qBraid Lab (JupyterLab). Extra arguments are passed through.

Arguments are forwarded directly to jupyter-lab, with one exception:
`--help`/`-h` are consumed by the qbraid CLI and print this text. Use
`qbraid lab -- --help` for JupyterLab's own help.

Examples:

```bash
qbraid lab                           # launch with defaults

qbraid lab --port 9999 --no-browser  # custom port, no browser

qbraid lab --notebook-dir ~/projects # set working directory

qbraid lab --dev-mode --debug        # forwarded to jupyter-lab
```

**Usage**:

```console
$ qbraid lab [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.
