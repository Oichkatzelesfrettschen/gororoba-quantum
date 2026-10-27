# Codex review: primorial coherence case 2 (second draft)

Reviewer: Codex CLI 0.164.0, model `gpt-daybreak-blue-latest` at high reasoning effort, read-only sandbox, run on
2026-10-26 against the second draft of `results/live/PRIMORIAL_COHERENCE_CASE_2.md` and its code (commit 5af7101:
23 paths per PUB, a two-delay readout preflight, a Bonferroni band on the largest bias). The brief asked it to
hold the case to the run-economy rules, the QPU rules of AGENTS.md and the repetition-rate guide. Its report
follows verbatim, with local absolute paths reduced to repository paths, and then the disposition of each finding
in the third draft.

## Report

Review target: Python QPU planning/analysis code plus a hardware-spending approval case, spanning hardware execution, statistics, and reproducibility. I reviewed every file named by the brief in full and both requested diffs.

## Findings

1. **P1 — Initialization error is modeled as terminal readout error.**  
   `scripts/primorial_probe_case.py:980` raises snapshot `e10`, but `gororoba_quantum/calibration_snapshot.py:220` installs `e10` exclusively as a terminal readout channel. IBM locates the short-delay penalty in initialization before circuit execution (`docs/notes/ibm_quantum/repetition-rate-execution.md:14`). These channels are not interchangeable: initial excitation followed by an X gate changes the final quantum state, while increasing terminal `e10` does not model that evolution. The rule can approve 20 microseconds using the wrong noise law.  
   **Fix:** insert an explicit bounded pre-circuit excitation channel in every simulated arm, or prove observable-level conservative domination; retain terminal readout error separately.

2. **P1 — The delay decision accepts unbound or duplicate acquisitions.**  
   `scripts/primorial_probe_case.py:997` discards both records and compares only path lists. Passing the 50-microsecond directory as both inputs produces near-zero excess and can select 20 microseconds without any 20-microsecond measurement. Different backends, repetition delays, snapshots, calibrations, or execution intervals also pass. `scripts/primorial_probe_case.py:1042` similarly accepts an unrelated snapshot or delay verdict.  
   **Fix:** require exact 50- and 20-microsecond record fields, distinct job identities, matching backend/path/shot schemas, execution-start calibration fingerprints, and snapshot digests; retain all identities in the verdict. Bound queue/drift separation or use an interleaved drift control.

3. **P1 — Stage 0 assumes an execution order IBM explicitly declines to guarantee.**  
   `results/live/PRIMORIAL_COHERENCE_CASE_2.md:43` claims packed `|000>` shots follow `|111>`-ending shots. Each member is a separate PUB, an isolated `cp_readout_0` PUB is also present, and IBM provides neither PUB-order nor single-batch guarantees (`docs/notes/ibm_quantum/repetition-rate-execution.md:28`). Reordering can measure benign history, underestimate preparation error, and authorize later stages at 20 microseconds.  
   **Fix:** use a dedicated wide history-setting circuit/job whose repeated executions themselves end in `|111>`, with a simultaneous excess bound.

4. **P1 — `estimate + 2 SE` is not the simultaneous bound the decision requires.**  
   `scripts/primorial_probe_case.py:1003` applies an individual approximate one-sided bound to as many as 69 wires. Under independent normal marginals, joint coverage is only `Phi(2)^36 = 0.437` for the minimum 12 paths and `Phi(2)^69 = 0.204` for all 23. One understated wire can approve the shorter delay.  
   **Fix:** use simultaneous one-sided exact binomial intervals, or a validated joint procedure, across every retained wire.

5. **P1 — The claimed stage-2 family-wise false-alarm rate is unsupported.**  
   `scripts/primorial_probe_case.py:897` requests Bonferroni tail quantiles from only 128 deterministic Sobol evaluations. With 12 paths the upper target is `0.997917`, so `_quantile` merely returns the sample maximum. The measurement widening also applies one path-level normal quantile to the maximum of seven coefficients. At 12 paths, the current `z=3` permits a union-bound error of about `0.227`, not `0.05`.  
   **Fix:** derive a validated joint-maximum distribution or correct across all `7 × k` coefficients, provide adequate tail resolution, and account for path selection.

6. **P1 — The crosstalk veto applies Pearson chi-square outside its sparse-table regime.**  
   `scripts/primorial_probe_case.py:1095` tests a sparse `2 × 8` table. The first gap-88 member’s ideal law has support on only two outcomes; at 1,600–3,200 shots, several noisy outcome cells can remain below the usual expected-count condition for `chi2_contingency`. The resulting `p < 0.01` decision has uncalibrated size and can improperly admit or veto the device claim. The existing test uses uniform counts and misses the sparse regime.  
   **Fix:** use an exact or Monte Carlo conditional homogeneity test, or preregistered sparse-bin pooling.

7. **P1 — The case requests approval before its binding dry runs exist.**  
   `results/live/PRIMORIAL_COHERENCE_CASE_2.md:116` leaves future `RECORD_DIR` and `RECORD_SHA256` placeholders, while `AGENTS.md:245` requires dry run, analysis, written case, approval, then submission. Approval now would authorize records the approver has never seen.  
   **Fix:** produce and analyze each binding dry run, record its exact path and SHA-256, then request case-specific approval.

