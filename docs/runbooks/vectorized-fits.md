# Batched classical fits across synthetic replicates

The ring-down null calibration (`scripts/qi_readout_ringdown_cases.py
--null-calibration`) fits 14 targets x 200000 H1 replicates with `fit_h2`.
One scalar fit evaluates `h2_at` about 607 times (a 401-point `T_GRID` scan,
`GOLDEN_STEPS` = 100 golden-section steps, 5 candidates), each a weighted
two-parameter least squares over 6 arms in pure Python. `fit_h2_batch` runs
the same fit for a block of replicates at once and returns the scalar fit's
bits for every replicate. The full record, 2.8 million fits, regenerates in
163 s pooled and 573 s serial on the 12-CPU build host, where the scalar
code took 7317 s on a 4-CPU Kaggle kernel, and its bytes equal the retained
scalar record
(`results/quantum_inspire/readout_ringdown_tuna_17_null_calibration.json`,
sha256 dd8e1ed2c2a5fd1f608b2396b820cdc2798b63286dcfa2cd641436d8a01e3153).

## Mechanism

- **Fixed weights.** Every replicate of a target shares one weight pattern,
  so for a given T the sums `sw`, `sf`, `sff` and the determinant are
  T-only numbers; `grid_argmin` computes them with builtin `sum()` over
  Python floats exactly as `h2_at` does. Only `sy` and `sfy` depend on the
  replicate, and the grid profile is a `replicates x 401` array built from
  one broadcast per arm.
- **Masked golden section.** `fit_h2_batch` holds `low`, `high`, `left`,
  `right`, `f_left` and `f_right` as arrays. Each step evaluates the branch
  test `f_left <= f_right` per row, moves the bracket of every row with
  `np.where`, and evaluates one new point per row, the point the scalar
  branch would evaluate. Both arms of each `np.where` are the scalar
  expressions on the same operands, so the selected value has the scalar
  bits.
- **First minimum.** `min(range(...), key=...)` and `min(candidates,
  key=...)` keep the first minimum; `np.argmin` returns the first index of
  the minimum as well. `np.errstate(over, invalid, divide = "raise")` keeps
  NaN out of every array, so the NaN rule of `np.argmin` never applies.
- **Per-replicate tail.** `NullFit.statistic` (H1 fit, `h2_errors`,
  `round`, `detects`) runs scalar on each replicate's Python floats after
  the batched fit. It costs about 27 us against 140 us for the batched fit
  and stays exact by construction; `round(delta, 6)` must stay the Python
  builtin, since `np.round` scales, rounds and divides.
- **Blocks.** `NullBlock` fits `NULL_BLOCK` = 2048 replicates per call and
  `parallel.ordered_map` maps the blocks; the normal draws of a stream are
  all taken first from `random.Random(stream)`, so serial, pooled and
  differently blocked runs write the same bytes. Results leave a block as
  Python floats (`tolist()`), so JSON and list equality see `float`, never
  `np.float64`.

## Bitwise-equality rules

Each rule was measured on this host before the code relied on it.

| Rule | Measurement | Consequence in fit_h2_batch |
|---|---|---|
| Builtin `sum()` of floats is Neumaier-compensated (CPython 3.12 and later), starting from `0 + x0` | 76461 of 200000 random 6-term sums differ from left-to-right addition; a vectorized Neumaier emulation differs in 0 | `fsum_rows` repeats CPython's update term by term over the arms; no `np.sum`, `einsum` or matmul touches a value that feeds a decision or an output |
| Python `x ** 2` calls libm `pow` | 2481 of 3000000 random doubles give `pow(x, 2) != x * x`; numpy `x ** 2` and `np.power(x, 2.0)` compute `x * x` | every replicate-dependent square goes through `math.pow` mapped over `.tolist()` (about 80 ns per element) |
| `np.exp` and array-exponent `np.power` may use numpy's own float64 SIMD kernels | 0 of 8000000 `np.exp` values differ from `math.exp` on this host, whose numpy reports baseline X86_V2/X86_V3 and no AVX512; on an AVX512 host numpy dispatches float64 exp and power to its own kernels | every replicate-dependent exp goes through `math.exp` mapped over `.tolist()` (about 65 ns per element); `exp(-0 / T)` is exactly 1 in every C99 libm and is not called |
| numpy `+ - * /` and comparisons are IEEE binary64 operations | identical to Python float operations | expressions keep the scalar association: `(w * f) * f`, `(w * f) * y`, `(y - c) - a * f` |
| Scalar division by a zero determinant raises `ZeroDivisionError` | a singular weight pattern raises in `fit_h2` | `h2_at_batch` and `grid_argmin` raise `ZeroDivisionError` on any zero determinant |

