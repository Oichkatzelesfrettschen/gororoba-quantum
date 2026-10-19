> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_schedules.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_schedules.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd3ef92e1fffbd7946b1dd1fbfdae134973e20bfeeccbc650f8e50155797e579.

# iqm.cpc.compiler.layering_stages.layer_schedules

iqm.cpc.compiler.layering_stages.layer_schedules(*schedules*, *builder*, *components*, *flux_layer_transformations=None*, *non_flux_layer_transformations=None*)  
Extract flux and non-flux layers from the full schedule and apply the prescribed transformations to them.

Note

Assumes the Schedules are already layered, will not be enforcing layering.

Parameters:  
- **schedules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")*\]*) – The Schedules representing the circuits.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The schedule builder

- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping")) – The full set of active locus components for the circuit batch.

- **flux_layer_transformations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of transformations applied to flux layers. These should correspond to a transformation “gate” registered in the schedule builder.

- **non_flux_layer_transformations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of transformations applied to non-flux layers. These should correspond to a transformation “gate” registered in the schedule builder.

Returns:  
`schedules` with the prescribed transformations applied to their respective layers.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")\]
