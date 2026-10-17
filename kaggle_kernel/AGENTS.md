# Kaggle kernel agent guide

This file travels inside every kernel that `scripts/kaggle_run.py` pushes
and is printed at the top of its log. The repository's root AGENTS.md owns
every rule; this guide states what a Kaggle kernel is for, what it runs on,
and what it must prove before its output counts.

## What runs where

| Substrate | Runs | Never runs |
| --- | --- | --- |
| Kaggle CPU kernel (the default) | every simulation of 14 qubits or fewer whose widest density matrix stays below 12 qubits (8 with mid-circuit measurement), and the CI gate shards (`kaggle_run.py shards`) | IBM jobs; anything needing an IBM credential |
| Kaggle GPU kernel (Aer on GPU, `--machine NvidiaTeslaT4`) | simulations whose widest density matrix reaches 12 qubits, or 8 with mid-circuit measurement (docs/notes/kaggle/substrates.md, "CPU against T4") | IBM jobs; narrow replays, which the T4 speeds up by at most 3 times |
| Kaggle CPU in the same kernel | transpilation, package builds, the hypercomplex table extraction | |
| Kaggle TPU (`TpuV5E8`, `TpuV6E8`) | JAX code only; Aer has no TPU backend. An account without Persona identity verification gets a 4-core CPU machine for every TPU request; a verified account's request queues for a TPU, one batch session at a time (docs/notes/kaggle/tpu-research.md) | Qiskit or Aer |
| Kaggle Gemma models (attached through `model_sources`) | text tasks on request | evidence: a language-model answer supports no physical or mathematical claim |
| IBM Heron (ibm_fez, ibm_kingston, ibm_marrakesh) | 15 or more qubits, or a question about a named device qubit, only after the owner approves a written case | simulations |
| GitHub Actions CPU | the CPU replay gate that re-derives a reduced case of each Kaggle result | GPU work |
| Build host (Arch, RTX 4070 Ti 12 GB; guide in the untracked `docs/local/`) | development, dry runs, calibration exports, CPU replays, the Arch-packaged hypercomplex stack and SageMath | runs the routing rule sends to Kaggle |

## Every kernel's phases

`kaggle_kernel/kernel_main.py` writes one JSON file per phase into
`/kaggle/working/output`:

1. `environment.json`: Python and package versions, CPU model and cores,
   RAM, working disk, every GPU (name, memory, driver, compute capability),
   CUDA driver version, TPU devices, Aer devices and attached models.
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
4. The entry's stdout, stderr, exit code and changed files.

## Package stack

| Package | Pin | Kernel source |
| --- | --- | --- |
| qiskit | 2.5.2 | PyPI |
| qiskit-aer-gpu-cu11 | 0.17.2 (the CUDA 12 `qiskit-aer-gpu` stops at 0.15.1 and has no Python 3.13 wheel) | PyPI |
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
