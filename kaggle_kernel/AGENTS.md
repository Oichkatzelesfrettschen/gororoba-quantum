# Kaggle kernel agent guide

This file travels inside every kernel that `scripts/kaggle_run.py` pushes
and is printed at the top of its log. The repository's root AGENTS.md owns
every rule; this guide states what a Kaggle kernel is for, what it runs on,
and what it must prove before its output counts.

## What runs where

| Substrate | Runs | Never runs |
| --- | --- | --- |
| Kaggle CPU kernel (the default) | every simulation of 14 qubits or fewer whose widest density matrix stays below 12 qubits (8 with mid-circuit measurement) | IBM jobs; anything needing an IBM credential |
| Kaggle GPU kernel (Aer on GPU, `--machine NvidiaTeslaT4`) | simulations whose widest density matrix reaches 12 qubits, or 8 with mid-circuit measurement (docs/notes/kaggle/substrates.md, "CPU against T4") | IBM jobs; narrow replays, which the T4 speeds up by at most 3 times |
| Kaggle CPU in the same kernel | transpilation, package builds, the hypercomplex table extraction | |
| Kaggle TPU (`TpuV5E8`, `TpuV6E8`) | JAX code only; Aer has no TPU backend. An account without Persona identity verification gets a 4-core CPU machine for every TPU request; a verified account's request queues for a TPU, one batch session at a time (docs/notes/kaggle/tpu-research.md) | Qiskit or Aer |
| Kaggle Gemma models (attached through `model_sources`) | text tasks on request | evidence: a language-model answer supports no physical or mathematical claim |
| A 15-qubit run (decision-gated) | the substrate an approved written case names: Kaggle T4 x2 or build host Aer, a GPU state wider than one T4 cache-blocked across both (`calibration_snapshot.blocking_options`; docs/notes/kaggle/gpu-runbook.md), or Tuna-17 through Quantum Inspire, whose `submit` refuses while another session's hardware job is live | any substrate the case does not name |
| IBM Heron (ibm_fez, ibm_kingston, ibm_marrakesh) | 16 or more qubits, or a question about a named device qubit, only after the owner approves a written case | simulations |
| GitHub Actions CPU | the CPU replay gate that re-derives a reduced case of each Kaggle result | GPU work |
| Build host (Arch, RTX 4070 Ti 12 GB; guide in the untracked `docs/local/`) | development, dry runs, calibration exports, CPU replays, the Arch-packaged hypercomplex stack and SageMath | runs the routing rule sends to Kaggle |

## Every kernel's phases

`kaggle_kernel/kernel_main.py` writes one JSON file per phase into
`/kaggle/working/output`:

1. `environment.json`: Python and package versions, CPU model and cores,
   RAM, working disk, every GPU (name, memory, driver, compute capability),
   CUDA driver version, TPU devices, Aer devices, the Aer device the entry
   runs on (`entry_aer_device`) and attached models.
2. `hypercomplex.json`: the hypercomplex stack, built and proved by
   `scripts/algebra_package_tables.py`. `--fetch` downloads the seventeen
   archives `RELEASES` pins and keeps each only if its sha256 matches.
   `--install` installs sixteen of them with `pip install --no-deps`,
   applying `BUILD_RECIPES` (the cayley-dickson, SplitOct and pyquaternion
   PKGBUILD `prepare()` steps) and taking the Octonion-Sedenion wheel as
   published, then installs `RUNTIME_PINS`: numpy-quaternion, the
   seventeenth, as its pinned compiled wheel, and numba, sparse and
   anywidget. `--extract` binds all seventeen
   installed distributions to their archives and regenerates
   `docs/evidence/algebra_packages/tables.json`; the kernel stops with exit
   code 3 unless those bytes equal the retained ones. The build host passes
   the same test against its Arch packages, so a run that reaches its entry
   used the same algebra code as the host. The file's `packages` field
   records the versions `kernel_main.REPORTED_PACKAGES` names, nine of the
   seventeen algebra distributions; the byte comparison binds the rest.
