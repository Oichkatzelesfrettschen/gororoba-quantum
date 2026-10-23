# Numerics: conditioning, precision, vectorization and runtime packages

This note collects the numerical rules the repository's measurements
support. Each rule names the record or gate that carries its evidence; a
rule marked *inferred* has no measurement behind it yet and names the probe
that would decide it.

## Least squares and conditioning

The [least-squares conditioning study](../../evidence/lsq_conditioning/README.md)
(`scripts/lsq_conditioning_study.py`, gate core-489 and gate `core-self-test-08` (`tests/test_cli_self_tests.py`)) measures
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
  Scaling each column by the power of two that puts its norm in
  [2^-1/2, 2^1/2) (`A D`, then `x = D y`; `equilibration()` in the study)
  is exact in binary floating point and cut kappa a median 341 times on the
  854 designs whose column norms spread by 100 or more. Van der Sluis bounds
  unit-norm columns within sqrt(n) of the optimal diagonal scaling; the
  power-of-two rounding adds at most a factor of 2 to that bound. Householder QR is invariant under such scaling, so equilibration
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
  `atlas_coherent_families.compare()` uses a per-value rule. The study
  measures every SVD, QR and equilibrated float64 value within 1.8e-4 of its
  tolerance of the exact solution; the float64 normal equations reach 0.26
  of tolerance on a component and 0.75 on a held-out prediction (margins
  3.9 and 1.3).

## Precision

| Format | Significand | eps | Where it runs here |
|---|---|---|---|
| float32 / complex64 | 24 bits | 1.2e-7 | `jax_bridge` storage on the CPU (matmuls at `Precision.HIGHEST`); a GPU or TPU run is an unqualified target |
| float64 / complex128 | 53 bits | 2.2e-16 | the default: numpy, AOCL-BLAS or OpenBLAS, Aer `precision="double"` |
| `np.longdouble` / `np.clongdouble` | 64 bits (x87 extended, stored in 128 bits) | 1.1e-19 | scalar x87 only: no SIMD, no BLAS or LAPACK; `einsum` accepts it |
| double-double | about 106 bits | about 1e-32 | software (pairs of float64 with error-free transformations) |
| IEEE binary128 | 113 bits | 1.9e-34 | software only on x86 (libquadmath, MPFR, mpmath) |
| `Fraction`, mod p | exact | 0 | stdlib `fractions`, pyadic `ModP`, python-flint, galois |
| p-adic `PAdic` | fixed precision p^k | capped at O(p^k) | pyadic; exact only through a certified lift plus rational reconstruction |

- **float64 is enough wherever sampling sets the error.** The n21 exact
  model agrees with Aer's exact density-matrix law to 1.2e-15 under the
  cleaned noise model; under the raw calibration model the gap is 1.06e-9
  per outcome and 2.0e-9 in the contrast, which is Aer's own truncation of
  noise components at 1e-10, not rounding
  ([cross-check](../../evidence/n21_exact_model/README.md), core-487). The
  run's statistical radii are about 1e-2. Aer accepts only
  `precision="double"` and `"single"`.
- **Extra precision reduces rounding by 2^-(p-53) and nothing else.** The
  study's emulated p-bit Householder QR (bit-identical to Python doubles at
  p = 53 and to x87 `np.longdouble` at p = 64) shows the predicted scaling at
  p = 64, 106 and 113 with no retained value moving.
- **Certificates use exact arithmetic, not wide floats.** Rank and nullity
  claims run in `Fraction` or modulo a prime (2^61 - 1). A p-adic value is
  exact only once a lift to precision p^k above a proved reconstruction bound
  (core-489: p^k > 2 max(N, D)^2) is rationally reconstructed and checked
  against the system; a fixed-precision `PAdic` result alone is an
  approximation. Two independent exact
  paths that agree (core-489's Fraction and p-adic solutions on all 2716
  designs) outrank any finite precision.
