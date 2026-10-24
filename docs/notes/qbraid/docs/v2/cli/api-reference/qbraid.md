> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 349093983774f31c5b3406d3ef5e92163f93a8f8f842a3ac2d253652ddc14724.

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

# qbraid

> The qBraid CLI — A unified interface for AI agents, quantum computing, Python environments, and cloud compute.

Version: [0.16.16](https://pypi.org/project/qbraid-cli/0.16.16)

Whether you're running AI coding agents locally or on cloud servers,
managing quantum experiments across providers, or setting up reproducible
Python environments — qBraid brings it all into one CLI.

**Usage**:

```console
$ qbraid [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `-v, --version`: Show the version and exit.
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `lab`: Launch qBraid Lab (JupyterLab).
- `admin`: CI/CD commands for qBraid maintainers.
- `agents`: Manage AI coding agent sessions.
- `ai`: Use qBraid as your AI provider.
- `compute`: Manage cloud compute and SSH.
- `comms`: Send updates and read replies.
- `configure`: Configure CLI settings.
- `account`: Manage qBraid account.
- `devices`: Browse quantum devices.
- `jobs`: Submit and track quantum computing jobs.
- `projects`: Browse and install qBraid Hub projects.
- `skills`: Create, install, and share AI coding skills.
- `troubleshoot`: Diagnose qBraid platform issues.
- `envs`: Manage Python environments.
- `kernels`: Add, remove, and repair Jupyter kernels.
- `pip`: Run pip command in active qBraid environment.
