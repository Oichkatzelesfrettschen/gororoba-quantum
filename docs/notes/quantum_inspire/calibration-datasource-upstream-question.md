# Calibration datasource: question to the provider (unsent draft)

Status: draft, unsent. The [contact-route audit](upstream-readout-report.md#verified-contact-routes) owns the
verified addresses; the owner chooses the route and sends the text.

## Observations the question rests on

The [status-source observations of 2026-11-15](../../evidence/quantum_inspire/status-sources-2026-11-15/README.md)
record them:

- The Tuna-17 public dashboard carries the notice "[2026-10-22] We are unable to show the latest performance data
  due to concerns related to the security leaks in PHP."
- Every calibration panel of the Tuna-17 and Tuna-9 public dashboards answered HTTP 400 on 2026-11-15, with
  Grafana reporting a connection timeout to the datasource `prometheus-qi2-monitoring`; the same failure was read
  on 2026-10-27. The Tuna-5 dashboard's panels answered HTTP 500.
- The Status dashboard and the compute API answered normally on both days.
- The compute API's OpenAPI definition lists no calibration route, and `GET /metadata/backend/7` answers 404.

## Text

> Subject: Tuna-17 and Tuna-9 performance data on the public dashboards
>
> Dear Quantum Inspire team,
>
> Thank you for keeping Tuna-17 available; we run small characterization-sensitive experiments on it and rely on
> the per-qubit T1, T2, readout and gate-error panels to plan them. Since your notice of 22 October the panels of
> the Tuna-17 and Tuna-9 dashboards return a datasource timeout (we read this on 27 October and again on
> 15 November), while the Status dashboard works as before.
>
> Could you tell us:
>
> 1. whether the performance data will return to the public dashboards, and roughly when;
> 2. whether, in the meantime, an authenticated route exists through which an account can read the latest
>    per-qubit calibration values, for example a backend metadata endpoint of the compute API;
> 3. whether the calibration values in force when a job ran can be attached to that job's result.
>
> We are glad to run a short characterization batch of our own in the meantime, and would welcome your advice on a
> schedule that least disturbs your calibration cycle.
>
> With thanks and best regards

## What an answer changes

An answer to the first question dates the return of the `data` state that `scripts/qi_status.py` reports. A route
under the second or third replaces the dated rows of the
[characterization draft](tuna17-characterization-case-draft.md) with provider values.
