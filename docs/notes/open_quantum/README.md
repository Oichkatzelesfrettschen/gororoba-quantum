# Open Quantum

Open Quantum (operated by Quantum Rings, Public Compute supplied by qBitTensor
Labs) brokers IonQ, Rigetti, IQM and AQT processors through one account, one
management API and one scheduler API. The repository reaches it through the
official Python SDK, its single-job CLI and its stdio MCP server, all pinned in
their own environment. The live pages stay the authority because they change;
the captures below record what they said when read.

| Path | Content |
|---|---|
| `docs/` | the 56 pages of docs.openquantum.com (`scripts/capture_oq_docs.py --docs`) |
| `site/` | the pricing, free-credit, terms, privacy, citation and provider pages of openquantum.com (`--site`) |
| `pypi/` | release metadata and wheel sha256 of the six SDK packages (`--pypi`) |
| `pricing/` | identities of the pricing page's script chunks searched for a credit rate (`--pricing`) |
| `requirements-oq.txt` | the pinned environment |
| `../../evidence/open_quantum/catalogue.json` | the account snapshot: backends, constraint documents, shot schemas, categories, MCP tool schemas, balances (`scripts/oq_platform.py snapshot`) |
| `../../evidence/open_quantum/pricing.json` | the price list parsed from the pricing page (`capture_oq_docs.py --pricing`) |

## Environment and credential

The SDK and the MCP server need their own environment: openquantum-mcp 0.2.0
requires `mcp<2`, while the Quantum Inspire environment runs mcp 2.3.0.

```sh
OQ_ENV=$HOME/.local/share/openquantum/venv
OQ_PYTHON=${OQ_PYTHON:-$OQ_ENV/bin/python}
uv venv --python 3.14 "$OQ_ENV"
VIRTUAL_ENV="$OQ_ENV" uv pip install -r docs/notes/open_quantum/requirements-oq.txt
```

| Package | Version | wheel sha256 | Role |
|---|---|---|---|
| openquantum-sdk | 1.0.0 | a189be97...bdfc | `OpenQuantumClient`, `ManagementClient`, `SchedulerClient`, the `openquantum-sdk` CLI |
| openquantum-mcp | 0.2.0 | 8973ac5a...6f4d | the 13-tool stdio MCP server |
| openquantum-sdk-qiskit | 1.0.0 | 21b0814c...53e6 | `OQBackend` (BackendV2 with a Target), `OQSampler`, `OQEstimator` |
| qiskit | 2.5.2 | | the repository's pin; the plugin accepts any `qiskit>=2.0` |

The full wheel digests are in `pypi/`. The PennyLane,
Cirq and Qrisp plugins are not installed.

An SDK key is a Client ID and Client Secret created at
https://www.openquantum.com/settings/keys (two keys per account; the secret is
shown once). The key lives outside every checkout as
`~/.config/openquantum/sdk-key.json`, `{"client_id": ..., "client_secret": ...}`,
directory mode 700 and file mode 600, and every consumer names it by path
through `OPENQUANTUM_SDK_KEY`, so the secret enters no MCP registration,
command line or log. `openquantum_sdk.credentials.resolve_env_credentials`
resolves, first match winning: an explicit token, an explicit client pair, the
key file (`sdk_key_path` or `OPENQUANTUM_SDK_KEY`), `OPENQUANTUM_TOKEN`, then
`OPENQUANTUM_CLIENT_ID` with `OPENQUANTUM_CLIENT_SECRET`. The MCP server
accepts client credentials only. `save_account` writes
`~/.config/OpenQuantum/accounts.json` (or `~/.openquantum/accounts.json`
without platformdirs) and puts the secret in the system keyring when one is
available; the repository does not use it.

## Interfaces

| Interface | Command | Reach |
|---|---|---|
| Core SDK | `OpenQuantumClient`, `SchedulerClient.submit_job(JobSubmissionConfig, ...)` | every API: upload, prepare, quote, plan and priority choice, create, poll, download output and calibration, cancel |
| SDK CLI | `"$OQ_PYTHON" -m openquantum_sdk --sdk-key KEY --input FILE.qasm --backend CODE --subcategory oth:oth --shots N` | one job: upload, quote, ask, submit, wait; prints counts |
| MCP | `"$OQ_PYTHON" -I -m openquantum_mcp` | the 13 tools below |
| Qiskit | `openquantum_sdk_qiskit.OQBackend`, `OQSampler`, `OQEstimator` | transpile to the backend's Target, run as SamplerV2 or EstimatorV2 |
| Portal | https://www.openquantum.com | job creation, monitoring, keys, credits, referral and claim pages |

`scripts/oq_platform.py snapshot --out docs/evidence/open_quantum` performs
the read-only half of the core SDK (organizations, credits, providers, backend
classes with their constraint documents, categories, job count, the MCP tool
schemas) and uploads nothing.

