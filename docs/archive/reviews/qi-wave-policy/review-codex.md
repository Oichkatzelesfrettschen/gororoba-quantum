# Review of PR 881 head `088021c80`

Verdict: the policy table and bracket arithmetic are sound, but the wave safety, ordering, and six-pause execution claims are not established. The current written submission procedure does not submit waves.

## Findings, ranked by consequence

1. **FATAL to the claimed wave contract — queue and pause admission is a non-atomic snapshot.** `[proved/computed]`

   `scripts/qi_platform.py:778` counts in-flight batches only through nonterminal rows returned by `/jobs`; a non-`planned` batch with no returned job is absent from the count. The probe produced:

   ```text
   three-visible REFUSE ... 3 batches in flight
   third-batch-zero-jobs ADMIT (3, 0)
   old-planned-third ADMIT (3, 0)
   recent-planned-third REFUSE ... being planned
   finished-ten-seconds REFUSE ... wait 20 more seconds
   other-type-running REFUSE ... jobs finish
   ```

   A second probe gave `(3, 0)` when `/batch_jobs` reported `finished` but `/jobs` still reported `queued`. Thus inconsistent or changing endpoint snapshots can skip the pause.

   The queue count is read at `qi_platform.py:1006-1013`, hardware state at `:1014-1017`, remote resources are then created through `:1045-1119`, and enqueue occurs at `:1122` without another admission read. A batch can finish during that window and the new enqueue skips its newly applicable pause.

   `SUBMIT_LOCK` is a local `flock` beside the local token file (`qi_platform.py:132-137,199-209,920-941`). It serializes two processes sharing that file, but not another host, container, web client, or CLI. Two hosts can both observe two batches and enqueue a third and fourth; whether provider timing realizes that schedule is `[hypothesis]`, while the missing cross-host exclusion is `[proved]`.

   Remedy: scope the contract to snapshot-based admission, or add an account-wide distributed lease, count every non-`planned` batch fail-closed until its job membership is complete, and repeat admission immediately before enqueue. Exact enforcement ultimately needs provider-side atomic admission.

2. **SERIOUS — sequential enqueue does not prove platform execution order.** `[proved]`

   `hardware_admission` asserts that submission order keeps queue order (`qi_platform.py:839-843`), and `results/quantum_inspire/cases/pathion_one_cz_null_bracketed_tuna_17/CASE.md:38` relies on it for mirror cancellation.

   The provider terms expressly allow priority “without regard to the order of the queue” (`docs/notes/quantum_inspire/usage.md:195-197,212`). `_submit` knows one batch only and carries no wave ordinal into service scheduling.

   The analyzer records actual `queued_at` order but only reports it (`qi_pathion_one_cz_null_cases.py:1207-1219`); it does not reject a permutation before deciding. A real wave therefore needs an execution-order gate or an order-invariant analysis. The current one-batch-at-a-time wrapper does impose batch series order by waiting for collection, but that is not the claimed three-batch queue behavior.

3. **SERIOUS — the supplied commands incur 18 pauses, not 6.** `[proved]`

   `scripts/qi_pathion_one_cz_null_submit.sh:2` submits, collects, and sanity-checks each batch before submitting the next (`:33-60`). It explicitly keeps at most one batch queued (`:9-10`).

   CASE.md acknowledges that concurrent wave submission is an unwritten separate procedure (`:46-47`) but budgets six pauses at `:137-138` and invokes the serial wrapper at `:255-279`.

   Nineteen hardware batches have 18 intervening pauses: 540 seconds, not 180. The execution-only range of 1,521.0–1,675.8 seconds is correct; the supplied procedure totals 2,061.0–2,215.8 seconds plus queue time. Six pauses apply only to the unwritten seven-wave procedure.

4. **SLOPPY — user-facing platform documentation still states the legacy rule as universal.** `[proved]`

   `qi_platform.py:31-33`, `docs/notes/quantum_inspire/usage.md:243-263`, and `docs/notes/quantum_inspire/ry-emulator.md:42-45` say every unfinished hardware job refuses and at most one three-circuit batch queues. Those statements contradict `wave-v1`. The policy-specific description at `usage.md:72-108` is accurate.

