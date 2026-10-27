# Goal: deep peer review of the Belenos teleportation rehearsal and its job-01 case

This file is the standing brief for one Codex CLI review session. Re-read it at every item boundary and after every
compaction. The session runs in a disposable detached worktree at the head of pull request #560
(`quandela/teleportation-job-01`) of gororoba-quantum. Its findings go to the owner, who decides whether job-01 is
submitted to Quandela's `qpu:belenos` after the chip leaves maintenance (booked to end 2026-10-29 11:30 UTC).

## Standing rules

These rules bind every step, and the sandbox does not enforce all of them.

- Review only. Write exactly one file, the report at
  `docs/archive/reviews/2026-10-26-belenos-teleportation-rehearsal-review.md` inside the working directory. Edit no
  other file. Run no `git commit`, `git push`, `git checkout`, `git reset`, `git stash` or `git worktree` command.
- Read no credential. That covers every file under `~/.config/`, `~/.quantuminspire/`, `~/.qiskit/`, `~/.codex/`
  and `~/.ssh/`, every file the environment variables `QUANDELA_TOKEN_FILE`, `IQM_TOKENS_FILE`,
  `OPENQUANTUM_SDK_KEY`, `ANU_QRNG_KEY_FILE` or `OUTSHIFT_QRNG_KEY_FILE` name, and any file whose name contains
  `token`, `key` or `secret` outside the repository. Print no environment variable's value.
- Contact no provider and no network service. Every job, upload, plan, booking or QRNG read on any provider needs the
  owner's approval of a written case, and this review has none. Do not run any of these:
  - `qd_platform.py snapshot`, `plan`, `submit`, `collect`, `observe`, `status` or `cancel`;
  - `qd_teleportation_rehearsal.py --plan`, `--body`, `--submit`, `--prepare`, `--estimate` or `--justify`;
  - `qd_record_watch.py check`, or `anu_qrng.py draw` / `outshift_qrng.py draw`;
  - any `gh` command or any MCP tool.

  Offline commands are allowed: `--check`, `--analyze RUN --check`, `qd_rehearsal_secondary.py RUN --check`,
  `--simulate OUT` into a fresh directory under `/tmp`, `qd_record_watch.py --self-test`, `anu_qrng.py check`,
  `outshift_qrng.py check`, `ci/seed_provenance.py --check`, pytest, and short Python snippets that import the
  scripts.
- Environment for every Python command:
  `export PYTHON=$HOME/.cache/gororoba-quantum/ci-py3.14.7/bin/python GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1`.
  Then run `"$PYTHON" -m pytest -p no:cacheprovider -q PATH` and `"$PYTHON" scripts/NAME.py ...` from the working
  directory. `GOROROBA_WORKERS=1` keeps `gororoba_quantum/parallel.py` serial, so its spawn pool needs no
  semaphores.
- Ground every claim in a file and line, a command and its output, or a cited paper section. Mark each statement
  **verified** (you ran or read it) or **inferred** (reasoning without a check), and list every check you could not
  run, with the reason.

## Owner decisions already made

Review these for soundness, and do not reopen them as defects of process.

- Job-00 ran once under a single-use anchor-gate approval (2026-10-26 02:54 UTC, 2.2 credits, 0 samples, verdict
  `inconclusive`).
- On 2026-10-26 the owner chose to preregister job-01 at its own fresh platform read, not at job-00's 2026-10-24
  anchor read. Only the live `binding` gate admits job-01.
- The record watch's 0.86 is job-00's F* and serves as the trigger to read the record; job-01's admission is its own
  F*.

## Items

Work through them in order and record each item's findings in the report before starting the next.

1. **Plan and design.** Read `docs/state/plans/ascella-belenos-entanglement-teleportation.json` and these sections of
   `docs/design/ascella-belenos-entanglement-teleportation.md`: Claim levels, Protocol reference, Decision
   statistics, Single-chip rehearsal (job-00), Secondary analyses of job-00, Recovered-chip rehearsal (job-01).
   Check that the stated claim (C1 local conformance), the question and the falsifier match what the code tests.
2. **Physics of the instrument.** In `scripts/qd_network_protocol.py` and `scripts/qd_teleportation_rehearsal.py`,
   check:
   - the postselected Ralph CNOT taken from `pcvl.catalog['postprocessed cnot']` and its vacuum heralds;
   - the partial Bell analyzer, the frame table (1100/0011 give (1,0); 1001/0110 give (1,1)) and `decode_bit`;
   - the acceptance rule;
   - the ideal acceptance of 1/18 and conditional fidelity 1.

   Confirm by running the tests or a snippet. Say whether accepted events can include a failed CNOT branch, and
   whether threshold detection, multi-photon terms or the three-click filter bias the pooled fidelity.
