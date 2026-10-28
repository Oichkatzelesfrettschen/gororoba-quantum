# Retention bookkeeping bound per record

A retained QPU run must stay lossless, accounted and findable: its raw archive keeps every shot, its charge
reconciles against the instance's usage window, and the registry names it. Each of those properties is a fact
about one job, so each binding that proves it names that job. The bindings below instead name the sha256 of a
whole aggregate file, so appending one job invalidates every earlier proof that cites the file, and each
retention rewrites successor evidence about jobs it never touched.

## Measured cost

Retaining the two primary-instance jobs of 2026-10-27 (#618) inserted 64,640 lines across 24 files in 12
commits:

| Artifact | Lines | Why it moved |
|---|---|---|
| `docs/evidence/algebra-device-conjectures-11/` | 40,834 | the selected claim `hw-ghost-calibration-replay` binds the whole primary audit, so a new job changed the claim and the bundle refroze; main moved under it once, so it froze twice |
| `docs/evidence/submitted_circuits/comparison-qpy18-full-retrieval.json` | 2,323 | `compare_submitted_circuits.py` binds the audit's and its own sha256 and requires one file naming exactly the audit's jobs, so every retention writes a full successor |
| `docs/evidence/calibration/history/ibm_kingston/*.json` | 20,996 | `ghost_calibrations.py` indexes exactly the audited jobs, each with the full 156-qubit properties of its execution calibration |
| registry, audit, inventory, views, plans | about 500 | the facts the retention adds |

October 2026 carries 57 commits on the comparison successors and the algebra-device bundles, 26 comparison files
(2.4 MB) and 10 bundles (about 1.5 MB each). A retention also pays wall time: on the build host the offline audit
check verifies all 3.0 GB of raw archives in 156 s (35 s on the hosted runner, nightly tier), the registry
check takes 24.6 s (5.2 s hosted), and the inventory read takes 37 s on the backup instance and 50 s on the
primary.

## Invariants and what proves each

1. **Every audited job has a compared submitted program.** `--check` already re-derives each job's expected QPY
   digests from the retained `isa.qpy` and requires the rows to name exactly the audit's jobs. The audit's
   whole-file digest and the script's own digest add no check; they only force a successor.
2. **A claim's evidence is the jobs it cites.** `hw-charge-prediction-residuals` cites 5 acquisitions (8 audit
   jobs) and `hw-ghost-calibration-replay` 27 acquisitions (35 jobs). A job outside those sets changes nothing the
   claims state.
3. **A frozen bundle replays its sources.** The bundle re-derives every acquisition's facts through the provider
   adapters; its sources come from the selected claims' evidence, so they inherit the claims' granularity.
4. **A raw archive's denominators are a function of its bytes.** Each archive carries an index of sha256s, so an
   archive whose index digest is unchanged needs no re-verification.

## Changes

| Lever | Change | Effect | Falsifier |
|---|---|---|---|
| Per-record registry evidence | `research_state.py` accepts `FILE.json#COLLECTION/FIELD=VALUE` evidence, digested by `plan_records.evidence_digest` (the plan tracker's receipt rule); the two audit claims bind their jobs' audit rows | an appended job leaves both claims unchanged | a retention that edits either claim |
| Per-record bundle sources | `algebra_device_conjectures.py` records and verifies a `#` source by the same rule; one successor bundle freezes under it | no bundle refreeze per retention | a retention that stales the bundle |
| Per-job comparison rows | one immutable row file per job under `jobs/qiskit-<release>/`; `--append` retrieves only jobs without a row; `--check-rows` re-derives every audited job (#625) | one small file per new job instead of a 2,300-line successor | a retention that rewrites an existing row |
| Audit verification speed | each shot string's `re.fullmatch` (167 million calls, nearly all of the check's time) becomes one translate over the joined register, and the per-archive verification runs through `parallel.ordered_map` | 156 s to 12 s on the build host; every audit row byte-identical, only `replay_source_sha256` moves | an audit row that differs between the serial and pooled paths |
| Registry check | the views compute the acquisition rows once instead of three times | 31.7 s to 17.5 s at one load | a rendered view that differs |
| One retention command | `scripts/retain_run.sh RUN ID FAMILY QUESTION` chains the seed rows, inventory read, audit, comparison rows, ghost index, acquisition (`research_state.py --add-acquisition`) and views; `research_state.py --check` fails while an audit lists a run awaiting observation | the registry step can no longer be skipped (Codex P1 on #614); 69 s end to end on the backup instance at load average 30 | a retained run on main whose audit still awaits observation |

Retained successors keep their bytes; each change applies from its merge onward. Two self-bindings remain and no
longer ripple: each audit records its producer's sha256 and the bundle result its producer's, but the claims, the
bundle sources and the comparison rows bind job records, so regenerating an audit after a producer edit changes
that one field and nothing downstream. A cache of verified archives was the first design for the audit speed; the
profile placed the cost in the per-shot match instead, so the audit verifies every archive on every run and keeps no
trust ledger. Two whole-file bindings stay open: plan receipts that bind a shared Markdown note flag its plans for
revalidation on any edit of the note, and the comparison's QPY digests follow the Qiskit release (35 of 684 retained
circuits serialize differently under 2.5.2 and 2.6.0 at one QPY format), so a Qiskit pin change refills the row
ledger. Calibration history keeps its
full snapshots, which are replay inputs rather than bindings; trimming them to the placed qubits is a separate
question for `ghost_calibrations.py`.
