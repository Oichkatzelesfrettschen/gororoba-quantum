# Brief: gororoba-quantum pull request 907, residual nullity-4 strata of the orbit normal forms

Read first: the workspace AGENTS.md, then AGENTS.md of this repository. Work read-only: change no
file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git
here. NO computation runs on this machine (owner rule): every python, pytest or Singular command runs on the remote
checkout of the same head (ac3255d55), reached as
  REMOTE 'cd CHECKOUT && export PYTHON=PINNED_PYTHON PATH=SINGULAR_DIR:$PATH GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_SINGULAR_REQUIRED=1 && CMD'
(4 vCPU, 84 GB, Python 3.14.7 with sympy and python-flint, Singular 4.4.1). Keep each computation under 10 minutes;
write scratch only under SCRATCH on the remote; change nothing in the remote checkout;
use fixed deterministic test points, no random seed.

Material: this worktree, branch a5-nullity4-residual-strata; the pull request is
`git diff origin/main...origin/a5-nullity4-residual-strata` (21 files). Sources of truth, all under
docs/evidence/a5-kernel-bundles-residuals/ unless a path is given: the producers nullity4_polar_line_module.py,
nullity4_quartic_discriminant.py (+ the two nullity4_quartic_discriminant_*.sing), nullity4_real_polar_line.py,
nullity4_qg_intersection.py, nullity4_polar_line_stack.sing (module docstrings hold the arguments), their
*-result.json records, README.md, docs/evidence/a5-exceptional-fibers/ledger.tsv rows A5-441, A5-442, A5-530 to
A5-541, A5-550 to A5-554 and every row they cite, tests/test_a5_nullity4_*.py, ci/gates.json (the five
core-a5-nullity4-* gates), docs/runbooks/ci-runtime.md. The predecessor review is docs/archive/reviews/pr904/.

Setting: M(t) is the 15 x 15 skew matrix with M(t) k = Im(t k) for imaginary elements of the complexified sedenions,
t = (u, mu, v), Q = u.u + mu^2 + v.v, Delta = (u.u)(v.v) - (u.v)^2, G = Q^2 - 4 Delta, K(z) = ker M(z), l_z the polar
line, C(P) the common kernel of M on a plane P, L the fiber of the pair of real Gauss maps.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-537. Rank of M on l_z minus 0 is 8 (mu nonzero) / 6 (mu = 0) and dim C(l_z) is 3 / 6 with the stated SL_2-module
   structure, at EVERY nullity-4 point of V(G) minus V(Q). Status: proved (unit-ideal certificates over Q plus the
   normal form of A5-530). Check: that the certificates quantify over every rank-12 normal-form point and both sign
   branches, that each localization (inverted element) is justified on the stratum, that the stack certificate
   (rank-8 module, nullity4_polar_line_stack.sing) proves "C(l_z) outside O' is 0", and that normal-form coverage
   reaches every point. Falsifier: a point with another rank or dimension; a certificate that is vacuous.
2. A5-540. Singular scheme length of the kernel quartic is 3 + deg gcd(chi, chi') with A_{2e-1} points, and the quartic
   is absolutely irreducible at every point of V(Q) minus V(G), both triple-root branches included. Status: proved
   (Singular certificates over Q plus an argument, length 6 - N against 8 - N for two conics). Check the argument
   step by step, the case rho = 0, and that irreducibility is absolute. Falsifier: a point whose quartic is a product
   of two conics, or a wrong length.
3. A5-539. Orbit rank = 16 - dim of the stabilizer in compact g_2 of the real span W; 13 exactly in quaternion
   position. Status: proved (argument, exact checks at 64 fixtures). Check the stabilizer dimensions for every
   dimension of W (1, 2, 3, 4) and the claim "0 otherwise". Falsifier: a W outside quaternion position with a
   nonzero stabilizer and Delta nonzero.
4. A5-550. ker A(p, conj p) = {0} x (ker M(p) n conj(p)-perp); with mu = 0 and kernel plane l_z, dim L = 12; with mu
   nonzero dim L is 2, 4 or 6; 8 and 10 never occur. Status: proved. A5-554 (survives) holds the fixture-checked
   real-nullity identification. Check that A5-550 uses nothing that A5-554 only measures.
5. A5-551. Open: dim L = 4 at real points with mu nonzero rests on two double-precision witnesses. Check that the row
   claims no more than that, and propose the cheapest exact or interval certificate.
6. A5-541 is refuted and A5-552 proved: on real nullity-4 points of V(Q) n V(G), K lies in C(P), dim L =
   2 (dim C(P) - 2), exact Q(i) witnesses at s = 0, 2 with dim L 6, 4, 4. Check that the witnesses are real
   nullity-4 points of the stratum, that the old routine (fiber_dimension of nullity4_gauss_image.py) and the new one
   compute the same L, the normal-form family and what it misses (A5-553), and the nullity-12 clause.
7. Dispositions: A5-441, A5-442, A5-538 superseded, A5-541 refuted. Check that every clause of each has a successor
   row (proved, survives or open) and none is dropped or strengthened; that primes and status columns of every
   touched row match its basis; that rows 530, 531, 533, 534, 535 changed only in supersedes.
8. docs/runbooks/ci-runtime.md: the two new paragraphs (unreproduced remote-https fetch failure; wall-time call budget
   under contention). Check each sentence against what a measurement can support.

## Questions to answer

- Defects: code, claims and records, with file:line. Does each producer's --check verify what its docstring and row
  say? Does a test or gate pass for a wrong reason (skips without Singular, tautological comparisons of a record
  with itself, mutants that fail for an unrelated reason)?
- Any gap in a proof: the exact step and a candidate counterexample or the missing lemma.
- Conjecture: structure the evidence suggests and no row states (A5-551, A5-553, the orbit types at s = +-1 and the
  totally isotropic pairs), each with its falsifier and cheapest test, and the host it fits.

Report ranked by consequence, every finding tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 250 lines.