The grid holds 401 x 6 squares per replicate, so it prunes before paying
for libm. The profile is first evaluated with `r * r`; `pow(r, 2)` and
`r * r` agree to an ulp, the terms are nonnegative, and the two profiles
therefore differ by a few machine epsilons relative. Every exact minimizer
lies within `GRID_PRUNE` = 2^-30 (relative, plus `sw * 2^-1000` absolute for
squares in the subnormal range) of the fast minimum, so only those grid
points are recomputed with `math.pow`, and the first exact minimum among
them is the first exact minimum of the whole grid. The golden section takes
no such prune: in 300 null fits of target P/0, 68 to 95 (median 76) of the
100 steps compare `f_left` and `f_right` within 2^-30 of each other, the
first such step falling between steps 3 and 32 (median 24), so most branch
decisions need the exact values.

## Equivalence gates

The scalar `fit_h2` stays the reference: `analyze_target` calls it, so the
preregistered analyses (core-369, core-386, core-430) replay unchanged.

- core-437 (`--null-self-test`, normal and `-O`): 817 fits of
  `batch_cases()` bit-identical to `fit_h2` (null draws under synthetic,
  equal and clamp-weighted patterns; all-zero, signed-zero and constant rates
  whose profile ties at every grid point and every golden step; noise-free
  and noisy decays at T = 5, at a grid point, at T = 100 and outside the
  bounds), 4006 `fsum_rows` sums bit-identical to `sum()` (signed zeros,
  cancellation, huge and subnormal terms), and `ZeroDivisionError` from both
  paths on a singular weight pattern.
- core-438 (`--null-equivalence`): the first `NULL_EQUIVALENCE` = 2000
  replicates of each of the 14 record streams, fitted by `NullFit` and by
  `NullBlock`; 28000 of 28000 fits (chi2, c, A, T compared by `float.hex`)
  and statistics identical. It runs in the full tier, since its scalar half
  costs about 154 CPU seconds.
- core-436 (pr tier): its replay runs the first 5000 replicates of every
  target through the batched path and compares their hash with the
  `prefix_sha256` that the scalar Kaggle run wrote, so every pull request
  keeps a stream-level equality check.
- Record regeneration: at N = 5200 the batched run, the refactored scalar
  run and the scalar code before batching wrote the same bytes (sha256
  f30810ef5f1eddff54a25dae5e51fbc1ea174b20551a73b1df2388eb6bd0b865); at
  N = 200000 the pooled and the serial batched runs equal the retained
  Kaggle scalar record byte for byte, so every `statistic_sha256`,
  `prefix_sha256` and `tail_sha256` reproduces.

A difference in any gate stops with its count and its largest absolute and
relative size; a tolerance is never the criterion.

## Measured timings

Build host: AMD Ryzen 5 5600X3D (6 cores, 12 CPUs), shared with other sessions;
Python 3.14.7, numpy 2.5.4, glibc 2.44. Per-fit times use the synthetic
weights of `batch_cases()` at load 11 to 15 and target P/0's weights at load
19 to 21; the wall times of the full record include the normal draws and the
per-replicate statistic.

