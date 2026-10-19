> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.split_along_dimension.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.split_along_dimension.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0ccb397980cca7973a440898cd8478d71bb9c2e1ffbc125a84f191d2233e64b2.

# iqm.cpc.core.dataset.split_along_dimension

iqm.cpc.core.dataset.split_along_dimension(*data*, *dimension*)  
Slice an N-dimensional dataArray along specified dimension.

Parameters:  
- **data** (*DataArray*) – dataArray to split

- **dimension** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the dimension to split

Returns:  
list of dataArrays corresponding to each value along dimension.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*DataArray*\]
