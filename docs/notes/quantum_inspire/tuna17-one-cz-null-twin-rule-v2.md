# Tuna-17 one-CZ null: single-ended twin readout, twin-control rule v2 and finite-count zero-error policy

The case [pathion_one_cz_null_tuna_17](../../../results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/CASE.md) was
approved and run on 2026-11-07, and its `cases.json`, `prediction.json` and preregistered rule are hashed by the retained
records, so this note and the code it names are the versioned successors of four limits that the hosted review of the case
raised (issue 791). The retained series reads `unresolved_batch` (b0 base replicates chi-square 34.86 > 10.83), so none of
the four changes a recorded verdict.

| limit | disposition | home |
|---|---|---|
| single-ended twin readout reference | stated and bounded below; the bracketed successor case reads every twin against its own bracket | this note, `scripts/qi_pathion_one_cz_null_bracketed_cases.py` |
| twin control admits a large negative t0 | rule v2 with an `unresolved_negative_twin` row | `scripts/qi_pathion_one_cz_null_rule_v2.py`, `results/quantum_inspire/pathion_one_cz_null_tuna_17_rule_v2.json` |
| `pooled` divides by zero for a deterministic arm | finite-count error per arm, named refusal of a zero error | `scripts/qi_pathion_one_cz_null_analysis.py` |
| k8 and k12 of `c2_one_cz_twins.txt` unchecked | every `oc.LOW_NAMES` template read against `oc.PREDICTED` | `tests/scripts/test_qi_pathion_one_cz_null_models.py` |

## Twin readout reference

A twin batch holds the coin-0 twin, the coin-1 twin and one readout circuit: `readout-0` in the forward round and
`readout-1` in the mirror round (`oc.batch_rows`). A base batch holds both readouts around its template. The twin
decision reads the raw counts of the selector qubit and applies no readout correction, so a twin batch carries no
bracket and the single readout serves only the drift covariate.

