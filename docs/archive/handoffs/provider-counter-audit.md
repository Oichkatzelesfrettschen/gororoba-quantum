# Provider-counter audit handoff

This handoff carries the provider-counter audit from its merged contract and reconciliation to plan closure. It is
written for a reader who has not seen the session that produced it. The plan record
[provider-counter-audit.json](../../state/plans/provider-counter-audit.json) owns the work status. The evidence
bundle [provider-counter-audit/README.md](../../evidence/provider-counter-audit/README.md) owns the counter
contract, the classification of every consumer that turns a counter into a scientific result, and the claim
reconciliation table. The code contract is
[provider_counters.py](../../../gororoba_quantum/provider_counters.py). Main stood at `707ea38` when this handoff
was written (2026-10-27 23:30 UTC).

## Merged

| PR | Merge | Content |
|---|---|---|
| #605 | `3d993ee` | `provider_counters.py`; 13 contract tests and 3 audit-marked replays; the Quandela counter table (81 runs), the gate-model census (392 Quantum Inspire results, 776 IQM circuits, 59 IBM jobs) and the exposure sensitivity of every retained dark subtraction, each replaying a frozen inventory taken from main at `d333878` |
| #606 | `8c70375` | `DECISION_CASES` confines the teleportation decision rule (`beats-classical` against `attempts_benchmark`) to job-00; job-00's analysis replays `inconclusive` |
| #608 | `d1a1bbb` | Boundaries of `qd-belenos-random-meshes-no-class-fits-under-receipt-model`, `qd-belenos-q1-leak-needs-single-job-and-large-budget` and `qd-belenos-q1-leak-single-job-form-whatever-seed` qualified, each citing the audit README |

The five-experiment branch `feature/quantum-experiment-conformance` merged as #602 (`000eca9`, 2026-10-27
23:03 UTC). Its Quandela adapter in `scripts/experiment_analysis.py` treats `nb_shots_used` as provider detection
events and reports `accepted_vs_detected_fraction`, which the audit's contract supports; it does not import
`provider_counters`. No pull request of this program is open, and no other session holds work this program needs.

## Plan steps

| Step | State | Remaining |
|---|---|---|
| `freeze-and-inventory` | done | none |
| `counter-contract` | done | none |
| `exposure-sensitivity` | done | none |
| `teleportation-benchmark-repair` | done | none |
| `claim-boundaries` | done | its acceptance text names `exposure_sensitivity.json` as the citation, while the claims cite the audit README; task D2 reconciles the obligation |
| `collection-boundaries` | doing | tasks C0 to C7 |
| `review-and-merge` | todo | task D3 |

The plan's `reconciliation.status` reads `unresolved` and stays so until task D4 closes the plan.

## Executable now: collection boundaries

The step's obligation: new Quandela records carry counter semantics and iteration scope, and retained raw bytes and
analyses keep their hashes. Four facts set its cost:

- **`qd_platform.collect` output.** It writes three counters at the top level of `results.json`:
  - `shots`, the provider's top-level value, which is the job-level `max_shots` request for an iterated job and the
    detection-event count for a single job;
  - `shots_used`, the sum of the iterations' `nb_shots_used`;
  - `samples`.

  A job that answered a provider `RuntimeError` is recorded with `partial: true` and `samples: 0`
  (`ascella-static-input-readiness` and five more).
- **Producers that consume the ambiguous `shots`.** `qd_box_kite_analysis.analyze` copies `collected.get("shots")`
  into every analysis record, so that field's population changes with the job form.
- **Producer digests bound elsewhere.** Retained records bind the digests of the producers this step would edit:

  | Producer | Retained records that bind its digest | Gates that run it |
  |---|---|---|
  | `scripts/qd_platform.py` | 10 records under `docs/evidence/quantum-experiment-conformance/` (validation, provenance, regeneration-route admission) | `core-502` |
  | `scripts/experiment_analysis.py` | 3 conformance plan receipts (`quarter-mass-amplification-conformance`, `sedenion-herald-conformance`, `dimension-six-transition-conformance`) and `validation-portable-operators.json` | `core-quantum-experiment-analysis` |
  | `scripts/qd_belenos_mesh.py` | `results/quandela/runs/ascella-mosaiq-update-order-retry/analysis.json` and 4 Kaggle submissions under `results/kaggle/` | `core-510`, `core-511`, `core-513` to `core-515`, `core-534` to `core-536` |
  | `scripts/qd_box_kite_analysis.py` | the same 4 Kaggle submissions | `core-508`, `core-537` |

  A change to one of these producers makes every gate that checks those bindings fail, until each binding record
  gets a successor receipt.
