# qBraid MCP server

The hosted server is `https://mcp.qbraid.com/mcp`. It speaks Streamable HTTP
and authenticates with OAuth against the qBraid account. The checksummed
vendor page, retrieved 2026-10-24, stays at
[docs/v2/ai/integrations/mcp-server.md](docs/v2/ai/integrations/mcp-server.md);
`scripts/capture_qbraid_docs.py --check` binds those bytes. This page records
the live discovery documents, the tool categories that page publishes, and
the client registration on this host. A connected client lists the full
catalog after sign-in. The discovery read and the 97-tool catalog below are from 2026-10-30.

## Discovery

An unauthenticated `initialize` (protocol `2025-03-26`, `Accept:
application/json, text/event-stream`, header `MCP-Protocol-Version`) returns
HTTP 401, body `{"error":"unauthorized"}`, and:

```text
WWW-Authenticate: Bearer resource_metadata="https://mcp.qbraid.com/.well-known/oauth-protected-resource/mcp"
```

The protected-resource document for `/mcp` is:

```json
{
  "resource": "https://mcp.qbraid.com/mcp",
  "authorization_servers": ["https://mcp.qbraid.com"],
  "bearer_methods_supported": ["header"]
}
```

The host document is the same shape with `"resource": "https://mcp.qbraid.com"`.
The authorization-server metadata and the OpenID configuration are the same
document:

```json
{
  "issuer": "https://mcp.qbraid.com",
  "authorization_endpoint": "https://mcp.qbraid.com/mcp/oauth/authorize",
  "token_endpoint": "https://mcp.qbraid.com/mcp/oauth/token",
  "registration_endpoint": "https://mcp.qbraid.com/mcp/oauth/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none"],
  "scopes_supported": ["openid", "email", "profile"],
  "client_id_metadata_document_supported": true
}
```

The client is public: the token endpoint takes no client secret, PKCE is
S256, and the grants are authorization code and refresh token. The bearer
token travels in the `Authorization` header. Dynamic client registration is
`POST /mcp/oauth/register`. Scopes are `openid`, `email`, and `profile`.

The REST key in [README.md](README.md) is a different credential. Sending it
as `Authorization: Bearer` or as `X-API-Key` on the same `initialize` request
returns HTTP 401 and `{"error":"unauthorized"}`. The tool catalog stays
behind the OAuth bearer token.

Repeat the challenge read with:

```sh
curl -sS -D - -o /dev/null -X POST https://mcp.qbraid.com/mcp \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' \
  -H 'MCP-Protocol-Version: 2025-03-26' \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
```

## Published tools

The vendor page says the server exposes 80 or more tools and prints the
examples in the table below. A Claude Code session signed in on 2026-10-30
completed `initialize` and `tools/list`. The server identifies itself as
`qbraid` version 1.0.0, negotiates protocol `2025-03-26`, and advertises a
`tools` capability. That `initialize` response carried no `Mcp-Session-Id`,
and `tools/list` still returned one page of 97 tools. The names and hints
below are that page. The effect column is the tool's own first sentence,
shortened where the sentence was an instruction to the client. No tool was
called.

| Category | Examples on the vendor page |
|---|---|
| Quantum devices | `list_quantum_devices`, `get_device_details`, `get_device_calibrations` |
| Quantum jobs | `submit_quantum_job`, `estimate_job_cost`, `get_job_result`, `get_job_circuit_diagram` |
| Circuits | `validate_qasm`, `parse_qasm`, `convert_qasm`, `simulate_circuit` |
| Compute | `list_compute_profiles`, `start_server`, `stop_server`, `list_compute_instances` |
| Environments | `list_environments`, `get_environment_details`, `build_kernel` |
| Credits and billing | `get_my_credit_balance`, `list_billing_transactions`, `purchase_personal_credits` |
| Organizations | `get_organization_details`, `invite_organization_members`, `transfer_organization_credits` |
| Learning (qBook) | `list_qbook_articles`, `create_qbook_course`, `enroll_in_qbook_course` |
| Files | `list_files`, `read_file` |
| Support | `create_support_ticket`, `list_support_tickets` |

Server hints are the tool annotations from that `tools/list`. `read-only`
is `readOnlyHint: true`. `writes` is `readOnlyHint: false`. `destructive`,
`idempotent`, and `open-world` are the matching hints when the server set
them. Several tools whose names only fetch a record are still marked
`writes` and `destructive`, including `get_job_details`, `get_job_result`,
and `get_qbook_processing_status`. The hint is what the server sent.

### Account and organization

