> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bdc1aa65a5411be243c2920f7d4d1a4b20eb4375033bd6455375061e9e9b8d1c.

# iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule

iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule(*builder*, *schedule*)  
Merge adjacent `Wait` instructions in the drive channels of the given schedule.

Makes a deep copy `schedule` and iterates through its drive channels to merge adjacent `Wait` instructions into a single `Wait` instruction.

Also merges `Wait` instructions if they are separated by `Block` instructions.

Parameters:  
- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – Provides channel information.

- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")) – Schedule to process.

Returns:  
Deep copy of `schedule` with `Wait` instructions merged.

Return type:  
[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")
