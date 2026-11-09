# Brief: adversarial analysis and synthesis across PRs #788, #789, #790 and the A_5 findings

Read first: the workspace AGENTS.md (in the directory above the primary checkout) if reachable, then AGENTS.md here.
This directory is a detached checkout of origin/main. Change no file except your own report (named at the end); never
commit, push, stash, submit to a provider, or start a cloud resource; spawn no subagents. Read-only commands, git,
Python (PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python", GLIBC_TUNABLES=
glibc.rtld.optional_static_tls=4096) and Singular may be used to check claims; keep any computation under 10 minutes.

## Material

The three open pull requests, read through git without checking them out:
`git diff origin/main...origin/<branch>` and `git show origin/<branch>:<path>`.
- #788 `ibm/cd64-128-coset-blocks`: whole-operand nullity of two-term operands of the 64- and 128-dimensional
  Cayley-Dickson algebras in one wide circuit, retained runs on ibm_fez and ibm_kingston
  (`scripts/pathion_wide_coset_analysis.py`).
- #789 `qi/pathion-one-cz-null-block`: the Tuna-17 6-CZ null-block series with coin-fixed twins, retained
  (`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json`; the preregistered rule reads unresolved_batch).
- #790 `a5/e8bar-n18-p32029`: h_5 = 952 for E8-bar -> N- at p = 32029 (ledger A5-220).

The takeaway and findings documents on main:
- `docs/notes/topics/a5-hardware-algebra-synthesis.md`;
- `docs/notes/topics/a5-exceptional-fiber-findings.md` and `docs/notes/topics/quantum-linear-algebra-fit-a5.md`;
- `results/live/PATHION_KERNEL_MAP_FINDINGS.md`;
- `docs/evidence/a5-exceptional-fibers/ledger.tsv` (every A5 claim and status) and the `tslice/` and
  `hardware-orbits/` READMEs there;
- `docs/evidence/pathion-kernel-map/conjectures/` (`REPORT.md`, `mechanisms.md`);
- `docs/runbooks/ascella-block-run-design.md`.

The program and the lower-dimensional work:
- `docs/notes/rank_locus_two_dimension_gap.md` ("Route to the global classification") and
  `docs/design/dimension32-global-topology-program.md`;
- `docs/design/a5-kernel-attachments-program.md` and `a5-kernel-bundles*-program.md`;
- `docs/evidence/a5-zero-divisor-strata/`, `a5-strata-regularity/` and `a5-rank-strata-equations/`;
- for the 16-dimensional sedenions: `docs/notes/topics/sedenion_hardware_witness_review.md`,
  `cayley_dickson_sparse_census.md`, `kaplansky-mechanisms-cayley-dickson.md`, the `cd-*` evidence directories, and
  `gororoba_quantum/cd_core.py` (the specification).
- Compute hosts and their limits: `docs/runbooks/compute-flags.md`, `docs/runbooks/run-rulebook.md`,
  `docs/notes/kaggle/README.md` (12 h sessions).

## Work

1. Justify or falsify every open, survives or hypothesis row of the A5 ledger that the three PRs or the takeaway docs
   rest on. For each, give the decisive check you ran or the source line, and say what would move it.
2. Conjecture where nothing is posited. Name structural statements the evidence suggests but no record states. Each
   needs its falsifier and the cheapest computation that tests it. Candidates to examine, not to assume:
   - does the 32-dimensional nullity stratification restrict to, or decompose through, the sedenion zero-divisor
     structure (A_4 inside A_5 under doubling, coset blocks, the G_2 action);
   - does the Tuna q11 readout fault or the Fez k28 placement fault share a mechanism with earlier instrument
     findings;
   - do the contact orders (eps vs eps^2) predict the fiber-cone degrees or the arc limit orders;
   - does the 64/128-dimensional nullity ratio (2.148 measured, 2.143 ideal) follow a closed form along the ladder;
   - does h_d of E8-bar -> N- (21, 83, 225, 495, 952) fit a Hilbert polynomial predicting h_6 = 1666.
3. Connect results across programs, not only within one, from first principles: which algebraic fact explains which
   hardware observation and the reverse. Mark each connection proved, computed, or hypothesis.
4. Remaining items: for each open item of the A5 program (item 6 attachments, the W8 and E8-bar -> VB same-dimension
   components of A5-218, characteristic 0, the Iso degree-6 ladder, the 64/128 interpretation, the Tuna rerun), give
   the computation, its expected cost and peak memory with the evidence for the estimate, and the host it fits: the
   laptop (WSL; the N = 18 run took 26 h at 35 GiB), an Azure FX4mds_v2 (84 GB), or a Kaggle CPU session under 12 h.
   Say which items no available host can finish and why.
5. Review defects in the three PRs (code, claims, records) with file:line.

Report, ranked by consequence, with every claim tied to a file, line or command: name it
`docs/local/reviews/findings-32d-<codex|grok>.md`. Codex writes that file; Grok prints the report as its answer.
Under 400 lines.
