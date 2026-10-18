# Least-squares conditioning and arithmetic precision of the coherent-family fits

`scripts/lsq_conditioning_study.py` measures how the solver and the
arithmetic move the least-squares solutions of
`scripts/atlas_coherent_families.py`. Each identified model of every lane is
solved by `np.linalg.lstsq`, on the full design and on each leave-one-edge-out
fold. The study reads that script and its retained `result.json`; it changes
neither, and it runs no hardware, Quantum Inspire or Kaggle job.

## Predictions, stated before measuring

kappa is the 2-norm condition number of the design A (m x n).
rho = ||r*|| / (||A|| ||x*||), where x* is the exact least-squares solution
and r* = b - A x*. eps = 2^-52. Errors are normwise relative,
||x - x*|| / ||x*||, unless named componentwise. A value's tolerance is the
per-value rule of `atlas_coherent_families.compare()`:
max(1.5e-6, 1e-9 |v|, eps kappa_rule^2 |v|). kappa_rule is the retained
full-design `condition` for a full fit and the retained `fold_condition_max`
for a fold.

- **P1.** The normal equations lose accuracy as eps kappa^2. Householder QR
  and SVD are backward stable, with forward error about
  eps (kappa + kappa^2 rho).
  - Falsified if any float64 QR or SVD error on a rebuilt design exceeds
    m n eps (kappa + kappa^2 rho).
  - Falsified if any normal-equations error exceeds m n eps kappa^2.
  - Falsified if, on the synthetic graded design of the self-test
    (kappa 1e7, rho 0), the normal-equations error fails to exceed the QR
    error by kappa / 100. The built case has kappa 2^25 = 3.4e7 and
    rho 1.8e-17: it is assembled from Householder reflectors in sequential
    Python floats, so its bytes are the same under every LAPACK build.
  - Falsified if, over the rebuilt designs with kappa >= 1e4, the median
    ratio of normal-equations error to QR error is below 10.
- **P2.** Column equilibration, A D with D a power of two per column that
  brings each column norm into [2^-1/2, 2^1/2], cuts kappa by orders of
  magnitude when the column scales differ. Van der Sluis: unit-norm columns
  lie within sqrt(n) of the best diagonal scaling. Rounding D to powers of
  two adds at most a factor of 2.
  - Falsified if kappa(A D) > 2 sqrt(n) kappa(A) on any design. This is van
    der Sluis against the scaling D = I.
  - Falsified if the self-test's column-scaling case drops kappa by less
    than 100x.
  - Falsified if the median kappa(A) / kappa(A D) is below 10 over the
    rebuilt designs whose column norms spread by at least 100. On lane 4
    these are the detuning pairs with CZ phase, SX amplitude and axis tilt,
    and the detuning, ZZ and symmetric-ZZ models with a constant.
  - The worst-conditioned design, `axis_tilt_plus_mean`, has a column-norm
    spread near 2.7. Its kappa comes from near-collinearity of the tilt block
    with the constant column (axis tilt alone has kappa 4.8). Equilibration
    is predicted to change its kappa by less than 3x. This case is reported
    separately and carries no pass/fail.
- **P3.** Extra precision cuts the rounding part of the error by
  2^-(p-53). The precisions are x87 80-bit (p = 64), double-double
  (about 106 bits) and binary128 (p = 113). None of these changes anything a
  1.5e-6 tolerance can see.
  - Falsified if, on any ladder design, the emulated Householder error at
    p exceeds 100 * 2^-(p-53) times its error at p = 53.
  - Falsified if any float64 solution component (SVD, all designs; emulated
    QR at p = 53, ladder designs) differs from x* by tolerance / 10 or more,
    or if any fold prediction a_held . x does. The predictions cover the SVD
    solves of all designs and, on the ladder designs, the p = 53 solution's
    predictions evaluated in p = 53 arithmetic (`p53_pred_margin`).
  - The emulator is validated, not falsified. It is required to reproduce
    the same Householder code run in Python floats bit for bit at p = 53,
    and in `np.longdouble` at the host's long-double precision (p = 64 on
    x86-64 x87). Its R factor is also required to match `np.linalg.qr`
    within m n eps ||A|| on designs with kappa <= 100.
