# Least-squares precision of the Ascella CZ tomography prediction

The ensemble case's estimate 5 compares its scores with a prediction from the retained two-run tomography fit
([design](../../design/ascella-cz-compilation-ensemble-case.md)). The prediction is a least-squares problem: a
576 x 256 design matrix A (condition number 31.2, smallest singular value 0.219) maps the 256 Hermitian Choi
coefficients to the 576 observed outcome rates, solved for the point rates and 500 bootstrap replicates, then mapped
to 32 predicted rates, the table scores F and F', the process fidelity and the bootstrap summaries. This directory
measures how many bits of those outputs each arithmetic gets right, and why the producer now computes them in
certified arb ball arithmetic.

## Finding

The float64 producer (`numpy.linalg.pinv`, then a Choi matrix and a trace per setting) scored 48.7 on the precision
score defined below at one OpenBLAS thread, the runner-image ledger's setting, and its last bits moved with the thread
count: thread counts 1, 2, 4, 6 and 10 gave four different records, up to 1.1e-15 apart, scoring 47.8 to 48.8, and
the ledger bytes equalled the one- and two-thread record ([producer-records/](producer-records/), recorded from the
producer's commit by [producer_record.py](producer_record.py) and scored in [producer-scores.json](producer-scores.json)
by [score_producer.py](score_producer.py)). Near-zero wrong-outcome rates showed 1,000 to 3,000 ulp of error, which is
cancellation at 1e-17 absolute, not instability. The forecast gate's absolute tolerance of 1e-12 absorbed all of it.
The float64 pinv rows of the sweep evaluate the solved coefficients through a precomputed rate matrix, a
reassociation of the producer's traces, so they score 48.6 with other per-quantity errors (ZX/F at 10.2 ulp against
the producer's 0.77) and rank the solvers rather than reproduce the producer.

`tomography_prediction` in `scripts/ascella_cz_ensemble_case.py` now solves the normal equations in python-flint
`arb_mat` at 128 bits (256 and 512 bits as fallbacks) and writes each float64 only when every point of its ball
rounds to that float64 under round-to-nearest. Each written value is therefore the correctly rounded exact value of
the producer's float64 inputs, and the solve and every step after it no longer depend on the BLAS or its thread
count: the prediction came out byte-identical at 1 and 10 FLINT threads and in the runner image, and certified at
128 bits. The inputs themselves (design matrix, rate observables, Hermitian basis, ideal Choi vector, observed rate
columns) still come from float64 libm and BLAS calls, so the record carries their SHA-256 digests under
`arithmetic.inputs_sha256`; the bytes match across hosts whose input digests match. All five digests agree on the
build host (Zen 3, numpy `X86_V3`, OpenBLAS Haswell core), in the runner image, and under Intel SDE 10.13.1
emulating Sapphire Rapids (`-spr`) and Ice Lake server (`-icx`) with numpy's AVX-512 loops dispatched, and on real
hardware: an Intel Xeon Platinum 8488C (Sapphire Rapids, AVX-512), an AMD Ryzen 9 7945HX (Zen 4, AVX-512) and an Arm
Neoverse N1, each exporting the inputs itself ("Results across hosts" below). AMD Zen 5 stays untested. `check_forecast` therefore removes the digests before its
float tolerance comparison and prints the inputs that moved, so an identity whose inputs differ by an ulp reports
them instead of failing.

## Reference and certificate

- Reference: arb normal equations at 256 bits, largest ball radius 9.4e-73 over every scored quantity.
- Corroboration: mpmath at 80 digits evaluates the normal-equation gradient A^T (A x - b) of the reference midpoints
  on four of the 501 columns: largest norm 7.9e-78, which gives a solution error near 1.7e-76 through
  ||x - x*|| <= ||g|| / sigma_min^2 with the float64 estimate sigma_min = 0.219; without a certified lower bound on
  sigma_min this corroborates the reference rather than proving it.
- The precision score below is 52 minus the base-2 logarithm of the worst error, in ulp of the float64 nearest the
  exact value, over F, F' and the process
  fidelity of the point fit and the F_sd and 2.5 and 97.5 percentiles of both tables.

## Sweep

Every configuration ran in its own `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` scope, one at a
time, twice; precision is deterministic per configuration and the time is the faster of the two solves (scoring
excluded). [sweep-checklist.md](sweep-checklist.md) is the filled compute-flags checklist. Other sessions' pytest
workers shared the 10 CPUs (load average 2 to 22, recorded per row), so the times rank the configurations only
roughly; the precision column does not depend on load. [sweep.jsonl](sweep.jsonl) holds every row,
[sweep-contended.jsonl](sweep-contended.jsonl) the float64 rows of the first pass at load 13 to 19, and
[fp-backends.json](fp-backends.json) the full-size five-backend run with the mpmath certificate.

