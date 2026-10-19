> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1d56dc37c1937c1a70a770c6fc6c2b5cfc67deed266fc63b8d09734a7bafd7e5.

# iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections

iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections(*schedules*, *builder*, *context*, *move_gate_frame_tracking_mode='full'*)  
Apply calibrated phase corrections if MOVE gates are used.

Parameters:  
- **schedules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")*\]*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)"))

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **move_gate_frame_tracking_mode** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")\]
