# Audit: tools/kaggle-aer-runner (adb795d) vs main and kaggle/substrate-routing-libraries

Method: content, not subjects. Read-only. Scratch lists in the same directory (class.txt, files.txt, uniq_objs.txt).

Why `git diff main branch` is misleading: 1051 of its 1131 entries are deletions (230 commits of main the branch lacks), 78 modifications
are main's newer versions, 0 additions. The branch's own work is `git log --no-merges main..branch`: 13 wip commits touching 153 paths.

## Result by path (153 paths touched by the branch's non-merge commits)
- 129 paths: the branch tip blob is byte-identical to main's blob. These include all 95 results/kaggle files (substrate probes, T4/TPU
  probes, aer-gpu smoke, design-c run 2026-10-15T230733Z incl. submission.json, collect.json, kernel/run.py, output/), 31 docs/notes
  files (docs/notes/kaggle/cli, site, README, MANIFESTs), scripts/capture_kaggle_docs.py, scripts/algebra_package_tables.py, scripts/AGENTS.md. Class (c).
- 20 paths: tip blob differs from main's tip, but the tip blob exists in main/substrate history (git rev-list --objects). Main holds the
  same file evolved (class a). Branch-only lines are earlier wording, listed per file below.
- 4 paths: deleted on the branch tip (see "Not on main" below).
- Unique objects: `rev-list --objects main..branch` minus all objects reachable from main and origin/kaggle/substrate-routing-libraries =
  127 objects = 13 commits + trees + 37 blobs. All 37 blobs are intermediate revisions inside wip commits; each is superseded by a later
  branch blob that main carries, except the three listed under (b).

## Class (a), 20 files where main carries a superset or newer version
- docs/notes/kaggle/substrates.md, workflow.md: branch-only lines are the "GPU is the default / route <=14 qubits to Kaggle GPU" wording and
  a width-routing table with Kaggle L4/A100/H100 rows. Main replaced the routing with the CPU-default rule (AGENTS.md "Machine" section:
  CPU default, GPU only at 11+ qubit density matrices), measured T4/TPU rows and the --accelerator flag. Superseded by policy, not lost data;
  the L4/A100 "not measured/restricted" rows are unmeasured speculation.
- docs/evidence/design_c_cubic_noise/{README.md,result.json,kaggle_environment.json}: branch = the 2026-10-15T230733Z run (calibration
  15:29:07, no hypercomplex stack proof). Main = run 2026-10-16T033027Z (kernel v3, calibration 19:42:21, stack proof, commit c4f6cad
  "replace the Design C result with the run that passed the stack proof"). Branch result.json sha256 0425267605... equals the retained
  main file results/kaggle/2026-10-15T230733Z-.../output/output/repo/results/kaggle_out/design_c_cubic_noise.json, so the old numbers are
  retained byte-for-byte in main's results/kaggle.
- docs/evidence/calibration/ibm_kingston.json: branch holds the 15:29:07 export without `reset`; main holds 19:42:21 with `reset`
  (commit ef9a761 "keep reset in snapshots"). The 15:29 blob is in main history (8f8e17c / c4f6cad era) and its digest is bound in the
  retained 230733Z submission.json.
- gororoba_quantum/calibration_snapshot.py, kaggle_kernel/kernel_main.py, kaggle_kernel/AGENTS.md, scripts/kaggle_run.py,
  scripts/design_c_cubic_noise.py: branch-only lines are the first-generation GPU-only runner (KERNEL_PINS, DEFAULT_MACHINE, hard-wired
  GOROROBA_AER_DEVICE=GPU, bundle self-test, `noise_simulator(snapshot, device)` without method/batched_shots, CPU replay of GPU result).
  Main's versions add accelerator selection, --ci-env, method="density_matrix"|"statevector", restrict_circuit, version-bound collect,
  shards, quota/timeout rules. Spot check of the branch-only lines found no function or option absent from main.
  The "barrier-kept factorized blocks" change (05a85b4) is in main via scripts/associator_cubic_normal_form.py `factorized_blocks`
  (imported by main's design_c_cubic_noise.py), not as a literal "barrier" token in the entry.
- .gitattributes, .gitignore, ci/gates.json, AGENTS.md, gororoba_quantum/AGENTS.md, README.md, docs/RESEARCH_ROADMAP.md,
  docs/state/{research_state.json,RESEARCH_STATE.md}: pure staleness. Branch lacks main's later lines (SDK_KEY.md and .kaggle-shards
  ignores, Reality Ripple -text rules, gates core-284.. and 289, QI sections, provider fields). Branch-only lines are older wording of
  sections main rewrote.
