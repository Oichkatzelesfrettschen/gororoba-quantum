# Review record: A_5 null-slice covariance by XOR blocks and the family proof

Pull request 1019, branch `a5-null-slice-covariance-blocks`. Reviewers, as the owner directed for this program:
- one red-team round by `agy` on `gemini-4-neon-low` at head `80d4f998c`, read-only, with its computations on the compute workstation;
- the Advisor (the `advisor` tool) last;
- Codex, the hosted review.

The proof of the commutation-set lemma comes from a delegated Opus task (pool row MATH-73, owner approval of
2026-11-26). Its check script ran again on the compute workstation (rc 0, every line passing). The parent re-derived
Step 0, the lower half of Lemma R and both compositions before the proof entered this record.

## Red team, round 1 (head `80d4f998c`)

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | A5-618's "four vector modules" and A5-626's "nullity 4 at a null point" had no bridge in the proof README | read | ledger rows and README | survives; the README states the four modules (one per u in T, by the boost action of A5-617), and A5-626 says its nullity is computed per level |
| 2 | The peel-sign control negated every sign, so it failed for a trivial reason | read | `self_test` | survives; the mutant drops a ^ t from S |
| 3 | `validate()` left the constraint counts, the space sizes and the Clifford space unchecked | read | both `validate` functions | survives; each has a require, and the proof record checks the octonion-space Clifford property at n = 6 to 12 |
| 4 | G_2 inside the covariance algebra follows from the Leibniz rule; the content is the reverse inclusion | argued by the reviewer, who opened Baez 2002 section 4.1 for Der(O) = g_2 | the argument needs D to extend to A_n; that step was not opened on the page | survives with the step checked: the derivation-type system (Y = -X) gives 14 at A_6 and A_7 |
| 5 | The block decomposition is exact; a dense A_4 system agrees with the block method | computed by the reviewer | not rerun here | noted |
| 6 | The upper-half cases of Lemmas R and U are proved by four factor ratios each | proved by the reviewer | the README's case split | survives; the README records two agreeing derivations |
| 7 | Conjecture: the octonion-space slice of A_7 has covariance G_2 | hypothesis, then computed | prediction 14 written before the run; A_7 gives 14, 14, 0 and equality with the derivations | survives; A_7 enters the record and A5-619 |

## Advisor, after the red team

| Finding | Resolution |
|---|---|
| The Leibniz inclusion needed D to extend from O to A_n, a step no opened source covered | the record solves the derivation-type system (Y = -X): 14 at A_6 and A_7; the README names the step and the check |
| The boost-algebra and associator-envelope READMEs and the roadmap still listed these results as open | each points at the new records |
| A5-626 said "superseded in scope", which collides with the ledger status | "extended by" |
| Lemma T's special cases for a = H + a' are {0, a'} | corrected |
| The hosted lanes, not the path explanation alone, decide the replicated-series test | the PR body states the path explanation as a hypothesis |

## Hosted review (Codex, head `ecfc17ec6`)

| Finding | Check | Resolution |
|---|---|---|
| P1: the U and R checks ran one whole level per task, so the 64,770 pairs of level 9 stayed serial | read `check_item` and `compute` | Fixed in `e01aebf51`: the parent maps shards of 8 indices a per task and sums them per level; the result is unchanged (sha256 e0fe71d2) |

The reviewer ran in auto mode. Afterwards `git status --short` showed no tracked change in any of the six workspace repositories.