| Measurement | Load average (1 min) | Scalar | Batched |
|---|---|---|---|
| one fit, single process | 11 to 15 | 3182 to 3491 us | 141 to 159 us (block 2048) |
| one fit, single process | 19 to 21 | 8805 to 10794 us | 405 to 584 us |
| full record, N = 200000 x 14, pooled (12 workers) | 21 to 25 | 7317 s on 4 Kaggle CPUs (Intel Xeon 2.20 GHz), kernel log time at the record line | 163 s wall, 790 s user |
| full record, `GOROROBA_WORKERS=1` | 17 falling to 10 | | 573 s wall, 461 s user |
| N = 5200 x 14, pooled | 15 | 49 s (53 s before batching) | 8.6 s |
| core-438, 2000 x 14 both paths, pooled | 13 | | 30 s wall, 154 s user |
| core-436, cmp plus 5000-replicate prefix replay of 14 targets, normal and `-O` | 24 scalar, 14 batched | 679 s | 12.4 s |
| core-437, normal and `-O` | 24 scalar, 22 batched | 51 s | 20.1 s, 817 scalar reference fits per mode included |
| core-436, `GOROROBA_WORKERS=2` | 63 | | 61.5 s |
| core-437, `GOROROBA_WORKERS=2` | 47 | | 27.0 s |
| core-438, `GOROROBA_WORKERS=2` | 42 to 52 | | 178.4 s |

The batched fit spends about 45 percent of its time in the libm map
(roughly 1080 `math.exp` and `math.pow` calls per replicate, mostly in the
golden section), 30 percent in `fsum_rows`, and the rest in the grid
broadcasts.

## When to batch and when to shard

Batch first whenever one classical estimator runs over many synthetic
replicates that share their structure: null calibrations, parametric
bootstraps, resampling bootstraps, permutation tests. The batched path
removes interpreter overhead per arithmetic operation, typically a factor
of 15 to 25 here, and composes with the process pool, which divides by the
CPU count on top. Shard to Kaggle CPU sessions only when the batched,
pooled run still exceeds one host's budget, and shard by item range so the
merged record is index-ordered. Keep the scalar form as the reference that
analyses call, prove equality with a gate on the record's own streams plus
adversarial inputs, and keep every transcendental and every power on the
libm entry points the scalar code uses.

## Measured opportunity: the calibration-sensitivity bootstrap

core-434 (`--sensitivity ... --replay`, 535 to 1041 s) resamples the readout
and Ramsey counts `CALIBRATION_REPLICATES` = 2000 times per series and calls
`analyze_target` twice per usable target per replicate. Profiled serially on
series Q with 20 replicates, `fit_h2` takes 20.19 of the 20.74 s that
`sensitivity` spends (97 percent), across 414 calls. The same batching applies with one
difference: the arm errors, and therefore the weights, change with every
resampled table, so `sw`, `sf`, `sff` and the determinant become
`replicates x 401` arrays instead of T-only numbers. The batched path is not
implemented for it.

## Batched null calibration of the diagnostic case's tests

`scripts/bdsc_null_calibration.py` batches the statistics of `bdsc_diagnostic.analyse` (the nine
chi-square tests, the three class calibration shifts and the count of residuals beyond `MARGIN`) across
replicates of pure binomial counting at `TRIALS` = 40000 with equal f and g performance, and reports each
test's false-resolution rate (p-value below `ALPHA` = 0.01) with its binomial error. The same rules apply
with these sites:

- `se ** 2`, `(change - mean) ** 2`, `(v - mean) ** 2` and `(effect / se) ** 2` go through `math.pow`;
  the `sum()` calls over a group go through `fsum_rows`, while the running totals that `analyse` builds
  with `+=` stay plain additions;
- `math.hypot` of the block-change error is CPython's own algorithm, so it maps through the math module
  and `np.hypot` is refused;
- the template effect is `np.mean` of four slot differences, repeated with `np.mean(axis=1)` on a
  C-contiguous array;
