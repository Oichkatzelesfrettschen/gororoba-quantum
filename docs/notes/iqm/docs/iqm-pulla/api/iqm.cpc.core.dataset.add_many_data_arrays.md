> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.add_many_data_arrays.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.add_many_data_arrays.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9fa3456c367d91de1b7c0c1eb6295df73cdffc84c3eebe668a2fe1122db6cc6f.

# iqm.cpc.core.dataset.add_many_data_arrays

iqm.cpc.core.dataset.add_many_data_arrays(*ds*, *arrays*)  
Efficiently add multiple DataArrays to a Dataset in one shot.

Builds a dictionary from names to DataArrays and updates the Dataset in place. Variable attrs and coords on the DataArrays are preserved.

Parameters:  
- **ds** (*Dataset*) – Dataset to add to.

- **arrays** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[DataArray\]*) – Iterable of DataArrays to be added to the dataset.

Return type:  
None
