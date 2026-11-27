# Brief: gororoba-quantum pull request 1020, module map of the nilradical, E8-bar prime sections, the X+ cell at 32009

Read first: the workspace AGENTS.md, then AGENTS.md. Work read-only: change no file
except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents.
You may run git and read files. This host takes no Singular, Python batch or test run: run none here; where a
computation would decide a point, write the exact command and the expected output instead, and mark the point
hypothesis. Use no random draw.

Material: worktree the worktree of the branch (branch a5-nilradical-module-map-and-e8-primes, two commits on origin/main). Read the change
with `git -C the worktree of the branch diff origin/main...HEAD -- . ':!docs/evidence/a5-exceptional-fibers/working'`. Files: docs/evidence/a5-exceptional-fibers/structure/quadric_and_germ_probes.py
(MAP_SING, E8P_SING, module_map, e8_primes, expected_map, check), docs/evidence/a5-exceptional-fibers/structure/quadric-and-germ-probes.json (34
rows), docs/evidence/a5-exceptional-fibers/structure/embedded_plane_images.py and its record, docs/evidence/a5-exceptional-fibers/structure/README.md, docs/evidence/a5-exceptional-fibers/ledger.tsv (rows A5-151,
A5-544, A5-546, A5-548, A5-638, A5-639), tests/test_a5_quadric_and_germ_probes.py, ci/gates.json, and the receipt
docs/evidence/a5-exceptional-fibers/working/distribute/out/a5-xp-p1-d2/xp_p1/d2/receipt-d2.json. Notation: K2 is the ideal of the quadratic relations
of a fiber cone in S = k[y], k = F_32009 or F_32029; R its radical; N the linear forms of R; A = K2 : R; B = S / A;
m the irrelevant ideal of B.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-638: R / K2 is isomorphic to m as a graded B-module, for same-sign X (g = 3, B a polynomial ring in 3
   variables) and E8-bar -> N+- (g = 5, B a quadric hypersurface ring in 5 variables). Status: computed plus an
   argument. Support: eight module-map rows; the argument in the row and in the docstring: a k-linear theta from the
   coordinates x_j of B to span(N) with x_j theta(x_k) - x_k theta(x_j) in K2 for all pairs, and for E8-bar
   sum_j (dq/dx_j) theta(x_j) in K2, extends to a B-linear map m -> R / K2; onto since theta is invertible and
   R = K2 + N; an isomorphism since the Hilbert functions agree (A5-544, A5-547). Falsifier: a gap in the claim that
   the Koszul relations (and the Euler relation of q over B = k[x]/(q)) generate the syzygy module of (x_1..x_g)
   over B; a flaw in characteristic p (the Euler relation uses 2 q = sum x_j dq/dx_j); a way the Singular code tests
   something weaker (the lifts of x_j to S, the reduction modulo std(K2) in the product ordering, the use of coef).
2. The control: the system with x_j theta(x_k) + x_k theta(x_j) has only the zero solution on all eight files, so the
   solver is able to return zero solutions. Status: computed. Falsifier: a reason the control is vacuous.
3. A5-639: each of the two minimal primes of the radical of the E8-bar quadric ideal is absolutely prime at both
   primes and both basepoints, from a reduced zero-dimensional linear section with an F_p-point. Status: computed
   plus the argument of A5-020. Falsifier: orbits() miscounts (it takes vdim of each minAssGTZ component with the
   last variable set to 1), or minAssChar of the radical is not the list of minimal primes of K2.
4. The cell X+ -> N+ at 32009: the degree-2 receipt certifies 69 relations and h_2 = 51, and the x-colon, module-map
   and plane rows of that cell match the other cells. Status: computed. Falsifier: the receipt's input is not the
   canonical header of that cell (compare input_sha256 with the file), or A5-151, A5-544, A5-546 claim more than the
   rows show.
5. check() rejects every record that departs from claims 1 to 4 (expected_map binds each module-map row whole; the
   e8-primes rows bind identity, shape and the section condition). Status: tested on 28 mutations. Falsifier: a
   changed record that check() accepts.
6. A5-548 now says the rank-one clause holds at the two primes by A5-638. Status: deduction. Falsifier: isomorphism
   to m does not give what the row calls the rank-one nilradical clause.

## Questions to answer

- Does any status in this diff exceed what its evidence decides under the STATUSES of ledger.py?
- Conjecture where nothing is posited: structure these rows suggest; each with its falsifier and cheapest test.
- Defects: code, claims and records, with file:line.

Report ranked by consequence, every finding tied to a file:line, a theorem name or a stated command, each marked
proved, computed or hypothesis. Print it as your answer, under 120 lines.
