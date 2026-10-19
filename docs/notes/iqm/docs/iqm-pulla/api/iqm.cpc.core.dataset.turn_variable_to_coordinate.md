> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.turn_variable_to_coordinate.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.turn_variable_to_coordinate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 393ccaa9ead6bf86181bd84b6aa39a9919ef87a40a097efe7d4bc669a1c906bd.

# iqm.cpc.core.dataset.turn_variable_to_coordinate

iqm.cpc.core.dataset.turn_variable_to_coordinate(*dataset*, *variable_name_to_convert*)  
Turns variable of xarray dataset into a coordinate.

The function is added because the native xarray utilities always return a new dataset, so changes don’t stick inside analysis dataset.

Parameters:  
- **dataset** (*Dataset*) – the dataset where the change will happen

- **variable_name_to_convert** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of variable which needs to be turned into a coordinate

Returns:  
None

Return type:  
None
