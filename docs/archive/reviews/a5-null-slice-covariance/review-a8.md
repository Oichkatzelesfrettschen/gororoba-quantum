# Review record: octonion-space covariance at A_8 and for every n

Pull request 1022, branch `a5-octonion-slice-covariance-a8`. Reviewers, as the owner directed for this program:
- two red-team rounds by `agy` on `gemini-4-neon-low`, read-only, with computations on the compute workstation;
- the Advisor last;
- Codex, the hosted review.

## Red team, round 1 (head `5729139d8`)

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | `validate()` lacked the A_7 and A_8 constraint counts | read | `validate` | survives; both have a require |
| 2 | The README listed 3b before 3a, and the titles named A_6 only | read | README and docstring | survives; reordered and retitled |
| 3 | Route to every n: G_2 inside by derivation extension; the upper bound through the invariant span V, whose tables do not depend on n | proved (extension), hypothesis (V gives 14) | the extension algebra and the Step 0 peels checked by the parent; V computed | the extension survives; the V hypothesis is refuted, since V admits 21 rotations and no boost. Two parts survive: no boost at any n, and V's n-independence. The parent replaced the hypothesis with the exact coset decomposition |

## Red team, round 2 (head `7d9a06399`)

| # | Finding | Class | Check against the source | Verdict |
|---|---|---|---|---|
| 1 | The restricted-sign lines needed a in 1..7, and the j = 0 case of the second line goes through I1, not HL | proved | Step 0 | survives; README corrected |
| 2 | Closure: the four cosets c in {0, 8, Q, Q + 8} exist at every n >= 6, keep their tables, and intersect in 14, so the covariance algebra is G_2 for every n >= 6 | proved | the record checks the anchor tables at n = 6 to 12 and their intersection | survives; A5-640 reads proved |
| 3 | A5-640's falsifier was inverted (a new coset type can only shrink an intersection) | read | ledger cell | survives; rewritten |
| 4 | The coset decomposition is exact; off-diagonal coset blocks are homogeneous and share no unknowns with the diagonal ones | proved | the equation structure | survives |
| 5 | The derivation extension and the e_tau argument hold | proved | the Leibniz expansion | survives |
| 6 | The same 7 coset types appear at n = 11 and 12 | computed by the reviewer | not rerun here | noted in the README |

After each round, `git status --short` showed no tracked change in any of the six workspace repositories.
