# Brief: red team of gororoba-quantum pull request 1032, the A_5 nullity-transition record

Read first: WORKSPACE/AGENTS.md, then WORKTREE/AGENTS.md. Work read-only: change no file;
never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. This host allows reads
and git only: run no computation here (no python, no computer algebra). Reason from the files and by hand; where a
check needs a computation, write the exact command and the result that would refute the claim.

Material: the worktree WORKTREE (branch a5-nullity-transitions, one commit on origin/main; `git -C WORKTREE diff origin/main...HEAD --stat`). Files:
scripts/a5_nullity_transitions.py, docs/evidence/a5-nullity-transitions/README.md and result.json,
docs/archive/reviews/a5-outside-transition-report/README.md, docs/design/a5-nullity-transitions-program.md,
rows A5-650 to A5-658 at the end of docs/evidence/a5-exceptional-fibers/ledger.tsv,
tests/gororoba_quantum/test_a5_nullity_transitions.py. Background: docs/evidence/a5-zero-divisor-strata/README.md,
gororoba_quantum/kernel_limits.py, gororoba_quantum/cd_core.py.

Your role is red team: try to break each claim, the script's logic and the wording. A claim you cannot break gets one
line saying what you tried.

## Claims under review (each is a claim, not a fact)

1. For a path y(s) with coefficients in Q[s], the nullity of L_y(s) at a real s equals the order of x in the
   characteristic polynomial of L^T L, and the real s with nullity above the generic value are exactly the real
   roots of the lowest nonzero coefficient c_k(s). Status: argued. Support: README "Conventions"; path_item in the
   script. Falsifier: a real root of a higher coefficient that raises the nullity without being a root of c_k, or a
   flaw in how path_item reduces c_k (square-free part, rational roots, count_roots) so that an irrational or
   repeated real root escapes the `distinct_real_roots == len(roots)` requirement.
2. Three lines have nullity profiles 4 -> 8 (exceptional set {0}), 8 -> 12 ({1}), 12 -> 16 ({-1, 1}).
   Status: computed. Support: result.json "paths". Falsifier: a real parameter with another nullity.
3. At e_1 + e_10 the two limiting 4-planes of the lines with directions e_9 + e_26 and e_2 + e_17 are orthogonal and
   span the kernel. Status: computed (kernel_limits certificate). Falsifier: a defect in limits_item, for instance
   the test of "projector constant on the branch".
4. The compression pencil at e_1 + e_10 has dimension 7, commutant dimension 4, Lie closure dimension 10, and
   Pfaffian 16 ((u.u + m^2 + v.v)^2 - 4 ((u.u)(v.v) - (u.v)^2)). Status: computed. Support: pencil_item.
   Falsifier: an error in the pfaffian function, the commutant system or the Lie-closure loop (does the loop reach
   closure; is the rank test sound when the pivot selection changes the spanning set).
5. The real zeros of that Pfaffian are exactly m = 0, u.v = 0, |u| = |v|. Status: argued (README statement 6).
   Falsifier: a gap in the inequality chain.
6. Limiting planes depend only on u x v and satisfy trace(P P') = 2 (1 + cos angle). Status: computed on ten
   rational pairs; ledger status "survives". Falsifier: a flaw in the law test in pencil_item (it compares
   (trace/2 - 1)^2 |n|^2 |n'|^2 with (n.n')^2 and a sign condition), or a reason the ten pairs are degenerate.
7. The reading "sp(2) on H^2, limiting planes form a round 2-sphere in HP^1" is marked hypothesis (A5-656).
   Falsifier: an argument that dimensions 4 and 10 fit another pair of algebras, or that the reading is already
   implied or already refuted by the stated facts.
8. Every README sentence has a require in validate, and every self-test mutant fails for its named reason.
   Falsifier: a README sentence with no require; a vacuous control; a self-test that passes for another reason
   (the self-test rebinds the module global PATHS; path items run in a process pool in build_result).
9. The review record's "Statements corrected" and "no support" tables are fair to the outside report and accurate
   about arXiv 2611.34924 (not in this repository; judge only internal consistency with ledger rows A5-620, A5-628).

## Questions

- Defects in code, claims and records, with file:line.
- Is the Pfaffian form a known consequence of the invariants Q and G of A5-357 (a restriction, a tangent-cone or a
  transversal-slice statement)? Give the derivation or the obstacle; this decides how much of claim 4 is new.
- Conjectures the evidence suggests and no record states, each with its falsifier and cheapest test.

Report ranked by consequence, every finding tied to a file:line or a derivation, each marked proved, computed or
hypothesis. Print it as your answer, under 150 lines.
