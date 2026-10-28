# Kaggle guides

Kaggle kernels run every simulation of 14 qubits or fewer (root AGENTS.md,
"QPU time and calibration"; the section below holds the machine, GPU and CI-replay rules). These guides play the role
`docs/notes/ibm_quantum/` plays for IBM hardware:

| Guide | Content |
| --- | --- |
| [workflow.md](workflow.md) | `scripts/kaggle_run.py` push, status and collect; authentication; how a result enters the research state |
| [substrates.md](substrates.md) | measured CPU, RAM, disk, GPU, TPU and qubit limits of each machine shape, and what runs on which substrate |
| [gpu-runbook.md](gpu-runbook.md) | how to run a GPU kernel without wasting quota: the procedure, the failures that shaped it, Aer and numpy practice, the quota ledger and the 15-qubit routing gate |
| [custatevec.md](custatevec.md) | the cuQuantum libraries the cu11 Aer wheel loads, their pins, the cuStateVec T4 check and how to read it |
| [hypercomplex-stack.md](hypercomplex-stack.md) | the eight hypercomplex packages built and proved identically on the host and in every kernel |
| [interfaces.md](interfaces.md) | every CLI command, kagglesdk method and MCP tool, mapped onto shared operations; which call addresses which kernel version, where a session id comes from, how a session is cancelled; accelerator fields, authentication and the host's MCP permission policy |
| [tpu-research.md](tpu-research.md) | every TPU request route measured on this account, the server record of each version, the markers that decide whether a session is a TPU VM, the root-cause analysis and its sources, and the push procedure |
| [libraries.md](libraries.md) | the Kaggle PyPI packages: kaggle, kagglesdk and kagglehub as installed Arch packages with their recipes and run examples, the packages left out and why, and what a kernel image carries |

## Captured Kaggle documentation

`scripts/capture_kaggle_docs.py` keeps Kaggle's own documentation here
byte for byte, with `MANIFEST.json` in each directory naming every file's
source URL and sha256 (gate `core-record-check-05` (`tests/test_cli_record_checks.py`) rechecks the bytes):

| Directory | Source | Content |
| --- | --- | --- |
| [site/](site/) | kaggle.com/docs, each page's Markdown source at `https://www.kaggle.com/docs/<page>.md`, for every page the docs navigation lists; root-relative links are relative to kaggle.com | [notebooks](site/notebooks.md) (session resources and limits), [efficient-gpu-usage](site/efficient-gpu-usage.md), [tpu](site/tpu.md), [api](site/api.md) (auth, OAuth scopes, rate limits), [mcp](site/mcp.md) (56 MCP tools with request and response), [models](site/models.md), [datasets](site/datasets.md), [packages](site/packages.md), [benchmarks](site/benchmarks.md), [competitions](site/competitions.md), [competitions-setup](site/competitions-setup.md), [organizations](site/organizations.md), [groups](site/groups.md) |
| [cli/](cli/) | github.com/Kaggle/kaggle-cli `docs/` at commit 931014d, verbatim | [kernels](cli/kernels.md) (push, `--accelerator`, the accelerator list), [kernels_metadata](cli/kernels_metadata.md), [configuration](cli/configuration.md), models, datasets, output format, search |

Facts the guides above rest on, with their source:

- Session resources: 12 h per CPU or GPU session and 9 h per TPU session;
  20 GB saved in `/kaggle/working` plus unsaved scratch; CPU sessions 4
  cores and 30 GB RAM; GPU sessions 4 cores and 29 GB RAM; the TPU VM 96
  cores and 330 GB RAM; interactive sessions end after 20 idle minutes
  ([site/notebooks.md](site/notebooks.md)).
- TPU use: up to 20 hours per week and 9 hours per session
  ([site/tpu.md](site/tpu.md)).
- Account quotas on the settings page, read 2026-10-28: private datasets and
  private models 214.75 GB each (330.47 MB of datasets used); GPU 30 h and TPU
  20 h a week; AI models 10 USD a day and 100 USD a month. The provider
  credits monitor reads the hours and the AI-model spend; no CLI or API call
  reports the storage quota ([provider-credits.md](../../runbooks/provider-credits.md)).
- Accelerator IDs as of September 2026: NvidiaTeslaT4 (2 x T4),
  NvidiaTeslaA100, NvidiaL4, NvidiaL4X1, NvidiaH100, NvidiaRtxPro6000,
  TpuV5E8, TpuV6E8, some restricted to competitions or admins; the push's
  `--accelerator` selects one ([cli/kernels.md](cli/kernels.md)), and
  `enable_gpu` and `enable_tpu` are deprecated in favor of `machine_shape`
  ([site/mcp.md](site/mcp.md)).

The pages lag the service, and the service decides. Where they disagree,
the guides follow what a kernel measured:

| Page statement | Service behavior | Authority |
| --- | --- | --- |
| The TPU is a TPU v3-8 with 8 cores and 128 GB of TPU memory ([site/tpu.md](site/tpu.md), [site/notebooks.md](site/notebooks.md)) | the accelerator list offers TpuV5E8 and TpuV6E8 only | [cli/kernels.md](cli/kernels.md), [tpu-research.md](tpu-research.md) |
| No page names an identity requirement for TPUs | the notebook editor's session panel reads "Some accelerators, such as TPUs, require identity verification"; every TPU request from an account without Persona verification ran on the 4-core CPU image | [tpu-research.md](tpu-research.md) |
| The free GPU is one Tesla P100 ([site/efficient-gpu-usage.md](site/efficient-gpu-usage.md), [site/notebooks.md](site/notebooks.md) "Using a GPU") | `NvidiaTeslaT4` gives 2 x T4; the same notebooks page also specifies the T4 x2 shape | [substrates.md](substrates.md) |
| Interactive sessions stay alive until a 60-minute idle timeout ([site/efficient-gpu-usage.md](site/efficient-gpu-usage.md)) | 20 idle minutes end an interactive session ([site/notebooks.md](site/notebooks.md) "Idle time") | the shorter limit binds a plan |
| A GPU session waits only when a queue forms (notebooks "Using a GPU") | a third concurrent GPU batch push is refused with "Maximum batch GPU session count of 2 reached", whatever weekly quota is left; quota and concurrency are separate limits | [workflow.md](workflow.md) |

`kaggle_kernel/AGENTS.md` is the instruction file that travels inside each
kernel, and `kaggle_kernel/kernel_main.py` is the program every kernel runs.

## Simulation on Kaggle: CPU, GPU and CI replay

`"$PYTHON" scripts/kaggle_run.py push ENTRY --slug SLUG -- ARGS` runs a
repository script on a private Kaggle kernel, and `status` and `collect`
retain its output under results/kaggle/. The kernel's own guide is
`kaggle_kernel/AGENTS.md`. The measurements behind the choices below are in
`docs/notes/kaggle/substrates.md`
(`results/kaggle/2026-10-16T204620Z-gororoba-aer-gpu-probe`).

- **Machine.**
  - CPU, the default: every noisy simulation whose widest density matrix
    stays below 11 qubits, and every small dynamic circuit.
  - GPU (`--machine NvidiaTeslaT4`, two T4s): density matrices of 11 to 14
    qubits and statevectors up to 29 qubits per T4.
  - Measured on the 7-qubit N=21 order-finding circuits: statevector
    trajectories took 2.8 and 36 ms per shot on the CPU against 21.7 and
    54.6 ms on a T4.
  - A dynamic circuit's density matrix evolves per shot, about 160 times
    slower than trajectories of the same channel.
- **A GPU push.** It carries `--timeout SECONDS` sized to the work, and
  kaggle_run.py refuses an accelerator push without one. Read `kaggle quota`
  before and after; the weekly 30 h resets at 00:00 UTC on Saturday. Two GPU
  sessions run at once, and a version is never repushed while it runs. For
  example:

  ```sh
  "$PYTHON" scripts/kaggle_run.py push --slug NAME --machine NvidiaTeslaT4 \
      --timeout 3600 --include SNAPSHOT.json scripts/ENTRY.py -- ARGS
  ```

- **Inside the entry.**
  1. The kernel installs qiskit-aer-gpu-cu11 0.17.2 and sets
     `GOROROBA_AER_DEVICE=GPU`, and `calibration_snapshot.aer_device()`
     reads it.
  2. `calibration_snapshot.noise_simulator(snapshot, device,
     method="density_matrix" | "statevector")` builds live_run's noise
     channels.
  3. `snapshot_laws.restrict_circuit(isa)` with `restrict(snapshot, qubits)`
     keeps the circuit and the noise model at the active width.
  4. `set_options(max_parallel_threads=parallel.workers())` uses every host
     CPU.
- **cuStateVec.** `noise_simulator(..., custatevec=True)` sets Aer's
  `cuStateVec_enable` on a GPU statevector or density-matrix run, and
  `GOROROBA_AER_CUSTATEVEC=1` sets it for every GPU call that leaves
  `custatevec` unset (`calibration_snapshot.aer_custatevec`). qiskit-aer-gpu-cu11 0.17.2
  links libcustatevec.so.1 and libcutensornet.so.2, which `cuquantum-cu11`
  24.8.0 and `cutensor-cu11` 2.2.0 (`KERNEL_PINS` entries) supply. Aer
  0.17.2 reports `cuStateVec_enable` False when `batched_shots_gpu` is also
  set.
  `scripts/aer_gpu_probe.py --workloads n21 --configurations
  cpu_statevector,gpu_statevector_unbatched,gpu_statevector_custatevec` records the three paths
  with Aer's reported `cuStateVec_enable`. On the T4 x2 (gate `core-record-check-04`)
  cuStateVec ran the dynamic density matrix 1.44 and 1.63 times faster than
  the plain GPU executor at 7 and 10 qubits and statevector trajectories
  1.19 to 1.29 times slower, and Aer spread per-shot and batched runs over both
  GPUs (`docs/evidence/aer_gpu_configuration/README.md`).
  `docs/notes/kaggle/custatevec.md` holds the kernel's library chain and
  the T4 check, and `docs/notes/build_host/custatevec.md` the host build.
