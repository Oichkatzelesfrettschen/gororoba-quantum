# Brief: gororoba-quantum pull request 817, kernel-plane limits at the special VB point and the fiber-to-Grassmannian map

Read first: WORKSPACE/AGENTS.md, then AGENTS.md. Work read-only: change no file
except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents.
You may run git and python3 (python-flint and sympy are available in the repository interpreter that docs/PYTHON.md
names); keep each computation under 5 minutes and write scratch files under /tmp only. Draw no random numbers.

Material: the worktree the worktree of branch a5-kernel-limits-fiber-image on branch a5-kernel-limits-fiber-image; the change is `git diff origin/main...HEAD` (two
commits). Evidence root: docs/evidence/a5-exceptional-fibers (E); the files under review are in E/kernel-limits.

Background. For an incidence S -> T of nullity strata of left multiplication L_a on the 32-dimensional
Cayley-Dickson algebra A_5, a slice V(J) through a base point b of T with ideal I = (G_1..G_s) has exceptional fiber
E0 = Proj F(I), F(I) = k[y]/L, with K2 the degree-2 part of L. Along an arc of V(J) through b, the fiber point y is
the normalized leading coefficient vector of G, and ker L_a (dimension 8 on S) has a limit, an 8-plane inside
ker L_b. plucker_limits.py (already on main) computes y and the plane per arc. All statements are over F_32009 and
F_32029.

## Claims under review (each is a claim; justify or falsify it against the source)

1. vb_special_arcs.py and vb-special-arcs-result.json (ledger A5-295): along arcs of the closure of E8-bar through
   the VB point with k0 = -9 (e0 = (1 + 9i)/(1 - 9i) in the header of E8-bar -> N-, w of order 2), the limit is
   8-dimensional inside the 12-dimensional base kernel; Plucker spans have rank 22 (finite e), 18 (special patterns
   alone) and 34 (total); the mirror point of e0 and the neighbor e0(8) add nothing. Status: computed.
   Falsifier: the relation between the two parametrizations (k/(1 + k^2) = i omega, e = (1 + ik)/(1 - ik)) being
   wrong, so that the arcs pass through another point; or the controls not discriminating.
2. fiber_plucker_map.py and fiber-plucker-map-*.json (ledger A5-296): on 320 sampled arcs per case the Plucker
   vector Pl of the limit plane satisfies c_s Pl_s = v_2(y_s) T with one matrix T; the solution space for the
   scalars c has dimension 1 at degree 2 and 0 at degree 1; T has rank equal to the rank of v_2 on the sample;
   40 held-out arcs per case are proportional to the fit. Cases: opposite-sign X, same-sign X, Iso, W8 (degree-30
   component, degree-20 component, both). Status: computed. Falsifiers: the linear system N diag(Pl[:, j]) c = 0
   not being equivalent to the fit; the held-out arcs not being independent of the fitted ones (same parameter
   values, same y); the SHA-256 parameter values lying on a subvariety that makes the fit trivially exact; the
   normalization of y or Pl hiding a sign or scalar.
3. The README sentence "the kernel plane is the image of the fiber point under the second Veronese map followed by
   a linear injection into Plucker space" says no more than the record supports, including the stated limit on
   same-sign X (12 of 15 coordinates, 45 of 51 quadrics). Status: hypothesis.
4. Ledger rows A5-295 and A5-296 state no more than the records.

## Questions to answer

- Is the fit in claim 2 a real test? Construct the cheapest mutation under which it must fail (for example Plucker
  vectors permuted against fiber points) and say whether the code would report the failure.
- Defects in code, claims and records, with file:line.
- Conjectures the evidence suggests and no record states, each with its falsifier and cheapest test.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
