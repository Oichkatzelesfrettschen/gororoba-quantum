> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_drive_crosstalk.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_drive_crosstalk.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b5e1cf8938cda4e9f4b4dd39f8cd0d40a59657af1c23c3a134a012eef50a001c.

# iqm.cpc.compiler.standard_stages.apply_drive_crosstalk

iqm.cpc.compiler.standard_stages.apply_drive_crosstalk(*schedules*, *builder*, *context*, *drive_crosstalk_is_enabled=False*, *crosstalk_loci=None*)  
Add drive-crosstalk compensation pulses to the schedules.

For each `<target>__<control>` locus in `crosstalk_loci`, the control’s drive channel content is replayed on `<target_drive_channel>.aux0`, IQ-scaled by the calibrated crosstalk amplitude and phase-shifted by adding the calibrated crosstalk phase to the `phase_increment` of the first replayed `IQPulse`. The compensation pulses are built by the `drive_crosstalk.drive_crosstalk` gate implementation (see `DriveCrossTalk`), fetched via the builder.

This runs as the last schedule-level pass so the compensation pulses are not modified by any later pass. If compensation is disabled or no loci are given, the schedules are returned unchanged.

Parameters:  
- **schedules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")*\]*) – Schedules representing the compiled circuits.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – ScheduleBuilder used to resolve channels and the compensation implementation.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Compiler context (currently unused by this pass).

- **drive_crosstalk_is_enabled** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Enables/disables this pass.

- **crosstalk_loci** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – `target__control` strings for which compensation is attempted.

Returns:  
Schedules with auxiliary compensation channels added where possible.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")\]