| Configuration | Precision score | Worst rate error | Fastest solve (s) | Load average before |
|---|---|---|---|---|
| float64 pinv with rate-matrix evaluation, OpenBLAS threads 1 | 48.6 | 5.8e-18 | 0.50 | 2.3 |
| float64 pinv, OpenBLAS threads 2 | 48.6 | 5.8e-18 | 0.08 | 2.2 |
| float64 pinv, OpenBLAS threads 4 | 48.6 | 5.8e-18 | 0.53 | 2.1 |
| float64 pinv, OpenBLAS threads 6 | 48.6 | 5.8e-18 | 0.36 | 5.0 |
| float64 pinv, OpenBLAS threads 10 | 48.6 | 5.8e-18 | 1.84 | 7.8 |
| float64 numpy lstsq, OpenBLAS threads 1 | 48.8 | 7.3e-18 | 0.24 | 2.2 |
| float64 numpy lstsq, OpenBLAS threads 2 | 48.8 | 7.3e-18 | 0.38 | 2.1 |
| float64 numpy lstsq, OpenBLAS threads 4 | 48.8 | 7.3e-18 | 0.73 | 5.3 |
| float64 numpy lstsq, OpenBLAS threads 6 | 48.8 | 7.3e-18 | 1.82 | 6.1 |
| float64 numpy lstsq, OpenBLAS threads 10 | 48.8 | 7.3e-18 | 3.08 | 8.3 |
| float64 scipy lstsq gelsd, OpenBLAS threads 1 | 48.8 | 7.3e-18 | 3.83 | 7.6 |
| float64 scipy lstsq gelsd, OpenBLAS threads 4 | 48.8 | 7.3e-18 | 3.99 | 8.0 |
| float64 scipy lstsq gelsd, OpenBLAS threads 10 | 48.8 | 7.3e-18 | 3.64 | 7.8 |
| float64 scipy lstsq gelss, OpenBLAS threads 1 | 47.2 | 7.7e-18 | 8.94 | 10.9 |
| float64 scipy lstsq gelss, OpenBLAS threads 4 | 47.2 | 7.7e-18 | 5.00 | 14.3 |
| float64 scipy lstsq gelss, OpenBLAS threads 10 | 47.2 | 7.7e-18 | 5.61 | 13.9 |
| float64 scipy lstsq gelsy, OpenBLAS threads 1 | 49.9 | 4.8e-18 | 1.60 | 9.1 |
| float64 scipy lstsq gelsy, OpenBLAS threads 4 | 49.9 | 4.8e-18 | 1.67 | 9.1 |
| float64 scipy lstsq gelsy, OpenBLAS threads 10 | 49.9 | 4.8e-18 | 1.85 | 8.3 |
| float64 pinv + 1 x87 refinement step | 51.5 | 3.0e-19 | 6.88 | 12.9 |
| float64 pinv + 2 x87 refinement steps | 51.6 | 3.1e-19 | 7.59 | 13.2 |
| float64 pinv + 3 x87 refinement steps | 51.5 | 3.2e-19 | 15.22 | 21.7 |
| x87 Householder, 1 worker processes | 59.5 | 5.7e-21 | 1.01 | 12.0 |
| x87 Householder, 2 worker processes | 59.5 | 5.7e-21 | 0.87 | 11.2 |
| x87 Householder, 4 worker processes | 59.5 | 5.7e-21 | 0.80 | 10.2 |
| x87 Householder, 6 worker processes | 59.5 | 5.7e-21 | 0.73 | 10.6 |
| x87 Householder, 8 worker processes | 59.5 | 5.7e-21 | 0.62 | 10.1 |
| x87 Householder, 10 worker processes | 59.5 | 5.7e-21 | 0.67 | 9.5 |
| x87 normal equations (Cholesky) | 57.2 | 8.8e-21 | 0.62 | 9.1 |
| binary128 Householder, backend sleef, QuadBLAS threads 1 | 108.1 | 2.0e-35 | 10.72 | 8.1 |
| binary128 Householder, backend sleef, QuadBLAS threads 4 | 108.1 | 2.0e-35 | 10.56 | 5.7 |
| binary128 Householder, backend sleef, QuadBLAS threads 10 | 108.1 | 2.0e-35 | 10.90 | 4.7 |
| binary128 normal equations, backend sleef, QuadBLAS threads 1 | 109.7 | 2.9e-36 | 8.28 | 6.4 |
| binary128 normal equations, backend sleef, QuadBLAS threads 4 | 109.7 | 2.9e-36 | 8.38 | 4.8 |
| binary128 normal equations, backend sleef, QuadBLAS threads 10 | 109.7 | 2.9e-36 | 8.41 | 3.8 |
| quaddtype longdouble backend (x87) Householder, QuadBLAS threads 1 | 59.8 | 6.2e-21 | 2.63 | 22.3 |
| quaddtype longdouble backend (x87) Householder, QuadBLAS threads 4 | 59.8 | 6.2e-21 | 3.90 | 17.8 |
| quaddtype longdouble backend (x87) Householder, QuadBLAS threads 10 | 59.8 | 6.2e-21 | 2.41 | 16.8 |
| quaddtype longdouble backend (x87) normal equations, QuadBLAS threads 1 | 57.2 | 8.8e-21 | 2.37 | 20.2 |
| quaddtype longdouble backend (x87) normal equations, QuadBLAS threads 4 | 57.2 | 8.8e-21 | 1.84 | 17.7 |
| quaddtype longdouble backend (x87) normal equations, QuadBLAS threads 10 | 57.2 | 8.8e-21 | 3.04 | 16.7 |
| arb normal equations, 64 bits, FLINT threads 1 | 56.7 | 2.8e-21 | 1.85 | 4.3 |
| arb normal equations, 64 bits, FLINT threads 4 | 56.7 | 2.8e-21 | 0.87 | 4.0 |
| arb normal equations, 64 bits, FLINT threads 10 | 56.7 | 2.8e-21 | 0.77 | 3.8 |
| arb normal equations, 128 bits, FLINT threads 1 | 120.7 | 2.3e-40 | 2.60 | 3.8 |
| arb normal equations, 128 bits, FLINT threads 4 | 120.7 | 2.3e-40 | 1.04 | 4.4 |
| arb normal equations, 128 bits, FLINT threads 10 | 120.7 | 2.3e-40 | 0.91 | 4.4 |
| arb normal equations, 192 bits, FLINT threads 1 | 184.8 | 7.1e-60 | 3.20 | 4.4 |
| arb normal equations, 192 bits, FLINT threads 4 | 184.8 | 7.1e-60 | 1.39 | 4.2 |
| arb normal equations, 192 bits, FLINT threads 10 | 184.8 | 7.1e-60 | 1.22 | 4.2 |
| arb normal equations, 256 bits, FLINT threads 1 | reference | 0.0e+00 | 2.24 | 4.2 |
| arb normal equations, 256 bits, FLINT threads 4 | reference | 0.0e+00 | 1.28 | 4.7 |
| arb normal equations, 256 bits, FLINT threads 10 | reference | 0.0e+00 | 1.18 | 5.0 |

