# Reviewer report: codex

`codex exec`, model `gpt-daybreak-blue-latest`, reasoning effort high, read-only sandbox, 2026-11-15, on [brief.md](brief.md) at head `5f4a0e26e`. Paths are relative to this repository. The text below is the reviewer's answer, with absolute local paths and link syntax rewritten to repository-relative code spans.

Reviewed commit `5f4a0e26e`; the worktree remained clean. No network or provider action occurred.

## Findings, ranked by consequence

1. **SERIOUS — proved:** The admission record falsely says the QX prerequisite completed. Tuna CASE.md:77 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md:77`) says the QX run “has been collected,” while the QX CASE.md:3 (`results/quantum_inspire/cases/characterization_qx/CASE.md:3`) says nothing was submitted. The draft also records both runs as not run at draft:87 (`docs/notes/quantum_inspire/tuna17-characterization-case-draft.md:87`). The hardware admission condition is therefore unsatisfied.

2. **SERIOUS — proved:** CLI analysis cannot produce the promised retained-readout verdict. `readout_within_tolerance` exists only when `retained` is supplied at script:339 (`scripts/qi_tuna17_characterization_cases.py:339`), but `--analyze` calls `analyze()` without it at script:398 (`scripts/qi_tuna17_characterization_cases.py:398`). This contradicts prediction.json:19 (`results/quantum_inspire/cases/characterization_tuna_17/prediction.json:19`) and CASE.md:82 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md:82`). The test masks the defect by passing a retained dictionary directly at test:86 (`tests/scripts/test_qi_tuna17_characterization_cases.py:86`).

3. **SERIOUS — proved:** `sanity()` does not implement claim 6. Its only scientific check is the mean readout separation at script:247 (`scripts/qi_tuna17_characterization_cases.py:247`). A completed T1 batch containing only zero shots has no readout pair and passes. Reversing bit order is undetectable because every circuit treats all qubits identically. Even one fully inverted qubit passes the mean test: with the other 16 at retained-like `(0.03, 0.94)`, the means are `(0.087, 0.885)`, inside `(≤0.2, ≥0.8)`. No sanity regression test exists.

4. **SERIOUS — computed:** The 256-pulse ladder threshold does not bound coherent X90 error monotonically. From the stated model, \(P_0=\cos^2(256\epsilon/2)\):

   - `ε=0.3515625°` gives `P0=0.5`;
   - `ε=0.703125°` gives `P0=0`;
   - the larger `ε=1.40625°` gives `P0=1`.

   Thus CASE.md:88 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md:88`) and prediction.json:15 (`results/quantum_inspire/cases/characterization_tuna_17/prediction.json:15`) provide a falsifiable endpoint but not the claimed coherent-error upper bound. The exponential ladder fit at script:362 (`scripts/qi_tuna17_characterization_cases.py:362`) also drops negative cosine contrast rather than fitting coherent oscillation.

5. **SERIOUS — proved:** The T1 chi-square verdict treats estimated readout calibration as exact. The opening/closing assignments are estimated at script:330 (`scripts/qi_tuna17_characterization_cases.py:330`), but the point uncertainty at script:350 (`scripts/qi_tuna17_characterization_cases.py:350`) propagates only T1-shot binomial variance. It omits the shared uncertainty and covariance introduced by `zero` and `span`, so the resulting chi-square probability is not calibrated near the population floor. The degrees of freedom `n−2` are otherwise correct, and the gamma implementation matched SciPy over a 600-point grid with maximum absolute error `4.27e-15`.

6. **SERIOUS — proved:** Claim 9 is false. The synthetic-shot test seeds `random.Random(20261115)` at test:62 (`tests/scripts/test_qi_tuna17_characterization_cases.py:62`), contrary to the repository seed rule at AGENTS.md:83 (`AGENTS.md:83`). Replace the stochastic fixture with deterministic exact counts or bind it to a recorded QRNG draw.

7. **MODERATE — proved:** The paired written case does not state every Hardware-services field. The Tuna case itself states measurement, simulation insufficiency, Tuna-17, shots, 115.8 seconds, and zero expected credits. The provider QX case states backend, shots, and seconds at QX CASE.md:8 (`results/quantum_inspire/cases/characterization_qx/CASE.md:8`), but never states expected credits and only implies—rather than states—why local simulation cannot answer the remote submission/collection question. Because the requested approval covers both runs, the combined case is incomplete under AGENTS.md:173 (`AGENTS.md:173`).

8. **MODERATE — proved:** The claimed provider limit of 500,000 measurements per qubit has no located authority. It appears only in CASE.md:49 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md:49`) and its test. The retained backend record instead specifies 131,072 shots and 300 seconds at catalogue.json:1127 (`docs/evidence/quantum_inspire/catalogue.json:1127`); `qi_platform.py` enforces those fields at qi_platform.py:912 (`scripts/qi_platform.py:912`). The series remains comfortably inside the proven limits, but “provider’s 500,000” is unsupported.

9. **SLOPPY — proved:** The limit test compares the whole series estimate with the per-job 300-second limit at test:31 (`tests/scripts/test_qi_tuna17_characterization_cases.py:31`). It passes here because 115.8 seconds is below 300, but it does not calculate the maximum individual job as CASE.md claims.

## Claim disposition

1. **Confirmed — proved:** The generator imports no provider client and reaches no request path. `qxelarator` is imported only inside explicit `--local`.
2. **Confirmed with one unsupported attribution — computed:** 6 batches, widths `2,3,3,2,2,2`; 14 jobs; 147,456 shots; maximum 16,384 shots/job. All manifest circuit digests match. The 500,000 figure is unproven.
3. **Confirmed — computed/measured:** Recalculation gives `36.4 + 78.15168 + 1.26976 = 115.82144`, rounded to `115.8 s`. Retained 16,384-shot jobs measured 9.87–12.57 seconds, consistent with the model’s 11.3-second readout job.
4. **Confirmed — proved:** Circuit construction supplies the stated X, wait, X90 counts, measurement order, and noiseless outcomes. The retained toolchain record contains 28/28 characterization entries with `libqasm=ok`, `compiled=ok`, and both sequence-preservation flags true.
5. **Falsified in part — proved:** Bit order, assignment inversion, `n−2` degrees of freedom, and the chi-square function are sound. CLI verdict delivery and calibration-error propagation are not.
6. **Falsified — proved:** `sanity()` accepts broken data batches and cannot detect bit reversal.
7. **Confirmed — computed:** Pure generation produced 22 files per profile; all 44 bytes matched the checkout, with no ungenerated non-CASE file. The mutation test names the changed and stray files.
8. **Partially confirmed — computed:** Thresholds predate any run and can all fail, but the ladder endpoint does not support its claimed coherent-error interpretation.
9. **Falsified — proved:** The test contains a seeded call.

## Further quantity already present

**Hypothesis:** the ordered shots determine a per-qubit shot-order spectrum—especially amplitude and phase near the already observed `~0.020 cycles/shot` line associated with 50 Hz wall time. `p1()` destroys this information by summing every bit at script:202 (`scripts/qi_tuna17_characterization_cases.py:202`), while the repository already records the Tuna-17 line at experiments.md:805 (`docs/notes/quantum_inspire/experiments.md:805`). The cycles-per-shot spectrum is directly determined; calling it exactly 50 Hz additionally requires the acquisition cadence.

Verdict: the generation, circuit counts, timing arithmetic, digests, and basic T1 estimator are sound, but the case is not approval-ready because its admission record is false, its CLI omits one promised verdict, its sanity gate is ineffective for data batches, and its X90 endpoint cannot support the stated coherent-error bound.