| Tool | Server hints | Effect |
|---|---|---|
| `get_user_context` | read-only | Returns the signed-in user's profile and the organizations they belong to, including each organization's slug. |
| `get_organization_details` | read-only | Get detailed information about a specific organization |
| `get_organization_members` | read-only | Get list of members in an organization. |
| `get_organization_usage` | writes, idempotent | An organization's disk usage and compute hours, plus the signed-in user's member wallet. |
| `get_my_membership` | read-only | What the CALLER can do in an organization: their roles, membership status, and permission overrides. |
| `list_my_organization_invitations` | read-only | List the caller's own pending organization invitations (organizations they have been invited to but not yet joined). |
| `invite_organization_member` | writes, destructive, open-world | Invite a single user to an organization by email, optionally granting them qBraid credits. |
| `invite_organization_members` | writes, destructive, open-world | Invite users to an organization by email (up to 100 per call). |
| `resend_organization_invitation` | writes, destructive, open-world | Re-send the invitation email to a member whose invite is still pending. |
| `cancel_organization_invitation` | writes, destructive, idempotent | Remove someone from an organization. |
| `change_organization_member_role` | writes, destructive, idempotent | Set a member's role in an organization, replacing their current one. |
| `set_organization_member_status` | writes, destructive, idempotent | Suspend, deactivate or reactivate a member without removing them — their membership and history survive, but suspended and inactive members lose access. |
| `get_organization_wallet` | read-only | The organization's credit balance. |
| `transfer_organization_credits` | writes, destructive | Move qBraid credits between an organization's wallet and one member's wallet, in either direction. |
| `transfer_organization_credits_bulk` | writes, destructive | Move credits from the organization wallet to MANY named members in one call. |
| `purchase_organization_credits` | writes, open-world | Create a Stripe checkout link to buy credits for an organization. |
| `request_organization_credits` | writes | Ask an organization's admins or owner to grant you credits from the organization wallet. |
| `list_my_credit_requests` | read-only | Your own credit requests to an organization and their status. |
| `cancel_my_credit_request` | writes, destructive, idempotent | Withdraw a credit request you submitted. |
| `list_credit_requests` | read-only | All members' credit requests for an organization, for review. |
| `approve_credit_request` | writes, destructive, idempotent | Approve a member's credit request, moving credits from the organization wallet to that member. |
| `reject_credit_request` | writes, idempotent | Decline a member's credit request. |
| `list_member_credit_transactions` | read-only | Credit movements for one organization member — grants, transfers and deductions. |

### Circuits

| Tool | Server hints | Effect |
|---|---|---|
| `validate_qasm` | read-only | Check whether an OpenQASM program is well-formed, and get its shape. |
| `parse_qasm` | read-only | Turn an OpenQASM program into qubit and classical-bit counts plus a gate list. |
| `convert_qasm` | read-only | Translate a program between OpenQASM 2.0 and 3.0 and return the converted source, plus warnings for anything that could not be expressed exactly in the target version. |
| `simulate_circuit` | read-only | Run an OpenQASM program on qBraid's built-in state-vector simulator and get the output probability distribution keyed by bitstring, along with the qubit count. |

### Files and notifications

| Tool | Server hints | Effect |
|---|---|---|
| `list_files` | read-only | List the files and folders in the user's qBraid Lab home directory, one level at a time. |
| `read_file` | read-only | Read the text content of one file in the user's Lab home directory. |
| `list_notifications` | read-only | List the user's qBraid notifications, newest first. |
| `mark_notification_read` | writes, idempotent | Mark one notification as read, by id from list_notifications. |

### qBook

| Tool | Server hints | Effect |
|---|---|---|
| `list_qbook_articles` | read-only | Browse qBook, qBraid's learning content: courses (structured, with chapters and enrollled students) or blog posts. |
| `get_qbook_article` | read-only | Catalog detail for a single qBook article: description, tags, visibility, and for a course its structure. |
| `get_qbook_content` | read-only | The lesson text of a qBook course or blog post, plus the chapter outline and kernel. |
| `list_my_qbook_articles` | read-only | qBook articles the caller AUTHORS or collaborates on, including unpublished drafts hidden from the public catalog in list_qbook_articles. |
| `get_qbook_processing_status` | writes, destructive, open-world | Check asynchronous course processing by customId. |
| `enroll_in_qbook_course` | writes, idempotent | Enroll the caller in a qBook course. |
| `list_my_course_enrollments` | read-only | The courses the CALLER is enrollled in, with their own progress, enrolllment status and certificate state. |
| `list_qbook_questions` | read-only | Find question-bank entries you created or collaborate on in the selected organization. |
| `get_qbook_question` | read-only | Read the complete authoring content, including correct answers and rubrics. |
| `create_qbook_mcq_question` | writes, open-world | Create an instructor-authored multiple-choice question, including agent-generated content. |
| `update_qbook_mcq_question` | writes, destructive, open-world | Edit a question you may manage. |
| `create_qbook_frq_question` | writes, open-world | Create an instructor-authored free-response question, including agent-generated content. |
| `update_qbook_frq_question` | writes, destructive, open-world | Edit a question you may manage. |
| `delete_qbook_question` | writes, destructive, idempotent, open-world | Permanently delete a question you may manage and its owned attachments. |
| `copy_qbook_questions` | writes, open-world | Copy up to 100 MCQ or free-response questions within an organization or into another organization. |
| `create_qbook_course` | writes, destructive, open-world | Create a qBook course from GitHub notebooks, or retry an existing course with the same name when processing failed, has not started, or produced no openable lessons. |
| `update_qbook_course` | writes, destructive, idempotent, open-world | Update an existing qBook course by customId. |

