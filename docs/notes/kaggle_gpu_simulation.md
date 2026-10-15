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
- **Aer on GPU.** `qiskit-aer-gpu` targets CUDA 12 and replaces the CPU
  `qiskit-aer`. It runs statevector, density-matrix and unitary methods with
  `AerSimulator(device="GPU")`, on x86_64 Linux only.
  `AerSimulator().available_devices()` confirms the device in the notebook
  before any run. The repository pins `qiskit-aer==0.17.2`; a Kaggle run
  installs the matching GPU wheel and records its version.
- **TPU.** Aer has no TPU backend. TPU hours help only simulators written in
  JAX, for example batched density-matrix contractions. None exists in the
  repository, so the TPU stays unused until a design needs one.

## Which designs need it

On the build host, density-matrix noise simulation on the CPU is
comfortable up to about 12 to 14 qubits. GPU memory extends that to about
16 (16 GB holds a 15-qubit complex128 density matrix). Candidates:

| Design | Qubits | Why a GPU helps |
| --- | --- | --- |
| Census-frequency witness over sampled sedenion triples | 4 data + control, many circuits | thousands of per-triple noisy runs |
| Signed kernel probe at hardware noise | 7 | sweeps over t and noise scale |
| Walk scaffold under coherent over-rotation and leakage models | 4 | separates hypothesis 3's candidates against the retained floors |
| Detuning map designs (checkerboard Ramsey) | a patch, not the chip | power and winding analysis at realistic visibility |

The four-qubit and two-qubit designs run on the CPU here in seconds, so the
GPU matters for sweeps and batched trials, not for single circuits.

## Workflow

The Kaggle CLI drives notebooks with three commands:

- `kaggle kernels push -p DIR` uploads a notebook whose
  `kernel-metadata.json` sets `enable_gpu` (or `enable_tpu`) and
  `enable_internet` for the pip install.
- `kaggle kernels status USER/SLUG` polls the run.
- `kaggle kernels output USER/SLUG -p OUT` retrieves the results.

The credential lives in the Kaggle account store or in the environment,
never in the repository. A retained Kaggle result is listed with:

- the notebook, its output, the package versions (`qiskit`, `qiskit-aer-gpu`,
  CUDA) and the accelerator type;
- every seed;
- the evidence class `numerical or stochastic simulation`.

CI cannot rerun it, so it enters the research state with byte checks only
until a CPU replay of a reduced case exists.

## Retained notebooks

The notebooks in `docs/evidence/ghost-frequency/` and
`docs/evidence/transpiler-audit/` ran on Kaggle. Their corrected readings
are in those directories' READMEs.
