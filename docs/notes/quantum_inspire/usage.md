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
execution seconds its results report, and the sorted ids of the ledger jobs
that no run directory of the tree retains (`unretained`, schema
`qi-usage-v2`). The ledger covers the whole account, so jobs that another
branch's runs hold appear there and are declared by id; `research_state.py`
checks the retained jobs against their ledger rows and every other ledger
job against that list.

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

### Queue rules: the FAQ governs

The FAQ is the source of truth for how much this account may queue:

> You are not allowed to have more than 3 jobs in the queue for a hardware
> backend, in order to provide equal access opportunities for everybody.
> (Attempts of) abuse will lead to removal of your account.

(<https://www.quantum-inspire.com/faq/>, [capture](site/faq.md); the live
page read on 2026-10-24 carries the same sentence.) The API's
`max_jobs_per_batch_job` 5 and `batchjobs_per_queue_limit` 5 (per user and
backend type, [OpenAPI](api/openapi.json) schema `BackendType`) describe what
the service mechanically accepts, up to 25 queued circuits per backend type.
They grant no permission: no plan, case or batch size is derived from them
on hardware, and where the FAQ is silent they remain the ceiling the service
enforces.

The FAQ does not say whether a "job" is a batch or a circuit, so the runner
satisfies both readings at once. On every backend type the catalogue flags
`is_hardware`, `qi_platform.py submit`

- holds a batch to `HARDWARE_BATCH_CIRCUITS` (3) circuits;
- enqueues a batch only while the account has no batch queued on that type
  (`HARDWARE_QUEUED_BATCHES`, 1);