- **A total arithmetic replaces divide-and-check.**
  `gororoba_quantum/wheel_algebra.py` (its `--self-test` in gate `core-self-test-08` (`tests/test_cli_self_tests.py`)) implements the wheel of
  fractions over Q: 1/0 is infinity and 0/0 is bottom, so elimination on a
  consistent singular symmetric positive semidefinite system (right side in
  the column space, as rank-deficient normal equations are) returns bottom
  instead of raising; an inconsistent one can return infinity
  (`solve([[0]], [1])`). Bottom carries no kernel or consistency
  information; nullity still comes from exact rank.

## Vectorization in numpy

- **Express independent arithmetic as array operations.** Broadcasting,
  `np.einsum`, batched `@` over leading axes and `np.linalg` on stacked
  matrices run in compiled loops; a Python loop over array elements pays
  interpreter dispatch on every element.
- **Contract tensors with a planned order.** `np.einsum(..., optimize=...)`
  chooses a pairwise order on every call. `dynamic_density` caches only its
  subscript strings per qubit tuple and calls `np.einsum(..., optimize="greedy")`
  per operation, so the path search repeats; `np.einsum_path` computed once
  per (subscripts, shapes) and passed as `optimize=path` would move it out of
  the inner loop (unmeasured). For networks beyond a few tensors,
  opt_einsum or cotengra find better orders.
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
CI's OpenBLAS 0.3.34, the n21 cross-check replay (core-487) with six workers
([observations](../../evidence/blas_worker_threads/observations.json), single
wall-clock runs on a host whose load average other jobs set between 27 and
85):

| BLAS threads per worker | seconds, by series |
|---|---|
| per-CPU default (12) | 99 and 65 |
| 2 | 45 to 102 |
| 1 | 11 and 9; 43, 52 and 36 in the three interleaved series |

Within every series that ran both, one thread per worker was fastest; the
absolute seconds move with the host's load.

The matrices (128 x 128 for seven qubits) are small enough that BLAS
threading plausibly costs more than it saves; the pool is the parallelism.
`parallel.ordered_map` therefore sets the BLAS and OpenMP thread variables
to 1 while it spawns workers, keeps any value the caller set, and leaves the
calling process's own settings alone (gate core-520). A serial run
(`GOROROBA_WORKERS=1`) keeps the libraries' defaults, where a single large
BLAS call can use every CPU.

## Exact backends

SymPy 1.14.0 chooses its ground types when it is imported: python-flint when
the installed version is in its tested list (0.6 to 0.10), else gmpy2, else
pure Python. requirements.txt pins python-flint 0.9.0, so CI and the build
host both run `flint` ground types; `SYMPY_GROUND_TYPES=python` reproduces a
flint-free stack for a comparison. Ground types alone move the SymPy gates by
under 10 percent: their time goes to Matrix construction, `sympify` and
entrywise `Matrix` products, not to integer or rational arithmetic.

| work | backend | measured on | speedup |
|---|---|---|---|
| rank modulo 2^61 - 1, 16 to 32 square | flint `nmod_mat.rank` (`scripts/exact_rank.py`) | core-324's 170 calls of 10 frames | 10.6 to 14.5x over Python ints |
| rational null space by RREF | flint `fmpq_mat.rref` | core-324's 130 calls | 22 to 32x over `Fraction` elimination |
| rational null space by RREF | SymPy `DomainMatrix` over QQ | same | 3.3 to 3.6x |
| rational null space by RREF | gmpy2 `mpq` in place of `Fraction` | same | 4.6x |
| rank modulo p | SymPy `DomainMatrix` over GF(p) | same | 0.3 to 0.5x (slower) |
| 64 x 64 integer matrix products | SymPy `DomainMatrix` over ZZ | complex_skew `coefficient_control` | about 2800x over `Matrix` products |
| whole gate | core-324 (d_locus_nullity, flint) | serial, build host | 7.3x (126.7 s to 17.4 s) |
| whole gate | core-063 (complex_skew, DomainMatrix) | serial, build host | 2.2x (94.1 s to 42.7 s) |

