> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cb64293183b83d18984d9d9232e31a2c1c45a4689a5f3986298bee29030367ee.

# iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts

iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts(*schedules*, *builder*, *context*, *compute_execution_time_metrics=False*, *ignore_input_components=False*)  
Build the playlist from the schedules and merge the contexts for individual sweep spots.

When merging the context, the active components are the union of the active components in each sweep spot (unless explicitly given by the user). The default context keys are not merged (these should not be modified by any of the sweep spots), and any other keys in the context will be merged to mapping from the sweep spot id to the context entry.

Parameters:  
- **schedules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")*\]*) – Schedules to build into a Playlist.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The ScheduleBuilder.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The Compiler context.

- **compute_execution_time_metrics** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to compute schedule duration and minimum execution time for circuits.

- **ignore_input_components** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, components are always replaced with the ones found in context.

Returns:  
The Playlist containing schedules.

Return type:  
*Playlist*
