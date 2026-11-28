# Brief: red team of gororoba-quantum PR 1053 (a5-pencil-types-and-loci)

Read first: WORKSPACE/AGENTS.md, then the sections "Comments, commits and pull-request detail" and "Reviews and merges detail" of WORKSPACE/gororoba-infrastructure/workspace/reference.md, then ~/worktrees/gororoba-quantum/a5-pencil-types-loci/AGENTS.md and ~/worktrees/gororoba-quantum/a5-pencil-types-loci/scripts/AGENTS.md. Work read-only: change no file (print your report as your answer); never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. Computation does not run on this machine (the build host): run Python over the compute workstation in the checkout WORKTREE there, which is at commit f917aa07b with a clean tree (`git log -1` there confirms it), with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON"` and Singular 4.4.1 on the path, writing only under SCRATCH, each computation under 15 minutes. No random draw is needed.

Material: gororoba-quantum pull request 1053, branch a5-pencil-types-loci, head f917aa07b, worktree ~/worktrees/gororoba-quantum/a5-pencil-types-loci. Read the change with `git -C ~/worktrees/gororoba-quantum/a5-pencil-types-loci diff origin/main...HEAD`. Files: scripts/a5_pencil_types_and_loci.py, docs/evidence/a5-nullity-transitions/types-and-loci.json, docs/evidence/a5-nullity-transitions/README.md (statements 19 to 23, Predictions, Replay), docs/evidence/a5-nullity-transitions/fourth-round-predictions.md, docs/evidence/a5-exceptional-fibers/ledger.tsv (rows A5-660, A5-667, A5-676 to A5-680), tests/gororoba_quantum/test_a5_pencil_types_and_loci.py, ci/gates.json, docs/design/a5-nullity-transitions-program.md. Prior art: math_0511691.pdf (Biss, Dugger, Isaksen; Theorem 14.6 and its proof on pages 23 to 25).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. With the e_16 coordinate kept, the pencil Pfaffian is irreducible over Q at VB (degree 6, 50 terms) and at N- and N+ (degree 8, 12,579 terms). Status: computed (fmpz_mpoly factor). Falsifier: a factorization.
2. Every W8 point y = (p, q) built from a census pair has the type its dim (ker L_p n ker L_q) names (177 R, 3,282 C, 139 H). Status: computed. Support: type_census, type_item. Falsifier: a census W8 point of the wrong type; a sampling rule that hides a family; a fallback route that disagrees with the bounds route.
3. In the BDI normal form the kernel splits into an alpha-independent Omega x Omega part and a part that moves exactly when alpha leaves <1, k>, and J_k commutes with all 31 compressions at seven alpha. Status: computed. Falsifier: an alpha in Case 1 where J_k fails; a wrong reading of the normal form (t, k, slot order, alpha t versus t alpha).
4. At VB the real directions of compression rank at most 4 are the plane m = x3 = x4 = x11 = x12 = 0 with rank exactly 4 off the origin; on 284 unit sums of rank 4 in the plane the second-order Schur form vanishes exactly on the 100 nullity-8 lines. Status: proved (power membership in Singular plus sum-of-squares sub-Pfaffians) and computed (line census). Falsifier: a real rank-4 direction off the plane; a wrong pseudo-inverse or kernel convention in the second-order form.
5. At e_1 + e_10 the second-order, mixed and cubic Schur terms lie in the pencil span, so every nullity-4 arc of effective order at most 3 limits on the 2-sphere (A5-680; A5-660 now survives). Status: computed (terms) plus the derivation of README statement 23. Falsifier: a term outside the span; an error in the order-3 arc equations (the c1 and c2 corrections) that makes another term enter.
6. Ledger rows and README sentences state exactly what the record computes. Falsifier: a sentence without a require in validate, or a scope word the loop bounds do not support.

## Your role

You are a red-teamer: try to break each claim. Run the cheapest decisive check you can over the compute workstation. Look especially for: a derivation gap in statement 23 (the order-3 equations); points of W8 outside the census families where the type rule fails; an alpha where J_k stops commuting; whether the second-order criterion at VB fails off the unit-sum family; and a proof route for the dim A = 0 half of the type rule.

## Questions to answer

- Which claims fall, and by what evidence.
- Conjectures with falsifiers and cheapest tests.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