### MCP tools

The server registers as `openquantum` at Claude Code user scope and in
`~/.codex/config.toml`, both launching `"$OQ_PYTHON" -I -m openquantum_mcp`
with `OPENQUANTUM_SDK_KEY`, `OPENQUANTUM_MCP_MAX_CREDITS=1`,
`OPENQUANTUM_MCP_WAIT_TIMEOUT_SECONDS=45` and
`OPENQUANTUM_MCP_PREP_TIMEOUT_SECONDS=120`. The Claude launcher in
`~/.config/shell/codex-env.sh` loads it by default
(`CLAUDE_MCP_SERVERS` defaults to `kaggle,quantum-inspire,openquantum`).
`catalogue.json` retains every tool's description and input schema.

| Tool | Parameters | Effect | Claude / Codex approval |
|---|---|---|---|
| `list_organizations` | `limit` | organizations of the key's account | allow / approve |
| `get_credits` | `organization_id` | Spark and Full balances, the cap and the spend policy | allow / approve |
| `list_backends` | `online_only`, `device_type`, `name_contains`, `max_qubits`, `limit` | backend classes with status, `accepting_jobs`, queue depth | allow / approve |
| `get_backend` | `backend_class_id` (short code or UUID) | backend record, shot schema, constraint summary (the full document is in `catalogue.json`) | allow / approve |
| `list_job_categories` | `limit` | categories and subcategories for `job_subcategory_id` | allow / approve |
| `list_jobs` | `organization_id`, `limit`, `status`, `cursor` | the organization's jobs | allow / approve |
| `get_job` | `job_id` | one status read | allow / approve |
| `wait_for_job` | `job_id`, `timeout_seconds`, `poll_interval_seconds` | polls to a terminal state or the timeout | allow / approve |
| `get_job_results` | `job_id`, `top_n`, `include_raw` | top-N counts; the raw payload truncates at 8000 characters | allow / approve |
| `get_job_calibration` | `job_id`, `include_raw` | the calibration snapshot when the backend tagged one | allow / approve |
| `prepare_job` | `backend_class_id`, `qasm` or `file_path`, `shots`, `name`, `organization_id`, `job_subcategory_id`, `input_format`, `execution_plan`, `queue_priority` | uploads the circuit and returns `preparation_id`, `estimated_credits`, `quote_summary` and `spend_preview`; creates no job and spends nothing | ask / prompt |
| `submit_job` | `preparation_id` and `confirm_spend`, or every `prepare_job` field for a one-shot upload-and-submit | creates the job and spends credits | ask / prompt |
| `cancel_job` | `job_id` | cancels a Pending job; credits return | ask / prompt |

Codex applies a tool's `approval_mode = "prompt"` through its session
approval policy: under the global `approval_policy = "never"` a `codex exec`
call to `cancel_job` returned "MCP tool call requires approval, but approval
policy is never" without reaching the server, so a non-interactive Codex run
holds the three tools closed and an interactive session asks.

Source facts of openquantum-mcp 0.2.0 that bind its use:

- `openquantum_mcp.safety.evaluate_spend` rejects a quote above
  `OPENQUANTUM_MCP_MAX_CREDITS` (default 10, here 1), passes a zero-cost job,
  passes a Public job whose cost the Spark balance covers without
  `confirm_spend`, and demands `confirm_spend=true` for any spend that reaches
  Full credits. The model sets `confirm_spend`, so the harness prompt on
  `submit_job` is the human approval. The cap binds each job, not a session,
  and the SDK and CLI bypass it.
- `prepare_job` sends `configuration_data={"shots": N}` only, so
  `disable_qubit_rewiring` stays at its default `false` through MCP; a run
  that must hold a physical layout goes through the core SDK.
- `submit_job` with a `preparation_id` from the same server process reuses
  the cached plan and priority. A server restarted between the two calls
  re-selects from the stored quote under the `submit_job` call's own
  `execution_plan` and `queue_priority`, so both calls name `public` and
  `standard`.
- `file_path` uploads any file the server process can read; inline `qasm` is
  the form this repository uses.
- Results arrive through a presigned `output_data_url` that is regenerated on
  each job read; `SchedulerClient.download_job_output` returns a counts
  histogram, so shot order is not part of the result.

### SDK and plugin facts

- The core SDK's `JobSubmissionConfig.auto_approve_quote` defaults to `True`,
  so a direct `submit_job` or a Qiskit `backend.run` spends without asking;
  a run from this repository sets it `False` and approves the quote itself.
- The CLI parses `--organization` but `JobSubmissionConfig` receives no
  organization, plan or priority: it runs `auto` plan and priority on the
  SDK's default organization and asks before a positive quote unless
  `--auto-approve` is given. It has no prepare-only mode and no
  `configuration_data`.
