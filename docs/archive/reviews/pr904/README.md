# Review of PR 904 (orbit normal forms of the nullity-4 strata)

The owner chose two local reviewers for this pull request: `codex` on gpt-daybreak-blue-latest at high effort and
`agy` on gemini-3.8-flash-high. Both read [brief.md](brief.md) at head d129e83a3 and wrote
[review-codex.md](review-codex.md) and [review-agy-flash.md](review-agy-flash.md). Both confirm the arguments of
A5-530 to A5-536 and the successor of every clause of A5-433, A5-443, A5-444 and A5-445. Each finding is checked
against the source below; the Advisor reviewed last. Local paths in the three files are replaced by placeholders.

| # | Reviewer | Finding | Verdict | Evidence and action |
|---|---|---|---|---|
| 1 | codex, agy | mypy fails in the test at the product of a list with `CERTIFICATE["entries"]` | holds | The `types` lane reproduced it. The constant is typed `dict[str, Any]` and the test narrows to `int`; the lane reports no issues in 1109 files. |
| 2 | codex | The retained-record test compares key names only | holds | The test now compares the whole retained text with the record the constants determine, runs the record rules on it and checks that a changed value fails them. |
| 3 | codex | The docstring says items 1 to 7 are checked exactly, while the producer checks identities | holds | The docstring separates the checked identities and the Groebner certificate from the written arguments. |
| 4 | codex | README: "a quartic of length 3 is irreducible" drops the no-line hypothesis | holds | Restored; `z (x^3 + y^3 + z^3)` is reducible with singular scheme of length 3. |
| 5 | codex | A test comment says the quartic at `rho = v_1 = 0` holds no line | holds | The quartic there is `(s - i t)(s + i t) n`; the comment is corrected and the test asserts the factorization. |
| 6 | agy | The case `eps = 0` of the tangent line has no check | holds | `tangent_line_restrictions` gains `rho^2 + mu^2 = -eps^2`, the minor that makes the tangent the line `r = 0`. |
| 7 | agy | The symbol `W` of the certificate shadows the matrix `W` of the docstring | holds | Renamed to slack symbols. |
| 8 | agy | The rank of `M` is constant on `l_z` (marked proved) | holds, no change | It follows from the transitivity of `SL_2` on the line; the values 8 and 6 stay open in A5-537. |
| 9 | agy | The quartic is irreducible at five discriminant points and at the triple root (its own Singular run) | bounded | The run factors over `Q(rho)` and modulo 32029, which is not absolute irreducibility, and no record retains it; A5-540 stays open and does not cite it. |

## Advisor verdict

The Advisor confirmed all nine dispositions and rechecked the case analysis of A5-531 and the reduction of A5-535 to
`W = 0` against the row texts. Before the reviewers ran it had required four changes, all made: A5-532 and A5-535
state their `dim L` clauses for real points only; the immersion clause of A5-433 (b) is proved in A5-532 by the
derivative of the kernel of a constant-rank family; the quaternion position of the fixtures is computed, not
asserted; and the branch was brought onto the moved `main`.
