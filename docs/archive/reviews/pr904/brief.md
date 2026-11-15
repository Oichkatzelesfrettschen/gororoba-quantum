# Brief: gororoba-quantum pull request 904, orbit normal forms of the nullity-4 strata

Read first: the workspace AGENTS.md, then
AGENTS.md. Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud
resource; spawn no subagents. You may run git, python3 (with GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096;
sympy and python-flint are installed) and Singular; keep each computation under 10 minutes, in a scratch directory
outside every repository. Use fixed deterministic test points, no random seed.

Material: worktree the worktree of branch a5-nullity4-orbit-normal-forms, branch a5-nullity4-orbit-normal-forms; the pull request is
`git diff origin/main...origin/a5-nullity4-orbit-normal-forms` (7 files). Sources of truth:
docs/evidence/a5-kernel-bundles-residuals/nullity4_orbit_normal_forms.py (module docstring holds the arguments),
its record nullity4-orbit-normal-forms-result.json, docs/evidence/a5-exceptional-fibers/ledger.tsv rows A5-530 to
A5-540 and the rows they cite (A5-357, A5-429, A5-430, A5-435, A5-440, A5-441, A5-442, A5-479, A5-487, A5-488,
A5-491, A5-492, A5-493), docs/evidence/a5-kernel-bundles-residuals/README.md section "Orbit normal forms decide the
kernel-plane hypotheses", tests/test_a5_nullity4_orbit_normal_forms.py.

Setting: M(t) is the 15 x 15 skew matrix with M(t) k = Im(t k) for imaginary elements of the complexified sedenions,
t = (u, mu, v), Q = u.u + mu^2 + v.v, Delta = (u.u)(v.v) - (u.v)^2, G = Q^2 - 4 Delta, K(z) = ker M(z).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-530. Every point with Delta nonzero is carried by G_2(C), the 120-degree rotation of (u, v) and scaling to
   (e_1; mu; v_1 e_1 + rho e_2), rho nonzero; for t in coordinates 1,2,3,8,9,10,11, M(t) is a direct sum of a 7 x 7
   and an 8 x 8 block with Pfaffian G. Status: proved (argument plus exact identities). Falsifier: a pair (u, v) with
   nondegenerate Gram matrix outside the orbit, or a failing identity.
2. A5-531. On V(Q) minus V(G) the higher zero divisors of P(K(z)) are exactly the zero set of G restricted to K(z),
   the quartic is 4 (n (n + r^2) + q^2) at the normal form, and it contains no line. Status: proved. Check every step
   of the binary-form case analysis in the docstring item 4, including eps = 0. Falsifier: a point whose quartic
   contains a line.
3. A5-532. On V(Q) minus V(G) a plane of K(z) off z has common kernel C z; dim L = 2 at every real point; the real
   Gauss map is an injective immersion. Status: proved (argument). Check the immersion step (derivative of the
   kernel of a constant-rank linear family) and whether L lies in the tangent space.
4. A5-533. The quartic is singular at the base points of the net x cross y, roots of chi; the points with singular
   scheme longer than 3 form a proper closed subset; a quartic of length 3 without a line is irreducible. Status:
   proved, with a semicontinuity step from the modular record of A5-442. Check that step.
5. A5-534. On V(G) minus V(Q) the higher zero divisors of P(K(z)) are exactly the polar line. Status: proved
   (SL_2 orbit argument plus A5-479 and A5-492).
6. A5-535. A plane of K(z) off z other than l_z has common kernel C z; at a real point dim L > 2 needs the kernel
   plane to be l_z. Status: proved (reduction to W = M_C(h) Omega = 0 and three Groebner bases). Check the reduction
   in docstring item 7 line by line, and that the Groebner certificate proves what the row says (both signs sigma,
   the role of 1 - y rho, the excluded point).
7. A5-536. At a real rank-12 point with u, v in one quaternion subalgebra, the kernel plane is l_z and dim L >= 6.
   Status: proved (argument).
8. A5-537 to A5-540 are open hypotheses; check that each basis states only what the record holds.
9. The dispositions: A5-433, A5-443, A5-444, A5-445 are superseded; check that every clause of each has a successor
   row (proved or open) and none is dropped.

## Questions to answer

- Defects: code, claims and records, with file:line. Does the producer check what its docstring says? Does a test
  pass for a wrong reason? Is any row's primes column or status stronger than its basis?
- Any gap in a proof: name the exact step and a candidate counterexample or the missing lemma.
- Conjecture: structure the evidence suggests and no row states (for example the rank of M on l_z, the dimension of
  C(l_z), irreducibility of the quartic on the discriminant), each with its falsifier and cheapest test.

Report ranked by consequence, every finding tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
