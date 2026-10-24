> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_kernels.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_kernels.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 93bd3685ee52e958cc9b69b476049a5158fc07df51859b2d77e6f23ee3597b14.

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

# qbraid kernels

> Add, remove, and repair Jupyter kernels.

Manage Jupyter kernel specs for qBraid environments. Each environment
can have its own kernel visible in JupyterLab's launcher.

Use this when you want to:

- Make an environment available as a Jupyter kernel
- Fix a broken kernel that points to a missing environment
- Clean up orphaned kernels from deleted environments

**Usage**:

```console
$ qbraid kernels [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List all available kernels.
- `add`: Add a kernel to Jupyter.
- `remove`: Remove a kernel from Jupyter.
- `status`: Check kernel status for an environment.
- `repair`: Repair a kernel's Python path.
- `clean`: Remove orphaned kernels.

## qbraid kernels list

List all available kernels.

**Usage**:

```console
$ qbraid kernels list [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid kernels add

Add a kernel to Jupyter.

**Usage**:

```console
$ qbraid kernels add [OPTIONS] {environment}
```

**Arguments**:

- `environment`: Name of environment for which to add ipykernel. Values from 'qbraid envs list'. [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid kernels remove

Remove a kernel from Jupyter.

**Usage**:

```console
$ qbraid kernels remove [OPTIONS] {environment}
```

**Arguments**:

- `environment`: Name of environment for which to remove ipykernel. Values from 'qbraid envs list'. [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid kernels status

Check kernel status for an environment.

**Usage**:

```console
$ qbraid kernels status [OPTIONS] {environment}
```

**Arguments**:

- `environment`: Environment name or env_id to check kernel status. [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid kernels repair

Repair a kernel's Python path.

Fixes kernel.json with the correct Python path.

**Usage**:

```console
$ qbraid kernels repair [OPTIONS] {environment}
```

**Arguments**:

- `environment`: Environment name or env_id to repair kernel. [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid kernels clean

Remove orphaned kernels.

Removes kernels whose Python environment no longer exists.
Without arguments, scans all kernels and prompts to remove broken ones.
With a kernel name, removes it directly without checking validity.

**Usage**:

```console
$ qbraid kernels clean [OPTIONS] [slug]
```

**Arguments**:

- `slug`: Kernel name to remove directly (no validation check).

**Options**:

- `-y, --yes`: Skip confirmation prompt
- `--help`: Show this message and exit.
