> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.prepend_heralding.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.prepend_heralding.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4f26b90c4a3d0b37a4804c79c7363f0c9d841f4c66e6fa9982c47f8d96aadc62.

# iqm.cpc.compiler.standard_stages.prepend_heralding

iqm.cpc.compiler.standard_stages.prepend_heralding(*timeboxes*, *builder*, *context*, *add_heralding=False*, *measure_operation='measure'*, *\**, *probe_all=True*)  
Add the heralding measurement TimeBox to all circuits (locus: active components that can be measured).

Parameters:  
- **timeboxes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")*\]*) – Timeboxes representing circuits.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The ScheduleBuilder.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Compiler context.

- **add_heralding** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to add the heralding measurement timebox to the schedules.

- **measure_operation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The measure operation to use, defaults to “measure”. NOTE: using “measure_fidelity” is not recommended, since the heralding measurement should be projective to be effective, and “measure_fidelity” is typically not calibrated to be projective.

- **probe_all** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to send the probe pulse to all components in the heralding measurement.

Returns:  
The timeboxes with the prepended heralding measurement.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")\]