3. `capacity.json` (smoke kernels): the widest GHZ circuit each Aer method
   runs on the GPU.
4. The entry's stdout and stderr, written to `stdout.txt` and `stderr.txt`
   as the entry prints (`kernel_main.start_entry` sets
   `PYTHONUNBUFFERED=1`), then its exit code and the repository files it
   changed, which the kernel copies under `repo/` after the entry exits.
   A session Kaggle ends at `--timeout` still returns
   `/kaggle/working/output` but never reaches that copy, so an entry that
   may outlive its timeout writes its record to an absolute path under
   `/kaggle/working/output` and rewrites it after every finished unit of
   work, as `scripts/aer_gpu_probe.py` does per row.

## Package stack

| Package | Pin | Kernel source |
| --- | --- | --- |
| qiskit | 2.6.0 | PyPI |
| qiskit-aer-gpu-cu11 | 0.17.2 (the CUDA 12 `qiskit-aer-gpu` stops at 0.15.1 and has no Python 3.13 wheel) | PyPI |
| cuquantum-cu11 | 24.8.0 (brings custatevec-cu11 1.6.0.post1 and cutensornet-cu11 2.5.0; the libraries the cu11 Aer wheel links) | PyPI |
| cutensor-cu11 | 2.2.0 (the newest release inside cutensornet-cu11 2.5.0's `>=2.0.1,<3`) | PyPI |
| qiskit-ibm-runtime | 0.50.0 (fake backends such as FakeFez; no account or credential) | PyPI |
| hypercomplex, hypercomplex-engine, hypercomplex-algebra, Cayley-Calculator, octonion, mathdunders | 0.3.4, 0.5.0, 0.2.0.2, 1.3.1, 0.1.0, 0.4.2 | PyPI sdist, sha256-pinned |
| quaternionic, clifford, kingdon, galgebra, pyoctonion | 1.0.18, 1.5.1, 3.0.0, 0.6.0, 3.12 | PyPI sdist, sha256-pinned |
| pyquaternion | 0.9.9 | PyPI sdist, sha256-pinned, PKGBUILD recipe (writes the VERSION.txt the sdist omits) |
| cayley-dickson, SplitOct | commits abf96e7, e29e72f | GitHub archive, sha256-pinned, PKGBUILD recipe |
| hyprat | 0.2.0 | GitHub tag archive, sha256-pinned |
| Octonion-Sedenion | 1.0.0 | PyPI wheel (its only release form), sha256-pinned |
| numpy-quaternion | 2024.0.13 | PyPI compiled wheel at the pin; `--extract` binds its Python files to the sha256-pinned sdist (Octonion-Sedenion builds on it) |
| numba, sparse, anywidget | 0.68.0, 0.17.0, 0.11.0 | PyPI (`RUNTIME_PINS`; runtime dependencies of quaternionic, clifford and kingdon) |
| numpy, scipy, sympy, pandas, torch | Kaggle image versions, recorded per run | Kaggle image |
| SageMath | 10.10 | build host only; a computation that needs Sage stays there |

## Rules

- A kernel is private, has internet enabled (and a GPU when one is
  requested), and holds no IBM credential. Noise comes from a retained
  `gororoba_quantum/calibration_snapshot.py` export.
- The entry reads `GOROROBA_AER_DEVICE`, which the kernel sets to its
  machine's device.
- An output is a numerical simulation. It enters
  `docs/state/research_state.json` only after a CPU replay gate re-derives
  a reduced case.
- The push selects hardware with `--accelerator`; `environment.json`
  records what actually ran.
- Measured limits of each machine shape, the qubit size guide and the
  captured Kaggle documentation are in `docs/notes/kaggle/`.
- An entry whose output a CI gate recompiles runs with `push --ci-env` on a
  CPU or GPU machine, using CPU Aer either way. The kernel then builds CI's Python 3.14.7 with CI's pins
  through `ci/install_pins.sh` and runs the entry under it, because the
  image's Python 3.13 and numpy 2.1.3 change compiled depths and durations.

## Aer on the GPU

- **Requesting a GPU.** Push with `--machine NvidiaTeslaT4` and a `--timeout`
  sized to the work; kaggle_run.py refuses an accelerator push without one.
  The kernel installs qiskit-aer-gpu-cu11 0.17.2, cuquantum-cu11 24.8.0 and
  cutensor-cu11 2.2.0 and sets `GOROROBA_AER_DEVICE=GPU`.
- **cuStateVec.** `noise_simulator(..., custatevec=True)`, or
  `GOROROBA_AER_CUSTATEVEC=1` in the entry's environment, sets
  `cuStateVec_enable` on a GPU statevector or density-matrix run; `scripts/aer_gpu_probe.py
  --workloads n21 --configurations
  cpu_statevector,gpu_statevector_unbatched,gpu_statevector_custatevec` records
  the three paths with Aer's reported `cuStateVec_enable`. The option excludes
  `batched_shots_gpu`. `docs/notes/kaggle/custatevec.md` holds the library
  chain, the T4 push command and how to read its result.
- **Pinned GPU environment.** A push with `--gpu-env` runs the entry in
  /tmp/gororoba/gpu-venv:
  - The venv runs the image's Python with the repository's pins and the GPU
    Aer wheels in qiskit-aer's place.
  - Before the entry, gpu_env.json records each pin's installed version, the
    owners of `qiskit_aer/__init__.py`, Aer's devices, and two seeded Bell
    runs on the GPU.
  - A nonempty `failures` list stops the kernel with exit 4, before the
    entry starts. Each failure names what to fix:
    - a pin that resolved to another version;
    - a CPU qiskit-aer that shares the qiskit_aer/ files;
    - a GPU that nvidia-smi does not list;
    - a Bell run that raised, ran on another device, or left cuStateVec off.
  - `push --gpu-env-with torch` adds torch 2.14.1, the build host's version,
    to the venv's pins, so a torch entry runs over the repository's numpy
    and qiskit instead of the image's; the preflight requires it at that
    version like every other pin.
  - Under `--gpu-aer cu13` the Aer wheel comes from an attached dataset:
    gpu_env.json's `wheel` names the file found under /kaggle/input and its
    sha256, and a missing or different file is a failure before any install.
    The report's `controller_wrappers` and `cuda_libraries` show where each
    CUDA library resolved.
  - Read gpu-env-report.txt and install-pins.txt in the output for the
    commands' own output.
  - "Keeping the run on the GPU" in `docs/notes/kaggle/custatevec.md` maps
    each route to the CPU to the check that closes it.
- **Using it in an entry.** The entry passes
  `calibration_snapshot.aer_device()` to `noise_simulator(snapshot, device,
  method=...)`. On a GPU the simulator batches shots of circuits of at most
  10 active qubits without control flow and runs feed-forward circuits shot
  by shot (`calibration_snapshot.SnapshotSimulator`).
- **Noise model width.** Restricting the snapshot and the circuit to the
  active qubits (`snapshot_laws.restrict` and `restrict_circuit`) keeps
  Aer's noise model at the circuit's width on either device.
- **What the GPU is for.** It pays for density matrices at
  `local_compute.GPU_MIN_ACTIVE_QUBITS` (11) qubits or more and for wide
  statevectors. Small dynamic circuits sample faster on the host CPUs. On
  the 7-qubit N=21 order-finding circuits, statevector trajectories took 2.8
  and 36 ms per shot on the CPU, against 21.7 and 54.6 ms on one T4.
- **Batched shots.** `noise_simulator(..., batched_shots=True)` enables Aer's
  `batched_shots_gpu`, which aborts on any circuit with control flow
  (`if_else` lowers to `jump`), so only static circuits may batch. Batched
  static runs are unmeasured here.
- **Replay.** A GPU's seeded counts differ from the CPU's. Its records are
  replayed from their retained counts, never by resampling on CI.

The measurements are in `docs/notes/kaggle/substrates.md`, from
`results/kaggle/2026-10-16T204620Z-gororoba-aer-gpu-probe`.
