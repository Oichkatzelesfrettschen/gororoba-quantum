> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.resolve_layers.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.resolve_layers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 787837374fad36b72019761069f1421c955fc0328a1b7f4967afde2d9b6f9937.

# iqm.cpc.compiler.layering_stages.resolve_layers

iqm.cpc.compiler.layering_stages.resolve_layers(*circuits*, *components*, *builder*)  
Resolve the layered circuits into TimeBoxes, while applying the prescribed transformations.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitLayer*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html#iqm.cpc.compiler.layering_stages.CircuitLayer "iqm.cpc.compiler.layering_stages.CircuitLayer")*\]\]*) – The layered circuits.

- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping")) – The full set of active locus components for the circuit batch.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The schedule builder

Returns:  
TimeBoxes representing the circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")\]
