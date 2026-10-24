> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_envs.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_envs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 7f7d69f069fe84ca68947c5e9ac02d30c5d537f1591cf342c347ffdd1df15bd3.

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

# qbraid envs

> Manage Python environments.

Create, install, upload, and share Python environments.
Isolated Python environments with automatic Jupyter kernel integration.
Create environments locally, upload them to the cloud, share with
teammates, or install pre-built environments from the catalog. Works
identically on qBraid Lab and local machines.

Use this when you want to:

- Set up a reproducible Python environment for a project
- Share your environment with collaborators
- Install a pre-configured environment (e.g., qBraid SDK, Qiskit)
- Publish an environment to the public catalog

Quick start:

```bash
qbraid envs create             # Create new environment
qbraid envs available          # Browse installable environments
qbraid envs install <slug>     # Install from cloud
qbraid envs list               # List local environments
qbraid envs upload <name>      # Upload to cloud
```

**Usage**:

```console
$ qbraid envs [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `create`: Create a new qBraid environment.
- `uninstall`: Remove a local environment.
- `delete`: (Admin) Delete a cloud environment.
- `list`: List installed qBraid environments.
- `activate`: Activate qBraid environment.
- `available`: List installable environments.
- `info`: Show environment details.
- `install`: Install an environment.
- `upload`: Upload an environment.
- `health`: Check the health of an environment.
- `repair`: Repair a broken environment.
- `pythons`: List available Python versions.
- `config`: View or update environment configuration.
- `publish`: Manage environment publishing.
- `share`: Manage environment sharing via share codes.
- `groups`: Manage environment groups.
- `registry`: Manage the local environment registry.

## qbraid envs create

Create a new qBraid environment.

Run without options for an interactive walkthrough, or provide options via flags.

**Usage**:

```console
$ qbraid envs create [OPTIONS]
```

**Options**:

- `-n, --name <str>`: Name of the environment to create
- `-d, --description <str>`: Short description of the environment
- `-l, --logo <str>`: Company name for logo (e.g., 'ibm', 'google')
- `-r, --requirements <str>`: Path to requirements.txt file
- `-k, --kernel-name <str>`: Display name for Jupyter kernel
- `-t, --tags <str>`: Comma-separated tags
- `-y, --yes`: Automatically answer 'yes' to all prompts
- `--help`: Show this message and exit.

## qbraid envs uninstall

Remove a local environment.

By default this removes only the local copy — the cloud environment is
preserved so you can reinstall it later. Pass `--delete-cloud` to also
retire the cloud environment (requires ownership).

**Usage**:

```console
$ qbraid envs uninstall [OPTIONS]
```

**Options**:

- `-n, --name <str>`: Name of the environment to remove [required]
- `-c, --delete-cloud`: Also delete the environment from qBraid cloud (requires ownership). By default only the local copy is removed and the cloud slug is preserved, so you can reinstall it later.
- `-y, --yes`: Automatically answer 'yes' to all prompts
- `--help`: Show this message and exit.

## qbraid envs delete

(Admin) Delete a cloud environment.

Removes the DB entry and storage files.

**Usage**:

```console
$ qbraid envs delete [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Slug of the cloud environment to delete [required]

**Options**:

- `-y, --yes`: Automatically answer 'yes' to all prompts
- `--help`: Show this message and exit.

## qbraid envs list

List installed qBraid environments.

**Usage**:

```console
$ qbraid envs list [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid envs activate

Activate qBraid environment.

NOTE: Currently only works on qBraid Lab platform, and select few other OS types.

**Usage**:

```console
$ qbraid envs activate [OPTIONS] {name}
```

**Arguments**:

- `name`: Name of the environment. Values from 'qbraid envs list'. [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid envs available

List installable environments.

Shows available pre-built environments for installation.

**Usage**:

```console
$ qbraid envs available [OPTIONS]
```

**Options**:

- `-p, --page <int>`: Page number for pagination (default: 1)
- `-l, --limit <int>`: Number of environments per page (default: 20)
- `--help`: Show this message and exit.

## qbraid envs info

Show environment details.

Get detailed information about an environment.
Accepts either a local env_id or a cloud slug. Shows information from
both local registry and cloud catalog when available.

Examples:

```bash
$ qbraid envs info qiskit_1.0       # By slug (cloud + local if installed)
$ qbraid envs info a1b2             # By env_id (local only)
$ qbraid envs info my_custom_abc123 # Custom environment
```

**Usage**:

```console
$ qbraid envs info [OPTIONS] {identifier}
```

**Arguments**:

- `identifier`: Environment identifier (env_id or slug) [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid envs install

Install an environment.

Installs a pre-built environment from cloud storage.
If the environment was built for a different platform or requires a Python
version not available on your system, you'll be offered options to either
create a similar local environment or proceed with the download anyway.

**Usage**:

```console
$ qbraid envs install [OPTIONS] {env_slug}
```

**Arguments**:

- `env_slug`: Environment slug to install (from 'qbraid envs available') [required]

**Options**:

- `-t, --temp`: Install as temporary environment (faster, non-persistent)
- `--target <str>`: Custom target directory (defaults to ~/.qbraid/environments)
- `-y, --yes`: Automatically proceed with default options without prompting
- `--help`: Show this message and exit.

## qbraid envs upload

Upload an environment.

Upload environment to qBraid cloud storage (private by default).
This uploads your local environment to make it available for sharing
with specific users. Use 'qbraid envs publish request' after upload to request
public visibility.

Examples:

```bash
$ qbraid envs upload my_custom_env
$ qbraid envs upload a1b2 --overwrite
$ qbraid envs upload my_env --group quantum_sdk
$ qbraid envs upload my_env --slug existing_slug_abc123  # Re-upload
```

**Usage**:

```console
$ qbraid envs upload [OPTIONS] {identifier}
```

**Arguments**:

- `identifier`: Environment name (if unique) or env_id to upload [required]

**Options**:

- `-s, --slug <str>`: Re-upload to existing slug (replaces previous upload)
- `-g, --group <str>`: Environment group to add this environment to
- `-o, --overwrite`: Overwrite existing uploaded environment
- `-y, --yes`: Skip confirmation prompts
- `--help`: Show this message and exit.

## qbraid envs health

Check the health of an environment.

This performs comprehensive checks on the virtual environment:

- Python symlinks and executables
- pyvenv.cfg configuration
- Activate scripts
- Kernel configuration (if present)

Examples:

```bash
$ qbraid envs health my_env
$ qbraid envs health a1b2
```

**Usage**:

```console
$ qbraid envs health [OPTIONS] {identifier}
```

**Arguments**:

- `identifier`: Environment name or env_id to check [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid envs repair

Repair a broken environment.

This attempts to fix common issues:

- Broken Python symlinks
- Invalid pyvenv.cfg paths
- Broken activate scripts
- Invalid kernel.json paths

Use --auto-install to automatically install Python via uv if the
required version is not available.

Examples:

```bash
$ qbraid envs repair my_env
$ qbraid envs repair a1b2 --auto-install
```

**Usage**:

```console
$ qbraid envs repair [OPTIONS] {identifier}
```

**Arguments**:

- `identifier`: Environment name or env_id to repair [required]

**Options**:

- `-a, --auto-install`: Automatically install Python via uv if needed
- `--help`: Show this message and exit.

## qbraid envs pythons

List available Python versions.

Shows all Python installations found on the system, including:

- System Python (PATH)
- uv-managed Python
- Conda environments
- Homebrew (macOS)
- pyenv installations

Use this to see which Python versions are available for creating
new environments.

Examples:

```bash
$ qbraid envs pythons
```

**Usage**:

```console
$ qbraid envs pythons [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid envs config

View or update environment configuration.

Without flags, prints the current config. With flags, applies the updates
and prints the new state. Multiple update flags can be combined in one call.

Examples:

```bash
$ qbraid envs config 5dcc
$ qbraid envs config myenv --description "Quantum sim env"
$ qbraid envs config myenv --tags "quantum,sim,gpu"
$ qbraid envs config myenv --add-tag gpu --add-tag cuda
$ qbraid envs config myenv --remove-tag deprecated
$ qbraid envs config myenv --system-site-packages true
```

**Usage**:

```console
$ qbraid envs config [OPTIONS] {environment}
```

**Arguments**:

- `environment`: Environment name, env_id, or slug [required]

**Options**:

- `-d, --description <str>`: Update environment description
- `--tags <str>`: Replace tags (comma-separated, use '' to clear)
- `--add-tag <str>`: Append a tag (repeatable)
- `--remove-tag <str>`: Remove a tag (repeatable)
- `--kernel-name <str>`: Update Jupyter kernel display name
- `--system-site-packages <str>`: Enable/disable inheriting packages from parent Python (true/false)
- `--help`: Show this message and exit.

## qbraid envs publish

Manage environment publishing.

**Usage**:

```console
$ qbraid envs publish [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `request`: Request to publish environment.
- `status`: Check publish status.
- `cancel`: Cancel a pending publish request.
- `review`: (Admin) Mark as under review.
- `approve`: (Admin) Approve and publish.
- `deny`: (Admin) Deny a publish request.

### qbraid envs publish request

Request to publish environment.

Submits your uploaded environment to the public catalog for admin review. Once approved,
it will be publicly visible and installable by all users.

The environment must be uploaded first with 'qbraid envs upload'.

Examples:

```bash
$ qbraid envs publish request my_env_abc123
```

**Usage**:

```console
$ qbraid envs publish request [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug (from upload) [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs publish status

Check publish status.

Check the publishing status of an environment.
Status values:

    - none: Not submitted for publishing
    - requested: Waiting for admin review
    - pending: Under admin review
    - approved: Published to public catalog
    - denied: Publish request was denied

Examples:

```bash
$ qbraid envs publish status my_env_abc123
```

**Usage**:

```console
$ qbraid envs publish status [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to check [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs publish cancel

Cancel a pending publish request.

This withdraws your publish request before it's approved.
You can resubmit later with 'qbraid envs publish request'.

Examples:

```bash
$ qbraid envs publish cancel my_env_abc123
```

**Usage**:

```console
$ qbraid envs publish cancel [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs publish review

(Admin) Mark as under review.

Transitions the environment from 'requested' to 'pending' status,
indicating an admin is actively reviewing it.

Examples:

```bash
$ qbraid envs publish review my_env_abc123
```

**Usage**:

```console
$ qbraid envs publish review [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to review [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs publish approve

(Admin) Approve and publish.

Approve and publish an environment to the public catalog.
This makes the environment publicly visible and installable by all users.
After approval, you'll be prompted to add the environment to a group
if it's not already in one.

Examples:

```bash
$ qbraid envs publish approve my_env_abc123
$ qbraid envs publish approve my_env_abc123 --group qiskit
$ qbraid envs publish approve my_env_abc123 --no-group
```

**Usage**:

```console
$ qbraid envs publish approve [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to approve [required]

**Options**:

- `-g, --group <str>`: Add environment to this group after approval
- `--no-group`: Skip the group assignment prompt
- `--help`: Show this message and exit.

### qbraid envs publish deny

(Admin) Deny a publish request.

The owner will be notified with the denial reason.

Examples:

```bash
$ qbraid envs publish deny my_env_abc123
$ qbraid envs publish deny my_env_abc123 --message "Missing documentation"
```

**Usage**:

```console
$ qbraid envs publish deny [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to deny [required]

**Options**:

- `-m, --message <str>`: Reason for denial (sent to owner)
- `--help`: Show this message and exit.

## qbraid envs share

Manage environment sharing via share codes.

**Usage**:

```console
$ qbraid envs share [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List users with access.
- `create-code`: Generate a share code.
- `delete-code`: Delete the share code for an environment.
- `redeem-code`: Redeem a share code.

### qbraid envs share list

List users with access.

Shows all users with read or write access to the specified environment.

Examples:

```bash
$ qbraid envs share list my_env_abc123
```

**Usage**:

```console
$ qbraid envs share list [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to check [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs share create-code

Generate a share code.

Creates an 8-character code that others can redeem with
'qbraid envs share redeem-code' to gain read access to your environment.
Only the owner can generate codes.

Generating a new code invalidates any previous code for this environment.

Examples:

```bash
$ qbraid envs share create-code my_env_abc123
Share code: ABC12XYZ

# Share the code with collaborators, they can redeem it with:
$ qbraid envs share redeem-code ABC12XYZ
```

**Usage**:

```console
$ qbraid envs share create-code [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to generate share code for [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs share delete-code

Delete the share code for an environment.

Removes the share code, preventing new users from redeeming it.
Users who have already redeemed the code keep their access.

Examples:

```bash
$ qbraid envs share delete-code my_env_abc123
```

**Usage**:

```console
$ qbraid envs share delete-code [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Environment slug to delete share code for [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs share redeem-code

Redeem a share code.

Redeem a share code to gain access to an environment.
Enter a share code received from an environment owner to gain read access.
The code is case-insensitive.

Examples:

```bash
$ qbraid envs share redeem-code ABC12XYZ
Access granted to: My Environment (my_env_abc123)

# After redeeming, you can install the environment:
$ qbraid envs install my_env_abc123
```

**Usage**:

```console
$ qbraid envs share redeem-code [OPTIONS] {code}
```

**Arguments**:

- `code`: Share code to redeem [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid envs groups

Manage environment groups.

**Usage**:

```console
$ qbraid envs groups [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List all environment groups.
- `info`: Show environment group details.
- `create`: (Admin) Create a new environment group.
- `update`: (Admin) Update an environment group.
- `delete`: (Admin) Delete an environment group.

### qbraid envs groups list

List all environment groups.

Environment groups are collections of related environments. Use the group
slug when uploading an environment to add it to a group.

Examples:

```bash
$ qbraid envs groups list
```

**Usage**:

```console
$ qbraid envs groups list [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

### qbraid envs groups info

Show environment group details.

Examples:

```bash
$ qbraid envs groups info quantum_sdk
```

**Usage**:

```console
$ qbraid envs groups info [OPTIONS] {group_slug}
```

**Arguments**:

- `group_slug`: Group slug to get details for [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid envs groups create

(Admin) Create a new environment group.

Environment groups are collections of related environments, typically
different versions of the same package or tool.

Examples:

```bash
$ qbraid envs groups create "Qiskit" --description "IBM Qiskit environments"
$ qbraid envs groups create "Cirq" --category package --visibility public
$ qbraid envs groups create "PennyLane" --envs "pen_1x0,pen_0x9" --latest pen_1x0
```

**Usage**:

```console
$ qbraid envs groups create [OPTIONS] {display_name}
```

**Arguments**:

- `display_name`: Display name for the group (1-100 chars) [required]

**Options**:

- `-d, --description <str>`: Group description (max 500 chars)
- `-t, --tags <str>`: Comma-separated tags
- `-c, --category <str>`: Category: 'package' or 'subject-matter'
- `-v, --visibility <str>`: Visibility: 'private' or 'public'
- `-e, --envs <str>`: Comma-separated environment slugs to include
- `-l, --latest <str>`: Environment slug to set as the current version
- `--help`: Show this message and exit.

### qbraid envs groups update

(Admin) Update an environment group.

Use --add and --remove for delta updates to the environment list.
Use --latest to set which environment is the &quot;current&quot; version.

Examples:

```bash
$ qbraid envs groups update qiskit --add qiskit_1x0abc --latest qiskit_1x0abc
$ qbraid envs groups update cirq --remove cirq_0x8xyz,cirq_0x7def
$ qbraid envs groups update pennylane --name "PennyLane SDK" --visibility public
```

**Usage**:

```console
$ qbraid envs groups update [OPTIONS] {group_slug}
```

**Arguments**:

- `group_slug`: Slug of the group to update [required]

**Options**:

- `-n, --name <str>`: New display name
- `-d, --description <str>`: New description
- `-a, --add <str>`: Comma-separated environment slugs to add
- `-r, --remove <str>`: Comma-separated environment slugs to remove
- `-l, --latest <str>`: Set the current version environment slug
- `-c, --category <str>`: Category: 'package' or 'subject-matter'
- `-v, --visibility <str>`: Visibility: 'private' or 'public'
- `--help`: Show this message and exit.

### qbraid envs groups delete

(Admin) Delete an environment group.

This removes the group but does not delete the environments in it.

Examples:

```bash
$ qbraid envs groups delete old_group
$ qbraid envs groups delete old_group --yes
```

**Usage**:

```console
$ qbraid envs groups delete [OPTIONS] {group_slug}
```

**Arguments**:

- `group_slug`: Slug of the group to delete [required]

**Options**:

- `-y, --yes`: Skip confirmation prompt
- `--help`: Show this message and exit.

## qbraid envs registry

Manage the local environment registry.

**Usage**:

```console
$ qbraid envs registry [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `add`: Register an external environment.
- `remove`: Unregister an external environment.
- `sync`: Sync the environment registry.

### qbraid envs registry add

Register an external environment.

Allows you to use existing Python environments (conda, venv, etc.)
with qBraid commands like kernel management and activation.

Examples:

```bash
$ qbraid envs registry add /path/to/my_env --alias myenv
$ qbraid envs registry add ~/conda/envs/quantum --name quantum_abc123
```

**Usage**:

```console
$ qbraid envs registry add [OPTIONS] {path}
```

**Arguments**:

- `path`: [required]

**Options**:

- `-a, --alias <str>`: Alias for the environment
- `-n, --name <str>`: Name/slug for the environment
- `-y, --yes`
- `--help`: Show this message and exit.

### qbraid envs registry remove

Unregister an external environment.

This only removes the environment from qBraid's registry.
The actual environment files are NOT deleted.

**Usage**:

```console
$ qbraid envs registry remove [OPTIONS] {name}
```

**Arguments**:

- `name`: Name or alias of environment to unregister [required]

**Options**:

- `-y, --yes`
- `--help`: Show this message and exit.

### qbraid envs registry sync

Sync the environment registry.

This will:

- Remove registry entries for deleted environments
- Auto-discover new environments in default paths
- Verify all registered paths still exist

**Usage**:

```console
$ qbraid envs registry sync [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.