- float64: the LAPACK driver sets the score (gelsy, pivoted QR, 49.9; gelss 47.2); threads change only the last bits
  and the time.
- x87 80-bit: numpy `longdouble` (64-bit significand) Householder QR scores 59.5 in about 0.6 s, the fastest
  configuration that beats float64; it exists only on x86 (ARM's `long double` is binary128, MSVC's is float64).
- binary128 (numpy-quaddtype 1.0.0, SLEEF backend) scores 108 to 110 in 8 to 11 s; QuadBLAS threads change
  nothing at this size. Its `longdouble` backend is x87 arithmetic under the quad dtype's name (57 to 60).
- arb: 128 bits scores 120.7 with a rigorous radius in 0.9 s on 10 FLINT threads (2.6 s on one), faster than
  binary128 and with an error bound; python-flint 0.9.0 is already an arithmetic pin of the runner image.

## Library defects found

- numpy-quaddtype 1.0.0, the only release (2026-01-23), has two matmul defects in its QuadBLAS path.
  [quad_matmul_falsify.py](quad_matmul_falsify.py) multiplies small-integer matrices, whose products are exact in
  float64 and binary128, so the float64 product is an exact oracle compared in the quad dtype, and runs six
  non-contiguous view cases (sub-block, transpose, reversed and every-other-row strides), a contiguous control and two
  empty inner dimensions. Its per-machine records are in [quad-falsification/](quad-falsification/):

  | Machine | OS | CPU | Build | QuadBLAS | View cases | Empty inner dimension |
  |---|---|---|---|---|---|---|
  | build host | CachyOS (capsule) | Ryzen 5 5600X3D, Zen 3, AVX2 | source build and PyPI wheel | enabled | 6 of 6 wrong | raises |
  | ALIENWARE | WSL Ubuntu 26.04 | Ryzen 9 7945HX, Zen 4, AVX-512 | PyPI wheel | enabled | 6 of 6 wrong | raises |
  | Vostro | CachyOS | Turion 64 X2 TL-66, SSE3, no AVX | PyPI wheel on CachyOS numpy 2.5.3 | enabled | 6 of 6 wrong | raises |
  | MacBook Air | macOS 27.0 | Apple M1, arm64 | PyPI wheel | enabled | 6 of 6 wrong | raises |
  | ALIENWARE | Windows 11 | Ryzen 9 7945HX | PyPI wheel | disabled | all correct | returns zeros |
  | build host | CachyOS (capsule) | Ryzen 5 5600X3D | upstream `main` 888042c (QBLAS 1.5.0) | enabled | all correct | returns zeros |

  The contiguous control is correct everywhere. What survives across four CPUs, three operating systems, both builds
  and both instruction-set families: with QuadBLAS enabled, matmul with any non-C-contiguous operand returns wrong
  products without an error, and matmul with an empty inner dimension raises `RuntimeError: QBLAS operation failed`;
  the same inputs are correct on the Windows wheel, which disables QuadBLAS, so both defects belong to the QuadBLAS
  path, not to the dtype. Upstream issue numpy/numpy-quaddtype#89 reports the non-contiguous case and PR #108 (merged
  2026-07-16) fixes it; at `main` 888042c, `src/csrc/umath/matmul.cpp` sends a zero dimension or a stride QuadBLAS
  cannot take to a naive strided loop and gathers other strided operands into contiguous copies. No release carries
  those fixes (`main` still declares version 1.0.0 and the repository has no 1.x branch); a source build of `main`
  passes all six view cases and both empty inner
  dimensions on the build host, and its own suite passes there (8313 tests). `fp_backends.mm` multiplies contiguous
  copies and handles the empty case.
