# Review of PR 929 (the open hypotheses of the nullity-4 rows)

The owner chose two local reviewers for this pull request: `codex` on gpt-daybreak-blue-latest at high effort, on
[brief.md](brief.md), and `agy` on gemini-4-hydrogen-high as a red-teamer, on the same brief with a red-team
closing paragraph. Both read head 75e830cdb and ran every computation on a remote checkout of that head. Their
reports are [review-codex.md](review-codex.md) and [review-agy-hydrogen-red-team.md](review-agy-hydrogen-red-team.md).
Local paths, host names and the remote command in the three files are replaced by placeholders, and links into the
worktree are reduced to their text. Advisor: not run, owner ruling.

Row numbers: while this pull request was open, main assigned `A5-559` and `A5-560` to other rows. The rows that
the brief, the two reports and the table below call `A5-559`, `A5-560` and `A5-561` are `A5-561`, `A5-562` and
`A5-563` in the ledger; the brief and the reports keep the numbers their authors read.

Both reviewers confirm `A5-560` and the arguments of `A5-561`. Each finding is checked against the source below.

| # | Reviewer | Finding | Verdict | Action |
|---|---|---|---|---|
| 1 | codex | `A5-559` proves a line in each fiber and a rank-4 Jacobian at six points, which does not give codimension 4 in the whole stratum | holds | The row states the fiberwise and the local result. The dimension in the stratum returns to `A5-558` as a hypothesis with its missing lemma (the kernels form a family of real dimension 20 over which the exceptional lines are line bundles). |
| 2 | agy | "In every fiber" is false: at `s = +-1` the line lies in the cone, and at `s = 2` a Hermitian element found at 50 digits puts the complement of `g P_y` inside `g P_x` | holds | The producer and the row say that the set in a fiber is empty or the punctured line. The 50-digit element is recorded as the reviewer's measurement, outside the record. The row regains "away from the roots of `D1 D2`". |
| 3 | both | `evaluation_at` set the precision and then called `ff._pairing_factors`, which sets 200 bits on its first call in a process, so the products ran at 200 bits | holds | The factors are built before the precision is set, each evaluation and each test end with a check of the context precision, and a test clears the cache and runs both precisions. The factors are exact, and the test results at 131 and 400 bits are unchanged. |
| 4 | agy | The outer map over the two precisions ran serially (`min_items` left at its default) | holds | `precision_record` passes `min_items=2`. |
| 5 | agy | `root_subgroup` tested identical vanishing alone, so the 76 other nilpotent elements were not searched for a zero of `F` | holds | `root_subgroup` returns a third fact: a lexicographic Groebner basis in `(Re t, Im t)` whose real zero set is the origin. All 76 pass, which reproduces the reviewer's computation inside the record. |
| 6 | agy | Equivariance of the boost elements was checked at one rational point | holds | `family_structure` checks `M(g t) = g M(t) g^T` as an identity modulo the two relations. |
| 7 | agy | `family_incidence_at_zero` takes `C_R = 1` and omits `C_R = -1` | bounded | `C = cosh theta` is at least 1 in the family the row names; the docstring says so. The reviewer computed that the branch `C_R = -1` gives the same `F` and `R = 0`. |
| 8 | agy | The docstring called the basis of `C(l)` `(z_0, c_2, c_3)`; no column of `polar()` is `z_0` | holds | The basis is named `k_0, k_1, k_2` with `z_0 = i k_0 + 3 k_1 + 5 k_2`, and the minor is on the rows `k_1, k_2`. |
| 9 | codex | The mutant of the `g_2` membership test fails three other clauses too | holds | `family_structure` returns one fact per clause; one test plants a generator outside `g_2` and reads the membership clause, another plants a derivation that does not commute and reads that clause with membership intact. |
| 10 | codex | `_combination_rows` computed 14 products in a serial comprehension | holds | The products run through `parallel.ordered_map`. |
| 11 | codex | The message "z_0 is outside C(l)" states the opposite of the accepted relation | refuted | `_require(condition, message)` raises the message when the condition fails; rank 3 of `[C(l), z_0]` is the accepted case and the message names the failure, as every other `_require` of the module does. |

The reviewers' hypotheses are recorded with their falsifiers in the rows they concern: the dimension of the two
sets in the stratum (`A5-558`), and an exact point of `A5-551` in a rational chart, for which the red-team
reviewer gives a rational family of Hermitian elements of the subgroup `SL(3, C)` that fixes `e_4` and a real
zero at 50 digits of a system of three polynomials of degrees 8, 8 and 16 (`A5-551`). The first is not computed in
this pull request.

Two additions follow the local review, so neither local reviewer read them and the hosted round is their first
review. `A5-564` (`nullity4_real_polar_sl3_chart.py`) computes the red-team reviewer's lead: the chart is checked
as an identity, a Krawczyk box holds one real zero of the three polynomials with pairing rank 1, and the point
lies on a factor of degree 88 of the eliminating polynomial that msolve 0.9.4 returns (the degree is computed, the
eliminant is retained and not recomputed). The evidence README gains one table of the nullity-4 strata by kernel
plane, `dim C(P)`, `dim L` and row. Both passed the sweep for the five finding classes of the earlier reviews
before the push: the factor loop runs through `parallel.ordered_map`, each test computes what it compares, each
fact name states what its code evaluates, the Krawczyk test refuses a precision below 64 bits, a radius that selects
the point evaluation and an unknown box, and the gate runs the producer directly.
