> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_skills.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_skills.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 1acf02b2b9150c8f34cb624196f7d8eecb8675c6a4f9ccb694a74f24122d33fc.

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

# qbraid skills

> Create, install, and share AI coding skills.

Skills are reusable prompt templates and tools that give AI agents
specialized capabilities — like running quantum circuits, deploying
to specific platforms, or following team conventions.

Use this when you want to:

- Give your AI agent domain-specific knowledge
- Share team-specific workflows with collaborators
- Install community-built skills from the catalog
- Create custom skills for your projects

Quick start:

```bash
qbraid skills list             # Browse available skills
qbraid skills install <slug>   # Install a skill
qbraid skills create           # Create a new skill
```

**Usage**:

```console
$ qbraid skills [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List available qBraid skills.
- `search`: Search for qBraid skills.
- `info`: Get detailed information about a skill.
- `install`: Install a skill for AI coding tools.
- `uninstall`: Uninstall a skill from AI coding tools.
- `installed`: List locally installed skills.
- `check`: Check if a skill is installed and where.
- `share`: Share a skill with another user.
- `unshare`: Revoke a user's access to a skill.
- `shared-with`: List users with access to a skill.
- `share-code`: Generate a share code for a skill.
- `redeem`: Redeem a skill share code.
- `request-publish`: Request to publish a skill publicly.
- `revoke-publish`: Revoke a pending publish request.
- `pending-reviews`: List skills pending review (admin only).
- `approve-publish`: Approve skill publishing.
- `deny-publish`: Deny a publish request (admin only).
- `mark-pending`: Mark a skill as under review (admin only).
- `create`: Create a new skill.
- `upload`: Upload files to a skill.
- `update`: Update skill metadata.
- `delete`: Delete a skill (owner or admin only).

## qbraid skills list

List available qBraid skills.

Pass --json for the full, untruncated records.

**Usage**:

```console
$ qbraid skills list [OPTIONS]
```

**Options**:

- `-q, --query <str>`: Search query for skills
- `-t, --tags <str>`: Filter by tags (comma-separated)
- `-v, --visibility <private|public|shared>`: Filter by visibility
- `-l, --limit <int>`: Maximum number of results [default: 20]
- `--json`: Output as JSON array (for programmatic use)
- `--help`: Show this message and exit.

## qbraid skills search

Search for qBraid skills.

Pass --json for the full, untruncated records.

**Usage**:

```console
$ qbraid skills search [OPTIONS] {query}
```

**Arguments**:

- `query`: Search query [required]

**Options**:

- `-l, --limit <int>`: Maximum number of results [default: 10]
- `--json`: Output as JSON array (for programmatic use)
- `--help`: Show this message and exit.

## qbraid skills info

Get detailed information about a skill.

**Usage**:

```console
$ qbraid skills info [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to get info for [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills install

Install a skill for AI coding tools.

By default, installs to Claude Code (~/.claude/skills/). Use --target all
for every supported tool; --target codex or --target pi both land in
~/.agents/skills/, which Codex and CodeQ (pi) read.

In a tool's skills directory the skill is placed under its own name (not
its slug); with --path it is placed under its slug at that path. The
download is checked against the registry's checksum, and installing an
unchanged skill again is a no-op.

**Usage**:

```console
$ qbraid skills install [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to install [required]

**Options**:

- `-t, --target <claude-code|codex|pi|cursor|copilot|all>`: Target AI coding tool(s) to install for [default: claude-code]
- `-p, --path <str>`: Install into this directory instead of a tool's skills directory
- `-f, --force`: Replace the installed copy even if it is unchanged or was not installed by qbraid
- `--help`: Show this message and exit.

## qbraid skills uninstall

Uninstall a skill from AI coding tools.

By default, uninstalls from all supported tools. Accepts the registry slug
or the installed directory name.

**Usage**:

```console
$ qbraid skills uninstall [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug (or installed name) to uninstall [required]

**Options**:

- `-t, --target <claude-code|codex|pi|cursor|copilot|all>`: Target AI coding tool(s) to uninstall from [default: all]
- `--path <str>`: Uninstall from this directory instead of the tool directories
- `--help`: Show this message and exit.

## qbraid skills installed

List locally installed skills.

Shows each skill's name, registry slug and version per tool.

**Usage**:

```console
$ qbraid skills installed [OPTIONS]
```

**Options**:

- `-t, --target <claude-code|codex|pi|cursor|copilot|all>`: Show skills for specific tool only
- `--path <str>`: List skills installed in this directory
- `--help`: Show this message and exit.

## qbraid skills check

Check if a skill is installed and where.

**Usage**:

```console
$ qbraid skills check [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to check [required]

**Options**:

- `--path <str>`: Check this directory instead of the tool directories
- `--help`: Show this message and exit.

## qbraid skills share

Share a skill with another user.

**Usage**:

```console
$ qbraid skills share [OPTIONS] {slug} {email}
```

**Arguments**:

- `slug`: The skill slug to share [required]
- `email`: Email of user to share with [required]

**Options**:

- `-w, --write`: Grant write permission (default is read-only)
- `--help`: Show this message and exit.

## qbraid skills unshare

Revoke a user's access to a skill.

**Usage**:

```console
$ qbraid skills unshare [OPTIONS] {slug} {email}
```

**Arguments**:

- `slug`: The skill slug [required]
- `email`: Email of user to revoke access from [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills shared-with

List users with access to a skill.

**Usage**:

```console
$ qbraid skills shared-with [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills share-code

Generate a share code for a skill.

**Usage**:

```console
$ qbraid skills share-code [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills redeem

Redeem a skill share code.

Redeems a share code to get access to a skill.

**Usage**:

```console
$ qbraid skills redeem [OPTIONS] {code}
```

**Arguments**:

- `code`: The share code to redeem [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills request-publish

Request to publish a skill publicly.

**Usage**:

```console
$ qbraid skills request-publish [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to publish [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills revoke-publish

Revoke a pending publish request.

**Usage**:

```console
$ qbraid skills revoke-publish [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills pending-reviews

List skills pending review (admin only).

**Usage**:

```console
$ qbraid skills pending-reviews [OPTIONS]
```

**Options**:

- `-l, --limit <int>`: Maximum number of results [default: 20]
- `--help`: Show this message and exit.

## qbraid skills approve-publish

Approve skill publishing.

Approves a skill for publishing (admin only).

**Usage**:

```console
$ qbraid skills approve-publish [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to approve [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills deny-publish

Deny a publish request (admin only).

**Usage**:

```console
$ qbraid skills deny-publish [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to deny [required]

**Options**:

- `-r, --reason <str>`: Reason for denial
- `--help`: Show this message and exit.

## qbraid skills mark-pending

Mark a skill as under review (admin only).

**Usage**:

```console
$ qbraid skills mark-pending [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug [required]

**Options**:

- `--help`: Show this message and exit.

## qbraid skills create

Create a new skill.

Optionally upload a directory with --dir.

**Usage**:

```console
$ qbraid skills create [OPTIONS]
```

**Options**:

- `-n, --name <str>`: Display name for the skill (1-100 chars) [required]
- `-d, --description <str>`: Skill description (max 500 chars)
- `-v, --version <str>`: Skill version [default: 1.0.0]
- `-t, --tags <str>`: Comma-separated tags
- `--visibility <private|public|shared>`: Skill visibility [default: private]
- `--dir <str>`: Path to skill directory to upload after creation
- `--help`: Show this message and exit.

## qbraid skills upload

Upload files to a skill.

Uploads a skill directory to an existing skill.

**Usage**:

```console
$ qbraid skills upload [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to upload to [required]

**Options**:

- `--dir <str>`: Path to skill directory to upload [required]
- `--help`: Show this message and exit.

## qbraid skills update

Update skill metadata.

**Usage**:

```console
$ qbraid skills update [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to update [required]

**Options**:

- `-n, --name <str>`: New display name
- `-d, --description <str>`: New description
- `-v, --version <str>`: New version
- `-t, --tags <str>`: New comma-separated tags
- `--visibility <private|public|shared>`: New visibility
- `--help`: Show this message and exit.

## qbraid skills delete

Delete a skill (owner or admin only).

**Usage**:

```console
$ qbraid skills delete [OPTIONS] {slug}
```

**Arguments**:

- `slug`: The skill slug to delete [required]

**Options**:

- `-y, --yes`: Skip confirmation prompt
- `--help`: Show this message and exit.
