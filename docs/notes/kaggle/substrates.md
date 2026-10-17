# Substrates: measured capacity and what runs where

Every number below was measured by a kernel's `environment.json` and
`capacity.json` (`kaggle_kernel/kernel_main.py`) or read from the Kaggle
API; the run directory under results/kaggle/ that measured it is named in
each table. A Kaggle image changes without notice, so every run records its
own environment and these tables describe the probes, not a guarantee.

## Routing

| Work | Substrate | Reason |
| --- | --- | --- |
| Noise simulation, power analysis, parameter sweeps of 14 qubits or fewer | Kaggle CPU kernel; a GPU kernel when the widest density matrix reaches `local_compute.GPU_MIN_ACTIVE_QUBITS` (11) | routing rule (root AGENTS.md); small dynamic circuits sample faster on the CPU (below) |
| Statevector simulation beyond the density-matrix limit | Kaggle GPU kernel, `method="statevector"` | ideal semantics only; a noisy question needs the density matrix or trajectories |
| Hypercomplex package builds and table extraction | every kernel's CPU, then the host | `docs/notes/kaggle/hypercomplex-stack.md` |
| Transpilation against a calibration export | kernel CPU | about 0.06 s per Design C pair (three 5-qubit circuits) on the build host; the pair's three 20,000-shot density-matrix simulations take about 4 s on the build host CPU and about 8 s on a Kaggle T4, so a 5-qubit noise run is simulation-bound and the GPU does not speed it up |
| JAX code | Kaggle TPU v5e-8 | Aer and Qiskit have no TPU backend |
| Gemma inference | Kaggle GPU or TPU with the model attached | text tasks; never evidence |
| IBM jobs (15 or more qubits, or a named device qubit) | IBM Heron, after an approved case | the device is the question |
| CPU replay of a reduced case of every Kaggle result | GitHub Actions | the gate that admits a Kaggle result |
| Dry runs, calibration exports, SageMath, Arch-packaged stack | build host | IBM credential and Sage live there |

## Substrate permutations

A Kaggle session has one accelerator or none, and always a CPU host beside
it. Combinations beyond one session come from running sessions in
parallel (at most two GPU batch sessions per account) or from pairing a
Kaggle session with the build host.

| Permutation | Where it exists | What it runs here |
| --- | --- | --- |
| CPU only | Kaggle CPU session (4 cores, 30 GB); build host (Ryzen 5 5600X3D, 12 threads, 62 GiB) | transpilation, package builds, Aer CPU methods (stabilizer, matrix product state, extended stabilizer are CPU-only in Aer), the CPU replay of a reduced case |
| GPU (with its host CPU) | Kaggle GPU sessions (4 cores, 29 GB RAM); build host RTX 4070 Ti | Aer `device="GPU"` statevector, density matrix, unitary, superop and tensor network; the host CPU transpiles meanwhile |
| Two GPUs in one session | Kaggle `NvidiaTeslaT4` (2 x T4) | either independent experiments on separate GPUs (one process per GPU through `CUDA_VISIBLE_DEVICES`), or one state split across both with Aer chunking (`blocking_enable`, `blocking_qubits`), which moves the double-precision density matrix from 14 to 15 qubits and the statevector from 29 to 30 (estimate, not measured) |
| TPU (with its host CPU) | Kaggle `TpuV5E8`, `TpuV6E8` | JAX only; Aer has no TPU backend, so a TPU session would serve the repository as a large CPU host (96 cores and 330 GB RAM on the documented v3-8 VM). Every batch request with either ID (CLI, MCP, the editor's commit) ran on a 4-core Xeon CPU machine on the CPU image without libtpu, with the TPU accelerator recorded server-side and TPU quota unused, with Persona identity verification, which the editor names as a TPU requirement, absent on the account; [tpu-research.md](tpu-research.md) holds the routes and the root-cause analysis |
| CPU + GPU + TPU at once | not inside one Kaggle session | across sessions: Kaggle GPU kernels for Aer, a Kaggle TPU session for CPU-heavy Aer or JAX, the build host for dry runs, calibration exports and replay gates |
| Any of the above + IBM | only after an approved case | IBM answers device questions; every substrate above feeds its design, never its result |

## Qubit size guide

Exact state memory is 16 x 2^n bytes for a double-precision statevector,
8 x 2^n in single precision (`precision="single"`), 16 x 4^n for a
double-precision density matrix and 8 x 4^n in single. The estimates below
allow 90 percent of the device or host memory for the state and ignore
Aer's workspace; the measured columns come from `capacity.json` (a GHZ
circuit at 256 shots, each width tried once in its own process).