- numpy-flint-arb 1.5.4 maps matmul element by element over object arrays; peak memory grew about tenfold per
  doubling of the matrix side (50 MiB at 12 x 6, 1.1 GiB at 96 x 48; [nfa_scaling.py](nfa_scaling.py)), and an
  uncapped run on the 576 x 256 design reached 29.8 GB before it was stopped. The sweep excludes it.

## Reproduce

The study runs under the system Python, where gororoba-infrastructure `packaging/` installs numpy-quaddtype and
numpy-flint-arb; the exporter runs under the repository's `$PYTHON`.

```sh
"$PYTHON" docs/evidence/least-squares-precision/fp_export.py docs/local/fp-inputs.npz --host-label build-host
cd docs/evidence/least-squares-precision
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 "$PYTHON" -u fp_backends.py ../../local/fp-inputs.npz ../../local/fp-backends.json --mpmath
"$PYTHON" -u fp_sweep.py ../../local/fp-inputs.npz ../../local/sweep.jsonl 2 --host-label build-host
```

The `sweep.jsonl` rows above predate the portable sweep and carry no host record; [hosts/](hosts/) holds the portable
rows.

## Portable sweep across hosts

`fp_sweep.py` runs unchanged on any host that holds `fp_host.py`, `fp_backends.py`, `gororoba_quantum/parallel.py`
(standard library only) and the inputs file, in the layout of this repository. [hosts/](hosts/) holds the rows;
[hosts/sweep-checklist.md](hosts/sweep-checklist.md) is the compute-flags checklist.

- Memory cap: `min(8 GiB, 0.6 x physical memory)`. `fp_host.choose_cap` starts a trial `systemd-run --user --scope -p
  MemoryMax=N -p MemorySwapMax=0` and reads `memory.max` and `memory.swap.max` back from the scope's cgroup, because
  systemd accepts the properties without a delegated memory controller. A host without a working user manager (WSL
  without systemd, macOS) falls to `RLIMIT_AS` in the child, held at 2 GiB or more because OpenBLAS reserves address
  space at import (`prlimit --as` runs of the build-host stack fail at 1 GiB and pass at 2 GiB); the probe records
  whether a mapping above the cap is refused. Native Windows runs uncapped. `--cap auto|systemd|rlimit|none` forces
  a mechanism.
