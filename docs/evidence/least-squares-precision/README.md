# Least-squares precision of the Ascella CZ tomography prediction

The ensemble case's estimate 5 compares its scores with a prediction from the retained two-run tomography fit
([design](../../design/ascella-cz-compilation-ensemble-case.md)). The prediction is a least-squares problem: a
576 x 256 design matrix A (condition number 31.2, smallest singular value 0.219) maps the 256 Hermitian Choi
coefficients to the 576 observed outcome rates, solved for the point rates and 500 bootstrap replicates, then mapped
to 32 predicted rates, the table scores F and F', the process fidelity and the bootstrap summaries. This directory
measures how many bits of those outputs each arithmetic gets right, and why the producer now computes them in
certified arb ball arithmetic.

## Finding

The float64 producer path (`numpy.linalg.pinv`) got 48.6 of float64's 53 bits right, and its last bits moved with the
OpenBLAS thread count: thread counts 1, 2, 4, 6 and 10 gave four different float64 results, up to 1.5e-15 apart, and
the runner-image ledger bytes equalled the one- and two-thread result. Near-zero wrong-outcome rates showed 1,000 to
3,000 ulp of error, which is cancellation at 1e-17 absolute, not instability. The forecast gate's absolute tolerance
of 1e-12 absorbed all of it.

`tomography_prediction` in `scripts/ascella_cz_ensemble_case.py` now solves the normal equations in python-flint
`arb_mat` at 128 bits (256 and 512 bits as fallbacks) and writes each float64 only when every point of its ball
rounds to that float64 under round-to-nearest. Each written value is therefore the correctly rounded exact value of
the producer's float64 inputs, whatever the host, BLAS or thread count: the prediction came out byte-identical at 1
and 10 FLINT threads and certified at 128 bits.

## Reference and certificate

- Reference: arb normal equations at 256 bits, largest ball radius 9.4e-73 over every scored quantity.
- Independent check: mpmath at 80 digits evaluates the normal-equation gradient A^T (A x - b) of the reference
  midpoints on four columns: largest norm 7.9e-78, so the solution error is at most 1.7e-76
  (||x - x*|| <= ||g|| / sigma_min^2).
- "Correct bits" below is 52 minus the base-2 logarithm of the worst error in float64 ulp over F, F' and the process
  fidelity of the point fit and the F_sd and 2.5 and 97.5 percentiles of both tables.

## Sweep

Every configuration ran in its own `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` scope, one at a
time, twice; precision is deterministic per configuration and the time is the faster of the two solves (scoring
excluded). [sweep-checklist.md](sweep-checklist.md) is the filled compute-flags checklist. Other sessions' pytest
workers shared the 10 CPUs (load average 2 to 22, recorded per row), so the times rank the configurations only
roughly; the precision column does not depend on load. [sweep.jsonl](sweep.jsonl) holds every row,
[sweep-contended.jsonl](sweep-contended.jsonl) the float64 rows of the first pass at load 13 to 19, and
[fp-backends.json](fp-backends.json) the full-size five-backend run with the mpmath certificate.

| Configuration | Correct bits | Worst rate error | Fastest solve (s) | Load average before |
|---|---|---|---|---|
| float64 pinv, OpenBLAS threads 1 | 48.6 | 5.8e-18 | 0.50 | 2.3 |
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

- float64: the LAPACK driver sets the bits (gelsy, pivoted QR, 49.9; gelss 47.2); threads change only the last bits
  and the time.
- x87 80-bit: numpy `longdouble` (64-bit significand) Householder QR gives 59.5 bits in about 0.6 s, the fastest
  configuration that beats float64; it exists only on x86 (ARM's `long double` is binary128, MSVC's is float64).
- binary128 (numpy-quaddtype 1.0.0, SLEEF backend) gives 108 to 110 bits in 8 to 11 s; QuadBLAS threads change
  nothing at this size. Its `longdouble` backend is x87 arithmetic under the quad dtype's name (57 to 60 bits).
- arb: 128 bits gives 120.7 bits with a rigorous radius in 0.9 s on 10 FLINT threads (2.6 s on one), faster than
  binary128 and with an error bound; python-flint 0.9.0 is already an arithmetic pin of the runner image.

## Library defects found

- numpy-quaddtype 1.0.0 matmul returns wrong products, without an error, when an operand is a strided view (2709
  instead of 5334 on an 8 x 6 example), and raises `RuntimeError: QBLAS operation failed` on an empty inner
  dimension where numpy returns zeros; [quad_view_matmul.py](quad_view_matmul.py) reproduces both, and
  `fp_backends.mm` multiplies contiguous copies.
- numpy-flint-arb 1.5.4 maps matmul element by element over object arrays; peak memory grew about tenfold per
  doubling of the matrix side (50 MiB at 12 x 6, 1.1 GiB at 96 x 48; [nfa_scaling.py](nfa_scaling.py)), and an
  uncapped run on the 576 x 256 design reached 29.8 GB before it was stopped. The sweep excludes it.

## Reproduce

The study runs under the system Python, where gororoba-infrastructure `packaging/` installs numpy-quaddtype and
numpy-flint-arb; the exporter runs under the repository's `$PYTHON`.

```sh
"$PYTHON" docs/evidence/least-squares-precision/fp_export.py docs/local/fp-inputs.npz
cd docs/evidence/least-squares-precision
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 python3 -u fp_backends.py ../../local/fp-inputs.npz ../../local/fp-backends.json --mpmath
python3 -u fp_sweep.py ../../local/fp-inputs.npz ../../local/sweep.jsonl 2
```

Host: AMD Ryzen 5 5600X3D capsule (10 CPUs visible, AVX2 and FMA, no AVX-512), OpenBLAS 0.3.34 (`Zen` core,
OpenMP), numpy 2.5.4 (baseline x86-64-v3), scipy 1.18.1, python-flint 0.9.0 on FLINT 3.6.0, mpmath 1.4.1,
numpy-quaddtype 1.0.0 built `-march=native -O3` (meson release, SLEEF 3.9.0 scalar FMA quad path, QuadBLAS 1.0.0).
