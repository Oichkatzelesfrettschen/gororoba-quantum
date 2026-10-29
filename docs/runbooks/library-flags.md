# Library flags: per-package knobs for the Python and executable stack

This runbook is the per-library companion of [compute-flags.md](compute-flags.md).
That runbook holds the memory caps, the pre-run checklist and the measured
combinations; this one lists, for each package the tracked Python files import,
the environment variables, API options and build facts that change speed or
results, the setting a workload starts from, and the measurement that would
overturn it. Versions come from the system `python3` (Python 3.14) on the build
host; every row says what verified it. Start every command that imports qiskit
with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; the combined Qiskit
Rust and Aer OpenMP extensions require it ([AGENTS.md](../../AGENTS.md)).

Status values: `verified` means the knob exists in the installed package at the
cited source or command output; `unverified` means the name comes from
documentation or memory and no installed source confirms it; `unmeasured` on a
recommendation means no retained run compares it with the alternatives. A
measured recommendation cites its document.

## Build facts of the host

| Fact | Value | Verified by |
|---|---|---|
| CPU | AMD Ryzen 5 5600X3D, 6 cores, 12 threads | `lscpu` |
| System BLAS and LAPACK | `blas-openblas` 0.3.34 provides `blas`, `cblas`, `lapack` and `lapacke`; numpy, scipy, FLINT, Macaulay2, Sage and the Aer CUDA build link it | `pacman -Qo /usr/lib/libblas.so`; `threadpoolctl.threadpool_info()` lists `openblas` 0.3.34 |
| numpy SIMD baseline | X86_V2, X86_V3 | `numpy.show_config()` |
| scipy 1.18.1 BLAS | `blas`/`lapack` 3.12.0 through the same system provider | `scipy.show_config()` |
| torch 2.14.1 | built against Intel MKL 2026.0, OpenMP 202111, CUDA runtime 13.4, CPU capability AVX2; `torch.get_num_threads()` returns 6 | `torch.__config__.show()` |
| jax 0.9.0 | jaxlib is a self-built CPU wheel; `jax.default_backend()` returns `cpu` and logs that no CUDA-enabled jaxlib is installed | `import jax` |
| qiskit-aer 0.17.2 | devices `CPU` and `GPU` (CUDA Thrust build, cuStateVec path) | `AerSimulator().available_devices()`; [custatevec.md](../notes/build_host/custatevec.md) |

OpenBLAS is the BLAS on every substrate the repository uses: the build host
through `blas-openblas`, and Kaggle, Azure and the hosted CI runners through the
OpenBLAS that numpy and scipy wheels bundle. `OPENBLAS_NUM_THREADS` and
`OPENBLAS_CORETYPE` therefore mean the same thing everywhere. A run that must
reproduce a CI-written record on the build host sets `OPENBLAS_CORETYPE=Haswell`
and `NPY_DISABLE_CPU_FEATURES` as `ci/run_gates.py` does, because numpy's
dispatched loops and OpenBLAS kernels round differently above x86-64-v3.

The host carried AMD AOCL-BLAS 5.3 before; its single library-wide thread
setting made LU and symmetric eigensolves slower at 6 threads than at 1 (rows
below). Removing it broke two local builds that had linked `libblis-mt` and
`libflame` directly through AOCL's `libblas.so` (the Aer CUDA package and the
Macaulay2 AUR build); both were rebuilt against OpenBLAS. Before removing any
library package, list `readelf -d` NEEDED entries across `/usr` and
site-packages: pacman's "Required By" misses direct links.

## Process-wide variables

