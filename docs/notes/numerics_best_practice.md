# Numerics: conditioning, precision, vectorization and runtime packages

This note collects the numerical rules the repository's measurements
support. Each rule names the record or gate that carries its evidence; a
rule marked *inferred* has no measurement behind it yet and names the probe
that would decide it.

## Least squares and conditioning

The [least-squares conditioning study](../evidence/lsq_conditioning/README.md)
(`scripts/lsq_conditioning_study.py`, gates core-489 and core-492) measures
2716 atlas fits against an exact `Fraction` solution and an independent
p-adic solution.

- **Solve with `np.linalg.lstsq` (SVD) or Householder QR, never the normal
  equations.** Normal equations square the condition number: on designs
  with kappa >= 1e4 they lose a median 25 times more accuracy than QR, and
  on a graded design at kappa = 2^25 they lose 1e8 times more. SVD and QR
  stay within 0.19 of `m n eps (kappa + kappa^2 rho)`, where
  `rho = ||r|| / (||A|| ||x||)`; the kappa^2 rho term belongs to the problem
  whenever the fit has a residual, and no solver removes it.
- **Equilibrate columns when their norms differ by orders of magnitude.**
  Scaling each column by a power of two to unit norm (`A D`, then
  `x = D y`) is exact in binary floating point and cut kappa a median 341
  times on the 854 designs whose column norms spread by 100 or more (Van der
  Sluis: unit-norm columns are within sqrt(n) of the optimal diagonal
  scaling). Householder QR is invariant under such scaling, so equilibration
  matters for the condition number a tolerance reads, not for QR's answer.
- **Collinearity is a model defect, not an arithmetic one.** The atlas
  `axis_tilt_plus_mean` model keeps kappa near 4.7e5 after equilibration
  (a 1.3 times gain), because its tilt block and lane constant are nearly
  collinear. Its folds turn a 1e-14 to 1e-13 substrate design difference
  into contrast moves of 1e-5 to 1e-3. The remedy is to drop or regularize
  the model, or bound its outputs by a sensitivity measured on its own
  design (#213); more digits change nothing.
- **Bound small components componentwise.** A normwise bound
  `eps kappa^2 max|x|` admits errors far larger than a small component;
  `atlas_coherent_families.compare()` uses a per-value rule, and the study
  measures every float64 value within 1.8e-4 of its tolerance of the exact
  solution.

## Precision

| Format | Significand | eps | Where it runs here |
|---|---|---|---|
| float32 / complex64 | 24 bits | 1.2e-7 | GPU storage in `jax_bridge` (matmuls at `Precision.HIGHEST`) |
| float64 / complex128 | 53 bits | 2.2e-16 | the default: numpy, AOCL-BLAS or OpenBLAS, Aer `precision="double"` |
| `np.longdouble` / `np.clongdouble` | 64 bits (x87 extended, stored in 128 bits) | 1.1e-19 | scalar x87 only: no SIMD, no BLAS or LAPACK; `einsum` accepts it |
| double-double | about 106 bits | about 1e-32 | software (pairs of float64 with error-free transformations) |
| IEEE binary128 | 113 bits | 1.9e-34 | software only on x86 (libquadmath, MPFR, mpmath) |
| `Fraction`, p-adic, mod p | exact | 0 | stdlib `fractions`, pyadic, python-flint, galois |

- **float64 is enough wherever sampling sets the error.** The n21 exact
  model agrees with Aer's exact density-matrix law to 1.2e-15
  ([cross-check](../evidence/n21_exact_model/README.md), core-487), and an
  80-bit `clongdouble` run of `dynamic_density` moves its laws by at most
  4.4e-16 while running 2 to 9 times slower; the run's statistical radii are
  about 1e-2. Aer accepts only `precision="double"` and `"single"`.
- **Extra precision reduces rounding by 2^-(p-53) and nothing else.** The
  study's emulated p-bit Householder QR (bit-identical to Python doubles at
  p = 53 and to x87 `np.longdouble` at p = 64) shows the predicted scaling at
  p = 64, 106 and 113 with no retained value moving.
- **Certificates use exact arithmetic, not wide floats.** Rank and nullity
  claims run in `Fraction`, modulo a prime (2^61 - 1), or p-adically with
  rational reconstruction (pyadic `rationalise`); two independent exact
  paths that agree (core-489's Fraction and p-adic solutions on all 2716
  designs) outrank any finite precision.
- **A total arithmetic replaces divide-and-check.**
  `gororoba_quantum/wheel_algebra.py` (core-493) implements the wheel of
  fractions over Q: 1/0 is infinity and 0/0 is bottom, so elimination on a
  singular symmetric positive semidefinite system returns bottom instead of
  raising. Bottom carries no kernel or consistency information; nullity
  still comes from exact rank.

## Vectorization in numpy

