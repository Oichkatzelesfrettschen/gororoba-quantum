# Kaggle GPU simulation for design validation

Kaggle notebooks supply free accelerator hours that suit noise simulation of
designs before any QPU case. Their results are numerical simulations: they
validate a design or price a readout, and they never stand in for a hardware
result or an approval.

## What the hours buy

- **Accelerators.**
  - GPU: one P100 (16 GB) or two T4s (2 x 16 GB).
  - TPU: a v5e-8 replaced the v3-8 in 2025.
  - The weekly GPU quota is reported at about 30 hours with sessions of
    about 12 hours. Kaggle shows the live figure in the account settings
    and changes it without notice, so a plan reads the quota there.
- **Aer on GPU.** The CUDA 12 wheel `qiskit-aer-gpu` stops at 0.15.1 on
  PyPI and ships no wheel for Python 3.13, which Kaggle kernels run. The
  CUDA 11.8 build `qiskit-aer-gpu-cu11` carries the pinned 0.17.2 for
  Python 3.13 and runs on Kaggle's CUDA 12 driver, so kernels install
  `qiskit==2.5.2` with `qiskit-aer-gpu-cu11==0.17.2`. It runs
  statevector, density-matrix and unitary methods with
  `AerSimulator(device="GPU")`. Kaggle's own numpy and scipy (2.1.3 and
  1.16.3 on the T4 image) differ from the repository pins; every run
  records them in `environment.json`.
- **TPU.** Aer has no TPU backend. TPU hours help only simulators written in
  JAX, for example batched density-matrix contractions. None exists in the
  repository, so the TPU stays unused until a design needs one.

## Which designs need it

A complex128 density matrix on n qubits takes `16 * 4^n` bytes: 4 GiB at 14
qubits, 16 GiB at 15 and 64 GiB at 16, before Aer's workspace. On a 16 GB
GPU a density-matrix run therefore fits up to about 14 qubits with headroom;
15 qubits fill the card. A 2xT4 pair does not pool into one 32 GB device for
a single matrix. The GPU's gain is speed at 10 to 14 qubits and throughput
for batched trials, not width. Candidates:

| Design | Qubits | Why a GPU helps |
| --- | --- | --- |
| Census-frequency witness over sampled sedenion triples | 4 data + control, many circuits | thousands of per-triple noisy runs |
| Signed kernel probe at hardware noise | 7 | sweeps over t and noise scale |
| Walk scaffold under coherent over-rotation and leakage models | 4 | separates hypothesis 3's candidates against the retained floors |
| Detuning map designs (checkerboard Ramsey) | a patch, not the chip | power and winding analysis at realistic visibility |

The four-qubit and two-qubit designs run on the CPU here in seconds, so the
GPU matters for sweeps and batched trials, not for single circuits.

## Workflow

`scripts/kaggle_run.py` is the path from the repository to Kaggle:

