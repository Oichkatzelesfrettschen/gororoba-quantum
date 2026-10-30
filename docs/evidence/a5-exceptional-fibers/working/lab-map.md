# Lab map: every machine, service and API available to the repository (2026-10-29 UTC)

Evidence tags: **M** = measured by a command run on 2026-10-29 for this map; **M0** = measured on 2026-10-29 and
carried over from the previous version of this file (not rerun); **D** = documented in the cited file, whose own
date governs. Paths are relative to the primary checkout (~/Projects/IBMQuantum) unless they begin with `~`.
Credential files are named by environment variable or path pattern only. Policy authorities: AGENTS.md (approval
rules), docs/runbooks/compute-flags.md (flag review, memory rule), docs/PYTHON.md (interpreters),
docs/notes/kaggle/ (Kaggle). Live provider pages outrank every D row.

Standing rules that bind every layer below (AGENTS.md "Hardware services", "QPU time and calibration", "Seeds"):

| Rule | Statement | Tag | Source |
| --- | --- | --- | --- |
| Job approval | every job (QPU, emulator, simulator, mock), upload, provider QRNG read, timeslot booking and notebook session on any provider waits for the user's approval of a written case | D | AGENTS.md |
| Routing | simulation of 14 qubits or fewer runs on Kaggle; 15 qubits is decision-gated; IBM hardware serves 16 or more qubits or a device-itself question | D | AGENTS.md |
| Seeds | every new random seed comes from a QRNG draw (ANU first) | D | AGENTS.md "Seeds" |
| Flag review | every costly command passes docs/runbooks/compute-flags.md first | D | AGENTS.md |
| Read-only | status, calibration, catalogue and balance reads need no approval | D | AGENTS.md; docs/notes/ibm_quantum/account-access.md |

## 1. Local hardware (build host)

| Resource | Value | Tag | Source |
| --- | --- | --- | --- |
| CPU | AMD Ryzen 5 5600X3D, 6 cores / 12 threads, 96 MiB L3 | M | `lscpu` |
| RAM | 62 GiB total; 32 GiB used and 30 GiB available at read time; swap is not headroom | M | `free -g` |
| GPU | NVIDIA GeForce RTX 4070 Ti, 12,282 MiB, driver 615.78.08, SM 89 (Aer, cuStateVec; no GPU path for Groebner or rank) | M | `nvidia-smi`; docs/PYTHON.md |
| CUDA stack | CUDA 13.4.3, cuQuantum 26.09.0.8 (libcustatevec.so.1, libcutensornet.so.2), cutensor 2.8.1.0 | D | docs/PYTHON.md |
| Disk, root | 3.6 TB NVMe, 3.2 TB used, 394 GB free (90 % full) | M | `df -h /` |
| Disk, /tmp | 125 GB, 58 GB free, separate device | M | `df -h /tmp` |
| OS | CachyOS (Arch), Linux 7.2.11-1-cachyos | M | environment |
| Simulator ceilings | GPU density matrix 14 qubits, statevector 29; CPU density matrix 15 (17 s), statevector 31 (74 s); never CPU widths above 56 GiB (DM 16, SV 32) | D | memory note build-host-substrate.md (2026-10-16); docs/notes/kaggle/substrates.md |
| Memory rule | every heavy job in a `systemd-run --user --scope -p MemoryMax=NG -p MemorySwapMax=0` scope; systemd-oomd kills the session tab above about 90 % RAM+swap (incident 09:45 UTC 2026-10-29); never `prlimit --as` | M0 | docs/runbooks/compute-flags.md |
| Timers | user unit `gororoba-credits.timer` (daily 14:00 UTC provider-credit snapshot) is active | M | `systemctl --user is-active` |
| Container runtime | podman builds the runner-image replay (`ci/runner_image.sh`) | D | ci/AGENTS.md |
| Cleanup classes | scratch / rebuildable / retained / credential; deletion through `trash-put` | D | docs/runbooks/cache-locations.md |
| Cache root | `${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum` (`$GQ`); CI venv `ci-py3.14.7-qiskit261` | M0 | docs/runbooks/cache-locations.md |
| Credential store | `~/.qiskit/qiskit-ibm.json`, `~/.config/<provider>/...` mode 600, `~/.quantuminspire/config.json`, `~/.aws/config` | D | AGENTS.md "Records"; provider guides |

## 2. Local software stacks and interpreters