- the weighted least-squares terms of `seed_split` run the scalar function per replicate on the batched
  floats, since LAPACK `dgelsd`, the BLAS product and numpy's pairwise `np.sum` fix bits that no
  reformulation reproduces.

All replicates' counts come from one `rng.binomial` call seeded with `NULL_SEED` (ANU draw
`docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json`, index 0), so serial, pooled and differently blocked runs
write the same bytes. Gate core-685 compares ten replicates with the scalar `analyse` by `float.hex` and runs
three mutants (naive sum, numpy square, `np.hypot`), each of which must differ; two of the ten draw
indices (81 and 349) are the ones whose block-change statistic differs between `pow(x, 2)` and `x * x`.
Gate core-686 runs 3000 replicates (about 6 s serial) and requires every rate within `ALPHA` plus or minus
three nominal binomial errors (0.0018 each) and no more than the upper bound for a residual beyond the margin.

## Batched null of the measurement-sequence envelope

`gororoba_quantum/msq_envelope_null.py` replays the envelope's decision pipeline on synthetic devices, and each
replicate of width 32 runs `measurement_sequence_analysis.evaluate_qubit` on 32 qubits. Profiled serially, a scalar
replicate takes 4.41 s on a quiet host (8.1 s at load average 10); 85 percent of it is `chain_matrix` (173872 calls
of the 4 x 4 Bloch propagation, reached through `corrected_z`), and the callers split into `propagate_many` 42
percent, `fit_eps` 40 percent, `gate_curves` 17 percent and, inside `propagate_many`, `implied_loss` 19 percent.
The two SciPy solvers cost little themselves (bounded Brent of `fit_t1` 7 percent, `brentq` about 0.02 s beyond its
objective); they need porting because the fitted T1 and q and the root-finder's eps are replicate-dependent inputs
of every chain call. Draws and screens take under 1 percent.

- **Replicate axis.** `analyse_block` draws a block of `NULL_BLOCK` = 25 replicates with the scalar `draw`, then
  `evaluate_batch` hands each qubit's replicates to `evaluate_qubit_rows`, which runs the fit on a replicates-long
  axis. Replicates of a block share every context (`null_contexts`), so only the sx residual and the binomial counts
  differ.
- **Perturbation rows.** `propagate_many` evaluates `quantities` at the base point and at 19 up and 19 down points;
  `propagate_rows` stacks the 39 points of all replicates along one row axis, evaluates them in one pass of
  `quantities_rows`, and accumulates the delta-method sums in input order. `fit_eps_rows` stacks the 101 grid
  points, both evaluations of a golden-section step and the three curvature points the same way; `curve_values`
  stacks the 249 gate points of the eight gate-curve halves.
- **Stacked Bloch chain.** `chain_rows` builds the products with stacked `@` and `np.linalg.matrix_power` in the
  scalar association; `sx_rows` calls the cached scalar `sx_map` once per distinct (T1, T2, dephasing, angle) of the
  rows, and `damped_sx` is computed once per fit and shared by every arm.
- **Masked solvers.** `minimize_rows` ports SciPy 1.18.1's `_minimize_scalar_bounded` and `brentq_rows` its
  `brentq` (the algorithm of `scipy/optimize/Zeros/brentq.c`; the wheel ships the compiled routine only). Every
  branch is a per-row `np.where` whose arms are the scalar expressions, a finished row leaves the live set, and the
  objective sees live rows only.
- **Scalar tails.** The gate-curve stops, `gate_propagation`, the row assembly of `evaluate_qubit`
  (`qubit_row`), `widen_for_device_scatter`, `informative` and `device_verdict` run the scalar functions on the
  Python floats of the batched arrays; they cost under 1 percent.

### Bitwise-equality rules

Each rule was measured on this host (numpy 2.5.4, SciPy 1.18.1, glibc 2.44) before the code relied on it.