3. **Noise model and its omissions.** Check `photon_distribution`, `detected_clicks`, `detection_efficiency`,
   `variants` and `derive`. Is F* (the floor of the lowest pooled fidelity of three variants) conservative for what
   the model omits, as the design lists it (multi-photon distinguishability beyond pairwise HOM, compilation phase
   error, dark counts)? Does the 0.02 allowance cover those terms? Give magnitudes where you can.
4. **Classical bound.** Check `scripts/qd_classical_benchmark.py` (the PPT Choi-cone program, `attempts_benchmark`)
   and how the rehearsal uses it: the larger of the bound at the reported shots and at the modeled attempts.
   Re-derive B = 0.6937 and the 2/3 limit. Is the modeled-attempts substitution sound when the service reports shots
   equal to samples?
5. **Decision rule.** Check `hoeffding_radius`, `bernoulli_decision_count`, the verdicts `beats-classical`,
   `at-or-below-classical` and `inconclusive`, and their treatment of partial and silent inputs. Re-derive the 314
   accepted outcomes at alpha 0.01 and beta 0.10. Is pooling six inputs with unequal acceptance under one Hoeffding
   radius valid (independence, the per-input weights)?
6. **Job-00 retained evidence.** Read `results/quandela/cases/teleportation_rehearsal/job-00/` and
   `results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/`. Replay both analyses
   offline. Check the registry claim `qd-belenos-teleportation-rehearsal-job-00` in
   `docs/state/research_state.json` against the run. Check the billing rule (1 + largest `max_shots` * 1e-6) against
   `docs/runbooks/quandela-credit-optimization.md` and the run's billing record.
7. **Job-01 machinery.** Read `git diff origin/main...HEAD`, the commits of #560. Check:
   - the `Request`/`Job` threading, and any remaining path where job-01 would silently use job-00's layout, seeds,
     anchor, directory or derivation (`grep -n "LAYOUT\|COMPILATION_SEEDS\|ANCHOR_READ\|job-00"`);
   - `--prepare`: its staging of the estimate, its resumability, the no-power refusal and the `max_duration`
     refusal;
   - `expected_seconds`, which reproduces job-00's 120 s;
   - the own-anchor refusal of `--anchor`;
   - the printed `REQUESTS`/`JOBS` rows;
   - the secondary module.

   Run `tests/scripts/test_qd_teleportation_rehearsal.py`, `test_qd_rehearsal_secondary.py` and
   `test_qd_record_watch.py`.
8. **Preregistration at the case's own read.** Judge the statistics:
   - Is deriving F*, the allowance and the budget from the same calibration read that the live gate checks sound?
   - Does a gate at F* computed from the very figures it tests carry information?
   - What does drift between `--prepare` and `--submit` do?
   - Is the feasibility table in `docs/archive/handoffs/belenos-recovery-watch.md` (F* 0.77 fits 300 s; 0.76 needs
     420 s) right?
   - Should job-01 raise `max_duration`, or split into several jobs, rather than refuse?
9. **Seeds.**
   - `JOB_01_COMPILATION_SEEDS` from `docs/evidence/outshift_qrng/draw-2026-10-26T204106Z.json`: check them against
     `docs/notes/qrng/README.md` (source order) and `docs/evidence/qrng_seeds/allocations.json`.
   - `qd_rehearsal_secondary.CONTROL_SEED` (64095), which job-01's exploratory lens would reuse: is that a
     reproduction seed (the same null tables by name) or new randomness that needs a draw? Say which, and why.
10. **What the owner receives and what can go wrong on submission day.** Read
    `.github/workflows/quandela-record-watch.yml`, `scripts/qd_record_watch.py` and the handoff.
    - Walk the six-step procedure of the design's job-01 section as the operator would on 2026-10-29.
    - Name every failure point: estimate None, a changed layout, a plan refusal, body-digest drift, the record
      changing between prepare and submit, a job cut off at `max_duration` and billed in full, and a partial result.
    - Say whether any path submits without the owner's approval or reads a credential.

## Report

The report holds:
- a summary verdict: is job-01, as built, ready to prepare on 2026-10-29, and what blocks it;
- one section per item;
- findings ranked P0, P1, P2:
  - P0: would submit wrongly, waste credits, or support an invalid claim;
  - P1: a defect reachable through a documented interface;
  - P2: clarity or documentation.

Each finding gives its severity, `file:line`, the evidence (command and output, or a source line), whether it is
verified or inferred, and the smallest fix. End with the list of checks not run.

## Done

The goal is done when the report covers all ten items and every finding carries evidence. Before you mark the goal
complete, audit the report against this item list.
