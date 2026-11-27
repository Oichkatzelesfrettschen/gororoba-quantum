# Review of the induced slice map of same-sign X and the comparison of its module maps

The change adds [the X slice-map directory](../../../evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/README.md),
the `--family x` mode of `slice_module_map_comparison.py` in
[the kernel-attachment evidence](../../../evidence/a5-kernel-attachments/README.md), ledger rows A5-644 and A5-645 of
[ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv), and moves the slice-comparison row from the
duplicated id A5-642 to A5-643 (pull request 1026, issue 1025).

The owner chose one local reviewer, `opencode` on a free DeepSeek model, and the Advisor last. `opencode` ran
`opencode/deepseek-v4.1-flash-free` through `opencode-redteam.sh` on [the brief](brief.md) at head c96ea49f1
(verdict `ok`, a report of 8182 characters: [review-opencode.md](review-opencode.md)); the brief and the report are
retained with the worktree path written as WORKTREE. The Advisor read head 157129faa with that report. The
dispositions below are in af4d57df2 and in the commit that adds this record, both before the hosted round.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| opencode 1: the driver ran 18 Singular processes in serial shell loops, against the `parallel.py` rule | fixed in af4d57df2: `x_induced_slice_map.py --run` sends the six Q(i) scripts and the twelve reductions through `parallel.ordered_map`; 11 s on the workers of the compute host against 35 s, 22 s on one worker, every retained file byte for byte the same |
| opencode 2: the X paragraph of the comparison docstring did not say that the identity is forced | fixed in af4d57df2 |
| opencode 3: the other-root control rejected only the line with two zero remainders | fixed in af4d57df2: a control passes only with the FAIL verdict and nonzero remainders in both directions |
| opencode 4: a mutation test asserted only that some problem is reported | fixed in af4d57df2: `REASONS` and `X_REASONS` name the one text every reported line must hold, for the 22 E8-bar and the 10 X mutations |
| opencode 5: the record prints symmetric residues and the ledger the residues in [0, p) | no change: one value in two spellings; `problems()` compares modulo the prime and a test covers the symmetric form |
| opencode 6: the subject of c96ea49f1 has 85 characters | Refuted: the 72-column rule of the workspace guide covers commit-body lines |
| opencode 7: 826052e37 drops the final newline of the slice-comparison review README | Boundary: c96ea49f1 restores it; the intermediate commit stays, since a rewrite of pushed history needs a force-push |
| opencode, structural statement: the reduction logs of X- and X+ are byte-identical at each prime, so the six cells carry three independent tests | accepted in a narrower form: `witnesses.jsonl` holds a sign isomorphism of the two header presentations at 32009 and 32029 (the ideals compared at 32029 alone, no witness at 32057), and equal logs show equal counts and no more; the X README and A5-644 call the two cells correlated and state no count of independent tests; the sign of the module-map scalar as a consequence of that isomorphism is a labeled hypothesis with its test |
| opencode, process: one `python3` call on the session host, which the brief forbade | recorded: it loaded `ci/gates.json` and computed nothing |
| Advisor: issue 1025 and the pull-request body quoted `ledger.py --check` on `main`, which had not been run; the measurement was a duplicate scan of the id column | run on the compute host at ebca38361: `A5-642: id used more than once`, exit 1, as both texts state |
| Advisor: the literature note on A5-548 named search terms whose hits had not been read, counted works where it had counted transcriptions, and moved the date of the last status change | fixed: every hit of every named term read in its line, the count stated as 155 transcriptions, the terms whose hits have another sense named as such, the date restored |
| Advisor: "one line of evidence at each prime" overstated the witness | fixed with the structural statement above |
| Advisor: `--run` started Singular without a timeout or an address-space cap | fixed: the cap and the timeout of the weight-slice producer; the retained files are unchanged |
| Advisor: the scalar depends on G as well as on the two normalizations; A5-598 still read "not covered: X" | fixed in A5-645 and A5-598 |
| Advisor: a second id race | checked before the hosted round: no branch on the remote adds a row A5-643 to A5-649 |

## Open

- `hypothesis:` the opposite signs of the scalar on X- and X+ follow from the sign isomorphism of the header
  presentations; the test is to transport the X- module maps by it.
- Opposite-sign X, W8 and Iso have no retained slice map.