| Variable | Effect | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `GOROROBA_WORKERS` | caps the worker count of `parallel.ordered_map`; must be a positive integer | `gororoba_quantum/parallel.py` `default_threads` | free physical cores of the job | wall time of one gate at N and N/2 workers | verified, unmeasured |
| `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `BLIS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, `NUMEXPR_NUM_THREADS`, `RAYON_NUM_THREADS`, `QISKIT_NUM_PROCS` | `parallel.py` sets each to 1 in a pool worker unless the caller already set it | `parallel.WORKER_THREAD_VARIABLES`, `WORKER_BLAS_THREADS` | leave to the pool for CPU-bound loops over independent items | a gate whose per-item matrices exceed about 256 x 256 and run faster with 2 BLAS threads per worker | verified, unmeasured |
| `MALLOC_ARENA_MAX=2` or `GLIBC_TUNABLES=glibc.malloc.arena_max=2` | glibc arena count; `kaggle_run.py` sets the tunable | `scripts/kaggle_run.py`; [compute-flags.md](compute-flags.md) | 2 for every multithreaded C program | peak resident set and wall time with the default arena count | verified, unmeasured |
| `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` | static TLS room for the Qiskit and Aer extensions | [AGENTS.md](../../AGENTS.md); `scripts/provider_credits.py` | always when importing qiskit | an import failure without it on the target interpreter | verified |
| `MPLBACKEND=Agg` | non-interactive matplotlib backend | `matplotlib/__init__.py` reads it; `.github/workflows/ci.yml`, `kaggle_kernel/kernel_main.py` set it | `Agg` for every script and CI lane | none; the installed default is `qtagg` | verified |

## qiskit 2.5.2 and qiskit-aer 0.17.2

Uses: `transpile` and pass managers in `gororoba_quantum/` and `live_run.py`;
Aer noise simulation in `local_compute.py`, `calibration_snapshot.py` and the
Kaggle kernel.

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `transpile(optimization_level=)` | default is 2 when `None`, or the `transpile_optimization_level` entry of the user config | `qiskit/compiler/transpiler.py` | pass the level explicitly in every record-producing call | routed CZ count at levels 2 and 3 over three seeds on the target circuit; [simulation-cost-levers.md](simulation-cost-levers.md) retains one such comparison (786 to 799 CZ at level 3) | verified |
| `transpile(seed_transpiler=)` | when `None`, `QISKIT_TRANSPILER_SEED` or the `transpiler_seed` user-config entry applies, else the transpiler is unseeded | `qiskit/compiler/transpiler.py` | a QRNG-drawn value per [AGENTS.md](../../AGENTS.md) Seeds | two seeds giving different CZ counts, which makes the seed part of the record | verified |
| `transpile(num_processes=)` | process count for multi-circuit transpiles; `QISKIT_NUM_PROCS` and `QISKIT_PARALLEL` also read | signature of `transpile`; `grep` of `qiskit/` for `QISKIT_` | 1 inside a `parallel.py` worker | wall time of a 100-circuit transpile at 1 and 6 processes | verified, unmeasured |
| `QISKIT_SABRE_ALL_THREADS` | Sabre uses all threads | name present in `qiskit/` sources; behavior unread | leave unset | unverified | unverified |
| `AerSimulator(method=)` | `automatic`, `statevector`, `density_matrix`, `stabilizer`, `matrix_product_state`, `extended_stabilizer`, `unitary`, `superop`, `tensor_network` | `AerSimulator().available_methods()` | `statevector` for dynamic circuits of 7 active qubits under noise; `density_matrix` only as the cross-check | [simulation-cost-levers.md](simulation-cost-levers.md): statevector restricted 3.4 ms per shot, density_matrix restricted 181 ms per shot | verified, measured there |
| `device` | `CPU` or `GPU` | `available_devices()` | `CPU` below 20 qubits | GPU lost at 7 qubits (54.6 against 36 ms per shot, [substrates.md](../notes/kaggle/substrates.md)); cuStateVec won 1.25x at 20 qubits and 1.18x at 26 ([custatevec.md](../notes/build_host/custatevec.md)) | verified, measured there |
| `cuStateVec_enable` | cuStateVec path on GPU; raises with `batched_shots_gpu=True` per the build-host note | `AerSimulator` options; [custatevec.md](../notes/build_host/custatevec.md) | on only at 20 qubits or more | the 1-qubit if_else circuit costs 2x per shot with it | verified, measured there |
| `max_parallel_threads` | OpenMP core cap; 0 means all cores | docstring in `qiskit_aer/backends/aer_simulator.py` | `GOROROBA_WORKERS` for the job; 1 inside a pool worker (`aer_delay_sentinels.py` uses 1) | per-shot time at 1, 6 and 12 threads on a 20-qubit statevector | verified, unmeasured |
| `max_parallel_experiments` | experiments in parallel up to the thread cap; 0 means the cap; the docstring states default 1 | same docstring | 0 for a batch of many circuits ([simulation-cost-levers.md](simulation-cost-levers.md) keeps it within one call because seeds are positional) | bit-identity of counts against the serial call | verified |
| `max_parallel_shots` | shots in parallel; the docstring says it cannot run beside parallel experiments | same docstring | 1 for seed-stable single-circuit calls (`calibration_snapshot.py` sets it) | counts that change with the thread count | verified |
| `statevector_parallel_threshold` | qubit count above which one statevector uses OpenMP; default 14 | docstring and `AerSimulator().options` | default | time per gate at 13 to 16 qubits at 1 and 6 threads | verified, unmeasured |
| `fusion_enable`, `fusion_max_qubit`, `fusion_threshold` | gate fusion; statevector defaults 5 and 14, density_matrix 2 and 7 | table in the `AerSimulator` docstring | defaults | circuit time with fusion off and `fusion_max_qubit` 3 to 6 | verified, unmeasured |
| `precision` | `double` default | `AerSimulator().options` | `double` for any record | none; single precision changes bits | verified |
| `seed_simulator` | circuit `k` of one run draws seed `seed_simulator + 2113 k` | [simulation-cost-levers.md](simulation-cost-levers.md) (Aer source cited there) | one Aer call per planning choice | changed counts when choices merge into one batch | verified there |
| `max_memory_mb` | state-memory cap; an error when exceeded | docstring | leave unset beside a cgroup `MemoryMax` | none | verified |
| `enable_truncation` | drops qubits that do not affect the outcome; default True | docstring | default | n/a | verified |
| shot branching | drops a mid-circuit measurement's readout channel | [simulation-cost-levers.md](simulation-cost-levers.md) | never enabled | n/a | measured there |
| `exqalibur`, `samplomatic`, `qiskit-ibm-runtime` 0.50.0 | Rust extensions and the client-side Sampler | [AGENTS.md](../../AGENTS.md) Qiskit skills | follow the migrate skill | n/a | no knob read |