- kaggle/substrate-routing-libraries (PR #148) was compared at the same blobs; it supplies none of the branch-only lines either.
  `git grep` on main finds the distinctive phrases of the dropped note (Census-frequency witness, P100, v5e-8, numerical or stochastic
  simulation, kaggle.com/mcp, OAuth) in 2 to 4 files each.

## Class (b), bytes in no ref other than the branch
1. docs/notes/kaggle_gpu_simulation.md (blob c1e655a, 86 lines, last at f291dce). Deleted by the branch's own commit 17c7fc4 and by
   main's 8f8e17c. Its content (accelerators, Aer GPU wheel choice, 16*4^n density-matrix sizing, candidate-design table, workflow,
   retained-notebooks pointer) was folded into docs/notes/kaggle/{substrates,workflow}.md and AGENTS.md. Only the "Which designs need it"
   candidate table (Census-frequency, Signed kernel probe, Walk scaffold, Detuning map) is matched in a single main file (count 1 for
   "Detuning map designs"); the sizing table is present. Residual loss: wording only.
2. results/kaggle/2026-10-15T230436Z-gororoba-design-c-cubic-noise/{submission.json, kernel/run.py} (blobs 1a2248f, d3ae682;
   kernel-metadata.json blob is in history). A superseded push (git_commit 07ca961-dirty, pre-factorized-fix entry, calibration_snapshot
   digest 970fdaa...) with no collect.json and no output. Replaced three minutes later by 230733Z, which main retains. Bytes of no evidential
   weight.
3. Intermediate blobs of wip commits (e.g. results/kaggle/2026-10-15T225852Z-gororoba-aer-gpu-smoke/collect.json earlier revision,
   intermediate AGENTS.md, ci/gates.json, substrates.md, workflow.md, kaggle_run.py, design_c_cubic_noise.py, capture_kaggle_docs.py,
   kernel_main.py revisions). Each is overwritten by the branch tip, which is class (a) or (c).

## Not run
No file-by-file semantic diff of every one of the ~800 branch-only lines in the 20 class (a) files; coverage is the line-set test
(branch lines absent from main) read in full for substrates.md, workflow.md, design_c README, calibration_snapshot.py, kernel_main.py,
design_c_cubic_noise.py, kaggle_run.py, plus the diffs of .gitattributes, .gitignore, ci/gates.json, ibm_kingston.json,
kaggle_environment.json. AGENTS.md, README.md, RESEARCH_ROADMAP, RESEARCH_STATE, gororoba_quantum/AGENTS.md were judged stale by
size of absent_main counts (98, 36, 24, 45, 20 lines) and not read line by line.
Confidence that nothing of value is lost: high (about 90 percent); a hand read of those five docs would raise it.

## Recommendation
Delete the branch and worktree. No named content needs rescue: every branch tip blob is byte-identical to main or exists in main history with
a newer successor, and the three unique leftovers are a deleted 86-line planning note folded into docs/notes/kaggle/, a superseded
uncollected kernel push, and intermediate wip revisions. If archive insurance is wanted for the wip history itself,
`git push origin tools/kaggle-aer-runner:archive/kaggle-aer-runner` first; it costs one ref and is not required for any content.
