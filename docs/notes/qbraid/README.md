# qBraid

qBraid (<https://www.qbraid.com>) is a broker and simulator platform: one
REST API, `https://api-v2.qbraid.com/api/v1`, reaches its own CPU and GPU
simulators and routes jobs to AWS Braket, Azure, IonQ, IQM, Rigetti, Open
Quantum and others (documentation <https://docs.qbraid.com/v2/home/introduction>).
`GET /users/verify` names `subscriptionTier` Free, and the wallet holds no
credits, so the working surface is the free simulators, the included Lab
allowance, and read-only catalogue calls. Device figures are the read-only
probe of 2026-10-24. Lab profiles, capacity, the CPU-hour renewal, storage,
and the AI reset are the read-only probe of 2026-10-28. The live API and the
captured docs stay the authority.

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

On the build host the Arch package `qbraid-stack` from the local PKGBUILD tree
(`~/Github/PKGBUILDs/qbraid-stack`) installs the same SDK as a hash-locked Python
3.13 environment under `/opt/qbraid-stack` and the interpreter `/usr/bin/qbraid-python`
(qbraid 0.13.0 and qbraid-core 0.6.36); its `check()` runs an offline test, kept at
`/usr/share/qbraid-stack/test_qbraid_stack.py`. A case sets `QB_PYTHON=/usr/bin/qbraid-python`; the venv
above serves a machine without the package. The qbraid-core wheel carries the "qBraid Commercial Software License" (all rights reserved, authorized licensees only), so the built package stays on this machine and is not redistributed.

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
| `GET /users/verify` | `subscriptionTier` and a validity flag |
| `GET /compute/profiles` | the Lab profile catalogue: spawner, host size, GPU model, rate |
| `GET /compute/bma/availability` | on-demand capacity, region counts, and the effective credit rate |
| `GET /compute-sessions/usage` | CPU-hour quota and `renewalDate`, storage quota, on-demand debt |
| `GET /compute/servers/status` | whether the subscription Lab server is running |
| `GET /ai/quota` | AI allowance and `resetDate` |

The captured `api/openapi-v2.json` stops at jobs, devices, credit balance,
and simulator usage. The Lab and quota routes above are the ones qbraid-core
0.6.36 calls. A device is named by its QRN `vendor:provider:type:name`.
`PATCH /usage/simulator/settings` changes billing and counts as an
approval-gated action.

## Allotment

| Item | Value | Source |
|---|---|---|
| Balance | 0 qBraid credits, 0 AWS credits, auto-recharge disabled | `GET /billing/credits/balance` |
| Managed simulators | 100 jobs per simulator per UTC day on Free (500 on Standard, unlimited on Pro) | docs `home/pricing`; API `quota` |
| GPU simulators | 25 circuits per GPU simulator per UTC day on Free; beyond it, refused unless usage-based billing is on, then 5 credits a minute with a 3 s minimum | docs `home/pricing`; API `autoSwitchToCredits` |
| Reset | daily at 00:00 UTC; the 2026-10-28 read named `resetsAt` 2026-10-29T00:00:00Z | API |
| Plans | Free $0, Standard $20 a month, Pro $100 a month | docs `home/pricing` |
| Account plan | Free | `GET /users/verify` `subscriptionTier` |
| Lab CPU hours | 0 used of 100; renews 2026-11-10T05:00:22Z; auto-switch off | `GET /compute-sessions/usage` |
| Lab storage | 0 of 15 GB; the payload has no expiry | same route, `diskUsage` |
| AI allowance | $5 allowed, $0 used; resets 2026-11-18T07:33:30Z; auto-switch off | `GET /ai/quota` |
| Credit expiry | not stated | balance and pricing return no expiry field |

The included Lab server draws the CPU-hour allowance. On-demand instances
draw credits and have no expiry field of their own. Detail is in
[Lab compute](#lab-compute).

## Lab compute

The included Lab CPU and storage and the on-demand CPU and GPU instances have
product pages in the captured [pricing](docs/v2/home/pricing.md),
[usage limits](docs/v2/lab/user-guide/usage-limits.md),
[on-demand instances](docs/v2/lab/user-guide/on-demand-instances.md), and
[GPUs](docs/v2/lab/user-guide/gpus.md). The rows below are `GET
/compute/profiles` joined to `GET /compute/bma/availability`. That
availability document was cached at 2026-10-28T19:00:33.380Z with `ttlSec`
360. `listCreditsPerHour` matched `effectiveCreditsPerHour` on every row,
and `discountPct` was 0. One hundred credits equal one US dollar, so the
credit rate is the dollar rate times 100. `creditCost` on a profile is that
hourly credit rate divided by 60, in credits per minute.

`spawnerType` `docker-vm` is an on-demand instance. A missing spawner is a
subscription server, and those six slugs are absent from the availability
document. `billingMode` `payg` is set on `gpu-a10`, `gpu-a100-2x`,
`gpu-a100-4x`, `gpu-a100-8x`, `gpu-h100-2x`, `gpu-h100-4x`, `gpu-b200-2x`,
`gpu-b200-4x`, and `gpu-b200-8x`. The other on-demand profiles leave
`billingMode` empty and still bill credits. The same day's `GET
/compute/servers/status` reported the subscription server stopped on cluster
`lab2`. No on-demand instance was allocated.

GPU profiles carry `availability.pct30d`. Those stamps are
2026-06-03T21:35:10Z, except `gpu-a100-sxm` at 2026-06-03T18:10:18Z. The
percentage is that June field, not the October capacity snapshot. On-demand
CPU profiles have no `pct30d` and an empty region list; their availability
`hasCapacity` is null while the profile's own `hasCapacity` is true.

### Included servers

The CPU and memory columns are `kubespawner_override.cpu_limit` and
`mem_limit`. The limit equals the guarantee. Display names say 2, 4, and 8
vCPU; the limits are 1.8, 3.6, and 7.4. Memory matches the names. The rate
is the overflow price. With auto-switch off, included use draws CPU hours
and this rate is idle. Only the Free rows draw this account's allowance.
Standard and Pro rows are in the catalogue under those plan tags.

| Slug | Display | Plan tag | CPU limit | Memory | Overflow rate | Profile capacity |
|---|---|---|---:|---:|---|---|
| `2vCPU_4GB` | Small | Free | 1.8 | 4 GB | $0.002/min, 0.2 credits/min | true |
| `2vCPU_4GB_VSCODE` | Small, VS Code | Free | 1.8 | 4 GB | $0.002/min, 0.2 credits/min | true |
| `2vCPU_4GB_INTEL` | Small, Intel Quantum SDK | Free | 1.8 | 4 GB | $0.002/min, 0.2 credits/min | true |
| `4vCPU_8GB` | Medium | Standard | 3.6 | 8 GB | $0.004/min, 0.4 credits/min | true |
| `8vCPU_25GB` | Large | Pro | 7.4 | 25 GB | $0.008/min, 0.8 credits/min | true |
| `vscode_8vCPU_25GB` | Large, VS Code | Pro | 7.4 | 25 GB | $0.008/min, 0.8 credits/min | true |

### On-demand CPU

The instance type and host size are `spawner_config`. Credits per hour are
the availability document.

| Slug | Cloud | Instance type | vCPU | RAM | Credits/hour | Profile capacity |
|---|---|---|---:|---:|---:|---|
| `cpu-4v-6g` | gcp | `e2-custom-4-6144` | 4 | 6 GB | 15 | true |
| `cpu-4v-16g` | azure | `Standard_D4as_v5` | 4 | 16 GB | 24 | true |
| `cpu-8v-32g` | nebius | `cpu-d3:8vcpu-32gb` | 8 | 32 GB | 48 | true |
| `cpu-32v-128g` | azure | `Standard_D32as_v5` | 32 | 128 GB | 192 | true |
| `nanoacademic-small` | azure | `Standard_D32as_v5` | 32 | 128 GB | 192 | true |
| `cpu-64v-256g` | azure | `Standard_D64as_v5` | 64 | 256 GB | 384 | true |
| `nanoacademic-medium` | azure | `Standard_D96as_v5` | 96 | 384 GB | 576 | true |

`nanoacademic-small` and `nanoacademic-medium` are the same host sizes as
`cpu-32v-128g` and a 96-vCPU Azure host, with a pre-baked Nanoacademic image
(`nanodcal` / `RESCU`). `documentationDetails` on `cpu-4v-16g` names Azure
`Standard_D4s_v3` while `spawner_config` names `Standard_D4as_v5`. The same
`Standard_D4s_v3` sentence is copied onto `cpu-32v-128g`, `cpu-64v-256g`,
and `cpu-4v-6g`. The spawner instance type is the launch spec; `cpu-4v-6g`
launches the GCP custom machine above, not that Azure size.

### On-demand GPU models

`gpu_spec` supplies vendor, model, variant, count, and `vram_gb` per card.
Host CPU and RAM are `spawner_config.cpu_limit` and `mem_limit`. NVIDIA is
the vendor on every row. An empty variant means `gpu_spec.variant` was
empty. Highlights on the single A100 and H100 also name PCIe alongside SXM,
and the H100 highlight adds NVL.

| Slug | Model | Variant | Count | VRAM each | Host CPU | Host RAM | Vendors |
|---|---|---|---:|---:|---:|---:|---|
| `gpu-l4` | L4 | | 1 | 24 GB | 12 | 48 GB | RunPod |
| `gpu-l40s` | L40S | | 1 | 48 GB | 16 | 64 GB | RunPod, Nebius |
| `gpu-rtx-4090` | RTX 4090 | | 1 | 24 GB | 16 | 62 GB | RunPod |
| `gpu-rtx-5090` | RTX 5090 | | 1 | 32 GB | 16 | 48 GB | RunPod |
| `gpu-rtx-6000-ada` | RTX 6000 Ada | | 1 | 48 GB | 16 | 94 GB | RunPod |
| `gpu-a10` | A10 | | 1 | 24 GB | 28 | 180 GB | Lambda |
| `gpu-a100-sxm` | A100 | SXM | 1 | 80 GB | 24 | 125 GB | RunPod |
| `gpu-a100-2x` | A100 | | 2 | 40 GB | 56 | 380 GB | Lambda |
| `gpu-a100-4x` | A100 | | 4 | 40 GB | 116 | 760 GB | Lambda |
| `gpu-a100-8x` | A100 | | 8 | 40 GB | 120 | 1700 GB | Lambda |
| `gpu-h100-sxm` | H100 | SXM | 1 | 80 GB | 16 | 125 GB | Nebius, RunPod, Lambda |
| `gpu-h100-2x` | H100 | | 2 | 80 GB | 48 | 420 GB | Lambda |
| `gpu-h100-4x` | H100 | | 4 | 80 GB | 100 | 850 GB | Lambda |
| `gpu-h100-8x` | H100 | | 8 | 80 GB | 200 | 1800 GB | Lambda |
| `gpu-h200` | H200 | | 1 | 141 GB | 16 | 180 GB | Nebius, RunPod |
| `gpu-gh200` | GH200 | | 1 | 96 GB | 64 | 432 GB | Lambda |
| `gpu-b200` | B200 | | 1 | 180 GB | 20 | 224 GB | Nebius, RunPod, Lambda |
| `gpu-b200-2x` | B200 | | 2 | 180 GB | 48 | 680 GB | Lambda |
| `gpu-b200-4x` | B200 | | 4 | 180 GB | 100 | 1360 GB | Lambda |
| `gpu-b200-8x` | B200 | | 8 | 180 GB | 200 | 2750 GB | Lambda |

Highlights state a different host than the spawner on several profiles. The
spawner numbers are the table. The highlight host is the range or the
larger figure:

| Slug | Highlight host |
|---|---|
| `gpu-l40s` | 16 vCPU, 64–94 GB |
| `gpu-a10` | 30 vCPU, 200 GB |
| `gpu-a100-2x` | 60 vCPU, 400 GB; VRAM called 40–80 GB per card |
| `gpu-a100-4x` | 120 vCPU, 800 GB; VRAM called 40–80 GB per card |
| `gpu-a100-8x` | 124–240 vCPU, 1800 GB; VRAM called 40–80 GB per card |
| `gpu-h100-sxm` | 16–26 vCPU, 125–225 GB |
| `gpu-h100-2x` | 52 vCPU, 450 GB |
| `gpu-h100-4x` | 104 vCPU, 900 GB |
| `gpu-h200` | 16–24 vCPU, 180–200 GB |
| `gpu-b200` | 20–28 vCPU, 224–250 GB |
| `gpu-b200-2x` | 52 vCPU, 720 GB |
| `gpu-b200-4x` | 104 vCPU, 1440 GB |
| `gpu-b200-8x` | 208 vCPU, 2900 GB |

`gpu-h100-8x` highlights 640 GB total, which is 8 times the 80 GB
`vram_gb`. The multi-B200 highlights name Blackwell and 180 GB per card.
`gpu_spec` still leaves their variant empty.

### On-demand GPU availability

Profile capacity is `hasCapacity` on the profile. Availability capacity,
the capacity note, and region counts are the cached availability document.
An empty region cell means that document sent no region rows. Route quotes
are `documentationDetails` strings that begin "Routes across"; they are
vendor quotes, and the billed rate is the credits-per-hour column.

| Slug | Credits/hour | Profile capacity | Availability capacity | Note | Regions | 30-day % | Route quotes |
|---|---:|---|---|---|---|---:|---|
| `gpu-l4` | 49 | true | true | low | | 94.9 | RunPod $0.392 |
| `gpu-l40s` | 228 | true | true | low | eu-north1: 0 | 91.2 | RunPod $0.862; Nebius $1.823 |
| `gpu-rtx-4090` | 87 | true | true | high | | 88 | RunPod $0.692 |
| `gpu-rtx-5090` | 124 | true | true | medium | | 100 | RunPod $0.992 |
| `gpu-rtx-6000-ada` | 92 | true | true | low | | 89.9 | RunPod $0.738 |
| `gpu-a10` | 162 | true | true | | us-east-1: 1; us-west-1: 1 | 97.6 | |
| `gpu-a100-sxm` | 249 | true | true | low | | 100 | RunPod $1.492; Lambda $1.992 |
| `gpu-a100-2x` | 498 | false | false | | | 0 | |
| `gpu-a100-4x` | 995 | false | false | | | 0 | |
| `gpu-a100-8x` | 2790 | false | false | | | 72.7 | |
| `gpu-h100-sxm` | 537 | true | true | high | eu-north1: 75 | 100 | Nebius $2.954; RunPod $3.292; Lambda $4.292 |
| `gpu-h100-2x` | 1048 | false | false | | | 23.4 | |
| `gpu-h100-4x` | 2045 | false | false | | | 5.8 | |
| `gpu-h100-8x` | 3990 | false | false | | | 7.2 | Lambda $31.923 |
| `gpu-h200` | 549 | true | true | medium | eu-north1: 10; eu-west1: 9; us-central1: 14 | 100 | Nebius $3.5; RunPod $4.392 |
| `gpu-gh200` | 287 | false | false | | | 36.4 | Lambda $2.292 |
| `gpu-b200` | 874 | false | false | | us-central1: 0 | 97.4 | Nebius $5.5; RunPod $5.892; Lambda $6.992 |
| `gpu-b200-2x` | 1723 | false | false | | | 0 | |
| `gpu-b200-4x` | 3395 | false | null | | | 0 | |
| `gpu-b200-8x` | 6690 | false | false | | | 8.6 | |

`gpu-l40s` in eu-north1 and `gpu-b200` in us-central1 report available 0.
`gpu-b200-4x` is the one row whose profile capacity is false while the
availability capacity is null. Launch of any on-demand profile still
requires credits, and the wallet balance is 0.

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
