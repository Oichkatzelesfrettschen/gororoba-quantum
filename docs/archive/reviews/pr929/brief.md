# Brief: gororoba-quantum pull request 929, the open hypotheses of the nullity-4 rows (review)

Read first: the workspace AGENTS.md, then AGENTS.md of this repository. Work read-only:
change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may
run git here. NO computation runs on this machine (owner rule): every python or pytest command runs on the remote
checkout of the same head (75e830cdb), reached as
  REMOTE 'cd CHECKOUT && export PYTHON=PINNED_PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 && CMD'
(4 vCPU, Python 3.14.7, sympy 1.14.0, python-flint 0.9.0; no Singular). Keep each computation under 10 minutes; write
scratch only under SCRATCH on the remote; change nothing in the remote checkout; start, stop or
reboot nothing there; use fixed deterministic test points, no random seed.

Material: this worktree, branch a5-nullity4-open-hypotheses; the pull request is
`git diff origin/main...origin/a5-nullity4-open-hypotheses`. Sources of truth, under
docs/evidence/a5-kernel-bundles-residuals/ unless a path is given: the producers nullity4_qg_plane_incidence.py and
nullity4_real_polar_rational_charts.py (module docstrings hold the arguments), the modules they import
(nullity4_qg_intersection.py, nullity4_qg_orbit_types.py, nullity4_real_polar_fiber_four.py,
nullity4_real_polar_line.py, nullity4_orbit_normal_forms.py), their *-result.json records, README.md,
docs/evidence/a5-exceptional-fibers/ledger.tsv rows A5-551, A5-552, A5-555, A5-557, A5-558 (edited) and A5-559,
A5-560, A5-561 (new) with every row they cite, tests/test_a5_nullity4_qg_plane_incidence.py,
tests/test_a5_nullity4_real_polar_rational_charts.py, ci/gates.json (gates core-a5-nullity4-qg-plane-incidence,
core-a5-nullity4-real-polar-rational-charts), ci/pr_checks.sh. The predecessor review is docs/archive/reviews/pr915/.

Setting: M(t) is the 15 x 15 skew matrix of the frame vector t = (u, mu, v), Q = u.u + mu^2 + v.v,
Delta = (u.u)(v.v) - (u.v)^2, G = Q^2 - 4 Delta, K(z) = ker M(z), J the cone of vectors of K of nullity above 3,
P_x, P_y, P_z its planes, P = K n conj(z)-perp the kernel plane of the real point z, C(P) the common kernel of M on
P, dim L = 2 (dim C(P) - 2) on V(Q) n V(G); on V(G) minus V(Q), l is the polar plane, C(l) its common kernel and N
the pairing of C(l) / C z with l.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-559, status proved. The nullity-4 points of V(Q) n V(G) are the disjoint union over kernels K of K minus J;
   in each fiber the real points with kernel plane P_j are the complex line Hermitian-orthogonal to P_j minus J; so
   the real points with dim L = 6 and with dim L = 4 have real codimension 4 "fiber by fiber". Support: the
   docstring argument (items 1, 2) and incidence_facts at six witnesses (rank 4 of a real 4 x 36 Jacobian, tangent
   span 13). Check: every step of the fibration argument (z in K(z); kernel of a vector of K outside J; that P_j
   depends on K alone; surjectivity onto C^2); whether "real codimension 4 in the stratum" follows from a fiberwise
   statement, and what the row may and may not claim; whether the Jacobian of item 2 is the differential of the
   stated map (the s-derivative of the frame, the conjugate-linear slot, the directions i D_k z); whether the frame
   independence claim holds; whether the tangent span is the tangent space. Falsifier: a rank other than 4, or a
   real point with kernel plane P_j not Hermitian-orthogonal to P_j.
2. A5-560, status proved. At s = +-1 no real point has kernel plane P_y or P_z, so with A5-555 the type holds
   dim L = 2 alone. Support: docstring items 3, 4; complement_fact at the base frame and at g = exp(D_0 + i D_9).
   Check: that q lies in P_y and P_z (where is it computed and retained); the orthogonal-sum step for every g of
   G_2(C), not only the tested one; that the cone J at s = +-1 contains all of P_x; that every real point of the
   type has a kernel of the form g K(z(+-1)) (which group, and does it include the scaling and the rotation);
   whether the unipotent element is in G_2(C) and what the single tested g adds. Falsifier: a g of G_2(C) whose
   complement of g P_y or g P_z in g K has rank 12.
3. A5-561, status proved as a bounded negative. At the normal form (4, 3, 5i): the stabilizers of z_0, l and C(l)
   are one 3-dimensional subalgebra with zero first-order pairings; 24 of 100 nilpotent D_a +- i D_b keep F = 0 and
   those keep R = 0; on two four-parameter Hermitian families the minor of R is 400 S_R^2 (S_R^2 + 1) (2 S_L^2 +
   1)^2 and F = 0 at S_R = 0 forces the identity, so rank R is 0 or 2 on F = 0. Check: that A_L and A_R are the
   stated exponentials and lie in G_2(C) (what the code verifies symbolically, what only at one rational point);
   that rank R equals rank N when F = 0; the reduction modulo the two relations (_reduced) and whether factored
   strings can hide a sign or a zero; that "rank 0 or 2" follows (rows c_2, c_3 independent implies rank 2, and
   what happens to the row of z_0); that the row claims no more than these charts. Falsifier: a point of a family
   with F = 0 and rank R = 1.
4. A5-551, status certified, basis extended: the Krawczyk test holds at 131 and 400 bits with the precision passed
   to every evaluation. Check: that krawczyk_at repeats ff.krawczyk exactly apart from the precision (compare the
   two functions line by line), that no evaluation runs at another precision (workers start by spawn), and that the
   edited basis text of A5-551, A5-555 and A5-558 drops or strengthens nothing.

## Questions to answer

- Defects: code, claims and records, with file:line. Does each producer's --check verify what its docstring and row
  say? Look in particular for these classes, each raised in earlier reviews: a serial CPU-bound loop over
  independent items that the repository requires through parallel.py; a test that compares two pinned constants; a
  check whose name claims more than it evaluates; a function that accepts an input for which its certificate is
  void; a gate that passes on a failed process; a mutant test that fails for an unrelated reason.
- Any gap in a proof: the exact step and a candidate counterexample or the missing lemma.
- Conjecture: structure the evidence suggests and no row states (in particular a rational family of Hermitian
  elements of G_2(C) on which rank N = 1 is a proper closed condition, for an exact point of A5-551), each with its
  falsifier, cheapest test and cost.

Report ranked by consequence, every finding tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 250 lines.
