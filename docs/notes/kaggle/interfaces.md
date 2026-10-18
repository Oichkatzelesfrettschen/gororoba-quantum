# Kaggle interfaces: CLI, kagglesdk, MCP and the web API

Four interfaces reach the same Kaggle backend, and they differ exactly where
running and stopping a kernel needs them to agree: which version a call
addresses, where a session id comes from, and which one can cancel. The
inventories below were read on 2026-10-16 from kaggle 2.2.4 (the `kaggle`
CLI), kagglesdk 0.1.37 and the Kaggle MCP server at
`https://www.kaggle.com/mcp` (server `Kaggle.Web` 1.0.0.0, MCP protocol
2025-06-18, 76 tools). kagglehub 1.0.2 is a fifth client built on kagglesdk;
[libraries.md](libraries.md) covers the packages themselves.

## Findings for running and stopping kernels

- **The CLI drops the version from `OWNER/SLUG/N`.** `KaggleApi.kernels_status`,
  `kernels_output`, `kernels_logs` and `kernels_pull` parse the suffix
  (`parse_kernel_string`) and build `ApiGetKernelSessionStatusRequest`,
  `ApiListKernelSessionOutputRequest` or `ApiGetKernelRequest` without
  setting `version_label`, so every one of them answers for the latest
  version. Measured: `kaggle kernels output
  probablyeric/gororoba-atlas-detuning-map/3` and `.../5` both wrote the log
  of version 8 (sha256 prefix `cf5204b8884d`; version 3's log is
  `dbbffe800a05`). `scripts/kaggle_run.py collect` therefore reads a run's
  version through kagglesdk `ListKernelSessionOutput` with `version_label
  vN` and writes the CLI's layout (`download_version`): on one kernel,
  version 1 returns its exit code 3 where `kernels output .../1` returned
  version 2's 0. Every retained versioned run under results/kaggle/ (18
  runs) holds its own version's log: each was collected before its slug's
  next push, under the earlier CLI path.
- **Per-version reads exist outside the CLI.** kagglesdk's `version_label`
  and the MCP tools' `versionLabel` select a version when given as `vN`:
  `get_kernel`, `get_kernel_session_status` and
  `list_kernel_session_output` (MCP `get_notebook_info`,
  `get_notebook_session_status`, `list_notebook_session_output`) return
  version 3's metadata, status and log for `v3`. A bare `3` fails (kagglesdk
  HTTP 404; MCP "Kernel version with label '3' not found"), and omitting the
  label returns the latest version. kagglesdk `download_kernel_output`
  (MCP `download_notebook_output`) takes an integer `version_number`, which
  `kagglehub.notebook_output_download("OWNER/SLUG/versions/N")` sets.
- **A running version's session id comes only from the web API.** Each
  version runs as one session whose id is its `scriptVersionId`.
  `kernels.KernelsService/ListKernelVersions` returns every version's id and
  status ([workflow.md](workflow.md), "Accelerator sessions";
  `scripts/kaggle_sessions.py versions`). The public interfaces return no
  id field. A version that has written output exposes its id indirectly:
  the file URLs `list_kernel_session_output` returns sit under
  `www.kaggleusercontent.com/kf/<scriptVersionId>/`, and for versions 3 and 8
  of gororoba-atlas-detuning-map those numbers equal the ids
  ListKernelVersions reports. A running version with no output yet is not
  covered by that observation.
- **Cancel takes the session id.** The CLI has no cancel command. kagglesdk
  `cancel_kernel_session` and MCP `cancel_notebook_session` take
  `kernel_session_id` / `kernelSessionId`; the MCP tool is the one this
  repository has exercised (status moves to CANCEL_REQUESTED, then
  CANCEL_ACKNOWLEDGED). The kagglesdk call is unexercised here.
- **Reserved time shows a live accelerator session.** kagglesdk
  `get_accelerator_quota_statistics` and MCP `get_accelerator_quota` return
  `time_used`, `time_reserved` and `total_time_allowed` per GPU and TPU
  quota. `kaggle quota` (table, CSV or JSON) prints used, remaining, total
  and refresh time and omits `time_reserved`, so it cannot show a running
  session.
- **Only a saved version takes a timeout.** `session_timeout_seconds`
  exists on `ApiSaveKernelRequest` (CLI `kernels push -t`, MCP
  `save_notebook` `sessionTimeoutSeconds`). `ApiCreateKernelSessionRequest`
  and MCP `create_notebook_session` carry no timeout field, so an
  interactive session ends at Kaggle's own limits (12 h per session, 20 idle
  minutes; [site/notebooks.md](site/notebooks.md)).

## Operation matrix

`vN` marks a call that addresses a version through a version label. kagglesdk
entries read `<area>.<method>`, reached as `kaggle.<area>.<client>.<method>`
(full client names in the inventory below).

| Operation | CLI (`kaggle`) | kagglesdk client method | MCP tool | kagglehub | Web only |
| --- | --- | --- | --- | --- | --- |
| Save and run a kernel version | `kernels push -p DIR [-t S] [--accelerator ID]` | `kernels.save_kernel` | `save_notebook` | -- | editor "Save Version" (the only route to a TPU on this account) |
| Kernel metadata and source | `kernels pull [-m]` (latest only) | `kernels.get_kernel` (`vN`) | `get_notebook_info` (`vN`) | -- | -- |
| Version status | `kernels status` (latest only) | `kernels.get_kernel_session_status` (`vN`) | `get_notebook_session_status` (`vN`) | -- | `ListKernelVersions` lists every version |
| Version list with session ids | -- | -- | -- | -- | `kernels.KernelsService/ListKernelVersions` |
| Output listing and log | `kernels output`, `kernels logs [-f]` (latest only) | `kernels.list_kernel_session_output` (`vN`), `kernels.get_kernel_session_logs_stream` (session id) | `list_notebook_session_output` (`vN`) | -- | version page |
| Output download | `kernels output [--file-pattern RE]` (latest only) | `kernels.download_kernel_output` (`version_number`), `kernels.download_kernel_output_zip` (session id) | `download_notebook_output` (`versionNumber`), `download_notebook_output_zip` (session id) | `notebook_output_download("OWNER/SLUG/versions/N")` | -- |
| Interactive session create | -- | `kernels.create_kernel_session` | `create_notebook_session` | -- | editor |
| Session cancel | -- | `kernels.cancel_kernel_session` | `cancel_notebook_session` | -- | version page Stop |
| Accelerator quota | `quota` (no reserved time) | `kernels.get_accelerator_quota_statistics` | `get_accelerator_quota` | -- | account settings |
| Kernel list, files, delete | `kernels list`, `kernels files`, `kernels delete` | `kernels.list_kernels`, `list_kernel_files`, `delete_kernel` | `search_notebooks`, `list_notebook_files` (no delete) | -- | -- |
| Datasets: read | `datasets list`, `files`, `download`, `metadata`, `status` | `datasets.list_datasets`, `get_dataset`, `list_dataset_files`, `list_tree_dataset_files`, `get_dataset_metadata`, `get_dataset_status`, `get_dataset_files_summary`, `download_dataset`, `download_dataset_raw` | `search_datasets`, `get_dataset_info`, `list_dataset_files`, `list_dataset_tree_files`, `get_dataset_metadata`, `get_dataset_status`, `get_dataset_files_summary`, `download_dataset` | `dataset_download`, `dataset_load` | -- |
| Datasets: write | `datasets create`, `version`, `metadata --update`, `delete`, `files upload` | `datasets.create_dataset`, `create_dataset_version`, `create_dataset_version_by_id`, `update_dataset_metadata`, `upload_dataset_file`, `delete_dataset`, `blobs.start_blob_upload` | `update_dataset_metadata`, `upload_dataset_file` | `dataset_upload` | -- |
| Models: read | `models list`, `get`; `models instances get`, `files`, `list`; `models instances versions list`, `files`, `download` | `models.list_models`, `get_model`, `list_model_instances`, `get_model_instance`, `list_model_instance_versions`, `list_model_instance_version_files`, `download_model_instance_version` | `list_models`, `get_model`, `list_model_variations`, `get_model_variation`, `list_model_variation_versions`, `list_model_variation_version_files`, `download_model_variation_version` | `model_download` | -- |
| Models: write | `models create`, `update`, `delete`; `models instances create`, `update`, `delete`; `models instances versions create`, `delete` | `models.create_model`, `update_model`, `delete_model`, `create_model_instance`, `update_model_instance`, `delete_model_instance`, `create_model_instance_version`, `delete_model_instance_version`, `upload_model_file` | `create_model`, `update_model`, `update_model_variation` | `model_upload` | -- |
| Competitions: read | `competitions list`, `files`, `download`, `leaderboard`, `submissions`, `submission-limits`, `pages list`, `hosts`, `episodes`, `replay`, `logs`, `team-submissions` | `competitions.list_competitions`, `get_competition`, `list_data_files`, `list_data_tree_files`, `download_data_file(s)`, `get_leaderboard`, `download_leaderboard`, `list_submissions`, `get_submission`, `download_submission`, `get_submission_limits`, `list_competition_pages`, `list_competition_hosts`, `list_submission_episodes`, `get_episode_replay`, `get_episode_agent_logs`, `list_team_public_submissions` | `search_competitions`, `get_competition`, `list_competition_data_files`, `list_competition_data_tree_files`, `download_competition_data_file(s)`, `get_competition_leaderboard`, `download_competition_leaderboard`, `search_competition_submissions`, `get_competition_submission`, `download_competition_submission`, `list_competition_pages`, `list_submission_episodes`, `get_episode_replay`, `get_episode_agent_logs`, `list_team_public_submissions` | `competition_download` | -- |
| Competitions: submit | `competitions submit` | `competitions.create_submission`, `create_code_submission`, `start_submission_upload` | `submit_to_competition`, `create_code_competition_submission`, `start_competition_submission_upload` (all denied on this host) | -- | -- |
| Competitions: host and create | `competitions init`, `create`, `launch`, `data update`, `settings get/update`, `solution create/status`, `pages create/update/delete` | `competitions.create_competition`, `launch_competition`, `create_competition_data`, `get/update_competition_settings`, `create_competition_solution`, `get_competition_solution_status`, `create_competition_sample_submission`, `create/update/delete_competition_page`, `add_competition_host`, `list/add_competition_judge` | -- | -- | -- |
| Hackathons | -- | `competitions.list_hackathon_tracks`, `get_hackathon_overview`, `list_hackathon_write_ups`, `get_hackathon_write_up`, `export_hackathon_write_ups_csv`, `export_enriched_hackathon_write_ups_csv` | `list_hackathon_tracks`, `get_hackathon_overview`, `list_hackathon_write_ups`, `get_hackathon_write_up`, `download_hackathon_write_ups` | -- | -- |
| Benchmarks | `benchmarks tasks push`, `run`, `list`, `status`, `download`, `log`, `models`, `delete`, `publish`; `benchmarks auth`, `init`, `leaderboard` | `benchmarks.create_benchmark_task`, `batch_schedule_benchmark_task_runs`, `list_benchmark_tasks`, `get_benchmark_task`, `list_benchmark_task_runs`, `download_benchmark_task_run_output`, `get_benchmark_task_run_logs`, `get_benchmark_task_quota`, `publish_benchmark_task`, `get_benchmark_leaderboard`, model-version configs and agent mappings | `get_benchmark_leaderboard`, `create_benchmark_task_from_prompt`, `get/create/update_benchmark_arena_settings`, `list/update_benchmark_arena_combinations` | -- | -- |
| Forums, topics, writeups | `forums list`, `forums topics list/show`, `competitions topics list/show`, `competitions topic-messages`, `{datasets,kernels,models,benchmarks} topics list/show` | `discussions.list_forums`, `list_topics`, `get_topic`, `list_comments`, `list_{dataset,model,benchmark,kernel}_topics`, `get_resolved_write_up_links`, `competitions.list_competition_topics`, `list_topic_messages` | `list_forums`, `get_forum`, `list_forum_topics`, `get_forum_topic`, `list_competition_topics`, `list_topic_messages`, `get_writeup`, `get_writeup_by_slug`, `get_writeup_by_topic`, `get_resolved_writeup_links` | -- | -- |
| Search across content types | -- | `search.list_entities` | `search_content` | -- | -- |
| User identity and profile | `config view` (configured username) | -- | `get_user_profile` | `whoami()` | profile page |
| Authentication | `auth login`, `auth print-access-token`, `auth revoke` | `security.start_oauth_flow`, `exchange_oauth_token`, `introspect_token`, `users.generate_access_token`, `expire_api_token` | `authorize` | `login()` | sign-in |
| Packages and utility scripts | -- | -- | -- | `package_import`, `utility_script_install`, `get_package_asset_path` | -- |

