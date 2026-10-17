# Quantum Inspire usage, limits and cost

## What the account is

One account type exists, free, with access to the hardware backends, the
emulator backends and storage for jobs and results (KB,
[managing-your-account](site/kbase_managing-your-account.md),
<https://www.quantum-inspire.com/kbase/managing-your-account/>). The API
shows one team marked `individual_user` with one active member of role
`member` (catalogue.json, which retains no team, member or user identifier
in any form, since a hash of a small integer id reverses by enumeration).

## Metered usage: the transaction ledger

The compute job manager keeps a ledger, `GET /transactions/`: each row
carries a `domain` (`compute`, `networking` or `simulate`), the `job`, the
team and member, a signed integer `change` (-32768 to 32767, unit undocumented)
and a timestamp (API schema, [api/openapi.json](api/openapi.json)).
`"$QI_PYTHON" scripts/qi_platform.py snapshot` writes it to
[usage.json](../../evidence/quantum_inspire/usage.json) aggregated by domain
and backend type, beside each job's requested and completed shots and the
execution seconds its results report.

Observed: the ledger held no row before the first job and still held none
after forty-two jobs on 2026-10-16 (QX, the Ry emulator and Tuna-17;
369664 shots completed, 285.9 s of reported execution; snapshot
2026-10-16T23:09Z). The account
therefore spends no metered seconds, credits or minutes as observed; the
`change` unit stays unmeasured until a row appears. Recheck with a fresh
snapshot before stating a quota: `qi_usage` on the MCP server returns the
same structure.

## Structural limits (per backend type, API)

| Limit | QX emulator | Ry emulator | Tuna-5 / Tuna-9 / Tuna-17 | Field |
|---|---|---|---|---|
| Qubits | 10 | 9 | 5 / 9 / 17 | `nqubits` |
| Default shots | 1024 | 1024 | 8192 | `default_number_of_shots` |
| Maximum shots per job | 2048 | 1024 | 131072 | `max_number_of_shots` |
| Execution time per job | 3600 s | 3600 s | 300 s | `job_execution_time_limit` |
| Jobs (circuits) per batch job | 5 | 5 | 5 | `max_jobs_per_batch_job` |
| Batch jobs per queue | 5 | 5 | 5 | `batchjobs_per_queue_limit` |
| Raw per-shot data | yes | yes | yes | `supports_raw_data` |

The general conditions state the same kinds of limit in prose: each backend
limits qubits, shots per request and execution time, and running executions
that exceed the time limit are aborted (KB,
[terms-and-conditions](site/terms-and-conditions.md),
<https://www.quantum-inspire.com/terms-and-conditions/>). The FAQ limits a
user to 3 jobs queued per hardware backend and warns that abuse removes the
account (<https://www.quantum-inspire.com/faq/>), stricter than the API's 5.

## Measured time per job and per shot

| Backend | Shots per job | Execution per job | Per shot | Source |
|---|---|---|---|---|
| Tuna-17 | 16384 | 9.87-12.57 s | 0.60-0.77 ms | runs/2026-10-16T211635Z-tuna_17/results.json |
| Tuna-17, 66-70 CZ witness | 16384 | 12.58-15.36 s | 0.77-0.94 ms | runs/2026-10-16T221133Z-zero_divisor_tuna_17 |
| Tuna-17, readout only | 16384 | 10.69-10.88 s | 0.65-0.66 ms | same run, readout-0 and readout-1 |
| QX emulator | 2048 | 0.028-0.289 s | 14-141 us | runs/2026-10-16T211635Z-QXsinglenodesimulator |
| QX emulator, two 5-qubit witnesses | 2048 | 0.81-10.39 s | 0.4-5.1 ms | runs/2026-10-16T221133Z-zero_divisor_qx |
| Ry emulator | 1024 | 16.26 s (2-qubit X-only diagnostic); a failed job with no shot also spent 16 s | at most 15.9 ms (a fixed per-job cost fits as well) | runs/2026-10-16T213823Z-Rydberg-diagnostic, runs/2026-10-16T211635Z-Rydberg |

A Tuna shot is dominated by the 500 us initialization (KB tuna page), so
the per-shot time barely depends on a short circuit's gates. Planning rule
for Tuna: execution seconds ~ shots x 0.7 ms; 131072 shots fit the 300 s
limit with room for circuits up to a few hundred microseconds. The KB quotes
30-90 s per typical hardware job including compilation and pulse upload, and
up to 15 minutes or more for a hybrid job.

Queue: a Tuna-17 batch submitted at 21:16:52 UTC started at 21:17:29 and
its five jobs ran back to back, each starting when the previous finished.
The `queue` statistics of a backend type report jobs waiting and min, mean
and max wait; for QX they reported 5.3-5.6 h while this account's QX jobs
started within seconds, so they describe other users' long jobs, not a wait
forecast.

## Calibration and maintenance

- Hardware backends retune automatically; a tuning program takes seconds to
  30 minutes and a job scheduled during it waits (KB faq,
  displaying-and-downloading-your-results). Tuna-17 read `calibrating`
  between two catalogue reads minutes apart (API status enum: offline, idle,
  executing, calibrating, benchmarking).
- No ledger row records calibration, so calibration costs the account
  nothing as observed; it costs queue time.
- Backends serve QuTech research and development as well, so they go
  offline for longer periods, announced on the website where possible;
  simulators stay available (KB faq, release-notes).
- QuTech may assign priority to particular jobs regardless of queue order,
  relay jobs to external computing providers, decline to execute or store an
  algorithm, and interrupt the service at any time (terms, item 6).

## Conditions that bind every submission

From the general conditions of use (6 Feb 2025,
<https://www.quantum-inspire.com/terms-and-conditions/>):

- Every algorithm, datum or code uploaded, stored or executed is open to use
  by QuTech for its own or public activities and may be disseminated to third
  parties under a free irrevocable license, unless agreed otherwise in
  writing before upload (item 14). Nothing confidential is submitted.
- Access is screened against international sanctions and export-control
  regulations.
- Third-party computing providers can gain access to relayed code (item 6c).

## Rules this repository adds

- A submission waits for the user's approval of a written case and goes
  through `scripts/qi_platform.py submit`, which records the approval text;
  the MCP `qi_submit_case` tool invokes the same guarded runner. The legacy
  raw-string `qi_submit` refuses execution and names this replacement.
- Before creating any remote resource, the runner reads the current user's
  queue with `user_only=true`. It refuses a batch that would exceed the API's
  `batchjobs_per_queue_limit`. On hardware it also refuses a batch of more
  than three circuits and any batch while one of the account's batches is
  still queued, so at most three jobs are queued whether the FAQ's "jobs"
  means batches or circuits. The receipt records that scoped queue and the
  applied limit. The queue count is in batches: the API endpoint names
  "(batch) job queue statistics", and both retained five-circuit Tuna-17
  receipts reported queue count 2 before their first child-job `queued_at`
  timestamps (21:16:52 versus 21:17:29, and 22:11:41 versus 22:11:56 UTC on
  2026-10-16; [first run](../../../results/quantum_inspire/runs/2026-10-16T211635Z-tuna_17/),
  [witness run](../../../results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17/)).
  This is an inference from the API and retained runs; the FAQ itself says
  "jobs" without distinguishing batches from their circuits, which is why the
  hardware rule bounds both. Those two five-circuit Tuna-17 batches predate
  the rule and held five queued circuits. Between hardware batches a series
  collects the previous batch, passes its sanity checks and pauses before
  submitting the next.
- The case directory acquires an exclusive `submission-state.json` before
  the client creates any remote resource. It checkpoints the batch and job
  IDs and the enqueue intent; either this state or `submission.json` blocks
  a repeat submission, including after a timeout or local write failure.
  `"$QI_PYTHON" scripts/qi_platform.py reconcile CASE_DIR` reads the recorded
  batch and jobs and recovers the receipt when the service confirms the
  complete batch was enqueued. Reconciliation never enqueues a planned
  batch, creates a resource or clears the submission guard. If creation was
  interrupted before its IDs were retained, its outcome remains unknown;
  inspect the account records without resubmitting the case.
  The checkpoint's candidate receipt has `state: created`; only an accepted
  enqueue response or successful read-only reconciliation sets
  `state: enqueued` and publishes the final receipt. A recovered `submitted_utc`
  records the local confirmation time when no earlier confirmation was
  retained; the job timestamps remain the execution chronology.
- Every run keeps its circuits, cases.json digests, submission.json,
  raw shots and results.json under results/quantum_inspire/runs/.
  New receipts use `qi-submission-v2` and carry `cases_sha256`, the SHA-256 of
  the exact manifest bytes checked before upload. That manifest binds each
  circuit digest to its submitted job, and each `jobs` entry also carries
  its uploaded circuit's `sha256`. Collection, reconciliation and the
  research-state check reject a missing or changed v2 digest, including an
  edit that changes a circuit and its manifest digest together. Historical
  `qi-submission-v1` receipts remain readable without changing their bytes;
  they predate this extra receipt binding.
- Collection compares all returned raw shots with the retained ordered
  lists before publishing new files. Identical recollection preserves the
  existing bytes and timestamps; a different order, histogram or retained
  result rejects the collection. An updated collection timestamp alone is
  ignored, so it does not rewrite a prior result or break its evidence hash.
- A simulation of 14 qubits or fewer runs on Kaggle (root AGENTS.md); a
  Quantum Inspire hardware run answers a question about the device.