- `push ENTRY --slug SLUG [--include FILE] [-- ARGS]` bundles ENTRY with
  its repository imports and named data files, writes a private kernel (a
  CPU machine by default) and pushes it. The kernel records its
  environment, runs ENTRY with `GOROROBA_AER_DEVICE` set to its device, and
  returns every file the run created under the repository root. A case
  passes `--machine NvidiaTeslaT4` when its widest density matrix reaches
  12 qubits, or 8 in a circuit with mid-circuit measurement: below that a
  Kaggle CPU kernel matches or beats a T4 (substrates.md, "CPU against
  T4"), and the weekly GPU quota goes to the runs that need it. The bundle
  travels inside run.py, and SaveKernel answers a bare 400 once run.py
  reaches about 1.35 MB while 0.63 MB pushes, so a data file of megabytes
  goes as a dataset instead.
- `dataset --slug SLUG --include FILE ...` uploads tracked files as a
  private dataset, one tar archive with its sha256 manifest, and records it
  under `results/kaggle/datasets/`; `push --dataset SLUG` attaches it, and
  the kernel verifies every file against the manifest before ENTRY runs. A GPU or TPU push needs
  `--timeout SECONDS` (at most four hours) and refuses while the slug's
  latest version is still running (next section). `--with GROUP` adds an
  opt-in package group from `PIN_GROUPS` (`quantum-tools`,
  `exact-arithmetic`) at the build host's versions, installed under a
  constraints file that holds the core pins and the image's numpy, scipy
  and JAX fixed; `pin_groups.json` records what installed. Every bundle
  carries the usage guides in `KERNEL_DOCS` (docs/notes/kaggle,
  docs/notes/packages, docs/notes/quantum-tools and the Qiskit ecosystem
  audit). A `Tpu*` machine is pushed as a notebook with latest image
  pinning, no `docker_image` and no notebook `kaggle` block, with the CPU
  build of Aer; batch pushes have not reached a TPU (next section).
- `shards [--tier pr] [--count N] [--only I,J] [--machine M,...]
  [--slot-wait S]` pushes one kernel per CI shard of the committed HEAD,
  with CI's shard count by default (6 for pr, 12 for full), on the first
  machine in the list with a free session; a default run waits up to two
  hours for sessions, since six shards outnumber the five CPU sessions. A
  commit that a branch of the canonical repository (`REMOTE`, whose branches
  `shards` mirrors under `refs/kaggle-shards/remote/`) contains is fetched as
  itself. Any other commit, a fork-only one included, is rebuilt from the
  merge base with that repository's main plus the bundled files
  changed since then, with their modes and deletions; Kaggle refuses a
  script near 1.7 MB (HTTP 400 on SaveKernel) and accepts 706 KB, so
  `shards` stops above `KERNEL_SOURCE_LIMIT` (1 MB) and asks for a push.
  Either way the kernel runs no gate unless `git write-tree` equals HEAD's
  tree. It then installs CI's
  Python through uv and CI's pins through `ci/install_pins.sh` (the script
  `.github/workflows/ci.yml` runs), and runs `ci/run_gates.py` on its
  shard with the CPU device. Shard runs live under the ignored
  `.kaggle-shards/`, iteration records and never evidence;
  `shards-report RUN_DIR...` prints each collected shard's summary and
  failing gates. CI stays the merge authority: a shard that passes on
  Kaggle and fails on CI exposes an environment difference. A machine list
  that names an accelerator needs `--timeout`, as `push` does.
- `status RUN_DIR` and `collect RUN_DIR` poll the kernel and download the
  run's own version with a sha256 manifest; `collect` reads that version
  through kagglesdk's `ListKernelSessionOutput` with `version_label vN`,
  because the CLI's `kernels output OWNER/SLUG/N` returns the latest
  version. `kernels status` reports the
  slug's latest version whatever version it names, so `collect` decides
  completion from the `exit.json` the kernel writes on every exit path; a
  version that returns none is not collected.
- `verify` checks every retained collect.json against its output files
  offline (gate core-290). Runs pushed before kernel versions were recorded
  also predate exit.json and keep the status Kaggle reported; the substrate
  probes of 2026-10-16T025230Z and T025231Z ended in ERROR because a
  capacity trial killed the kernel, which led to one process per trial,
  and the P100 probe is the record that a P100 request ran on two T4s.
- `push --smoke` (always on a GPU, `NvidiaTeslaT4` unless `--machine`
  names another accelerator) probes the environment and measures the widest
  density-matrix and statevector circuits the GPU runs; it carries a
  30-minute ceiling unless `--timeout` names another.
- `--machine` names the accelerator, passed to the push as
  `--accelerator`: `cpu` (the default, none), `NvidiaTeslaT4` (two T4s),
  or another ID from [cli/kernels.md](cli/kernels.md). `machine_shape` in
  kernel-metadata.json alone does not select hardware: probes that set only
  it for `NvidiaL4` and `TpuV5E8` ran on 4-core CPU machines, and
  `NvidiaTeslaP100`, absent from the current list, returned two T4s. A
  kernel's `environment.json`, not the request, records what ran.