## Accelerator, image and timeout fields

| Setting | kernel-metadata.json (read by `kernels push`) | CLI flag | `ApiSaveKernelRequest` / MCP `save_notebook` | `ApiCreateKernelSessionRequest` / MCP `create_notebook_session` |
| --- | --- | --- | --- | --- |
| Machine shape | `machine_shape` | `--accelerator ID` | `machine_shape` / `machineShape` | `machine_shape` / `machineShape` |
| GPU flag (deprecated for `machine_shape`) | `enable_gpu` | -- | `enable_gpu` / `enableGpu` | -- |
| TPU flag (deprecated for `machine_shape`) | `enable_tpu` | -- | `enable_tpu` / `enableTpu` | -- |
| Docker image | `docker_image` | -- | `docker_image` / `dockerImage` | `docker_image` / `dockerImage` |
| Image pinning | `docker_image_pinning_type` | -- | `docker_image_pinning_type` / `dockerImagePinningType` | -- |
| Run-time limit | -- | `-t, --timeout SECONDS` | `session_timeout_seconds` / `sessionTimeoutSeconds` | -- |
| Internet | `enable_internet` | -- | `enable_internet` / `enableInternet` | `enable_internet` / `enableInternet` |
| Kernel type | `kernel_type` (`script`, `notebook`) | -- | `kernel_type` / `kernelType` | `kernel_type` / `kernelType` |
| Execution type | -- | -- | `kernel_execution_type` / `kernelExecutionType` (`SaveAndRunAll`, `InterActive`, `QuickSave`) | -- |
| Queue priority | -- | -- | `priority` (restricted to certain clients) | -- |

- `KaggleApi.kernels_push` sets `request.machine_shape` to `--accelerator`
  when given and to the metadata's `machine_shape` otherwise, so both routes
  fill the same request field. [workflow.md](workflow.md) records that
  probes setting only the metadata field ran on CPU machines while
  `--accelerator` selected the hardware; the CLI source does not explain
  that difference, and it remains a measured behavior of the service.
- The `machine_shape` docstrings in kagglesdk name `NvidiaTeslaT4`,
  `NvidiaTeslaP100` and `Tpu1VmV38`. The live accelerator list
  ([cli/kernels.md](cli/kernels.md)) has replaced the last two, and a
  `NvidiaTeslaP100` request ran on two T4s.
- `kernels push` also reads `keywords` (tag ids) and `kernel_sources`,
  `model_sources`, `competition_sources` and `dataset_sources`; the captured
  [cli/kernels_metadata.md](cli/kernels_metadata.md) omits `enable_tpu`,
  `docker_image` and `docker_image_pinning_type`.
- The captured [cli/kernels.md](cli/kernels.md) (kaggle-cli commit 931014d)
  documents `kernels push --no-run`; the installed 2.2.4 accepts only `-p`,
  `-t` and `--accelerator`.

## Capabilities unique to each interface

- **CLI.** Pushes a local folder after validating kernel-metadata.json
  (language, kernel type, source references), strips notebook outputs
  before upload, scaffolds metadata (`kernels init`, `datasets init`,
  `models init`), follows a log (`kernels logs -f`), converts a percent
  script to a notebook for `benchmarks tasks push` (jupytext), drives
  competition creation (pages, settings, solution, launch), runs the OAuth
  sign-in (`auth login`) and prints tables, CSV or JSON.
- **kagglesdk.** Every call the CLI makes, plus interactive session create
  and cancel, version-labeled reads, output download by session id, log
  streaming by session id, agents and harnesses, model-proxy quotas and
  tokens, IAM policies, group memberships, hackathon CSV exports and
  long-running operation polling.
- **MCP.** A user's public profile, cross-type content search, writeups and
  their resolved links, forum details, benchmark arena settings and
  combinations, and benchmark task creation from a prompt. It has no kernel
  delete and no dataset or model-variation creation.
- **kagglehub.** Version-pinned notebook output download, a local cache,
  dataset loading into pandas, polars or Hugging Face datasets
  (`dataset_load`), and Kaggle Packages (`package_import`) and utility
  scripts.
- **Web only.** `ListKernelVersions` (every version with session id and
  status, and `run.isTpuEnabled` on a version the server classified as a
  TPU session), `GetKernelSessionLog` (request `{"sessionId": N}`; empty
  while the session is queued), the editor's interactive TPU sessions, and
  the version page's Stop button. Batch sessions are capped per account at
  five CPU, two GPU and one TPU, each refused at push time with "Maximum
  batch CPU/GPU/TPU session count of N reached"; the caps are separate from
  the weekly GPU and TPU quotas.

## Authentication

| Interface | Credential source, in resolution order |
| --- | --- |
| CLI | `KaggleApi.authenticate`: an access token (`KAGGLE_API_TOKEN`, else `~/.kaggle/access_token`), then a legacy key (`KAGGLE_USERNAME` and `KAGGLE_KEY`, else `~/.kaggle/kaggle.json`), then the OAuth credentials `kaggle auth login` writes to `~/.kaggle/credentials.json`, then anonymous access where a command allows it |
| kagglesdk | `KaggleHttpClient` sends `Authorization: Bearer` with the access token (`KAGGLE_API_TOKEN`, else `~/.kaggle/access_token`), else basic auth from `~/.kaggle/kaggle.json`; `KaggleApi().authenticate()` then `api.build_kaggle_client()` gives a client carrying the CLI's resolved credentials |
| kagglehub | the same access-token lookup, then `KAGGLE_USERNAME` and `KAGGLE_KEY`, then `~/.kaggle/kaggle.json`, then Colab secrets; `credentials.json` is not read |
| MCP | `Authorization: Bearer` with the same `KGAT` access token; Claude Code registers the server as an HTTP MCP server at `https://www.kaggle.com/mcp` whose `headersHelper` runs `~/.config/shell/kaggle-mcp-headers.sh`, because Kaggle's OAuth discovery leads Claude Code's own sign-in into a failing client-secret flow; `scripts/kaggle_sessions.py` calls the same helper |
| Web API | a signed-in browser session: cookies plus the page's `XSRF-TOKEN` echoed as `x-xsrf-token` |

This host keeps `~/.kaggle/access_token` and `~/.kaggle/credentials.json`
at mode 600 and no `kaggle.json`, so the CLI, kagglesdk, kagglehub and the
MCP helper all authenticate with the access token. kagglesdk sends every
call as `POST https://api.kaggle.com/v1/<service>/<Rpc>` with the request as
JSON (`KaggleHttpClient._prepare_request`); the REST path and HTTP method a
request type declares (`endpoint_path()`, `method()`) are metadata the
client does not send.

## What this repository uses for which job

