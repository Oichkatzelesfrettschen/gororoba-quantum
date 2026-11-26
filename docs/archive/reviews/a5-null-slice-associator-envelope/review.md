# Review record: A_5 null-slice associator envelope

Pull request 1015, branch `a5-null-slice-associator-envelope`. Reviewers: the Advisor (the `advisor` tool) twice
before the red team and last after it, and one red-team round by `agy` on `gemini-4-neon-medium` at head
`24f690825`, under the owner's standing selection of that reviewer for this program. The reviewer also audited four
reports that mined mathematics from the owner's private chat history; those reports and their images stay in the
ignored `docs/local/` tree, and only results the record computes enter this repository.

## Advisor, before the red team

| Finding | Check | Resolution |
|---|---|---|
| M_16(R) needs the commutant type, since dimension 256, commutant dimension 4 and signature (2, 1) also fit a sum with a commutative commutant | added `commutant_closed_under_products` and `commutant_is_commutative` | the commutant is closed and not commutative; README statement 3 states the argument |
| A5-623's fibers cell named only V(Q) minus V(G) | the Euclidean cone has G = 0, Q != 0; the null space has both zero | the cell lists the three pieces |
| The hardware sentence quoted only the corrected coset-block values | read `results/live/PATHION_KERNEL_MAP_FINDINGS.md` lines 18 and 86 | the full map's unresolved reading (23 of 32 signs) and the raw values stand beside the corrected ones |
| The program note named a private commit and another session's branch | read | removed |
| A5-627 said "agree with" Skiouris while the record tests counts | read | the record now checks the criterion itself (below) |
| The real containment nullity >= 12 in V(Q) n V(G) | read `a5-zero-divisor-strata` | the modular Euclidean cone has Q != 0; README statement 2 states that the containment rests on reality |

## Red team, round 1 (head `24f690825`)

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | An eighth unit U_8 = L_(e_2) D_8, D_8 = diag((-1)^(bit 3 of i)), completes Cl(0,8) | computed | the record now builds U_8, checks anticommutation, square -I, membership in the envelope, rank 256 of the 256 monomials and J in their span | survives; A5-625 proved |
| 2 | validate() leaves volume, anticommutant, word growth, traceless rank, struts, point counts, pair counts and relation counts unchecked | read | read validate | survives; every listed value has a require |
| 3 | Self-test control 1 mutated the reference, control 5 used a weak predicate, control 6 failed on an empty common support | read and computed | read self_test; the stars of time 225 have common support 0 | survives; control 1 mutates the vectorized table, control 5 expects 8, control 6 widens the space by e_9 and keeps a common support of 4 |
| 4 | The nullity >= 12 argument holds; characteristic above 24 suffices | proved | read each step | survives; the README keeps the stated bound |
| 5 | Q(i) points of the Euclidean cone have nullity 12 | computed | the record adds three Q(i) points by the 64 x 64 real form | survives |
| 6 | Nullity 4 forces strut above 8 through the strata record's Theorem 6 (u, v independent) | proved | the record checks the criterion on all 225 pairs | survives; README statement 5 states the mechanism |
| 7 | e_1 + e_26 is named in Skiouris Proposition 3.1, not 2.2 | read | the filed transcription, lines 167 to 172 and 224 to 229 | survives; corrected |
| 8 | The spatial commutant "M_8(R) acting four times" is an inference | read | result.json stores the dimension | survives; labeled an inference |
| 9 | The connection rows for Albert and Hopf searched too narrowly; Cl(0,8) is closed; Q_p has the bound | read | read the program note | survives; rows rewritten |
| 10 | History items: the nilpotent and idempotent counts over F_p, the non-associating triple count (D-2)(D-4)(D+6)/2, the commutant 1 of the left tables for n = 3 to 7, dim Der(J_3(O)) = 52 | computed by the reviewer | not recomputed here | open; the program note lists the first and last as next computations |
| 11 | Two errors in the history reports (unit zero divisors of A_4 have dimension 11, not 10; the loop automorphism count) | computed by the reviewer | read | recorded in the local reports only |

No finding is refuted. The reviewer ran in auto mode; `git status --short` in the workspace repositories after the
round was clean.

## Validation of the fixed head

On the compute workstation under WSL with the pinned interpreter: ruff format and check and mypy clean; `--self-test`
in normal and `-O` modes passes seven controls; `--out` in 59 s; `--check` matches; `ledger.py --check` and
`check_markdown_links.py` clean; `sh ci/pr_checks.sh tests` on the record's test file and the ledger test: 16 passed.
