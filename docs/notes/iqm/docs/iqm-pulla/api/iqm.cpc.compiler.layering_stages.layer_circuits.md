> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_circuits.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 728421af8f1c1cc9bdd1f96925c671f155f8ef09ad01d8db72dda443cbf9c513.

# iqm.cpc.compiler.layering_stages.layer_circuits

iqm.cpc.compiler.layering_stages.layer_circuits(*circuits*, *components*, *skip_layering=False*)  
Layer circuits into flux and non-flux layers.

The algorithm maximises the flux-layer depth, by merging any `CircuitOperation` involving flux pulses into the previous flux layer if there’s no operations in between that with colliding loci. The layers containing flux pulses will have CircuitLayer.layer_type == “flux”, and the ones that do not contain flux pulses will have CircuitLayer.layer_type == “non-flux”.

Note

If a flux CircuitOperation resolves into `Schedule` that contains also drive pulses (like ACStark CZ gate), this pass will not produce correct flux layering.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]*) – The circuits to layer.

- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping")) – The full set of active locus components for the circuit batch.

- **skip_layering** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, group the whole circuit into a single layer with CircuitLayer.layer_type == “full_circuit”.

Returns:  
For each circuit, its layering into flux and non-flux layers.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitLayer*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html#iqm.cpc.compiler.layering_stages.CircuitLayer "iqm.cpc.compiler.layering_stages.CircuitLayer")\]\]
