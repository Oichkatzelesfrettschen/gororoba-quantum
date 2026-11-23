# Review record: records corrections and the Moreno review record (pull request 993)

Subject: the novelty labels of docs/notes/prior_work_synthesis.md, the singular-sector-split boundary of
docs/state/research_state.json, the literature section of docs/evidence/a5-stiefel-pfaffian-germs/README.md and the
review record docs/archive/reviews/moreno-stiefel-answer/README.md. The seats read 193be559b: codex on
gpt-daybreak-blue at high effort (reviewer) and opencode on opencode-go/deepseek-v4-pro (red team). Raw reports stay
outside the tree.

| # | Seats | Finding | Disposition |
|---|---|---|---|
| 1 | codex, opencode | The prior-work credit exceeded its propositions. BCDI Prop. 7.4 covers the sedenion Stiefel zero divisors (42 index pairs), not every two-term element. Skiouris Prop. 2.2 covers e_i + e_j with i in 1..15, j in 17..31 (126 of nullity 12, 84 of nullity 4, 15 of nullity 0) and excludes e_16 and the same-half pairs. Prop. 2.2 is in the pathion preprint, published 2026-08-24, not 2026-08-19 | Fixed in docs/notes/prior_work_synthesis.md: each credit is narrowed to its domain with the date and Zenodo record. The claim singular-sector-split keeps its bytes, since the algebra-device-conjectures bundles 2, 8 and 15 bind it |
| 2 | opencode | BCDI 2007 Prop. 8.2 (the elements reaching 2^(n-1) - 4; "BDI II" in the singular-sector note) was dropped from the credit | Fixed: credited in docs/notes/prior_work_synthesis.md under the table's name BCDI 2007 |
| 3 | codex | "de Marrais read in full" conflicts with the reading scopes their notes record | Fixed: the claim is narrowed to the portions read, and the novelty of the rest is unassessed |
| 4 | codex, opencode | Moreno review rows 2 and 3 cite reviewer computations (384 and 840 elements) that the tree does not retain | Fixed: both rows read "Reviewer-reported: the computation was not retained in the tree" |
| 5 | opencode | Row 4 read as if the reviewers had re-run the Rocq kernel check of the A_6 witness | Fixed: the row credits the gororoba-math gate's rocq check, not a reviewer run |
| 6 | opencode | "Question 1" is Moreno's unnumbered question; its page | Fixed: the subject names the question of Section 5, p. 25. The paper's page footers place the question on p. 25 and the second, "Open Question" (on the forms of b), on p. 26; docs/notes/math-0512517.md says p. 26 for the first, a slip this pull request leaves to the note's next edit |
| 7 | codex, opencode | The literature section gave counts without query strings or identifiers, and kept a stale "twelve" next to "thirteen" | Fixed: a table of every query, its raw count and identifiers; the earlier count is dated |
| 8 | codex, opencode | No digest-pinned file changed | Confirmed: the sha256 of each changed file's main version matches nothing in this repository or gororoba-open |

## Advisor

The Advisor read the record after both seats and found five errors they missed, each checked against the sources and fixed:

- The citing-list comparison named the wrong differences. Ten works are shared. OpenAlex alone lists BCDI II and Latre;
  Semantic Scholar alone lists Koebisu 2512.13002, the false match and the 2007 report.
- arXiv 2608.26893 and 2608.26890 cite the preprint as background in range citations, not in their reference lists
  alone.
- "Read in full" now follows each paper's recorded reading scope. Koebisu's A_5 note records none. The later Moreno
  items were screened by title.
- BCDI 2009 Prop. 7.4 covers every sedenion zero divisor (a, b), not only the 84 two-term elements that the first
  correction named.
- The main-branch boundary of singular-sector-split ("Two-term elements only; the de Marrais higher-dimensional
  comparison and any hardware echo contrast remain open") states no novelty, so the bundle-bound claim needs no
  successor.
