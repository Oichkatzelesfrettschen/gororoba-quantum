# Brief: PR 916 of gororoba-quantum, the owed falsifiers of ledger rows A5-002, A5-003, A5-009, A5-024, A5-032 and A5-548

Read first: the workspace AGENTS.md, then
the repository AGENTS.md. Work read-only: change no file in any
repository; write only inside your scratch directory (your working directory) and your report. Never commit, push,
stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git, Python as
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3` (python-flint 0.9.0 installed), and `Singular` 4.4.1 from
PATH. Keep each computation under 15 minutes and 8 GB of memory, one heavy process at a time (12 threads, 62 GB host
shared with other work); run scripts with their output paths pointed into your scratch directory, never at the record.

Material: the worktree of this repository (branch
`a5-ledger-owed-falsifiers`, head 43feb6fac). Read the change as `git -C WT diff origin/main...HEAD` (WT = that path);
the PR body is `gh pr view 916`. Evidence root: `docs/evidence/a5-exceptional-fibers/` (call it A5/). The ledger is
`A5/ledger.tsv`, one claim per row, checked by `A5/ledger.py --check`; row ids and their statuses are the claims.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. A5-009 / A5-559: on the E8-bar -> N+ and N- header slices at primes 32009 and 32029, the relation ideal L equals
   the degree-2 ideal K2 in every degree. Status: proved, given K2 contained in L. Support:
   `A5/arcs/relation_ideal_orders.py`, record `A5/arcs/relation-ideal-orders.json`, logs in
   `A5/arcs/relation-ideal-orders/`; the deduction pattern is the one ledger row A5-457 uses (read its basis). The
   argument: `primdecGTZ` gives K2 three associated primes P1, P2 and an embedded A; three monomial arc families over
   F_p(W,R,S,Z,E)[[s]] have limit primes P2, P1 and A; on the embedded family the nilpotent linear forms have order
   nu+1 while the argument needs below nu+2; J vanishes on every arc. Falsifier: an associated prime of K2 that no arc
   family reaches, an arc on which an element of L fails to vanish, a wrong order count, or a gap in the deduction
   from these facts to L = K2 in all degrees. For N+ at 32009, K2 inside L comes by sign transport (A5-013, A5-024),
   not a direct receipt; judge whether that premise is sound.
2. A5-548 / A5-560: the quadric rings of the six fibers at the third split prime 32057 are Cohen-Macaulay exactly
   when reduced. Status: survives (three primes). Support: `A5/third-prime/quadric_rings.py`, records
   `A5/third-prime/quadric-rings-p32057.json` and `A5/third-prime/calibration-p32009.json`, predictions written
   before the run in `A5/third-prime/predictions.md` (with a labeled correction), README `A5/third-prime/README.md`.
   Methods: CM by `k2_cm.test`; nonreduced by a nilpotent linear form; reduced by a section chart whose
   multiplication-matrix characteristic polynomial is squarefree (flint). Falsifier: a certificate that does not
   prove what it is said to prove (in particular: does a squarefree characteristic polynomial on one chart prove the
   whole ring reduced?), a calibration that does not exercise the failure mode, or a verdict that disagrees with
   an independent check.
3. A5-024: over Q(i) the 16 generators of J and 21 of G for E8-bar -> N+ map under t8, t9 -> -t8, -t9 onto those of
   N- with coefficients +1 or -1, as a bijection. Status: proved. Support: `A5/structure/sign-symmetry/npm_map_qi.py`
   and `npm_map_qi.json`. Falsifier: a generator without a signed image, a non-bijection, or reduction to the tracked
   headers failing.
4. A5-032: `signed_perm_sweep.py` on the nine 32029 headers writes the 32009 sweep record byte for byte. A5-002 and
   A5-003: `asymmetry.py` and `base_locus.py` replay their retained tables. Status: proved by replay. Falsifier: a
   replay that differs, or a record that a byte-identical replay does not actually test.
5. Bookkeeping: `ledger.py` admits prime 32057; `nullity8_fiber_import.py` regenerated in place; three on-demand
   gates in `ci/gates.json` (core-a5-e8-sign-map-qi, core-a5-header-relation-ideal-orders,
   core-a5-third-prime-quadric-rings); tests `tests/test_a5_owed_falsifier_programs.py`; the `pr.yml` sparse
   checkouts now leave out `A5/third-prime/relations/[ew]8-nm/d2/sq.txt.part*` and `nf-d2.txt*` (split products
   files, 475 MB). Falsifier: a gate that passes on a corrupted record, a test that cannot fail, a sparse pattern
   that drops a file some check reads, or a ledger status the evidence does not carry.

## Questions to answer

- Defects in code, claims and records, with file:line, ranked by consequence.
- Is the status of each changed ledger row (proved, survives) earned by the evidence it cites?
- Conjectures the evidence suggests and no record states, each with its falsifier and cheapest test.
- Remaining work for A5-548 (characteristic 0, a fourth prime) and A5-559 (characteristic 0 on the header slices):
  the computation, cost and peak memory with the evidence for the estimate.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your final answer, under 250 lines.