| Environment | Interpreter variable and location | Contents | Tag | Source |
| --- | --- | --- | --- | --- |
| Build host system | `$PYTHON` (Python 3.14, system) | qiskit 2.6.1, qiskit-aer-cuda 0.18.2-3 (cuStateVec), qiskit-ibm-runtime 0.51.0, samplomatic 0.21.0, Perceval 1.3.1, numpy, scipy, sympy, python-flint, cvxpy, mcp | D | docs/PYTHON.md; docs/notes/build_host/python-stack.md |
| CI / PR | Python 3.14.7, `ci/pinned_tool.py` | ruff 0.17.1, mypy 2.4.0 via uv; `ci/requirements-ci.txt` | D | docs/PYTHON.md |
| Browser checks | `ci/requirements-browser.txt` | playwright 1.64.0 | D | docs/PYTHON.md |
| Replay runtime | `REPLAY_PYTHON` | Qiskit 2.5.2, pydantic 2.13.5, ibm-quantum-schemas 0.12.20260921, samplomatic 0.21.0; gates marked runtime `qiskit-2.5` | D | docs/PYTHON.md; ci/requirements-replay.txt |
| Quantum Inspire | `QI_PYTHON`, `QI_ENV=~/.local/share/quantuminspire/venv` (Python 3.13) | quantuminspire 4.1.0, qxelarator, libqasm, opensquirrel, qiskit-quantuminspire (Qiskit < 2.4) | D | docs/notes/quantum_inspire/README.md |
| Open Quantum | `OQ_PYTHON`, `OQ_ENV=~/.local/share/openquantum/venv` (Python 3.14) | openquantum-sdk 1.0.0, openquantum-mcp 0.2.0, openquantum-sdk-qiskit 1.0.0, qiskit 2.5.2 | D | docs/notes/open_quantum/README.md |
| Quandela | system `$PYTHON` for Perceval; `QD_PYTHON` for the MCP server | perceval-quandela 1.3.1, exqalibur 1.4.2, scmver, mcp 1.29.0 | D | docs/notes/quandela/README.md |
| IQM Resonance | `iqm-python`, `/opt/iqm-resonance-stack` (Python 3.13, IQM OS 4.7) | iqm-client 36.0.0, qiskit 2.1.2, cirq-core, qrisp, iqm-pulla 15, iqm-pulse 15 | D | docs/notes/iqm/README.md |
| IonQ | `IONQ_PYTHON=/usr/bin/ionq-python` (`/opt/ionq-stack`, Python 3.13) or `~/.local/share/ionq/venv` | qiskit-ionq 1.1.1, Qiskit 2.6.1 | D | docs/notes/ionq/README.md |
| BlueQubit | `BQ_PYTHON=/usr/bin/bluequbit-python` (`/opt/bluequbit-stack`) | bluequbit 0.19.0b1 | D | docs/notes/bluequbit/README.md |
| Quafu | `QF_PYTHON=/usr/bin/quafu-python` (`/opt/quafu-stack`, Python 3.11) | pyquafu 0.4.5, numpy 1.26.4 | D | docs/notes/quafu/README.md |
| Origin Quantum | `OG_PYTHON=/usr/bin/originquantum-python` (`/opt/originquantum-stack`) | pyqpanda3 0.5.0 | D | docs/notes/originquantum/README.md |
| qBraid | `QB_PYTHON=/usr/bin/qbraid-python` (`/opt/qbraid-stack`); license keeps it on this machine | qbraid 0.13.0, qbraid-core 0.6.36 | D | docs/notes/qbraid/README.md |
| Planck | `PL_PYTHON=/usr/bin/planck-python`; account deleted 2026-10-25, package uninstalled, PKGBUILD kept | planck_sdk 1.0.0 | D | docs/notes/planck/README.md |
| Kaggle client | `kaggle` CLI 2.2.4, kagglesdk 0.1.37, kagglehub 1.0.2 as Arch packages | CLI, SDK, MCP at the Kaggle web host | D | docs/notes/kaggle/interfaces.md; libraries.md |
| AWS client | aws-cli v2 2.37.9 (Arch `extra`), profile `gororoba` | CLI, `uvx` proxy for `aws-mcp` | D | docs/notes/aws/README.md |
| Azure client | azure-cli 2.90.0 with `quantum` extension 1.0.0b30 | CLI | D | docs/notes/azure/README.md |
| Packaging | paru at /usr/bin/paru; `makepkg -si` in each PKGBUILD directory | local Arch packages | M | `which paru`; docs/notes/quandela/README.md |
| Package tree | 100 directories holding a PKGBUILD in ~/Github/PKGBUILDs | see section 3 | M | `ls -d */PKGBUILD` |
| Wheel packaging | `packaging/qiskit-aer-cuda/` (build==1.6.0, scikit-build==0.19.1, pybind11==3.1.0) | custom CUDA 13 Aer wheel | D | docs/PYTHON.md |
| Library register | 362 distributions with role and importing files | gate core-630 | D | docs/state/hypercomplex-libraries/libraries.md |
| Required environment | `export PYTHON="${PYTHON:-python3}"` and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` | an unexported `PYTHON` makes every gate exit 127 | D | AGENTS.md |

## 3. Algebra and symbolic tools

| Tool | Version | Role | Tag | Source |
| --- | --- | --- | --- | --- |
| Singular | 4.4.1 (x86_64, built 2026-06-30) | Groebner, `minAssGTZ`, `sat`; global orderings (`dp`, `lp`) only for exact replays | M | `Singular --version`; AGENTS.md "Computer algebra" |
| msolve | 0.11.0 | F4 elimination; flags in compute-flags.md (`-e`, `-g`, `-t`, `-s`, `-u`, `-l`) | M | `msolve -V`; docs/runbooks/compute-flags.md |
| Macaulay2 | 1.26.06-3 (makepkg build, dirty tree) | computer algebra | M | `M2 --version` |
| SageMath | 10.10 | exact algebraic geometry, rotation-composite audits | M | `sage --version` |
| PARI/GP | 2.19.0 | number theory | M | `gp --version-short` |
| giac | installed (`giac --version` printed no version line) | CAS | M | `giac --version` |
| python-flint | 0.9.0 (`nmod_mat` rank and nullspace) | modular rank, rational null spaces | M | `python3 -c "import flint"` |
| GAP, Maxima | on PATH (versions not read) | group theory, CAS | M | `which gap maxima` |
| Absent | Magma, Maple, Julia/OSCAR, CoCoA5 | none available | M | `which` |
| Rocq (opam) | pinned in `ci/rocq_toolchain.pin`; 9.3 with `-w @all` | formal certificates under proofs/ | D | ci/AGENTS.md; memory open-gororoba-rocq-reuse |
| Algebra reference packages | 17 hypercomplex packages (octonion, splitoct, clifford, galgebra, ...) checked against `cd_core` | tables in docs/evidence/algebra_packages/tables.json | D | docs/PYTHON.md |
| Exact arithmetic | `pyadic` (finite-field and p-adic valuations) | no Cayley-Dickson table | D | docs/PYTHON.md |
| Notable local PKGBUILDs | python-flint, python-qiskit-aer(-cuda), python-qiskit-ibm-runtime, python-qiskit-experiments, python-qiskit-serverless, python-qiskit-addon-{slc,utils}, python-perceval-quandela, python-perceval-interop, cuquantum, python-cuquantum, quantuminspire-qiskit-stack, iqm-resonance-stack, qbraid-stack, ionq-stack, bluequbit-stack, quafu-stack, originquantum-stack, planck-stack, kaggle-benchmarks-stack, kaggle-environments-stack, quantum-pipeline-stack | M | `ls -d */` in ~/Github/PKGBUILDs |
| Singular on remote VMs | from sage wheels (`~/tools/sage_wheels/bin/Singular`) plus msolve | Azure VM tools | M0 | prior lab-map |
| Flag authority | memory and time limits, threads, environment checked per tool against `--help` before every run | | D | docs/runbooks/compute-flags.md |
| Cost levers | planner stages, ghost replay, noise-model serialization reuse | | D | docs/runbooks/simulation-cost-levers.md |

## 4. Quantum providers

Common facts: every submit, upload, timeslot booking and QRNG read needs an approved case. "Read" means a
read-only call that spends nothing.

### 4.1 IBM Quantum (Heron r2)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Devices | ibm_fez, ibm_kingston, ibm_marrakesh: Heron r2, 156 qubits, heavy-hex, 352 coupling pairs, dt 4 ns | D | AGENTS.md; docs/notes/ibm_heron_platform.md |
| Basis | cz, id, rz, sx, x, xslow; fractional rx and rzz; measure_2, reset_2, dynamic circuits; `rep_delay_range` [0, 0.002] s | D | docs/notes/ibm_quantum/account-access.md; fractional-gates.md |
| Pulse access | removed by IBM on 2025-02-03 | D | AGENTS.md |
| Access route | qiskit-ibm-runtime 0.51 under `$PYTHON`; `gororoba_quantum/ibm_account.py open_service`; no IBM MCP server | D | docs/notes/ibm_quantum/account-access.md |
| Accounts | two saved accounts in `~/.qiskit/qiskit-ibm.json`: default (primary) and `backup-ibm-quantum-platform`; `GOROROBA_IBM_ACCOUNT` selects; quotas never pool | D | AGENTS.md; account-access.md |
| Quota | 600 s of quantum time per account on a rolling 28-day window; no reset date; the backup serves when primary remaining minus reserve falls below the case's summed ceilings | D | AGENTS.md "QPU time"; docs/notes/ibm_quantum/qpu-submission.md |
| Read surfaces | `service.usage()`, `backends()`, `backend.status()`, `.target`, `.properties()`, `.configuration()`, `service.jobs()`, `job.metrics()`, `job.result()` | D | account-access.md |
| Billing | per sub-job QPU lock time; failed jobs bill lock time consumed (2 to 5 s on four 2026-10-18 jobs) | D | account-access.md; ibm_heron_platform.md |
| Approval | every `--submit` waits for a written case; `sh scripts/approved_run.sh --check CMD -- FLAGS` binds dry run and submit; `--approved-record(-sha256)`, `--max-execution-seconds` | D | AGENTS.md |
| Calibration | fetched afresh by `live_run.py` in the deciding process; cadence 30 to 40 min; `scripts/wait_calibration.sh` chains a start | D | AGENTS.md; memory ibm-calibration-reads |
| Controls | `--exclude-qubits`, `approved_backend_scope`, calibration fingerprints, prediction reuse | D | docs/notes/ibm_quantum/qpu-submission.md; hardware-controls.md |
| Dynamic-circuit split | mid-circuit measurement, reset or feed-forward circuits go in their own job with twirling and DD off | D | AGENTS.md "Qiskit skills" |
| Reference docs | 18 transcribed guides (processor types, transpiler stages, timing, repetition rate, calibration jobs, run-time estimate) | D | docs/notes/ibm_quantum/README.md |
| Live data | `docs/evidence/heron_platform/targets.json` snapshots all 156 qubits and 352 pairs | D | AGENTS.md |

### 4.2 Quantum Inspire (QuTech)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Backends | QX emulator (10 qubits per API), Ry emulator (9 qubits, neutral-atom model), Tuna-5 (5 transmons, offline), Tuna-9 (9 transmons, offline), Tuna-17 (17 transmons, 24 couplers, online) | D | docs/notes/quantum_inspire/backends.md |
| Shots and run limit | 1024 to 2048 on emulators; 8192 default and 131072 maximum on Tuna; 300 s on Tuna, 3600 s on emulators | D | backends.md |
| Account | one free account type with access to every listed backend; transaction ledger shows no metered charge after 42 jobs (2026-10-16) | D | docs/notes/quantum_inspire/usage.md |
| Access routes | `qi` CLI (4.1.0), REST, SDK, Qiskit, PennyLane; login `qi login`; tokens in `~/.quantuminspire/config.json` | D | setup.md; AGENTS.md |
| MCP | `quantum-inspire`: qi_backends, qi_backend, qi_compile, qi_submit, qi_submit_case, qi_run_local, qi_job(s), qi_results, qi_usage, qi_hardware_status, qi_performance_dashboard, qi_performance_query | D | docs/notes/quantum_inspire/mcp.md; MCP tool list |
| Exposes | submit, compile, local qxelarator run, job and result reads, usage ledger, public Grafana status and calibration | D | mcp.md |
| Limits | Tuna-9 Q8 carries a two-level-system message; Tuna-17 q9 idle P1 about 0.27 (design without q9); 30 s pause between batches, ladder to 120 s on failure, 3 circuits | D | tuna-9.md; memory tuna17-q9-readout-shift |
| Result order | qubit-0-leftmost on Ry; see `qx-runs.md` for the measurement-register root cause | D | ry-emulator.md; qx-runs.md |

### 4.3 Open Quantum (broker)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Backends | aqt:ibex-q1 (12 trapped-ion), ionq:forte-1 and ionq:forte-ent (36 trapped-ion), iqm:emerald (54), iqm:garnet (20), rigetti:cepheus-1-108q (108, 107 per job) | D | docs/notes/open_quantum/README.md facts table |
| Credits | Spark 25 granted at signup and every 90 days (claimed by hand), Public plan only, expire after 90 days; Full credits purchased, expire after 12 months; refund on failure or cancel | D | open_quantum/README.md "Accounts, credits and public runs" |
| Cost rule | credits = ceil(per_task + shots x per_shot), per_task 0.18 USD-equivalent; Private plan twice Public; Priority +2 credits; minimum 1 credit per job | D | open_quantum/README.md |
| Privacy | Public Compute makes every circuit and result public; unpublished methods stay off it | D | AGENTS.md |
| Access | SDK 1.0.0 (`OpenQuantumClient`, `SchedulerClient`), SDK CLI, Qiskit plugin (`OQBackend`, `OQSampler`, `OQEstimator`), portal; key file named by `OPENQUANTUM_SDK_KEY` (path `~/.config/openquantum/sdk-key.json`) | D | open_quantum/README.md |
| MCP | `openquantum`, 13 tools: list_organizations, get_credits, list_backends, get_backend, list_job_categories, prepare_job, submit_job, wait_for_job, get_job, list_jobs, get_job_results, get_job_calibration, cancel_job; `OPENQUANTUM_MCP_MAX_CREDITS` 1 here; `confirm_spend` gates Full credit spend | D | open_quantum/README.md; MCP server instructions |
| Read-only snapshot | `scripts/oq_platform.py snapshot` (organizations, credits, backends, constraint documents, categories) | D | open_quantum/README.md |

### 4.4 Quandela Cloud (photonic)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| QPUs | qpu:ascella (1..12 modes, 1..6 photons), qpu:belenos (1..24 modes, 1..12 photons); threshold detectors; 300 s per job | D | docs/notes/quandela/README.md platform table |
| Simulators | sim:ascella (Arcturus), sim:belenos, sim:slos, sim:sampling, sim:gpu:small, sim:gpu:medium (decommissioned) | D | same |
| Credits | Explorer offer: 200 free credits per calendar month (UTC reset, no carry-over); QPU 1.0 base credit per job plus 1e-06 per shot; simulators bill fractional per-shot credit | D | quandela/README.md "Explorer plan"; legal ToS 13.3 |
| Access | REST https://api.cloud.quandela.com; Perceval 1.3.1 (system Python); `scripts/qd_platform.py`; token file named by `QUANDELA_TOKEN_FILE`; Jupyter, Quantum Toolbox, Usage Explorer on the portal | D | quandela/README.md |
| MCP | `quandela` (repository-owned, `scripts/qd_mcp_server.py`, `QD_PYTHON`): qd_platforms, qd_platform, qd_availability, qd_plan, qd_simulate_local, qd_job_status, qd_job_result, qd_job_billing, qd_cancel_job, qd_usage; verb-specific Bash denies guard the token | D | quandela/README.md; memory quandela-token-deny-rules |
| Local simulation | `qd_simulate_local` (SLOS, Naive; at most 24 modes, 1,000,000 output states) | D | quandela/README.md |
| Schedules | GitHub Actions `quandela-schedule.yml` and `quandela-record-watch.yml` | D | docs/runbooks/quandela-scheduled-runs.md; .github/workflows |
| Caution | shared token: other sessions can cancel our jobs | D | memory quandela-shared-token-cancels |

### 4.5 IQM Resonance (superconducting)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Emerald | 54 qubits, 90 couplings, 20000 shots, 100 circuits, 0.75 credits/s, timeslot 2400 per hour | D | docs/notes/iqm/README.md facts table |
| Garnet | 20 qubits, 30 couplings, 20000 shots, 100 circuits, 0.50 credits/s, timeslot 1800 per hour | D | same |
| Sirius | 16 qubits plus COMPR1 resonator, 24 couplings, `move` gate, 0.30 credits/s, timeslot 1080 per hour | D | same |
| Mocks | emerald:mock (54), garnet:mock (20), sirius:mock (24); free | D | same |
| Account | PERSONAL; 30.00 credits expiring 2026-11-01 (monthly grant, up to 30 credits per month); 2.50 left on 2026-10-26 | D | iqm/README.md; memory iqm-billing-and-reset-facts |
| Gates | cc_prx, cz, measure, measure_012, prx, prx_12, reset_wait; cc_prx needs passive reset and same-probe-line pairs | D | iqm/README.md; memory |
| Access | IQM Server API v1 https://resonance.iqm.tech; iqm-client 36.0.0; token pair file named by `IQM_TOKENS_FILE` | D | iqm/README.md |
| MCP | `iqm`: iqm_quantum_computers, iqm_quantum_computer, iqm_architecture, iqm_metrics, iqm_queue_availability, iqm_timeslots, iqm_job, iqm_job_artifact, iqm_cancel_job, iqm_credit, iqm_tokens, iqm_artifact | D | MCP tool list; iqm/README.md |
| Exposes | submit circuit, run (protobuf) and sweep; calibration sets and dynamic architecture; queue availability; timeslot book and cancel; GraphQL credit | D | iqm/README.md API table |
| Billing | ceil(runtime in seconds) x rate; mocks free | D | memory iqm-billing-and-reset-facts |

### 4.6 Other providers

| Provider | Devices | Quota and cost | Access | Status | Tag | Source |
| --- | --- | --- | --- | --- | --- | --- |
| IonQ | simulator (29 qubits, noise models ideal, aria-1, aria-2, forte-1, forte-enterprise-1); qpu.forte-1 (36, all-to-all) | simulator free; QPU needs organization credit (0.249 credits per compute second); 1,000,000 shots, 5000 circuits per job | REST api.ionq.co/v0.4; key at `~/.config/ionq/api-key`; `GET /jobs/estimate` creates nothing | simulator-only key; no adapter yet | D | docs/notes/ionq/README.md |
| BlueQubit | cpu (34 qubits statevector), mps.cpu (96), pauli-path (192), GPU variants, quantum (108) | Free: cpu 50,000 jobs per day, 60 min per job; others credit-only; balance read by `GET /balance` | REST app.bluequbit.io/api/v1; key at `~/.config/bluequbit/api-key`; `bq.estimate()` counts as a submission | Free plan inferred; no adapter yet | D | docs/notes/bluequbit/README.md |
| Quafu (BAQIS) | ScQ-Sim10, ScQ-P5 (5, queue about 1750), Baihua (119) online; others offline or obsolete | no quota route; browser only | pyquafu 0.4.5; token at `~/.config/quafu/api-token` | open access; no adapter yet | D | docs/notes/quafu/README.md |
| Origin Quantum | WK_C180 (166 usable of 180), WK_C180_2 (17), WK_C180_3 (30), PQPUMESH8 (3); simulators 35 / 68 / 200 | 60 s Wukong grant at registration; usage = 0.3 s overhead x multiplier + runtime | pyqpanda3 0.5.0; key at `~/.config/originquantum/api-key`; HTTPS URL passed explicitly | no adapter yet | D | docs/notes/originquantum/README.md |
| qBraid | 38-device catalogue (broker to Braket, Azure, IonQ, IQM, Rigetti, Open Quantum); own CPU and GPU simulators; Lab | Free tier: 100 jobs per simulator per UTC day; 25 GPU circuits per day; 100 Lab CPU hours (renews 2026-11-10); AI allowance 5 USD; 0 credits; 1000 requests per 15 min | REST api-v2.qbraid.com/api/v1; key at `~/.config/qbraid/api-key` | Free; read-only catalogue plus simulators | D | docs/notes/qbraid/README.md |
| Planck | digital twin (returns random bits) | none | account deleted 2026-10-25 | closed; source audit only | D | docs/notes/planck/README.md |
| Azure Quantum | quantinuum.sim.h2-1sc (syntax checker), h2-1e (emulator), pasqal.sim.emu-free, rigetti.sim.qvm; no hardware | 1,000 eHQC one-time on H2 emulator (HQC = 5 + C(N1q + 10 N2q + 5 Nm)/5000); Pasqal 5 emulator hours per month | `az quantum` extension; workspace `gororoba-quantum`, eastus | free plans only; trial spending limit on | D | docs/notes/azure/README.md |
| AWS Braket | not available to the project (managed SCP denies every Braket call) | n/a | n/a | excluded | D | docs/notes/aws/README.md |

## 5. QRNG sources (seed draws)

| Order | Source | Quota | Credential | Approval | Tag | Source |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ANU Quantum Numbers (keyed), `scripts/anu_qrng.py draw` | 100 requests per calendar month, 1 per second, up to 1024 uint16 values per request | key file under `~/.config/anu-qrng/` (mode 600) | none | D | docs/notes/qrng/README.md |
| 2 | ANU legacy (keyless), `draw --source legacy` | 1 request per minute; to be retired | none | none | D | same |
| 3 | Cisco Outshift QRNG, `scripts/outshift_qrng.py draw` | 100000 bits per month; 1 to 10000 bits per block, 1 to 1000 blocks per request | key file under `~/.config/outshift-qrng/` | none | D | same |
| 4 | Quandela Cloud QRNG, `scripts/quandela_qrng.py draw --approved-case FILE` | priced per byte through the account offer; CHSH must exceed 2 and stay at most 2 sqrt 2 | Quandela token | approved case required | D | same |
| pending | QCi uQRNG | free to 1 Gbit per month | token pending | n/a | D | same |

Each draw writes `docs/evidence/<source>/draw-<UTC>.json` with raw bytes and sha256; `ci/seed_provenance.py`
requires every integer seed literal to be a row of `ci/reproduction_seeds.json` or an allocation in
`docs/evidence/qrng_seeds/allocations.json`; runtime seeds go through `qrng_seeds.add_seed_argument`
(`qrng:<draw>#<index>`, the flag default, or `repro:<integer>`) (D, AGENTS.md "Seeds").

