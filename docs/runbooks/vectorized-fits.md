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
