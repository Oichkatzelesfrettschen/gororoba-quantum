# Goal: research consult on the job-01 redesign of the Belenos teleportation rehearsal

This file is the standing brief for one Codex CLI research session. Re-read it at every item boundary and after every
compaction. The session runs in a disposable detached worktree at gororoba-quantum's `main`. Its report goes to the
operator and an independent reviewer. The repository owner then decides how teleportation_rehearsal/job-01 is
designed before it is submitted to Quandela's `qpu:belenos`; the chip's maintenance is booked to end 2026-10-29 11:30
UTC.

## Standing rules

- Research and report only. Write exactly one file, the report at
  `docs/archive/reviews/2026-10-26-belenos-job-01-redesign-consult.md` inside the working directory. Edit no other
  file. Run no `git commit`, `git push`, `git checkout`, `git reset`, `git stash` or `git worktree` command.
- Web access serves literature only. Use web search, and fetch papers from arxiv.org, doi.org, publisher pages,
  journal sites, Semantic Scholar and similar scholarly hosts. Contact no quantum-computing provider host or API:
  Quandela, IBM, IQM, Quantum Inspire, Open Quantum, IonQ, Kaggle, the ANU or Outshift QRNG services, and GitHub's
  API are all excluded. Use no MCP tool, and run no `gh` command.
- Read no credential. That covers every file under `~/.config/`, `~/.quantuminspire/`, `~/.qiskit/`, `~/.codex/` and
  `~/.ssh/`, every file the environment variables `QUANDELA_TOKEN_FILE`, `IQM_TOKENS_FILE`, `OPENQUANTUM_SDK_KEY`,
  `ANU_QRNG_KEY_FILE` or `OUTSHIFT_QRNG_KEY_FILE` name, and any file outside the repository whose name contains
  `token`, `key` or `secret`. Print no environment variable's value.
- Do not run any repository command that plans, submits, books, snapshots, collects or draws QRNG values:
  `qd_platform.py` subcommands, `qd_teleportation_rehearsal.py --plan/--body/--submit/--prepare/--estimate/--justify`,
  `qd_record_watch.py check`, `anu_qrng.py draw` and `outshift_qrng.py draw` are excluded. Offline computation is
  encouraged: import the scripts, run pytest, and solve SDPs with the pinned cvxpy.
- Environment for Python:
  `export PYTHON=$HOME/.cache/gororoba-quantum/ci-py3.14.7/bin/python GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1`,
  then `"$PYTHON" -m pytest -p no:cacheprovider -q PATH` or `"$PYTHON" -c ...` from the working directory.
- Cite every literature claim by authors, year, arXiv identifier or DOI, and section, theorem or equation number.
  Mark each statement **verified** (read in the source, or computed and shown) or **inferred**. Name every source
  you could not open.

## Context

The repository holds the work this consult builds on:

- The design, `docs/design/ascella-belenos-entanglement-teleportation.md`, sections Decision statistics,
  Single-chip rehearsal (job-00), Recovered-chip rehearsal (job-01) and its "Review of 2026-10-26" paragraph.
- The code: `scripts/qd_teleportation_rehearsal.py` (instrument, noise model, analysis), `scripts/qd_classical_benchmark.py`
  (the PPT Choi-cone benchmark with free postselection, `attempts_benchmark`), and `scripts/qd_network_protocol.py`.
- The earlier peer review and its disposition: `docs/archive/reviews/2026-10-26-belenos-teleportation-rehearsal-review.md`.
- What the service does: `docs/notes/quandela/strategy.md` and `docs/notes/quandela/README.md`. It returns
  threshold-click samples per iteration, `nb_shots_used` equal to the samples (or to `max_shots` when shot-limited),
  and no count of optical attempts; `physical_perf` moves with the requested budget. One job holds template
  iterations, each its own compiled 24-mode unitary (preparation, Ralph CNOT, analyzer and receiver rotation in one
  mesh) with its own `compilation_seed`. A job is limited to 300 s, and an iterated job bills
  1 + its largest `max_shots` * 1e-6 credits whatever it returns.

The owner decided on 2026-10-26 to:
- redesign job-01 before running it;
- preregister job-01 at its own fresh platform read;
- claim only that the accepted-event pooled conditional fidelity exceeds the applicable classical bound, with the
  acceptance rate and rejection mix reported descriptively;