The twin contrast of one batch is t = P(s = 0 | coin-1 twin) - P(s = 0 | coin-0 twin). With assignment errors e01 and e10 of
the selector, each raw P(s = 0) is e10 + lambda p with lambda = 1 - e01 - e10 and p the ideal probability, so
t_raw = lambda t_true: an additive readout shift cancels inside the batch, and a scale lambda < 1 shrinks the contrast.
On the retained series the selector q8 reads e01 in [0.0254, 0.0310] and e10 in [0.0275, 0.0322] over the 16 template
batches (`drift_covariate.references.pairs` of
`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, measured on Tuna-17, 2026-11-07), so lambda lies in
[0.937, 0.947]. Two effects follow for the b0 offset 0.0164 against the pooled b0 twin standard error 0.00276:

- the attenuation itself, a shortfall of 8.7e-4 to 1.04e-3 (0.31 to 0.38 standard errors), enters s0 and t0 alike as a
  raw reading: the decision rows are `pca.selector_stat(plus, minus)` of the raw coin counts for the base contrast
  (`qi_pathion_one_cz_null_cases.py:1168-1170`; the readout matrix of line 1172 feeds only the `template_rows` detail) and
  the raw selector-0 fraction of each twin for the twin contrast (lines 1183-1186), and `decide_estimates` reads
  `s0, t0 = base["b0"], twin["b0"]` from those (line 857; the v3 analyzer repeats both at
  `qi_pathion_one_cz_null_analysis.py:256` and `265-268`). Neither contrast is bracket-corrected, so the shortfall is not
  cancelled in s0 - t0; it is part of the model, since the predicted contrasts of `c2_one_cz_twins.txt` apply the bracket
  product readout to base and twin alike (the base contrast, conditioned on the coin readout, carries the coin's assignment
  factor as well), and the decision compares raw readings with raw predictions;
- the spread of lambda between batches, at most 1.8e-4 (0.062 standard errors), is the part that a bracket in every batch
  would correct and the single-ended layout leaves in.

The bound covers the unconditional assignment of the selector; a selector error that depends on the coin is the
coin-conditioned dropout the case tests, which no readout circuit of the series measures and the X-only calibration
batches (16 to 18) estimate. An additive shift cancels only while both twins of a batch share one assignment channel.

A bracket around both twins of a pair needs two readouts beside them, four circuits per batch, which the legacy hardware
policy (three circuits per batch, `PLATFORM_CIRCUITS_PER_BATCH` in `tests/scripts/test_qi_pathion_one_cz_null_rule_v2.py`)
refuses and the `wave-v1` policy admits ([usage.md](usage.md#queue-rules-the-faq-governs)). The successor case
[pathion_one_cz_null_bracketed_tuna_17](../../../results/quantum_inspire/cases/pathion_one_cz_null_bracketed_tuna_17/CASE.md)
(owner rulings 2026-11-14) runs each pair as `[readout-0, coin-0 twin, coin-1 twin, readout-1]` in one batch, four replicates of
every template and kind at 16,384 shots per circuit: 35 batches in 12 waves of at most three (a 60 s pause after each
wave), and it preregisters rule v2, the finite-count error and the chi-square 16.266 batch bound of its three degrees of
freedom (the predecessor's 10.828 is the one-degree value of its two replicates). Both twins share the batch's bracket, so
the additive readout shift that the retained series moves between batches (the selector e01 steps by about 0.005 between
adjacent batches, chi-square 84.4 on 11 degrees of freedom over the 12 readout-0 circuits; the bracket offset
c = (e10 - e01)/2 scatters with chi-square 61.56 on 7 degrees of freedom over the 8 batches holding both readouts, range
-0.0014 to +0.0032) cancels exactly in the twin contrast, and each batch reports its own c and the corrected twin readings.
What the bracket still leaves is a drift of the offset itself between the two twins of a batch (10 to 147 s in the
retained series), which no readout circuit corrects; the successor's operating characteristics price it (CASE.md there).

## Twin-control rule v2

The preregistered rule (CASE.md, "Preregistered decision rules", item 4) assigns `superposition_only` when t0 sits below
+3 standard errors and s0 - t0 exceeds 3 combined standard errors, which includes a t0 far below zero. No modeled mechanism
predicts a negative twin contrast, so that reading says "the offset exists only with the coin in superposition" about a
response that has the opposite sign. Rule v2 states:

> b0 twin contrast t0 above 3 se; if not, t0 within 3 se of zero (|t0| <= 3 se) and s0 - t0 above 3 combined se, the offset
> exists only with the coin in superposition; t0 below -3 se is unresolved (negative twin); otherwise unresolved.

`qi_pathion_one_cz_null_rule_v2.decide_estimates` applies the v3 analyzer's decision and relabels a
`superposition_only` reading with t0 < -3 se as `unresolved_negative_twin`, which decides nothing and leaves A5-186
unchanged. Every other label, number and threshold is the preregistered one, so the two rules differ only on that region
(`test_rule_v2_differs_from_the_preregistered_rule_only_on_a_superposition_only_reading_with_a_negative_twin`).

The operating characteristics repeat the eight worlds of the case's table from QRNG value 0 of
`docs/evidence/anu_qrng/draw-2026-11-07T185234Z.json` at 20,000 series per world, and add the negative-twin world (b0
twin contrast = minus its base contrast, 6-CZ blocks zero; a hypothesis row, no simulation). The inherited worlds draw first
and in order, so their rows equal the stored ones except where a series read superposition-only with t0 < -3 se:

| world | stationary | with batch drift 0.003 |
|---|---|---|
| superposition-only offset | superposition_only 0.9399 (stored 0.9412), unresolved_negative_twin 0.0013 | superposition_only 0.7680 (0.7751), unresolved_negative_twin 0.0072 |
| negative twin (preregistered rule: superposition_only about 0.97) | unresolved_negative_twin 0.9706, superposition_only 0.0017 | unresolved_negative_twin 0.8415, superposition_only 0.0088 |

A negative twin reads superposition-only in under 1 percent of runs under v2; under the preregistered rule it read that row
in nearly every run it was decided. `"$PYTHON" scripts/qi_pathion_one_cz_null_rule_v2.py --check` regenerates the record, which stores every value in ten-thousandths as an
integer (float-free, so the replay needs no numeric binding); gate `core-pathion-one-cz-null-tuna-analysis-replay` runs it and declares it under `replays`.

## Zero-error policy

`pathion_coset_analysis.selector_stat` returns a standard error of 0 when both arms of a coin selector are deterministic,
and `pooled` then divides by zero. In the Tuna-17 series no arm is deterministic (selector error rates 0.025 to 0.032), so
the v3 record is unchanged (`--check` of `qi_pathion_one_cz_null_analysis.py` reproduces its bytes and the 1,365 floats of
its predecessor). The v3 analyzer now defines the case:

- `arm_variance(rate, shots)` is rate (1 - rate) / shots for an interior rate and, for a deterministic arm, the variance of
  the Agresti-Coull interval at z = 3 (`Z_RESOLVE`): center (shots rate + 4.5) / (shots + 9), variance center
  (1 - center) / (shots + 9). The adjustment covers a deterministic arm only; every other float keeps its arithmetic.
  The error steps from about 1/shots at an interior rate next to 0 to about 2.1/shots at 0, and no coverage calibration of
  that step is supplied.
- The base selector estimate (`selector_estimate`) and the twin contrast use `arm_variance`.
- `pooled` and `heterogeneity` refuse a pair whose error is not positive and finite with a named `ValueError`; the calibration's
  matched pairs, which the joint statistics pool, take that refusal, since a calibration cell without a single misassigned
  shot at 16,384 shots has not occurred and would need its own interval.

The frozen producer `qi_pathion_one_cz_null_cases.py` keeps `ZeroDivisionError` for a zero error and its preregistered
arithmetic; the Tuna-17 decision runs through the v3 analyzer.

## Validation

`sh ci/pr_checks.sh tests tests/scripts/test_qi_pathion_one_cz_null_models.py
tests/scripts/test_qi_pathion_one_cz_null_rule_v2.py tests/scripts/test_qi_pathion_one_cz_null_analysis.py` covers the
rule, the policy and the per-template coverage; `-m audit` replays the stored rule-v2 table and the case directory's
operating characteristics. The successor simulation `simulated_shares` of `qi_pathion_one_cz_null_rule_v2.py` (the world list as an optional
argument, its own module-level v2 decision) leaves `qi_pathion_one_cz_null_cases.py` at its pinned bytes and
regenerates the stored rule-v2 record byte-equal.
