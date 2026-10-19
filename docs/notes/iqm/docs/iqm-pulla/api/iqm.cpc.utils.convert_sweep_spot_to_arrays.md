> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 62b455504026d60094e79f634822cace2529701fa66086380f7d23febf8ad59d.

# iqm.cpc.utils.convert_sweep_spot_to_arrays

iqm.cpc.utils.convert_sweep_spot_to_arrays(*results*, *readout_mappings*)  
Convert the sweep measurement results from Station Control into circuit batch measurement results.

Parameters:  
- **results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *np.ndarray\]*) – mapping of acquisition labels to 1D arrays of readout results with the length `num_shots * num_triggers_for_label_in_batch`

- **readout_mappings** (*ReadoutMappingBatch*) – for each circuit in the batch, a mapping of measurement keys to corresponding tuples of acquisition labels

Yields:  
Converted measurement results for each circuit in the batch.

Return type:  
Iterator\[\_CircuitMeasurementResultsNew\]
