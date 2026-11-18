# Reconciliation of the review of pull request 914

The pull request carries the Tuna-17 phase scan case of the null block (scripts/qi_pathion_null_phase_scan_cases.py,
its tests, `results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/` and `..._qx/`, the error-law extension in
`gororoba_quantum/elementary_error_laws.py` and the decision probes under
`docs/evidence/qi-null-phase-scan-decision-probes/`). Five review rounds read it at successive heads, three local and
two hosted, and the Advisor read it in two of the local stages. Each finding below was checked against the source at
the head the reviewer read. The briefs are [brief-round1.md](brief-round1.md), [brief-round2.md](brief-round2.md),
[brief-round2-redteam.md](brief-round2-redteam.md) and [brief-round3.md](brief-round3.md); the raw reviewer reports are
session-local and not retained, so each finding is stated here in the reconciliation's own words. Where the available
records are silent the text says "not recorded".

| Round | Reviewer | Head read |
|---|---|---|
| 1 | `codex` on `gpt-daybreak-blue` at high effort; the Advisor afterwards | a90f84184 (codex); dee88da10 (Advisor) |
| 2 | `codex` on `gpt-daybreak-blue` at high effort; `agy` on `gemini-3.8-flash-high` as red-teamer | fc9c84b12 |
| 3 | `codex` on `gpt-daybreak-blue-latest`, selected by the owner as the local reviewer of rules R2 to R6 | e5ba2a787 |
| 4 | the Advisor, partial read | 031e12272 |
| 5 | hosted Codex | 864ab8cf8 |
| 6 | hosted Copilot | c8419222e |

Not recorded: any Advisor read of fc9c84b12 or e5ba2a787; any local review of 864ab8cf8, c8419222e or ff28e5166; the
owner's local-reviewer selection after round 3. The Advisor read of round 4 was a partial read; its extent beyond the
items listed there is not recorded. The reconciliation drafted after round 3 names the Advisor as its last step; no Advisor read of e5ba2a787 or of its fix commits is recorded.

## Round 1: codex on a90f84184, Advisor on dee88da10

The commits `dee88da10` and `af669a933` follow this round; the records tie each resolution to the round and not to a
single commit.

| # | Finding | Check against the source | Disposition |
|---|---|---|---|
| 1 | `q12_phase` cannot identify a before-pulse placement | `forward_law(arm, AFTER_PULSE, -0.18)` equals `forward_law(arm, "q12_phase", -0.18)` to 1e-12 on all nine arms | survives; the label names a single-qubit phase on q12 and no placement (preregistered text, CASE.md label table and "Limits"); no new arm |
| 2 | Batchwise parameters let a mixed series change the ledger | +-10 from q12 -0.18 with outer arms from coupler -0.25 read `coupler_phase` (chi-square 42.2 and 12.5) | survives; a deciding label needs every admitted z12 batch within 20.52 under the labeled world and no higher than the other error world, else `phase_mixed`; tests for both orders |
| 3 | The draft is stale and states `Rz` as fact | the draft stated the zero-duration frame update unqualified | survives; the draft points at the case and its `Rz` sentence carries `hypothesis:` |
| 4 | Angle choice | separations 51.8 least at +-20 degrees, 95.2 at +-30, 120.7 at +-35, 153.6 at +-40 reproduced | survives; outer arms at +-30 degrees, +-10 kept for the cancellation point |
| 5 | The q4 arms cover one sign | the predecessor's q4 arms read +0.039 at -10 and -0.006 at +10 degrees, so the zero is bracketed | refuted as a defect, recorded as a limit in CASE.md "Limits" |
| 6 | "0.001 point" is ambiguous | wording | survives; "upper 0.001 point (the 99.9th percentile)" in code and CASE.md |
| 7 | The constant-offset control is not a forward law | `center_offset` had no forward law | survives; removed; two truths with the predecessor's selector flip (0.0166 and 0.036) beside exact gates read `exact_parabola` and `none_adequate`, the smaller at 48.9 against 49.73, stated in CASE.md |
| 8 | Cold-reader terms | the terms and one q4 sentence and one test message | survives; a "Terms" paragraph in CASE.md, the sentence rewritten, the test message corrected |
| 9 | Independence of contrast and d2 split (claim 5) | the reviewer computed correlations within +-0.002 and no label change | the limit stays stated |

Advisor on dee88da10:

| # | Finding | Disposition |
|---|---|---|
| A1 | Findings 1, 3, 4, 6, 7 and 8 | confirmed; 5 accepted as a stated limit |
| A2 | Blocker: the per-batch rule is untested under noise | confirmed by simulation (per batch with no margin a single mechanism read `phase_mixed` in 33 to 48 of 200 series); fixed in `af669a933`: the test sums each z12 kind over its replicates at margin 0, and `prediction.json` holds 500 series per truth; a margin of 6.63 gives 1 to 2 and 257, so the rule stays strict |
| A3 | Blocker: the retained center d2 split of +0.0083 +- 0.0017 is unmodeled | confirmed; the fit takes each outer arm's split less its batch center's, and the simulation adds a static 0.0083 to every split |
| A4 | `exact_parabola` cannot fire at the observed offset | stated in CASE.md (the falsifier is `none_adequate` with the parabola's least point at phi = 0); a fitted selector-flip world was not added in this round |
| A5 | q11 guard: the four-qubit guard admits 10 of 10 and 19 of 19 bracket pairs, q11 alone 10 of 10 and 15 of 19 | q11 guards the splits alone; a failing batch is fitted on its contrasts |

Open at the end of the round, by the Advisor's statement: the pull request body was not updated for the third commit;
no second Advisor call on the third commit; the hosted round had not started.

## Round 2: codex and agy Flash on fc9c84b12 (rule R1)

`agy` ran under the red-team brief and `codex` under the audit brief on the same head. Both reports were partly
overwritten by their tools' own output; the findings survive in the text that remains and in the session logs. Rules R2
to R5, written after this round, carry the fixes; the branch holds them from `e5ba2a787`.

| # | Finding | Check against the source | Disposition |
|---|---|---|---|
| F1 | A q8 phase at coupler 8-12 reads `coupler_phase` (agy 1, codex 3) | q8 truths at -0.17, +0.09 and +0.10 rad read `coupler_phase` at expected values (coupler sums 29.4, 21.8, 27.4 against 61.10); -0.20, +0.12 and +0.16 read `phase_mixed`; -0.25 read `none_adequate` only because its coupler sum, 64.67, missed the bound by 3.6 | survives, critical; the q8 phase is the fourth world of the fit (`Q8_PHASE`, label `q8_phase_at_coupler`); q8 truths fit their own world and the coupler world lies 11.6 to 250 above, so +-0.1 rad reads `phase_unresolved`; coupler and q12 truths lie 31.7 to 586 below the q8 world |
| F2 | `cases.json` says "no higher than the other error world" while `decide()` adds 6.63 | the text at the two lines read | survives; the `labels` text states "at most 6.63 above every other error world" from `KIND_MARGIN` |
| F3 | The q4 zero recovery error is 0.60 degrees at q12 +0.18 rad | the reviewer's true zero was -13.00; bisection on fractional q4 steps gives -13.117, so the +-5/+-10 line errs by 0.485 (0.482 at +0.15 rad) | refuted as stated; the claim "within 0.5" holds and CASE.md states 0.49 and the method |
| F4 | The bridge tests the intercept and not the q4 slope yet gates the pooled q4 line (agy 4, codex 4) | pooling required only agreeing centers | survives; the retained q4 points pool only when the bridge agrees and the new +-10 degree slope lies within 3 standard errors of the retained slope; the audit test's planted series (retention 0.5) differs by 3.6 standard errors and stays apart |
| F5 | A control stack that drops `Rz(0.0)` but plays nonzero `Rz` lengthens the injected arms alone while the bridge passes | no evidence beyond the compiler record | survives as a limit stated in CASE.md "Limits" |
| F6 | Omitted noise produces a false `q12_phase` (exact gates, selector flip 0.0166, CZ phase damping 0.10) (codex 1) | two causes: the visibility clamp (the center's visibility tops out at 0.2987 at retention 1 against the design 0.42, and `truth_row` clamped the retention) and separation under misfit (value 8 read `q12_phase` in 29 and 48 of 500 series; the false series fit at 1.26 to 1.97 per degree of freedom and led by 25 to 45 unscaled, at most 29.0 scaled, while true q12 and coupler series led by 24 to 384 scaled) | survives, critical; a noise model whose center misses a batch's visibility by more than `VISIBILITY_TOLERANCE` (0.0083) takes an infinite chi-square and `truth_row` takes the largest reachable visibility; the separation is `SEPARATION` times max(1, least sum per degree of freedom); value 9 calibrated it (no wrong label at 30, 35, 40), value 10 recorded 30 with one wrong label in 500, the owner fixed 40, value 11 records no wrong label; q8 phases of 0.17 rad and less pay for it (own label in 36 and 37 of 500) |
| F7 | Damping coverage claim and interpolation error (codex 2) | the 13-point grid and its interpolation | survives; `FIT_DAMPING` computes all 49 multiples directly and the table key binds the error-law bytes, arm operations, world items and grid; coverage under the final rule: q12 truth reads `q12_phase` from multiple 0 to 2.125, coupler truth `coupler_phase` from 0 to 1.875, beyond that `phase_unresolved` or (from 2.875, q12) `offset_absent`, never a wrong error world |
| F8 | Margin chronology (codex 5) | `calibration.json` (value 0, margins 0 and 6.63) is retained with its command | survives as stated; CASE.md "Limits" says the order rests on file times alone and that the four-world decision keeps the margin |
| F9 | The table cache key lacks implementation digests (codex 6) | key content | survives; fixed in `table_directory()` (`TABLE_VERSION` 2) |
| F10 | "Every circuit but `b0-rx`" is overbroad (codex 7) | readout circuits carry no `Rz` | survives; CASE.md reads "every arm of a data batch, and the bridge's padded center"; the downstream-schedule hypothesis stays a stated limit |
| F11 | Noise outside the fitted family (agy) | pure phase or amplitude damping, inverted ratio, pulse damping and depolarizing CZ to 0.05 read their own labels | recorded as supporting evidence, not rerun |

## Round 3: codex on e5ba2a787 (rules R2 to R6, value-12 record)

The reviewer's sandbox refused its report write, so the report text was recovered from its session record. Verdict:
not ready for approval.

| # | Finding | Check against the source | Disposition |
|---|---|---|---|
| 1 | `exact_parabola` reads a true phase (q12 -0.15 rad with CZ damping x3, 6 of 500) and `wrong_labels()` omits it | the retained counts show 6 of 500 (value 11: 1 of 500); `wrong_labels` listed error worlds only | survives; fixed in `098e01c2a`: `wrong_labels` counts `exact_parabola` for phase and mixed scenarios, the label's meaning narrows to "no phase is needed at this offset", CASE.md rule 4, the labels table and the operating-characteristics prose restate it, and `test_exact_parabola_misreads_a_phase_and_not_exact_gates` pins it; `small_phase.py` measures the rate for 0.05 to 0.12 rad phases |
| 2 | No exit-0 full regression transcript | the first run passed part 1 and failed in part 2; the rerun passed part 2 alone | survives; a full rerun writes `readout-flip/r6_regression.log` |
| 3 | Committed logs carry local absolute paths; the timing log is malformed | three logs held local paths; a resource-tracker warning cut the timing JSON | survives; the two regression logs and the timing log were regenerated with stderr kept out, and two warning lines were removed from `nuisance_first12.log` and noted in the README |
| 4 | The value-8 counts have no retained record | no seed-8 record survives (later writes replaced `prediction.json`) | survives; CASE.md, the probes README and the generator comment state that the record is not retained |
| 5a | The `exact_parabola` center range +0.0023 to +0.0050 is unsupported | `nulls.json` gives 0.00232 to 0.00496 | refuted; CASE.md cites `nulls.json` |
| 5b | The exact-world flip bias is unsupported | only ignored part files held the numbers | survives; `readout-flip/nuisance_flips.json` is written from the part files and the README states the means it holds |

The commits `e6e86e9e3`, `3e78c7416` and `cbda06344` (the value-12 record and the small-phase reading) and the QRNG reseeding of the flip probes
(`d18461253`, `08371509c`) follow this round. The phase refit of pull request 933 corrected the damping citation
independently: (0.019, 0.031) are the CZ terms of `five_noise_terms_selector_flip`, not of the five-term fit, and the
ratio sits between the two fits', so the grid stands and the citation moved (CASE.md, generator comment).

## Round 4: Advisor on 031e12272 (partial read)

The extent of the read beyond the items below is not recorded.

| # | Finding | Disposition |
|---|---|---|
| 1 | The seed swap, the nuisance degrees-of-freedom fix (confirmed by inference) and the cross-check | confirmed |
| 2 | Blocking: `final_round.py`, new on the branch, carries a pseudo-random seed (20261119) and falls under the owner's ruling that seeds come from a QRNG draw | survives; fixed in `864ab8cf8`: the seed is value 35685, index 2 of the QRNG draw `draw-2026-11-16T041214Z.json` |
| 3 | CASE.md and README prose with "2.125", "pseudo-random" and "sampling alone" to recheck | survives; prose fixed in `864ab8cf8` |
| 4 | Hosted checks | the six checks read SUCCESS on 031e12272; the pull request body scan was clean |

The case-directory `--check` exited 0 in 4,089 s at `864ab8cf8`.

## Round 5: hosted Codex on 864ab8cf8

The request was an `@Codex review` comment at 12:14Z and the review posted at 12:22Z with three inline threads. Each
reply begins with its disposition and each thread is resolved.

| # | Thread | Finding | Disposition |
|---|---|---|---|
| 1 | scripts/qi_pathion_null_phase_scan_cases.py (P2) | An admitted batch whose center visibility no noise model reaches returns infinite chi-squares, and `--analyze` then fails at `json.dumps(..., allow_nan=False)` instead of writing the legitimate `none_adequate` decision | Fixed in 80985b3ae: `decide()` keeps the infinities for its comparisons and reports each as null with an `unavailable` field naming the worlds and the reason; `test_a_series_no_world_reaches_writes_its_decision_with_null_statistics` serializes the report under `allow_nan=False` through `report_text()` |
| 2 | same file (P1) | The 25 readout-flip fits run serially on the hardware path regardless of `GOROROBA_WORKERS` | Fixed in c8419222e: `fit_flips()` maps one fit per flip through `parallel.ordered_map` and reduces in flip order with `keep_least()`, so the smaller flip wins a tie; each worker clears its caches after its flip; the decision on a planted series is byte-identical to the serial one (47.0 s serial, 8.6 s on 8 workers, 445 MB peak resident per process); `test_the_readout_flips_mapped_over_the_pool_equal_the_serial_loop` pins it |
| 3 | same file (P1) | The fitting engine (`fit_batch`, `seen_contrasts`, `decide`) belongs in `gororoba_quantum/` and not in the case-generation script | Boundary: the move turns module state into explicit inputs and changes the producer that the case directories and the retained probe records bind; it needs its own `--check` and a review of the probe records; tracked in https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/939 |

## Round 6: hosted Copilot on c8419222e

Copilot was requested because round 5 needed a fix. Two medium threads, both resolved.

| # | Thread | Finding | Disposition |
|---|---|---|---|
| 1 | calibrate_separation.py | A rerun overwrites the retained R5 separation record under the R6 defaults (fitted flips, 5,000 null series, more scenarios) | Fixed in 2bd9b4833: the script takes its rule as an argument; `r5` passes the historical rule (flip 0, the 25 scenarios of value 9 in their order, 500 series each) and writes `separation_calibration.json`, reproduced byte for byte on value 9 (SHA-256 53c1d77995c053ddcc7650470d8bfe9506f8e4e9138fa8b4cf4d993a4349d2d4); `r6 --index N` writes `separation_calibration_r6.json`; an invocation without a rule exits without writing; tests cover each case |
| 2 | probe_decision.py | The `coverage` and `nulls` modes overwrite the retained R5 `coverage.json` and `nulls.json` under R6 defaults | Fixed in ff28e5166: those modes write `coverage_r6.json` and `nulls_r6.json`; the new `coverage-r5` and `nulls-r5` modes pin `flips=(0.0,)` and are the only writers of the R5 files; reruns of all four modes on a second host reproduce the four retained files byte for byte; the README table and docstring name each mode's rule and file |

## State at the merge decision

- Head ff28e5166: the six hosted checks read SUCCESS (lint, types, tests, contracts, arm on ubuntu-26.04-arm and on
  macos-15); CodeRabbit was skipped. The case-directory `--check` was last run at c8419222e (exit 0, 4,944 s) and not
  rerun at ff28e5166, since the generator is unchanged and no ledger binds the two touched probe scripts and
  README. The suite read 62 passing tests at ff28e5166.
- Open, as hypotheses with no discriminating run yet: `test_seed_provenance.py` failed 10 tests once under a load
  average near 60 (the failure text was not kept) and passed alone, on rerun and in five runs under concurrent
  load; the cause is a load-sensitive timeout or shared temporary state, and no run reproduced it.
- Follow-up issues: https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/938 (one Kraus damping law for
  the histogram fit and the elementary error laws) and issue 939 (the fitting engine move, round 5 thread 3).
- Case status: the case is a request for hardware time; the QX twin and the Tuna-17 series stay unsubmitted until
  the owner approves them.
- The owner decided on 2026-11-16 to add this record and then merge.
