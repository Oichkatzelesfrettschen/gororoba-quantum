# Base and calibration batches of the bracketed series: executed-time weights, a drift monitor and validation

Status: preregistered 2026-11-15 on the owner's ruling (issue 791, task 881-B). The estimator, the monitor and their tests exist in
`scripts/qi_pathion_one_cz_null_executed_order.py` (`constrained_weights`, `level_at`, `drift_monitor`); the integration into
`evaluate`, the injection harness and the power tables do not, and no Tuna-17 job has run. The twin batches take the position-offset
fit of [bracketed-executed-order-analysis.md](bracketed-executed-order-analysis.md); this note covers the 16 base batches and the 3
calibration batches, where position inside a batch does not enter and execution time does.

## Why a rule is needed

A base contrast is the raw selector statistic of one circuit (`pca.selector_stat`), so it is a level and not a difference. A level
read at a time t differs from the same level read at the twins' time by the drift accumulated between them. The retained
predecessor places the mean time of a template's two base batches 0.15 to 0.31 h from the mean time of its twin batches; at the
largest plausible drift of 0.01 per hour that is a shift of 0.0015 to 0.0031, 9 to 19 percent of the 0.0164 contrast, and at the
0.0017 per hour that b0's two base replicates show it is 0.0003 to 0.0005 (computed from `queued_at`). The retained data cannot
separate such a term from replicate scatter: each template has two base batches, and the pooled slope against position
(-0.0176 per rank, z -5.5) loses its significance when b0 is omitted (z -1.21).
The label order does not cancel the term by itself: a forward-and-mirror order
cancels a linear drift only when the executed times are symmetric about the reference, and a platform that reorders breaks that.
A published analysis of a fixed-order acquisition states the same degeneracy (arXiv 2608.18153v1, Sec. IV, Eqs. 15 and 16: a linear
additive drift enters the combined score as S_obs = S_true + 2 beta and no model-independent correction exists without randomized
or counterbalanced orders).

## Estimand and model

