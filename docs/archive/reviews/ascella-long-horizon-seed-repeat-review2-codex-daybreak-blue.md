# Adversarial Review

Review scope: commit `782b189ad`, as fixed by the brief.

## SERIOUS — Chip attribution exceeds the implementation evidence

`docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:23` and `docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:29` treat the returned `computed_circuit` and `computed_input` as the implemented optical transformation, then attribute the remaining error to physical realization. The earlier design explicitly limits those fields to the provider-reported model and excludes applied voltages and the implemented unitary at `docs/design/ascella-signed-coherence-conformance.md:712`.

The served-ideal and simulator controls refute a large error in the returned digital model. They do not exclude deterministic effects introduced downstream by compilation layers, control firmware, heater mapping, mode mapping, or analog realization. Repetition across twelve days supports persistence somewhere in the chip-control path, rather than uniquely on the photonic chip.

**Fix:** Narrow “compiler refuted” to “returned-model mismatch refuted” and “chip supported” to “persistent implementation-path error supported.” Require applied-control telemetry, voltage readback, or an independent implemented-unitary witness before assigning the error specifically to the chip.

## SERIOUS — The claimed out-of-sample correction is post hoc

`docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:59` calls the correction out of sample, while `scripts/ascella_mesh_error_controls.py:102` defines the estimator after job-08 was retained. The preregistered acquisition and reading plan at `docs/state/plans/ascella-long-horizon-seed-repeat-case.json:84` fixes persistence readings but contains no per-seed correction rule. Both the estimator and its interpretation first appear in commit `782b189ad`, after the job-08 result.

The arithmetic reproduces: standard deviation falls from `0.0103595` to `0.00373076`, a variance factor of `7.71056`. The residual variance comprises approximately `4.6147e-6` job-08 counting variance, `6.1526e-6` estimated table noise, and `3.1512e-6` unexplained remainder. The files do not establish that the remainder is changed physical error.

**Fix:** Describe the result as a retrospective held-run analysis, label the final component unexplained residual variance, freeze the estimator and uncertainty calculation, then score them unchanged on a fresh acquisition.

## SERIOUS — “No redrawn share” is stronger than the persistence test

`docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:49` reports `r = 0.92455` against a full-persistence ceiling of `0.93607`, but line 55 claims redraw would lower the correlation “which it does not.” The correlation is lower. `scripts/ascella_long_horizon_reading.py:162` classifies “fixed per mesh” by comparison with a lower Fisher threshold, not by demonstrating equality with the ceiling.

The observed 99% Fisher interval is approximately `0.8617–0.9595`. Direct noise correction gives a latent-correlation point estimate near `0.981`, while the standard-deviation ratio is about `0.882` and the attenuation-adjusted slope ratio about `0.890`. These values support a mostly persistent pattern with roughly 10–12% amplitude shrink. They do not identify a zero redrawn component.

**Fix:** Replace “which it does not” with “no redrawn component is detected at the available precision,” report the correlation interval, and fit or bound persistent-plus-redrawn variance explicitly.

## SLOPPY — The assumption ledger closes broader hypotheses than its controls test

`docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:73` marks time, order, and predecessor effects as holding based on a linear position trend and one-step scalar predecessor distance. These checks do not exclude nonlinear drift, longer-memory carryover, or interactions between predecessor and mesh. Line 74 generalizes anchor underdispersion into a multinomial counting model without testing mesh-dependent overdispersion.

**Fix:** State the exact bounded controls that passed. Retain nonlinear timing, higher-order carryover, and mesh-dependent counting dispersion as unresolved assumptions.

## Checks Finding Nothing

- All three QPU records echoed the expected seed and circuit parameters for `64/64` iterations; every computed input occupied mode 0.
- Raw-result and case SHA-256 bindings matched for jobs 02, 03, and 08.
- Independent recomputation reproduced by-name `r = 0.924550`, position-paired `r = -0.199119`, and background-adjusted `r = 0.925583`.
- The anchor definition, centering, block counts, X-statistic denominator, and relabeling construction exposed no arithmetic defect.
- The simulator spread was `0.002105` against counting standard deviation `0.002025`; simulator and QPU mesh errors correlated at approximately `-0.045`.
- The direct one-photon mode-count argument is correct: full 32- or 64-dimensional encodings require 32 or 64 modes. Higher-dimensional algebra can improve witnesses, folding strategies, and controls, but the reviewed evidence demonstrates no reduction in physical hardware error.