- **No retained run postdates the freeze.** No Quandela, Quantum Inspire, IQM or IBM run was retained after the
  frozen inventories (checked against main `707ea38`).

Task C0 chose between two designs, and C1 to C7 follow from it.

- **C0, design choice (decided: (a), by the owner on 2026-10-27).**
  - **(a) Derived view.** Add `provider_counters.quandela_record(results, job_body)`. It reads a collected
    `results.json` and the job body, and returns typed per-iteration and top-level counters. `qd_platform.py` and
    every analyzer keep their bytes, and records keep their verbatim fields, so no digest binding moves. The
    semantics then live in a reader rather than in the record.
  - **(b) Record field.** Add a `counters` block to new `results.json` files written by `qd_platform.collect`. The
    record then carries its own semantics, but the 10 conformance records and `core-502` need rebinding.

  The owner chose (a). The record keeps its provider bytes, and the plan obligation is met by the view and its
  tests.
- **C1.** Implement the chosen surface. In progress on branch `provider-counters/quandela-record-view` (worktree
  `~/worktrees/IBMQuantum/quandela-record-view`): `provider_counters.quandela_record(results, budgets)` takes
  `qd_platform.iteration_budgets(cases.json)` instead of parsing the job body, because the job body's job-level
  `max_shots` equals the largest per-iteration `max_shots` on every retained iterated job, and an audit-marked
  test checks that equality on all 81 inventoried runs.
  - Under (a): `quandela_record` returns one `IterationCounters` per counted iteration, using `quandela_iteration`
    with each iteration's `max_shots` and `max_samples` from the job body; `quandela_top_level_shots` with the job
    body's job-level `max_shots`; and an unavailable sample counter for an error payload or a partial answer.
  - Under (b): add the same structure as a JSON block in `collect`, and extend `run_facts` so it accepts records
    with and without the block.
- **C2.** Fixtures in `tests/gororoba_quantum/test_provider_counters.py`, each built from retained bytes:
  - an iterated job, mesh job-03;
  - a single job, Q1 box-kite job-04;
  - the one-iteration exception, mesh job-14, whose top-level shots are unavailable;
  - both caps reached, Ascella signed-coherence job-04;
  - shot-budget termination, the teleportation job-00;
  - an error payload, `ascella-static-input-readiness`;
  - a partial iterated job, `ascella-hypercomplex-order-pilot`.
- **C3.** Route the box-kite `shots` field. New `qd_box_kite_analysis` records name the top-level counter's
  population (`requested_cap` or `detection_event`). Under (a) the change goes into a successor analysis writer
  that leaves `analyze` untouched, because `core-508` and `core-537` replay retained analyses byte for byte.
- **C4.** Bring `experiment_analysis.analyze_qd` onto the contract: it computes `accepted_vs_detected_fraction`
  through `provider_counters.ratio`. On the gate-model path, rename `incident_shots=len(shots)` (line 518) to a
  returned-execution name. For a gate-model run that value counts circuit executions, so the population is right
  and only the name is wrong. Editing this file moves the bindings in the table above, so rebind those records in
  the same change.
- **C5.** Label `qd_belenos_mesh.analyze_run`'s dark apportionment (`duration x nb_shots_used` share) as the
  `job_duration` exposure scenario in any new analysis schema. Retained analyses keep their bytes, and every
  retained `dark_expected` stays 0.0 because of `capped_dark`.
- **C6.** Lanes and receipts:
  - run `sh ci/pr_checks.sh lint`, `types`, `tests` and `gates`;
  - run `tests -m audit tests/gororoba_quantum/test_provider_counters.py`;
  - run `scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries` when a new tracked `.py`
    appears;
  - append a `collection-boundaries` receipt at the merged revision.
- **C7.** Rerun the three audit replays with `--check`. Any README edit makes the `freeze-and-inventory` and
  `teleportation-benchmark-repair` receipts stale, because both bind the README, so append a revalidation receipt
  to each.

## Executable now: coverage the pasted program asked for and the audit has not yet done

- **G1.** Semgrep and `ast-grep` sweeps for counter arithmetic outside the inventoried consumers. Look for divisions
  or sums over `shots`, `nb_shots_used`, `samples`, `physical_perf`, `duration` and `shots_used` across `scripts/`,
  `gororoba_quantum/` and `docs/evidence/**/*.py`. Both tools are installed (`/usr/bin/semgrep`,
  `~/.local/bin/ast-grep`). Retain the rules and their findings in the evidence bundle, and classify every new hit
  in the sink table.
