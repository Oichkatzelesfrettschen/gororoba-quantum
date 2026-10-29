# Ascella repeat: scheduler admission and start window

The [CI case](README.md) keeps its operators, compiled meshes, request body
(`body_sha256` b349e2d0...), 1.131072-credit ceiling and 140-endpoint analysis.
This amendment changes two admission rules of the hosted scheduler and the
start rule of the matched check. The case README stays byte-identical because
`cases.json` and `campaign.json` bind its sha256.

**Platform status.** The Quandela Explorer row for `qpu:ascella` reads
`running` while the processor serves other users' jobs and `available` only
when it is idle. Every tick from 2026-10-29T00:40Z to 07:17Z read `running`
(`qd_schedule.py` reason "qpu:ascella is running"), while the Explorer
statistic reported 90 to 92 % daily availability. The job admitted only
`available`, so it waited through its whole window and held at its
`latest_start`, 2026-10-29T06:59Z, without sending a request. The schedule now
admits `running` beside `available`, as the BDSC drift-series schedule does,
and `scripts/ascella_transition_ci_check.py --plan-check` requires that pair.
A token busy with another job still waits.

**Start window.** The schedule drops `latest_start`, and the matched check
admits any provider start at least 24 hours after the forward baseline
(2026-10-28T00:38:05Z), the separation `cases.json` preregisters ("matched
returned-mesh output distributions at least 24 hours apart"). The earlier
requirement that the start fall on the following Pacific calendar date
(2026-10-28 Pacific) is withdrawn; the analysis records `elapsed_hours`, so the
comparison states the separation it measured. A longer separation widens the
drift interval the comparison spans and leaves its test family unchanged.

**Resubmission key.** The held job keeps its record `matched-repeat.hold.json`
on the results branch. The amended job runs under the new key
`matched-repeat-admitted`, the scheduler's form for a resubmission after a
hold ([runbook](../../runbooks/quandela-scheduled-runs.md)).

**Calibration.** Each submit plans afresh against the live platform record
inside the submit lock, so the request runs under the processor's calibration
at submission; the returned input and compiled-circuit records identify the
served meshes.

**Authority.** The user's instruction of 2026-10-29, quoted in the schedule's
`approval`: run the repeat with the latest calibration regardless of the
self-imposed timeframes, and collect when it is collecting.