## 6. Cloud compute

| Platform | Resource | Value | Tag | Source |
| --- | --- | --- | --- | --- |
| Azure VM | size | Standard_FX4mds_v2: 4 vCPU, about 82 GiB RAM, retail about 0.547 USD/h | M0 | prior lab-map |
| Azure VM | quota | 4 regional vCPUs in eastus and 4 in westus2: one FX4mds_v2 per region at a time | M0 | prior lab-map |
| Azure VM | instances | gororoba-a5-fiber (eastus) and gororoba-a5-fiber-2 (westus2), both deallocated, disks retained; a case file is required per VM start (approved: azure-cases/vm2-fiber-b.md) | M0 | prior lab-map |
| Azure VM | failures | address-space cap at 32 GiB stopped e8_nm_fiber at 17 h; VM 2 lost ssh at about 20:38 UTC with 58 GB headroom (cause unidentified) | M0 | prior lab-map |
| Azure subscription | offer | FreeTrial_2014-09-01, 200 USD credit for 30 days, spending limit on; upgrade is the owner's decision | D | docs/notes/azure/README.md |
| Kaggle TPU | v5e-8 VM | 224 logical CPUs (`os.cpu_count`), about 390 to 400 GB available RAM; 9 h session cap, 20 h per week | M0 | prior lab-map; docs/notes/kaggle/README.md |
| Kaggle TPU | quota | 7,390 s used of 72,000 s; refresh 2026-10-31T00:00Z | M0 | prior lab-map |
| Kaggle GPU | T4 x2 or P100 | 11,920 s used of 108,000 s; at most two GPU batch sessions per account; 29 to 30 GB host RAM, 4 cores, 12 h | M0 / D | prior lab-map; substrates.md |
| Kaggle CPU | session | 4 cores, about 30 GB, 12 h; no accelerator quota; 20 GB saved output | M0 / D | prior lab-map; docs/notes/kaggle/README.md |
| Kaggle observed | msolve E8bar to VB | degree-16 matrix 86M x 88M, peak about 209 GB, about 23 effective cores, cancelled near 7,380 s (initiator unresolved) | M0 | prior lab-map |
| Kaggle observed | TPU smoke kernel | a5-fiber-tpu-smoke queued 6+ h with no v5e-8 assignment; earlier TPU pushes ran on 4-core CPU machines | M0 / D | prior lab-map; tpu-research.md |
| Kaggle accelerators | IDs (Sept 2026) | NvidiaTeslaT4 (2 x T4), NvidiaTeslaA100, NvidiaL4, NvidiaL4X1, NvidiaH100, NvidiaRtxPro6000, TpuV5E8, TpuV6E8; push with `--accelerator` | D | docs/notes/kaggle/README.md |
| Kaggle interfaces | CLI 2.2.4, kagglesdk 0.1.37, kagglehub 1.0.2, MCP https://www.kaggle.com/mcp (76 tools: notebooks sessions, datasets, models, competitions, quota, benchmarks) | D | docs/notes/kaggle/interfaces.md; MCP tool list |
| Kaggle workflow | `scripts/kaggle_run.py push/status/collect`; `scripts/kaggle_sessions.py quota`; every GPU push needs `--timeout`; collect reads per-version output through kagglesdk | D | docs/notes/kaggle/workflow.md; interfaces.md |
| Kaggle capacity | T4 density matrix 14, statevector 29; T4 x2 cache blocking DM 15, SV 30; TPU host RAM 34/35 qubit SV (unreached) | D | docs/notes/kaggle/substrates.md |
| AWS | project on the free plan, Region us-east-2 (other regions denied), 100.00 USD credit (99.91 on 2026-10-28), plan end 2027-04-24; Braket excluded; no instances running | D | docs/notes/aws/README.md; free-plan-usage.md |
| AWS | tooling | `aws-mcp` server (proxy `mcp-proxy-for-aws==1.7.0`, profile `gororoba`), 24 installed skills, 115 remote skills (2026-10-24); sessions renew via `aws login`; 2026-10-29 re-read stopped on an expired session | D | docs/notes/aws/README.md |
| AWS | EC2 | ordinary On-Demand `RunInstances` allowed in us-east-2; host tenancy, instance-store root, spot denied | D | aws/README.md |
| GitHub Actions | hosted runners | `ubuntu-26.04` (jobs in pr.yml, ci.yml, null-shards.yml, quandela workflows), `ubuntu-24.04` (one ci.yml job), `ubuntu-latest` (pr-agent.yml); about 4 logical CPUs and 16 GB; standing approval for slow classical jobs and nulls | M / D | `grep runs-on .github/workflows`; docs/runbooks/ci-runtime.md |
| Provider credits | daily snapshot of IBM, Kaggle, IQM, Open Quantum, Quandela, Quantum Inspire, qBraid, BlueQubit, AWS, Azure, ANU; IonQ, Quafu, Origin Quantum read `not readable` | D | docs/runbooks/provider-credits.md |

