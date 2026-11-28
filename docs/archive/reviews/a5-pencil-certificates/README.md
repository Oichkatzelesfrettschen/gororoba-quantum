# Review of the pencil-certificate change (pull request 1045)

The change adds [`scripts/a5_pencil_certificates.py`](../../../../scripts/a5_pencil_certificates.py) and its record
`certificates.json`, README statements 16 to 18 of [the transition record](../../../evidence/a5-nullity-transitions/README.md),
and ledger rows A5-657 (now proved), A5-667, A5-670 and A5-671. The owner chose one reviewer and two red-teamers; the
Advisor reviews last. Head under review: `e9e3c33f0`. Local paths in the retained files read `WORKTREE`,
`WORKSPACE` and `SCRATCH`, and the compute host is named by its role.

| Role | Agent | Run |
|---|---|---|
| reviewer | `codex` on gpt-daybreak-blue, high effort, read-only sandbox | [report](reports/report-codex-daybreak-blue.md), [brief](reports/brief-review.md) |
| red team | `agy` on gemini-4-neon-medium | [report](reports/report-agy-neon.md), [brief](reports/brief-redteam.md) |
| red team | `opencode` on opencode/deepseek-v4.1-flash-free | [report](reports/report-opencode-deepseek-v4.1-flash-free.md), same brief |

The OpenCode Go weekly window read 79 percent at the launch, the ceiling of `workspace/opencode-redteam.sh` in
gororoba-infrastructure, so every paid Go model was refused. The free model ran first and answered, and the owner
chose that route after an audit of the plan's usage.

## Findings and verdicts

| Finding | Source | Verdict |
|---|---|---|
| The tower bounds use the correct directions: mod-p commutant nullity above, verified rational elements below, mod-p bracket span below, Gram-skew container above | all three | confirmed; no change |
| The 60 determinant evaluations drew coordinates modulo 11, so they were 11 distinct points | Codex, opencode | confirmed; the points are drawn modulo 1009, `validate` requires 60 distinct points and no vanishing target, and the README records the deviation of P26 |
| A5-671 needs the bound dim Ann(x) <= 4 in A_4 (Proposition 9.10), and Biss, Dugger and Isaksen already prove the whole statement (Lemmas 9.5, 9.6, 9.9) | Codex, Neon, opencode | confirmed on the paper's pages 15 to 17; README statement 18 and A5-671 call the statement known and cite every lemma |
| The polynomial identity covered the 18 basis units only; the forms of all 30 doubly pure units span the basis space and lead Q, lead G are constant along the kernel on R^30 | Neon (scope and computed check) | confirmed and adopted: `strata_item` checks the rank and the constancy by expansion, and A5-657 states the identity on all 30 units |
| At type C the closure can be bounded by 15 through tr(J X) = 0 for the commutant element J, since tr(J m) = 0 on the pencil and tr(J [A, B]) = tr([J, A] B) | Neon | confirmed and adopted: the certificate now reads closure 15, su(4), with the container value 16 kept for the self-test |
| `table_mismatches` sampled the left factor at a stride above A_4 | Codex, Neon, opencode | confirmed; every basis product is checked against a recursive basis product from the doubling formula, and the vector formula keeps its stride sample |
| `validate` lacked requires: calibration skewness, type-R lower bound, type-C trace form, VB factor degrees, determinant labels, counts and zero targets | Codex, Neon, opencode | confirmed; each added |
| The certificate does not bind the source of Q and G | Codex | confirmed; `scripts/a5_zero_divisor_strata.py` joins the digests |
| N- and N+ are exchanged by the automorphism e_k -> (-1)^(bit 3 of k) e_k | Codex (proved) | confirmed and recorded (`automorphism`): the character is multiplicative, it maps N- to N+, and the Pfaffians correspond under x_w -> chi(w) x_w |
| The type-C self-test control asserted only that the lower bound differs from 16 | opencode | confirmed; the control requires 15 at both bounds and 16 from the container alone |
| The e_16 mutant is weak because Q and G cannot see e_16 | opencode | boundary: e_16 lies outside the doubly pure domain of Q and G by definition (the strata record), so the mutant tests exactly the scope the statement names, the off-domain coordinate that P14 found to break the identity |
| The census rebuilds all 26,096 matrices in each of 64 workers and enumerates serially | Codex | boundary: the census takes a small share of the 359 s record, dominated by the A_8 item; a shared-memory layout is left for a change that needs it |
| `strata_item` returns a partial row on its mutant path, and the schema is untyped | Codex | partly fixed: the partial row is reachable only with the mutant flag, which `require` now enforces; a TypedDict schema is left open |
| The PR body said hosted checks were not run and called the type-C check a mutant | Codex | confirmed; the body is updated |
| A5-667 words a universal rule ("for a real point y = (p, q) of W8") from finite samples | Codex | boundary: the row's status is `survives`, which the ledger uses for a tested hypothesis that no check has refuted, and its falsifier names the counterexample; README statement 13 scopes the evidence to the points of the record. The rule stays open (MATH-225) |
| Both Pfaffian routes share the frame-normalization formula and FLINT's kernel frame | Codex | boundary: the formula is the transformation law Pf(T^T A T) = det(T) Pf(A) for K = K_2 T with K_2^T K_2 = 2 I (derived in the Neon report), so c_2^2 = c^2 2^k / det(K^T K) holds for any frame; a wrong frame would change both routes by the same factor, so the routes check the multiplication and the polynomial evaluation independently and the frame jointly |
| Three-type rule: in the normal form a = (t, kt), b = (alpha t, (alpha k) t) of the proof of Theorem 14.6 of Biss, Dugger and Isaksen (pages 23 to 25, read for this record), an operator J_k (+L_k on H x H, -L_k on its complement) commutes with all 31 compressions at dim A = 2 and 4 | Neon (computed at six points) | reviewer-reported, not reproduced; recorded as a lead in the program note (T2) with its falsifier |
| Elements of A generate the commutant | opencode (tested) | reviewer-reported refutation, not reproduced: their compressions vanish on the kernel; recorded in the program note |
| Conjectures without a check here: a symbolic proof of the J_k statement over alpha, the converse for dim A = 0, the full N+- Pfaffian with e_16, a 30-unit determinant identity as a polynomial | Neon, opencode | recorded, untested; the last is now proved by the 30-unit reduction of `strata_item` |

Neon and opencode both ran computations on the compute workstation in a scratch directory, and codex ran none,
because the workstation checkout sat one commit behind the head. No reviewer changed a checkout. The codex browser
left two snapshot files in the workspace root, and they were moved to the trash.

## Advisor

The Advisor reviewed last, on the findings above and the fix commit `73868afb6`. It confirmed every bound direction,
the trace condition and the 30-unit reduction, and named these gaps, each resolved in the commit after it:

| Finding | Resolution |
|---|---|
| The table lacked rows for two Codex findings (the universal wording of A5-667, the shared normalization) and for the reviewers' conjectures | rows added above |
| The self-test time (3 s) and the gate estimate (6 s) predate the new checks | measured 11 s a run; README and gate updated |
| Theorem 14.6 was cited from a report, and the J_k and Clifford results are reviewer computations | the theorem's pages were opened; both results are labeled reviewer-reported, not reproduced |
| The record's digests at the pushed head were unconfirmed | the four `sources` digests of `certificates.json` equal `git show 73868afb6:PATH \| sha256sum` |
| The workstation checkout was one commit behind the head the briefs named, so Codex ran no computation | recorded here; a later round syncs that checkout before launch |
