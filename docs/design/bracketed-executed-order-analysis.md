# Executed-order analysis of the bracketed twin contrasts

Status: preregistered 2026-11-15 and confirmed by the owner's ruling of 2026-11-16 23:52Z on issue 791 ("Preregistered
executed-order analysis": the analysis is registered on the order the provider executed, recorded per job, so a reordered
batch stays usable and the strict gate decides nothing). The estimator, the decision integration (`evaluate` of
`qi_pathion_one_cz_null_bracketed_cases`), the base-batch rule of [bracketed-base-contrast-weights.md](bracketed-base-contrast-weights.md)
and their tests exist; the power tables under reordering are in the case's `prediction.json`, and no Tuna-17 job has run. The strict reading (`order_gate`) stays in the record beside the decision.

## Why

The bracketed Tuna-17 series needs every one of its 35 batches to execute in the requested order for the strict gate to keep
the decision. The retained predecessor ran 7 of 19 batches out of order by `queued_at` (batches 01, 06, 08, 10, 12, 15, 16).
If batches reorder independently at 7/19, all 35 stay in order with probability 1.0e-7 (8.0e-4 at half the rate, 3.4e-2 at a
quarter, an even chance only at 0.020 per batch). The series as written predicts `unresolved_order` with 2.6 million shots
spent (`results/quantum_inspire/cases/pathion_one_cz_null_bracketed_tuna_17/CASE.md`, "Pre-flight record").

## Model

A twin batch reads its contrast t = P1 - P0 with the coin-1 twin and the coin-0 twin in consecutive jobs, so a drift g of the
selector offset per position adds g x x, with x the executed position of the coin-1 twin minus that of the coin-0 twin among
the circuits of the batch, read from `queued_at` (x = +1 forward and -1 mirror when the order is kept, and for example -3 when
the coin-1 twin runs three places before the coin-0 twin, as in batch 02 of the hosted QX run). The requested rounds alternate x
per template and cancel the term in the pooled contrast. A reordered batch changes its own x; the cancellation is then broken,
not lost: x is known from the stamps (`queued_at` follows the previous job's `finished_at` by 0.03 to 0.19 s in the retained
batches, a measured provider behavior and no documented guarantee).

`scripts/qi_pathion_one_cz_null_executed_order.py` fits `v_b = t_T + g x_b + e_b` by weighted least squares with one drift g
shared by every twin batch and one contrast t_T per template; its module docstring states the closed form and
`executed_offset` reads x from a batch's stamps. A balanced order returns the pooled mean and error, so the estimator costs
nothing when the platform keeps the order. `adjusted_rows` gives the (value, error) rows that the preregistered rule pools:
values reduced by g x and errors multiplied by f_T, so the pooled error carries the uncertainty of g.

## Decision rules (preregistered)

1. The decision reads the adjusted rows when the start stamp of every circuit of every batch is ISO 8601 text with a UTC offset
   (`stamp_instant`: ranked by integer-microsecond instant, so differently written stamps of one instant tie) and no two
   circuits of a twin batch share an instant; a stamp that is missing, null, not text, not ISO 8601 or without an offset in
   any batch, a tie inside a twin batch or an empty stamp mapping reads `unresolved_order`, and no exception reaches the caller.
2. A series in which every template has one x in all its twin batches has Sxx = 0 and no separable drift, even if the templates
   differ in direction: it reads `unresolved_order_confounded`.
3. A template whose own drift (`template_drift`) departs from the shared g by more than 3 times the error of the difference
   (`template_drift_difference_se`, sqrt(1 / own - 1 / Sxx): the shared g is the own-drift average weighted by own / Sxx, so
   cov(own, g) = var(g))
   reads `unresolved_drift_heterogeneity`: the common-drift hypothesis failed for that run, and the label the rule would have
   read stays beside it.
4. The template contrasts share g, so they are correlated: cov(t_T, t_U) = x_T x_U var(g). The decision pools the 6-CZ twin
   contrasts and tests their agreement by generalized least squares and sizes r - m with cov(t0, d) (`decide_correlated`;
   a diagonal covariance reproduces `rule.decide_estimates`). The enumeration at a flip rate of 0.25 gives a largest
   correlation of 0.13 to 0.15 in fixtures of three reordered templates and a true-to-reported error ratio of d between 0.95 and
   1.05 (5th to 95th percentile; extremes 0.69 and 1.46): the independent pool understates the error in 24 percent of series
   and overstates it in the rest, so the term is included (CASE.md, item 6).
