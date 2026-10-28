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

| Lever | Change | Predicted effect | Falsifier |
|---|---|---|---|
| Per-record registry evidence | `research_state.py` accepts `FILE.json#COLLECTION/FIELD=VALUE` evidence, digested by `plan_records.evidence_digest` (the plan tracker's receipt rule); the two audit claims bind their jobs' audit rows | an appended job leaves both claims unchanged | a retention that edits either claim |
| Per-record bundle sources | `algebra_device_conjectures.py` records and verifies a `#` source by the same rule; one successor bundle freezes under it | no bundle refreeze per retention | a retention that stales the bundle |
| Per-job comparison rows | the comparison becomes one immutable row file per job; `--write` retrieves and appends only missing jobs; `--check` re-derives every audited job | one small file per new job instead of a 2,300-line successor | a retention that rewrites an existing row |
| Incremental raw verification | the audit check skips archives whose index digest a verification ledger records; the nightly tier verifies everything | local audit check from 156 s to seconds | an audit written with the ledger that differs from one written without it |
| Registry check memoization | acquisition rows and provider facts computed once per process | 24.6 s to about 12 s locally | a rendered view that differs |
| One retention command | `scripts/retain_run.sh RUN` chains the seed rows, inventory read, audit, acquisition stub and views; a test fails a retained run without an acquisition | the registry step can no longer be skipped (Codex P1 on #614) | a retained run on main without an acquisition |

Retained successors keep their bytes; each change applies from its merge onward. Calibration history keeps its
full snapshots, which are replay inputs rather than bindings; trimming them to the placed qubits is a separate
question for `ghost_calibrations.py`.
