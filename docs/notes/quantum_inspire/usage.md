# Quantum Inspire usage, limits and cost

## What the account is

One account type exists, free, with access to the hardware backends, the
emulator backends and storage for jobs and results (KB,
[managing-your-account](site/kbase_managing-your-account.md),
<https://www.quantum-inspire.com/kbase/managing-your-account/>). The API
shows one team marked `individual_user` with one active member of role
`member` (catalogue.json, identifiers stored only as 12-hex sha256).

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
after twenty-two jobs on 2026-10-16 (ten on QX, two on the Ry emulator, ten
on Tuna-17; 185344 shots completed, 166.48 s of reported execution; snapshot
2026-10-16T22:2xZ). The account
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
| Ry emulator | 1024 | 16.26 s (2-qubit X-only diagnostic) | 15.9 ms | runs/2026-10-16T213823Z-Rydberg-diagnostic |

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
  the MCP `qi_submit` tool asks before running.
- Every run keeps its circuits, cases.json digests, submission.json,
  raw shots and results.json under results/quantum_inspire/runs/.
- A simulation of 14 qubits or fewer runs on Kaggle (root AGENTS.md); a
  Quantum Inspire hardware run answers a question about the device.