| Rule | Measurement | Consequence |
|---|---|---|
| Slices of a stacked `@` and of `np.linalg.matrix_power` equal the single-matrix calls | 0 of 5000 4 x 4 products differ, for stacked, left-broadcast and right-broadcast operands and powers 2, 3, 4, 5, 8, 16, 32 | `chain_rows` stacks every product |
| A stacked `scipy.linalg.expm` does not | 91 of 300 matrices differ from the single call | `sx_rows` calls `sx_map` per distinct key |
| `np.sum(a, axis=1)` of a C-contiguous (rows, 5) array equals `np.sum` of each row | 0 of 100000 rows differ; emulating it as `a[0] + (sum of a[1:] left to right)` differs in 23787 | `fit_t1_rows` keeps `np.sum(axis=1)`; a hand-written reduction order is refused |
| `np.exp` of a (rows, 5) array equals `np.exp` of each row | 0 of 100000 rows differ | `fit_t1_rows` keeps `np.exp` and `** 2` on arrays |
| Python-float `x ** 2` is libm `pow`; numpy's array `** 2` is `x * x` | 104 of 260224 squares in the `propagate_many` and `fit_eps` steps of 128 qubit-replicates differ between `pow` and `x * x` | the delta-method terms and the `fit_eps` chi-square go through `math.pow`; the array squares of `fit_t1` stay numpy |
| Builtin `sum()` is compensated | the unit test requires a field of a row to change when `neumaier_rows` is replaced by plain addition | the `fit_eps` chi-square sums with `neumaier_rows` |
| The `brentq` and `minimize_scalar` points are a sequence, not only a result | the objective sees the same points in the same order for every row | the solver tests compare the whole sequence of points |

### Equivalence gates

The scalar `replicate()` stays the reference. The unmarked tests in `tests/test_msq_envelope.py` run on every pull
request, in normal and `-O` mode, and name the first differing path of any mismatch:

- the bounded Brent and `brentq` ports replay SciPy on 400 rows each: the objective sees SciPy's points in SciPy's
  order and the minimizer or root matches by `float.hex`; the rows take the accepted, bound-clamped and rejected
  parabolic steps, the golden-section step and every bracket and keep-point update of Brent, and the
  interpolation, extrapolation, rejected-step bisection, plain bisection, endpoint-swap and minimum-step branches
  of `brentq`, which `SolverTrace` counts;
- three qubits of eight contexts, three replicates each, through `evaluate_qubit_rows` against
  `evaluate_qubit`, every field (floats by `float.hex`, the retained gate-curve arrays by bytes), with a mutant
  that replaces the compensated sum and must differ;
- a block of two replicates at width 8 through `analyse_block` against `replicate_detail`: record row, per-qubit
  rows after the device-level widening, and the device verdict, plus the withheld path.

The record `docs/evidence/measurement_sequence/envelope-null-w32.json` (sha256
6ed17f600fd9bff894b0ae265670f6b355b6af66f34ccf11be4b54f2cd5f6975) regenerates byte for byte from
`msq_envelope_null.py --width 32 --replicates 400` pooled, with `GOROROBA_WORKERS=1`, and under the hosted lane's
environment (`OPENBLAS_CORETYPE=Haswell`, `NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR"`). The record
holds the fire count, the withheld count, the mean kept count and the bound, none of which moves with the last bits
of a per-qubit row, so the byte match is necessary and does not discriminate; the row-level tests carry the
bit-equality claim.

### Measured timings

Width 32, build host (12 CPUs shared with other sessions), Python 3.14.7. Load average is the 1-minute value at the
end of each run.

| Measurement | Load | Scalar | Batched |
|---|---|---|---|
| one replicate, single process | 6 to 12 | 4.41 s | 0.33 s per replicate in blocks of 25 (14 times faster) |
| 48 replicates, `GOROROBA_WORKERS=1` | 10 | 390 s (8.13 s per replicate) | 15.6 s (0.32 s per replicate) |
| 48 replicates, 12 workers (batched: two blocks, so two busy workers) | 16 / 9 | 60.2 s | 12.2 s |
| 400 replicates, `GOROROBA_WORKERS=1` | 5 to 14 | not run (extrapolates to 1760 to 3250 s) | 131.5 s in a timing script, 165.6 s for the command (414 s user) |
| 400 replicates, 12 workers | 14 to 18 | not run | 36.6 s wall, 345 s user |

