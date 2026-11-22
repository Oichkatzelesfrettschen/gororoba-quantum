# Review record: retention of the Tuna-17 null phase scan series (PR 977)

The retention was written by a Sonnet implementer from a brief and accepted by the parent after a review of its note.
Reviewers chosen by the owner (2026-11-21): codex (gpt-daybreak-blue-latest, high) and grok on one brief; agy Flash
(gemini-3.8-flash-high) as red-teamer. All read head 97a4c3170. The Advisor reviewed last.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, grok | The Tuna-17 analysis provenance ("the log") and the QX byte replay are not auditable from the tree | Fixed: `docs/evidence/qi-null-phase-scan/analysis-provenance.json` holds the commit, commands, environment, exit status, times, runs and digests, and a QX replay rerun at the branch head (00:31 UTC 2026-11-22) with its comparison |
| 2 | codex, grok, Flash | Both open hypotheses carry tests that cannot discriminate them: each batch has its own phase and center, so between-batch drift moves no world's sum except the exact world's; the rule 8 fold decides nothing and folds other arms; a same-data joint refit has no penalty | Fixed: the note says where the excess sits (inside batches) and replaces both with three hypotheses whose tests move the cited chi-squares (replicate pairing by kind, a joint q12-plus-coupler fit narrowed to what it decides, time bins within a job) |
| 3 | codex, grok | "No world's chi-square reaches its adequacy limit" reverses the threshold's direction | Fixed: every world's minimum chi-square exceeds its limit |
| 4 | Flash | Ranking rejected worlds as "nearest" invites a physical attribution | Fixed: the note states that every world is rejected and that the ordering carries no attribution |
| 5 | Flash | The z8c parabola's least point extrapolates past its sampled range, and both parabola errors omit the chi-square scaling and the shared center offsets | Fixed: stated beside the fits |
| 6 | Flash, grok | The q4 slope differs from the retained series' by 9.7 standard errors, which the bridge's center agreement does not cover; the q4 zero angle is poorly located | Fixed: stated beside the q4 line |
| 7 | Flash | The case's budget understated the analysis (3.8 h against about 50 min) and the turnaround (up to 1,965 s per batch) | Fixed: the note's Budget line |
| 8 | grok | The ledger snapshot lists jobs both retained and unretained (taken in a sparse checkout without the runs) | Fixed with the merge after PR 975: a fresh snapshot taken in a tree that holds both series declares no job unretained |
| 9 | grok | CASE.md's status line still reads "awaiting approval" | Boundary: the approved case keeps its bytes; the note quotes the approval each `submission.json` carries |
| 10 | codex, grok | Conjectures: a nonlinear response at the ±30 degree arms; padding that changes the q4 channel | The q4 reading enters the note; the others stay in the reports as leads |

Claims 1, 3 and 5 of the brief stand; every reviewer confirmed the 33 batches, the approval line, the 84 ledger jobs,
the decision fields and the acquisition rows.
