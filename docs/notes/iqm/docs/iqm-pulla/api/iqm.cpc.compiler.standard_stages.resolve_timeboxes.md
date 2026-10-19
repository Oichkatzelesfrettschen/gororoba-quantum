> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_timeboxes.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_timeboxes.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f20f2fd9d0fc49b966816fc21acfa97d70fe7a9a1af0e7924e4a161cbce31821.

# iqm.cpc.compiler.standard_stages.resolve_timeboxes

iqm.cpc.compiler.standard_stages.resolve_timeboxes(*timeboxes*, *builder*, *neighborhood=1*)  
Resolve the timeboxes to schedules.

Parameters:  
- **timeboxes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")*\]*) – TimeBoxes representing circuits.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The ScheduleBuilder.

- **neighborhood** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The neighborhood for the scheduling (see: `ScheduleBuilder.resolve_timebox()`).

Returns:  
The time-resolved schedules (one for each circuit).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")\]
