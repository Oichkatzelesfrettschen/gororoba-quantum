# Brief: audit of the E8-bar -> VB degree-7 and W8 -> N- characteristic-0 plan (branch a5/vb-degree7-export-and-w8-char0)

Read first: docs/local/briefs/workspace-AGENTS.md (a copy of the workspace guide), then AGENTS.md at the root of this
checkout (the branch a5/vb-degree7-export-and-w8-char0, stacked on the head of PR 803). Work read-only: change no file
except your report (named at the end); never commit, push, stash, submit to a provider or start a cloud resource;
spawn no subagents. You may run git, Python as `$PYTHON` (set `PYTHON=python3` and
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; numpy, sympy and python-flint are installed) and Singular as
`Singular -q --no-rc < script` (4.4.1; close stdin). Keep each computation under 15 minutes and 6 GiB, in a scratch
directory under /tmp, never inside a checkout. The host already runs Singular jobs of this branch (a 16 GB lift and a
truncation check), so run at most one computation at a time and never touch a process you did not start. A random
sample takes its seed from docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json values at indices 1600-1699; name the
indices you use.

Material: `git diff d970b76f3...HEAD` on this branch, and the files it cites. The plan is
docs/design/a5-vb-degree7-and-w8-char0-plan.md. Read the code, records and ledger as the authority, not the plan's
summary of them. Ledger: docs/evidence/a5-exceptional-fibers/ledger.tsv (rows A5-010, A5-061, A5-062, A5-066, A5-138 to
A5-149, A5-247 to A5-249, A5-258, A5-260, A5-269, A5-277 to A5-279). Transfer proposition:
docs/notes/topics/a5-char0-and-kernel-limits.md. Engine: docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py.

## Audit dimensions (cover every one; a dimension with no defect gets one line saying what you checked)

1. Mathematics of the transfer: the proposition's three checks, the lower-semicontinuity directions, and whether
   radicality enters the per-degree statement.
2. The all-degree hypothesis for W8 (flatness of k[y]/K2 over the localized Z[i], openness of geometric reducedness
   and Cohen-Macaulayness, EGA IV_3 12.2.4 and 12.1.6, component degrees 20 + 30). Check the cited theorems' hypotheses
   (properness, flatness, finite presentation, reducedness versus radicality of the affine cone) against this family.
3. Cost extrapolations: the std(J + m^N) table, the ratio bracketing for N = 21 and 22, and the lever threshold.
   Recompute from the records.
