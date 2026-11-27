# Review record: nilpotent and idempotent counts of A_n over F_p, and the Albert anchor stabilizers

Pull request: gororoba-quantum PR 1033 (branch a5-nilpotent-albert-records, head 443408924).
Owner decisions (2026-11-27): local reviewer a DeepSeek red team through opencode; both DeepSeek routes were
unavailable at the time of the review, so the owner chose the agy Neon low red team in its place.

## Acceptance before review

`--check` of both records was rerun by the session on an aarch64 host from bytes equal (sha256) to the branch head:
exit 0 for both (18.5 s and 167.7 s); a copy of the Albert `result.json` with one rank changed exits 1.

## Red team: agy gemini-4-neon-low (read-only; `git status` clean after the run)

| # | Finding | Resolution |
|---|---|---|
| 1 | Claim 1 justified: the identity x^2 = 2 Re(x) x - N(x) 1 follows from e_i^2 = -1 and anticommutation under cd_core; the scalar case closes. | Accepted. |
| 2 | Claim 2 justified: the enumeration partitions every index once; int64 products stay below 576; the seven rows match both formulas. | Accepted. |
| 3 | Claim 3 justified as a hypothesis: N is the sum of 2^n - 1 squares with determinant 1, k = 2^(n-1) - 1 is odd for n >= 2, so chi((-1)^k c) = chi(1/4) = +1. | Accepted; A5-660 stays `survives` until the point-count theorem is opened on the page. |
| 4 | Claim 4 justified: the derivation system, the Hermitian basis and the doubled Jordan product are encoded as stated; equal dimensions plus equal stacked rank give the subspace equalities. | Accepted. |
| 5 | Claim 5 justified: `--check` compares the whole serialized record; note that `validate()` checks only the EXPECTED keys. | Accepted; the exact-serialization comparison covers the other fields. |
| 6 | Claim 6 justified: ledger statuses match the records; the README labels the F_4 facts as known facts confirmed under the convention. | Accepted. |
| Q | No host, private path or private identifier in the diff. | Accepted; the session's own grep agrees. |

Conjectures the red team names, tested after the review (predictions written first; exhaustive, one run): (a) the split Cayley-Dickson algebras over F_p, p odd, have
the same counts (split imaginary norm with determinant +1; cheapest test: M_2(F_3), 81 elements, expect 9 and 12);
(b) over F_2, x^2 = (sum of the coordinates) 1, so the elements with x^2 = 0 form the even-weight hyperplane
(2^(2^n - 1) elements) and no idempotent other than 0 and 1 exists (cheapest test: A_2 and A_3 over F_2).
Results: M_2(F_3) gives 9 and 12, M_2(F_5) gives 25 and 30; A_1, A_2, A_3 over F_2 give 2, 8 and 128 elements with
x^2 = 0, the same with x^4 = 0, no other idempotent, and x^2 = (sum of the coordinates) 1 at every element. Both
predictions held at these sizes; the split case beyond n = 2 and the F_2 case beyond n = 3 stay untested.

## Advisor

- The pull-request body said pr.yml runs the four gates.json entries; the repository guide runs them on demand.
  Fixed: the body names the direct `--check` and `--self-test` runs.
- The mutant loop of the Albert script ran serially, against the parallel.py rule. Fixed: `mutant_dims` runs through
  `parallel.ordered_map`; `--check` (18.9 s) and `--self-test` (plain and `-O`) pass again; the counts script already
  used `parallel.ordered_map`.
- mypy through `ci/pinned_tool.py` was not run locally; the hosted `types` check decides.