## Claim dispositions

1. **Policy selection: confirmed.** `[computed/proved]` `hardware_policy` and `hardware_limits` at `qi_platform.py:761-775` implement the table and componentwise minimum. Both routes validate an unknown policy before constructing `Client` (`qi_platform.py:970-990`; deadline route `:103-123`). Valid legacy manifests retain the 3-circuit/1-batch path. Policy suite: `36 passed in 0.12s`.

2. **Wave admission: falsified as an absolute guarantee.** `[computed/proved]` Consistent snapshots correctly refuse a fourth batch, recent `planned` batches, recent finished jobs, and another hardware type’s unfinished job. Zero-job/stale snapshots, state transitions after the read, and cross-host sessions remain open as finding 1 describes.

3. **Single policy table: confirmed.** `[proved]` Both `_submit` implementations call `hardware_admission` (`qi_platform.py:1014-1017`; deadline route `:149-155`), and retention uses `hardware_limits` (`check_qi_platform_retention.py:223-245`). The requested constant grep found legacy generators and documents, but no other cap reached by these `wave-v1` manifests.

4. **Twin estimator: conditionally proved.** `[proved]` The identity `(P1-c)-(P0-c)=P1-P0` and independent-shot variance sum are implemented at `qi_pathion_one_cz_null_bracketed_cases.py:205-209` and in the analyzer at `qi_pathion_one_cz_null_analysis.py:258-268`. A coin-conditioned assignment channel, within-batch temporal change, or different twin contexts violates the shared-`c` premise; the case correctly retains these as residual risks at CASE.md:245-249.

5. **Layout arithmetic: counts confirmed; pause count rejected for the written procedure.** `[computed]` Direct manifest recount returned 19 batches, batch sizes `[3,4,4,3,3,4,4,3,3,4,4,3,3,4,4,3,3,3,2]`, 64 jobs, and 2,555,904 shots. `design()` returned 7 waves, 1,521.0–1,675.8 seconds, and 180 seconds of wave pauses. Finding 3 states why the command path instead takes 540 seconds of pauses.

6. **Operating-characteristic numbers: confirmed as simulation, not physical calibration.** `[computed/hypothesis]` The stored counts reproduce 0.8211/0.8687 under pair-common drift and 0.7249/0.7712 under independent contrast drift. A review resample using draw indices **900–910** gave ranges:

   ```text
   common:      dropout 0.8157–0.8240; superposition 0.8632–0.8717
   independent: dropout 0.7190–0.7319; superposition 0.7670–0.7780
   ```

   The threshold conclusions are seed-robust in this model. Which drift model governs hardware remains `[hypothesis]`, as CASE.md:209-212 states.

7. **QX layout: confirmed at expected counts only.** `[computed]` The generator produces four five-circuit batches in the stated order, and the focused suite validates ideal-count bracket arithmetic. A local qxelarator execution remains `not run`, as CASE.md:220-225 records.

## Layout-consumer audit

`git grep` found no active 27-batch consumer. CASE.md:106 is explicitly a rejected design; the test’s “27 simulations” means three drift tables across nine worlds.

- `docs/state` contains no bracketed-series entry.
- `ci/gates.json:6088-6095` replays the generated directories rather than hard-coding counts.
- `ci/runner_image_records.json:819-820` binds directory paths only.
- `toolchain-token-recovery.json` contains 64 Tuna circuits in batches 00–18 and 20 QX circuits in batches 00–03.

## Verification

- Focused suites: `36 passed`; `42 passed in 89.68s`.
- Full relevant replay command: all four record/generator comparisons passed byte-for-byte.
- `git diff --check`: passed.
- Pinned Ruff check/format and targeted mypy: passed.
- Worktree remained clean at `088021c80644a019a3ee9e7191a3243004641fd3`.
- No provider, credential, network, or cloud action ran.