## 7. Cloud LLM and APIs

| Service | Models and credit | Access | Tag | Source |
| --- | --- | --- | --- | --- |
| AWS Bedrock | ordinary inference is priced and draws the 100 USD plan credits; cross-region Bedrock invoke meters sit outside the region policy; the Bedrock-playground activity pays a 20 USD reward on completion (status NOT_STARTED); model list not captured in the repository | `aws bedrock-runtime` through profile `gororoba`; `aws-mcp`; skill `amazon-bedrock` | D | docs/notes/aws/free-plan-usage.md |
| AWS SageMaker, Rekognition, Lex, Polly | credit-metered; SageMaker free meter is a short trial and not active | AWS CLI | D | free-plan-usage.md |
| Azure AI services | none attached to the subscription; the only Azure resource is the Quantum workspace and its storage account | `az` | D | docs/notes/azure/README.md |
| Anthropic (Claude) | Claude Code session model; subagents capped at 2 at once (haiku lookup, sonnet build, opus review); usage-limited | Claude Code `Agent` tool | D | memory no-background-agents-except-haiku |
| OpenAI (through Codex CLI) | see section 8 | Codex CLI 0.165.0 | M | `codex --version` |
| Google Gemini API (through opencode) | 35 `google/` models, including gemini-2.5 and 3.x flash and pro, gemini-3.8-flash, gemini-4-argon, gemma-4 (26b, 31b), deep-research, image and Lyria models, embeddings | `opencode` 2.1.2 | M | `opencode models` |
| Google Antigravity (through opencode) | `google/antigravity-claude-opus-4-6-thinking`, `-claude-sonnet-4-6`, `-gemini-3-flash`, `-gemini-3-pro`, `-gemini-3.1-pro` | `opencode`; also `agy` CLI | M | `opencode models` |
| Groq (through opencode) | 7 models: allam-2-7b, llama-prompt-guard-2 (22m, 86m), gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen3.8-27b | `opencode` | M | `opencode models` |
| OpenAI API (through opencode) | 83 `openai/` models | `opencode` | M | `opencode models` |
| Qwen (through opencode) | `qwen/coder-model` | `opencode` | M | `opencode models` |
| Gemini CLI 0.46.0 | installed, but refused: the client is retired for the individual tier | `gemini` | M / D | `gemini --version`; prior lab-map |

