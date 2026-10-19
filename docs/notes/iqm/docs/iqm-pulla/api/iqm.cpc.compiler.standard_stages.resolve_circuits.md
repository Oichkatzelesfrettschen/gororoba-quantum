> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_circuits.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 779983aa6cb2489c3cb58f41178d0087b8d7406f25b4663da229d6352b7b658a.

# iqm.cpc.compiler.standard_stages.resolve_circuits

iqm.cpc.compiler.standard_stages.resolve_circuits(*circuits*, *builder*, *scheduling_strategy='ASAP'*)  
Resolve the circuits to timeboxes.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")*\]*) – The circuit to resolve.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The schedule builder.

- **scheduling_strategy** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Scheduling strategy to be used in the resolved TimeBoxes (see `TimeBox`).

Returns:  
List of TimeBoxes (one TimeBox per circuit).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")\]
