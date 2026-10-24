> Full piece: [https://docs.qbraid.com/v2/cli/user-guide/config-files.md](https://docs.qbraid.com/v2/cli/user-guide/config-files.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 ced0510265f787067c86e2791001ea84976648da79c8fcae14c086ba3eefe25e.

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

# Configuration Files

> Manage your qBraid account credentials and settings

qBraid uses configuration files to store your account credentials and settings. The main configuration file is called `qbraidrc`.

## The qbraidrc file

The `qbraidrc` file is an INI-format configuration file that stores your qBraid account credentials and settings. It is located in your home directory at:

- Linux/macOS: `~/.qbraid/qbraidrc`
- Windows: `C:\Users\<username>\.qbraid\qbraidrc`

These qBraid tools use the configuration file:

- qBraid-SDK
- qBraid-CLI
- qBraid Jupyter Lab extensions
- qBraid VS Code extensions

### File structure

A typical `qbraidrc` file contains the following:

```ini
[default]
url = https://api-v2.qbraid.com/api/v1
api-key = <your-api-key>
```

### Creating new configuration file

To create a new `qbraidrc` file:

```
qbraid configure
```

This interactive command:

1. Prompts you to enter your API key
2. Sets the qBraid API URL
3. Creates the configuration file in the correct location

### Updating configuration values

To update a specific configuration value:

```
qbraid configure set <field> <value>
```

For example, to update your API key:

```
qbraid configure set api-key your-new-api-key
```

### Viewing configuration values

To view a specific configuration value:

```
qbraid configure get <field>
```

For example:

```
qbraid configure get api-key
```

To view all configuration values in your default profile:

```
qbraid configure list
```

### Finding your configuration file

To locate your `qbraidrc` file programmatically:

```python
from pathlib import Path

config_path = Path.home() / ".qbraid" / "qbraidrc"

print(config_path)
```

## Security note

Your API key provides access to your qBraid account. Keep it secure and never share it with others. If you believe your API key has been compromised, you can generate a new one from your qBraid account settings and update it using the CLI commands above.

See [API key security](https://docs.qbraid.com/v2/account/api-keys#rotate-a-key) for more information.
