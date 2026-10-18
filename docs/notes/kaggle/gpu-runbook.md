# GPU kernel runbook

A Kaggle GPU kernel spends quota from the push until it ends, whether or
not it measures anything. This runbook is the procedure that took the Aer
GPU configuration question from a 1.5 h push that returned no row to a
complete T4 x2 record in 0.84 h. It then answered the cache-blocking
question in 0.30 h more. Each rule below names the failure that produced
it and the code or gate that enforces it.

## What the T4 runs settled

| Record | Question | Answer |
| --- | --- | --- |
| `results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config` (core-450) | Does the pinned GPU venv run on both T4s, and which Aer executor wins? | every GPU row on the GPU; batched trajectories 3.5 and 3.8 times faster than unbatched at 7 and 10 qubits; cuStateVec 1.44 and 1.63 times faster on the dynamic density matrix; Aer spreads per-shot and batched runs over both GPUs |
| `results/kaggle/2026-10-17T211857Z-gororoba-aer-gpu-env-preflight` | Does the preflight stop a CPU fallback? | exit 4 on a CPU machine, at no GPU quota |
| `results/kaggle/2026-10-18T041945Z-gororoba-ghost-branching-t4` (core-441) | Does the exact branching ghost sweep gain from a T4, or from one process per T4? | no: the CPU pool map takes 34 s in every row and the GPU phases 4 s, so numpy over 4 workers (34.9 s) beats torch CUDA (39.3 s); one process per T4 ran 0.994 of one process; torch complex128 laws match numpy within 1.4e-15 (`docs/evidence/ghost_error_scale_branching/README.md`) |
| `results/kaggle/2026-10-18T041018Z-gororoba-ghost-branching-preflight` | Does `--gpu-env-with torch` install torch 2.14.1 in the pinned venv? | yes, at version, and the CPU machine stopped at the preflight with exit 4 |
| `results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config` (core-442) | Does a CUDA 13 build of Aer 0.17.2 run on the T4s under driver 580? | yes: both T4s, cuStateVec on, all 35 rows; GPU density-matrix rows draw the cu11 wheel's seeded counts and run 1 to 14 percent faster, while statevector trajectories differ by build (`docs/notes/kaggle/custatevec.md`) |
| `results/kaggle/2026-10-18T055207Z-gororoba-ghost-branching-sweep` | Does the CPU route reproduce the sweep under CI's Python and pins? | yes: every serialized distance and best point of the 14 evaluated runs equals the build host's output at six decimals; the pool map took 36.1 s on 4 CPUs (`docs/evidence/ghost_error_scale_branching/README.md`) |
| `results/kaggle/2026-10-17T225519Z-gororoba-aer-blocking` and `2026-10-17T230346Z-gororoba-aer-blocking` (core-451) | Why did density matrix 15 and statevector 30 die on a T4? | Aer's automatic blocking filled host memory and the OOM killer ended it; explicit chunks ran both across the two T4s in 4.2 and 7.2 s |

The timings are in `docs/evidence/aer_gpu_configuration/README.md` and
`docs/notes/kaggle/substrates.md`.

## The procedure

1. **Decide the substrate before writing code.** The routing rule and the
   width table in `substrates.md` settle CPU, GPU, build host or hardware.
   Measured on Kaggle (`substrates.md`, "CPU against T4"): a static
   density matrix runs 8.5 s on the 4 CPUs against 3.0 s on a T4 at 10
   qubits and 1955 s against 111 s at 14; a dynamic density matrix 69.6 s
   against 24.3 s at 6. Statevector trajectories of the 7-qubit N=21
   feed-forward circuits run faster on the CPUs (root AGENTS.md,
   "Simulation on Kaggle"). A GPU push needs a GPU question.
2. **Optimize the classical code first.** Batch replicate estimators with
   numpy under the bit-equality rules (below,
   `docs/notes/build_host/vectorized-fits.md`) and map CPU-bound loops
   through `parallel.ordered_map`. A GPU hour spent on a pure-Python loop
   buys the loop, not the GPU.