## numpy, scipy, threadpoolctl

Uses: every module; `threadpoolctl` in `ci/runner_specs.py` and
`scripts/numerics_fingerprint.py` to record the loaded BLAS.

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `OPENBLAS_NUM_THREADS` | OpenBLAS threads, identical on the host, Kaggle, Azure and CI | `threadpoolctl` reports the value | 1 inside `parallel.py` workers; physical cores (6 on the host, 2 on a Standard_FX4mds_v2, 2 on Kaggle) for one large dense call | the BLAS rows of compute-flags.md Measured combinations | measured on the host |
| `threadpoolctl.threadpool_limits(limits=, user_api=)` | runtime thread bound per API | `threadpoolctl` 3.7.0 module; used in `ci/runner_specs.py` | bound inside a function instead of mutating the environment | none | verified |
| `NPY_DISABLE_CPU_FEATURES` | numpy dispatch mask; `ci/run_gates.py` sets it for CI-written records | `scripts/numerics_fingerprint.py`, `ci/run_gates.py` | set it exactly as `ci/run_gates.py` does when replaying a CI record | a replay bit mismatch without it | verified use |
| `NPY_PROMOTION_STATE` | accepted only as `weak` in numpy 2.5 | `numpy/__init__.py` line 913 | leave unset | a numpy that accepts another value | verified |
| `scipy.optimize.linprog(method=)` | `highs` is the default | `scipy/optimize/_linprog.py` | `highs` | n/a | verified |
| `linprog(method='simplex')` | the installed 1.18.1 emits a DeprecationWarning that says removal in 1.11.0 and still runs | executed under `timeout` | never use | n/a | verified |
| `scipy.optimize.minimize(method=)` | the repository uses `L-BFGS-B` 14 times, `Nelder-Mead` 5 and `bounded` 6 (scalar) | `grep` of `gororoba_quantum`, `scripts` | keep the method named in the call; pass `options={'maxiter'}` for long fits | iteration count against the bound | verified use |
| `scipy.linalg.expm`, `eigh`, `svd` | OpenBLAS-backed; no thread argument | `scipy.show_config()` | bound threads through `OPENBLAS_NUM_THREADS` | none | verified |