### Devices, jobs, and hub

| Tool | Server hints | Effect |
|---|---|---|
| `list_quantum_providers` | read-only | List the global, publicly visible quantum computing providers on qBraid. |
| `get_provider_details` | read-only | Get the description and resource links for a global quantum provider (organization-owned providers cannot be resolved by this tool). |
| `list_quantum_devices` | read-only | List available quantum computing devices and simulators on qBraid |
| `get_device_details` | read-only | Get detailed information about a specific quantum device including specs, availability, and pricing |
| `get_device_calibrations` | read-only | The most recent calibration snapshot for a quantum device. |
| `estimate_job_cost` | read-only | Price a job in credits before submitting it. |
| `submit_quantum_job` | writes, destructive, open-world | Submit a quantum job to run on a quantum device or simulator. |
| `list_recent_jobs` | read-only | List recent quantum computing jobs submitted by the user, sorted by creation date |
| `get_job_details` | writes, destructive, idempotent | Get detailed information about a specific quantum job by its QRN. |
| `get_job_result` | writes, destructive, idempotent | Get the measurement results of a completed quantum job. |
| `get_job_program` | read-only | Fetch the source program submitted with a job, and optionally the compiled program the device ran. |
| `get_job_circuit_diagram` | read-only | Render the job's circuit as an ASCII diagram — the qubit-wire drawing with gates laid out in columns. |
| `cancel_job` | writes, destructive, idempotent, open-world | Cancel a pending or running quantum job. |
| `list_job_groups` | writes, idempotent | List job groups that bundle related jobs. |
| `get_job_group` | writes, idempotent | Details of one job group, and with includeJobs:true the jobs inside it. |
| `cancel_job_group` | writes, destructive, idempotent, open-world | Cancel every job in a group. |
| `list_hub_projects` | read-only | List open-source quantum computing projects from the qBraid Hub Explore page (account.qbraid.com/explore), optionally filtered by tags. |

### Product reference

| Tool | Server hints | Effect |
|---|---|---|
| `info_platform` | read-only | qBraid platform overview: qBraid Lab, VS Code, environment manager, compute resources, and key features |
| `info_cli` | read-only | Complete qBraid CLI reference with all confirmed commands and examples |
| `info_sdk` | read-only | qBraid SDK reference: transpilation, providers, runtime, supported frontends |
| `info_core` | read-only | qbraid-core reference: low-level Python client for qBraid cloud services |
| `info_providers` | read-only | Quantum provider setup guides: QbraidProvider, BraketProvider (AWS), QiskitRuntimeProvider (IBM), IonQProvider, AzureQuantumProvider |

### Lab compute

| Tool | Server hints | Effect |
|---|---|---|
| `list_compute_profiles` | read-only | List available compute profiles (CPU and GPU instances) for launching JupyterLab or VS Code environments |
| `get_compute_profile` | read-only | Get detailed information about a specific compute profile including resources, pricing, and availability. |
| `get_server_status` | writes, idempotent | Get the current status of the user's JupyterHub server. |
| `start_server` | writes, destructive | Start a paid JupyterHub compute server with a specific compute profile. |
| `stop_server` | writes, destructive, idempotent | Stop the user's currently running JupyterHub compute server. |
| `list_server_ssh_keys` | writes, idempotent | List the SSH public keys installed on the user's running Lab server. |
| `install_server_ssh_key` | writes, destructive | Install an SSH public key on the user's currently RUNNING lab server, enabling direct SSH access (editor remote mode, scp, rsync). |
| `remove_server_ssh_key` | writes, destructive, idempotent | Remove an SSH public key from the user's currently RUNNING lab server. |
| `list_compute_sessions` | read-only | List the caller's own compute-session history in an organization (start/stop times, duration, compute-hours and credits charged). |
| `get_compute_usage_analytics` | writes, idempotent | Get the caller's daily compute-usage buckets and totals for the last N days in an organization. |
| `list_compute_instances` | read-only | List the caller's on-demand (docker-VM) compute instances that have not been terminated, including STOPPED ones. |

