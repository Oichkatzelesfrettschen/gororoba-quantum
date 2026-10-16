# Kaggle kernel agent guide

This file travels inside every kernel that `scripts/kaggle_run.py` pushes
and is printed at the top of its log. The repository's root AGENTS.md owns
every rule; this guide states what a Kaggle kernel is for, what it runs on,
and what it must prove before its output counts.

## What runs where

| Substrate | Runs | Never runs |
| --- | --- | --- |
| Kaggle CPU kernel (the default) | every simulation of 14 qubits or fewer whose widest density matrix stays below `local_compute.GPU_MIN_ACTIVE_QUBITS`, and the CI gate shards (`kaggle_run.py shards`) | IBM jobs; anything needing an IBM credential |
| Kaggle GPU kernel (Aer on GPU, `--machine NvidiaTeslaT4`) | simulations whose widest density matrix reaches `local_compute.GPU_MIN_ACTIVE_QUBITS` | IBM jobs; narrow replays the CPU runs faster |
| Kaggle CPU in the same kernel | transpilation, package builds, the hypercomplex table extraction | |
| Kaggle TPU (`TpuV5E8`, `TpuV6E8`) | JAX code only; Aer has no TPU backend. Every batch request for either ID, through any interface, ran on a 4-core CPU machine without libtpu (docs/notes/kaggle/tpu-research.md) | Qiskit or Aer |
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
2. `hypercomplex.json`: the hypercomplex stack. The kernel fetches the eight
   pinned archives (sha256-checked), installs them through the PKGBUILD
   recipes in `scripts/algebra_package_tables.py`, runs `--extract`, and
   stops with exit code 3 unless the regenerated
   `docs/evidence/algebra_packages/tables.json` equals the retained bytes.
   The build host passes the same test against its Arch packages, so a run
   that reaches its entry used the same algebra code as the host.
3. `capacity.json` (smoke kernels): the widest GHZ circuit each Aer method
   runs on the GPU.
4. The entry's stdout, stderr, exit code and changed files.

## Package stack

| Package | Pin | Kernel source |
| --- | --- | --- |
| qiskit | 2.5.2 | PyPI |
| qiskit-aer-gpu-cu11 | 0.17.2 (the CUDA 12 `qiskit-aer-gpu` stops at 0.15.1 and has no Python 3.13 wheel) | PyPI |
| hypercomplex, hypercomplex-engine, hypercomplex-algebra, Cayley-Calculator, octonion, mathdunders | 0.3.4, 0.5.0, 0.2.0.2, 1.3.1, 0.1.0, 0.4.2 | PyPI sdist, sha256-pinned |
| cayley-dickson, SplitOct | commits abf96e7, e29e72f | GitHub archive, sha256-pinned, PKGBUILD recipe |
| numpy-quaternion | 2024.0.13 | PyPI (Cayley-Calculator runtime) |
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