## 8. Local LLMs and review CLIs

| Tool | Version | Capability | Tag | Source |
| --- | --- | --- | --- | --- |
| Codex CLI | 0.165.0 | `codex exec -m MODEL -c model_reasoning_effort=EFFORT -s workspace-write -C DIR -o OUT`; models in models_cache.json: gpt-6.1-sol, gpt-6.1-terra (500k context), gpt-6-sol, gpt-6-astra, gpt-6-luna, gpt-5.6-sol, -terra, -luna, gpt-daybreak-blue-latest (272k to 500k context, efforts low to ultra); gpt-6-sol at low effort is the cheap delegate, gpt-6-astra costs more than a Claude frontier model and is never the delegate; hidden entries gpt-reserve and codex-auto-review | M | `codex --version`; ~/.codex/models_cache.json; ~/AGENTS.md |
| Codex review roles | reviews and diagnoses read-only (tmux TUI, gpt-daybreak-blue-latest LOW by default); Claude implements every change; hosted `@codex review` on pull requests is the only hosted reviewer | D | memory codex-cli-reviews-in-tmux; AGENTS.md "Reviews and merges" |
| opencode | 2.1.2 | multi-provider agent CLI: providers google (35), ollama (28), groq (7), openai (83), qwen (1) | M | `opencode models` |
| grok CLI | 1.0.70 (stable) | Grok Build TUI; flags `--agent`, `--agents`, `--allow`, `--deny`, `--always-approve`, `--cwd`, `--add-dir`, `--continue`; prior use: referee report docs/archive/reviews/2026-10-27-ascella-replication-review-grok.md | M / D | `grok --help` |
| agy CLI | 1.4.10 | `--print`, `--model`, `--effort low..max`, `--mode accept-edits/auto/plan`, `--output-format json/stream-json`, `--json-schema`, `mcp`, `models`, `plugin`, `--sandbox`; prior use: docs/archive/reviews/2026-10-27-ascella-replication-review-agy.md | M / D | `agy --help` |
| Gemini CLI | 0.46.0 | refused for this account tier | M | `gemini --version` |
| ollama | 0.40.7, local tags (27 listed) | glm-4.7-flash (19 GB; 64k and 128k variants; uncensored variant), qwythos-9b (10 GB; 64k, 128k), qwenseer-2b (1.3 GB), qwen3.8 distill 9b and 4b, qwen3.8-27b IQ2_XXS (8.2 GB; 64k, 128k), qwen3.5-4b, gemma-4-26b (17 GB; 256k), whiterabbitneo-2.5-coder-7b, foundation-sec-8b-instruct, rwkv7-g1k (7.9 GB) | M | `ollama list` |
| Local-LLM limit | 12 GiB VRAM; models above it spill to RAM; text outputs are never evidence | D | docs/notes/kaggle/substrates.md ("Gemma inference ... never evidence") |
| Claude subagents | max 2 at once; check usage before launching; two sonnet launches once consumed 94 % of the budget | D | memory agent-launch-usage-budget |
| MCP servers (repository) | `quantum-inspire`, `openquantum`, `quandela`, `iqm`, `kaggle`, plus `aws-mcp` (Claude, Codex, Gemini CLI, OpenCode, Windsurf, Grok, Agy) | D | AGENTS.md; docs/notes/aws/README.md; MCP tool list |
| Skills | migrate-qiskit-ibm-runtime (pinned upstream a5499c7c); 24 AWS skills; Codex skills under ../.codex/skills | D | AGENTS.md "Qiskit skills" |
| Review runbook | critical peer review criteria (12 items) | D | docs/runbooks/critical-peer-review.md |