4. Falsifiers and mutation arms: every prediction and probe has a falsifier that can actually fire.
5. Engine identity and digest rules: whether a lever changes the export identity, and the successor-engine rule.
6. Repository canon: global orderings only, `parallel.py` for independent loops, QRNG seeds, the 3-hour cap.
7. Ledger consistency: statuses against evidence for the rows listed above.
8. Probe and lift scripts: docs/evidence/a5-exceptional-fibers/vb-export-levers/ and
   docs/evidence/a5-char0-transfer/cofactors/. Do the scripts compute what the plan says, and does the
   canonicality test of the cofactors (same support at two primes) decide what the plan claims?

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The Singular std call is 99 percent of an E8-bar -> VB cell's wall time. Status: measured. Support:
   vb-d6-laptop/*.json `export.computed_seconds`. Falsifier: a record in which tables, products or closure dominate.
2. N = 21 alone tests three of the four degree-7 predictions. Status: argued. Falsifier: a prediction among r_21 = 609,
   closure at exactly 22, and the 7 / 8 / 0 / 0 split that N = 21 cannot refute.
3. The W8 per-degree transfer for d = 1 to 5 needs check 2 and check 3 only, and the 24,548 s radical test belongs
   to the all-degree statement. Status: argued from the proposition. Falsifier: a step of the proposition that uses
   radicality.
4. The multi-modular identity check is exact: an identity polynomial whose coefficients are below B in absolute
   value and that vanishes modulo split primes with product above 2B is zero over Z[i]. Status: argued. Falsifier: a
   gap in how B bounds the Gaussian coefficients, or in using split primes for Z[i].
5. Lift cofactors with equal support at two primes are the image of one Q(i) computation. Status: hypothesis.
   Falsifier: an example where supports agree and the reconstruction still fails, or where supports differ at a good
   prime for a deterministic algorithm.

## The open task list, and the thesis to attack

The session's open tasks follow, each quoted from its tracker entry. Attack this thesis adversarially: "nothing more
can be done with the present foundations. The N = 19 and N = 20 computations (and N = 21, 22 for E8-bar -> VB degree
7) take days, and the program lacks the foundational items needed to make them feasible, especially for tasks 37 and
42." For each task, either name a concrete computation that advances it under the 3-hour cap on a named substrate
(the build host: 12 threads, 38.6 GiB budget, RTX 4070 Ti; the Windows workstation laptop: RTX 4090 Laptop 16 GiB,
52.5 GB budget; Kaggle CPU sessions: 4 cores, 30 GB, 12 h, five at once; Kaggle GPU sessions: 2 x T4, 29 GB, 30 GPU-hours
a week, two at once; an Azure FX4mds_v2: 4 vCPU, 84 GB; docs/runbooks/classical-compute-pool.md), with its falsifier
and expected cost from a record, or show from the records that the thesis holds for it and name the missing foundation
precisely (the theorem, the engine change, or the measurement). Say which items run in tandem.

- 5 (umbrella, in progress): compute the A_5 exceptional fibers.
- 37: E8-bar -> VB degree-3 component, arcs into it (A5-016). Chart t7 normalized (isPrim, 7.5 min). Inference:
  exceptional divisor over P(L) = P^3 (t1:t3:t5:t7), so the t7 chart adds only one point; P1 needs order-2 arcs on a
  2-dimensional stratum (plane t1 = 0) with one jet parameter. Next: (a) order-1 arcs in chart t7 with t1 != 0 land in
  V(P2); (b) order-2 arcs over the t1 = 0 plane in charts t3, t5, t7, testing P1 generators on leading vectors.
- 42 (umbrella): characteristic 0. Done: structure checks, sign pairs, the W8 twisted product in characteristic 0.
  Open: check 2 (task 75) and the per-pair transfers; ladder numbers stay F_p statements.
- 56: Iso arc support certificates. Is E0 = V(K2) (prime, degree 23, projective dimension 4)? The dense chart's
  saturation did not finish in 8 h on an Azure FX4 (84 GB); coordinate charts G16, G2 used 5 GB in 34 min. Options:
  a larger VM for saturation alone, or a degree-6 membership upper bound.
- 75 (in progress): check 2 for X- -> N- (the cofactor pilot in docs/evidence/a5-char0-transfer/cofactors/).
- 103: claims for the merged IBM wide and Tuna 6-CZ acquisitions (a separate change).
- 106: gororoba-open follow-up (right-nullity corollary, zero-lower-half companion, div-by-4 test, mutation arm for
  CDUnconditionalDoublingNullity.v), in the other repository.
- 110: E8-bar h_6 membership route: a membership test that avoids std(J + m P_d) (the degree-2 receipt took 12,678 s;
  degree 3 never finished). Test membership of the 91 forms in L at degree 5, then the 140 forms at degree 6.
- 113 (gated): W8 degree-6 h_6 = 8,624 rank test; not needed for F(I) by A5-066. Products need L = 103 GiB dense under
  v11 (docs/evidence/a5-exceptional-fibers/w8-engine-map/efficiency-levers.md).
- 115: exact torus over Q in the Klein centralizer, then a weighted std of J (A5-258).
- VB degree 7 (A5-279) and W8 in characteristic 0: the plan under review.

## Questions to answer

- Which VB degree-7 option should the owner take, the N = 21 cell or a lever first, and what result would change that?
- A lever not in the plan that stays in global orderings and could cut std(J + m^N) by 2 to 9 times at N = 18.
- The cheapest sound route to W8 check 2, given the X- pilot's numbers.
- Conjectures the records suggest and no row states, each with its falsifier and cheapest test.
- Defects in code, claims and records, with file:line.

Report ranked by consequence. Tie every claim to a file:line, a command with its output, or a theorem name, and mark
each proved, computed, measured or hypothesis. Write it to docs/archive/reviews/a5-vb7-w8-char0/review-codex.md, under
400 lines.