3. **Rehearse the exact entry locally in the kernel's environment.**
   - Build a venv like the kernel's: the image's Python 3.13, the
     repository pins with qiskit-aer-gpu-cu11 and the cuQuantum wheels in
     qiskit-aer's place (`ci/install_pins.sh` with `AER_PINS`).
   - Run the entry with the push's arguments. The host run of the T4
     probe's arguments measured 47 s for the toy rows and 1,226 s for the
     width rows. The three 10-qubit dynamic density-matrix rows took 769 s
     of that, the cost the timeout had to cover.
   - A rehearsal on the build host's single GPU skips every two-GPU row.
     The probe's `target_gpus` row is one, and a direct local call found
     that `set_options` rejects `target_gpus` before any T4 run reached the
     row. Exercise every two-GPU option by a direct local call before the
     push.
4. **Size the run, then cut it.**
   - Push only the rows the question needs: the T4 probe ran
     `--workloads toy,width --widths 7,10` rather than the full matrix.
   - Order rows cheap first, so a timeout cuts only the most expensive
     ones. The probe writes its record after every row, so a cut-off kernel
     keeps every finished row.
   - Set `--timeout` from the rehearsal at two to three times the build
     host's GPU time, plus about 5 minutes for the venv install.
     kaggle_run.py refuses an accelerator push without one.
5. **Prove the failure path at no GPU cost.** The same push with
   `--machine cpu` runs the preflight on a CPU machine. Its exit 4 shows the
   kernel stops instead of falling back to the CPU.
6. **Push with the pinned GPU environment.** Use `--gpu-env`, plus
   `--require-gpu` where the entry has it. Read `kaggle quota` before the
   push. Never push a new version while one runs.
7. **Collect, check, retain.**
   - `status` and `collect` retain the output under results/kaggle/, and
     collect.json pins each file's sha256 (core-290). A collected file is
     never rewritten; a later rule that needs more fields reads them from
     the arguments `--check` is given.
   - Run the record's `--check` in normal and `-O` mode and add it as a gate
     in the same change.
   - Read `kaggle quota` after the run.

## Failure modes met, and the rule each one produced

| Symptom | Cause | Rule | Enforced by |
| --- | --- | --- | --- |
| First T4 push: 1.5 h, `--timeout 5400` reached, no row | the 1-minute load average counts the probe's own previous row, so every row of a 4-CPU probe read busy, waited 30 s and reran | contention is foreign CPUs from /proc/stat less the probe's own process tree | `aer_gpu_probe.contended`, `held` |
| The same push returned no stdout and no record | the entry's output was captured in memory and copied after exit | the entry's stdout, stderr and `--out` stream into /kaggle/working/output | `kernel_main.start_entry`, core-280 |
| `run.py` at 1,041,184 bytes, over the 1,000,000-byte source limit | per-member deflate of the bundled files | one xz stream over a stored zip, about 696 KB of base64 | `kaggle_run.pack_bundle`, core-280 |
| `available_devices()` lists GPU on a CPU machine | the cu11 build reports GPU without a CUDA device | only a run's result metadata `device` proves the GPU | `gpu_env_report.py` Bell runs, `gpu_fallback` |
| The image's `sitecustomize` ran inside the venv entry | the image exports PYTHONPATH | the venv drops PYTHONPATH, PYTHONHOME, PYTHONSTARTUP and PYTHONUSERBASE, and the preflight fails on any sys.path entry outside the venv and the standard library | `kernel_main.gpu_interpreter`, core-280 |
| A CPU qiskit-aer could replace the CUDA module | qiskit-aer and qiskit-aer-gpu-cu11 both install `qiskit_aer/` | the GPU wheel is the only owner of `qiskit_aer/__init__.py` | `install_pins.sh` `AER_PINS`, `gpu_env_failures` |
| The two-GPU row raised `Invalid option target_gpus` | Aer 0.17.2 takes `target_gpus` only as a run option | `RUN_OPTIONS` travel with `run()` | `aer_gpu_probe.execute`, `aer_blocking_probe.run_one` |
| A trial's OOM kill took the kernel driver with it | a 30 GiB host allocation in one child | each trial child sets `oom_score_adj` 1000 | `aer_blocking_probe.sampled` |
| `std::bad_alloc` or an OOM kill past one GPU's memory | Aer's automatic blocking picks a chunk as wide as a whole device, which lands in host memory | `blocking_qubits_for`: a chunk under a quarter of one GPU | `SnapshotSimulator.run`, core-452 |
| `Invalid jump destination` aborts the process | the blocking pass splits an if_else's jump and mark into different chunk blocks | a blocked batch runs in `lower_conditionals` form or raises ValueError | `calibration_snapshot.blocked_batch`, core-452 |
| Wrong outcomes from blocked conditions on the CPU | Aer's CPU chunk executor misplaces bfunc conditions | blocking applies on a GPU device only | core-452 asserts the CPU fault |
| `--check` passed a truncated record | the check read only the rows present | the record writes its plan before the first row, and the rows must equal it | `aer_gpu_probe.binding_problems`, core-367, core-450 |
| `--with` groups were absent from the entry | the bootstrap installs groups into the image interpreter | `--gpu-env` refuses `--with` | `kaggle_run.build_kernel`, core-280 |