- **Express independent arithmetic as array operations.** Broadcasting,
  `np.einsum`, batched `@` over leading axes and `np.linalg` on stacked
  matrices run in compiled loops; a Python loop over array elements pays
  interpreter dispatch on every element.
- **Contract tensors with a planned order.** `np.einsum(..., optimize=True)`
  chooses a pairwise order; `dynamic_density` and `jax_bridge` precompute
  their subscript strings per qubit tuple, which keeps the plan out of the
  inner loop. For networks beyond a few tensors, opt_einsum or cotengra
  (both on the build host) find better orders.
- **Keep dtypes concrete.** Object arrays (Fractions, wheels, p-adics)
  run element by element in Python; keep them to exact certificates and
  small designs, and keep float work in float64 or complex128.
- **Reduce with the compiled kernels.** `np.bincount`, `np.add.at`,
  `np.cumsum` and boolean masks replace dictionary counting and
  accumulation loops over shots.
- **Allocate once.** Preallocate outputs, write with `out=`, and keep arrays
  C-contiguous along the axis a kernel reads.

## Parallelism and BLAS threads

`gororoba_quantum/parallel.py` runs independent items on a spawn process
pool sized to the CPUs the process may use. OpenBLAS (CI and Kaggle) and
OpenMP start one thread per CPU in every process unless
`OPENBLAS_NUM_THREADS` and `OMP_NUM_THREADS` say otherwise, so a pool of N
workers asks for N times the CPUs' threads; AOCL-BLAS (BLIS) on the build
host reports one thread. Measured on the build host (12 logical CPUs) under
CI's OpenBLAS 0.3.34, the n21 cross-check replay (core-487) with six workers:

| BLAS threads per worker | seconds |
|---|---|
| per-CPU default (12) | 65 to 99 |
| 2 | 60 to 102 |
| 1 | 9 to 11 on a lightly loaded host; 36 to 52 at load averages of 35 to 85 |

One thread per worker is fastest because the matrices (128 x 128 for seven
qubits) are too small to repay BLAS threading: the pool is the parallelism.
`parallel.ordered_map` therefore sets the BLAS and OpenMP thread variables
to 1 while it spawns workers, keeps any value the caller set, and leaves the
calling process's own settings alone (gate core-520). A serial run
(`GOROROBA_WORKERS=1`) keeps the libraries' defaults, where a single large
BLAS call can use every CPU.

## Runtime packages

CI imports only the pins in `requirements.txt` and
`ci/requirements-ci.txt` (numpy, scipy, sympy, qiskit, qiskit-aer,
qiskit-ibm-runtime, rustworkx, matplotlib, mypy, ruff). A gate that needs
anything else retains its result at `--out` and checks it with the pinned
stack, as core-489 does for pyadic. Versions below are the build host's.

| Package | Version | Use it for | Boundary |
|---|---|---|---|
| numpy | 2.5.4 (CI pin) | arrays, einsum, linalg through AOCL-BLAS 5.3.0 on the host | longdouble has no linalg |
| scipy | 1.18.1 (CI pin) | `scipy.linalg` (QR with pivoting, `lstsq` drivers, `solve_triangular`), sparse, optimize | |
| numba | 0.68.0 | JIT for scalar loops numpy cannot vectorize (shot-ordered register decoding, branch walks) | host only |
| jax / jaxlib | 0.9.0 | `jax_bridge` density-matrix sweeps, batched over error scales; TPU | host only; complex64 storage |
| cupy | 14.2.0 | numpy-shaped GPU arrays on the RTX 4070 Ti | host only; float64 runs at 1/64 of float32 speed on that GPU |
| opt_einsum, cotengra, quimb | 3.4.0, 0.8.2, 1.15.0 | contraction order search and tensor networks | host only; quimb and cotengra are the `quantum-tools` Kaggle group |
| threadpoolctl | 3.6.0 | limit BLAS threads per process | host only |
| python-flint | 0.9.0 | fast exact `fmpz_mat` / `fmpq_mat` rank, solve and determinants | host only |
| gmpy2 | 2.3.2 | fast big integers and rationals where `Fraction` dominates a profile | host only |
| pyadic | 0.3.0 | `ModP`, `PAdic`, rational reconstruction | host only; [note](packages/manual/pyadic.md) |
| galois | 0.4.11 | finite-field numpy arrays and linear algebra | `quantum-tools` group |
| mpmath | 1.4.1 | arbitrary-precision reals and complexes | sympy's dependency |
| cython | 3.3.0 | compiled extensions | no compiled module in the tree |
| torch | 2.14.1 | python-octonion's tensors only | not a numerics backend here |
| dask, joblib | 2026.8.0, 1.6.0 | none: `parallel.py` is the repository's pool | |

Profile before optimizing: `py-spy record` for Python stacks, `perf` for
native code, and `hyperfine` for whole-command timing are on the host.
