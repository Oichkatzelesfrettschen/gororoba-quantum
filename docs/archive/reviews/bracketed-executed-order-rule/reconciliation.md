# Reconciliation of the review of pull request 881

Two local reviewers ran on head `cd5b1064d`, `codex` on `gpt-daybreak-blue-latest` at high effort and `agy` on
`gemini-4-hydrogen-high` in its regular mode, both read-only and both reading the whole pull request: the executed-order
rule of the bracketed one-CZ null case (`evaluate`, `executed_order`, `rule_v2`, the case text and the design notes). The
Advisor reviewed the findings with their justifications and then the fix pass; rows 15 and 16 are its findings on the fix
pass. The raw reports stay outside the repository. C names a finding of `codex`, A a finding of `agy`; each row keys the finding by
its text, gives the check against the source at the reviewed head, and names the outcome with its commit. No check ran on
`cd5b1064d`: the draft pull request showed no workflow run for it.

Commits of the fix pass: `b2faddcfe` (code, manifests and tests), `ad4d838ea` (case text and design notes),
`767e297d4` (label wording and the test seed), `7f2b2ae6a` (the QX digest test), `27bab9471` (the pinned reader and the
stress tables). Commits after it: the pinned producer, the stamp, tie, covariance and digest tests, the case statements.

