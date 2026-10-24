> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_projects.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_projects.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 4ad04ae02f4469c396107720b8223ffcd2a647123f24457fa20b24d56d188e30.

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

# qbraid projects

> Browse and install qBraid Hub projects.

Hub projects are GitHub-hosted templates with optional pre-configured
environments. Use 'qbraid projects install &lt;slug&gt;' to clone a project
and install its environments in one step.

**Usage**:

```console
$ qbraid projects [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List qBraid Hub projects.
- `get`: Get project metadata.
- `install`: Install a Hub project.

## qbraid projects list

List qBraid Hub projects.

**Usage**:

```console
$ qbraid projects list [OPTIONS]
```

**Options**:

- `-s, --search <str>`: Search query across title and description
- `-f, --featured`: Show only featured projects
- `-c, --category <str>`: Filter by category
- `-v, --visibility <str>`: Filter by visibility: 'public' or 'private'
- `--help`: Show this message and exit.

## qbraid projects get

Get project metadata.

Fetches metadata for a single qBraid Hub project.

**Usage**:

```console
$ qbraid projects get [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The slug of the project to fetch. [required]

**Options**:

- `--no-fmt`: Disable rich formatting (output raw data) [default: True]
- `--help`: Show this message and exit.

## qbraid projects install

Install a Hub project.

Clone the repo and install envs.
Automatically handles platform and Python version mismatches:

- Platform mismatch: creates a similar local environment instead
- Python mismatch + uv available: installs the required Python, then downloads
- Python mismatch + no uv: creates a similar local environment instead

**Usage**:

```console
$ qbraid projects install [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The slug of the project to install. [required]

**Options**:

- `-t, --target-dir <str>`: Directory to clone the project into (defaults to ~/).
- `--no-envs`: Skip installing the project's associated environments.
- `--help`: Show this message and exit.
