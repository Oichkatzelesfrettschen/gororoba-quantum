# Brief: adversarial review of "C30 lies in the W8 exceptional fiber, so F(I) = k[y]/K2 in every degree"

Read first: the workspace AGENTS.md, then AGENTS.md at the root of this worktree
(~/worktrees/gororoba-quantum/docs/a5-32d-findings, branch docs/a5-32d-findings), then
docs/runbooks/computer-algebra.md. Work read-only: change no file except your report (named at the end); never commit,
push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git, Singular
(`/usr/bin/Singular`, or the passagemath build that `structure/c30-bounded/run.sh` resolves), and
`"${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python"` with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. Keep each computation under 15 minutes and 8 GiB
(`systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 timeout 900 ...`), in a scratch directory under /tmp
outside every repository. A new random point takes its coordinates from
docs/evidence/anu_qrng/draw-2026-11-08T182935Z.json values at indices 70 to 99 (indices 0 to 69 are used); name the
indices you use.

Material: commit 6144d16fd on branch docs/a5-32d-findings. Paths below are under
docs/evidence/a5-exceptional-fibers/ unless they start with docs/.

- structure/c30-bounded/README.md: the reduction (steps 1 to 7), the computation table, the controls, falsifiers.
- structure/c30-bounded/c30_gen.py, templates/, sing/, logs/, points.json, run.sh: the scripts and their outputs.
- structure/arcs-iso-w8/README.md: the C20 arc certificate and the statement that the degree-2 parts of G cut the
  tangent cone in L0 doubled.
- structure/w8-kp/README.md, check.sing, quotient.txt: K2 = P cap (K2 : P), V(P) = C20 (degree 20),
  V(K2 : P) = C30 (degree 30), K2 radical and Cohen-Macaulay.
- ledger.tsv rows A5-066, A5-138 to A5-149, A5-218, A5-236, A5-237; claims.json (W8 -> N-).
- docs/archive/reviews/fold-32d/review-codex-final-report.md ("Next computations", item 1): the earlier test design.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Step 2 of the reduction: the fiber of Bl_{I'} B over a point p of the exceptional divisor {s = 0} maps into
   E0 = Proj F(I) over the origin, because I O_B = s^2 I', Bl_{I'} B = Bl_{I O_B} B, and the composite factors through
   Bl_I V(J) preserving the projective coordinate [G] = [G']. Status: argued (README lines 34 to 37). Falsifier: a
   point of the fiber over p whose image is not a limit of [G] along a curve in V(J) minus V(I) tending to the origin,
   or a failure of the universal-property factorization (for example, I O_B not invertible on Bl_{I'} B).
2. Step 4: on the transversal slice B_4 at p in P(L0), I'|_{B_4} = (G'_2, G'_11, v2 s, v2^2), a monomial ideal in
   the coordinates (G'_2, G'_11, s, v2) with fiber cone k[Z1..Z4], and Proj F(I'|_{B_4}) embeds in the fiber over p
   because F(I'_{B,p}) maps onto F(I'|_{B_4}). Status: computed (Newton iteration to order 10, vdim 1 in `ds`) plus an
   argued surjection. Falsifier: a truncation order too low for the Nakayama step, a surjection that fails (the fiber
   cone of a restriction is a quotient of the restriction of the fiber cone only under conditions; check which
   direction holds), or a generator set whose exponents are affinely dependent.
3. Step 6: the planes Pi_p sweep a set T of projective dimension at least 5, from Jacobian rank 6 of
   [M(p) | dM/db Y0 | dM/dc Y0] at one point via lower semicontinuity of rank; T lies in V(K2), not in C20, so T = C30.
   Status: computed at five QRNG points (three at 32009, two at 32029), README table lines 87 to 93. Falsifier: rank
   below 6 at a new point, a derivative error that the tangent-consistency check (README lines 98 to 102) would not
   catch, or an irreducibility gap (T irreducible requires the parameter set U irreducible and M rational on it).
4. Placement at 32029 rests on V(K2) = C20 cup C30 and C20 in V(Lambda), with P and K2 : P not retained there.
   Status: argued. Falsifier: a third component of V(K2) at 32029, or C20 not contained in V(Lambda) at 32029.
5. Conclusion: E0 = V(K2), and since K2 is radical and lies in L, L = K2 and F(I) = k[y]/K2 in every degree at both
   primes. Status: argued from claims 1 to 4. Falsifier: E0 = V(K2) set-theoretically does not give L = K2 as ideals
   unless L is radical or saturated in the right sense; check whether "K2 radical and K2 in L and V(L) = V(K2)" implies
   L = K2 for the defining ideal of a fiber cone (L need not be radical), and what extra fact closes the gap if not.
6. Prediction: HF(k[y]/K2, 6) = 8,624 and every certified h_d (d <= 5) equals HF(k[y]/K2, d) at both primes.
   Status: computed (README lines 66 to 70; ledger A5-138 to A5-149). Falsifier: a degree-6 truncated rank below 8,624.

## Questions to answer

- Does claim 5 follow? If set-theoretic equality E0 = V(K2) plus K2 radical and K2 in L does not force L = K2, state
  the exact missing hypothesis and the cheapest computation that supplies it (for example a Hilbert-function
  comparison in one more degree, or a primary decomposition of L in low degree).
- Is the direction of the surjection in claim 2 right, and does the embedding of Proj F(I'|_{B_4}) into the fiber
  over p hold as stated?
- Re-run one plane script at a new QRNG point from indices 70 to 99 at 32009 and report the RESULT lines.
- Conjecture where nothing is posited: the structure of E0 over P(L0) (is every fiber over P(L0) a linear 3-space; is
  C30 a P^3-bundle over an open set of P^2 and what is its degree from that description); whether the same local
  route decides the W8 -> N+ degree-6 rows A5-131 and A5-137; each conjecture with its falsifier and cheapest test.
- Remaining work: what computation would make the W8 degree-6 rank run (N = 19, measured preflight 375.62 GiB,
  forecast peak about 160 GiB, 17 to 20 h; docs/evidence/a5-exceptional-fibers/working/azure-cases/w8-d6-n19.md and
  w8-d6-n19-probe/README.md) unnecessary beyond doubt, and what it would still test.
- Defects: code, claims and records, with file:line.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Write it to
./docs/local/reviews/c30-<your-reviewer-name>.md, under 150
lines.