## 9. CI

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Workflows | ci.yml (nightly audit, 8 jobs), pr.yml (lint, types, tests, gates), null-shards.yml (2 jobs), pr-agent.yml, quandela-schedule.yml, quandela-record-watch.yml | M | `ls .github/workflows` |
| PR checks | `sh ci/pr_checks.sh lint|types|tests|gates`; branch protection requires all four on the head; gates of at most 15 measured seconds that the diff reaches | D | AGENTS.md |
| Audit | `ci.yml` runs every gate, retained-evidence replays, Rocq replays and the ledger nightly on main; a failing run updates the issue "Nightly audit failing" | D | AGENTS.md |
| Runner profile | about 4 logical CPUs, 16 GB, AMD EPYC 7763 / 9V45 / 9V74; Python 3.14.7; QI lane uses 3.13 | D | docs/runbooks/ci-runtime.md |
| Measured run cost | PR run 674 s wall, 2,678 s runner time; main run 2,885 s wall (1,040 s queue delay) | D | ci-runtime.md |
| Gate machinery | `ci/run_gates.py`, `ci/gates.json`, `ci/gate_ledger.py`, `ci/premerge_gates.py`, `ci/runner_image.sh` (podman replay), `ci/gate_timings.json` | D | ci/AGENTS.md; ci/ listing |
| Shards | null calibrations offloaded to GitHub Actions shards | D | docs/runbooks/null-shards.md |
| Style gates | `"$PYTHON" ci/pinned_tool.py ruff format --target-version py313`, `ruff check`, `mypy` | D | AGENTS.md |
| Review loop | `@codex review` per push; `scripts/codex_review_status.sh`, `scripts/resolve_answered_threads.sh`; merge via `gh api` REST with merge commit | D | AGENTS.md "Reviews and merges" |

