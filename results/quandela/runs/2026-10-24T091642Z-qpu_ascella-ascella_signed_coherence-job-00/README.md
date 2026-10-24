# Ascella signed-coherence acquisition

Ascella completed the frozen 64-setting signed-coherence request of
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md)
under the owner's approval of its
[written acquisition case](../../../../docs/design/ascella-signed-coherence-conformance.md#written-acquisition-case).
The sent body matches the retained request: its digest without `process_id`
is `e323b1c6fd98747215a7c7a4574ab10a08f5392c1fc0b5edfafafcde09905c07`, and
the cases digest is
`3c92af45df7502bab5c6f2d74779aa83b04f7af2094b62b499b6e29ca0e69520`.

| Observation | Result |
|---|---|
| Job | `739a5271-bb84-42b7-9fc3-0562ca5cef47` |
| Submitted / started | 2026-10-24 09:18:04 / 09:18:14 UTC |
| Terminal status | completed |
| Settings / detected samples | 64 / 524,288; 8,192 per setting |
| Provider execution duration | 186 seconds (case: 200 expected, 300 cap) |
| Token-reported debit | 1.016384 free credits; zero paid credits |
| Platform at plan | available; HOM 87.72 %, g2 1.9 %, clock 13.33 MHz |
| Client versions | perceval-quandela 1.3.1, exqalibur 1.4.2 |

The token's Ascella totals move from 7 jobs, 31 seconds and 1.016384 free
credits to 8 jobs, 217 seconds and 2.032768 free credits. This is the first
completed Ascella job with a twelve-entry input, an explicit empty mitigation
list and more than eight iterations.

The [preflight](preflight.json), [submission](submission.json),
[sent body](job-body.json), [checkpoint](submission-state.json),
[raw result](raw/result.json) and [parsed results](results.json) retain the
request and service response. `platform-before/` and `platform-after/` hold
the platform catalogue and the observation of every readable Quandela cloud
and account route, taken before submission and after collection.

## Analysis

[`ascella_coherence_run.py --run`](../../../../scripts/ascella_coherence_run.py)
writes [analysis.json](analysis.json) and reproduces its bytes on a rerun.
All 27 preregistered endpoints qualify; none is falsified or inconclusive.
The analysis admits 524,175 twelve-mode single-photon events and excludes 113
multiple-occupation events and no vacuum events.

| Endpoint group | Result |
|---|---|
| Sign-odd X, Y and dark coefficients (15) | every one qualifies; largest deviation 0.0303 |
| Sign-even X and Y coefficients (10) | every one qualifies; largest magnitude 0.0116 |
| Mutation difference | 0.1646 against ideal 0.1727, radius 0.0229 |
| Mutation dark | 0.0008 against ideal 0, radius 0.0162 |

Two coefficients qualify under the 0.05 tolerance while their intervals
exclude the exact ideal: the X sign-odd constant reads 0.4697 (radius 0.0102)
and the Y sign-odd sin(2 theta) coefficient reads 0.4777 (radius 0.0145),
both against 0.5.

## Events outside the logical block

6,659 of 524,288 events (1.27 %) fall outside the logical block, against the
case's dark-count bound of about 0.91 % per setting. The share is setting
specific: it ranges from 4 to 586 events per setting (0.05 % to 7.2 %),
and no readout or arm groups the large values; the six largest are
`theta3-direct-arm3` (586), `theta3-y-arm3` (549), `theta0-x-arm3` (542),
`theta4-y-arm2` (531), `theta0-y-arm1` (449) and `theta2-x-arm0` (344).
Dark counts in proportion to the reported detector rates predict a
setting-independent share, so these events come from a rate-independent,
setting-dependent mechanism, which the case named as the condition that breaks
its bound. Eligible events include the outside-block events, so they dilute
every coefficient; that the 2 to 6 % attenuation of the two sign-odd
coefficients excluding their ideal comes from this dilution is an inference
of medium confidence, which a per-setting decomposition of those two
coefficients would confirm or refute. The analysis rests on the
preregistered estimators and tolerances; a model of the outside-block
mechanism is a separate question this run does not answer.

## Later reading

The [device diagnostics](../../../../docs/evidence/ascella-order-coefficients/job-00-diagnostics.json)
and the [permuted repeat](../2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/README.md)
replace the two inferences above. The outside-block clicks are mostly dark
counts (modes 8 to 10) whose exposure alternates with execution position and
grows with the sample budget; the repeat in another order shows no
per-setting cause. Dilution accounts for about a fifth of the two sign-odd
shortfalls: block-conditioned counts give 0.4751 and 0.4851, and the
remainder is an analyzer contrast of 0.970 on X and Y with per-setting
residuals that reproduce across the two jobs.
