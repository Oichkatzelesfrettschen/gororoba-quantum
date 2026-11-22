# Review record: claims for seven recent hardware series

Reviewers (owner's selection for pull requests 978 to 981, 2026-11-22): codex on gpt-daybreak-blue at high and grok as reviewers; agy on gemini-4-neon-high and opencode on opencode-go/deepseek-v4-pro as red-teamers; the Advisor last. All four read one brief covering the four pull requests at the heads below; this record keeps the findings on pull request 981 (head read 885e75d3b). Raw reports stay outside the tree.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, agy, grok | Every evidence digest matches its file and every statement matches its result document and analysis record | Confirmed |
| 2 | agy | The q4 slope difference is 9.76 standard errors from the unrounded record, not 9.7 | Fixed in 1a263d52e, in the claim and the note |
| 3 | opencode | The Grover depth claim pairs a raw f with a corrected-f z | Refuted: z -3.37 = (-0.1222 - 0.0104) / 0.0393, the raw statistic of analysis.json |
| 4 | codex, grok | The results-index edit changes only the claim-timing rule | Confirmed |
