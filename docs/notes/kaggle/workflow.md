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
  its repository imports and named data files, writes a private GPU kernel
  (machine shape `NvidiaTeslaT4` by default) and pushes it. The kernel
  records its environment, runs ENTRY with `GOROROBA_AER_DEVICE=GPU`, and
  returns every file the run created under the repository root.
- `status RUN_DIR` and `collect RUN_DIR` poll the kernel and download the
  run's own version with a sha256 manifest. `kernels status` reports the
  slug's latest version whatever version it names, so `collect` decides
  completion from the `exit.json` the kernel writes on every exit path.
- `verify` checks every retained collect.json against its output files
  offline (gate core-290).
- `push --smoke` probes the environment and measures the widest
  density-matrix and statevector circuits the GPU runs.
- `--machine` names the accelerator, passed to the push as
  `--accelerator`: `NvidiaTeslaT4` (the default, two T4s), another ID from
  [cli/kernels.md](cli/kernels.md), or `cpu` for none. `machine_shape` in
  kernel-metadata.json alone does not select hardware: probes that set only
  it for `NvidiaL4` and `TpuV5E8` ran on 4-core CPU machines, and
  `NvidiaTeslaP100`, absent from the current list, returned two T4s. A
  kernel's `environment.json`, not the request, records what ran.
- The account runs at most two GPU batch sessions at once; a third push
  fails with "Maximum batch GPU session count of 2 reached", and `push`
  exits with that message and removes the unsent run directory, as it does
  for any failed push. The limit
  was reached once with a single kernel listed as running, after a second
  version of it had been pushed, so a superseded version appears to keep
  its session until it ends.

A kernel holds no IBM credential, so its noise model comes from a retained
calibration export (`gororoba_quantum/calibration_snapshot.py --export
BACKEND --out FILE`), which refuses to write unless every gate and readout
channel it rebuilds equals live_run's noise model for the same fetch.

Kaggle authenticates through `kaggle auth login`, a browser OAuth flow
whose token stays in the CLI's own store, never in the repository. Kaggle
also serves an OAuth MCP endpoint at `https://www.kaggle.com/mcp`.

Each run directory under results/kaggle/ keeps submission.json (entry,
arguments, git commit, bundle digests, pins), the generated kernel, and
after collection the output with collect.json. Retaining it registers no
claim. A `numerical or stochastic simulation` claim in the research state
needs a replay gate that re-derives it in CI, so a Kaggle result becomes a
claim only once a reduced case reproduces it on the CPU under a gate. Until
then it informs a design as a retained artifact.

## Retained notebooks

The notebooks in `docs/evidence/ghost-frequency/`,
`docs/evidence/transpiler-audit/`, `docs/evidence/ccz-reduction/`,
`docs/evidence/cd_census/`, `docs/evidence/simulation/` and
`docs/evidence/falsification/` ran on Kaggle. Their kernel logs and the
reading of each verdict against its own output are in
`docs/evidence/simulation-notebook-audit/`.
