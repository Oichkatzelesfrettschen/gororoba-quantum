> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.set_layer_transformations.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.set_layer_transformations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e8f86645a8bc38069d2ae763bdb86a16da7422af3fc54e9639364beaa70d4e1b.

# iqm.cpc.compiler.layering_stages.set_layer_transformations

iqm.cpc.compiler.layering_stages.set_layer_transformations(*circuits*, *flux_layer_transformations=None*, *non_flux_layer_transformations=None*)  
Set layer transformations for the layered circuits.

Note

Modifies `circuits` in-place.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitLayer*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html#iqm.cpc.compiler.layering_stages.CircuitLayer "iqm.cpc.compiler.layering_stages.CircuitLayer")*\]\]*) – The layered circuits.

- **flux_layer_transformations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of transformations applied to flux layers. These should correspond to a transformation “gate” registered in the schedule builder.

- **non_flux_layer_transformations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of transformations applied to non-flux layers. These should correspond to a transformation “gate” registered in the schedule builder.

Returns:  
The layered circuits with the applied transformations.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitLayer*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html#iqm.cpc.compiler.layering_stages.CircuitLayer "iqm.cpc.compiler.layering_stages.CircuitLayer")\]\]