- **Batched GPU shots.** On a GPU `noise_simulator` enables Aer's
  `batched_shots_gpu` by default for circuits of at most
  `BATCHED_SHOTS_MAX_QUBITS` (10) active qubits, and `batched_shots=False`
  opts out. `SnapshotSimulator.run` runs any circuit with control flow
  unbatched: the batched executor rejects `jump`, and with if_else lowered
  to bfunc-conditioned gates it evaluates the condition before the readout
  channel. Shot branching is never enabled, since Aer 0.17.2's shot
  branching drops a mid-circuit measurement's readout channel
  (`docs/evidence/aer_gpu_configuration/README.md`).
- **Cache blocking.** `SnapshotSimulator.run` blocks a GPU batch whose
  widest active state exceeds one GPU's memory, Aer's own trigger, with
  `calibration_snapshot.blocking_qubits_for`'s chunk (27 statevector, 13
  density-matrix qubits on a T4) and `max_parallel_shots=1`, so every run
  that fits one GPU keeps its executor and counts. On the T4 x2 a 15-qubit
  density matrix ran in 4.2 s and a 30-qubit statevector in 7.2 s across
  both GPUs, where Aer's automatic choice filled host memory until the OOM
  killer ended it. if_else aborts under blocking, so a blocked batch runs in
  `lower_conditionals` form and raises ValueError where none exists; Aer's
  CPU chunk executor misplaces conditions, so blocking stays on the GPU
  (gates core-451 and core-452, `docs/notes/kaggle/substrates.md`).
- **CI replay.**
  - Seeded GPU counts differ from CPU counts, so a gate re-derives a GPU
    record from its retained counts and never resamples on CI.
  - An entry whose output a CI gate recompiles is pushed with `--ci-env`,
    on a CPU or a GPU machine. The kernel then builds CI's Python 3.14.7
    with `ci/install_pins.sh` and runs the entry under CPU Aer, because the
    image's Python 3.13 and numpy 2.1.3 change compiled depths and
    durations.
  - Replays hold routed CZ, layout and classical stages exact, and depth
    and duration within a relative 0.002 across BLAS builds.
- **Pinned GPU environment.** `push --gpu-env` on `NvidiaTeslaT4` runs the
  entry in a venv on the image's Python 3.13, the newest Python the cu11
  wheel ships, holding requirements.txt and ci/requirements-ci.txt with
  `GPU_ENV_AER_PINS` in qiskit-aer's place (`ci/install_pins.sh` with
  `AER_PINS`).
  - Before the entry, `kernel_main.gpu_interpreter` requires every pin at its
    version, the selected GPU Aer distribution as the only owner of
    `qiskit_aer/__init__.py`, both T4s in nvidia-smi, and seeded Bell runs
    on the GPU that report device GPU, the cuStateVec one with
    `cuStateVec_enable` true.
  - A miss lists its reasons under `failures` in gpu_env.json, and the kernel
    exits 4 without running the entry.
  - `aer_gpu_probe.py --require-gpu` then stops at the first row that leaves
    the GPU.
  - `--gpu-env-with torch` adds `GPU_ENV_GROUPS["torch"]`, torch 2.14.1 at
    the host's version, to the same resolve and to the pins the preflight
    requires; `ghost_branching_benchmark.py --require-gpu NAME --gpus N`
    then exits 3 unless torch lists both T4s and a complex128 matmul on
    each matches numpy.
  - `--gpu-aer cu13` replaces the cu11 wheels with `GPU_AER_PINS["cu13"]`:
    the CUDA 13 wheel `docs/notes/kaggle/recipes/build_aer_gpu_cu13_wheel.sh`
    builds, which the push attaches from its `kaggle_run.py artifact`
    dataset (`AER_GPU_WHEELS`) and the kernel installs only when its sha256
    matches (`docs/notes/kaggle/custatevec.md`, "CUDA 13 build"). On the
    T4 x2 it ran every probe row with cuStateVec on; its GPU density-matrix
    rows draw the cu11 wheel's seeded counts, while seeded statevector
    trajectories differ by build (gate `core-record-check-04`).
  - Only Python itself differs from CI's 3.14.7.
  - On a CPU machine the same push stops at the preflight, which proves the
    error path at no GPU cost.
- **Sessions.** Five CPU and two GPU batch sessions run per account. A GPU
  machine's four host CPUs run CPU work, `--ci-env` included, when the CPU
  pool is full, at the price of GPU quota.