## Aer on Kaggle

| Work | Configuration | Why |
| --- | --- | --- |
| Static noisy trajectories, at most 10 active qubits | `noise_simulator(..., "GPU", method="statevector")`, batched by default | 3.5 to 3.8 times unbatched on the T4 |
| Feed-forward trajectories | `SnapshotSimulator.run` turns batching off | the batched executor rejects `jump` and reads lowered conditions before the readout channel |
| Dynamic density matrix | `custatevec=True` | 1.44 and 1.63 times the plain GPU executor at 7 and 10 qubits on the T4 |
| Statevector trajectories with cuStateVec | leave it off | 1.19 to 1.29 times slower |
| A state wider than one GPU | automatic in `SnapshotSimulator.run` | chunks across both T4s; feed-forward lowered |
| Many shots on two GPUs | nothing to add for per-shot and batched runs | Aer reports two GPUs in use; a measurement-sampled run evolves one state on one GPU |
| Seeded counts for a CI gate | CPU sampler, or a gate that re-derives from retained GPU counts | seeded GPU counts differ from CPU counts |
| Shot branching | never | it drops a mid-circuit measurement's readout channel |

A process per GPU (`CUDA_VISIBLE_DEVICES`) adds nothing to Aer's own
two-GPU spread for per-shot and batched runs. A measurement-sampled run, a
static circuit whose shots Aer draws from one final state, holds one GPU:
the 29-qubit GHZ under Aer's defaults used GPU 0 alone, with GPU 1 at its
209 MiB baseline. On the ghost-branching estimator the
GPU phases are 2.4 s of a 58.7 s run, so it would gain about 1 percent; the
#68 T4 row measures it.

## Python numerics: speed without losing the bits

The pinned GPU venv holds the build host's numerical stack: numpy 2.5.4
and scipy 1.18.1 on scipy-openblas 0.3.34. The image's own numpy 2.1.3 and
scipy 1.16.3 stay out of the entry. OpenBLAS's DYNAMIC_ARCH picks its
kernels per host, and numpy dispatches SIMD per host as well. On the T4
machine numpy found X86_V3 and X86_V4 (AVX-512). On the CPU preflight
machine it found X86_V3 only. `gpu_env.json` and the probe record carry
both readings.

**Order of work**, from `docs/notes/build_host/vectorized-fits.md`:
1. Batch replicate estimators with numpy, keeping the scalar version as
   the reference.
2. Map blocks through `parallel.ordered_map`.
3. Shard across Kaggle CPU sessions by item range only if the run is still
   too slow.

Batching one null calibration (2.8 million fits) took it from 7,317 s on a
4-CPU Kaggle kernel to 163 s pooled on the build host, with the same bytes.
One fit dropped from 3,182 to 3,491 us scalar to 141 to 159 us batched.

