# Review of PR 915 (the real nullity and the open nullity-4 rows)

The owner chose one local reviewer for this pull request: `codex` on gpt-daybreak-blue-latest at high effort. It read
[brief.md](brief.md) at head efaa3a824 and wrote [review-codex.md](review-codex.md); every computation ran on a
remote checkout of that head. It confirms the arguments of A5-554, A5-551 and A5-555 to A5-558 and the dispositions of
A5-553, and it is the only outside audit of those arguments. Each finding is checked against the source below, and
all three hold. Local paths, host names and the remote command in both files are replaced by placeholders.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | The identity `rank_8_on_the_polar_line` of `nullity4_real_polar_fiber_four.py` evaluates M at five vectors of the polar line, which does not prove a rank on the whole line | holds | The identity is named `rank_8_at_five_polar_vectors` in the producer, the record and the test; the row's basis already takes the rank on the whole line from A5-537. |
| 2 | The test that sigma = 0 has the facts of s = 0 compares two pinned tables, and the planted derivation mutant is not skew, so its rejection does not isolate one clause | holds | The test compares the two computations (`sigma_facts` with `special_facts(0)`, and the fiber dimension at each computed witness). The reviewer's remedy, an explicit scaling map between the two chart points, is not implemented: the identification of s and 1 / s is an argument through the normal form of A5-552 and names no explicit group element, so the test claims the computed equality alone. The mutant is skew; it still fails equivariance and the map of E_eps together. |
| 3 | The 256 constructor entries, the 14 derivations and the six Jacobian columns run as serial loops over independent items | holds | The constructor rows and the derivations run through `parallel.ordered_map`, and the Jacobian test is parametrized by column. Inside a pool worker of `--check` the nested map runs in the worker's single slot, as `parallel.py` gives every worker one. |

The reviewer's three hypotheses are recorded with their falsifiers in the bases of the rows they concern: an exact
algebraic point for A5-551; neither P_y nor P_z at s = +-1 is the kernel plane of a real point (A5-555; the reviewer's
exact probe of the base frames is not retained); the real points with dim L of 4 and of 6 each have real codimension 4
(A5-558).

## Advisor verdict

The Advisor reviewed last and confirmed the three findings and their fixes from the source lines. It did not audit
the proofs again. It required, before the hosted review: the three hypotheses recorded in the ledger; this record
free of local paths and addresses; the tree validated on the remote equal to the pushed commit; a search for the
replaced digests and test names (none found under `ci/`, `docs/`, `tests/` and `scripts/`); and the test count of
the pull-request body brought to the validated run.