## 10. Repo tree

| Path | What lives there | Tag | Source |
| --- | --- | --- | --- |
| gororoba_quantum/ | 169 entries: runtime modules run as scripts (not a package): `cd_core.py` (canonical Cayley-Dickson specification), `live_run.py`, `experiments.py`, `parallel.py`, `ibm_account.py`, `local_compute.py`, `qpu_planning.py` | M | `ls gororoba_quantum`; AGENTS.md |
| scripts/ | 321 entries: provider adapters (`qd_platform.py`, `qi_platform.py`, `oq_platform.py`, `iqm_platform.py`), MCP servers, QRNG draws, `kaggle_run.py`, `approved_run.sh`, `provider_credits.py`, plan tracker, source-registry tools | M | `ls scripts` |
| ci/ | gate runner, gate ledger, pins, replay and Rocq machinery, seed provenance, reproduction seeds | M | `ls ci` |
| tests/ | 27 top-level entries: pytest suites (`tests/scripts/`, gate-contract tests); the `audit` marker holds replays | M | `ls tests` |
| kaggle_kernel/ | `kernel_main.py`, `gpu_env_report.py`: the entry that runs inside Kaggle sessions | M | `ls kaggle_kernel` |
| proofs/ | Rocq certificates (TargetFlipN21, FoldAverageDescent, TerminalChannelSeparation, C881) | D | AGENTS.md |
| packaging/ | `qiskit-aer-cuda` wheel build | M | `ls packaging` |
| plans/ | plan records beside docs/state/plans.md | M | `ls plans` |
| literature/ | link to docs (`literature -> docs` keeps recorded paths) | D | AGENTS.md |
| docs/notes/ | provider guides (ibm_quantum, quantum_inspire, open_quantum, quandela, iqm, ionq, bluequbit, quafu, originquantum, planck, qbraid, aws, azure, kaggle, qrng, build_host), source notes, topic notes | M | `ls docs/notes` |
| docs/evidence/ | 150 replay and evidence directories (account snapshots, heron_platform targets, QRNG draws, ledgers) | M | `ls docs/evidence` |
| docs/runbooks/ | operator procedures (compute-flags, ci-runtime, cache-locations, provider-credits, simulation-cost-levers, null-shards, evidence-closure, plan-tracker) | M | `ls docs/runbooks` |
| docs/state/ | generated registries: research_state.json, plans, hypercomplex-libraries | D | AGENTS.md |
| docs/design, docs/archive, docs/sources, docs/pdf | designs and plans; handoffs and review reports; source ledgers; retained PDFs | M / D | docs/README.md |
| docs/local/ | ignored session scratch (this file, BUILD_HOST.md, plans) | D | AGENTS.md |
| results/ | audit records: hw_estimate, live, quandela, quantum_inspire, open_quantum, iqm, kaggle, local_compute, local-simulation, hypercomplex, ripple | M | `ls results` |
| Worktrees | 15 listed by `git worktree list` (primary checkout, one under `~/worktree`, one `a9e6`-named agent tree, twelve under `~/worktrees/IBMQuantum/<branch>` named for their topic, e.g. a5-kernel-attachments, kaggle-stacks, msq-envelope-backend, pin-baseline) | M | `git worktree list` |
| Current branch | experiment/ascella-21pair-octonion-atlas with uncommitted Ascella character scripts and results | D | gitStatus at session start |

## 11. Policy gates