### Billing

| Tool | Server hints | Effect |
|---|---|---|
| `get_my_credit_balance` | read-only | The caller's personal wallet balance. |
| `get_my_subscription` | read-only | Get the caller's subscription snapshot in an organization: tier, status, billing interval, current period end, and whether cancellation is scheduled. |
| `list_billing_transactions` | read-only | List the caller's own credit transactions in an organization (purchases, deductions, transfers, refunds), newest first. |
| `list_billing_invoices` | read-only | List the caller's real-money invoices (amounts, status, dates) from the payment provider, newest first. |
| `purchase_personal_credits` | writes, open-world | Create a Stripe checkout link so the caller can buy credits for their own wallet. |

### Environments and kernels

| Tool | Server hints | Effect |
|---|---|---|
| `list_environments` | read-only | List the qBraid software environments visible to the caller — public ones plus any they own or have been given access to. |
| `get_environment_details` | read-only | Full detail for a single qBraid environment: description, Python version, the installed package list and visibility. |
| `list_kernel_catalog` | read-only | The kernels a qBook course can run on: baseline kernels plus any your organization has built. |
| `build_kernel` | writes, destructive, open-world | Build a new kernel from a Dockerfile so a course can run against it. |
| `get_kernel_build_status` | writes, idempotent | Poll a kernel build started by build_kernel. |
| `list_course_students` | read-only | List enrolled users of a course the caller owns or collaborates on. |
| `get_course_report` | read-only | Compiled analytics for a course the caller owns or collaborates on. |

### Support

| Tool | Server hints | Effect |
|---|---|---|
| `list_support_tickets` | read-only | List the caller's own support tickets, newest first, optionally filtered by status. |
| `get_support_ticket` | read-only | One of the user's own support tickets in full, including the comment thread. |
| `create_support_ticket` | writes, destructive, open-world | File a support ticket with the qBraid team on behalf of the signed-in user. |
| `add_support_ticket_comment` | writes, destructive, open-world | Add a comment to one of the caller's own OPEN support tickets (closed tickets reject comments). |

A job, upload, or other provider action still waits for the owner's approval
of a written case ([Hardware services](../../../AGENTS.md#hardware-services)).
Registering this server and completing OAuth leaves that rule in force. The
free daily simulator allowance in [README.md](README.md) is the budget a case
states. This repository has no qBraid adapter; a first run adds one and a
retained-run directory under `results/qbraid/`.

The captured page prefers `qbraid-cli` at version 0.12 or newer for
programmatic platform actions. [requirements-qbraid.txt](requirements-qbraid.txt)
does not install that CLI. The MCP server is the client integration; the CLI
is a separate program.

## Client registration

The URL is registered on this host. Sign-in is a browser authorization-code
flow with PKCE. qBraid's page already allows the Grok redirect, and it asks
for a support request that includes the full URL when a client stops on
`redirect_mismatch`.

| Client | Entry | Sign-in |
|---|---|---|
| Claude Code | user scope, HTTP, `https://mcp.qbraid.com/mcp` | `claude mcp login qbraid`, or `/mcp` inside Claude Code. `claude mcp get qbraid` reports Connected after the 2026-10-30 sign-in |
| Codex | `[mcp_servers.qbraid]` `url` in `~/.codex/config.toml`, enabled | `codex mcp login qbraid` completed on 2026-10-30 and reported a successful login |
| Grok | `[mcp_servers.qbraid]` `url` and `oauth_scopes` in `~/.grok/config.toml`, enabled | Grok opens the browser flow when a session connects. The MCP commands are list, add, remove, enable, disable, and doctor. `grok mcp doctor qbraid` starts the URL and stops at `AuthRequired` with the `WWW-Authenticate` challenge above. An already open session keeps the server list it started with |
| agy and Gemini CLI | `serverUrl` in `~/.gemini/config/mcp_config.json`, timeout 300000 ms, enabled | both CLIs share that file. Their `mcp` commands are add, remove, list, enable, and disable. The app starts OAuth when it connects |
| Vibe | `[[mcp_servers]]` name `qbraid`, `transport = "streamable-http"`, and `[mcp_servers.auth]` `type = "oauth"` with the three scopes, in `~/.vibe/config.toml` | `/mcp` inside Vibe runs the login. The loopback callback is `http://127.0.0.1:47823/callback`. There is no `vibe mcp` subcommand |

`oauth_scopes` on the Grok entry, and `scopes` on the Vibe entry, are
`openid`, `email`, and `profile`, matching `scopes_supported`. Claude Code
and Codex take those scopes from the authorization server during
`mcp login`. agy and Gemini CLI keep the URL and discover the same server
when they connect.
