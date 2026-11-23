# Review record: IQM billing refit with per-shot duration terms

Reviewers (2026-11-22): codex on gpt-daybreak-blue at high as reviewer; opencode on opencode-go/deepseek-v4-pro as red-teamer (owner's substitute for agy, whose quota reads exhausted until about 2026-11-28). Raw reports stay outside the tree.

| # | Reviewer | Finding | Disposition |
|---|---|---|---|
| 1 | codex | The Emerald miss rejects the Garnet-fitted linear duration terms, not the padding mechanism, which two Emerald jobs cannot reject | Fixed in 87bb94c93: the README states it and keeps padding or a nonlinear train-length dependence open |
| 2 | codex | The 13-credit ceiling is the conservative all-jobs band choice; the Grover-only band needs 10 to 11 | Fixed in 87bb94c93 and the next commit: both bands stated; the record field reads case_max_credits, since the spend is not approved |
| 3 | codex | The maximum-duration term improves Garnet only without the anchor job and in sample; over all jobs its leave-one-out root mean square worsens | Fixed in 87bb94c93 |
| 4 | opencode | The pooled two-device fits carry negative coefficients (v4_pad per-mid-record, v4_sum per-circuit-shot, the Emerald offset), a sign the duration terms sit at the edge of identifiability | Boundary: the pooled fits stay out of sizing; the Garnet-only fits used for sizing have positive coefficients |
| 5 | codex, opencode | Inputs and arithmetic: 20 retained jobs read through the validated reader, schedules match to 1e-18 s, serial regeneration reproduces the record | Confirmed |
