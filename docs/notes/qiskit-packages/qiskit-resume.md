# qiskit-resume

qiskit-resume 0.2.1 (`python-qiskit-resume`, console script `qresume`)
records every primitive call of a script into a local `.qresume` database.
A rerun replays the recorded calls, reconnects to a job still running on
IBM instead of resubmitting it, and spends new QPU time only on calls not
yet recorded. It wraps `BaseSamplerV2` and `BaseEstimatorV2`. It records
`BitArray`, `DataBin` and `PrimitiveResult` objects, and circuits as QPY.
`resume_run(path, seed=..., qpu_budget_s=..., on_divergence=...,
on_backend_change=...)` opens a run. The run stops with `DivergenceStop`
when the rerun's calls differ from the record, `BackendChangedStop` when
the backend changes, and `BudgetExceeded` or `QuotaExhausted` at its
budget.

## Hazards

Reading a database unpickles every segment tagged `__p__`. The
`allow_pickle` flag gates writing only, so opening a `.qresume` file from
another source runs its code. Open only databases written on this host.

## Connections

- It overlaps live_run.py's own retention: `--collect` writes the lossless
  `raw/<job_id>/` record before analysis, and `--preserve-raw` recovers it.
  A replayed call returns recorded data, never a fresh calibration. The
  calibration rule of [AGENTS.md](../../../AGENTS.md) (QPU time and
  calibration) keeps qiskit-resume out of the approved submit path, whose
  binding dry run and `--submit` run back to back in `approved_run.sh`.
- `qpu_budget_s` is a client-side guard. It complements the 600 s rolling
  quota and the case's `--max-execution-seconds` and replaces neither.
- Wrapping Aer or `StatevectorSampler` primitives makes long local sweeps
  restartable without approval.
- The `seed` argument follows the repository seed rule: a new run takes a
  QRNG draw.