| Gate | What it blocks | Tag | Source |
| --- | --- | --- | --- |
| Approved written case | any submit, upload, QRNG read, booking, notebook session | D | AGENTS.md |
| Approved record binding | `--submit` runs only after the plan matches the record's digest; a mismatch writes `approval_required` and sends nothing | D | AGENTS.md; qpu-submission.md |
| 15-qubit gate | a 15-qubit run waits for a written case naming the substrate | D | AGENTS.md |
| Public-data gate | Open Quantum Public Compute publishes circuits and results | D | AGENTS.md |
| Flag review | every solver, simulator, pool or launcher command | D | docs/runbooks/compute-flags.md |
| Memory scope | heavy jobs in capped `systemd-run` scopes, one at a time | M0 / D | compute-flags.md; memory oomd-kills-session-tab |
| Azure VM case file | each VM start needs a case file | M0 | prior lab-map |
| Spend policy | AWS credits and Azure trial: upgrade to a paid plan is the owner's decision alone | D | aws/README.md; azure/README.md |
| Seed provenance | integer seed literals must come from QRNG allocations or the reproduction ledger | D | ci/seed_provenance.py |
| Mock outcomes | `--native-dry-run` timing never enters scientific analysis | D | AGENTS.md |
| Retained bytes | files bound by a ledger or digest keep path and bytes | D | AGENTS.md "Documents" |
| Merge gate | pr.yml `lint`, `types`, `tests`, `gates` green plus Codex review loop | D | AGENTS.md |
| Delete | `trash-put`, never `rm -rf` | D | ~/AGENTS.md |
| Secrets | tokens, account ids, CRNs, emails, local absolute paths stay out of commits; an IBM instance is named by a 12-hex sha256 of its CRN | D | AGENTS.md "Records" |

## 12. Gaps (capabilities documented but not confirmed in this pass)

- Live provider state (queues, balances, device status) was not read: no provider call was permitted. Every Quantum
  Inspire, IQM, Quandela, Open Quantum, qBraid and IBM figure is the dated D value, and the credit snapshot
  (`latest.md` under `${XDG_STATE_HOME:-~/.local/state}/gororoba-quantum/credits/`) was not opened.
- Kaggle and Azure rows marked M0 (TPU and GPU quota used, VM state, Kaggle capacity) were not re-measured; the
  Kaggle TPU v5e-8 assignment has never been confirmed in this tree and earlier pushes ran on 4-core CPU machines.
- AWS Bedrock: the model list, regional availability and per-token credit cost are not recorded anywhere in docs/notes/aws;
  the AWS session had expired on 2026-10-29, so no live read was possible.
- Azure AI services (Foundry, OpenAI): no document and no resource; the subscription holds only the Quantum workspace.
- giac, GAP and Maxima versions were not captured; Rocq/opam version on this host was not run.
- IonQ, BlueQubit, Quafu and Origin Quantum have no adapter or MCP server; their guides record probes of 2026-10-24
  only, and Quafu and Origin Quantum quotas are readable only in a browser.
- Grok and agy model catalogues (`grok models`, `agy models`) were not listed; their provider credit and rate limits are
  undocumented in the repository.
- Local-LLM throughput on the RTX 4070 Ti and the ollama GPU offload fraction were not measured.
- QCi uQRNG token is pending; the Quandela QRNG `count` unit (bytes or integers) is unsettled until a first approved draw.
- Heron r3 and Nighthawk appear in docs/notes/ibm_quantum/processor-types.md, but the account reaches Heron r2 only.
- Remote-host CPU/RAM figures for the Azure VMs and Kaggle sessions are per prior measurement; no unified host
  inventory beyond the primary build host exists in the repository.

## 13. Review-model catalogues (measured 2026-10-29)

| CLI | Models | Tag | Source |
| --- | --- | --- | --- |
| grok 1.0.70 | grok-4.7 (default), grok-4.7-build-fast, grok-4.6, grok-4.5 | M | `grok models` |
| agy 1.4.10 | gemini-4-argon low/medium/high, gemini-3.8-flash low/medium/high, claude-opus-5-5 and claude-sonnet-5-5 low/medium/high, gpt-oss-120b medium | M | `agy models` |
| opencode 2.1.2 | groq: gpt-oss-120b, gpt-oss-20b, qwen3.8-27b (fast inference); google incl. antigravity and gemini-3.8-flash; openai; 28 ollama tags | M | `opencode models` |
| AWS Bedrock | session expired at read time; model list not captured | M | `aws` session state |

## 14. Reset and expiry times, Pacific and UTC side by side

Read 2026-10-29 16:34 PDT (23:34 UTC) from the 15:21 UTC credits snapshot. US Pacific leaves daylight time on
Sunday 2026-11-01 at 02:00, so dates from Nov 1 on are PST (UTC-8); earlier ones are PDT (UTC-7).

| Resource | Remaining | Pacific | UTC |
| --- | --- | --- | --- |
| qBraid simulator daily quotas | 100 jobs x9, 25 GPU circuits x2 | Thu 2026-10-29 17:00 PDT | 2026-10-30 00:00 |
| Kaggle TPU (weekly) | 17.95 of 20 h | Fri 2026-10-30 17:00 PDT | 2026-10-31 00:00 |
| Kaggle GPU (weekly) | 26.69 of 30 h | Fri 2026-10-30 17:00 PDT | 2026-10-31 00:00 |
| IQM Resonance (expiry) | 2.5 credits | Sat 2026-10-31 17:00 PDT | 2026-11-01 00:00 |
| Quandela Cloud (monthly reset) | about 96 of 200 | Sat 2026-10-31 17:00 PDT | 2026-11-01 00:00 |
| Azure Quantum Pasqal emulator | 5 h | Sat 2026-10-31 17:00 PDT | 2026-11-01 00:00 |
| ANU QRNG (monthly) | 66 of 100 requests | Sat 2026-10-31 17:00 PDT | 2026-11-01 00:00 |
| IBM primary (rolling 28 d) | 68 s; next 9 s returns | Sun 2026-11-08 07:31 PST | 2026-11-08 15:31 |
| qBraid AI allowance | 5 USD | Tue 2026-11-17 23:33 PST | 2026-11-18 07:33 |
| IBM backup (rolling 28 d) | 160 s; next 40 s returns | Sun 2026-11-22 11:40 PST | 2026-11-22 19:40 |
| AWS Free plan credits | 179.91 USD | Sat 2027-04-24 11:14 PDT | 2027-04-24 18:14 |
| Open Quantum Spark | 25 credits | expiry not reported | - |
| Azure Quantum Quantinuum | 1,000 eHQC, one-time | no reset | - |