| # | Finding (reports) | Check against the source | Outcome |
|---|---|---|---|
| 1 | The manifests and `prediction.json` preregister the plain pool and not the executed-order rule (C1) | `preregistered()` restated `estimates` as inverse-variance pooling; the Tuna-17 text and the registered outcomes lacked the five labels | fixed in `b2faddcfe`: the Tuna-17 manifests and `prediction.json` state the executed-order text once with the five labels; no checked file cites their hashes. Boundary: the four QX manifests keep the control text, since the hosted receipts bind their sha256 (`cases_sha256`); the case text says so (`71bbdff16`) |
| 2 | Shared drift couples the template contrasts and rule v2 pools them as independent (C2) | `var(t_T)` alone entered the pool; `cov(t_T, t_U) = x_T x_U var(g)` was omitted | fixed in `b2faddcfe`: the decision pools with the covariance (`pool_correlated`); the independent pool understates the error in 24 percent of series at flip rate 0.25 and overstates it in the rest. A three-batch fixture now pins the covariance, the pool and its chi-square by hand arithmetic (`02ed6b080`) |
| 3 | A non-ISO, naive or mixed-offset stamp bypasses the fail-closed label (C3, A2) | ranking by raw text; a stamp on an exact second sorts after its fractional neighbors | fixed in `b2faddcfe`: stamps rank by integer-microsecond instant in every path; mixed spellings are tested in the twin offsets, the seconds, the strict gate and the decision (`02ed6b080`) |
| 4 | A null stamp raises `TypeError` and no label is read (A1) | `oc.evaluate` sorted the raw stamps | fixed in `b2faddcfe`: a null or absent `queued_at` reads `unresolved_order` through `evaluate` and `analyze` |
| 5 | Equal start stamps have no stated rule (A2) | two circuits of a twin batch at one instant have no executed order | fixed: the tie reads `unresolved_order`; a tie outside a twin batch is counted by the strict gate and withholds nothing; stated in the case text (`71bbdff16`) and tested for equal text, two spellings and one microsecond apart (`02ed6b080`) |
| 6 | The heterogeneity gates do not carry their stated chi-square law (C4, A4a) | the errors carry f >= 1 | bounded: false rejects of the batch gate stay under 0.5 percent per world and the drift gate fires on about 1.0 percent of series; the design note calls the gate conservative |
| 7 | The monitor places c at the mean readout time though the readouts differ in time (C5, A4c) | the term (u + v)(t1 - t0) / 4 enters c | bounded: 5.8e-5 (twin batch) and 3.9e-5 (base batch) at 0.01 per hour, 6.3 and 4.2 percent of the offset standard error; recorded in the design note |
| 8 | The stored power tables describe the old row-pooling rule (C6) | `_series_label` called `decide_estimates` on unstamped rows | fixed in `b2faddcfe` and `ad4d838ea`: five executed-order tables regenerate through the case generator and the case text cites them |
| 9 | `label_if_order_ignored` appears on a withheld decision only, and the quadrature and batch counts differ from the code (C7, A5) | `unresolved` wrote it; a decided record held the top-level key only | fixed in `ad4d838ea` and `767e297d4`: `order_ignored_label` on every record, `label_if_order_ignored` on a withheld decision; the counts and the quadrature wording match the code |
| 10 | The reordered-series test shares its helpers with the code under test (C8, A6) | the fixture monkeypatched `evaluate_decision`, `bracket_series` and `calibration_readings` | fixed in `b2faddcfe`: a hand-written pairing fixture with literal batch ids; `bracket_series` and `calibration_readings` run on hand-counted shots; `also_withheld` is covered; the real `evaluate_decision` runs in the fail-closed tests |
| 11 | 14.77 lacks a retained derivation (C9) | the eight z^2 terms are not stored | fixed: recomputed as 14.7723 (p 0.0637) from the retained shot lists; the command and inputs are in the pull-request body |
| 12 | A false `unresolved_drift_heterogeneity` from float rounding when one template varies (A3) | `own - shared` of order 1e-18 against an error of 0 | confirmed by run (652 of 1,970 random series); fixed in `b2faddcfe` with `DRIFT_DEPARTURE_FLOOR` and `OWN_DRIFT_FLOOR`; the test stays |
| 13 | Twin drift per rank and base drift per second, and the calibration error choice (A4b, A4d) | design properties of the registered rule | bounded: recorded as hypotheses in the design note |
| 14 | Hosted macOS arm64 fails the digest test that hashed a rebuild of the QX manifests | a rebuild rounds a 12-digit float differently there (hypothesis: last-bit libm or fused multiply-add) | fixed in `7f2b2ae6a`: the stored bytes are hashed; the rebuild equals them on linux x86_64 and is tested only there (`02ed6b080`); issue 945 tracks a platform-stable serialization |
| 15 | Advisor, fix pass: `pathion_coset_analysis.py` is bound by sha256 in two retained submissions | the Kaggle submissions of 2026-11-13 and 2026-11-14 list its digest | fixed in `27bab9471`: the edit is reverted and a missing `queued_at` reads as a null stamp through the bracketed analyzer's own `load_run` wrapper |
| 16 | Advisor, fix pass: the 80 percent power claim needs the rule's own stress | the margin over 80 percent is stated at the rule's own stress drift only | fixed in `27bab9471`: two executed-order tables at independent and pair-common drift 0.003 (81.6 and 83.8 percent; 87.2 and 89.2 percent); the Wilson interval is in the case text (`71bbdff16`) |
| 17 | A pin sweep over every ref finds `qi_pathion_one_cz_null_cases.py` bound by the same two submissions, and the pull request edits it (verification pass) | 14 hits of one digest in 7 refs; no check re-hashes the script against the submissions, and the submissions are written once at push time | fixed in `743bd05b2`: the file returns to the bytes of main (blob `2f9420ead`); `rule_v2.simulated_shares` carries the successor simulation and regenerates the stored rule-v2 record byte-equal |

Conjectures of the reviewers (hypothesis, not added to the rule): elapsed time and not rank as the twin drift coordinate;
common-mode motion of the two readouts tripping the monitor; reordering that depends on circuit duration or role. The
retained stamps can test the last without a provider job.

## Process slips

- Three commit subjects of the fix pass exceed 72 columns (`b2faddcfe`, `767e297d4` and `ad4d838ea`); they stay, since a rewrite
  after the push would need a force-push.
- Items 1 to 5 of the fix pass landed in one commit (`b2faddcfe`: code, manifests and tests), so the mechanism changes are not
  separable by bisection.
- Two repository-wide searches ran on a build host during the review, outside the allowed list; no other computation ran there.
- The second pinned file (row 17) was found by the verification pass and not by the earlier sweeps, which named one.