## JAX 0.9.0 and torch 2.14.1

Uses: `gororoba_quantum/jax_bridge.py`, `branch_dm.py`, `kaggle_kernel/kernel_main.py`,
`scripts/jax_bridge_sweep.py`; torch only in optional package checks
(`scripts/box_kite_packages.py`).

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `JAX_ENABLE_X64` | 64-bit types; default False in this install | `jax.config.jax_enable_x64` returns False; name in `jax/_src/config.py` | `1` for any record compared to complex128 numpy; `jax_bridge` stores complex64 by default ([simulation-cost-levers.md](simulation-cost-levers.md)) | agreement with numpy complex128 at 1e-12 versus complex64 error | verified |
| `JAX_PLATFORMS` | restricts platforms | name in `jax/_src/config.py` | `cpu` locally, where jaxlib has no CUDA | a CUDA jaxlib build | verified |
| `JAX_DEFAULT_MATMUL_PRECISION` | matmul precision level; `jax_bridge.py` passes `precision=highest` to einsum | `jax/_src/config.py`; `jax_bridge.py` line 471 | leave the in-code `highest` | error against a numpy reference | verified |
| `JAX_DISABLE_JIT`, `JAX_DEBUG_NANS`, `JAX_ENABLE_COMPILATION_CACHE`, `JAX_COMPILATION_CACHE_DIR`, `JAX_NUMPY_DTYPE_PROMOTION` | names present | `jax/_src/config.py` | cache dir under `~/.cache/gororoba-quantum` for repeated sweeps | compile time of a repeated sweep | name verified, unmeasured |
| `XLA_FLAGS` | XLA options, for example host device count | not read in this install; no repository use | unverified | unverified | unverified |
| `torch.set_num_threads` | intra-op threads; the default is 6 on this host | `torch.get_num_threads()` | match `GOROROBA_WORKERS` | none | verified |
| `CUDA_VISIBLE_DEVICES` | GPU selection, read by the CUDA runtime | an empty value gives `torch.cuda.device_count()` 0, unset gives 1 (RTX 4070 Ti) | unset on the host; `0` or `0,1` on a Kaggle T4 x2 | a run whose device count differs from the value | verified |

JAX measurement: the restructured sweep cut CPU time from 1389 s to 22 s on 105
replicas ([jax-bridge-structure-report.md](../notes/kaggle/jax-bridge-structure-report.md)).

## CUDA across substrates

| Substrate | GPU | CUDA | Aer GPU path |
|---|---|---|---|
| Build host | RTX 4070 Ti, 12 GiB, compute capability 8.9, driver 615.78 | runtime 13.4 | `python-qiskit-aer-cuda` 0.17.2-3: devices `CPU` and `GPU`, links cuStateVec and cuTensorNet |
| Kaggle | T4 x2 (compute 7.5) or P100 (6.0) on a GPU kernel | the image's CUDA | the Kaggle Aer wheel; [kaggle notes](../notes/kaggle/README.md) record CPU beating T4 on small dynamic circuits |
| Azure FX4mds_v2 | none | none | CPU only |

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `AerSimulator(device="GPU")` | statevector or density matrix on CUDA | `available_devices()` lists `GPU`; a Bell circuit gives identical counts on CPU and GPU at one seed | GPU for 25 or more statevector qubits on the host; CPU below | the crossover in [custatevec.md](../notes/build_host/custatevec.md) | measured in that note |
| `cuStateVec_enable` | cuStateVec kernels instead of Thrust (default False) | `AerSimulator().options` | True on the host build | cuStateVec slower than Thrust at the same width | verified, see custatevec.md |
| `batched_shots_gpu`, `batched_shots_gpu_max_qubits` | batch shots of noisy runs on the GPU (defaults False, 16) | options | True for noisy sampling at 16 qubits or fewer | batched slower than unbatched at equal shots | verified, unmeasured |
| `blocking_enable`, `blocking_qubits` | split a statevector across chunks or GPUs (defaults False, None) | options | off on one 12 GiB card below 29 qubits | a width that fits only with blocking | verified, unmeasured |
| `precision` | `double` default, `single` halves memory | options | `double` for evidence; `single` only for a scan whose tolerance is stated | a single-precision result differing beyond the tolerance | verified |
| `target_gpus` | not an option in Aer 0.17.2 | absent from `AerSimulator().options` | use `CUDA_VISIBLE_DEVICES` | | verified absent |

