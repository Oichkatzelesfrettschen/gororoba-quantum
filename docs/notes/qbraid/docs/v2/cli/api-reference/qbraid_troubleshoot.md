> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_troubleshoot.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_troubleshoot.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 a8fb722e3480201cd2a2b0a68a5be1a615b98966d3b60889183bf03d962ba023.

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

# qbraid troubleshoot

> Diagnose qBraid platform issues.

Diagnose and troubleshoot qBraid platform issues.
Runs automated checks on authentication, configuration,
network connectivity, JupyterLab integration, environments,
and system compatibility.

Use this when you want to:

- Debug authentication or connectivity issues
- Verify JupyterLab extension setup
- Check environment health
- Generate a bug report for support

**Usage**:

```console
$ qbraid troubleshoot [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--auth`: Run authentication checks only
- `--config`: Run configuration checks only
- `--network`: Run network checks only
- `--jlab`: Run JupyterLab checks only
- `--envs`: Run environment checks only
- `--system`: Run system checks only
- `-v, --verbose`: Show detailed output including per-environment checks
- `--export`: Export diagnostic report as JSON
- `--report`: Open a GitHub issue with diagnostic results
- `--help`: Show this message and exit.