For template T with R base replicates read at executed times t_r (the `queued_at` of the base circuit) with errors se_r, and the
reference time tau_T (the mean executed time of the template's twin circuits), the estimand is the base offset mu_T at tau_T:

    v_r = mu_T + g_1 (t_r - tau_T) + ... + g_k (t_r - tau_T)^k + e_r,   var(e_r) = se_r^2.

hypothesis: the selector offset that the twins and the base circuit read is one quantity, and its drift over a template's span is
a polynomial of low order. Linear drift (k = 1) is the preregistered decision model; a failed monitor reads
`unresolved_drift_model`. Quadratic weighting (k = 2) is a tested numerical capability with no decision path.

## Estimator

mu_hat = sum_r w_r v_r is unbiased for mu_T for every drift coefficient exactly when B^T w = e_0, with B_rj = (t_r - tau_T)^j for
j = 0..k: the weights sum to 1 and annihilate each power of the time offset. Minimizing var(mu_hat) = w^T C w with C = diag(se^2)
under that constraint (Lagrange) gives w = C^-1 B (B^T C^-1 B)^-1 e_0, the intercept at tau_T of the weighted regression. For k = 1:

    var(mu_hat) = (1 / W) (1 + (t_w - tau)^2 / S_tt),   W = sum 1/se^2,   t_w = sum(t / se^2) / W,   S_tt = sum((t - t_w)^2 / se^2) / W.

The cost over the plain inverse-variance mean is 1 + (t_w - tau)^2 / S_tt: nothing when the weighted mean time is the reference,
large when the replicates cluster in time; fewer distinct times than k + 1 leave the polynomial unseparated (`ConfoundedOrder`,
label `unresolved_base_drift_confounded`). The two options the owner named are the special cases: the plain pool is k = 0, the
common-drift time fit is k = 1; the batch heterogeneity gates stay as the check of the fit (16.266 at 3 degrees of freedom; the fit
spends degrees of freedom, so the unchanged threshold is conservative). `tests/scripts/test_qi_pathion_one_cz_null_executed_order.py`
pins the moment conditions, the exact recovery under a linear and (with k = 2) a quadratic drift where the plain mean is biased, the
closed-form variance and the rank condition; dropping the drift columns fails four of them.

## Calibration batches

The 3 X-only calibration batches (3, 3 and 2 circuits) are single measurements, so no drift fit exists for them. Each carries a
systematic term sigma_sys = g_up |t_cal - tau|, with g_up the 95 percent upper bound of |slope| from the monitor below, added in
quadrature to its standard error; a calibration estimate whose sigma_sys exceeds its standard error reads
`unresolved_calibration_drift` and is reported beside the decision, not inside it.

## Monitor (preregistered pass or fail of the drift model)

Every batch carries readout-0 and readout-1 circuits, so the bracket offset c_b of each of the 35 batches at its executed time is a
free series of the selector offset. `drift_monitor` fits a line by weighted least squares and tests the residual chi-square with
n - 2 degrees of freedom at alpha 0.001 (`MONITOR_ALPHA`); a residual above the threshold means a step, burst or curve (the Quantum
Inspire processors show error bursts and days-to-weeks excursions, arXiv 2602.18388v2), so the linear model is refused and the
decision reads `unresolved_drift_model`; the slope bounds g_up for the calibration batches and is reported beside the decision. Its
comparison with the drift that the twin and base fits imply stays a scope cut: the twin fit counts executed rank, `level_at` returns no
slope, and no covariance-aware statistic in common units is preregistered. Spectral and structure-function thresholds
at n = 35 follow arXiv 1907.13608v3 and need their own simulation before preregistration. hypothesis: the bracket offset drifts with
the selector offset the contrasts read; falsifier: a series whose slope disagrees with the contrast-implied slope, once that comparison
is defined.

## Validation before the real series

1. Freeze: the pipeline (weights, monitor, labels, thresholds) and its commit digest are fixed before any Tuna-17 result is read.
2. Blind: a hidden offset drawn from a QRNG value is added to the b0 base counts' statistic and revealed after the freeze.
3. Inject: run the frozen pipeline on retained raw counts (the predecessor series and the hosted QX run) with a synthetic contrast
   of 0.016 injected by flipping shots at the matching rate, 2,000 injections seeded from a QRNG draw; measure the bias, the
   false-reject rate at zero injection (accepted when its exact binomial upper bound is at most the preregistered alpha) and the
   power at 0.016 (accepted at 0.8 or more).
The harness is not built (scope cut below).

## Randomized order and anytime-valid inference (the added layer)

Reading of the stage-3 documents (arXiv 1603.05766v1, 2406.06488v1, 1810.08240v9, 2010.09686v7 and the Monte Carlo p-value note):
every p-value follows the (1 + count) / (1 + b) convention, never zero. Drawing each batch's requested twin order from a QRNG
value gives an unbiased contrast without a drift model only if the platform's reordering is independent of that draw (a table
from `queued_at` tests it). The exact resolution is the limit: a template with 4 waves has 2^4 sign patterns and a smallest
two-sided p of 0.125. Independent sign assignment gives minimum exact two-sided p-values 2 / 2^n: 0.125, 0.03125 and 0.0078125 for 4, 6
and 8 waves. The Bonferroni level for 16 contrasts, 0.003125, stays below the 8-wave floor. A sweep simulation of the test's power is not
retained in this tree, so no power figure is stated here. Range-only confidence sequences need 50 to 460 waves. The layer
therefore cannot carry the decision of this 4-wave design: it enters only as a pooled global-null diagnostic (a sign-flip test over
the 16 twin batches, floor 2^-15) and as a requirement for any successor. The wave count follows the level: 6 waves per template
reach a two-sided floor of 0.03125, enough for an unadjusted 0.05 per template only; 8 waves (floor 0.0078) serve 0.05 over the four
templates (Bonferroni 0.0125); 10 waves (floor 0.00195) serve 0.05 over 16 contrasts (0.003125). Sequential
estimation of the selector offset (arXiv 1207.1655v2) reduces to the generalized least squares and Kalman filter of this model and
is parked.

## Not done (scope cut, removal condition)

- Integration: `evaluate` still applies the strict gate. Removal: a reviewed change that reads executed times, applies
  `level_at` per template, runs the monitor, adds the labels `unresolved_base_drift_confounded`, `unresolved_drift_model` and
  `unresolved_calibration_drift`, and keeps the strict result beside them.
- The injection and blinding harness and its acceptance run (a remote host under the build-host ruling).
- Power under reordering for the base contrasts and of the sign-flip layer; spectral monitor thresholds at n = 35.
- The slope comparison between the monitor and the twin and base fits (units, covariance and statistic).
- The QRNG draw and indices of the injection and blinding harness: its commit takes them from a draw file under the seed rule of
  `AGENTS.md` and cites each index in order.
- Per-circuit execution times: `queued_at` is a job-level stamp that follows the previous job's `finished_at` by 0.03 to 0.19 s; a
  circuit's start inside a job is not recorded, which the weights treat as a time error of that size.

## Falsifiers

A retained or new series whose monitor refuses the linear model on every batch; a base replicate set whose times cluster (S_tt
small) so that the cost 1 + (t_w - tau)^2 / S_tt exceeds 2; reordering that depends on the requested order (the randomization
premise); a bracket slope that disagrees with the contrast-implied slope.
