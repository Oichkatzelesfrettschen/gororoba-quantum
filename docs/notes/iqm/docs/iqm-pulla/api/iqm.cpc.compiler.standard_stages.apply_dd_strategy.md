> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_dd_strategy.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_dd_strategy.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 506d7fd2b4bf3f349c7370fa1e4f059a2b98a24780352b7effa590fe820c67df.

# iqm.cpc.compiler.standard_stages.apply_dd_strategy

iqm.cpc.compiler.standard_stages.apply_dd_strategy(*schedules*, *builder*, *context*, *dd_is_disabled=True*, *use_standard_dd_strategy=True*, *DDStrategy_merge_contiguous_waits=True*, *DDStrategy_target_qubits=None*, *DDStrategy_skip_leading_wait=True*, *DDStrategy_skip_trailing_wait=True*, *DDStrategy_gate_sequences_ratio=None*, *DDStrategy_gate_sequences_gate_pattern_xy=None*, *DDStrategy_gate_sequences_align=None*)  
Insert dynamical decoupling sequences into the schedules, if dynamical decoupling is enabled.

DDStrategy can also be read from the Compiler context, from under the key “DDStrategy”. In this case, the strategy provided will override the DDStrategy options given as args to this function.

Parameters:  
- **schedules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")*\]*) – Schedules representing the compiled circuits.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The ScheduleBuilder.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Compiler context.

- **dd_is_disabled** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Set to `False` to enable dynamical decoupling.

- **use_standard_dd_strategy** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to use the standard decoupling strategy (overrides the below arguments).

- **DDStrategy_target_qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – The qubits to which DD is applied (`None` means apply to every applicable qubit).

- **DDStrategy_merge_contiguous_waits** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to merge contiguous waits (see `DDStrategy`).

- **DDStrategy_skip_leading_wait** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to skip leading waits (see `DDStrategy`).

- **DDStrategy_skip_trailing_wait** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to skip trailing waits (see `DDStrategy`).

- **DDStrategy_gate_sequences_ratio** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Minimal durations for the Wait to be replaced with the DD sequence (in PRX gate durations) in the DD sequence.

- **DDStrategy_gate_sequences_gate_pattern_xy** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – XY Gate patterns in the DD sequence. If you want to provide custom PRX angles instead of XY patterns, you must provide the DDStrategy in the Compiler context.

- **DDStrategy_gate_sequences_align** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Alignments in the DD sequence (“asap”, “alap” or “center”)

Returns:  
THe schedules where applicable Waits are replaced with DD sequences.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")\]