| Job | Interface | Code |
| --- | --- | --- |
| Bundle and push a kernel; refuse a GPU or TPU push without `--timeout` or over a live version | CLI `kernels push --accelerator -t`, `kernels status`, `config view` | `scripts/kaggle_run.py push` |
| Poll a run | CLI `kernels status OWNER/SLUG/N` (answers for the latest version) | `scripts/kaggle_run.py status` |
| Download and ledger a run's output | kagglesdk `list_kernel_session_output` with `version_label vN` (the CLI's `kernels output` downloads the latest version) | `scripts/kaggle_run.py collect` |
| Retain repository files as a dataset | CLI `datasets create`, `datasets version` | `scripts/kaggle_run.py dataset` |
| A kernel's numeric id | CLI `kernels pull -m` (`id_no`) | `scripts/kaggle_sessions.py` |
| Every version's session id and status | web API `ListKernelVersions` through headless Firefox | `scripts/kaggle_sessions.py versions` |
| Quota and cancel | MCP `get_accelerator_quota`, `cancel_notebook_session` over HTTP | `scripts/kaggle_sessions.py quota`, `cancel`, `cancel-running` |
| Agent reads and interactive control | MCP tools in a Claude Code session, under the policy below | -- |

## MCP permission policy on this host

`~/.claude/settings.json` (user scope) classifies every served tool:

- **Allow** (4 rules, 60 tools): `mcp__kaggle__get_*`, `list_*`,
  `search_*` and `download_*`.
- **Ask** (18 rules): `authorize`, `save_notebook`,
  `create_notebook_session`, `cancel_notebook_session`, `create_dataset`,
  `create_dataset_version`, `create_dataset_version_by_id`,
  `upload_dataset_file`, `update_dataset_metadata`, `create_model`,
  `create_model_variation`, `create_model_variation_version`,
  `update_model`, `update_model_variation`,
  `create_benchmark_task_from_prompt`, `create_benchmark_arena_settings`,
  `update_benchmark_arena_settings`, `update_benchmark_arena_combinations`.
  Thirteen of them match served tools; `create_dataset`,
  `create_dataset_version`, `create_dataset_version_by_id`,
  `create_model_variation` and `create_model_variation_version` appear in
  the captured [site/mcp.md](site/mcp.md) and not in the live tool list.
- **Deny** (3 rules): `submit_to_competition`,
  `create_code_competition_submission`,
  `start_competition_submission_upload`. A Claude Code session lists the
  other 73 tools.

The repository's untracked `.claude/settings.local.json` also allows
`mcp__kaggle__save_notebook` and `mcp__kaggle__cancel_notebook_session`,
which the user scope lists under ask.

## Live tool list against the captured documentation

The live `tools/list` returns 76 tools; [site/mcp.md](site/mcp.md),
captured 2026-10-16T03:13Z, documents 56.

- **Served, undocumented (25):** `authorize`,
  `create_benchmark_arena_settings`, `download_competition_submission`,
  `get_accelerator_quota`, `get_benchmark_arena_settings`,
  `get_episode_agent_logs`, `get_episode_replay`, `get_forum`,
  `get_forum_topic`, `get_resolved_writeup_links`, `get_user_profile`,
  `get_writeup`, `get_writeup_by_slug`, `get_writeup_by_topic`,
  `list_benchmark_arena_combinations`, `list_competition_pages`,
  `list_competition_topics`, `list_forums`, `list_forum_topics`,
  `list_submission_episodes`, `list_team_public_submissions`,
  `list_topic_messages`, `search_content`,
  `update_benchmark_arena_combinations`, `update_benchmark_arena_settings`.
  `scripts/kaggle_sessions.py quota` depends on `get_accelerator_quota`
  from this set.
- **Documented, not served (5):** `create_dataset`, `create_dataset_version`,
  `create_dataset_version_by_id`, `create_model_variation`,
  `create_model_variation_version`.

## Inventories

The tables below are the complete surfaces as read on 2026-10-16. The CLI
table walks the argparse tree `kaggle.cli.main` builds (subcommand parsers
sit in `_name_parser_map`, because `main` replaces `choices` with a help
list); the kagglesdk table reads every `kagglesdk/*/services/*.py` client
method, the `(service, Rpc)` pair it passes to `KaggleHttpClient.call`, its
request type and that type's `endpoint_path()`; the MCP table is the
server's `tools/list` after an `initialize` handshake, with each tool's
`request` properties minus the generated `has*`, `*Nullable` and `*Setter`
companions and `readMask`.

### CLI commands (kaggle 2.2.4)

Top-level aliases: `competitions` is `c`, `datasets` is `d`, `kernels` is
`k`, `models` is `m`, `forums` is `f`, `benchmarks` is `b`, `files upload`
is `files u`. Uppercase entries are positional arguments.

