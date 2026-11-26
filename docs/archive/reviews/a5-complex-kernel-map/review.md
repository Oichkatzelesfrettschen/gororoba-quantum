# Review record: A_5 complex kernel map, left-table census and family relations

Pull request 1017, branch `a5-complex-kernel-map-statevector`. Reviewers, as the owner directed:
- the Advisor (the `advisor` tool), before the work and last;
- one red-team round by `agy` on `gemini-4-neon-low` at head `2583d25f7`, read-only, with its computations on the compute workstation;
- Codex, the hosted review.

The reviewer of round 2 of the null-slice review computed the A5-630 values (16, 12, -14, -2) that this record now
reproduces independently. Its script stays outside the repository.

## Advisor, before the work

| Finding | Resolution |
|---|---|
| `pathion_kernel_map.py` is digest-pinned (transport manifest, Kaggle submissions) | left unchanged; a sibling builder imports it and reproduces its 16 laws at t = +-1 |
| Run all six operands at t = i, add t = -i, keep plain +-i as the failing control, and write the predictions first | done; the predictions stood in A5-630 and MATH-72 before the run, and all held |
| Leave MATH-69, MATH-70 and PROOF-66 to the session that claimed them; claim the workstation heavy slot before any job above 2 GB | no job above 2 GB ran; the n = 12 run uses 16 workers beside another session's jobs |
| Close A5-630 for the ideal circuit only | the device reading is A5-632, open, with pool row QPU-68 |

## Red team, round 1 (head `2583d25f7`)

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | The relations README claimed an exhaustive check at n = 12 | read | result files exist for n = 10 and 11 only | survives; the sentence names n = 10 and 11 |
| 2 | The census README counted four controls; the script runs five | read | `self_test` | survives; corrected |
| 3 | `validate()` left the selector marginals, cz counts, cone membership, Hensel preconditions and lemma metadata unchecked | read | `validate` | survives for the kernel map and the census: each has a require; Boundary for the relations script: its bytes stay fixed while the n = 12 record runs, and `--check` compares every key of the result by byte equality |
| 4 | The S-form equivalence was recorded at three points | computed by the reviewer on all 465 pairs | record | survives; every pair is checked at t = i and -i in both arms, and a failure fails the pair |
| 5 | L_0 = I is symmetric, not skew | read | README statement 2 | survives; the sentence names both cases |
| 6 | The recursion step flips the commutation sign off k in {0, a, tau', tau' ^ a}, not off {tau', tau' ^ a} | proved by the reviewer | probe at n = 5 to 8, both families, a < 40: every mismatch lies in that set, and the level-n sign at 0 and a is -1 | survives; README statement 6 corrected |
| 7 | All eight ledger rows survive; every control fails for its named reason (mutant values 1800, 0, 0, 5 and others reported) | computed | recomputation on the workstation | survives |
| 8 | Conjecture: time 2^(n-1) + 2^(n-2) + 2^r with space [1, 2^r) obeys the lemma | hypothesis | for r = n - 3 the space lies inside the first family's space, so the lemma restricts trivially there; a separate statement only for smaller r | recorded here; no row |
| 9 | The lemma also holds for the octonion-space family at n = 13 | computed by the reviewer | not recomputed here | noted; the record keeps n <= 12 |

The reviewer ran in auto mode. Afterwards `git status --short` showed no tracked change in any of the six workspace repositories.

## After the round

The n = 12 relation check finished after the round (533,209,082 relations, 0 failures, 1242 s at 16 workers). Its
result names the same checker sha256 (7ee2b676) as n = 10 and 11. It adds a row to the relations README, ledger
A5-637 and a gate, and reaches the Advisor and Codex unreviewed by the red team.

## Validation after the fixes

On the compute workstation under WSL with the pinned interpreter:
- ruff and mypy clean;
- the self-tests pass;
- the kernel-map and census `--out` runs reproduce the committed results byte for byte (sha256 8a18f07c and ec07cf64);
- `ledger.py --check` and `check_markdown_links.py` clean;
- the new tests and the ledger test pass.
