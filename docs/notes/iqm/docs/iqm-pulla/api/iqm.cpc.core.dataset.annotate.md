> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.annotate.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.annotate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1d9d3b4c44a92ae036e352c26655dca37bb77f527f36d559acf7cd8e0760d90c.

# iqm.cpc.core.dataset.annotate

iqm.cpc.core.dataset.annotate(*data*, *annotation=None*, *prefix=''*)  
Add parameter data to an array.

Attaches a name to a DataArray. Also adds “parameter” data to the attributes.

Various Exa functions leverage the additional metadata, mostly for display purposes.

Parameters:  
- **data** (*DataArray*) – Array to be modified.

- **annotation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)") *\|* *None*) – new name for the array. If annotation is a Parameter, use its name and label instead. If not given, prefix will be added to existing names.

- **prefix** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – If given, this prefix is added to the new name and labels. If the new name already has the same prefix, it won’t be duplicated.

Returns:  
The modified array.

Return type:  
*DataArray*