Block sizes 8, 16, 25 and 50 give 50, 54, 42 and 44 s for the pooled 400 replicates at load 14 to 19; the choice
of 25 divides 400 into 16 equal blocks.

## Library, dispatch and cross-host choices

`scripts/numerics_fingerprint.py --out FILE` hashes the float64 output of every kernel the measurement-sequence nulls
run, over fixed grids, in a fresh interpreter per dispatch configuration (default; NumPy without AVX-512,
`NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR"`; OpenBLAS `OPENBLAS_CORETYPE=Haswell`; both): `np.exp`
and `math.exp`, `np.power` and `math.pow`, `chi2.sf`, stacked and single 4 x 4 `@`, `matrix_power(., 16)` on a
stack, `scipy.linalg.expm` on a stack of sx generators, `measurement_sequence_analysis.corrected_z` and
`msq_successor_analysis.fit_gamma_rate`. A null splits replicates across hosts only when every host's digests equal
the build host's.

| Measurement | Result |
|---|---|
| Kaggle CPU kernel (`results/kaggle/2026-10-27T233744Z-gororoba-numerics-fingerprint`: Intel Xeon 2.20 GHz without AVX-512, glibc 2.39, `--ci-env` pins) against the build host (Ryzen 5 5600X3D, glibc 2.44), all four configurations | all 11 digests equal: shards from Kaggle CPU kernels merge byte for byte with build-host shards |
| stacked `a @ b`, `np.linalg.matrix_power` and `scipy.linalg.expm` on (R, 4, 4) against the per-matrix calls | 0 mismatches over 4096 and 256 rows: a batched chain may stack these |
| `np.einsum("rij,rjk->rik")` against stacked `@` | 25108 of 65536 values differ: einsum and tensordot stay out of a bit-identical path |
| Numba 0.68 `@njit(fastmath=False)` 4 x 4 product loop against OpenBLAS | 0.55 against 3.5 us per row, but 62143 of 65536 values differ; its `math.exp` equals libm. Numba, JAX and CuPy sit outside the CI pins, so a gate or replay cannot use them |
| scalar `chain_matrix` against the stacked chain | 40 us per call against 0.6 us per row; a serial 31-qubit successor replay spends about half its 21 s in `chain_matrix` and a fifth in SciPy's bounded Brent, all per-call overhead on 4 x 4 and 5-element arrays |
| accuracy against Arb (python-flint, 200 bits) and mpmath (50 digits) | `expm` of the sx generator 2.5e-13 relative; `(1 + x)^(-k)` survival 1.1e-13 for k up to 1000 (`exp(-k log1p x)` 1.3e-15) |
| rate average over Gamma(k) at 64 nodes against adaptive quad and 1024-node references | quantile midpoint rule 1.6e-5 to 3.8e-5 low at k = 0.25 to 1; generalized Gauss-Laguerre within 5e-7. SciPy's `roots_genlaguerre` weights carry Gamma(k) and overflow near k = 170; the Golub-Welsch form (`eigh_tridiagonal` of the Laguerre Jacobi matrix, weights the squared first eigenvector components) sums to 1 within 1e-15 and reproduces three Gamma(k, 1) moments to 2e-15 for k = 0.25 to 1000 |

A host whose digests differ (an AVX-512 machine running NumPy's own float64 loops, or OpenBLAS's SkylakeX kernel)
gets the two environment pins above before NumPy loads, as the hosted lane sets them, and runs the fingerprint again;
a host that still differs runs whole arms rather than shards of one. The floating-point budget is many orders below
the statistical one: the null's precision is set by its replicate count and its one-sided binomial bound.