5. The batch heterogeneity gates keep their thresholds at the batch counts of the layout (16.266 at 3 degrees of freedom); the
   fit spends one more degree of freedom, so the unchanged threshold is conservative against false trips.

## Operating characteristics of the twin batches (exact enumeration, no random draw)

`operating_characteristics(rate)` enumerates the 2^16 flip patterns of the 16 twin batches (4 templates x 4 replicates, requested
x = +1, -1, +1, -1, equal batch errors), each batch flipping its sign independently with probability `rate`:

| flip rate per batch | P(confounded) | mean error of one template's contrast against the balanced error | 95th percentile |
|---|---:|---:|---:|
| 0 | 0 | 1.000 | 1.000 |
| 0.05 | 0 | 1.007 | 1.035 |
| 0.10 | 0 | 1.013 | 1.038 |
| 0.20 | 1e-5 | 1.026 | 1.155 |
| 0.25 (measured: 2 of 8 predecessor twin batches flipped; 3 of 12 with PR 927's hosted-QX batches) | 2.4e-5 | 1.032 | 1.168 |
| 7/19 (the predecessor's) | 1.4e-4 | 1.043 | 1.183 |

`P(confounded)` equals (2 r^2 (1 - r)^2)^4 (a test pins it): a template ends one-directional with probability 2 r^2 (1 - r)^2,
which is 0.109 at 7/19, and the series is confounded only when all four do. These figures cover the twin batches under a
model (hypothesis: independent flips, equal errors, a drift linear in the offset). The predecessor's retained twin batches give the measured
flip rate: 2 of 8, with executed offsets -2 and +1. The hosted-QX run adds 1 of 4 (offset -3), for 3 of 12; its run directories
`results/quantum_inspire/runs/2026-11-15T184810Z-pathion_one_cz_null_bracketed_qx-batch-00..03` and
`results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json` arrive with the stacked PR 927, so the QX share of that
count resolves in the tree only after PR 927 lands. The three flipped batches executed at offsets -2, +1 and -3 against
requested +1, -1 and +1; the strict gate's 7 of 19 counts any permutation of a batch, readouts included, and overstates the twin-flip rate.
Under the strict gate the 16 twin batches alone all stay intact with probability 0.75^16 = 0.010 at 0.25. They are not the probability that
the series decides.

## What is not covered

- Base and calibration batches: 16 base batches (three circuits) and 3 calibration batches also execute in an order the
  platform sets, and the mirror rounds reverse the base batches. A base contrast is a level, so its position inside the
  batch does not enter and its execution time does; the strict gate no longer decides on them. The rule that covers the time
  term (`bracketed-base-contrast-weights.md`: executed-time weights, a drift monitor and a calibration systematic) is part of the
  decision.
- Integration (done): `evaluate` in `scripts/qi_pathion_one_cz_null_bracketed_cases.py` maps the stamps to `executed_offset`
  (`twin_offsets`), replaces the twin rows by `adjusted_rows` (`executed_twin_fit`), emits the five labels (`WITHHELD_LABELS`) and keeps the
  label of the pool that ignores the order as `order_ignored_label` (repeated as `label_if_order_ignored` in a withheld decision) and the strict result as `order_gate`.
- Power under reordering (done): `prediction.json` holds five tables of the registered rule, simulated with reordering at 0.5
  per batch, a linear drift and a planted departure (CASE.md, "Operating characteristics"): 91.6 to 93.3 percent at the design
  effect, a heterogeneity-gate false-alarm rate of about 1.0 percent and detection of 46 and 94 percent at departures of
  0.0075 and 0.015 per position. The pricing simulator of the layout choice (`scripts/qi_pathion_one_cz_null_bracketed_pricing.py`)
  still prices the pool that ignores the order, and its retained cells keep their bytes.
- The common-drift hypothesis: tested by rule 3 on the run itself and by nothing before it.

## Falsifiers

A retained series whose `template_drift` values differ beyond rule 3; reordering that clusters in whole waves (then the
independence model understates the confounded fraction, and `P(confounded)` must be recomputed from the clusters); stamps that
no longer follow the previous job's `finished_at`.
