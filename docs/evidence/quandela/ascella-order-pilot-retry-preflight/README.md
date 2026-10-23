# Ascella order pilot authorized retry preflight

The user authorized Ascella again with "ascella authorized" after the
execution hold. The bounded interpretation is one fresh retry of the original
order pilot, with manifest SHA-256
`1d1b9abfe727d92f6af1c81002b3e41e056b1b16330d3b8ae9746303bc3968fa`,
eight settings, at most 65,536 detected samples and 131,072 shots total,
180 seconds, and expected debit at most 1.016384 credits under the recorded
tariff. A repeated instrument error or zero-sample result stops further
Ascella submissions. The authorization grants neither a different case nor
unbounded retries.

The [catalogue](catalogue.json) was refreshed at 20:15:11 UTC on 22 October
2026. Ascella reported `available`, a 300-second platform limit, and
0.000001 credits per shot. The case retains its stricter 180-second cap.
The API exposes the per-shot price; the one-credit per-job component remains
the recorded offer value rather than a fresh authenticated offer quote.

The submit-free plan of the unchanged original case stopped at token
occupancy: zero running jobs and one queued job, against maxima of one
running and one queued job. The [occupancy read](occupancy.json) identifies
the queued job as `4058ce4e-7892-4da4-9e86-7f78f5fa9777`, the separate
Belenos diagnostic acquisition
`2026-10-22T170900Z-qpu_belenos-bdsc_diagnostic-b2-j1`. An active collector
was observed for that acquisition. Its status was `waiting`, with zero shots
and no start time. The acquisition remains owned by its independent workflow.

The [second tariff and occupancy read](tariff-and-occupancy.json), at
20:17:08 UTC, reports the same Ascella status, per-shot rate and occupied
queue slot. The preflight submitted zero jobs and canceled zero jobs.
The original acquisition receipts and raw result bytes remain at their
original paths.

The [instrument-readiness design](../../../design/ascella-instrument-readiness-and-packed-tests.md)
records the prior configuration error and the boundaries of instrument
recovery evidence. Platform availability alone cannot establish recovery.