- The account runs at most five CPU batch sessions at once, shared by
  every kernel it pushes; a sixth push fails with "Maximum batch CPU session
  count of 5 reached", and `shards --slot-wait` retries until a session
  ends. A `TpuV5E8` request draws on the same pool: with five CPU sessions
  running, it fails with the same CPU-count message (2026-10-16), so the
  GPU pool is the only capacity beyond the five. Neither a script nor a
  notebook kernel pushed with `--accelerator TpuV5E8` (plus
  `machine_shape`) receives a TPU: both ran on 4-core Xeon machines with no
  `/dev/accel*`, no TPU environment and JAX reporting only `cpu:0`, and
  `kaggle quota` kept TPU use at 0.00 h. The batch push exposes no docker
  image, while the MCP `create_notebook_session` call takes `docker_image`
  and `machine_shape`; whether a TPU VM image through that call reaches the
  TPU is untested. `shards --machine
  cpu,NvidiaTeslaT4` falls through to a GPU session when the CPU pool is
  full; a GPU session runs the shard on its 4-core host.
- The account runs at most two GPU batch sessions at once; a third push
  fails with "Maximum batch GPU session count of 2 reached", and `push`
  exits with that message and removes the unsent run directory, as it does
  for any failed push. A superseded version keeps its session until it
  ends: Kaggle's version list showed versions 2 and 3 of one T4 kernel
  both RUNNING after a re-push, each billing a T4 (next section).

A kernel holds no IBM credential, so its noise model comes from a retained
calibration export (`gororoba_quantum/calibration_snapshot.py --export
BACKEND --out FILE`), which refuses to write unless every gate and readout
channel it rebuilds equals live_run's noise model for the same fetch.

The CLI (`kaggle-api`), kagglesdk and kagglehub authenticate from the
access token in `~/.kaggle/` (mode 600), never from the repository; the
Kaggle MCP endpoint `https://www.kaggle.com/mcp` takes the same token as a
bearer header. [interfaces.md](interfaces.md) maps every CLI command, SDK
method and MCP tool onto the operations they share.

Each run directory under results/kaggle/ keeps submission.json (entry,
arguments, git commit, bundle digests, pins), the generated kernel, and
after collection the output with collect.json. Retaining it registers no
claim. A `numerical or stochastic simulation` claim in the research state
needs a replay gate that re-derives it in CI, so a Kaggle result becomes a
claim only once a reduced case reproduces it on the CPU under a gate. Until
then it informs a design as a retained artifact.

## Accelerator sessions: budget, finding and stopping a run

A GPU or TPU batch session bills its whole wall time against the weekly
quota (`kaggle quota`: 30 GPU hours and 20 TPU hours, refreshed weekly), and
a running session holds its `--timeout` as reserved time until it ends. A
CPU session draws on no accelerator quota; the account runs at most five
batch CPU sessions at once ("Maximum batch CPU session count of 5 reached"),
shared with every other session on the account.

**Prevention, enforced by `scripts/kaggle_run.py push`:**

- A non-CPU push needs `--timeout SECONDS`, at most four hours; Kaggle ends
  the session there. Without it a session runs to the 12-hour notebook
  limit.
- A non-CPU push refuses while the slug's latest version is RUNNING or
  QUEUED, because a new version leaves the old session running. Push under
  a new slug, or cancel the live version first.
