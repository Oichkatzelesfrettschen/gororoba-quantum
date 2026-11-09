# Legacy branch mining

Fourteen legacy branches were compared with `origin/main` at `4b144ee81`
(2026-11-09) for content a squash merge hides: a branch whose commits entered
main as one squash differs from main only by later edits, so a plain
`git diff` cannot tell a later edit from a lost hunk.

## Method

For each branch B, every path in `git diff --name-only $(git merge-base origin/main B) B`
received one of four classes against `origin/main`.

- Identical: the blob at that path equals main's.
- Superseded: main holds the path with later edits. The check counted the
  lines B added over its merge base that main lacks, then located the main
  commit that rewrote the same content and compared function, test, field and
  key names.
- Deliberately removed: the path is absent on main and
  `git log --diff-filter=D -- PATH` names a deleting commit with a stated reason.
- Unique: content, record, finding or code present nowhere on main and never
  removed on purpose. `git log -S` and `git grep` on distinctive identifiers
  tested whether a unique hunk landed under another path.

`archive/k2-decompositions-w8-n16` and `archive/a5-k2-decompositions-w8-n16`
point at one commit (`3993396f0`) and share one row.

## Result

One item was unique: the checker `scripts/check_kernel_resource_policy_receipt.py`
that three retained receipts name and that exists on no main path. It is
retained as
[docs/evidence/archive_imports/check_kernel_resource_policy_receipt.py.txt](../../../evidence/archive_imports/check_kernel_resource_policy_receipt.py.txt)
(commit `76d3fa33e`). The copy carries a `.txt` suffix because a script under
`scripts/` enters the hypercomplex library inventory and the gate manifest,
and the checker replays only at its source commit `42b463afc`. Its sha256 is
`7fc58ced14e68254e964c1624bc016d3e069cb92b9605420a59c1363d07f2db2`, and no
pinned file names that prefix.

