# Review record: A_5 null-slice associator envelope

Pull request 1015, branch `a5-null-slice-associator-envelope`. Reviewers: the Advisor (the `advisor` tool) twice
before the red team and last after it, and one red-team round by `agy` on `gemini-4-neon-medium` at head
`24f690825`, under the owner's standing selection of that reviewer for this program. The reviewer also audited
mathematical notes held outside this repository; only results the record computes enter it.

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
| 10 | Further computations outside the record: nilpotent and idempotent counts over F_p, the count (D-2)(D-4)(D+6)/2 of non-associating basis triples, commutant 1 for the left tables at n = 3 to 7, dim Der(J_3(O)) = 52 | computed by the reviewer | not recomputed here | open; the program note lists the first and last as next computations |
| 11 | Controls 2, 3 and 4 compute inline instead of calling associator_item and strata_item; two_term_strata, envelope, signature, block_nullity and clifford_space have no paired control | read | read self_test | Boundary: each of those functions is pinned by validate on exact values (strata counts, envelope growth, commutant data, the 225 criterion agreements, family rows); a mutation control for each is follow-up work |
| 12 | "[x, x, .] = 0 on the slice" in statement 1 rests on A5-612, not on this record | read | README statement 1 | Boundary: the statement cites the earlier record's Clifford-space check |
| 13 | "The slice misses nullity 8" is certified on the grid and at two primes only | read | program note | Boundary: the connection row names the grid and primes as its evidence |

No finding is refuted. The reviewer ran in auto mode; `git status --short` in six workspace repositories (gororoba-quantum, -infrastructure, -math, -open, -documents-public,
-documents-private) after the round was clean.

## Validation of the fixed head

On the compute workstation under WSL with the pinned interpreter: ruff format and check and mypy clean; `--self-test`
in normal and `-O` modes passes seven controls; `--out` in 56 s (sections and family levels pooled); `--check` matches; `ledger.py --check` and
`check_markdown_links.py` clean; `sh ci/pr_checks.sh tests` on the record's test file and the ledger test: 16 passed.

## Advisor, after the red team

The Advisor asked for the committed record's bytes to be checked on their own (the sha256 of the committed
`result.json` equals the compute host's output), for the citations taken from the reviewer to be opened (Theorem 6
of the strata record, the Lean file `Clifford/ZeroEight.lean` and the Mathlib pin were read; the mechanism now reads
"computed, in agreement with Theorem 6"), for stale text after the round to be updated (the PR body, the open lists,
the program note, the roadmap row and the first record's open items), for verdicts on every reviewer item (rows 11 to
13) and for the independent sections of `compute()` to run through the pool.

## Hosted review (Codex, head `68b1432b6`)

| Finding | Check | Resolution |
|---|---|---|
| P1: the five family levels ran serially; star construction and block ranks stayed off the pool | read `compute` and `family_rows` | Fixed in `9c96daf51`: three flat maps over all levels (structure, sign chunks, relation triples); `--out` 75 s to 56 s |
| P2: a one-dimensional abelian algebra maps nonzero into the defects, so "only trivially" is wrong | [K_a, K_a] = 0 | Fixed in `9c96daf51`: README and A5-628 state that a map exists for each single defect and that the paper singles none out |

## Pull request 1016: complex two-term kernels (red team round 2, head `6b2155d1a`)

The owner selected the Neon round for this pull request, with a local Codex reviewer on `daybreak-blue` only if
needed; the round below found no refutation, so no Codex reviewer ran locally.

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | A5-630 holds with orientation phases +-i s_k and fails with plain +-i (N = -14, -2); the mechanism is N(e_a + i e_b) = 16 - N(e_a + e_b) | computed by the reviewer | the record now checks the complement law on all 465 pairs of A_5 | survives; the hypothesis names +-i s_k, and the law enters A5-629 |
| 2 | The half-dimension step of the A5-629 argument needs trace i L_a L_b = 0 | proved | L_a L_b is a signed XOR permutation by a XOR b != 0 | survives; the README states the step and the record checks the trace on every pair |
| 3 | The kernel check ran on three pairs per dimension, all inside the octonions | computed | read complex_two_term | survives; the record checks every anticommuting pair (63, 171, 435) |
| 4 | validate checked anticommuting_pairs > 0; no mutation control covered complex_nullity; the program note lost a heading and named rows to A5-628 | read | read validate, self_test and the note | survives; exact counts, an eighth control (e_1 + i e_2 against e_1 + i e_1) and the note fixed |
| 5 | The proof-status table's header overstated scope; the octonion-space family has direct checks to 4096 | read | read the table | survives; header and row corrected |
| 6 | The involution identity is standard complexified Clifford (Witt-basis) algebra | documented | read | survives; the README states it; no statement of the so(n,1) relations of the defects was found by the reviewer's searches either |
