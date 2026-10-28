# Ascella day-separated matched-mesh repeat

The user requested a repeat tomorrow to assess time-dependent changes. This case repeats all five
settings in the seven-job context diagnostic's forward-packed iterator with the same complete operators,
parameters and registered compilation identifiers. The previous forward job started on
2026-10-27 at 17:38:05.339165 Pacific time. The earliest admitted repeat is 2026-10-28 at
17:38:05.339165 Pacific time, exactly 24 hours after that provider start. The case also requires the
local Pacific calendar date to be 2026-10-28; an execution on a later date requires a successor case.

The one `qpu:ascella` job carries five iterator entries, each requesting 65,536 accepted events with a
131,072 detected-shot cap. It retains every physical port and invalid photon-number outcome. The job's
execution stop is 300 seconds and its credit ceiling is **1.131072 credits** under the current per-shot
tariff and recorded one-credit job price. The earlier identical-size forward job took 16 seconds; that
measurement is a runtime reference, not a guarantee. The CLI's `expected_seconds=300` is the stop-limit
compatibility input. The runner refreshes the provider offer, processor, token occupancy and price before
submission and rejects a changed payload or unavailable status.

The frozen family covers the five baseline settings and five next-day settings, with thirteen physical
or invalid categories and one leakage aggregate for each observation: **140 endpoints**. The analysis
reports total-variation point estimates and simultaneous bounds for each baseline-to-repeat comparison,
with 95% Clopper-Pearson coverage conditional on IID accepted events within each setting. It checks
returned circuit and input digests and reports a matched-mesh interpretation only for equal records.
The user selected the five settings before the baseline job; the later repeat retains all five rather
than selecting favorable outcomes after observing the diagnostic data.

Matching returned serialization does not establish unchanged analog controls. Time, calibration and
source or detector response can confound a day-separated difference. Packed list order attributes
settings to metadata but does not establish individual physical iteration timestamps. Incident source
pulses and undetected-photon loss remain outside the measured denominator.

The [case producer](../../../scripts/ascella_transition_day_repeat.py) binds the previous forward job,
the completed mesh-and-port analysis, source code, the user-authorized written case and the exact
provider payload. Before a POST, the runner checks the Pacific-date and 24-hour boundaries, confirms
the acquisition worktree has no uncommitted changes, checks the live price and availability, and
uses the provider's persistent submission checkpoint. An existing ambiguous checkpoint blocks retries;
an existing submission is collected instead of resent. The scheduled service may repeat read-only
admission checks for up to one hour if the token is busy or Ascella is calibrating. It does not retry a
POST whose outcome is unknown.

The service collects raw result bytes before analysis, then writes a source-bound analysis, acquisition
inventory and findings. If tracked files changed during acquisition, it retains the data and stops
before integrating the research registry. Otherwise it appends the acquisition and its bounded claim,
then regenerates and validates the research-state views. The service preserves the original pilot and
seven-job results. The earlier 54-setting pilot remains failed; the next-day diagnostic does not
retroactively change that decision.

The proposed service depends on this acquisition worktree remaining available and clean until the
admitted time. A persistent user timer with user linger can survive logout and reboot. A suspended or
powered-off host may run the service only after it wakes, and the date guard prevents a late job on a
later calendar day.
