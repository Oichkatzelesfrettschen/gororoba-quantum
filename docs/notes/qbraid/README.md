# qBraid

qBraid (<https://www.qbraid.com>) is a broker and simulator platform: one
REST API, `https://api-v2.qbraid.com/api/v1`, reaches its own CPU and GPU
simulators and routes jobs to AWS Braket, Azure, IonQ, IQM, Rigetti, Open
Quantum and others (documentation <https://docs.qbraid.com/v2/home/introduction>).
The account is on the Free plan by inference and holds no credits, so its use
here is the free simulators and the read-only surface. Every account fact
below comes from the read-only probe of 2026-10-24; the live API and docs
stay the authority.

| Path | Content |
|---|---|
| `docs/` | every docs page that `llms.txt` lists, 163 pages as served Markdown, with `llms.txt` and `llms-full.txt` (`scripts/capture_qbraid_docs.py --docs`) |
| `api/` | the REST API OpenAPI document `openapi-v2.json` (`--api`) |
| `pypi/` | release metadata and file sha256 of `qbraid` 0.13.0 and `qbraid-core` 0.6.36 (`--pypi`) |
| `requirements-qbraid.txt` | the environment lock |

`capture_qbraid_docs.py --check` rechecks every captured byte offline
(`tests/test_cli_record_checks.py`), and its `--self-test` proves the check
rejects removed, unlisted and altered files.

## Environment and credential

```sh
QB_ENV=$HOME/.local/share/qbraid/venv
QB_PYTHON=${QB_PYTHON:-$QB_ENV/bin/python}
uv venv --python 3.13 "$QB_ENV"
VIRTUAL_ENV="$QB_ENV" uv pip install -r docs/notes/qbraid/requirements-qbraid.txt
```

The key is one line in `~/.config/qbraid/api-key` (directory 700, file 600),
read inside Python and sent as the `X-API-KEY` header, or passed as
`QbraidProvider(api_key=key)`; the SDK's own `~/.qbraid/qbraidrc` stays
unused. The API allows 1,000 authenticated requests per 15 minutes and
answers 429 beyond (docs, "Rate limiting").

## API surface

| Call | Returns |
|---|---|
| `GET /billing/credits/balance` | qBraid and AWS credit balances, auto-recharge state |
| `GET /billing/credits/pricing` | credit rate (100 credits = 1 USD), minimum purchase 5 USD |
| `GET /usage/simulator` | per-simulator daily usage, quota, remaining and `resetsAt` |
| `GET /devices`, `GET /devices/{qrn}`, `GET /devices/{qrn}/calibrations` | the 38-device catalogue with pricing and status; calibration data |
| `GET /jobs`, `/jobs/summary`, `/jobs/statuses`, `/jobs/group` | job lists and counts |
| `GET /jobs/cost-estimate?deviceQrn=..&shots=..` | a cost quote in credits; creates nothing |

A device is named by its QRN `vendor:provider:type:name`. `PATCH
/usage/simulator/settings` changes billing and counts as an approval-gated
action.

## Allotment

| Item | Value | Source |
|---|---|---|
| Balance | 0 qBraid credits, 0 AWS credits, auto-recharge disabled | `GET /billing/credits/balance` |
| Managed simulators | 100 jobs per simulator per UTC day on Free (500 on Standard, unlimited on Pro) | docs `home/pricing`; API `quota` |
| GPU simulators | 25 circuits per GPU simulator per UTC day on Free; beyond it, refused unless usage-based billing is on, then 5 credits a minute with a 3 s minimum | docs `home/pricing`; API `autoSwitchToCredits` |
| Reset | daily at 00:00 UTC (`resetsAt`) | API |
| Plans | Free $0, Standard $20 a month, Pro $100 a month; Free includes 100 CPU hours a month of lab compute and 15 GB storage | docs `home/pricing` |
| Credit expiry | not stated | open |

The API names no plan; Free is inferred from quotas equal to the Free plan's.

## Devices usable at zero cost

| QRN | Qubits | Shots | Daily allowance |
|---|---|---|---|
| `qbraid:qbraid:sim:qir-sv` | 30 | 2,000 | 100 jobs |
| `qbraid:quobly:sim:alloy-forge` | 10 | 1,000 | 100 jobs |
| `ionq:ionq:sim:simulator` | 29 | 1,000,000 | 100 jobs |
| `qbraid:qbraid:sim:gpu-sv` | 35 | 1,000,000 | 25 circuits |
| `qbraid:qbraid:sim:gpu-tn` | 500 | 10,000 | 25 circuits |

The `openquantum:*` devices carry no qBraid price and bill the linked Open
Quantum account instead, under its public-data terms (root AGENTS.md,
"Hardware services"). The priced QPUs (AWS-routed IonQ, IQM, Rigetti,
QuEra and AQT; direct Rigetti Cepheus) need credits. The six `ibm:ibm:qpu:*`
entries are dynamic-priced, return no quote and stay hidden by the SDK;
IBM is a self-managed provider reached with the repository's own IBM
account. `GET /usage/simulator` also lists Quantinuum and QUDORA emulators
that `GET /devices` omits.

## Data terms

`https://www.qbraid.com/terms` and `/privacy` are placeholders ("in legal
review"), so no retention, privacy or license text governs submitted
circuits; routed jobs fall under each hardware vendor's terms. Nothing
confidential is submitted.

## Use in this repository

The GPU tensor-network simulator (500 qubits) and the 35-qubit GPU
statevector reach past the build host and Kaggle, so a qBraid job is
warranted for a noiseless reference too wide for them, or for the Quobly
emulator as a device model. Every job waits for the owner's approval of a
written case (root AGENTS.md, "Hardware services"), and the free daily
allowance is the budget it states. No adapter or MCP server exists yet; a
first run adds one with its retained-run directory under `results/qbraid/`.
qBraid's own MCP server is documented at `docs/v2/ai/integrations/mcp-server.md`
and is not registered.
