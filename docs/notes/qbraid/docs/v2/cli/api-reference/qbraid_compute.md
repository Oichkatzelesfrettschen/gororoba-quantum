> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e8d7c45464280b9e89807a840149987e529840c6c0dad07695e5e261f0b51234.

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

# qbraid compute

> Manage cloud compute and SSH.

Manage cloud compute servers, profiles, and SSH access.
Start GPU or CPU servers on qBraid infrastructure. SSH in from any
terminal, connect your IDE (VS Code, Cursor), or launch AI agents
on remote hardware. Persistent storage across sessions.

Use this when you want to:

- Run heavy workloads on cloud GPUs without local setup
- SSH into a cloud dev environment from your terminal
- Connect VS Code or Cursor to a remote server
- Launch AI agents on more powerful hardware

Quick start:

```bash
qbraid compute up <profile>          # Launch an instance + configure SSH
qbraid compute status                # List your instances
qbraid compute instances ...         # launch/start/stop/terminate/ssh/...
qbraid compute down                  # Stop an instance
```

**Usage**:

```console
$ qbraid compute [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `up`: Launch an instance and configure SSH.
- `down`: Stop an instance.
- `status`: List your instances.
- `list`: List compute profiles.
- `sessions`: List compute sessions.
- `usage`: Show compute usage summary.
- `instances`: Manage compute instances.
- `profiles`: Manage compute profiles.
- `server`: (deprecated) Use `qbraid compute instances`.
- `ssh`: SSH access to compute servers.

## qbraid compute up

Launch an instance and configure SSH.

Alias for `qbraid compute instances launch &lt;profile&gt; --ssh`. On-demand
profiles always launch a new instance; the subscription server attaches
if it's already running.

Example:

```bash
qbraid compute up gpu-l4
```

**Usage**:

```console
$ qbraid compute up [OPTIONS] {profile_slug}
```

**Arguments**:

- `profile_slug`: Profile slug to launch [required]

**Options**:

- `-c, --cluster <str>`: Subscription cluster ID
- `-t, --timeout <int>`: Seconds to wait (default 600 on-demand, 120 subscription)
- `--no-ssh`: Skip SSH configuration
- `--help`: Show this message and exit.

## qbraid compute down

Stop an instance.

Alias for `qbraid compute instances stop`. With no target, stops your
running on-demand instance (asking which if several) or else the
subscription server.

Example:

```bash
qbraid compute down
qbraid compute down trainer
```

**Usage**:

```console
$ qbraid compute down [OPTIONS] [target]
```

**Arguments**:

- `target`: Instance: id, hash, label, profile slug, or 'subscription'

**Options**:

- `-c, --cluster <str>`: Subscription cluster ID
- `-i, --instance <str>`: Same as the positional target
- `-f, --force`: Skip confirmation
- `--cleanup-ssh`: Remove the subscription SSH config
- `--help`: Show this message and exit.

## qbraid compute status

List your instances.

Alias for `qbraid compute instances list`.

**Usage**:

```console
$ qbraid compute status [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

## qbraid compute list

List compute profiles.

Quick list profiles (alias for 'profiles list').

**Usage**:

```console
$ qbraid compute list [OPTIONS]
```

**Options**:

- `-g, --gpu`: Show only GPU profiles
- `-a, --available`: Show only available profiles
- `-l, --limit <int>`: Number of results [default: 20]
- `--help`: Show this message and exit.

## qbraid compute sessions

List compute sessions.

**Usage**:

```console
$ qbraid compute sessions [OPTIONS]
```

**Options**:

- `-l, --limit <int>`: Number of sessions to show [default: 10]
- `-s, --status <str>`: Filter by status (active, ended)
- `-t, --type <str>`: Filter by type (cpu, gpu)
- `-d, --days <int>`: Show sessions from last N days
- `--help`: Show this message and exit.

## qbraid compute usage

Show compute usage summary.

**Usage**:

```console
$ qbraid compute usage [OPTIONS]
```

**Options**:

- `-d, --days <int>`: Number of days (default: 30)
- `--tz <str>`: Timezone (e.g. America/New_York)
- `--daily`: Show daily breakdown
- `--help`: Show this message and exit.

## qbraid compute instances

Manage compute instances.

One list for both tiers: on-demand instances (billed from your wallet, several at once) and the subscription server (one at a time).

Quick start:

```bash
qbraid compute instances launch <profile>   # new instance, waits, prints URL
qbraid compute instances list               # both tiers, rates, uptime
qbraid compute instances stop <target>      # keeps the disk; bills storage
qbraid compute instances terminate <target> # the only zero-cost state
```

&lt;target&gt; is an instance id, its hash, a label, a profile slug, or 'subscription'.

**Usage**:

```console
$ qbraid compute instances [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List your instances across both tiers.
- `show`: Show one instance in detail.
- `launch`: Launch a new instance from a profile.
- `start`: Start (resume) a stopped instance.
- `stop`: Stop a running instance; the disk is kept.
- `terminate`: Terminate an instance; deletes its disk.
- `set`: Change an instance's label or auto-stop.
- `ssh`: Configure SSH for a running instance.
- `history`: List terminated instances and what they cost.
- `availability`: Show on-demand capacity and rates by profile.

### qbraid compute instances list

List your instances across both tiers.

Example:

```bash
qbraid compute instances list
```

**Usage**:

```console
$ qbraid compute instances list [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

### qbraid compute instances show

Show one instance in detail.

Example:

```bash
qbraid compute instances show trainer
qbraid compute instances show subscription --show-url
```

**Usage**:

```console
$ qbraid compute instances show [OPTIONS] {target}
```

**Arguments**:

- `target`: Instance id, hash, label, profile slug, or 'subscription' [required]

**Options**:

- `--show-url`: Show the full URL including the auth token
- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

### qbraid compute instances launch

Launch a new instance from a profile.

On-demand profiles always launch a new instance — the tier is
multi-instance — and you're told if you already have one up. The
subscription tier is one server at a time, so launching attaches if it's
already running.

Example:

```bash
qbraid compute instances launch gpu-l4 --ssh
qbraid compute instances launch gpu-l4 --label trainer --no-wait
```

**Usage**:

```console
$ qbraid compute instances launch [OPTIONS] {profile_slug}
```

**Arguments**:

- `profile_slug`: Profile slug (see `qbraid compute profiles list`) [required]

**Options**:

- `--no-wait`: Return right after the launch is accepted
- `--ssh`: Configure SSH once the instance is ready
- `-t, --timeout <int>`: Seconds to wait (default 600 on-demand, 120 subscription)
- `-l, --label <str>`: Label for the new instance (on-demand)
- `--region <str>`: Preferred region (on-demand; a preference, not a pin)
- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

### qbraid compute instances start

Start (resume) a stopped instance.

Its disk is kept, so you pick up where you left off. With a profile slug,
resumes your stopped instance of that profile — and asks which if there
are several.

Example:

```bash
qbraid compute instances start trainer
qbraid compute instances start gpu-l4 --ssh
```

**Usage**:

```console
$ qbraid compute instances start [OPTIONS] [target]
```

**Arguments**:

- `target`: Stopped instance: id, hash, label, or profile slug

**Options**:

- `--no-wait`: Return right after the start is accepted
- `--ssh`: Configure SSH once the instance is ready
- `-t, --timeout <int>`: Seconds to wait (default 600)
- `--help`: Show this message and exit.

### qbraid compute instances stop

Stop a running instance; the disk is kept.

A stopped on-demand instance keeps billing a small storage rate until you
terminate it. Refuses on clouds that can't preserve the disk (stop would
destroy it) — terminate those instead.

Example:

```bash
qbraid compute instances stop trainer
qbraid compute instances stop subscription
```

**Usage**:

```console
$ qbraid compute instances stop [OPTIONS] [target]
```

**Arguments**:

- `target`: Running instance: id, hash, label, profile slug, or 'subscription'

**Options**:

- `-y, --yes`: Skip the confirmation
- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

### qbraid compute instances terminate

Terminate an instance; deletes its disk.

The only zero-cost state: a stopped instance still bills storage. Works
from any state, including one that is still starting.

Example:

```bash
qbraid compute instances terminate trainer
```

**Usage**:

```console
$ qbraid compute instances terminate [OPTIONS] [target]
```

**Arguments**:

- `target`: Instance: id, hash, label, or profile slug

**Options**:

- `-y, --yes`: Skip the confirmation
- `--help`: Show this message and exit.

### qbraid compute instances set

Change an instance's label or auto-stop.

Example:

```bash
qbraid compute instances set a1b2c3d4 --label trainer
qbraid compute instances set trainer --max-session 240
```

**Usage**:

```console
$ qbraid compute instances set [OPTIONS] {target}
```

**Arguments**:

- `target`: Instance: id, hash, label, or profile slug [required]

**Options**:

- `-l, --label <str>`: New label ('' clears it)
- `--max-session <int>`: Stop after this many minutes running (0 disables)
- `--auto-stop <int>`: Stop after this many idle minutes (0 disables)
- `--help`: Show this message and exit.

### qbraid compute instances ssh

Configure SSH for a running instance.

Example:

```bash
qbraid compute instances ssh trainer
```

**Usage**:

```console
$ qbraid compute instances ssh [OPTIONS] [target]
```

**Arguments**:

- `target`: Running instance: id, hash, label, profile slug, or 'subscription'

**Options**:

- `-c, --cluster <str>`: Subscription cluster ID
- `--help`: Show this message and exit.

### qbraid compute instances history

List terminated instances and what they cost.

Example:

```bash
qbraid compute instances history --page 2
```

**Usage**:

```console
$ qbraid compute instances history [OPTIONS]
```

**Options**:

- `-p, --page <int>`: Page number [default: 1]
- `-l, --limit <int>`: Results per page (max 100) [default: 50]
- `--help`: Show this message and exit.

### qbraid compute instances availability

Show on-demand capacity and rates by profile.

Example:

```bash
qbraid compute instances availability gpu-l4
```

**Usage**:

```console
$ qbraid compute instances availability [OPTIONS] [profile_slug]
```

**Arguments**:

- `profile_slug`: Only this profile

**Options**:

- `--help`: Show this message and exit.

## qbraid compute profiles

Manage compute profiles.

**Usage**:

```console
$ qbraid compute profiles [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List available compute profiles.
- `info`: Get detailed profile information.
- `create-try`: Create a try-mode profile.
- `create-save`: Create a save-mode profile.
- `build-status`: Check build status for a save-mode profile.
- `delete`: Delete a user-owned profile.

### qbraid compute profiles list

List available compute profiles.

**Usage**:

```console
$ qbraid compute profiles list [OPTIONS]
```

**Options**:

- `-p, --plan <str>`: Filter by plan tier
- `-g, --gpu`: Filter GPU profiles
- `-c, --has-capacity`: Filter by capacity
- `--cluster <str>`: Filter by cluster
- `-l, --limit <int>`: Results per page [default: 50]
- `--help`: Show this message and exit.

### qbraid compute profiles info

Get detailed profile information.

**Usage**:

```console
$ qbraid compute profiles info [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Profile slug [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid compute profiles create-try

Create a try-mode profile.

Standard+ plan required.
Try-mode profiles use on-the-fly overlay injection - no build step required.

**Usage**:

```console
$ qbraid compute profiles create-try [OPTIONS]
```

**Options**:

- `-i, --image <str>`: Base Docker image (required) [required]
- `-n, --name <str>`: Display name
- `-d, --description <str>`: Description
- `--cpu <float>`: CPU cores (guarantee and limit)
- `-m, --mem <str>`: Memory (e.g., '8G')
- `-g, --gpu`: Enable GPU
- `--ide <str>`: IDE type: lab, vscode, ssh [default: lab]
- `-f, --features <str>`: Features (e.g., 'claude,codeq')
- `--help`: Show this message and exit.

### qbraid compute profiles create-save

Create a save-mode profile.

Pro+ plan required.
Save-mode profiles trigger a Cloud Build to create a permanent overlay image.
Use --wait to wait for the build to complete.

**Usage**:

```console
$ qbraid compute profiles create-save [OPTIONS]
```

**Options**:

- `-i, --image <str>`: Base Docker image (required) [required]
- `-n, --name <str>`: Display name
- `-d, --description <str>`: Description
- `--cpu <float>`: CPU cores (guarantee and limit)
- `-m, --mem <str>`: Memory (e.g., '8G')
- `-g, --gpu`: Enable GPU
- `--ide <str>`: IDE type: lab, vscode, ssh [default: lab]
- `-f, --features <str>`: Features (e.g., 'claude,codeq')
- `-w, --wait`: Wait for build to complete
- `-t, --timeout <int>`: Build timeout in seconds [default: 600]
- `--help`: Show this message and exit.

### qbraid compute profiles build-status

Check build status for a save-mode profile.

**Usage**:

```console
$ qbraid compute profiles build-status [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Profile slug [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid compute profiles delete

Delete a user-owned profile.

**Usage**:

```console
$ qbraid compute profiles delete [OPTIONS] {slug}
```

**Arguments**:

- `slug`: Profile slug to delete [required]

**Options**:

- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.

## qbraid compute server

(deprecated) Use `qbraid compute instances`.

**Usage**:

```console
$ qbraid compute server [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `status`: (deprecated) Use `instances list`.
- `start`: (deprecated) Use `instances launch`/`start`.
- `stop`: (deprecated) Use `instances stop`.
- `terminate`: (deprecated) Use `instances terminate`.
- `url`: (deprecated) Use `instances show`.
- `stop-all`: Stop all subscription servers.

### qbraid compute server status

(deprecated) Use `instances list`.

**Usage**:

```console
$ qbraid compute server status [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `--show-url`: Show full server URL with auth token
- `--help`: Show this message and exit.

### qbraid compute server start

(deprecated) Use `instances launch`/`start`.

**Usage**:

```console
$ qbraid compute server start [OPTIONS] {target}
```

**Arguments**:

- `target`: Profile slug (launch) or instance target (resume) [required]

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `-w, --wait`: Wait until ready
- `-t, --timeout <int>`: Seconds to wait
- `--ssh`: Configure SSH once ready
- `--help`: Show this message and exit.

### qbraid compute server stop

(deprecated) Use `instances stop`.

**Usage**:

```console
$ qbraid compute server stop [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `-i, --instance <str>`: Instance target
- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.

### qbraid compute server terminate

(deprecated) Use `instances terminate`.

**Usage**:

```console
$ qbraid compute server terminate [OPTIONS]
```

**Options**:

- `-i, --instance <str>`: Instance target
- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.

### qbraid compute server url

(deprecated) Use `instances show`.

**Usage**:

```console
$ qbraid compute server url [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `--help`: Show this message and exit.

### qbraid compute server stop-all

Stop all subscription servers.

**Usage**:

```console
$ qbraid compute server stop-all [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.

## qbraid compute ssh

SSH access to compute servers.

**Usage**:

```console
$ qbraid compute ssh [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `setup`: Configure SSH for the server.
- `connect`: SSH into the running server.
- `token`: Get SSH session token.
- `config`: Show or edit SSH configuration.
- `remove`: Remove SSH configuration for a host.

### qbraid compute ssh setup

Configure SSH for the server.

Sets up SSH config with a ProxyCommand that tunnels SSH through
the jupyter-server-proxy WebSocket endpoint. No websocat required.

On-demand BMA instances are handled automatically: if one is running
it's configured under its own alias; pass --instance to target a specific
one. Each instance gets an independent alias so several can be reachable at
once.

**Usage**:

```console
$ qbraid compute ssh setup [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `-i, --instance <str>`: On-demand instance: id, hash, label, or profile slug
- `-t, --tool <str>`: Configure for specific tool: vscode, cursor, claude-code, codex
- `-a, --alias <str>`: SSH config alias (default: qbraid-&#123;cluster&#125;)
- `--help`: Show this message and exit.

### qbraid compute ssh connect

SSH into the running server.

This opens an interactive SSH session to the server. Pass --instance to
connect to a specific on-demand instance (resolves to its per-instance
alias from 'ssh setup --instance').

**Usage**:

```console
$ qbraid compute ssh connect [OPTIONS]
```

**Options**:

- `-a, --alias <str>`: SSH config alias (auto-detected if not set)
- `-i, --instance <str>`: On-demand instance: id, hash, label, or profile slug
- `--help`: Show this message and exit.

### qbraid compute ssh token

Get SSH session token.

Retrieves a JupyterHub session token for SSH access.

**Usage**:

```console
$ qbraid compute ssh token [OPTIONS]
```

**Options**:

- `-c, --cluster <str>`: Cluster ID
- `-r, --raw`: Output raw token only
- `--help`: Show this message and exit.

### qbraid compute ssh config

Show or edit SSH configuration.

**Usage**:

```console
$ qbraid compute ssh config [OPTIONS]
```

**Options**:

- `-e, --edit`: Open config in editor
- `--help`: Show this message and exit.

### qbraid compute ssh remove

Remove SSH configuration for a host.

**Usage**:

```console
$ qbraid compute ssh remove [OPTIONS] {alias}
```

**Arguments**:

- `alias`: SSH alias to remove [required]

**Options**:

- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.
