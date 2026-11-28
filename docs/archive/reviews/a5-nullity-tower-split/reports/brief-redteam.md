# Brief: red team of gororoba-quantum pull request 1037, the second A_5 nullity-transition change

Read first: WORKSPACE/AGENTS.md, then WORKTREE/AGENTS.md. Work read-only: change no file;
never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. This host allows reads
and git only: run no computation here (no python, no tests, no computer algebra). Reason from the files and by hand;
where a check needs a computation, write the exact command and the result that would refute the claim.

Material: the worktree WORKTREE (branch a5-nullity-tower-split, two commits on origin/main;
`git -C WORKTREE diff origin/main...HEAD`). Files changed: scripts/a5_nullity_transitions.py,
docs/evidence/a5-nullity-transitions/README.md (statements 11 to 15, "Reading", "Predictions") and result.json,
rows A5-657, A5-660 and A5-661 to A5-665 of docs/evidence/a5-exceptional-fibers/ledger.tsv,
docs/design/a5-nullity-transitions-program.md, tests/gororoba_quantum/test_a5_nullity_transitions.py, ci/gates.json.
Background: statements 1 to 10 of the same README (landed by pull request 1032),
docs/evidence/a5-zero-divisor-strata/README.md, gororoba_quantum/kernel_limits.py, gororoba_quantum/parallel.py.

Role: red team. Try to break each claim, the script logic and the wording; a claim you cannot break gets one line saying what you tried.

## Claims under review (each is a claim, not a fact)

1. structure_item (job = (dimension, base point)) computes the compression pencil, its commutant, the algebra test
   (noncommutative, trace form negative definite on the traceless part) and the Lie closure correctly for a kernel
   frame that is not orthogonal, and its three "kernel in half" fields mean what README statement 13 says.
   Status: computed. Falsifier: a flaw in the intersection dimensions (size - upper.rank(), size - lower.rank()) or
   in the equality test of the two intersections.
2. Tower (statement 12, A5-661): A_4 (kernel 4, pencil 3, closure 3), A_5 (8, 7, 10), A_6 (16, 15, 36), each with a
   quaternion commutant, read as sp(1), sp(2), sp(4). Status: computed at three levels. Falsifier: the dimensions
   3, 10, 36 with a quaternion commutant fit another family; the reading overstates what three levels show.
3. Kernel-split rule (statement 13, A5-664, status "survives"): on 8 named and 36 sampled W8 points the pencil is
   quaternionic exactly when the kernel meets each half in one 4-dimensional subspace, scalar exactly when it meets
   each half in 0. Falsifier: bias in the sample (four_term_points takes the first sign pattern of nullity 8 for
   each index triple through e_1, then every ninth); a reason the rule is trivial (follows from the definition) or
   false in general; a mechanism the README should state.
4. Statement 14 (A5-663) and the refutation of A5-657: the VB Pfaffian is -64 times an irreducible sextic with 50
   terms while Q vanishes to order 1 and G to order 2, "so it is no product of squared moduli of their leading
   forms". Falsifier: vb_pfaffian_item's subset expansion has a sign error; the conclusion does not follow (for
   example because the pencil has coordinates outside the doubly pure domain, or irreducible over Q differs from
   irreducible over Q(i) or R).
5. Statement 15 (A5-665): the census of lines along zero-compression units and pairs at s = 3 only, the 20 lines
   of generic nullity 4 with limiting planes of normals +-e_3, and two curved arcs. Falsifier: nullity at the one
   parameter s = 3 does not give the generic nullity of the 360 other lines as the README words it; sphere_normal's
   least-squares solve accepts a plane off the sphere (it checks the span, not |n| = 1).
6. Statement 11 (A5-662): order 8 with the stated cofactors. Falsifier: the loop in path_item miscounts.
7. validate has a require for every sentence of statements 11 to 15, and each of the eight self-test controls fails
   for its named reason. Falsifier: a sentence without a require; a vacuous control.
8. The README paragraph on arXiv 2611.34924-unrelated prior art: the relation to S. Koebisu, arXiv 2611.30652
   (principal cosines (p, p, q, q), cos^2(theta/2) <= p <= cos(theta/2)), and the claim P P' P = cos^2(theta/2) P
   from the Clifford relations. Falsifier: the algebra does not give it.
9. ci/gates.json sets 120 s and 20 s for the two gates; the record takes 103 s on 32 threads. Falsifier: a
   repository rule the new run time or the pooled items break (AGENTS.md, ci/AGENTS.md).

## Questions

- Defects in code, claims and records, with file:line.
- A proof or a counterexample sketch for the kernel-split rule, and the cheapest computation that would test it
  beyond the sample.
- Conjectures the evidence suggests and no record states, each with its falsifier and cheapest test.

Report ranked by consequence, every finding tied to a file:line or a derivation, each marked proved, computed or
hypothesis. Print it as your answer, under 150 lines.