- Route by measured cost: on the build host the CPU matches or beats the
  GPU for density matrices up to 8 active qubits and every retained IBM job
  replays at 1 to 6, so those runs go to `--machine cpu`. A GPU kernel does
  only work that needs the GPU; a CPU phase inside it (a CPU timing
  baseline, transpilation, Aer's shot-by-shot dynamic circuits) bills the
  GPU at CPU speed.
- Before and after an accelerator push, read the quota:
  `"$PYTHON" scripts/kaggle_sessions.py quota` prints used and reserved
  hours (`kaggle quota` prints no reserved time), and reserved time above the
  expected timeout means a session is running that should not be.

**Finding a running version.** Each kernel version runs as one session
whose id is the version's `scriptVersionId`; its page is
`https://www.kaggle.com/code/OWNER/SLUG?scriptVersionId=ID`, while
`https://www.kaggle.com/code/OWNER/SLUG` shows only the kernel. The Kaggle
CLI parses `OWNER/SLUG/N` and sends no version, so `kernels status`,
`output` and `logs` answer for the slug's latest version whatever N says;
kagglesdk and the Kaggle MCP take a version as the label `vN`
(`version_label`, `versionLabel`) and answer for it. None of them returns a
running version's session id. Kaggle's web API returns every version's id
and status through `kernels.KernelsService/ListKernelVersions`, which needs a
signed-in browser session:

```sh
"$PYTHON" scripts/kaggle_sessions.py versions OWNER/SLUG
```

copies the session files of the default Firefox profile (cookies,
certificate and key stores) into a private temporary profile, loads the
kernel page in headless Firefox, calls that endpoint with the page's XSRF
token, prints each version's session id, number, status and URL, and
deletes the copy. It prints no cookie value. The web UI's Active Events
pane listed one CPU kernel while two T4 versions were running, so it is not
an inventory of batch sessions.

**Stopping it.** `cancel_notebook_session` (Kaggle MCP) takes that session
id:

```sh
"$PYTHON" scripts/kaggle_sessions.py cancel SESSION_ID
"$PYTHON" scripts/kaggle_sessions.py cancel-running OWNER/SLUG   # every RUNNING or QUEUED version
"$PYTHON" scripts/kaggle_sessions.py quota                       # reserved time drops to 0
```

The script calls the MCP server over HTTP with the bearer header that
`~/.config/shell/kaggle-mcp-headers.sh` prints, so it needs no MCP tools in
the agent session; a session with the Kaggle MCP loaded can call
`cancel_notebook_session` directly with the same id. The version moves to
CANCEL_REQUESTED, then CANCEL_ACKNOWLEDGED, and the quota's reserved time
for it returns to zero. The version page in the web UI also stops a run.

**TPU.** The editor's session panel states that TPUs require identity
verification, and this account carries phone verification without Persona
identity verification; no route has attached a TPU to its sessions, and a
TPU push after verification is the test that decides the cause. Every
batch request (CLI script or notebook push, with or without an image pin or
`--accelerator`; MCP `save_notebook`; the editor's "Save & Run All
(Commit)") reached Kaggle's server with the TPU
accelerator recorded in the version's commit settings and ran in a container
on the CPU image on a 4-core machine without `libtpu`; the TPU quota's
`time_used` stayed at zero. kagglesdk `create_kernel_session` returned a
session id and no observable execution. A pinned `docker_image` overrides the TPU VM
(kaggle-api issue 1197), so `kaggle_run.py` pins none, but the unpinned
pushes ran on the CPU image as well. A TPU request counts against the
five-session CPU pool. The route-by-route record, the markers that decide
whether a session is a TPU VM, the root-cause analysis and the interactive editor
probe, which ran on a 4-core CPU as well, are in
[tpu-research.md](tpu-research.md). The kernel's
`tpu_probe.py` hardware block decides whether a session is a TPU VM;
`kaggle kernels pull -m` named the CPU image on every CPU session and is
unobserved on a TPU VM.

## Retained notebooks

The notebooks in `docs/evidence/ghost-frequency/`,
`docs/evidence/transpiler-audit/`, `docs/evidence/ccz-reduction/`,
`docs/evidence/cd_census/`, `docs/evidence/simulation/` and
`docs/evidence/falsification/` ran on Kaggle. Their kernel logs and the
reading of each verdict against its own output are in
`docs/evidence/simulation-notebook-audit/`.