- Threads: 1, 2, 4, ... up to `min(os.cpu_count(), parallel.workers())`, plus that count when it is not a power of two.
- Skips: x87 rows need an x86 CPU and `numpy.finfo(numpy.longdouble).nmant == 63`; the quaddtype `longdouble`-backend
  rows are x87 rows under the quad dtype's name; quaddtype rows need the wheel and an enabled QuadBLAS
  (`fp_host.quadblas_status` calls `numpy_quaddtype.get_quadblas_version()`, which raises `NotImplementedError` where
  the wheel disables QuadBLAS, as `numpy_quaddtype.set_num_threads` does in every quaddtype configuration). A skipped
  configuration is a row with a `skipped` reason, so every host's grid aligns.
- Row additions: `host` (label, machine, OS family, CPU model, numpy `__cpu_features__` subset, numpy SIMD baseline
  and dispatch lists, BLAS runtime through threadpoolctl, package versions), `cap`, `mode`, `idle_wait`,
  `load_average_before`, `knobs`, `inputs_sha256` and `inputs_provenance`. The old fields keep their names. The host
  record is a public substrate profile; the exact kernel release, the distribution string and the memory size stay
  out of the rows, and the infrastructure chart in the private gororoba-infrastructure repository holds the host
  facts behind each label.
- Input digests: `fp_host.input_digests` rebuilds the five `arithmetic.inputs_sha256` digests from the arrays;
  `fp_export.py` stores the producer's own digests in the npz, and `matches_producer_digests` compares them. On the
  build host all five equal the digests retained in `results/quandela/cases/ascella_cz_ensemble/forecast.json`. A
  host that receives the npz reports the exporting host's digests; a host that runs `fp_export.py` itself reports
  digests of its own libm and BLAS results.
- `--idle-wait` starts each run only when the 1 minute load average is below 0.5 x `os.cpu_count()` (exit 3 after
  `--idle-timeout` seconds; native Windows has no load average and the wait is a recorded no-op). `--quick` keeps one
  thread count per family (`min(cpus, 4)`), the three scipy drivers, two refinement steps, arb at 128 bits and one
  repeat.

Interpreter: the new files use no syntax newer than Python 3.10 by inspection and ran on 3.14.9 only; use 3.13 or
later on remote hosts. The pins below are the build host's versions; PyPI wheel availability of numpy, scipy and
python-flint on Windows, macOS arm64 and Linux aarch64 is unchecked, and only the numpy-quaddtype 1.0.0 wheels are
evidenced above. Install into a venv:
`numpy==2.5.4 scipy==1.18.1 python-flint==0.9.0 numpy-quaddtype==1.0.0 threadpoolctl==3.7.0`.

```sh
# Linux x86_64, Linux aarch64, macOS arm64 (POSIX sh); run from the directory that holds docs/ and gororoba_quantum/
PYTHON=${PYTHON:-python3}
"$PYTHON" -m venv "$HOME/fp-venv" && PYTHON="$HOME/fp-venv/bin/python"
"$PYTHON" -m pip install numpy==2.5.4 scipy==1.18.1 python-flint==0.9.0 numpy-quaddtype==1.0.0 threadpoolctl==3.7.0
D=docs/evidence/least-squares-precision
"$PYTHON" -u $D/fp_sweep.py fp-inputs.npz $D/hosts/LABEL-full.jsonl --host-label LABEL --idle-wait
"$PYTHON" -u $D/fp_sweep.py fp-inputs.npz $D/hosts/LABEL-quick.jsonl --host-label LABEL --quick   # 1 GiB hosts
```

```powershell
# Windows native (PowerShell); fp_export.py cannot run here because the producer imports fcntl, so copy fp-inputs.npz
$env:PYTHON = "C:\Path\To\python.exe"
& $env:PYTHON -m venv "$env:USERPROFILE\fp-venv"; $env:PYTHON = "$env:USERPROFILE\fp-venv\Scripts\python.exe"
& $env:PYTHON -m pip install numpy==2.5.4 scipy==1.18.1 python-flint==0.9.0 numpy-quaddtype==1.0.0 threadpoolctl==3.7.0
$D = "docs\evidence\least-squares-precision"
& $env:PYTHON -u "$D\fp_sweep.py" fp-inputs.npz "$D\hosts\LABEL-full.jsonl" --host-label LABEL --cap none
```

A Linux or macOS host that should put its own libm and BLAS behind the input digests also installs `qiskit==2.6.2
sympy==1.14.0 rustworkx==0.18.1` and runs `"$PYTHON" $D/fp_export.py fp-inputs.npz --host-label LABEL` from a full
checkout before the sweep. Whether numpy-quaddtype publishes a Linux aarch64 wheel is unverified here; the sweep
skips its rows with the import error when none installs.