- **P4.** The contrast moves between substrates in #161 come from the
  resimulation, not from the least squares.
  - Every rebuilt design is perturbed by seeded noise of 2-norm
    3.5e-13 ||A||, the largest measured AOCL-to-OpenBLAS design difference,
    and solved by SVD.
  - On the real lane-4 designs of Fez and Kingston (`--out` only), the two
    moved predictions are resimulated at the fold solution and at the
    perturbed fold solution: Fez `axis_tilt_plus_mean` `predicted_log_ratio[1]`
    and Kingston `axis_tilt_plus_mean` `predicted_log_ratio[0]`.
  - Holds if every least-squares-induced move of those predictions stays
    below 1e-7, a tenth of the smallest #161 move.
  - Falsified if any reaches 1e-6.
  - Inconclusive in between.
  - Amended after the first measurement: a perturbation touches only the
    family slope columns, scaled to 2-norm 3.5e-13 (or 1.3e-14) times the
    slope block's norm. The lane-constant ones column that fit_models
    synthesizes exactly stays fixed, because no BLAS build or simulation
    changes it. The first measurement perturbed the whole design, constant
    included; its numbers are kept below for comparison.
- **P5.** The p-adic (Dixon and Hensel) solution of the integer-scaled
  normal equations, reconstructed as rationals, equals the Fraction solution
  on every design.
  - Falsified by one differing digest.
  - The rank of every integer-scaled design modulo each recorded prime is
    predicted to be full (n). The rank-deficient control is predicted to
    give n - 1 modulo every prime.
- **P6.** The wheel solve equals Fraction elimination, with every component
  finite, on every full-fit and worst-fold design.
  - On the consistent rank-deficient control, every component is predicted
    to be bottom (0/0), and no exception is raised.
  - Falsified by one differing or non-finite component on a full-rank design,
    or by any finite component on the control.

## What each arithmetic establishes

- **Float64, the emulated p-bit ladder and x87 measure rounding.** Each runs
  the same algorithm with a different unit roundoff, so the change in error
  from p = 53 to p = 113 is the rounding part of the error and nothing else.
  The emulator rounds every exact dyadic result to p bits, ties to even. At
  p = 53 it reproduces the same Householder code in Python floats bit for
  bit. At p = 64 it reproduces `np.longdouble` (x87, 64-bit significand) bit
  for bit, on all 448 ladder designs.
- **Fraction and p-adic give two independent exact references.**
  - Fraction elimination works in Q from the dyadic floats.
  - The Dixon solve works modulo a prime power.
  - These share no intermediate value, and their solutions agree on every
    design.
  - `padic_witness.json` retains each design's lift, the residues of the
    scaled solution modulo p^k. `--check` verifies it with integers alone:
    the lift solves the scaled normal equations modulo p^k, and its
    half-extended Euclid reconstruction equals the fresh Fraction solution.
  - A witness computed some other way, as residues of the Fraction solution,
    is the same certificate, because the lift of a rational below the bound
    is unique. What the check rejects is any witness that differs from it:
    one unit off, the residues of the float64 solution, too small a k, or
    the wrong prime.
- **Mod-p certifies rank.**
  - A full-column-rank reduction modulo a prime proves the integer design
    has full column rank over Q. A nonzero n x n minor mod p is nonzero
    over Z.
  - Three primes guard against the false negative: a prime that divides
    every maximal minor.