| Command | Aliases | Arguments and options |
| --- | --- | --- |
| `competitions list` |  | `--group` `--category` `--sort-by` `-p, --page` `-s, --search` `-v, --csv` `--format` `--page-size` `--page-token` |
| `competitions files` |  | `COMPETITION` `-c, --competition` `-v, --csv` `--format` `-q, --quiet` `--page-token` `--page-size` |
| `competitions download` |  | `COMPETITION` `-c, --competition` `-f, --file` `-p, --path` `-w, --wp` `-o, --force` `-q, --quiet` |
| `competitions submit` |  | `COMPETITION` `-c, --competition` `-f, --file` `-k, --kernel` `-m, --message` `-v, --version` `-q, --quiet` `--sandbox` |
| `competitions submissions` |  | `COMPETITION` `-c, --competition` `-v, --csv` `--format` `-q, --quiet` `--page-size` `--page-token` |
| `competitions leaderboard` |  | `COMPETITION` `-c, --competition` `-s, --show` `-d, --download` `-p, --path` `-v, --csv` `--format` `-q, --quiet` `--page-size` `--page-token` |
| `competitions team-submissions` |  | `TEAM_ID` `-v, --csv` `--format` `-q, --quiet` |
| `competitions submission-limits` |  | `COMPETITION` `-c, --competition` `--json` `-q, --quiet` |
| `competitions episodes` |  | `SUBMISSION_ID` `-v, --csv` `--format` `-q, --quiet` |
| `competitions replay` |  | `EPISODE_ID` `-p, --path` `-q, --quiet` |
| `competitions logs` |  | `EPISODE_ID` `AGENT_INDEX` `-p, --path` `-q, --quiet` |
| `competitions pages list` |  | `COMPETITION` `-c, --competition` `-v, --csv` `--format` `-q, --quiet` `--content` `--page-name` |
| `competitions pages create` |  | `COMPETITION` `-c, --competition` `--page-name` `-f, --file` `--mime-type` `--post-title` `--publish` `-q, --quiet` |
| `competitions pages update` |  | `COMPETITION` `-c, --competition` `--page-name` `-f, --file` `--new-name` `--mime-type` `--post-title` `--publish` `--unpublish` `-q, --quiet` |
| `competitions pages delete` |  | `COMPETITION` `-c, --competition` `--page-name` `-y, --yes` `-q, --quiet` |
| `competitions hosts` |  | `COMPETITION` `-c, --competition` `-v, --csv` `--format` `-q, --quiet` |
| `competitions data update` |  | `COMPETITION` `-c, --competition` `-p, --path` `-m, --message` `--rerun` `--include-hidden` `-q, --quiet` `--ignore-patterns` |
| `competitions settings get` |  | `COMPETITION` `-c, --competition` `--json` `-q, --quiet` |
| `competitions settings update` |  | `COMPETITION` `-c, --competition` `-f, --from-file` `--json` `-q, --quiet` |
| `competitions solution create` |  | `COMPETITION` `-c, --competition` `-p, --path` `-q, --quiet` |
| `competitions solution status` |  | `COMPETITION` `-c, --competition` `--json` `-q, --quiet` |
| `competitions launch` |  | `COMPETITION` `-c, --competition` `--at` `-q, --quiet` |
| `competitions init` |  | `FOLDER` |
| `competitions create` |  | `-p, --path` |
| `competitions topics list` |  | `-p, --page` `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `COMPETITION` `-c, --competition` `-s, --sort-by` |
| `competitions topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `competitions topic-messages` |  | `COMPETITION` `TOPIC_ID` `-c, --competition` `-s, --sort-by` `-n, --page-size` `-v, --csv` `--format` `-q, --quiet` |
| `datasets delete` |  | `DATASET` `-y, --yes` |
| `datasets list` |  | `--sort-by` `--size` `--file-type` `--license` `--tags` `-s, --search` `-m, --mine` `--user` `--page-size` `--page-token` `-p, --page` `-v, --csv` `--format` `--max-size` `--min-size` |
| `datasets files` |  | `DATASET` `-d, --dataset` `-v, --csv` `--format` `--page-token` `--page-size` |
| `datasets download` |  | `DATASET` `-d, --dataset` `-f, --file` `-p, --path` `-w, --wp` `--unzip` `-o, --force` `-q, --quiet` |
| `datasets create` |  | `-p, --path` `-u, --public` `-q, --quiet` `-t, --keep-tabular` `-r, --dir-mode` `--ignore-patterns` |
| `datasets version` |  | `-m, --message` `-p, --path` `-q, --quiet` `-t, --keep-tabular` `-r, --dir-mode` `-d, --delete-old-versions` `--ignore-patterns` |
| `datasets init` |  | `-p, --path` |
| `datasets metadata` |  | `DATASET` `-d, --dataset` `--update` `-p, --path` |
| `datasets status` |  | `DATASET` `-d, --dataset` `--format` |
| `datasets topics list` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `ENTITY_REF` `--sort-by` `-s, --search` |
| `datasets topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `kernels list` |  | `-m, --mine` `--page-token` `--page-size` `-p, --page` `-s, --search` `-v, --csv` `--format` `--parent` `--competition` `--dataset` `--user` `--language` `--kernel-type` `--output-type` `--sort-by` |
| `kernels files` |  | `KERNEL` `-k, --kernel` `-v, --csv` `--format` `--page-token` `--page-size` |
| `kernels init` |  | `-p, --path` |
| `kernels push` | push: update | `-p, --path` `-t, --timeout` `--accelerator` |
| `kernels pull` | pull: get | `KERNEL` `-k, --kernel` `-p, --path` `-w, --wp` `-m, --metadata` |
| `kernels output` |  | `KERNEL` `-k, --kernel` `-p, --path` `-w, --wp` `-o, --force` `-q, --quiet` `--file-pattern` `--page-size` `--page-token` |
| `kernels status` |  | `KERNEL` `-k, --kernel` |
| `kernels logs` |  | `KERNEL` `-k, --kernel` `-f, --follow` `--interval` |
| `kernels delete` |  | `KERNEL` `-y, --yes` |
| `kernels topics list` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `ENTITY_REF` `--sort-by` `-s, --search` |
| `kernels topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `models instances versions list` | instances: i, variations, v; versions: v | `MODEL_INSTANCE` `-v, --csv` `--format` `--page-size` `--page-token` |
| `models instances versions create` | instances: i, variations, v; versions: v | `MODEL_INSTANCE` `-p, --path` `-n, --version-notes` `-q, --quiet` `-r, --dir-mode` `--ignore-patterns` |
| `models instances versions download` | instances: i, variations, v; versions: v | `MODEL_INSTANCE_VERSION` `-p, --path` `--untar` `-f, --force` `-q, --quiet` |
| `models instances versions files` | instances: i, variations, v; versions: v | `MODEL_INSTANCE_VERSION` `-v, --csv` `--format` `--page-size` `--page-token` |
| `models instances versions delete` | instances: i, variations, v; versions: v | `MODEL_INSTANCE_VERSION` `-y, --yes` |
| `models instances get` | instances: i, variations, v | `MODEL_INSTANCE` `-p, --path` |
| `models instances init` | instances: i, variations, v | `-p, --path` |
| `models instances create` | instances: i, variations, v | `-p, --path` `-q, --quiet` `-r, --dir-mode` `--ignore-patterns` |
| `models instances files` | instances: i, variations, v | `MODEL_INSTANCE` `-v, --csv` `--format` `--page-size` `--page-token` |
| `models instances list` | instances: i, variations, v | `MODEL_INSTANCE` `-v, --csv` `--format` `--page-size` `--page-token` |
| `models instances delete` | instances: i, variations, v | `MODEL_INSTANCE` `-y, --yes` |
| `models instances update` | instances: i, variations, v | `-p, --path` |
| `models get` |  | `MODEL` `-p, --path` |
| `models list` |  | `--sort-by` `-s, --search` `--owner` `--page-size` `--page-token` `-v, --csv` `--format` |
| `models init` |  | `-p, --path` |
| `models create` |  | `-p, --path` |
| `models delete` |  | `MODEL` `-y, --yes` |
| `models update` |  | `-p, --path` |
| `models topics list` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `ENTITY_REF` `--sort-by` `-s, --search` |
| `models topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `files upload` | upload: u | `-i, --inbox-path` `LOCAL_PATHS` `--no-resume` `--no-compress` |
| `forums list` |  | `-v, --csv` `--format` `-q, --quiet` |
| `forums topics list` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `FORUM` `--sort-by` `-s, --search` `--category` `--group` |
| `forums topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `benchmarks tasks push` | tasks: t | `TASK` `-f, --file` `--wait` `--poll-interval` `-v, --verbose` `-d, --kaggle-dataset` |
| `benchmarks tasks run` | tasks: t | `TASK` `-m, --model` `--wait` `--poll-interval` `-v, --verbose` |
| `benchmarks tasks list` | tasks: t | `--name-regex` `--status` `--page-size` `--all` |
| `benchmarks tasks status` | tasks: t | `TASK` `-m, --model` |
| `benchmarks tasks download` | tasks: t | `TASK` `-m, --model` `-o, --output` `-s, --include-source` `-f, --force` |
| `benchmarks tasks log` | tasks: t; log: logs | `TASK` `-m, --model` |
| `benchmarks tasks models` | tasks: t | (none) |
| `benchmarks tasks delete` | tasks: t | `TASK` `-y, --yes` |
| `benchmarks tasks publish` | tasks: t | `TASK` `--no-publish-backing-notebook` |
| `benchmarks auth` |  | `-y, --yes` `--env-file` |
| `benchmarks init` |  | `-y, --yes` `--env-file` `--example-file` |
| `benchmarks leaderboard` |  | `BENCHMARK` `--version` `-s, --show` `-d, --download` `-p, --path` `-q, --quiet` `-v, --csv` `--format` |
| `benchmarks topics list` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `ENTITY_REF` `--sort-by` `-s, --search` |
| `benchmarks topics show` |  | `--page-size` `--page-token` `-v, --csv` `--format` `-q, --quiet` `TOPIC_REF` `TOPIC_ID_ARG` |
| `config view` |  | (none) |
| `config set` |  | `-n, --name` `-v, --value` |
| `config unset` |  | `-n, --name` |
| `auth login` |  | `--no-launch-browser` `--force` |
| `auth print-access-token` |  | `--expiration` |
| `auth revoke` |  | `--reason` |
| `quota` |  | `-v, --csv` `--format` |

### kagglesdk service methods (kagglesdk 0.1.37)

A client is reached as `kaggle.<area>.<client>` inside
`with api.build_kaggle_client() as kaggle:`. The RPC column is what the
client sends (`POST https://api.kaggle.com/v1/<RPC>`); the REST path is the
alias the request type declares, empty where the generated code names none.