- The Qiskit `OQBackend.run` result carries `job_id="oq_job_id_placeholder"`;
  the platform job id comes from the scheduler. Its `memory` is synthesized
  from counts, and `OQSampler` pads a short count total with all-zero
  bitstrings and truncates a long one to the PUB's shots, so a run retains
  the platform's own counts beside any Qiskit result.

## Accounts, credits and public runs

The live account (`catalogue.json`, `account`) holds one organization,
25 Spark Credits, 0 Full Credits and no jobs.

| Item | Rule | Source |
|---|---|---|
| Spark Credits | free; Public execution plan only; expire 90 days after grant | `docs/concepts/credits.md` |
| Grant | 25 Spark Credits, published as $50 of compute, at signup and again every 90 days; each later batch is claimed by hand on the free-credits page, never added automatically | `site/free-credits.md` |
| Referral | 25 Spark Credits to the referrer per signup, no cap | `site/free-credits.md` |
| Classes | $50 of compute per student through a single class code for a verified course | `site/use-cases_professors.md` |
| Full Credits | purchased through Stripe; Public or Private; expire after 12 months | `docs/concepts/credits.md` |
| Consumption | earliest-expiring batch first; Public spends Spark before Full, Private spends Full only | `docs/concepts/credits.md` |
| Refund | automatic, to the original batches, when a job fails at any stage or a Pending job is cancelled | `docs/concepts/credits.md` |
| Active jobs | at most 10 Public and 100 Private per organization (Created, Pending, Queued or Running), counted separately | `docs/concepts/job-lifecycle.md` |
| Input | OpenQASM, at most 10 MB per file | `docs/concepts/job-lifecycle.md` |
| Retry | a failed execution retries up to 3 times before Failed | `docs/concepts/job-lifecycle.md` |
| Cancel | Pending only; Queued and Running jobs run to completion | `docs/concepts/job-lifecycle.md` |

**A public run.** Spark Credits pay only for the Public execution plan, so a
free run is a Public run: `prepare_job(..., execution_plan="public",
queue_priority="standard")`, read `estimated_credits`, `quote_summary` and
`spend_preview`, then `submit_job(preparation_id=...)` with the same plan
and priority. In the core SDK the same choice is
`JobSubmissionConfig(execution_plan=ExecutionPlanType.PUBLIC,
queue_priority="standard", auto_approve_quote=False)`. Standard priority
carries no surcharge; Priority and Instant add the quote's
`price_increase`.

**What public means.** The Public tier is the free tier, and it is not
confidential:

- circuits and results are broadcast to a decentralized network of operators
  run through qBitTensor Labs on the bittensor network, which execute and
  verify them; "Your circuits and results are not confidential in this
  tier", and Quantum Rings keeps a copy "for unlimited use, including
  research, analytics, product development, or AI training"
  (`site/quantumrings_privacy.md`);
- a public-mode circuit carries a "perpetual, irrevocable, worldwide,
  royalty-free, sublicensable, and transferable" license to store, use,
  reproduce, modify, distribute and derive from it for any purpose
  (`site/quantumrings_terms.md`, 5.2), and its retention "may be indefinite"
  while Private circuits are deleted after execution (6.4);
- research outputs materially derived from public mode (papers, preprints,
  presentations, datasets, models, repositories) credit Quantum Rings and the
  Open Quantum platform (3.4), with the BibTeX entry in `site/citation.md`
  (Zenodo DOI 10.5281/zenodo.22103261).

The upload in `prepare_job` already transfers the circuit, before any
credit moves. Private Compute keeps circuits confidential and costs Full
Credits only.

## Backends, shots and price

`docs/evidence/open_quantum/pricing.json` holds the pricing page's
USD-equivalent rates: a task fee and a per-shot rate per backend and plan
(the table shows the Public pair), Private exactly twice Public, which
`oq_platform.py check` requires. The page publishes no
credit-to-dollar rate. The scheduler's circuit-free estimate
(`POST /v1/pricing/estimate` with a backend class and shots, the call the
pricing calculator makes; it uploads nothing) answers in credits, and
`estimates.json` retains it at each backend's minimum and maximum shots and
at 100, 128, 1000, 1024 and 4096 inside those bounds. Every retained
estimate, on both plans, equals

    credits = ceil(per_task + shots * per_shot)

at one credit per USD-equivalent dollar, with Standard queue at +0 and
the Priority surcharge the table's last line gives; no Instant priority was
offered. `oq_platform.py check` holds every retained estimate to that rule.
So 25 Spark Credits buy 25 USD-equivalent of Public compute; the site's
"$50" equals the same work at the Private rate, twice the Public one. Every
job costs at least one whole credit, so a grant is at most 25 jobs.