- **The wheel totalizes division.** Carlstrom's wheel of fractions
  ([source note](../../notes/wheels-carlstrom.md)) adjoins /0 and 0/0 to Q.
  - Elimination over it returns bottom (0/0) where Fraction elimination
    raises at a zero pivot. It does not raise an exception or return a huge
    float.
  - The study applies it only to normal equations: symmetric positive
    semidefinite matrices whose right side lies in their column space.
  - On that class every component is finite exactly when the matrix is
    positive definite, where the solve equals Fraction elimination.
    Otherwise every component is bottom.
  - Outside that class bottom and infinity carry no consistency or kernel
    information. `solve([[0, -1], [0, -1]], [-1, 0])` is inconsistent and
    returns bottom. `solve([[1, 1], [1, 1]], [1, 2])` is inconsistent and
    returns infinity. The wheel self-test keeps both as the documented
    limitation.

## Method

**Designs.**
- The study rebuilds 224 identified models over 14 lanes (Fez and Kingston,
  7 lanes each). Each gives a full design plus one fold per edge: 2716
  least-squares problems in all.
- A design is the model's `fitted_slopes` blocks in
  `atlas_coherent_families.MODELS` order, plus a ones column for a
  lane-constant model. The data are `measured_offset_rad`.
- These retained values carry nine and six decimals. The rebuilt bytes are
  therefore the same on every host, and the gate solves exactly these
  problems.

**Bridge to the real designs (`--out` only).**
- `--out` wraps `fit_models` in-process to capture the unrounded lane-4
  designs of both runs.
- Retained condition numbers match the real designs to the retained three
  decimals.
- SVD on each real design reproduces every retained six-decimal parameter.
- The rebuilt designs differ from the real ones by up to 1.3e-7, relative to
  their 2-norm, and the offsets by up to 4.9e-7.
- That rounding moves the exact solution by up to 631 times its tolerance
  (Fez `detuning_and_zz`). Values move by more than one tolerance on 12 of
  18 Fez models and 8 of 14 Kingston models.
- The retained record therefore cannot reproduce its own parameters from its
  rounded inputs. Every comparison here is between solvers on the same
  stored problem, against that problem's own exact solution.

**Per-design measurements and the ladder.** The script docstring lists the
measurements on each design. The precision ladder, the Python-float and
long-double runs and the wheel solve cover the full fit and the
worst-conditioned fold of each model: 448 designs. The ladder costs about
5 ms per design, so all 2716 designs would add about 14 s per mode and take
core-489 past the pr tier's one minute.

**p-adic certificate.**
- The Dixon lift runs modulo 2^61 - 1, the first recorded prime, which left
  every scaled A^T A invertible.
- It lifts to k = 2 to 55 digits. k is the smallest value with
  p^k > 2 max(N, D)^2, where N and D are the Hadamard bounds of the Cramer
  numerators and the determinant. That is 108 to 3332 bits.
- `pyadic.rationalise` (lattice Gauss reduction) returns the shortest vector
  of a lattice of determinant p^k. Under this bound the reconstruction is
  exact.
- The recorded primes are 2^61 - 1, 2^89 - 1 and 2^107 - 1.
- The residual r* has p-adic valuation 0 in every component for all three
  primes. Its 2-adic valuations run from -71 to -20, the binary scale of
  the dyadic data.
- The lifts of all 2716 designs fill `padic_witness.json` (4.5 MB, base64
  integers), bound to `result.json` by its sha256.

**P4 resimulation.**
- For every fold of `axis_tilt_plus_mean` on the real lane-4 designs, the
  held-out contrast prediction is resimulated at the fold solution
  (`atlas_coherent_families.Resimulate`).
- It is resimulated again at 8 seeded perturbations of the slope block of
  2-norm 3.5e-13 times the block's norm, the worst design difference #161
  measured. The lane-constant column stays fixed (`mutable_columns`).
- It is resimulated again at 8 more of 1.3e-14 times the block's norm, the
  median measured difference.
- All noise arrays are drawn first, in the seeded (fold, level, trial)
  order, and the fold solves run through `parallel.ordered_map`, so pooled
  and serial runs give the same solutions. The per-design drift `p4_*`
  fields perturb the same slope block.
- The record retains the witness of each backend: the real design and
  offsets, the seed, and all 17 resimulated log ratios per fold.