Host: AMD Ryzen 5 5600X3D capsule (10 CPUs visible, AVX2 and FMA, no AVX-512), OpenBLAS 0.3.34 (`Zen` core,
OpenMP), numpy 2.5.4 (baseline x86-64-v3), scipy 1.18.1, python-flint 0.9.0 on FLINT 3.6.0, mpmath 1.4.1,
numpy-quaddtype 1.0.0 built `-march=native -O3` (meson release, SLEEF 3.9.0 scalar FMA quad path, QuadBLAS 1.0.0).

## Results across hosts

Each host below ran `fp_sweep.py` on pinned wheels (numpy 2.5.4, scipy 1.18.1, python-flint 0.9.0, numpy-quaddtype
1.0.0) in a venv, one configuration at a time; the rows are in [hosts/](hosts/) under each label. A host that ran
`fp_export.py` itself compared its five input digests with the build host's.

| Label | CPU | OS | Own export: digests equal to the build host's | Full rows (skipped) |
|---|---|---|---|---|
| build-host | Ryzen 5 5600X3D, Zen 3 | Linux on WSL2 | reference | 74 (0) |
| zen4-wsl | Ryzen 9 7945HX, Zen 4, AVX-512 | Linux on WSL2 | 5 of 5 | 88 (0) |
| zen4-windows | Ryzen 9 7945HX | Windows 11 | not run: `fp_export.py` needs `fcntl` | 88 (22 x87 skipped, 12 QuadBLAS errors) |
| aws-sapphire-rapids | Xeon Platinum 8488C, AVX-512 | Linux on a cloud VM | 5 of 5 | 32 (0) |
| oci-a1-neoverse-n1 | Neoverse N1 | Linux aarch64 on a cloud VM | 5 of 5 | 32 (14: 8 quaddtype, 6 x87) |
| m1-macos | Apple M1 | macOS 27.0 | 4 of 5: `observed_rate_columns` differs | 60 (16 x87) |

- Arithmetic that bypasses the BLAS gives the same error on every host where it runs. The arb normal equations (all
  six hosts), binary128 through SLEEF (four hosts) and x87 (three x86 hosts under Linux) score identically to the
  last recorded digit. Every float64 configuration routes through the BLAS, and its error moves with the host.
  Unrefined float64 pinv scores 0.2 to 14.8 ulp on the process fidelity across the six hosts at one thread, and
  the scipy drivers 0.2 to 13.2. This measures the reason the producer computes in arb.
- The macOS difference is the bootstrap replicate array. The design matrix, rate observables, basis, ideal Choi
  vector and observed rates are identical bit for bit; 41,634 of the 288,000 replicate rates differ, by up to 6.4e-4,
  so the random-variate stream diverged rather than rounded. Hypothesis: numpy's binomial and Poisson samplers take
  accept-reject decisions through libm calls, and Apple's libm rounds some of them differently from glibc, which
  agrees on x86-64 and aarch64. Falsifier: the same numpy wheel drawing the producer's `resampled_rates` stream
  identically on macOS. Bootstrap intervals are reproducible across Linux hosts and not onto macOS.
- numpy-quaddtype is not installed on the Neoverse host (`ModuleNotFoundError`), so its rows skip quaddtype; whether a
  Linux aarch64 wheel exists is unverified. The Windows wheel disables QuadBLAS: the 12 SLEEF configurations (six
  thread counts, two kinds, two repeats each) are error rows there (`NotImplementedError: QuadBLAS is disabled`), a
  capability that `fp_host.quadblas_status` now probes, so a rerun on that wheel records skips. The retained rows
  predate the probe and stay as measured.
- numpy 2.5.4 dies with SIGILL on the Vostro's Turion 64 X2 (SSE3, no SSSE3, SSE4 or POPCNT), so the K8 host is not
  run in this sweep: its wheels need an x86-64 baseline that the CPU lacks.
- Times rank the hosts only within a row. The build host shared its CPUs with other sessions' Singular jobs (load 1.9
  to 5.7), and its float64 single-thread solves ran 10 to 20 times slower than the two-core cloud hosts. At one
  thread, arb at 128 bits took 0.77 s on the M1, 0.98 to 1.09 s on Zen 4 and Sapphire Rapids, and 2.5 to 3.2 s on the
  build host and the Neoverse N1.

