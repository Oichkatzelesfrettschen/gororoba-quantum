# Red-team brief: gororoba-quantum PR 996, head bc6b65e34

Read first: the workspace AGENTS.md, then the tree under review/AGENTS.md. You are a red-teamer: try to break the claims, not to audit their wording. Work read-only: change no file, never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents; run no test suite and no computation longer than 2 minutes on this host (git, grep, short python3 one-liners on small inputs are fine; do not run Singular here).

Tree under review: the tree under review (branch a5-pfaffian-boost-stability, one commit over origin/main). See it with: git -C the tree under review show --stat HEAD.

## Claims under review (each is a claim, not a fact)

1. A5-602, status proved (exact computation). With D the linear vector field u' = v, v' = u on the split coordinates z = (u, mu, v) of C^15 and P the 3,003 ten-Pfaffians of the 15 x 15 skew matrix C(z): modulo the closure ideal I(Y) of W8, Iso, X+ or X-, D(P_k) lies in span(P) + I(Y) for every k; modulo the 37-generator E8-bar closure ideal 1,470 derivatives lie outside; D maps the generators of all five closure ideals into the ideal. Support: docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/stab-qi.log, stab-p32009.log, derivation_stability.py, expected-results.txt. Falsifier: a rerun with other RESULT lines; or a defect in the script that makes "outside 0" unable to fail.
2. A5-603, status survives (argument). For those four sources g_w = exp(tD) is an automorphism of the closure scheme carrying the Pfaffian ideal to itself, so the Rees algebra and fiber cone at g_w z0 are isomorphic to those at z0 in every degree, for every nonzero w. Support: the README section "Consequence". Falsifier: a gap in the argument (degBound 5 against the full ideal; Leibniz step; exp of a derivation on graded pieces; local rings; whether the ideal the retained fiber-cone records blow up is this ideal; whether the closure equations define the right scheme), or a retained computation at a boosted basepoint with other invariants (see docs/evidence/a5-kernel-attachments/boost-fiber-variation-result.json, A5-419, A5-428, A5-600).
3. A5-604, status certified. Stabilizer dimensions modulo 32009: Pfaffian span 15; W8 closure 59; Iso closure 40; pairs 31 = 15 + 14 + 1 + 1. The Pfaffian conditions use every 13th Pfaffian (upper bound); the lower bound is a list of fields. Support: docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/alg-p32009.log and its CONSTRAINT lines. Falsifier: the 31 named fields are dependent, or the readings 44 = 2 x 22 and 25 = 21 + 4 are wrong, or the procedure cons() drops conditions (coef against the monomial zall, interred).
4. A5-605, status stalled, and the corrected cost wording of A5-600.
5. The updates of docs/notes/topics/a5-exceptional-fiber-status.md and docs/evidence/a5-exceptional-fibers/README.md.

Context to read: rows A5-414, A5-419, A5-428, A5-593, A5-597 to A5-605 of docs/evidence/a5-exceptional-fibers/ledger.tsv; docs/evidence/a5-kernel-attachments/weight_slice_fiber_relations.py (source_equations, _boost_matrix, _derivation_matrix, _c_basis).

## What to attack

- Does derivation_stability.py compute what the README says? Phases i^popcount in CZ, the recursive Pfaffian, the direction of the vector field (M times z as a column), reduce against std with degBound, size() of an ideal as a count of nonzero entries, option(redSB).
- Is "modulo the closure" tested correctly: reduce(DB, std(P + Y)) with degBound 5 where Y has generators of degree 1 to 4 and inhomogeneous degree? Are the closure ideals homogeneous? Does degBound truncate products Y * monomials needed in degree 5?
- Is the control set able to fail, and does any path of run_stability.sh exit 0 without its verdict?
- Is the status of each row justified by its evidence? Does any sentence of the README, the rows or the status note claim more than the logs show?
- The E8-bar failure: name mechanisms that would let the fiber be constant along the boost although the ideal is not D-stable, and the cheapest computation that separates them.

## Also deliver

- Novel connections: structural statements the evidence suggests and no row states (for example what 31 = 15 + 16 says about the orbit geometry of V and VB, how the boost acts on u + v and u - v, links to the G_2 and Klein-group rows), each marked hypothesis with its falsifier and cheapest test.
- Defects with file:line.

Report ranked by consequence; every finding tied to a file:line or a command with its output and marked proved, computed or hypothesis. End with the list of claims you could not break and what you tried.
