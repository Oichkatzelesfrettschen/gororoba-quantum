# Executed-order analysis of the bracketed twin contrasts

Status: preregistered 2026-11-15 on the owner's ruling (issue 791); the estimator and its tests exist, the integration into the
decision path and the power tables do not, and no Tuna-17 job has run. The strict gate (`order_gate`) stays the series rule until
the integration lands and takes its review round.

## Why

The bracketed Tuna-17 series needs every one of its 35 batches to execute in the requested order for the strict gate to keep
the decision. The retained predecessor ran 7 of 19 batches out of order by `queued_at` (batches 01, 06, 08, 10, 12, 15, 16).
If batches reorder independently at 7/19, all 35 stay in order with probability 1.0e-7 (8.0e-4 at half the rate, 3.4e-2 at a
quarter, an even chance only at 0.020 per batch). The series as written predicts `unresolved_order` with 2.6 million shots
spent (`results/quantum_inspire/cases/pathion_one_cz_null_bracketed_tuna_17/CASE.md`, "Pre-flight record").

A second measurement of the same shape: on the hosted QX emulator on 2026-11-15, 2 of the 4 batches of five circuits executed
out of the requested order by `queued_at` (CASE.md, "QX remote"), so reordering is not particular to the Tuna-17 device or to
three-circuit batches.

## Model

A twin batch reads its contrast t = P1 - P0 with the coin-1 twin and the coin-0 twin in consecutive jobs, so a drift g of the
selector offset between consecutive jobs adds g x s, with s = +1 when coin 1 executes after coin 0 and -1 otherwise. The
requested forward and mirror rounds alternate s per template and cancel the term in the pooled contrast. A reordered batch
flips its own s; the cancellation is then broken, not lost: s is known from the stamps (`queued_at` follows the previous job's
`finished_at` by 0.03 to 0.19 s in the retained batches, a measured provider behavior and no documented guarantee).

`scripts/qi_pathion_one_cz_null_executed_order.py` fits `v_b = t_T + g s_b + e_b` by weighted least squares with one drift g shared
by every twin batch and one contrast t_T per template. Its module docstring states the closed form. A balanced order returns the
pooled mean and error, so the estimator costs nothing when the platform keeps the order. `adjusted_rows` gives the (value, error)
rows that the preregistered rule pools: values reduced by g s and errors multiplied by f_T, so the pooled error carries the
uncertainty of g.

## Decision rules (preregistered)

1. The decision reads the adjusted rows when the stamps of every twin batch are present and pairwise distinct inside a batch; a
   missing or tied stamp reads `unresolved_order` (the strict gate's rule for those inputs stays).
2. A series whose twin batches all share one executed s has no separable drift and reads `unresolved_order_confounded`.
3. A template whose own drift (`template_drift`) departs from the shared g by more than 3 times the error of the difference reads
   `unresolved_drift_heterogeneity`: the common-drift hypothesis failed for that run, and the label the rule would have read
   stays beside it.
4. The batch heterogeneity gates keep their thresholds at the batch counts of the layout (16.266 at 3 degrees of freedom); the
   fit spends one more degree of freedom, so the unchanged threshold is conservative against false trips.

## Operating characteristics (computed 2026-11-15, 20,000 series per rate, equal batch errors 0.005524, 4 templates x 4 replicates, independent reordering)

| reorder rate per batch | P(confounded) | mean error of b0's contrast against the balanced error | 95th percentile |
|---|---:|---:|---:|
| 0 | 0 | 1.000 | 1.000 |
| 0.05 | 0 | 1.007 | 1.035 |
| 0.10 | 0 | 1.013 | 1.038 |
| 0.20 | 0 | 1.026 | 1.155 |
| 0.37 (the predecessor's) | 0.0002 | 1.043 | 1.183 |

The standard error of g is 0.0014 per unit sign at the balanced design. At the predecessor's rate the strict gate decides with
probability 1.0e-7 and this estimator decides with probability 0.9998 at an error 4 percent above the balanced one on
average. This is a model computation (hypothesis: independent reordering, equal errors, a drift linear in the sign), not a
measurement.

## Not yet done (scope cut, removal condition)

- Integration: `evaluate` in `scripts/qi_pathion_one_cz_null_bracketed_cases.py` still applies the strict gate. Removal
  condition: a change that maps the stamps to `executed_sign`, replaces the twin rows by `adjusted_rows`, adds the three labels
  and keeps the strict result beside it, reviewed before the series is approved.
- Power under reordering: the 82.1 / 85.3 percent power of the case is computed without reordering; the pricing and operating
  characteristic simulators need a reordering world.
- Base contrasts: the base batches (three circuits) also reverse in the mirror rounds; whether their arm contrasts carry an
  order term is untested, and this note covers the twin contrasts only.
- The common-drift hypothesis: tested by rule 3 on the run itself and by nothing before it.

## Falsifiers

A retained series whose `template_drift` values differ beyond rule 3; reordering that clusters in whole waves (then the
independence model understates the confounded fraction, and `P(confounded)` must be recomputed from the clusters); stamps that
no longer follow the previous job's `finished_at`.
