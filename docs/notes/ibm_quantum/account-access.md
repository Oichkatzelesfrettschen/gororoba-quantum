# IBM account access and the job inventory

The repository reaches IBM Quantum through qiskit-ibm-runtime 0.50.0 only.
No IBM MCP server is registered: `claude mcp list` shows the quantum-inspire,
openquantum, quandela and kaggle servers connected, and on 2026-10-19
qi_backends, qi_jobs, get_credits, qd_availability and get_accelerator_quota
each answered, so every IBM read is a script call under the repository's
Python.

## Accounts

`QiskitRuntimeService.saved_accounts()` lists two saved accounts in
`~/.qiskit/qiskit-ibm.json`: `default-ibm-quantum-platform` (primary) and
`backup-ibm-quantum-platform`. `gororoba_quantum/ibm_account.py`
(`open_service`) selects one through `GOROROBA_IBM_ACCOUNT`; unset or empty
opens the default. Each account is a separate IBM Cloud instance with its own
600 s rolling quota and its own inventory file (gate core-587).

## Read surfaces

Every surface below is read-only and spends no quota. A probe of each, on
both accounts, read the following on 2026-10-19 (qiskit 2.5.2):

| Surface | Call | Result |
|---|---|---|
| Service | `ibm_account.open_service(QiskitRuntimeService)` | opens in 1.6 to 2.8 s |
| Quota | `service.usage()` | primary 402 s consumed, 198 s remaining; backup 0 s consumed |
| Backends | `service.backends()` | ibm_fez, ibm_kingston, ibm_marrakesh on both accounts |
| Status | `backend.status()` | operational, pending-job counts per backend |
| Target | `backend.target` | 156 qubits on each backend |
| Calibration | `backend.properties()` | each backend's `last_update_date` |
| Configuration | `backend.configuration()` | `processor_type` Heron r2, `rep_delay_range` [0, 0.002] s |
| Jobs | `service.jobs(limit=N)`, `job.status()`, `job.metrics()`, `job.inputs`, `job.result()` | primary lists every job; backup holds none |

A shell reproduces the probe from `gororoba_quantum/` with
`GOROROBA_IBM_ACCOUNT` set per account. The output names no instance CRN,
account identifier or token, and none enters a record (`AGENTS.md`, Records).

## Failed jobs and settlement

A job the service cancels at its `max_execution_time` ends in `ERROR`
(error code 1305), returns no result and bills the QPU lock time it
consumed. The four Kingston state-prep control jobs of 2026-10-18 that ended
this way carry `qpu_charge_time_seconds` of 2, 2, 5 and 5 in
`job.metrics()["usage"]`. Their usage status still read `pending` nine hours
after they ended, while the account's consumed seconds already include the
14 s: the primary's consumption rose from 382 s to 402 s between the
inventory observation and the probe, which equals the two completed jobs'
3 s each plus the four failed charges. The usage period's start moved
from 2026-09-20T09:20Z to 2026-09-21T05:13Z between the two readings, and
`reconcile_qpu_inventory.window_charge` over the inventory's jobs reads
382 s in either period, so no job left the window. A later collection
read all four settled, `final` in collect.json, which is the service's
`complete` in the inventory, at the same 2, 2, 5 and 5 s; the refreshed
inventory records them and the reconciliation binds each to its run.

`scripts/observe_qpu_job_inventory.py` records DONE, ERROR and CANCELLED
jobs and refuses while any job is unfinished or its usage status differs
from `complete`, so an observation waits for settlement.
`scripts/reconcile_qpu_inventory.py` binds a failed job's settled charge to
the run whose collect.json records `result_unavailable` and counts it in the
usage-window sum. A job cancelled before it ran has no running timestamp and
bills zero; both scripts record it as an unexecuted cancellation that needs
no archive or collection and adds nothing to the window, while a CANCELLED
job with a running timestamp or a charge follows the failed-job rule. The
zero-charge shape is inferred from the service's billing rules; no retained
job has shown it.

## Inventory freshness

The inventory is an observation at its `observed_at`. A run whose
`record.json` submission started at or after that instant names jobs the
observation cannot hold: `inventory_retained_runs.py` (core-264) lists them
under `awaiting_observation_job_ids` and `reconcile_qpu_inventory.py`
(core-196) lists their raw archives under `awaiting_observation`, so a
retained run lands without a live refresh. Every job of a run submitted
earlier must appear in the inventory. The next observation, once every
charge settles, moves the awaiting jobs into coverage:

```sh
"$PYTHON" scripts/observe_qpu_job_inventory.py --out results/live/qpu-job-inventory.json
"$PYTHON" scripts/reconcile_qpu_inventory.py --snapshot results/live/qpu-job-inventory.json \
    --out results/live/qpu-job-retention-audit.json
"$PYTHON" scripts/inventory_retained_runs.py
```

`reconcile_qpu_inventory.py` writes its audit with exclusive creation, so the
previous audit moves out of the way first. A failed job's run needs a fresh
`live_run.py --collect` after settlement, so its collect.json records the
final charge the reconciliation compares.