| Client (`kaggle.<area>.<client>`) | Method | RPC | Request type | Declared REST path |
| --- | --- | --- | --- | --- |
| `admin.inbox_file_client` | `create_inbox_file` | `admin.InboxFileService/CreateInboxFile` | `CreateInboxFileRequest` |  |
| `agents.agent_exam_client` | `create_agent_exam_agent` | `agents.AgentExamService/CreateAgentExamAgent` | `ApiCreateAgentExamAgentRequest` |  |
| `agents.agent_exam_client` | `get_agent_exam_agent` | `agents.AgentExamService/GetAgentExamAgent` | `ApiGetAgentExamAgentRequest` | `/api/v1/agentExamAgent/{agent_id}` |
| `agents.agent_exam_client` | `create_agent_exam_submission` | `agents.AgentExamService/CreateAgentExamSubmission` | `ApiCreateAgentExamSubmissionRequest` |  |
| `agents.agent_exam_client` | `complete_agent_exam_submission` | `agents.AgentExamService/CompleteAgentExamSubmission` | `ApiCompleteAgentExamSubmissionRequest` |  |
| `agents.agent_exam_client` | `get_agent_exam_submission` | `agents.AgentExamService/GetAgentExamSubmission` | `ApiGetAgentExamSubmissionRequest` | `/api/v1/agentExamSubmission/{submission_id}` |
| `agents.agent_exam_client` | `list_top_agent_exam_agents` | `agents.AgentExamService/ListTopAgentExamAgents` | `ApiListTopAgentExamAgentsRequest` |  |
| `agents.agent_exam_client` | `get_agent_exam_insights` | `agents.AgentExamService/GetAgentExamInsights` | `ApiGetAgentExamInsightsRequest` |  |
| `agents.agents_api_client` | `create_harness` | `agents.AgentsApiService/CreateHarness` | `ApiCreateHarnessRequest` |  |
| `agents.agents_api_client` | `get_harness` | `agents.AgentsApiService/GetHarness` | `ApiGetHarnessRequest` | `/api/v1/agents/harnesses/{id}` |
| `agents.agents_api_client` | `create_harness_version` | `agents.AgentsApiService/CreateHarnessVersion` | `ApiCreateHarnessVersionRequest` |  |
| `agents.agents_api_client` | `get_harness_version` | `agents.AgentsApiService/GetHarnessVersion` | `ApiGetHarnessVersionRequest` | `/api/v1/agents/harnesses/versions/{id}` |
| `agents.agents_api_client` | `list_harnesses` | `agents.AgentsApiService/ListHarnesses` | `ApiListHarnessesRequest` |  |
| `agents.agents_api_client` | `create_agent` | `agents.AgentsApiService/CreateAgent` | `ApiCreateAgentRequest` |  |
| `agents.agents_api_client` | `get_agent` | `agents.AgentsApiService/GetAgent` | `ApiGetAgentRequest` | `/api/v1/agents/{id}` |
| `agents.agents_api_client` | `list_agents` | `agents.AgentsApiService/ListAgents` | `ApiListAgentsRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `create_benchmark_task` | `benchmarks.BenchmarkTasksApiService/CreateBenchmarkTask` | `ApiCreateBenchmarkTaskRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `batch_schedule_benchmark_task_runs` | `benchmarks.BenchmarkTasksApiService/BatchScheduleBenchmarkTaskRuns` | `ApiBatchScheduleBenchmarkTaskRunsRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `list_benchmark_tasks` | `benchmarks.BenchmarkTasksApiService/ListBenchmarkTasks` | `ApiListBenchmarkTasksRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `get_benchmark_task` | `benchmarks.BenchmarkTasksApiService/GetBenchmarkTask` | `ApiGetBenchmarkTaskRequest` | `/api/v1/benchmarks/tasks/{slug.task_slug}` |
| `benchmarks.benchmark_tasks_api_client` | `list_benchmark_task_runs` | `benchmarks.BenchmarkTasksApiService/ListBenchmarkTaskRuns` | `ApiListBenchmarkTaskRunsRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `download_benchmark_task_run_output` | `benchmarks.BenchmarkTasksApiService/DownloadBenchmarkTaskRunOutput` | `ApiDownloadBenchmarkTaskRunOutputRequest` | `/api/v1/benchmarks/tasks/runs/{run_id}/output` |
| `benchmarks.benchmark_tasks_api_client` | `get_benchmark_task_run_logs` | `benchmarks.BenchmarkTasksApiService/GetBenchmarkTaskRunLogs` | `ApiGetBenchmarkTaskRunLogsRequest` | `/api/v1/benchmarks/tasks/runs/{run_id}/logs` |
| `benchmarks.benchmark_tasks_api_client` | `get_benchmark_task_quota` | `benchmarks.BenchmarkTasksApiService/GetBenchmarkTaskQuota` | `ApiGetBenchmarkTaskQuotaRequest` |  |
| `benchmarks.benchmark_tasks_api_client` | `publish_benchmark_task` | `benchmarks.BenchmarkTasksApiService/PublishBenchmarkTask` | `ApiPublishBenchmarkTaskRequest` |  |
| `benchmarks.benchmarks_api_client` | `create_benchmark_model_version_config` | `benchmarks.BenchmarksApiService/CreateBenchmarkModelVersionConfig` | `ApiCreateBenchmarkModelVersionConfigRequest` |  |
| `benchmarks.benchmarks_api_client` | `get_benchmark_model_version_config` | `benchmarks.BenchmarksApiService/GetBenchmarkModelVersionConfig` | `ApiGetBenchmarkModelVersionConfigRequest` | `/api/v1/benchmarks/models/versions/configs/{id}` |
| `benchmarks.benchmarks_api_client` | `list_benchmark_model_version_configs` | `benchmarks.BenchmarksApiService/ListBenchmarkModelVersionConfigs` | `ApiListBenchmarkModelVersionConfigsRequest` |  |
| `benchmarks.benchmarks_api_client` | `get_benchmark_leaderboard` | `benchmarks.BenchmarksApiService/GetBenchmarkLeaderboard` | `ApiGetBenchmarkLeaderboardRequest` | `/api/v1/benchmarks/{owner_slug}/{benchmark_slug}/leaderboard` |
| `benchmarks.benchmarks_api_client` | `list_benchmark_models` | `benchmarks.BenchmarksApiService/ListBenchmarkModels` | `ApiListBenchmarkModelsRequest` |  |
| `benchmarks.benchmarks_api_client` | `create_benchmark_version_agent_mappings` | `benchmarks.BenchmarksApiService/CreateBenchmarkVersionAgentMappings` | `ApiCreateBenchmarkVersionAgentMappingsRequest` |  |
| `benchmarks.benchmarks_api_client` | `delete_benchmark_version_agent_mappings` | `benchmarks.BenchmarksApiService/DeleteBenchmarkVersionAgentMappings` | `ApiDeleteBenchmarkVersionAgentMappingsRequest` |  |
| `benchmarks.benchmarks_api_client` | `list_benchmark_version_agent_mappings` | `benchmarks.BenchmarksApiService/ListBenchmarkVersionAgentMappings` | `ApiListBenchmarkVersionAgentMappingsRequest` |  |
| `blobs.blob_api_client` | `start_blob_upload` | `blobs.BlobApiService/StartBlobUpload` | `ApiStartBlobUploadRequest` |  |
| `common.operations_client` | `get_operation` | `common.OperationsService/GetOperation` | `GetOperationRequest` |  |
| `competitions.competition_api_client` | `list_competitions` | `competitions.CompetitionApiService/ListCompetitions` | `ApiListCompetitionsRequest` |  |
| `competitions.competition_api_client` | `create_competition` | `competitions.CompetitionApiService/CreateCompetition` | `ApiCreateCompetitionRequest` |  |
| `competitions.competition_api_client` | `list_submissions` | `competitions.CompetitionApiService/ListSubmissions` | `ApiListSubmissionsRequest` | `/api/v1/competitions/submissions/list/{competition_name}` |
| `competitions.competition_api_client` | `list_team_public_submissions` | `competitions.CompetitionApiService/ListTeamPublicSubmissions` | `ApiListTeamPublicSubmissionsRequest` | `/api/v1/competitions/teams/{team_id}/public-submissions` |
| `competitions.competition_api_client` | `list_data_files` | `competitions.CompetitionApiService/ListDataFiles` | `ApiListDataFilesRequest` | `/api/v1/competitions/data/list/{competition_name}` |
| `competitions.competition_api_client` | `list_data_tree_files` | `competitions.CompetitionApiService/ListDataTreeFiles` | `ApiListDataTreeFilesRequest` | `/api/v1/competitions/{competition_name}/data-tree/list/` |
| `competitions.competition_api_client` | `get_leaderboard` | `competitions.CompetitionApiService/GetLeaderboard` | `ApiGetLeaderboardRequest` | `/api/v1/competitions/{competition_name}/leaderboard/view` |
| `competitions.competition_api_client` | `download_leaderboard` | `competitions.CompetitionApiService/DownloadLeaderboard` | `ApiDownloadLeaderboardRequest` | `/api/v1/competitions/{competition_name}/leaderboard/download` |
| `competitions.competition_api_client` | `create_submission` | `competitions.CompetitionApiService/CreateSubmission` | `ApiCreateSubmissionRequest` |  |
| `competitions.competition_api_client` | `create_code_submission` | `competitions.CompetitionApiService/CreateCodeSubmission` | `ApiCreateCodeSubmissionRequest` |  |
| `competitions.competition_api_client` | `get_submission` | `competitions.CompetitionApiService/GetSubmission` | `ApiGetSubmissionRequest` |  |
| `competitions.competition_api_client` | `download_submission` | `competitions.CompetitionApiService/DownloadSubmission` | `ApiDownloadSubmissionRequest` | `/api/v1/competitions/submissions/download/{submission_id}` |
| `competitions.competition_api_client` | `get_submission_limits` | `competitions.CompetitionApiService/GetSubmissionLimits` | `ApiGetSubmissionLimitsRequest` | `/api/v1/competitions/{competition_name}/submissions/limits` |
| `competitions.competition_api_client` | `start_submission_upload` | `competitions.CompetitionApiService/StartSubmissionUpload` | `ApiStartSubmissionUploadRequest` |  |
| `competitions.competition_api_client` | `download_data_files` | `competitions.CompetitionApiService/DownloadDataFiles` | `ApiDownloadDataFilesRequest` | `/api/v1/competitions/data/download-all/{competition_name}` |
| `competitions.competition_api_client` | `download_data_file` | `competitions.CompetitionApiService/DownloadDataFile` | `ApiDownloadDataFileRequest` | `/api/v1/competitions/data/download/{competition_name}/{file_name}` |
| `competitions.competition_api_client` | `get_competition` | `competitions.CompetitionApiService/GetCompetition` | `ApiGetCompetitionRequest` | `/api/v1/competitions/get/{competition_name}` |
| `competitions.competition_api_client` | `get_competition_data_files_summary` | `competitions.CompetitionApiService/GetCompetitionDataFilesSummary` | `ApiGetCompetitionDataFilesSummaryRequest` | `/api/v1/competitions/data/summary/{competition_name}` |
| `competitions.competition_api_client` | `list_submission_episodes` | `competitions.CompetitionApiService/ListSubmissionEpisodes` | `ApiListSubmissionEpisodesRequest` | `/api/v1/competitions/submissions/{submission_id}/episodes` |
| `competitions.competition_api_client` | `get_episode_replay` | `competitions.CompetitionApiService/GetEpisodeReplay` | `ApiGetEpisodeReplayRequest` | `/api/v1/competitions/episodes/{episode_id}/replay` |
| `competitions.competition_api_client` | `get_episode_agent_logs` | `competitions.CompetitionApiService/GetEpisodeAgentLogs` | `ApiGetEpisodeAgentLogsRequest` | `/api/v1/competitions/episodes/{episode_id}/agents/{agent_index}/logs` |
| `competitions.competition_api_client` | `list_competition_pages` | `competitions.CompetitionApiService/ListCompetitionPages` | `ApiListCompetitionPagesRequest` | `/api/v1/competitions/{competition_name}/pages` |
| `competitions.competition_api_client` | `create_competition_page` | `competitions.CompetitionApiService/CreateCompetitionPage` | `ApiCreateCompetitionPageRequest` |  |
| `competitions.competition_api_client` | `update_competition_page` | `competitions.CompetitionApiService/UpdateCompetitionPage` | `ApiUpdateCompetitionPageRequest` |  |
| `competitions.competition_api_client` | `delete_competition_page` | `competitions.CompetitionApiService/DeleteCompetitionPage` | `ApiDeleteCompetitionPageRequest` |  |
| `competitions.competition_api_client` | `update_competition_settings` | `competitions.CompetitionApiService/UpdateCompetitionSettings` | `ApiUpdateCompetitionSettingsRequest` |  |
| `competitions.competition_api_client` | `get_competition_settings` | `competitions.CompetitionApiService/GetCompetitionSettings` | `ApiGetCompetitionSettingsRequest` | `/api/v1/competitions/{competition_name}/settings` |
| `competitions.competition_api_client` | `launch_competition` | `competitions.CompetitionApiService/LaunchCompetition` | `ApiLaunchCompetitionRequest` |  |
| `competitions.competition_api_client` | `create_competition_data` | `competitions.CompetitionApiService/CreateCompetitionData` | `ApiCreateCompetitionDataRequest` |  |
| `competitions.competition_api_client` | `create_competition_solution` | `competitions.CompetitionApiService/CreateCompetitionSolution` | `ApiCreateCompetitionSolutionRequest` |  |
| `competitions.competition_api_client` | `get_competition_solution_status` | `competitions.CompetitionApiService/GetCompetitionSolutionStatus` | `ApiGetCompetitionSolutionStatusRequest` | `/api/v1/competitions/{competition_name}/solution` |
| `competitions.competition_api_client` | `create_competition_sample_submission` | `competitions.CompetitionApiService/CreateCompetitionSampleSubmission` | `ApiCreateCompetitionSampleSubmissionRequest` |  |
| `competitions.competition_api_client` | `list_competition_hosts` | `competitions.CompetitionApiService/ListCompetitionHosts` | `ApiListCompetitionHostsRequest` | `/api/v1/competitions/{competition_name}/hosts` |
| `competitions.competition_api_client` | `add_competition_host` | `competitions.CompetitionApiService/AddCompetitionHost` | `ApiAddCompetitionHostRequest` |  |
| `competitions.competition_api_client` | `list_competition_judges` | `competitions.CompetitionApiService/ListCompetitionJudges` | `ApiListCompetitionJudgesRequest` | `/api/v1/competitions/{competition_name}/judges` |
| `competitions.competition_api_client` | `add_competition_judge` | `competitions.CompetitionApiService/AddCompetitionJudge` | `ApiAddCompetitionJudgeRequest` |  |
| `competitions.competition_api_client` | `list_competition_topics` | `competitions.CompetitionApiService/ListCompetitionTopics` | `ApiListCompetitionTopicsRequest` | `/api/v1/competitions/{competition_name}/topics` |
| `competitions.competition_api_client` | `list_topic_messages` | `competitions.CompetitionApiService/ListTopicMessages` | `ApiListTopicMessagesRequest` | `/api/v1/competitions/{competition_name}/topics/{topic_id}/messages` |
| `competitions.hackathon_api_client` | `get_hackathon_write_up` | `competitions.HackathonApiService/GetHackathonWriteUp` | `ApiGetHackathonWriteUpRequest` | `/api/v1/competitions/{competition_name}/hackathon-write-ups/{hackathon_write_up_id}` |
| `competitions.hackathon_api_client` | `list_hackathon_write_ups` | `competitions.HackathonApiService/ListHackathonWriteUps` | `ApiListHackathonWriteUpsRequest` | `/api/v1/competitions/{competition_name}/hackathon-write-ups` |
| `competitions.hackathon_api_client` | `list_hackathon_tracks` | `competitions.HackathonApiService/ListHackathonTracks` | `ApiListHackathonTracksRequest` | `/api/v1/competitions/{competition_name}/hackathon-tracks` |
| `competitions.hackathon_api_client` | `export_hackathon_write_ups_csv` | `competitions.HackathonApiService/ExportHackathonWriteUpsCsv` | `ApiExportHackathonWriteUpsCsvRequest` | `/api/v1/competitions/{competition_name}/hackathon-write-ups-csv` |
| `competitions.hackathon_api_client` | `get_hackathon_overview` | `competitions.HackathonApiService/GetHackathonOverview` | `ApiGetHackathonOverviewRequest` | `/api/v1/competitions/{competition_name}/hackathon-overview` |
| `competitions.hackathon_client` | `export_enriched_hackathon_write_ups_csv` | `competitions.HackathonService/ExportEnrichedHackathonWriteUpsCsv` | `ExportEnrichedHackathonWriteUpsCsvRequest` | `/api/v1/competitions/{competition_name}/enriched-hackathon-write-ups-csv` |
| `datasets.dataset_api_client` | `list_datasets` | `datasets.DatasetApiService/ListDatasets` | `ApiListDatasetsRequest` |  |
| `datasets.dataset_api_client` | `get_dataset` | `datasets.DatasetApiService/GetDataset` | `ApiGetDatasetRequest` | `/api/v1/datasets/view/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `list_dataset_files` | `datasets.DatasetApiService/ListDatasetFiles` | `ApiListDatasetFilesRequest` | `/api/v1/datasets/list/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `list_tree_dataset_files` | `datasets.DatasetApiService/ListTreeDatasetFiles` | `ApiListTreeDatasetFilesRequest` | `/api/v1/datasets/list-tree/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `get_dataset_metadata` | `datasets.DatasetApiService/GetDatasetMetadata` | `ApiGetDatasetMetadataRequest` | `/api/v1/datasets/metadata/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `update_dataset_metadata` | `datasets.DatasetApiService/UpdateDatasetMetadata` | `ApiUpdateDatasetMetadataRequest` |  |
| `datasets.dataset_api_client` | `download_dataset` | `datasets.DatasetApiService/DownloadDataset` | `ApiDownloadDatasetRequest` | `/api/v1/datasets/download/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `download_dataset_raw` | `datasets.DatasetApiService/DownloadDatasetRaw` | `ApiDownloadDatasetRawRequest` | `/api/v1/datasets/download-raw/{owner_slug}/{dataset_slug}/{file_name}` |
| `datasets.dataset_api_client` | `create_dataset_version` | `datasets.DatasetApiService/CreateDatasetVersion` | `ApiCreateDatasetVersionRequest` |  |
| `datasets.dataset_api_client` | `create_dataset_version_by_id` | `datasets.DatasetApiService/CreateDatasetVersionById` | `ApiCreateDatasetVersionByIdRequest` |  |
| `datasets.dataset_api_client` | `create_dataset` | `datasets.DatasetApiService/CreateDataset` | `ApiCreateDatasetRequest` |  |
| `datasets.dataset_api_client` | `get_dataset_status` | `datasets.DatasetApiService/GetDatasetStatus` | `ApiGetDatasetStatusRequest` | `/api/v1/datasets/status/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `get_dataset_files_summary` | `datasets.DatasetApiService/GetDatasetFilesSummary` | `ApiGetDatasetFilesSummaryRequest` | `/api/v1/datasets/files/summary/{owner_slug}/{dataset_slug}` |
| `datasets.dataset_api_client` | `upload_dataset_file` | `datasets.DatasetApiService/UploadDatasetFile` | `ApiUploadDatasetFileRequest` |  |
| `datasets.dataset_api_client` | `delete_dataset` | `datasets.DatasetApiService/DeleteDataset` | `ApiDeleteDatasetRequest` |  |
| `discussions.discussion_api_client` | `list_forums` | `discussions.DiscussionApiService/ListForums` | `ApiListForumsRequest` |  |
| `discussions.discussion_api_client` | `list_topics` | `discussions.DiscussionApiService/ListTopics` | `ApiListTopicsRequest` |  |
| `discussions.discussion_api_client` | `get_topic` | `discussions.DiscussionApiService/GetTopic` | `ApiGetTopicRequest` | `/api/v1/discussions/{id}/get` |
| `discussions.discussion_api_client` | `list_comments` | `discussions.DiscussionApiService/ListComments` | `ApiListCommentsRequest` | `/api/v1/discussions/{topic_id}/comments` |
| `discussions.discussion_api_client` | `list_dataset_topics` | `discussions.DiscussionApiService/ListDatasetTopics` | `ApiListDatasetTopicsRequest` | `/api/v1/datasets/{owner_slug}/{dataset_slug}/topics/list` |
| `discussions.discussion_api_client` | `list_model_topics` | `discussions.DiscussionApiService/ListModelTopics` | `ApiListModelTopicsRequest` | `/api/v1/models/{owner_slug}/{model_slug}/topics/list` |
| `discussions.discussion_api_client` | `list_benchmark_topics` | `discussions.DiscussionApiService/ListBenchmarkTopics` | `ApiListBenchmarkTopicsRequest` | `/api/v1/benchmarks/{owner_slug}/{benchmark_slug}/topics/list` |
| `discussions.discussion_api_client` | `list_kernel_topics` | `discussions.DiscussionApiService/ListKernelTopics` | `ApiListKernelTopicsRequest` | `/api/v1/kernels/{owner_slug}/{kernel_slug}/topics/list` |
| `discussions.write_ups_api_client` | `get_resolved_write_up_links` | `discussions.WriteUpsApiService/GetResolvedWriteUpLinks` | `ApiGetResolvedWriteUpLinksRequest` | `/api/v1/writeups/{write_up_id}/resolved-links` |
| `education.education_api_client` | `track_exercise_interaction` | `education.EducationApiService/TrackExerciseInteraction` | `ApiTrackExerciseInteractionRequest` |  |
| `kernels.kernels_api_client` | `list_kernels` | `kernels.KernelsApiService/ListKernels` | `ApiListKernelsRequest` |  |
| `kernels.kernels_api_client` | `list_kernel_files` | `kernels.KernelsApiService/ListKernelFiles` | `ApiListKernelFilesRequest` |  |
| `kernels.kernels_api_client` | `get_kernel` | `kernels.KernelsApiService/GetKernel` | `ApiGetKernelRequest` |  |
| `kernels.kernels_api_client` | `save_kernel` | `kernels.KernelsApiService/SaveKernel` | `ApiSaveKernelRequest` |  |
| `kernels.kernels_api_client` | `list_kernel_session_output` | `kernels.KernelsApiService/ListKernelSessionOutput` | `ApiListKernelSessionOutputRequest` |  |
| `kernels.kernels_api_client` | `get_kernel_session_status` | `kernels.KernelsApiService/GetKernelSessionStatus` | `ApiGetKernelSessionStatusRequest` |  |
| `kernels.kernels_api_client` | `download_kernel_output` | `kernels.KernelsApiService/DownloadKernelOutput` | `ApiDownloadKernelOutputRequest` | `/api/v1/kernels/output/download/{owner_slug}/{kernel_slug}` |
| `kernels.kernels_api_client` | `download_kernel_output_zip` | `kernels.KernelsApiService/DownloadKernelOutputZip` | `ApiDownloadKernelOutputZipRequest` | `/api/v1/kernels/output/download_zip/{kernel_session_id}` |
| `kernels.kernels_api_client` | `delete_kernel` | `kernels.KernelsApiService/DeleteKernel` | `ApiDeleteKernelRequest` | `/api/v1/kernels/delete/{user_name}/{kernel_slug}` |
| `kernels.kernels_api_client` | `cancel_kernel_session` | `kernels.KernelsApiService/CancelKernelSession` | `ApiCancelKernelSessionRequest` | `/api/v1/kernels/cancel-session/{kernel_session_id}` |
| `kernels.kernels_api_client` | `create_kernel_session` | `kernels.KernelsApiService/CreateKernelSession` | `ApiCreateKernelSessionRequest` | `/api/v1/kernels/create-session/{slug}` |
| `kernels.kernels_api_client` | `get_kernel_session_logs_stream` | `kernels.KernelsApiService/GetKernelSessionLogsStream` | `ApiGetKernelSessionLogsStreamRequest` | `/api/v1/kernels/sessions/{kernel_session_id}/logs/stream` |
| `kernels.kernels_api_client` | `get_accelerator_quota_statistics` | `kernels.KernelsApiService/GetAcceleratorQuotaStatistics` | `ApiGetAcceleratorQuotaStatisticsRequest` |  |
| `models.model_api_client` | `create_model` | `models.ModelApiService/CreateModel` | `ApiCreateModelRequest` |  |
| `models.model_api_client` | `create_model_instance` | `models.ModelApiService/CreateModelInstance` | `ApiCreateModelInstanceRequest` |  |
| `models.model_api_client` | `create_model_instance_version` | `models.ModelApiService/CreateModelInstanceVersion` | `ApiCreateModelInstanceVersionRequest` |  |
| `models.model_api_client` | `delete_model` | `models.ModelApiService/DeleteModel` | `ApiDeleteModelRequest` |  |
| `models.model_api_client` | `delete_model_instance` | `models.ModelApiService/DeleteModelInstance` | `ApiDeleteModelInstanceRequest` |  |
| `models.model_api_client` | `delete_model_instance_version` | `models.ModelApiService/DeleteModelInstanceVersion` | `ApiDeleteModelInstanceVersionRequest` |  |
| `models.model_api_client` | `get_model` | `models.ModelApiService/GetModel` | `ApiGetModelRequest` | `/api/v1/models/{owner_slug}/{model_slug}/get` |
| `models.model_api_client` | `get_model_instance` | `models.ModelApiService/GetModelInstance` | `ApiGetModelInstanceRequest` | `/api/v1/models/{owner_slug}/{model_slug}/{framework}/{instance_slug}/get` |
| `models.model_api_client` | `download_model_instance_version` | `models.ModelApiService/DownloadModelInstanceVersion` | `ApiDownloadModelInstanceVersionRequest` | `/api/v1/models/{owner_slug}/{model_slug}/{framework}/{instance_slug}/{version_number}/download` |
| `models.model_api_client` | `list_models` | `models.ModelApiService/ListModels` | `ApiListModelsRequest` |  |
| `models.model_api_client` | `list_model_instances` | `models.ModelApiService/ListModelInstances` | `ApiListModelInstancesRequest` | `/api/v1/models/{owner_slug}/{model_slug}/list` |
| `models.model_api_client` | `list_model_instance_versions` | `models.ModelApiService/ListModelInstanceVersions` | `ApiListModelInstanceVersionsRequest` | `/api/v1/models/{owner_slug}/{model_slug}/{framework}/{instance_slug}/list` |
| `models.model_api_client` | `list_model_instance_version_files` | `models.ModelApiService/ListModelInstanceVersionFiles` | `ApiListModelInstanceVersionFilesRequest` | `/api/v1/models/{owner_slug}/{model_slug}/{framework}/{instance_slug}/files` |
| `models.model_api_client` | `update_model` | `models.ModelApiService/UpdateModel` | `ApiUpdateModelRequest` |  |
| `models.model_api_client` | `update_model_instance` | `models.ModelApiService/UpdateModelInstance` | `ApiUpdateModelInstanceRequest` |  |
| `models.model_api_client` | `upload_model_file` | `models.ModelApiService/UploadModelFile` | `ApiUploadModelFileRequest` |  |
| `models.model_api_client` | `create_model_signing_token` | `models.ModelApiService/CreateModelSigningToken` | `CreateModelSigningTokenRequest` |  |
| `models.model_api_client` | `well_know_endpoint` | `models.ModelApiService/WellKnowEndpoint` | `WellKnowEndpointRequest` |  |
| `models.model_api_client` | `keys` | `models.ModelApiService/Keys` | `KeysRequest` |  |
| `models.model_api_client` | `list_model_gating_user_consents` | `models.ModelApiService/ListModelGatingUserConsents` | `ApiListModelGatingUserConsentsRequest` | `/api/v1/models/{owner_slug}/{model_slug}/user-consents` |
| `models.model_api_client` | `review_model_gating_user_consent` | `models.ModelApiService/ReviewModelGatingUserConsent` | `ApiReviewModelGatingUserConsentRequest` |  |
| `models.model_proxy_api_client` | `get_model_proxy_quotas` | `models.ModelProxyApiService/GetModelProxyQuotas` | `ApiGetModelProxyQuotasRequest` |  |
| `models.model_proxy_api_client` | `create_default_model_proxy_token` | `models.ModelProxyApiService/CreateDefaultModelProxyToken` | `ApiCreateDefaultModelProxyTokenRequest` |  |
| `models.model_client` | `get_model_metrics` | `models.ModelService/GetModelMetrics` | `GetModelMetricsRequest` | `/models/{owner_slug}/{model_slug}/metrics` |
| `search.search_api_client` | `list_entities` | `search.SearchApiService/ListEntities` | `ListEntitiesRequest` |  |
| `security.iam_client` | `get_iam_policy` | `security.IamService/GetIamPolicy` | `GetIamPolicyRequest` | `/api/v1/iam/get/{resource_id}` |
| `security.iam_client` | `set_iam_policy` | `security.IamService/SetIamPolicy` | `SetIamPolicyRequest` |  |
| `security.oauth_client` | `start_oauth_flow` | `security.OAuthService/StartOAuthFlow` | `StartOAuthFlowRequest` |  |
| `security.oauth_client` | `exchange_oauth_token` | `security.OAuthService/ExchangeOAuthToken` | `ExchangeOAuthTokenRequest` |  |
| `security.oauth_client` | `introspect_token` | `security.OAuthService/IntrospectToken` | `IntrospectTokenRequest` |  |
| `security.oauth_client` | `register_oauth_client` | `security.OAuthService/RegisterOAuthClient` | `RegisterOAuthClientRequest` |  |
| `users.account_client` | `expire_api_token` | `users.AccountService/ExpireApiToken` | `ExpireApiTokenRequest` |  |
| `users.account_client` | `generate_access_token` | `users.AccountService/GenerateAccessToken` | `GenerateAccessTokenRequest` |  |
| `users.group_api_client` | `list_user_managed_group_memberships` | `users.GroupApiService/ListUserManagedGroupMemberships` | `ApiListUserManagedGroupMembershipsRequest` | `/api/v1/groups/{group_slug}/members` |
| `users.group_api_client` | `list_synchronized_group_memberships` | `users.GroupApiService/ListSynchronizedGroupMemberships` | `ApiListSynchronizedGroupMembershipsRequest` | `/api/v1/sync_groups/{group_slug}/members` |

### MCP tools (Kaggle.Web 1.0.0.0)

Every tool takes one `request` object, except `authorize`, which takes
none. The policy column is the user-scope rule from the section above.

| Tool | Description | Request properties | Host policy |
| --- | --- | --- | --- |
| `authorize` | This tool can be used to authorize with Kaggle but it is only compatible with certain clients. See kaggle.com/docs/mcp for more information | (none) | ask |
| `cancel_notebook_session` | Cancel a notebook session. | `kernelSessionId` | ask |
| `create_benchmark_arena_settings` | Create a benchmark version's arena. | `ownerSlug`, `benchmarkSlug`, `versionNumber`, `settings` | ask |
| `create_benchmark_task_from_prompt` | Create a new benchmark task from a prompt. | `taskDescription`, `assertionDescription` | ask |
| `create_code_competition_submission` | Submit a kernel to a competition. | `competitionName`, `kernelOwner`, `kernelSlug`, `kernelVersion`, `fileName`, `submissionDescription` | deny |
| `create_model` | Create a new model. | `ownerSlug`, `slug`, `title`, `subtitle`, `isPrivate`, `description`, `publishTime`, `provenanceSources` | ask |
| `create_notebook_session` | Create a new notebook session. | `slug`, `language`, `kernelType`, `dockerImage`, `machineShape`, `enableInternet` | ask |
| `download_competition_data_file` | Download a single data file for a competition. | `competitionName`, `fileName` | allow |
| `download_competition_data_files` | Download all data files for a competition. | `competitionName` | allow |
| `download_competition_leaderboard` | Download the leaderboard for a competition. | `competitionName` | allow |
| `download_competition_submission` | Download the file for one of your competition submissions. | `submissionId` | allow |
| `download_dataset` | Download a dataset. | `ownerSlug`, `datasetSlug`, `fileName`, `datasetVersionNumber`, `raw`, `hashLink` | allow |
| `download_hackathon_write_ups` | Exports a CSV with the data from all submitted writeups after the hackathon has closed. | `competitionId`, `competitionName` | allow |
| `download_model_variation_version` | Get a url where the files for a model variation version can be downloaded. | `ownerSlug`, `modelSlug`, `framework`, `instanceSlug`, `versionNumber`, `path` | allow |
| `download_notebook_output` | Download the output of a notebook. | `ownerSlug`, `kernelSlug`, `filePath`, `versionNumber` | allow |
| `download_notebook_output_zip` | Download the zipped output of a notebook. | `kernelSessionId` | allow |
| `get_accelerator_quota` | Get the current user's weekly GPU and TPU quota usage. | (none) | allow |
| `get_benchmark_arena_settings` | Get a benchmark version's arena settings. | `ownerSlug`, `benchmarkSlug`, `versionNumber` | allow |
| `get_benchmark_leaderboard` | Get the leaderboard for a benchmark. | `ownerSlug`, `benchmarkSlug`, `versionNumber` | allow |
| `get_competition` | Get competition metadata. | `competitionName` | allow |
| `get_competition_data_files_summary` | Get a summary of the data files for a competition, including number and type of files as well as column metadata. | `competitionName` | allow |
| `get_competition_leaderboard` | Get the leaderboard for a competition. | `competitionName`, `overridePublic`, `pageSize`, `pageToken` | allow |
| `get_competition_submission` | Get metadata about a competition submission. | `ref` | allow |
| `get_dataset_files_summary` | Get a summary of the data files in a dataset, including number and type of files as well as column metadata. | `ownerSlug`, `datasetSlug`, `datasetVersionNumber` | allow |
| `get_dataset_info` | Get information about a dataset. | `ownerSlug`, `datasetSlug` | allow |
| `get_dataset_metadata` | Get metadata about a dataset. | `ownerSlug`, `datasetSlug` | allow |
| `get_dataset_status` | Get the processing status of a dataset, indicating whether the dataset is still processing, completed, or failed. | `ownerSlug`, `datasetSlug` | allow |
| `get_episode_agent_logs` | Download agent logs for a simulation episode. | `episodeId`, `agentIndex` | allow |
| `get_episode_replay` | Download the replay for a simulation episode. | `episodeId` | allow |
| `get_forum` | Get details about a discussion forum, including its name, description, and topic count. | `forumId`, `forumSlug`, `forumIdOrSlugCase` | allow |
| `get_forum_topic` | Get a discussion topic by ID, optionally including its comments. | `forumTopicId`, `includeComments`, `initialPageSize`, `startingCommentId` | allow |
| `get_hackathon_overview` | Get all the overview page content for a hackathon competition. | `competitionName` | allow |
| `get_hackathon_write_up` | Get a single hackathon write-up submission by ID for a competition. | `competitionName`, `hackathonWriteUpId` | allow |
| `get_model` | Get a metadata about a model. | `ownerSlug`, `modelSlug` | allow |
| `get_model_variation` | Get metadata about a model variation. | `ownerSlug`, `modelSlug`, `framework`, `instanceSlug` | allow |
| `get_notebook_info` | Get information about a notebook. | `userName`, `kernelSlug`, `versionLabel` | allow |
| `get_notebook_session_status` | Get the status of a notebook session, indicating whether it is running, completed, or failed. | `userName`, `kernelSlug`, `versionLabel` | allow |
| `get_resolved_writeup_links` | Get resolved information for all links in a writeup, including download URLs, file summaries, and metadata for datasets, notebooks, YouTube videos, and external links. | `writeUpId` | allow |
| `get_user_profile` | Get a user's public profile. | `userName`, `userId`, `userIdentifierCase` | allow |
| `get_writeup` | Get a writeup by ID. | `writeUpId` | allow |
| `get_writeup_by_slug` | Get a writeup by its slug. | `slug`, `userName`, `competitionName`, `forumName`, `slugAssociationCase` | allow |
| `get_writeup_by_topic` | Get a writeup by its linked forum topic ID. Use this when you found a writeup via forum discussions. | `forumTopicId` | allow |
| `list_benchmark_arena_combinations` | List the task and candidate combinations opted into a benchmark version's arena. | `ownerSlug`, `benchmarkSlug`, `versionNumber` | allow |
| `list_competition_data_files` | List the data files for a competition. | `competitionName`, `pageSize`, `pageToken` | allow |
| `list_competition_data_tree_files` | List the data files by directory for a competition. | `competitionName`, `path`, `pageSize`, `pageToken` | allow |
| `list_competition_pages` | List the content pages for a competition (overview, rules, evaluation, data description, etc.). | `competitionName`, `pageName` | allow |
| `list_competition_topics` | List discussion topics for a competition. | `competitionName`, `sortBy`, `page` | allow |
| `list_dataset_files` | List the files in a dataset. | `ownerSlug`, `datasetSlug`, `datasetVersionNumber`, `pageToken`, `pageSize` | allow |
| `list_dataset_tree_files` | List the files in a dataset by directory. | `ownerSlug`, `datasetSlug`, `datasetVersionNumber`, `path`, `pageToken`, `pageSize` | allow |
| `list_forum_topics` | List and search discussion topics. Omit forum_id to search across all forums. | `category`, `forumId`, `group`, `page`, `searchQuery`, `sortBy`, `recency`, `myActivity`, `author`, `filterCategoryIds` | allow |
| `list_forums` | List all top-level discussion forums on Kaggle. | (none) | allow |
| `list_hackathon_tracks` | List the tracks for a hackathon competition. | `competitionName` | allow |
| `list_hackathon_write_ups` | List hackathon write-up submissions for a competition. Supports filtering by track and winner status. | `competitionId`, `teamId`, `hackathonTrackIds`, `published`, `winner`, `template`, `pageSize`, `pageToken`, `skip`, `hostOrJudge`, `competitionName` | allow |
| `list_model_variation_version_files` | List the files of a model variation version. | `ownerSlug`, `modelSlug`, `instanceSlug`, `framework`, `versionNumber`, `pageSize`, `pageToken` | allow |
| `list_model_variation_versions` | List model variation versions. | `ownerSlug`, `modelSlug`, `instanceSlug`, `framework`, `pageSize`, `pageToken` | allow |
| `list_model_variations` | List model variations. | `ownerSlug`, `modelSlug`, `pageSize`, `pageToken` | allow |
| `list_models` | List models. | `search`, `sortBy`, `owner`, `pageSize`, `pageToken`, `onlyVertexModels` | allow |
| `list_notebook_files` | List the files in a notebook. | `userName`, `kernelSlug`, `pageSize`, `pageToken`, `versionLabel` | allow |
| `list_notebook_session_output` | List the output files of a notebook session. | `userName`, `kernelSlug`, `pageSize`, `pageToken`, `versionLabel` | allow |
| `list_submission_episodes` | List episodes for a submission in a simulation competition. | `submissionId` | allow |
| `list_team_public_submissions` | List the public-safe submissions for a team. For simulation competitions this is every active (leaderboard-eligible) submission; for regular competitions it is the single submission currently on the public leaderboard. | `teamId` | allow |
| `list_topic_messages` | List discussion messages within a competition topic. | `competitionName`, `topicId`, `sortBy`, `pageSize` | allow |
| `save_notebook` | Save a notebook and run it from top to bottom. | `id`, `slug`, `newTitle`, `text`, `language`, `kernelType`, `datasetDataSources`, `kernelDataSources`, `competitionDataSources`, `categoryIds`, `isPrivate`, `enableGpu`, `enableTpu`, `enableInternet`, `dockerImagePinningType`, `modelDataSources`, `sessionTimeoutSeconds`, `priority`, `dockerImage`, `kernelExecutionType`, `machineShape` | ask |
| `search_competition_submissions` | Search for competition submissions. | `competitionName`, `sortBy`, `group`, `page`, `pageToken`, `pageSize` | allow |
| `search_competitions` | Search for competitions. | `group`, `category`, `sortBy`, `search`, `page`, `pageToken`, `pageSize` | allow |
| `search_content` | Search across all Kaggle content types (competitions, datasets, notebooks, models, discussions, users, benchmarks). | `maxPageSize`, `filters`, `canonicalOrderBy`, `competitionsOrderBy`, `datasetsOrderBy`, `kernelsOrderBy`, `modelsOrderBy`, `discussionsOrderBy`, `usersOrderBy`, `pageToken`, `pageSize`, `skip`, `orderByCase` | allow |
| `search_datasets` | Search for datasets. | `group`, `sortBy`, `size`, `fileType`, `license`, `viewed`, `tagIds`, `search`, `user`, `minSize`, `maxSize`, `page`, `pageToken`, `pageSize` | allow |
| `search_notebooks` | Search for notebooks. | `competition`, `dataset`, `parentKernel`, `group`, `kernelType`, `language`, `outputType`, `search`, `sortBy`, `user`, `page`, `pageSize`, `pageToken` | allow |
| `start_competition_submission_upload` | Get a link to upload a competition submission file. | `competitionName`, `contentLength`, `lastModifiedEpochSeconds`, `fileName` | deny |
| `submit_to_competition` | Submit a new competition submission. | `competitionName`, `blobFileTokens`, `submissionDescription`, `benchmarkModelVersionId`, `sandbox` | deny |
| `update_benchmark_arena_combinations` | Opt task and candidate combinations into or out of a benchmark version's arena. | `ownerSlug`, `benchmarkSlug`, `versionNumber`, `add`, `remove` | ask |
| `update_benchmark_arena_settings` | Update a benchmark version's arena settings. | `ownerSlug`, `benchmarkSlug`, `versionNumber`, `settings`, `updateMask` | ask |
| `update_dataset_metadata` | Update the metadata for a dataset. | `ownerSlug`, `datasetSlug`, `settings` | ask |
| `update_model` | Update a model. | `ownerSlug`, `modelSlug`, `title`, `subtitle`, `isPrivate`, `description`, `publishTime`, `provenanceSources`, `updateMask` | ask |
| `update_model_variation` | Update a model variation. | `ownerSlug`, `modelSlug`, `framework`, `instanceSlug`, `overview`, `usage`, `fineTunable`, `trainingData`, `updateMask`, `licenseName`, `modelInstanceType`, `baseModelInstance`, `externalBaseModelUrl` | ask |
| `upload_dataset_file` | Upload a file to a dataset. | `fileName`, `contentLength`, `lastModifiedEpochSeconds` | ask |