**Bit-equality rules** (each measured before the code relied on it,
`vectorized-fits.md`):
- Keep the scalar association, for example `(w * f) * f`. numpy's
  `+ - * /` and comparisons are IEEE binary64, identical to Python floats.
- Sum the way builtin `sum()` does, which on CPython 3.12 and later
  compensates rounding (Neumaier). 76,461 of 200,000 random 6-term sums
  differ from left-to-right addition. No `np.sum`, `einsum` or matmul
  touches a value that feeds a decision or an output.
- Square through `math.pow`. Python's `x ** 2` calls libm `pow`, while
  numpy computes `x * x`; 2,481 of 3,000,000 doubles differ.
- Take `exp` through `math.exp`. On an AVX-512 host, the T4 machine among
  them, numpy dispatches float64 `exp` and `power` to its own kernels.
- Keep the builtin `round`: `np.round` scales, rounds and divides.
- A gate proves the batched path returns the reference's bits; a tolerance
  is never the criterion.

**Process pool rules** (`gororoba_quantum/parallel.py`):
- Workers start under spawn. A fork of a process that already runs Aer or
  rustworkx thread pools can deadlock a child.
- Each worker starts with one BLAS and OpenMP thread, so N workers do not
  start N times the CPUs' threads.
- `available_cpus()` takes the affinity mask bounded by the cgroup CPU
  quota, so a Kaggle container uses what it grants.
- `GOROROBA_WORKERS=1` runs serially.
- A script that starts a pool keeps a `__main__` guard.

**Libraries by role** (`docs/notes/quantum-tools/` holds each note; the
pins are in requirements.txt and `scripts/kaggle_run.py` KERNEL_PINS and
PIN_GROUPS):

| Library | Role here | Speed or accuracy fact | Trap |
| --- | --- | --- | --- |
| qiskit-aer 0.17.2 (GPU: qiskit-aer-gpu-cu11) | noisy replay, `noise_simulator` | GPU and CPU draw identical seeded counts on a static circuit; executor choice above | the cu11 build lists GPU without a device; `NoiseModel.from_backend` carries relaxation only, and the snapshot's readout errors are reported values (Kingston q0 and q1 read 39 and 27 percent misassignment against under 1 percent reported) |
| cuQuantum (custatevec-cu11 1.6.0.post1, cutensornet-cu11 2.5.0) | loaded by Aer through its RPATH | dynamic density matrix 1.44 to 1.63 times faster on the T4 | off under `batched_shots_gpu` |
| qiskit 2.5.2 | circuits, Target, transpile | compare compiled gate counts, not nominal ones | transpile of several circuits uses a process pool, so scripts keep a `__main__` guard; pin `seed_transpiler` and `initial_layout`; `Operator` above about 12 qubits exhausts memory |
| rustworkx 0.18.1 | replica placement (`vf2_mapping`) | `id_order=True` fixes the match order for replay | Rust thread pools plus fork deadlock |
| scipy 1.18.1 | statistics, `linalg.expm`, sparse feasibility | none measured | Kaggle's image carries 1.16.3; the venv replaces it |
| sympy 1.14.0 with python-flint 0.9.0 | exact rank and certificates | exact where float64 is no proof: numpy's det of `[[1..9]]` reads 6.661e-16, sympy 0 | a rank or singularity claim is a sympy statement, never a float one |
| stim 1.16.0 | Clifford sampling at thousands of qubits | parity probability 0.01454 against Aer's 0.01471 at 200,000 shots, from symmetric X errors | CPU only, never a GPU kernel; no `rz(theta)` off multiples of pi/2 |
| quimb 1.15.0, cotengra 0.8.2, autoray 0.11.0 | ideal simulation past 14 qubits | a 22-qubit expectation agrees with numpy to 10 digits on torch-cpu, torch-cuda and cupy | no kahypar, so cotengra's path quality is lower; `HyperOptimizer(seed=)` needs `optlib="random"`; compare to 1e-10, since contraction order changes the last digits |
| mthree 3.0.0 | readout mitigation | mitigated `<Z0>` 0.7986 against raw 0.7946 and ideal 0.8 | `mthree.openmp` reads False; a 4000-shot calibration carries about 0.002 error per element; mid-circuit measurement breaks `final_measurement_mapping` |
| qiskit-experiments 0.14.2, lmfit 1.3.4 | readout, RB, T1 and Ramsey fits | T1 298 +/- 13 us against 313.2 us; Ramsey tau 373.3 +/- 5.6 us against T2 366.7 us | unweighted lmfit fits assume unit variance; quality "good" judges the fit, not agreement with calibration |
| torch (image 2.11.0; 2.14.1 in the venv with `--gpu-env-with torch`) | quimb backend, package checks, branch_dm's GPU evolver | complex128 matmul on the GPU within 1e-10 of numpy; branch_dm laws within 1.4e-15 | warm up before timing; the first CUDA call costs seconds; a GPU evolver fed from a CPU pool pays the plans' transfer to the GPU process |
| jax (host 0.9.0, CPU jaxlib) | `jax_bridge` evolver | numpy complex128 stays the reference | the JAX evolver stores complex64 |
| pyzx 0.10.7, galois 0.4.11, numba 0.68.0 | T-count rewriting, GF(2) algebra, JIT for galois and the quaternion packages | a 200 x 200 GF(2) product takes 0.0004 s on a repeat call | CPU only; `compare_tensors` allocates 2^n x 2^n |

