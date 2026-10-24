> Full piece: [https://docs.qbraid.com/v2/cli/user-guide/overview.md](https://docs.qbraid.com/v2/cli/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e12452948db3c32813c81e65a9314a047ed5f3953f362c084b1fbe251c02b613.

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
    src="/v2/cli/_static/cli_banner.png"
    alt="qBraid-CLI"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/cli/_static/cli_banner_dark.png"
    alt="qBraid-CLI"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _Universal command line interface for interacting with all parts of the qBraid
  platform._
</div>

The qBraid CLI manages cloud compute, quantum jobs, environments, and AI agents from your terminal. It can also route AI coding tools through qBraid as their provider, and send you Slack or email updates from long-running work.

## Getting started

The qBraid-CLI comes pre-installed and pre-configured in qBraid Lab:

- [Launch qBraid Lab &rarr;](https://lab.qbraid.com/)
- [Make an account &rarr;](https://account.qbraid.com/)

For help, see qBraid Lab User Guide: [Getting Started](https://docs.qbraid.com/v2/lab/user-guide/getting-started).

### Local setup

If you prefer to use qBraid-CLI on your local machine, you can install it from PyPI with:

```bash
pip install qbraid-cli
```

<Warning>
qbraid-cli versions &lt;0.12 are *not* compatible with qBraid API V2. See [migration guide](https://docs.qbraid.com/v2/api-reference/rest/migration).

Use qbraid-cli &ge; 0.12.0 with API V2.

</Warning>

To manage qBraid [environments](https://docs.qbraid.com/v2/lab/user-guide/environments) using the CLI, you must also install the `envs` extra:

```bash
pip install 'qbraid-cli[envs]'
```

To SSH into qBraid [compute instances](#manage-compute-instances) from your local machine, install the `compute` extra:

```bash
pip install 'qbraid-cli[compute]'
```

After installation, you must configure your account credentials to use the CLI locally:

1. Create a qBraid account or log in to your existing account by visiting
   [account.qbraid.com](https://account.qbraid.com/)
2. Open [API Keys](https://account.qbraid.com/account/api-keys) and create a key. See [API key management](https://docs.qbraid.com/v2/account/api-keys) for scope and rotation details.
3. Save your API key from step 2 in local configuration file `~/.qbraid/qbraidrc` using:

```bash
$ qbraid configure
```

### Add the CLI to PATH on Windows

If you encounter a warning like:

```bash
WARNING: The script qbraid.exe is installed in 'C:\Users\<YourUsername>\AppData\Local\Packages\PythonSoftwareFoundation.Python.<version>\LocalCache\local-packages\Python<version>\Scripts' which is not on PATH.
```

You need to add the directory containing qbraid.exe to your system's PATH.

1. Copy the directory path provided in the warning.
2. Follow these steps:

- Open the Start Menu, search for "Environment Variables," and select "Edit the system environment variables."
- In the System Properties window, click the Environment Variables button.
- Under "User variables," locate the Path variable, click Edit, and add the copied directory.

3. Save the changes and restart your terminal.

## Basic commands

```bash
$ qbraid
----------------------------------
  * Welcome to the qBraid CLI! *
----------------------------------

        ____            _     _
   __ _| __ ) _ __ __ _(_) __| |
  / _` |  _ \| '__/ _` | |/ _` |
 | (_| | |_) | | | (_| | | (_| |
  \__,_|____/|_|  \__,_|_|\__,_|
     |_|


- Use 'qbraid --help' to see available commands.

- Use 'qbraid --version' to see the current version.

Reference Docs: https://docs.qbraid.com/v2/cli/api-reference/qbraid
```

A qBraid CLI command has the following structure:

```bash
$ qbraid <command> <subcommand> [options and parameters]
```

To list installed environments:

```bash
$ qbraid envs list
```

To view help documentation, use one of the following:

```bash
$ qbraid --help
$ qbraid <command> --help
$ qbraid <command> <subcommand> --help
```

For example:

```bash
$ qbraid --help

Usage: qbraid [OPTIONS] COMMAND [ARGS]...

The qBraid CLI — A unified interface for AI agents, quantum computing,
Python environments, and cloud compute.

Commands
  lab           Launch qBraid Lab (JupyterLab).
  agents        Manage AI coding agent sessions.
  ai            Use qBraid as your AI provider.
  compute       Manage cloud compute and SSH.
  comms         Send updates and read replies.
  jobs          Submit and track quantum computing jobs.
  envs          Manage Python environments.
  ...
```

This is an excerpt. The [API reference](https://docs.qbraid.com/v2/cli/api-reference/qbraid) lists every command and option for the current release.

To get the version of the qBraid CLI:

```bash
$ qbraid --version
```

## Manage compute instances

Current CLI releases use `qbraid compute instances` for both subscription and on-demand compute:

```bash
qbraid compute instances list
qbraid compute instances availability
qbraid compute instances show subscription
```

Run `qbraid compute instances --help` for commands and `<command> --help` for their options, or see the [`qbraid compute` reference](https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute). The older `qbraid compute server` group is deprecated.
