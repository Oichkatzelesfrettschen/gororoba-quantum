> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.construct_run_result.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.construct_run_result.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a4bc3bb12936033956ce8b14211b05da13e453c44ff1cd71b52c8c47c46e19ba.

# iqm.cpc.core.run_result.construct_run_result

iqm.cpc.core.run_result.construct_run_result(*run_data*, *sweep_results*, *post_processes=None*)  
Construct the complete experiment results of a run.

Loads data that was saved by Station Control, using reconstructing functionality for run result. Runs post-processing functionality against the dataset of the constructed run result and packages it to a single structure along with run data.

Parameters:  
- **run_data** ([*RunData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "(in iqm-station-control-client v14.0.0)")) – Data of the run for which a run result should be constructed.

- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]\]*) – Sweep results of the run for which a run result should be constructed.

- **post_processes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[*[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")*\],* [*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")*\]\]* *\|* *None*) – List of functions to apply for dataset of the reconstructed run result. Default to returning reconstructed run result without changes.

Returns:  
Run result which contains the post-processed run data and the post-processed dataset.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")
