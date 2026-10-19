> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.merge_datasets_dac.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.merge_datasets_dac.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f45380f813ec11e9de332caf28993f40f3fd37ff4ca5628601efb6187ec573e.

# iqm.benchmarks.benchmark_definition.merge_datasets_dac

iqm.benchmarks.benchmark_definition.merge_datasets_dac(*datasets: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Dataset\]*) → Dataset  
Merges a list of datasets recursively to minimize dataset sizes during merge.

Parameters:  
**datasets** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Dataset\]*) – A list of xarray datasets

Returns:  
A list containing a single merged dataset

Return type:  
*Dataset*