8. **P2 — The documented procedure cannot execute as written.**  
   After `cd gororoba_quantum`, the commands at `results/live/PRIMORIAL_COHERENCE_CASE_2.md:129` address nonexistent `gororoba_quantum/scripts/...` paths. `SNAPSHOT` is required before delay selection, but `results/live/PRIMORIAL_COHERENCE_CASE_2.md:142` says the later stage-1 dry run exports it; `live_run.py` performs no such export.  
   **Fix:** invoke `../scripts/primorial_probe_case.py` and add an explicit `calibration_snapshot.py --export` step before delay selection, with the resulting snapshot bound to later records.

9. **P2 — Missing crosstalk evidence becomes a clean result.**  
   `scripts/primorial_probe_case.py:1095` returns `crosstalk_detected=false` when the isolated reference is absent.  
   **Fix:** return an indeterminate/error outcome and add a missing-reference test.

10. **P3 — The ceilings are adequate but not tight.**  
    `results/live/PRIMORIAL_COHERENCE_CASE_2.md:100` models approximately 3.0–3.8 seconds for each preflight against a 10-second ceiling, 5.0–7.4 against 20, and 7.7–23.1 against 40. The aggregate cap is 80 seconds against a worst modeled total of 37.2.  
    **Fix:** justify the explicit split/rounding margin from retained wide-job evidence or reduce the ceilings after the binding dry runs.

## Questions settled

- Pinned replica mapping, per-path in-job inversion, `summary_per_replica`, and `measured[member][k]` preserve the declared path order.
- The submit-time second `campaign_pin` call reconstructs the same ordered multi-path surface; QPY and manifest comparison reject divergence.
- Multi-path campaigns add the first-member/first-path isolated reference, and `crosstalk` reads the correct packed and isolated distributions when both exist.
- The N2 formula and monotonic invariant are sound: two repeated arms give `2 × N2` effective shots, and `100 × ceil(need/200)` is the least 100-shot increment covering that need.
- Per-path voiding is sound. The delay bound and Bonferroni claim are not.
- Charge arithmetic reproduces the table: approximately 19.4 seconds for 20 microseconds with N2=1600 and 37.2 seconds for 50 microseconds with N2=3200.

Verdict: do not approve the hardware case. The multi-path execution mechanics are sound, but the short-delay control does not establish the physical quantity it claims to bound, and the statistical admission rules do not earn their stated error rates.

Checks passed: both `git diff --check` scopes, pinned Ruff format/check, mypy on all eight named Python files, and the 16 focused tests. The tests required `TMPDIR=/dev/shm` because the checkout and `/tmp` were read-only. No provider call or submission occurred.

During review, another process advanced `HEAD` from `fd40fc3` to `5af7101`. The new commit contains the exact reviewed named-file blobs. The remaining uncommitted modification is `docs/evidence/primorial_cover/README.md`; this review did not modify or evaluate that unrelated file.


## Disposition

1. Initialization as readout: fixed. The two-delay readout preflight is gone. Each path's excitation bound eps
   from the `state-prep-control` family and `scripts/state_prep_excess.py` enters every decision as an X error
   before the circuit (`ExcitedArmLaw`, `dynamic_density.with_prep_excitation`), beside the reported readout
   error. At eps 0 the decision on 58-71-72 is bit-identical to the earlier one.
2. Unbound acquisitions: fixed. `decide_delay` is gone. `decide_paths` requires the snapshot to equal every probe
   member's execution calibration with no change during the shots, and `path_excitation` requires the excess
   output's plan sha256 to equal the run's approved record and its delay to equal the run's.
3. Unguaranteed execution order: fixed. prep0 and x_history run in jobs of their own, so each arm's shot history
   holds by construction.
4. Per-wire bounds: fixed. `state_prep_excess.py` takes one-sided Clopper-Pearson bounds simultaneous over every
   controlled qubit.
5. Family-wise rate: fixed. The band on the largest bias is replaced by per-coefficient bands at
   z(1 - 0.025/(7k)), at least 3, from the draws' mean and standard deviation rather than their tail quantiles,
   under a stated Gaussian approximation. Path selection uses probe shots only, independent of the stage-2 data.
6. Sparse chi-square: fixed. `pooled_counts` merges every outcome whose expected count falls below 5, and a
   two-outcome law test covers the regime.
7. Approval before binding dry runs: boundary. AGENTS.md's sequence (dry run, analysis, written case, approval,
   submission) is followed with representative dry runs retained in `results/live/` and cited by sha256 in the
   case. The binding dry runs are re-made from main after merge, as for the first case, which the owner approved
   on the same pattern. Their subset follows the case's preregistered drop rules.
8. Commands: fixed. The commands run from `gororoba_quantum/` with `../scripts/`, and an explicit
   `calibration_snapshot.py --export` step comes first.
9. Missing crosstalk evidence: fixed. A missing reference, or a table that pools to one column, returns
   `indeterminate`, which the case treats as a failed check. A test covers it.
10. Loose ceilings: fixed. The ceilings are 8, 15 and 30 s, sized to the 15 us edge of the fixed per-execution
    time the first case's bill admits.