- `--check` recomputes every P4 summary from that witness:
  - The real design must round to the atlas record's nine-decimal slopes and
    six-decimal offsets.
  - Each unperturbed resimulation must lie within compare()'s contrast
    tolerance of the retained prediction.
  - The fold solutions and perturbations are solved again from the seed,
    so the parameter drifts are fresh. They agree within 1e-2 relative,
    since the perturbation, not LAPACK roundoff, sets them.
  - The moves, ranks and moved-prediction values follow exactly from the
    retained log ratios.
- Rerunning the resimulation itself needs the captured lane designs, about
  3 minutes on one worker, so the gate checks the witness instead.

## Results

`result.json` was written on the build host. That host runs AOCL numpy
2.5.4, Python 3.14.7 and pyadic 0.3.0; long double there is x87, with a
64-bit significand.

**Worst-conditioned designs.** spread is the largest column norm over the
smallest.

| Design | m x n | kappa(A) | kappa(A D) | spread | rho |
| --- | --- | ---: | ---: | ---: | ---: |
| Kingston lane 4 `axis_tilt_plus_mean`, fold 0 | 9 x 6 | 4.70e5 | 3.58e5 | 2.7 | 6.2e-6 |
| Fez lane 4 `axis_tilt_plus_mean`, fold 1 | 11 x 6 | 4.40e5 | 3.37e5 | 2.5 | 1.8e-5 |
| Fez lane 5 `detuning_and_axis_tilt`, fold 7 | 11 x 10 | 2.96e5 | 694 | 3676 | 6.0e-6 |
| Fez lane 2 `detuning_and_axis_tilt`, fold 4 | 11 x 10 | 1.56e5 | 136 | 3593 | 9.5e-6 |
| Kingston lane 5 `axis_tilt_plus_mean`, full | 10 x 6 | 9.28e4 | 4.86e4 | 4.6 | 1.3e-5 |
| Fez lane 4 `axis_tilt_plus_mean`, full | 12 x 6 | 7.05e4 | 5.31e4 | 2.7 | 1.8e-5 |
| Fez lane 2 `detuning_and_axis_tilt`, full | 12 x 10 | 5.90e4 | 58 | 3352 | 1.2e-5 |
| Kingston lane 0 `zz_symmetric_plus_mean`, fold 2 | 9 x 5 | 2.54e4 | 12.9 | 5827 | |

Equilibration splits the designs in two:
- Where the detuning block's scale meets other families, a spread of about
  3e3, it removes kappa by up to 2e3x.
- On `axis_tilt_plus_mean` it gains only 1.3x. There the tilt block is
  nearly collinear with the lane constant.

**Errors against x* on the worst design** (Kingston lane 4
`axis_tilt_plus_mean`, fold 0; |x*| from 0.0029 to 1985):

| Method | componentwise rel | max abs | normwise rel | margin |
| --- | ---: | ---: | ---: | ---: |
| normal equations | 5.2e-6 | 1.0e-2 | 5.2e-6 | 9.5 |
| Householder QR (numpy) | 1.1e-11 | 1.4e-8 | 6.9e-12 | 7.1e6 |
| SVD lstsq (current) | 3.8e-10 | 1.4e-8 | 6.9e-12 | 4.3e5 |
| QR on A D | 1.1e-11 | 1.4e-8 | 6.9e-12 | 7.1e6 |
| SVD lstsq on A D | 3.7e-10 | 1.4e-8 | 6.9e-12 | 4.3e5 |
| Householder, p = 53 | 2.2e-11 | 3.3e-8 | 1.6e-11 | 3.0e6 |
| Householder, p = 64 (= x87 long double, bit for bit) | 7.3e-15 | 1.0e-11 | 5.0e-15 | > 1e8 |
| Householder, p = 106 | 1.4e-27 | 9.6e-25 | 4.8e-28 | > 1e8 |
| Householder, p = 113 | 1.1e-29 | 1.1e-26 | 5.5e-30 | > 1e8 |

