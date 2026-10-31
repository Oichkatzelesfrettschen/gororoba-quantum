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
| A 15-qubit run | build host or Kaggle T4 x2 Aer with cache blocking, or Tuna-17 through Quantum Inspire, the substrate named in an approved case | decision-gated (root AGENTS.md); 15 qubits fit both simulation and Tuna-17 |
| IBM jobs (16 or more qubits, or a named device qubit) | IBM Heron, after an approved case | the device is the question |
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
| Two GPUs in one session | Kaggle `NvidiaTeslaT4` (2 x T4) | Aer spreads per-shot and batched runs over both (`batched_shots_optimization_parallel_gpus`, `gpu_parallel_shots_` 2), while a measurement-sampled run evolves one state on one GPU, and `SnapshotSimulator.run` splits a state wider than one T4 across both with cache blocking: a 15-qubit density matrix in 4.2 s and a 30-qubit statevector in 7.2 s (measured, `results/kaggle/2026-10-17T230346Z-gororoba-aer-blocking`) |
| TPU (with its host CPU) | Kaggle `TpuV5E8`, `TpuV6E8` | JAX only; Aer has no TPU backend, so a TPU session would serve the repository as a large CPU host (96 cores and 330 GB RAM on the documented v3-8 VM). Every batch request with either ID (CLI, MCP, the editor's commit) ran on a 4-core Xeon CPU machine on the CPU image without libtpu, with the TPU accelerator recorded server-side and TPU quota unused, with Persona identity verification, which the editor names as a TPU requirement, absent on the account; [tpu-research.md](tpu-research.md) holds the routes and the root-cause analysis |
| CPU + GPU + TPU at once | not inside one Kaggle session | across sessions: Kaggle GPU kernels for Aer, a Kaggle TPU session for CPU-heavy Aer or JAX, the build host for dry runs, calibration exports and replay gates |
| Any of the above + IBM | only after an approved case | IBM answers device questions; every substrate above feeds its design, never its result |

## Weekly budget and tandem capacity

Kaggle meters GPU and TPU time per account per week and caps live batch
sessions per pool; the two limits are independent
([workflow.md](workflow.md) holds the session-count messages). The MCP call
`get_accelerator_quota` returns the weekly allowance, the time used and
`quota_refresh_time`, and `kaggle quota` prints the same numbers.

| Pool | Weekly allowance | Live batch sessions | Per session |
| --- | --- | --- | --- |
| CPU | unmetered | 5, shared with TPU requests | 4 cores, about 30 GiB RAM, 19.5 GiB `/kaggle/working`, 12 h run limit |
| GPU (T4 x2, P100, L4 shapes) | 30 h (108,000 s) | 2 | 4 cores, about 29 GiB RAM beside the accelerator |
| TPU (`TpuV5E8`, `TpuV6E8`) | 20 h (72,000 s) | 1 | v5e-8 VM; no repository run has yet reached it (see [tpu-research.md](tpu-research.md)) |

The quota refreshes weekly at Saturday 00:00 UTC, which is Friday 17:00
Pacific daylight time (PDT, UTC-7) and, after daylight time ends on the
first Sunday of November, Friday 16:00 Pacific standard time (PST, UTC-8).
Unused hours do not carry over.

Run in tandem, one account holds at most eight live sessions: five CPU
sessions (one fewer per live TPU request), two GPU sessions and one TPU
session, each with its own 4-core host or TPU VM. A classical algebra job
that needs RAM rather than an accelerator gains only from the hosts: a CPU
or GPU session gives about 30 GiB and 4 cores, so jobs larger than that
stay on the build host (62 GiB) or an approved cloud VM, and GPU hours spent
on CPU-only work buy nothing a CPU session lacks. The usable ceiling is the
session cgroup's `memory.max` less `memory.current`, measured at 29.5 GiB
of headroom on a fresh session ([Managed memory past VRAM](#managed-memory-past-vram)),
so a job that peaks under about 27 GiB with a 2 GiB margin and finishes
inside the 12 h run limit fits one CPU session, five at once and unmetered.
That rule covers the Singular and FLINT stages of the A_5 exceptional-fiber
program as well as qubit simulation; a Singular `std` is single-threaded
CPU work, so it goes to a CPU session, never a GPU one. Each such job runs
under a resource limit set below the ceiling (`ulimit -v` or a cgroup
`memory.max` from the kernel script) so an overrun ends the job with its
partial output saved rather than drawing the session's OOM kill. Measured
peaks of A_5 jobs on the 82 GiB Azure VMs decide placement:

| A_5 job | Peak resident memory | Kaggle CPU session |
| --- | --- | --- |
| Chart-5 normalization and Hensel arcs of the E8-bar to VB fiber | 3.2 GiB | fits |
| Isotropic fiber, membership rank at degree 4 | 18.9 GiB, still rising at 5.5 h | fits so far; settles at completion |
| E8-bar to N- fiber, membership rank at degree 3 | 21.4 GiB, still rising at 5.1 h | fits so far; settles at completion |
| W8 fiber, membership rank at degree 3 | 39.0 GiB | exceeds; stays on an 82 GiB VM |
| X- fiber, degree 2 | 2 GiB (build host) | fits |

The degree-3 and degree-4 rows carry peaks read at the stated elapsed time
from each job's cgroup `memory.peak`; a row whose job is still running
records a lower bound, and its final peak decides whether a repeat or a
neighboring degree moves to Kaggle.

## Qubit size guide

Exact state memory is 16 x 2^n bytes for a double-precision statevector,
8 x 2^n in single precision (`precision="single"`), 16 x 4^n for a
double-precision density matrix and 8 x 4^n in single. The estimates below
allow 90 percent of the device or host memory for the state and ignore
Aer's workspace; the measured columns come from `capacity.json` (a GHZ
circuit at 256 shots, each width tried once in its own process).

| Substrate | Memory | Statevector, double / single (estimate) | Density matrix, double / single (estimate) | Measured |
| --- | --- | --- | --- | --- |
| Kaggle T4 (one GPU) | 15 GiB | 29 / 30 | 14 / 15 | density matrix 14 (1.0 s); statevector 29 (4.4 s); 31 refused by Aer (target maximum 30, from host memory) |
| Kaggle T4 x2, cache blocking | 2 x 15 GiB | 30 | 15 | density matrix 15 (4.2 s, 9,437 MiB per GPU); statevector 30 (7.2 s, 10,461 and 10,507 MiB); Aer's automatic choice at either width: host OOM kill |
| Kaggle CPU or GPU-session host RAM | 29 to 30 GB | 30 / 31 | 15 / 15 | not measured |
| Kaggle TPU VM host RAM | 330 GB (documented, v3-8) | 34 / 35 | 17 / 17 | not reachable: TPU pushes ran on 4-core CPU machines |
| Build host RTX 4070 Ti | 12 GiB | 29 / 30 | 14 / 15 | density matrix 14, statevector 29; one wider fails with `std::bad_alloc` (detail in the untracked `docs/local/`) |
| Build host RAM | 62 GiB | 31 / 32 | 15 / 16 | density matrix 15 (17 s), statevector 31 (74 s); wider widths need 64 GiB and are not tried |

Rows list only substrates whose memory was measured or is documented
(`site/notebooks.md`); Kaggle publishes no memory for the L4, A100, H100 or
RTX Pro 6000 IDs, none of which this account reached, so this guide states
no width for them. Single precision is not configured in
`calibration_snapshot.noise_simulator` and is not measured here; cache
blocking is (below).

What goes where by width, under the routing rule (root AGENTS.md: 14 qubits
or fewer on Kaggle, 15 by an approved case, 16 or more on IBM):

| Width | Noisy simulation | Ideal simulation | Hardware |
| --- | --- | --- | --- |
| 1 to 10 qubits | Kaggle CPU: statevector trajectories, or the density matrix of a static circuit | Kaggle CPU statevector | IBM only for a named-device question with an approved case |
| 11 to 14 qubits | Kaggle GPU, double-precision density matrix (measured on one T4 to 14); a dynamic circuit stays on the CPU's trajectories unless a probe at its width shows the GPU faster | Kaggle GPU statevector | IBM only for a named-device question with an approved case |
| 15 qubits | Kaggle T4 x2, density matrix cache-blocked across both GPUs (4.2 s static; a feed-forward shot about 15 s), or the build host (CPU density matrix 15 in 17 s), after an approved case | Kaggle GPU statevector | Tuna-17 through Quantum Inspire after an approved case that names the excluded qubits it uses |
| 16 qubits or more | none measured on Kaggle for the density matrix | Kaggle GPU statevector up to 30 qubits blocked across both T4s, as design support for a hardware case | IBM after an approved case |

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
| Density matrix (double) | 12 to 14 qubits in under 1 s; 15 killed (signal 9) under Aer's automatic choice |
| Statevector (double) | 26 to 29 qubits in under 5 s; 30 killed (signal 9) under Aer's automatic choice; 31 refused by Aer, whose target reports 30 qubits at most |

Each width ran in its own process, so the killed trials ended only
themselves. Both machines' GPUs were visible. The kill is the host's, not
the GPU's: the blocking probe (`scripts/aer_blocking_probe.py`,
`results/kaggle/2026-10-17T225519Z-gororoba-aer-blocking` and
`2026-10-17T230346Z-gororoba-aer-blocking`) shows Aer's automatic blocking
of a 16 GiB state placing it whole in host memory (30,155 MiB peak RSS of
the machine's 31 GiB, each GPU at its 209 MiB baseline) until the cgroup
OOM killer ends it, the first time with the kernel driver too.

## Cache blocking across both T4s

Aer blocks a state on its own once it exceeds one GPU's memory
(ParallelStateExecutor::multiple_chunk_required), with a chunk as wide as a
whole device, and that choice lands in host memory. `SnapshotSimulator.run`
keeps Aer's trigger and sets the chunk from
`calibration_snapshot.blocking_qubits_for`, the widest double-precision
chunk under a quarter of one GPU's memory as Aer's `blocking_qubits`
documentation asks: 27 qubits for a statevector and 13 for a density matrix
on a T4 or the build host's RTX 4070 Ti. Measured on the T4 x2 (gate core-451):

| Run | Seconds | Memory |
| --- | --- | --- |
| density matrix 15, blocked across both T4s | 4.2 | 9,437 MiB per GPU |
| the same with cuStateVec | 4.0 | 9,463 MiB per GPU |
| the same on GPU 0 with chunks in host memory (`target_gpus=[0]`) | 16.1 | 14,563 MiB on GPU 0, 4,524 MiB RSS |
| statevector 30, blocked across both T4s | 7.2 | 10,461 and 10,507 MiB |
| the same with cuStateVec | 5.4 | 10,541 and 10,495 MiB |
| the same on GPU 0 with chunks in host memory | 24.7 | 14,629 MiB on GPU 0, 6,573 MiB RSS |
| feed-forward, lowered, density matrix 15, 2 shots | 29.1 | both GPUs |
| feed-forward, lowered, statevector 30, 2 shots | 46.6 | both GPUs |

- An if_else under blocking aborts the process (`Invalid jump destination`):
  AerCompiler inlines it into jump and mark, and the blocking pass splits
  them into different chunk blocks. `SnapshotSimulator.run` therefore runs a
  blocked batch in `lower_conditionals` form and raises ValueError where
  none exists (an else body, a measurement in the body, nested flow).
- On the GPU the blocked lowered readout toy draws the if_else toy's seeded
  counts with the condition on the recorded, post-readout bit, statevector
  and density matrix; Aer's CPU chunk executor under the same blocking
  leaves the condition's bit (gate core-452), so blocking applies on a GPU
  only.
- `max_parallel_shots=1` keeps Aer from sizing parallel shots of a dynamic
  circuit against the whole state ("a circuit requires more memory than
  max_memory_mb" on one GPU).
- A blocked feed-forward shot re-evolves the full state: about 15 s per
  density-matrix-15 shot and 23 s per statevector-30 shot on the T4 x2, and
  on the build host's single 12 GiB GPU with chunks in host memory 308 s per
  statevector-30 shot. Wide feed-forward work stays a few-shot measurement.
- A 15-qubit run is decision-gated under the root AGENTS.md rule: an
  approved case names this Kaggle route, the build host, or Tuna-17.

## Managed memory past VRAM

`results/kaggle/2026-10-31T012131Z-gororoba-memory-probe-t4` (kernel
`probablyeric/memory-probe` version 3, T4 x2 shape, one GPU used)

The probe measures three memory regimes in turn: host RAM with numpy and
scipy, device memory with CuPy, and CUDA managed memory
(`cupy.cuda.malloc_managed`, which calls `cudaMallocManaged`) sized past the
T4's memory so the driver pages the overflow to host RAM. Each managed size
runs in its own subprocess, because pages a process frees stay charged to
the session cgroup until that process exits, and each subprocess starts only
when the cgroup headroom exceeds its size plus 2 GiB. The pass criterion is
an exact device-side sum of an array filled with ones, then of the same
array scaled by two.

| Quantity | Measured |
| --- | --- |
| Host | 4 logical CPUs, 31.35 GiB total, 29.5 GiB cgroup headroom |
| numpy 2.1.3, float64 4096 x 4096 matmul / LU (scipy 1.16.3) | 1.21 s / 0.77 s |
| T4 memory (CuPy 14.0.1) | 14.56 GiB total, 14 GiB largest single allocation in 1 GiB steps |
| CuPy float32 4096 x 4096 matmul | 0.048 s |
| `cudaDevAttrPageableMemoryAccess` | 0: the GPU cannot address ordinary `malloc` memory (heterogeneous memory management needs the open kernel module or ATS) |
| `cudaDevAttrConcurrentManagedAccess` | 1: managed allocations oversubscribe device memory |

| Managed size | Residence | Fill | Sum | Scale and sum |
| --- | --- | --- | --- | --- |
| 4 GiB | device | 1.63 s | 0.11 s | 0.17 s |
| 8 GiB | device | 1.62 s | 1.52 s | 1.46 s |
| 12 GiB | device | 2.29 s | 2.20 s | 2.30 s |
| 14 GiB | device, at the limit | 2.50 s | 2.43 s | 2.56 s |
| 16 GiB | spilled to host | 3.04 s | 7.02 s | 12.15 s |
| 20 GiB | spilled | 4.3 s | 8.73 s | 15.73 s |
| 24 GiB | spilled | 5.4 s | 11.09 s | 19.45 s |
| 26 GiB | spilled | 6.0 s | 11.41 s | 21.02 s |

Every sum is exact, and no size failed. A pass over a spilled array costs
about 0.44 s per GiB against 0.17 s per GiB resident, so streaming work
past device memory runs at roughly a third of resident speed, with no cliff.
The ceiling of a managed allocation is the cgroup headroom less the margin,
about 27 GiB; 26 GiB was the largest size tried. A GPU job that holds
between 14.5 and 27 GiB therefore runs on one T4 through managed memory, and
for a statevector that is one qubit beyond device memory. Aer's own
automatic blocking places a 16 GiB state in host memory and draws the OOM
kill ([T4 x2 GPU kernel](#t4-x2-gpu-kernel)), so an Aer run past one T4
uses [cache blocking across both GPUs](#cache-blocking-across-both-t4s) rather than relying on
oversubscription.

Two earlier versions of the probe drew the session's OOM kill and recorded
nothing past the kill: a guard that read `/proc/meminfo` saw the machine's
free memory rather than the cgroup limit, and one process that allocated
and freed every size in turn accumulated the charge of its freed managed
pages. A kernel script on Kaggle reads `memory.max` and `memory.current`
from `/sys/fs/cgroup` for its memory guard, saves each step's result as it
completes, and isolates each large allocation in a subprocess.

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
  flow. `docs/evidence/aer_gpu_configuration/README.md` measures it on
  circuits without control flow (3.8 and 2.7 times faster than unbatched at
  7 and 10 qubits, 2.2 times slower at 14), which sets
  `calibration_snapshot.BATCHED_SHOTS_MAX_QUBITS` to 10 and keeps
  feed-forward circuits unbatched.
- **Agreement.** Every sampler that completed agrees with the CPU
  trajectories within its sampling scale.

## cuStateVec on the GPU kernel

[custatevec.md](custatevec.md) holds the cu11 wheel's cuQuantum library
chain, the pins that hold it, the T4 push command and the success test.

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