## sympy 1.14.0, python-flint 0.9.0, mpmath 1.4.1, numba 0.68.0

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `SYMPY_USE_CACHE` | `yes` (default), `no` or `debug` | `sympy/core/cache.py` | `yes` | memory growth in a long symbolic loop | verified |
| sympy ground types | `sympy.external.gmpy.GROUND_TYPES` reports `flint` on this host | executed | keep flint | time of a `Poly` factorization under `SYMPY_GROUND_TYPES=python` | name unverified, backend verified |
| `flint.ctx.threads` | threads for FLINT parallel routines; default 1, settable | executed (`flint.ctx.threads = 2` read back 2) | 1 beside a Singular job; the free core count alone | time of a large `fmpz_mpoly` or `fmpz_mat` product at 1 and 4 threads | verified, unmeasured |
| `flint.ctx.prec`, `dps`, `cap` | arb/acb precision (53), digits, series cap (10) | `flint.ctx` attributes | set `prec` explicitly per computation | certified ball width | verified |
| mpmath backend | `gmpy` | `mpmath.libmp.BACKEND` | keep | time against the `python` backend | verified |
| `NUMBA_NUM_THREADS`, `NUMBA_THREADING_LAYER`, `NUMBA_CACHE_DIR`, `NUMBA_DISABLE_JIT`, `NUMBA_OPT`, `NUMBA_CPU_NAME` | numba configuration | names in `numba/core/config.py` | none in use; [simulation-cost-levers.md](simulation-cost-levers.md) rejects numba for `dynamic_density` | n/a | name verified; no repository import found in imports scan |

## cvxpy 1.9.3, networkx 3.7, rustworkx 0.18.1, matplotlib 3.11.2

| Knob | Meaning | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|
| `problem.solve(solver=)` | installed solvers: CLARABEL, SCS, ECOS, GLPK, GLPK_MI, CBC, CVXOPT, SCIP, SCIPY, HIGHS, CUCLARABEL, ECOS_BB, PDCS, OSQP | `cvxpy.installed_solvers()` | `CLARABEL`, the value of `SOLVER` in `scripts/qd_classical_benchmark.py` | status and objective of the same problem under SCS and HIGHS | verified, unmeasured |
| `cvxpy.settings.NUM_THREADS` | compile threads; -1 follows `OMP_NUM_THREADS` | `cvxpy/settings.py` | leave -1 | none | verified |
| `CVXPY_DEFAULT_TO_COMMERCIAL_SOLVERS` | boolean environment switch | `cvxpy/settings.py` | leave default; no commercial solver is installed | n/a | verified |
| networkx `NETWORKX_CACHE_CONVERTED_GRAPHS` | backend graph cache | `networkx/utils/backends.py` | default | n/a | verified |
| rustworkx | Rust threads follow `RAYON_NUM_THREADS` (set to 1 in pool workers) | `parallel.py` | as pool | n/a | variable verified in repo; rustworkx read unverified |
| matplotlib backend | installed default `qtagg` | `matplotlib.get_backend()` | `MPLBACKEND=Agg` | n/a | verified |

## Algebra and hypercomplex packages (one group)