Margin is tolerance over error, smallest over the components. Over all
designs:
- QR on A D equals QR on A to every recorded digit. Householder QR commutes
  exactly with power-of-two column scaling.
- SVD on A D is more accurate than SVD on A on 1449 of 2716 designs. On
  designs with spread >= 100 the median gain is 19x. Even so, both stay at
  least 1.2e4 times inside tolerance.
- The smallest current-solver (SVD) margin is 1.2e4, on the Kingston lane-4
  `axis_tilt_plus_mean` full fit.
- The smallest normal-equations margins are 3.9, on a parameter, and 1.3, on
  a held-out prediction.

**P4.** Contrast moves of the resimulated held-out predictions on
`axis_tilt_plus_mean`, lane 4:

| | Fez | Kingston |
| --- | ---: | ---: |
| prediction that moved between substrates in #161 | `[1]` | `[0]` |
| its move at 3.5e-13 of the slope block | 2.0e-4 | 3.5e-5 |
| its move at 1.3e-14 of the slope block | 1.6e-5 | 1.1e-6 |
| its rank among the lane's held-out edges, by move | 1 of 12 | 1 of 10 |
| fold-parameter drift at 3.5e-13, that edge / median edge | 1.2e-4 / 4.7e-6 | 1.1e-4 / 4.6e-6 |
| first measurement, whole design perturbed: move at 3.5e-13 / 1.3e-14 | 5.7e-4 / 2.1e-5 | 1.9e-4 / 7.7e-6 |
| largest host-vs-retained difference of the unperturbed prediction | 9.2e-7 | 4.3e-7 |

The two predictions that moved between AOCL, OpenBLAS and Kaggle in #161
are the most sensitive fold of their lanes, by a factor of about 25 in
parameter drift. Holding the constant column fixed removes 65 to 81 percent
of the moves the first measurement reported. At the median measured design
difference the least squares moves Kingston `[0]` by 1.1e-6, inside the
observed 1e-6 to 3e-6, and Fez `[1]` by 1.6e-5, above it.

The fold parameters behind them stay inside their own tolerance,
eps kappa_fold^2 |x|, which is 1e-2 or more at |x| >= 337. The contrast
vector does not. Under #207's normwise rule its tolerance is
eps kappa_fold^2 max|vector|:

| | Fez | Kingston |
| --- | ---: | ---: |
| contrast tolerance | 9.5e-5 | 7.3e-5 |
| margin at the worst measured difference | 0.47 | 2.1 |
| margin at the median measured difference | 6.0 | 66 |
| first measurement (whole design): worst / median | 0.17 / 4.5 | 0.39 / 9.5 |

