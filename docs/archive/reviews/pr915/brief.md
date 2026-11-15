# Brief: gororoba-quantum pull request 915, the real nullity and the open nullity-4 rows

Read first: the workspace AGENTS.md, then AGENTS.md of this repository. Work read-only: change no
file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git
here. NO computation runs on this machine (owner rule): every python, pytest or Singular command runs on the remote
checkout of the same head (efaa3a824), reached as
  REMOTE 'cd CHECKOUT && export PYTHON=PINNED_PYTHON PATH=SINGULAR_DIR:$PATH GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_SINGULAR_REQUIRED=1 && CMD'
(4 vCPU, Python 3.14.7 with sympy and python-flint 0.9.0, Singular 4.4.1). Keep each computation under 10 minutes;
write scratch only under SCRATCH on the remote; change nothing in the remote checkout; use
fixed deterministic test points, no random seed.

Material: this worktree, branch a5-nullity4-open-row-certificates; the pull request is
`git diff origin/main...origin/a5-nullity4-open-row-certificates`. Sources of truth, under
docs/evidence/a5-kernel-bundles-residuals/ unless a path is given: the producers real_nullity_bordered_matrix.py,
nullity4_real_polar_fiber_four.py, nullity4_qg_orbit_types.py (module docstrings hold the arguments), the modules
they import (nullity4_qg_intersection.py, nullity4_real_polar_line.py, kernel_frames.py,
scripts/a5_stiefel_pfaffian_germs.py, gororoba_quantum/cd_core.py), their *-result.json records, README.md,
docs/evidence/a5-exceptional-fibers/ledger.tsv rows A5-364, A5-359, A5-360, A5-550 to A5-558 and every row they cite,
tests/test_a5_real_nullity_bordered_matrix.py, tests/test_a5_nullity4_real_polar_fiber_four.py,
tests/test_a5_nullity4_qg_orbit_types.py, ci/gates.json (gates core-a5-real-nullity-bordered-matrix,
core-a5-nullity4-real-polar-fiber-four, core-a5-nullity4-qg-orbit-types). The predecessor review is
docs/archive/reviews/pr907/.

Setting: M(t) is the 15 x 15 skew matrix with M(t) k = Im(t k) for imaginary elements of the complexified sedenions,
t = (u, mu, v), Q = u.u + mu^2 + v.v, Delta = (u.u)(v.v) - (u.v)^2, G = Q^2 - 4 Delta, K(z) = ker M(z), l_z the polar
line, C(P) the common kernel of M on a plane P, L the fiber of the pair of real Gauss maps, A(z, w) the bordered
matrix whose kernel is the complex image of the real kernel of L_y for a doubly pure sedenion pair.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-554, status proved. The bordered matrix of kernel_frames._bordered_matrix equals the bordered matrix of
   scripts/a5_stiefel_pfaffian_germs.py entry by entry as polynomial matrices, the two left-multiplication matrices
   agree, and with the transport of A5-364 the real nullity of a doubly pure y is 2 (nullity M(z) - 1). Check: that
   the comparison is symbolic in every coordinate and not at sample points; that A5-364 proves the transport for the
   constructor compared; that conjugate-linearity gives real dimension = 2 x complex dimension; the 30 transport
   cases; that the row claims no more. Falsifier: a doubly pure y whose real nullity differs.
2. A5-551, status certified. A real point with mu nonzero has dim L = 4: the exact normal-form point
   (s, v_1, mu) = (4, 3, 5i) is moved by Theta = exp(i sum xi_k D_k) over the 14 octonion derivations; the kernel
   plane of Theta z_0 is the polar line exactly when z_0^* Pi l = 0 (Pi = Theta^* Theta) and dim L = 4 exactly when
   the 2 x 2 pairing N has rank 1; an arb Krawczyk box of radius 2^-24 holds exactly one zero of a 6 x 6 real system
   (z_0^* Pi l = 0, det N = 0) with contraction margin 2^-13, and an entry of N has modulus above 2^36 on the box.
   Check: the reduction from "real point with dim L = 4" to the 6 x 6 system step by step (which unknowns, why six
   equations suffice, why the zero is a REAL point of the stratum with mu nonzero, why rank N is exactly 1 and not
   0); that every interval operation is rigorous (no midpoint evaluation where an enclosure is needed, the
   exponential enclosed, the Jacobian enclosed over the whole box, the Krawczyk inclusion strict); that ranks claimed
   "exact at z_0 and constant on the orbit" are; what "certified" means in the ledger against "proved". Falsifier: a
   step that uses a floating-point value as exact; a box test that passes for a system with no zero.
3. A5-555 to A5-558, status proved, succeeding A5-553 (superseded). On the real nullity-4 points of V(Q) n V(G):
   at s = +-1 the plane P_x lies in the G_2(C)-invariant subspace E_eps = {(a; 0; eps i a)} and its Hermitian
   complement in K lies in the cone J, so no real point has kernel plane P_x and dim L = 10 does not occur; the
   point (beta, lambda) = (i, 0) has dimensions 5, 4, 4 in the chart sigma = 1 / s; exact maximal minors over
   Q(i)[s] show a plane with dim C(P) = 5 is P_x with s^2 other than 1, so dim L = 6 forces plane nullity 7; points
   with u.u = 0 are rotation images of roots of s^4 + 14 s^2 + 1; dim L takes exactly the values 2, 4, 6. Check:
   the invariance of E_eps under all 14 derivations and why invariance under the Lie algebra suffices; the step
   "complement in J implies no real point"; that the minors are maximal and their gcd argument covers every s,
   including s = 0, s = infinity and the roots of each factor; the normal form of A5-552 that the rows rely on and
   what it misses; that P_y and P_z at s = +-1 (not analyzed) cannot change "exactly 2, 4, 6"; the citation of
   A5-359 and A5-360 for totally isotropic pairs. Falsifier: a real nullity-4 point of V(Q) n V(G) with dim L
   outside {2, 4, 6}, or with dim L = 6 and plane nullity other than 7.
4. Dispositions: A5-553 superseded by A5-555 to A5-558; A5-551 and A5-554 changed status. Check that every clause of
   A5-553 has a successor, none is dropped or strengthened, and that the status and basis columns of each touched
   row match what its producer verifies.

## Questions to answer

- Defects: code, claims and records, with file:line. Does each producer's --check verify what its docstring and row
  say? Does a test or gate pass for a wrong reason (tautological comparison of a record with itself, constants
  pinned from the function under test, mutants that fail for an unrelated reason, serial CPU-bound loops that the
  repository requires through parallel.py)?
- Any gap in a proof: the exact step and a candidate counterexample or the missing lemma.
- Conjecture: structure the evidence suggests and no row states (an exact algebraic point for A5-551, the dimension
  of the sets with dim L 4 and 6, P_y and P_z at s = +-1), each with its falsifier, cheapest test and the host it
  fits.

Report ranked by consequence, every finding tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 250 lines.