| Substrate | Memory | Statevector, double / single (estimate) | Density matrix, double / single (estimate) | Measured |
| --- | --- | --- | --- | --- |
| Kaggle T4 (one GPU) | 15 GiB | 29 / 30 | 14 / 15 | density matrix 14 (1.0 s), 15 killed; statevector 29 (4.4 s), 30 killed, 31 refused by Aer (target maximum 30) |
| Kaggle CPU or GPU-session host RAM | 29 to 30 GB | 30 / 31 | 15 / 15 | not measured |
| Kaggle TPU VM host RAM | 330 GB (documented, v3-8) | 34 / 35 | 17 / 17 | not reachable: TPU pushes ran on 4-core CPU machines |
| Build host RTX 4070 Ti | 12 GiB | 29 / 30 | 14 / 15 | density matrix 14, statevector 29; one wider fails with `std::bad_alloc` (detail in the untracked `docs/local/`) |
| Build host RAM | 62 GiB | 31 / 32 | 15 / 16 | density matrix 15 (17 s), statevector 31 (74 s); wider widths need 64 GiB and are not tried |

Rows list only substrates whose memory was measured or is documented
(`site/notebooks.md`); Kaggle publishes no memory for the L4, A100, H100 or
RTX Pro 6000 IDs, none of which this account reached, so this guide states
no width for them. Single precision and two-GPU chunking are not configured
in `calibration_snapshot.noise_simulator` and are not measured here.

What goes where by width, under the routing rule (root AGENTS.md: 14 qubits
or fewer on Kaggle, 15 or more on IBM):

| Width | Noisy simulation | Ideal simulation | Hardware |
| --- | --- | --- | --- |
| 1 to 10 qubits | Kaggle CPU: statevector trajectories, or the density matrix of a static circuit | Kaggle CPU statevector | IBM only for a named-device question with an approved case |
| 11 to 14 qubits | Kaggle GPU, double-precision density matrix (measured on one T4 to 14); a dynamic circuit stays on the CPU's trajectories unless a probe at its width shows the GPU faster | Kaggle GPU statevector | IBM only for a named-device question with an approved case |
| 15 qubits or more | none on Kaggle: the 15-qubit density matrix was killed on a T4, and no measured mode extends it | Kaggle GPU statevector up to the measured 29 qubits, as design support for an IBM case | IBM after an approved case |

## CPU against T4