`Cayley_Calculator` 1.3.1, `cayley-dickson` 0.1.0, `clifford` 1.5.1, `galgebra`
0.6.0, `hypercomplex` 0.3.4, `hypercomplex-algebra` 0.2.0.2, `hypercomplex-engine`
0.5.0, `hyprat` 0.2.0, `kingdon` 3.0.0, `numpy-quaternion` 2024.0.13,
`octonion` 0.1.0, `pyoctonion` 3.12, `pyquaternion` 0.9.9, `pyadic` 0.3.0,
`quaternionic` 1.0.18, `SplitOct` 0.16, `sagemath` 10.10 and `spglib`. They run
in `docs/` and `scripts/` as cross-checks of `cd_core.py`, the specification; a
package result enters evidence only through a declared map checked on every
basis pair. None carries a performance knob the repository sets. Their numeric
paths call numpy, so `OPENBLAS_NUM_THREADS` governs them. Per-package options:
unverified. Recommended setting: one process per package under
`GOROROBA_WORKERS`; falsifier: any pair where the package product differs from
`cd_core`; status unmeasured.

## Other imports

| Package | Version | Use | Knob |
|---|---|---|---|
| `perceval-quandela` | 1.3.1 | Quandela circuits and serialization (`scripts/ascella_*.py`) | none read; `QD_PYTHON` names the MCP interpreter |
| `kaggle`, `kagglesdk` | 2.2.5, 0.1.38 | kernel push and collect (`scripts/kaggle_run.py`) | `--timeout` per [gpu-runbook.md](../notes/kaggle/gpu-runbook.md) |
| `pillow`, `requests`, `pydantic`, `anyio`, `mcp`, `playwright`, `selenium`, `platformdirs`, `pytest` | 13.0.0, 2.34.2, 2.14.1, 4.15.1, 1.29.0, 1.64.0, 4.44.0, 4.13.0, 9.1.1 | tooling and tests | no performance knob read |

## Provider-venv modules (versions not read)

The system `python3` lacks these; each lives in the provider interpreter named
in [AGENTS.md](../../AGENTS.md) Hardware services.

| Module | Venv |
|---|---|
| `quantuminspire`, `qiskit_quantuminspire`, `pennylane_quantuminspire`, `qi2_shared`, `cqasm`, `opensquirrel`, `qxelarator` | `QI_PYTHON` (Quantum Inspire venv `QI_ENV`) |
| `openquantum_sdk`, `openquantum_mcp` | `OQ_PYTHON` (venv `OQ_ENV`) |
| `pennylane`, `qiskit_algorithms`, `qiskit_nature`, `seekpath`, `gamma_mod`, `sedenion` | no interpreter named in AGENTS.md; used in `docs/` and `scripts/` |

## Executables

| Tool | Version | Knob | Verified by | Recommended | Falsifier | Status |
|---|---|---|---|---|---|---|
| Singular | 4.4 | `--cpus=N`, `--threads=N`, `--flint-threads=N`, `--min-time`, `-q`, `--no-warn`, `-r SEED` | `Singular --help` | `--flint-threads=1` and `--cpus=1` for the process-per-item model of [compute-flags.md](compute-flags.md) | `std`/`eliminate` time at `--flint-threads` 1 and 4 | verified, unmeasured |
| msolve | 0.11.0 on the system `PATH`; compute-flags.md measured 0.10.1 | `-t`, `-v`, `-g`, `-c`, `-d`, `-e`, `-l`, `-m`, `-q`, `-r`, `-s`, `-u` | `msolve -h` | flags and caps in [compute-flags.md](compute-flags.md); rerun the measured row on 0.11.0 before reusing its numbers | the Rees elimination row at 0.10.1 and 0.11.0 | verified, version differs from the runbook |
| Macaulay2 | `M2` binary | `--no-threads`, `--silent`, `--stop`, `--no-prompts`, `-q`, `--script`, `--no-randomize`, `--read-only-files`, `-e`; environment `GC_INITIAL_HEAP_SIZE`, `GC_NPROCS` | `M2 --help` | `--script` for batch runs (implies `--stop`, `--silent`, `-q`); `--no-threads` beside other jobs | wall time with and without `--no-threads` on a Groebner basis | verified, unmeasured |
| FLINT | 3.6.0 (system library behind python-flint) | thread count through `flint.ctx.threads` | `pacman -Q flint`; executed | see python-flint row | see above | verified, unmeasured |