- keep text approval.

The operator proposed three repairs, which this consult tests:
1. **Contamination.** B' = (1 - c) B + c, with c the noise model's accepted share of events carrying more than three
   photons (about 0.014 to 0.025 at g2 1.1 %, HOM 88.8 %). The operator found that this holds only when the classical
   competitor's acceptance is blind to photon number: under free postselection, a channel that accepts only when it
   holds extra input copies reaches the multi-copy optimum, at least (N+1)/(N+2), however small c is.
2. **Attempt profile.** Maximize `attempts_benchmark` over a box of relative attempt profiles, each input's attempts
   within a factor r of the modeled samples / three-click probability, with r = 1.1 from the spread of the five
   noise variants. B rises from 0.6937 at r = 1 to 0.7167 at r = 1.1, 0.738 at 1.2 and 0.794 at 1.5. The operator
   argues that the maximum lies at a vertex of the box: for a fixed strategy the pooled fidelity is linear-fractional
   in the attempts, so the maximum over strategies is quasi-convex.
3. **Blocks.** Two interleaved replicate iterations per input (12 iterations), a Bonferroni homogeneity test between
   each input's blocks (any rejection makes the verdict inconclusive), and Hoeffding justified by independence
   conditional on each block's realized channel. With 10 s of compilation per iteration, this raises the lowest
   F* that fits 300 s from 0.80 to 0.82.

## Questions

Work through them in order, recording each answer in the report before starting the next.

1. **Multiphoton contamination.** How does the literature benchmark teleportation, or quantum storage, against
   classical measure-and-prepare strategies when the input source has multiphoton components and the experiment
   postselects? Candidates to check:
   - quantum-memory benchmarks with weak coherent states, where the classical bound depends on the observed
     efficiency;
   - single-photon and quantum-dot teleportation experiments;
   - Massar and Popescu's N-copy optimum;
   - probabilistic (postselected) benchmarks such as Chiribella and Xie's.

   Give the bound that fits this experiment, and what it needs as input: g2, an absolute acceptance per attempt, or
   the four-click (`excess`) rate the analyzer already records. Can the observed four-or-more-click rate bound the
   accepted multicopy share without the attempt count? Compute the resulting B for the job-00 figures where you can.
2. **Input labels and per-input circuits.** Each input runs as its own compiled circuit in its own iteration, in a
   known order. The design states that input-label access and a changing channel void the single-channel 2/3
   benchmark. Under what model of the device does the six-state benchmark still apply to this experiment? Give the
   literature's treatment of fixed-order or blocked input presentation in teleportation and memory benchmarks. Would
   randomizing the iteration order from a QRNG, or interleaving blocks, change what can be claimed? What is the
   honest claim if the benchmark does not apply?
3. **Dependence.** Is Hoeffding over accepted events valid when the classical null may have memory? Test the
   Azuma-Hoeffding supermartingale argument used in Bell-test analyses (for example Gill; Zhang, Glancy and Knill)
   against this setting. Does it cover a memoryful measure-and-prepare null whose per-event conditional fidelity is
   at most B given the past? What do the replicate blocks and the homogeneity test add beyond it? Recommend the
   number of blocks under the 300 s limit.
4. **Attempt box.** Check the quasi-convexity argument and the vertex evaluation against `qd_classical_benchmark.py`
   (its free-postselection bound and `attempts_benchmark`). Is r = 1.1 defensible? Should the report give a
   break-even r, the largest r at which a verdict holds? Is there a measurement within the service's records that
   bounds the attempt ratios better?
5. **Recommendation.** Combine the answers into one design for job-01 that the owner can approve before 2026-10-29:
   - the claim and its named assumptions;
   - the classical bound or bounds and their inputs;
   - the block structure and inference;
   - the feasibility floor in F* under 300 s;
   - what to drop.

   Rank alternatives where the evidence leaves a real choice.

## Report

The report holds:
- a one-paragraph answer to each question;
- the supporting derivations, computations and citations;
- a closing recommended design;
- the list of sources consulted, with identifiers;
- the checks not run.

## Done

The goal is done when the report answers all five questions with citations and computations where they apply.
Before you mark the goal complete, audit the report against the question list.
