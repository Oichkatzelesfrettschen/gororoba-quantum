# Kingston mock scheduling diagnosis

Runtime 0.50.0 reaches the IBM service but receives HTTP 404 from
`GET /backends/mock_kingston/configuration`. Both automatic lookup and an
explicit lookup in the resolved active instance produce the same response.
Physical `ibm_kingston` status returns HTTP 200 and reports active. The
read-only probe submits zero primitive jobs.

The observed failure precedes circuit submission and server scheduling. The
client transforms `ibm_kingston` into `mock_kingston` for `dry_run=True`, then
looks up the mock backend. `QiskitRuntimeService.backend()` already tries an
uncached direct configuration fetch when discovery omits a backend. A fresh
service and explicit instance therefore test the context and negative-cache
explanations directly. The saved account omits an instance, while the public
`active_instance()` method resolves the instance used by the successful real
backend lookup. The retained report identifies it only by a 12-hex hash.

The installed 0.50.0 release matches the latest published Runtime release
observed during diagnosis. An upgrade is unsupported as a repair for the
observed failure. HTTP 404 establishes service unavailability to the selected
instance; it cannot distinguish absent deployment from entitlement masking.
IBM must restore the mock endpoint or provide access to resolve that boundary.

## Replay and source grounding

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/diagnose_qiskit_mock.py --backend ibm_kingston
```

The diagnostic observes SDK HTTP responses without altering requests. It
retains backend/endpoint/status only, excludes credentials and response bodies,
and restores the logger's original level. The report is
`kingston-mock-diagnosis.json` beside this note.

Installed Runtime 0.50 source paths establish the causal chain:

- `executor_sampler/sampler.py`: `Sampler.run(..., dry_run=True)` passes the
  option to the Executor; its documentation permits restricted mock access.
- `executor/executor.py`: Executor forwards `dry_run` to the service.
- `qiskit_runtime_service.py`: `_run` rewrites the backend name and calls
  `backend()` before `program_run`; `backend()` tries uncached lookup.
- `api/rest/cloud_backend.py`: configuration lookup issues the GET above.

Official references:

- [Sampler dry-run API](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/executor-sampler-sampler)
- [Runtime 0.50.0 release](https://github.com/Qiskit/qiskit-ibm-runtime/releases/tag/0.50.0)
- [Circuit time and billing](https://quantum.cloud.ibm.com/docs/guides/estimate-job-run-time)

## Timing and remaining work

Local compilation and simulation validate circuits and model predictions.
The Target gives a gate-duration lower bound. Local dynamic scheduling restarts
relative time after reset/control flow and assigns control flow zero duration;
that model cannot recover the unavailable controller's event schedule.

The [pilot protocol](../../gororoba_quantum/MODEL_DISCRIMINATION.md) retains its
historical 11.242518272-second estimate for four PUBs at 8,192 shots. A fresh
execution estimate and physical ceiling await qualified mock schedules and
production admission. The prepared circuit archive records the exact
intervention; successful local tests do not change the native qualification.

The supported next action is restoring service access, replaying the diagnostic,
and rerunning the exact preparation. Backend renaming, fabricated calibration,
and physical execution cannot establish the missing mock evidence.
