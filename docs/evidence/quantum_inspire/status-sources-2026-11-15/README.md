# Quantum Inspire status sources, read 2026-11-15

These files record which sources report the state of the Quantum Inspire backends on 15 November 2026 and at what
granularity. They are the measurements behind `scripts/qi_status.py`. Every request was a read: GET on the compute
API, and the stored panel queries of QuTech's public dashboards. Status and availability change after the read.

| File | Observation |
|---|---|
| `status-document.json` | one run of `scripts/qi_status.py`: backend types, instances, heartbeats, both queue scopes, the public status record and each backend dashboard's notices and calibration reach |
| `calibration-panel-observation.json` | every data panel of the four backend dashboards queried once: all 16 panels of Tuna-17 and of Tuna-9 answer HTTP 400 after 10.2 s with the datasource error `dial tcp ...:443: i/o timeout`; all 20 panels of Tuna-5 answer HTTP 500; the Ry emulator dashboard holds no data panel |
| `link-burst-observation.json` | 20 requests to the link service inside 4.9 s: the first four are redirected, the fifth and every later one answer HTTP 428 |
| `time-range-observation.txt` | the Status dashboard answers over its stored `now-6h` range whatever range the request names |
| `api-route-observation.json` | `/healthz` 200; `/drain_mode` and `/backends/hostnames` 403; `/metadata/backend/7` 404; `/reservations` an empty page; the field names of a backend type and of the job, batch job, result and queue schemas |

## What each source reports

- Compute API, `GET /backends`: one of `offline`, `idle`, `executing`, `calibrating`, `benchmarking` per physical
  instance, with its message and last heartbeat. In `status-document.json` Tuna-17 is `calibrating` with a heartbeat 5.7 s old.
- Compute API, `GET /backend_types/{id}/queue`: the job count and the minimum, average and maximum wait, over all
  users (`user_only=false`) and over the account. In `status-document.json` the Tuna-17 queue holds 13 jobs, 0 of them the account's.
- Public Status dashboard (datasource `prometheus-qtc`): the status value of each backend type at one-minute
  spacing over the last 6 hours. In `status-document.json` Tuna-17 changes state 8 times in that window.
- Public backend dashboards: dated notices, and per-qubit T1, T2 Ramsey, T2 echo, initialization, readout, readout
  QND, single-qubit gate and Bell-state error from the datasource `prometheus-qi2-monitoring`.

## Per-qubit calibration

The per-qubit series are unavailable from every source read. The Tuna-17 dashboard's notice of 2026-10-22 states
that the provider is "unable to show the latest performance data due to concerns related to the security leaks in
PHP". Grafana reports a TCP dial timeout to that datasource on both days it was read, 2026-10-27
([tuna-projector-geometry](../../tuna-projector-geometry/README.md)) and 2026-11-15; the state between those days
is unmeasured. The compute API serves no calibration route: its OpenAPI definition lists none, and
`/metadata/backend/7` answers 404. A backend type's fields carry the gate set, topology, limits and compiler passes
and no coherence or error figure.

`scripts/qi_status.py` reports this as each dashboard's `calibration.state`. The run that first finds `data` also
carries the latest value of every "Latest" panel, so the return of the series needs no code change.

hypothesis: the datasource is closed on purpose, as the notice says, and returns when the provider reopens it.
Falsifier: a `datasource-error` that persists after the notice is withdrawn. A characterization run on the device
is the remaining source of per-qubit figures; it is a hardware job and follows the approval rule of AGENTS.md
("Hardware services").

## Link service

hypothesis: `dashboard.quantum-inspire.com` applies a burst limit. Evidence: the 428 answers above, a redirect 7 s
after the burst, and redirects for every request of three later runs that spaced the five link requests 3 s
apart. `scripts/qi_monitoring.py` resolves the link on every call, so a caller that queries several panels in a
row meets the limit; `scripts/qi_status.py` resolves each dashboard once per run.