| Branch | Verdict | Evidence | Recommendation |
|---|---|---|---|
| `archive-local/successor-pre-squash` (3 commits, 8 files) | Superseded | The carryover weights by class sizes at the pooled reader P1 are `b6dd804f1`; the replicate generator, arms and CLI are `e244f4210`; `fit_gamma_rows`, `FitMemo`, `evaluate_rows` and `shape_bound_rows` all stand in `gororoba_quantum/msq_successor_null_batch.py`. Seeds 35417 and 39316 lie in `docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json` and the seed ledger. The four tests absent from main (`test_q_arm_plants_each_tolerance_bound` and three collected/required-PUB tests) have rewritten successors in `tests/test_msq_successor_null.py` and `tests/test_msq_successor_analysis.py` after the analysis moved carryover reading into the predecessor circuit (`619cd7c62`, `accc99d93`). `libraries.json` is a regenerated artifact. | Safe to delete. |
| `archive/a5-k2-decompositions-w8-n16` and `archive/k2-decompositions-w8-n16` (19 commits, 289 files) | Superseded, with 235 MB of bytes held only here | 265 files are identical. The 14 differing files are earlier revisions of the A_5 ledger, arc scripts, rulebook and READMEs; every ledger row id of the branch is on main (243 rows against 174) and the 33 rows whose text differs carry newer status. Ten table files under `docs/evidence/a5-exceptional-fibers/working/exports/w8nm-n16-rcpt/` (`qB`, `qM1` to `qM7`, `s`; 235 MB) were removed on purpose by `18a222da1` ("The 235 MB of tables pushed the tests job's checkout past its time limit"); main keeps the manifest, the producing scripts and every sha256, and the README gives the regeneration command. | Keep until the W8 N = 16 export has been regenerated once and matched to the recorded sha256 values, because these branches hold the only copy of the tables. Restoring them to the tree is excluded by `18a222da1`. |
| `archive/ci-pr-tier-only-nightly-full` (1 commit, 6 files) | Deliberately removed | `ci.yml`, `ci/full_gate_inputs.json` and `ci/gate_timings.json` were deleted by `5d9c588d5` (#732): "the owner removed the scheduled audit", pull requests run every gate of `ci/gates.json`, replays moved to `ci/replays.json`. The branch's pr-tier-only rule describes the deleted nightly split. `docs/notes/build_host/ci-runtime.md` moved by `a45858510`. | Safe to delete. |
| `archive/codex-qpu-job-retention-reconciliation` (10 commits, 23 files) | Partly unique; integrated | Nine receipt files are identical. `reconcile_qpu_inventory.py` has `window_charge` and `timestamp` on main (later revisions `9fad1a148`, `d068af1fc`). `inventory_retained_runs.py` is on main at a later revision, and its inventory output is `docs/evidence/archive_imports/retained-run-channel-inventory.json`. `ci/check_run_gates.py` was removed by `1c622260e` (contracts moved into a pytest suite). The half-CPU default for `ci/run_gates.py` was reworked in `f24598d6f`. The ripple measured payloads are re-rendered later. Integrated: the receipt checker (see Result). | Safe to delete after commit `76d3fa33e` merges. |
| `archive/docs/quandela-validation-evidence-retention` (14 commits, 351 files) | Superseded | 346 files are identical. The branch entered main as the squash `e562d8beb` (#370). The remaining differences are gate `core-654` (present on main with later text), `libraries.json` (regenerated), `.gitattributes` and the `docs/README.md` map. `ci/full_gate_inputs.json` was removed by `5d9c588d5`. | Safe to delete. |
| `archive/heron-citations-pre-rebase` (1 commit, 3 files) | Superseded | Main holds the corrected citations in `docs/notes/heron_spatial_multiprogramming.md` and `gororoba_quantum/heron_multiprogramming.py` (Shokrian-Zini, Isaksen, Gavinsky-Roetteler-Roland, van der Vaart and Wellner Proposition A.6.6), the Hahn refusal in `steane_z_syndrome_patch`, and the Hahn test in `tests/gororoba_quantum/test_heron_multiprogramming_contracts.py` (the old `gororoba_quantum/test_heron_multiprogramming.py` moved there in `66be77fdc`). Main later added the `quadrature` and keyword-only `alphabet_size` interfaces. | Safe to delete. |
| `archive/kaggle-aer-runner` (14 commits, 150 files) | Superseded | 114 files are identical, including the substrate-probe run directories under `results/kaggle/`. The Design C result on the branch is the earlier run that `c4f6cad18` replaced with the run that passed the stack proof. `docs/notes/kaggle_gpu_simulation.md`, deleted by `8f8e17c09`, is replaced by `docs/notes/kaggle/`. The captured Kaggle site pages, runner, kernel and calibration snapshot are later revisions on main. `RESEARCH_STATE.md` was replaced by `research_state.json` (`6a77bfb38`). | Safe to delete. |
| `archive/n21-orbit-rca-window-unitary-model` (2 commits, 1 file; a stash) | Superseded | The optional `window` unitary and the `cphase_one` parameter in `distribution()` landed as `62cd34c18` and stand in `scripts/n21_orbit_rca.py`. | Safe to delete. |
| `archive/n21-window-bracket-refreshed-case` (1 commit, 4 files) | Superseded | Three files are identical. `UNAPPROVED_CASE.md` is the version before `f56feb1b7` withdrew its submit command: the dry run was retired because its cost carried the 20 us classical-latency allowance the planner no longer applies. Restoring the approval-only template would reopen a retired submission. | Safe to delete. |
| `archive/qpu-campaign-execution-evidence` (1 commit, 23 files) | Superseded | 22 files are identical. `results/live/qpu-coordination.json` is the 2026-10-12T17:55Z revision; main holds the settled ledger from `d378de6a6`, `f38ef86e6` and `0792f01f7`. The campaign narrative is already retained under `docs/evidence/archive_imports/README.md`. | Safe to delete. |
| `archive/readout-acquisition-validation` (1 commit, 2 files) | Fully on main | `test_killed_raw_collector_releases_lock_and_recovers` and the design paragraph on the abrupt collector exit stand in `tests/scripts/test_readout_sparse_receipt.py` and `docs/design/readout-information-context-and-budget.md`. | Safe to delete. |
| `archive/tuna-bipartite-walsh-and-lcu-packing` (1 commit, 1 file) | Fully on main | The one file is identical. | Safe to delete. |
| `archive/tuna-zz-map` (2 commits, 1128 files) | Superseded | 832 files are identical. 278 `batch-*/cases.json` files differ only in three digest fields (`catalogue_sha256`, `proposal_builder_sha256`, `qi_platform_source_sha256`), because main regenerated the Tuna-17 and QX proposals (`61bdf48ca`, `d1c701ac9`, `7eb25f6a6`). `qi_zero_divisor_secondary.py` bound its inputs by revision on the branch; main binds by sha256 alone (`c4d265277`). The pause constants and the 16,560 s figure are in `docs/notes/quantum_inspire/tuna_zz_map.md` and `qi_platform.py` (`b3a250745` changed the pacing). The reconciliation handback differs from main by one link to the removed `RESEARCH_STATE.md` (`6a77bfb38`). | Safe to delete. |

## Residual risk

The line-level comparison counts lines, so a hunk that main reworded rather
than dropped shows as missing; each such hunk above was resolved by the named
main commit or by name checks of the functions, tests and fields it carried.
The Kaggle site captures and the Design C result were judged by commit
history, not by a byte-level replay of the later runs.
