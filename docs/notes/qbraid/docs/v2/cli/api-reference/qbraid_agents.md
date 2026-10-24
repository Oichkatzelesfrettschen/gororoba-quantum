> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_agents.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_agents.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 eb1f82f0e4559c996da24935a4e9eab0cad6d4f72ea242f63f73957633559d60.

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

# qbraid agents

> Manage AI coding agent sessions.

Launch, monitor, and control AI coding agents.
Run Claude Code, OpenCode, or Codex in managed tmux sessions. Send
instructions, stream transcripts, handle permissions, and orchestrate
multiple agents — all from one place. Works locally and on remote
compute servers via SSH.

Use this when you want to:

- Spin up agents on specific repos or projects
- Watch what agents are doing in real-time
- Approve or deny tool-use permissions remotely
- Manage agents running on cloud compute machines
- Resume previous coding sessions

Getting started:

```bash
qbraid agents launch                    # Interactive launch
qbraid agents list                      # Show active sessions
qbraid agents watch <name>              # Stream live activity
qbraid agents send <name> --text "..."  # Send instructions
```

**Usage**:

```console
$ qbraid agents [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `interrupt`: Interrupt one verified active turn.
- `jobs`: Inspect agent schedules and jobs.
- `register`: Register an agent session.
- `deregister`: Deregister an agent session.
- `list`: List agent sessions.
- `discover`: Discover new agent sessions.
- `status`: Show detailed status for an agent session.
- `update`: Update metadata fields on an agent session.
- `kill`: Stop an agent by name, session ID, or PID.
- `readiness`: Check this destination before launch.
- `machine`: Serve the fleet machine protocol.
- `settings`: Inspect or configure agent execution.
- `launch`: Launch an AI coding agent.
- `resume`: Resume a previous agent session.
- `send`: Send text to a running agent's terminal.
- `read`: Read recent terminal output from an agent.
- `notifier`: Wake idle agents when inbox mail arrives.
- `approve`: Approve a tool-use prompt.
- `watch`: Stream agent transcript.
- `attach`: Attach to an agent's terminal.
- `clean`: Clean up orphaned sessions.
- `send-to`: Send a message to another agent's inbox.
- `broadcast`: Broadcast to multiple agent inboxes.
- `team`: Show a team roster with unread counts.
- `hooks`: Manage agent lifecycle hooks.
- `keep-alive`: Opt-in local managed agent recovery.
- `queue`: Queue follow-ups for a managed runtime.
- `inbox`: Read messages sent to this agent's inbox.

## qbraid agents interrupt

Interrupt one verified active turn.

Request one Escape and pause queued input, without ending the agent process.

**Usage**:

```console
$ qbraid agents interrupt [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Exact destination session ID. [required]

**Options**:

- `--preflight`: Inspect availability and turn without sending Escape.
- `--compute <str>`
- `--request-id <str>`
- `--json`
- `--help`: Show this message and exit.

## qbraid agents jobs

Inspect agent schedules and jobs.

This observes provider-owned work. It never creates a schedule, wakes an
agent, or treats missing telemetry as an empty list. Manage tasks through
the agent's own terminal. Claude reports snapshots after completing turns;
other providers report unsupported until they expose an inventory.

**Usage**:

```console
$ qbraid agents jobs [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Exact qBraid session ID from agents list. [required]

**Options**:

- `-c, --compute <str>`: SSH alias for the owning machine.
- `--json`: Emit one JSON object; errors go to stderr.
- `--help`: Show this message and exit.

## qbraid agents register

Register an agent session.

Reads session data from stdin JSON (used by hooks).

**Usage**:

```console
$ qbraid agents register [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid agents deregister

Deregister an agent session.

Reads session data from stdin JSON (used by hooks).

**Usage**:

```console
$ qbraid agents deregister [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid agents list

List agent sessions.

Use --compute to list on a remote server.

**Usage**:

```console
$ qbraid agents list [OPTIONS]
```

**Options**:

- `-t, --tool <str>`: Filter by tool (claude, codeq, codex)
- `--status <str>`: Filter by status
- `--tag <str>`: Filter by tag (repeatable)
- `--since <str>`: Time window (e.g., '1h', '30m', '2d')
- `-c, --compute <str>`: SSH alias for remote compute (runs list on remote)
- `-s, --search <str>`: Text search across name/cwd/tags
- `-a, --all`: Include stopped sessions
- `-l, --limit <int range>`: Entries per page [default: 25; x&gt;=1]
- `-p, --page <int range>`: Page number (non-interactive mode) [default: 1; x&gt;=1]
- `--sort <str>`: Sort by: recent, oldest, name, tool, status, cwd, model [default: recent]
- `--no-interactive`: Disable interactive pagination
- `--json`: Output as JSON array (for programmatic use)
- `--help`: Show this message and exit.

## qbraid agents discover

Discover new agent sessions.

Scans transcript files and registers new agent sessions.

**Usage**:

```console
$ qbraid agents discover [OPTIONS]
```

**Options**:

- `-f, --full`: Full data enrichment for all sessions (slower)
- `-c, --compute <str>`: Sync sessions from remote compute server (SSH alias)
- `--help`: Show this message and exit.

## qbraid agents status

Show detailed status for an agent session.

Without `--compute` this reads the local registry, which is per-host: an
agent on another machine is simply absent and reports as not found.

**Usage**:

```console
$ qbraid agents status [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (full or prefix) [required]

**Options**:

- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents update

Update metadata fields on an agent session.

--type, --team and --parent let agents started from a terminal join a
team after launch, so they can message each other. From your own shell
any change is allowed. Inside an agent, it may only place teamless
sessions or its teammates into a team it leads, never as or out of
leader. These are coordination guardrails, not a security boundary.

**Usage**:

```console
$ qbraid agents update [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (full or prefix) [required]

**Options**:

- `--tag <str>`: Tag to add (can be repeated)
- `--name <str>`: Set terminal name for the session
- `--model <str>`: Set model name (e.g. claude-sonnet-4-20250514)
- `--cwd <str>`: Set working directory for the session
- `--status <str>`: Set session status (working, waiting, idle, error, stopped)
- `--type <str>`: Set the agent type (leader, worker, observer, reviewer); '' clears it.
- `--team <str>`: Join a team by id; '' leaves it.
- `--parent <str>`: Set the parent session (id, prefix or name); '' clears it.
- `--help`: Show this message and exit.

## qbraid agents kill

Stop an agent by name, session ID, or PID.

With `--compute` the agent is stopped on that machine. Without it, an
agent running elsewhere is simply not in this host's registry and reports
as not found -- the registry is per-host.

**Usage**:

```console
$ qbraid agents kill [OPTIONS] {target}
```

**Arguments**:

- `target`: Agent name, ID prefix, or PID [required]

**Options**:

- `-f, --force`: Use SIGKILL instead of SIGTERM
- `-c, --compute <str>`: SSH alias for remote compute
- `-y, --yes`: Confirm disabling keep-alive before Stop.
- `--json`: Print a JSON receipt; enrolled Stop requires --yes.
- `--help`: Show this message and exit.

## qbraid agents readiness

Check this destination before launch.

Known blockers exit with status 1.

**Usage**:

```console
$ qbraid agents readiness [OPTIONS]
```

**Options**:

- `--tool <str>`: Provider to inspect: claude, codex, or codeq. [required]
- `--cwd <str>`: Working directory on this machine.
- `--approval <ask|auto|manual|auto-review|yolo>`
- `--execution-mode <native|workspace|container>`
- `--json`: Print structured checks and recovery actions.
- `--verify-auth`: Explicitly check provider authentication; does not sign in or transfer credentials.
- `--help`: Show this message and exit.

## qbraid agents machine

Serve the fleet machine protocol.

Protocol v1 writes only JSON frames to stdout.

**Usage**:

```console
$ qbraid agents machine [OPTIONS]
```

**Options**:

- `--serve`: Serve JSON lines over authenticated SSH stdin/stdout.
- `--once`: Read one JSON request from stdin and return one response.
- `--help`: Show this message and exit.

## qbraid agents settings

Inspect or configure agent execution.

Defaults are shared by the CLI and dashboard on this machine.

**Usage**:

```console
$ qbraid agents settings [OPTIONS]
```

**Options**:

- `--execution-mode <native|workspace|container>`: Save the Codex execution default for this machine.
- `--reset`: Remove this machine's execution preference.
- `--json`: Print structured settings and sandbox readiness.
- `--help`: Show this message and exit.

## qbraid agents launch

Launch an AI coding agent.

Uses the owning Lab terminal when available; otherwise starts in tmux.

Detached agents may wait for approval until you open their terminal or dashboard.
Approval and execution mode are independent and remembered for resume.
--approval auto disables approval prompts; --execution-mode container
explicitly uses the current user's access without an extra Codex sandbox.
Choose it only where you trust the surrounding machine/container isolation.

**Usage**:

```console
$ qbraid agents launch [OPTIONS]
```

**Options**:

- `--backend <auto|jupyter|tmux>`: auto: prefer the owning Lab terminal; jupyter: require Lab; tmux: run independently. [default: auto]
- `-t, --tool <str>`: Agent tool (claude, codeq, codex; claude-auto = claude --approval auto)
- `--cwd <str>`: Working directory
- `-n, --name <str>`: Agent name
- `-i, --instructions <str>`: Initial instructions
- `-r, --repo <str>`: GitHub repo URL, org/repo, or issue/PR URL
- `--type <str>`: Agent type: leader, worker, observer, reviewer
- `--parent <str>`: Parent session ID
- `--team <str>`: Team ID
- `--tag <str>`: Tags (repeatable)
- `-c, --compute <str>`: SSH alias for remote compute server
- `--request-id <str>`: Remote launch UUID retained for reconciling an interrupted request.
- `--execution-mode <native|workspace|container>`: Codex only: native uses Codex defaults; workspace adds its workspace sandbox; container uses current user access without an extra Codex sandbox (no sudo). Omitted preserves existing behavior. Independent of --approval.
- `--approval <ask|auto|manual|auto-review|yolo>`: manual: the agent asks you. auto-review: the tool's own automatic reviewer decides. yolo: no permission checks. ask/auto: legacy modes, unchanged.
- `--trust-hooks`: Codex only, DANGEROUS: run ALL enabled hooks (yours, the project's and plugins') without Codex's hook review, for this launch only. Not retained on resume. Refused with --repo. Independent of --approval and --yolo.
- `--trust-folder / --no-trust-folder`: Answer the agent's 'trust this folder?' prompt now (Claude, Codex), so a detached agent does not stop at it. The answer is remembered for later launches and resumes. Trusting a folder lets its own settings, hooks and MCP servers run. Default: Claude trusts the folder, except a fresh --repo clone; Codex asks.
- `--skip-bypass-confirmation`: Claude with --yolo: skip its bypass-permissions confirmation, for this launch only.
- `--yolo`: Claude: skip permissions. Codex: bypass approvals and its sandbox.
- `--help`: Show this message and exit.

## qbraid agents resume

Resume a previous agent session.

Resumes with the selected terminal backend. With `--compute` the session is resumed
on that machine, and a session id is required -- the interactive picker
reads the local registry and cannot see another host's sessions.

`--confirm-owner-gone` is for a session whose old Lab (in another PID
namespace, after a restart) cannot be verified gone. Core's preflight runs
first; when it allows a confirmation, its reason and the risk are shown and
the person is asked (default No). Without a terminal it refuses unless
`--yes` is given. An agent must never pass `--yes` on its own judgement:
only after the person has confirmed that the old Lab is closed or restarted.

**Usage**:

```console
$ qbraid agents resume [OPTIONS] [session_id]
```

**Arguments**:

- `session_id`: Session ID, prefix, or name. Omit for interactive picker.

**Options**:

- `--backend <auto|jupyter|tmux>`: auto: prefer the owning Lab terminal; jupyter: require Lab; tmux: run independently. [default: auto]
- `-n, --name <str>`: Agent name for the resumed session
- `--execution-mode <native|workspace|container>`: Override the recorded Codex execution mode for this resume.
- `--approval <ask|auto|manual|auto-review|yolo>`: Override recorded permissions for this resume. Omit to preserve them.
- `--trust-hooks`: Codex only, DANGEROUS: run ALL enabled hooks without Codex's hook review, for this resume only. Hooks are reviewed again on every run that omits it.
- `--trust-folder / --no-trust-folder`: Answer 'trust this folder?' for the folder it resumes in (remembered). Default: keep the answer given at launch.
- `--confirm-owner-gone`: For a session from a restarted Lab that cannot be verified: confirm its old Lab is closed or restarted, and resume anyway. Asks first; confirming while that Lab still runs starts a second copy of the agent.
- `-y, --yes`: With --confirm-owner-gone: do not ask. Agents must not pass this unless the person has confirmed the old Lab is gone.
- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents send

Send text to a running agent's terminal.

**Usage**:

```console
$ qbraid agents send [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (prefix match) [required]

**Options**:

- `-m, --text <str>`: Text to send [required]
- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents read

Read recent terminal output from an agent.

**Usage**:

```console
$ qbraid agents read [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (prefix match) [required]

**Options**:

- `-n, --lines <int>`: Number of lines to capture [default: 50]
- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents notifier

Wake idle agents when inbox mail arrives.

Inbox delivery is passive: an agent parked at its prompt never notices a
message. This watches the inboxes of this machine's managed agents and
types a one-line nudge into an idle agent's pane. Busy agents are left
alone until they go idle, and a burst of messages is one nudge.

qBraid Lab runs this for you. Use it on a machine reached only over SSH.
Same-host: it watches the inboxes on the machine it runs on.

**Usage**:

```console
$ qbraid agents notifier [OPTIONS]
```

**Options**:

- `-i, --interval <float range>`: Seconds between checks [default: 4.0; x&gt;=1.0]
- `--once`: Check once, print who was nudged, and exit
- `--help`: Show this message and exit.

## qbraid agents approve

Approve a tool-use prompt.

Sends 'y' + Enter to the agent's terminal. With `--compute` the approval
is sent on that machine.

**Usage**:

```console
$ qbraid agents approve [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (prefix match) [required]

**Options**:

- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents watch

Stream agent transcript.

Streams live transcript from an agent session.

**Usage**:

```console
$ qbraid agents watch [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Session ID (prefix match) [required]

**Options**:

- `-n, --lines <int>`: Initial history lines [default: 20]
- `--interactive / --no-interactive`: Prompt for permission decisions [default: interactive]
- `--stream`: Stream-only mode: emit JSON events, no interactive prompts (for frontends)
- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents attach

Attach to an agent's terminal.

Reconnects to its recorded native terminal or tmux window.

**Usage**:

```console
$ qbraid agents attach [OPTIONS] [session_id]
```

**Arguments**:

- `session_id`: Session ID (prefix match). Omit for interactive picker.

**Options**:

- `-c, --compute <str>`: SSH alias for remote compute
- `--help`: Show this message and exit.

## qbraid agents clean

Clean up orphaned sessions.

Removes orphaned tmux windows and stopped sessions.

**Usage**:

```console
$ qbraid agents clean [OPTIONS]
```

**Options**:

- `-y, --yes`: Skip confirmation
- `--help`: Show this message and exit.

## qbraid agents send-to

Send a message to another agent's inbox.

For multi-recipient / team broadcast, use `qbraid agents broadcast`.

Same-host only: an inbox is a JSONL file under `~/.qbraid/inboxes/` on
the machine that owns it, so there is no `--compute`. Cross-host
messaging is not supported yet.

Delivery is a JSONL append at ~/.qbraid/inboxes/&lt;to-session-id&gt;.jsonl
(local host only — cross-host messaging isn't yet supported and will raise
a clear error). Permission rules (leader/worker/observer/reviewer) are
enforced by default.

**Usage**:

```console
$ qbraid agents send-to [OPTIONS] {to} {text}
```

**Arguments**:

- `to`: Target session id (full or prefix), tmux window name, or terminal name. [required]
- `text`: Message body. [required]

**Options**:

- `--from <str>`: Sender session id. Defaults to $QBRAID_SESSION_ID (set by the qBraid launcher for every managed agent shell).
- `--type <str>`: One of: message, task_assignment, status_update, shutdown_request. Controls how the recipient's UI/hooks categorize it. [default: message]
- `--no-permission-check`: Skip the sender→target permission check (agent-type rules from qbraid_core.services.agents.types.can_message). Use for testing.
- `--help`: Show this message and exit.

## qbraid agents broadcast

Broadcast to multiple agent inboxes.

Same-host only: an inbox is a JSONL file under `~/.qbraid/inboxes/` on
the machine that owns it, so there is no `--compute`. Cross-host
messaging is not supported yet.

Two selectors — pick exactly one:

- `--team &lt;team_id&gt;` — every session with that team_id (except sender)
- `--to A,B,C` — explicit id/prefix/name list

Delivery is all-or-nothing on target resolution: if any target can't be
resolved, NOTHING is sent (avoids partial-delivery surprises). Once
resolved, per-target send failures are reported individually; a partial
delivery exits with code 3.

**Usage**:

```console
$ qbraid agents broadcast [OPTIONS] {text}
```

**Arguments**:

- `text`: Message body — delivered to every target. [required]

**Options**:

- `--team <str>`: Deliver to every session with this team_id (excluding the sender). Use one of --team or --to.
- `--to <str>`: Comma-separated list of target session ids/prefixes/names for multi-recipient send. Use one of --team or --to.
- `--from <str>`: Sender session id. Defaults to $QBRAID_SESSION_ID.
- `--type <str>`: One of: message, task_assignment, status_update, shutdown_request. Controls how the recipient's UI/hooks categorize it. [default: message]
- `--no-permission-check`: Skip the sender→target permission check. Use for testing.
- `--help`: Show this message and exit.

## qbraid agents team

Show a team roster with unread counts.

Same-host only: an inbox is a JSONL file under `~/.qbraid/inboxes/` on
the machine that owns it, so there is no `--compute`. Cross-host
messaging is not supported yet.

Answers the leader-orchestrator question &quot;who is on my team, how many
unread messages do they have, and what was the last thing they heard from
anyone?&quot; — which today requires peeking each worker's inbox individually.

Rows are sorted with the current session first (identified via
$QBRAID_SESSION_ID), then by agent_type (leader → worker → observer →
reviewer), then by session_id.

**Usage**:

```console
$ qbraid agents team [OPTIONS] {team_id}
```

**Arguments**:

- `team_id`: Team identifier (matches AgentSession.team_id). [required]

**Options**:

- `-w, --wide`: Show full session ids instead of the 12-char prefix.
- `--help`: Show this message and exit.

## qbraid agents hooks

Manage agent lifecycle hooks.

**Usage**:

```console
$ qbraid agents hooks [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `install`: Install agent lifecycle hooks.
- `uninstall`: Remove agent lifecycle hooks.

### qbraid agents hooks install

Install agent lifecycle hooks.

Installs hooks for AI coding tools.

**Usage**:

```console
$ qbraid agents hooks install [OPTIONS]
```

**Options**:

- `-t, --tool <str>`: Install hooks for a specific tool (claude, codeq, codex)
- `--help`: Show this message and exit.

### qbraid agents hooks uninstall

Remove agent lifecycle hooks.

Removes hooks from all supported tools.

**Usage**:

```console
$ qbraid agents hooks uninstall [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## qbraid agents keep-alive

Opt-in local managed agent recovery.

Restore enrolled local conversations after an instance restart. A process exit in the same instance pauses recovery for attention. Off by default. Explicit Stop disables recovery. A compatible running host is required; these commands do not install a daemon or support remote compute.

**Usage**:

```console
$ qbraid agents keep-alive [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List local recovery policies.
- `enable`: Enable recovery for one exact session.
- `disable`: Disable recovery; leave the agent running.
- `forget`: Remove an already disabled policy.
- `run`: Run the local recovery host.

### qbraid agents keep-alive list

List local recovery policies.

Does not enroll or launch anything.

**Usage**:

```console
$ qbraid agents keep-alive list [OPTIONS]
```

**Options**:

- `--json`: Print policy data as JSON.
- `--help`: Show this message and exit.

### qbraid agents keep-alive enable

Enable recovery for one exact session.

Preserves the live conversation's recorded permissions.

**Usage**:

```console
$ qbraid agents keep-alive enable [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Complete local managed session ID; names/prefixes are refused. [required]

**Options**:

- `--json`: Print the resulting policy as JSON.
- `--help`: Show this message and exit.

### qbraid agents keep-alive disable

Disable recovery; leave the agent running.

**Usage**:

```console
$ qbraid agents keep-alive disable [OPTIONS] {policy_id}
```

**Arguments**:

- `policy_id`: Complete policy ID from keep-alive list. [required]

**Options**:

- `--json`: Print the resulting policy as JSON.
- `--help`: Show this message and exit.

### qbraid agents keep-alive forget

Remove an already disabled policy.

Does not change any agent runtime.

**Usage**:

```console
$ qbraid agents keep-alive forget [OPTIONS] {policy_id}
```

**Arguments**:

- `policy_id`: Complete, already disabled policy ID. [required]

**Options**:

- `--json`: Print a JSON acknowledgement.
- `--help`: Show this message and exit.

### qbraid agents keep-alive run

Run the local recovery host.

Ctrl-C exits without disabling policies.
Exiting leaves policies armed, but recovery requires another compatible host
to be running. Native policies pause here and require the owning Lab host.
This command never enrolls a session or installs a daemon.

**Usage**:

```console
$ qbraid agents keep-alive run [OPTIONS]
```

**Options**:

- `--once`: Reconcile once and exit; installs no background host.
- `--interval <float range>`: Seconds between ticks. [default: 5.0; 1.0&lt;=x&lt;=300.0]
- `--json`: Print each tick's policies as newline-delimited JSON.
- `--help`: Show this message and exit.

## qbraid agents queue

Queue follow-ups for a managed runtime.

**Usage**:

```console
$ qbraid agents queue [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `enqueue`: Queue a follow-up for this runtime.
- `list`: List retained messages and delivery state.
- `continue`: Continue this paused queue.
- `edit`: Edit a queued message at its revision.
- `cancel`: Cancel a queued message at its revision.
- `resolve`: Resolve an uncertain delivery.
- `request-status`: Inspect a request without replaying it.
- `watch`: Host queued delivery on this machine.

### qbraid agents queue enqueue

Queue a follow-up for this runtime.

Delivery waits for a confirmed completed turn and a running watcher.

**Usage**:

```console
$ qbraid agents queue enqueue [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: Exact destination session ID. [required]

**Options**:

- `--text <str>`: Plain follow-up text.
- `--file <path>`: UTF-8 text file (at most 32768 characters).
- `--compute <str>`: Destination SSH alias.
- `--request-id <str>`: Retain this UUID to reconcile a lost reply.
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue list

List retained messages and delivery state.

Includes uncertain outcomes and wait reasons across all receipt pages.

**Usage**:

```console
$ qbraid agents queue list [OPTIONS] {session_id}
```

**Arguments**:

- `session_id`: [required]

**Options**:

- `--compute <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue continue

Continue this paused queue.

Releases only the displayed hold. The watcher still checks turn completion,
pending approvals and uncertain messages; no input is sent by this command.

**Usage**:

```console
$ qbraid agents queue continue [OPTIONS] {session_id} {hold_id}
```

**Arguments**:

- `session_id`: Exact destination session ID. [required]
- `hold_id`: Hold UUID shown by queue list. [required]

**Options**:

- `--revision <int range>`: Hold revision shown by queue list. [x&gt;=1; required]
- `--compute <str>`
- `--request-id <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue edit

Edit a queued message at its revision.

A concurrent delivery or edit refuses this operation.

**Usage**:

```console
$ qbraid agents queue edit [OPTIONS] {session_id} {message_id}
```

**Arguments**:

- `session_id`: [required]
- `message_id`: [required]

**Options**:

- `--revision <int range>`: Revision shown by queue list. [x&gt;=1; required]
- `--text <str>`
- `--file <path>`
- `--compute <str>`
- `--request-id <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue cancel

Cancel a queued message at its revision.

This cannot interrupt a message already submitted.

**Usage**:

```console
$ qbraid agents queue cancel [OPTIONS] {session_id} {message_id}
```

**Arguments**:

- `session_id`: [required]
- `message_id`: [required]

**Options**:

- `--revision <int range>`: [x&gt;=1; required]
- `--compute <str>`
- `--request-id <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue resolve

Resolve an uncertain delivery.

Check the terminal and clear partial input first. This never resends text.

**Usage**:

```console
$ qbraid agents queue resolve [OPTIONS] {session_id} {message_id}
```

**Arguments**:

- `session_id`: [required]
- `message_id`: [required]

**Options**:

- `--revision <int range>`: [x&gt;=1; required]
- `--terminal-checked`: Confirm you inspected the terminal and cleared partial input.
- `--compute <str>`
- `--request-id <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue request-status

Inspect a request without replaying it.

Not-found does not prove non-delivery.

**Usage**:

```console
$ qbraid agents queue request-status [OPTIONS] {request_id}
```

**Arguments**:

- `request_id`: [required]

**Options**:

- `--compute <str>`
- `--json`
- `--help`: Show this message and exit.

### qbraid agents queue watch

Host queued delivery on this machine.

Run on the destination; Ctrl+C pauses delivery.
Closing this watcher preserves queued input. A tick sends at most one message
per session; an uncertain write pauses that runtime until explicitly resolved.

**Usage**:

```console
$ qbraid agents queue watch [OPTIONS]
```

**Options**:

- `--once`: Run one delivery tick and exit.
- `--interval <float range>`: [default: 4.0; 1.0&lt;=x&lt;=60.0]
- `--json`: Emit one JSON object per tick.
- `--help`: Show this message and exit.

## qbraid agents inbox

Read messages sent to this agent's inbox.

Follow, filter unread, and mark-read messages sent to this agent
session's inbox. Inboxes are per-session JSONL files at
~/.qbraid/inboxes/. Every agent session has one; peers use
`qbraid agents send-to` to write to it.

**Usage**:

```console
$ qbraid agents inbox [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `-s, --session <str>`: Session whose inbox to read. Accepts full id, prefix, or tmux/terminal name (resolved via the registry). Defaults to $QBRAID_SESSION_ID.
- `-f, --follow`: Stream new messages as they arrive.
- `-u, --unread`: Show only unread messages.
- `-n, --limit <int>`: Max messages to show (most recent). [default: 50]
- `--mark-read / --no-mark-read`: Mark shown messages as read after display. Default on. [default: mark-read]
- `-w, --wide`: Show full session ids in the From column and title (not the 12-char prefix). Use when multiple senders share a prefix.
- `--help`: Show this message and exit.

**Commands**:

- `mark-read`: Mark inbox messages as read.

### qbraid agents inbox mark-read

Mark inbox messages as read.

Without --message-id, marks every unread message in the session's inbox.

**Usage**:

```console
$ qbraid agents inbox mark-read [OPTIONS]
```

**Options**:

- `-s, --session <str>`: Session whose inbox to update. Accepts full id, prefix, or tmux/terminal name. Defaults to $QBRAID_SESSION_ID.
- `-m, --message-id <str>`: Specific message id(s) to mark. May be passed multiple times. Omit to mark ALL unread messages in the inbox.
- `--help`: Show this message and exit.
