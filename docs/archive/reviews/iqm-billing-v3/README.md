# Review record: Garnet billing model scored on every active-reset job

Reviewers (owner's selection for pull requests 978 to 981, 2026-11-22): codex on gpt-daybreak-blue at high and grok as reviewers; agy on gemini-4-neon-high and opencode on opencode-go/deepseek-v4-pro as red-teamers; the Advisor last. All four read one brief covering the four pull requests at the heads below; this record keeps the findings on pull request 980 (head read 7a5fc647b). Raw reports stay outside the tree.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex | Excluding the measure-heavy run selects terms; over all jobs both fourth terms lower the largest leave-one-out residual | Fixed in 7e0bf626d: both criteria reported, no term adopted |
| 2 | agy | Cohort, per-circuit and per-schedule terms beat three terms under the script's own criterion | Fixed in 7e0bf626d: all three fitted and reported (0.18 to 0.19 s against 0.252 s); a cohort shift or per-circuit saving is stated as a hypothesis |
| 3 | agy | Runtime minus execution equals compilation_seconds | Fixed in 7e0bf626d: recorded per job (difference below 1e-15 s) |
| 4 | agy | The curvature term's leave-one-out failure is leverage of the 320,000 circuit-shot job | Fixed: the README states it |
| 5 | agy | The README cited an unretained account read and kept a stale October sentence | Fixed in d4ecd787d: credit_after of the sedenion run is cited and the audit sentence dated |
| 6 | grok | v2's over-prediction of the later jobs grows with circuit-shots | Recorded: consistent with the per-circuit and cohort terms; the hypothesis names the separating job |
