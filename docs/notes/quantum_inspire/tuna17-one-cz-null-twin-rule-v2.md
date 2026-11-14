# Tuna-17 one-CZ null: single-ended twin readout, twin-control rule v2 and finite-count zero-error policy

The case [pathion_one_cz_null_tuna_17](../../../results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/CASE.md) was
approved and run on 2026-11-07, and its `cases.json`, `prediction.json` and preregistered rule are hashed by the retained
records, so this note and the code it names are the versioned successors of four limits that the hosted review of the case
raised (issue 791). The retained series reads `unresolved_batch` (b0 base replicates chi-square 34.86 > 10.83), so none of
the four changes a recorded verdict.

| limit | disposition | home |
|---|---|---|
| single-ended twin readout reference | stated and bounded below; a bracketed successor layout is costed, not built | this note |
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
t_raw = lambda t_true: an additive readout shift cancels inside the batch, and only a drift of lambda between batches scales
the contrast. On the retained series the selector q8 reads e01 in [0.0254, 0.0310] and e10 in [0.0275, 0.0322] over the 16
template batches (`drift_covariate.references.pairs` of
`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, measured on Tuna-17, 2026-11-07), so lambda lies in
[0.937, 0.947], a spread of 1.1 percent. For the b0 offset 0.0164 that moves t by at most 1.8e-4, 0.065 of the pooled b0
twin standard error 0.00276. The bound covers the unconditional assignment of the selector; a selector error that depends
on the coin is the coin-conditioned dropout the case tests, which no readout circuit of the series measures and the X-only
calibration batches (16 to 18) estimate.

A bracket around every twin needs two readouts beside each twin, four circuits for a pair, and a batch holds three
(`PLATFORM_CIRCUITS_PER_BATCH` in `tests/scripts/test_qi_pathion_one_cz_null_rule_v2.py`). The successor layout that
brackets every twin runs each twin as `[readout-0, twin, readout-1]`: 16 twin batches instead of 8, 27 batches instead of
19, and 8 more pauses of 30 s (240 s). It separates the two twins of a pair across batches, so a batch drift enters
t directly (the case's preregistered drift is 0.003, 1.1 pooled twin standard errors) in exchange for a correction of an
effect that the bound above puts at 0.065 standard errors. The single-ended layout keeps the within-batch pairing and
stays the recommended design; the bracketed layout is not built.

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

The operating characteristics repeat the nine worlds of the case's table from QRNG value 0 of
`docs/evidence/anu_qrng/draw-2026-11-07T185234Z.json` at 20,000 series per world, and add the negative-twin world (b0
twin contrast = minus its base contrast, 6-CZ blocks zero; a hypothesis row, no simulation). The inherited worlds draw first
and in order, so their rows equal the stored ones except where a series read superposition-only with t0 < -3 se:

| world | stationary | with batch drift 0.003 |
|---|---|---|
| superposition-only offset | superposition_only 0.9399 (stored 0.9412), unresolved_negative_twin 0.0013 | superposition_only 0.7680 (0.7751), unresolved_negative_twin 0.0072 |
| negative twin (preregistered rule: superposition_only about 0.97) | unresolved_negative_twin 0.9706, superposition_only 0.0017 | unresolved_negative_twin 0.8415, superposition_only 0.0088 |

A negative twin reads superposition-only in under 1 percent of runs under v2; under the preregistered rule it read that row
in nearly every run it was decided. `"$PYTHON" scripts/qi_pathion_one_cz_null_rule_v2.py --check` regenerates the record.

## Zero-error policy

`pathion_coset_analysis.selector_stat` returns a standard error of 0 when both arms of a coin selector are deterministic,
and `pooled` then divides by zero. In the Tuna-17 series no arm is deterministic (selector error rates 0.025 to 0.032), so
the v3 record is unchanged (`--check` of `qi_pathion_one_cz_null_analysis.py` reproduces its bytes and the 1,365 floats of
its predecessor). The v3 analyzer now defines the case:

- `arm_variance(rate, shots)` is rate (1 - rate) / shots for an interior rate and, for a deterministic arm, the variance of
  the Agresti-Coull interval at z = 3 (`Z_RESOLVE`): center (shots rate + 4.5) / (shots + 9), variance center
  (1 - center) / (shots + 9). The adjustment covers a deterministic arm only; every other float keeps its arithmetic.
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
operating characteristics. The change to `oc.operating_characteristics` and `oc._series_label` (a successor rule and
world list as optional arguments) leaves `prediction.json` byte-identical.
