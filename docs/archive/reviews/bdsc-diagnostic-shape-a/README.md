# Review record: Belenos six-slot diagnostic successor (shape A)

Reviewers (owner's selection for pull requests 982, 983 and 984 and gororoba-open 303, 2026-11-22): codex on gpt-daybreak-blue at high and grok as reviewers; agy on gemini-4-neon-high and opencode on opencode-go/deepseek-v4-pro as red-teamers; the Advisor last. All four read one brief covering the four pull requests; this record keeps the findings on pull request 983 (head read 24f3fbcd9). Raw reports stay outside the tree.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | agy | The power statement modeled the two blocks as independent replicates, while block 2 repeats block 1's returned circuits, so a seed's effect is common to both blocks and the pooled statistic is (1 + 2 k (s / e)^2) X + Y with X and Y chi-squares of df / 2; at six slots `seed_common` reaches power 0.908 rather than 0.95 at the stated ratio (Monte Carlo, 400,000 draws) | Fixed in fb2f6fae0: `rejection` integrates that law and `detectable_ratio` inverts it; the six-slot ratios move to 0.801 and 0.958 (`seed_superposition`), 0.664 and 0.879 (`seed_common`), 0.880 and 1.066 (`seed_interaction`), within 0.002 of agy's Monte Carlo; the test integrates over the other variable, checks the size at a zero effect and that each ratio exceeds its independent-block value; the runbook table and case record follow |
| 2 | codex, agy | The forked `self_test` carries four-element seed and endpoint vectors and `v["n"] == 16`, so the six-slot `--self-test` indexes past them | Fixed in fb2f6fae0: the fork replaces `self_test` with a refusal naming the six-slot synthetic runs of the test file; a test checks the replacement |
| 3 | agy, grok | The forked `draw_values` refuses a repeated seed with the frozen text "four distinct seeds" | Fixed in fb2f6fae0: a successor `draw_values` reads SLOTS in its refusal; a test feeds a 150-value draw whose sixth seed repeats the first |
| 4 | opencode, agy | `DRAW_VALUES = 150` draws 72 values (indices 78 to 149) that block 2 never uses, since a block-2 instance reuses its block-1 match's order value | Boundary: the frozen formula's count and CASE.md shape A's figure; the module docstring states the unused range |
| 5 | codex, grok, opencode | The frozen producers keep their bytes; counts, price, draw citation and the authorization text match shape A | Confirmed; no change |
| 6 | (this round) | Recomputing the power statement on every case-record call made the readout tests slow | Fixed in 4b1de7893: the ratios are cached per process (45 tests in 20 s on the compute workstation) |

The rebuilt case record has sha256 872b3c529844b4e77814597ba917e0bb39ff4a56475a73cfb112282eda876131 (was c3773a3c3db0092c8f70338e675e5671ab4fbdd353f2516e463e39d30365021e); nothing has been submitted.
