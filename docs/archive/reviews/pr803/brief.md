# Brief: adversarial review of PR 803 (a5/ledger-audit-and-engine-v12) at commit 5f787dfe4

Read first: docs/local/briefs/workspace-AGENTS.md (a copy of the workspace guide), then AGENTS.md at the root of this
checkout (the review checkout, detached at 5f787dfe4, the head of draft PR 803). Work
read-only: change no file except your report (named at the end); never commit, push, stash, submit to a provider or
start a cloud resource; spawn no subagents. You may run git, Python as `$PYTHON` (set `PYTHON=python3` and
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; numpy, sympy and python-flint are installed), Singular as
`Singular -q --no-rc < script` (4.4.1; close stdin) and Rocq from the opam switch `rocq-9.3`
(`eval "$(opam env --switch=rocq-9.3)"`). Keep each computation under 15 minutes and 8 GiB, in a scratch directory
under /tmp, never inside a checkout. This host is an interactive desktop already running two Singular jobs: run at
most one computation at a time. A random sample takes its seed from docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json
values at indices 1400-1499 (codex) or 1500-1599 (grok); name the indices you use.

Material: the PR diff, `git diff origin/main...HEAD` (198 files). The PR body is the claim list below; read the code and
records, not this summary, as the authority.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Engine v12 (`gororoba_quantum/modular_echelon.py`, `docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v12.py`)
   returns the same reduced echelon bases, pivots and ranks as the flint backend; records in `engine-v12/` are
   byte-equal on W8 degree 4 N = 13 and Iso degree 6 N = 19. Status: measured. Falsifier: a code path where the INT8
   digit product or the PLUQ back substitution is inexact for p < 2^15 or an inner dimension above 32,768.
2. Check 1 of the characteristic-0 transfer (ledger A5-247, `docs/evidence/a5-char0-transfer/reduction_check.py`): J
   and G of the ten pairs reduce well at 32009 and 32029 and equal the retained headers. Status: computed. Falsifier: a
   comparison that cannot fail (inspect the mutation arm), or a header path that is not the one the certificates bind.
3. Check 3 (A5-249, `truncation_check.py`): the reduced standard basis of J + m^N over Q(i), m the slice variables, is
   integral and equals the header basis at N = 4, 8, 11, 15 for X- -> N-. Status: computed. Falsifier: m not the ideal
   the rank engine truncates by, or a comparison that ignores coefficients.
4. Check 2 (A5-248, `quadric_lift.py`) computes the degree-2 relation space {q : q(G) in J + m I^2} over Q(i) exactly as
   the modular receipts do (`working/distribute/out/a5-xm-d4/xm_p1/d2/d2-products.sing`). Status: running, no verdict.
   Falsifier: a difference between the two computations, or a comparison of echelon forms that is not sound.
5. A5-270 (`x_opposite_qi.py`, `x-opposite-qi.json`): F(I) = Q(i)[y1, y2, y3] in every degree for X+ -> N- and
   X- -> N+, from J smooth of dimension 4 at the origin, a parametrization Phi that is a formal isomorphism onto V(J),
   and I = w (G'') with (G'') a smooth curve germ; `span_check.py` shows (G) is the full Pfaffian ideal over Q(i).
   Status: proved (claimed). Falsifier: a gap in the local-algebra argument (germ, Nakayama, global versus local
   membership, the u = 1/(1+w) substitution), or an identity the script tests incorrectly.
6. The notes `docs/notes/topics/a5-char0-and-kernel-limits.md`: the three-check transfer argument (lower
   semicontinuity of rank, good reduction of J + m^N for the lower bound) and the Hurwitz and Gurvits alignments, each
   marked documented, computed or hypothesis. Status: argument plus citations. Falsifier: a wrong direction of
   semicontinuity, a missing hypothesis, or a citation that does not say what is attributed.
7. Ledger rows A5-248 to A5-276 (`docs/evidence/a5-exceptional-fibers/ledger.tsv`): each status matches its basis,
   each evidence path supports the claim, and A5-029's split into A5-272 to A5-276 preserves its falsifier. Status: the
   ledger checker passes (`ledger.py --check`). Falsifier: a row whose basis does not support its status.
8. A5-260 and A5-269: E8-bar -> VB closes at N = 3d + 1 (d = 4, 5, 6) with last jump 2d + 1 on blocks 0 and 1; the
   degree-5 split 5/6/0/0 was preregistered in commit dceef9bc6 before its cells ran. Status: measured. Falsifier: a
   record in `vb-d6-laptop/` or `d4-p2/` that disagrees, or a preregistration that postdates its run (compare the commit
   time with `vb-d6-laptop/cells*.events`).
9. `docs/archive/reviews/cd-tower/pasted-analyses-verification.md` verdicts on 58 claims, and the corrected facts in
   that directory's README. Status: computed by one agent, two numbers reproduced. Falsifier: a verdict its own script
   does not reproduce.
10. The ledger-audit reconciliation `docs/archive/reviews/ledger-audit/README.md` and the corrected run-plan rows in
    `docs/notes/topics/a5-exceptional-fiber-findings.md` and `docs/runbooks/compute-flags.md`. Status: reconciled.
    Falsifier: a correction that contradicts its cited record.

## Questions to answer

- Rank defects by consequence for the goal: the kernel-plane attaching data (`a5-exceptional-fiber-status.md`, "The goal").
- Is the characteristic-0 transfer argument complete for a pair once checks 1 to 3 pass? Name any missing step.
- Conjecture where nothing is posited: the VB jump law at degree 7 (running: r_21 = 609, r_22 = 624 predicted), what
  explains 2d + 1 for VB against (2d + 1)^2 for Iso, W8 and X-, and the cheapest test of each conjecture.
- Defects in code, claims and records, with file:line.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Write it to docs/local/reviews/pr803-<your reviewer name>.md in this
checkout, under 700 lines.
