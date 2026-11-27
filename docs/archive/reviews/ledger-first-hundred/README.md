# Review of the first hundred rows of the A_5 claim ledger (pull request 910)

Pull request 910 reconciled rows A5-001 to A5-100 of
[ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv) and added the probes of
[structure/](../../../evidence/a5-exceptional-fibers/structure/README.md). Two local reviewers read its first two
commits on one brief each, the Advisor reviewed last, and the hosted round followed.

| File | Reviewer | Role |
|---|---|---|
| [brief.md](brief.md) | | audit brief |
| [brief-red-team.md](brief-red-team.md) | | red-team brief |
| [review-codex.md](review-codex.md) | `codex` on gpt-daybreak-blue, high effort | audit |
| [review-agy-red-team.md](review-agy-red-team.md) | `agy` on gemini-4-hydrogen-high | red team |

The briefs and reports name the rows the pull request added by their numbers on the reviewed head: A5-542 to
A5-546 there are A5-544 to A5-548 on `main`, since `main` gained two rows before the merge. Local paths in the
reports are replaced by repository-relative paths, `"$PYTHON"` and `SCRATCH`. The reviewers' scratch scripts are
not retained; each computation a row rests on was reimplemented in the tracked scripts.

## Findings and dispositions

| Finding | Source | Disposition |
|---|---|---|
| `check()` accepted a dropped pivot test, a nonlinear colon form, a duplicated germ row, a relabeled prime and eight further mutations | both reviewers | fixed: rows compared in job order with expected identities and values; each mutation is a test |
| The embedded plane of same-sign X is not the image of the opposite-sign P^2 fiber | red team | confirmed by `embedded_plane_images.py`; A5-545 refuted, A5-546 records where the plane sits |
| Rank 18 of two source matrices cannot tell skew spans from different kernel frames | Advisor | fixed: the refutation rests on the section through V^a (ranks 12 and 3) |
| A5-544 covered X+ -> N+ at 32009 without a computation | both reviewers | fixed: the basis cites the sign isomorphism A5-013 |
| A5-027 and the structure README claimed a comparison the record lacked for E8-bar -> N- | audit | fixed: the record holds the 32009 input and the comparison |
| A5-022 rested irreducibility on a `survives` row | red team | fixed: the record runs the section test on the prime |
| A5-030 widened to both primes without a 32029 normalization | red team | fixed: 32009, claim corrected, chart 3 cited to A5-331 |
| A5-006 cited an opposite-sign row; fiber names of A5-027 and A5-028; falsifier of A5-031 | red team | fixed |
| The `updated` column did not move on dated basis entries | red team | refuted: `ledger.py` defines `updated` as the date of the last status change |
| Modular E8-bar nilradical structure | both reviewers, as a conjecture | tested in the pull request: A5-547, proved |
| A quadric ring is Cohen-Macaulay exactly when its ideal is radical | audit, as a conjecture | A5-548, open at the merge; later rows test it at a third prime and over Q(i) |
| The nilradical module is isomorphic to the irrelevant ideal of the smaller cone | red team, as a conjecture | A5-638, open |
| The two minimal primes of the modular E8-bar quadric ideal are absolutely prime | red team, as a conjecture | A5-639, open |
| `embedded_plane_images.py` looped serially over independent items | Advisor | fixed: `parallel.ordered_map` |
| The test replayed a retained record inside the pull-request suite | hosted Codex | fixed: fixtures built from the modules' tables; two on-demand gates replay the records |
| A paired change of the E8-bar numerators in one degree passed `check()`; `flag_rows()` had no behavioral test | hosted Copilot | fixed: the whole numerator is bound; a contained and a transverse two-form test the containment equations |