Run stim, pyzx, galois, lmfit, mthree, rustworkx and samplomatic on a CPU
kernel or the build host; none has a GPU path. `push --with quantum-tools`
installs the group into the image interpreter, which `--gpu-env` refuses.

## Quota ledger of the runs above

| Push | Machine | GPU hours | Outcome |
| --- | --- | --- | --- |
| gororoba-aer-gpu-config v1 | T4 x2 | 1.5 | timeout, no row: the contention and output-capture faults |
| gororoba-aer-gpu-env-preflight | CPU | 0 | exit 4 on the missing GPU, as designed |
| gororoba-aer-gpu-config v2 | T4 x2 | 0.84 | 35 rows, every GPU row on the GPU |
| gororoba-aer-blocking v1 | T4 x2 | 0.09 | 3 trials, then the OOM kill took the kernel |
| gororoba-aer-blocking v2 | T4 x2 | 0.21 | 14 trials, both wide widths blocked across both GPUs |
| gororoba-ghost-branching-preflight | CPU | 0 | torch 2.14.1 at version in the venv, exit 4 on the missing GPU |
| gororoba-ghost-branching-t4 | T4 x2 | 0.19 | 5 rows; the sweep is CPU-bound, so its route is a CPU kernel |
| gororoba-ghost-branching-sweep | CPU, `--ci-env` | 0 | the full sweep under CI's pins, equal to the build host's output apart from timings |
| gororoba-aer-gpu-cu13-preflight | CPU | 0 | the cu13 wheel verified and imported, exit 4 on the missing GPU |
| gororoba-aer-gpu-cu13-config | T4 x2 | 0.85 | 35 rows on the cu13 wheel, every GPU row on the GPU |

The plan before the fixes budgeted a 3 h rerun of the full matrix
(`--timeout 10800`). The rehearsal, the reduced matrix and the contention
fix answered the question in 0.84 h, and the blocking question took 0.30 h.

## Fifteen qubits

A 15-qubit run waits for an approved case under the root AGENTS.md routing
rule. The case names one of three substrates:
- the build host's Aer, where the CPU ran a 15-qubit density matrix in 17 s;
- the Kaggle T4 x2 under cache blocking, about 4 s static and 15 s per
  feed-forward shot;
- Tuna-17 through Quantum Inspire, whose `submit` refuses while another
  session's hardware job is unfinished or recent. The case names each
  Tuna-17 qubit it uses that the device notes exclude.
