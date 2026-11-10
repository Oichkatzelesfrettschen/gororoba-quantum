# Brief: final adversarial review of the A_5 roadmap-item-6 direction, every open task and the compute environment

Read first: docs/local/briefs/workspace-AGENTS.md (a copy of the workspace guide), then AGENTS.md at the root of this
checkout (branch a5/vb-degree7-export-and-w8-char0 at 84276830f, stacked on PR 803). Spawn no subagents. Never commit,
push, stash, submit to a provider, start a Kaggle session or create a cloud resource; recommend those instead. Change
no repository file except your report. You run without a sandbox: run computations only where the rules below allow.

Computation allowed:
- **Build host (this machine).** At most one Singular or Python computation of yours at a time, under 8 GiB, in
  /tmp/codex-a5-final/. The session's own jobs are running here; never signal a process you did not start.
- **Windows workstation laptop.** Reached as `ssh ALIENWARE 'wsl -e sh -c "..."'`; PowerShell expands `$` on the way,
  so upload a script file and run it. At most 8 threads and 12 GiB there, in ~/a5/codex-final/. Its tmux sessions
  `vbd7`, `vbladder` and `vblevers` are the session's runs: read their outputs under ~/a5/engine/v13/out and
  ~/a5/probes/vb-levers/, never stop them.
- **OCI `lab-a1`** (2 OCPU aarch64, 12 GB) if reachable, under 8 GiB.

Each computation runs under a stated deadline, and its result goes into the report with the command and output.

Material:
- `git log --oneline d970b76f3..HEAD`, the diff, and the files below. The records are the authority, not the
  summaries.
- docs/design/a5-open-tasks-and-compute-scope.md: the task list by blocker, hardware and run policy.
- docs/design/a5-vb-degree7-and-w8-char0-plan.md.
- docs/archive/reviews/a5-vb7-w8-char0/review-codex.md, the first audit, and README.md, its reconciliation.
- docs/design/dimension32-global-topology-program.md (roadmap items 6 to 8) and
  docs/design/a5-kernel-attachments-program.md (the item-6 deliverables).
- docs/evidence/a5-exceptional-fibers/ledger.tsv, docs/notes/topics/a5-char0-and-kernel-limits.md and
  docs/notes/topics/a5-exceptional-fiber-findings.md.
- docs/runbooks/classical-compute-pool.md, docs/runbooks/compute-flags.md and docs/runbooks/computer-algebra.md.
- gororoba-infrastructure (read-only, at ~/Projects/gororoba-workspace/gororoba-infrastructure): `hosts/` and
  `clouds/`.
- The engine docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v13.py, which is v12 with `slimgb` in the
  export.

The owner's ruling of 2026-11-09 is the run policy: well-scoped long runs are approved, and Kaggle sessions under 12 h
are free and approved; paid cloud and QPU keep the written-case rule.

## Measured since the first audit (live; the records named are the authority)

- `slimgb` against `std` for E8-bar -> VB J + m^13 at p = 32009 returns byte-identical s, the same kbase and the same
  multiplication tables, in 66.1 s against 112.2 s (`vb-export-levers/slimgb-identity-n13.log`).
- N = 15: 301 s against 562 s. N = 16: 649 s; the N = 16 `std` cell is running.
- The laptop runs `std` at N = 18 beside `slimgb` at N = 18, 19 and 20, a `slimgb`/`std` ladder for N = 1 to 17, and
  engine v13 on VB: a degree-5 validation at N = 15 (record r = 255, 75/50/65/65) and degree 7 at N = 21 and 22 at
  both primes. Predictions: r_21 = 609, r_22 = 624, split 7/8/0/0.

## Attack, dimension by dimension (cover every one)

1. **Direction.** Do the open tasks produce what roadmap item 6 admits, attaching maps on every admitted incidence?
   Which deliverable of a5-kernel-attachments-program.md has no task at all? Name each gap with the record that shows
   it. Then state what roadmap items 7 and 8 need from item 6, and whether any item-6 output they need is missing.
   Falsify or justify the claim that no gap remains beyond the listed tasks.
2. **`slimgb` from first principles.** Explain why `slimgb` (slim Groebner bases, Brickenstein: pair selection by
   polynomial length and weighted length, reductions balanced by length) beats `std` on J + m^N. Explain how the
   reduced basis under option(redSB) is unique. List every Singular option, ordering and argument that changes
   `slimgb`'s cost (option(prot), redTail, the weighted-length heuristic, degBound, `groebner` and its methods,
   `modStd` and `parallel.lib`, the variable order), with Singular's own help text (`Singular -q --no-rc -c 'help
   slimgb;' < /dev/null`). Measure the promising ones at N = 13 to 15 on the laptop.
3. **Libraries and software, CPU and GPU.** Falsify that Singular is the right tool for each computation class:
   - the truncated standard basis;
   - the rank closure;
   - membership;
   - check 2;
   - saturation;
   - the Q(i) checks.

   Compare against what is installed or installable: msolve, FLINT and python-flint, M4RI/M4RIE, FFLAS-FFPACK and
   LinBox, Macaulay2, CoCoA, Giac, openF4, and the GPU path (engine v12, cupy, torch on CUDA, Kaggle T4). Say which
   class each fits, with a measured or cited rate, not a preference.
4. **Placement.** For every open task give cores, RAM, GPU, host, a runtime estimate from a measured rate, and what
   runs in tandem. Cover the laptop, the build host, lab-a1, five Kaggle CPU sessions plus two GPU sessions, the Azure
   FX4 (credit lapses 2026-11-23), GCP (12 vCPU, 300 USD) and AWS (2 vCPU, 8 GiB). Give the schedule that resolves
   roadmap item 6 soonest.
5. **Foundations.** Name each foundation a task lacks: a theorem, an engine change or a measurement. Falsify that
   every listed blocker is real.
6. **Ledger and records.** Check statuses against evidence for the rows the scope document cites.
7. **Code.** Check engine v13, `run-cells-v13.sh`, the ladder and the probe scripts for defects with file:line.

Write the report to docs/archive/reviews/a5-vb7-w8-char0/review-codex-final.md, ranked by consequence, under 500 lines,
every claim tied to a file:line, a command with its output, or a source, each marked proved, computed, measured or
hypothesis. End with the owner decisions, each with options, estimates and a recommendation.