Kingston's margin at the worst measured difference changes class, from a
core-329 failure (0.39) to a pass (2.1). Fez stays a failure (0.47): a
substrate whose slope block moved by the worst measured amount on this model
would still fail core-329 on Fez's contrasts, with every solver and every
precision in this study. The measured AOCL-to-OpenBLAS difference on this
model's slope block is about 1e-14, not 3.5e-13, and it moves Fez `[1]` by
2.2e-6 (see [Substrate split of the P4 moves](#substrate-split-of-the-p4-moves)).

Over all 2716 designs, the worst-size slope perturbation leaves the smallest
parameter margin at 2.49, on Fez lane 6 `detuning_and_axis_tilt`, fold 9.
The whole-design perturbation gave 1.26, on Fez lane 6
`zz_symmetric_plus_mean`, fold 4.

**Ladder.**
- The error at p = 64, 106 and 113 is at most 0.33 of 100 * 2^-(p-53) times
  the p = 53 error. The median ratio to 2^-(p-53) times the p = 53 error is
  1.0.
- The p = 53 R factor matches `np.linalg.qr` within 2.5 ulps of ||A|| on
  designs with kappa <= 100, and within 13.4 ulps on all designs.

**Cross-substrate check.** `--check` passes against this record under CI's
numpy, built with scipy-openblas 0.3.34, in a uv venv on Python 3.14.7 with
the requirements.txt pins.
- Between the two builds, an error raised to its floor (eps kappa, or
  eps kappa^2 for the normal equations, in the field's units) moves by at
  most 13.6x. ROUNDOFF_FACTOR is 64.
- Below the floor, single componentwise errors move by up to 200x, so the
  check does not compare them there.
- Every condition number, norm and rho agrees to nine digits.

## Verdict

- **P1 holds for QR and SVD and fails as stated for the normal equations.**
  - QR and SVD errors stay at most 0.19 of m n eps (kappa + kappa^2 rho).
  - On the graded case, the normal equations lose 1.0e8 times more than QR,
    against a required kappa / 100 = 3.4e5.
  - Over designs with kappa >= 1e4, the median normal-equations-to-QR ratio
    is 25.
  - The normal-equations bound m n eps kappa^2 holds at 0.46 on AOCL. It
    fails at 2.28 on OpenBLAS, on Kingston lane 5 `lane_mean`, fold 5
    (kappa 1, rho 89): the mean of nine offsets whose mean is near zero.
    The stated bound left out the residual term that its QR counterpart
    carries. The normal equations' forming of A^T b loses
    eps kappa^2 (1 + rho), not eps kappa^2.
  - That clause depends on the LAPACK build, so `--check` prints it for the
    host and compares every other clause.
- **P2 holds.**
  - kappa(A D) stays at most 0.5 of 2 sqrt(n) kappa(A) on every design.
  - The synthetic column-scaled case drops from 7.7e9 to 4.2.
  - The 854 designs with spread >= 100 gain a median 341x.
  - On the worst design, kappa(A D) is 3.58e5 against kappa(A) = 4.70e5, a
    1.3x gain, under the predicted 3x. Its conditioning is collinearity,
    which no column scaling can remove.
- **P3 holds.**
  - Each precision step cuts the rounding error as 2^-(p-53).
  - The emulator is validated bit for bit against IEEE double and x87 long
    double.
  - No float64 value is more than 1.8e-4 of its tolerance from x*. The
    p = 53 held-out predictions stay at margins of 8.1e4 or more. Extra
    precision therefore changes nothing a 1.5e-6 tolerance sees.
- **P4 is falsified.**
  - At the worst measured design difference on the slope block, the least
    squares alone moves the two #161 predictions by 2.0e-4 (Fez) and 3.5e-5
    (Kingston), over the 1e-6 falsifier. The verdict is the same as with the
    whole-design perturbation (5.7e-4 and 1.9e-4).
  - At the median difference it moves them by 1.6e-5 and 1.1e-6 (first
    measurement: 2.1e-5 and 7.7e-6).
  - Inference, rated likely: the cross-substrate contrast moves are
    least-squares amplification of the substrate's design differences.
    - For: the two moved predictions are the most sensitive fold of their
      lanes, rank 1 of 12 and rank 1 of 10.
    - Unmeasured: the actual design difference on this model. Kingston's
      median-size move, 1.1e-6, matches the observed moves. Fez's, 1.6e-5,
      exceeds them, so Fez's real difference must be near 1e-15 or smaller.
    - Falsifier: rebuild the real lane-4 designs under OpenBLAS numpy.
      Resimulate the OpenBLAS fold solution under AOCL, and the AOCL fold
      solution under OpenBLAS. The two runs split each move between the
      solve and the resimulation, and a move that stays when only the
      resimulation substrate changes refutes the attribution.
    - Measured in
      [Substrate split of the P4 moves](#substrate-split-of-the-p4-moves):
      the slope block differs by about 1e-14. The solve share is 2.2e-6
      (Fez) and 5.4e-7 (Kingston), and the resimulation share is below
      1e-15, so the attribution holds.
- **P5 holds.**
  - The p-adic reconstruction equals the Fraction solution on all 2716
    designs.
  - Every design has full column rank modulo all three primes.
  - The rank-deficient control has rank 3 of 4 modulo each.
- **P6 holds.**
  - The wheel solve equals Fraction elimination, with every component
    finite, on all 448 full-fit and worst-fold designs.
  - The consistent rank-deficient control gives bottom in all four
    components where Fraction elimination raises ZeroDivisionError.
  - The wheel self-test also gives bottom in every component on 20 singular
    consistent Gram systems, and equality with Q on 20 nonsingular ones.

**Recommendation.**
- Keep `np.linalg.lstsq` in float64.
- The current solver's distance from the exact solution is the most that
  column equilibration or any precision step could recover, and it stays at
  8.2e-5 of tolerance on every value:
  - equilibrated paths: 8.3e-5;
  - Householder at p = 53: 1.8e-4.
- No step moves a retained value by tolerance / 10.
  - This covers parameters and linear predictions directly.
  - It covers resimulated contrasts through P4's measured amplification:
    contrast move over parameter drift is at most 3.6 over every lane-4
    fold of `axis_tilt_plus_mean`.
  - On those folds, every float64 solver lies within 1.8e-8 of x* in every
    parameter, so two solvers differ by at most about 4e-8. That bounds a
    solver-induced contrast move near 1.5e-7, against a tenth of the
    contrast tolerance, 7e-6.
- The dominant error source is the conditioning of the models themselves.
  On `axis_tilt_plus_mean` the tilt block and the lane constant are nearly
  collinear. Its folds turn substrate design differences of 1e-14 to 1e-13
  into contrast moves of 1e-6 to 2e-4.
- Neither a better-conditioned algorithm nor extra precision changes the
  sensitivity of the problem.
- #207's normwise contrast rule admits the moves at the median measured
  design difference (margins 6.0 and 66). At the worst measured difference it
  admits Kingston's (margin 2.1) and not Fez's (margin 0.47). On the
  measured OpenBLAS build both pass, at core-329 margins of 31.7 and 72.6
  ([Substrate split of the P4 moves](#substrate-split-of-the-p4-moves)).
- The lever is the model or the tolerance, not the arithmetic.
  - An exact change of variables leaves x*, its sensitivity to the design,
    and the resimulated contrasts unchanged.
  - Three options change the outcome:
    - drop `axis_tilt_plus_mean`, whose fold condition near 4.5e5 comes from
      the tilt-constant collinearity;
    - regularize it, which changes the estimator;
    - bound its contrast outputs by a sensitivity measured on the lane's own
      design, as this study's resimulation does.
- For anyone re-deriving fits from `result.json`, the retained rounding of
  slopes and offsets dominates everything here, at up to 631 tolerances.

## Substrate split of the P4 moves

`scripts/axis_tilt_substrate_split.py` runs P4's falsifier on two real
substrates. It writes `substrate_split.json`.

**Prediction, stated before measuring.** P4's worst-perturbation moves
(#213) are 2.0e-4 (Fez `[1]`) and 3.5e-5 (Kingston `[0]`). They come from a
random slope-block perturbation of 3.5e-13.
- If the solve share between AOCL and OpenBLAS stays below a tenth of those
  moves, the issue is moot on these substrates.
- If core-329's margin on OpenBLAS comes out at or below 2, the issue stands.
- A resimulation share comparable to the solve share refutes P4's
  least-squares attribution.

**Substrates.** Both run on the build host: Python 3.14.7, numpy 2.5.4,
scipy 1.18.1 and qiskit 2.5.2.
- S is the Arch numpy on AMD AOCL BLAS 5.3 (BLIS and libflame).
- T is a uv venv with the pip numpy on scipy-openblas 0.3.34 (CI's numpy,
  scipy and BLAS pins). Its qiskit stays at the host's 2.5.2, so BLAS is the
  only difference.
- The retained atlas record, which core-329 compares against, comes from a
  third substrate: the Kaggle kernel, with numpy 2.1.3 and Python 3.13.15.

**Method.**
- Each substrate captures lane 4 of both backends (`--capture`) and solves
  every `axis_tilt_plus_mean` fold.
- It resimulates the held-out edge at four solutions:
  - its own;
  - the other substrate's;
  - its own lstsq of the other's fold problem;
  - its own lstsq of the other's design with its own offsets.
- The four cells split each move: full = own_T - own_S, solve =
  resim_S(x_T) - own_S, resimulation = resim_T(x_S) - own_S, interaction =
  full - solve - resimulation.
- Two captures on each substrate agree bit for bit, so no run-to-run term
  enters the split.

**Results**, the moved prediction of each lane, base S:

| | Fez `[1]` | Kingston `[0]` |
| --- | ---: | ---: |
| slope-block difference, that fold (relative 2-norm) | 1.0e-14 | 1.2e-14 |
| largest lane-4 design difference, any model | 3.5e-13 (`zz_symmetric` fold 11) | 2.0e-13 (`zz_symmetric` fold 9) |
| full move | 2.20e-6 | 5.38e-7 |
| solve share | 2.20e-6 | 5.38e-7 |
| design share (T's slope block alone) | 2.05e-6 | 5.38e-7 |
| resimulation share | -4.4e-16 | -2.4e-16 |
| full move / core-329 contrast tolerance | 0.023 | 0.0074 |
| P4's random move scaled to the measured difference | 5.8e-6 | 1.2e-6 |
| design share / scaled random move | 0.35 | 0.45 |
| core-329 margin, S / T | 95.2 / 31.7 | exact / 72.6 |

- Over every fold of both lanes, the full move stays at most 0.023 of the
  tolerance.
- The resimulation share and the interaction stay below 1.2e-15.
- The core-329 margins equal what core-329 prints on each substrate. They
  measure the distance to the Kaggle record, not the S-to-T move.

**Verdict.**
- The solve share is 91 times (Fez) and 65 times (Kingston) below P4's
  worst-perturbation moves, under the tenth that the prediction set.
- core-329 passes on T at margins of 31.7 and 72.6.
- The resimulation contributes nothing measurable, so P4's least-squares
  attribution holds.
- #213's worst case puts the largest lane-4 design difference on this
  model's slope block. That difference sits in the `zz_symmetric` block.
  The `axis_tilt` block moves by 9.5e-15 (Fez) and 1.1e-14 (Kingston) on
  the full designs, and by 8.2e-15 to 1.28e-14 across the folds. That is
  near the median over all designs.
- Scaled linearly along the measured direction, a 3.5e-13 tilt-block
  difference would give Fez a margin near 1.3. That figure is a
  hypothetical that no measured substrate reaches.

## Gates

- core-489: `--check` in normal and optimized Python, pr tier, 64 s of CPU
  time with one worker.
- core-492: `--self-test` in both modes, pr tier, 2.1 s.
- core-493: `gororoba_quantum/wheel_algebra.py --self-test` in both modes,
  pr tier, 3.9 s. Its axiom cases run in chunks through
  `parallel.ordered_map`.
- core-458: `scripts/axis_tilt_substrate_split.py --check` and
  `--self-test` on `substrate_split.json` in both modes, pr tier, 3.5 s.
  - The check binds the atlas record by sha256.
  - It requires each retained slope block and offset vector to round to the
    atlas lane.
  - It requires each own fold solution to equal this host's lstsq within
    m n eps (kappa + kappa^2 rho).
  - It recomputes every share, fraction and margin exactly from the retained
    log ratios.
  - The captures rerun the simulation, about a minute per substrate, so the
    gate checks the witness instead.
  - It binds the P4 moves of `result.json` through `study_inputs()`. A
    regenerated study record fails core-458 until `--combine` rewrites
    `substrate_split.json`.

`--check` recomputes everything but the pyadic lifting, the lane-4 bridge
and the resimulations. Those need pyadic, which CI does not pin, and the
captured real designs, which cost about 3 minutes on one worker. The check
verifies the p-adic witness with integers and recomputes the P4 summary from
its retained witness.