- refuses while any account job on a hardware type is unfinished or finished
  less than `HARDWARE_PAUSE_SECONDS` ago ([pause escalation](#pause-escalation)),
  whichever session submitted it.

At most three circuits of the account therefore wait for a hardware
backend, in one batch, and nothing else of the account is queued or running
on hardware meanwhile. The constants are fixed in the source, and
submission routes that bypass `submit` (`QIProvider` `backend.run`, which
batches up to the API's 5; the `qi` CLI; the web editor) carry no FAQ guard
and stay unused for runs.

| Backend | Quantum Inspire's classification | FAQ queue rule | Rule the runner applies | Procedure |
|---|---|---|---|---|
| Tuna-17 (type 7); Tuna-5 and Tuna-9 when online | hardware ([KB hardware backends](site/kbase_hardware-backends.md)) | at most 3 jobs queued | the hardware rules above | [Run on Tuna-17](#run-on-tuna-17) |
| Ry emulator (type 5) | emulator ([KB emulator backends](site/kbase_emulator-backends.md)); the API flags it `is_hardware` | none | the hardware rules above, a choice stricter than the FAQ, since the runner keys on the flag | [ry-emulator.md](ry-emulator.md#do-a-ry-emulator-run) |
| QX emulator (type 1) | emulator | none | the service's own ceilings: 5 circuits per batch, 5 queued batches; terms item 9 asks for syntax checking first | [qx-runs.md](qx-runs.md#do-a-qx-dry-run-remote-emulator) |

[Rules this repository adds](#rules-this-repository-adds) holds the evidence
that the API's queue count is in batches.

### Run on Tuna-17

A Tuna-17 run answers a question about the device itself; a simulation of
14 qubits or fewer runs on Kaggle (root AGENTS.md, "QPU time and
calibration"). Every step below is a repository command; the approval steps
follow root AGENTS.md "Hardware services".

1. Generate the cases with the experiment's generator, which emits
   `batch-NN/` directories of at most 3 circuits each, and run its `--check`
   and `"$QI_PYTHON" scripts/qi_toolchain_check.py` (libqasm analysis and
   compilation with the Tuna-17 compiler configuration).
2. Run the QX dry run of the same cases ([qx-runs.md](qx-runs.md#do-a-qx-dry-run-remote-emulator))
   and analyze it against the stated noiseless outcome.
3. Write the case: the question, why Aer cannot answer it, the qubits and
   couplers used (the excluded qubits of [experiments.md](experiments.md)
   named), the batch list, shots per circuit (at most 131072; execution
   about 2.6 s per job plus 0.53 ms per shot against the 300 s limit) and
   the series duration including one pause per batch. Wait for the owner's
   approval and quote it verbatim.
4. Read the device and the account: MCP `qi_backend` for type 7,
   `qi_hardware_status` and `qi_jobs` (or `qi_platform.py snapshot --out DIR`
   with DIR outside `docs/`). Proceed only while Tuna-17 is online and none
   of the account's hardware batches is queued or running.
5. For each batch in order: copy it to
   `results/quantum_inspire/runs/<UTC stamp>-<case>-batch-NN/`, then
   `"$QI_PYTHON" scripts/qi_platform.py submit RUN_DIR --backend-type-id 7 --approval "QUOTE"`,
   `"$QI_PYTHON" scripts/qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`
   and the generator's `--sanity RUN_DIR`. The next batch goes in only after
   that collection, its sanity checks and the pause; `submit` refuses an
   early one before any remote write and names the seconds left.
6. Stop the series at the first platform failure, raise
   `QI_HARDWARE_PAUSE_SECONDS` one step of the ladder, and never resubmit a
   directory that holds `submission.json` or `submission-state.json`
   (`qi_platform.py reconcile` recovers its receipt).
7. Analyze with the generator's `--analyze`, then commit the run
   directories, the analysis, its `--replay` gate, a refreshed `usage.json`
   and the `docs/state/research_state.json` registration in one change
   (root AGENTS.md, "Records").

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

## What the provider requires

Every rule below is quoted from a live page read on 2026-10-22 and from the
capture retained on 2026-10-16 (`scripts/capture_qi_docs.py --check` verifies
the captures; [knowledge-base.md](knowledge-base.md) lists them). The live
General Conditions of Use still carry the date 6 Feb 2025.

| Rule | Quote | Live page | Retained capture |
|---|---|---|---|
| Queue, hardware only | "You are not allowed to have more than 3 jobs in the queue for a hardware backend, in order to provide equal access opportunities for everybody. (Attempts of) abuse will lead to removal of your account." | <https://www.quantum-inspire.com/faq/> | [site/faq.md:84](site/faq.md) |
| Shared resources, per-backend limits | "Each backend imposes a limit on the number of qubits that can be executed upon or simulated. The number of shots for each execution request is also limited. In addition, a limit on the amount of time an execution may run will be enforced by aborting running executions that exceed this limit." | <https://www.quantum-inspire.com/terms-and-conditions/> | [site/terms-and-conditions.md:39](site/terms-and-conditions.md) |
| Processor time | "To take precautions to avoid unnecessary loss of processor hours, e.g. by using the syntax checking tools provided by QI." (item 9) | same | [site/terms-and-conditions.md:61](site/terms-and-conditions.md) |
| Non-commercial use, suspension | "Non-adherence or violation of these terms and conditions may lead to immediate suspension or revocation of the account(s) associated with the violation." "Please note that QI is solely intended for non-commercial use." | same | [site/terms-and-conditions.md:35](site/terms-and-conditions.md) |
| Operator rights | "To assign priority to particular jobs without regard to the order of the queue; b. To assign computing or storage resources to the uploaded jobs; c. To relay certain jobs to external providers ..." and to decline or suspend a job that "would exceed the available computer time" (item 6) | same | [site/terms-and-conditions.md:55](site/terms-and-conditions.md) |
| Submission by script | "Code has to be written on the website or submitted via the API (either by using an SDK or by initiating requests to the API directly)." | same | [site/terms-and-conditions.md:39](site/terms-and-conditions.md) |
| QX emulator size and time | "On our commodity server you cabn simulate up to 26 qubits." "Depending on the type of user account job durations could be maximized to 30 minutes compute time." | <https://www.quantum-inspire.com/backends/qx-simulator/> | [site/backends_qx-simulator.md:21](site/backends_qx-simulator.md), [:27](site/backends_qx-simulator.md) |
| Tuning | "Each backend comes with an extensice automated tuning program that takes from a few seconds to 30 minutes long. When your job is scheduled while tuning is ongoing, this will add to your waiting time." | FAQ | [site/faq.md:89](site/faq.md) |

The API catalogue adds the structural numbers of the table above (QX: 3600 s
per job, 5 jobs per batch, 5 batches queued; this account's QX record holds
10 qubits, below the page's 26).

No provider page sets an interval between submissions, a rate limit or a cap
on emulator use: the FAQ, the general conditions and the QX page were read in
full for one on 2026-10-22 and hold none. The pause of `qi_platform.py` is
therefore a repository rule, and tuning needs no idle time from the account:
the platform runs it on its own schedule and a job that meets it waits.

From the same conditions:

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
  submitting the next. `submit` enforces the pause account-wide: it refuses a
  hardware batch while any account job on a hardware backend type is
  unfinished or finished less than `HARDWARE_PAUSE_SECONDS` ago, so
  concurrent sessions sharing the account alternate. The pause is 30 s by
  default and follows the escalation below; the provider sets none.
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


## Pause escalation

`HARDWARE_PAUSE_LADDER` = (30, 60, 90, 120) s in `scripts/qi_platform.py`;
`QI_HARDWARE_PAUSE_SECONDS` selects a step, unset selects 30 s, and any other
value is refused. A series starts at 30 s. A system issue moves it one step up
for the rest of that series and the next: a submission the API refuses or
answers with a server error, a job that fails or returns fewer shots than
requested, or a platform message about load or fair use; a series whose own
preregistered stop ends it on such an issue resumes, as a new series, at the
next step. The step that ran
is recorded in each batch's `series-gate.json` (`pause_seconds`) for the
series that write one, and the case states it. The `bdsc_pauli_tuna_17`
batch-00 and batch-01 receipts predate the field: both were submitted under
the fixed 120 s pause that preceded the ladder, and the 129 s between
batch-00's last finish and batch-01's creation in their `results.json`
records matches it; batches 02 to 08 record 30 s. Case budgets take the top
step, 120 s, as their wall-time ceiling, so a series run at any step stays
inside its approved budget and its manifests do not depend on the step.