`scripts/substrate_crossover.py` times Aer density-matrix runs of one
workload by active width on each device of a kernel: ISA circuits on a
connected chain of physical qubits, 8 layers of rz and sx on every qubit
and CZ on alternating pairs, under the noise rebuilt from the retained
`ibm_kingston` snapshot; a batch of 8 circuits at 2048 shots, the best of
2 repeats, and no wider width once one exceeds 180 s. The dynamic variant
adds one mid-circuit measurement with a conditioned X, which makes Aer
simulate shot by shot.
Runs `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu`
(Intel Xeon 2.20 GHz, 4 CPUs) and
`results/kaggle/2026-10-16T212614Z-gororoba-substrate-crossover-t4-gpu`
(2 x Tesla T4; Intel Xeon 2.00 GHz, 4 CPUs), both qiskit 2.5.2 with the
`qiskit-aer-gpu-cu11==0.17.2` build (each run's `submission.json` pins and
`environment.json`; the CPU run predates `CPU_KERNEL_PINS`, so its CPU
timings come from the cu11 build's CPU path):

| Active qubits | Static, CPU | Static, T4 | Dynamic, CPU | Dynamic, T4 |
| --- | --- | --- | --- | --- |
| 2 | 2.9 s | 2.4 s | 4.3 s | 6.1 s |
| 4 | 3.0 s | 2.5 s | 7.3 s | 9.2 s |
| 6 | 3.1 s | 2.6 s | 69.6 s | 24.3 s |
| 8 | 3.4 s | 2.6 s | 548.3 s | 19.4 s |
| 10 | 8.5 s | 3.0 s | not run | 309.3 s |
| 12 | 105.4 s | 8.3 s | not run | not run |
| 14 | 1955.2 s | 110.8 s | not run | not run |

Static circuits through 8 qubits cost the per-call overhead on both
devices; the T4 is 2.8 times faster at 10 qubits, 12.8 at 12 and 17.7 at
14. With mid-circuit measurement the CPU leads through 4 qubits and the T4
is 2.9 times faster at 6 and 28 at 8. The routing rule takes the widths
where the gain passes 10: 12 static qubits and 8 dynamic ones. The dynamic
threshold rests on one best-of-2 point that is not monotone in width: the
T4 ran 8 dynamic qubits in 19.4 s and 6 in 24.3 s. Each device ran once on
one machine draw, and the CPU machine (Intel Xeon 2.20 GHz) differs from
the CPU probe's (AMD EPYC 7B12), so Kaggle's CPU pool is heterogeneous and
a repeat can move both thresholds. The build
host's crossover is a different measurement on different hardware and
sets `local_compute.GPU_MIN_ACTIVE_QUBITS` for local runs only
(`gororoba_quantum/LOCAL_COMPUTE.md`).

## T4 x2 GPU kernel

`results/kaggle/2026-10-16T025758Z-gororoba-substrate-probe-t4`

| Quantity | Measured |
| --- | --- |
| CPU | Intel Xeon @ 2.00 GHz, 4 logical CPUs |
| RAM | 31.35 GiB total |
| GPUs | 2 x Tesla T4, 15,360 MiB each, compute capability 7.5, driver 580.178.04, CUDA 13.0 |
| Working disk | 19.52 GiB |
| Image packages | numpy 2.1.3, scipy 1.16.3, torch 2.11.0+cu128 |
| Hypercomplex stack | built and proved byte-identical |
| Density matrix (one GPU, double) | 12 to 14 qubits in under 1 s; 15 killed (signal 9) |
| Statevector (one GPU, double) | 26 to 29 qubits in under 5 s; 30 killed (signal 9); 31 refused by Aer, whose GPU target reports 30 qubits at most |

Each width ran in its own process, so the killed trials ended only
themselves. Both failures sit where the state first exceeds one T4's 15 GiB
(16 GiB at density matrix 15 and statevector 30), which places the single-GPU
limits exactly at the memory estimate.

## Small dynamic circuits: CPU against GPU

`results/kaggle/2026-10-16T204620Z-gororoba-aer-gpu-probe`
(`scripts/aer_gpu_probe.py`).

The probe ran on a T4 x2 host with 4 CPUs, using the ibm_fez calibration
of 2026-10-16T12:12:52-07:00, restricted to each circuit's 7 active qubits.
It compares five samplers on two circuits, both in the coset-281 encoding
(columns 1, 2, 5, 13, 25, the surrogate optimum; 3,978 routed CZ for ten
rounds):
- the two-round N=21 n21-feedback diagnostic (one mid-circuit measurement
  and if_else);
- the ten-round circuit (nine of each).

Each configuration ran in its own process. A configuration whose full shot
count would exceed 120 s ran fewer shots, and the table gives the count it
ran.

| Sampler | Two-round, per shot | Ten-round, per shot | Agreement with CPU trajectories (two-round) |
| --- | --- | --- | --- |
| CPU statevector trajectories | 2.8 ms (32,768 shots) | 36 ms (3,227) | reference |
| CPU density matrix | 445 ms (266) | 2.19 s (54) | total variation 0.052 against a sampling scale of 0.062 |
| GPU statevector, unbatched | 21.7 ms (5,276) | 54.6 ms (2,051) | total variation 0.0045 against 0.015 |
| GPU statevector, `batched_shots_gpu` | aborted (signal 6) | aborted | none |
| GPU density matrix, `batched_shots_gpu` | aborted | Aer error: invalid instruction `jump` | none |

- **Speed.** CPU trajectories are the fastest sampler for these circuits,
  1.5 to 8 times faster than the unbatched GPU.
- **Density matrix.** A dynamic circuit's density matrix evolves per shot,
  which makes it about 160 times slower than trajectories of the same
  channel.
- **Batched shots.** Aer 0.17.2's batched GPU sampler does not run control
  flow.
- **Agreement.** Every sampler that completed agrees with the CPU
  trajectories within its sampling scale.

## cuStateVec on the GPU kernel

The qiskit-aer-gpu-cu11 0.17.2 wheel (sha256 2684a4bf8dc7...f2892, cp313
manylinux2014) lists libcustatevec.so.1 and libcutensornet.so.2 as NEEDED
libraries, resolved through the RPATH `$ORIGIN/../../cuquantum/lib`, and its
Requires-Dist names `cuquantum-cu11>=23.3.0,<24.11.0`, so every GPU kernel
that pip-installed the wheel with dependencies already carries the libraries:
the 2026-10-16T204620Z probe imported it and ran GPU trajectories, which the
NEEDED entries require to resolve (its pip.txt holds download progress bars
only, with no package names). The wheel carries cubins for sm_70 through sm_87, which
include the T4's sm_75. The retained GPU runs never set `cuStateVec_enable`,
whose Aer default is off, so no retained record exercises the library.
`KERNEL_PINS` now pins `cuquantum-cu11==24.8.0` (custatevec-cu11
1.6.0.post1, cutensornet-cu11 2.5.0) and the kernel reports all three
versions in `environment.json`.

The T4 check pushed after this change:

```sh
"$PYTHON" scripts/kaggle_run.py push --slug aer-custatevec-probe \
    --machine NvidiaTeslaT4 --timeout 1800 \
    --include docs/evidence/calibration/ibm_kingston.json \
    scripts/aer_gpu_probe.py -- \
    --snapshot docs/evidence/calibration/ibm_kingston.json \
    --out /kaggle/working/output/aer-gpu-probe.json \
    --only cpu_statevector gpu_statevector gpu_statevector_custatevec
```

It succeeds when the `gpu_statevector_custatevec` rows carry `cuStateVec_enable`
true in `metadata`, no `failed` field, and a total variation from
`cpu_statevector` inside the row's `sampling_scale`. A `failed` row with the
text "does not support cuStateVec" means the wheel's library failed to load;
the `environment.json` versions then identify the cuquantum release.
Host measurements of the same option on a CUDA 13 build are in
`docs/notes/build_host/custatevec.md`.

## CPU-only kernel

`results/kaggle/2026-10-15T232053Z-gororoba-substrate-probe-cpu`

| Quantity | Measured |
| --- | --- |
| CPU | AMD EPYC 7B12, 4 logical CPUs (4 in the affinity mask) |
| RAM | 31.35 GiB total, 30.19 GiB available |
| Working disk (`/kaggle/working`) | 19.52 GiB |
| Python | 3.13.15 |
| Image packages | numpy 2.1.3, scipy 1.16.3, sympy 1.14.0, pandas 2.3.3, torch 2.11.0+cpu |
| Hypercomplex stack | all eight packages built from the pinned archives; `tables.json` regenerated byte-identical |

`AerSimulator().available_devices()` lists `GPU` on this kernel although no
GPU is attached: the qiskit-aer-gpu-cu11 build reports its compiled
devices, so `environment.json` takes GPUs from `nvidia-smi` only.

## Gemma models on Kaggle

The Kaggle API lists these Gemma 4 variations (`google/gemma-4`); sizes are
the uncompressed bytes the API reports. A kernel attaches one through
`model_sources`. Only `gemma-4-e2b-it` (transformers) has run in this
account, on one T4.

| Variation | Framework | Size (GB) |
| --- | --- | ---: |
| gemma-4-e2b-it | transformers | 10.28 |
| gemma-4-e4b-it | transformers | 16.02 |
| gemma-4-31b-it | transformers | 62.58 |
| gemma-4-e2b-it-qat-q4_0-gguf | GGUF | 4.34 |
| gemma-4-e4b-it-qat-q4_0-gguf | GGUF | 6.15 |
| gemma-4-12b-it-qat-q4_0-gguf | GGUF | 7.15 |
| gemma-4-26b-a4b-it-qat-q4_0-gguf | GGUF | 15.63 |
| gemma-4-31b-it-qat-q4_0-gguf | GGUF | 18.85 |
| gemma-4-26b-a4b-it, gemma-4-31b-it | Flax | 95.69, 115.78 |

A model answer is a text artifact. It supports no physical or mathematical
claim, and `docs/evidence/simulation-notebook-audit/README.md` records why.
