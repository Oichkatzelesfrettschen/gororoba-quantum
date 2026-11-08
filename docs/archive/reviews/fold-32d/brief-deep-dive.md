# Brief: adversarial deep dive on the Cayley-Dickson folding program

Read first: the workspace AGENTS.md (workspace guide), then
AGENTS.md. Work read-only: change no file except your
report (named at the end); never commit, push, stash, submit to a provider or start a cloud resource; spawn no
subagents. You may run git, Python (PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python",
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096, modules importable with PYTHONPATH=gororoba_quantum), Singular
(the passagemath build under ${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/venv-passagemath-singular) and rocq
(`rocq`); keep each computation under 15 minutes and in a scratch directory outside both
repositories. Any random sample you draw takes its seed from
docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json values at indices 2 onward (indices 0 and 1 are taken); name the
indices you use.

Repositories: gororoba-quantum (branch
docs/a5-32d-findings) and gororoba-open (sibling checkout).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Half fold (proved): (a, 0)(c, d) = (ac, da), and the kernel of L_(a,0) is ker L_a x ker L_a for every a; nullity
   doubles. Rocq: gororoba-quantum `proofs/CdHalfFold.v` (all operands, kernel identity) and gororoba-open
   `proofs/theories/CDPureDoublingKernel.v` (`pure_doubling_kernel_decomposition`, `pure_doubling_rank` for pure
   operands, rank in mathcomp). Check overlap, which statement is stronger, and whether the rank doubling for every
   operand follows from what is proved.
2. Mixed fold (computed through D = 512, docs/notes/singular_sector_dynamics.md, scripts/singular_sector_dynamics.py):
   n_2h(e_i +- e_(h+j)) = h - 4 - 2 n_h(e_i +- e_j), 0 when j = 0 or j = i; maximum D/2 - 4 (Biss-Dugger-Isaksen II
   Prop 8.2); recurrence and palindromic spectrum. Is there a proof route from claim 1's machinery? State the Rocq
   target precisely.
3. Twisted product (computed 2026-11-08, not yet committed): with z_k = x_k + i x_(16+k), z'_k = x_k - i x_(16+k)
   over a field holding i, the 32-coordinate W8 closure ideal (x_0, x_16 and real and imaginary parts of mu, U - V, W;
   docs/evidence/a5-zero-divisor-strata/README.md "Pieces" and line 276, W8 = N x N) equals J(z) + J(z'), where
   J = (y_0, y_8, U - V, W) is the sedenion zero-divisor ideal; at p = 32009 and p = 32003 the ideal has dimension 24,
   degree 16 and Hilbert numerator N_J(t)^2 = 1,-4,2,12,-17,-8,28,-8,-17,12,2,-4,1. Check it against the record's own
   W8 generators (`a5-zero-divisor-strata` scripts `piece_ideals`), not a hand construction. Say whether it is new or
   is already stated by the record, and what it does and does not imply for the fiber ideals F(W8) and the ladder
   numbers h_d (docs/evidence/a5-exceptional-fibers/).
4. Nullity sum rule (refuted): n_32(x) = n_16(z) + n_16(z') held at 10 seeded random points (6 on W8, 2 on the real
   diagonal, 2 off W8) and failed on 480 of 512 mixed basis pairs e_i +- e_(16+j); the observed cells
   (n_32, n_16(z), n_16(z')) are (0,0,0) x32, (0,8,8) x60, (4,4,4) x168, (12,8,8) x252. Reproduce, then find the
   law that maps the complex nullity n_16(z) and the real nullity n_16(e_i +- e_j) to n_32. Conjecture the general
   (non-basis) relation, with a falsifier, and test it on seeded random points off the basis.
5. W8 restriction (A5-222, docs/evidence/a5-w8-a4-restriction/): the restriction of W8 to x_16..x_31 = 0 is J, the
   radical of the A_4 Pfaffian ideal PB, with U - V and W outside PB. Does claim 3 explain it (the real slice is the
   diagonal z = z')?
6. The synthesis (docs/notes/topics/a5-hardware-algebra-synthesis.md, sections "Findings across the open
   acquisitions" and "Remaining computations by host"): audit every folding statement against claims 1-5.

## Questions to answer

- Nullity atlas: can folding locate the nullity strata of A_5 (and A_6, A_7) from A_4 data, and which strata does it
  miss (E8-bar, Iso, X)? Give the stratum-by-stratum answer with evidence.
- Compute cost: which of the open computations (Iso and W8 degree 6, E8-bar degree 6, the A5-218 components,
  characteristic 0) can a folding or product identity shrink, by how much, and why; which it cannot touch.
- Hardware: which folding statements are hardware-testable on the access we have (IBM Heron r2 156 qubits, Tuna-17,
  Quandela Belenos/Ascella), with the observable, the ideal value and the mutation test that would break it.
- Rocq: list the theorems to prove next, in order of value, each with its exact statement, the existing lemmas it
  reuses (file:line in either repository) and the evidence it rests on.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name; mark
each statement proved, computed (with the command) or hypothesis. Write it to
docs/local/reviews/fold-deep-dive-codex.md, under
400 lines.