- **G2.** `results/hypercomplex/` (Belenos repeat readout and compilation-measurement audits, from
  `scripts/photonic_repeat_readout.py`). These read `nb_shots_used` and `physical_perf` as `reported_shots` and
  `reported_physical_perf`. Their runs are in the frozen Quandela inventory, but the analyses are not in the sink
  table. Classify them; the registered claim already conditions on "reported total occupation one".
- **G3.** Simulator outputs: `results/kaggle/`, `results/local_compute/` and `results/local-simulation/`. A
  simulated shot is one sampled execution, so a census extension like the IBM one is expected to classify them as
  supported. Run it rather than assume it.
- **G4.** Providers with no retained executions: Open Quantum (`results/open_quantum/proposals/` only), IonQ,
  BlueQubit, Quafu and Origin Quantum. Record "no executed result" for each in the README provider list, with the
  checked paths.

## Closure tasks

- **D1.** After C7, update the README reconciliation table for any consumer that C1 to C5 changed.
- **D2.** Reconcile the `claim-boundaries` obligation.
  - Its acceptance reads "each named claim cites `docs/evidence/provider-counter-audit/exposure_sensitivity.json`".
    The merged claims cite the audit README instead, which is the record of all three corrections; only the
    random-meshes correction rests on retained `dark_expected` values, not on the sensitivity replay.
  - Patch the step's acceptance to "each named claim cites the provider-counter audit README". A changed obligation
    invalidates every receipt bound to it: `plan_records.check_receipts` requires each receipt's `scope_sha256` to
    match the current obligation, not only the newest receipt's. Follow the changed-obligation procedure of
    [plan-tracker.md](../../runbooks/plan-tracker.md): reopen the step, remove its old receipts from the record
    (Git history keeps them), reassess, and attach one receipt over the three registry records
    (`docs/state/research_state.json#claims/id=...`) under the new obligation.
- **D3.** Give `review-and-merge` a receipt that lists #605, #606, #608 and the collection PR with their merge
  commits.
- **D4.** Close the plan: disposition `completed`, a plan receipt binding `plan_records.obligation(plan)`, and
  `reconciliation.status` set to `verified`. Keep the open provider questions below as named limitations in the
  README.

## Waiting on others

Nothing in C0 to D4 waits on a provider, a job or another session. Only C0 waits on the owner's decision. The
limitations below wait on Quandela and change no task above:

- what `nb_shots_used` counts in a sample-limited QPU iteration under `min_detected_photons` above 1 (no retained
  run exercises it);
- what `physical_perf` measures on a QPU;
- whether acquisition is pulse-gated, and the exposure a catalogue dark rate multiplies;
- the source-trigger count of an iteration.

[Perceval issue 798](https://github.com/Quandela/Perceval/issues/798) carries the result-contract questions and had
no reply as of 2026-10-26. A question sent to Quandela is an outward action that needs the owner's approval.

## Procedure facts

- **Receipts that bind the README.** `freeze-and-inventory` and `teleportation-benchmark-repair` both bind
  `docs/evidence/provider-counter-audit/README.md`. A README edit makes the plan check report them stale; append a
  revalidation receipt with `plan_tracker.py step ID STEP --receipt FILE`.
- **Merging main.** It conflicts on the generated views `docs/state/plans.md` and `docs/state/plan-catalogue.md`,
  and on `docs/state/hypercomplex-libraries/libraries.json` when both sides add Python files. Take either copy of a
  generated file, regenerate it with `plan_tracker.py render --write` or
  `hypercomplex_libraries.py --out docs/state/hypercomplex-libraries`, then commit. A conflict in a plan record
  under `docs/state/plans/` is different: the JSON is the authority, so reconcile it field by field (scope, steps,
  states, acceptance, notes and both sides' receipts), as the root guide's planning rules require. Taking one side
  wholesale and re-recording receipts discards the other side's obligation changes.
- **Seed-provenance timing.** At host load average above about 9, `tests/ci/test_seed_provenance.py` exceeds its
  10 s test budget locally. The hosted `tests` job passed it on every head of #605 and #608.
- **Codex reviews.**
  - A round can stall at Running: one did on #605 for 25 minutes. Re-request with an `@codex review` comment.
  - A round runs only on a head whose `mergeable_state` is not dirty, and the same holds for the `pr.yml` checks;
    merge main first.
- **Pool rule.** Codex enforces the repository's pool rule on evidence scripts too. Every loop over independent
  runs goes through `parallel.ordered_map(..., min_items=1)`; the default floor of 64 items runs short lists
  serially.
