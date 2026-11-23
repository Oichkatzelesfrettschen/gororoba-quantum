# Review record: records corrections and the Moreno review record (pull request 993)

Subject: the novelty labels of docs/notes/prior_work_synthesis.md, the singular-sector-split boundary of
docs/state/research_state.json, the literature section of docs/evidence/a5-stiefel-pfaffian-germs/README.md and the
review record docs/archive/reviews/moreno-stiefel-answer/README.md. The seats read 193be559b: codex on
gpt-daybreak-blue at high effort (reviewer) and opencode on opencode-go/deepseek-v4-pro (red team). Raw reports stay
outside the tree.

| # | Seats | Finding | Disposition |
|---|---|---|---|
| 1 | codex, opencode | The prior-work credit exceeded its propositions. BCDI Prop. 7.4 covers the sedenion Stiefel zero divisors (42 index pairs), not every two-term element. Skiouris Prop. 2.2 covers e_i + e_j with i in 1..15, j in 17..31 (126 of nullity 12, 84 of nullity 4, 15 of nullity 0) and excludes e_16 and the same-half pairs. Prop. 2.2 is in the pathion preprint, published 2026-08-24, not 2026-08-19 | Fixed: both texts narrow each credit to its domain and give the date and Zenodo record; the remaining split is the repository's |
| 2 | opencode | BDI II Prop. 8.2 (the elements reaching 2^(n-1) - 4) was dropped from the credit | Fixed: credited in both texts |
| 3 | codex | "de Marrais read in full" conflicts with the reading scopes their notes record | Fixed: the claim is narrowed to the portions read, and the novelty of the rest is unassessed |
| 4 | codex, opencode | Moreno review rows 2 and 3 cite reviewer computations (384 and 840 elements) that the tree does not retain | Fixed: both rows read "Reviewer-reported: the computation was not retained in the tree" |
| 5 | opencode | Row 4 read as if the reviewers had re-run the Rocq kernel check of the A_6 witness | Fixed: the row credits the gororoba-math gate's rocq check, not a reviewer run |
| 6 | opencode | "Question 1" is Moreno's unnumbered question; its page | Fixed: the subject names the question of Section 5, p. 25 (checked against the paper: the question sits on p. 25; the second, "Open Question", on p. 26) |
| 7 | codex, opencode | The literature section gave counts without query strings or identifiers, and kept a stale "twelve" next to "thirteen" | Fixed: a table of every query, its raw count and identifiers; the earlier count is dated |
| 8 | codex, opencode | No digest-pinned file changed | Confirmed: the sha256 of each changed file's main version matches nothing in this repository or gororoba-open |
