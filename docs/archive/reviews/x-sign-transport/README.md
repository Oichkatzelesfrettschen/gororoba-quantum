# Review of the sign transport of the same-sign X module maps

The change adds `x_sign_transport.py` and its record to
[the kernel-attachment evidence](../../../evidence/a5-kernel-attachments/README.md), ledger row A5-647 of
[ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv), the gate `core-a5-x-sign-transport`, the decision
on the registry entry of X+ at 32009 in [the registry-regeneration record](../registry-regeneration/README.md) and
[the evidence README](../../../evidence/a5-exceptional-fibers/README.md), and the close of the Moreno lead in row
A5-548 (pull request 1028).

The owner's reviewer question went unanswered, so the recommended default ran: `opencode` on a free DeepSeek model,
then the Advisor. `opencode` ran `opencode/deepseek-v4.1-flash-free` through `opencode-redteam.sh` on
[the brief](brief.md) at head 10aed094b (verdict `ok`, a report of 6513 characters:
[review-opencode.md](review-opencode.md)); the brief and the report are retained with the worktree path written as
WORKTREE. Its 63 shell calls were `grep`, `sed`, `git`, `head`, `wc`, `ls` and one `sha256sum`; it started no
interpreter. The Advisor read head f5b596e75 with that report. The dispositions below are in f5b596e75 and in the
commit that adds this record, both before the hosted round. The row on the hosted round was added after it and changes no file the round read
apart from this record.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| opencode 1: `problems()` accepted a record in which only one of the 15 substitutions with one more generator negated failed, while the row and the README say that none carries ideal to ideal | fixed in f5b596e75: the row of 15 must be all zero; mutation "one added sign accepted" |
| opencode 2: the README counted 22 mutations where the test held 21 | fixed: the test holds 24 after the two fixes and the README says 24 |
| opencode 3: `control_indices` was in the field set and never read; the fixture's indices differ from the record's | fixed in f5b596e75: the check of `slice_module_map_comparison.py` (three indices, each at least 1, the last two distinct), with two mutations; the indices name the generators a control acts on and their values are not part of the finding |
| opencode, minor: "its registry entry comes from the X- row" overstates what `transport()` copies | fixed: "the degrees and certifications of its registry entry come from the X- row" |
| opencode, minor: the prediction is asserted by the row alone | no change: the docstring of the program held it before the first run, and no file retains that earlier state; the row says "written before the first run" and no more |
| opencode, triviality: both scalars and the diagonal shape are derivable from the retained records without a run | accepted and stated in the docstring, the README and A5-647: the run adds the matrix of S_w, the sign vectors at 32057, the transport of the ideals over Q(i) and the controls |
| opencode, structural statement: S_w followed by conjugation preserves K_w(X-), "a real structure on the 27-dimensional quotient" | accepted in a narrower form: S_w is a real involution and both S_w and conjugation carry K_w(X-) onto K_w(X+), so their composite is a semilinear involution that maps K_w(X-) to itself; stated as a deduction. The number 27 is the count of nonzero remainders of the identity control and names no quotient |
| Advisor: the A5-548 sentence named "the search terms" where the first search had used another list | rerun with the row's own terms on the two transcriptions (Macaulay, Hilbert, nilradical, reduced, Pfaffian, variety, scheme, ideal, quadric): one hit, "reduced to", as the sentence says; the second zbMATH record read: arXiv:math/0512517 |
| Advisor: issue 1029 said the hosted lanes were green and named an idle core, neither measured | corrected in the issue: hosted run 46052574002 on head 10aed094b passed, its durations are in the table, and the serial timing is marked as taken under load |
| Advisor: the pull-request body named an old head and counts and said the full lane had not run | body rewritten for the final head |
| Hosted Codex round on head 3495da4d2 | clean, no review thread; the ten checks passed on that head |
| Advisor: `build_registry.py` reads `k2-hilbert.jsonl` alone, so a successor file by itself would not reach the registry | the README sentence now says the route needs a registry change and a `k2-span` witness as well |

## Open

- The module-map scalars are measured at three primes; no module map is solved over Q(i) in this run.
- Opposite-sign X, W8 and Iso have no retained slice map.