- **Compute with FLINT, check the certificate without it.**
  `exact_rank.rational_kernel` reads the basis from the unique RREF, so it
  returns the same `Fraction` vectors as Python elimination (the `exact_rank.py --self-test` of gate `core-self-test-09` (`tests/test_cli_self_tests.py`)
  compares the two on 254 matrices). `d_locus_nullity.nullity` verifies each
  kernel vector it certifies as integer dot products after lcm scaling; the
  rank modulo p still bounds the rational rank from below. The kernels that
  `frame_spaces` and `rank_locus_local_dimension.tangent_bound` read carry no
  such check.
- **Multiply integer SymPy matrices as `DomainMatrix`.** `Matrix * Matrix`
  on mixed mutable and immutable operands takes SymPy's entrywise expression
  path. `.to_DM()` products over ZZ return the same equality.
- **Profile SymPy gates under `SYMPY_GROUND_TYPES=python`** when the question
  is what a flint-free stack spends.

## Runtime packages

`ci/install_pins.sh` defines CI's stack: the pins in `requirements.txt` and
`ci/requirements-ci.txt` (numpy, scipy, sympy, qiskit, qiskit-aer,
qiskit-ibm-runtime, rustworkx, python-flint, matplotlib, mypy, ruff), then mpmath 1.4.1
with `--no-deps` and the sympy 1.14.0 patch that pair needs. A gate that needs
anything else retains its result at `--out` and checks it with the pinned
stack, as core-489 does for pyadic. Versions below are the build host's.

| Package | Version | Use it for | Boundary |
|---|---|---|---|
| numpy | 2.5.4 (CI pin) | arrays, einsum, linalg through AOCL-BLAS 5.3.0 on the host | longdouble has no linalg |
| scipy | 1.18.1 (CI pin) | `scipy.linalg` (QR with pivoting, `lstsq` drivers, `solve_triangular`), sparse, optimize | |
| numba | 0.68.0 | JIT for scalar loops numpy cannot vectorize (shot-ordered register decoding, branch walks) | not in CI; Kaggle `quantum-tools` group |
| jax / jaxlib | 0.9.0 | `jax_bridge` density-matrix sweeps, batched over error scales, on CPU | host only; complex64 storage; TPU is a target no retained run has qualified ([TPU research](../kaggle/tpu-research.md)) |
| cupy | 14.2.0 | numpy-shaped GPU arrays on the RTX 4070 Ti | host only; the GPU's nominal float64 throughput is 1/64 of float32 (a hardware ratio, not a measured workload speed) |
| opt_einsum, cotengra, quimb | 3.4.0, 0.8.2, 1.15.0 | contraction order search and tensor networks | host only; quimb and cotengra are the `quantum-tools` Kaggle group |
| threadpoolctl | 3.6.0 | limit BLAS threads per process | host only |
| python-flint | 0.9.0 (CI pin) | exact rank modulo p (`nmod_mat`), RREF null spaces (`fmpq_mat`), SymPy's ground types | Kaggle images take it through `--ci-env` or the `exact-arithmetic` group |
| gmpy2 | 2.3.2 | fast big integers and rationals where `Fraction` dominates a profile | host only |
| pyadic | 0.3.0 | `ModP`, `PAdic`, rational reconstruction, Hensel lifts of smooth germs (`scripts/rank_locus_padic_lift.py`) | not in CI; Kaggle `exact-arithmetic` group; precision model and traps in the [manual page](../packages/manual/pyadic.md#precision-model) |
| galois | 0.4.11 | finite-field numpy arrays and linear algebra | `quantum-tools` group |
| mpmath | 1.4.1 | arbitrary-precision reals and complexes | CI pin through `ci/install_pins.sh` |
| cython | 3.3.0 | compiled extensions | no compiled module in the tree |
| torch | 2.14.1 | python-octonion's tensors only | not a numerics backend here |
| dask, joblib | 2026.8.0, 1.6.0 | none: `parallel.py` is the repository's pool | |

Profile before optimizing: `py-spy record` for Python stacks, `perf` for
native code, and `hyperfine` for whole-command timing are on the host.