The table is the facts table of this guide, rendered by
`oq_platform.py facts docs/evidence/open_quantum`; gate core-382 holds the
marked body here equal to it:

<!-- open-quantum-facts:begin -->
| backend (short code) | provider, modality | qubits (per job) | native ops | shots min / default / max | circuits per job | Public USD task + per shot | Public credits at 128 / 1024 / max shots | shots in a 1-credit job | 1024-shot jobs per 25 Spark |
|---|---|---|---|---|---|---|---|---|---|
| IBEX Q1 (`aqt:ibex-q1`) | AQT, Trapped-ion | 12 | prx, rz, xx | 1 / 100 / 2000 | 1024 | 0.18 + 0.0141 | 2 / 15 / 29 | 58 | 1 |
| Forte-1 (`ionq:forte-1`) | IonQ, Trapped-ion | 36 | gpi, gpi2, zz | 100 / 100 / 5000 | 1024 | 0.18 + 0.048 | 7 / 50 / 241 | - | 0 |
| Forte Enterprise (`ionq:forte-ent`) | IonQ, Trapped-ion | 36 | gpi, gpi2, zz | 100 / 100 / 5000 | 1024 | 0.18 + 0.048 | 7 / 50 / 241 | - | 0 |
| Emerald (`iqm:emerald`) | IQM, Superconducting | 54 | cc_prx, cz, measure_ff, prx | 1 / 100 / 20000 | 1024 | 0.18 + 0.00096 | 1 / 2 / 20 | 854 | 12 |
| Garnet (`iqm:garnet`) | IQM, Superconducting | 20 | cc_prx, cz, measure_ff, prx | 1 / 100 / 20000 | 1024 | 0.18 + 0.00087 | 1 / 2 / 18 | 942 | 12 |
| Cepheus-1-108Q (`rigetti:cepheus-1-108q`) | Rigetti, Superconducting | 108 (107 per job) | cz, rx, rz | 10 / 100 / 50000 | 1024 | 0.18 + 0.000255 | 1 / 1 / 13 | 3215 | 25 |

Features by backend: barriers: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; defcal: rigetti:cepheus-1-108q; dynamic_circuits: iqm:emerald, iqm:garnet; measure: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; mid_circuit_measure: ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet; physical_qubits: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; result_pragmas: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; verbatim_boxes: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q.

Queue priority increases in credits: Private Plan Priority Queue +2, Private Plan Standard Queue +0, Public Plan Priority Queue +2, Public Plan Standard Queue +0.
<!-- open-quantum-facts:end -->

Reading it for a free budget of 25 Spark Credits: a backend's 1-credit
column is the most shots one credit buys (a dash where its minimum shot
count already costs more), and the last column is how many 1024-shot jobs
one grant pays for. The MCP cap of 1 credit admits only 1-credit jobs; a
larger job needs `OPENQUANTUM_MCP_MAX_CREDITS` raised in both
registrations, a configuration change made with the case that needs it.
Whether a backend accepts jobs (`accepting_jobs`) changes between reads and
lives in `catalogue.json`, never in the table.

The platform accepts OpenQASM only (`supported_formats`); the constraint
documents in `catalogue.json` carry each backend's coupling map, supported
operation set and the features the table lists. The documents carry no gate durations (`timing.durations` is empty) and no noise
figures; `get_job_calibration` returns a calibration snapshot only for a
completed job on a backend that tags one.

## Use in this repository

- Every `prepare_job` and `submit_job` waits for the user's approval of a
  written case, as an IBM or Quantum Inspire submission does: what the run
  measures, why a noise simulation cannot answer it, the backend, shots,
  quoted credits, and the statement that its circuit becomes public. An
  upload for a quote is a publication and waits for the same approval.
- Before a case, read `status` and `accepting_jobs` (an Online backend can
  refuse jobs) and re-snapshot; quote limits and prices from the snapshot,
  never from memory.
- A run retains the submitted QASM and its sha256, the backend's constraint
  document at submission, organization-free plan and priority, shots, the
  preparation id and quote, the platform job id, the full output and
  calibration downloads, and the package versions, under
  `results/open_quantum/runs/`; the research-state registry gains an
  `open_quantum` provider adapter in the change that retains the first run.
- Published work derived from Public Compute cites the infrastructure as
  `site/citation.md` gives it.
- CI never imports the stack: its gates read retained JSON with the standard
  library. Unpublished methods stay off the Public tier.

## Gates

Gates core-380 (`capture_oq_docs.py --check`), core-381 (its `--self-test`),
core-382 (`oq_platform.py check docs/evidence/open_quantum --agents
docs/notes/open_quantum/README.md`) and core-383 (its `--self-test`) hold the
captures, the facts table and the credit rule.
