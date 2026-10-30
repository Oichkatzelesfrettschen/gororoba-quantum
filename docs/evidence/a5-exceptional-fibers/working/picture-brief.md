# Brief: granular picture of the A_5 fiber program, the old E8-bar->VB run, and what to build

Read only; return your analysis as your final message. A separate reviewer audits code correctness
(`review-brief.md`); your job is the whole picture and the build advice.

Read: `purpose.md`, `decision-record.md` (all sections), `first-principles-plan.md`, `codex-consult-v2.md`,
`runs/*/out.log` and `runs/*/input.sing`, the templates and probes, and the old E8-bar->VB run in `e8vb-old/`
(`e8vb_split_homog.sing` input, `out.log` Singular protocol, `progress.log`, `samples.tsv` RSS/MemAvailable trace,
`floor_fired`, `exit`, and `extend-timeout.sh`, the deadline-hold script that SIGSTOPped the run's `timeout`).
Resources and installables are listed in `codex-consult-brief.md`; `~/Github/PKGBUILDs` is the owner's Arch package
tree (one directory per package) for anything worth building.

Answer:
1. **Old E8-bar->VB run.** From its logs: what it computed (Rees graph in 20 variables, homogenized, eliminate a,
   special fiber, minAssGTZ), how far it got (pair counts over time from `out.log`/`progress.log`, memory from
   `samples.tsv`), whether any partial result is usable, and why it did not converge. Confirm or refute that
   `extend-timeout.sh` disabled both kill paths (SIGSTOP on `timeout`, floor signal delivered to the stopped
   process). Compare with method A, which gave h1 = 10, h2 = 34 for the same input in 7 s (`runs/e8vb_a2/`).
2. **Granular picture.** One table over every pair (X+-, Iso, E8-bar->N+, E8-bar->N-, W8->N-+, E8-bar->VB): what is
   established (h_d, V(K2) dimension and degree, symmetry), what is running and where, what remains to reach the
   purpose's deliverable (full fiber, components, char-0 support), and what each result means for roadmap item 6.
3. **What to build.** Concrete tooling with expected payoff, for example: a reusable driver that runs method A
   degree by degree and extracts relations automatically; a faster completion certificate than saturation (a
   Hilbert-series bound, a regular-sequence or Cohen-Macaulay argument, a dimension-plus-primality argument); a
   modular second-prime and CRT harness; GPU or LinBox sparse rank for large normal-form matrices; packages from
   PKGBUILDs or GitHub (Macaulay2 ReesAlgebra/MultigradedImplicitization, Normaliz, CoCoA-5, OSCAR, msolve master),
   each with why and the falsifier for its payoff. Say also what not to build.
4. **Placement.** Given the host memory incident (decision record section 7), which jobs belong on the host,
   Kaggle CPU, Azure VMs (4 vCPU / 84 GB, one region per VM), or GitHub Actions, with memory and time budgets.
Cite file:line for every claim read from a file.
